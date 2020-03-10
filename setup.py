from setuptools import setup, find_packages

setup(
    name='gdcdictionary',
    version="2.1.0",
    packages=find_packages(),
    install_requires=[
        'PyYAML',
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
