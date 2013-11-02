""" Setup script for PyPI """
from setuptools import setup


setup(
    name='cumulus',
    version='0.6.0-SNAPSHOT',
    license='Proprietary',
    description='Cumulus AWS deployment tools',
    author='Sebastian Dahlgren',
    author_email='sebastian.dahlgren@skymill.se',
    url='http://www.skymillsolutions.com',
    keywords="cumulus cloudformation amazon web services",
    platforms=['Any'],
    packages=['lib'],
    scripts=['cumulus'],
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