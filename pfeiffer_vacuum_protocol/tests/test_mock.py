import unittest
import pfeiffer_vacuum_protocol.mock as mock
from pfeiffer_vacuum_protocol import ErrorCode
import io


class TestSerial(unittest.TestCase):
    def test_write(self):
        s = mock.Serial(mock.PPT100(), "COM1")
        r = s.write(b"test")
        self.assertEqual(r, 4)

    def test_wrong_type(self):
        s = mock.Serial(mock.PPT100(), "COM1")
        with self.assertRaises(TypeError):
            s.write("blah blah blah")

    def test_read(self):
        s = mock.Serial(mock.PPT100(), "COM1")
        s.write(b"0010073902=?114\r")
        r = s.read(1)
        self.assertEqual(r, b"0")

    def test_io_readline(self):
        s = mock.Serial(mock.PPT100(), "COM1")
        sio = io.TextIOWrapper(io.BufferedRWPair(s, s), newline="\r")
        sio.write("0010073902=?114\r")
        sio.flush()
        r = sio.readline()
        self.assertEqual(r, "0011073906NO_DEF198\r")

    def test_wrong_baudrate(self):
        s = mock.Serial(mock.PPT100(), "COM1", 19200)
        s.write(b"0010073902=?114\r")
        r = s.read(1)
        self.assertEqual(r, b"")

    def test_flush(self):
        s = mock.Serial(mock.PPT100(), "COM1")
        s.flush()


class TestPPT100(unittest.TestCase):
    def test_nonascii(self):
        g = mock.PPT100(nonascii=True)
        r = g.get_response(b"0010030302=?101\r")
        self.assertEqual(r[:40], b'\xff'*40)

    def test_no_cr(self):
        g = mock.PPT100()
        r = g.get_response(b"0010074002=?106")
        self.assertEqual(r, b"")

    def test_no_def(self):
        g = mock.PPT100()
        r = g.get_response(b"0010073902=?114\r")
        self.assertEqual(r, b'0011073906NO_DEF198\r')

    def test_no_device(self):
        g = mock.PPT100()
        r = g.get_response(b"0020074002=?107\r")
        self.assertEqual(r, b"")

    def test_bad_cs(self):
        g = mock.PPT100()
        r = g.get_response(b"0010074002=?107\r")
        self.assertEqual(r, b"")

    def test_actual_err_none(self):
        g = mock.PPT100()
        r = g.get_response(b"0010030302=?101\r")
        self.assertEqual(r, b'0011030306000000014\r')

    def test_actual_err_trans(self):
        g = mock.PPT100(err_state=ErrorCode.DEFECTIVE_TRANSMITTER)
        r = g.get_response(b"0010030302=?101\r")
        self.assertEqual(r, b'0011030306Err001168\r')

    def test_actual_err_mem(self):
        g = mock.PPT100(err_state=ErrorCode.DEFECTIVE_MEMORY)
        r = g.get_response(b"0010030302=?101\r")
        self.assertEqual(r, b'0011030306Err002169\r')

    def test_software_vers(self):
        g = mock.PPT100()
        r = g.get_response(b"0010031202=?101\r")
        self.assertEqual(r, b'0011031206010100016\r')

    def test_component_name(self):
        g = mock.PPT100()
        r = g.get_response(b"0010034902=?111\r")
        self.assertEqual(r, b'0011034906    A3236\r')

    def test_pressure_in(self):
        g = mock.PPT100()
        r = g.get_response(b"0010074002=?106\r")
        self.assertEqual(r, b'0011074006100023025\r')

    def test_pressure_setpoint(self):
        g = mock.PPT100()
        r = g.get_response(b"0011074103001130\r")
        self.assertEqual(r, b'0011074103001130\r')
        r = g.get_response(b"0011074103000129\r")
        self.assertEqual(r, b'0011074103000129\r')

    def test_pressure_setpoint_range(self):
        g = mock.PPT100()
        r = g.get_response(b"0011074103002131\r")
        self.assertEqual(r, b'0011074106_RANGE192\r')
        r = g.get_response(b"0011074103003132\r")
        self.assertEqual(r, b'0011074106_RANGE192\r')
        r = g.get_response(b"0011074103011131\r")
        self.assertEqual(r, b'0011074106_RANGE192\r')
        r = g.get_response(b"0011074103101131\r")
        self.assertEqual(r, b'0011074106_RANGE192\r')

    def test_pirani_correction_write(self):
        g = mock.PPT100()
        r = g.get_response(b"0011074206000100022\r")
        self.assertEqual(r, b'0011074206000100022\r')

    def test_pirani_correction_read(self):
        g = mock.PPT100()
        r = g.get_response(b"0010074202=?108\r")
        self.assertEqual(r, b'0011074206000100022\r')

    def test_wrong_datalen_read(self):
        g = mock.PPT100()
        r = g.get_response(b"0010074201=044\r")
        self.assertEqual(r, b"")

    def test_wrong_datalen_write(self):
        g = mock.PPT100()
        r = g.get_response(b"0011074203100131\r")
        self.assertEqual(r, b'0011074206NO_DEF192\r')

    def test_wrong_data_read(self):
        g = mock.PPT100()
        r = g.get_response(b"00100742021?096\r")
        self.assertEqual(r, b"")
        r = g.get_response(b"0010074201=?107\r")
        self.assertEqual(r, b"")

    def test_wrong_data_write(self):
        g = mock.PPT100()
        r = g.get_response(b"0011074206000133\r")
        self.assertEqual(r, b"")


if __name__ == '__main__':
    unittest.main()
