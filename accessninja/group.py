#!/usr/bin/env python
import sys

from config import Config
from inspect import currentframe, getframeinfo

from ipaddr import IPNetwork

class HostGroup(object):

    @property
    def name(self):
        return self._name


    @property
    def has_inline_groups(self):
        return len(self._inline_hostgroups)


    @property
    def inline_groups(self):
        return self._inline_hostgroups

    @name.setter
    def name(self, value):
        self._name = value

    def __init__(self, groupname):
        self.config = Config()
        self._prefixes = list()
        self._inline_hostgroups = list()
        self.name = groupname


    def __eq__(self, other):
        if self.name == other.name:
            return True

    def __repr__(self):
        return self.name


    def print_stats(self):
        print('\tHostgroup {} contains {} prefixes'.format(self.name, len(self._prefixes)))

    def parseFile(self, rec_name=None):
        try:
            if rec_name:
                f = open('{}/{}.hosts'.format(self.config.objects, rec_name))
            else:
                f = open('{}/{}.hosts'.format(self.config.objects, self.name))
            lines = f.readlines()

            for line in lines:
                if line.startswith('#'):
                    continue
                if line.startswith('@'):
                    rec_group = line.split(' ')[0][1:].replace('\n', '')
                    inline_hg = HostGroup(rec_group)
                    inline_hg.parseFile()
                    self._inline_hostgroups.append(inline_hg)
                    prefix = line.split('#')[0].strip()
                    self._prefixes.append(prefix)
                    continue
                if line.strip():
                    prefix = line.split('#')[0].strip()
                    self._prefixes.append(prefix)
        except Exception, e:
            frameinfo = getframeinfo(currentframe())
            print frameinfo.filename, frameinfo.lineno, e

    def hosts(self):
        return self._prefixes


    def render_junos(self):
        config = ''
        for prefix in self._prefixes:
            if prefix.startswith('@'):
                config = '{}\nset policy-options prefix-list {} apply-groups {}'.format(config, self.name, prefix)
            else:
                config = '{}\nset policy-options prefix-list {} {}'.format(config, self.name, prefix)
        return config

class PortGroup(object):

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def __init__(self, groupname):
        self.config = Config()
        self.name = None
        self._ports = list()
        self.name = groupname

    def parseFile(self, rec_name=None):
        try:
            if rec_name:
                f = open('{}/{}.ports'.format(self.config.objects, rec_name))
            else:
                f = open('{}/{}.ports'.format(self.config.objects, self.name))

            lines = f.readlines()

            for line in lines:
                if line.startswith('#'):
                    continue
                if line.startswith('@'):
                    rec_group = line.split(' ')[0][1:].replace('\n', '')
                    self.parseFile(rec_group)
                    continue
                if line.strip():
                    port = line.split('#')[0].strip()
                    self._ports.append(port)
        except Exception, e:
            print e


    def ports(self):
        return self._ports

if __name__ == '__main__':
    hg = HostGroup('qa')
    hg.parseFile()
    print hg.hosts()
    print hg.render_junos()
    pg = PortGroup('hadoop_mn_services')
    pg.parseFile()
    print pg.ports()
