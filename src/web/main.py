import os, random, hashlib, logging
from flask import Flask, redirect, url_for, abort, request, send_from_directory, session
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized, exceptions
from modules.setup.logging import init_logging
from oauthlib.oauth2.rfc6749.errors import MissingCodeError

init_logging()

logger = logging.getLogger("web") # This subprocess uses the logger 'web' - compared to the bot which uses 'main'

AUTHORIZED_GUILDS = [1136504183948857397]


app = Flask(__name__)

app.secret_key = hashlib.md5(random.randbytes(64)).hexdigest()
logger.debug(f"INSECURE (disable debug mode before using in prod) - Secret key: {app.secret_key}")


if os.getenv("PROD_LEVEL") is not None:
    if os.getenv("PROD_LEVEL").lower() == 'debug': #type:ignore
        app.debug = True
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true"
    else:
        app.debug = False
        pass


app.config["DISCORD_CLIENT_ID"] = os.getenv("DISCORD_CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("DISCORD_CLIENT_SECRET")
app.config["DISCORD_BOT_TOKEN"] = os.getenv("TOKEN")
app.config["DISCORD_REDIRECT_URI"] = os.getenv("DISCORD_REDIRECT_URI")

discord = DiscordOAuth2Session(app)

@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))

@app.errorhandler(403)
def forbidden(e):
    return send_from_directory('./static/errors/403', "index.html"), 403


@app.route("/")
def index():
    return send_from_directory('./static/root', "index.html")

@app.route('/static/index/<path:filename>')
def serve_index_static_files(filename):
    return send_from_directory('./static/root', filename)

@app.route("/login/")
def serve_login_page():
    discord.revoke()
    return send_from_directory('./static/login', "index.html")

@app.route("/static/login/<path:filename>")
def serve_static_files(filename):
    return send_from_directory('./static/login', filename)



@app.route("/login/discord/")
def discord_oauth_login():
    discord.revoke()
    return discord.create_session(scope=["identify", "guilds", "guilds.members.read"])

@app.route("/login/discord/callback/")
def discord_oauth_callback():
    try:
        discord.callback()
    except exceptions.AccessDenied:
        discord.revoke()
        return redirect("/login/discord/unauthorized/?error=access_denied")
    except MissingCodeError:    
        discord.revoke()
        return abort(400)
    
    guilds = discord.fetch_guilds()

    if not [guild.id for guild in guilds if guild.id in AUTHORIZED_GUILDS]:
        discord.revoke()
        return redirect("/login/discord/unauthorized/?error=unauthorized_guild")

    return redirect(url_for("index"))


@app.route("/login/discord/unauthorized/")
def unauthorized():
    query_str = request.args.get("error", "")
    logger.debug(f"Unauthorized - error: {query_str}")

    if query_str == "access_denied":
        return abort(403)
    elif query_str == "unauthorized_guild":
        return abort(403)
    else:
        return abort(403)

if __name__ == '__main__':
    app.run(port=3000)