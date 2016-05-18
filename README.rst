Cumulus Deployment Suite
========================

**Cumulus**

.. image:: https://img.shields.io/pypi/v/cumulus.svg
    :target: https://pypi.python.org/pypi/cumulus/
    :alt: Latest Version
.. image:: https://img.shields.io/pypi/dm/cumulus.svg
    :target: https://pypi.python.org/pypi/cumulus/
    :alt: Downloads
.. image:: https://img.shields.io/pypi/l/cumulus.svg
    :target: https://pypi.python.org/pypi/cumulus/
    :alt: License

**Cumulus Bundle Handler**

.. image:: https://img.shields.io/pypi/v/cumulus-bundle-handler.svg
    :target: https://pypi.python.org/pypi/cumulus-bundle-handler/
    :alt: Latest Version
.. image:: https://img.shields.io/pypi/dm/cumulus-bundle-handler.svg
    :target: https://pypi.python.org/pypi/cumulus-bundle-handler/
    :alt: Downloads
.. image:: https://img.shields.io/pypi/l/cumulus-bundle-handler.svg
    :target: https://pypi.python.org/pypi/cumulus-bundle-handler/
    :alt: License

Cumulus is a deployment suite used to deploy and manage environments built with AWS CloudFormation. Cumulus will help you bundle your code and configuration and unpack the bundle to new instances on CloudFormation.

Documentation
-------------

The Cumulus documentation is hosted at `http://cumulus-ds.readthedocs.org/ <http://cumulus-ds.readthedocs.org/>`__.


Installation
------------

Cumulus consists of two parts, ``cumulus`` which is used to manage the software
bundling and deployment and the ``cumulus-bundle-handler`` which handles
the software installation on the target servers.

Installing ``cumulus``
^^^^^^^^^^^^^^^^^^^^^^

Install Cumulus via PyPI:
::

    pip install cumulus

``cumulus`` will now be available as a global command.

Installing ``cumulus-bundle-handler``
^^^^^^^^^^^^^^^^^^^^^^

Install Cumulus Bundle Handler via PyPI:
::

    pip install cumulus-bundle-handler

``cumulus-bundle-handler`` will now be available as a global command.


Attribution
-----------

This project is written and maintained by `Sebastian Dahlgren <http://www.sebastiandahlgren.se>`_ (`GitHub <https://github.com/sebdah>`_ | `Twitter <https://twitter.com/sebdah>`_ | `LinkedIn <http://www.linkedin.com/in/sebastiandahlgren>`_).

Cumulus development is supported by `Skymill Solutions <http://www.skymillsolutions.com>`__.

License
-------

APACHE LICENSE 2.0
Copyright 2013-2014 Skymill Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   `http://www.apache.org/licenses/LICENSE-2.0 <http://www.apache.org/licenses/LICENSE-2.0>`__

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
