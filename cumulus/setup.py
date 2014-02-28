""" Setup script for PyPI """
import os
from setuptools import setup
from ConfigParser import SafeConfigParser

settings = SafeConfigParser()
settings.read(os.path.realpath('cumulus_ds/settings.conf'))


setup(
    name='cumulus',
    version=settings.get('general', 'version'),
    license='Apache Software License',
    description='Cumulus Deployment Suite for Amazon Web Services',
    author='Sebastian Dahlgren',
    author_email='sebastian.dahlgren@skymill.se',
    url='http://www.skymillsolutions.com',
    keywords="cumulus cloudformation amazon web services",
    platforms=['Any'],
    packages=['cumulus_ds'],
    scripts=['cumulus'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'boto >= 2.12.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
