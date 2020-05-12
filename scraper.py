import cfscrape
import eyed3
import json
import sys
from os import listdir
import datetime
from dateutil import parser

### Parameters ###
## Destination for download
dest = "/home/jdistefano/UIC/personal_projects/htwws_scraper/"
## URL for 2 week archive, get from wdcb.org/archive network traffic
url = "https://wdcb-recast.streamguys1.com//api/sgrecast/podcasts/40/5d8119e7aa956?format=json"
##################

# Get 2 week archive page
scraper = cfscrape.create_scraper()

# Find how many programs have already been saved
track_num = 1
for filename in listdir(dest):
	if "mp3" in filename.split('.')[-1]:
		track_num += 1

# Try at most 3 times to get page
htwws = "not found"
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

# If unable to connect to page, then exit
if htwws == "not found":
	sys.exit()

# Get date string
# ex) "Tue, 12 May 2020 10:00:03 -0500"
fulldate = htwws['pubDate']
dateobj = parser.parse(fulldate)
datestring = dateobj.strftime("%m-%d-%y")

# Download Raw Audio
raw_audio = scraper.get(htwws['url'], stream=True)
filename = dest + "htwws-" + datestring + ".mp3"
with raw_audio as r:
	r.raise_for_status()
	with open(filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=8192):
			f.write(chunk)

# Set MP3 Tags
file = eyed3.load(filename)
file.initTag()
print(file)
file.tag.artist = "WDCB"
file.tag.album = "How The West Was Strung"
file.tag.title = datestring
file.tag.track_num = track_num

# read cover into memory
imagedata = open("cover.jpg","rb").read()
file.tag.images.set(3, imagedata, "image/jpeg", u"How The West Was Strung: 11pm - 12am 90.9FM WDCB")
file.tag.save()