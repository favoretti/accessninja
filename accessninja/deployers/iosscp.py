import netrc
import sys
import time
from tempfile import NamedTemporaryFile

import paramiko
from Exscript.protocols import SSH2, Account
from Exscript.protocols import Exception
from Exscript.util.interact import read_login
from scp import SCPClient
from paramiko import SSHClient

class SCPDeployer(object):
    def __init__(self, device):
        self._device = device

    def render_to_file_and_deploy(self):
        username = ''
        password = ''
        try:
            username, acc, password = \
                netrc.netrc().authenticators(self._device.name)
            account = Account(name=username, password=password, key=None)
        except Exception, e:
            print e
            print("ERROR: could not find device in ~/.netrc file")
            print("HINT: either update .netrc or enter username + pass now.")
            try:
                account = read_login()
            except EOFError:
                print("ERROR: could not find proper username + pass")
                print("HINT: set username & pass in ~/.netrc for device %s"
                      % self._device.name)
                sys.exit(2)

        def s(local_conn, line):
            # print("   %s" % line)
            local_conn.execute(line)


	def progress(filename, size, sent):
	    print filename + " " + str(size) + " " + str(sent)

	def connect_ssh(server, port, user, password):
	    client = paramiko.SSHClient()
	    client.load_system_host_keys()
	    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	    client.connect(server, port, user, password, look_for_keys=False)
	    return client


        f = NamedTemporaryFile(delete=False)
        print('[{}] Stored temporary config at {}'.format(self._device.name, f.name))
        f.write(self._device.rendered_config)
        f.flush()
	#paramiko.common.logging.basicConfig(level=paramiko.common.DEBUG)
	
	src_file = f.name
	dst_file = "nvram:running-config"

	ssh = connect_ssh(self._device.name, 22, username, password)
	scp = SCPClient(ssh.get_transport())
        print('[{}] dumping ACLs to running-config'.format(self._device.name))
	scp.put(src_file, dst_file)
	scp.close()

        if self._device.transport == 'ssh':
            conn = SSH2(verify_fingerprint=False, debug=0, timeout=30)
        else:
            print("ERROR: Unknown transport mechanism: {}".format(self._device.transport))
            sys.exit(2)

        conn.set_driver('ios')
        conn.connect(self._device.name)
        conn.login(account)

        conn.execute('term len 0'.format(dst_file))
        conn.execute('term width 0'.format(dst_file))
        conn.execute('copy {} running-config\r'.format(dst_file))
        print('[{}] Done.'.format(self._device.name))
	ssh.close()
        f.close()
