import io
from .pfeiffer_vacuum_protocol import ErrorCode

# Pulled from pySerial
PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)


def to_bytes(seq):
    """convert a sequence to a bytes type"""
    if isinstance(seq, bytes):
        return seq
    elif isinstance(seq, bytearray):
        return bytes(seq)
    elif isinstance(seq, memoryview):
        return seq.tobytes()
    elif isinstance(seq, str):
        raise TypeError('unicode strings are not supported, please encode to bytes: {!r}'.format(seq))
    else:
        # handle list of integers and bytes (one or more items) for Python 2 and 3
        return bytes(bytearray(seq))


class Serial(io.RawIOBase):
    """\
    Mockup of a serial port named COM1 connected to a pfeiffer device
    """
    # Default values copied from pySerial
    BAUDRATES = (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
                 9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000,
                 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000,
                 3000000, 3500000, 4000000)
    BYTESIZES = (FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS)
    PARITIES = (PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE)
    STOPBITS = (STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO)

    def __init__(self,
                 connected_device,
                 port=None,
                 baudrate=9600,
                 bytesize=EIGHTBITS,
                 parity=PARITY_NONE,
                 stopbits=STOPBITS_ONE,
                 timeout=None,
                 xonxoff=False,
                 rtscts=False,
                 write_timeout=None,
                 dsrdtr=False,
                 inter_byte_timeout=None,
                 exclusive=None,
                 **kwargs):
        """\
        Initializes the com port object
        """
        self.buffer = b""
        self.dev = connected_device
        self.baudrate = baudrate

    def flush(self):
        self.buffer = b""

    def write(self, output):
        self.buffer += self.dev.get_response(to_bytes(output))
        return len(output)

    def read(self, readlen=-1):
        if self.baudrate != 9600:
            return b""

        ret = self.buffer[:readlen]
        self.buffer = self.buffer[readlen:]
        return ret

    def readinto(self, b):
        data = self.read(len(b))
        n = len(data)
        b[:n] = data
        return n

    def readable(self):
        return True

    def writable(self):
        return True

    def seekable(self):
        return False


class PPT100:
    """\
    Mockup of the Pfeiffer vacuum gauge model PPT 100
    """

    def __init__(self, address=1, err_state=ErrorCode.NO_ERROR, nonascii=False):
        self.address = address
        self.err_state = err_state
        self.nonascii = nonascii  # Include array of  \xff before message (github issue 1)

    def _get_response(self, bin_str):
        # Convert to a unicode str
        in_str = bin_str.decode("ascii")

        # If it doesn't end in a carriage return, exit
        if in_str[-1] != '\r':
            return b""

        # Validate the checksum and exit if bad
        if int(in_str[-4:-1]) != (sum([ord(x) for x in in_str[:-4]]) % 256):
            return b""

        # Get the address, and exit if it isn't correct
        if int(in_str[:3]) != 1:
            return b""

        # Get the data length and return if it's wrong
        if len(in_str) - 14 != int(in_str[8:10]):
            return b""

        # Get the operation type (read/write)
        op_type = int(in_str[3])

        # Get the paramter number
        param_num = int(in_str[5:8])

        # If we are reading
        if op_type == 0:
            # Check that the data length is right and exit if not
            if int(in_str[8:10]) != 2:
                return b""

            # Check that the data is =? exit if it isn't
            if in_str[10:12] != "=?":
                return b""

            # If it is error code, return the right one
            if param_num == 303:
                if self.err_state == ErrorCode.NO_ERROR:
                    return b'0011030306000000014\r'

                elif self.err_state == ErrorCode.DEFECTIVE_TRANSMITTER:
                    return b'0011030306Err001168\r'

                elif self.err_state == ErrorCode.DEFECTIVE_MEMORY:
                    return b'0011030306Err002169\r'

                else:
                    raise ValueError("unknown error state")

            # Or, if it's version number, return it
            elif param_num == 312:
                return b'0011031206010100016\r'

            # Or, if it's the component name, return it
            elif param_num == 349:
                return b'0011034906    A3236\r'

            # Or, if it's pressure, return it
            elif param_num == 740:
                return b'0011074006100023025\r'

            # Or, if it's the correction value, return it
            elif param_num == 742:
                return b'0011074206000100022\r'

            # If it wasn't any of these, return the error code
            else:
                resp = "00110{:03d}06NO_DEF".format(param_num)
                resp += "{:03d}\r".format(sum([ord(x) for x in resp]) % 256)
                return resp.encode()

        # Or, if it's write
        else:
            # If it was set point
            if param_num == 741:
                # Check the datatype
                if int(in_str[8:10]) != 3:
                    return b'0011074106NO_DEF191\r'

                # Check bounds and return error if we're out
                val = int(in_str[10:13])
                if val < 0 or val > 1:
                    return b'0011074106_RANGE192\r'

                # Return the confirmation
                return in_str.encode()

            # Or, if it was the correction value
            elif param_num == 742:
                # Check the datatype
                if int(in_str[8:10]) != 6:
                    return b'0011074206NO_DEF192\r'

                # Return the confirmation
                return in_str.encode()

            # If it wasn't a valid parameter, return an error
            else:
                return b'0011074206NO_DEF192\r'

    def get_response(self, bin_str):
        """
        Wrap the get response function to optionally add chars before/after
        """
        r = self._get_response(bin_str)
        if self.nonascii:
            r = b'\xff'*40 + r
        return r
