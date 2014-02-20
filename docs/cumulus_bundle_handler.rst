.. _cumulus-bundle-handler:

Cumulus Bundle Handler
======================

The Cumulus Bundle Handle is a Python script that should reside on each server
in the environment. The script is responsible for

* Downloading and extracting the correct bundles for the host
* Running pre and post deployment scripts on the host, e.g. to restart relevant services and trigger various deployment hooks

The bundles are generated via the ``cumulus`` command (or in your build server)
and uploaded to S3. Cumulus Bundle Handler will then download the bundle when
the script is triggered (usually by a CloudFormation ``create`` or ``update``).

Init scripts
------------

The Cumulus Bundle Handler supports scripts to be executed:

* Before bundle extraction (good for stopping services etc)
* After bundle extraction (good for starting services)
* Both before and after extraction (typically cleaning jobs)

All init script should reside in ``/etc/cumulus-init.d`` on Linux systems and
in ``C:\cumulus\init.d`` on Windows systems and must be executable.

* Scripts starting with ``pre`` are executed *after* the bundle is extracted
* Scripts starting with ``post`` are executed *before* the bundle is extracted
* Scripts starting with anything else than ``pre`` or ``post`` are executed both before and after the bundle is extracted

Configuration file
------------------

The configuration file for Cumulus Bundle Handler should reside on your
EC2 instances under ``/etc/cumulus/metadata.conf`` on Linux systems and
under ``C:\cumulus\conf\metadata.conf`` on Windows systems. It recommended
to serve it to that location using CloudFormation `AWS::CloudFormation::Init <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-init.html#aws-resource-init-files>`_.


``metadata.conf`` example
^^^^^^^^^^^^^^^^^^^^^^^^^
The Cumulus Bundle Handler relies on a configuration file called
``metadata.conf``. Here's an example configuration file.
::

    [metadata]
    log-level: INFO
    access-key-id: <AWS_ACCESS_KEY>
    secret-access-key: <AWS_SECRET_KEY>
    region: eu-west-1
    bundle-bucket: com.example.bundles
    environment: stage
    bundle-types: webserver
    bundle-extraction-paths:
        generic -> /etc/example
        webserver -> /
    version: 1.0.0-SNAPSHOT


Configuration options for ``metadata.conf``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

=========================== ================== ======== ==========================================
Option                      Type               Required Comment
=========================== ================== ======== ==========================================
``access-key-id``           String             Yes      AWS access key
``secret-access-key``       String             Yes      AWS secret access key
``region``                  String             Yes      AWS region name, e.g. ``us-east-1``
``bucket``                  String             Yes      AWS S3 bucket to fetch bundles from
``environment``             String             Yes      Environment name
``version``                 String             Yes      Environment version to apply
``bundle-types``            List               Yes      Bundle names to apply to this host
``bundle-extraction-paths`` New line sep. list No       Decide in which parent directory a bundle shall be extracted. Default is `/` on Linux and Mac OS X and `C:\` on Windows systems. Expecting absolute paths
``log-level``               String             No       Log level for the bundle handler
=========================== ================== ======== ==========================================

Logging
-------

Cumulus Bundle Handler will log to ``/var/log/cumulus-bundle-handler.log`` on
Linux systems and to ``C:\cumulus\logs\cumulus-bundle-handler.log`` on Windows
systems.

This log file can be really helpful when trying to debug your deployments.
