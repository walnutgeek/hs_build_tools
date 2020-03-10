from os import makedirs
from os.path import exists, join
from shutil import rmtree
from subprocess import check_call

from setuptools import Command


class PyzCommand(Command):
    description = f"""
            Build runtime pyz executable using shiv.
            """
    DEFAULT_DIR = "./dist"
    DEFAULT_EP = "hashkernel.cli:main"

    user_options = [
        ("dir=", None, f"where to create .pyz file, default is: {DEFAULT_DIR}"),
        ("name=", None, f"name of .pyz file, if omitted defaults to package name"),
        (
            "script=",
            None,
            f"entry point used in .pyz file created, default is {DEFAULT_EP}",
        ),
    ]

    def initialize_options(self):
        self.dir = self.DEFAULT_DIR
        self.script = self.DEFAULT_EP
        self.name = f"{self.distribution.get_name()}.pyz"

    def target_dir(self):
        return join(self.dir, "site_packages_for_pyz")

    def finalize_options(self):
        pass

    def run(self):
        """
        Execute command. Create runenv and install dependencies
        """
        if not exists("setup.py"):
            raise ValueError(f"Has to be run from root of the project")
        rmtree(self.target_dir(), ignore_errors=True)
        makedirs(self.target_dir(), exist_ok=True)
        check_call(["pip", "install", ".", "--target", self.target_dir()])
        makedirs(self.dir, exist_ok=True)
        self.run_shiv(self.script)

    def run_shiv(self, ep_method):
        pyz_name = join(self.dir, self.name)
        check_call(
            [
                "shiv",
                "--site-packages",
                self.target_dir(),
                "-o",
                pyz_name,
                "-e",
                ep_method,
            ]
        )
        print(f"Created: {pyz_name} with entry point: {ep_method}")
