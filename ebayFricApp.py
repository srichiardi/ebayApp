import requests
import json
from urllib import urlencode


# items details retrieval
ebayShoppingUrl = "http://open.api.ebay.com/shopping?"
esPayload = { 'appid' : 'StefanoR-ebayFric-PRD-19f17700d-ff298548',
        'callname' : 'GetMultipleItems',
        'version' : '975',
        'responseencoding' : 'JSON',
        'ItemID' : ['182192210924','272276595883'],
        'IncludeSelector' : 'Details'}



def getItemsFromSeller(sellerId, resultsPerPage=100):
    ebayFindinghUrl = "http://svcs.ebay.co.uk/services/search/FindingService/v1?OPERATION-NAME=findItemsAdvanced&SERVICE-VERSION=1.13.0&SECURITY-APPNAME=StefanoR-ebayFric-PRD-19f17700d-ff298548&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD&"
    efPayload = { 'itemFilter(0).name' : 'Seller',
                 'itemFilter(0).value' : sellerId,
                 'paginationInput.entriesPerPage' : resultsPerPage,
                 'paginationInput.pageNumber' : 1 }
    
    url = ebayFindinghUrl + urlencode(efPayload)
    r = requests.get(url)
    j = json.loads(r.text)
    totResults = int(j['findItemsAdvancedResponse'][0]['paginationOutput'][0]['totalEntries'][0])
    totPages = int(j['findItemsAdvancedResponse'][0]['paginationOutput'][0]['totalPages'][0])
    pageNr = int(j['findItemsAdvancedResponse'][0]['paginationOutput'][0]['pageNumber'][0])
    
    if 'item' in j['findItemsAdvancedResponse'][0]['searchResult'][0].keys():
        itemsList = []
        for item in j['findItemsAdvancedResponse'][0]['searchResult'][0]['item']:
            itemsList.append(item['itemId'][0])
            
        while len(itemsList) < totResults:
            efPayload['paginationInput.pageNumber'] += 1
            url = ebayFindinghUrl + urlencode(efPayload)
            r = requests.get(url)
            j = json.loads(r.text)
            for item in j['findItemsAdvancedResponse'][0]['searchResult'][0]['item']:
                itemsList.append(item['itemId'][0])
    
