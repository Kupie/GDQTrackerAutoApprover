#Change this URL to the URL of the donation page:

EventID = 16

#Should we buffer the number with spaces, so a left-justified text is "centered" anyway in OBS? 
#True/False only. Should be False if you are centering the text in OBS
CenterText = False

#How many seconds in between updates. Don't crank this number too low, bullying servers is rude
donoRefreshRate = 15

#Check python version
import sys
if sys.version_info < (3, 0):
    print ('Sorry, requires Python 3.x, not Python 2.x')
    sys.exit(1)

#Make sure BeautifulSoup is installed
try:
    from bs4 import BeautifulSoup
except ImportError:
    print ('Python module BeautifulSoup not installed, please run "pip install bs4" to install and then run this script again')
    sys.exit(1)

#Make sure lxml is installed
try:
    import lxml
except ImportError:
    print ('Python module lxml not installed, please run "pip install lxml" to install and then run this script again')
    sys.exit(1)

from datetime import datetime
import os
import requests
import time
try:
    import ctypes
except:
    pass

import urllib3

#sets nice title
try:
    ctypes.windll.kernel32.SetConsoleTitleW("Donations Updater")
except:
    pass
#disable SSL warnings. SRC requires HTTPS but sometimes their certificate isn't "proper", this makes it connect
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Makes a universal cls function to clear screen. Thanks popcnt: https://stackoverflow.com/a/684344
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

#initial donations total setting
DonoTotal = '0'
url = 'https://tracker.2dcon.net/tracker/event/' + str(EventID)

cls()
#They have set us up the loop
while True:
    try:
        #Make the request to tracker, plus the "goals" and "bidwars" page
        page = requests.get(url, verify=False)
    except:
        #If it fails, URL is invalid... or tracker is down. That's always an option
        print ("Invalid URL connection to tracker failed. Open this python script and check that 2nd line! Exiting in 10 seconds...")
        time.sleep(10)
        sys.exit(1)
        
    soup = BeautifulSoup(page.content,'html.parser')

    span = soup.find('h2', class_='text-center')
    try:
        spantext1 = span.text.split('(')
	
        spantext2 = spantext1[-2].split('$')[-1]
        spantext3 = spantext2.replace(',', '')
        spanint = int(spantext3.split(".")[0])


    
        if (spanint > int(DonoTotal)):
            DonoTotal = spanint
            DonoTotal = str(int(DonoTotal) )
    
        
        #Manually adjust donations total from Donations_Adjust value
        
#        Used for testing different number values
#        DonoTotal = '2000'
        if CenterText:
            if len(DonoTotal) == 1:
                TotalValue = "     $" + DonoTotal
            elif len(DonoTotal) == 2:
                TotalValue = "    $" + DonoTotal
            elif len(DonoTotal) == 3:
                TotalValue = "   $" + DonoTotal
            elif len(DonoTotal) == 4:
                TotalValue = "  $" + DonoTotal
            else:
                TotalValue = " $" + DonoTotal
        else:
            TotalValue = "$" + DonoTotal
                
        TotalRaisedText = "Total Raised: $" + DonoTotal
        text_file = open("Totals.txt", "w")
        
        text_file.write(TotalValue)
        text_file.close()
        text_file = open("TotalRaised.txt", "w")
        text_file.write(TotalRaisedText)
        text_file.close()
        
        #Doesn't even flash since it's all one "print" command ran immediately
        print(TotalRaisedText + '\n-Last Run at ' + datetime.now().strftime("%I:%M:%S %p") + ', Waiting ' + str(donoRefreshRate) + ' seconds to run again...')
    
    
    except:
        print('Could not fetch donation total. Donation Server Down?...')
        
    print ('--------------------------------------------------')
    #Wait "donoRefreshRate" amount of seconds before running again
    time.sleep(donoRefreshRate)
    
