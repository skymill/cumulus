""" Setup script for PyPI """
import os
from setuptools import setup
from ConfigParser import SafeConfigParser

settings = SafeConfigParser()
settings.read(os.path.realpath('lib/settings.conf'))


setup(
    name='cumulus-bundle-handler',
    version=settings.get('general', 'version'),
    license='Proprietary',
    description='Cumulus AWS deployment tools',
    author='Sebastian Dahlgren',
    author_email='sebastian.dahlgren@skymill.se',
    url='http://www.skymillsolutions.com',
    keywords="cumulus cloudformation amazon web services",
    platforms=['Any'],
    packages=['lib'],
    scripts=['cumulus-bundle-handler'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'boto >= 2.12.0'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)