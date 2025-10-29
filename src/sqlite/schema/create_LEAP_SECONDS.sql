-- LEAP_SECONDS PARAMETRIC SCHEMA
-- Table to containmappings between nominal times and True/UTC times
-- auth: Renate Hartog
-- editor: Nathan T. Stevens
-- org: PNSN / AQMS-SWG
-- license: CC-1.0
 CREATE TABLE LEAP_SECONDS 
 (	S_NOMINAL BIGINT, 
	E_NOMINAL BIGINT, 
	S_TRUE BIGINT, 
	E_TRUE BIGINT, 
	LS_COUNT BIGINT 
 ); 
