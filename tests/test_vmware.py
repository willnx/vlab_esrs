# -*- coding: UTF-8 -*-
"""
A suite of tests for the functions in vmware.py
"""
import unittest
from unittest.mock import patch, MagicMock

from vlab_esrs_api.lib.worker import vmware


class TestVMware(unittest.TestCase):
    """A set of test cases for the vmware.py module"""
    @classmethod
    def setUpClass(cls):
        vmware.logger = MagicMock()

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'vCenter')
    def test_show_esrs(self, fake_vCenter, fake_get_info):
        """``show_esrs`` returns a dictionary when everything works as expected"""
        fake_vm = MagicMock()
        fake_vm.name = 'myESRS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta' : {'component': 'ESRS',
                                                'created': 1234,
                                                'version': '3.28',
                                                'configured': False,
                                                'generation': 1}}

        output = vmware.show_esrs(username='alice')
        expected = {'myESRS': {'meta' : {'component': 'ESRS',
                                         'created': 1234,
                                         'version': '3.28',
                                         'configured': False,
                                         'generation': 1}}}

        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'vCenter')
    def test_show_esrs_nothing(self, fake_vCenter, fake_get_info):
        """``show_esrs`` returns an empty dictionary no esrs is found"""
        fake_vm = MagicMock()
        fake_vm.name = 'myESRS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta' : {'component': 'otherThing',
                                                'created': 1234,
                                                'version': '3.28',
                                                'configured': False,
                                                'generation': 1}}

        output = vmware.show_esrs(username='alice')
        expected = {}

        self.assertEqual(output, expected)

    @patch.object(vmware.virtual_machine, 'set_meta')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'vCenter')
    def test_create_esrs(self, fake_vCenter, fake_deploy_from_ova, fake_get_info, fake_Ova, fake_consume_task, set_meta):
        """``create_esrs`` returns the new esrs's info when everything works"""
        fake_logger = MagicMock()
        fake_deploy_from_ova.return_value.name = 'myESRS'
        fake_Ova.return_value.networks = ['vLabNetwork']
        fake_get_info.return_value = {'worked' : True}
        fake_vCenter.return_value.__enter__.return_value.networks = {'someNetwork': vmware.vim.Network(moId='asdf')}

        output = vmware.create_esrs(username='alice',
                                    machine_name='myESRS',
                                    image='3.28',
                                    network='someNetwork',
                                    logger=fake_logger)
        expected = {'myESRS': {'worked': True}}

        self.assertEqual(output, expected)

    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'vCenter')
    def test_create_esrs_value_error(self, fake_vCenter, fake_deploy_from_ova, fake_get_info, fake_Ova, fake_consume_task):
        """``create_esrs`` raises ValueError if supplied with a non-existing network"""
        fake_logger = MagicMock()
        fake_Ova.return_value.networks = ['vLabNetwork']
        fake_get_info.return_value = {'worked' : True}
        fake_vCenter.return_value.__enter__.return_value.networks = {'someNetwork': vmware.vim.Network(moId='asdf')}

        with self.assertRaises(ValueError):
            vmware.create_esrs(username='alice',
                                    machine_name='myESRS',
                                    image='3.28',
                                    network='not a thing',
                                    logger=fake_logger)

    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'vCenter')
    def test_create_esrs_bad_image(self, fake_vCenter, fake_deploy_from_ova, fake_get_info, fake_Ova, fake_consume_task):
        """``create_esrs`` raises ValueError if supplied with a non-existing image to deploy"""
        fake_logger = MagicMock()
        fake_Ova.side_effect = FileNotFoundError('testing')
        fake_get_info.return_value = {'worked' : True}
        fake_vCenter.return_value.__enter__.return_value.networks = {'someNetwork': vmware.vim.Network(moId='asdf')}

        with self.assertRaises(ValueError):
            vmware.create_esrs(username='alice',
                                    machine_name='myESRS',
                                    image='a.3.sdf',
                                    network='someNetwork',
                                    logger=fake_logger)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'vCenter')
    def test_delete_esrs(self, fake_vCenter, fake_power, fake_consume_task, fake_get_info):
        """``delete_esrs`` powers off the VM then deletes it"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'myESRS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'meta' : {'component': 'ESRS',
                                                'created': 1234,
                                                'version': '3.28',
                                                'configured': False,
                                                'generation': 1}}

        vmware.delete_esrs(username='alice', machine_name='myESRS', logger=fake_logger)

        self.assertTrue(fake_power.called)
        self.assertTrue(fake_vm.Destroy_Task.called)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'vCenter')
    def test_delete_esrs_value_error(self, fake_vCenter, fake_power, fake_consume_task, fake_get_info):
        """``delete_esrs`` raises ValueError if no esrs machine has the supplied name"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'myESRS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'worked': True, 'note': "ESRS=3.28"}

        with self.assertRaises(ValueError):
            vmware.delete_esrs(username='alice', machine_name='not a thing', logger=fake_logger)

    @patch.object(vmware.os, 'listdir')
    def test_list_images(self, fake_listdir):
        """``list_images`` returns a list of images when everything works as expected"""
        fake_listdir.return_value = ['esrs_3.28.ova']

        output = vmware.list_images()
        expected = ['3.28']

        self.assertEqual(output, expected)

    def test_convert_name(self):
        """``convert_name`` defaults to converting versions to images"""
        output = vmware.convert_name('3.28')
        expected = 'ESRS_3.28.ova'

        self.assertEqual(output, expected)

    def test_convert_name_to_version(self):
        """``convert_name`` can convert from versions to image names"""
        output = vmware.convert_name('ESRS_3.28.ova', to_version=True)
        expected = '3.28'

        self.assertEqual(output, expected)


    @patch.object(vmware.virtual_machine, 'change_network')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_update_network(self, fake_vCenter, fake_consume_task, fake_get_info, fake_change_network):
        """``update_network`` Returns None upon success"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'myESRS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_vCenter.return_value.__enter__.return_value.networks = {'wootTown' : 'someNetworkObject'}
        fake_get_info.return_value = {'meta': {'component' : 'ESRS'}}

        result = vmware.update_network(username='pat',
                                       machine_name='myESRS',
                                       new_network='wootTown')

        self.assertTrue(result is None)

    @patch.object(vmware.virtual_machine, 'change_network')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_update_network_no_vm(self, fake_vCenter, fake_consume_task, fake_get_info, fake_change_network):
        """``update_network`` Raises ValueError if the supplied VM doesn't exist"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'myESRS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_vCenter.return_value.__enter__.return_value.networks = {'wootTown' : 'someNetworkObject'}
        fake_get_info.return_value = {'meta': {'component' : 'ESRS'}}

        with self.assertRaises(ValueError):
            vmware.update_network(username='pat',
                                  machine_name='SomeOtherMachine',
                                  new_network='wootTown')

    @patch.object(vmware.virtual_machine, 'change_network')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'vCenter')
    def test_update_network_no_network(self, fake_vCenter, fake_consume_task, fake_get_info, fake_change_network):
        """``update_network`` Raises ValueError if the supplied new network doesn't exist"""
        fake_logger = MagicMock()
        fake_vm = MagicMock()
        fake_vm.name = 'myESRS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_vCenter.return_value.__enter__.return_value.networks = {'wootTown' : 'someNetworkObject'}
        fake_get_info.return_value = {'meta': {'component' : 'ESRS'}}

        with self.assertRaises(ValueError):
            vmware.update_network(username='pat',
                                  machine_name='myESRS',
                                  new_network='dohNet')



if __name__ == '__main__':
    unittest.main()
