-- REMARK TABLE PARAMETRIC SCHEMA
-- Table definition for a table that holds indexed remarks that can be referenced
-- to in number of other tables via the `commid` key.
-- auth: Renate Hartog
-- editor: Nathan T. Stevens
-- orgs: PNSN / AQMS-SWG
-- license: CC 1.0
 CREATE TABLE REMARK 
 (	COMMID BIGINT, 
	LINENO BIGINT NOT NULL , 
	REMARK VARCHAR(80), 
	LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP), 
	 CONSTRAINT REMARK01 CHECK (commid > 0) , 
	 CONSTRAINT REMARK02 CHECK (lineno > 0) , 
	 CONSTRAINT REMKEY01 PRIMARY KEY (COMMID, LINENO) 
 ); 
