from setuptools import setup, find_packages

setup(
    name='ribbon',
    version='0.2.0',
    description='A tool for building and running enzyme design pipelines.',
    author='Nicholas Freitas',
    author_email='nicholas.freitas@ucsf.edu',
    packages=find_packages(include=['ribbon', 'ribbon.*', 'ribbon_tasks', 'ribbon_tasks.*']),
    install_requires=[],
    classifiers=[
        # See https://pypi.org/classifiers/ for the full list
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)