import browser
import re
import locale
import datetime

from bs4 import BeautifulSoup


RX_OCCUPATION = re.compile(r"([0-9]+)/([0-9]+)")
RX_TIME = re.compile(r"([0-9]{2}:[0-9]{2})-([0-9]{2}:[0-9]{2})")


class AuthenticationFailure(Exception):
    pass


class Webinterface:
    def login(self, username, password):
        # Prime session
        self.b.open_url("https://publiek.usc.ru.nl/publiek/login.php")
    
        # Submit login form
        self.b.open_url("https://publiek.usc.ru.nl/publiek/login.php",
                        [("username", username), ("password", password)])
        
        # Open main page; check if login was successful
        body, _headers = self.b.open_url("https://publiek.usc.ru.nl/publiek/")
        soup = BeautifulSoup(body)
        
        if soup.find("a", href="logout.php") is None:
            raise AuthenticationFailure
            
        print "Logged in successfully as '%s'" % soup.find("div", "footer").string.strip()
        pass

    def __init__(self, username, password):
        self.b = browser.Browser("Vrijbrief/0.1")
        self.login(username, password)
        pass
    
    def listCategories(self):
        result = []
    
        body, _headers = self.b.open_url("https://publiek.usc.ru.nl/publiek/laanbod.php")
        soup = BeautifulSoup(body)
        groups = soup.find("table", rules="groups", class_="clickable_option")
        for tr in groups.find_all("tr", class_="clickabletr"):
            inputradio = tr.find("input", class_="inputradio")
            fields = tr.find_all("td")
            
            assert inputradio["name"] == "PRESET[Laanbod][inschrijving_id_pool_id][]"
            
            value = inputradio["value"]

            series = fields[1].get_text().strip()
            pool = fields[2].get_text().strip()
            
            result.append((value, series, pool))
            
        return result
    
    def listEntries(self, catId):
        body, _headers = self.b.open_url("https://publiek.usc.ru.nl/publiek/laanbod.php", [("PRESET[Laanbod][inschrijving_id_pool_id][]", catId)])
        soup = BeautifulSoup(body)
        
        groups = soup.find("table", rules="groups", class_="clickabletr")
        for tr in groups.find_all("tr", class_="clickabletr"):
            fields = tr.find_all("td")
            
            date = fields[1].get_text().strip()
            time = fields[2].get_text().strip()
            accesskey = fields[3].a["href"]
            occupation = fields[4].get_text().strip()
            
            availability = 0
            if occupation != "VOL":
                occupation_matched = RX_OCCUPATION.match(occupation)
                assert occupation_matched
                availability = int(occupation_matched.groups()[1]) - int(occupation_matched.groups()[0])
            
            time_matched = RX_TIME.match(time)
            assert(time_matched)
            startTime, endTime = time_matched.groups()
            
            locale.setlocale(locale.LC_TIME, ("nl_NL", "utf8@euro"))
            date = datetime.datetime.strptime(date, "%a %d %b %Y").date()
            
            print date, startTime, endTime, availability, accesskey
        pass
