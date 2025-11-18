#!/bin/bash
# script: populate_aqms_db_pg.sh
# editor: Nathan T. Stevens, 
# auths: Renate Hartog, Paul Freiburg, Victor Kress
# editor org: PNSN
# license: CC0-1.0
# purpose: This provides a quick-start option for populating the ANSS schema into a pre-initiaized PostgreSQL server
# that does not have the specified DB_NAME database in existance

PG_PORT=5454
DB_NAME='tahoma'
PG_HOST='localhost'
EVID_SEQ_START=100000009
SEQ_START=9
SEQ_INC=10


PWD=$(pwd)
# Stack Overflow Attribution: SCRIPT_DIR syntax
# Source - https://stackoverflow.com/a
# Posted by dogbane, modified by community. See post 'Timeline' for change history
# Retrieved 2025-11-10, License - CC BY-SA 4.0 
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Repo Root
ROOT=$SCRIPT_DIR/../postgresql/aqms-db-pg

# Create Database as user postgres
psql -p $PG_PORT -h $PG_HOST -U postgres -c "CREATE DATABASE $DB_NAME WITH TABLESPACE pg_default;"
# Install PostGIS extension
psql -p $PG_PORT -h $PG_HOST -U postgres -d $DB_NAME -c "CREATE EXTENSION postgis;"
# Create Roles on database
psql -p $PG_PORT -h $PG_HOST -U postgres -d $DB_NAME -f $ROOT/create/users/create_roles.sql
# Create Users on database with default passwords
psql -p $PG_PORT -h $PG_HOST -U postgres -d $DB_NAME -f $ROOT/create/users/create_users.template
# Create Sequences as user `trinetdb` 
declare -a seqnames=("EVSEQ" "EQSEQ" "SPECTRALAMPSEQ")
for i in "${seqnames[@]}"
do
    psql -p $PG_PORT -h $PG_HOST -U trinetdb -d $DB_NAME -c "CREATE SEQUENCE $i START WITH $EVID_SEQ_START INCREMENT BY $SEQ_INC NO MINVALUE NO MAXVALUE CACHE 1;"
done

declare -a seqnames=("AMPSEQ" "AMPSETSEQ" "ARSEQ"  \
                    "CATSEQ" "COMMSEQ" "COSEQ"  \
                    "MAGSEQ" "MECSEQ" "MECDATASEQ"  \
                    "MECFREQSEQ" "ORSEQ" "FISEQ"  \
                    "SDSEQ" "WASEQ" "ABBSEQ" "COMSEQ"  \
                    "DCSEQ" "DMSEQ" "FORSEQ" "NTSEQ"  \
                    "POSEQ" "PZSEQ" "UNISEQ" "SIGSEQ"  \ 
                    "SUBSEQ" "TRIGSEQ" "REQSEQ"  \
                    "UNASSOCSEQ" "GAZSEQ")
for i in "${seqnames[@]}"
do
    psql -p $PG_PORT -h $PG_HOST -U trinetdb -d $DB_NAME -c "CREATE SEQUENCE $i START WITH $SEQ_START INCREMENT BY $SEQ_INC NO MINVALUE NO MAXVALUE CACHE 1;"
done
# Populate table schema
declare -a schema=("waveform" "parametric" "instrument_response" "hardware" "application")
for i in "${schema[@]}"
do
    cd $ROOT
    cd create/tables/${i}_schema/
    FILE=install_${i}_tables.sql
    psql -p $PG_PORT -h $PG_HOST -U trinetdb -d $DB_NAME -f $FILE
done
cd ../
psql -p $PG_PORT -h $PG_HOST -U trinetdb -d $DB_NAME -f grant_all_tables.sql

# Update Spectralampseq and eqseq
declare -a seqnames=("EQSEQ" "SPECTRALAMPSEQ")
for i in "${seqnames[@]}"
do
    psql -p $PG_PORT -h $PG_HOST -U trinetdb -d $DB_NAME -c "ALTER SEQUENCE $i START WITH $EVID_SEQ_START INCREMENT BY $SEQ_INC RESTART WITH $EVID_SEQ_START;"
done
# Install custom types as user `code`
psql -p $PG_PORT -h $PG_HOST -U code -d $DB_NAME -c "CREATE TYPE latlon AS (lat numeric(9,7), lon numeric(10,7));"

# Install stored procedures
cd $ROOT/storedprocedures
declare -a users=("code" "postgres" "trinetdb")
for i in "${users[@]}"
do
    psql -p $PG_PORT -h $PG_HOST -U $i -d $DB_NAME -f install_as_user_${i}.sql
done

# Populate indices as `trinetdb`
cd $ROOT/create/indexes
psql -p $PG_PORT -h $PG_HOST -U trinetdb -d $DB_NAME -f aqms_indexes.sql
