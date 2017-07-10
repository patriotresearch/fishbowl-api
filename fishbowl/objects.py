from __future__ import unicode_literals
import copy
import collections
from collections import OrderedDict
import sys
import inspect
import datetime
import decimal

import six


def fishbowl_datetime(text):
    return datetime.strptime(text, '%Y-%m-%dT%H:%M:%S')


fishbowl_datetime.type = datetime.datetime


def fishbowl_boolean(text):
    if not text:
        return False
    if text.lower() in ('0', 'false', 'f'):
        return False
    return True


fishbowl_boolean.type = bool


def all_fishbowl_objects():
    return dict(inspect.getmembers(
        sys.modules[__name__],
        lambda member: (
            inspect.isclass(member) and member.__module__ == __name__)
    ))


@six.python_2_unicode_compatible
class FishbowlObject(collections.Mapping):
    id_field = None
    name_attr = None
    encoding = 'utf-8'

    def __init__(
            self, data=None, lazy_data=None, name=None, custom_fields=None):
        if not (data is None) ^ (lazy_data is None):
            raise AttributeError('Expected either data or lazy_data')
        self.name = name
        self.custom_fields = custom_fields
        self._lazy_load = lazy_data
        if data is not None:
            self.mapped = self.parse_fields(data)

    def __str__(self):
        if self.name:
            return self.name
        if not self.name_attr:
            return ''
        value = self
        for attr in self.name_attr.split('.'):
            value = value[attr]
        return value or ''

    def __bool__(self):
        return bool(self.mapped)

    __nonzero__ = __bool__

    @property
    def mapped(self):
        if not hasattr(self, '_mapped'):
            self._mapped = self.parse_fields(self._lazy_load())
        return self._mapped

    @mapped.setter
    def mapped(self, value):
        self._mapped = value

    def parse_fields(self, data, fields=None):
        if data is None:
            return {}
        if fields is None:
            fields = self.fields
            if self.custom_fields:
                fields = copy.deepcopy(fields)
                fields.update(self.custom_fields)
        if not isinstance(data, dict):
            data = self.get_xml_data(data)
        output = collections.OrderedDict()
        items = list(fields.items())
        if self.id_field and 'ID' not in fields:
            items.append(('ID', int))
        # Load the data in without case sensitivity.
        data_map = dict((k.lower(), k) for k in data)
        for field_name, parser in items:
            key = data_map.get(field_name.lower())
            value = data.get(key)
            if value is None:
                continue
            if isinstance(parser, dict):
                if not value:
                    continue
                if isinstance(value, list):
                    value = value[0]
                value = self.parse_fields(value, parser)
            elif isinstance(parser, list):
                new_value = []
                if parser:
                    classes = dict((cls.__name__, cls) for cls in parser)
                else:
                    classes = all_fishbowl_objects()
                if not isinstance(value, list):
                    value = [value]
                for value_item in value:
                    for tag, child in value_item.items():
                        child_parser = classes.get(tag)
                        if not child_parser:
                            continue
                        new_value.append(child_parser(child))
                value = new_value
            elif isinstance(parser, FishbowlObject):
                value = parser(data)
            else:
                if parser:
                    try:
                        value = parser(value)
                    except Exception:
                        continue
            output[field_name] = value
        if self.id_field and self.id_field not in output:
            value = output.pop('ID', None)
            if value:
                output[self.id_field] = value
        return output

    def get_xml_data(self, base_el):
        data = collections.OrderedDict()
        for child in base_el:
            children = len(child)
            key = child.tag
            if six.PY2:
                key = key.encode(self.encoding)
            if children:
                if [el for el in child if el.text.strip()]:
                    data[key] = self.get_xml_data(child)
                else:
                    inner = []
                    for el in child:
                        inner_key = el.tag
                        if six.PY2:
                            inner_key = inner_key.encode(self.encoding)
                        inner.append({inner_key: self.get_xml_data(el)})
                    data[key] = inner
            else:
                value = child.text
                if value is not None and six.PY2:
                    value = value.encode(self.encoding)
                data[key] = value
        return data

    def __getitem__(self, key):
        return self.mapped[key]

    def __setitem__(self, key, value):
        if key not in self.fields:
            raise KeyError('No field named {}'.format(key))
        expected_type = self.fields[key]
        expected_type = getattr(expected_type, 'type', expected_type)
        if expected_type is None:
            expected_type = six.text_type
        if not isinstance(value, expected_type):
            raise ValueError('Value was not type {}'.format(expected_type))
        self.mapped[key] = value

    def __iter__(self):
        return iter(self.mapped)

    def __len__(self):
        return len(self.mapped)

    def squash(self):
        return self.squash_obj(self.mapped)

    def squash_obj(self, obj):
        if isinstance(obj, dict):
            return dict(
                (key, self.squash_obj(value)) for key, value in obj.items())
        if isinstance(obj, list):
            return [self.squash_obj(value) for value in obj]
        if isinstance(obj, FishbowlObject):
            return obj.squash()
        return obj


