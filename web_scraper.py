import time
from datetime import datetime, timedelta
import os
import json
import csv
import selenium
import dropbox
from bs4 import BeautifulSoup
from selenium import webdriver


class Tournament():
    """ Required Fields: name (string), grade (string), date (string),
        finalists (string array), semifinalists (string array), upsets (string array)
    """
    def __init__(self, name, url, grade, date, finalists, semi_finalists, quarter_finalists, upsets):
        self.name = name
        self.url = url
        self.grade = grade
        self.date = date
        self.finalists = finalists
        self.semi_finalists = semi_finalists
        self.quarter_finalists = quarter_finalists
        self.upsets = upsets

    def __str__(self):
        return str(("Tournament: " + self.name + "\n\tURL: " + self.url + "\n\tGrade: " + self.grade \
                    + "\n\tDate: " + self.date + "\n\tFinalists: " + str(self.finalists) \
                    + "\n\tSemifinalists: " + str(self.semi_finalists) + "\n\tQuarterfinalists: " + str(self.quarter_finalists) \
                    + "\n\tUpsets: " + str(self.upsets)).encode('utf-8'))


def create_tournament(html, url):
    """ Creates a tournament object given data on tournament homepage
        Parameters: tournament page html and url
        Return: Tournament Object
        1) Parse initial HTML to find tournament name, date, and grade
        2) Find and click on results element
        3) Find and execute AJAX call to load results for Boys Main Draw Singles
        4) Create and return Tournament Object
    """
    tournament_soup = BeautifulSoup(html, 'html.parser')
    name = tournament_soup.find("h1", {"id": "ltH1Header"}).text.strip()
    date = ""
    grade = ""
    finalists = []
    semi_finalists = []
    quarter_finalists = []
    upsets = []
    tournament_details = tournament_soup.find("div", {"class": "pn-in tnews clfx"})
    for li_tag in tournament_details.find_all("li", {"class": "hlf fl"}):
        if "Date:" in str(li_tag):
            date = li_tag.find("strong").text.strip()
        elif "Grade" in str(li_tag):
            grade = li_tag.find("strong").text.strip()
    try:
        driver.find_element_by_id("tabResults_tab").click()
        results_soup = BeautifulSoup(driver.page_source, 'html.parser')
        for h4_tag in results_soup.find_all("h4"):  #get the ajax call to display boys singles main draw results
            if "BOYS" in h4_tag.text:
                for li_tag in h4_tag.find_next_sibling().find_all("li"):
                    if "Singles" in li_tag.text:
                        for a_tag in li_tag.find_all("a"):
                            if "Main Draw" in a_tag.text:
                                singles_ajax_script = a_tag['onclick']
        driver.execute_script(singles_ajax_script)
        time.sleep(1.5)  # delay until ajax call completes, and prevent server lockout
        results_soup = BeautifulSoup(driver.page_source, 'html.parser')
        results = results_soup.find("div", {"id": "divTourResults"})
        print grade
        for h2_tag in results.find_all("h2",{"style":"padding:10px 0 10px 0;"}):
            if grade == "Grade 5" or grade == "Grade 4" or grade == "Grade 3":  # looking for finalists
                if h2_tag.text == "Final":
                    for a_tag in h2_tag.find_next_sibling().find_all("a", {"style":"background-color:transparent;"}):
                        if a_tag['id'] == "lnkPlayerW1":
                            finalists.append(a_tag.text + " (winner)")
                        elif a_tag['id'] == "lnkPlayerL1" and (grade == "Grade 4" or grade == "Grade 3"): # only show second place for G4 and G3
                            finalists.append(a_tag.text + " (second)")
            if h2_tag.text == "Semifinal":  # add semifinalists for G4 and G3
                for a_tag in h2_tag.find_next_sibling().find_all("a", {"style":"background-color:transparent;"}):
                    if a_tag['id'] == "lnkPlayerL1" and (grade == "Grade 3" or grade == "Grade 2"):
                        semi_finalists.append(a_tag.text)
            elif h2_tag.text == "Quarterfinal":  # add quarterfinalists for G2
                for a_tag in h2_tag.find_next_sibling().find_all("a", {"style":"background-color:transparent;"}):
                    if a_tag['id'] == "lnkPlayerL1" and grade == "Grade 2":
                        quarter_finalists.append(a_tag.text)
            elif (h2_tag.text == "1st Round" or h2_tag.text == "2nd Round") and grade == "Grade 1":  # find upsets in G1 first round (seed wins)
                for a_tag in h2_tag.find_next_sibling().find_all("a", {"style":"background-color:transparent;"}):
                    if a_tag['id'] == "lnkPlayerW1" and grade == "Grade 1":
                        winner = a_tag.text
                        loser = str(a_tag.parent.text.encode("utf-8")).splitlines()[3]
                        if "[" in str(loser):  # because a seed is of form First Last [3]
                            upsets.append((winner + " beat " + loser).encode("utf-8"))
        current_tournament = Tournament(name, url, grade, date, finalists, semi_finalists, quarter_finalists, upsets)
        return current_tournament
    except selenium.common.exceptions.NoSuchElementException:  # catch cancelled tournaments
        return Tournament(name, url, grade, date, finalists, semi_finalists, quarter_finalists, upsets)


