from ipaddr import IPNetwork

class Rule(object):

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

    @property
    def policy(self):
        return self._policy

    @policy.setter
    def policy(self, value):
        if not value in ['allow', 'deny']: raise Exception("policy should be either 'allow' or 'deny'")
        self._policy = value

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        if not value in ['tcp', 'udp', 'tcpudp', 'any']: raise Exception("protocol must be either 'tcp', 'udp', 'tcpudp' or 'any'")
        self._protocol = value

    @property
    def src(self):
        return self._src

    @src.setter
    def src(self, value):
        if value is None:
            return
        # TODO IP validation
        value = value.split(' ')[1].lstrip().rstrip()
        self._src = value

    @property
    def srcport(self):
        return self._srcport

    @srcport.setter
    def srcport(self, value):
        if value is None:
            return
        # TODO IP validation
        value = value.split(' ')[1].lstrip().rstrip()
        self._srcport = value

    @property
    def dst(self):
        return self._dst

    @dst.setter
    def dst(self, value):
        if value is None:
            return
        # TODO IP validation
        value = value.split(' ')[1].lstrip().rstrip()
        self._dst = value

    @property
    def dstport(self):
        return self._dstport

    @dstport.setter
    def dstport(self, value):
        if value is None:
            return
        # TODO IP validation
        value = value.split(' ')[1].lstrip().rstrip()
        self._dstport = value

    def __str__(self):
        return "RULE: {} {} {} {} {} {}".format(self._policy, self._protocol, self._src, self._srcport, self._dst, self._dstport)

    def __repr__(self):
        return "Ruleset"
