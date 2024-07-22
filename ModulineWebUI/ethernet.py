import ipaddress
import subprocess

import netifaces as ni


def get_ethernet_mode() -> dict:
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
    return mode


def set_ethernet_mode(mode: str) -> dict:
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
        return {"mode": "static"}
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
        return {"mode": "auto"}
    return {"err": "Invalid mode, send either 'static' or 'auto'"}


def set_static_ip(ip: str) -> dict:
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        return {"err": "Invalid IP"}
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
    if get_ethernet_mode() == "static":
        subprocess.run(["nmcli", "con", "down", "Wired connection static"])
        subprocess.run(["nmcli", "con", "up", "Wired connection static"])
    return {"ip": ip}


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


def get_ethernet_ip() -> dict:
    try:
        return {"ip": ni.ifaddresses("eth0")[ni.AF_INET][0]["addr"]}
    except:
        return {"err": "no IP available"}
