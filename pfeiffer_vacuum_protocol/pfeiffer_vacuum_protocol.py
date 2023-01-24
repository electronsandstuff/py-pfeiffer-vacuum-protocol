from enum import Enum


class InvalidCharError(Exception):  # Custom exception when failing on invalid chars
    pass


# Control non-ascii char filtering
_filter_invalid_char = False


def enable_valid_char_filter():
    """
    Globally enable a filter to ignore invalid characters coming from the serial device.
    :return:
    """
    global _filter_invalid_char
    _filter_invalid_char = True


def disable_valid_char_filter():
    """
    Globally disable a filter to ignore invalid characters coming from the serial device.
    :return:
    """
    global _filter_invalid_char
    _filter_invalid_char = False


# Error states for vacuum gauges
class ErrorCode(Enum):
    NO_ERROR = 1
    DEFECTIVE_TRANSMITTER = 2
    DEFECTIVE_MEMORY = 3


def _send_data_request(s, addr, param_num):
    c = "{:03d}00{:03d}02=?".format(addr, param_num)
    c += "{:03d}\r".format(sum([ord(x) for x in c]) % 256)
    s.write(c.encode())


def _send_control_command(s, addr, param_num, data_str):
    c = "{:03d}10{:03d}{:02d}{:s}".format(addr, param_num, len(data_str), data_str)
    c += "{:03d}\r".format(sum([ord(x) for x in c]) % 256)
    return s.write(c.encode())


def _read_gauge_response(s, valid_char_filter=None):
    if valid_char_filter is None:
        valid_char_filter = _filter_invalid_char

    # Read until newline or we stop getting a response
    r = ""
    for _ in range(64):
        c = s.read(1)

        if c == b"":
            break

        try:
            r += c.decode("ascii")
        except UnicodeDecodeError:
            if valid_char_filter:
                continue
            raise InvalidCharError("Cannot decode character. This issue may sometimes be resolved by ignoring invalid "
                                   "characters. Enable the filter globally by running the function "
                                   "`pfeiffer_vacuum_protocol.enable_valid_char_filter()` after the import statement.")

        if c == b"\r":
            break

    # Check the length
    if len(r) < 14:
        raise ValueError("gauge response too short to be valid")

    # Check it is terminated correctly
    if r[-1] != "\r":
        raise ValueError("gauge response incorrectly terminated")

    # Evaluate the checksum
    if int(r[-4:-1]) != (sum([ord(x) for x in r[:-4]]) % 256):
        raise ValueError("invalid checksum in gauge response")

    # Pull out the address
    addr = int(r[:3])
    rw = int(r[3:4])
    param_num = int(r[5:8])
    data = r[10:-4]

    # Check for errors
    if data == "NO_DEF":
        raise ValueError("undefined parameter number")
    if data == "_RANGE":
        raise ValueError("data is out of range")
    if data == "_LOGIC":
        raise ValueError("logic access violation")

    # Return it
    return addr, rw, param_num, data


def read_error_code(s, addr, valid_char_filter=None):
    """
    Reads Pfeiffer's low level error code on the gauge.  This appears to be useful for diagnosing failure of the transmitter itself.

    :param s: The open serial object pointing to an adapter attached to the gauge.
    :param addr: The address of the gauge.
    :type addr: int
    :param valid_char_filter: Manually override the valid character filter.
    :type valid_char_filter: bool/None

    :returns: The error code returned by the gauge, this can be one of `NO_ERROR`, `DEFECTIVE_TRANSMITTER`, or `DEFECTIVE_MEMORY`
    :rtype: pfeiffer_vacuum_protocol.ErrorCode enum element
    """
    _send_data_request(s, addr, 303)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s, valid_char_filter=valid_char_filter)

    if raddr != addr or rw != 1 or rparam_num != 303:
        raise ValueError("invalid response from gauge")

    if rdata == "000000":
        return ErrorCode.NO_ERROR
    elif rdata == "Err001":
        return ErrorCode.DEFECTIVE_TRANSMITTER
    elif rdata == "Err002":
        return ErrorCode.DEFECTIVE_MEMORY
    else:
        raise ValueError("unexpected error code from gauge")


