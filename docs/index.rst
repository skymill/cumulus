.. toctree::
    :hidden:
    :maxdepth: 3

    installation
    cumulus_configuration
    cumulus_bundle_handler
    cf_example
    command_line_options
    release_notes
    license

Cumulus
=======

Cumulus is a deployment tool used to deploy and maintain environments built with AWS CloudFormation. Cumulus will help you bundle your code and configuration and unpack the bundle to new instances on CloudFormation.

Overview
========

Basic concepts
--------------

Cumulus is built around three main concepts:

* An **environment** references a whole environment and all it's CloudFormation stacks. It holds together information about the AWS account, which stacks to deploy and in which version.
* A **stack** is simply a CloudFormation stack.
* And a **bundle** is a `tar.bz2` file with code and configuration to unpack to instances.

Requirements
------------

Cumulus requires Python 2.7 and ``boto``. Please install requirements with
::

    pip install -r cumulus/requirements.txt

Supported platforms
-------------------

Cumulus supports Linux and Windows systems both as client and target systems.

Deployment workflow
-------------------

The deployment workflow is roughly as follows

1. Bundle your software
2. Upload the bundle to AWS S3
3. Trigger a ``create`` or ``update`` of your CloudFormation template
4. The :ref:`cumulus-bundle-handler` will then download and extract the bundle on each host
5. Deployment complete

All you need to do is to run the command below. This will bundle and upload all your software to AWS S3. It will then trigger an create or update at AWS CloudFormation.
::

    cumulus --environment production --deploy

| **Note!**
| When running on Windows, you'll need to invoke Cumulus with ``python cumulus``

The rest of the work is down within the AWS CloudFormation template. Please have a look at our :ref:`cloudformation-template-example`.

Environment specific configuration
----------------------------------

To have files that should only be included in specific environments, prefix them with `__cumulus-environment__filename`. So for example: `__cumulus-production__nginx.conf` is the `nginx.conf` for the production environment.
