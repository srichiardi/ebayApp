import requests
import json
from urllib import urlencode

# active listing search payload
ebayFindinghUrl = "http://svcs.ebay.co.uk/services/search/FindingService/v1?OPERATION-NAME=findItemsAdvanced&SERVICE-VERSION=1.13.0&SECURITY-APPNAME=StefanoR-ebayFric-PRD-19f17700d-ff298548&RESPONSE-DATA-FORMAT=JSON&REST-PAYLOAD&"
efPayload = { 'itemFilter(0).name' : 'Seller',
             'itemFilter(0).value' : 'al-rawda',
             'paginationInput.entriesPerPage' : '2' }


# items details retrieval
ebayShoppingUrl = "http://open.api.ebay.com/shopping?"
esPayload = { 'appid' : 'StefanoR-ebayFric-PRD-19f17700d-ff298548',
        'callname' : 'GetMultipleItems',
        'version' : '975',
        'responseencoding' : 'JSON',
        'ItemID' : ['182192210924','272276595883'],
        'IncludeSelector' : 'Details'}



getData = urlencode(payload)
url = ebaySearch + getData

r = requests.get(url)
j = json.loads(r.text)