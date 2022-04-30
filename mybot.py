import os.path
#from os import path
import time
from bs4 import BeautifulSoup
#import requests
#import re
import csv
import urllib.request
#from datetime import date
from selenium import webdriver
#from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
#from random import randint
#import subprocess
import http.client
import urllib.parse
#import ssl
from pikepdf import Pdf
import chromedriver_autoinstaller
"""
This code downloads landfill reports from the noted website, cleans them, while retaining a URL to the file in pdf_links.csv.
The code can be changed to reflect a different site and different button clicks to get to the filtered files desired.
The code requires a copy of chromedriver.exe, and everything runs within one folder.
"""
chromedriver_autoinstaller.install()  
#>>>>>>>>>>>>>>>>>>>>> here you asign the starting and the ending page <<<<<<<<<<<<<<<<<<<<<<<
startPage = 1 #from
pagelimit =80 #till (check this occassionally to confirm a reasonable maximum to save time)
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

baseurl = "https://geos.epd.georgia.gov"
filesDir = "files/"
pagecount = 2
fileheader = 0
failureheader = 0
skippingprevious = True

def fixPDF(filename):
  
  print ("Fixing: ", filename)
  
  file_basename = filename[:-4]
  original_input_file_path = filename
  new_output_file_path = file_basename+".pdf"
  final_input_file_path = file_basename+".old"

  #print ("Original Input File Path:",original_input_file_path)
  #print ("New Output File Path:",new_output_file_path)
  #print ("Final Input File Path:",final_input_file_path)
  
  os.rename(original_input_file_path, final_input_file_path)
  
  pdf = Pdf.open(final_input_file_path)
  new_pdf = Pdf.new()
  for page_obj in pdf.pages:
      new_pdf.pages.append(page_obj)
  new_pdf.save(new_output_file_path)

  #os.rename(original_input_file_path, final_input_file_path)
  #os.rename(tmp_output_file_path, original_input_file_path)
  print("Fixed: ",filename)
  return

def getPDF(docLink, fileName):
  global filesDir
  url = docLink
  title = fileName
  if "https" in url:
    splitUrl = url
    splitUrl = splitUrl.split("=")
    formid=splitUrl[len(splitUrl)-2].replace("&type","")
    filename = filesDir + title.replace("/","_") + "_" + formid + ".pdf"
    if skippingprevious and not os.path.isfile(filename):
        print("downloading ID = " + formid)
        try:
            urllib.request.urlretrieve(url, filename)
            fixPDF(filename)
  
        except Exception as inst:
            print (inst)
            print ("error downloading")
    else:
        print ("skipping ID = " + formid)
  return
            
def writerow(docLink, fileName):
  global fileheader
  with open ('pdf_links.csv', 'a', newline='', encoding='utf-8') as f:
    fieldnames = ['Document Link', 'title']
    # fieldnames = ['Document Link']
    thewriter = csv.DictWriter(f, fieldnames = fieldnames) 
    if (fileheader ==  0 ):
      thewriter.writeheader()
      fileheader = fileheader+1
      print("running file if")
    thewriter.writerow({'Document Link':docLink, 'title':fileName})
    # thewriter.writerow({'Document Link':docLink})
  return

def rowfailure(fileName, currentPage, viewstate):
  global failureheader
  with open ('failures.csv', 'a', newline='', encoding='utf-8') as f:
    fieldnames = ['title', 'page#', 'viewstate']
    # fieldnames = ['Document Link']
    thewriter = csv.DictWriter(f, fieldnames = fieldnames) 
    if (failureheader ==  0 ):
      thewriter.writeheader()
      failureheader = failureheader+1
      print("running file if")
    thewriter.writerow({ 'title':fileName, 'page#':currentPage, 'viewstate':viewstate })
    # thewriter.writerow({'Document Link':docLink})
  return

