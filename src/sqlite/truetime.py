"""
module: sqlite.truetime
auth: Nathan T. Stevens
org: PNSN
license: CC-1.0
purpose: This module contains simple methods for converting times between
    DATABASE `datetime` TIMES and UTC DateTimes

    This takes the place of the TrueTime stored procedures that are installed in the PostgreSQL database,
    specifically the TrueTime.getEpoch(datetime, 'UNIX') syntax used in production AQMS procedures.


    DATABASE TIME - Production AQMS system have leap seconds added on top of UTC times, 
        so conversion to UTC time requires subtracting leap seconds from database times

    UTC TIME - (True Time) seconds since 1970-01-01T00:00:00Z with appropriate leap seconds. 
        This is the timestamp sequence used for more or less everything end users interact with
        for earthquake data (data from ComCat / data queried using ObsPy clients from IRIS/EarthScope)
"""

import pandas as pd
from obspy import UTCDateTime

# Current leap seconds corrections as of 10-29-2025
# Structure is:
#   key: leap second amount
#   value: [first NOMINAL second this adjustment applies to,
#           last NOMINAL second that this adjustment applies to]
NOMRANGES = {
    0:[-62135596800,78796799],
    1:[78796800,94694399],
    2:[94694400,126230399],
    3:[126230400,157766399],
    4:[157766400,189302399],
    5:[189302400,220924799],
    6:[220924800,252460799],
    7:[252460800,283996799],
    8:[283996800,315532799],
    9:[315532800,362793599],
    10:[362793600,394329599],
    11:[394329600,425865599],
    12:[425865600,489023999],
    13:[489024000,567993599],
    14:[567993600,631151999],
    15:[631152000,662687999],
    16:[662688000,709948799],
    17:[709948800,741484799],
    18:[741484800,773020799],
    19:[773020800,820454399],
    20:[820454400,867715199],
    21:[867715200,915148799],
    22:[915148800,1136073599],
    23:[1136073600,1230767999],
    24:[1230768000,1341100799],
    25:[1341100800,1435708799],
    26:[1435708800,1483228799],
    27:[1483228800,32503680000]}


def dbtime2utc(dbtime):
    """Convert from database time to UTC time

    :param dbtime: database `datetime` values
    :type dbtime: float
    :return: utc
    :rtype: float
    """    
    for _l, (_m, _M) in NOMRANGES.items():
        if _m <= dbtime <= _M:
            utc = dbtime - _l
            return utc

def utc2dbtime(utc):
    """Convert to database time from UTC timestamp (includes leap-second)

    :param utc: UTC seconds since 1970-01-01 00:00:00Z
    :type utc: float
    :return: dbtime
    :rtype: float
    """    
    if isinstance(utc, UTCDateTime):
        _utc = utc.timestamp
    elif isinstance(utc, pd.Timestamp):
        _utc = utc.timestamp()
    else:
        _utc = float(utc)
    for _l, (_m, _M) in NOMRANGES.items():
        if _m <= _utc - _l <= _M:
            dbtime = _utc + _l
            return dbtime

def dbtime2timestamp(dbtime, format='obspy'):
    """Convert from database `datetime` values into a UTCDateTime timestamp
     and format in one of a selection of date/time objects 

    :param epoch: nominal time (seconds since 1970-01-01T00:00:00 EXCLUDING leap-seconds)
    :type epoch: float
    :param format: formatting to use, defaults to 'obspy'
        Supported: 'obspy' - obspy.UTCDateTime
                   'pandas' - pandas.Timestamp
    :type format: str, optional
    :return: timestamp object
    :rtype: see 'format'
    """    
    utc = dbtime2utc(dbtime)
    if format == 'obspy':
        return UTCDateTime(utc)
    elif format == 'pandas':
        return pd.Timestamp(utc, unit='s')
    else:
        raise ValueError(f'format "{format}" not supported. Only "obspy" and "pandas"')