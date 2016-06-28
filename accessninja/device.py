#!/usr/bin/env python

import netrc
import paramiko
import time
import sys

from config import Config
from Exscript.util.interact import read_login
from Exscript.protocols import SSH2, Telnet, Account
from group import HostGroup, PortGroup
from os.path import join
from parser import Parser
from tempfile import NamedTemporaryFile


class Device(object):

    def __init__(self):
        self._name = None
        self._vendor = None
        self._transport = None
        self._save_config = None
        self._include_list = list()
        self._rules = list()
        self._hostgroups = list()
        self._portgroups = list()
        self._config = Config()
        self._rendered_groups = list()
        self._rendered_rules = dict()
        self._rendered_config = ''

    @property
    def vendor(self):
        return self._vendor

    @vendor.setter
    def vendor(self, value):
        if value not in ['junos', 'ios', 'arista', 'asa']:
            raise Exception("The only vendors currently supported are junos, arista, ios, asa")
        self._vendor = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def transport(self):
        return self._transport

    @transport.setter
    def transport(self, value):
        if value not in ['ssh']:
            raise Exception("The only transport supported currently is ssh")
        self._transport = value

    @property
    def save_config(self):
        return self._save_config

    @save_config.setter
    def save_config(self, value):
        self._save_config = value

    def add_include(self, value):
        self._include_list.append(value)

    def parse_file(self, name):
        self.name = name
        config = Config()
        try:
            f = open('{}/{}'.format(config.devices, name))
        except Exception, e:
            print('Could not open device file', e)
            raise e

        lines = f.readlines()

        for line in lines:
            if line.startswith('#'):
                continue
            if line.strip().startswith('vendor'):
                self.vendor = line.strip().split(' ')[1]
            if line.strip().startswith('transport'):
                self.transport = line.strip().split(' ')[1]
            if line.strip().startswith('save_config'):
                self.save_config = line.strip().split(' ')[1]
            if line.strip().startswith('include'):
                self.add_include(line.strip().split(' ')[1])

    def print_stats(self):
        for hg in self._hostgroups:
            hg.print_stats()
        for rule in self._rules:
            rule.print_stats()

    def render(self):
        print('Rendering {}'.format(self._name))
        for include in self._include_list:
            parsed_ruleset = Parser()
            parsed_ruleset.parse_file(join(self._config.policies, include))
            self._rules.append(parsed_ruleset)

        for ruleset in self._rules:
            self.resolve_hostgroups(ruleset)
            self.resolve_portgroups(ruleset)

        self.render_junos_hostgroups()
        self.render_junos_rules()

    def render_junos_rules(self):
        for ruleset in self._rules:
            self.render_junos_icmp_rules(ruleset.name, ruleset.icmp_rules)
            self.render_junos_tcp_rules(ruleset.name, ruleset.tcp_rules)

    def render_to_file_and_deploy(self):
        self.render()
        try:
            username, acc, password = \
                netrc.netrc().authenticators(self.name)
            account = Account(name=username, password=password, key=None)
        except Exception, e:
            print e
            print("ERROR: could not find device in ~/.netrc file")
            print("HINT: either update .netrc or enter username + pass now.")
            try:
                account = read_login()
            except EOFError:
                print("ERROR: could not find proper username + pass")
                print("HINT: set username & pass in ~/.netrc for device %s"
                      % self.name)
                sys.exit(2)

        def s(conn, line):
            print("   %s" % line)
            conn.execute(line)

        f = NamedTemporaryFile(delete=False)
        print f.name

        f.write(self._rendered_config)
        f.flush()

        print self.name

        tr = paramiko.Transport((self.name, 22))
        tr.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(tr)
        try:
            sftp.remove(f.name)
        except IOError, e:
            if e.errno != 2:
                print "Something wrong while uploading"
                sys.exit(1)

        upload_filename = "./config-{}".format(time.strftime("%d-%m-%Y-%H-%M-%S"))
        print 'Uploading as file: {}'.format(upload_filename)
        sftp.put(f.name, upload_filename)
        sftp.close()

        tr.close()
        f.close()

        print('Config uploaded as {}'.format(upload_filename))

        if self.transport == 'ssh':
            conn = SSH2(verify_fingerprint=False, debug=1, timeout=360)
        else:
            print("ERROR: Unknown transport mechanism: {}".format(self.transport))
            sys.exit(2)

        print('Logging in to apply the config')
        conn.set_driver('junos')
        conn.connect(self.name)
        conn.login(account)

        conn.execute('cli')
        conn.execute('edit')
        s(conn, 'load set {}'.format(upload_filename))
        print('Set loadded, commiting')
        s(conn, 'commit')
        print('Commited')

    def print_rendered_config(self):
        if len(self._rendered_groups):
            self._rendered_config = '\n'.join(self._rendered_groups)

        for ruleset_name, rules in self._rendered_rules.iteritems():
            self._rendered_config += '\ndelete firewall filter {}'.format(ruleset_name)
            for idx, rule in enumerate(rules):
                self._rendered_config += '\nedit firewall filter {} term {}'.format(ruleset_name, idx+1)
                self._rendered_config += '\n'+rule
                self._rendered_config += '\ntop'

        print self._rendered_config

    def render_junos_icmp_rules(self, name, icmp_rules):
        for rule in icmp_rules:
            if name not in self._rendered_rules:
                self._rendered_rules[name] = list()
            self._rendered_rules[name].append(rule.render_junos())

    def render_junos_tcp_rules(self, name, tcp_rules):
        for rule in tcp_rules:
            if name not in self._rendered_rules:
                self._rendered_rules[name] = list()
            self._rendered_rules[name].append(rule.render_junos(self._portgroups))

    def render_junos_hostgroups(self):
        for hg in self._hostgroups:
            self._rendered_groups.append(hg.render_junos())

    def resolve_hostgroup(self, hgname):
        hg = HostGroup(hgname)
        hg.parse_file()
        if hg.has_inline_groups:
            for ihg in hg.inline_groups:
                if ihg not in self._hostgroups:
                    self._hostgroups.append(ihg)
        if hg not in self._hostgroups:
            self._hostgroups.append(hg)

    def resolve_hostgroups(self, ruleset):
        for rule in ruleset.tcp_rules:
            if type(rule.src) == str and rule.src_is_group:
                self.resolve_hostgroup(str(rule.src)[1:])

            if type(rule.dst) == str and rule.dst_is_group:
                self.resolve_hostgroup(str(rule.dst)[1:])

    def resolve_portgroups(self, ruleset):
        for rule in ruleset.tcp_rules:
            if type(rule.srcport) == str and rule.srcport_is_group:
                self.resolve_portgroup(str(rule.srcport)[1:])

            if type(rule.dstport) == str and rule.dstport_is_group:
                self.resolve_portgroup(str(rule.dstport)[1:])

    def resolve_portgroup(self, pgname):
        pg = PortGroup(pgname)
        pg.parse_file()
        if pg not in self._portgroups:
            self._portgroups.append(pg)
