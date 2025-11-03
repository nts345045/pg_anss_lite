"""
script: ingest_assoc_ver_3.py
auth: Nathan T. Stevens
org: PNSN
license: CC-1.0
purpose: This script maps semi-arbitrary integer indexed origin-to-arrival
    associations and travel time residual data from the GraphDD(+coherence)
    solutions based on the  machine learning ensemble picks (ELEP) for the 
    Cascadia offshore OBS study led by H. Bito and M. Denolle 
    (University of Washington) facilitated by Ian McBrearty (Stanford) and 
    other Stanford colleagues. This script iterates across unique Station.Network
    codes in the provided association file, queries all picks for this station
    from the PostgreSQL database, and then uses table joins informed by structured
    indexing from the other two `ingest*.py` scripts to map ARRIVAL and ORIGIN
    table entries together in the ASSOCARO table

Notes on adaptations to the ANSS ASSOCARO table schema:
 - No notable divergences from fields as described in the CISN/ANSS parametric
   schema documentation

   https://ncedc.org/db/Documents/NewSchemas/PI/v1.6.4/PI.1.6.4/index.htm

"""

import psycopg2
import pandas as pd
from getpass import getpass
from pathlib import Path
from tqdm import tqdm

def orid2oidx(value, orid_base=90000000):
    """Convert back to native Origin INDex values provided in input CSVs
    which had the general form

    ORID = orid_base + (OIDX*10) + offset_integer

    :param value: _description_
    :type value: _type_
    :param orid_base: _description_, defaults to 90000000
    :type orid_base: int, optional
    :return: _description_
    :rtype: _type_
    """    
    return (value - orid_base)//10

def oidx2orid(value, orid_base=90000000, offset_integer=3):
    return orid_base + (value*10) + offset_integer


ROOT = Path(__file__).parent.parent.parent
AFILE = ROOT/'data'/'cascadia'/'Cascadia_relocated_catalog_picks_ver_3.csv'
OFILE = ROOT/'data'/'cascadia'/'picks_from_phase_picker'/'origin_2010_2015_reloc_cog_ver3.csv'

LOCALCONN = {'host': 'localhost',
             'user': 'nates',
             'port': '5432',
             'dbname': 'offshore_ml'}

df_orig = pd.read_csv(OFILE)
df_orig = df_orig.rename(columns={'Unnamed: 0': 'iorid'})
# Populate GDD+COH origin IDs
df_orig = df_orig.assign(pgorid=[oidx2orid(x) for x in df_orig.iorid])
df_assoc = pd.read_csv(AFILE)

df_assoc = df_assoc.assign(pgorid=[df_orig.loc[x, 'pgorid'] for x in df_assoc['Event ID']])

conn = psycopg2.connect(**LOCALCONN, password=getpass('Enter password for user `nates` of database `offshore_ml`: '))
cur = conn.cursor()

uns = df_assoc['Station Name'].unique()

for _e, stanet in enumerate(uns):
    print(f'RUNNING {stanet} ({_e + 1}/{len(uns)})')
    _s, _n = stanet.split('.')
    _n = _n.strip()
    _s = _s.strip()
    _df_assoc = df_assoc[df_assoc['Station Name'] == stanet]
    _df_assoc = _df_assoc.assign(truetime = [int(pd.Timestamp(x).timestamp()*1e6) for x in _df_assoc['Pick Time (UTC)']])
    _df_assoc.index = _df_assoc.truetime
    _df_assoc = _df_assoc[['pgorid','Phase Type', 'Station Name','Residual (s)']]
    _sql = f"""
            SELECT 
                a.arid, 
                TrueTime.getEpoch(a.datetime, 'UNIX')*1000000::int as truetime, 
                a.iphase 
            FROM arrival a 
                LEFT JOIN assocaro x ON a.arid = x.arid 
            WHERE x.orid IS NULL AND 
                a.net = '{_n}' 
                AND a.sta = '{_s}' 
            ORDER BY a.datetime;
           """
    # Read from database
    df_pgarr = pd.read_sql(_sql, con=conn, index_col='truetime')
    # Force integer microseconds timestamps
    df_pgarr.index = [int(round(x)) for x in df_pgarr.index]
    # breakpoint()
    # Get time matches
    df_pgarr = df_pgarr.join(_df_assoc, how='inner', lsuffix='pg', rsuffix='csv')
    # breakpoint()
    for _, row in tqdm(df_pgarr.iterrows(), total=len(df_pgarr)):
        _sql = """
                INSERT INTO assocaro 
                    (orid, arid, auth, subsource, iphase, timeres, rflag) 
                VALUES
                    (%(orid)s, %(arid)s, %(auth)s, %(subsource)s, %(iphase)s, %(timeres)s, 'A');
               """
        _var = {'orid': int(row.pgorid),
                'arid': int(row.arid),
                'auth': 'Stanford',
                'subsource': 'gddcoh',
                'iphase': row.iphase,
                'timeres': row['Residual (s)']}
        try:
            cur.execute(_sql, _var)
        except psycopg2.Error as e:
            print(e)
            conn.rollback()
            breakpoint()
        # And also do the GraphDD W/O Coherence
        _var.update({'orid': _var['orid'] - 1,
                     'subsource': 'gdd'})
        try:
            cur.execute(_sql, _var)
        except psycopg2.Error as e:
            print(e)
            conn.rollback()
            breakpoint()
    conn.commit()


# for idx, orow in df_orig.iterrows():
#     _df_assoc = df_assoc[df_assoc['Event ID'] == idx]
#     for _, arow in _df_assoc.iterrows():
#         _sql = """
#             SELECT arid, TrueTime.getEpoch(datetime, 'UNIX') FROM arrival 
#             WHERE net = %(network)s 
#                 AND sta = %(station)s 
#                 AND iphase = %(iphase)s 
#                 AND datetime BETWEEN TrueTime.putEpoch(%(atime)s, 'UNIX') - 1
#                     AND TrueTime.putEpoch(%(atime)s, 'UNIX') + 1;
#         """
#         _n, _s = arow['Station Name'].split('.')
#         if arow['Phase Type'] == 0:
#             iphase = 'P'
#         elif arow['Phase Type'] == 1:
#             iphase = 'S'
#         else:
#             breakpoint()
#         _var = {'atime': pd.Timestamp(arow['Pick Time (UTC)']).timestamp(),
#                 'network': _n,
#                 'station': _s,
#                 'iphase': iphase}
#         cur.execute(_sql, _var)
#         result = cur.fetchall()
#         breakpoint()