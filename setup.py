#!/usr/bin/env python
from setuptools import setup

if __name__ == '__main__':
    setup(
        name='interactive_ocr',
        version='0.0.0',
        description='Simple utility to read images',
        author='Pierre Delaunay',
        packages=['interactive_ocr'],
        setup_requires=['setuptools'],
        entry_points={
            'console_scripts': [
                'interactive-ocr = interactive_ocr.image_reader:main',
                'convert-ocr = interactive_ocr.convert.py:main',
            ]
        },
    )
