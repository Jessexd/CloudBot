# -*- coding: utf-8 -*-
from cloudbot import hook

import re
import requests

from bs4 import BeautifulSoup as BS
from contextlib import closing

url_re = re.compile('https?:\/\/speccy\.piriform\.com\/results\/[a-zA-Z0-9]+',
                    re.I)

PICO_RE = re.compile('.*pico', re.I)
KMS_RE = re.compile('.*kms', re.I)
BOOSTER_RE = re.compile('.*booster', re.I)
REVIVER_RE = re.compile('.*reviver', re.I)
KILLER_RE = re.compile('.*Killer.+Service', re.I)


@hook.regex(url_re)
def get_speccy_url(match):

    with closing(requests.get(match.group(), )) as response:
        soup = BS(response.content, "lxml", from_encoding=response.encoding)

    body = soup.body

    data = []

    osspec = body.find("div", text='Operating System')
    if osspec:
        data.append(
            "\x02OS:\x02" + " " + osspec.next_sibling.next_sibling.text)

    ramspec = body.find("div", text='RAM')
    if ramspec:
        data.append(
            "\x02RAM:\x02" + " " + ramspec.next_sibling.next_sibling.text)

    cpuspec = body.find("div", text='CPU')
    if cpuspec:
        data.append(
            "\x02CPU:\x02" + " " + cpuspec.next_sibling.next_sibling.text)

    gpufind = body.find("div", text='Graphics').next_sibling.next_sibling.text
    GPU_RE = re.finditer(
        r'.*(amd|radeon|intel|integrated|nvidia|geforce|gtx).*\n.*', gpufind,
        re.IGNORECASE)
    gpuspec = ""
    for gpustring in GPU_RE:
        gpuspec += gpustring.group()
    if gpuspec:
        data.append("\x02GPU:\x02" + " " + gpuspec)

    picospec = body.find("div", text=PICO_RE)
    if picospec:
        data.append("\x02Bad:\x02" + " " + picospec.text)

    kmsspec = body.find("div", text=KMS_RE)
    if kmsspec:
        data.append("\x02Bad:\x02" + " " + kmsspec.text)

    boosterspec = body.find("div", text=BOOSTER_RE)
    if boosterspec:
        data.append("\x02Bad:\x02" + " " + boosterspec.text)

    reviverspec = body.find("div", text=REVIVER_RE)
    if reviverspec:
        data.append("\x02Bad:\x02" + " " + reviverspec.text)

    killerspec = body.find("div", text=KILLER_RE)
    if killerspec:
        data.append("\x02Bad:\x02" + " " + killerspec.text)

    def smartcheck():
        drivespec = body.find_all("div", text="05")
        number_of_drives = len(drivespec)

        values = []
        for i in range(0, number_of_drives):
            z = drivespec[i].next_sibling.next_sibling.stripped_strings
            saucy = list(z)
            rv_index = saucy.index("Raw Value:")
            raw_value = saucy[rv_index + 1]
            if raw_value != "0000000000":
                values.append(str(i + 1))
        return values

    z = smartcheck()
    if z:
        for item in z:
            data.append("\x02Bad Disk:\x02 #{}".format(item))

    specout = re.sub(r"\s+", " ", ' ● '.join(data))

    return specout
