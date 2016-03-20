import webinterface
import time
import os
import datetime

if __name__ == '__main__':
    wi = webinterface.Webinterface("s0814857", "PASSPHRASE", "S_RU")
    
    catId = None
    for catId, series, pool in wi.listCategories():
        if series == "Sportkaart Ru Student  15/16" and pool == "zwemmen":
            print "Using %s (%s %s)" % (catId, series, pool)
            
            foundEntry = False
            while not foundEntry:
                entries = list(wi.listEntries(catId)) # Force fetching entries before continuing
                print(chr(27) + "[2J") # Clear terminal
                print "Fetched for %s" % time.strftime("%c")
                for date, startTime, endTime, availability, accesskey in entries:
                    print date, startTime, endTime, availability
                    if date == datetime.date(2016, 03, 07) and startTime == "08:30" and availability > 0:
                        wi.addEntry(accesskey)
                        foundEntry = True
                
                if foundEntry:
                    print "Confirming reservations, will get logged out"
                    wi.confirm()
                else:
                    time.sleep(120)
            break
    
    for pool, date, startTime, endTime, accesskey in wi.listReservations():
        print "Got %s %s %s-%s" % (pool, date, startTime, endTime)
    
    #print "Killing all reservations"
    #for pool, date, startTime, endTime, accesskey in wi.listReservations():
    #    wi.killReservation(accesskey)
