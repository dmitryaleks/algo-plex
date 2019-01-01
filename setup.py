# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='algoplex',
    version='1.0.0',
    description='Crypto trading framework',
    long_description=readme,
    author='Dmitry Aleks',
    author_email='alekseenkodima@gmail.com',
    url='https://github.com/dmitryaleks/algo-plex',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
