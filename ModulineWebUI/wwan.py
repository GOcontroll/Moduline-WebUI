import json

from microdot import Request
from microdot.session import Session, with_session

from PyModuline import wwan

from ModulineWebUI.app import app, auth


@app.get("/api/get_wwan")
@with_session
@auth
async def get_wwan(req: Request, session: Session):
    return json.dumps({"state": wwan.get_wwan()})


@app.post("/api/set_wwan")
@with_session
@auth
async def set_wwan(req: Request, session: Session):
    new_state = req.json["new_state"]
    is_changed, error = wwan.set_wwan(new_state)
    if is_changed:
        return json.dumps({"new_state": new_state})
    else:
        raise EnvironmentError(f"could not switch state to {new_state}\n{error}")

@app.post("/api/set_sim_num")
@with_session
@auth
async def get_sim_num(req: Request, session: Session):
    return json.dumps(wwan.get_sim_num())


@app.get("/api/get_wwan_stats")
@with_session
@auth
async def get_wwan_stats(req: Request, session: Session):
    return json.dumps(wwan.get_wwan_stats())

@app.post("/api/get_apn")
@with_session
@auth
async def get_apn(req: Request, session: Session):
    json.dumps(wwan.get_apn())

@app.post("/api/set_apn")
@with_session
@auth
async def set_apn(req: Request, session: Session):
    new_apn: str = req.json["new_apn"]
    wwan.set_apn(new_apn)
    return json.dumps({})

@app.post("/api/set_pin")
@with_session
@auth
async def set_pin(req: Request, session: Session):
    new_pin: str = req.json["new_pin"]
    wwan.set_pin(new_pin)
    return json.dumps({})
