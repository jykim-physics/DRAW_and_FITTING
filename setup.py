from setuptools import setup, find_packages
from pkg_resources import resource_filename
from pathlib import Path


with (Path(__file__).parent / 'README.md').open() as readme_file:
    readme = readme_file.read()

setup(
    name='DRAW_and_FITTING',
    packages=find_packages(),
    url="",
    author='Jaeyoung Kim',
    author_email='jaeyoung_kim@yonsei.ac.kr',
    description='''
Draw plots and do fitting with .root files.
''',
    install_requires=[
        'numpy<1.23',  # Remove this when numba becomes compatible with numpy>=1.23
        'scipy',
        'numba',
        'matplotlib', 
        'jupyterlab', 
        'uncertainties',
        'iminuit',
        'gvar',
        'numdifftools',
    ],
    extras_require={
        "examples":  [],
    },
    long_description=readme,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License "
    ],
    license='MIT',
)
