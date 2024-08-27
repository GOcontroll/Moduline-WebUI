import json
import os
import subprocess

from microdot import Request, send_file
from microdot.session import Session, with_session

from ModulineWebUI.app import app, auth

# keep this list up to date with index 0 of the list in services.js
# this list limits the services that can be accessed through this api
services = [
    "ssh",
    "go-simulink",
    "nodered",
    "go-bluetooth",
    "go-upload-server",
    "go-auto-shutdown",
    "gadget-getty@ttyGS0",
    "getty@ttymxc2",
]


# services
def get_service(service: str) -> bool:
    return not bool(subprocess.run(["systemctl", "is-active", service]).returncode)


@app.post("/api/get_service")
@with_session
@auth
async def get_service_route(req: Request, session: Session):
    service: str = req.json
    if service in services:
        return json.dumps({"state": get_service(service)})
    else:
        return json.dumps({"err": "Invalid service"})


def set_service(service: str, new_state: bool) -> bool:
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


@app.post("/api/set_service")
@with_session
@auth
async def set_service_route(req: Request, session: Session):
    data = req.json
    new_state: bool = data["new_state"]
    service: str = data["service"]
    if service in services:
        return json.dumps({"new_state": set_service(service, new_state)})
    else:
        return json.dumps({"err": "Invalid service"})


# simulink
@app.get("/api/get_sim_ver")
@with_session
@auth
async def get_sim_ver(req: Request, session: Session):
    try:
        with open("/usr/simulink/CHANGELOG.md", "r") as changelog:
            head = changelog.readline()
        return json.dumps({"version": head.split(" ")[1].strip()})
    except Exception as ex:
        return json.dumps({"err": f"No changelog found\n{ex}"})


@app.get("/api/GOcontroll_Linux.a2l")  # last part of route determines file name
@with_session
@auth
async def a2l_down(req: Request, session: Session):
    return send_file("/usr/simulink/GOcontroll_Linux.a2l")


# bt
def get_bt_name() -> str:
    pass


def set_bt_name(name: str):
    pass


# controller info
@app.get("/api/get_hardware")
@with_session
@auth
async def get_hardware(req: Request, session: Session):
    try:
        with open("/sys/firmware/devicetree/base/hardware", "r") as hardware_file:
            return json.dumps({"hardware": hardware_file.read().strip()})
    except Exception as ex:
        return json.dumps({"err": f"No hardware description found\n{ex}"})


@app.get("/api/get_software")
@with_session
@auth
async def get_software(req: Request, session: Session):
    try:
        with open("/version.txt", "r") as file:
            return json.dumps({"version": file.readline().strip()})
    except:
        try:
            with open("/root/version.txt", "r") as file:
                return json.dumps({"version": file.readline().strip()})
        except Exception as ex:
            return json.dumps({"err": f"No version file found\n{ex}"})


@app.get("/api/get_serial_number")
@with_session
@auth
async def get_serial_number(req: Request, session: Session):
    try:
        res = subprocess.run(["go-sn", "r"], stdout=subprocess.PIPE, text=True)
        res.check_returncode()
        return json.dumps({"sn": res.stdout.strip()})
    except subprocess.CalledProcessError as ex:
        return json.dumps({"err": f"Could not get the serial number\n{ex.output}"})
    except Exception as ex:
        return json.dumps({"err": f"Could not get the serial number\n{ex}"})


# errors
@app.get("/api/get_errors")
@with_session
@auth
async def get_errors(req: Request, session: Session):
    # try to import a custom get_errors script
    try:
        import modulinedtc.errors as errors

        return json.dumps(errors.get_errors())
    # default route
    except:
        output = []
        try:
            files = os.listdir("/usr/mem-diag")
            for file in files:
                output.append({"fc": file})
            return json.dumps(output)
        except Exception as ex:
            return json.dumps({"err": f"Could not get errors\n{ex}"})


@app.post("/api/delete_errors")
@with_session
@auth
async def delete_errors(req: Request, session: Session):
    errors: "list[str]" = req.json
    try:
        for file in errors:
            if ".." in file:
                continue
            os.remove(f"/usr/mem-diag/{file}")
    except Exception as ex:
        return json.dumps({"err": f"Could not delete all requested errors\n{ex}"})
    return json.dumps({})


# modules
def get_modules() -> dict:
    pass


def scan_modules() -> dict:
    pass


def update_modules() -> dict:
    pass


def overwrite_module(module: int, firmware: str) -> dict:
    pass
