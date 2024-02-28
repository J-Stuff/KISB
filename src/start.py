import threading
import subprocess
import os
from dotenv import load_dotenv

if os.path.exists("../.env"):
    load_dotenv("../.env")  # Used for development


def start(cwd: str, entrypoint: str):
    if not os.getenv("VENV_LOCATION"):
        print(f"Starting KISB subprocess: {cwd}")
        subprocess.run(["python", "-Xfrozen_modules=off", entrypoint], cwd=cwd)
    else:
        path = os.getenv("VENV_LOCATION")
        if path is None:
            exit("VENV_LOCATION not set correctly! Exiting...")
        print(f"Starting KISB subprocess: {cwd} @ {path}")
        subprocess.run([path, "python", "-Xfrozen_modules=off", entrypoint], cwd=cwd)


discord = threading.Thread(target=start, args=("./discord/", "./main.py"))
web = threading.Thread(target=start, args=("./web/", "./main.py"))

if __name__ == "__main__":
    # discord.start()
    web.start()
