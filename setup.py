import os
from setuptools import setup, find_packages


SERVICE_VERSION = open('VERSION').readline()
REQUIREMENTS_PATH = os.getenv('REQUIREMENTS_PATH', '')

requirements = [
    line.strip() for line in open(
        os.path.join(REQUIREMENTS_PATH, 'requirements.txt'))
]

setup(
    name='item_menu',
    version=SERVICE_VERSION,
    keywords='item_menu',
    packages=find_packages(exclude=['tests']),
    install_requires=requirements,
    python_requires='3.5'
)
