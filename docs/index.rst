Table of contents
=================
.. toctree::

   configuration

Cumulus
=======

Cumulus is a deployment tool used to deploy and maintain environments built with AWS CloudFormation. Cumulus will help you bundle your code and configuration and unpack the bundle to new instances on CloudFormation.

Basic concepts
==============

Cumulus is built around three main concepts:

* An **environment** references a whole environment and all it's CloudFormation stacks. It holds together information about the AWS account, which stacks to deploy and in which version.
* A *stack* is simply a CloudFormation stack.
* And a **bundle** is a `tar.bz2` file with code and configuration to unpack to instances.

Requirements
============

Cumulus requires Python 2.7 and ``boto``. Please install requirements with
::

    pip install -r cumulus/requirements.txt
