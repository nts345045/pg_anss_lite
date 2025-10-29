"""
script: ingest_catalog_ver_3.py
auth: Nathan T. Stevens
org: PNSN
license: CC-1.0
purpose: This script converts ANSS schema adjacent origin data from
    machine learning ensemble picks (ELEP) for the Cascadia offshore
    OBS study led by H. Bito and M. Denolle (University of Washington), 
    and in collaboration with Ian McBrearty (Stanford) and other Stanford
    colleagues.

Note on time format for the ANSS parametric schema
 - datetime: datetime values are in NOMINAL / GPS time and 
    DO NOT INCLUDE LEAP SECONDS. If you are using the PostgreSQL
    formatted database/server, use the `TrueTime.getEpoch(datetime, 'UNIX')`
    command in your SQL `SELECT` statements to read out TRUE TIME 
    values that include leap seconds.

Notes on alterations to data to fit the ANSS ORIGIN table schema
 - depth: GraphDD (+coherence) produced some origin depths with
       unrealistically large elevations (> 10 km). Depths for these
       air-quakes are hard set to -10 (km below sea level) in the 
       database ORIGIN table
 - quality: Detection values for Genie/GraphDD in this study
    are in the range [0, 2], whereas the ANSS parametric schema only
    allows `quality` values in the range [0, 1]. Detection values were
    divided by 2 to conform to the ANSS parameteric schema for the
    ORIGIN table

CISN/ANSS Parametric Schema Documentation:
   https://ncedc.org/db/Documents/NewSchemas/PI/v1.6.4/PI.1.6.4/index.htm

"""
from pathlib import Path
from getpass import getpass
import psycopg2
import pandas as pd
from tqdm import tqdm
from obspy import UTCDateTime

ROOT = Path(__file__).parent.parent.parent
DATA_DIR = ROOT/'data'/'cascadia'

PGDB = {'host':'localhost',
        'port': '5432',
        'dbname': 'offshore_ml'}

print('Provide user name for "offshore_ml" database:')
user = input()
conn = psycopg2.connect(**PGDB, user=user, password=getpass(f'Provide password for database user {user}'))

df_orig_in = pd.read_csv(DATA_DIR/'picks_from_phase_picker'/'origin_2010_2015_reloc_cog_ver3.csv')
df_orig_in = df_orig_in.rename(columns={'Unnamed: 0':'iorid'})

df_orig = pd.read_csv(DATA_DIR/'Cascadia_relocated_catalog_ver_3.csv',
                      index_col='Event ID')
df_orig_coh = pd.read_csv(DATA_DIR/'Cascadia_relocated_catalog_ver_3_waveform_coherency.csv',
                      index_col='Event ID')
# df_pick = pd.read_csv(DATA_DIR/'Cascadia_relocated_catalog_picks_ver_3.csv',
#                       index_col='Pick ID')
breakpoint()
cur = conn.cursor()

orid_base = 90000000
evid_base = 90000000

