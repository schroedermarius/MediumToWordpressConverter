#!/usr/bin/env python3
"""
Setup script for Medium to WordPress Converter
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    with open(readme_path, 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(req_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='medium-to-wordpress-converter',
    version='1.0.0',
    author='Marius Schröder',
    author_email='contact@marius-schroeder.de',
    description='Convert Medium blog posts to WordPress XML format',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/schroedermarius/MediumToWordpressConverter',
    py_modules=['medium_to_wordpress_optimized'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing :: Markup :: XML',
    ],
    python_requires='>=3.7',
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'medium-to-wordpress=medium_to_wordpress_optimized:main',
        ],
    },
    keywords='medium wordpress migration blog export import xml converter',
    project_urls={
        'Bug Reports': 'https://github.com/schroedermarius/MediumToWordpressConverter/issues',
        'Source': 'https://github.com/schroedermarius/MediumToWordpressConverter',
        'Documentation': 'https://github.com/schroedermarius/MediumToWordpressConverter#readme',
    },
)
