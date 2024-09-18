# KISB - Kitchen Island Service Bot

KISB is a Service Bot for the Kitchen Island game network.

## Developers
- JStuffNZ - Main Developer


## Codebase

```
.
├── .github                      // Github related files.
|   └── workflows
|       └── docker-publish.yml   // Github Action to publish to Github Packages.
├── scripts                      // Scripts needed for development.
└── src                          // Source code.
    ├── cache                    // Static directory, where cache files are placed during runtime.
    ├── data                     // Database & log store. Bound to a volume when running in Docker.
    ├── modules                  // Modules that are loaded at runtime.
    ├── _kisb.py                 // Bot base.
    ├── bot.py                   // Main cog file.
    └── main.py                  // Entrypoint.
```

## Version: 
- 2.0.0

### Required Environment Variables
"TOKEN" - Discord Bot Token

"SCPSL_ID" - Server ID for the Lobby List API. See https://support.scpslgame.com/article/61

"SCPSL_KEY" - Server Key for the Lobby List API. See https://support.scpslgame.com/article/61

### Optional Environment Variables
"LOG_LEVEL" - Logging Level. Can be either "DEBUG" or "INFO" | <!> DANGEROUS <!> - Setting this to "DEBUG" will log sensitive information.

### Docker Volume Paths
"/worker/data" - Main Datastore
