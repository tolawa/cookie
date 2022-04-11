from setuptools import setup

setup(
    name='cookie',
    py_modules=['imgmat'],
    install_requires=[
        'pillow',
    ],
    entry_points='''
        [console_scripts]
        imgmat=imgmat:main
    ''',
)
