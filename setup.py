#!/usr/bin/env python
from setuptools import setup

try:
    from shortcutter import ShortCutter
    HAS_SHORTCUTTER=True

except ImportError:
    HAS_SHORTCUTTER=False

if __name__ == '__main__':
    setup(
        name='interactive_ocr',
        version='0.0.0',
        description='Simple utility to read images',
        author='Pierre Delaunay',
        packages=['interactive_ocr'],
        setup_requires=['setuptools'],
        install_requires=[
            'shortcutter',
            "numpy",			
            "PyQt5",			
            "pandas",			
            "pytesseract",	
            "pillow",
            "opencv-python",

        ],
        entry_points={
            'console_scripts': [
                'interactive-ocr = interactive_ocr.image_reader:main',
                'convert-ocr = interactive_ocr.convert:main',
            ]
        },
    )

    if HAS_SHORTCUTTER:
        sc = ShortCutter()
        sc.create_desktop_shortcut("interactive-ocr")
        sc.create_menu_shortcut("interactive-ocr")
        sc.create_shortcut_to_env_terminal()

        sc = ShortCutter()
        sc.create_desktop_shortcut("convert-ocr")
        sc.create_menu_shortcut("convert-ocr")
        sc.create_shortcut_to_env_terminal()
