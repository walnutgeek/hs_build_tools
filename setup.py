from setuptools import setup, find_packages
from setuptools.command.sdist import sdist
from subprocess import check_call
import os
from hs_build_tools.setup import get_version_and_add_release_cmd



cmdclass_dict = {}


# MANIFEST.in ensures that requirements are included in `sdist`
install_requires = open('requirements.txt').read().split()

with open("README.md", "r") as fh:
    long_description = fh.read()

version = get_version_and_add_release_cmd('version.txt', cmdclass_dict)

setup(name='hs_build_tools',
      version=str(version),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Software Development :: Build Tools',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
      ],
      description='hashstore build tools',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/walnutgeek/hashstore',
      author='Walnut Geek',
      author_email='wg@walnutgeek.com',
      license='Apache 2.0',
      packages=find_packages(exclude=("tests",)),
      package_data={},
      cmdclass=cmdclass_dict,
      entry_points={},
      install_requires=install_requires,
      zip_safe=True)