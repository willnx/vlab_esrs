# -*- coding: UTF-8 -*-
"""
Entry point logic for available backend worker tasks
"""
from celery import Celery
from celery.utils.log import get_task_logger

from vlab_esrs_api.lib import const
from vlab_esrs_api.lib.worker import vmware

app = Celery('esrs', backend='rpc://', broker=const.VLAB_MESSAGE_BROKER)
logger = get_task_logger(__name__)
logger.setLevel(const.VLAB_ESRS_LOG_LEVEL.upper())


@app.task(name='esrs.show')
def show(username):
    """Obtain basic information about ESRS

    :Returns: Dictionary

    :param username: The name of the user who wants info about their ESRS instances
    :type username: String
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        info = vmware.show_esrs(username)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
        resp['content'] = info
    return resp


@app.task(name='esrs.create')
def create(username, machine_name, image, network):
    """Deploy a new instance of ESRS

    :Returns: Dictionary

    :param username: The name of the user who wants to create a new ESRS
    :type username: String

    :param machine_name: The name of the new instance of ESRS
    :type machine_name: String

    :param image: The image/version of ESRS to create
    :type image: String

    :param network: The name of the network to connect the new instance up to
    :type network: String
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        resp['content'] = vmware.create_esrs(username, machine_name, image, network)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    logger.info('Task complete')
    return resp


@app.task(name='esrs.delete')
def delete(username, machine_name):
    """Destroy an instance of ESRS

    :Returns: Dictionary

    :param username: The name of the user who wants to create a new ESRS instance
    :type username: String

    :param machine_name: The name of the instance of esrs
    :type machine_name: String
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    try:
        vmware.delete_esrs(username, machine_name)
    except ValueError as doh:
        logger.error('Task failed: {}'.format(doh))
        resp['error'] = '{}'.format(doh)
    else:
        logger.info('Task complete')
    return resp


@app.task(name='esrs.image')
def image():
    """Obtain a list of the available images/versions of ESRS that can be deployed

    :Returns: Dictionary

    :param username: The name of the user who wants to create a new default gateway
    :type username: String
    """
    resp = {'content' : {}, 'error': None, 'params': {}}
    logger.info('Task starting')
    resp['content'] = {'image': vmware.list_images()}
    logger.info('Task complete')
    return resp
