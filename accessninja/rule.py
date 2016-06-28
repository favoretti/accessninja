from ipaddr import IPNetwork


class TCPRule(object):

    def __init__(self):
        self._policy = None
        self._protocol = None
        self._src = None
        self._srcport = None
        self._dst = None
        self._dstport = None
        self._stateful = None
        self._expire = None
        self._log = None

    def __eq__(self, other):
        if self.policy == other.policy and\
                self.protocol == other.protocol and\
                self.src == other.src and\
                self.srcport == other.srcport and\
                self.dst == other.dst and\
                self.dstport == other.dstport and\
                self.stateful == other.stateful and\
                self.expire == other.expire and\
                self.log == other.log:
                    return True
        else:
            return False

    @property
    def policy(self):
        return self._policy

    @policy.setter
    def policy(self, value):
        if value not in ['allow', 'deny']:
            raise Exception("policy should be either 'allow' or 'deny'")
        self._policy = value

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        if value not in ['tcp', 'udp', 'tcpudp', 'any']:
            raise Exception("protocol must be either 'tcp', 'udp', 'tcpudp' or 'any'")
        self._protocol = value

    @property
    def src(self):
        return self._src if type(self._src) == str else self._src.with_netmask

    @src.setter
    def src(self, value):
        n = None
        if not value.startswith('@') and not value == 'any':
            try:
                n = IPNetwork(value)
            except ValueError, e:
                raise Exception(e)
        self._src = (value if n is None else n)

    @property
    def src_is_group(self):
        return self.src and self.src.startswith('@')

    @property
    def src_is_any(self):
        return self.src == 'any'

    @property
    def srcport(self):
        return self._srcport

    @srcport.setter
    def srcport(self, value):
        self._srcport = value

    @property
    def srcport_is_group(self):
        return self.srcport and self.srcport.startswith('@')

    @property
    def srcport_is_any(self):
        return self.srcport == 'any'

    @property
    def dst(self):
        return self._dst if type(self._dst) == str else self._dst.with_netmask

    @dst.setter
    def dst(self, value):
        n = None
        if not value.startswith('@') and not value == 'any':
            try:
                n = IPNetwork(value)
            except ValueError, e:
                raise Exception(e)
        self._dst = (value if n is None else n)

    @property
    def dst_is_group(self):
        return self.dst and self.dst.startswith('@')

    @property
    def dst_is_any(self):
        return self.dst == 'any'

    @property
    def dstport(self):
        return self._dstport

    @dstport.setter
    def dstport(self, value):
        self._dstport = value

    @property
    def dstport_is_group(self):
        return self.dstport and self.dstport.startswith('@')

    @property
    def dstport_is_any(self):
        return self.dstport == 'any'

    @property
    def stateful(self):
        return self._stateful

    @stateful.setter
    def stateful(self, value):
        self._stateful = value

    @property
    def expire(self):
        return self._expire

    @expire.setter
    def expire(self, value):
        self._expire = value

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, value):
        self._log = value

    @staticmethod
    def format_port_range(port):
        if port.startswith('-'):
            fport = '0{}'.format(port)
        elif port.endswith('-'):
            fport = '{}65535'.format(port)
        else:
            fport = port

        return fport

    def render_port_list(self, portlist, direction):
        config_blob = ''
        for port in portlist:
            config_blob = '{}{}-port {} '.format(config_blob, direction, self.format_port_range(port))

        return config_blob

    def render_junos(self, portgroups):
        config_blob = list()
        if self.protocol != 'any' and self.protocol != 'tcpudp':
            config_blob.append('set from protocol {}'.format(self.protocol))

        if self.protocol == 'tcpudp':
            config_blob.append('set from protocol tcp from protocol udp')

        if self.src and not self.src_is_any:
            if self.src_is_group:
                config_blob.append('set from source-prefix-list {}'.format(str(self.src)[1:]))
            else:
                config_blob.append('set from source-address {}'.format(self.src))

        if self.srcport and not self.srcport_is_any:
            if self.srcport_is_group:
                gname = str(self.srcport)[1:]
                group = next((g for g in portgroups if g.name == gname), None)
                ports = self.render_port_list(group.ports, 'source')
                config_blob.append('set from {}'.format(ports))
            else:
                config_blob.append('set from source-port {}'.format(self.format_port_range(self.srcport)))

        if self.dst and not self.dst_is_any:
            if self.dst_is_group:
                config_blob.append('set from destination-prefix-list {}'.format(str(self.dst)[1:]))
            else:
                config_blob.append('set from destination-address {}'.format(self.dst))

        if self.dstport and not self.dstport_is_any:
            if self.dstport_is_group:
                gname = str(self.dstport)[1:]
                group = next((g for g in portgroups if g.name == gname), None)
                ports = self.render_port_list(group.ports, 'destination')
                config_blob.append('set from {}'.format(ports))
            else:
                config_blob.append('set from destination-port {}'.format(self.format_port_range(self.dstport)))

        if self.log:
            config_blob.append('then syslog')

        if self.policy == 'allow':
            config_blob.append('then accept')
        else:
            config_blob.append('then discard')

        return '\n'.join(config_blob)

    def __str__(self):
        return "RULE: POL:{} PROTO:{} SRC:{} PORT:{} "\
            "DST:{} PORT:{} STATE:{} EXPIRE:{} LOG:{}".format(self._policy,
                                                              self._protocol,
                                                              self._src if type(self._src) == str
                                                              else self._src.with_netmask,
                                                              self._srcport,
                                                              self._dst if type(self._dst) == str
                                                              else self._dst.with_netmask,
                                                              self._dstport,
                                                              self._stateful,
                                                              self._expire,
                                                              self._log)

    def __repr__(self):
        return "Ruleset"


