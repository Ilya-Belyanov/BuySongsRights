import pymysql.cursors


def checkInputTable(func):
    def wrapper(cls, *args, **kwargs):
        if args[0] not in cls.tables():
            return None
        else:
            return func(cls, *args, **kwargs)
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
            return [row[f"Tables_in_{self.config['db'].lower()}"] for row in cursor]

    def getTable(self, tbl: str, innerJoin=None, where: str = "") -> list:
        if innerJoin is None:
            innerJoin = []
        if len(innerJoin) != 0:
            sql = f"INNER JOIN {innerJoin[0]} ON {innerJoin[0]}.{innerJoin[1]} = {tbl}.{innerJoin[2]}"
        else:
            sql = ""
        whr = f"WHERE {where}" if where else ""
        sql += whr
        return self.tableRequest(tbl, "SELECT * FROM",  sql)

    def getColumns(self, tbl: str) -> list:
        return self.tableRequest(tbl, "SHOW COLUMNS FROM")

    def getIndex(self, tbl: str) -> dict:
        answer = self.tableRequest(tbl, "SHOW INDEX FROM")
        return answer[0] if answer is not None else None

    def getCreateTable(self, tbl: str) -> dict:
        answer = self.tableRequest(tbl, "SHOW CREATE TABLE")
        return answer[0] if answer is not None else None

    def getKeyLastElement(self, tbl: str, id: str = "id"):
        with self.connection.cursor() as cursor:
            sql = f"SELECT {id} FROM {tbl} ORDER BY {id} DESC LIMIT 1"
            cursor.execute(sql)
            return [row[id] for row in cursor][0]

    @checkInputTable
    def intoTable(self, tbl: str, data: dict) -> bool:
        with self.connection.cursor() as cursor:
            fields = ','.join([key.lower() for key in data.keys()])
            args = ','.join([self.fieldArg(data[key]) for key in data.keys()])
            sql = f"INSERT INTO {tbl} ({fields}) VALUES ({args})"
            try:
                cursor.execute(sql)
                self.connection.commit()
                return True
            except Exception as e:
                print(e)
                return False

    @staticmethod
    def fieldArg(arg):
        if isinstance(arg, int):
            return str(arg)
        elif isinstance(arg, str):
            return "'" + arg + "'"

    @checkInputTable
    def deleteFromTable(self, tbl: str, where: str = ""):
        with self.connection.cursor() as cursor:
            whr = f"WHERE {where}" if where else ""
            sql = f"DELETE FROM {tbl} {whr}"
            cursor.execute(sql)
            self.connection.commit()

    @checkInputTable
    def truncateTable(self, tbl: str):
        with self.connection.cursor() as cursor:
            sql = "SET FOREIGN_KEY_CHECKS=0"
            cursor.execute(sql)
            sql = f"TRUNCATE TABLE {tbl}"
            cursor.execute(sql)
            sql = "SET FOREIGN_KEY_CHECKS=1"
            cursor.execute(sql)
            self.connection.commit()

    @checkInputTable
    def tableRequest(self, tbl: str, command: str, postCommand: str = "") -> list:
        with self.connection.cursor() as cursor:
            cursor.execute(f"{command} {tbl} {postCommand}")
            return [row for row in cursor]

    @checkInputTable
    def renameTable(self, tbl: str, newTable: str) -> bool:
        with self.connection.cursor() as cursor:
            cursor.execute(f" RENAME TABLE {tbl} TO {newTable}")
        return True

    def close(self) -> bool:
        self.connection.close()
        return True
