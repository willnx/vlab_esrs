# -*- coding: UTF-8 -*-
"""Business logic for backend worker tasks"""
import time
import random
import os.path
from celery.utils.log import get_task_logger
from vlab_inf_common.vmware import vCenter, Ova, vim, virtual_machine, consume_task

from vlab_esrs_api.lib import const


logger = get_task_logger(__name__)
logger.setLevel(const.VLAB_ESRS_LOG_LEVEL.upper())


def show_esrs(username):
    """Obtain basic information about esrs

    :Returns: Dictionary

    :param username: The user requesting info about their ESRS instances
    :type username: String
    """
    info = {}
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        esrs_vms = {}
        for vm in folder.childEntity:
            info = virtual_machine.get_info(vcenter, vm)
            kind, version = info['note'].split('=')
            if kind == 'ESRS':
                esrs_vms[vm.name] = info
    return esrs_vms


def delete_esrs(username, machine_name):
    """Unregister and destroy a user's esrs

    :Returns: None

    :param username: The user who wants to delete an instance of ESRS
    :type username: String

    :param machine_name: The name of the VM to delete
    :type machine_name: String
    """
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER, \
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        folder = vcenter.get_by_name(name=username, vimtype=vim.Folder)
        for entity in folder.childEntity:
            if entity.name == machine_name:
                info = virtual_machine.get_info(vcenter, entity)
                kind, version = info['note'].split('=')
                if kind == 'ESRS':
                    logger.debug('powering off VM')
                    virtual_machine.power(entity, state='off')
                    delete_task = entity.Destroy_Task()
                    logger.debug('blocking while VM is being destroyed')
                    consume_task(delete_task)
                    break
        else:
            raise ValueError('No {} named {} found'.format('ESRS', machine_name))


def create_esrs(username, machine_name, image, network):
    """Deploy a new instances of ESRS

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
    with vCenter(host=const.INF_VCENTER_SERVER, user=const.INF_VCENTER_USER,
                 password=const.INF_VCENTER_PASSWORD) as vcenter:
        image_name = convert_name(image)
        logger.info(image_name)
        try:
            ova = Ova(os.path.join(const.VLAB_ESRS_IMAGES_DIR, image_name))
        except FileNotFoundError:
            error = "Invalid version of ESRS supplied: {}".format(image)
            raise ValueError(error)
        try:
            network_map = vim.OvfManager.NetworkMapping()
            network_map.name = ova.networks[0]
            try:
                network_map.network = vcenter.networks[network]
            except KeyError:
                raise ValueError('No such network named {}'.format(network))
            the_vm = virtual_machine.deploy_from_ova(vcenter, ova, [network_map],
                                                     username, machine_name, logger)
        finally:
            ova.close()
        spec = vim.vm.ConfigSpec()
        spec.annotation = 'ESRS={}'.format(image)
        task = the_vm.ReconfigVM_Task(spec)
        consume_task(task)
        return virtual_machine.get_info(vcenter, the_vm)


def list_images():
    """Obtain a list of available versions of ESRS that can be created

    :Returns: List
    """
    images = os.listdir(const.VLAB_ESRS_IMAGES_DIR)
    images = [convert_name(x, to_version=True) for x in images]
    return images


def convert_name(name, to_version=False):
    """This function centralizes converting between the name of the OVA, and the
    version of software it contains.

    The naming convention for the OVA ESRS_<version>.ova, like ESRS_3.28.ova

    :param name: The thing to covert
    :type name: String

    :param to_version: Set to True to covert the name of an OVA to the version
    :type to_version: Boolean
    """
    if to_version:
        return name.split('_')[-1].rstrip('.ova')
    else:
        return 'ESRS_{}.ova'.format(name)