def waitTillLoader(driver):
  while True:
    time.sleep(3)
    pageData = driver.page_source
    html = BeautifulSoup(pageData, 'html.parser')
    loader = html.find("div", id='masterUpdateProgress').get("style")
    print(loader)
    if "block" in loader:
      time.sleep(3)
      continue
    else:
      return

def goNext(driver):
  global pagecount
  if(pagecount <= pagelimit):
    driver.execute_script('javascript:__doPostBack("ctl00$ctl00$SimpleMainContent$MainContent$ucApplicationSubmitList$GridView1","Page$+'+str(pagecount)+'")')
    waitTillLoader(driver)
    pagecount = pagecount + 1
    extractpage(driver)
  else:
    driver.close()

def navigate(driver, currentPage, startPage):
  global pagecount
  while True:
    pageData = driver.page_source
    html = BeautifulSoup(pageData, 'html.parser')
    currentPage = html.find("tr", class_="grdPager")
    currentSeg = currentPage.find("tbody").tr.find_all("td")
    currentPage = currentPage.find("span").text
    for i in range(0, len(currentSeg)):
      if (i == int(currentPage)):
        continue
      if (currentSeg[i].text.strip() == '...'):
        continue
      if( int(currentSeg[i].text.strip() ) == startPage):
        driver.execute_script('javascript:__doPostBack("ctl00$ctl00$SimpleMainContent$MainContent$ucApplicationSubmitList$GridView1","Page$+'+str(startPage)+'")')
        waitTillLoader(driver)
        pagecount = startPage
        extractpage(driver)
    nextSeg = currentSeg[len(currentSeg)-1].a.get("href")
    print(nextSeg)
    driver.execute_script(str(nextSeg))
    waitTillLoader(driver)

def extractpage(driver):
  global startPage
  pageData = driver.page_source
  html = BeautifulSoup(pageData, 'html.parser')
  currentPage = html.find("tr", class_="grdPager")
  currentPage = currentPage.find("span").text

  if ( int(currentPage) < startPage):
    navigate(driver, currentPage, startPage)

  tds = html.find_all("input", type='image')
  viewstate = ""
  viewstate = urllib.parse.quote(html.find("input", id='__VIEWSTATE').get("value"), safe="")
  # print(viewstate)
  #print(len(tds))
  for x in range(0, len(tds)):
    button_name = urllib.parse.quote(tds[x].get("name"), safe="")
    try:
      fileName = tds[x].find_next("td").text.strip()
    except:
      fileName = "file name not found or Empty"
    print("Reading Page: ",currentPage)
    setFirstCall(button_name, viewstate, fileName, currentPage)
  goNext(driver)

