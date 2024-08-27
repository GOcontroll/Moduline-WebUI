import json
import os
import subprocess

import netifaces as ni
from microdot import Request
from microdot.session import Session, with_session

from ModulineWebUI.app import app, auth
from ModulineWebUI.handlers.service import get_service, set_service


@app.get("/api/get_wifi")
@with_session
@auth
async def get_wifi(req: Request, session: Session):
    return json.dumps({"state": get_service("go-wifi")})


@app.post("/api/set_wifi")
@with_session
@auth
async def set_wifi(req: Request, session: Session):
    """Set the wifi state, request contains a json boolean value\n
    Returns the state of wifi after this function is finished"""
    state = req.json["new_state"]
    try:
        if state:
            set_service("go-wifi", state)
        else:
            # stopping wifi requires a little bit more effort
            set_service("go-wifi", state)
            subprocess.run(["/sbin/modprobe", "-r", "brcmfmac"]).check_returncode()
        return json.dumps({"state": state})
    except Exception as ex:
        return json.dumps({"err": f"could not switch state to {state}\n{ex}"})


@app.post("/api/set_wifi_type")
@with_session
@auth
async def set_wifi_type(req: Request, session: Session):
    """Set the wifi type, AP or receiver, request is a string containing 'ap' or 'wifi'"""
    wifi_type: str = req.json["new_type"]
    # to make the switch permanent all wifi connections need to have their autoconnect settings altered
    # so all wifi connections need to be gathered
    try:
        try:
            stdout = subprocess.run(
                ["nmcli", "-t", "con"], stdout=subprocess.PIPE, text=True
            )
            stdout.check_returncode()
        except:
            return json.dumps({"err": "Could not get list of connections"})
        connections = stdout.stdout.rstrip().split("\n")
        wifi_connections = []
        for con in connections:
            if "wireless" in con:
                if "GOcontroll-AP" not in con:
                    wifi_connections.append(con.split(":")[0])
        if wifi_type == "ap":
            for con in wifi_connections:
                try:
                    subprocess.run(
                        ["nmcli", "con", "mod", con, "connection.autoconnect", "no"]
                    ).check_returncode()
                except:
                    return json.dumps(
                        {"err": "could not turn of autoconnect on all wifi connections"}
                    )
            try:
                subprocess.run(
                    [
                        "nmcli",
                        "con",
                        "mod",
                        "GOcontroll-AP",
                        "connection.autoconnect",
                        "yes",
                    ]
                ).check_returncode()
            except:
                return json.dumps(
                    {"err": "could not set the access point to autoconnect"}
                )
            try:
                enable_connection("GOcontroll-AP")
            except:
                return json.dumps({"err": "Could not raise the access point"})
            return {"type": "ap"}
        elif wifi_type == "wifi":
            for con in wifi_connections:
                try:
                    subprocess.run(
                        ["nmcli", "con", "mod", con, "connection.autoconnect", "yes"]
                    ).check_returncode()
                except:
                    return json.dumps(
                        {"err": "Could not set all wifi connections to autoconnect"}
                    )
            try:
                subprocess.run(
                    [
                        "nmcli",
                        "con",
                        "mod",
                        "GOcontroll-AP",
                        "connection.autoconnect",
                        "no",
                    ]
                ).check_returncode()
            except:
                return json.dumps(
                    {"err": "Could not disable access point auto connect"}
                )
            try:
                disable_connection("GOcontroll-AP")
            except:
                return json.dumps({"err": "Could not deactivate access point"})
            return json.dumps({"type": "wifi"})
        else:
            return json.dumps({"err": "Invalid type given, must be 'ap' or 'wifi'"})
    except:
        return json.dumps({"err": "Could not set wifi type"})


@app.get("/api/get_wifi_type")
@with_session
@auth
async def get_wifi_type(req: Request, session: Session):
    try:
        try:
            output = subprocess.run(
                ["nmcli", "-t", "con", "show", "GOcontroll-AP"],
                stdout=subprocess.PIPE,
                text=True,
            )
            output.check_returncode()
        except:
            return json.dumps({"err": "Could not get access point information"})
        option = "connection.autoconnect:"
        idx = output.stdout.find(option)
        if idx >= 0:
            if output.stdout[idx + len(option)] == "y":
                return json.dumps({"type": "ap"})
            else:
                return json.dumps({"type": "wifi"})
        else:
            return json.dumps({"err": "Could not determine current wifi type"})
    except Exception as ex:
        return json.dumps({"err": f"Could not determine current wifi type:\n{ex}"})


def reload_ap():
    """Reload the access point after changes have been made for example
    raises subprocess.CalledProcessError when unsuccessfull"""
    disable_connection("GOcontroll-AP")
    enable_connection("GOcontroll-AP")


@app.post("/api/set_ap_pass")
@with_session
@auth
async def set_ap_pass(req: Request, session: Session):
    new_password: str = req.json
    try:
        subprocess.run(
            [
                "nmcli",
                "con",
                "mod",
                "GOcontroll-AP",
                "wifi-sec.psk",
                new_password,
            ]
        ).check_returncode()
    except subprocess.CalledProcessError as ex:
        return json.dumps({"err": f"Failed to set new password:\n{ex.output}"})
    except Exception as ex:
        return json.dumps({"err": f"Failed to set new password:\n{ex}"})
    reload_ap()
    return json.dumps({})


