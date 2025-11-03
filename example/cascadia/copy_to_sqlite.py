"""
script: copy_to_sqlite.py
auth: Nathan T. Stevens
org: PNSN
license: CC-1.0
purpose:
    This script connects to an existing PostgreSQL database and copies the table contents of specified tables
    to a new SQLite database. 

    If the SQLite database does not exist, it is created and populated with the AQMS schema tables used in
    this repository, minus the epochtimebase table schema.

"""
import psycopg2, os, glob
from sqlalchemy import create_engine, MetaData, Table, insert
from pathlib import Path
import pandas as pd
from tqdm import tqdm

ROOT = Path(__file__).parent.parent.parent
DBLITE = ROOT/'db'/'cascadia_obs2.db'
SCHEMADIR = Path(__file__).parent/'schema'
tables = ['event','origin','assocaro','netmag','remark','leap_seconds']
# conn_lite = sqlite3.connect(str(DBLITE))

if not os.path.isfile(DBLITE):
    print('Creating SQLite database and initializing database schema')
    for file in glob.glob(str(SCHEMADIR/'create_*.sql')):
        cmd = f'sqlite3 {DBLITE} < {file}'
        print(cmd)
        os.system(cmd)

print('Connecting to databases')
engine = create_engine(f'sqlite:////{DBLITE}', echo=False)
conn_pg = psycopg2.connect(host='localhost',port=5432,dbname='offshore_ml')

metadata = MetaData()

for tname in tables:
    print(f'Transferring table {tname}')
    df = pd.read_sql(f'SELECT * FROM {tname};', con=conn_pg)
    # Create SQLite/SQLalchemy table object for this table
    table = Table(tname, metadata, autoload_with=engine)
    with engine.connect() as conn:
        insert_data = []
        for _, row in tqdm(df.iterrows(), total=len(df)):
            values = {_k.upper(): _v for _k, _v in row.items()}
            insert_data.append(values)
            # stmt = insert(table).values(**values)
        conn.execute(insert(table), insert_data)



with conn_pg.cursor() as cur:
    cur.execute("SELECT MIN(arid), MAX(arid) FROM arrival;")
    first_arid, last_arid = cur.fetchall()[0]

next_arid = first_arid - 1
print("Transferring ARRIVAL in batch mode")

while True:
    print(f'Batch starting after ARID {next_arid}')
    df = pd.read_sql(f'SELECT * FROM arrival WHERE arid > {next_arid} ORDER BY arid LIMIT 100000;', con=conn_pg)
    if len(df) > 0:
        table = Table('arrival', metadata, autoload_with=engine)
        with engine.connect() as conn:
            insert_data = []
            for _, row in tqdm(df.iterrows(), total=len(df)):
                values = {_k.upper(): _v for _k, _v in row.items()}
                insert_data.append(values)
                
            #    stmt = insert(table).values(**values)
            conn.execute(insert(table), insert_data)  
        next_arid = df.arid.max()
    elif next_arid < last_arid:
        next_arid += 1
    else:
        break          
    #     # Replace table on first iteration
    #     if first_time:
    #         if_exists = 'replace'
    #     # Append on all subsequent iterations
    #     else:
    #         if_exists = 'append'
    #     df.to_sql('arrival', con=conn_lite, if_exists=if_exists, chunksize=10000)
    #     next_arid = df.arid.max()
    # # If it somehow gets hung, increment up (note - this SHOULD NOT HAPPEN)
    # elif next_arid < last_arid:
    #     next_arid += 1
    # # If 
    # else:
    #     break
        # for _, row in tqdm(df.iterrows(), total=len(df)):
        #     table.insert(row.to_dict())
        #     breakpoint()
#         _sql = f"""
#             INSERT INTO {tname} 
#                 ({', '.join(list(row.index))}) 
#             VALUES 
#                 (:{', :'.join(list(row.index))});
#                 """
#         _var = row.to_dict()
#         breakpoint()
#         try:
#             conn_lite.execute(text(_sql), _var)
#         except:
#             breakpoint()
# #     .to_sql(tname, con=conn_lite, if_exists='replace', chunksize=10000)

    