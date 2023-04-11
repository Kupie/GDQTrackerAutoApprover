#CONFIGURE STUFF HERE


#Tracker Login Info
trackerUser = "USERNAME_HERE"
trackerPassword = "PASSWORD_HERE"

#How many seconds in between updates. Don't crank this number too low, bullying servers is rude
donoRefreshRate = 30

#Should we update donation totals? Set to True/False only
#currently unimplemented, always does this
updateTotals = True

#add spaces to donation totals
spaceCenteredDono = True

#Should we automatically approve donations to send to the host? True/False only
#currently unimplemented, always does this
autoApprove = True

#Force through donations with "Flagged" transaction state?
#currently unimplemented
approveFlaggedDonos = False

#Force through donations with "Pending" transaction state?
#currently unimplemented
approvePendingDonos = False



#Event ID in tracker (Go to "edit event" and look at the URL, number between 'event' and 'change'; MWSF2021 is "3" for example: https://tracker.2dcon.net/admin/tracker/event/3/change/
EventID = 16


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
	pass

#Set Window Title. I stuck this under a "try" command because this would fail on Linux systems due to no ctypes/window stuffs
#This also disables quick edit mode as selecting the window freezes everything
try:
	k32 = windll.kernel32
	k32.SetConsoleTitleW("Donations Engine")
	k32.SetConsoleMode(kernel32.GetStdHandle(-10), 128)
except:
	if os.name=='nt':
		print('Missing module ctypes, somehow... it is packaged in Python these days...')
		os.system('title Donations Engine')
	else:
		pass
	pass

#Import the rest
import time
from datetime import datetime

try:
	import requests
except ImportError:
	print ('Python module requests not installed, please run "pip install requests" to install and then run this script again')
	sys.exit(1)


try:
	import traceback
except ImportError:
	print ('Python module traceback not installed, please run "pip install traceback" to install and then run this script again')
	sys.exit(1)


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
	import urllib3
except ImportError:
	print ('Python module urllib3 not installed, please run "pip install urllib3" to install and then run this script again')
	sys.exit(1)
#disable SSL warnings. Tracker requires HTTPS but sometimes their certificate isn't "proper", this makes it connect
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
	
#-------------------END IMPORTING AREA---------------------#

requestsSession = None

