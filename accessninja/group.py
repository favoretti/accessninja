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

            for line in lines:
                if line.startswith('#'):
                    continue
                if line.startswith('@'):
                    rec_group = line.split(' ')[0][1:].replace('\n', '')
                    self.parseFile(rec_group)
                    continue
                if line.strip():
                    prefix = line.split('#')[0].strip()
                    print prefix
        except Exception, e:
            print e

class PortGroup(object):

    def __init__(self):
        self._name = None
        self._ports = list()


if __name__ == '__main__':
    hg = HostGroup()
    hg.parseFile(sys.argv[1])
