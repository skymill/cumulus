""" Bundling functions """
import logging
import os
import os.path
import tarfile

logger = logging.getLogger(__name__)


def build_bundles(config):
    """ Build bundles for the environment

    :type config: config_handler.Configuration
    :param config: Configuration object
    """
    for bundle in config.get_bundles():
        for path in config.get_bundle_paths(bundle):
            logger.info('Building bundle {}'.format(bundle))
            logger.debug('Bundle paths: {}'.format(', '.join(
                config.get_bundle_paths(bundle))))
            _bundle(
                bundle,
                config.get_environment(),
                config.get_environment_option('version'),
                config.get_bundle_paths(bundle))


def _bundle(bundle_name, environment, version, paths):
    """ Create bundle

    :type bundle: str
    :param bundle: Bundle name
    :type environment: str
    :param environment: Environment name
    :type version: str
    :param version: Version number
    :type paths: list
    :param paths: List of paths to include
    """
    # Define a filter to modify the tar object
    def tar_filter(tarinfo):
        """ Modify the tar object.

        See: http://docs.python.org/library/tarfile.html#tarfile.TarInfo
        """
        # Make sure that the files are placed in the / root dir
        #tarinfo.name = tarinfo.name.replace(
        #    '{}/'.format(self.base_path[1:]),
        #    '')

        # Change user permissions on all files
        tarinfo.uid = 0
        tarinfo.gid = 0
        tarinfo.uname = 'root'
        tarinfo.gname = 'root'

        return tarinfo

    def exclusion_filter(filename):
            """ Filter excluding files for other environments """
            if os.path.basename(filename).startswith('__cumulus-'):
                cnt = len(os.path.basename(filename).split(
                    '__cumulus-{}__'.format(environment)))

                if cnt == 2:
                    return False
                else:
                    logger.debug('Excluding file {}'.format(filename))
                    return True
            else:
                return False

    bundle = '{}/target/cct-bundle-{}-{}-{}.tar.bz2'.format(
        os.curdir,
        environment,
        version,
        bundle_name)

    # Ensure that the bundle target exists
    if not os.path.exists(os.path.dirname(bundle)):
        os.makedirs(os.path.dirname(bundle))

    tar = tarfile.open(bundle, 'w:bz2')
    for path in paths:
        tar.add(
            path,
            exclude=exclusion_filter,
            filter=tar_filter)
    tar.close()
    logger.info('Wrote bundle to {}'.format(bundle))
