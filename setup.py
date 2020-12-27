from setuptools import setup

from cocktail.__init__ import __version__


with open('README.md') as file:
    long_description = file.read()

with open('requirements.txt') as file:
    requirements = file.read().strip().split('\n')


setup(
    name='cocktail-lang-peterhunt',
    version=__version__,
    author='Peter Hunt',
    author_email='huangtianhao@icloud.com',
    description='Cocktail Programming Language',
    long_description=long_description,
    long_description_content_type='text/markdown',
    setup_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
)
