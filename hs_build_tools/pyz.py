from os import makedirs
from os.path import exists, join
from shutil import rmtree
from subprocess import check_call

from setuptools import Command


class PyzCommand(Command):
    description = f"""
            Build runtime pyz executable using shiv.
            """
    DEFAULT_DIR = join("dist", "site_packages_for_pyz")

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
        rmtree(self.dir, ignore_errors=True)
        makedirs(self.dir, exist_ok=True)
        check_call(["pip", "install", ".", "--target", self.dir])
        makedirs("dist", exist_ok=True)
        for ep in self.distribution.entry_points["console_scripts"]:
            ep_name, ep_method = map(lambda s: s.strip(), ep.split("="))
            check_call(
                [
                    "shiv",
                    "--site-packages",
                    self.dir,
                    "-o",
                    f"dist/{ep_name}.pyz",
                    "-e",
                    ep_method,
                ]
            )
