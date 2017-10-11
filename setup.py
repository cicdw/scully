#!/usr/bin/env python

from os.path import exists
from setuptools import setup


setup(name='scully-bot',
      version='0.0.1',
      description='scully-bot!',
      url='https://github.com/moody-marlin/scully.git',
      maintainer='Chris White',
      maintainer_email='white.cdw@gmail.com',
      packages=['scully'],
      install_requires=list(open('requirements.txt').read().strip().split('\n')),
      entry_points = {
        'console_scripts': ['scully=scully.scully:main'],
      },
      zip_safe=False)
