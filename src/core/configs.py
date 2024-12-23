from enum import StrEnum
import json

class Config:
    # This class needs to remain thread-safe at all times.

    class Build(StrEnum):
        Version = (json.load(open("./version.json", 'r')))["version"]
        Author = "https://github.com/J-Stuff"
    
    class Paths:
        data_path = None

        cache_path = None

        @classmethod
        def set_data_path(cls, path):
            cls.data_path = path

        @classmethod
        def get_data_path(cls):
            return cls.data_path
            
        @classmethod
        def set_cache_path(cls, path):
            cls.cache_path = path

        @classmethod
        def get_cache_path(cls):
            return cls.cache_path
            

    class Static:
        
        required_loggers = ["boot", "slapi", "bot", "schedule"]
        
        server_translations = { # These need to be the {"SERVER ID": "DISPLAY NAME"}
            "60048": "Official 1",  # Port: 7777
            "68070": "Official 2",  # Port: 7778
            "70516": "Community 3", # Port: 7779
            "79856": "Community 4", # Port: 7780,
            # "81948": "SCP:SL Public Beta 1", # Port: 7775
            # "82935": "SCP:SL Public Beta 2" # Port: 7776

        }

    class Discord(StrEnum):
        emoji_HighConnection = "<:HighConnection:1136504263204421732>"
        emoji_NoConnection = "<:NoConnection:1136504297853550744>"
        emoji_ServerFull = "<:ServerFull:1137640034439286826>"

        asset_SCPslLogo = "https://cdn.discordapp.com/attachments/1136583178191114270/1136583568475291648/vn5K5O6d_400x400.jpg"

    class DiscordUsers:
        authorized_users = [946234576538304603]