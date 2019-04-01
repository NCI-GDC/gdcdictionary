import os

from setuptools import setup, find_packages

setup(
    name='gdcdictionary',
    version="1.16.0",
    packages=find_packages(),
    install_requires=[
        'PyYAML==5.1',
        'jsonschema',
    ],
    package_data={
        "gdcdictionary": [
            "schemas/*.yaml",
            "schemas/projects/*.yaml",
            "schemas/projects/*/*.yaml",
        ]
    },
)
