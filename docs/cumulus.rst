Cumulus
=======

Cumulus (``cumulus``) is used for software bundling and for managing
CloudFormation deployments.

Cumulus configuration
---------------------

Example ``cumulus.conf``
^^^^^^^^^^^^^^^^^^^^^^^^

All configuration is read form ``/etc/cumulus.conf``, ``~/.cumulus.conf`` and
``./cumulus.conf`` in order. You can also specify a custom configuration file
with ``--config``.

Below is a full example configuration:
::

    [general]
    log-level: info

    [environment: stage]
    access-key-id: <AWS ACCESS KEY>
    secret-access-key: <AWS SECRET KEY>
    bucket: se.skymill.bundles
    region: eu-west-1
    stacks: full
    bundles: webserver, database, app
    version: 1.0.0-SNAPSHOT
    pre-deploy-hook: /path/to/script
    post-deploy-hook: echo "Yay" > ~/test.log
    stack-name-prefix: myproject
    #stack-name-suffix: myproject

    [stack: full]
    template: /Users/sebastian/tmp/hosts/webserver.json
    disable-rollback: true
    #timeout-in-minutes: 10
    parameters:
        version = 1.1.0,
        test tag = my test value
        key = value
    tags:
        project = Example project

    [bundle: webserver]
    pre-bundle-hook: git clone git://git.example.com/my.git
    post-bundle-hook: rm -rf my
    paths:
        /Users/sebastian/tmp/hosts/webserver
        /Users/sebastian/tmp/code/wordpress

    [bundle: database]
    pre-bundle-hook: /path/to/script
    paths: /Users/sebastian/tmp/hosts/database
    path-rewrites:
        /wordpress -> /var/www/wordpress
        /nginx -> /etc/nginx

    [bundle: app]
    pre-built-bundle: /Users/sebastian/build/app.zip


Section: ``general``
^^^^^^^^^^^^^^^^^^^

The configuration options here modify the behavior of Cumulus features that are
not environment or stack specific.

======================= ================== ======== ==========================================
Option                  Type               Required Comment
======================= ================== ======== ==========================================
``log-level``           String             No       Log level (one of: ``debug``, ``info``, ``warning`` and ``error``)
======================= ================== ======== ==========================================


Section: ``environment``
^^^^^^^^^^^^^^^^^^^^^^^

The following configuration options are available under ``[environment: env_name]``. The ``env_name`` is the identifier for the environment.

======================= ================== ======== ==========================================
Option                  Type               Required Comment
======================= ================== ======== ==========================================
``access-key-id``       String             Yes      AWS access key
``secret-access-key``   String             Yes      AWS secret access key
``bucket``              String             Yes      AWS S3 bucket to store bundles in
``region``              String             Yes      AWS region name, e.g. ``us-east-1``
``stacks``              List               Yes      List of stack names to deploy
``bundles``             List               Yes      List of bundles to build and upload
``version``             String             Yes      Environment version number
``pre-deploy-hook``     String             No       Command to execute before deployment
``post-deploy-hook``    String             No       Command to execute after deployment
``stack-name-prefix``   String             No       Prepend a prefix to the stack name
``stack-name-suffix``   String             No       Append a suffix to the stack name
======================= ================== ======== ==========================================


Section: ``stack``
^^^^^^^^^^^^^^^^^^

Options for the ``[stack: stack_name]`` configuration section.

======================= ================== ======== ==========================================
Option                  Type               Required Comment
======================= ================== ======== ==========================================
``template``            String             Yes      Path to local CloudFormation JSON file
``disable-rollback``    Boolean            No       Should CloudFormation rollbacks be disabled? Default: ``false``
``timeout-in-minutes``  Int                No       Set a CloudFormation creation timeout
``parameters``          Line sep. string   Yes      Parameters to send to the CloudFormation template. Should be on the form ``key = value``. Each parameter is separated by a new line.
``tags``                Line sep. string   No       CloudFormation tags to add to the stack
======================= ================== ======== ==========================================


Section: ``bundle``
^^^^^^^^^^^^^^^^^^^

Options for the ``[bundle: bundle_name]`` configuration section.

======================= ================== ======== ==========================================
Option                  Type               Required Comment
======================= ================== ======== ==========================================
``pre-bundle-hook``     String             No       Command to execute before bundling
``post-bundle-hook``    String             No       Command to execute after bundling
``paths``               Line sep. string   Yes      Paths to include in the bundle. Each path should be declared on a new line.
``pre-build-bundle``    String             No       Path to a pre-built bundle. This option will make the `paths` redundant.
======================= ================== ======== ==========================================

Command line options
--------------------

Below is a listing of the ``cumulus`` command line options.
::

    usage: cumulus [-h] [-e ENVIRONMENT] [-s STACKS] [--version VERSION]
                   [--parameters PARAMETERS] [--config CONFIG] [--cumulus-version]
                   [--bundle] [--deploy] [--deploy-without-bundling] [--events]
                   [--list] [--validate-templates] [--undeploy]

    Cumulus cloud management tool

    optional arguments:
      -h, --help            show this help message and exit

    General options:
      -e ENVIRONMENT, --environment ENVIRONMENT
                            Environment to use
      -s STACKS, --stacks STACKS
                            Comma separated list of stacks to deploy. Default
                            behavior is to deploy all stacks for an environment
      --version VERSION     Environment version number. Overrides the version
                            value from the configuration file
      --parameters PARAMETERS
                            CloudFormation parameters. On the form: stack_name:par
                            ameter_name=value,stack_name=parameter_name=value
      --config CONFIG       Path to configuration file.
      --cumulus-version     Print cumulus version number

    Actions:
      --bundle              Build and upload bundles to AWS S3
      --deploy              Bundle and deploy all stacks in the environment
      --deploy-without-bundling
                            Deploy all stacks in the environment, without bundling
                            first
      --events              List events for the stack
      --list                List stacks for each environment
      --validate-templates  Validate all templates for the environment
      --undeploy            Undeploy (DELETE) all stacks in the environment

Stack naming
------------

CloudFormation stacks must have a unique name. Cumulus will therefore combine the environment name and the stack name from the configuration. The pattern is ``<environment>-<stack_name>``. So, if your environment is called ``production`` and your stack is ``webservers`` then your CloudFormation stack will be named ``production-webservers``.

Deploying an environment
------------------------

To deploy (create or update) an environment run the following:
::

    cumulus --environment production --deploy

| **Note!**
| When running on Windows, you'll need to invoke Cumulus with ``python cumulus``

If you only want to deploy a certain stack, use the ``--stacks`` option.

Undeploying (deleting) an environment
-------------------------------------

If you want to remove a whole environment, you'll undeploy it by running:
::

    cumulus --environment production --undeploy

| **WARNING!** This will delete all resources defined in your CloudFormation
| template

| **Note!**
| When running on Windows, you'll need to invoke Cumulus with ``python cumulus``

Note on environment specific configuration
------------------------------------------

Cumulus supports environment specific configuration, if you are using
``cumulus`` to create your bundles. This is useful if you have one
``httpd.conf`` for production purposes and another for testing. To have files
that should only be included in specific environments, prefix them with
`__cumulus-environment__filename`.

So for example: `__cumulus-production__nginx.conf` is the `nginx.conf` for
the production environment.

