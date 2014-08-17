import webinterface

import datetime

if __name__ == '__main__':
    wi = webinterface.Webinterface("s0814857", "test")
    
    catId = None
    for catId, series, pool in wi.listCategories():
        if series == "Sportkaart Ru Student  13/14" and pool == "zwemmen":
            print "Using %s (%s %s)" % (catId, series, pool)
            
            for date, startTime, endTime, availability, accesskey in wi.listEntries(catId):
                print date, startTime, endTime, availability
                if date == datetime.date(2014, 8, 18) and startTime == "09:30" and availability > 0:
                    wi.addEntry(accesskey)
            
            print "Confirming reservations, will get logged out"
            wi.confirm()
            break
    
    for pool, date, startTime, endTime, accesskey in wi.listReservations():
        print "Got %s %s %s-%s" % (pool, date, startTime, endTime)
    
    #print "Killing all reservations"
    #for pool, date, startTime, endTime, accesskey in wi.listReservations():
    #    wi.killReservation(accesskey)
