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


class TestCaseUsers(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        confDir = os.getcwd().replace("tests", "data\\")
        with open(confDir + "config.txt") as f:
            config = json.load(f)
        self.dataBase = PyMySQLAdapter(config)

    def test_addUser(self):
        user = {"name": "Гоша", "password": "Aloha"}
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
        self.dataBase.close()


class TestCaseTags(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        confDir = os.getcwd().replace("tests", "data\\")
        with open(confDir + "config.txt") as f:
            config = json.load(f)
        self.dataBase = PyMySQLAdapter(config)

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
        self.dataBase.close()


class TestCaseStaff(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        confDir = os.getcwd().replace("tests", "data\\")
        with open(confDir + "config.txt") as f:
            config = json.load(f)
        self.dataBase = PyMySQLAdapter(config)

    def test_addStaffUser(self):
        user = {"name": "Алексей", "password": "Aloha"}
        self.assertEqual(self.dataBase.intoTable("users", user), True)
        staff = {"user_id": self.dataBase.getKeyLastElement("users")}
        self.assertEqual(self.dataBase.intoTable("staff", staff), True)

        user = {"name": "Максим", "password": "Aloha"}
        self.assertEqual(self.dataBase.intoTable("users", user), True)
        staff = {"user_id": self.dataBase.getKeyLastElement("users")}
        self.assertEqual(self.dataBase.intoTable("staff", staff), True)
        self.assertEqual(self.dataBase.intoTable("staff", staff), False)

    def test_getStaffUser(self):
        staff = self.dataBase.getTable("staff", ["users", "id", "user_id"])
        self.assertEqual(staff[0]['name'], 'Алексей')

    def test_truncateStaff(self):
        self.dataBase.truncateTable("staff")
        self.dataBase.truncateTable("users")
        self.dataBase.close()


class TestCaseSongTag(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        confDir = os.getcwd().replace("tests", "data\\")
        with open(confDir + "config.txt") as f:
            config = json.load(f)
        self.dataBase = PyMySQLAdapter(config)

    def test1_addSongUser(self):
        user = {"name": "Алексей"}
        self.assertEqual(self.dataBase.intoTable("users", user), True)
        song = {"name": "Intro", "owner_id": self.dataBase.getKeyLastElement("users")}
        self.assertEqual(self.dataBase.intoTable("songs", song), True)

    def test2_addSongTag(self):
        tags = [{"name": "METAL"}, {"name": "PUNK"}, {"name": "HARD"}]
        for tag in tags:
            self.assertEqual(self.dataBase.intoTable("tags", tag), True)
        songtotag = {"song_id": self.dataBase.getKeyLastElement("songs"), "tag_name": "HARD"}
        self.assertEqual(self.dataBase.intoTable("songtotag", songtotag), True)
        songtotag = {"song_id": self.dataBase.getKeyLastElement("songs"), "tag_name": "PUNK"}
        self.assertEqual(self.dataBase.intoTable("songtotag", songtotag), True)

    def test3_getSongTag(self):
        tags = self.dataBase.getTable("songtotag", ["songs", "id", "song_id"])
        self.assertEqual(tags[0]['song_id'], 1)
        self.assertEqual(tags[0]['tag_name'], 'HARD')
        self.assertEqual(tags[1]['song_id'], 1)
        self.assertEqual(tags[1]['tag_name'], 'PUNK')

    def test4_truncateSongTag(self):
        self.dataBase.truncateTable("tags")
        self.dataBase.truncateTable("songs")
        self.dataBase.truncateTable("users")
        self.dataBase.truncateTable("songtotag")
        self.dataBase.close()


if __name__ == '__main__':
    unittest.main()
