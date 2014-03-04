Cumulus release notes
=====================

1.1.0
-----

**Release date:** 2014-03-04

- Cumulus is now comparing the md5 checksums after uploads to ensure file integrity (#115 <https://github.com/skymill/cumulus/issues/115>`__)
- CloudFormation output is now shown after template deployment and if you issue the ``--outputs`` command (`#114 <https://github.com/skymill/cumulus/issues/114>`__)
- Cumulus will only upload bundles to S3 if it does not exist or if the md5 checksum is updated (`#99 <https://github.com/skymill/cumulus/issues/99>`__)
- Bug fix: `--cumulus-version is broken #116 <https://github.com/skymill/cumulus/issues/116>`__
1.0.3
-----

**Release date:** 2014-02-28

- Fixed licensing. Removed old references to proprietary

1.0.2
-----

**Release date:** 2014-02-24

- `Ensure removed backslashes in Windows rewrites #113 <https://github.com/skymill/cumulus/issues/113>`__

1.0.1
-----

**Release date:** 2014-02-24

- `Update default cumulus.conf paths for Windows #112 <https://github.com/skymill/cumulus/issues/112>`__
- Minor fixes

1.0.0 (First open source release)
---------------------------------

**Release date:** 2014-02-20

- `Write event status reason in terminal output #110 <https://github.com/skymill/cumulus/issues/110>`__
- `Make it possible to force undeployment #105 <https://github.com/skymill/cumulus/issues/105>`__
- `Break out Cumulus Bundle Handler to it's own module #90 <https://github.com/skymill/cumulus/issues/90>`__
- Bug fix: `Catch missing pre-built bundles cleanly #109 <https://github.com/skymill/cumulus/issues/109>`__
- Bug fix: `Proper error message when CBH can't find the config #101 <https://github.com/skymill/cumulus/issues/101>`__
- Bug fix: `Old update events are shown when new updates are performed #79 <https://github.com/skymill/cumulus/issues/79>`__

0.8.0
-----

**Release date:** 2014-01-31

This release is the first Cumulus release to support Windows. Windows is supported
both as client system and a target system.

- `Support for running Cumulus on a Windows client #80 <https://github.com/skymill/cumulus/issues/80>`__
- `Support using pre-bundled software #82 <https://github.com/skymill/cumulus/issues/82>`__
- `Create clean error when command line options are missing #85 <https://github.com/skymill/cumulus/issues/85>`__
- `Windows support in Cumulus Bundle Handler #83 <https://github.com/skymill/cumulus/issues/83>`__
- `Custom extraction path in Cumulus Bundle Handler #84 <https://github.com/skymill/cumulus/issues/84>`__
- `Support zip, tar.gz and tar.bz2 in Cumulus Bundle Handler #88 <https://github.com/skymill/cumulus/issues/88>`__

0.7.0
-----

**Release date:** 2014-01-28

- `Support deployment of certain stacks only #70 <https://github.com/skymill/cumulus/issues/70>`__
- `Add support for stack creation timeouts #76 <https://github.com/skymill/cumulus/issues/76>`__
- `Ensure stack deletion order #74 <https://github.com/skymill/cumulus/issues/74>`__
- `Support CloudFormation stack tags #78 <https://github.com/skymill/cumulus/issues/78>`__
- `Update for all stacks fail if one stack fails #73 <https://github.com/skymill/cumulus/issues/73>`__
- `Log level config in CBH #64 <https://github.com/skymill/cumulus/issues/64>`__
- `Ugly error when trying to deploy unconfigured environment #71 <https://github.com/skymill/cumulus/issues/71>`__
- `Stack deletion events are not handled properly #72 <https://github.com/skymill/cumulus/issues/72>`__
- `Catch ctrl-c interruptions cleanly #75 <https://github.com/skymill/cumulus/issues/75>`__

0.6.4
-----

**Release date:** 2014-01-21

- `Fix odd syntax in parameters option #69 <https://github.com/skymill/cumulus/issues/69>`__

0.6.3
-----

**Release date:** 2014-01-20

- `It is not possible to run --deploy with a cumulus.conf without bundles #67 <https://github.com/skymill/cumulus/issues/67>`__
- Minor fix: Enhanced event log output

0.6.2
-----

**Release date:** 2013-01-20

- `Exclude all other configuration files if --config is set #68 <https://github.com/skymill/cumulus/issues/68>`__

0.6.1
-----

**Release date:** 2013-12-02

- `All cumulus-init.d scripts run both before and after bundle deploy #66 <https://github.com/skymill/cumulus/issues/66>`__
- `Widen output formatting for Logical ID #65 <https://github.com/skymill/cumulus/issues/65>`__

0.6.0
-----

**Release date:** 2013-11-29

Major features:

- `Global cumulus command and documentation generation #56 <https://github.com/skymill/cumulus/issues/56>`__
- `Support multiple bundle types on hosts #52 <https://github.com/skymill/cumulus/issues/52>`__
- `Support CloudFormation templates served from S3 #58 <https://github.com/skymill/cumulus/issues/58>`__
- `Cumulus bundle handler should support both start and kill scripts in init.d #49 <https://github.com/skymill/cumulus/issues/49>`__
- `Generate Python docs with autodoc #59 <https://github.com/skymill/cumulus/issues/59>`__
- `Added Sphinx documentation #48 <https://github.com/skymill/cumulus/issues/48>`__
- `Set CF parameters on command line #61 <https://github.com/skymill/cumulus/issues/61>`__
- `Log level is now configurable #63 <https://github.com/skymill/cumulus/issues/63>`__

Minor improvements:

- `Stop writing to target dir, use tempfile instead #62 <https://github.com/skymill/cumulus/issues/62>`__
- `Harmonize CBH option names #53 <https://github.com/skymill/cumulus/issues/53>`__
- `Restructured project folders #54 <https://github.com/skymill/cumulus/issues/54>`__
- `Bundle Cumlus in a Python egg #55 <https://github.com/skymill/cumulus/issues/55>`__
- `Remove docs from README #57 <https://github.com/skymill/cumulus/issues/57>`__
- `Read versions from one place #60 <https://github.com/skymill/cumulus/issues/60>`__
- `Bug: paths should be \n separated, not comma separated #51 <https://github.com/skymill/cumulus/issues/51>`__

0.5.0
-----

**Release date:** 2013-10-28

- `Clean up host on bundle update #38 <https://github.com/skymill/cumulus/issues/38>`__
- `Cumulus bundle handler should use Python logging #40 <https://github.com/skymill/cumulus/issues/40>`__
- `Get rid of Cumulus metadata.conf and make the bundle handler self-contained #41 <https://github.com/skymill/cumulus/issues/41>`__
- `Remove __name__ from logging output #42 <https://github.com/skymill/cumulus/issues/42>`__
- `Filter events when creating/updating/deleting stacks #43 <https://github.com/skymill/cumulus/issues/43>`__
- `Add function for listing stack events on command line #45 <https://github.com/skymill/cumulus/issues/45>`__
- `Enhance status output when waiting for stack change to complete #46 <https://github.com/skymill/cumulus/issues/46>`__

0.4.0
-----

**Release date:** 2013-10-25

- `Path prefix in bundles #36 <https://github.com/skymill/cumulus/issues/36>`__

0.3.1
-----

**Release date:** 2013-10-24

- `Error handling stack delete status #34 <https://github.com/skymill/cumulus/issues/34>`__
- `Running --deploy on existing stack fails #35 <https://github.com/skymill/cumulus/issues/35>`__
- `Initial stack creation fails when using --deploy-without-bundling #33 <https://github.com/skymill/cumulus/issues/33>`__
- `Bundle type missing in Cumulus metadata #37 <https://github.com/skymill/cumulus/issues/37>`__

0.3.0
-----

**Release date:** 2013-10-11

- `Write hooks for Cumulus deployments #26 <https://github.com/skymill/cumulus/issues/26>`__
- `Wait until stack is done updating/creating #20 <https://github.com/skymill/cumulus/issues/20>`__
- `Specify config file location as input parameter #30 <https://github.com/skymill/cumulus/issues/30>`__
- `Set environment version as input parameter #28 <https://github.com/skymill/cumulus/issues/28>`__
- `Make it possible to environment prefix whole directories #10 <https://github.com/skymill/cumulus/issues/10>`__
- `Create shortcut for both bundling and deploying #27 <https://github.com/skymill/cumulus/issues/27>`__
- `Ask before delete when running --undeploy #24 <https://github.com/skymill/cumulus/issues/24>`__
- `Ensure that boto is available for cumulus bundle handler #25 <https://github.com/skymill/cumulus/issues/25>`__
- `Remove skymill reference from JSON template #23 <https://github.com/skymill/cumulus/issues/23>`__
- `Remove unnecessary stack name in metadata #22 <https://github.com/skymill/cumulus/issues/22>`__
- `Remove unnecessary bundle-type in metadata #21 <https://github.com/skymill/cumulus/issues/21>`__

0.2.3
-----

**Release date:** 2013-09-26

- `Symbolic links should be dereferenced in bundles #19 <https://github.com/skymill/cumulus/issues/19>`__
- `Current directory is added to bundle #18 <https://github.com/skymill/cumulus/issues/18>`__

0.2.2
-----

**Release date:** 2013-09-25

- `Mismatch in metadata and cumulus_bundle_handler.py #16 <https://github.com/skymill/cumulus/issues/16>`__
- Various bug fixes in the bundle handler system

0.2.1
-----

**Release date:** 2013-09-25

- `Cumulus CF namespace conflicts with some rules #15 <https://github.com/skymill/cumulus/issues/15>`__

0.2.0
-----

**Release date:** 2013-09-24

- `Custom parameters in CloudFormation #14 <https://github.com/skymill/cumulus/issues/14>`__
- `Expand ~ in config template & bundle paths #12 <https://github.com/skymill/cumulus/issues/12>`__
- `Read the bucket name from configuration in CF template #11 <https://github.com/skymill/cumulus/issues/11>`__
- `Exception when building non-configured bundle #13 <https://github.com/skymill/cumulus/issues/13>`__

0.1.1
-----

**Release date:** 2013-09-23

- `Prefixes for prefixed files is not removed in bundle #9 <https://github.com/skymill/cumulus/issues/9>`__

0.1.0
-----

**Release date:** 2013-09-23

Initial release with some basic functions and concepts.

- Basic bundling and stack management features implemented


Cumulus Bundle Handler release notes
====================================

1.0.2
-----

**Release date:** 2014-02-28

- Fixed licensing. Removed old references to proprietary

1.0.1
-----

**Release date:** 2014-02-21

- Bugfix: `Bundle extraction paths are not determined properly #111 <https://github.com/skymill/cumulus/issues/111>`__
