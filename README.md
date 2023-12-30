# KISB - Kitchen Island Status Bot
## What is this?
This is a bot that will post the status of the KI Network to a Discord embed. As well as using a custom command to post the status of the KI Network in response to a command.

## Developers
- JStuffNZ - Main Developer


## Codebase

```
.
├── .github                      // Github related files.
|   └── workflows
|       └── docker-publish.yml   // Github Action to publish to Github Packages.
└── src                          // Source code.
    ├── cache                    // Static directory, where cache files are placed during runtime.
    ├── data                     // Database & log store. Bound to a volume when running in Docker.
    ├── modules                  // Modules that are loaded at runtime.
    ├── _kisb.py                 // Bot base.
    ├── bot.py                   // Main cog file.
    └── main.py                  // Entrypoint.
```

## Version: 
- 1.3.0

### Required Environment Variables

| Variable | Description | Default |
| --- | --- | --- |
| TOKEN | Discord Bot Token | `None` |
| SCPSL_ID | Server ID for the Lobby List API. See https://support.scpslgame.com/article/61 | `None` |
| SCPSL_KEY | Server Key for the Lobby List API. See https://support.scpslgame.com/article/61 | `None` |
| TZ | Timezone for the bot. See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones | `Pacific/Auckland` |
| LOG_LEVEL | Logging level for the bot. Can be either `info` or `debug` | `info` |



<b>PLEASE NOTE:
Some functions should ideally be run overnight when the server is empty. These will run at 0600 (6AM) in the timezone specified.

See the ./modPlaytimeTracker/_tasks.py/start() function for what and when these tasks are run.</b>

### Docker Volume Paths
"/worker/data" - Main Datastore
