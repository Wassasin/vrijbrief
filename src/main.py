import webinterface

import datetime

if __name__ == '__main__':
    wi = webinterface.Webinterface("s0814857", "test")
    
    catId = None
    for catId, series, pool in wi.listCategories():
        if series == "Sportkaart Ru Student  13/14" and pool == "squash student":
            print "Using %s (%s %s)" % (catId, series, pool)
            
            for date, startTime, endTime, availability, accesskey in wi.listEntries(catId):
                if date == datetime.date(2014, 8, 9) and startTime == "20:00":
                    wi.addEntry(accesskey)
            
            print "Confirming reservations, will get logged out"
            wi.confirm()
            break
    
    for pool, date, startTime, endTime, accesskey in wi.listReservations():
        print "Got %s %s %s-%s" % (pool, date, startTime, endTime)
    
    print "Killing all reservations"
    for pool, date, startTime, endTime, accesskey in wi.listReservations():
        wi.killReservation(accesskey)
