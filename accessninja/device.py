#!/usr/bin/env python
import sys

from os.path import join

from config import Config
from group import HostGroup, PortGroup
from parser import Parser

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


    @property
    def vendor(self):
        return self._vendor

    @vendor.setter
    def vendor(self, value):
        if not value in ['junos', 'ios', 'arista', 'asa']: raise Exception("The only vendors currently supported are junos, arista, ios, asa")
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
        if not value in ['ssh']: raise Exception("The only transport supported currently is ssh")
        self._transport = value

    @property
    def save_config(self):
        return self._save_config

    @save_config.setter
    def save_config(self, value):
        self._save_config = value


    def add_include(self, value):
        self._include_list.append(value)


    def print_stats(self):
        for hg in self._hostgroups:
            hg.print_stats()
        for rule in self._rules:
            rule.print_stats()


    def render(self):
        print('Rendering {}'.format(self._name))
        for include in self._include_list:
            parsed_ruleset = Parser()
            parsed_ruleset.parseFile(join(self._config.policies, include))
            self._rules.append(parsed_ruleset)

        for ruleset in self._rules:
            self.resolve_hostgroups(ruleset)
            #self.resolve_portgroups()

        #self.print_stats()

        print(self.render_junos_hostgroups())
        #self.render_junos_rules()



    def afi_match(host):
        if host == "any":
            return True
        elif IPNetwork(host).version == afi:
            return True
        else:
            return False


    def render_junos(self, ruleset, afi):
        pass


    def render_junos_hostgroups(self):
        config_blob = []
        for hg in self._hostgroups:
            config_blob.append(hg.render_junos())

        return '\n'.join(config_blob)

    def resolve_hostgroup(self, hgname):
        hg = HostGroup(hgname)
        hg.parseFile()
        if hg.has_inline_groups:
            for ihg in hg.inline_groups:
                if ihg not in self._hostgroups:
                    self._hostgroups.append(ihg)
        if hg not in self._hostgroups:
            self._hostgroups.append(hg)

    def resolve_hostgroups(self, ruleset):
        for rule in ruleset.tcp_rules:
            if type(rule.src) == str and rule.src.startswith('@'):
                self.resolve_hostgroup(str(rule.src)[1:])

            if type(rule.dst) == str and rule.dst.startswith('@'):
                self.resolve_hostgroup(str(rule.dst)[1:])
