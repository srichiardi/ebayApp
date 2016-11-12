import os
import csv
import requests
import json
from urllib import urlencode

def getItemsFromSeller(sellerId, totResults=10):
    ebayFindinghUrl = "http://svcs.ebay.co.uk/services/search/FindingService/v1?OPERATION-NAME=findItemsAdvanced&SERVICE-VERSION=1.13.0&SECURITY-APPNAME=StefanoR-ebayFric-PRD-19f17700d-ff298548&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD&"
    efPayload = { 'itemFilter(0).name' : 'Seller',
                  'itemFilter(0).value' : sellerId,
                  'SoldItemsOnly' : 'true',
                  'paginationInput.entriesPerPage' : 100,
                  'paginationInput.pageNumber' : 1 }
    
    
    url = ebayFindinghUrl + urlencode(efPayload)
    r = requests.get(url)
    j = json.loads(r.text)
    #totResults = int(j['findItemsAdvancedResponse'][0]['paginationOutput'][0]['totalEntries'][0])
    totPages = int(j['findItemsAdvancedResponse'][0]['paginationOutput'][0]['totalPages'][0])
    pageNr = int(j['findItemsAdvancedResponse'][0]['paginationOutput'][0]['pageNumber'][0])
    itemsList = []

    print "found %d items" % totResults
    
    if 'item' in j['findItemsAdvancedResponse'][0]['searchResult'][0].keys():
        for item in j['findItemsAdvancedResponse'][0]['searchResult'][0]['item']:
            itemsList.append(item['itemId'][0])
            
        while len(itemsList) < totResults:
            efPayload['paginationInput.pageNumber'] += 1
            url = ebayFindinghUrl + urlencode(efPayload)
            r = requests.get(url)
            j = json.loads(r.text)
            for item in j['findItemsAdvancedResponse'][0]['searchResult'][0]['item']:
                itemsList.append(item['itemId'][0])
            print "retieved %d item ids" % len(itemsList)
                
    return itemsList

def getNrOfSold(listOfItems):
    # dedup listOfItems
    setOfItems = list(set(listOfItems))
    asciiItemsStr = setOfItems[0]
    for item in setOfItems[1:]:
        asciiItemsStr += ',' + item
        
    ebayShoppingUrl = "http://open.api.ebay.com/shopping?"
    esPayload = { 'appid' : 'StefanoR-ebayFric-PRD-19f17700d-ff298548',
            'callname' : 'GetMultipleItems',
            'version' : '975',
            'responseencoding' : 'JSON',
            'ItemID' : asciiItemsStr,
            'IncludeSelector' : 'Details'}
    url = ebayShoppingUrl + urlencode(esPayload)
    r = requests.get(url)
    j = json.loads(r.text)
        
    itemsList = []
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
        itemsList.append(itemDict)
    return itemsList

def writeItemsToCsv(itemsList):
    filePath = os.getcwd() + "\\AppResults.csv"
    fileToWrite = open(filePath, 'ab')
    fieldnames = itemsList[0].keys()
    csvWriter = csv.DictWriter(fileToWrite, fieldnames, restval='',
                               extrasaction='ignore', dialect='excel')
    csvWriter.writeheader()
    for item in itemsList:
        csvWriter.writerow(item)
    fileToWrite.close()


# aggiungere SoldItemsOnly nella ricerca e status active/inactive in output + parole chiave
