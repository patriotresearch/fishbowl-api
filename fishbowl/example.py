"""
Example use of api.

Create a fishbowl.ini file in this project root that looks something like
this::

    [connect]
    host = 192.168.1.10
    port = 28192
    timeout = 6000
    username = someuser
    password = somepassword

Then run::

    python fishbowl/__init__.py
"""

import collections
import datetime
import json
import logging
import os
import sys

from lxml import etree

from fishbowl.api import FishbowlAPI, FishbowlJSONAPI

try:
    import configparser
except ImportError:  # Python 2
    import ConfigParser as configparser

FILENAME = os.path.join(os.path.dirname(__file__), "fishbowl.ini")


def run():
    config = configparser.ConfigParser()
    config.read(FILENAME)
    connect_options = dict((key, config.get("connect", key)) for key in config.options("connect"))

    logging.basicConfig(
        filename="fishbowl.log",
        level=logging.DEBUG,
        format="[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - " "%(message)s",
        datefmt="%H:%M:%S",
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # # set a format which is simpler for console use
    # formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger("").addHandler(console)

    with FishbowlAPI(**connect_options) as fishbowl:
        if len(sys.argv) > 1:
            value = None
            if len(sys.argv) > 2:
                value = json.loads(sys.argv[2], object_pairs_hook=collections.OrderedDict)
            response = fishbowl.send_request(sys.argv[1], value)
            return etree.tostring(response).decode("utf-8")

        # parts = fishbowl.get_parts_all()
        # print(parts)

        # serial = fishbowl.get_serial_numbers()
        # print(serial)

        # fishbowl.send_request(
        #     'GetSOListRq',
        #     {
        #         'DateCreatedEnd': datetime.datetime(1900, 1, 1),
        #     }
        # )
        # fishbowl.send_request('GetPartListRq')
        # with open('LightPartListRq.xml', 'w') as f:
        #     f.write(etree.tostring(fishbowl.send_request('LightPartListRq')))
        # response = fishbowl.send_request('GetShipListRq')

        # products = fishbowl.get_products()
        # customers = fishbowl.get_customers_fast(
        #     populate_pricing_rules=False, populate_addresses=False
        # )
        # rules = fishbowl.get_pricing_rules()
        # import ipdb; ipdb.set_trace()

        # response = fishbowl.send_request("CustomerNameListRq")
        # return etree.tostring(response)

        # imports = fishbowl.get_available_imports()

        # # data = fishbowl.get_import_headers("ImportSalesOrder")

        # print(data)

        # headers = data.split(,)

        # print(headers)

        data = [
            # "Flag,SONum,Status,CustomerName,CustomerContact,BillToName,BillToAddress,BillToCity,BillToState,BillToZip,BillToCountry,ShipToName,ShipToAddress,ShipToCity,ShipToState,ShipToZip,ShipToCountry,ShipToResidential,CarrierName,TaxRateName,PriorityId,PONum,VendorPONum,Date,Salesman,ShippingTerms,PaymentTerms,FOB,Note,QuickBooksClassName,LocationGroupName,OrderDateScheduled,URL,CarrierService,DateExpired,Phone,Email,CF-Well Name",
            "SO,123TESTAPI,10,bh oil,,Joe,123 Place,Odessa,TX,79762,United States,Joe,123 Place,Odessa,TX,79762,United States,false,UPS,TEXAS,,,,,,,,,,,,,,,,,,",
            "Item,10,200018,,1,ea,20000,,,,,,,,,,",
        ]

        fishbowl.run_import("ImportSalesOrder", data)


if __name__ == "__main__":
    run()
