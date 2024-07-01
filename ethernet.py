import subprocess
import netifaces as ni
import ipaddress

def get_ethernet_mode() -> str:
	stdout = subprocess.run(["nmcli", "-t", "con"], stdout=subprocess.PIPE, text=True)
	result = stdout.stdout
	result = result.split("\n")
	mode = "unknown"
	for name in result:
		if "Wired connection static" in name:
			if "eth0" in name:
				mode = "static"
				break
		elif "Wired connection auto" in name:
			if "eth0" in name:
				mode = "auto"
				break
	return mode

def set_ethernet_mode(mode: str) -> bool:
	if mode == "static":
		subprocess.run(["nmcli", "con", "mod", "Wired connection auto", "connection.autoconnect", "no"])
		subprocess.run(["nmcli", "con", "mod", "Wired connection static", "connection.autoconnect", "yes"])
		subprocess.run(["nmcli", "con", "down", "Wired connection auto"])
		subprocess.run(["nmcli", "con", "up", "Wired connection static"])
		return True
	elif mode == "auto":
		subprocess.run(["nmcli", "con", "mod", "Wired connection static", "connection.autoconnect", "no"])
		subprocess.run(["nmcli", "con", "mod", "Wired connection auto", "connection.autoconnect", "yes"])
		subprocess.run(["nmcli", "con", "down", "Wired connection static"])
		subprocess.run(["nmcli", "con", "up", "Wired connection auto"])
		return True
	return False

def set_static_ip(ip: str) -> str:
	try:
		ipaddress.ip_address(ip)
	except ValueError:
		return "Error: Invalid IP"
	subprocess.run(["nmcli", "con", "mod", "Wired connection static", "ipv4.addresses", ip+"/16"])
	if get_ethernet_mode() == "static":
		subprocess.run(["nmcli", "con", "down", "Wired connection static"])
		subprocess.run(["nmcli", "con", "up", "Wired connection static"])
	return "Success"

def get_static_ip() -> str:
	pass

def get_ethernet_ip() -> str:
	try:
		return ni.ifaddresses("eth0")[ni.AF_INET][0]["addr"]
	except:
		return "no IP available"