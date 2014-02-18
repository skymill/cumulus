""" Functions for calculating the teminal size """
import os
import shlex
import struct
import platform
import subprocess


def get_terminal_size():
    """ Get the current terminal size """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        print "default"
        tuple_xy = (80, 25)      # default value
    return tuple_xy


def _get_terminal_size_windows():
    """ Get the terminal size on Windows """
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        handle = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(handle, csbi)
        if res:
            (_, _, _, _, _,
             left, top, right, bottom,
             _, _) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass


def _get_terminal_size_tput():
    """ Fallback function for Windows """
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass


def _get_terminal_size_linux():
    """ Get the terminal size in Linux / Darwin """
    def ioctl_GWINSZ(fdd):
        """ Undocumented """
        try:
            import fcntl
            import termios
            crd = struct.unpack(
                'hh',
                fcntl.ioctl(fdd, termios.TIOCGWINSZ, '1234'))
            return crd
        except:
            pass
    crd = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not crd:
        try:
            fdd = os.open(os.ctermid(), os.O_RDONLY)
            crd = ioctl_GWINSZ(fdd)
            os.close(fdd)
        except:
            pass
    if not crd:
        try:
            crd = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(crd[1]), int(crd[0])
