"""
Basic setup copied from https://packaging.python.org/tutorials/packaging-projects/#creating-setup-py

author: Alexandra DeLucia
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="littlebird",
    version="0.0.2",
    author="Alexandra DeLucia",
    author_email="aadelcuia@jhu.edu",
    description="Utilities for opening and processing Tweets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=["jsonlines", "regex", "filetype", "lxml", "emoji", "nltk"],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