def write_and_upload_csv(tournaments):
    """ Parameters: array of Tournament objects
        Returns: void
        1) Get dropbox access token from json file and create Dropbox API v3 connection
        2) Create csv, write data, upload to Dropbox, and delete local csv file
    """
    with open("dropbox_access_token.json") as token_file:
        json_data = json.load(token_file)
        dropbox_access_token = json_data["accessToken"]
    dbx = dropbox.Dropbox(dropbox_access_token)
    csv_name = "DATE" + str(datetime.now())[:-7].replace(' ', 'TIME').replace(':', '-') + ".csv"
    with open(csv_name, 'wb') as results_csv:
        writer = csv.writer(results_csv)
        writer.writerow(["Tournament", "Date", "Grade", "Finalists", "Semifinalists", "Quarterfinalists", "Upsets", "Link"])
        for current_tournament in tournaments:
            writer.writerow([str(current_tournament.name.encode('utf-8')), str(current_tournament.date.encode('utf-8')), str(current_tournament.grade).encode('utf-8').replace("Grade ", " "), \
                             str(', '.join(current_tournament.finalists)), str(', '.join(current_tournament.semi_finalists)), str(', '.join(current_tournament.quarter_finalists)), \
                             str(', '.join(current_tournament.upsets)), str(current_tournament.url.encode('utf-8'))])
    with open(csv_name, 'rb') as results_csv:
        dbx.files_upload(results_csv.read(), '/' + csv_name)
    os.remove(csv_name)

#Main Script
BASE_URL = "http://www.itftennis.com"
base_tournament_url = BASE_URL + "/juniors/tournaments/calendar.aspx"
today = datetime.today()
two_weeks_ago = datetime.now() - timedelta(days=14)
try:
    month = input("Enter the tournament start month to search by (or press return to use two weeks ago): ")
    day = input("Enter the tournament start day to search by: ")
    year = input("Enter the tournament start year to search by: ")
    from_date = str(day).zfill(2) + "-" + str(month).zfill(2) + "-" + str(year)
except SyntaxError:
    from_date = str(two_weeks_ago.day) + "-" + str(two_weeks_ago.month) + "-" + str(two_weeks_ago.year)
    print("No valid start date provided. Using " + from_date + " instead")
try:
    month = input("Enter the tournament end month to search by (or press enter to use today): ")
    day = input("Enter the tournament end day to search by: ")
    year = input("Enter the tournament end year to search by: ")
    to_date = str(day).zfill(2) + "-" + str(month).zfill(2) + "-" + str(year)
except SyntaxError:
    to_date = str(today.day) + "-" + str(today.month) + "-" + str(today.year)
    print("No valid end date provided, using " + str(to_date) + " instead")
tournament_search_url = base_tournament_url + "?fromDate=" + str(from_date) + "&toDate=" + str(to_date)
print "tournament search url is " + tournament_search_url
driver = webdriver.PhantomJS()
driver.set_page_load_timeout(60)
driver.set_script_timeout(60)
driver.get(tournament_search_url)
soup = BeautifulSoup(driver.page_source, 'html.parser')
tournament_spans = soup.find_all("span", {"class":"liveScoreTd"})
tournament_links = []
for a in soup.find_all('a', href=True):
    if "tournamentid" in a["href"]:
        tournament_links.append(a["href"])
count = 0
tournaments = []
for tournament_link in tournament_links:
    if count < 200:  # set tournament search cap to 200 to avoid maxing out server requests
        driver.get(BASE_URL + tournament_link)
        print "processing " + BASE_URL + tournament_link
        tournament = create_tournament(driver.page_source, BASE_URL + tournament_link)
        tournaments.append(tournament)
        print str(tournament)
    count += 1
write_and_upload_csv(tournaments)
print "Script executed successfully"