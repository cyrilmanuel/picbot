"""Super Picbot."""

from setuptools import setup, find_packages

setup(
    name='picbot',
    version='1.0',
    description=__doc__,
    packages=find_packages(),
    install_requires=(
        'pypandoc',
        'xkcd',
        'aiohttp',
        'asyncio',
        'cchardet'
    ),
    extras_requires={
        'test': ('pytest', 'pytest-flake8', 'pytest-coverage'),
        'doc': ('Sphinx', 'sphinx_rtd_theme'),
    }
)
