Bundle structure
================

Bundles are `.tar.bz2` files.

    infrastructure/
         etc/
            applicationX/
                __ct-stage__app.conf
                __ct-production__app.conf
                timeouts.conf
            nginx/
                nginx.conf
            skymill-init.d/
                00-install-dependencies.sh
        usr/
            local/
                bin/
                    update_host.py
    applications/
        applicationX/
            usr/
                lib/
                    tomcat7/
                        webapps/
                            app.war


Skymill tool suite
==================

`skymill-tool-suite/sts.conf`

    [environment: stage]
    aws-access-id: <AWS ACCESS KEY>
    aws-secret-access-key: <AWS SECRET ACCESS KEY>
    region: eu-west-1

    [environment: production]
    aws-access-id: <AWS ACCESS KEY>
    aws-secret-access-key: <AWS SECRET ACCESS KEY>
    region: eu-west-1

Bundle a release
----------------

    skymill-tool-suite/bundler.py --base ../hosts --environment stage
    skymill-tool-suite/bundler.py --base ../hosts/webserver/.skymill/get_app.sh --environment stage
    skymill-tool-suite/bundler.py --base ../hosts/backend --environment stage
    skymill-tool-suite/stack_manager.py --template ../cf-templates/skymill.json --environment stage --create
