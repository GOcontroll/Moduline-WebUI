import json
import subprocess

from microdot import Request
from microdot.session import Session, with_session

from ModulineWebUI.controller import get_service, set_service
from ModulineWebUI.go_webui import app, auth


@app.get("/api/get_wwan")
@with_session
@auth
async def get_wwan(req: Request, session: Session):
    return json.dumps({"state": get_service("go-wwan")})


@app.post("/api/set_wwan")
@with_session
@auth
async def set_wwan(req: Request, session: Session):
    new_state = req.json["new_state"]
    return json.dumps({"new_state": set_service("go-wwan", new_state)})


def get_sim_num() -> dict:
    pass


@app.get("/api/get_wwan_stats")
@with_session
@auth
async def get_wwan_stats(req: Request, session: Session):
    try:
        modem = subprocess.run(
            ["mmcli", "-J", "--list-modems"], stdout=subprocess.PIPE, text=True
        )
        modem.check_returncode()
        modem = json.loads(modem.stdout)
        modem_number = modem["modem-list"][0]
        output = subprocess.run(
            ["mmcli", "-J", "--modem=" + modem_number],
            stdout=subprocess.PIPE,
            text=True,
        )
        output.check_returncode()
        mmcli = json.loads(output.stdout)
        stats = {}
        stats["imei"] = mmcli["modem"]["3gpp"]["imei"]
        stats["operator"] = mmcli["modem"]["3gpp"]["operator-name"]
        stats["model"] = mmcli["modem"]["generic"]["model"]
        stats["signal"] = mmcli["modem"]["generic"]["signal-quality"]["value"]
        return json.dumps(stats)
    except:
        return json.dumps({"err": "Could not get wwan information"})


def get_apn() -> dict:
    pass


def set_apn(apn: dict):
    pass


def set_pin(pin: dict):
    pass
