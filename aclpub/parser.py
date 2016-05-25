#!/usr/bin/env python
import re
import sys
from rule import Rule

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

    m = re.search("^(allow|deny)?\s+(tcp|udp|tcpudp|any)\s+?(src\s\S+)\s*?(port\s+\S+)?\s*?(dst\s\S+)\s?(port\s+\S+)?\s*?(\S+)?\s*?(\S+)?", line)
    if m is not None:
        rule = Rule()
        rule.policy = m.group(1)
        rule.protocol = m.group(2)
        rule.src = m.group(3)
        rule.srcport = m.group(4)
        rule.dst = m.group(5)
        rule.dstport = m.group(6)
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
