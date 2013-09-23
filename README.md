# Cumulus Cloud Tools

## Requirements

Cumulus requires Python 2.7 and `boto`. Please install requirements with

    sudo pip install -r cumulus/requirements.txt

## Configuration

All configuration is read form `/etc/cumulus.conf`, `~/.cumulus.conf` and , `./cumulus.conf` in order. This is an example configuration:

    [environment: stage]
    access-key-id: <AWS ACCESS KEY>
    secret-access-key: <AWS SECRET KEY>
    bucket: se.skymill.bundles
    region: eu-west-1
    stacks: full
    bundles: webserver, database
    version: 1.0.0-SNAPSHOT

    [stack: full]
    template: /Users/sebastian/tmp/hosts/webserver.json
    disable-rollback: true

    [bundle: webserver]
    paths:
        /Users/sebastian/tmp/hosts/webserver,
        /Users/sebastian/tmp/code/wordpress

    [bundle: database]
    paths: /Users/sebastian/tmp/hosts/database

All configuration options are required to be set.

## Deployment workflow

First off you need to create a bundle. Run

    cumulus --environment production --bundle

This will bundle and upload all your software to AWS S3. The next step is to update CloudFormation. That is done with the `--deploy` command:

    cumulus --environment production --deploy

Cumulus will create or update the CloudFormation stacks as needed.
