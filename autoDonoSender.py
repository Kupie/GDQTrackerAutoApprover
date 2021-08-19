#CONFIGURE STUFF HERE

#Tracker Login Info
trackerUser = "GDQTRACKERUSER"
trackerPassword = "GDQTRACKERPASSWORD"

#How many seconds in between approving donations. Don't crank this number too low, bullying servers is rude
autoSendRate = 10

#Event ID in tracker (Go to "edit event" and look at the URL, number between 'event' and 'change'; MWSF2021 is "3" for example: https://tracker.2dcon.net/admin/tracker/event/3/change/
EventID = 3

#Set to True to log everything to console window instead of just showing current status
Logging = False



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

#Set Window Title
import ctypes
ctypes.windll.kernel32.SetConsoleTitleW("Donations Engine")


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
    global killApp
    killApp = False
        
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
def sleepy(timesleep):
    global killApp
    for x in range(timesleep * 2):
        if (not killApp):
            #print ('Sleeping 1/2 a second...')
            time.sleep(0.5)
        else:
            #print ('Sleepy Kill received, exiting Selenium thread...')
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
    
    try:
        elem.select_by_value(str(EventID))
    except:
        print ('Not able to find and select event #' + str(EventID) + '. Please check event ID.')
        sys.exit(1)
        
    driver.find_element_by_xpath("/html/body/form/p/input").click()
    
    driver.get("https://tracker.2dcon.net/admin/tracker/donation/process_donations")
    
    cls()
    
    while not killApp:
        #Tracker needs time to get donations

        sleepy(1)

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
            print('----Sent Donation to reader')
        except:
            print('----Could not find any donations to send to reader, probably none')
            pass
        print ('----Last Run at ' + datetime.now().strftime("%I:%M:%S %p") + ', Waiting ' + str(autoSendDonoRate) + ' seconds to run again...')
        print ('--------------------------------------------------')

        sleepy(autoSendDonoRate)
        #Click Refresh Button
        elem = driver.find_element_by_xpath('//button[normalize-space()="Refresh"]')
        elem.click()
        
#-------End main loop for browser, next part only runs if keyboardinterrupt happened during a non-sleep command------
    #print('Kill Received, exiting Selenium thread....')
    browserKill()
    sys.exit(1)    




if __name__ == '__main__':
    # execute only if run as a script 
    main()
