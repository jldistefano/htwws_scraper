import cfscrape
import requests
import eyed3
import json
import sys
import logging
from os import listdir
from os import path
from os import mkdir
import datetime
from dateutil import parser

### Parameters ###
## Destination for download
dest = sys.argv[1]
## URL for 2 week archive, get from wdcb.org/archive network traffic
url = sys.argv[2]
##################

# Checks for a valid internet connection every 'interval' seconds up to a maximum of 'seconds' seconds
def waitForInternetConnection(seconds, interval):
	# Loop until either valid request is made or time is up
	while interval < seconds:
		try:
			r = requests.get('https://www.google.com')
		except:
			sleep(interval)
			interval += interval
			continue

		# If a ok status is returned, then there is a valid internet connection
		if r.status_code == requests.codes.ok:
			return True

	return False

# Set up logging file if not exists
logging_path = path.dirname(path.abspath(__file__)) + '/.logs'
logging_file = logging_path + '/htwws_scraper.log'

if not path.exists(logging_file):
	if not path.exists(logging_path):
		mkdir(logging_path)
	fh = open(logging_file, 'w+')
	fh.close()

# Set up logging
logging.basicConfig(filename=logging_file, filemode='a', format='%(asctime)s %(message)s', level=logging.INFO)

# Get 2 week archive page
scraper = cfscrape.create_scraper()

# If destination does not end in /, insert /
if dest[-1] != '/':
	dest += '/'

# Find how many programs have already been saved
track_num = 1
try:
	for filename in listdir(dest):
		if "mp3" in filename.split('.')[-1]:
			track_num += 1
except Exception as e:
	logging.error(e)
	logging.error("Destination location \"" + dest + "\" could not be found. Exiting...")
	sys.exit()

# Wait 60 seconds for internet connection
if not waitForInternetConnection(60, 5):
	logging.error("Could not connect to internet. Exiting...")
	sys.exit()

# Try at most 3 times to get page
logging.info("Connecting to WDCB 2 Week Archive")
htwws = "not found"
for attempt in range(3):
	try:
		r = scraper.get(url)
		archive_json = json.loads(r.content)

		# Find Most Recent HTWWS
		for program in archive_json['channel']['items']:
			if "How the West was Strung" in program['title']:
				htwws = program
				break

		# If htwws changes, then break out of loop
		if htwws != "not found":
			break

	# If error, then retry
	except Exception as e:
		logging.error(e)
		logging.error("Error connecting to WDCB archive. Attempt # " + str(attempt + 1))
		continue

# If unable to connect to page, then exit
if htwws == "not found":
	logging.error("Could not connect to WDCB archive after 3 attempts, logs above. Exiting...")
	sys.exit()

# Get date string
# ex) "Tue, 12 May 2020 10:00:03 -0500"
fulldate = htwws['pubDate']
dateobj = parser.parse(fulldate)
datestring = dateobj.strftime("%m-%d-%y")

# Check if file exists, if so then exit
filename = dest + "htwws-" + datestring + ".mp3"
if path.isfile(filename):
	logging.warning(filename + " already exists. Exiting...")
	sys.exit()

# Download Raw Audio
logging.info("Downloading " + filename)
raw_audio = scraper.get(htwws['url'], stream=True)
try:
	with raw_audio as r:
		r.raise_for_status()
		with open(filename, 'wb') as f:
			for chunk in r.iter_content(chunk_size=8192):
				f.write(chunk)
except Exception as e:
	logging.error(e)
	logging.error("Error while writing sound file to destination. Exiting...")
	sys.exit()

# Set MP3 Tags
file = eyed3.load(filename)
file.initTag()
file.tag.artist = "WDCB"
file.tag.album = "How The West Was Strung"
file.tag.title = datestring
file.tag.track_num = track_num

# read cover into memory
try:
	imagedata = open(dest + "cover.jpg","rb").read()
	file.tag.images.set(3, imagedata, "image/jpeg", u"How The West Was Strung: 11pm - 12am 90.9FM WDCB")
except:
	logging.warning("Could not find cover art, continuing with no art")

file.tag.save()

logging.info(filename + " scraped and saved. Exiting...")