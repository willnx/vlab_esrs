# -*- coding: UTF-8 -*-
"""
A suite of tests for the HTTP API schemas
"""
import unittest

from jsonschema import Draft4Validator, validate, ValidationError
from vlab_esrs_api.lib.views import esrs


class TestESRSViewSchema(unittest.TestCase):
    """A set of test cases for the schemas of /api/1/inf/esrs"""

    def test_post_schema(self):
        """The schema defined for POST is valid"""
        try:
            Draft4Validator.check_schema(esrs.ESRSView.POST_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_delete_schema(self):
        """The schema defined for DELETE is valid"""
        try:
            Draft4Validator.check_schema(esrs.ESRSView.DELETE_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_get_schema(self):
        """The schema defined for GET is valid"""
        try:
            Draft4Validator.check_schema(esrs.ESRSView.GET_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_images_schema(self):
        """The schema defined for GET on /images is valid"""
        try:
            Draft4Validator.check_schema(esrs.ESRSView.IMAGES_SCHEMA)
            schema_valid = True
        except RuntimeError:
            schema_valid = False

        self.assertTrue(schema_valid)

    def test_delete(self):
        """The DELETE schema happy path test"""
        body = {'name': "myESRS"}
        try:
            validate(body, esrs.ESRSView.DELETE_SCHEMA)
            ok = True
        except ValidationError:
            ok = False

        self.assertTrue(ok)

    def test_delete_required(self):
        """The DELETE schema requires the parameter 'name'"""
        body = {}
        try:
            validate(body, esrs.ESRSView.DELETE_SCHEMA)
            ok = False
        except ValidationError:
            ok = True

        self.assertTrue(ok)

    def test_post(self):
        """The POST schema happy path test"""
        body = {'name': "myESRS", 'network': "someNetwork", 'image': "3.28"}
        try:
            validate(body, esrs.ESRSView.POST_SCHEMA)
            ok = True
        except ValidationError:
            ok = False

        self.assertTrue(ok)

    def test_post_name_required(self):
        """The POST schema requires the 'name' parameter"""
        body = { 'network': "someNetwork", 'image': "3.28"}
        try:
            validate(body, esrs.ESRSView.POST_SCHEMA)
            ok = False
        except ValidationError:
            ok = True

        self.assertTrue(ok)

    def test_post_network_required(self):
        """The POST schema requires the 'network' parameter"""
        body = { 'name': "myESRS", 'image': "3.28"}
        try:
            validate(body, esrs.ESRSView.POST_SCHEMA)
            ok = False
        except ValidationError:
            ok = True

        self.assertTrue(ok)

    def test_post_image_required(self):
        """The POST schema requires the 'image' parameter"""
        body = { 'name': "myESRS", 'network': "someNetwork"}
        try:
            validate(body, esrs.ESRSView.POST_SCHEMA)
            ok = False
        except ValidationError:
            ok = True

        self.assertTrue(ok)


if __name__ == '__main__':
    unittest.main()
