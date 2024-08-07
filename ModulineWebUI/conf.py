import hashlib


def get_conf() -> dict:
    conf = {}
    with open("/etc/go_webui.conf", "r") as conf_file:
        for line in conf_file.readlines():
            if line.startswith("#"):
                continue
            option = line.split("=", 1)
            if len(option) == 2:
                conf[option[0].strip().lower()] = option[1].strip()
    return conf


def create_default_conf():
    with open("/etc/go_webui.conf", "x") as conf_file:
        default_hash = hashlib.sha256("Moduline".encode()).hexdigest()
        conf_file.write(f"""#the ip the server listens on
ip=127.0.0.1
#the port the server listens on
port=5000
#generate a new ssl certificate/key when this program is executed
ssl_gen=false
#set ssl_key with a path to your ssl certificate, does nothing if ssl_gen is true
ssl_cert=
#set ssl_key with a path to your ssl key, does nothing if ssl_gen is true
ssl_key=
#set pass_hash with a sha256 of your passkey, the default value is the has of "Moduline"
pass_hash={default_hash}""")


def modify_conf(key: str, val: str):
    try:
        conf = get_conf()
    except FileNotFoundError:
        create_default_conf()
    conf = get_conf()
    conf[key] = val
    write_conf(conf)


def write_conf(conf: dict):
    with open("/etc/go_webui.conf", "w") as conf_file:
        for key, value in conf.items():
            if key in ["ip", "port", "ssl_gen", "ssl_cert", "ssl_key", "pass_hash"]:
                conf_file.write(f"{key}={value}\n")
            pass
