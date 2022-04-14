# coding=utf-8

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

from codecs import open

version = {}
with open("boardgamegeek/version.py") as fp:
    exec(fp.read(), version)

long_description = open("README.md", encoding="utf-8").read()


class PyTest(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)


tests_require = ["pytest", "pytest-mock"]

setup(
    name="python-boardgamegeek",
    version=version["__version__"],
    packages=find_packages(),
    license="BSD",
    author="CJ O'Hara",
    author_email="mmonkey@gmail.com",
    description="A Python interface to boardgamegeek.com's API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mmonkey/boardgamegeek",
    tests_require=tests_require,
    extras_require={'test': tests_require},
    cmdclass={'test': PyTest},
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Games/Entertainment :: Board Games",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    install_requires=["requests>=2.27.1", "requests-cache>=0.9.3"],
    entry_points={
        "console_scripts": [
            "boardgamegeek = boardgamegeek.main:main"
        ]
    }
)
