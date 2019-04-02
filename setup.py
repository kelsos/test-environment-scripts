#!/usr/bin/env python

from glob import glob
from os.path import basename, splitext

from setuptools import find_packages, setup

with open('README.md', encoding='utf-8') as readme_file:
    readme = readme_file.read()

history = ''

version = '0.0.1'  # Do not edit: this is maintained by bumpversion (see .bumpversion.cfg)

setup(
    name='test-scripts',
    description='test scripts',
    version=version,
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Konstantinos Paparas',
    author_email='kelsos@kelsos.net',
    url='https://github.com/kelsos/test-environment-scripts.',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    license='MIT',
    zip_safe=False,
    keywords='test scripts',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
    ],
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    python_requires='>=3.7',
)
