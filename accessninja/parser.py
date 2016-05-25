#!/usr/bin/env python
import re
import sys
from rule import Rule, ICMPRule

line = { 'policy': 'allow/deny',
         'protocol': 'tcp/udp/any',
         'src': 'prefix/$ip/any/@hostgroup/any',
         'srcport': 'pnumber/range/@portgroup/any',
         'dst': 'prefix/$ip/any/@hostgroup/any',
         'dstport': 'pnumber/range/@portgroup/any',
         'stateful': 'True/False',
         'expire': 'date, internal to parsing, skip generation if past',
         'log': 'True/False'
}

def parseLine(line):
    m = re.search("^(allow|deny)?\s+(tcp|udp|tcpudp|any)\s+?(?:src\s(\S+))\s*(?:port\s+(\S+))?\s*(?:dst\s(\S+))\s?(?:port\s+(\S+))?(?=(?:.*(stateful))?)(?=(?:.*expire (\d{8}))?)(?=(?:.*(log))?)", line)
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
    elif m is None:
        m = re.search("^(allow|deny)?\s+(icmp)\s+(?:(?:type\s)?(\S+|any))\s+(?:src\s(\S+))\s+(?:dst\s(\S+))(?=(?:.*expire (\d{8}))?)(?=(?:.*(log))?)", line)
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
            print "NO MATCH: {}".format(line)



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
