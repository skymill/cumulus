# Cumulus

Cumulus is a deployment tool used to deploy and maintain environments built with AWS CloudFormation. Cumulus will help you bundle your code and configuration and unpack the bundle to new instances on CloudFormation.

## Installation

Checkout the code and run

    make install

`cumulus` will now be available as a global command


## Generate documentation

Cumulus docs are generated using Sphinx. Generate documentation using


    make gen-docs

The HTML output is stored under `docs/_build/html`.


## Release notes

**NEXT**

- [Ensure stack deletion order #74](https://github.com/skymill/cumulus/issues/74)
- [Update for all stacks fail if one stack fails #73](https://github.com/skymill/cumulus/issues/73)
- [Ugly error when trying to deploy unconfigured environment #71](https://github.com/skymill/cumulus/issues/71)
- [Stack deletion events are not handled properly #72](https://github.com/skymill/cumulus/issues/72)

**0.6.4 (2014-01-21)**

- [Fix odd syntax in parameters option #69](https://github.com/skymill/cumulus/issues/69)

**0.6.3 (2014-01-20)**

- [It is not possible to run `--deploy` with a `cumulus.conf` without bundles #67](https://github.com/skymill/cumulus/issues/67)
- Minor fix: Enhanced event log output

**0.6.2 (2013-01-20)**

- [Exclude all other configuration files if `--config` is set #68](https://github.com/skymill/cumulus/issues/68)

**0.6.1 (2013-12-02)**

- [All `cumulus-init.d` scripts run both before and after bundle deploy #66](https://github.com/skymill/cumulus/issues/66)
- [Widen output formatting for Logical ID #65](https://github.com/skymill/cumulus/issues/65)

**0.6.0 (2013-11-29)**

Major features:
- [Global `cumulus` command and documentation generation #56](https://github.com/skymill/cumulus/issues/56)
- [Support multiple bundle types on hosts #52](https://github.com/skymill/cumulus/issues/52)
- [Support CloudFormation templates served from S3 #58](https://github.com/skymill/cumulus/issues/58)
- [Cumulus bundle handler should support both start and kill scripts in init.d #49](https://github.com/skymill/cumulus/issues/49)
- [Generate Python docs with autodoc #59](https://github.com/skymill/cumulus/issues/59)
- [Added Sphinx documentation #48](https://github.com/skymill/cumulus/issues/48)
- [Set CF parameters on command line #61](https://github.com/skymill/cumulus/issues/61)
- [Log level is now configurable #63](https://github.com/skymill/cumulus/issues/63)

Minor improvements:
- [Stop writing to `target` dir, use `tempfile` instead #62](https://github.com/skymill/cumulus/issues/62)
- [Harmonize CBH option names #53](https://github.com/skymill/cumulus/issues/53)
- [Restructured project folders #54](https://github.com/skymill/cumulus/issues/54)
- [Bundle Cumlus in a Python egg #55](https://github.com/skymill/cumulus/issues/55)
- [Remove docs from README #57](https://github.com/skymill/cumulus/issues/57)
- [Read versions from one place #60](https://github.com/skymill/cumulus/issues/60)
- [Bug: paths should be \n separated, not comma separated #51](https://github.com/skymill/cumulus/issues/51)

**0.5.0 (2013-10-28)**

- [Clean up host on bundle update #38](https://github.com/skymill/cumulus/issues/38)
- [Cumulus bundle handler should use Python logging #40](https://github.com/skymill/cumulus/issues/40)
- [Get rid of Cumulus metadata.conf and make the bundle handler self-contained #41](https://github.com/skymill/cumulus/issues/41)
- [Remove `__name__` from logging output #42](https://github.com/skymill/cumulus/issues/42)
- [Filter events when creating/updating/deleting stacks #43](https://github.com/skymill/cumulus/issues/43)
- [Add function for listing stack events on command line #45](https://github.com/skymill/cumulus/issues/45)
- [Enhance status output when waiting for stack change to complete #46](https://github.com/skymill/cumulus/issues/46)

**0.4.0 (2013-10-25)**

- [Path prefix in bundles #36](https://github.com/skymill/cumulus/issues/36)

**0.3.1 (2013-10-24)**

- [Error handling stack delete status #34](https://github.com/skymill/cumulus/issues/34)
- [Running `--deploy` on existing stack fails #35](https://github.com/skymill/cumulus/issues/35)
- [Initial stack creation fails when using `--deploy-without-bundling` #33](https://github.com/skymill/cumulus/issues/33)
- [Bundle type missing in Cumulus metadata #37](https://github.com/skymill/cumulus/issues/37)

**0.3.0 (2013-10-11)**

- [Write hooks for Cumulus deployments #26](https://github.com/skymill/cumulus/issues/26)
- [Wait until stack is done updating/creating #20](https://github.com/skymill/cumulus/issues/20)
- [Specify config file location as input parameter #30](https://github.com/skymill/cumulus/issues/30)
- [Set environment version as input parameter #28](https://github.com/skymill/cumulus/issues/28)
- [Make it possible to environment prefix whole directories #10](https://github.com/skymill/cumulus/issues/10)
- [Create shortcut for both bundling and deploying #27](https://github.com/skymill/cumulus/issues/27)
- [Ask before delete when running `--undeploy` #24](https://github.com/skymill/cumulus/issues/24)
- [Ensure that boto is available for cumulus bundle handler #25](https://github.com/skymill/cumulus/issues/25)
- [Remove skymill reference from JSON template #23](https://github.com/skymill/cumulus/issues/23)
- [Remove unnecessary stack name in metadata #22](https://github.com/skymill/cumulus/issues/22)
- [Remove unnecessary bundle-type in metadata #21](https://github.com/skymill/cumulus/issues/21)

**0.2.3 (2013-09-26)**

- [Symbolic links should be dereferenced in bundles #19](https://github.com/skymill/cumulus/issues/19)
- [Current directory is added to bundle #18](https://github.com/skymill/cumulus/issues/18)

**0.2.2 (2013-09-25)**

- [Mismatch in metadata and cumulus_bundle_handler.py #16](https://github.com/skymill/cumulus/issues/16)
- Various bug fixes in the bundle handler system

**0.2.1 (2013-09-25)**

- [Cumulus CF namespace conflicts with some rules #15](https://github.com/skymill/cumulus/issues/15)

**0.2.0 (2013-09-24)**

- [Custom parameters in CloudFormation #14](https://github.com/skymill/cumulus/issues/14)
- [Expand ~ in config template & bundle paths #12](https://github.com/skymill/cumulus/issues/12)
- [Read the bucket name from configuration in CF template #11](https://github.com/skymill/cumulus/issues/11)
- [Exception when building non-configured bundle #13](https://github.com/skymill/cumulus/issues/13)

**0.1.1 (2013-09-23)**

- [Prefixes for prefixed files is not removed in bundle #9](https://github.com/skymill/cumulus/issues/9)

**0.1.0 (2013-09-23)**

Initial release with some basic functions and concepts.

- Basic bundling and stack management features implemented
