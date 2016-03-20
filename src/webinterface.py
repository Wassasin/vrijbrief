import browser
import re
import datetime

from bs4 import BeautifulSoup, NavigableString


RX_OCCUPATION = re.compile(r"([0-9]+)/([0-9]+)")
RX_TIME = re.compile(r"([0-9]{2}:[0-9]{2})-([0-9]{2}:[0-9]{2})")
RX_FULLDATE = re.compile(r"[a-z]{2} ([0-9]{2}) ([a-z]{3}) ([0-9]{4})")

MONTHS = ["jan", "feb", "maa", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]

class AuthenticationFailure(Exception):
    pass


class Webinterface:
    def login(self, mode=None):
        # Prime session
        self.b.open_url("https://publiek.usc.ru.nl/publiek/login.php")
    
        # Submit mode
        body = self.b.open_url("https://publiek.usc.ru.nl/publiek/login.php", [("PRESET[Login][login_groep][]", self.mode)])
    
        # Submit login form
        self.b.open_url("https://publiek.usc.ru.nl/publiek/login.php",
                        [("username", self.username), ("password", self.password)])
        
        # Open main page; check if login was successful
        body, _headers = self.b.open_url("https://publiek.usc.ru.nl/publiek/")
        soup = BeautifulSoup(body)
        
        if soup.find("a", href="logout.php") is None:
            raise AuthenticationFailure
            
        print "Logged in successfully as '%s'" % soup.find("div", "pullrightfooterinfo").string.strip()
        pass

    def __init__(self, username, password, mode='S_RU'):
        self.username = username
        self.password = password
        self.mode = mode
        self.b = browser.Browser("Vrijbrief/0.1")
        
        self.login()
        pass

    def parseDate(self, date):
        matched = RX_FULLDATE.match(date)
        d, mstr, y = matched.groups()
        m = MONTHS.index(mstr)+1

        return datetime.date(int(y), int(m), int(d))

    def listCategories(self):
        body, _headers = self.b.open_url("https://publiek.usc.ru.nl/publiek/laanbod.php")
        soup = BeautifulSoup(body, "html5lib")
        groups = soup.find("form", id="target")
        current_series = None
        for tr in groups.children:
            if type(tr) is NavigableString:
                continue
            elif tr.has_attr('class') and "list-group-item-heading" in tr["class"]:
                current_series = tr.find("b").get_text().strip()
            elif tr.name == "label": 
                assert current_series is not None
                inputradio = tr.find("input")
                assert inputradio["name"] == "PRESET[Laanbod][inschrijving_id_pool_id][]"
                
                value = inputradio["value"]
                pool = tr.find('i').get_text().strip()
                
                yield value, current_series, pool
    
    def listEntries(self, catId):
        body, _headers = self.b.open_url("https://publiek.usc.ru.nl/publiek/laanbod.php", [("PRESET[Laanbod][inschrijving_id_pool_id][]", catId)])
        soup = BeautifulSoup(body)
        
        groups = soup.find("table", class_="responstable clickabletr")
        for tr in groups.find_all("tr"):
            if not tr.has_attr("class") or "clickabletr" not in tr["class"]:
                continue

            fields = tr.find_all("td")
            
            date = fields[0].get_text().strip()
            time = fields[1].get_text().strip()
            accesskey = fields[2].a["href"]
            occupation = fields[3].get_text().strip()
            
            availability = 0
            if occupation != "VOL":
                occupation_matched = RX_OCCUPATION.match(occupation)
                assert occupation_matched
                availability = int(occupation_matched.groups()[1]) - int(occupation_matched.groups()[0])
            
            time_matched = RX_TIME.match(time)
            assert(time_matched)
            startTime, endTime = time_matched.groups()
            
            date = self.parseDate(date)
            
            yield date, startTime, endTime, availability, accesskey
        pass
    
    def addEntry(self, accesskey):
        # View entry page
        body, _headers = self.b.open_url("https://publiek.usc.ru.nl/publiek/" + accesskey)
        soup = BeautifulSoup(body)
        
        a = soup.find("a", class_="btn btn-responsive btn-success pull-right")
        assert(a.get_text().strip() == "Toevoegen aan Keuzelijst")
        
        # Press on add-button
        confirmkey = a["href"]
        body, _headers = self.b.open_url("https://publiek.usc.ru.nl/publiek/" + confirmkey)
        pass
    
    def confirm(self):
        body, _headers = self.b.open_url("https://publiek.usc.ru.nl/publiek/bevestigen.php",
                                         [("actie", "bevestig"), ("tabel", "klant"), ("kolom", "klant_id"), ("waarde", self.username)])
                        
        # Confirming logs you out; thus we need to log back in
        self.login()
        pass

    def listReservations(self):
        body, _headers = self.b.open_url("https://publiek.usc.ru.nl/publiek/overzicht.php")
        soup = BeautifulSoup(body)
        
        reservations_label = soup.find(text="Reserveringen Locaties")
        if reservations_label is None:
            return
            
        thr = list(reservations_label.parents)[3]
        assert thr.name == "tr"
        
        for tr in thr.find_next_siblings("tr"):
            fields = tr.find_all("td")
            
            accesskey = fields[0].a["href"]
            pool = fields[1].get_text().strip()
            date = fields[2].get_text().strip()
            time = fields[3].get_text().strip()
            
            time_matched = RX_TIME.match(time)
            assert(time_matched)
            startTime, endTime = time_matched.groups()
            
            date = self.parseDate(date)
            
            yield pool, date, startTime, endTime, accesskey
        pass
    
    def killReservation(self, accesskey):
        body, _headers = self.b.open_url("https://publiek.usc.ru.nl/publiek/" + accesskey)
        soup = BeautifulSoup(body)
        
        linschrijving_id = soup.find("input", attrs={"name": "linschrijving_id"})["value"]
        
        self.b.open_url("https://publiek.usc.ru.nl/publiek/" + accesskey,
                        [("linschrijving_id", linschrijving_id), ("actie", "bevestig"), ("tabel", "klant"), ("kolom", "klant_id"), ("waarde", self.username)])
        
        print "Killed %s" % linschrijving_id
        
        pass
