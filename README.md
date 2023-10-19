# example-package
# KISB - Kitchen Island Status Bot
## What is this?
This is a bot that will post the status of the KI Network to a Discord embed. As well as using a custom command to post the status of the KI Network in response to a command.

## Developers
- JStuffNZ - Main Developer


## Version: 
- 1.1.2

### Required Environment Variables
"TOKEN" - Discord Bot Token

"SCPSL_ID" - Server ID for the Lobby List API. See https://support.scpslgame.com/article/61

"SCPSL_KEY" - Server Key for the Lobby List API. See https://support.scpslgame.com/article/61

"LOG_CHANNEL_ID" - (OPTIONAL) Discord Channel ID for the bot to log to. If not set, the bot will not log.


### Docker Volume Paths
"/worker/data" - Main Datastore
