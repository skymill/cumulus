Command line options
====================

Below is a listing of the Cumulus command line options.
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
