from setuptools import setup, find_packages

setup(
    name='gdcdictionary',
    packages=find_packages(),
    use_scm_version={
        'local_scheme': 'dirty-tag',
        'write_to': 'gdcdictionary/_version.py',
    },
    setup_requires=['setuptools_scm<6'],
    install_requires=[
        'PyYAML>=5.1.2,<5.5',
        'jsonschema>=3.0.2,<3.3',
    ],
    package_data={
        "gdcdictionary": [
            "schemas/*.yaml",
            "schemas/projects/*.yaml",
            "schemas/projects/*/*.yaml",
        ]
    },
)
