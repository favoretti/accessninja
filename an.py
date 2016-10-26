#!/usr/bin/env python
"""Access Ninja.

Usage:
  an.py compile <device>|all
  an.py deploy <device>|all

Options:
  -h --help     Show this screen.
"""
import sys

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
            thread.daemon = True  # Daemonize thread
            thread.start()
            # device_object.render_to_file_and_deploy()


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Access Ninja 0.1')
    if arguments is not None:
        main(arguments)
