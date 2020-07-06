## How The West Was Strung Scraper

This python script downloads the WDCB Radio Program *How the West Was Strung* whenever called

`Usage: python3 ./scraper.py [dest] [url]`

The current URL that lists the json content of the two week archive is

`https://wdcb-recast.streamguys1.com//api/sgrecast/podcasts/40/5d8119e7aa956?format=json`

This script is best utilized as an anacron job as follows

`7	0	htwws.scraper	/usr/bin/python3 [path to scraper.py] "[save destination]" "[above url]"`

Remember to have libraries available to anacron by running

`sudo -H pip3 install [lib]`

for the imports used