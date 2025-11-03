import sqlite3
import pandas as pd
from truetime import dbtime2timestamp

def connect_to_database(sqlite_file):
    conn = sqlite3.connect(sqlite_file)
    return conn

def select_preferred_origins(conn, event_ids, include_phases=False, truetime=False):
    """Fetch records for the hypocentral parameter estimates tied to the preferred origins of
    specified event IDs (EVID) with the option to include contributing phase arrival information.

    Mapping ANSS to ObsPy:
    The `_sql` statements in this method demonstrate a selection of formatting adjustment "recipes" 
    for converting from the ANSS channel naming conventions to those customarily used in ObsPy.
    In particular, see the line starting with `CASE WHEN` and comma delimited entries containing `AS` 
    statements.

    NOMINAL TIME NOTICE: 
    - TL;DR - add leap-second correction(s) to times to line up with IRIS/etc. archived waveform data

    The ANSS schema uses nominal times (i.e., no leap-second corrections), so the time columns for
    origin times and phase arrival times are aliased to `nom_origin` and `nom_arrival`, respectively,
    to flag that leap-second corrections are NOT applied. These float-type values convey elapsed seconds
    since 1970-01-01T00:00:00Z (UTC). For conversion recipes see :meth:`~sqlite.truetime.nominal2true`

    :param conn: sqlite3 connection to the desired database (see :meth:`~.connect_to_database`)
    :type conn: sqlite3.connect.Connection
    :param event_ids: one or more integer-like event IDs to query
    :type event_ids: int, str or list, tuple, or set thereof
    :param include_phases: should phase-arrival data be included? Defaults to False
    :type include_phases: bool, optional
    :return: result dataframe
    :rtype: pandas.DataFrame
    """    
    if isinstance(event_ids, (str, int)):
        event_ids = [str(int(event_ids))]
    elif isinstance(event_ids, (list, tuple, set)):
        if all(isinstance(_e, (int, str)) for _e in event_ids):
            event_ids = [str(int(_e)) for _e in event_ids]
    if include_phases:
        _sql = f"""
                SELECT e.evid, e.etype, 
                    o.orid, o.datetime AS nom_origin, o.lat, o.lon, o.depth, o.erhor as herr_km, o.sdep as verr_km, o.wrms,
                    a.arid, a.datetime AS nom_arrival, a.net AS network, a.sta AS station, 
                    CASE WHEN a.location = '  ' THEN '' ELSE a.location END AS location,
                    a.seedchan AS channel, a.iphase AS label, a.quality 
                FROM event e 
                    INNER JOIN origin o ON e.prefor = o.orid
                    INNER JOIN assocaro x ON o.orid = x.orid 
                    INNER JOIN arrival a ON x.arid = a.arid
                WHERE e.evid IN ({','.join(event_ids)});
            """
    else:
        _sql = f"""
                SELECT e.evid, e.etype, 
                    o.orid, o.datetime AS nom_origin, o.lat, o.lon, o.depth, o.erhor as herr_km, o.sdep as verr_km, o.wrms,
                FROM event e 
                    INNER JOIN origin o ON e.prefor = o.orid 
                WHERE e.evid IN ({','.join(event_ids)});
            """
    df = pd.read_sql(_sql, con=conn)
    if truetime:

        df.nom_origin = df.nom_origin.apply(lambda x: nominal2timestamp(x, format='pandas'))
        df = df.rename(columns={'nom_origin':'origin'})
        if include_phases:
            df.nom_arrival = df.nom_arrival.apply(lambda x: nominal2timestamp(x, format='pandas'))
            df = df.rename(columns={'nom_arrival': 'arrival'})
    return df

