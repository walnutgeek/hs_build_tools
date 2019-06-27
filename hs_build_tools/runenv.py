import locale
from os.path import exists, sep
from subprocess import check_call, check_output
from venv import EnvBuilder

from setuptools import Command


class RunEnv(Command):
    description = f"""
            Build runtime venv for given project 
            and install it there.
            """
    DEFAULT_DIR = f".{sep}.runenv"

    user_options = [
        ("dir=", None, f"where to create runenv, default is: {DEFAULT_DIR}")
    ]

    def initialize_options(self):
        self.dir = self.DEFAULT_DIR

    def finalize_options(self):
        pass

    def run(self):
        """
        Execute command. Create runenv and install dependencies
        """
        if not exists("setup.py"):
            raise ValueError(f"Has to be run from root of the project")
        builder = EnvBuilder(
            system_site_packages=False, clear=False, symlinks=False, with_pip=False
        )
        builder.create(self.dir)
        site_packages = (
            check_output(
                [f"{self.dir}/bin/python", "-Ic", "import sys; print(sys.path[-1])"]
            )
            .decode(locale.getpreferredencoding(False))
            .strip()
        )

        check_call(["pip", "install", ".", "--target", site_packages])
