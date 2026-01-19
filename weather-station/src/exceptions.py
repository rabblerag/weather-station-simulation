class InvalidHMACError(Exception):
    """Raised if packet HMAC is invalid"""
    pass


class StationKeyError(Exception):
    """Raised if server cannot find the HMAC key of the sender"""
    pass


class MetricRangeError(Exception):
    """Raised if received metric is out-of-range"""
    pass


class OldTimestampError(Exception):
    """Raised if packet timestamp is too old"""
    pass


class MissingHeaderFields(Exception):
    """Raised if packet is missing necessary header fields"""
    pass


class ClientTimeoutError(Exception):
    """Raised if client takes too long to send rest of packet"""
    pass


class ConnectionClosedError(Exception):
    """Raised if length field is 0. This means the server has disconnected"""
    pass
