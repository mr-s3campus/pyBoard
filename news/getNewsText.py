from requests import request, ConnectionError, ReadTimeout
from bs4 import BeautifulSoup


def getNewsText(link: str):
    try:
        page = request(method="get", url=link, timeout=10)
        print("Fetching full news text @ ", link, "...")
        soup = BeautifulSoup(page.content, "html.parser")
        content = soup.find("div", {"id": "readcontent"}).findChildren("p")

        text = ""
        text = text.join(str(x) for x in content[1::])

        if text == "":
            content = soup.find("div", {"id": "readcontent"}).findChildren("div")
            text = text.join(str(x) for x in content[3:4:])

        return text
    except ReadTimeout:
        raise ConnectionError
