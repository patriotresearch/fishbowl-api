from __future__ import unicode_literals
import os
from decimal import Decimal

from fishbowl import objects
from . import utils


class PartTest(utils.ObjectTest):
    xml_filename = os.path.join(os.path.dirname(__file__), 'part.xml')
    fishbowl_object = objects.Part
    expected = {
        'ActiveFlag': True,
        'Configurable': True,
        'Description': 'Custom Value Bike',
        'HasBOM': False,
        'Height': 0,
        'Len': 0,
        'Num': 'BB2005',
        'PartClassID': 0,
        'PartID': 60,
        'SerializedFlag': True,
        'StandardCost': Decimal(0),
        'TrackingFlag': True,
        'TypeID': 10,
        'Weight': 0,
        'Width': 0,
        'UOM': {
            'Active': True,
            'Code': 'ea',
            'Integral': True,
            'Name': 'Each',
            'Type': 'Count',
            'UOMID': 1,
        },
    }