def read_software_version(s, addr, valid_char_filter=None):
    """
    Returns the vacuum gauge's firmware version.

    :param s: The open serial device attached to the gauge.
    :param addr: The address of the gauge.
    :type addr: int
    :param valid_char_filter: Manually override the valid character filter.
    :type valid_char_filter: bool/None

    :returns: The version numbers as the tuple (major, minor, sub-minor)
    """
    _send_data_request(s, addr, 312)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s, valid_char_filter=valid_char_filter)

    if raddr != addr or rw != 1 or rparam_num != 312:
        raise ValueError("invalid response from gauge")

    return int(rdata[0:2]), int(rdata[2:4]), int(rdata[4:])


def read_gauge_type(s, addr, valid_char_filter=None):
    """
    Returns the name of the vacuum gauge attached at this address.

    :param s: The open serial device attached to the gauge.
    :param addr: The address of the gauge.
    :type addr: int
    :param valid_char_filter: Manually override the valid character filter.
    :type valid_char_filter: bool/None

    :returns: The model name of the gauge attached
    :rtype: str
    """
    _send_data_request(s, addr, 349)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s, valid_char_filter=valid_char_filter)

    if raddr != addr or rw != 1 or rparam_num != 349:
        raise ValueError("invalid response from gauge")

    if rdata == "    A1":
        return "CPT 100"
    elif rdata == "    A2":
        return "RPT 100"
    elif rdata == "    A3":
        return "PPT 100"
    elif rdata == "    A4":
        return "HPT 100"
    elif rdata == "    A5":
        return "MPT 100"
    else:
        raise ValueError("unrecognized gauge type")


def read_pressure(s, addr, valid_char_filter=None):
    """
    Reads the pressure from the gauge and returns it in bars.

    :param s: The open serial device attached to the gauge.
    :param addr: The address of the gauge.
    :type addr: int
    :param valid_char_filter: Manually override the valid character filter.
    :type valid_char_filter: bool/None

    :returns: Pressure measured by gauge in bars
    :rtype: float
    """
    _send_data_request(s, addr, 740)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s, valid_char_filter=valid_char_filter)

    if raddr != addr or rw != 1 or rparam_num != 740:
        raise ValueError("invalid response from gauge")

    # Convert to a float
    mantissa = int(rdata[:4])
    exponent = int(rdata[4:])
    return float(mantissa * 10 ** (exponent - 26))


def write_pressure_setpoint(s, addr, val, valid_char_filter=None):
    """
    Sets the gauge's "vacuum setpoint".  In the manual, this appears to tell the gauge if it's operating in a high or low pressure regime to change some of its signal processing.

    :param s: The open serial device attached to the gauge.
    :param addr: The address of the gauge.
    :type addr: int
    :param valid_char_filter: Manually override the valid character filter.
    :type valid_char_filter: bool/None
    :param val: Manually override the valid character filter.
    :type val: The setpoint
    :returns: None
    :rtype: None
    """
    # Format the data
    data = "{:03d}".format(val)
    _send_control_command(s, addr, 741, data)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s, valid_char_filter=valid_char_filter)

    # Check the response
    if raddr != addr or rw != 1 or rparam_num != 741:
        raise ValueError("invalid response from gauge")

    if rdata != data:
        raise ValueError("invalid acknowledgment from gauge")


def read_correction_value(s, addr, valid_char_filter=None):
    """
    Returns the current correction value used to adjust pressure measurements for different gas compositions.

    :param s: The open serial device attached to the gauge.
    :param addr: The address of the gauge.
    :type addr: int
    :param valid_char_filter: Manually override the valid character filter.
    :type valid_char_filter: bool/None

    :returns: The current correction value
    """
    _send_data_request(s, addr, 742)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s, valid_char_filter=valid_char_filter)

    if raddr != addr or rw != 1 or rparam_num != 742:
        raise ValueError("invalid response from gauge")

    return float(rdata) / 100


def write_correction_value(s, addr, val, valid_char_filter=None):
    """
    Sets the correction value on the gauge.  Used to adjust the pressure measurement for different gas compositions.

    :param s: The open serial device attached to the gauge.
    :param addr: The address of the gauge.
    :type addr: int
    :param valid_char_filter: Manually override the valid character filter.
    :type valid_char_filter: bool/None
    :param val: The value it will be set to
    :type val: float
    :returns: None
    :rtype: None
    """
    # Format the data
    data = "{:06d}".format(int(val * 100))
    _send_control_command(s, addr, 742, data)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s, valid_char_filter=valid_char_filter)

    # Check the response
    if raddr != addr or rw != 1 or rparam_num != 742:
        raise ValueError("invalid response from gauge")

    if rdata != data:
        raise ValueError("invalid acknowledgment from gauge")
