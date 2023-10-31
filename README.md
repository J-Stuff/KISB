# KISB - Kitchen Island Status Bot
## What is this?
This is a bot that will post the status of the KI Network to a Discord embed. As well as using a custom command to post the status of the KI Network in response to a command.

## Developers
- JStuffNZ - Main Developer


## Codebase

```
.
├── .github   // Github related files.
|   └── workflows
|       └── docker-publish.yml   // Github Action to publish to Github Packages.
├── scripts   // Scripts needed for development.
└──src      // Source code.
```

## Version: 
- 1.2.3

### Required Environment Variables
"TOKEN" - Discord Bot Token

"SCPSL_ID" - Server ID for the Lobby List API. See https://support.scpslgame.com/article/61

"SCPSL_KEY" - Server Key for the Lobby List API. See https://support.scpslgame.com/article/61

### Docker Volume Paths
"/worker/data" - Main Datastore
