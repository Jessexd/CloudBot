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
    if os_spec is not None:
        data.append(
            "\x02OS:\x02" + " " + os_spec.next_sibling.next_sibling.text)

    def cspace():
        c_space_spec = body.find("div", class_="datavalue", text='C:')
        if c_space_spec is not None:
            c_space_spec_found = c_space_spec.parent.parent
            c_space_data = c_space_spec_found.find("div", text='Free Space:\xA0', class_="datakey").parent
            return c_space_data.find(class_="datavalue").text

    c_space_spec = cspace()
    if c_space_spec is not None:
        data.append("\x02Space Left (C:\):\x02" + " " + c_space_spec)

    ram_spec = body.find("div", text='RAM')
    if ram_spec is not None:
        data.append(
            "\x02RAM:\x02" + " " + ram_spec.next_sibling.next_sibling.text)

    def ramusg():
        ram_usg_spec = body.find("div", class_="blue clear", text='Physical ramory')
        if ram_usg_spec is not None:
            ram_usg_spec_found = ram_usg_spec.next_sibling.next_sibling
            ram_usg_data = ram_usg_spec_found.find("div", text='Memory Usage:\xA0', class_="datakey").parent
            return ram_usg_data.find(class_="datavalue").text

    ram_usg_spec = ramusg()
    if ram_usg_spec is not None:
        data.append("\x02RAM USG:\x02" + " " + ram_usg_spec)

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

    has_badware = False

    pico_spec = body.find("div", text=PICO_RE)
    if pico_spec is not None:
        has_badware = True
        data.append("\x02Badware:\x02" + " " + pico_spec.text)

    kms_spec = body.find("div", text=KMS_RE)
    if kms_spec is not None:
        has_badware = True
        data.append("\x02Badware:\x02" + " " + kms_spec.text)

    booster_spec = body.find("div", text=BOOSTER_RE)
    if booster_spec is not None:
        has_badware = True
        data.append("\x02Badware:\x02" + " " + booster_spec.text)

    reviver_spec = body.find("div", text=REVIVER_RE)
    if reviver_spec is not None:
        has_badware = True
        data.append("\x02Badware:\x02" + " " + reviver_spec.text)

    killer_spec = body.find("div", text=KILLER_RE)
    if killer_spec is not None:
        has_badware = True
        data.append("\x02Badware:\x02" + " " + killer_spec.text)

    if not has_badware:
        data.append("\x02No Badware\x02")

    def smartcheck():
        drive__spec = body.find_all("div", class_="blue clear", text="05")
        drive_spec_SMART_checked = body.find("div", class_="blue clear", text="05")
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
    if drives is not None:
        for item in drives:
            data.append("\x02Bad Disk:\x02 #{}".format(item))
    else:
        data.append("\x02Disks Healthy\x02")

    spec_out = re.sub(r"\s+", " ", ' ● '.join(data))

    return spec_out
