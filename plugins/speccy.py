# -*- coding: utf-8 -*-

from cloudbot import hook

import re
import requests

from bs4 import BeautifulSoup as BS
from contextlib import closing

url_re = \
    re.compile(
        'https?:\/\/speccy\.piriform\.com\/results\/[a-zA-Z0-9]+', re.I)
GPU_RE = \
    re.compile(
        '.*(amd|radeon|intel|integrated|nvidia|geforce|gtx).*\n.*', re.I)
PICO_RE = \
    re.compile(
        '.*pico', re.I)
KMS_RE = \
    re.compile(
        '.*kms', re.I)
BOOSTER_RE = \
    re.compile(
        '.*booster', re.I)
REVIVER_RE = \
    re.compile(
        '.*reviver', re.I)
KILLER_RE = \
    re.compile(
        '.*killer.+service', re.I)


@hook.regex(url_re)
def get_speccy_url(match):

    with closing(requests.get(match.group(), )) as response:
        soup = BS(response.content, "lxml", from_encoding=response.encoding)

    body = soup.body

    data = []

    os_spec = body.find("div", text='Operating System')
    if os_spec is not None:
        data.append(
            "\x02OS:\x02" + " " + os_spec.next_sibling.next_sibling.text)

    ram_spec = body.find("div", text='RAM')
    if ram_spec is not None:
        data.append(
            "\x02RAM:\x02" + " " + ram_spec.next_sibling.next_sibling.text)

    cpu_spec = body.find("div", text='CPU')
    if cpu_spec is not None:
        data.append(
            "\x02CPU:\x02" + " " + cpu_spec.next_sibling.next_sibling.text)

    def gpuspec():
        gpu_find = body.find("div", text='Graphics')
        if gpu_find is not None:
            gpu_find = gpu_find.next_sibling.next_sibling.text
            gpu_spec = ""
            for gpu_string in GPU_RE.finditer(gpu_find):
                gpu_spec += gpu_string.group()
                return gpu_spec

    gpu_spec = gpuspec()
    if gpu_spec is not None:
        data.append("\x02GPU:\x02" + " " + gpu_spec)

    def cspace():
        c_space_spec = body.find("div", class_="datavalue", text='C:')
        if c_space_spec is not None:
            c_space_spec_found = c_space_spec.parent.parent
            c_space_data = c_space_spec_found.find(
                "div", text='Free Space:\xA0', class_="datakey").parent
            return c_space_data.find(class_="datavalue").text

    c_space_spec = cspace()
    if c_space_spec is not None:
        data.append("\x02Space Left (C:\):\x02" + " " + c_space_spec)

    def ramusg():
        ram_usg_spec = body.find(
            "div", class_="blue clear", text='Physical Memory')
        if ram_usg_spec is not None:
            ram_usg_spec_found = ram_usg_spec.next_sibling.next_sibling
            ram_usg_data = ram_usg_spec_found.find(
                "div", text='Memory Usage:\xA0', class_="datakey").parent
            return ram_usg_data.find(class_="datavalue").text

    ram_usg_spec = ramusg()
    if ram_usg_spec is not None:
        data.append("\x02RAM USG:\x02" + " " + ram_usg_spec)

    badware_patterns = [KILLER_RE, REVIVER_RE, BOOSTER_RE, KMS_RE, PICO_RE]
    badware = body.find_all("div", text=badware_patterns)
    if badware:
        for tag in badware:
            data.append("\x02Badware:\x02" + " " + tag.text)
    else:
        data.append("\x02No Badware\x02")

    drive_spec_bad = False
    for drive_spec_smart in body.find_all(
            "div", class_="blue clear", text="05"):
        drive_spec_smart_find = \
            drive_spec_smart.next_sibling.next_sibling
        for drive_spec_smart_found in drive_spec_smart_find.find_all(
                "div", class_="datakey", text="Raw Value:\xA0"):
            drives = drive_spec_smart_found.next_sibling.next_sibling
            if "0000000000" in drives != 0:
                str.strip('0')
            else:
                drive_spec_sn_find = drive_spec_smart.parent.parent \
                    .previous_sibling.previous_sibling.previous_sibling \
                    .previous_sibling.previous_element.previous_element \
                    .previous_sibling.previous_sibling
                for drive_spec_sn_check in drive_spec_sn_find.find_all(
                        "div", class_="datakey", text="Serial Number:\xA0"):
                    drive_spec_sn = \
                        drive_spec_sn_check.next_sibling.next_sibling.text
                    drive_spec_bad = True
                    if drive_spec_bad is True:
                        data.append(
                            "\x02Bad Disk:\x02 S/N: {}".format(drive_spec_sn))

    if drive_spec_bad is False:
        data.append("\x02Disks Healthy\x02")

    spec_out = re.sub(r"\s+", " ", ' ● '.join(data))

    return spec_out
