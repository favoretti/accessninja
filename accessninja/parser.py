#!/usr/bin/env python
import re
import sys
from rule import Rule, ICMPRule

def parseLine(line):
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
            "^(allow|deny)"                       # match policy
            "\s+"                                 # match space
            "(tcp|udp|tcpudp|any)"                # match protocol
            "\s+"                                 # match space
            "(?:src\s(\S+))\s*(?:port\s+(\S+))?"  # match 'src <value>'
            "\s+"                                 # match space
            "(?:dst\s(\S+))\s*(?:port\s+(\S+))?"  # match 'dst <value>'
            "(?=(?:.*(stateful))?)"               # match optional 'stateful'
            "(?=(?:.*expire (\d{8}))?)"           # match optional 'expire <value>'
            "(?=(?:.*(log))?)", line)             # match optional 'log'

    if m is not None:
        rule = Rule()
        rule.policy = m.group(1)
        rule.protocol = m.group(2)
        rule.src = m.group(3)
        rule.srcport = m.group(4)
        rule.dst = m.group(5)
        rule.dstport = m.group(6)
        rule.stateful = m.group(7)
        rule.expire = m.group(8)
        rule.log = m.group(9)
        print rule

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
              "^(allow|deny)"               # match policy
              "\s+"                         # match space
              "(icmp)"                      # match protocol, only icmp
              "\s+"                         # match space
              "(?:(?:type\s)?(\S+|any))"    # match icmp type or 'any'
              "\s+"                         # match space
              "(?:src\s(\S+))"              # match src
              "\s+"                         # match space
              "(?:dst\s(\S+))"              # match dst
              "(?=(?:.*expire (\d{8}))?)"   # match optional 'expire <value>'
              "(?=(?:.*(log))?)", line)     # match optional 'log'

        if m is not None:
            rule = ICMPRule()
            rule.policy = m.group(1)
            rule.protocol = m.group(2)
            rule.icmptype = m.group(3)
            rule.src = m.group(4)
            rule.dst = m.group(5)
            rule.expire = m.group(6)
            rule.log = m.group(7)
            print rule
        else:
            raise Exception("Could not parse the line: {}".format(line))


def parseFile(filename):
    with open(filename) as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith('#'):
            continue
        if line.startswith('allow') or line.startswith('deny'):
            parseLine(line)

if __name__ == "__main__":
    parseFile(sys.argv[1])
