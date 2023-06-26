from requests import request
from bs4 import BeautifulSoup
import json as j
import constants


def getLessons(aa: str, cc: str, aci: str, codInd: str):
    """This function get lessons from university website

    Args:
        aa (str): academic year
        cc (str): course code
        aci (str): course year
        codInd (str): course address code

    Returns:
        list: lessons list

    example: getLessons('2022/2023','2035','1','796')"""

    page = request(
        method="get",
        url=constants.CALENDAR_URL,
        params={"aa": aa, "cc": cc, "aci": aci, "codInd": codInd},
        timeout=3,
    )

    # BeautifulSoup makes a python editable representation of a web page
    soup = BeautifulSoup(page.content, "html.parser")
    a = soup.findAll("script")

    # eventsNumber within the calendar
    eventsNumber = None
    for i in range(len(a)):
        if str(a[i]).find('var events = {"result"') != -1:
            eventsNumber = i

    lessons = j.loads(
        (str(str(a[eventsNumber].getText()).split("\n")[2]).split("= ")[1])[:-1]
    )["result"]

    return lessons
