from setuptools import setup

setup(
    name='farkelbot',
    author='Chris Bremner',
    author_email='chrisjbremner@gmail.com',
    description='Python implementation of the dice game Farkel',
    url='https://github.com/chrisjbremner/farkelbot',
    packages=['farkelbot'],
    scripts=[],
    version=__import__('farkelbot').__version__,
)
