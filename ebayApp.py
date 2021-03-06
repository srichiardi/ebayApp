import os
import sys
import csv
import requests
import json
import time
import re
from collections import OrderedDict
from urllib import urlencode
from modules.ebayAppWidgets import appDlg
from modules.eBayGlobalMap import globalSiteMap


def json_flat(json_obj):
    assert isinstance(json_obj, dict), "input is not a dictionary"
    flat_data = {}
    
    def flatten(value, key=""):
        # for nested dictionaries, the function returns the most inner key value pair
        if isinstance(value, dict):
            for k, v in value.items():
                flatten(v, k)
        
        # for lists of values, the function returns a string with all values
        # assuming that json doesn't have list of lists, nested lists, the 
        # function doesn't check for those. 
        elif isinstance(value, list):
            if len(value) > 0 and isinstance(value[0], dict):
                for v in value:
                    flatten(v)
            else:
                flat_data[key] = ", ".join(value)
        
        else:
            flat_data[key] = value
            
    flatten(json_obj)
    return flat_data


def getItemsFromSeller(searchOptions):
    
    nrOfCalls = 0

    efPayload = { 'paginationInput.entriesPerPage' : 100 }
    
    i = 0
    
    if 'sellerId' in searchOptions.keys():
        efPayload['itemFilter({}).name'.format(i)] = 'Seller'
        efPayload['itemFilter({}).value'.format(i)] = searchOptions['sellerId']
        i += 1

    if 'keywords' in searchOptions.keys():
        efPayload['keywords'] = searchOptions['keywords']
        
    if len(searchOptions['sites']) == 0:
        searchOptions['sites'].append('US')
        
    if 'descriptionSearch' in searchOptions.keys():
        efPayload['descriptionSearch'] = searchOptions['descriptionSearch']
        
    findingUrlTmplt = "http://svcs.ebay.com/services/search/FindingService/v1?\
OPERATION-NAME=findItemsAdvanced&\
SERVICE-VERSION=1.13.0&\
SECURITY-APPNAME=StefanoR-ebayFric-PRD-19f17700d-ff298548&\
RESPONSE-DATA-FORMAT=JSON&\
GLOBAL-ID={}&\
REST-PAYLOAD&"
    
    itemsDict = {}
    
    for site in searchOptions['sites']:
        ebayFindingUrl = findingUrlTmplt.format( globalSiteMap[site]['globalID'] )
        efPayload['paginationInput.pageNumber'] = 1
        
        # pulling results from every page
        while True:
            url = ebayFindingUrl + urlencode(efPayload)
            r = requests.get(url)
            j = json.loads(r.text)
            totPages = int(j['findItemsAdvancedResponse'][0]['paginationOutput'][0]['totalPages'][0])
            pageNr = int(j['findItemsAdvancedResponse'][0]['paginationOutput'][0]['pageNumber'][0])
            totResults = int(j['findItemsAdvancedResponse'][0]['paginationOutput'][0]['totalEntries'][0])
            
            nrOfCalls += 1
            
            # break while loop if there are no results in the current site
            if totResults == 0: break
            
            # save item id in a dictionary key = item, value = list of sites
            for item in j['findItemsAdvancedResponse'][0]['searchResult'][0]['item']:
                try:
                    if site not in itemsDict[ item['itemId'][0] ]:
                        itemsDict[ item['itemId'][0] ].append(site)
                except KeyError:
                    itemsDict[ item['itemId'][0] ] = [site]
                    
            # break while loop if reached last page
            if totPages == pageNr or pageNr == 100: break
            
            efPayload['paginationInput.pageNumber'] += 1
    
    print "findItemsAdvanced API made %d calls" % nrOfCalls
    
    return itemsDict


def getNrOfSold(dictOfItems):
    
    nrOfCalls = 0
    
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
            #j = json.loads(r.text.decode('utf-8'))
            j = json.loads(r.text)
            
            nrOfCalls += 1
            
            for item in j['Item']:
                itemDict = OrderedDict()
                flat_item = json_flat(item)
                for key in ["UserID", "ItemID", "ListingStatus", "Location", "Quantity", "QuantitySold", "Value",
                            "CurrencyID", "Title", "PictureURL", "ViewItemURLForNaturalSearch", "GlobalShipping",
                            "ShipToLocations", "Name", "Street1", "Street2", "CityName", "StateOrProvince", "CountryName",
                            "Phone", "PostalCode", "CompanyName", "FirstName", "LastName", "Email", "LegalInvoice",
                            "TradeRegistrationNumber", "VATID", "VATPercent", "VATSite"]:
                    try:
                        itemDict[key] = flat_item[key]
                    except KeyError:
                        itemDict[key] = ""
                # making sure the Value is from the Current price and not from StartPrice
                itemDict["Value"] = item["CurrentPrice"]["Value"]
                itemDict["CurrencyID"] = item["CurrentPrice"]["CurrencyID"]
                itemDict["UserID"] = item["Seller"]["UserID"]
