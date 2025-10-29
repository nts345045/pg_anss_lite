"""
script: src/cascadia/ingest_morton.py
auth: Nathan T. Stevens
org: PNSN
license: CC-1.0
purpose: This script reads the ds01.csv earthquake catalog file from Morton et al. (2023),
    writes its data to an AQMS PostgreSQL style database and checks if any previously 
    existing origins in the database coincide with origins being loaded. 

    This script has a number of baked-in assumptions about indexing and largely serves
    as an example of how these data were loaded into the `offshore_ml` database and how
    one might load their own data into an AQMS PostgreSQL style database.

References: 
Morton, E.A., Bilek S.L., Rowe, C.A. (2023) Cascadia Subduction Zone Fault Heterogeneities From Newly
    Detected Small Magnitude Earthquakes. JGR Solid Earth 128(6). https://doi.org/10.1029/2023JB026607
"""

import psycopg2
from pathlib import Path
from getpass import getpass
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).parent.parent.parent
OFILE = ROOT/'data'/'cascadia'/'ds01.csv'

# Load data from their data repository
df = pd.read_csv(OFILE)
# Get rid of empty rows
df = df[df.YEAR.notna()]
# Populate datetime objects
df = df.assign(datetime = [ 
    pd.Timestamp(year=int(x.YEAR), month=int(x.MONTH), day=int(x.DAY),
                 hour=int(x.HOUR), minute=int(x.MINUTE)) + pd.Timedelta(float(x.SECOND), unit='s') 
    for _, x in df.iterrows()
])

# Start Morton et al. (2023) origins with 8 (avoids Cascadia OBS ML origins/events)
orid_base = 80000000
evid_base = 80000000
magid_base = 80000000
commid_base = 80000000
conn = psycopg2.connect(
    dbname='offshore_ml',
    port='5432',
    host='localhost',
    user='nates',
    password=getpass('password for `nates`: ')
)
cur = conn.cursor()
for idx, row in tqdm(df.iterrows(), total=len(df)):
    #Populate magnitude first
    sqlm = """
        INSERT INTO netmag 
            (magid, orid, magnitude, magtype, auth, magalgo, rflag) 
        VALUES 
            (%(magid)s, %(orid)s, %(magnitude)s, 'd', 'Morton2023','Eaton1992','H');
        """
    varm = {'magid': int(magid_base + idx),
            'orid': int(orid_base + idx),
            'magnitude': float(row.Md)}
    try:
        cur.execute(sqlm, varm)
    except psycopg2.Error as e:
        conn.rollback()
        print(f'{e}\nROLLBACK')
        breakpoint()

    # Populate remark if present
    remark1 = {'commid': int(commid_base + idx),
               'lineno': 1,
               'remark': f'Plate designation: {row['PLATE DESIGNATION']}'}
    remark2 = {'commid': int(commid_base + idx),
               'lineno': 2,
               'remark': f'Template event?: {row['TEMPLATE EVENT?']}'}
    sqlr = """
        INSERT INTO remark 
            (commid, lineno, remark) 
        VALUES 
            (%(commid)s, %(lineno)s, %(remark)s);
        """
    for remark in [remark1, remark2]:
        try:
            cur.execute(sqlr, remark)
        except psycopg2.Error as e:
            conn.rollback()
            print(f'{e}\nROLLBACK')
            breakpoint()        

    # Search for matches in catalog
    sql = """
        WITH timesubset AS (
            SELECT * FROM origin 
            WHERE datetime BETWEEN 
                TrueTime.putEpoch(%(truetime)s, 'UNIX') - 5 AND
                TrueTime.putEpoch(%(truetime)s, 'UNIX') + 5 AND 
            abs(lat - %(lat)s) < 0.1 AND abs (lon - %(lon)s) < 0.1 
            )
        SELECT * FROM timesubset 
        ORDER BY abs(lat - %(lat)s) + 
            abs(lon - %(lon)s) + 
            abs(datetime - TrueTime.putEpoch(%(truetime)s, 'UNIX'));
        """
    var = {'truetime': row.datetime.timestamp(),
           'lat': row.LAT,
           'lon': row.LON}
    
    cur.execute(sql, var)
    result = cur.fetchall()
    if len(result) > 0:
        evid = result[0][1]
        sqle = """
            UPDATE event SET prefor = %(orid)s, prefmag = %(magid)s, 
                auth='Morton2023', subsource='subspace', selectflag=1,
                version = 4 
            WHERE evid = %(evid)s;
            """
        vare = {'orid': int(orid_base + idx),
                'magid': int(magid_base + idx),
                'evid': int(evid)}
    else:
        evid = int(evid_base + idx)
        sqle = """
            INSERT INTO event 
                (evid, prefor, prefmag, etype, auth, subsource, version) 
            VALUES 
                (%(evid)s, %(orid)s, %(magid)s, 'eq', 'Morton2023','subspace',1);
            """
        vare = {'evid': int(evid),
                'orid': int(orid_base + idx),
                'magid': int(magid_base + idx)}
    try:
        cur.execute(sqle, vare)
    except psycopg2.Error as e:
        conn.rollback()
        print(f'{e}\nROLLBACK')
        breakpoint()     
    

    sqlo = """
        INSERT INTO origin 
            (orid, evid, prefmag, commid, 
            datetime, lat, lon, depth, 
            totalarr, gap, distance,
            wrms, erhor, sdep,
            auth, algorithm, algo_assoc) 
        VALUES 
            (%(orid)s, %(evid)s, %(magid)s, %(commid)s, 
             TrueTime.putEpoch(%(datetime)s, 'UNIX'), %(lat)s, %(lon)s, %(depth)s,
             %(totalarr)s, %(gap)s, %(distance)s, %(wrms)s, %(erhor)s, %(sdep)s, 
             'Morton2023', 'HYP2000','subspace');
        """
    varo = {
        'orid': int(orid_base + idx),
        'evid': int(evid),
        'magid': int(magid_base + idx),
        'commid': int(commid_base + idx),
        'datetime': row.datetime.timestamp(),
        'lat': float(row.LAT),
        'lon': float(row.LON),
        'depth': float(row.DEPTH),
        'totalarr': int(row['Num P&S with weights > 0.1']),
        'gap': int(row['max az gap']),
        'distance': float(row['dist to nearest stn']),
        'wrms': float(row['tt RMS']),
        'erhor': float(row.ERH),
        'sdep': float(row.ERZ)
    }

    try:
        cur.execute(sqlo, varo)
    except psycopg2.Error as e:
        conn.rollback()
        print(f'{e}\nROLLBACK')
        breakpoint()
    conn.commit()
