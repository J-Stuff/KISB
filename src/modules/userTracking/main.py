# No exportables in this file (except scheduled tasks)

from modules.slAPI.data import read_cache
from core.configs import Config
from typing import Literal
import sqlite3


class Database():
    data_path = f"{Config().Paths.get_data_path()}/users"
    user_db_path = f"{data_path}/users.db"
    playtime_db_path = f"{data_path}/playtime.db"
    sessions_db_path = f"{data_path}/sessions.db"

    @classmethod
    def get_userDB_cursor(cls) -> sqlite3.Cursor:
        path = cls.user_db_path
        con = sqlite3.connect(path)
        return con.cursor()
    
    @classmethod
    def get_playtimeDB_cursor(cls) -> sqlite3.Cursor:
        path = cls.playtime_db_path
        con = sqlite3.connect(path)
        return con.cursor()
    
    @classmethod
    def get_sessionsDB_cursor(cls) -> sqlite3.Cursor:
        path = cls.sessions_db_path
        con = sqlite3.connect(path)
        return con.cursor()
    
    @classmethod
    def create_db_if_not_present(cls, db: Literal["user", "playtime", "session"]):

        if db == "user":
            cursor = cls.get_userDB_cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "users" (
                "ID"     TEXT NOT NULL UNIQUE,
                "NAME"   TEXT NOT NULL,
                "LAST_SEEN"  INTEGER NOT NULL,
                "LAST_SEEN_WHERE"    INTEGER NOT NULL,
                "USERNAME_HISTORY"   TEXT DEFAULT '[]',
                PRIMARY KEY("ID")
                ); """).close()
        elif db == "playtime":
            cursor = cls.get_playtimeDB_cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "playtime" (
                "ID"    TEXT NOT NULL UNIQUE,
                "TODAY" INTEGER DEFAULT 0,
                "WEEK"  INTEGER DEFAULT 0,
                "MONTH" INTEGER DEFAULT 0,
                PRIMARY KEY("ID")
                ); """).close()
        elif db == "session":
            cursor = cls.get_sessionsDB_cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "sessions" (
                "ID"    TEXT NOT NULL,
                "SESSION_START" INTEGER,
                "SESSION_END"   INTEGER,
                "LAST_SEEN" INTEGER,
                "SESSION_LEN"   INTEGER,
                PRIMARY KEY("ID")
                ); """).close()
        else:
            pass


    @classmethod
    def add_user_playtime(cls, users:list[str]):
        """Add 1 min of playtime to a list of USER_IDs

        Args:
            users (list[str]): List of User ID strings
        """
        cursor = cls.get_playtimeDB_cursor()
        for user in users:
            # Get user to ensure they are in the DB. Add them if they are not
            result = cursor.execute("SELECT user FROM users")





def store_online_users():
    pass # (for now)