#!/usr/bin/env python
import sys

from os.path import join

from config import Config
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
        for rule in self._rules:
            rule.print_stats()


    def render(self):
        print('Rendering {}'.format(self._name))
        for include in self._include_list:
            parsed_ruleset = Parser()
            parsed_ruleset.parseFile(join(self._config.policies, include))
            self._rules.append(parsed_ruleset)

        self.print_stats()

