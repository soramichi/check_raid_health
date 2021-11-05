#!/usr/bin/env python3

import subprocess
import mail_config
import smtplib
from email.message import EmailMessage

from typing import List, Dict, Any


"""
def exec_mdadm_detail_dummy() -> List[str]:
    ret: List[str] = subprocess.check_output(["cat", "dummy_input.txt"], text=True, stderr=subprocess.DEVNULL).split('\n')[:-1]
    return ret
"""


def exec_mdadm_detail() -> List[str]:
    ret: List[str] = subprocess.check_output(["mdadm", "--detail", "/dev/md0"], text=True, stderr=subprocess.DEVNULL).split('\n')[:-1]
    return ret


def remove_head_spaces(s: str) -> str:
    index = 0
    for i in range(len(s)):
        if s[i] != ' ':
            index = i
            break

    return s[index:]


def notify(title: str):
    print(title)
    msg = EmailMessage()
    msg['Subject'] = title
    msg['From'] = mail_config.from_addr
    msg['To'] = mail_config.to_addr
    
    s = smtplib.SMTP(mail_config.server_addr, mail_config.port)
    s.starttls()
    s.login(mail_config.user, mail_config.password)
    s.send_message(msg)


def notify_bad(n1: int, n2: int):
    title: str = ("Fatal!! RAID1 array degraded!! (%d/%d)" % (n1, n2))
    notify(title)


def notify_good(n1: int, n2: int):
    title: str = ("RAID1 array is properly working (%d/%d)" % (n1, n2))
    notify(title)


def main():
    working_devices_should_be: int = 2
    working_devices_actual: int = 0
    
    lines: List[str] = exec_mdadm_detail()
    for l in lines:
        s: str = remove_head_spaces(l)
        if s.startswith("Working Devices"):
            working_devices_actual = int(s.split(":")[1])

    if working_devices_should_be != working_devices_actual:
        notify_bad(working_devices_should_be, working_devices_actual)
    else:
        notify_good(working_devices_should_be, working_devices_actual)


if __name__ == "__main__":
    main()
