#!/usr/bin/python3

import hashlib
import ipaddress
import os
import ssl
import subprocess
import sys

import pkg_resources

from ModulineWebUI.app import app, set_passkey
from ModulineWebUI.conf import create_default_conf, get_conf

#########################################################################################################


def parse_boolean(boolean: str) -> bool:
    if boolean.lower() in ["y", "yes", "true"]:
        return True
    elif boolean.lower() in ["n", "no", "false"]:
        return False
    else:
        raise ValueError


USAGE = f"""
go-webui V{pkg_resources.require("ModulineWebUI")[0].version}
for permanent settings see /etc/go_webui.conf
go-webui [options]

options:
-a address          the address to listen on
-p port             the port to listen on
-sslgen             generate a new self signed ssl key/certificate to use
-sslkey path        give a path to an existing sslkey to use
-sslcert path       give a path to an existing sslcert to use
-passkey passkey    pas in a passkey to use to log in

default ip = 127.0.0.1
default port = 5000

examples:
go-webui -a 0.0.0.0 -p 7500
go-webui -sslcert cert.pem -sslkey key.pen
go-webui -a 0.0.0.0 -p 7500 -sslgen
"""

if __name__ == "__main__":
    from ModulineWebUI.controller import *
    from ModulineWebUI.ethernet import *
    from ModulineWebUI.wifi import *
    from ModulineWebUI.wwan import *

    conf = {}
    try:
        conf = get_conf()
    except FileNotFoundError:
        print(
            "missing configuration file /etc/go_webui.conf, trying to create a default configuration"
        )
        try:
            create_default_conf()
            conf = get_conf()
        except PermissionError:
            print("not allowed to create default config, trying with arguments")
        except Exception as ex:
            print(ex)
    except Exception as ex:
        print(ex)

    # global current_passkey
    ip = conf.get("ip", "127.0.0.1")
    port = conf.get("port", 5000)
    sslg = conf.get("ssl_gen", "false")
    sslc = conf.get("ssl_cert", "")
    sslk = conf.get("ssl_key", "")
    current_passkey = conf.get("pass_hash", "")

    try:
        sslg = parse_boolean(sslg)
    except ValueError:
        print("""ssl_gen parameter in /etc/go_webui.conf is not configured right, check for typos
it should be set to yes/no or true/false.
continueing with the default which is false""")
        sslg = False

    # parse command line arguments
    args = iter(sys.argv)
    # skip the run argument
    next(args)

    for arg in args:
        if arg == "-a":
            ip = next(args)
            try:
                ipaddress.IPv4Address(ip)
            except ValueError:
                print("given ip address was not valid")
                exit(-1)
        elif arg == "-p":
            try:
                port = int(next(args))
            except ValueError:
                print("given port was not valid")
                exit(-1)
        elif arg == "-h":
            print(USAGE)
            exit(0)
        elif arg == "-sslkey":
            sslk = next(args)
        elif arg == "-sslcert":
            sslc = next(args)
        elif arg == "-sslgen":
            sslg = True
        elif arg == "-passkey":
            m = hashlib.sha256(next(args).encode())
            current_passkey = m.hexdigest()
            # print(f"set password hash to {current_passkey}")
    if current_passkey == "":
        print("""No passkey found in /etc/go_webui.conf or in the arguments.
A passkey must be given at all times""")
        exit(-1)
    set_passkey(current_passkey)
    # add path for the error module
    sys.path.append("/usr/moduline/python")

    if sslg:
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:4096",
                "-nodes",
                "-out",
                "cert.pem",
                "-keyout",
                "key.pem",
                "-days",
                "365",
                "-subj",
                "/C=NL/ST=Gelderland/L=Ulft/O=GOcontroll B.V./OU='.'/CN=GOcontroll",
            ]
        ).check_returncode()
        sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        sslctx.load_cert_chain("cert.pem", "key.pem")
        app.run(host=ip, port=port, ssl=sslctx)
        exit(0)

    if sslc != "" and sslk != "":
        if not os.path.exists(sslc):
            print(f"Could not find entered certificate at {sslc}")
        else:
            if not os.path.exists(sslk):
                print(f"Could not find entered key at {sslk}")
            else:
                sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                sslctx.load_cert_chain(sslc, sslk)
                app.run(host=ip, port=port, ssl=sslctx)
                exit(0)

    app.run(host=ip, port=port)
