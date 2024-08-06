#!/usr/bin/python3

import hashlib
import ipaddress
import os
import random
import ssl
import string
import subprocess
import sys

from microdot import Request, redirect, send_file
from microdot.session import Session, with_session

from ModulineWebUI.app import (
    app,
    auth,
    authenticate_token,
    register_token,
    remove_token,
)

print(__name__)
tokens = []
current_passkey = ""

#########################################################################################################
# login


@app.get("/")
@app.post("/")
@with_session
async def index(req: Request, session: Session):
    token = session.get("token")
    if req.method == "POST":
        passkey: str = req.form.get("passkey")
        pass_hash = hashlib.sha256(passkey.encode())
        passkey = pass_hash.hexdigest()
        print(f"entered hash: {passkey}, should be: {current_passkey}")
        if passkey == current_passkey:
            token = "".join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                for _ in range(10)
            )  # generate new token for every new authorized session
            session["token"] = token
            register_token(tokens, token)
            session.save()
            return redirect("/static/home.html")
        else:
            return send_file("ModulineWebUI/login.html")
    if token is None or not authenticate_token(tokens, token):
        return send_file("ModulineWebUI/login.html")
    elif authenticate_token(tokens, token):
        return redirect("/static/home.html")


@app.post("/logout")
@with_session
async def logout(req: Request, session: Session):
    remove_token(tokens, session.get("token"))
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


def parse_boolean(boolean: str) -> bool:
    if boolean.lower() in ["y", "yes", "true"]:
        return True
    elif boolean.lower() in ["n", "no", "false"]:
        return False
    else:
        raise ValueError


USAGE = """
go-webui V0.0.1

go-webui [options]

options:
-a address          the address to listen on
-p port             the port to listen on
-sslgen             generate a new self signed ssl key/certificate to use
-sslkey path        give a path to an existing sslkey to use
-sslcert path       give a path to an existing sslcert to use
-passkey passkey    pas in a passkey to use to log in

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

    conf = {}
    try:
        with open("/etc/go_webui.conf", "r") as conf_file:
            for line in conf_file.readlines():
                option = line.split("=", 1)
                if len(option) == 2:
                    conf[option[0].strip().lower()] = option[1].strip()
    except:
        print(
            "missing configuration file /etc/go_webui.conf, trying with arguments only"
        )
    # global current_passkey
    ip = conf.get("ip", "127.0.0.1")
    port = conf.get("port", 5000)
    sslg = conf.get("ssl_gen", "false")
    sslc = conf.get("ssl_cert", None)
    sslk = conf.get("ssl_key", None)
    current_passkey = conf.get("pass_hash", "")

    try:
        sslg = parse_boolean(sslg)
    except ValueError:
        print("""ssl_gen parameter in /etc/go_webui.conf is not configured right, check for typos
it should be set to yes/no or true/false.
continueing with the default which is false""")
        sslg = False

    # parse command line arguments
    args = iter(sys.argv)
    # skip the run argument
    next(args)

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
        elif arg == "-passkey":
            m = hashlib.sha256(next(args).encode())
            current_passkey = m.hexdigest()
            print(f"set password hash to {current_passkey}")
    if current_passkey == "":
        print("""No passkey found in /etc/go_webui.conf or in the arguments.
A passkey must be given at all times""")
        exit(-1)

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
