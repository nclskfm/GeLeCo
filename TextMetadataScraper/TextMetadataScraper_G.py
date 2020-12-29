'''
A web scraper of texts and metadata from gesetze-im-internet.de

Input file is a newline-separated .txt file of URLs.
The output from this initial scraping is like the following, for each text:

<text type="Gerichtsentscheidung" level="Bund" title="Konkurrenzverhältnis bei Betrug: Einreichung mehrerer
Kreditanträge am selben Tag bei demselben Bankinstitut ohne Rückzahlungswillen" title_abbreviation="NA"
drafting_date="23.06.2016" decade="2010" database_URL="rechtsprechung-im-internet.de" court="BGH"
court_detail="BGH 4. Strafsenat" reference="4 StR 75/16" year="2016" decision_type="Beschluss"
ECLI="ECLI:DE:BGH:2016:230616B4STR75.16.0">
...
</text>

The output is one single .txt file of all texts, each with a <text> tag and metadata.
'''
from bs4 import BeautifulSoup
from urllib3.util import Retry
import urllib3
import re
from yaspin import yaspin
from yaspin.spinners import Spinners
from xml.sax.saxutils import escape, unescape


retries = Retry(connect=15, read=10, redirect=15)
http = urllib3.PoolManager(retries=retries)

'''setting filepaths of input and output files'''
path_input = r""
path_output = r""

with open(path_input, "r") as f:
    mylist = f.read().splitlines()

len_list = len(mylist)

corpus_as_list = []

with yaspin(Spinners.aesthetic) as sp:  # printing spinner and % progress
    for id, url in enumerate(mylist):
        html = http.request('GET', url).data
        soup = BeautifulSoup(html, features="lxml")

        # getting/setting metadata
        type = "Gesetz"
        level = "Bund"
        database_URL = "gesetze-im-internet.de"
        court = "NA"
        court_detail = "NA"
        reference = "NA"         # court, court_detail and reference (Aktenzeichen) are metadata of court decisions only
        decision_type = "NA"
        ECLI = "NA"

        # getting title
        title = soup.find(class_="jnlangue").get_text()
        if "\n" in title:
            title = "NA"
        else:
            title = title.replace('"', "'") #substituting double quotes with single quotes to avoid XML parsing errors
            title = escape(unescape(title))

        #getting drafting_date
        drafting_date_match = soup.find(string=re.compile(r"Ausfertigungsdatum"))
        drafting_date_reg = re.search(r"Ausfertigungsdatum: (.{10})", drafting_date_match)
        drafting_date = drafting_date_reg.group(1)

        #getting title abbreviation
        previous = drafting_date_match.previous_element
        title_abbreviation = previous.previous_element
        if title_abbreviation:
            title_abbreviation = title_abbreviation.replace('"', "'")
            title_abbreviation = escape(unescape(title_abbreviation))
        else:
            title_abbreviation = "NA"

        #getting year and decade by slicing 7t to 9th character of drafting date and adding 0
        if drafting_date == "NA":
            decade = "NA"
            year = "NA"
        else:
            decade = drafting_date[6:9] + "0"
            year = drafting_date[6:10]

        # building the <text> tag
        text_tag = '<text type="%s" level="%s" title="%s" title_abbreviation="%s" drafting_date="%s" decade="%s" database_URL="%s" court="%s" court_detail="%s" reference="%s" year="%s" decision_type="%s" ECLI="%s">' % (type, level, title, title_abbreviation, drafting_date, decade, database_URL, court, court_detail, reference, year, decision_type, ECLI)

        #adding the <text> tag before the text
        corpus_as_list.append(text_tag)

        #scraping and adding the text body
        body = soup.get_text('\n', strip=True)
        corpus_as_list.append(body)

        #adding the </text> closing tag
        corpus_as_list.append("</text>")

        sp.text = "   %i out of %i (%.2f%%)" % (id, len_list, (id/len_list*100))

corpus_as_string = "\n".join(corpus_as_list)

with open(path_output, "w+", encoding="utf-8") as file:
    file.write(corpus_as_string)

print("\rDone")
