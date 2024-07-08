import json
import os
import random
import string
from functools import wraps

from microdot import Microdot, Request, Response, redirect, send_file
from microdot.session import Session, with_session

import controller
import ethernet
import wifi
import wwan


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
        if passkey == "test":  # store passkey somewhere safe
            token = "".join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits)
                for _ in range(10)
            )  # generate new token for every new authorized session
            session["token"] = token
            register_token(token)
            session.save()
            return redirect("/static/home.html")
        else:
            return send_file("login.html")
    if token is None or not authenticate_token(token):
        return send_file("login.html")
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
    return send_file("static/" + path)


@app.route("/style/<path:path>")
async def style(req: Request, path):
    if ".." in path:
        return "Not allowed", 404
    return send_file("style/" + path)


@app.route("/js/<path:path>")
async def js(request: Request, path):
    if ".." in path:
        return "Not allowed", 404
    return send_file("js/" + path)

@app.route("/assets/<path:path>")
async def assets(request: Request, path):
    if ".." in path:
        return "Not allowed", 404
    return send_file("assets/" + path)


@app.get("/favicon.ico")
async def favicon(request: Request):
    return send_file("favicon.ico")


#########################################################################################################

# api

# wifi


@app.get("/api/get_wifi")
@with_session
@auth
async def get_wifi(req: Request, session: Session):
    return json.dumps(not os.path.isfile("/etc/modprobe.d/brcmfmac.conf"))


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
    wifi.set_ap_password(new_password)
    wifi.reload_ap()
    return json.dumps("")


@app.post("/api/set_ap_ssid")
@with_session
@auth
async def set_ap_ssid(req: Request, session: Session):
    new_ssid: str = req.form.get("ssid")
    wifi.set_ap_ssid(new_ssid)
    wifi.reload_ap()
    return json.dumps("")


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
    delete_errors(errors)
    return json.dumps("")


# services


@app.get("/api/get_service")
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
    controller.set_service(service, new_state)
    return json.dumps({"new_state": new_state})


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
    new_state = req.json
    wwan.set_wwan(new_state)
    return json.dumps({"new_state": new_state})


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
    tokens = []
    app.run()
