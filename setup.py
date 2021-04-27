import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="viceroybot",
    version="0.0.1",
    author="Frank Male",
    description="A Twitter bot for mimicking the writings of others",
    long_description=read("README.md"),
    packages=["viceroybot"],
)
