# Daily Blast, Greg Sargent, DSR Network RSS Feed Filter

Given a paid private DSR network RSS feed, 
filter out and include only Daily Blast podcasts, 
from within the last 10 days,
and return those in RSS 2.0 XML format.

The script can be easily deployed as an AWS lambda. 

The XML is created by hand, which is unfortunate, but all the RSS 
and XML libraries I could find for python depend on the lxml library
which is difficult to get working on AWS Lambda since it requires a 
native binary.
