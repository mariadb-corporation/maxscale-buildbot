import os
import subprocess
import sys
import paramiko
import select

MDBCI_VM_PATH = os.path.expanduser("~/vms/")


def setupMdbciEnvironment():
    """
    Methods modifies the environment, so the VM managed by the MDBCI will always be in `~/vms/` directory.

    Also adds the `~/mdbci/` to the executable search path. This method should be called before calling runMdbci
    """
    os.environ["MDBCI_VM_PATH"] = MDBCI_VM_PATH
    os.environ["PATH"] = os.environ["PATH"] + os.pathsep + os.path.expanduser('~/mdbci')


def runMdbci(*arguments):
    """
    Run MDBCI with the specified arguments. Put all output to standard output streams
    :param arguments: the list of strings to pass as arguments to MDBCI
    :return: exit code of the MDBCI
    """
    all_commands = ['mdbci']
    all_commands.extend(arguments)
    process = subprocess.run(
        all_commands, stdout=sys.stdout, stderr=sys.stderr
    )
    return process.returncode


def getMdbciInfo(*cmd):
    all_commands = ['mdbci', '--silent']
    all_commands.extend(cmd)
    process = subprocess.Popen(all_commands,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
    output, _ = process.communicate()
    return output.decode("utf-8").splitlines()[0]


def createRunner(connection):
    """Creates a function that is able to run commands on specific runner"""

    def runRemoteCommand(command, **kwargs):
        _, output, _ = connection.exec_command(command, **kwargs)
        return output.channel.recv_exit_status()

    return runRemoteCommand


def interactiveExec(connection, cmd, consumer, outfile, get_pty=False, timeout=1):
    con_stdin, con_stdout, con_stderr = connection.exec_command(cmd, get_pty=get_pty)
    channel = con_stdout.channel

    con_stdin.close()
    channel.shutdown_write()

    def send_converted_text():
        data = channel.recv(len(channel.in_buffer))
        text = data.decode("utf-8", "replace")
        if text != '':
            consumer(text, outfile)

    send_converted_text()  # Pass all text from read buffer
    while not channel.closed:
        read_ready_queue, _, _ = select.select([channel], [], [], timeout)
        for ready_channel in read_ready_queue:
            if ready_channel.recv_ready():  # Pass stdout to the consumer
                send_converted_text()
            if ready_channel.recv_stderr_ready():  # Pass stderr to the consumer
                send_converted_text()
        if channel.exit_status_ready() and not channel.recv_stderr_ready() and not channel.recv_ready():
            channel.shutdown_read()
            channel.close()
            break
    con_stdout.close()
    con_stderr.close()
    return channel.recv_exit_status()


def printAndSaveText(text, outfile):
    outfile.write(text)
    print(text, end="")


def repoServerPassRead(passFile):
    f = open(os.path.expanduser(passFile), 'r')
    repository_server_password = f.read().rstrip('\r\n')
    f.close()
    return repository_server_password


def createSSH(machine):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(machine.ip_address, username=machine.ssh_user, key_filename=machine.ssh_key)
    return ssh


class Machine:
    def __init__(self, configName, nodeName):
        fullName = configName + '/' + nodeName
        self.ip_address = getMdbciInfo('show', 'network', fullName)
        self.ssh_key = getMdbciInfo('show', 'keyfile', fullName)
        self.ssh_user = getMdbciInfo('ssh', '--command', 'whoami', fullName)
        self.box = getMdbciInfo('show', 'box', fullName)
        self.platform = getMdbciInfo('show', 'boxinfo', '--box-name={}'.format(self.box), '--field', 'platform',
                                     fullName)
        self.platform_version = getMdbciInfo('show', 'boxinfo', '--box-name={}'.format(self.box),
                                             '--field', 'platform_version', fullName)
