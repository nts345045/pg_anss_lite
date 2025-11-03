"""
script: ingest_all_picks.py
auth: Nathan T. Stevens
org: PNSN
license: CC-1.0
purpose: This script converts SeisBench formatted phase arrivals from
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

Notes on alterations to data to fit the ANSS ARRIVAL table schema
 - deltim: for picks where the trigger onset and offset times are documented,
    the `deltim` column in the ARRIVAL table is used to convey the time difference
    in seconds (offset - onset) for the trigger
 - quality: pick maximum probabilities are stored in the `quality` column of the
    ARRIVAL table. Some picks did not document maximum probabilities, whereas others
    recorded an `inf` value. 
         - For missing max_prob, a uniform value of 0.01 is used
         - For max_prob = 'inf', a uniform value of 0.0 is used

         
CISN/ANSS Parametric Schema Documentation:
   https://ncedc.org/db/Documents/NewSchemas/PI/v1.6.4/PI.1.6.4/index.htm

"""

from pathlib import Path
from getpass import getpass
import psycopg2
import pandas as pd
from obspy import UTCDateTime
from tqdm import tqdm
import numpy as np

ROOT = Path(__file__).parent.parent.parent
DATA_DIR = ROOT/'data'/'cascadia'

PGDB = {'host':'localhost',
        'port': '5432',
        'dbname': 'offshore_ml'}

print('Provide user name for "offshore_ml" database:')
user = input()
conn = psycopg2.connect(**PGDB, user=user, password=getpass(f'Provide password for database user {user}: '))
print('LOADING BIG PICK FILE')
df_picks_all = pd.read_csv(DATA_DIR/'all_picks_all_regions_2010_2015_ver3.csv', index_col=[0])
print('DROPPING DUPLICATE ENTRIES')
pre_len = len(df_picks_all)
df_picks_all.drop_duplicates(keep='first', inplace=True)

cur = conn.cursor()
arid_base = 9000000000
cur.execute("SELECT max(arid) FROM arrival;")
last_arid = cur.fetchall()[0][0]
if last_arid is None:
    last_arid = arid_base - 1
else:
    df_picks_all = df_picks_all[df_picks_all.index > last_arid - arid_base]

print("SENDING TO DATABASE")
for arid, row in tqdm(df_picks_all.iterrows(), total=len(df_picks_all)):
    if arid + arid_base <= last_arid:
        continue
    sql = """
        INSERT INTO arrival 
            (arid, datetime, net, sta, seedchan, iphase, quality, deltim, auth, subsource, rflag) 
        VALUES 
            (%(arid)s, TrueTime.putEpoch(%(pick_time)s, 'UNIX'), %(network)s, 
             %(station)s, %(seedchan)s, %(label)s, %(quality)s, 
             %(deltim)s, 'UW', 'ELEP', 'A');
        """
    var = row.to_dict()
    if isinstance(row.band_inst, str):
        seedchan = row.band_inst + '?'
    else:
        seedchan = None

    if isinstance(row.trigger_onset, str) and isinstance(row.trigger_offset, str):
        deltim = UTCDateTime(row.trigger_offset) - UTCDateTime(row.trigger_onset)
    else:
        deltim = None

    if not np.isfinite(row.max_prob):
        if row.max_prob == float('inf'):
            quality = 0.0
        else:
            quality = 0.01
    else:
        quality = row.max_prob

    var.update({'arid': arid_base + arid,
                'seedchan': seedchan,
                'pick_time': UTCDateTime(row.pick_time).timestamp,
                'deltim': deltim,
                'quality': quality})
    
    # if not np.isfinite(var['max_prob']):
        # var['max_prob'] = 
    try:
        cur.execute(sql, var)
    except psycopg2.Error as e:
        print(e)
        conn.rollback()
        continue
    conn.commit()
