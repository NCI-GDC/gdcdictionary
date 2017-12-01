from setuptools import setup, find_packages

setup(
    name='gdcdictionary',
    version='0.0.0',
    packages=find_packages(),
    install_requires=[
        'PyYAML==3.11',
        'jsonschema==2.5.1',
        'dictionaryutils',
    ],
    dependency_links=[
       "git+https://github.com/uc-cdis/dictionaryutils.git@11cfcb2c8bd579960c76f2b8136f8f00db7a3c01#egg=dictionaryutils",
    ],
    package_data={
        "gdcdictionary": [
            "schemas/*.yaml",
            "schemas/projects/*.yaml",
            "schemas/projects/*/*.yaml",
        ]
    },
)
