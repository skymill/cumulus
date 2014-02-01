Overview
========

Introduction
------------

The target for the Cumulus project is to make cloud deployments scriptable,
reliable and repeatable. It is of great importance for productivity and
product stability that you are able to release often and with as few manual
steps as possible.

Cumulus consists of two parts, ``cumulus`` which is used to manage the software
bundling and deployment and the ``cumulus-bundle-handler`` which handles
the software installation on the target servers.

Basic concepts
--------------

Cumulus is built around three main concepts:

* An **environment** references a whole environment and all it's CloudFormation stacks. It holds together information about the AWS account, which stacks to deploy and in which version.
* A **stack** is simply a CloudFormation stack.
* A **bundle** is a `tar.bz2`, ``.tar.gz`` or ``.zip`` file with code and configuration to unpack to instances.

Deployment workflow
-------------------

Deployments with Cumulus can take many shapes depending on your project needs.
But a common pattern can look like the example below.

If your build server delivers a package (``.tar.bz2``, ``.tar.gz`` or ``.zip``),
then Cumulus can use that for deployment. The procedure would be something like
this:

1. The build server builds the software
2. The build server places a ``.tar.bz2`` file on the file system
3. ``cumulus`` picks up the software package - called a **bundle** in Cumulus - and rename it according to the given version and target environment
4. ``cumulus`` uploads the bundle to AWS S3
5. ``cumulus`` initiates a AWS CloudFormation ``CREATE`` or ``UPDATE`` (depending on whether or not the stack exists previously)
6. The EC2 instance has ``cumulus-bundle-handler`` installed
7. ``cumulus-bundle-handler`` will download the bundle from S3
8. ``cumulus-bundle-handler`` will deploy the bundle to the instance
9. ``cumulus-bundle-handler`` will restart necessary services and run any configured deployment hooks
10. Deployment is now completed

You can also use ``cumulus`` to build your bundle, if you don't get a
pre-packaged version of you software from the build server. ``cumulus`` can
then take a certain path on the file system and convert it to a bundle.
