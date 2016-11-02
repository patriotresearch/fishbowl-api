from __future__ import unicode_literals

import datetime
from lxml import etree
from collections import OrderedDict

import six


class Request(object):
    key_required = True

    def __init__(self, key=''):
        if self.key_required and not key:
            raise TypeError(
                "An API key was not provided (not enough arguments for {0} "
                "request)".format(self.__class__.__name__))
        self.el_root = etree.Element('FbiXml')
        el_ticket = etree.SubElement(self.el_root, 'Ticket')
        el_key = etree.SubElement(el_ticket, 'Key')
        el_key.text = key
        self.el_request = etree.SubElement(self.el_root, 'FbiMsgsRq')

    @property
    def request(self):
        return etree.tostring(self.el_root, pretty_print=True)

    def add_elements(self, parent, elements):
        if isinstance(elements, dict):
            elements = elements.items()
        for name, value in elements:
            el = etree.SubElement(parent, name)
            if value is not None:
                if isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%dT%H:%M:%S")
                else:
                    value = '%s' % value
                el.text = value

    def add_request_element(self, name):
        return etree.SubElement(self.el_request, name)

    def add_data(self, name, data):
        """
        Generate a request from a data dictionary.

        To create a node hierarchy, the values can be dicts or lists (which
        must contain dicts). For example::

            .add_data(
                'root-name',
                data={
                    'outer': {'inner': 0},
                    'items': [{'item': 1}, {'item': 2}],
                })

            <FbiXml>
              <Ticket>
                <Key>eCWMhC5n/E48OP7307qmZg==</Key>
              </Ticket>
              <FbiMsgsRq>
                <root-name>
                  <outer>
                    <inner>0</inner>
                  </outer>
                  <items>
                    <item>1</item>
                    <item>2</item>
                  </items>
                </root-name>
              </FbiMsgsRq>
            </FbiXml

        """
        self._add_data(self.el_request, {name: data})

    def _add_data(self, el, data):
        for k, v in six.iteritems(data):
            child = etree.SubElement(el, k)
            if isinstance(v, (tuple, list)):
                for inner_data in v:
                    self._add_data(child, inner_data)
                continue
            if isinstance(v, dict):
                self._add_data(child, v)
                continue
            v = self.format_data_value(v)
            child.text = self.format_data_value(v)

    def format_data_value(self, value):
        """
        Returns a data value formatted as text.
        """
        if isinstance(value, bool):
            value = 'true' if value else 'false'
        elif isinstance(value, datetime.datetime):
            value = value.strftime('%Y-%m-%dT%H:%M:%S')
        return '%s' % value


class Login(Request):
    key_required = False

    def __init__(self, username, password, key=''):
        Request.__init__(self, key)
        el_rq = self.add_request_element('LoginRq')
        self.add_elements(el_rq, {
            'IAID': '22',
            'IAName': 'PythonApp',
            'IADescription': 'Connection for Python Wrapper',
            'UserName': username,
            'UserPassword': password,
        })


class SimpleRequest(Request):

    def __init__(self, request_name, value=None, key=''):
        Request.__init__(self, key)
        el = self.add_request_element(request_name)
        if value is not None:
            if isinstance(value, dict):
                self.add_elements(el, value)
            else:
                el.text = str(value)


class ImportRequest(Request):

    def __init__(self, request_type, value=None, key=''):
        Request.__init__(self, key)
        el = self.add_request_element('ImportRq')
        self.add_elements(el, [('Type', request_type)])
        self.el_rows = etree.SubElement(el, 'Rows')
        if value:
            self.add_rows(value)

    def add_row(self, row):
        self.add_rows([row])

    def add_rows(self, rows):
        self.add_elements(self.el_rows, [('Row', row) for row in rows])


class AddInventory(Request):

    def __init__(
            self, partnum, qty, uomid, cost, loctagnum, note='', tracking='',
            key=''):
        Request.__init__(self, key)
        el_rq = self.add_request_element('AddInventoryRq')
        self.add_elements(el_rq, {
            'PartNum': partnum,
            'Quantity': qty,
            'UOMID': uomid,
            'Cost': cost,
            'Note': note,
            'Tracking': tracking,
            'LocationTagNum': loctagnum,
            'TagNum': '0',
        })


class CycleCount(Request):

    def __init__(self, partnum, qty, locationid, tracking='', key=''):
        Request.__init__(self, key)
        el_rq = self.add_request_element('CycleCountRq')
        self.add_elements(el_rq, {
            'PartNum': partnum,
            'Quantity': qty,
            'LocationID': locationid,
        })


class GetPOList(Request):

    def __init__(self, locationgroup=None, key=''):
        Request.__init__(self, key)
        el_rq = self.add_request_element('GetPOListRq')
        if locationgroup is not None:
            self.add_elements(el_rq, {
                'LocationGroup': locationgroup,
            })


class AddMemo(Request):
    item_types = (
        'Part', 'Product', 'Customer', 'Vendor', 'SO', 'PO', 'TO', 'MO',
        'RMA', 'BOM')

    def __init__(self, item_type, item_num, memo, username='', key=''):
        Request.__init__(self, key)
        if item_type not in self.item_types:
            raise TypeError(
                "{} is not a valid memo item type".format(item_type))
        # Use the correct node name for the item number type (falling back to
        # OrderNum for everything else).
        if item_type in ('Part', 'Product', 'Customer', 'Vendor'):
            num_attr = '{}Num'.format(item_type)
        else:
            num_attr = 'OrderNum'
        self.add_data('AddMemoRq', OrderedDict([
            ('ItemType', item_type),
            (num_attr, item_num),
            ('Memo', OrderedDict([
                ('Memo', memo),
                ('UserName', username),
            ])),
        ]))
