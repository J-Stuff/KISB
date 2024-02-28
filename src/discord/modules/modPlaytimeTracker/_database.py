import sqlite3, logging, time, io, json, datetime, typing

logger = logging.getLogger("main")
'''
game_id is usually the steam64 id of the user, Except if they are northwood staff, in which case it is "USER@northwood"

if game_id is an @northwood id, then last_nick is returned as `null` by the API, and must be set to their northwood nickname
'''

class Database:
    sqlite_location = "./data/playtimeData/data.sqlite"
    meta_location = "./data/playtimeData/meta.json"

    class Meta():                

        def get_fp_read(self) -> io.TextIOWrapper:
            return open(Database.meta_location, "r")
        
        def get_fp_write(self) -> io.TextIOWrapper:
            return open(Database.meta_location, "w") 
        

        def get_meta(self) -> dict:
            with self.get_fp_read() as f:
                return json.load(f)
            
        def set_meta(self, new_meta:dict) -> None:
            with self.get_fp_write() as f:
                json.dump(new_meta, f)
            return
        
        def get_last_update(self) -> datetime.datetime:
            return datetime.datetime.fromtimestamp(self.get_meta()['last_update'])
        
        def get_last_tickovers(self, return_datetime:bool=False) ->list[datetime.datetime]:
            return [datetime.datetime.fromtimestamp(self.get_meta()['last_tickover_d']), datetime.datetime.fromtimestamp(self.get_meta()['last_tickover_w']), datetime.datetime.fromtimestamp(self.get_meta()['last_tickover_m'])]
            
        def set_last_update(self) -> None:
            now = int(time.time())
            meta = self.get_meta()
            meta['last_update'] = now
            self.set_meta(meta)

        def set_last_tickover(self, type:typing.Literal["d", "w", "m"]) -> None:
            now = int(time.time())
            meta = self.get_meta()
            meta[f'last_tickover_{type}'] = now
            self.set_meta(meta)
            return
        
    def verify_update_timing_for_playtime(self) -> bool:
        meta = self.Meta()
        now = datetime.datetime.now()
        if now - meta.get_last_update() >= datetime.timedelta(minutes=1):
            return True
        else:
            return False
        
    def verify_update_timing_for_tickover(self, type:typing.Literal["d", "w"]) -> bool:
        meta = self.Meta()
        now = datetime.datetime.now()
        if type == "d":
            if now - meta.get_last_tickovers()[0] >= datetime.timedelta(days=1):
                return True
            else:
                return False
        elif type == "w":
            if now - meta.get_last_tickovers()[1] >= datetime.timedelta(days=7):
                return True
            else:
                return False


    def __init__(self):
        try:
            self.conn = sqlite3.connect(Database.sqlite_location)
            self.c = self.conn.cursor()
            self.c.execute("""CREATE TABLE IF NOT EXISTS mods (
                "game_id"	            TEXT NOT NULL UNIQUE,
                "last_nick"	            TEXT NOT NULL,
                "discord_id"         	TEXT NOT NULL UNIQUE,
                "last_seen"	            INTEGER NOT NULL,
                "playtime_today"    	INTEGER NOT NULL,
                "playtime_this_week"	INTEGER NOT NULL,
                "playtime_last_week"	INTEGER NOT NULL,
                "playtime_this_month"	INTEGER NOT NULL,
                "playtime_last_month"	INTEGER NOT NULL,
                PRIMARY KEY("game_id")
            )""")
            self.conn.commit()
        except:
            logger.exception("Failed to connect to database")
            exit("Failed to connect to database")

    # Add a moderator to the database
    def add_mod(self, game_id:str, discord_id:str) -> None:
        self.c.execute("INSERT INTO mods (game_id, last_nick, discord_id, last_seen, playtime_today, playtime_this_week, playtime_last_week, playtime_this_month, playtime_last_month) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (game_id, "", discord_id, 0, 0, 0, 0, 0, 0))
        self.conn.commit()
        return

    # Fetch a user from the database from their game_id
    def get_mod(self, game_id:str) -> tuple[str, str, str, int, int, int, int, int, int]|None:
        """Return data for a mod in the database

        Args:
            game_id (str): The unique game id of the mod

        Returns:
            tuple[str, str, str, int, int, int, int, int]: Returns a tuple containing the `game_id, last_nick, discord_id, last_seen, playtime_today, playtime_this_week, playtime_last_week, playtime_this_month, playtime_last_month` in that order
        """
        logger.debug(f"Fetching mod with game_id: {game_id}")
        self.c.execute("SELECT * FROM mods WHERE game_id=?", (game_id,))
        result = self.c.fetchone()
        logger.debug(result)
        if result is None:
            return None
        else:
            return result
    
    # Fetch a user from the database from their discord_id
    def get_mod_from_discord_id(self, discord_id:str) -> tuple[str, str, str, int, int, int, int, int, int]|None:
        """Return data for a mod in the database

        Args:
            discord_id (str): The unique discord id of the mod

        Returns:
            tuple[str, str, str, int, int, int, int, int]: Returns a tuple containing the `game_id, last_nick, discord_id, last_seen, playtime_today, playtime_this_week, playtime_last_week, playtime_this_month, playtime_last_month` in that order
        """
        self.c.execute("SELECT * FROM mods WHERE discord_id=?", (discord_id,))
        result = self.c.fetchone()
        if result is None:
            return None
        else:
            return result
            
    
    # Remove a user from the database from their game_id
    def remove_mod(self, game_id:str) -> None:
        self.c.execute("DELETE FROM mods WHERE game_id=?", (game_id,))
        self.conn.commit()
        return
    
    # Update a game_id in the database with a new discord_id
    def update_mod_discord_id(self, game_id:str, new_discord_id:str) -> None:
        self.c.execute("UPDATE mods SET discord_id=? WHERE game_id=?", (new_discord_id, game_id))
        self.conn.commit()
        return
    
    # Update a game_id in the database with a new game_id
    def update_mod_game_id(self, game_id:str, new_game_id:str) -> None:
        self.c.execute("UPDATE mods SET game_id=? WHERE game_id=?", (new_game_id, game_id))
        self.conn.commit()
        return

    # Get the game ids from all moderators in the database and return them as a list
    def get_all_moderator_game_ids(self) -> list[str]:
        self.c.execute("SELECT game_id FROM mods")
        return [x[0] for x in self.c.fetchall()]
    
    # Get all the discord ids from all moderators in the database and return them as a list
    def get_all_moderator_discord_ids(self) -> list[str]:
        """Returns a list of all mod ID's (as STRINGS)

        Returns:
            list[str]: List of all mod ID's in the database
        """
        self.c.execute("SELECT discord_id FROM mods")
        return [x[0] for x in self.c.fetchall()]
    

    # Add 1 to the integer value of playtime_today, playtime_this_week and playtime_this_month for the user with the specified game_id
    def add_playtime(self, game_id:str) -> None:
        while not self.verify_update_timing_for_playtime():
            time.sleep(1)
        self.c.execute("SELECT playtime_today, playtime_this_week, playtime_this_month FROM mods WHERE game_id=?", (game_id,))
        playtime_today, playtime_this_week, playtime_this_month = self.c.fetchone()
        self.c.execute("UPDATE mods SET playtime_today=?, playtime_this_week=?, playtime_this_month=? WHERE game_id=?", (playtime_today+1, playtime_this_week+1, playtime_this_month+1, game_id))
        self.conn.commit()
        self.Meta().set_last_update()
        return
    
    # Update the last_seen value to the current UNIX timestamp for the user with the specified game_id
    def update_last_seen(self, game_id:str) -> None:
        self.c.execute("UPDATE mods SET last_seen=? WHERE game_id=?", (int(time.time()), game_id))
        self.conn.commit()
        return
    
    # Update the last_nick value to a new value for the user with the specified game_id
    def update_last_nick(self, game_id:str, new_nick:str) -> None:
        self.c.execute("UPDATE mods SET last_nick=? WHERE game_id=?", (new_nick, game_id))
        self.conn.commit()
        return
    

    def reset_playtime_today(self) -> None:
        while not self.verify_update_timing_for_tickover("d"):
            time.sleep(1)
        self.c.execute("UPDATE mods SET playtime_today=0")
        self.conn.commit()
        return
    
    def tickover_playtime_week(self) -> None:
        while not self.verify_update_timing_for_tickover("w"):
            time.sleep(1)
        self.c.execute("UPDATE mods SET playtime_last_week=playtime_this_week, playtime_this_week=0")
        self.conn.commit()
        return
    
    def tickover_playtime_month(self) -> None:
        self.c.execute("UPDATE mods SET playtime_last_month=playtime_this_month, playtime_this_month=0")
        self.conn.commit()
        return