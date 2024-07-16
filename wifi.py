import os
import subprocess

import netifaces as ni


def set_wifi(state: bool) -> dict:
    """Set the state of the wifi receiver, true=on, false=off"""
    try:
        if state:
            os.remove("/etc/modprobe.d/brcmfmac.conf")
            subprocess.run(["modprobe", "brcmfmac"])
        else:
            with open("/etc/modprobe.d/brcmfmac.conf", "x") as file:
                file.write("blacklist brcmfmac")
            subprocess.run(["modprobe", "-r", "brcmfmac"])
        return {"state": state}
    except:
        return {"err": f"could not switch state to {state}"}


def set_wifi_type(type: str) -> dict:
    """Set the type that the wifi receiver should act as, 'ap'=access point 'wifi'=receiver"""
    # to make the switch permanent all wifi connections need to have their autoconnect settings altered
    # so all wifi connections need to be gathered
    stdout = subprocess.run(["nmcli", "-t", "con"], stdout=subprocess.PIPE, text=True)
    connections = stdout.stdout.rstrip().split("\n")
    wifi_connections = []
    for con in connections:
        if "wireless" in con:
            if "GOcontroll-AP" not in con:
                wifi_connections.append(con.split(":")[0])
    if type == "ap":
        for con in wifi_connections:
            subprocess.run(["nmcli", "con", "mod", con, "connection.autoconnect", "no"])
        subprocess.run(
            ["nmcli", "con", "mod", "GOcontroll-AP", "connection.autoconnect", "yes"]
        )
        subprocess.run(["nmcli", "con", "up", "GOcontroll-AP"])
        return {"type": "ap"}
    elif type == "wifi":
        for con in wifi_connections:
            subprocess.run(
                ["nmcli", "con", "mod", con, "connection.autoconnect", "yes"]
            )
        subprocess.run(
            ["nmcli", "con", "mod", "GOcontroll-AP", "connection.autoconnect", "no"]
        )
        subprocess.run(["nmcli", "con", "down", "GOcontroll-AP"])
        return {"type": "wifi"}
    else:
        return {"err": "Invalid type given, must be 'ap' or 'wifi'"}


def get_wifi_type() -> dict:
    output = subprocess.run(
        ["nmcli", "-t", "con", "show", "GOcontroll-AP"],
        stdout=subprocess.PIPE,
        text=True,
    )
    option = "connection.autoconnect:"
    idx = output.stdout.find(option)
    if idx >= 0:
        if output.stdout[idx + len(option)] == "y":
            return {"type": "ap"}
        else:
            return {"type": "wifi"}
    else:
        return {"err": "Could not determine current wifi type"}


def reload_ap():
    """Reload the access point after changes have been made for example"""
    subprocess.run(["nmcli", "con", "down", "GOcontroll-AP"])
    subprocess.run(["nmcli", "con", "up", "GOcontroll-AP"])


def set_ap_password(new_password: str):
    """Set a new access point password"""
    subprocess.run(
        ["nmcli", "con", "mod", "GOcontroll-AP", "wifi-sec.psk", new_password]
    )


def set_ap_ssid(new_ssid: str):
    """Set a new access point name"""
    subprocess.run(
        ["nmcli", "con", "mod", "GOcontroll-AP", "802-11-wireless.ssid", new_ssid]
    )


def get_ap_connections() -> dict:
    """Get a list of hostnames connected to the access point"""
    final_device_list = {}
    stdout = subprocess.run(
        ["ip", "n", "show", "dev", "wlan0"], stdout=subprocess.PIPE, text=True
    )
    connected_devices = stdout.stdout.split("\n")
    for i in reversed(range(len(connected_devices))):
        if (
            "REACHABLE" not in connected_devices[i]
            and "DELAY" not in connected_devices[i]
        ):
            connected_devices.pop(i)

    stdout = subprocess.run(
        ["cat", "/var/lib/misc/dnsmasq.leases"], stdout=subprocess.PIPE, text=True
    )
    previous_connections = stdout.stdout.split("\n")[:-1]

    for connected_device in connected_devices:
        connected_device_list = connected_device.split(" ")
        for previous_connection in previous_connections:
            if connected_device_list[2] in previous_connection:
                final_device_list[connected_device_list[2]] = previous_connection.split(
                    " "
                )[3]

    return final_device_list


def disable_connection(con: str):
    """Set the connection 'con' to down"""
    subprocess.run(["nmcli", "con", "down", con])


def enable_connection(con: str):
    """Set the connection 'con' to up"""
    subprocess.run(["nmcli", "con", "up", con])


def get_wifi_networks() -> dict:
    """Get the list of available wifi networks and their attributes"""
    # gets the list in a layout optimal for scripting, networks seperated by \n, columns seperated by :
    wifi_list = subprocess.run(
        ["nmcli", "-t", "dev", "wifi"], stdout=subprocess.PIPE, text=True
    )
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
    return networks_out


def connect_to_wifi_network(ssid: str, password: str) -> dict:
    """Try to connect to the wifi network with the given arguments"""
    result = subprocess.run(
        ["nmcli", "dev", "wifi", "connect", ssid, "password", password],
        stdout=subprocess.PIPE,
        text=True,
    )
    search_str = "Error:"
    idx = result.stdout.find(search_str)
    if idx >= 0:
        return {"err": f"{result.stdout[len(search_str):].strip()}"}
    return {}


def get_wifi_ip() -> dict:
    try:
        return {"ip": ni.ifaddresses("wlan0")[ni.AF_INET][0]["addr"]}
    except:
        return {"err": "no IP available"}
