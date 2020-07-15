import cfscrape
import eyed3
import json
import sys
import logging
from os import listdir
from os import path
import datetime
from dateutil import parser

### Parameters ###
## Destination for download
dest = sys.argv[1]
## URL for 2 week archive, get from wdcb.org/archive network traffic
url = sys.argv[2]
##################

# Set up logging
logging.basicConfig(filename='/var/log/htwws_scraper.log', filemode='a', format='%(asctime)s %(message)s', level=logging.DEBUG)
logger = logging.getLogger('htwws_scraper')
fh = logging.FileHandler('/var/log/htwws_scraper.log')
fh.setLevel(logging.INFO)
logger.addHandler(fh)

# Get 2 week archive page
scraper = cfscrape.create_scraper()

# If destination does not end in /, insert /
if dest[-1] != '/'
	dest += '/'

# Find how many programs have already been saved
track_num = 1
try:
	for filename in listdir(dest):
		if "mp3" in filename.split('.')[-1]:
			track_num += 1
except:
	logger.error("Destination location \"" + dest + "\" could not be found")
	sys.exit()

# Try at most 3 times to get page
htwws = "not found"
try:
	for attempt in range(3):
		archive_json = json.loads(scraper.get(url).content)

		# Find Most Recent HTWWS
		for program in archive_json['channel']['items']:
			if "How the West was Strung" in program['title']:
				htwws = program
				break

		# If not found, then retry
		if htwws == "not found":
			continue
except:
	logger.error("Error while trying to connect to WDCB two week archive url")
	sys.exit()

# If unable to connect to page, then exit
if htwws == "not found":
	logger.warning("How the West Was Strung could not be found")
	sys.exit()

# Get date string
# ex) "Tue, 12 May 2020 10:00:03 -0500"
fulldate = htwws['pubDate']
dateobj = parser.parse(fulldate)
datestring = dateobj.strftime("%m-%d-%y")

# Check if file exists, if so then exit
filename = dest + "htwws-" + datestring + ".mp3"
if path.isfile(filename):
	logger.warning(filename + " already exists, exiting...")
	sys.exit()

# Download Raw Audio
raw_audio = scraper.get(htwws['url'], stream=True)
try:
	with raw_audio as r:
		r.raise_for_status()
		with open(filename, 'wb') as f:
			for chunk in r.iter_content(chunk_size=8192):
				f.write(chunk)
except:
	logger.error("Error while writing sound file to destination")
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
	imagedata = open("cover.jpg","rb").read()
	file.tag.images.set(3, imagedata, "image/jpeg", u"How The West Was Strung: 11pm - 12am 90.9FM WDCB")
except:
	logger.warning("Could not find cover art, continuing with no art")

file.tag.save()

logger.info(filename + " scraped and saved")