#                 itemDict["Item_id"] = item["ItemID"]
#                 itemDict["ListingStatus"] = item["ListingStatus"]
#                 itemDict["Location"] = item["Location"]
#                 itemDict["Quantity"] = item["Quantity"]
#                 itemDict["Quantity_sold"] = item["QuantitySold"]
#                 itemDict["Price"] = item["CurrentPrice"]["Value"]
#                 itemDict["Currency"] = item["CurrentPrice"]["CurrencyID"]
#                 itemDict["Title"] = item["Title"]
#                 itemDict["PictureURL"] = ', '.join(item["PictureURL"])
#                 itemDict["OriginalURL"] = item["ViewItemURLForNaturalSearch"]
#                 itemDict["Sites"] = ', '.join(sitesByitem[ item["ItemID"] ])
#                 itemDict["GlobalShipping"] = str(item["GlobalShipping"])
#                 itemDict["ShipToLocations"] = ', '.join(item["ShipToLocations"])
#                 for key in ["Name", "Street1", "Street2", "CityName", "StateOrProvince", "CountryName",
#                              "Phone", "PostalCode", "CompanyName", "FirstName", "LastName"]:
#                     try:
#                         itemDict[key] = item["BusinessSellerDetails"]["Address"][key]
#                     except KeyError:
#                         itemDict[key] = ""
#                 for key in ["Email", "LegalInvoice", "TradeRegistrationNumber"]:
#                     try:
#                         itemDict[key] = item["BusinessSellerDetails"][key]
#                     except KeyError:
#                         itemDict[key] = ""
#                 for key in ["VATID", "VATPercent", "VATSite"]:
#                     try:
#                         itemDict[key] = item["BusinessSellerDetails"]["VATDetails"][key]
#                     except KeyError:
#                         itemDict[key] = ""

                itemsList.append(itemDict)
    
    print "GetMultipleItems API made %d calls" % nrOfCalls
            
    return itemsList


def get_seller_details(sellers_list):
    url_templ = "http://open.api.ebay.com/shopping?\
callname=GetUserProfile&\
responseencoding=JSON&\
appid=StefanoR-ebayFric-PRD-19f17700d-ff298548&\
version=967&\
IncludeSelector=FeedbackHistory&\
UserID={}"
    sellers_dict = {}
    for seller_id in sellers_list:
        url = url_templ.format(seller_id)
        r = requests.get(url)
        j = json.loads(r.text)
        flat_j = json_flat(j)
        sellers_dict[seller_id] = {}
        for key in ["FeedbackScore", "PositiveFeedbackPercent", "UniqueNegativeFeedbackCount",
                    "UniqueNeutralFeedbackCount", "UniquePositiveFeedbackCount"]:
            try:
                sellers_dict[seller_id][key] = flat_j[key]
            except KeyError:
                sellers_dict[seller_id][key] = ""
    
    return sellers_dict


def writeItemsToCsv(outputPath, sellerId, itemsList):
    
    # sanitizing sellerId to avoid issues with illegal file names
    sntzd_seller_id = re.sub('[^A-Za-z0-9-_]+', '', sellerId)
    
    filePath = outputPath + "/%s_eBayItems_%s.csv" % (sntzd_seller_id, time.strftime("%Y%m%d-%H%M%S"))
    fileToWrite = open(filePath, 'ab')
    fieldnames = itemsList[0].keys()
    csvWriter = csv.DictWriter(fileToWrite, fieldnames, restval='',
                               extrasaction='ignore', dialect='excel')
    csvWriter.writeheader()
    for item in itemsList:
        csvWriter.writerow({key : unicode(item[key]).encode("utf-8") for key in item.keys()})
        #csvWriter.writerow({key : item[key].encode("utf-8") for key in item.keys()})
    fileToWrite.close()


def main():
    print "Claudio sei un FRICO!!!"
    options = appDlg().mainloop()

    dictOfItems = getItemsFromSeller(options)
    print "found %d items" % len(dictOfItems.keys())
    itemsDesc = getNrOfSold(dictOfItems)
    
    # extract seller ids
    sellers_list = []
    for record in itemsDesc:
        if record["UserID"] not in sellers_list:
            sellers_list.append(record["UserID"])
    
    sellers_details = get_seller_details(sellers_list)
    
    # merge listings and seller details
    for item in itemsDesc:
        for key in ["FeedbackScore", "PositiveFeedbackPercent", "UniqueNegativeFeedbackCount",
                    "UniqueNeutralFeedbackCount", "UniquePositiveFeedbackCount"]:
            item[key] = sellers_details[item["UserID"]][key]
    
    if len(itemsDesc) > 0:
        if 'sellerId' in options.keys():
            writeItemsToCsv(options['outputFolder'], options['sellerId'], itemsDesc)
        else:
            writeItemsToCsv(options['outputFolder'], 'eBayAppSearch', itemsDesc)
        print "process completed"
        time.sleep(1)
    else:
        print "no items found"
        time.sleep(3)


if __name__ == "__main__":
    main()
    
##### TO DO #####
'''
Read error messages from calls reply
Log errors
Add Items Ended -- looks like it's not supported by eBay API
Implement check on nr of calls made and left
Implement country prioritization when same item listed on multiple sites (cases?)
Verify if same item appears multiple times in the same site search
Implement seller stats
Read error messages from calls reply
Implement status bar and text feedback.

'''

##### REFERENCES #####
'''
http://developer.ebay.com/Devzone/finding/Concepts/SiteIDToGlobalID.html
http://developer.ebay.com/Devzone/finding/Concepts/MakingACall.html
http://developer.ebay.com/Devzone/finding/CallRef/findItemsAdvanced.html
http://developer.ebay.com/DevZone/shopping/docs/CallRef/GetMultipleItems.html
http://developer.ebay.com/DevZone/XML/docs/Reference/eBay/GetApiAccessRules.html?rmvSB=true
'''