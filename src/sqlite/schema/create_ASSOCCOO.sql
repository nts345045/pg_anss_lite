-- ASSOCCOM TABLE PARAMETRIC SCHEMA
-- Association of Coda and Origin entries in the ANSS/CISN database parametric schema
-- lightly adapted for SQLite by modifying the lddate column definition
-- auth: Renate Hartog
-- editor: Nathan T. Stevens
-- orgs: PNSN / AQMS-SWG
-- license: CC-1.0
 CREATE TABLE ASSOCCOO 
 (	ORID BIGINT, 
	COID BIGINT, 
	COMMID BIGINT, 
	AUTH VARCHAR(15) NOT NULL , 
	SUBSOURCE VARCHAR(8), 
	RFLAG VARCHAR(2), 
	DELTA DOUBLE PRECISION, 
	SEAZ DOUBLE PRECISION, 
	LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'
       ), 
	 CONSTRAINT ASSOCCOOKEY04 CHECK (rflag in ('a','h','f','A','H','F')) , 
	 CONSTRAINT ASSOCCOOKEY01 PRIMARY KEY (ORID, COID) 
 ); 
