import os

from setuptools import setup, find_packages

setup(
    name='gdcdictionary',
    version="1.15.0",
    packages=find_packages(),
    install_requires=[
        'PyYAML>=4.2b1',
        'jsonschema',
        'future',
    ],
    package_data={
        "gdcdictionary": [
            "schemas/*.yaml",
            "schemas/projects/*.yaml",
            "schemas/projects/*/*.yaml",
        ]
    },
)
