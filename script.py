import re
import requests
from bs4 import BeautifulSoup
import mysql.connector

__author__ = "rafal stempowski"
__date__ = "$2017-04-04 20:10:03$"


def insert_to_db(name, diff, num, plat, time, hours,platform):
    try:
        cnx = mysql.connector.connect(user='root', database='trophies')
        cursor = cnx.cursor()
        add_trophies = ("INSERT INTO trophies "
                        "(Name, Difficulty, NumberOfTrophies, Platinum, Time, Hours,Platform) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s)")
        data_trophies = (str(name), int(diff), int(num), bool(plat), str(time), int(hours),str(platform))
        cursor.execute(add_trophies, data_trophies)
        cnx.commit()
        cursor.close()
        cnx.close()
    except:
        return


def forum_url_decode(url, name,platform):
    diff = 0
    hours = 100
    plat = False
    troCount = 0
    time = ""

    try:
        site_text = requests.get(url).text
        soup = BeautifulSoup(site_text, "html.parser")
        for li in soup.find_all("li"):
            b = li.find("b")
            if b is not None:
                if "difficulty" in str(b) and "affect" not in str(b) and diff == 0:
                    if re.search(r'(\d+)/10', b.next.next) is not None:
                        diff = re.search(r'(\d+)/10', b.next.next).group(1)
                if "time" in str(b) and time == "":
                    time = b.next.next
                    timeFrom = ""
                    timeTo = ""
                    if "Min" in time or "min" in time:
                        timeFrom = "1"
                        timeTo = "1"
                    else:
                        if re.search(r'(\d+)[^0-9]+(\d*)', b.next.next) != None:
                            timeFrom = re.search(r'(\d+)[^0-9]+(\d*)', b.next.next).group(1)
                            timeTo = re.search(r'(\d+)[^0-9]+(\d*)', b.next.next).group(2)
                    if timeFrom == "" or timeTo == "":
                        if timeTo == "" and timeFrom != "":
                            hours = int(timeFrom)
                    else:
                        hours = (int(timeTo) + int(timeFrom)) / 2
                if "Bronze" in str(li):
                    if "Platinum" in str(li):
                        plat = True
                    if re.search(r'(\d+).+', b.next.next) is not None:
                        troCount = troCount + int(re.search(r'(\d+).+', b.next.next).group(1))
        if diff != 0:
            print(str(name) + " - " + str(diff) + "/10  -   estimate: " + str(hours) + " hours  plat - " + str(plat) + '  trophies - ' + str(troCount))
            insert_to_db(name, diff, troCount, plat, time, hours, platform)
    except:
        return


def run2(max):
    url = "http://www.playstationtrophies.org/guides/retail/"
    site_text = requests.get(url).text
    site_object = BeautifulSoup(site_text, "html.parser")
    count = 0
    for a in site_object.findAll("a", {"class": "linkT"}):
        count += 1
        if max != -1 and count >= max:
            return
        if a.find("strong") is not None:
            if 'href' in a.attrs:
                forum_url = a.attrs['href']
                forum_url_decode("http://www.playstationtrophies.org" + forum_url, a.find("strong").contents[0], "PS3")



def run(max):
    url = "http://www.playstationtrophies.org/guides/ps4/"
    site_text = requests.get(url).text
    site_object = BeautifulSoup(site_text, "html.parser")
    count = 0
    for a in site_object.findAll("a", {"class": "linkT"}):
        count += 1
        if max != -1 and count >= max:
            return
        if a.find("strong") is not None:
            if 'href' in a.attrs:
                forum_url = a.attrs['href']
                forum_url_decode("http://www.playstationtrophies.org" + forum_url, a.find("strong").contents[0], "PS4")


if __name__ == "__main__":
    run(-1)
