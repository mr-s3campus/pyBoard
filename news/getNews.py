from requests import request, ConnectionError
from bs4 import BeautifulSoup
import json as j
import os, shutil
import constants
import getNewsText


def getNews():
    """Function to fetch all the news about Laurea Magistrale 2035 - Ingegneria Informatica

    Returns:
        list[dict[str: Any]]: news list (JSON formatted)
    """

    path = os.path.join(os.path.curdir + constants.NEWS_PATH)
    defaultPath = os.path.join(os.path.curdir + constants.NEWS_DEFAULT_PATH)

    try:
        page = request(method="get", url=constants.NEWS_URL, timeout=3)
        print("Fetching latest news...")
        soup = BeautifulSoup(page.content, "html.parser")

        newsContainer = soup.find(id="centercontainertemplate-end")
        section = newsContainer.findChildren("section")[1]

        titles = [i.getText() for i in section.findChildren("h2", {"class": "title"})]
        dates = [
            i.getText() for i in section.findChildren("p", {"class": "data-articolo"})
        ]
        contents = [
            i.findParent().getText().split("\n")[3]
            for i in section.findChildren("p", {"class": "data-articolo"})
        ]
        fullContents = [
            getNewsText.getNewsText(i["href"])
            for i in section.findChildren(attrs={"href": True})[5::]
        ]

        articles = [
            {"title": i[0], "date": i[1], "content": i[2], "fullContent": i[3]}
            for i in zip(titles, dates, contents, fullContents)
        ]

        try:
            print("Trying to create file " + path + "...")
            file = open(path, "x", encoding="utf8")
            print("File @ " + path + " doesn't exist -> Creating it...")
            file.close()
        except (FileNotFoundError, FileExistsError):
            print("File @ " + path + " not found/exists -> Continue")
            pass

        jsonArticles = j.dumps(articles, ensure_ascii=False).encode()

        try:
            shutil.copy2(path, defaultPath)
            print("File @ " + path + " backed up...")
        except IOError:
            print("Couldn't back up file @ " + path)

        file = open(path, "w")
        file.write(jsonArticles.decode())
        file.close()
        print("File @ " + path + " overwritten...")

        return articles
    except ConnectionError:
        print("A connection error occurred: using local copy of file @ " + path)
        file = open(defaultPath, "r", encoding="utf8")
        articles = j.loads(file.read())
        file.close()
        return articles
