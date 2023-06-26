from requests import ConnectionError
from datetime import datetime
import json as j
import os
import constants
import getLessons
import cleanTimetable


def buildTimetable(date: str, aa: str, cc: str, aci: str, codInd: str):
    """This function get lessons from university website and build the timetable as a json file

    Args:
        date (str): research date (format 'yyyy-mm-dd')
        aa (str): academic year (format 'yyyy/yyyy')
        cc (str): course code
        aci (str): course year
        codInd (str): course address code

    Returns:
        list: lessons list

    example: buildTimetable('2022-10-26','2022/2023','2035','1','796')"""

    print("executing buildTimetable with params:", date, aa, cc, aci, codInd)
    basePath = os.path.curdir + constants.FOLDER2035
    weekDays = constants.DAYS
    dateLessons = []
    dateObject = datetime.strptime(date, "%Y-%m-%d")
    weekday = dateObject.weekday()

    try:
        lessons = getLessons.getLessons(aa, cc, aci, codInd)

        if codInd == "796":
            path = os.path.join(
                basePath, "1/", "796/", weekDays[weekday] + constants.EXT
            )
        elif codInd == "797":
            path = os.path.join(
                basePath, "1/", "797/", weekDays[weekday] + constants.EXT
            )
        elif codInd is None:
            path = os.path.join(basePath, "2/", weekDays[weekday] + constants.EXT)

        print("Fetching lessons for " + cc + "-" + aci + "...")
        for lesson in lessons:
            if str(lesson["start"]).split(" ")[0] == date:
                dateLessons.append(lesson)

        # check file existence
        try:
            # if file doesn't exist, I create it
            print("Trying to create file " + path + "...")
            file = open(path, "x")
            print("File " + path + " doesn't exist -> Creating it...")
            file.close()
        except FileExistsError:
            # if file exists, I check if content is equal or not
            print("File " + path + " exists -> Continue")
            pass

        dateLessons = cleanTimetable.cleanTimetable(date, dateLessons, aci, codInd)

        # print(dateLessons)

        file = open(path, "r")
        if file.read() == j.dumps(dateLessons):
            print("Equal content, do nothing")
            file.close()
        else:
            print("Content is different. Overwriting Local Files...")
            file = open(path, "w")
            file.write(j.dumps(dateLessons))
            file.close()

        return dateLessons
    except ConnectionError:
        # if connection error, I load the default file
        if codInd == "796":
            path = os.path.join(
                basePath, "default/1/", "796/", weekDays[weekday] + constants.EXT
            )
        elif codInd == "797":
            path = os.path.join(
                basePath, "default/1/", "797/", weekDays[weekday] + constants.EXT
            )
        elif codInd is None:
            path = os.path.join(
                basePath, "default/2/", weekDays[weekday] + constants.EXT
            )

        print("A connection error occurred: using offline version of file @ " + path)
        file = open(path, "r")
        dateLessons = j.loads(file.read())

        # remove duplicates by lesson title (if needed)
        dateLessons = list({l["title"]: l for l in dateLessons}.values())

        file.close()
        return dateLessons
    except:
        # if generic error, I load the updated local file

        if codInd == "796":
            path = os.path.join(
                basePath, "1/", "796/", weekDays[weekday] + constants.EXT
            )
        elif codInd == "797":
            path = os.path.join(
                basePath, "1/", "797/", weekDays[weekday] + constants.EXT
            )
        elif codInd is None:
            path = os.path.join(basePath, "2/", weekDays[weekday] + constants.EXT)

        print("A generic error occurred: using local version of file @ " + path)
        file = open(path, "r")
        dateLessons = j.loads(file.read())

        # remove duplicates by lesson title (if needed)
        dateLessons = list({l["title"]: l for l in dateLessons}.values())

        file.close()
        return dateLessons
