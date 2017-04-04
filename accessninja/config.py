#!/usr/bin/env python
import ConfigParser
import os


class Config(object):
    def __init__(self):

        config = ConfigParser.ConfigParser()
        config.read(os.path.expanduser('~/.accessninja/config'))

        if not config.has_section('general'):
            raise Exception('Config must contain section general with values for devices, '
                            'objects and policies containing paths')

        if not config.has_option('general', 'devices') or not config.has_option('general', 'objects') \
                or not config.has_option('general', 'policies') \
		or not config.has_option('general', 'groups'):
            raise Exception('Config must contain section general with values for devices, '
                            'objects, policies and groups containing paths')

        self.devices  = config.get('general', 'devices')
        self.objects  = config.get('general', 'objects')
        self.policies = config.get('general', 'policies')
        self.groups   = config.get('general', 'groups')

if __name__ == '__main__':
    c = Config()
