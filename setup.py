from setuptools import setup

with open("README.md") as f:
    long_description = f.read()

setup(
    name="viceroybot",
    version="0.0.1",
    author="Frank Male",
    description="A Twitter bot for mimicking the writings of others",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["viceroybot"],
    install_requires=["tweepy"],
    python_requires=">=3.6",
)
