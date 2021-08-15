import os.path
from distutils import dir_util
from distutils.command.clean import clean as CleanCommand
from pathlib import Path
from typing import Set

REMOVE_DIRS = {
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    "htmlcov",
    "*.egg-info",
    "**/__pycache__",
    "**/.runenv",
}

REMOVE_FILES = {".coverage*"}
EXCLUDE_FILES = {".coveragerc"}

RUN_UTILS = ["isort .", "black ."]


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

        files: Set[Path] = set(
            f
            for p in REMOVE_FILES
            for f in curdir.glob(p)
            if not f.is_dir() and f.name not in EXCLUDE_FILES
        )

        for f in files:
            if f.exists():
                f.unlink()
            else:
                self.announce(f"skipping {f} since it does not exist")

        for dir_name in dir_names:
            if os.path.exists(dir_name):
                dir_util.remove_tree(dir_name, dry_run=self.dry_run)
            else:
                self.announce(f"skipping {dir_name} since it does not exist")

        for cmd in RUN_UTILS:
            if 0 != os.system(cmd):
                self.announce(f"unsuccessful cmd: {cmd}")
