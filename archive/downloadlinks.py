import urllib.request
import csv
import os.path

with open('pdf_links.csv', encoding="utf8") as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		url = row['Document Link']
		title = row ['title']
		if "https" in url:
			splitUrl = url
			splitUrl = splitUrl.split("=")
			formid=splitUrl[len(splitUrl)-2].replace("&type","")
			filename = "files/" + title.replace("/","_") + "_" + formid + ".pdf"
			if not os.path.isfile(filename):
				print("downloading ID = " + formid)
				try:
					urllib.request.urlretrieve(url, filename)
				except Exception as inst:
					print (inst)
					print ("error downloading")
			else:
				print ("skipping ID = " + formid)
		else:
			continue