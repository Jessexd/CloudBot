# -*- coding: utf-8 -*-

from cloudbot import hook

import re
import requests

from bs4 import BeautifulSoup as BS
from contextlib import closing

url_re = re.compile('https?:\/\/speccy\.piriform\.com\/results\/[a-zA-Z0-9]+', re.I)

GPU_RE = re.compile('.*(amd|radeon|intel|integrated|nvidia|geforce|gtx).*\n.*', re.I)
PICO_RE = re.compile('.*pico', re.I)
KMS_RE = re.compile('.*kms', re.I)
BOOSTER_RE = re.compile('.*booster', re.I)
REVIVER_RE = re.compile('.*reviver', re.I)
KILLER_RE = re.compile('.*killer.+service', re.I)


@hook.regex(url_re)
def get_speccy_url(match):

    with closing(requests.get(match.group(), )) as response:
        soup = BS(response.content, "lxml", from_encoding=response.encoding)

    body = soup.body

    data = []

    os_spec = body.find("div", text='Operating System')
    if os_spec:
        data.append(
            "\x02OS:\x02" + " " + os_spec.next_sibling.next_sibling.text)

    def cspace():
        c_drive = body.find("div", class_="datavalue", text='C:')
        if c_drive is not None:
            c_drive = body.parent.parent
            c_free_space_data = c_drive.find(
                "div", text='Free Space:\xA0', class_="datakey").parent
            return c_free_space_data.find(class_="datavalue").text

    if cspace():
        data.append("\x02Space Left (C:\):\x02" + " " + cspace())

    ram_spec = body.find("div", text='RAM')
    if ram_spec:
        data.append(
            "\x02RAM:\x02" + " " + ram_spec.next_sibling.next_sibling.text)

    ram_usg_spec = body.find(
        "div", class_="blue clear",
        text='Physical Memory').next_sibling.next_sibling.find(
            "div", text='Memory Usage:\xA0',
            class_="datakey").parent.find(class_="datavalue").text
    if ram_usg_spec:
        data.append("\x02RAM Usg:\x02" + " " + ram_usg_spec)

    cpu_spec = body.find("div", text='CPU')
    if cpu_spec:
        data.append(
            "\x02CPU:\x02" + " " + cpu_spec.next_sibling.next_sibling.text)

    gpu_find = body.find("div", text='Graphics').next_sibling.next_sibling.text
    gpu_spec = ""
    for gpu_string in GPU_RE.finditer(gpu_find):
        gpu_spec += gpu_string.group()
    if gpu_spec:
        data.append("\x02GPU:\x02" + " " + gpu_spec)

    pico_spec = body.find("div", text=PICO_RE)
    if pico_spec:
        data.append("\x02Badware:\x02" + " " + pico_spec.text)

    kms_spec = body.find("div", text=KMS_RE)
    if kms_spec:
        data.append("\x02Badware:\x02" + " " + kms_spec.text)

    booster_spec = body.find("div", text=BOOSTER_RE)
    if booster_spec:
        data.append("\x02Badware:\x02" + " " + booster_spec.text)

    reviver_spec = body.find("div", text=REVIVER_RE)
    if reviver_spec:
        data.append("\x02Badware:\x02" + " " + reviver_spec.text)

    killer_spec = body.find("div", text=KILLER_RE)
    if killer_spec:
        data.append("\x02Badware:\x02" + " " + killer_spec.text)

    if 'Badware' not in data:
        data.append("\x02No Badware\x02")

    def smartcheck():
        drive__spec = body.find_all("div", class_="blue clear", text="05")
        drive_spec_SMART_checked = body.find(
            "div", class_="blue clear", text="05")
        if drive_spec_SMART_checked is not None:
            values = []
            for i, found in enumerate(drive__spec):
                drives = found.next_sibling.next_sibling.stripped_strings
                SMART = list(drives)
                rv_index = SMART.index("Raw Value:")
                raw_value = SMART[rv_index + 1]
                if raw_value != "0000000000":
                    values.append(str(i + 1))
            return values

    drives = smartcheck()
    if drives:
        for item in drives:
            data.append("\x02Bad Disk:\x02 #{}".format(item))
    else:
        data.append("\x02Disks Healthy\x02")

    specout = re.sub(r"\s+", " ", ' ● '.join(data))

    return specout
