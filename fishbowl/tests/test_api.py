from __future__ import unicode_literals
from unittest import TestCase
from lxml import etree
import struct

from fishbowl import api, statuscodes

try:
    from unittest import mock
except ImportError:   # < Python 3.3
    import mock


LOGIN_SUCCESS = '''
<FbiXml>
<Key>ABC</Key>
<loginRs statusCode="{}"></loginRs>
</FbiXml>
'''.format(statuscodes.SUCCESS).encode('ascii')

LOGOUT_XML = '''
<FbiXml>
<Ticket><Key>ABC</Key></Ticket>
<FbiMsgsRs statusCode="1010"/>
</FbiXml>
'''

ADD_INVENTORY_XML = '''
<FbiXml>
<AddInventoryRs statusCode="{}"></AddInventoryRs>
</FbiXml>
'''.format(statuscodes.SUCCESS).encode('ascii')

ADD_INVENTORY_XML_FAIL = '''
<FbiXml>
<AddInventoryRs statusCode="{}"></AddInventoryRs>
</FbiXml>
'''.format('').encode('ascii')

CYCLE_INVENTORY_XML = '''
<FbiXml>
<CycleCountRs statusCode="{0}"></CycleCountRs>
</FbiXml>
'''.format(statuscodes.SUCCESS).encode('ascii')


class APIStreamTest(TestCase):

    @mock.patch('fishbowl.api.socket')
    def test_make_stream(self, mock_socket):
        api.Fishbowl().make_stream()
        self.assertTrue(mock_socket.socket.called)
        fake_socket = mock_socket.socket()
        self.assertTrue(fake_socket.connect)
        # Check default timeout set.
        fake_socket.settimeout.assert_called_with(5)


class APITest(TestCase):

    def setUp(self):
        self.api = api.Fishbowl()
        self.fake_stream = mock.MagicMock()
        # self.fake_stream.recv.return_value = '\0'
        self.api.make_stream = mock.Mock(return_value=self.fake_stream)

    def connect(self, login_return_value=LOGIN_SUCCESS, **kwargs):
        connect_kwargs = {'host': 'localhost', 'port': 28193}
        connect_kwargs.update(kwargs)
        self.api.send_message = mock.Mock(
            return_value=etree.fromstring(login_return_value))
        self.api.connect(
            username='test', password='password', **connect_kwargs)
        del self.api.send_message

    def test_connect(self):
        self.assertFalse(self.api.connected)
        self.connect()
        self.assertTrue(self.api.make_stream.called)
        self.assertTrue(self.api.connected)

        with mock.patch.object(self.api, 'send_message') as mock_message:
            mock_message.return_value = etree.fromstring(LOGOUT_XML)
            self.api.close()
        self.assertTrue(self.fake_stream.close.called)
        self.assertFalse(self.api.connected)

    def test_connect_bad_response(self):
        self.assertRaises(
            api.FishbowlError, self.connect,
            login_return_value=ADD_INVENTORY_XML)
        self.assertFalse(self.api.connected)

    def test_bad_close(self):
        self.connect()
        self.fake_stream.close.side_effect = ValueError()
        with mock.patch.object(self.api, 'send_message') as mock_message:
            mock_message.return_value = etree.fromstring(LOGOUT_XML)
            self.assertRaises(ValueError, self.api.close)
        self.assertFalse(self.api.connected)

    def test_bad_close_silent(self):
        self.connect()
        self.fake_stream.close.side_effect = ValueError()
        with mock.patch.object(self.api, 'send_message') as mock_message:
            mock_message.return_value = etree.fromstring(LOGOUT_XML)
            self.api.close(skip_errors=True)
        self.assertFalse(self.api.connected)

    def test_reconnect(self):
        self.assertFalse(self.api.connected)
        self.connect()
        self.assertTrue(self.api.make_stream.called)
        self.assertTrue(self.api.connected)

        self.assertFalse(self.fake_stream.close.called)
        self.api.make_stream.reset_mock()
        with mock.patch.object(self.api, 'close') as mock_close:
            self.connect()
            self.assertTrue(mock_close.called)
        self.assertTrue(self.api.make_stream.called)
        self.assertTrue(self.api.connected)

    def test_connect_custom_host(self):
        self.assertFalse(self.api.connected)
        self.connect(host='example.com', port='1234')
        self.assertTrue(self.api.connected)
        self.assertTrue(self.api.host, 'example.com')
        self.assertTrue(self.api.port, '1234')

    def test_required_connected_method(self):
        self.assertRaises(OSError, self.api.close)

    def set_response_xml(self, response_xml):
        self.fake_stream.recv.side_effect = [
            struct.pack('>L', len(response_xml))
        ] + list(response_xml)

    def test_send_message(self):
        self.connect()
        request_xml = b'<test></test>'
        response_xml = b'<FbiXml><FbiMsgsRq/></FbiXml>'
        self.set_response_xml(response_xml)
        self.fake_stream.recv.side_effect = [
            struct.pack('>L', len(response_xml))
        ] + list(response_xml)
        response = self.api.send_message(request_xml)
        self.assertEqual(etree.tostring(response), response_xml)
        self.fake_stream.send.assert_called_with(
            struct.pack('>L', len(request_xml)) + request_xml)

    def test_add_inventory(self):
        self.connect()
        self.set_response_xml(ADD_INVENTORY_XML)
        self.api.add_inventory(
            partnum=1, qty=1, uomid=1, cost=100, loctagnum=1)

    def test_add_inventory_fail(self):
        self.connect()
        self.set_response_xml(ADD_INVENTORY_XML_FAIL)
        self.assertRaises(
            api.FishbowlError, self.api.add_inventory,
            partnum=1, qty=1, uomid=1, cost=100, loctagnum=1)

    def test_cycle_inventory(self):
        self.connect()
        self.set_response_xml(CYCLE_INVENTORY_XML)
        self.api.cycle_inventory(partnum='abc', qty=2, locationid=1)
