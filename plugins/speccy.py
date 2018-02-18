# -*- coding: utf-8 -*-
from cloudbot import hook

import re
import requests

from bs4 import BeautifulSoup as BS
from contextlib import closing

url_re = re.compile('https?:\/\/speccy.piriform.com\/results\/[A-z0-9]+', re.I)


@hook.regex(url_re)
def get_speccy_url(message, match, chan, nick):

    with closing(requests.get(match.group(), stream=True,
                              timeout=3)) as response:
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
    gpuspec = ""
    for gpustring in re.finditer(
            r'.*(amd|radeon|intel|integrated|nvidia|geforce|gtx).*\n.*',
            gpufind, re.IGNORECASE):
        gpuspec += gpustring.group()
    if gpuspec:
        data.append("\x02GPU:\x02" + " " + gpuspec)

    picospec = body.find("div", text=re.compile('.*pico', re.I))
    if picospec:
        data.append("\x02Badware:\x02" + " " + picospec.text)

    kmsspec = body.find("div", text=re.compile('.*kms', re.I))
    if kmsspec:
        data.append("\x02Badware:\x02" + " " + kmsspec.text)

    boosterspec = body.find("div", text=re.compile('.*booster', re.I))
    if boosterspec:
        data.append("\x02Badware:\x02" + " " + boosterspec.text)

    reviverspec = body.find("div", text=re.compile('.*reviver', re.I))
    if reviverspec:
        data.append("\x02Badware:\x02" + " " + reviverspec.text)

    killerspec = body.find("div", text=re.compile('.*Killer.+Service', re.I))
    if killerspec:
        data.append("\x02Badware:\x02" + " " + killerspec.text)

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

    try:
        z = smartcheck()
        if len(z) != 0:
            smartspec = ""
            for item in z:
                smartspec += data.append("\x02Bad Disk:\x02" +
                                         (smartspec) + " #" + item + " ")
        else:
            smartspec = None
    except Exception:
        smartspec = None

    specout = re.sub("\s{2,}|\r\n|\n", " ", str(' + '.join(data)))

    return specout

