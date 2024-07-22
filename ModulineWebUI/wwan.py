import json
import subprocess

import ModulineWebUI.controller as controller


def get_wwan() -> bool:
    return controller.get_service("go-wwan")


def set_wwan(new_state: bool) -> bool:
    return controller.set_service("go-wwan", new_state)


def get_sim_num() -> dict:
    pass


def get_wwan_stats() -> dict:
    try:
        modem = subprocess.run(
            ["mmcli", "-J", "--list-modems"], stdout=subprocess.PIPE, text=True
        )
        modem = json.loads(modem.stdout)
        modem_number = modem["modem-list"][0]
        output = subprocess.run(
            ["mmcli", "-J", "--modem=" + modem_number],
            stdout=subprocess.PIPE,
            text=True,
        )
        mmcli = json.loads(output.stdout)
        stats = {}
        stats["imei"] = mmcli["modem"]["3gpp"]["imei"]
        stats["operator"] = mmcli["modem"]["3gpp"]["operator-name"]
        stats["model"] = mmcli["modem"]["generic"]["model"]
        stats["signal"] = mmcli["modem"]["generic"]["signal-quality"]["value"]
        return stats
    except:
        return {"err": "Could not get wwan information"}


def get_apn() -> dict:
    pass


def set_apn(apn: dict):
    pass


def set_pin(pin: dict):
    pass
