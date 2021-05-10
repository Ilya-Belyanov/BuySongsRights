import json
import os

from src.obj.pymysql_adapter import PyMySQLAdapter


class ConsoleDB:
    class Operations:
        TABLES = 0
        SHOW_TABLE = 1
        SHOW_COLUMNS_TABLE = 2
        SHOW_INDEX_TABLE = 3
        SHOW_CREATE_TABLE = 4
        RENAME_TABLE = 5
        CLOSE = 9

    # Commands with use only name database
    CommandsDB = {
                  Operations.TABLES: PyMySQLAdapter.tables,
                  Operations.CLOSE: PyMySQLAdapter.close
                 }

    # Commands with use only name of exist table
    CommandsTable = {
                     Operations.SHOW_TABLE: PyMySQLAdapter.getTable,
                     Operations.SHOW_COLUMNS_TABLE: PyMySQLAdapter.getColumns,
                     Operations.SHOW_INDEX_TABLE: PyMySQLAdapter.getIndex,
                     Operations.SHOW_CREATE_TABLE: PyMySQLAdapter.getCreateTable,
                     }

    def __init__(self):
        confDir = os.getcwd() + "\\data\\"
        with open(confDir + "config.txt") as f:
            config = json.load(f)
        self.dataBase = PyMySQLAdapter(config)
        print("Connect Successful!!!")

    def run(self):
        while True:
            print("\nChoice command:\n" +
                  f"{self.Operations.TABLES} - Show tables\n" +
                  f"{self.Operations.SHOW_TABLE} - Show table\n" +
                  f"{self.Operations.SHOW_COLUMNS_TABLE} - Show columns of table\n" +
                  f"{self.Operations.SHOW_INDEX_TABLE} - Show index of table\n" +
                  f"{self.Operations.SHOW_CREATE_TABLE} - Show create of table\n" +
                  f"{self.Operations.RENAME_TABLE} - Rename table\n" +
                  f"{self.Operations.CLOSE} - Close")
            try:
                command = int(input(": "))
            except ValueError:
                print("Enter number")
                continue
            print()
            if command in self.CommandsDB.keys():
                print(self.CommandsDB[command](self.dataBase))
                if command == self.Operations.CLOSE:
                    print("GoodBye")
                    break
            elif command in self.CommandsTable.keys():
                self.tableOperation(self.CommandsTable[command])
            elif command == self.Operations.RENAME_TABLE:
                self.renameTable()
            else:
                print("Wrong operation")

    def tableOperation(self, function):
        while True:
            command = input("Input name of table or !exit: ")
            if command == "!exit":
                break
            answer = function(self.dataBase, command)
            print(answer if answer else "Not such table or table is empty", end="\n\n")

    def renameTable(self):
        tbl = input("Input name of table or !exit: ")
        if tbl == "!exit":
            return
        newTable = input("Input new name of table or !exit: ")
        if newTable == "!exit":
            return
        print("Success" if self.dataBase.renameTable(tbl, newTable) else "Fail")


