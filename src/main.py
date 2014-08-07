import webinterface


if __name__ == '__main__':
    wi = webinterface.Webinterface("s0814857", "test")
    
    catId = None
    for catId, series, pool in wi.listCategories():
        if series == "Sportkaart Ru Student  13/14" and pool == "squash student":
            print "Using %s (%s %s)" % (catId, series, pool)
            
            wi.listEntries(catId)
            break
    
    