class ICMPRule(object):

    def __init__(self):
        self._policy = None
        self._protocol = None
        self._icmptype = None
        self._src = None
        self._dst = None
        self._expire = None
        self._log = None

    def __eq__(self, other):
        if self.policy == other.policy and\
                self.protocol == other.protocol and\
                self.icmptype == other.icmptype and\
                self.src == other.src and\
                self.dst == other.dst and\
                self.expire == other.expire and\
                self.log == other.log:
                    return True
        else:
            return False

    @property
    def policy(self):
        return self._policy

    @policy.setter
    def policy(self, value):
        if value not in ['allow', 'deny']:
            raise Exception("policy should be either 'allow' or 'deny'")
        self._policy = value

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        if value not in ['icmp']:
            raise Exception("protocol must be 'icmp'")
        self._protocol = value

    @property
    def icmptype(self):
        return self._icmptype

    @icmptype.setter
    def icmptype(self, value):
        self._icmptype = value

    @property
    def src(self):
        return self._src if type(self._src) == str else self._src.with_netmask

    @src.setter
    def src(self, value):
        n = None
        if not value.startswith('@') and not value == 'any':
            try:
                n = IPNetwork(value)
            except ValueError, e:
                raise Exception(e)
        self._src = (value if n is None else n)

    @property
    def src_is_group(self):
        return self.src.startswith('@')

    @property
    def src_is_any(self):
        return self.src == 'any'

    @property
    def dst(self):
        return self._dst if type(self._dst) == str else self._dst.with_netmask

    @property
    def dst_is_group(self):
        return self.dst.startswith('@')

    @property
    def dst_is_any(self):
        return self.dst == 'any'

    @dst.setter
    def dst(self, value):
        n = None
        if not value.startswith('@') and not value == 'any':
            try:
                n = IPNetwork(value)
            except ValueError, e:
                raise Exception(e)
        self._dst = (value if n is None else n)

    @property
    def expire(self):
        return self._expire

    @expire.setter
    def expire(self, value):
        self._expire = value

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, value):
        self._log = value

    def render_junos(self):
        config_blob = list()
        config_blob.append('set from protocol icmp')
        if not self.src_is_any:
            if self.src_is_group:
                config_blob.append('set from source-prefix-list {}'.format(str(self.src)[1:]))
            else:
                config_blob.append('set from source-address {}'.format(self.src))

        if not self.dst_is_any:
            if self.dst_is_group:
                config_blob.append('set from destination-prefix-list {}'.format(str(self.dst)[1:]))
            else:
                config_blob.append('set from destination-address {}'.format(self.dst))

        if self.log:
            config_blob.append('then syslog')

        if self.policy == 'allow':
            config_blob.append('then accept')
        else:
            config_blob.append('then discard')

        return '\n'.join(config_blob)

    def __str__(self):
        return "ICMP RULE: POL:{} PROTO:{} " \
            "TYPE: {} SRC:{} DST:{} EXPIRE:{} LOG:{}".format(self._policy,
                                                             self._protocol,
                                                             self._icmptype,
                                                             (self._src if type(self._src) == str
                                                                 else self._src.with_netmask),
                                                             (self._dst if type(self._dst) == str
                                                                 else self._dst.with_netmask),
                                                             self._expire,
                                                             self._log)

    def __repr__(self):
        return "Ruleset"
