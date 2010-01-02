class BINDTime(type):
    """Time handling for BIND time formats.
    Basically the goal here is to abstract the concept of seconds
    or any other kind of time from the user. Pass a time in any
    BIND format and get it back in either seconds or some other
    BIND format.

    see: http://www.zytrax.com/books/dns/apa/time.html
    """

    # Hrm... I probably don't like this but unless I think of something
    # better it stays.
    SEC_MIN = 60
    SEC_HRS = 3600
    SEC_DAY = 86400
    SEC_WEEK = 604800

    def __init__(self, time):
        """Class constructor.
        """
        self.time = time

    ############################################################
    #                       TIME PROPERTY

    __time = 0

    def __set_time(self, time):
        """Set time property.
        Internally we represent times as seconds so either accept a
        number (optionally terminated with an "s") and store it, otherwise
        some additional work will need to be done to convert it.
        """
        if time.isdigit():
            self.__time = int(time)
        elif time.endswith("s"):
            self.__time = int(time[:-1])
        else:
            self.convert_to_seconds(time)

    def __get_time(self):
        """Get time property.
        Returns the time in a friendly format (i.e. NOT seconds if possible).
        """
        return self.get_friendly_time(self.__time)

    time = property(fset=__set_time, fget=__get_time)

    ############################################################

    def convert_to_seconds(self, time):
        """Convert a time from BIND style to seconds.
        """
        pass

    def get_friendly_time(self, time):
        """Get a friendly representation of the time.
        Don't consider seconds friendly, instead get a higher-level
        representation of the time.
        """
        pass