class CustomListItem(FishbowlObject):
    fields = collections.OrderedDict([
        ('ID', int),
        ('Name', None),
        ('Description', None),
    ])


class CustomList(FishbowlObject):
    fields = OrderedDict([
        ('ID', int),
        ('Name', None),
        ('Description', None),
        ('CustomListItems', [CustomListItem]),
    ])


class CustomField(FishbowlObject):
    fields = collections.OrderedDict([
        ('ID', int),
        ('Type', None),
        ('Name', None),
        ('Description', None),
        ('SortOrder', int),
        ('Info', None),
        ('RequiredFlag', fishbowl_boolean),
        ('ActiveFlag', fishbowl_boolean),
        ('CustomList', CustomList),
    ])


class State(FishbowlObject):
    fields = OrderedDict([
        ('ID', int),
        ('Code', None),
        ('Name', None),
        ('CountryID', int),
    ])


class Country(FishbowlObject):
    fields = OrderedDict([
        ('ID', int),
        ('Name', None),
        ('Code', None),
    ])


class Address(FishbowlObject):
    fields = OrderedDict([
        ('ID', int),
        ('Temp-Account', OrderedDict([
            ('ID', int),
            ('Type', int),
        ])),
        ('Name', None),
        ('Attn', None),
        ('Street', None),
        ('City', None),
        ('Zip', None),
        ('LocationGroupID', int),
        ('Default', fishbowl_boolean),
        ('Residential', fishbowl_boolean),
        ('Type', None),
        ('State', State),
        ('Country', Country),
        ('AddressInformationList', OrderedDict([
            ('AddressInformation', OrderedDict([
                ('ID', int),
                ('Name', None),
                ('Data', None),
                ('Default', fishbowl_boolean),
                ('Type', None),
            ])),
        ])),
    ])


class Customer(FishbowlObject):
    id_field = 'CustomerID'
    fields = OrderedDict([
        ('CustomerID', int),
        ('AccountID', int),
        ('Status', None),
        ('DefPaymentTerms', None),
        ('DefShipTerms', None),
        ('TaxRate', None),
        ('Name', None),
        ('Number', None),
        ('DateCreated', fishbowl_datetime),
        ('DateLastModified', fishbowl_datetime),
        ('LastChangedUser', None),
        ('CreditLimit', decimal.Decimal),
        ('TaxExempt', fishbowl_boolean),
        ('TaxExemptNumber', None),
        ('Note', None),
        ('ActiveFlag', fishbowl_boolean),
        ('AccountingID', None),
        ('CurrencyName', None),
        ('CurrencyRate', int),  # was double
        ('DefaultSalesman', None),
        ('DefaultCarrier', None),
        ('DefaultShipService', None),
        ('JobDepth', int),
        ('QuickBooksClassName', None),
        ('ParentID', int),
        ('PipelineAccount', int),
        ('URL', None),
        ('Addresses', [Address]),
        ('CustomFields', [CustomField]),
    ])


class UOM(FishbowlObject):
    fields = OrderedDict([
        ('UOMID', int),
        ('Name', None),
        ('Code', None),
        ('Integral', fishbowl_boolean),
        ('Active', fishbowl_boolean),
        ('Type', None),
    ])


class LocationGroup(FishbowlObject):
    fields = OrderedDict([
        ('ID', int),
        ('Name', None),
        ('ActiveFlag', fishbowl_boolean),
    ])


class Part(FishbowlObject):
    id_field = 'PartID'
    fields = OrderedDict([
        ('PartID', int),
        ('PartClassID', int),
        ('TypeID', int),
        ('UOM', UOM),
        ('UOMID', int),   # Used for light parts
        ('Num', None),
        ('Description', None),
        ('Manufacturer', None),
        ('Details', None),
        ('TagLabel', None),
        ('StandardCost', decimal.Decimal),
        ('HasBOM', fishbowl_boolean),
        ('Configurable', fishbowl_boolean),
        ('ActiveFlag', fishbowl_boolean),
        ('SerializedFlag', fishbowl_boolean),
        ('TrackingFlag', fishbowl_boolean),
        ('UsedFlag', fishbowl_boolean),
        ('Weight', int),
        ('WeightUOMID', int),
        ('Width', int),
        ('Height', int),
        ('Len', int),
        ('SizeUOMID', int),
        ('CustomFields', [CustomField]),
        ('VendorPartNums', None),
    ])


