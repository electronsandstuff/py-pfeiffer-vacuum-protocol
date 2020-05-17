# pfeiffer_vacuum_protocol - Python interface to Pfeiffer vacuum gauges
# Copyright (C) 2020 Christopher M. Pierce (contact@chris-pierce.com)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU Lesser General Public
# License as published by the Free Software Foundation.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import unittest
import pfeiffer_vacuum_protocol.mock as mock

class TestSerial(unittest.TestCase):
    pass

class TesPPT100(unittest.TestCase):
    def test_no_cr(self):
        g = mock.PPT100()
        r = g.get_response(b"0010074002=?106")
        self.assertTrue(r == None)

    def test_no_def(self):
        g = mock.PPT100()
        r = g.get_response(b"0010073902=?114\r")
        self.assertTrue(r == b'0011073906NO_DEF198\r')

    def test_no_device(self):
        g = mock.PPT100()
        r = g.get_response(b"0020074002=?107\r")
        self.assertTrue(r == None)

    def test_bad_cs(self):
        g = mock.PPT100()
        r = g.get_response(b"0010074002=?107\r")
        self.assertTrue(r == None)

    def test_actual_err_none(self):
        g = mock.PPT100()
        r = g.get_response(b"0010030302=?101\r")
        self.assertTrue(r == b'0011030306000000014\r')

    def test_actual_err_trans(self):
        g = mock.PPT100(err_state=mock.DEFECTIVE_TRANSMITTER)
        r = g.get_response(b"0010030302=?101\r")
        self.assertTrue(r == b'0011030306Err001168\r')

    def test_actual_err_mem(self):
        g = mock.PPT100(err_state=mock.DEFECTIVE_MEMORY)
        r = g.get_response(b"0010030302=?101\r")
        self.assertTrue(r == b'0011030306Err002169\r')

    def test_software_vers(self):
        g = mock.PPT100()
        r = g.get_response(b"0010031202=?101\r")
        self.assertTrue(r == b'0011031206010100016\r' )

    def test_component_name(self):
        g = mock.PPT100()
        r = g.get_response(b"0010034902=?111\r")
        self.assertTrue(r == b'0011034906    A3236\r')

    def test_pressure_in(self):
        g = mock.PPT100()
        r = g.get_response(b"0010074002=?106\r")
        self.assertTrue(r == b'0011074006100023025\r' )

    def test_pressure_setpoint(self):
        g = mock.PPT100()
        r = g.get_response(b"0011074103001130\r")
        self.assertTrue(r == b'0011074103001130\r')
        r = g.get_response(b"0011074103000129\r")
        self.assertTrue(r == b'0011074103000129\r')

    def test_pressure_setpoint_range(self):
        g = mock.PPT100()
        r = g.get_response(b"0011074103002131\r")
        self.assertTrue(r == b'0011074106_RANGE192\r')
        r = g.get_response(b"0011074103003132\r")
        self.assertTrue(r == b'0011074106_RANGE192\r')
        r = g.get_response(b"0011074103011131\r")
        self.assertTrue(r == b'0011074106_RANGE192\r')
        r = g.get_response(b"0011074103101131\r")
        self.assertTrue(r == b'0011074106_RANGE192\r')

    def test_pirani_correction_write(self):
        g = mock.PPT100()
        r = g.get_response(b"0011074206000100022\r")
        self.assertTrue(r == b'0011074206000100022\r')

    def test_pirani_correction_read(self):
        g = mock.PPT100()
        r = g.get_response(b"0010074202=?108\r")
        self.assertTrue(r == b'0011074206000100022\r' )

    def test_wrong_datalen_read(self):
        g = mock.PPT100()
        r = g.get_response(b"0010074201=044\r")
        self.assertTrue(r == None)

    def test_wrong_datalen_write(self):
        g = mock.PPT100()
        r = g.get_response(b"0011074203100131\r")
        self.assertTrue(r == b'0011074206NO_DEF192\r' )

    def test_wrong_data_read(self):
        g = mock.PPT100()
        r = g.get_response(b"00100742021?096\r")
        self.assertTrue(r == None)
        r = g.get_response(b"0010074201=?107\r")
        self.assertTrue(r == None)

    def test_wrong_data_write(self):
        g = mock.PPT100()
        r = g.get_response(b"0011074206000133\r")
        self.assertTrue(r == None)

if __name__ == '__main__':
    unittest.main()
