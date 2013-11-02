Overview
========

Basic concepts
--------------

Cumulus is built around three main concepts:

* An **environment** references a whole environment and all it's CloudFormation stacks. It holds together information about the AWS account, which stacks to deploy and in which version.
* A *stack* is simply a CloudFormation stack.
* And a **bundle** is a `tar.bz2` file with code and configuration to unpack to instances.

Requirements
------------

Cumulus requires Python 2.7 and ``boto``. Please install requirements with
::

    pip install -r cumulus/requirements.txt

Deployment workflow
-------------------

All you need to do is to run the command below. This will bundle and upload all your software to AWS S3. It will then trigger an create or update at AWS CloudFormation.
::

    cumulus --environment production --deploy

Environment specific configuration
----------------------------------

To have files that should only be included in specific environments, prefix them with `__cumulus-environment__filename`. So for example: `__cumulus-production__nginx.conf` is the `nginx.conf` for the production environment.