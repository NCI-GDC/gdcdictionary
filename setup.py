import os

from setuptools import setup, find_packages

setup(
    name='gdcdictionary',
    packages=find_packages(),
    #use_scm_version={'local_scheme': 'dirty-tag'},
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    install_requires=[
        'PyYAML==3.11',
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
