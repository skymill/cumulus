# Cumulus Cloud Tools

## Configuration

All configuration is read form `/etc/cumulus-cloud-tools.conf` or `~/.cumulus-cloud-tools.conf`.  This is an example configuration:

    [environment: stage]
    access-key-id: <AWS ACCESS KEY>
    secret-access-key: <AWS SECRET KEY>
    region: eu-west-1
    bucket: se.skymill.bundles

    [environment: production]
    access-id: <AWS ACCESS KEY>
    secret-access-key: <AWS SECRET KEY>
    region: eu-west-1
    bucket: se.skymill.bundles

Each environment will require a separate configuration section. In the example above, we have one `stage` environment and one `production` environment.
