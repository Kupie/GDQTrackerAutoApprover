#CONFIGURE STUFF HERE

#Should we update donation totals? Set to True/False only
updateTotals = True

#Should we automatically approve donations to send to the host? True/False only
autoApprove = True

#Force through donations with "Flagged" transaction state?
approveFlaggedDonos = True

#Force through donations with "Pending" transaction state?
approvePendingDonos = False

#Tracker Login Info
trackerUser = "TRACKERUSERNAME"
trackerPassword = "TRACKERPASSWORD"

#How many seconds in between updates. Don't crank this number too low, bullying servers is rude
donoRefreshRate = 15

#How many seconds in between approving donations. Don't crank this number too low, bullying servers is rude
autoSendRate = 10

#Event ID in tracker (Go to "edit event" and look at the URL, number between 'event' and 'change'; MWSF2021 is "3" for example: https://tracker.2dcon.net/admin/tracker/event/3/change/
EventID = 7

#Set to True to log everything to console window instead of just showing current status
Logging = True




#------------END CONFIGURATION AREA--------------

#Check Python Version
import sys
if sys.version_info < (3, 0):
    sys.stdout.write("Sorry, requires Python 3.x, not Python 2.x\n")
    sys.exit(1)


#Makes a universal cls function to clear screen. Thanks popcnt: https://stackoverflow.com/a/684344
import os
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

#Set Window Title. I stuck this under a "try" command because this would fail on Linux systems due to no ctypes/window stuffs
#Although trying to run this on Linux would likely fail since we use a headless chrome browser window to approve donos...
try:
    import ctypes
    ctypes.windll.kernel32.SetConsoleTitleW("Donations Engine")
except:
    pass

#Oh boy parallel threads time to get into some fucky shit
import threading

#Import the rest
import subprocess
import time
from datetime import datetime

try:
    import psutil
except ImportError:
    print ('Python module psutil not installed, please run "pip install psutil" to install and then run this script again')
    sys.exit(1)
        

def main():
    browserKill()
    global killApp
    killApp = False

    if (updateTotals):
        totalsThread = threading.Thread(target=donoTotalsUpdateFunc)
        totalsThread.start()
        
    if (autoApprove):
        approverThread = threading.Thread(target=autoSendToReader)
        approverThread.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        killApp = True
        print('Exiting')




#My own "sleep" function that will sleep for how long we need, but also check if a kill signal has been sent every 1/2 second and exit if so
#Otherwise the python thread is locked with the "time.sleep" command until it's done, keyboard interrupts don't work
def sleepyKillCheck(timesleep):
    global killApp
    for x in range(timesleep * 2):
        if (not killApp):
            #print ('Sleeping 1/2 a second...')
            time.sleep(0.5)
        else:
            #print ('sleepyKillCheck Kill received, exiting Selenium thread...')
            browserKill()
            sys.exit(1)
    #Why not make my "sleepyKillCheck" function just check for killapp anyway? Can call it any time then
    if killApp:
        browserKill()
        sys.exit(1)

def checkBrowserKill():
    global killApp
    if killApp:
        #print('Kill Received, exiting Selenium thread....')
        browserKill()
        sys.exit(1)

