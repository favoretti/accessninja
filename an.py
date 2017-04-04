#!/usr/bin/env python
"""Access Ninja.

Usage:
  an.py compile <device>|all|groupname
  an.py deploy <device>|all|groupname

Options:
  -h --help     Show this screen.
"""
import sys
import threading

from docopt import docopt
from os import listdir
from os.path import isfile, join

from accessninja.config import Config
from accessninja.device import Device


def main(args):
    config = Config()
    groups_list = [f for f in listdir(config.groups) if isfile(join(config.groups, f)) and args['<device>'] in f and 'ignore' not in f]

    if args['<device>'] == 'all':
        print ('Rendering all devices')
        devicefiles = [f for f in listdir(config.devices) if isfile(join(config.devices, f)) and 'ignore' not in f]

    if args['<device>'] in groups_list:
        group_device = []
        devicefiles = []

        print ('Rendering devices in group: {}'.format(args['<device>']))
        with  open(config.groups + '/' + groups_list[0]) as group_device:
            for device in group_device:
               devicefiles.append(device.rstrip('\n'))
        print ('group devices: {}\n'.format(devicefiles))

    else:
        devicefiles = [f for f in listdir(config.devices) if isfile(join(config.devices, f)) and
                       'ignore' not in f and args['<device>'] in f]

    if not len(devicefiles):
        print('Could not process device {}, is it ignored?'.format(args['<device>']))
        sys.exit(1)

    if args['compile']:
        for device in devicefiles:
            device_object = Device()
            device_object.parse_file(device)

            if device_object.vendor not in ['junos', 'ios']:
                print('Skipping {}, unsupported vendor: {}'.format(device_object.name, device_object.vendor))
            else:
                device_object.render()
                device_object.print_rendered_config()

    if args['deploy']:
        for device in devicefiles:
            device_object = Device()
            device_object.parse_file(device)
            thread = threading.Thread(target=device_object.render_to_file_and_deploy, args=())
            thread.start()
            # device_object.render_to_file_and_deploy()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Access Ninja 0.1')
    if arguments is not None:
        main(arguments)
