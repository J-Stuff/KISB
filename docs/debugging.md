# Debugging KISB

## Exit Codes

KISB uses exit codes to indicate the reason for the exit. The following exit codes are used:

| Code Type | Description |
|-----------|-------------|
| 1xx       | General Error (internal) |
| 2xx       | Configuration Error |
| 3xx       | SL API Error |
| 4xx       | Discord API Error |
| 5xx       | Database Error |
| 6xx       | Cache Error |
| 7xx       | WEB API Error |



| Exit Code | Reason |
|-----------|--------|
| 100       | General Error - A description of the fault will be printed to the console. |
| 101       | KISB failed to set a suitable data directory. |
| 200       | Configuration Error - A description of the fault will be printed to the console. |
| 201       | KISB was not provided with the 'TOKEN' environment variable. |
| 202       | KISB was not provided with the 'SCPSL_ID' environment variable. |
| 203       | KISB was not provided with the 'SCPSL_KEY' environment variable. |
| 300       | SL API Error - A description of the fault will be printed to the console. |