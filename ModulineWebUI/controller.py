import json
import os
import subprocess

from microdot import Request, send_file
from microdot.session import Session, with_session

from ModulineWebUI.app import app, auth


# services
def get_service(service: str) -> bool:
    return not bool(subprocess.run(["systemctl", "is-active", service]).returncode)


@app.post("/api/get_service")
@with_session
@auth
async def get_service_route(req: Request, session: Session):
    service: str = req.json
    return json.dumps({"state": get_service(service)})


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
    return json.dumps({"new_state": set_service(service, new_state)})


# simulink
@app.get("/api/get_sim_ver")
@with_session
@auth
async def get_sim_ver(req: Request, session: Session):
    try:
        with open("/usr/simulink/CHANGELOG.md", "r") as changelog:
            head = changelog.readline()
        return json.dumps({"version": head.split(" ")[1]})
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
            return json.dumps({"hardware": hardware_file.read()})
    except Exception as ex:
        return json.dumps({"err": f"No hardware description found\n{ex}"})


@app.get("/api/get_software")
@with_session
@auth
async def get_software(req: Request, session: Session):
    try:
        with open("/version.txt", "r") as file:
            return json.dumps({"version": file.readline()})
    except:
        try:
            with open("/root/version.txt", "r") as file:
                return json.dumps({"version": file.readline()})
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
        import errors

        return json.dumps(errors.get_errors())
    # default route
    except:
        output = []
        try:
            for i in range(1, 6):
                files = os.listdir(f"/usr/mem-diag/{i}")
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
            severity = file[0]
            os.remove(f"/usr/mem-diag/{severity}/{file}")
            return json.dumps({})
    except Exception as ex:
        return json.dumps({"err": f"Could not delete all requested errors\n{ex}"})


# modules
def get_modules() -> dict:
    pass


def scan_modules() -> dict:
    pass


def update_modules() -> dict:
    pass


def overwrite_module(module: int, firmware: str) -> dict:
    pass
