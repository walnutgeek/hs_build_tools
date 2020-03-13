import os
import shutil
import sys
import time
from logging import getLogger

pyenv = f"py{sys.version.split()[0]}"


SEC_DELAYS = [0.0, *(0.05 * (1.4 ** i) for i in range(3))]


def negate(fn):
    def nope(*args, **kwargs):
        return not fn(*args, **kwargs)

    return nope


def repeat_action_with_delays(test_fn, action_fn, *args):
    for delay in SEC_DELAYS:
        if test_fn(*args):
            action_fn(*args)
            time.sleep(delay)
        else:
            break


def ensure_dir(d):
    repeat_action_with_delays(negate(os.path.isdir), os.makedirs, d)


def ensure_no_dir(dir):
    repeat_action_with_delays(os.path.isdir, shutil.rmtree, dir)


class LogTestOut:
    """
    Get logger and initalize `./test-out/py3.x.x/test_name` directory.

    >>> log, out = LogTestOut.get(__name__)
    >>> log is not None
    True
    >>> isinstance(out, LogTestOut)
    True
    >>> dir = out.child_dir("home") # ensure child directory
    >>> os.path.isdir(dir)
    True
    >>> log, out = LogTestOut.get(__name__) # reinitialise and force cleanup
    >>> os.path.isdir(dir)
    False
    """

    def __init__(self, name, root):
        self.log = getLogger(name)
        if root is None:
            root = os.path.abspath("test-out")
        self.dir = os.path.join(root, pyenv, name)
        ensure_no_dir(self.dir)
        self.child_dirs = {}

    def child_dir(self, dir_name):
        if dir_name not in self.child_dirs:
            child = os.path.join(self.dir, dir_name)
            ensure_dir(child)
            self.child_dirs[dir_name] = child
        return self.child_dirs[dir_name]

    @classmethod
    def get(cls, name, root=None):
        out = cls(name, root)
        return out.log, out
