#!/usr/bin/env python
from config import Config
from ipaddr import IPNetwork
import sys

class HostGroup(object):

    def __init__(self):
        self.config = Config()
        self._name = None
        self._prefixes = list()

    def parseFile(self, groupname):
        try:
            f = open('{}/{}.hosts'.format(self.config.objects, groupname))
            lines = f.readlines()
            self._name = groupname

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

class PortGroup(object):

    def __init__(self):
        self.config = Config()
        self._name = None
        self._ports = list()

    def parseFile(self, groupname):
        try:
            f = open('{}/{}.ports'.format(self.config.objects, groupname))
            lines = f.readlines()
            self._name = groupname

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
    hg = HostGroup()
    hg.parseFile('qa')
    print hg.hosts()
    pg = PortGroup()
    pg.parseFile('hadoop_mn_services')
    print pg.ports()
