# No exportables in this file (except scheduled tasks)

from modules.slAPI.data import read_cache
from core.configs import Config
from typing import Literal
import sqlite3
import logging

logger = logging.getLogger("user_tracker")


class Database():
    data_path = f"{Config().Paths.get_data_path()}/users"
    user_db_path = f"{data_path}/users.db"
    playtime_db_path = f"{data_path}/playtime.db"
    sessions_db_path = f"{data_path}/sessions.db"

    @classmethod
    def get_userDB_cursor(cls) -> tuple[sqlite3.Cursor, sqlite3.Connection]:
        path = cls.user_db_path
        con = sqlite3.connect(path)
        return con.cursor(), con
    
    @classmethod
    def get_playtimeDB_cursor(cls) -> tuple[sqlite3.Cursor, sqlite3.Connection]:
        path = cls.playtime_db_path
        con = sqlite3.connect(path)
        return con.cursor(), con
    
    @classmethod
    def get_sessionsDB_cursor(cls) -> tuple[sqlite3.Cursor, sqlite3.Connection]:
        path = cls.sessions_db_path
        con = sqlite3.connect(path)
        return con.cursor(), con
    
    @classmethod
    def create_db_if_not_present(cls, db: Literal["user", "playtime", "session"]):

        if db == "user":
            cursor, con = cls.get_userDB_cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "users" (
                "ID"     TEXT NOT NULL UNIQUE,
                "NAME"   TEXT NOT NULL,
                "LAST_SEEN"  INTEGER NOT NULL,
                "LAST_SEEN_WHERE"    INTEGER NOT NULL,
                "USERNAME_HISTORY"   TEXT DEFAULT '[]',
                PRIMARY KEY("ID")
                ); """).close()
            con.commit()
            con.close()
        elif db == "playtime":
            cursor, con = cls.get_playtimeDB_cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "playtime" (
                "ID"    TEXT NOT NULL UNIQUE,
                "TODAY" INTEGER DEFAULT 0,
                "WEEK"  INTEGER DEFAULT 0,
                "MONTH" INTEGER DEFAULT 0,
                PRIMARY KEY("ID")
                ); """).close()
            con.commit()
            con.close()
        elif db == "session":
            cursor, con = cls.get_sessionsDB_cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS "sessions" (
                "ID"    TEXT NOT NULL,
                "SESSION_START" INTEGER,
                "SESSION_END"   INTEGER,
                "LAST_SEEN" INTEGER,
                "SESSION_LEN"   INTEGER,
                PRIMARY KEY("ID")
                ); """).close()
            con.commit()
            con.close()
        else:
            pass

    @classmethod
    def add_user_to_playtime_db(cls, user:str):
        """Add a new user to the playtime DB.
        Checks to ensure the user does not already exist

        Args:
            user (str): Game ID of user (12345@steam, jstuff@northwood, jstuff#0@discord)
        """

        cursor, con = cls.get_playtimeDB_cursor()
        test = cursor.execute("SELECT \"{0}\" FROM playtime".format(user))
        test_result = test.fetchone()
        if test_result is not None:
            return
        cursor.execute("INSERT INTO playtime (ID) VALUES (\"{0}\")".format(user))
        con.commit()
        con.close()

        


    @classmethod
    def add_user_playtime(cls, users:list[str]):
        """Add 1 min of playtime to a list of USER_IDs

        Args:
            users (list[str]): List of User ID strings
        """
        cursor, con = cls.get_playtimeDB_cursor()
        updated_users = [] # Used as a catch to make sure we are not adding duplicate minutes to users who can appear twice (SCP:SL API buggy behavior)
        for user in users:
            if user in updated_users:
                logger.warning("The same user has appeared in the cache twice! This is probably because they switched servers close to the SCP:SL API poll for each server. I will ignore them to not add duplicate minutes to their playtime.")
                continue
            updated_users.append(user)

            # Get user to ensure they are in the DB. Add them if they are not
            result = cursor.execute("SELECT \"{0}\" FROM playtime".format(user))
            db_user = result.fetchone() # There should only ever be one user ID in the DB. If there isn't we have problems
            # ^ If exists, will return tuple
            if db_user == None:
                logger.debug(f"Could not find user ({user}) in the playtime DB. Adding them now.")
                cls.add_user_to_playtime_db(user)
                
                # Update the user result with them now in the database
                result = cursor.execute("SELECT \"{0}\" FROM playtime".format(user))
                db_user = result.fetchone()
            
            new_TODAY = int(db_user[1]) + 1 # Add 1 minute to TODAY
            new_WEEK = int(db_user[2]) + 1 # Add 1 minute to WEEK
            new_MONTH = int(db_user[3]) + 1 # Add 1 minute to MONTH
            cursor.execute("""UPDATE 'playtime' SET TODAY = {0}, WEEK = {1}, MONTH = {2} WHERE ID = '{3}'""".format(new_TODAY, new_WEEK, new_MONTH, user)) # Auto F-String plugin is being a BITCH on this line of code
        con.commit()
        con.close()







def store_online_users():
    pass # (for now)