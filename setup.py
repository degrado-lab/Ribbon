from setuptools import setup, find_packages

setup(
    name='ribbon-toolkit',
    version='0.2.3',
    description='A python API for running enzyme design pipelines.',
    author='Nicholas Freitas',
    author_email='nicholas.freitas@ucsf.edu',
    packages=find_packages(include=['ribbon', 'ribbon.*', 'ribbon_tasks', 'ribbon_tasks.*']),
    include_package_data=True,
    install_requires=[],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)