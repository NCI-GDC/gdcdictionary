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
       "git+https://github.com/uc-cdis/dictionaryutils.git@2.0.4#egg=dictionaryutils",
    ],
    package_data={
        "gdcdictionary": [
            "schemas/*.yaml",
            "schemas/projects/*.yaml",
            "schemas/projects/*/*.yaml",
        ]
    },
)
