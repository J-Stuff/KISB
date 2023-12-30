@REM This program quickly updates PDM to use the requirements.txt file. Not needed for running the bot, just a script to make developing it easier
@echo off
pdm import -f requirements requirements.txt
pdm update
pdm export -f requirements -o requirements.txt
EXIT