import subprocess
import os
import sys

def get_service(service: str) -> bool:
	return not bool(subprocess.run(["systemctl", "is-active", service]).returncode)

def set_service(service: str, new_state: bool):
	try:
		if new_state:
			subprocess.run(["systemctl", "enable", service]).check_returncode()
			subprocess.run(["systemctl", "start", service]).check_returncode()
		else:
			subprocess.run(["systemctl", "disable", service]).check_returncode()
			subprocess.run(["systemctl", "stop", service]).check_returncode()
		return new_state
	except:
		return not new_state

def get_sim_ver() -> dict:
	try:
		with open('/usr/simulink/CHANGELOG.md', 'r') as changelog:
			head = changelog.readline()
		return {"version": head.split(' ')[1]}
	except:
		return {"err": "No changelog found"}
	
def get_bt_name() -> str:
	pass

def set_bt_name(name: str):
	pass

def get_hardware() -> dict:
	try:
		with open("/sys/firmware/devicetree/base/hardware", "r") as hardware_file:
			return {"hardware": hardware_file.read()}
	except:
		return {"err": "No hardware description found"}

def get_software() -> dict:
	try:
		with open("/version.txt", "r") as file:
			return {"version": file.readline()}
	except:
		try:
			with open("/root/version.txt", "r") as file:
				return {"version": file.readline()}
		except:
			return {"err":"No version file found"}
		
def get_serial_number() -> dict:
	try:
		res = subprocess.run(["go-sn", "r"], stdout=subprocess.PIPE, text=True)
		if res.returncode:
			return {"err": "Could not get the serial number"}
		else:
			return {"sn": res.stdout.strip()}
	except:
		return {"err": "Could not get the serial number"}

def get_errors() -> "list[dict]":
	try:
		import errors
		sys.path.append("/usr/moduline/python")
		return errors.get_errors()
	except:
		output = []
		try:
			for i in range(1,6):
				files = os.listdir(f"/usr/mem-diag/{i}")
				for file in files:
					output.append({"fc": file})
			return output
		except:
			return {"err": "Could not get errors"}
			# return [{"fc": "test", "desc": "test error"}]

def delete_errors(errors: "list[str]") -> dict:
	try:
		for file in errors:
			severity = file[0]
			os.remove(f"/usr/mem-diag/{severity}/{file}")
			return {}
	except:
		return {"err": "Could not delete all requested errors."}

def get_modules() -> dict:
	pass

def scan_modules() -> dict:
	pass

def update_modules() -> dict:
	pass

def overwrite_module(module: int, firmware: str) -> dict:
	pass