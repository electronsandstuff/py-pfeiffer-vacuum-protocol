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

# Pulled from pySerial
PARITY_NONE, PARITY_EVEN, PARITY_ODD, PARITY_MARK, PARITY_SPACE = 'N', 'E', 'O', 'M', 'S'
STOPBITS_ONE, STOPBITS_ONE_POINT_FIVE, STOPBITS_TWO = (1, 1.5, 2)
FIVEBITS, SIXBITS, SEVENBITS, EIGHTBITS = (5, 6, 7, 8)

class Serial:
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
                 connected_device=None,
                 **kwargs):
        """\
        Initializes the com port object
        """
    pass

# Error states for vacuum gauges
NO_ERROR, DEFECTIVE_TRANSMITTER, DEFECTIVE_MEMORY = (0, 1, 2)

class PPT100:
    """\
    Mockup of the Pfeiffer vacuum gauge model PPT 100
    """
    def __init__(self, address=1, err_state=NO_ERROR):
        self.address = address
        self.software_version = "010100"
        self.component = "    A3"
        self.pressure = 1 # in bar
        self.pressure_setpoint = 1 # in bar
        self.err_state = err_state

    def get_response(self, bin_str):
        pass
