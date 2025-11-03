"""
script: sqlite/initdb.py
auth: Nathan T. Stevens
org: PNSN / AQMS-SWG
license: CC-1.0
purpose: This script provides an interactive prompt for
    initializing a SQLite database and populating it with
    a trucated version of the ANSS parametric schema

    See included tables in `sqlite/schema/create_*.sql`

    It also populates the leap_seconds table using data in:
    `sqlite/data/leap_seconds.csv`

"""

import os, glob
from pathlib import Path
import sqlite3

ROOT = Path(__file__).parent.parent.parent
SCHEMA = ROOT/'sqlite'/'schema'
LEAPCSV = ROOT/'sqlite'/'table_data'/'leap_seconds.csv'

default_db_path = ROOT/'db'
default_db_name = 'test.db'
prompt1 = 'Provide the absolute path for your new SQLite database'
prompt1 += f'\nDefault: "{default_db_path}"'
dbpath = input(prompt1)

if dbpath == '':
    dbpath = default_db_path
prompt2 = 'Provide the name of your new SQLite database (.db) will be appended if missing'
prompt2 += f'\nDefault: "{default_db_name}"'

dbname = input(prompt2)
if dbname == '':
    dbname = default_db_name
elif dbname[-3:] != '.db':
    dbname += '.db'
else:
    pass

# Path + DB name
pdb = Path(dbpath)/dbname

# Create directory structure if not present
if not os.path.exists(dbpath):
    print(f'Creating database-housing directory: {dbpath}')
    os.makedirs(dbpath)

# Safeguard database against being overwritten
if os.path.isfile(pdb):
    prompt3 = f'''Database file already exists!\n
                 "{pdb}" \n\n                
                 If you wish to delete it.\n
                 Please type in the database name:\n'''
    confirmation = input(prompt3)
    if confirmation != dbname:
        raise FileExistsError(f'Aborting overwrite of "{pdb}"')
    else:
        print(f'Proceeding with delete of "{pdb}"')
        os.system(f'rm {pdb}')

# Get list of schema files
sf_list = glob.glob(str(SCHEMA/'create_*.sql'))
# Install schema
for _sf in sf_list:
    _fname = Path(_sf).parts[-1]
    print(f'RUNNING {_fname} ON {dbname}')
    cmd = f'sqlite3 {pdb} < {_sf}'
    os.system(cmd)


# sqlite3 connection
with sqlite3.connect(pdb) as conn:
    print('Connected to database - populating leap_seconds table')
    # Populate leap_seconds table
    with open(str(LEAPCSV), 'r') as _f:
        cur = conn.cursor()
        for _e, line in enumerate(_f.readlines()):
            line = line[:-1]
            if _e == 0:
                hdr = line
                continue
            sql = f'INSERT INTO leap_seconds ({hdr}) VALUES ({line});'
            try:
                cur.execute(sql)
            except:
                cur.close()
                conn.rollback()

                breakpoint()
        conn.commit()        
