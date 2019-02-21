import os

from setuptools import setup, find_packages

VERSION_FILE = 'VERSION'


def get_version():
    """Returns the current  dictionary version"""

    current_dir = os.path.dirname(os.path.realpath(__file__))
    version_path = os.path.join(current_dir, VERSION_FILE)

    with open(version_path, 'r') as version_fd:
        return version_fd.read().strip()


setup(
    name='gdcdictionary',
    version=get_version(),
    packages=find_packages(),
    install_requires=[
        'PyYAML==3.13',
        'jsonschema==2.6.0',
    ],
    package_data={
        "gdcdictionary": [
            "schemas/*.yaml",
            "schemas/projects/*.yaml",
            "schemas/projects/*/*.yaml",
        ]
    },
)
