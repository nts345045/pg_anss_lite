-- ASSOCAMO TABLE PARAMETRIC SCHEMA
-- Association of Amplitude and Origin entries in the ANSS/CISN database parametric schema
-- lightly adapted for SQLite by modifying the lddate column definition
-- auth: Renate Hartog
-- editor: Nathan T. Stevens
-- orgs: PNSN / AQMS-SWG
-- license: CC-1.0
 CREATE TABLE ASSOCAMO 
 (	ORID BIGINT, 
	AMPID BIGINT, 
	COMMID BIGINT, 
	AUTH VARCHAR(15) NOT NULL , 
	SUBSOURCE VARCHAR(8), 
	DELTA DOUBLE PRECISION, 
	SEAZ DOUBLE PRECISION, 
	RFLAG VARCHAR(2), 
	LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP), 
	 CONSTRAINT ASSOCAMO01 CHECK (seaz >= 0.0 and seaz <= 360.0) , 
	 CONSTRAINT ASSOCAMO02 CHECK (delta >=0.0) , 
	 CONSTRAINT ASSOCAMO03 CHECK (rflag in ('a','h','f','A','H','F')) , 
	 CONSTRAINT ASSOCAMOKEY01 PRIMARY KEY (ORID, AMPID) 
 ); 
