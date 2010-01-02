import os


class SSHConnection(object):

    compress_data = False
    forward_agent = False
    ssh_key = None
    hard_failure = True

    _default_args = ['-x', '-o', 'BatchMode=yes',
                     '-o', 'StrictHostKeyChecking=no']

    def __init__(self, host="localhost", user=None, port=22):
        self.host = host
        self.port = port
        self.user = user if user else os.environ['USER']

    def _shell_escape(self, string):
        for char in ('"', '$', '`'):
            string = string.replace(char, '\{0}'.format(char))

        return string

    def _build_command(self, command):
        args = self._default_args[:]
        args.insert(0, 'ssh')

        args.extend(['-p', self.port])
        args.extend(['-l', self.user])
        args.append('-A' if self.forward_agent else '-a')

        if self.compress_data:
            args.append('-C')

        if self.ssh_key:
            args.extend(['-i', self.ssh_key])

        return args

    def run(self, command, *args):
        pass


class CommandHandler(object):

    def __init__(self, connection, logger=None):
        self.connection = connection

    def symlink(self, from_, to_):
        pass

    def make_directory(self, dirname, parent=False):
        pass

    def touch_file(self, filename):
        pass

    def send_files(self, from_, to_):
        pass

    def copy_files(self, from_, to_):
        pass

    def remove(self, filename):
        pass

    def list_directory(self, directory):
        pass

    def run_command(self, command, *args):
        pass

    def start_daemon(self, command, *args):
        pass

    def read_file(self, filename):
        pass

    def write_file(self, filename, contents):
        pass

    def stat(self, filename):
        pass
