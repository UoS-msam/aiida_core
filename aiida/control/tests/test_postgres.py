# -*- coding: utf-8 -*-
"""Unit tests for postgres database maintenance functionality"""
import unittest

from pgtest.pgtest import PGTest

from aiida.control.postgres import Postgres


class PostgresTest(unittest.TestCase):
    """Test the public API provided by the `Postgres` class"""

    def setUp(self):
        """Set up a temporary database cluster for testing potentially destructive operations"""
        self.pg_test = PGTest()
        self.postgres = Postgres(
            port=self.pg_test.port, interactive=False, quiet=True)
        self.dbuser = 'aiida'
        self.dbpass = 'password'
        self.dbname = 'aiida_db'

    def _setup_postgres(self):
        self.postgres.dbinfo = self.pg_test.dsn
        self.postgres.determine_setup()

    def test_determine_setup_fail(self):
        self.postgres.set_port('11111')
        self.postgres.determine_setup()
        self.assertFalse(self.postgres.pg_execute)

    def test_determine_setup_success(self):
        self._setup_postgres()
        self.assertTrue(self.postgres.pg_execute)

    def test_setup_fail_callback(self):
        """Make sure `determine_setup` works despite wrong initial values in case of correct callback"""

        def correct_setup(interactive, dbinfo):  # pylint: disable=unused-argument
            return self.pg_test.dsn

        self.postgres.set_port(11111)
        self.postgres.set_setup_fail_callback(correct_setup)
        self.postgres.determine_setup()
        self.assertTrue(self.postgres.pg_execute)

    def test_create_drop_db_user(self):
        """Check creating and dropping a user works"""
        self._setup_postgres()
        self.postgres.create_dbuser(self.dbuser, self.dbpass)
        self.assertTrue(self.postgres.dbuser_exists(self.dbuser))
        self.postgres.drop_dbuser(self.dbuser)
        self.assertFalse(self.postgres.dbuser_exists(self.dbuser))

    def test_create_drop_db(self):
        """Check creating & destroying a database"""
        self._setup_postgres()
        self.postgres.create_dbuser(self.dbuser, self.dbpass)
        self.postgres.create_db(self.dbuser, self.dbname)
        self.assertTrue(self.postgres.db_exists(self.dbname))
        self.postgres.drop_db(self.dbname)
        self.assertFalse(self.postgres.db_exists(self.dbname))
