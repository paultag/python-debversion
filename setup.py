from debversion import __appname__, __version__
from setuptools import setup


long_description = ""

setup(
    name=__appname__,
    version=__version__,
    scripts=[],
    packages=['debversion'],
    author="Paul Tagliamonte",
    author_email="tag@pault.ag",
    long_description=long_description,
    description='n/a',
    license="Expat",
    url="http://pault.ag/",
    platforms=['any'],
    entry_points={
    }
)