def setFirstCall(button_name, viewstate, fileName, currentPage):
  #print(button_name)
  conn = http.client.HTTPSConnection("geos.epd.georgia.gov")
  payload = 'SimpleMainContent_MainContent_tabView_IDX=0&__ASYNCPOST=true&__EVENTARGUMENT=&__EVENTTARGET=&__LASTFOCUS=&__VIEWSTATE='+viewstate+'&__VIEWSTATEGENERATOR=55AD252D&ctl00%24ctl00%24ScriptManager1=ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24UpdatePanel2%7C'+button_name+'&'+button_name+'.x=17&'+button_name+'.y=6&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24ddlApplication=2148&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24ddlApplicationType=10036&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24ddlCategory=1&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24ddlProgram=3&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24ddlSiteCounty=&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24ddlSubmissionStatus=&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24txtEndDate=&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24txtFacilityName=&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24txtPermitNumber=&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24txtSiteAddress1=&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24txtSiteCity=&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24txtStartDate=&ctl00%24ctl00%24SimpleMainContent%24MainContent%24ucApplicationSubmitList%24txtSubmissionId=&ctl00%24ctl00%24footerContent%24Footer1%24ctl00%24PopupPanel1eftPopPanlHF=false&ctl00%24ctl00%24footerContent%24Footer1%24ctl00%24pnleftPopPanlHF=false&ctl00%24ctl00%24sDateFormat=&hiddenInputToUpdateATBuffer_CommonToolkitScripts=1'
  headers = {
    'sec-ch-ua': '"Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cache-Control': 'no-cache',
    'X-Requested-With': 'XMLHttpRequest',
    'X-MicrosoftAjax': 'Delta=true',
    'sec-ch-ua-platform': '"Windows"',
    'Accept': '*/*',
    'Cookie': 'ASP.NET_SessionId=lyo0az01basqynsstsckdkew; BIGipServereft-http-pool-GOV-PRD-GA-GEOS=1470671020.20480.0000'
  }
  try:
    conn.request("POST", "/GA/GEOS/Public/Client/GA_GEOS/Public/Pages/PublicApplicationList.aspx", payload, headers)
  except:
    try:
      conn.request("POST", "/GA/GEOS/Public/Client/GA_GEOS/Public/Pages/PublicApplicationList.aspx", payload, headers)
    except:
      print("issues while POST request")
      rowfailure(fileName, currentPage, viewstate)
      return

  res = conn.getresponse()
  data = res.read()
  #next API call
  repayload = ''
  reheaders = {
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="100", "Google Chrome";v="100"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Cookie': 'ASP.NET_SessionId=lyo0az01basqynsstsckdkew; BIGipServereft-http-pool-GOV-PRD-GA-GEOS=1470671020.20480.0000'
  }
  try:
    conn.request("GET", "/GA/GEOS/Public/Client/GA_GEOS/Public/Pages/PublicApplicationDetail.aspx", repayload, reheaders)
  except:
    try:
      conn.request("GET", "/GA/GEOS/Public/Client/GA_GEOS/Public/Pages/PublicApplicationDetail.aspx", repayload, reheaders)
    except:
      print("issues while GET request")
      rowfailure(fileName, currentPage, viewstate)
      return
  reres = conn.getresponse()
  newdata = reres.read()
  res_html = BeautifulSoup(newdata, 'html.parser')
  try:
    formId_href = res_html.find("a", id='SimpleMainContent_MainContent_ucApplicationSubmitInfo_rptForms_lnkReport_0')
    formId = formId_href.get("href").replace("(","").replace(")","")
    button_name = ""
    docLink = baseurl+formId.replace("javascript:jsPopWin'", "").replace("';","")
  except:
    docLink="The File is not available for this record"
  print(docLink)
  writerow(docLink, fileName)
  getPDF(docLink, fileName)

def filterSelections():
  options = webdriver.ChromeOptions()
  options.add_argument("--incognito")
  driver = webdriver.Chrome(options=options)
  driver.get(baseurl+"/GA/GEOS/Public/Client/GA_GEOS/Public/Pages/PublicApplicationList.aspx")

  print(">>Selecting Category<<")
  select_cat = Select(driver.find_element(By.ID,'SimpleMainContent_MainContent_ucApplicationSubmitList_ddlCategory')) 
  select_cat.select_by_value('1')
  waitTillLoader(driver)

  print(">>Selecting Program<<")
  select_pro = Select(driver.find_element(By.ID, 'SimpleMainContent_MainContent_ucApplicationSubmitList_ddlProgram')) 
  select_pro.select_by_value('3')
  waitTillLoader(driver)

  print(">>Selecting App-type<<")
  select_app_type = Select(driver.find_element(By.ID, 'SimpleMainContent_MainContent_ucApplicationSubmitList_ddlApplicationType')) 
  select_app_type.select_by_value('10036')
  waitTillLoader(driver)

  print(">>Selecting App<<")
  select_app = Select(driver.find_element(By.ID,'SimpleMainContent_MainContent_ucApplicationSubmitList_ddlApplication')) 
  select_app.select_by_value('2148')
  waitTillLoader(driver)

  print(">>Fetching Reports<<")
  driver.find_element(By.ID, 'SimpleMainContent_MainContent_ucApplicationSubmitList_btnSearch').click()
  waitTillLoader(driver)
  extractpage(driver)

if __name__ == "__main__":
  filterSelections()
