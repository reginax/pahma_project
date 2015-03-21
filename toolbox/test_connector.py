__author__ = 'Julian Jaffe'

import unittest
import connector
from common import cspace
from os import path
from cspace_django_site import settings


class ConnectorTestCase(unittest.TestCase):
    def test_connection(self):
        # No module level setUp function, so just run this first
        config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), "testConnector")
        self.assertEqual(connector.testDB(config), "OK")

    def test_setQuery(self):
        pass


if __name__ == '__main__':
    unittest.main()
