import locale
from datetime import date, timedelta
from subprocess import CalledProcessError, check_call, check_output

from setuptools import Command


def next_month(d):
    """
    >>> next_month(date(2019,6,19))
    datetime.date(2019, 7, 1)
    >>> next_month(date(2019,12,19))
    datetime.date(2020, 1, 1)
    """
    cur_month = d.month
    while cur_month == d.month:
        d += timedelta(days=1)
    return d


class Version:
    """

    >>> Version((2019, 7, 1)).next_minor(date(2019,6,19))
    Version((2019, 7, 2))
    >>> Version((2019, 7, 1)).next_major(date(2019,6,19))
    Traceback (most recent call last):
    ...
    ValueError: cannot calc major version from: (2019, 7, 1) 2019-07-01
    >>> Version((2019, 7, 1)).next_major(date(2019,7,1))
    Version((2019, 8))

    """

    def __init__(self, s):
        self.nums = s if isinstance(s, tuple) else tuple(map(int, s.split(".")))
        if len(self.nums) not in (2, 3):
            raise ValueError(f"version has to have 2 or 3 parts: {s}")

    def __str__(self):
        return ".".join(map(str, self.nums))

    def __repr__(self):
        return f"Version({self.nums})"

    def next_major(self, now=date.today()):
        _nums = (now.year, now.month)
        if _nums > self.nums:
            return Version(_nums)
        else:
            now = next_month(now)
            _nums = (now.year, now.month)
            if _nums > self.nums:
                return Version(_nums)
            raise ValueError(f"cannot calc major version from: {self.nums} {now}")

    def next_minor(self, now=date.today()):
        last_num = 1
        if self.is_minor():
            last_num = self.nums[2]
        date_t = max(tuple(self.nums[:2]), (now.year, now.month))
        _nums = (*date_t, last_num)
        if self.nums == _nums:
            return Version((*date_t, last_num + 1))
        else:
            _nums = (now.year, now.month, 1)
            if _nums > self.nums:
                return Version(_nums)
            now = next_month(now)
            _nums = (now.year, now.month, 1)
            if _nums > self.nums:
                return Version(_nums)
            raise ValueError(f"cannot calc version from: {self.nums} {now}")

    def is_minor(self):
        return len(self.nums) == 3

    def type(self):
        return "minor" if self.is_minor() else "major"


def get_version_and_add_release_cmd(version_file, cmdclass_dict):
    version = Version(open(version_file).read().strip())

    class ReleaseCommand(Command):
        description = f"""
            Check release:
                return success errorCode if {version_file} match 
                current tag on branch. 
    
            Trigger release:
                change {version_file}, tag and push changes to git.
    
            """

        user_options = [
            ("azure", None, "publish azure vars"),
            ("minor", None, "trigger minor release "),
            ("major", None, "trigger major release "),
        ]

        def initialize_options(self):
            self.azure = self.minor = self.major = False

        def finalize_options(self):
            pass

        def azure_var(self, key, value):
            if self.azure:
                print(
                    f"##vso[task.setvariable " f"variable={key};isOutput=true]{value}"
                )

        def run(self):
            """Run command."""
            new_ver = None
            if self.major:
                new_ver = version.next_major()
            elif self.minor:
                new_ver = version.next_minor()
            else:
                try:
                    tag = (
                        check_output(["git", "describe", "--tags", "--exact-match"])
                        .decode(locale.getpreferredencoding(False))
                        .strip()
                    )
                    version_ = f"v{version}"
                    print(f"version.txt={version_!r} git={tag!r}")
                    match = tag == version_
                except CalledProcessError:
                    print(f"no tag found")
                    match = False
                    self.azure_var("type", "none")
                if match:
                    print(f"{version.type()} release. Git tag matched.")
                    self.azure_var("type", version.type())
                raise SystemExit(0)
            open(version_file, "wt").write(str(new_ver))
            print(f"New version: {new_ver}")
            tag = f"v{new_ver}"
            msg = ["-m", tag]
            check_call(["git", "add", version_file])
            check_call(["git", "commit", *msg])
            check_call(["git", "tag", "-a", tag, *msg])
            # check_call(f'git push origin --tags'.split())
            check_call("git push --tags origin HEAD".split())
            check_call("git push -u origin master".split())

    cmdclass_dict["release"] = ReleaseCommand
    return version
