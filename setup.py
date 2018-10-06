# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='scrapbox',
    version='0.0.3',
    description='Scrapbox Python',
    long_description=readme,
    author='meganii',
    author_email='tsubokawa.yuhei@gmail.com',
    url='https://gitlab.com/meganii/scrapbox-python.git',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)