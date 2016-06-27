#!/usr/bin/env python
from config import Config
from ipaddr import IPNetwork
import sys

class HostGroup(object):

    def __init__(self, groupname):
        self.config = Config()
        self._name = None
        self._prefixes = list()
        self._name = groupname

    def parseFile(self, rec_name=None):
        try:
            if rec_name:
                f = open('{}/{}.hosts'.format(self.config.objects, rec_name))
            else:
                f = open('{}/{}.hosts'.format(self.config.objects, self._name))
            lines = f.readlines()

            for line in lines:
                if line.startswith('#'):
                    continue
                if line.startswith('@'):
                    rec_group = line.split(' ')[0][1:].replace('\n', '')
                    self.parseFile(rec_group)
                    continue
                if line.strip():
                    prefix = line.split('#')[0].strip()
                    self._prefixes.append(prefix)
        except Exception, e:
            print e

    def hosts(self):
        return self._prefixes


    def render_junos(self):
        config = ''
        for prefix in self._prefixes:
            config = '{}\nset policy-options prefix-list {} {}'.format(config, self._name, prefix)
        return config

class PortGroup(object):

    def __init__(self, groupname):
        self.config = Config()
        self._name = None
        self._ports = list()
        self._name = groupname

    def parseFile(self, rec_name=None):
        try:
            if rec_name:
                f = open('{}/{}.ports'.format(self.config.objects, rec_name))
            else:
                f = open('{}/{}.ports'.format(self.config.objects, self._name))

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
