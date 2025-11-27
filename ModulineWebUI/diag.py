import json
import logging
import os

logger = logging.getLogger(__name__)

# SAE J1939 FMI codes
fmi_list = [
    "Value too high severe",
    "Value too low severe",
    "Erratic, intermittent or incorrect",
    "Voltage above normal",
    "Voltage below normal",
    "Current below normal",
    "Current above normal",
    "Not responding properly",
    "Abnormal frequency, pulse width, or period",
    "Abnormal update rate",
    "Abnormal rate of change",
    "Other failure mode",
    "Failure",
    "Out of calibration",
    "Special instruction",
    "Value too high warning",
    "Value too high moderate",
    "Value too low warning",
    "Value too low moderate",
    "Data error",
    "Data drifted high",
    "Data drifted low",  # 21
]

# spn mask has a very weird layout
# 0xe0ffff
# 0b1110_0000_1111_1111_1111_1111
# the three bits on the left must be shifted to join the other bytes
spn_mask = 0xFFFF
spn_mask2 = 0x5
fmi_mask = 0x1F

spns = []

def get_spns():
    global spns
    if len(spns):
        return spns
    try:
        with open('/usr/mem-diag/code_descriptor.json', 'r') as spn_map_file:
            # Parsing the JSON file into a Python dictionary
            spns = json.load(spn_map_file)
    except FileNotFoundError as ex:
        logger.error("Could not get spn map at /usr/mem-diag/code_descriptor.json")
        raise ex
    except json.JSONDecodeError as ex:
        logger.error(f"/usr/mem-diag/code_descriptor.json contains invalid JSON\n{ex}")
        raise ex
    return spns

def get_errors() -> "dict | list[dict]":
    spn_map = get_spns()
    output = []
    try:
        files = os.listdir("/usr/mem-diag")
        for file in files:
            try:
                errno = int(file)
            except ValueError:
                continue
            spn = errno & spn_mask + ((errno & (spn_mask2 << 21)) >> 5)
            fmi = (errno >> 16) & fmi_mask
            spn_str = spn_map.get(str(spn), "Unknown SPN")
            try:
                fmi_str = fmi_list[fmi]
            except IndexError:
                fmi_str = "Unknown FMI"
            description = f"{spn_str} - {fmi_str}"
            output.append({"file": file, "fc": spn, "desc": description})

        return output
    except Exception as ex:
        return {"err": f"Could not get errors: {ex}"}

# Function for an entry point in setup.py
def print_errors():
    print(get_errors())