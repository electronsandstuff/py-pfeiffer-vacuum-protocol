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
        self.assertEqual(r, (1, 1, 0))

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
