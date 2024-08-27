#!/usr/bin/python3

import hashlib
import ipaddress
import logging
import os
import ssl
import subprocess
import sys
from logging.handlers import RotatingFileHandler

import pkg_resources

from ModulineWebUI.app import app, set_passkey
from ModulineWebUI.conf import create_default_conf, get_conf

logger = logging.getLogger(__name__)
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
using the options overrides the settings in /etc/go_webui.conf
go-webui [options]

options:
-a address          the address to listen on
-p port             the port to listen on
-sslgen             generate a new self signed ssl key/certificate to use
-sslkey path        give a path to an existing sslkey to use
-sslcert path       give a path to an existing sslcert to use
-passkey passkey    pass in a passkey to use to log in
-h                  display this text and exit

default ip = 127.0.0.1
default port = 5000
default passkey (if /etc/go_webui.conf gets generated) = Moduline

examples:
go-webui
go-webui -a 0.0.0.0 -p 7500 -passkey test
go-webui -sslcert cert.pem -sslkey key.pem
go-webui -a 0.0.0.0 -p 7500 -sslgen
"""

def setup_logging():
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set the logging level

    # Format for log messages
    formatter = logging.Formatter('%(asctime)s {%(filename)s:%(lineno)d} %(levelname)s - %(message)s')

    # Create a rotating file handler
    file_handler = RotatingFileHandler('/var/log/go_webui.log', maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


if __name__ == "__main__":
    setup_logging()
    logger.debug("Setup logging...")

    # register the routes from these modules
    from ModulineWebUI.controller import *
    from ModulineWebUI.ethernet import *
    from ModulineWebUI.wifi import *
    from ModulineWebUI.wwan import *

    # process /etc/go_webui.conf
    conf = {}
    try:
        conf = get_conf()
    except FileNotFoundError:
        logger.warning(
            "missing configuration file /etc/go_webui.conf, trying to create a default configuration"
        )
        try:
            create_default_conf()
            conf = get_conf()
        except PermissionError:
            logger.error("not allowed to create default config, trying with arguments")
        except Exception as ex:
            logger.exception("Failed everything")
    except Exception as ex:
        logger.exception("Failed everything")

    # global current_passkey
    ip = conf.get("ip", "127.0.0.1")
    port = conf.get("port", 5000)
    sslg = conf.get("ssl_gen", "false")
    sslc = conf.get("ssl_cert", "")
    sslk = conf.get("ssl_key", "")
    current_passkey = conf.get("pass_hash", "")

    # validate values read from /etc/go_webui.conf
    try:
        ipaddress.IPv4Address(ip)
    except ValueError:
        logger.warning(
            "Invalid IP configured in /etc/go_webui.conf: %s, continuing with default 127.0.0.1",
            ip,
        )
        ip = "127.0.0.1"

    try:
        port = int(port)
    except ValueError:
        logger.warning(
            "Invalid port configured in /etc/go_webui.conf: %s, continuing with default 5000",
            port,
        )
        port = 5000

    try:
        sslg = parse_boolean(sslg)
    except ValueError:
        logger.warning("""ssl_gen parameter in /etc/go_webui.conf is not configured right, check for typos
it should be set to [y]es/[n]o or true/false, not %s.
continuing with the default which is false""", sslg)
        sslg = False
    if sslc != "":
        if not os.path.exists(sslc):
            logger.warning(
                "Could not find ssl certificate at %s, continuing without ssl",
                os.path.abspath(sslc)
            )
            sslc = ""
    if sslk != "":
        if not os.path.exists(sslk):
            logger.warning(
                "Could not find ssl key at %s, continuing without ssl",
                os.path.abspath(sslk)
            )
            sslk = ""

    # current_passkey gets check after parsing arguments

    # process cli arguments

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
            if not os.path.exists(sslk):
                print(f"Could not find ssl key at {os.path.abspath(sslk)}")
                exit(-1)
        elif arg == "-sslcert":
            sslc = next(args)
            if not os.path.exists(sslc):
                print(f"Could not find ssl certificate at {os.path.abspath(sslc)}")
                exit(-1)
        elif arg == "-sslgen":
            sslg = True
        elif arg == "-passkey":
            m = hashlib.sha256(next(args).encode())
            current_passkey = m.hexdigest()
            # print(f"set password hash to {current_passkey}")

    # if no passkey found in /etc/go_webui.conf or passed in through args, exit
    if current_passkey == "":
        print("""No passkey found in /etc/go_webui.conf or in the arguments.
A passkey must be given at all times""")
        exit(-1)

    # register the passkey in the app module
    set_passkey(current_passkey)

    # run the correct version of the server
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

    elif sslc != "" and sslk != "":
        sslctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        sslctx.load_cert_chain(sslc, sslk)
        app.run(host=ip, port=port, ssl=sslctx)

    else:
        app.run(host=ip, port=port)
