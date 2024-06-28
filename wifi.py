import subprocess
import string
import os

def set_wifi(state: bool):
	try:
		if (state):
			os.remove("/etc/modprobe.d/brcmfmac.conf")
			subprocess.run(["modprobe", "brcmfmac"])
		else:
			with open("/etc/modbprobe.d/brcmfmac.conf", "x") as file:
				file.write("blacklist brcmfmac")
			subprocess.run(["modprobe", "-r", "brcmfmac"])
		return True
	except:
		return False

def reload_ap():
	subprocess.run(["nmcli", "con", "reload", "GOcontroll-AP"])

def set_ap_password(new_password: string):
	subprocess.run(["nmcli", "con", "mod", "GOcontroll-AP", "wifi-sec.psk", new_password])

def set_ap_ssid(new_ssid: string):
	subprocess.run(["nmcli", "con", "mod", "GOcontroll-AP", "802-11-wireless.ssid", new_ssid])

def disable_connection(con: string):
	subprocess.run(["nmcli", "con", "down", con])

def enable_connection(con: string):
	subprocess.run(["nmcli", "con", "up", con])