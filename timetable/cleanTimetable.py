from datetime import datetime
import constants


def cleanTimetable(date: str, dateLessons: list, aci: str, codInd: str):
    """This function is needed to recover from some errors coming from UniPa website,
    like duplicates or wrong classes

    Args:
        date (str): research date
        dateLessons (list): lessons to be cleaned
        aci (str): course year
        codInd (str): course address code

    Returns:
        list: lessons
    """
    # remove duplicates by lesson title
    dateLessons = list({l["title"]: l for l in dateLessons}.values())

    fullDate = str(date).split("-")
    day = int(fullDate[2])
    month = int(fullDate[1])
    year = int(fullDate[0])
    objectDate = datetime(year, month, day)

    result = []
    subjects = []

    if aci == "1":
        if codInd == "796":
            if objectDate >= datetime(year, 8, 15) and objectDate <= datetime(
                year, 12, 25
            ):
                subjects = constants.LM2035_1_796_FirstPer_allowed
            else:
                subjects = constants.LM2035_1_796_SecondPer_allowed
        elif codInd == "797":
            if objectDate >= datetime(year, 8, 15) and objectDate <= datetime(
                year, 12, 25
            ):
                subjects = constants.LM2035_1_797_FirstPer_allowed
            else:
                subjects = constants.LM2035_1_797_SecondPer_allowed
    else:
        if codInd == "796":
            if objectDate >= datetime(year, 8, 15) and objectDate <= datetime(
                year, 12, 25
            ):
                subjects = constants.LM2035_2_796_FirstPer_allowed
            else:
                subjects = constants.LM2035_2_796_SecondPer_allowed
        elif codInd == "797":
            if objectDate >= datetime(year, 8, 15) and objectDate <= datetime(
                year, 12, 25
            ):
                subjects = constants.LM2035_2_797_FirstPer_allowed
            else:
                subjects = constants.LM2035_2_797_SecondPer_allowed
        else:
            if objectDate >= datetime(year, 8, 15) and objectDate <= datetime(
                year, 12, 25
            ):
                subjects = constants.LM2035_2_Generic_FirstPer_allowed
            else:
                subjects = constants.LM2035_2_Generic_SecondPer_allowed

    for lesson in dateLessons:
        for subject in subjects:
            # keep only the lessons that belong to our list of subjects
            if str(lesson["title"]).startswith(subject):
                result.append(lesson)

    return result
