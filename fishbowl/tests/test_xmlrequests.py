from __future__ import unicode_literals

from unittest import TestCase
from lxml import etree
from fishbowl.xmlrequests import Request


class TestRequest(Request):
    key_required = False


class XMLRequestsTest(TestCase):
    maxDiff = None

    def test_add_unicode(self):
        r = TestRequest()
        r.add_elements(r.el_request, [('test', '\u2022')])
        self.assertEqual(
            etree.tostring(r.el_request),
            b'<FbiMsgsRq><test>&#8226;</test></FbiMsgsRq>')
