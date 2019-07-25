import os
import shutil
import sys
import time
from logging import getLogger

pyenv = f"py{sys.version.split()[0]}"


def ensure_dir(d):
    if not os.path.isdir(d):
        os.makedirs(d)


def ensure_no_dir(dir):
    if os.path.isdir(dir):
        shutil.rmtree(dir)
        for i in range(6):
            time.sleep(1e-3 * (1 << i))
            if os.path.isdir(dir):
                shutil.rmtree(dir)
            else:
                break


class LogTestOut:
    """
    Get logger and initalize `./test-out/py3.x.x/test_name` directory.

    >>> log, out = LogTestOut.get(__name__)
    >>> log is not None
    True
    >>> isinstance(out, LogTestOut)
    True
    >>> dir = out.child_dir("home")
    >>> os.path.isdir(dir)
    True
    >>> log, out = LogTestOut.get(__name__) # force cleanup
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
