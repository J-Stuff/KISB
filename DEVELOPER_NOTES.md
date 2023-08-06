# Database Structures
## Cache
JSON

    "minecraft": {
        "playercount": INT
    },
    "pz": {
        "online": INT,
        "game": STR,
        "name": STR,
        "players: INT,
        "max_players": INT,
        "map": STR,
        "vac_secure": BOOL,
        "server_type": STR,
        "os": STR,
        "password_required": BOOL
    },
    "rust": {
        "online": INT,
        "game": STR,
        "name": STR,
        "players: INT,
        "max_players": INT,
        "map": STR,
        "vac_secure": BOOL,
        "server_type": STR,
        "os": STR,
        "password_required": BOOL
    },
    "scpsl": [
        "Server {NAME} - "XX/XX",
        "Server {NAME} - "XX/XX",
        "Server {NAME} - "XX/XX",
    ]


## Database
JSON

    "embedMessage": INT,   - ID of Embed Message
    "embedChannel": INT,   - ID of Embed Message Channel
    "minecraftLU": INT,    - Minecraft Last Updated Timestamp
    "zomoidLU": INT,       - Project Zomboid Last Updated Timestamp
    "rustLU": INT,         - Rust Last Updated Timestamp
    "scpslLU": INT         - SCP:SL Last Updated Timestamp

