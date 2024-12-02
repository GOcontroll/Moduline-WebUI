import json

from microdot import Request
from microdot.session import Session, with_session
from PyModuline import wifi

from ModulineWebUI.app import app, auth


@app.get("/api/get_wifi")
@with_session
@auth
async def get_wifi(req: Request, session: Session):
    return json.dumps({"state": wifi.get_wifi()})


@app.post("/api/set_wifi")
@with_session
@auth
async def set_wifi(req: Request, session: Session):
    """Set the wifi state, request contains a json boolean value\n
    Returns the state of wifi after this function is finished"""
    state = req.json["new_state"]
    res, err = wifi.set_wifi(state)
    if res:
        return json.dumps({"state": state})
    else:
        return json.dumps({"err": f"could not switch state to {state}\n{err}"})


@app.post("/api/activate_ap")
@with_session
@auth
async def activate_ap(req: Request, session: Session):
    """Turn on the wifi access point and disable automatic connecting"""
    wifi.activate_ap()
    return json.dumps({})


@app.post("/api/deactivate_ap")
@with_session
@auth
async def deactivate_ap(req: Request, session: Session):
    """disable the wifi access point and enable automatic connecting"""
    wifi.deactivate_ap()
    return json.dumps({})


@app.get("/api/get_ap_status")
@with_session
@auth
async def get_ap_status(req: Request, session: Session):
    return json.dumps(wifi.get_ap_status())


@app.post("/api/set_ap_pass")
@with_session
@auth
async def set_ap_pass(req: Request, session: Session):
    new_password: str = req.json
    wifi.set_ap_pass(new_password)
    return json.dumps({})


@app.post("/api/set_ap_ssid")
@with_session
@auth
async def set_ap_ssid(req: Request, session: Session):
    new_ssid: str = req.json
    wifi.set_ap_ssid(new_ssid)
    return json.dumps({})


@app.get("/api/get_ap_connections")
@with_session
@auth
async def get_ap_connections(req: Request, session: Session):
    """Get a list of hostnames connected to the access point"""
    return json.dumps(wifi.get_ap_connections())


@app.get("/api/get_wifi_networks")
@with_session
@auth
async def get_wifi_networks(req: Request, session: Session):
    """Get the list of available wifi networks and their attributes"""
    return json.dumps(wifi.get_wifi_networks())


@app.post("/api/connect_to_wifi_network")
@with_session
@auth
async def connect_to_wifi_network(req: Request, session: Session):
    args: dict = req.json
    ssid = args["ssid"]
    password = args["password"]
    wifi.connect_to_wifi_network(ssid, password)
    return json.dumps({})


@app.post("/api/get_wifi_ip")
@with_session
@auth
async def get_wifi_ip(req: Request, session: Session):
    return json.dumps(wifi.get_wifi_ip())
