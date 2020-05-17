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
import pfeiffer_vacuum_protocol as pvp

class TestPVP(unittest.TestCase):
    def test_read_error_code(self):
        s = mock.Serial(mock.PPT100(), "COM1")
        r = pvp.read_error_code(s, 1)
        self.assertEqual(r, pvp.ErrorCode.NO_ERROR)
        s = mock.Serial(mock.PPT100(err_state=pvp.ErrorCode.DEFECTIVE_TRANSMITTER), "COM1")
        r = pvp.read_error_code(s, 1)
        self.assertEqual(r, pvp.ErrorCode.DEFECTIVE_TRANSMITTER)
        s = mock.Serial(mock.PPT100(err_state=pvp.ErrorCode.DEFECTIVE_MEMORY), "COM1")
        r = pvp.read_error_code(s, 1)
        self.assertEqual(r, pvp.ErrorCode.DEFECTIVE_MEMORY)

    def test_read_software_version(self):
        s = mock.Serial(mock.PPT100(), "COM1")
        r = pvp.read_software_version(s, 1)
        self.assertEqual(r, (1,1,0))

    def test_read_gauge_type(self):
        s = mock.Serial(mock.PPT100(), "COM1")
        r = pvp.read_gauge_type(s, 1)
        self.assertEqual(r, "PPT 100")

    def test_read_pressure(self):
        s = mock.Serial(mock.PPT100(), "COM1")
        r = pvp.read_pressure(s, 1)
        self.assertEqual(r, 1.0)

    def test_write_pressure_setpoint(self):
        s = mock.Serial(mock.PPT100(), "COM1")
        pvp.write_pressure_setpoint(s, 1, 0)
        pvp.write_pressure_setpoint(s, 1, 1)
        with self.assertRaises(ValueError) as context:
            pvp.write_pressure_setpoint(s, 1, 2)

    def test_read_correction_value(self):
        s = mock.Serial(mock.PPT100(), "COM1")
        r = pvp.read_correction_value(s, 1)
        self.assertEqual(r, 1.0)

    def test_write_correction_value(self):
        s = mock.Serial(mock.PPT100(), "COM1")
        pvp.write_correction_value(s, 1, 1.0)

if __name__ == '__main__':
    unittest.main()
