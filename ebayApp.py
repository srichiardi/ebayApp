import os
import sys
import csv
import requests
import json
import time
from urllib import urlencode
from ebayAppWidgets import appDlg
from eBayGlobalMap import globalSiteMap

def getItemsFromSeller(searchOptions):

    efPayload = { 'itemFilter(0).name' : 'Seller',
                  'itemFilter(0).value' : searchOptions['sellerId'],
                  'paginationInput.entriesPerPage' : 100,
                  'paginationInput.pageNumber' : 1 }
    
    if 'soldOnly' in searchOptions.keys():
        efPayload['SoldItemsOnly'] = searchOptions['soldOnly']

    if 'keywords' in searchOptions.keys():
        efPayload['keywords'] = searchOptions['keywords']
        
    if len(searchOptions['sites']) == 0:
        searchOptions['sites'].append('US')
        
    ebayFindinghUrl = "http://svcs.ebay.co.uk/services/search/FindingService/v1?\
    OPERATION-NAME=findItemsAdvanced&\
    SERVICE-VERSION=1.13.0&\
    SECURITY-APPNAME=StefanoR-ebayFric-PRD-19f17700d-ff298548&\
    RESPONSE-DATA-FORMAT=JSON&\
    REST-PAYLOAD&"
    
    itemsDict = {}
    
    for site in searchOptions['sites']:
        ebayFindinghUrl += globalSiteMap[site]['globalID'] + "&"
        
        # pulling results from every page
        while True:
            url = ebayFindinghUrl + urlencode(efPayload)
            r = requests.get(url)
            j = json.loads(r.text)
            totPages = int(j['findItemsAdvancedResponse'][0]['paginationOutput'][0]['totalPages'][0])
            pageNr = int(j['findItemsAdvancedResponse'][0]['paginationOutput'][0]['pageNumber'][0])
            totResults = int(j['findItemsAdvancedResponse'][0]['paginationOutput'][0]['totalEntries'][0])
            
            # break while loop if there are no results in the current site
            if totResults == 0: break
            
            # save item id in a dictionary key = item, value = list of sites
            for item in j['findItemsAdvancedResponse'][0]['searchResult'][0]['item']:
                try:
                    itemsDict[item].append(site)
                except KeyError:
                    itemsDict[item] = [site]
                    
            # break while loop if reached last page
            if totPages == pageNr: break
            
            efPayload['paginationInput.pageNumber'] += 1
            
    return itemsDict


def getNrOfSold(dictOfItems):
    
    itemsBySite = {}
    sitesByitem = {}
    itemsList = []
    
    for site in globalSiteMap.keys():
        for item in dictOfItems.keys():
            if site in dictOfItems[item]:
                try:
                    itemsBySite[site].append(item)
                except KeyError:
                    itemsBySite[site] = [item]
                finally:
                    sitesByitem[item] = dictOfItems.pop(item)
    
    # requests are made in batches based on site id
    for site in itemsBySite.keys():
        siteID = globalSiteMap[site]['siteID']
        
        # split nr of item in single request if > 20 per request
        maxItems = 20
        ibs = itemsBySite[site]
        itemsMatrix = [ibs[i:i+maxItems] for i in range(0,len(ibs),maxItems)]
        
        for ilist in itemsMatrix:
            asciiItemsStr = ','.join(ilist)
                
            ebayShoppingUrl = "http://open.api.ebay.com/shopping?"
            esPayload = { 'appid' : 'StefanoR-ebayFric-PRD-19f17700d-ff298548',
                    'callname' : 'GetMultipleItems',
                    'version' : '975',
                    'responseencoding' : 'JSON',
                    'ItemID' : asciiItemsStr,
                    'IncludeSelector' : 'Details',
                    'siteid' : siteID }
            
            url = ebayShoppingUrl + urlencode(esPayload)
            r = requests.get(url)
            j = json.loads(r.text)
            
            for item in j['Item']:
                itemDict = {}
                itemDict["Item_id"] = item["ItemID"]
                itemDict["ListingStatus"] = item["ListingStatus"]
                itemDict["Location"] = item["Location"]
                itemDict["Price"] = item["CurrentPrice"]["Value"]
                itemDict["Currency"] = item["CurrentPrice"]["CurrencyID"]
                itemDict["Quantity_sold"] = item["QuantitySold"]
                itemDict["Title"] = item["Title"]
                itemDict["Quantity"] = item["Quantity"]
                itemDict["Seller_id"] = item["Seller"]["UserID"]
                itemDict["PictureURL"] = item["PictureURL"]
                itemDict["OriginalURL"] = item["ViewItemURLForNaturalSearch"]
                itemDict["Sites"] = ', '.join(sitesByitem[item])
                itemsList.append(itemDict)
            
    return itemsList


def writeItemsToCsv(outputPath, itemsList):
    filePath = outputPath + "/eBayItemDetails_%s.csv" % time.strftime("%Y%m%d-%H%M%S")
    fileToWrite = open(filePath, 'ab')
    fieldnames = itemsList[0].keys()
    csvWriter = csv.DictWriter(fileToWrite, fieldnames, restval='',
                               extrasaction='ignore', dialect='excel')
    csvWriter.writeheader()
    for item in itemsList:
        csvWriter.writerow(item)
    fileToWrite.close()


def main():
    print "Claudio sei un FRICO!!!"
    options = appDlg().mainloop()
    if 'sellerId' not in options.keys():
        print "missing seller ID!"
        time.sleep(3)
        sys.exit()
    else:
        itemsList = getItemsFromSeller(options)
        itemsDesc = getNrOfSold(itemsList)
        if len(itemsDesc) > 0:
            writeItemsToCsv(options['outputFolder'], itemsDesc)
        else:
            print "no items found"
            time.sleep(3)


if __name__ == "__main__":
    main()
    
##### TO DO #####
'''
Add Items Ended
Map siteIDs to GlobalIDs in seller search and item search calls
Add searches in Global eBay sites
Add link to the listing DONE
Add picturesURL to output DONE
'''

##### REFERENCES #####
'''
http://developer.ebay.com/Devzone/finding/Concepts/SiteIDToGlobalID.html
http://developer.ebay.com/Devzone/finding/Concepts/MakingACall.html#StandardURLParameters
http://developer.ebay.com/Devzone/finding/CallRef/findItemsAdvanced.html
'''