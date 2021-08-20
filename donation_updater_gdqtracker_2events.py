#EventIDs to grab then add

EventID1 = 3
EventID2 = 5


#How many seconds in between updates. Don't crank this number too low, bullying servers is rude
donoRefreshRate = 15

#Set to True to log everything to console window instead of just showing current status
Logging = False


#------------END CONFIGURATION AREA--------------


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
import ctypes
import urllib3

#sets nice title
ctypes.windll.kernel32.SetConsoleTitleW("Donations Updater")

#disable SSL warnings. SRC requires HTTPS but sometimes their certificate isn't "proper", this makes it connect
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Makes a universal cls function to clear screen. Thanks popcnt: https://stackoverflow.com/a/684344
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

#initial donations total setting
DonoTotal1 = '0'
DonoTotal2 = '0'
DonoTotalCombined = '0'

url1 = 'https://tracker.2dcon.net/tracker/event/' + str(EventID1)
url2 = 'https://tracker.2dcon.net/tracker/event/' + str(EventID2)

cls()

#They have set us up the loop

while True:
    if (not Logging):
        cls()

    try:
        #Make the request to tracker, plus the "goals" and "bidwars" page
        page1 = requests.get(url1, verify=False)
        page2 = requests.get(url2, verify=False)
    except Exception as e:
        #If it fails, URL is invalid... or SRC is down. That's always an option
        print ("Invalid URL connection to tracker failed. Open this python script and check that 2nd line! Exiting...")
        sys.exit(1)
        
    soup1 = BeautifulSoup(page1.content,'html.parser')
    soup2 = BeautifulSoup(page2.content,'html.parser')

    span1 = soup1.find('h2', class_='text-center')
    span2 = soup2.find('h2', class_='text-center')
    try:
        spantext1s1 = span1.text.split('(')
        spantext2s1 = span2.text.split('(')

        spantext1s2 = spantext1s1[-2].split('$')[-1]
        spantext2s2 = spantext2s1[-2].split('$')[-1]
        spanint1s3 = int(spantext1s2.split(".")[0])
        spanint2s3 = int(spantext2s2.split(".")[0])
    
    
        if (spanint1s3 > int(DonoTotal1)):
            DonoTotal1 = spanint1s3
            DonoTotal1 = str(int(DonoTotal1) )
            
        if (spanint2s3 > int(DonoTotal2)):
            DonoTotal2 = spanint2s3
            DonoTotal2 = str(int(DonoTotal2) )
        print (url1 + ' -- $' + DonoTotal1)
        print (url2 + ' -- $' + DonoTotal2)

        #We got two strings... time to add them together as numbers
        DonoTotalCombined = int(DonoTotal1) + int(DonoTotal2)
        
        #We still need the donation total as a string aaaaaaaaa
        DonoTotalCombined = str(DonoTotalCombined)
        #Manually adjust donations total from Donations_Adjust value
        
#        Used for testing different number values
#        DonoTotalCombined = '2000'
        if len(DonoTotalCombined) == 1:
            TotalValue = "     $" + DonoTotalCombined
        elif len(DonoTotalCombined) == 2:
            TotalValue = "    $" + DonoTotalCombined
        elif len(DonoTotalCombined) == 3:
            TotalValue = "   $" + DonoTotalCombined
        elif len(DonoTotalCombined) == 4:
            TotalValue = "  $" + DonoTotalCombined
        else:
            TotalValue = " $" + DonoTotalCombined
        TotalRaisedText = "Total Raised: $" + DonoTotalCombined
        text_file = open("TotalsCombined.txt", "w")
        
        text_file.write(TotalValue)
        text_file.close()
        text_file = open("TotalRaisedCombined.txt", "w")
        text_file.write(TotalRaisedText)
        text_file.close()
        
        #Doesn't even flash since it's all one "print" command ran immediately
        print(TotalRaisedText + '\n-Last Run at ' + datetime.now().strftime("%I:%M:%S %p") + ', Waiting ' + str(donoRefreshRate) + ' seconds to run again...')
    
    
    except Exception as e:
        print('Could not fetch donation total. Donation Server Down?...')
        
    print ('--------------------------------------------------')
    #Wait "donoRefreshRate" amount of seconds before running again
    time.sleep(donoRefreshRate)
    
