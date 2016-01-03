from setuptools import setup

setup(name=grdsegy,
      version='1.0',
      description='SEGY creator from Surfer GRD files',
      author='Terra Australis Geophysica',
      url='https://github.com/Mekkiss/grdsegy',
      author_email='grdsegy@nl.ti4200.info',
      license='MIT',
      install_requires=[
         'segpy'
      ],
      packages=find_packages(),
      entry_points={
        'console_scripts': [
        'grdsegy = grdsegy.grdsegy.main',
        ],
    },)