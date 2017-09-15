from xvfbwrapper import Xvfb
vdisplay = Xvfb()
vdisplay.start()


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import urllib2
import glob
import time
import os.path

driver = webdriver.Chrome()

def save_pdf(doi,link):
    doi_file = doi.replace("/","__")
    response = urllib2.urlopen(link)
    fh = open("../pdfs/" + doi_file + ".pdf", 'wb')
    fh.write(response.read())
    fh.close()
    print("Completed %s" % doi)

def get_pdf(doi):
    try:
        driver.get("http://libgen.io/scimag/")
        search = driver.find_element_by_name("s")
        search.clear()
        search.send_keys(doi)
        search.send_keys(Keys.RETURN)
        pdfs = driver.find_elements_by_id("pdf")
        if len(pdfs) != 0:
            pdf_link = pdfs[0].get_attribute("src")
            save_pdf(doi,pdf_link)
        else:
            doi_element = driver.find_element_by_link_text("Libgen")
            driver.get(doi_element.get_attribute("href"))
            download_element = driver.find_element_by_link_text("DOWNLOAD")
            pdf_link = download_element.get_attribute("href")
            save_pdf(doi,pdf_link)
    except:
        error_out = open("failed_scihub_download_doi.txt","a")
        error_out.write(doi+"\n")
        error_out.close()

def already_downloaded_doi():
    downloaded_already = []

    if os.path.exists("failed_scihub_download_doi.txt"):
        for i in open("failed_scihub_download_doi.txt","r"):
            downloaded_already.append(i.strip())

    pdfs = glob.glob("../pdfs/*.pdf")
    for pdf in pdfs:
        pdf = pdf.replace("__","/").replace("../pdfs/","").replace(".pdf","")
        downloaded_already.append(pdf)
    return downloaded_already



# read in Pubmed-ID to DOI csv file
pubmed_files = glob.glob("../data/*pubmed-crawl.csv")
latest_pubmed = pubmed_files[-1]
print("reading file %s" % latest_pubmed)
dois = []
with open(latest_pubmed) as pubmed_file:
    for line in pubmed_file:
        if line[0] != "#":
            la = line.strip().split("\t")
            if la[-1] != "DOI":
                dois.append(la[-1])

already_downloaded = already_downloaded_doi()
print(already_downloaded)

for doi in dois:
    if doi not in already_downloaded:
        if "/" in doi:
            get_pdf(doi)
            time.sleep(2)

vdisplay.stop()

