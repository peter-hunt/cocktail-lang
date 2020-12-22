from setuptools import setup

from __init__ import __version__


with open('README.md') as file:
    long_description = file.read()

with open('requirements.txt') as file:
    requirements = file.read().strip().split('\n')


setup(
    name='cocktail-lang',
    version=__version__,
    author='Peter Hunt',
    author_email='huangtianhao@icloud.com',
    description='Cocktail Programming Language',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    setup_requires=requirements,
)
