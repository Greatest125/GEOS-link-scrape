#!/usr/bin/python3.3
import os.path
import urllib.request
import ssl
from csv import reader

ssl._create_default_https_context = ssl._create_unverified_context

#Open CSV file and read headers (don't care)

with open('pdf_links.csv','r') as csvfile:
    csv_reader = reader(csvfile)

#Cycle through CSV file, splitting lines, and downloading files

    for row in csv_reader:
        if "https" in row:
            splitUrl = row[0]
		    splitUrl = splitUrl.split("=")
			formid=splitUrl[len(splitUrl)-2].replace("&type","")
            filename = "files/"+row[2]+" "+row[1].replace("/","_")+".pdf"
        
            if not os.path.isfile(filename):
                try:
                    urllib.request.urlretrieve(link, filename)
                    print('Downloaded: ' + filename)
                except Exception as inst:
                    print(inst)
                    print('  Encountered unknown error. Continuing.')

        else:
            continue