class Product(FishbowlObject):
    fields = OrderedDict([
        ('ID', int),
        ('PartID', int),
        ('Part', Part),
        ('Num', None),
        ('Description', None),
        ('Price', decimal.Decimal),
        ('UOM', UOM),
        ('DefaultSOItemType', None),
        ('DisplayType', None),
        ('Weight', int),
        ('WeightUOMID', int),
        ('Width', int),
        ('Height', int),
        ('Len', int),
        ('SizeUOMID', int),
        ('SellableInOtherUOMFlag', fishbowl_boolean),
        ('ActiveFlag', fishbowl_boolean),
        ('TaxableFlag', fishbowl_boolean),
        ('UsePriceFlag', fishbowl_boolean),
        ('KitFlag', fishbowl_boolean),
        ('ShowSOComboFlag', fishbowl_boolean),
        ('Image', None),
    ])


class SalesOrderItem(FishbowlObject):
    fields = OrderedDict([
        ('ID', int),
        ('ProductNumber', None),
        ('SOID', int),
        ('Description', None),
        ('CustomerPartNum', None),
        ('Taxable', fishbowl_boolean),
        ('Quantity', int),
        ('ProductPrice', int),
        ('TotalPrice', int),
        ('UOMCode', None),
        ('ItemType', int),
        ('Status', int),
        ('QuickBooksClassName', None),
        ('NewItemFlag', fishbowl_boolean),
        ('LineNumber', int),
        ('KitItemFlag', fishbowl_boolean),
        ('ShowItemFlag', fishbowl_boolean),
        ('AdjustmentAmount', decimal.Decimal),
        ('AdjustPercentage', int),
        ('DateLastFulfillment', fishbowl_datetime),
        ('DateLastModified', fishbowl_datetime),
        ('DateScheduledFulfillment', fishbowl_datetime),
        ('ExchangeSOLineItem', int),
        ('ItemAdjustID', int),
        ('QtyFulfilled', int),
        ('QtyPicked', int),
        ('RevisionLevel', int),
        ('TotalCost', decimal.Decimal),
        ('TaxableFlag', fishbowl_boolean),
    ])


class Memo(FishbowlObject):
    fields = OrderedDict([
        ('ID', int),
        ('Memo', None),
        ('UserName', None),
        ('DateCreated', fishbowl_datetime),
    ])


class SalesOrder(FishbowlObject):
    fields = OrderedDict([
        ('ID', int),
        ('Note', None),
        ('TotalPrice', decimal.Decimal),
        ('TotalTax', decimal.Decimal),
        ('PaymentTotal', decimal.Decimal),
        ('ItemTotal', decimal.Decimal),
        ('Salesman', None),
        ('Number', None),
        ('Status', int),
        ('Carrier', None),
        ('FirstShipDate', fishbowl_datetime),
        ('CreatedDate', fishbowl_datetime),
        ('IssuedDate', fishbowl_datetime),
        ('TaxRatePercentage', decimal.Decimal),
        ('TaxRateName', None),
        ('ShippingCost', decimal.Decimal),
        ('ShippingTerms', None),
        ('PaymentTerms', None),
        ('CustomerContact', None),
        ('CustomerName', None),
        ('CustomerID', int),
        ('FOB', None),
        ('QuickBooksClassName', None),
        ('LocationGroup', None),
        ('PriorityId', int),
        ('CurrencyRate', decimal.Decimal),
        ('CurrencyName', None),
        ('PriceIsInHomeCurrency', fishbowl_boolean),
        ('BillTo', OrderedDict([
            ('Name', None),
            ('AddressField', None),
            ('City', None),
            ('Zip', None),
            ('Country', None),
            ('State', None),
        ])),
        ('Ship', OrderedDict([
            ('Name', None),
            ('AddressField', None),
            ('City', None),
            ('Zip', None),
            ('Country', None),
            ('State', None),
        ])),
        ('IssueFlag', fishbowl_boolean),
        ('VendorPO', None),
        ('CustomerPO', None),
        ('UPSServiceID', int),
        ('TotalIncludesTax', fishbowl_boolean),
        ('TypeID', int),
        ('URL', None),
        ('Cost', decimal.Decimal),
        ('DateCompleted', fishbowl_datetime),
        ('DateLastModified', fishbowl_datetime),
        ('DateRevision', fishbowl_datetime),
        ('RegisterID', int),
        ('ResidentialFlag', fishbowl_boolean),
        ('SalesmanInitials', None),
        ('CustomFields', [CustomField]),
        ('Memos', [Memo]),
        ('Items', [SalesOrderItem]),
    ])


class TaxRate(FishbowlObject):
    fields = OrderedDict([
        ('ID', int),
        ('Name', None),
        ('Description', None),
        ('Rate', decimal.Decimal),
        ('TypeID', int),
        ('VendorID', int),
        ('DefaultFlag', fishbowl_boolean),
        ('ActiveFlag', fishbowl_boolean),
    ])
