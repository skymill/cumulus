""" Connection handler """
import boto

from logger import logger


def connect_aws_s3(access_key_id, secret_access_key):
    """ Connect to AWS S3

    :type access_key_id: str
    :param access_key_id: AWS access key
    :type secret_access_key: str
    :param secret_access_key: AWS secret accesskey
    :returns: boto.s3.connection
    """
    logger.debug('Connecting to AWS S3')
    return boto.connect_s3(
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key)
