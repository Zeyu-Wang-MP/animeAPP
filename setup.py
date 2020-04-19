from setuptools import setup
setup(
    name='anime',
    version='0.1.0',
    packages=['anime'],
    include_package_data=True,
    install_requires=[
        'bs4',
        'Flask',
        'requests',
    ],
)