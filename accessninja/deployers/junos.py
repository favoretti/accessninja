import netrc
import sys
import time
from tempfile import NamedTemporaryFile

import paramiko
from Exscript.protocols import SSH2, Account
from Exscript.util.interact import read_login


class JunosDeployer(object):
    def __init__(self, device):
        self._device = device

    def render_to_file_and_deploy(self):
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
            print("   %s" % line)
            local_conn.execute(line)

        f = NamedTemporaryFile(delete=False)
        print('Stored temporary config at {}'.format(f.name))
        f.write(self._device.rendered_config)
        f.flush()

        tr = paramiko.Transport((self._device.name, 22))
        tr.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(tr)
        try:
            sftp.remove(f.name)
        except IOError, e:
            if e.errno != 2:
                print "Something wrong while uploading"
                sys.exit(1)

        upload_filename = "/root/config-{}".format(time.strftime("%d-%m-%Y-%H-%M-%S"))
        print 'Uploading as file: {}'.format(upload_filename)
        sftp.put(f.name, upload_filename)
        sftp.close()

        tr.close()
        f.close()

        print('Config uploaded as {}'.format(upload_filename))

        if self._device.transport == 'ssh':
            conn = SSH2(verify_fingerprint=False, debug=1, timeout=360)
        else:
            print("ERROR: Unknown transport mechanism: {}".format(self._device.transport))
            sys.exit(2)

        print('Logging in to apply the config')
        conn.set_driver('junos')
        conn.connect(self._device.name)
        conn.login(account)

        conn.execute('cli')
        conn.execute('set cli screen-length 10000')
        conn.execute('edit')
        s(conn, 'load set {}'.format(upload_filename))
        print('Set loadded, commiting')
        s(conn, 'commit')
        print('Commited')
        s(conn, 'exit')
        s(conn, 'exit')
        print('Removing file {}'.format(upload_filename))
        s(conn, 'rm {}'.format(upload_filename))
        print('Done.')
