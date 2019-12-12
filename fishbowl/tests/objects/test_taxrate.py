from __future__ import unicode_literals
import os
from decimal import Decimal

from fishbowl import objects
from . import utils


class TaxRateTest(utils.ObjectTest):
    xml_filename = os.path.join(os.path.dirname(__file__), "taxrate.xml")
    fishbowl_object = objects.TaxRate
    expected = {
        "ActiveFlag": True,
        "DefaultFlag": True,
        "ID": 2,
        "Name": "Tax",
        "Rate": Decimal("0.05"),
        "TypeID": 10,
        "VendorID": 6,
    }
