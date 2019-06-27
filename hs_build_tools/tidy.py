import os.path
from distutils import dir_util
from distutils.command.clean import clean as CleanCommand
from pathlib import Path

REMOVE_DIRS = set(
    (
        "dist",
        "build",
        ".mypy_cache",
        ".pytest_cache",
        "htmlcov",
        "*.egg-info",
        "**/__pycache__",
        "**/.runenv",
    )
)

RUN_UTILS = ["isort -y", "black ."]


class TidyCommand(CleanCommand):
    def initialize_options(self):
        CleanCommand.initialize_options(self)

    def finalize_options(self):
        CleanCommand.finalize_options(self)
        self.all = True

    def run(self):
        CleanCommand.run(self)
        curdir = Path(".")
        dir_names = set(
            str(f) for p in REMOVE_DIRS for f in curdir.glob(p) if f.is_dir()
        )

        for dir_name in dir_names:
            if os.path.exists(dir_name):
                dir_util.remove_tree(dir_name, dry_run=self.dry_run)
            else:
                self.announce(f"skipping {dir_name} since it does not exist")

        for cmd in RUN_UTILS:
            if 0 != os.system(cmd):
                self.announce(f"unsuccessful cmd: {cmd}")
