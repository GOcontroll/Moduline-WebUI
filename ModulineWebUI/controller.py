import json

from microdot import Request, send_file
from microdot.session import Session, with_session
from PyModuline import internal, services

from ModulineWebUI.app import app, auth


@app.post("/api/get_service")
@with_session
@auth
async def get_service_route(req: Request, session: Session):
    service: str = req.json
    if service not in services.get_service_blacklist() and service in services.services:
        return json.dumps({"state": services.get_service(service)})
    else:
        raise EnvironmentError("Service doesn't exist or is not allowed to be viewed")


@app.post("/api/set_service")
@with_session
@auth
async def set_service_route(req: Request, session: Session):
    data = req.json
    new_state: bool = data["new_state"]
    service: str = data["service"]
    if service not in services.get_service_blacklist() and service in services.services:
        is_changed, error = services.set_service(service, new_state)
        if is_changed:
            return json.dumps({"new_state": new_state})
        else:
            return json.dumps(
                {"err": f"Failed to change service '{service}' state {error}"}
            )
    else:
        raise EnvironmentError("Service doesn't exist or is not allowed to be set")


# simulink
@app.get("/api/get_sim_ver")
@with_session
@auth
async def get_sim_ver(req: Request, session: Session):
    return json.dumps({"version": internal.get_sim_ver()})


@app.get("/api/GOcontroll_Linux.a2l")  # last part of route determines file name
@with_session
@auth
async def a2l_down(req: Request, session: Session):
    return send_file("/usr/simulink/GOcontroll_Linux.a2l")


# controller info
@app.get("/api/get_hardware")
@with_session
@auth
async def get_hardware(req: Request, session: Session):
    return json.dumps({"hardware": internal.get_hardware()})


@app.get("/api/get_software")
@with_session
@auth
async def get_software(req: Request, session: Session):
    return json.dumps({"software": internal.get_software()})


@app.get("/api/get_serial_number")
@with_session
@auth
async def get_serial_number(req: Request, session: Session):
    return json.dumps({"sn": internal.get_serial_number()})


# errors
@app.get("/api/get_errors")
@with_session
@auth
async def get_errors(req: Request, session: Session):
    return json.dumps(internal.get_errors())


@app.post("/api/delete_errors")
@with_session
@auth
async def delete_errors(req: Request, session: Session):
    errors: "list[str]" = req.json
    internal.delete_errors(errors)
    return json.dumps({})
