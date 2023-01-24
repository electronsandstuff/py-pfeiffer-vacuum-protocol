import unittest
import pfeiffer_vacuum_protocol.mock as mock
import pfeiffer_vacuum_protocol as pvp


# Suggested from https://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class
class BaseTestCases:
    class TestCommon(unittest.TestCase):
        def setUp(self) -> None:
            self.nonascii = False
            self.ascii_filter = None

        def test_read_error_code(self):
            s = mock.Serial(mock.PPT100(nonascii=self.nonascii), "COM1")
            r = pvp.read_error_code(s, 1, valid_char_filter=self.ascii_filter)
            self.assertEqual(r, pvp.ErrorCode.NO_ERROR)

            s = mock.Serial(mock.PPT100(err_state=pvp.ErrorCode.DEFECTIVE_TRANSMITTER, nonascii=self.nonascii), "COM1")
            r = pvp.read_error_code(s, 1, valid_char_filter=self.ascii_filter)
            self.assertEqual(r, pvp.ErrorCode.DEFECTIVE_TRANSMITTER)

            s = mock.Serial(mock.PPT100(err_state=pvp.ErrorCode.DEFECTIVE_MEMORY, nonascii=self.nonascii), "COM1")
            r = pvp.read_error_code(s, 1, valid_char_filter=self.ascii_filter)
            self.assertEqual(r, pvp.ErrorCode.DEFECTIVE_MEMORY)

        def test_read_software_version(self):
            s = mock.Serial(mock.PPT100(nonascii=self.nonascii), "COM1")
            r = pvp.read_software_version(s, 1, valid_char_filter=self.ascii_filter)
            self.assertEqual(r, (1, 1, 0))

        def test_read_gauge_type(self):
            s = mock.Serial(mock.PPT100(nonascii=self.nonascii), "COM1")
            r = pvp.read_gauge_type(s, 1, valid_char_filter=self.ascii_filter)
            self.assertEqual(r, "PPT 100")

        def test_read_pressure(self):
            s = mock.Serial(mock.PPT100(nonascii=self.nonascii), "COM1")
            r = pvp.read_pressure(s, 1, valid_char_filter=self.ascii_filter)
            self.assertEqual(r, 1.0)

        def test_write_pressure_setpoint(self):
            s = mock.Serial(mock.PPT100(nonascii=self.nonascii), "COM1")
            pvp.write_pressure_setpoint(s, 1, 0, valid_char_filter=self.ascii_filter)
            pvp.write_pressure_setpoint(s, 1, 1, valid_char_filter=self.ascii_filter)
            with self.assertRaises(ValueError) as context:
                pvp.write_pressure_setpoint(s, 1, 2, valid_char_filter=self.ascii_filter)

        def test_read_correction_value(self):
            s = mock.Serial(mock.PPT100(nonascii=self.nonascii), "COM1")
            r = pvp.read_correction_value(s, 1, valid_char_filter=self.ascii_filter)
            self.assertEqual(r, 1.0)

        def test_write_correction_value(self):
            s = mock.Serial(mock.PPT100(nonascii=self.nonascii), "COM1")
            pvp.write_correction_value(s, 1, 1.0, valid_char_filter=self.ascii_filter)


# Tests on typical devices
class TestVanilla(BaseTestCases.TestCommon):
    def setUp(self) -> None:
        self.nonascii = False
        self.ascii_filter = None
        pvp.disable_valid_char_filter()


# Tests with nonascii chars added before message (github issue 1)
class TestNonAscii(BaseTestCases.TestCommon):
    def setUp(self) -> None:
        self.nonascii = True
        self.ascii_filter = None
        pvp.enable_valid_char_filter()


# Use function override to solve issues
class TestNonAsciiFnOverride(BaseTestCases.TestCommon):
    def setUp(self) -> None:
        self.nonascii = True
        self.ascii_filter = True
        pvp.disable_valid_char_filter()


# Confirm errors are handled correctly
class NonAsciiErrorChecks(unittest.TestCase):
    def test_read_pressure(self):
        pvp.enable_valid_char_filter()
        s = mock.Serial(mock.PPT100(nonascii=True), "COM1")
        self.assertEqual(pvp.read_pressure(s, 1, valid_char_filter=None), 1.0)

        pvp.disable_valid_char_filter()
        with self.assertRaises(pvp.InvalidCharError):
            r = pvp.read_pressure(s, 1, valid_char_filter=None)

        self.assertEqual(pvp.read_pressure(s, 1, valid_char_filter=True), 1.0)

        pvp.enable_valid_char_filter()
        with self.assertRaises(pvp.InvalidCharError):
            r = pvp.read_pressure(s, 1, valid_char_filter=False)


if __name__ == '__main__':
    unittest.main()
