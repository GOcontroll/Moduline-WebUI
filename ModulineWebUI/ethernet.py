import ipaddress
import json
import subprocess

import netifaces as ni
from microdot import Request
from microdot.session import Session, with_session

from ModulineWebUI.app import app, auth


@app.get("/api/get_ethernet_mode")
@with_session
@auth
async def get_ethernet_mode(req: Request, session: Session) -> dict:
    stdout = subprocess.run(["nmcli", "-t", "con"], stdout=subprocess.PIPE, text=True)
    result = stdout.stdout
    result = result.split("\n")
    mode = {}
    for name in result:
        if "Wired connection static" in name:
            if "eth0" in name:
                mode["mode"] = "static"
                break
        elif "Wired connection auto" in name:
            if "eth0" in name:
                mode["mode"] = "auto"
                break
    else:  # if no break
        mode["error"] = "Unknown mode"
    return json.dumps(mode)


@app.post("/api/set_ethernet_mode")
@with_session
@auth
async def set_ethernet_mode(req: Request, session: Session):
    data = req.json
    mode = data["mode"]
    if mode == "static":
        subprocess.run(
            [
                "nmcli",
                "con",
                "mod",
                "Wired connection auto",
                "connection.autoconnect",
                "no",
            ]
        )
        subprocess.run(
            [
                "nmcli",
                "con",
                "mod",
                "Wired connection static",
                "connection.autoconnect",
                "yes",
            ]
        )
        subprocess.run(["nmcli", "con", "down", "Wired connection auto"])
        subprocess.run(["nmcli", "con", "up", "Wired connection static"])
        return json.dumps({"mode": "static"})
    elif mode == "auto":
        subprocess.run(
            [
                "nmcli",
                "con",
                "mod",
                "Wired connection static",
                "connection.autoconnect",
                "no",
            ]
        )
        subprocess.run(
            [
                "nmcli",
                "con",
                "mod",
                "Wired connection auto",
                "connection.autoconnect",
                "yes",
            ]
        )
        subprocess.run(["nmcli", "con", "down", "Wired connection static"])
        subprocess.run(["nmcli", "con", "up", "Wired connection auto"])
        return json.dumps({"mode": "auto"})
    return json.dumps({"err": "Invalid mode, send either 'static' or 'auto'"})


@app.post("/api/set_static_ip")
@with_session
@auth
async def set_static_ip(req: Request, session: Session):
    data = req.json
    ip = data["ip"]
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        return json.dumps({"err": "Invalid IP"})
    subprocess.run(
        [
            "nmcli",
            "con",
            "mod",
            "Wired connection static",
            "ipv4.addresses",
            ip + "/16",
        ]
    )
    with open("/etc/dnsmasq.conf", "r") as filer:
        content = str(filer.readlines())
    for line, i in enumerate(content):
        if line.find("dhcp-range") >= 0 and line.find("eth0") >= 0:
            last = int(ip.split(".")[-1])
            main = ip.split(".")[0:-1]
            content[i] = f"dhcp-range={main}.1,{main}.{last -1},12h"
    with open("/etc/dnsmasq.conf", "w") as filew:
        filew.write("\n".join(content))
    if get_ethernet_mode() == "static":
        subprocess.run(["nmcli", "con", "down", "Wired connection static"])
        subprocess.run(["nmcli", "con", "up", "Wired connection static"])
        subprocess.run(["systemctl", "restart", "dnsmasq"])
    return json.dumps({"ip": ip})


def get_static_ip() -> dict:
    output = subprocess.run(
        ["nmcli", "-t", "con", "show", "Wired connection static"],
        stdout=subprocess.PIPE,
        text=True,
    )
    option = "ipv4.addresses:"
    idx = output.stdout.find(option)
    if idx >= 0:
        ide = output.stdout.find("\n", idx + len(option))
        if ide == idx + len(option):
            return {"err": "No ip address configured"}
        elif ide >= 0:
            ip_ext = output.stdout[idx + len(option) : ide]
            ip = ip_ext.split("/")[0]
            return {"ip": ip}
        else:
            return {"err": "Could get the ip address"}
    else:
        return {"err": "Could get the ip address"}


@app.get("/api/get_ethernet_ip")
@with_session
@auth
async def get_ethernet_ip(req: Request, session: Session):
    try:
        return json.dumps({"ip": ni.ifaddresses("eth0")[ni.AF_INET][0]["addr"]})
    except:
        return json.dumps({"err": "no IP available"})
