# GEOS Link Scrape
A python script to scrape links for from Georgia EPD's GEOS database
This python script was written to create a list of links for all of the Solid Waste Disposal and Recycling Report for all solid waste facilities in Georgia.

Links are genererated from GA EPD's GEOS portal ([see this](https://geos.epd.georgia.gov/GA/GEOS/Public/Client/GA_GEOS/Public/Pages/PublicApplicationList.aspx))

The main script can be be adapted to download other reports from GEOS. For more information, [contact us](mailto:leel@duck.com?subject=GEOS%20link%20scraper). 

*The development of this script was funded by the [Energy Justice Network](energyjustice.net).*

## To download all quarterly reports from GEOS

1.  Run mybot.py (python3 mybot.py) → should create a list of links (need to run on a Windows PC with Visual Studio Code?)

Note: you might need to download and run the [lastest Chromedriver](https://chromedriver.chromium.org/downloads)

1.  Ask more reports are added to GEOS, there will be more than the 137 pages of tonnage reports that exist in Dec. 2021

2.  Therefore, before running mybot.py, open the script in your text editor and replace 137 in "pagelimit = 137" with the total number of pages. 

3.  Rename the list of links "links.csv" and create a folder in your Downloads directory titled "files"

4.  Run downloadlinks.py (python3 downloadlinks.py) in the same directory as links.csv

5.  In the "files" folder you should have all tonnage reports downloaded from the GEOS database

## How to determine the total number of pages of SW tonnage reports in GEOS

You can access the GEOS portal [here](https://geos.epd.georgia.gov/GA/GEOS/Public/GovEnt/Shared/Pages/Main/Login.aspx) or [here](https://geos.epd.georgia.gov/GA/GEOS/Public/Client/GA_GEOS/Public/Pages/PublicApplicationList.aspx)

To filter for solid waste tonnage reports do the following:

-   Under category, select "Report"

-   Under department, select "Land"

-   Under program, select "Solid Waste Program"

-   Under app type, select "SW09. Solid Waste Disposal and Recycling Report"

-   Click "Search"

Right click and click "Inspect" or "Inspect element". Click the "console" tab and paste in the following:

`javascript:__doPostBack('ctl00$ctl00$SimpleMainContent$MainContent$ucApplicationSubmitList$GridView1','Page$1000')`

This should take you to the last page (provided there are less than 1,000 pages). If there are more 1,000 pages, then you can modify the 1000 to be a greater number. Note that the page number of the last page is greyed out.