@app.post("/api/set_ap_ssid")
@with_session
@auth
async def set_ap_ssid(req: Request, session: Session):
    new_ssid: str = req.json
    try:
        subprocess.run(
            [
                "nmcli",
                "con",
                "mod",
                "GOcontroll-AP",
                "802-11-wireless.ssid",
                new_ssid,
            ]
        ).check_returncode()
    except subprocess.CalledProcessError as ex:
        return json.dumps({"err": f"Failed to set new ssid:\n{ex.output}"})
    except Exception as ex:
        return json.dumps({"err": f"Failed to set new ssid:\n{ex}"})
    reload_ap()
    return json.dumps({})


@app.get("/api/get_ap_connections")
@with_session
@auth
async def get_ap_connections(req: Request, session: Session):
    """Get a list of hostnames connected to the access point"""
    final_device_list = {}
    try:
        stdout = subprocess.run(
            ["ip", "n", "show", "dev", "wlan0"],
            stdout=subprocess.PIPE,
            text=True,
        )
        stdout.check_returncode()
    except subprocess.CalledProcessError as ex:
        return json.dumps({"err": f"Could not get information from ip:\n{ex.output}"})
    except Exception as ex:
        return json.dumps({"err": f"Could not get information from ip:\n{ex}"})

    connected_devices = stdout.stdout.split("\n")
    for i in reversed(range(len(connected_devices))):
        if (
            "REACHABLE" not in connected_devices[i]
            and "DELAY" not in connected_devices[i]
        ):
            connected_devices.pop(i)
    try:
        stdout = subprocess.run(
            ["cat", "/var/lib/misc/dnsmasq.leases"],
            stdout=subprocess.PIPE,
            text=True,
        )
        stdout.check_returncode()
    except subprocess.CalledProcessError as ex:
        return json.dumps({"err": f"Could not get dns leases:\n{ex.output}"})
    except Exception as ex:
        return json.dumps({"err": f"Could not get dns leases:\n{ex}"})

    previous_connections = stdout.stdout.split("\n")[:-1]

    for connected_device in connected_devices:
        connected_device_list = connected_device.split(" ")
        for previous_connection in previous_connections:
            if connected_device_list[2] in previous_connection:
                final_device_list[connected_device_list[2]] = previous_connection.split(
                    " "
                )[3]

    return json.dumps(final_device_list)


def disable_connection(con: str):
    """Set the connection 'con' to down
    raises subprocess.CalledProcessError when unsuccessfull"""
    subprocess.run(["nmcli", "con", "down", con]).check_returncode()


def enable_connection(con: str):
    """Set the connection 'con' to up
    raises subprocess.CalledProcessError when unsuccessfull"""
    subprocess.run(["nmcli", "con", "up", con]).check_returncode()


@app.get("/api/get_wifi_networks")
@with_session
@auth
async def get_wifi_networks(req: Request, session: Session):
    """Get the list of available wifi networks and their attributes"""
    # gets the list in a layout optimal for scripting, networks seperated by \n, columns seperated by :
    try:
        wifi_list = subprocess.run(
            ["nmcli", "-t", "dev", "wifi"], stdout=subprocess.PIPE, text=True
        )
        wifi_list.check_returncode()
    except subprocess.CalledProcessError as ex:
        return json.dumps({"err": f"Could not get wifi networks:\n{ex.output}"})
    except Exception as ex:
        return json.dumps({"err": f"Could not get wifi networks:\n{ex}"})

    networks = wifi_list.stdout.rstrip().split("\n")
    networks_out = {}
    for i in range(len(networks)):
        network = networks[i].split(":")
        if len(network) > 8:
            # some character that is not a space here means active
            connected = network[0] != " "
            # splitting by : unfortunately also splits the mac address, it also contains some \ characters
            # strip the \ characters and join it back
            mac = ":".join(map(lambda octet: octet.rstrip("\\"), network[1:7]))
            ssid = network[7]
            strength = network[11]
            security = network[13]
            networks_out[network[7]] = {
                "connected": connected,
                "mac": mac,
                "ssid": ssid,
                "strength": strength,
                "security": security,
            }
    return json.dumps(networks_out)


@app.post("/api/connect_to_wifi_network")
@with_session
@auth
async def connect_to_wifi_network(req: Request, session: Session):
    args: dict = req.json
    ssid = args["ssid"]
    password = args["password"]
    try:
        result = subprocess.run(
            ["nmcli", "dev", "wifi", "connect", ssid, "password", password],
            stdout=subprocess.PIPE,
            text=True,
        )
        result.check_returncode()
    except subprocess.CalledProcessError as ex:
        return json.dumps({"err": f"Could not connect to wifi network:\n{ex.output}"})
    # for some reason this function returns exit code 0 even on failure
    search_str = "Error:"
    idx = result.stdout.find(search_str)
    if idx >= 0:
        return json.dumps({"err": f"{result.stdout[len(search_str):].strip()}"})
    return json.dumps({})


@app.post("/api/get_wifi_ip")
@with_session
@auth
async def get_wifi_ip(req: Request, session: Session):
    try:
        return json.dumps({"ip": ni.ifaddresses("wlan0")[ni.AF_INET][0]["addr"]})
    except Exception as ex:
        return json.dumps({"err": f"Could not get ip:\n{ex}"})
