# from unittest import mock
#
# from dataiku_api_manager.auth import Auth
# from tests.mock_api_client import MockDssClient
#
#
# @mock.patch('dataiku_api_manager.auth.dataikuapi.DSSClient', return_value=MockDssClient())
# def test_auth_class(mock_dss_client):
#     auth = Auth("foourl", "footoken")
#     client = auth.dss_client()
#     assert client.check_mock()