def main():

	#Did you know we can just use a "session" class in requests and it'll automagically handle storing/retreiving cookies? dafuq, that's amazing
	#And then it just works using "session.request" instead of "requests.request"
	# #magic
	global requestsSession
	global DonoTotal
	#Only login once if requestsSession is null
	if not requestsSession:
		print('Logging in...')
		requestsSession = requests.Session()
		
		#Initial Donation Totals
		DonoTotal = '0'
		
		url = "https://tracker.2dcon.net/admin/login"
		
		payload={}
		headers = {
			'Host': 'tracker.2dcon.net'
		}
		
		try:
			#Make the request to tracker, plus the "goals" and "bidwars" page
			response = requestsSession.request("GET", url, headers=headers, data=payload, verify=False)
		except:
			#If it fails, URL is invalid... or Tracker is down. That's always an option
			print ("Invalid URL connection to tracker failed. Open this python script and check that 2nd line! Exiting...")
			sys.exit(1)
		
		
		csrfMiddlewareTokenVar = htmlGetCsrfMiddlewareToken(response)
		#print()
		#print('csrfmiddlewaretoken:')
		#print(csrfMiddlewareTokenVar)
		
		####################################################################################################
		##################################LOGIN#############################################################
		####################################################################################################
		url = "https://tracker.2dcon.net/admin/login/?next=/admin/"
		
		
		#tracker won't accept json content-type for some reason... who knows, I still wanna format things easily in a "dict" first and then this just converts it to urlencoded after
		payload_json = {
			'csrfmiddlewaretoken' : csrfMiddlewareTokenVar, 
			'username' : trackerUser,
			'password' : trackerPassword,
			}
		
		payload = str()
		for i in payload_json:
			payload += i + '=' + payload_json[i] + '&'
		
		headers = {
			'Host': 'tracker.2dcon.net',
			'Content-Type': 'application/x-www-form-urlencoded', 
			'Referer': 'https://tracker.2dcon.net/admin/login/?next=/admin/', 
		
		}
		
		response = requestsSession.request("POST", url, headers=headers, data=payload, verify=False)
		#print(response.text)
		#csrfMiddlewareTokenVar = htmlGetCsrfMiddlewareToken(response)
	
	
	
	####################################################################################################
	##################################GET DONATIONS TO APPROVE##########################################
	####################################################################################################
	url = "https://tracker.2dcon.net/tracker/api/v1/search/?type=donation&all_comments=&feed=toprocess&event=" + str(EventID)
	
	payload={}
	headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
	'Referer': 'https://tracker.2dcon.net/admin/tracker/donation/process_donations',
	}
	
	response = requestsSession.request("GET", url, headers=headers, data=payload, verify=False)
	
	####################################################################################################
	##################################APPROVE LIST OF DONATIONS#########################################
	####################################################################################################
	for i in response.json():
		url = "https://tracker.2dcon.net/tracker/api/v1/edit/"
		donoID = str(i['pk'])
		try:
			Donor = str(i['fields']['donor__public'])
		except:
			Donor = 'No Donor...lolwut?'
		payload = "type=donation&id=" + donoID + "&readstate=READY&commentstate=APPROVED"
		headers = {
			'Host': 'tracker.2dcon.net',
			'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
			'Referer': 'https://tracker.2dcon.net/admin/tracker/donation/process_donations',
		}
		
		response = requestsSession.request("POST", url, headers=headers, data=payload, verify=False)
		print('Approved Donation ID: ' + donoID + '; Donor: ' + Donor)
		#print(json.dumps(i, indent = 6))

	####################################################################################################
	##################################UPDATE DONATION TOTALS############################################
	####################################################################################################
	
	
	url = 'https://tracker.2dcon.net/tracker/event/' + str(EventID)
	try:
		#Make the request to tracker, plus the "goals" and "bidwars" page
		page = requests.get(url, verify=False)
	except:
		#If it fails, URL is invalid... or Tracker is down. That's always an option
		print ("Invalid URL connection to tracker failed. Open this python script and check that 2nd line! Trying again...")
		pass
	soup = BeautifulSoup(page.content,'html.parser')
	
	span = soup.find('h2', class_='text-center')
	spantext1 = span.text.split('(')
	
	spantext2 = spantext1[-2].split('$')[-1]
	spantext3 = spantext2.replace(',', '')
	spanint = int(spantext3.split(".")[0])
	
	
	if (spanint > int(DonoTotal)):
		DonoTotal = spanint
		DonoTotal = str(int(DonoTotal) )
	
	if (spaceCenteredDono):
		#Used for testing different number values
		#DonoTotal = '2000'
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
		


def htmlGetCsrfMiddlewareToken(requestResponse):
	soup = BeautifulSoup(requestResponse.content,'html.parser')
	csrfmiddlewaretoken = soup.find('input', attrs={'name':'csrfmiddlewaretoken', 'type':'hidden'}).get('value')
	return csrfmiddlewaretoken


if __name__ == '__main__':
	#Set up a log file
	
		# execute only if run as a script
		#Also, execute every seconds
		
		while True:
			try:
				cls()
				main()
				time.sleep(donoRefreshRate)
			except KeyboardInterrupt:
				print('Ctrl+C has been hit, exiting script...')
				time.sleep(2)
				sys.exit(1)
				
			except Exception as e:
				print(e)
				print('Donation Script failed with above error... restarting in ' + str(donoRefreshRate) + 'seconds!')
				file = open('Donation_Engine_Rewrite_log.txt', 'a')
				traceback.print_exc(file=file)
				file.close()
				try:
					time.sleep(donoRefreshRate)
				except KeyboardInterrupt:
					print('Ctrl+C has been hit, exiting script...')
					sys.exit(1)
				continue
				
			
