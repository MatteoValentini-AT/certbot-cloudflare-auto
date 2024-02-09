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
            return (int(interval_str[:-1]) * 3600, f"{int(interval_str[:-1])} hour(s)")
        elif interval_str[-1] == "d":
            return (int(interval_str[:-1]) * 3600 * 24, f"{int(interval_str[:-1])} day(s)")
        elif interval_str[-1] == "w":
            return (int(interval_str[:-1]) * 3600 * 24 * 7, f"{int(interval_str[:-1])} week(s)")
        elif interval_str[-1] == "m":
            return (int(interval_str[:-1]) * 3600 * 24 * 30, f"{int(interval_str[:-1])} month(s)")
        else:
            return (int(interval_str) * 3600 * 24, f"{int(interval_str)} day(s)")


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
    if not os.path.isdir("/etc/letsencrypt/dhparams"):
        subprocess.run("mkdir /etc/letsencrypt/dhparams", shell=True)
    if not os.path.isfile("/etc/letsencrypt/dhparams/dhparam.pem"):
        print("\033[32mGenerating dhparams\033[0m", flush=True)
        time.sleep(3)
        subprocess.run("openssl dhparam -out /etc/letsencrypt/dhparams/dhparam.pem 2048 2> /dev/null", shell=True)

def wait_for_next_renewal():
    if os.path.isfile("/etc/letsencrypt/next_renewal"):
        try:
            print("\033[32mWaiting for next renewal\033[0m", flush=True)
            next_renewal = int(open("/etc/letsencrypt/next_renewal", "r").read())
            time.sleep(next_renewal - time.time())
        except Exception as e:
            print(f"\033[31mError while reading next renewal: {e}\033[0m", flush=True)
            exit(1)

def main():
    print("\033[36mcertbot-cloudflare-auto by Matteo Valentini\033[0m", flush=True)
    try:
        with open("config/certs.yml", "r") as f:
            config = yaml.safe_load(f)
            commands = []
            try:
                sections = config["certs"]
                print("\033[32mLoading sections...\033[0m", flush=True)
                if sections is not None:
                    for section in sections.items():
                        commands.append(process_section(section[1], section[0]))
                check_and_generate_dhparams()
                wait_for_next_renewal()
                print("\033[32mCreating certificates\033[0m", flush=True)
                while True:
                    for command in commands:
                        print(f"\033[94mRunning command: \033[0mcertbot certonly {command}", flush=True)
                        subprocess.run(f"certbot certonly {command}", shell=True)
                        time.sleep(3)
                    print(f"\033[32mWaiting {interval[1]} before renewing certificates\033[0m", flush=True)
                    open("/etc/letsencrypt/next_renewal", "w").write(str(int(time.time() + interval[0])))
                    time.sleep(interval[0])
                    print("\033[32mRenewing certificates\033[0m", flush=True)
            except KeyError:
                print("\033[31mMissing certs section in config file\033[0m")
                exit(1)
    except FileNotFoundError:
        print("\033[31mUnable to load config file\033[0m")
        exit(1)
    except Exception as e:
        print(f"\033[31mError: {e}\033[0m")
        exit(1)

main()
