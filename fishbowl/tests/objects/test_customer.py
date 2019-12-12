from __future__ import unicode_literals
import os
from decimal import Decimal

from fishbowl import objects
from . import utils


class CustomerTest(utils.ObjectTest):
    xml_filename = os.path.join(os.path.dirname(__file__), "customer.xml")
    fishbowl_object = objects.Customer
    expected = {
        "ActiveFlag": True,
        "Addresses": [
            {
                "AddressInformationList": {
                    "AddressInformation": {
                        "Data": "Address Data",
                        "Default": True,
                        "Name": "Main Office",
                        "Type": "Home",
                    },
                },
                "Attn": "Attention",
                "City": "Murray",
                "Country": {"Code": "US", "Name": "United States"},
                "Default": True,
                "Name": "Main Office",
                "Residential": False,
                "State": {"Code": "UT", "CountryID": 2, "Name": "Utah"},
                "Street": "123 Neverland dr.",
                "Temp-Account": {"Type": 10},
                "Type": "Main Office",
                "Zip": "84121",
            }
        ],
        "CreditLimit": Decimal("1000000.00"),
        "CustomFields": [{"Info": "Custom Data", "Name": "Custom1", "Type": "CFT_TEXT",}],
        "DefPaymentTerms": "COD",
        "DefShipTerms": "Prepaid",
        "DefaultCarrier": "USPS",
        "DefaultSalesman": "jen",
        "JobDepth": 1,
        "Name": "Sam Ball",
        "Note": "Hello World",
        "Status": "Normal",
        "TaxExempt": True,
        "TaxExemptNumber": "12345",
        "TaxRate": "None",
    }
