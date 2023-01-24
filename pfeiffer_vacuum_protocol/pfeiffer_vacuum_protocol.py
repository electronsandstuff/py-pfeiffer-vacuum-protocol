from enum import Enum


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


def _read_gauge_response(s):
    # Read until newline or we stop getting a response
    r = ""
    for _ in range(64):
        c = s.read(1)
        if c == b"":
            break
        r += c.decode("ascii")
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


def read_error_code(s, addr):
    _send_data_request(s, addr, 303)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s)

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


def read_software_version(s, addr):
    _send_data_request(s, addr, 312)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s)

    if raddr != addr or rw != 1 or rparam_num != 312:
        raise ValueError("invalid response from gauge")

    return int(rdata[0:2]), int(rdata[2:4]), int(rdata[4:])


def read_gauge_type(s, addr):
    _send_data_request(s, addr, 349)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s)

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


def read_pressure(s, addr):
    _send_data_request(s, addr, 740)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s)

    if raddr != addr or rw != 1 or rparam_num != 740:
        raise ValueError("invalid response from gauge")

    # Convert to a float
    mantissa = int(rdata[:4])
    exponent = int(rdata[4:])
    return float(mantissa * 10 ** (exponent - 26))


def write_pressure_setpoint(s, addr, val):
    # Format the data
    data = "{:03d}".format(val)
    _send_control_command(s, addr, 741, data)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s)

    # Check the response
    if raddr != addr or rw != 1 or rparam_num != 741:
        raise ValueError("invalid response from gauge")

    if rdata != data:
        raise ValueError("invalid acknowledgment from gauge")


def read_correction_value(s, addr):
    _send_data_request(s, addr, 742)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s)

    if raddr != addr or rw != 1 or rparam_num != 742:
        raise ValueError("invalid response from gauge")

    return float(rdata) / 100


def write_correction_value(s, addr, val):
    # Format the data
    data = "{:06d}".format(int(val * 100))
    _send_control_command(s, addr, 742, data)
    raddr, rw, rparam_num, rdata = _read_gauge_response(s)

    # Check the response
    if raddr != addr or rw != 1 or rparam_num != 742:
        raise ValueError("invalid response from gauge")

    if rdata != data:
        raise ValueError("invalid acknowledgment from gauge")
