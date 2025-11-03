"""
script: src/postgresql/initdb.py
auth: Nathan T. Stevens
org: PNSN
license: CC-1.0
purpose: This script launches a user prompt to provide the relevant connection parameters
    and credentials to create a new database on a pre-existing, currently running PostgreSQL server.

    It then creates the database and populates select parametric schema tables and stored procedures
    used in AQMS (ANSS Quake Management System) production systems as defined by the contents
    of the accompanying `schema` and `stored_procedures` directories, respectively.
"""

from pathlib import Path
import psycopg2, glob, os
from getpass import getpass

ROOT = Path(__file__).parent

print("Provide the host name / IP address for your PostgreSQL server: [e.g., localhost]")
host = input()
print("Provide the port for your PostgreSQL server: [e.g., 5432]")
port = input()
print("Provide the name of a server superuser: [e.g., postgres]")
user = input()

print("Provide the name of the database you wish to create:")
dbname = input()

# Create database
print('psql will ask you for that password one more time:')
cmd = f'psql -U {user} -h {host} -p {port} -W -c "CREATE DATABASE {dbname};"'
os.system(cmd)

# Open connection to new database (and have implicit connection closure if script ends or fails)
with psycopg2.connect(host=host, port=port, user=user, password=getpass(f"Provide the password for user `{user}`:"), dbname=dbname) as conn:

    # Initialize parametric tables
    sqlfiles = glob.glob(str(ROOT/'schema'/'create_*.sql'))
    for sqlfile in sqlfiles:
        with conn.cursor() as cur:
            cur.execute(open(sqlfile, 'r').read())
            
    # Initialize stored procedures
    with conn.cursor() as cur:
        cur.execute(open(str(ROOT/'stored_procedures'/'truetime.sql'), 'r').read())
        cur.execute(open(str(ROOT/'stored_procedures'/'Init_Leap_Secs.sql'), 'r').read())

    # Commit alterations
    conn.commit()
