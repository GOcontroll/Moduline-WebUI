#!/usr/bin/python3

import ipaddress
import os
import random
import ssl
import string
import subprocess
import sys
from functools import wraps

from microdot import Microdot, Request, Response, redirect, send_file
from microdot.session import Session, with_session

tokens = []
app = Microdot()
Session(
    app,
    secret_key="".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(10)
    ),
)  # generate new session key when the server is restarted
Response.default_content_type = "text/html"


#########################################################################################################
# auth


def authenticate_token(token: str) -> bool:
    try:
        tokens.index(token)
        return True
    except ValueError:
        return False


def register_token(token: str):
    tokens.append(token)


def remove_token(token: str):
    try:
        tokens.remove(token)
    except ValueError:
        pass


def auth(func):
    @wraps(func)
    async def wrapper(req: Request, session: Session, *args, **kwargs):
        if not authenticate_token(session.get("token")):
            return redirect("/")
        return await func(req, session, *args, **kwargs)

    return wrapper


#########################################################################################################
# login


@app.get("/")
@app.post("/")
@with_session
async def index(req: Request, session: Session):
    token = session.get("token")
    if req.method == "POST":
        passkey = req.form.get("passkey")
        if passkey == "test":  # TODO store passkey somewhere safe
            token = "".join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                for _ in range(10)
            )  # generate new token for every new authorized session
            session["token"] = token
            register_token(token)
            session.save()
            return redirect("/static/home.html")
        else:
            return send_file("ModulineWebUI/login.html")
    if token is None or not authenticate_token(token):
        return send_file("ModulineWebUI/login.html")
    elif authenticate_token(token):
        return redirect("/static/home.html")


@app.post("/logout")
@with_session
async def logout(req: Request, session: Session):
    remove_token(session.get("token"))
    session.delete()
    return redirect("/")


#########################################################################################################

# file hosting


@app.route("/static/<path:path>")
@with_session
@auth
async def static(req: Request, session: Session, path: str):
    if ".." in path:
        return "Not allowed", 404
    return send_file("ModulineWebUI/static/" + path)


@app.route("/style/<path:path>")
async def style(req: Request, path):
    if ".." in path:
        return "Not allowed", 404
    return send_file("ModulineWebUI/style/" + path)


@app.route("/js/<path:path>")
async def js(request: Request, path):
    if ".." in path:
        return "Not allowed", 404
    return send_file("ModulineWebUI/js/" + path)


@app.route("/assets/<path:path>")
async def assets(request: Request, path):
    if ".." in path:
        return "Not allowed", 404
    return send_file("ModulineWebUI/assets/" + path)


@app.get("/favicon.ico")
async def favicon(request: Request):
    return send_file("ModulineWebUI/favicon.ico")


#########################################################################################################

USAGE = """
go-webui V0.0.1

go-webui [options]

options:
-a address          the address to listen on
-p port             the port to listen on
-sslgen             generate a new self signed ssl key/certificate to use
-sslkey path        give a path to an existing sslkey to use
-sslcert path       give a path to an existing sslcert to use

default ip = 127.0.0.1
default port = 5000

examples:
go-webui -a 0.0.0.0 -p 7500
go-webui -sslcert cert.pem -sslkey key.pen
go-webui -a 0.0.0.0 -p 7500 -sslgen
"""

if __name__ == "__main__":
    from ModulineWebUI.controller import *
    from ModulineWebUI.ethernet import *
    from ModulineWebUI.wifi import *
    from ModulineWebUI.wwan import *

    # parse command line arguments
    args = iter(sys.argv)
    # skip the run argument
    next(args)
    ip = "127.0.0.1"
    port = 5000
    sslk = None
    sslc = None
    sslg = False
    for arg in args:
        if arg == "-a":
            ip = next(args)
            try:
                ipaddress.IPv4Address(ip)
            except ValueError:
                print("given ip address was not valid")
                exit(-1)
        elif arg == "-p":
            try:
                port = int(next(args))
            except ValueError:
                print("given port was not valid")
                exit(-1)
        elif arg == "-h":
            print(USAGE)
            exit(0)
        elif arg == "-sslkey":
            sslk = next(args)
            if not os.path.exists(sslk):
                print("Could not find entered key")
                exit(-1)
        elif arg == "-sslcert":
            sslc = next(args)
            if not os.path.exists(sslc):
                print("Could not find entered certificate")
                exit(-1)
        elif arg == "-sslgen":
            sslg = True

    # add path for the error module
    sys.path.append("/usr/moduline/python")
    # create global list of authentication tokens

    if sslc is not None:
        sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        sslctx.load_cert_chain(sslc, sslk)
        app.run(host=ip, port=port, ssl=sslctx)
    elif sslg:
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:4096",
                "-nodes",
                "-out",
                "cert.pem",
                "-keyout",
                "key.pem",
                "-days",
                "365",
                "-subj",
                "/C=NL/ST=Gelderland/L=Ulft/O=GOcontroll B.V./OU='.'/CN=GOcontroll",
            ]
        ).check_returncode()
        sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        sslctx.load_cert_chain("cert.pem", "key.pem")
        app.run(host=ip, port=port, ssl=sslctx)
    else:
        app.run(host=ip, port=port)
