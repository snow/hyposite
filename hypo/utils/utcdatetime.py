from datetime import datetime, timedelta, tzinfo
import time

class SimpleTZ(tzinfo):
    ''''''
    offset_minutes = 0
        
    def __init__(self, hours=0, minites=0):
        ''''''
        self.offset_minutes = hours * 60 + minites
        
    def utcoffset(self, dt=None):
        return timedelta(minutes=self.offset_minutes)
    
    def dst(self, dt=None):
        return timedelta(0)
    
    def tzname(self, dt=None):
        name = '{}00'.format(str(self.offset_minutes / 60).zfill(2))
        
        if 0 < self.offset_minutes:
            name = '+{}'.format(name)
            
        return name
    
    def fromutc(self, dt):
        return dt + dt.utcoffset()

class UTCDatetime(object):
    timestamp = None
    microseconds = None
    __SECONDS_IN_HOUR = 60 * 60
    
    def __init__(self, timestamp, microseconds=None):
        self.timestamp = timestamp
        self.microseconds = microseconds
    
    def get_local_datetime(self, tz=None, hours=0, minutes=0):
        ''''''
        tz = self.__get_tz(tz, hours, minutes)
        
        ts = self.timestamp + tz.utcoffset().seconds
        d1 = datetime.fromtimestamp(ts)
        d2 = datetime(*d1.timetuple()[:6], tzinfo=tz)
        
        return d2
        
    def get_utc_datetime(self):
        ''''''
        return self.get_local_datetime()
    
    def strftime_local(self, format, tz=None, hours=0, minutes=0):
        dt = self.get_local_datetime(tz, hours, minutes)
        return dt.strftime(format)
        
    def strftime_utc(self, format):
        return self.strftime_utc(format)
        
    @classmethod
    def __get_tz(cls, tz=None, hours=0, minutes=0):
        return tz or SimpleTZ(hours, minutes)
        
    @classmethod
    def from_datetime(cls, dt, tz=None, hours=0, minutes=0):    
        ''''''
        tz = dt.tzinfo or cls.__get_tz(tz, hours, minutes)
        local_timestamp = time.mktime(dt.timetuple())
        
        return cls(local_timestamp - tz.utcoffset(dt).seconds)
    
    @classmethod
    def now(cls, tz=None, hours=0, minutes=0):
        return cls.from_datetime(datetime.now(), tz, hours, minutes)
        
    @classmethod
    def strptime(cls, str, format, tz, hours=0, minutes=0):
        ''''''
        dt = datetime.strptime(str, format)
        return cls.from_datetime(dt, tz, hours, minutes)