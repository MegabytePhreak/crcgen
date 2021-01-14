from setuptools import find_packages, setup

setup(
    name="crcgen",
    version="0.1",
    description="Generate a parallel CRC implementation for arbitrary polynomial and data width",
    author="Paul Roukema",
    author_email="roukemap@gmail.com",
    license="0BSD",
    test_suite="unittest",
    entry_points={
        "console_scripts": [
            "crcgen = crcgen.__main__:main",
        ]
    },
)
