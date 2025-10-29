# pg_anss_lite
A limited scope abstraction of the ANSS/CISN parametric database schema for PostgreSQL and
utilities for copying the PostgreSQL database contents to a SQLite database and subsequent
interactions.

## License & Attribution 
This repository is distributed under a Creative Commons Zero (CC-1.0) license (see attached).

If you find PostgreSQL/ANSS schema elements of the repository useful, consider citing [Hartog et al. (2020)](https://doi.org/10.1785/0220190219).  

If other aspects prove useful, consider citing the open-source software package(s) authors'.

### Author / Editor
 - Nathan T. Stevens (Pacific Northwest Seismic Network / University of Washington)

# Environment 
A `environment.yml` file is provided for creating conda environment for the python-facilitated
elements of this repository.

It assumes that you already have a running PostgreSQL server and access to a superuser account
on that server. To install PostgreSQL see their [downloads](https://www.postgresql.org/download/) page.

For locally hosted PostgreSQL servers on Mac with little overhead, consider the [postgres.app](https://postgresapp.com)! 

# Using this repository
The `src` directory contains two subdirectories that largely work to initialize databases in `postgresql` and `sqlite`, respectively.

## PostgreSQL Database Initialization
I structured it such that the reference database is the PostgreSQL one, so start by standing up a postgres database using the 
`src/postgresql/initdb.py` script.

## PostgreSQL Database Population
The `src/cascadia` directory contains example workflows for aggregating results from distributed, semi-structured analyses of
seismic data into a single, organized database. They were run in the following order:
 - ingest_all_picks.py
 - ingest_catalog_ver_3.py
 - ingest_assoc_ver_3.py
 - ingest_morton.py

NOTE: Input CSVs are not provided as part of this repository! These are strictly provided as an example of how you might migrate
your data into an ANSS-formatted PostgreSQL database.

## 'Exporting' to SQLite for Portability
The `src/sqlite` directory contains a driver script `copy_to_sqlite.py` for copying from the PostgreSQL database `offshore_ml` generated in the
`cascadia` example into a SQLite database file `cascadia_obs.db`. 

This is accompanied by the `query_helpers.py` module that has example methods for interacting with the database using python, and the `truetime.py` 
module that contains methods for converting from database `datetime` values into UTC datetime values.


# Notes on PostgreSQL server configuration settings 
Loosing data can be heartbreaking, but PostgreSQL can help! 

With a little modification to the default PostgreSQL server configurations, you can take advantage of Write Ahead Log (WAL) archiving that allows for [Point-In-Time Recovery (PITR)](https://www.postgresql.org/docs/current/continuous-archiving.html). The key arguments that need to be updated are:
 - archive_mode = `on`
 - archive_command (see documentation)

These can be done directly in the `postgresql.conf` file with a text editor or implemented using
`psql`. E.g., 
```
psql -U <my_superuser> -W -c "ALTER SYSTEM SET archive_mode = 'on';"
```

Although `wal_level = 'replica'` is the default setting, you may consider upgrading to `wal_level = 'logical'` as this allows logical replication to other PostgreSQL databases/servers. 