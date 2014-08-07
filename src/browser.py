import pycurl
import cStringIO as StringIO
from urllib import urlencode


class BrowserError(Exception):
    def __init__(self, inner_exception):
        self.inner_exception = inner_exception
    def __str__(self):
        return "<Browser `%s'>" % self.inner_exception


class Browser:
    def __init__(self, userAgent):
        self.userAgent = userAgent
        self.cookies = dict()
        self.sslVersion = pycurl.SSLVERSION_SSLv3  # SSLv23 / SSLv3
    
    ''' Parse string with headers to a list of key-value-pairs. '''
    def parseHeaders(self, headerStr):
        headers = []
        
        for line in headerStr.split('\r\n'):
            elements = line.split(": ")
            
            if len(elements) != 2 or elements[0] == "":
                continue
            
            headers.append((elements[0], elements[1]))
        return headers
    
    ''' Parses headers and sets cookies if applicable; return headers. '''
    def processHeaders(self, headerStr):
        headers = self.parseHeaders(headerStr)

        for key, value in headers:
            if key == "Set-Cookie":
                cookie = value.split(";")[0]
                cookieKey, cookieValue = cookie.split("=")
                self.cookies[cookieKey] = cookieValue
        
        return headers
    
    ''' Open a url with the current browser setup;
        setting postVars will make it a POST request. '''
    def open_url(self, url, postVars=None):
        try:
            headers = []
            headers.append("User-Agent: %s" % self.userAgent)
            
            for key, value in self.cookies.items():
                headers.append("Cookie: %s=%s" % (key, value))
        
            c = pycurl.Curl()
            c.setopt(pycurl.FAILONERROR, True)
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.HTTPHEADER, headers)
            
            bodyBuffer = StringIO.StringIO()
            headerBuffer = StringIO.StringIO()
            
            c.setopt(pycurl.WRITEFUNCTION, bodyBuffer.write)
            c.setopt(pycurl.HEADERFUNCTION, headerBuffer.write)
            
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(pycurl.MAXREDIRS, 5)
            c.setopt(pycurl.SSLVERSION, self.sslVersion)
            c.setopt(pycurl.SSL_VERIFYPEER, 1)
            # Verify that domain in URL matches to the Common Name Field or
            # a Subject Alternate Name field in the certificate.
            # (0 will not check it; 1 is an invalid value)
            c.setopt(pycurl.SSL_VERIFYHOST, 2)
            
            if postVars is not None:
                c.setopt(pycurl.POSTFIELDS, urlencode(postVars))
            
            c.perform()
            
            return bodyBuffer.getvalue(), self.processHeaders(headerBuffer.getvalue())
        except pycurl.error, e:
            raise BrowserError(e)
