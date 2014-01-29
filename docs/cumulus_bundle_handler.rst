.. _cumulus-bundle-handler:

Cumulus Bundle Handler
======================

The **Cumulus Bundle Handler (CBH)** is a Python script that should reside on each host in the system. The script is responsible for

* Downloading and extracting the correct bundles for the host
* Running pre and post deployment scripts on the host

The bundles are generated via the ``cumulus`` command and uploaded to S3. CBH will then download the bundle when the script is triggered (usually by a CloudFormation ``create`` or ``update``).


Init scripts
------------
The Cumulus Bundle Handler supports scripts to be executed:

* Before bundle extraction (good for stopping services etc)
* After bundle extraction (good for starting services)
* Both before and after extraction (typically cleaning jobs)

All init script should reside in ``/etc/cumulus-init.d`` and must be executable.

* Scripts starting with ``K`` (capital K) are executed *before* the bundle is extracted.
* Scripts starting with ``S`` (capital S) are executed *after* the bundle is extracted.
* Scripts starting with anything else than ``S`` or ``K`` are executed *both before and after* the bundle is extracted.


Configuration
-------------
This configuration should reside on your EC2 instances under ``/etc/cumulus/metadata.conf``. It is good practice to serve it to that location using CloudFormation `AWS::CloudFormation::Init <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-init.html#aws-resource-init-files>`_.


Full example
^^^^^^^^^^^^
::

    [metadata]
    access-key-id: <AWS_ACCESS_KEY>
    secret-access-key: <AWS_SECRET_KEY>
    region: eu-west-1
    bundle-bucket: com.example.bundles
    environment: stage
    bundle-type: webserver
    bundle-extraction-paths:
        generic -> /etc/example
        webserver -> /
    version: 1.0.0-SNAPSHOT
    log-level: INFO


Configuration options
^^^^^^^^^^^^^^^^^^^^^

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
``bundle-extraction-paths`` New line sep. list No       Decide in which parent directory a bundle shall be extracted. Default is `/` on Linux and Mac OS X and `C:\` on Windows systems
``log-level``               String             No       Log level for the bundle handler
=========================== ================== ======== ==========================================

