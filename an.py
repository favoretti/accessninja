#!/usr/bin/env python
"""Access Ninja.

Usage:
  an.py compile <device>|all
  an.py deploy <device>|all

Options:
  -h --help     Show this screen.
"""
import os

from docopt import docopt
from os import listdir
from os.path import isfile, join

from accessninja.config import Config
from accessninja.device import Device

def main(args):
    config = Config()

    if args['<device>'] == 'all':
        devicefiles = [f for f in listdir(config.devices) if isfile(join(config.devices, f)) and 'ignore' not in f]
    else:
        devicefiles = [f for f in listdir(config.devices) if isfile(join(config.devices, f)) and 'ignore' not in f and args['<device>'] in f]

    if not len(devicefiles):
        print('Could not process device {}, is it ignored?'.format(args['<device>']))
        os.exit(1)

    for device in devicefiles:
        try:
            f = open('{}/{}'.format(config.devices, device))
        except Exception, e:
            print("wheee", e)

        device_object = Device()
        device_object.name = device
        lines = f.readlines()

        for line in lines:
            if line.startswith('#'):
                continue
            if line.strip().startswith('vendor'):
                device_object.vendor = line.strip().split(' ')[1]
            if line.strip().startswith('transport'):
                device_object.transport = line.strip().split(' ')[1]
            if line.strip().startswith('save_config'):
                device_object.save_config = line.strip().split(' ')[1]
            if line.strip().startswith('include'):
                device_object.add_include(line.strip().split(' ')[1])

        if device_object.vendor != 'junos':
            print('Skipping {}, unsupported vendor: {}'.format(device_object.name, device_object.vendor))
        else:
            device_object.render()

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Access Ninja 0.1')
    if arguments is not None:
        main(arguments)
