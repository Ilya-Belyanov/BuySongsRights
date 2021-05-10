import unittest
import json
import os

from src.obj.pymysql_adapter import PyMySQLAdapter


class TestCaseDB(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        confDir = os.getcwd().replace("tests", "data\\")
        with open(confDir + "config.txt") as f:
            config = json.load(f)
        self.dataBase = PyMySQLAdapter(config)

    def test_getTables(self):
        tables = ["songs", "songtotag", "staff", "tags", "userbuysong", "users"]
        dbTables = self.dataBase.tables()
        for table in tables:
            self.assertEqual(table in dbTables, True)

    def test_addUser(self):
        user = {"name": "Алексей"}
        self.assertEqual(self.dataBase.intoTable("users", user), True)

    def test_deleteUser(self):
        users = self.dataBase.getTable("users")
        if len(users) != 0:
            where = "id = " + str(users[-1]["id"])
        else:
            where = ""
        self.dataBase.deleteFromTable("users", where=where)

    def test_truncateUser(self):
        self.dataBase.truncateTable("users")

    def test_addTags(self):
        tags = [{"name": "METAL"}, {"name": "PUNK"}, {"name": "HARD"}]
        for tag in tags:
            self.assertEqual(self.dataBase.intoTable("tags", tag), True)
        tags = [{"name": "METAL"}, {"name": "PUNK"}, {"name": "HARD"}]
        for tag in tags:
            self.assertEqual(self.dataBase.intoTable("tags", tag), False)

    def test_deleteTags(self):
        tags = self.dataBase.getTable("tags")
        if len(tags) >= 3:
            where = "name IN('" + tags[-1]["name"] + "', '" + tags[-2]["name"] + "', '" + tags[-3]["name"] + "')"
        else:
            where = ""
        self.dataBase.deleteFromTable("tags", where=where)

    def test_truncateTags(self):
        self.dataBase.truncateTable("tags")


if __name__ == '__main__':
    unittest.main()
