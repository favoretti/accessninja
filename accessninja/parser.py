#!/usr/bin/env python
import re
import sys

from config import Config
from rule import TCPRule, ICMPRule

class Parser(object):


    @property
    def tcp_rules(self):
        return self._tcp_rules

    @property
    def icmp_rules(self):
        return self._icmp_rules

    def __init__(self):
        self._name = None
        self._config = Config()
        self._tcp_rules = list()
        self._icmp_rules = list()

    def parseLine(self, line):
        #
        # < allow | deny > \
        # < tcp | udp | any > \
        # src < prefix | $ip | @hostgroup | any > [ port number | range | @portgroup | any ] \
        # dst < prefix | $ip | @hostgroup | any > [ port number | range | @portgroup | any ] \
        # [ stateful ] \
        # [ expire YYYYMMDD ] [ log ] \
        # [ # comment ]
        #

        m = re.search(
                "^(allow|deny)"                        # match policy
                "\s+"                                  # match space
                "(tcp|udp|tcpudp|any)"                 # match protocol
                "\s+"                                  # match space
                "(?:src\s*(\S+))\s*(?:port\s+(\S+))?"  # match 'src <value>'
                "\s+"                                  # match space
                "(?:dst\s*(\S+))\s*(?:port\s+(\S+))?"  # match 'dst <value>'
                "(?=(?:.*(stateful))?)"                # match optional 'stateful'
                "(?=(?:.*expire (\d{8}))?)"            # match optional 'expire <value>'
                "(?=(?:.*(log))?)", line)              # match optional 'log'

        if m is not None:
            rule = TCPRule()
            rule.policy = m.group(1)
            rule.protocol = m.group(2)
            rule.src = m.group(3)
            rule.srcport = m.group(4)
            rule.dst = m.group(5)
            rule.dstport = m.group(6)
            rule.stateful = m.group(7)
            rule.expire = m.group(8)
            rule.log = m.group(9)
            if not rule in self._tcp_rules:
                self._tcp_rules.append(rule)

        if m is None:
            # We probably encountered an ICMP policy
            #
            # < allow | deny > < icmp > < any | type <code|any> > \
            # src < prefix | $ip | @hostgroup | any > \
            # dst < prefix | $ip | @hostgroup | any > \
            # [ expire YYYYMMDD ] [ log ] \
            # [ # comment ]
            #

            m = re.search(
                  "^(allow|deny)"                # match policy
                  "\s+"                          # match space
                  "(icmp)"                       # match protocol, only icmp
                  "\s+"                          # match space
                  "(?:(?:type\s)?(\S+|any))"     # match icmp type or 'any'
                  "\s+"                          # match space
                  "(?:src\s*(\S+))"              # match src
                  "\s+"                          # match space
                  "(?:dst\s*(\S+))"              # match dst
                  "(?=(?:.*expire (\d{8}))?)"    # match optional 'expire <value>'
                  "(?=(?:.*(log))?)", line)      # match optional 'log'

            if m is not None:
                rule = ICMPRule()
                rule.policy = m.group(1)
                rule.protocol = m.group(2)
                rule.icmptype = m.group(3)
                rule.src = m.group(4)
                rule.dst = m.group(5)
                rule.expire = m.group(6)
                rule.log = m.group(7)
                if not rule in self._icmp_rules:
                    self._icmp_rules.append(rule)
            else:
                raise Exception("Could not parse the line: {}".format(line))


    def parseFile(self, filename, update_name=True):
        if update_name:
            self._name = filename
        with open(filename) as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith('#'):
                continue
            if line.startswith('allow') or line.startswith('deny'):
                self.parseLine(line)
            if line.startswith('@'):
                self.parseFile('{}/{}'.format(self._config.policies, line[1:].strip()), False)


    def dump_tcp_rules(self):
        for rule in self._tcp_rules:
            print(rule)


    def dump_icmp_rules(self):
        for rule in self._icmp_rules:
            print(rule)


    def print_stats(self):
        print('\tRuleset {} contains:'.format(self._name))
        print('\t\t{} parsed TCP rules'.format(len(self._tcp_rules)))
        print('\t\t{} parsed ICMP rules'.format(len(self._icmp_rules)))

if __name__ == "__main__":
    parser = Parser()
    parser.parseFile(sys.argv[1])
    parser.dump_icmp_rules()
