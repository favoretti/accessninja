#!/usr/bin/env python
from os.path import join

from config import Config
from group import HostGroup, PortGroup
from parser import Parser
from renderers.junos import JunosRenderer
from renderers.ios import IOSRenderer
from deployers.junos import JunosDeployer
from deployers.ios import IOSDeployer
from deployers.iosscp import SCPDeployer


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
    def rendered_config(self):
        return self._rendered_config

    @rendered_config.setter
    def rendered_config(self, value):
        self._rendered_config = value

    @property
    def rendered_rules(self):
        return self._rendered_rules

    @property
    def rendered_groups(self):
        return self._rendered_groups

    @property
    def hostgroups(self):
        return self._hostgroups

    @property
    def portgroups(self):
        return self._portgroups

    @property
    def rules(self):
        return self._rules

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

        if self._vendor == 'junos':
            renderer = JunosRenderer(self)
            renderer.render()

        if self._vendor == 'ios':
            renderer = IOSRenderer(self)
            renderer.render()

    def render_to_file_and_deploy(self):
        self.render()

        if self._vendor == 'junos':
            deployer = JunosDeployer(self)
            deployer.render_to_file_and_deploy()

        if self._vendor == 'ios':
            #deployer = IOSDeployer(self)
            deployer = SCPDeployer(self)
            deployer.render_to_file_and_deploy()

    def print_rendered_config(self):
        print self._rendered_config

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

    def resolve_portgroup(self, pgname):
        pg = PortGroup(pgname)
        pg.parse_file()
        if pg not in self._portgroups:
            self._portgroups.append(pg)

    def resolve_portgroups(self, ruleset):
        for rule in ruleset.tcp_rules:
            if type(rule.srcport) == str and rule.srcport_is_group:
                self.resolve_portgroup(str(rule.srcport)[1:])

            if type(rule.dstport) == str and rule.dstport_is_group:
                self.resolve_portgroup(str(rule.dstport)[1:])
