#!/usr/bin/env python
from config import Config
from inspect import currentframe, getframeinfo
from netaddr import IPNetwork


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

    @property
    def hosts(self):
        return self._prefixes

    def __init__(self, groupname):
        self.config = Config()
        self._prefixes = list()
        self._inline_hostgroups = list()
        self._name = groupname

    def __eq__(self, other):
        if self.name == other.name:
            return True

    def __repr__(self):
        return self.name

    def print_stats(self):
        print('\tHostgroup {} contains {} prefixes'.format(self.name, len(self._prefixes)))

    def parse_file(self, rec_name=None):
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
                    rec_group = line.split(' ')[0][1:].strip()
                    inline_hg = HostGroup(rec_group)
                    inline_hg.parse_file()
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
            raise e

    def render_junos(self):
        config = 'delete policy-options prefix-list {}'.format(self.name)
        for prefix in self._prefixes:
            if prefix.startswith('@'):
                for ihg in self._inline_hostgroups:
                    if ihg.name == prefix[1:]:
                        config = '{}\ndelete groups {}'.format(config, ihg.name)
                        for iprefix in ihg.hosts:
                            config = '{}\nset groups {} policy-options prefix-list {} {}'.format(config,
                                                                                                 ihg.name,
                                                                                                 ihg.name,
                                                                                                 iprefix)
                config = '{}\nset policy-options prefix-list {} apply-groups {}'.format(config, self.name, prefix[1:])
            else:
                config = '{}\nset policy-options prefix-list {} {}'.format(config, self.name, prefix)
        return config

    def render_ios(self, subgroup=False):
        config = ''
        if not subgroup:
            config = 'no object-group ip address {}\n'.format(self.name)
            config += 'object-group ip address {}'.format(self.name)
        for prefix in self._prefixes:
            if prefix.startswith('@'):
                ihg = [g for g in self._inline_hostgroups if g.name == prefix[1:]][0]
                config += ihg.render_ios(True)
            else:
                ipn = IPNetwork(prefix)
                if ipn.prefixlen == 32:
                    config = '{}\nhost {}'.format(config, ipn.ip)
                else:
                    config = '{}\n{} {}'.format(config, ipn.ip, ipn.netmask)
        if not subgroup:
            config += '\nexit'
        return config


class PortGroup(object):

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def ports(self):
        return self._ports

    def __init__(self, groupname):
        self.config = Config()
        self._ports = list()
        self._name = groupname

    def __eq__(self, other):
        return self.name == other.name

    def __repr__(self):
        return self.name

    def parse_file(self, rec_name=None):
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
                    rec_group = line.split(' ')[0][1:].strip()
                    self.parse_file(rec_group)
                    continue
                if line.strip():
                    port = line.split('#')[0].strip()
                    if port.startswith('-'):
                        port = '0-{}'.format(port)
                    if port.endswith('-'):
                        port = '{}65535'.format(port)
                    self._ports.append(port)
        except Exception, e:
            frameinfo = getframeinfo(currentframe())
            print frameinfo.filename, frameinfo.lineno, e
            raise e

    def render_ios(self):
        config = 'no object-group ip port {}\n'.format(self.name)
        config += 'object-group ip port {}\n'.format(self.name)
        for port in self.ports:
            if '-' in port:
                split = port.split('-')
                config += 'range {} {}\n'.format(split[0], split[1])
            else:
                config += 'eq {}\n'.format(port)
        config += 'exit'
        return config

if __name__ == '__main__':
    hg = HostGroup('qa')
    hg.parse_file()
    print hg.hosts
    print hg.render_junos()
    pg = PortGroup('web_services')
    pg.parse_file()
    print pg.ports