for evid, row_in in tqdm(df_orig_in.iterrows(), total=len(df_orig_in)):
    # Ingest non-coherence origin first
    sql = """
        INSERT INTO origin 
         (orid, evid, datetime, lat, lon, depth, 
          algorithm, algo_assoc, auth, subsource,
          wrms, erhor, sdep, totalarr, nbs, quality, rflag,
          gap) 
        VALUES 
         (%(orid)s, %(evid)s, TrueTime.putEpoch(%(truetime)s, 'UNIX'), 
          %(lat)s, %(lon)s, %(depth)s, %(algorithm)s, %(algo_assoc)s, %(auth)s,
          %(subsource)s, %(wrms)s, %(erhor)s, %(sdep)s, %(totalarr)s, %(nbs)s, %(quality)s, %(rflag)s, %(gap)s);
          """
    row = df_orig.loc[evid]
    var = {'orid': orid_base + (row_in.iorid*10) + 2,
           'evid': evid_base + evid,
           'truetime': UTCDateTime(row['Origin Time (UTC)']).timestamp,
           'lat': float(row['Latitude']),
           'lon': float(row['Longitude']),
           'depth': float(row['Depth (km)']),
           'algorithm': 'gdd',
           'algo_assoc': 'genie',
           'auth': 'Stanford',
           'subsource': 'IMcB',
           'wrms': float(row['RMS Residual (s)']),
           'erhor': float(row['Horizontal Uncertainity (km)']),
           'sdep': float(row['Uncertainity (km)']),
           'totalarr': int(row['Num. P'] + row['Num. S']),
           'nbs': int(row['Num. S']),
           'quality': float(row['Detection Value'])/2,
           'rflag': 'A',
           'gap': row_in.gap}
    if var['depth'] < -10:
        var['depth'] = 10
    try:
        cur.execute(sql, var)
    except psycopg2.Error as e:
        print(e)
        conn.rollback()
        breakpoint()    

    sql = """
        INSERT INTO origin 
         (orid, evid, datetime, lat, lon, depth, 
          algorithm, algo_assoc, auth, subsource,
          wrms, erhor, sdep, totalarr, nbs, quality, rflag) 
        VALUES 
         (%(orid)s, %(evid)s, TrueTime.putEpoch(%(truetime)s, 'UNIX'), 
          %(lat)s, %(lon)s, %(depth)s, %(algorithm)s, %(algo_assoc)s, %(auth)s,
          %(subsource)s, %(wrms)s, %(erhor)s, %(sdep)s, %(totalarr)s, %(nbs)s, %(quality)s, %(rflag)s);
          """
    # Ingest coherence solution next
    _row_coh = df_orig_coh.loc[evid]
    var = {'orid': orid_base + (row_in.iorid*10) + 3,
           'evid': evid_base + evid,
           'truetime': UTCDateTime(_row_coh['Origin Time (UTC)']).timestamp,
           'lat': float(_row_coh['Latitude']),
           'lon': float(_row_coh['Longitude']),
           'depth': float(_row_coh['Depth (km)']),
           'algorithm': 'gddcoh',
           'algo_assoc': 'genie',
           'auth': 'Stanford',
           'subsource': 'IMcB',
           'wrms': float(_row_coh['RMS Residual (s)']),
           'erhor': float(_row_coh['Horizontal Uncertainity (km)']),
           'sdep': float(_row_coh['Uncertainity (km)']),
           'totalarr': int(_row_coh['Num. P'] + _row_coh['Num. S']),
           'nbs': int(_row_coh['Num. S']),
           'quality': float(_row_coh['Detection Value'])/2,
           'rflag': 'A'} 
    if var['depth'] < -10:
        var['depth'] = -10
    try:
        cur.execute(sql, var)
    except psycopg2.Error as e:
        print(e)
        conn.rollback()
        breakpoint()

    # Create event entry with gddcoh solution as the preferred origin
    sql = """
        INSERT INTO event 
            (evid, prefor, auth, subsource, etype, selectflag, version) 
        VALUES 
            (%(evid)s, %(prefor)s, %(auth)s, %(subsource)s, %(etype)s, %(selectflag)s, %(version)s);
          """
    var = {'evid': evid_base + evid,
           'prefor': orid_base + (row_in.iorid*10) + 3,
           'auth': 'Stanford',
           'subsource': 'IMcB',
           'etype': 'eq',
           'selectflag': 0,
           'version': 3}
    try:
        cur.execute(sql, var)
    except psycopg2.Error as e:
        print(e)
        conn.rollback()
        breakpoint()
    
    conn.commit()

    # # Get used picks
    # _dfp = df_pick[df_pick['Event ID'] == evid]
    # for _pid, prow in _dfp.iterrows():
    #     sqlarr = """
    #         INSERT INTO arrival 
    #             (arid, datetime, sta, net, auth, subsource, 
    #              iphase, )
    #         """


    #     sqlaro = """
    #         INSERT INTO assocaro 
    #             (orid, arid, auth, subsource, iphase, timeres) 
    #         VALUES
    #             (%(orid)s, %(arid)s, %(auth)s, %(subsource)s, %(iphase)s, %(timeres)s);
    #           """

    # breakpoint()
    # next_orid += 1
    # next_evid += 1




