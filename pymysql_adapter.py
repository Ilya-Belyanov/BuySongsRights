import pymysql.cursors


def checkInputTable(func):
    def wrapper(cls, *args):
        if args[0] not in cls.tables():
            return None
        else:
            return func(cls, *args)
    return wrapper


class PyMySQLAdapter:
    def __init__(self, config: dict):
        self.config = config
        self.connection = pymysql.connect(host=config["host"],
                                          user=config["user"],
                                          password=config["password"],
                                          db=config["db"],
                                          charset=config["charset"],
                                          cursorclass=pymysql.cursors.DictCursor)

    def tables(self) -> list:
        with self.connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            return [row[f"Tables_in_{self.config['db']}"] for row in cursor]

    def getTable(self, tbl: str) -> list:
        return self.tableRequest(tbl, "SELECT * FROM")

    def getColumns(self, tbl: str) -> list:
        return self.tableRequest(tbl, "SHOW COLUMNS FROM")

    def getIndex(self, tbl: str) -> dict:
        answer = self.tableRequest(tbl, "SHOW INDEX FROM")
        return answer[0] if answer is not None else None

    def getCreateTable(self, tbl: str) -> dict:
        answer = self.tableRequest(tbl, "SHOW CREATE TABLE")
        return answer[0] if answer is not None else None

    @checkInputTable
    def tableRequest(self, tbl: str, command: str) -> list:
        with self.connection.cursor() as cursor:
            cursor.execute(f"{command} {tbl}")
            return [row for row in cursor]

    @checkInputTable
    def renameTable(self, tbl: str, newTable: str) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(f" RENAME TABLE {tbl} TO {newTable}")
        return True

    def close(self) -> bool:
        self.connection.close()
        return True
