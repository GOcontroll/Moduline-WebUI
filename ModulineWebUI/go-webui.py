#!/usr/bin/python3

import ipaddress
import json
import os
import random
import ssl
import string
import subprocess
import sys
from functools import wraps

from microdot import Microdot, Request, Response, redirect, send_file
from microdot.session import Session, with_session

import ModulineWebUI.controller as controller
import ModulineWebUI.ethernet as ethernet
import ModulineWebUI.wifi as wifi
import ModulineWebUI.wwan as wwan

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
# routes

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

# api

# wifi


@app.get("/api/get_wifi")
@with_session
@auth
async def get_wifi(req: Request, session: Session):
    return json.dumps({"state": not os.path.isfile("/etc/modprobe.d/brcmfmac.conf")})


@app.post("/api/set_wifi")
@with_session
@auth
async def set_wifi(req: Request, session: Session):
    """Set the wifi state, request contains a json boolean value\n
    Returns the state of wifi after this function is finished"""
    data = req.json
    return json.dumps(wifi.set_wifi(data["new_state"]))


@app.post("/api/set_wifi_type")
@with_session
@auth
async def set_wifi_type(req: Request, session: Session):
    """Set the wifi type, AP or receiver, request is a string containing 'ap' or 'wifi'"""
    data = req.json
    return json.dumps(wifi.set_wifi_type(data["new_type"]))


@app.get("/api/get_wifi_type")
@with_session
@auth
async def get_wifi_type(req: Request, session: Session):
    return json.dumps(wifi.get_wifi_type())


@app.post("/api/set_ap_pass")
@with_session
@auth
async def set_ap_pass(req: Request, session: Session):
    new_password: str = req.json
    res = wifi.set_ap_password(new_password)
    if "err" in res:
        return json.dumps(res)
    wifi.reload_ap()
    return json.dumps(res)


@app.post("/api/set_ap_ssid")
@with_session
@auth
async def set_ap_ssid(req: Request, session: Session):
    new_ssid: str = req.json
    res = wifi.set_ap_ssid(new_ssid)
    if "err" in res:
        return json.dumps(res)
    wifi.reload_ap()
    return json.dumps(res)


@app.get("/api/get_ap_connections")
@with_session
@auth
async def get_ap_connections(req: Request, session: Session):
    return json.dumps(wifi.get_ap_connections())


@app.get("/api/get_wifi_networks")
@with_session
@auth
async def get_wifi_networks(req: Request, session: Session):
    return json.dumps(wifi.get_wifi_networks())


@app.post("/api/connect_to_wifi_network")
@with_session
@auth
async def connect_to_wifi_network(req: Request, session: Session):
    args: dict = req.json
    return json.dumps(wifi.connect_to_wifi_network(args["ssid"], args["password"]))


@app.post("/api/get_wifi_ip")
@with_session
@auth
async def get_wifi_ip(req: Request, session: Session):
    return json.dumps(wifi.get_wifi_ip())


# simulink


@app.get("/api/get_sim_ver")
@with_session
@auth
async def sim_ver(req: Request, session: Session):
    return json.dumps(controller.get_sim_ver())


@app.get("/api/GOcontroll_Linux.a2l")  # last part of route determines file name
@with_session
@auth
async def a2l_down(req: Request, session: Session):
    return send_file("/usr/simulink/GOcontroll_Linux.a2l")


@app.get("/api/get_errors")
@with_session
@auth
async def get_errors(req: Request, session: Session):
    return json.dumps(controller.get_errors())


@app.post("/api/delete_errors")
@with_session
@auth
async def delete_errors(req: Request, session: Session):
    errors: "list[str]" = req.json
    return json.dumps(controller.delete_errors(errors))


# services


@app.post("/api/get_service")
@with_session
@auth
async def get_service(req: Request, session: Session):
    service: str = req.json
    return json.dumps({"state": controller.get_service(service)})


@app.post("/api/set_service")
@with_session
@auth
async def set_service(req: Request, session: Session):
    data = req.json
    new_state: bool = data["new_state"]
    service: str = data["service"]
    return json.dumps({"new_state": controller.set_service(service, new_state)})


# controller info


@app.get("/api/get_hardware")
@with_session
@auth
async def get_hardware(req: Request, session: Session):
    return json.dumps(controller.get_hardware())


@app.get("/api/get_software")
@with_session
@auth
async def get_software(req: Request, session: Session):
    return json.dumps(controller.get_software())


@app.get("/api/get_serial_number")
@with_session
@auth
async def get_serial_number(req: Request, session: Session):
    return json.dumps(controller.get_serial_number())


# wwan


@app.get("/api/get_wwan")
@with_session
@auth
async def get_wwan(req: Request, session: Session):
    return json.dumps({"state": wwan.get_wwan()})


@app.post("/api/set_wwan")
@with_session
@auth
async def set_wwan(req: Request, session: Session):
    new_state = req.json["new_state"]
    return json.dumps({"new_state": wwan.set_wwan(new_state)})


@app.get("/api/get_wwan_stats")
@with_session
@auth
async def get_wwan_stats(req: Request, session: Session):
    return json.dumps(wwan.get_wwan_stats())


# ethernet


@app.get("/api/get_ethernet_mode")
@with_session
@auth
async def get_ethernet_mode(req: Request, session: Session):
    return json.dumps(ethernet.get_ethernet_mode())


@app.post("/api/set_ethernet_mode")
@with_session
@auth
async def set_ethernet_mode(req: Request, session: Session):
    data = req.json
    return json.dumps(ethernet.set_ethernet_mode(data["mode"]))


@app.get("/api/get_ethernet_ip")
@with_session
@auth
async def get_ethernet_ip(req: Request, session: Session):
    return json.dumps(ethernet.get_ethernet_ip())


@app.post("/api/set_static_ip")
@with_session
@auth
async def set_static_ip(req: Request, session: Session):
    data = req.json
    return json.dumps(ethernet.set_static_ip(data["ip"]))


#########################################################################################################

if __name__ == "__main__":
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
    tokens = []
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
