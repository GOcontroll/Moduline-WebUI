import ipaddress
import json

from microdot import Request
from microdot.session import Session, with_session

from ModulineWebUI.app import app, auth

from PyModuline import ethernet


@app.get("/api/get_ethernet_mode")
@with_session
@auth
async def get_ethernet_mode(req: Request, session: Session) -> dict:
    is_static = ethernet.get_ethernet_static_status()
    if is_static:
        return json.dumps("static")
    else:
        return json.dumps("auto")


@app.post("/api/set_ethernet_mode")
@with_session
@auth
async def set_ethernet_mode(req: Request, session: Session):
    mode = req.json["mode"]
    if mode == "static":
        ethernet.activate_ethernet_static()
        return json.dumps({"mode": "static"})
    elif mode == "auto":
        ethernet.deactivate_ethernet_static()
        return json.dumps({"mode": "auto"})
    raise ValueError("Invalid mode")


@app.post("/api/set_static_ip")
@with_session
@auth
async def set_static_ip(req: Request, session: Session):
    ip = req.json["ip"]
    ipaddress.IPv4Address(ip)
    ethernet.set_static_ethernet_ip(ip)
    return json.dumps({"ip": ip})


@app.post("/api/get_static_ip")
@with_session
@auth
async def get_static_ip():
    return json.dumps({"ip": ethernet.get_ethernet_static_ip()})


@app.get("/api/get_ethernet_ip")
@with_session
@auth
async def get_ethernet_ip(req: Request, session: Session):
    return json.dumps({"ip": ethernet.get_ethernet_ip()})
