""" Script execution module """
import logging
import os
import subprocess
import sys

if sys.platform in ['win32', 'cygwin']:
    import ntpath as ospath
else:
    import os.path as ospath

LOGGER = logging.getLogger('cumulus_bundle_handler')


def run_init_scripts(start=False, kill=False, other=False):
    """ Execute scripts in /etc/cumulus-init.d or C:\\cumulus\\init.d

    :type start: bool
    :param start: Run scripts starting with S
    :type kill: bool
    :param kill: Run scripts starting with K
    :type others: bool
    :param others: Run scripts not starting with S or K
    """
    init_dir = '/etc/cumulus-init.d'
    if sys.platform in ['win32', 'cygwin']:
        init_dir = 'C:\\cumulus\\init.d'

    # Run the post install scripts provided by the bundle
    if not ospath.exists(init_dir):
        LOGGER.info('No init scripts found in {}'.format(init_dir))
        return

    LOGGER.info('Running init scripts from {}'.format(init_dir))

    filenames = []
    for filename in sorted(os.listdir(init_dir)):
        if ospath.isfile(ospath.join(init_dir, filename)):
            filenames.append(ospath.join(init_dir, filename))

    if start:
        for filename in filenames:
            if ospath.basename(filename)[0] == 'S':
                _run_command(ospath.abspath(filename))

    if kill:
        for filename in filenames:
            if ospath.basename(filename)[0] == 'K':
                _run_command(ospath.abspath(filename))

    if other:
        for filename in filenames:
            if ospath.basename(filename)[0] not in ['K', 'S']:
                _run_command(ospath.abspath(filename))


def _run_command(command):
    """ Run arbitary command

    :type command: str
    :param command: Command to execute
    """
    LOGGER.info('Executing command: {}'.format(command))

    cmd = subprocess.Popen(
        command,
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE)

    stdout, stderr = cmd.communicate()
    if stdout:
        print(stdout)
    if stderr:
        print(stderr)

    if cmd.returncode != 0:
        LOGGER.error('Command "{}" returned non-zero exit code {}'.format(
            command,
            cmd.returncode))
        sys.exit(cmd.returncode)
