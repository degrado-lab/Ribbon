from setuptools import setup, find_packages

setup(
    name='ribbon-toolkit',
    version='0.2.4',
    description='A python API for running enzyme design pipelines.',
    author='Nicholas Freitas',
    author_email='nicholas.freitas@ucsf.edu',
    packages=find_packages(include=['ribbon', 'ribbon.*', 'ribbon_tasks', 'ribbon_tasks.*']),
    include_package_data=True,
    install_requires=[
        'tomli>=1.2.0; python_version<"3.11"',  # TOML support for older Python versions
    ],
    entry_points={
        'console_scripts': [
            'ribbon=ribbon.cli.cli:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
