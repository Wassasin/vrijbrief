import webinterface
import sqlite3
from threading import Timer

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def create_db():
    return sqlite3.connect('tracker.db')

def create_interface():
    return webinterface.Webinterface("s0814857", "xxx")

def get_cat_id(wi):
    for catId, series, pool in wi.listCategories():
        if series == "Sportkaart Ru Student  14/15" and pool == "zwemmen":
            return catId

    return None

def scrape_entries(c):
    global wi, cat_id
    for date, startTime, endTime, availability, accesskey in wi.listEntries(cat_id):
        c.execute('insert into entry values (?, ?, ?, datetime(\'now\'))', (date, startTime, availability))
    print "Scraped"

def measure():
    with create_db() as conn:
        c = conn.cursor()
        for _i in range(3):
            try:
                scrape_entries(c)
                break
            except Exception, e:
                print e
                wi = create_interface()

if __name__ == '__main__':
    global wi, cat_id

    with create_db() as conn:
        c = conn.cursor()
        c.execute('create table if not exists entry (date DATE, start_time TIME, availability INT, moment DATETIME)')
    
    wi = create_interface()
    cat_id = get_cat_id(wi)
    print "Using %s" % cat_id

    rt = RepeatedTimer(20, measure)
    try:
        raw_input("Press Enter to stop...")
    finally:
        rt.stop()
