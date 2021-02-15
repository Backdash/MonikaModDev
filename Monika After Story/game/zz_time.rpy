# special time classes in case we have no timezones

python early:

    import pytz.tzinfo

    class MASLocalTz(pytz.tzinfo.StaticTzInfo):
        """
        Special Tz class that we use when we need to do dynamic timezone
        creation because we couldn't find existing timezone data.

        Despite using StaticTzInfo, this does respect DST, in the sense that
        we will use whatever offset the time library tells us to use.
        """
        import time
        _is_dst = False
        _tz_cache = None

        def __repr__(self):
            return "<MASLocalTz {0}>".format(self._utcoffset.total_seconds())

        @staticmethod
        def apply(dt):
            """
            Returns a datetime that has the same time info as the given one
            but with this timezone set to the tzinfo

            NOTE: will raise an error if tzinfo is already set

            IN:
                dt - datetime to generate new datetime with

            RETURNS: new datetime object with same time as previous but 
                tzinfo set to an instance of this MASLocalTz
            """
            mas_tz = MASLocalTz.create()
            return mas_tz.localize(dt)

        @classmethod
        def create(cls):
            """
            Generates an instance of this class that is prepared to localize
            a time or whatever.

            NOTE: this caches the timezone

            RETURNS:
                instance of MASLocalTz ready for usage
            """
            if cls._tz_cache is not None:
                return cls._tz_cache

            # in general, assume timezone is correct when loading from time
            tz_offset = 0
            is_dst = False
            if cls.time.daylight != 0 and cls.time.localtime().tm_isdst > 0:
                tz_offset = cls.time.altzone
                is_dst = True
            else:
                tz_offset = cls.time.timezone

            # time's zones do postive if west, negative if east, but tzinfo
            # is expecting the opposite, so flip the values.
            tz_offset *= -1

            tz_obj = MASLocalTz()

            # to prevent issues later, always round to whole number minutes
            tz_obj._utcoffset = datetime.timedelta(minutes=(tz_offset / 60))
            tz_obj._tzname = "Custom MAS Time"
            tz_obj.zone = "MAS"
            tz_obj._is_dst = is_dst

            if cls._tz_cache is None:
                cls._tz_cache = tz_obj

            return tz_obj

        @classmethod
        def reload(cls):
            """
            Reloads the cached localzone

            RETURNS: instance of MASLocalTz ready for usage
            """
            cls._tz_cache = None
            return MASLocalTz.create()
