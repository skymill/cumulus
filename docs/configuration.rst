Configuration
=============


Cumulus configuration (``cumulus.conf``)
----------------------------------------

All configuration is read form ``/etc/cumulus.conf``, ``~/.cumulus.conf`` and ``./cumulus.conf`` in order. This is a full example configuration:
::

    [environment: stage]
    access-key-id: <AWS ACCESS KEY>
    secret-access-key: <AWS SECRET KEY>
    bucket: se.skymill.bundles
    region: eu-west-1
    stacks: full
    bundles: webserver, database
    version: 1.0.0-SNAPSHOT
    pre-deploy-hook: /path/to/script
    post-deploy-hook: echo "Yay" > ~/test.log

    [stack: full]
    template: /Users/sebastian/tmp/hosts/webserver.json
    disable-rollback: true
    parameters:
        version = 1.1.0,
        test tag = my test value
        key = value

    [bundle: webserver]
    pre-bundle-hook: git clone git://git.example.com/my.git
    post-bundle-hook: rm -rf my
    paths:
        /Users/sebastian/tmp/hosts/webserver,
        /Users/sebastian/tmp/code/wordpress

    [bundle: database]
    pre-bundle-hook: /path/to/script
    paths: /Users/sebastian/tmp/hosts/database
    path-rewrites:
        /wordpress -> /var/www/wordpress
        /nginx -> /etc/nginx


Environment configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

The following configuration options are available under ``[environment: env_name]``. The ``env_name`` is the identifier for the environment.

======================= ================== ======== ==========================================
Option                  Type               Required Comment
======================= ================== ======== ==========================================
``access-key-id``       String             Yes      AWS access key
``secret-access-key``   String             Yes      AWS secret access key
``bucket``              String             Yes      AWS S3 bucket to store bundles in
``region``              String             Yes      AWS region name, e.g. ``us-east-1``
``stacks``              CSV                Yes      List of stack names to deploy
``bundles``             CSV                Yes      List of bundles to build and upload
``version``             String             Yes      Environment version number
``pre-deploy-hook``     String             No       Command to execute before deployment
``post-deploy-hook``    String             No       Command to execute after deployment
======================= ================== ======== ==========================================


Stack configuration
^^^^^^^^^^^^^^^^^^^

Options for the ``[stack: stack_name]`` configuration section.

======================= ================== ======== ==========================================
Option                  Type               Required Comment
======================= ================== ======== ==========================================
``template``            String             Yes      Path to local CloudFormation JSON file
``disable-rollback``    Boolean            No       Should CloudFormation rollbacks be disabled? Default: ``false``
``parameters``          Line sep. string   Yes      Parameters to send to the CloudFormation template. Should be on the form ``key = value``. Each parameter is separated by a new line.
======================= ================== ======== ==========================================


Bundle configuration
^^^^^^^^^^^^^^^^^^^^

Options for the ``[bundle: bundle_name]`` configuration section.

======================= ================== ======== ==========================================
Option                  Type               Required Comment
======================= ================== ======== ==========================================
``pre-bundle-hook``     String             No       Command to execute before bundling
``post-bundle-hook``    String             No       Command to execute after bundling
``paths``               Line sep. string   Yes      Paths to include in the bundle. Each path should be declared on a new line.
======================= ================== ======== ==========================================


Cumulus Bundle Handler configuration (``metadata.conf``)
--------------------------------------------------------
This file should reside on your EC2 instances under ``/etc/cumulus/metadata.conf``. It is good practice to serve it to that location using CloudFormation `AWS::CloudFormation::Init <http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-init.html#aws-resource-init-files>`_.
::

    [metadata]
    access-key-id: <AWS_ACCESS_KEY>
    secret-access-key: <AWS_SECRET_KEY>
    region: eu-west-1
    bundle-bucket: com.example.bundles
    environment: stage
    bundle-type: webserver
    version: 1.0.0-SNAPSHOT


Configuration options
^^^^^^^^^^^^^^^^^^^^^

======================= ================== ======== ==========================================
Option                  Type               Required Comment
======================= ================== ======== ==========================================
``access-key-id``       String             Yes      AWS access key
``secret-access-key``   String             Yes      AWS secret access key
``region``              String             Yes      AWS region name, e.g. ``us-east-1``
``bucket``              String             Yes      AWS S3 bucket to fetch bundles from
``environment``         String             Yes      Environment name
``version``             String             Yes      Environment version to apply
``bundle-types`         CSV                Yes      Bundle names to apply to this host
======================= ================== ======== ==========================================