def browserKill():
    #Find browsers running with webdriver and kill them
    #Not sure why the chromedriver sucks so badly at cleaning up its shit, I tried driver.close, driver.quit and driver.Dissomething and nothing cleaned it up
    try:
        for process in psutil.process_iter():
            if process.name() == 'chrome.exe' and '--test-type=webdriver' in process.cmdline():
                #print('Killing PID ' + str(process.pid))
                subprocess.run('taskkill /PID ' + str(process.pid) + ' /F', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass
        
#----BEGIN FUNCTION TO AUTOMAGICALLY SEND DONATIONS TO READER--------
def autoSendToReader():
    global killApp
    global driver
    #Selenium time awwyee remote controlling browsers like we're magic
    try:
        from selenium import webdriver
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.select import Select
    except ImportError:
        print ('Python module selenium not installed, please run "pip install selenium" to install and then run this script again')
        print ('Note that you will also need Google Chrome installed, along with the correct version of "chromedriver" executable in your path')
        sys.exit(1)
    
    
    #We use Chrome since it has a headless option
    options = webdriver.ChromeOptions()
    #Awwyiss no stupid browser window going
    options.add_argument('headless')
    #optional, may use less resources to have a small window?
    options.add_argument('window-size=800x600')
    #Shut up Chrome we don't need your stupid "devtools blahblah" message
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    #We finally start the web driver
    global driver
    driver = webdriver.Chrome(options=options)

    
    #Go to the select event page, and try to login
    driver.get("https://tracker.2dcon.net/admin/tracker/event/select_event")
    
    try:
        driver.find_element_by_id('id_username').send_keys(trackerUser)
        driver.find_element_by_id('id_password').send_keys(trackerPassword)
        driver.find_element_by_xpath("/html/body/div/div[2]/div/form/div[3]/input").click()
    #If it can't find it, we're already logged in!... somehow...
    except:
        pass
    
    
    
    #Select the event from the dropdown and submit. If it fails, login likely failed
    try:
        elem = Select(driver.find_element_by_id("id_event"))
    except:
        print ('Not able to load event page. Please check login information.')
        sys.exit(1)
    sleepyKillCheck(0)
    try:
        elem.select_by_value(str(EventID))
    except:
        print ('Not able to find and select event #' + str(EventID) + '. Please check event ID.')
        sys.exit(1)
        
    driver.find_element_by_xpath("/html/body/form/p/input").click()
    
    driver.get("https://tracker.2dcon.net/admin/tracker/donation/process_donations")
    sleepyKillCheck(0)
    
    while not killApp:
        #Tracker needs time to get donations
        driver.get("https://tracker.2dcon.net/admin/tracker/donation/process_donations")
        sleepyKillCheck(1)

        if (Logging == False):
            cls()
        autoSendDonoRate=autoSendRate
        try:
            elem = driver.find_elements_by_xpath('//button[normalize-space()="Send to Reader"]')
            if len(elem) > 1:
                autoSendDonoRate=0
                print('----Multiple donations found, enabling "gotta go fast" mode...')
                
    
            elem = driver.find_element_by_xpath('//button[normalize-space()="Send to Reader"]')
            elem.click()
            print(datetime.now().strftime("%I:%M:%S %p") +': Sent Donation to reader')
        except:
            print(datetime.now().strftime("%I:%M:%S %p") +': Could not find any donations to send to reader, probably none')
            pass

        sleepyKillCheck(0)
        #Click Refresh Button
        elem = driver.find_element_by_xpath('//button[normalize-space()="Refresh"]')
        elem.click()
        #here goes hacky shit while I'm drunk wooo
        #this should force donos through
        if (approveFlaggedDonos):
            try:
                driver.get("https://tracker.2dcon.net/admin/tracker/donation/?event__id__exact=" + str(EventID) + "&transactionstate__exact=FLAGGED")
                sleepyKillCheck(1)
                elem = Select(driver.find_element_by_id("id_form-0-transactionstate"))
                elem.select_by_value('COMPLETED')
                driver.find_element_by_xpath("/html/body/div/div[3]/div/div/form/p/input").click()
                sleepyKillCheck(1)
                print(datetime.now().strftime("%I:%M:%S %p") +": Forced a flagged dono through")
            except Exception as e:
                print(datetime.now().strftime("%I:%M:%S %p") +': Could not find any flagged donos to force through, continuing')
                pass
        if (approvePendingDonos):
            try:
                driver.get("https://tracker.2dcon.net/admin/tracker/donation/?event__id__exact=" + str(EventID) + "&transactionstate__exact=PENDING")
                sleepyKillCheck(1)
                elem = Select(driver.find_element_by_id("id_form-0-transactionstate"))
                
                elem.select_by_value('COMPLETED')
                driver.find_element_by_xpath("/html/body/div/div[3]/div/div/form/p/input").click()
                sleepyKillCheck(1)
                print(datetime.now().strftime("%I:%M:%S %p") +': Forced a pending dono through, waiting ' + str(autoSendDonoRate) + ' seconds to run again...')
            except Exception as e:
                print(datetime.now().strftime("%I:%M:%S %p") +': Could not find any pending donos to force through, waiting ' + str(autoSendDonoRate) + ' seconds to run again...')
                #print(str(e))
                pass

        sleepyKillCheck(autoSendRate - 4)
#-------End main loop for browser, next part only runs if keyboardinterrupt happened during a non-sleep command------
    #print('Kill Received, exiting Selenium thread....')
    browserKill()
    sys.exit(1)    






#---BEGIN DONATION TOTALS UPDATER FUNCTION------------------

def donoTotalsUpdateFunc():
    global killApp
    global donoRefreshRate
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
    
    try:
        import requests
    except ImportError:
        print ('Python module requests not installed, please run "pip install requests" to install and then run this script again')
        sys.exit(1)
        
    try:
        import urllib3
    except ImportError:
        print ('Python module urllib3 not installed, please run "pip install urllib3" to install and then run this script again')
        sys.exit(1)

    
    #disable SSL warnings. Tracker requires HTTPS but sometimes their certificate isn't "proper", this makes it connect
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    
    #initial donations total setting
    DonoTotal = '0'
    url = 'https://tracker.2dcon.net/tracker/event/' + str(EventID)
    sleepyKillCheck(0)
    cls()
    #They have set us up the loop
    while not killApp:
        try:
            #Make the request to tracker, plus the "goals" and "bidwars" page
            page = requests.get(url, verify=False)
        except:
            #If it fails, URL is invalid... or Tracker is down. That's always an option
            print ("Invalid URL connection to tracker failed. Open this python script and check that 2nd line! Exiting...")
            sys.exit(1)
        sleepyKillCheck(0)
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
            if len(DonoTotal) == 1:
                TotalValue = "     $" + DonoTotal
            elif len(DonoTotal) == 2:
                TotalValue = "    $" + DonoTotal
            elif len(DonoTotal) == 3:
                TotalValue = "   $" + DonoTotal
            elif len(DonoTotal) == 4:
                TotalValue = "  $" + DonoTotal
            elif len(DonoTotal) == 5:
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
            print(datetime.now().strftime("%I:%M:%S %p") +': ' + TotalRaisedText)
        
        
        except:
            print('Could not fetch donation total. Donation Server Down?...')
            continue
            
        #Wait "donoRefreshRate" amount of seconds before running again
        sleepyKillCheck(donoRefreshRate)
        
    sys.exit(1)    




if __name__ == '__main__':
    # execute only if run as a script
    main()
