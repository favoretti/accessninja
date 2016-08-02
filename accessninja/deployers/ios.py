import netrc
from tempfile import NamedTemporaryFile
from netmiko import ConnectHandler


class IOSDeployer(object):
    def __init__(self, device):
        self._device = device

    def render_to_file_and_deploy(self):
        username, acc, password = \
            netrc.netrc().authenticators(self._device.name)

        device_data = {
            'device_type': 'cisco_ios',
            'ip': self._device.name,
            'username': username,
            'password': password,
        }

        f = NamedTemporaryFile(delete=False)
        print('Stored temporary config at {}'.format(f.name))
        f.write(self._device.rendered_config)
        f.flush()

        net_connect = ConnectHandler(**device_data)
        output = net_connect.send_config_from_file(f.name)
        print(output)
        print('Config uploaded!')

        f.close()

        print('Done.')
