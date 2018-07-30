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
        fake_get_info.return_value = {'worked': True, 'note': "ESRS=3.28"}

        output = vmware.show_esrs(username='alice')
        expected = {'myESRS': {'worked': True, 'note': "ESRS=3.28"}}

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
        fake_get_info.return_value = {'worked': True, 'note': "noIIQ=3.28"}

        output = vmware.show_esrs(username='alice')
        expected = {}

        self.assertEqual(output, expected)

    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'vCenter')
    def test_create_esrs(self, fake_vCenter, fake_deploy_from_ova, fake_get_info, fake_Ova, fake_consume_task):
        """``create_esrs`` returns the new esrs's info when everything works"""
        fake_Ova.return_value.networks = ['vLabNetwork']
        fake_get_info.return_value = {'worked' : True}
        fake_vCenter.return_value.__enter__.return_value.networks = {'someNetwork': vmware.vim.Network(moId='asdf')}

        output = vmware.create_esrs(username='alice',
                                         machine_name='myESRS',
                                         image='3.28',
                                         network='someNetwork')
        expected = {'worked': True}

        self.assertEqual(output, expected)

    @patch.object(vmware, 'consume_task')
    @patch.object(vmware, 'Ova')
    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware.virtual_machine, 'deploy_from_ova')
    @patch.object(vmware, 'vCenter')
    def test_create_esrs_value_error(self, fake_vCenter, fake_deploy_from_ova, fake_get_info, fake_Ova, fake_consume_task):
        """``create_esrs`` raises ValueError if supplied with a non-existing network"""
        fake_Ova.return_value.networks = ['vLabNetwork']
        fake_get_info.return_value = {'worked' : True}
        fake_vCenter.return_value.__enter__.return_value.networks = {'someNetwork': vmware.vim.Network(moId='asdf')}

        with self.assertRaises(ValueError):
            vmware.create_esrs(username='alice',
                                    machine_name='myESRS',
                                    image='3.28',
                                    network='not a thing')

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'vCenter')
    def test_delete_esrs(self, fake_vCenter, fake_power, fake_consume_task, fake_get_info):
        """``delete_esrs`` powers off the VM then deletes it"""
        fake_vm = MagicMock()
        fake_vm.name = 'myESRS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'worked': True, 'note': "ESRS=3.28"}
        vmware.delete_esrs(username='alice', machine_name='myESRS')

        self.assertTrue(fake_power.called)
        self.assertTrue(fake_vm.Destroy_Task.called)

    @patch.object(vmware.virtual_machine, 'get_info')
    @patch.object(vmware, 'consume_task')
    @patch.object(vmware.virtual_machine, 'power')
    @patch.object(vmware, 'vCenter')
    def test_delete_esrs_value_error(self, fake_vCenter, fake_power, fake_consume_task, fake_get_info):
        """``delete_esrs`` raises ValueError if no esrs machine has the supplied name"""
        fake_vm = MagicMock()
        fake_vm.name = 'myESRS'
        fake_folder = MagicMock()
        fake_folder.childEntity = [fake_vm]
        fake_vCenter.return_value.__enter__.return_value.get_by_name.return_value = fake_folder
        fake_get_info.return_value = {'worked': True, 'note': "ESRS=3.28"}

        with self.assertRaises(ValueError):
            vmware.delete_esrs(username='alice', machine_name='not a thing')

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


if __name__ == '__main__':
    unittest.main()
