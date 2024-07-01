import subprocess
import os
import sys
sys.path.append("/usr/moduline/python")

def get_service(service: str) -> bool:
	return not bool(subprocess.run(["systemctl", "status", service]).returncode)

def set_service(service: str, new_state: bool):
	if new_state:
		subprocess.run(["systemctl", "enable", service])
		subprocess.run(["systemctl", "start", service])
	else:
		subprocess.run(["systemctl", "disable", service])
		subprocess.run(["systemctl", "stop", service])

def get_sim_ver() -> str:
	try:
		with open('/usr/simulink/CHANGELOG.md', 'r') as changelog:
			head = changelog.readline()
		return head.split(' ')[1]
	except:
		return "No changelog found"
	
def get_bt_name() -> str:
	pass

def set_bt_name(name: str):
	pass

def get_hardware() -> str:
	try:
		with open("/sys/firmware/devicetree/base/hardware", "r") as hardware_file:
			return hardware_file.read()
	except:
		return "No hardware description found"

def get_software() -> str:
	try:
		with open("/version.txt", "r") as file:
			return file.readline()
	except:
		try:
			with open("/root/version.txt", "r") as file:
				return file.readline()
		except:
			return "No version file found"

def get_errors() -> dict:
	try:
		import errors
		return errors.get_errors()
	except:
		output = {}
		for i in range(1,6):
			files = os.listdir(f"/usr/mem-diag/{i}")
			for file in files:
				output[file] = ""
		return output

def delete_errors(errors: "list[str]"):
	for file in errors:
		severity = file[0]
		os.remove(f"/usr/mem-diag/{severity}/{file}")
	pass