import os
import re
import time
from os.path import exists
import yaml
import subprocess


def get_interval():
    if os.environ.get("CERTBOT_INTERVAL") is None:
        return (3600 * 24 * 30, "30 days")
    else:
        interval_str = os.environ.get("CERTBOT_INTERVAL")
        if not re.fullmatch(r"\d+[hdwmHDWM]?", interval_str):
            print("\033[31mInvalid interval format\033[0m")
            exit(1)
        interval_str = interval_str.lower()
        if interval_str[-1] == "h":
            return (int(interval_str[:-1]) * 3600, f"{int(interval_str[:-1])} hours")
        elif interval_str[-1] == "d":
            return (int(interval_str[:-1]) * 3600 * 24, f"{int(interval_str[:-1])} days")
        elif interval_str[-1] == "w":
            return (int(interval_str[:-1]) * 3600 * 24 * 7, f"{int(interval_str[:-1])} weeks")
        elif interval_str[-1] == "m":
            return (int(interval_str[:-1]) * 3600 * 24 * 30, f"{int(interval_str[:-1])} months")
        else:
            return (int(interval_str) * 3600 * 24, f"{int(interval_str)} days")


interval = get_interval()


def process_section(section, section_name):
    secret = None
    try:
        secret = section["secret"]
    except KeyError:
        print(f"\033[31mMissing secret for section {section_name}\033[0m")
        return
    if not exists(f"/run/secrets/{secret}") and False:
        print(f"\033[31mSecret {secret} for section {section_name} does not exist\033[0m")
        return
    domains = None
    try:
        domains = section["domains"]
    except KeyError:
        print(f"\033[31mMissing domains for section {section_name}\033[0m")
        return
    mail = None
    try:
        mail = section["mail"]
    except KeyError:
        print(f"\033[31mMissing mail for section {section_name}\033[0m")
        return
    additional = ""
    try:
        additional = section["additional_params"]
    except KeyError:
        pass
    request_string = (f"--force-renew -n -q --dns-cloudflare --dns-cloudflare-credentials /run/secrets/{secret} --agree-tos --email {mail} --server https://acme-v02.api"
                      f".letsencrypt.org/directory {additional}")
    print(f"\033[94mSection {section_name}: \033[0m")
    for domain in domains:
        print(f"- {domain}")
    for domain in domains:
        request_string += f" -d {domain}"
    return request_string

def check_and_generate_dhparams():
    if not exists("/etc/letsencrypt/dhparams/dhparam.pem"):
        print("\033[32mGenerating dhparams\033[0m")
        subprocess.run("openssl dhparam -out /etc/letsencrypt/dhparams/dhparam.pem 2048", shell=True)

def main():
    try:
        with open("config/certs.yml", "r") as f:
            config = yaml.safe_load(f)
            commands = []
            try:
                sections = config["certs"]
                print("\033[32mLoading sections...\033[0m")
                for section in sections.items():
                    commands.append(process_section(section[1], section[0]))
                check_and_generate_dhparams()
                print("\033[32mCreating certificates\033[0m")
                while True:
                    for command in commands:
                        print(f"\033[94mRunning command: \033[0mcertbot certonly {command}")
                        subprocess.run(f"certbot certonly {command}", shell=True)
                        time.sleep(3)
                    print(f"\033[32mWaiting {interval[1]} before renewing certificates\033[0m")
                    time.sleep(interval[0])
                    print("\033[32mRenewing certificates\033[0m")
            except KeyError:
                print("\033[31mMissing certs section in config file\033[0m")
                exit(1)
    except FileNotFoundError:
        print("\033[31mUnable to load config file\033[0m")
        exit(1)


main()
