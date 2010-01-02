import re
from datetime import date

__all__ = [
    "SOARecord"
]

# RFC1035 Hostname Regex, probably too simple
HOSTNAME_FORMAT = re.compile("^[A-Z0-9-\.]+$", re.I)

class BaseResource(object):
    """Base Class for Resource Records
    """

    def __init__(self, name="", ttl=0, class_="IN"):
        """Class constructor.
        """
        self.name = name
        self.ttl = ttl
        self.record_class = class_

    @staticmethod
    def format_hostname(self, hostname):
        """Format hostname for us in zone files.
        Adds a trailing dot if needed, will also convert @ to . so email
        addresses could be formatted for use in SOA records. Will raise
        an exception if hostname doesn't comply with RFC1035 format.
        """
        hostname = "%(hostname)s." % locals() \
            if not hostname.endswith(".") else hostname

        hostname = hostname.replace("@", ".")

        if not HOSTNAME_FORMAT.match(hostname):
            raise Exception("Hostname could not be formatted.")

        return hostname

    @staticmethod
    def check_hostname(self, hostname):
        """Check that a hostname complies with RFC1035 formatting.
        """
        if not HOSTNAME_FORMAT.match(hostname):
            return False
        else:
            return True


class SOARecord(BaseResource):

    def __init__(self, serial, refresh, retry, expire, minumum, \
                    nameserver, email, name="@", ttl="2d", class_="IN"):

    def __str__(self):
        return """%(name)s %(ttl)s %(class)s SOA %(nameserver)s %(email)s
            (%(serial)s %(refresh)s %(retry)s %(expire)s %(minimum)s)
            """.strip("\n") % self

    def __generate_serial(self):
        """Generate a RFC1982 compliant zone serial number.
        """
        today = date.today().strftime("%Y%m%d")
        # Assumes the first 8 chars are the date and the remaining chars are
        # the serial number
        serial = int(self.serial[8:]) + 1

        # Pad out the number to at least two digits
        if len(serial) < 2:
            serial = str(lastserial).rjust(2, "0")

        return "%(today)s%(serial)s" % locals()
