-- EVENT TABLE Schema
-- This is an exact copy of the CISN EVENT TABLE for AQMS installations
-- Refer to the CISN parametric model for more information on fields
-- Editor commented out CONSTRAINT EVKEY02 for this simplified version
-- Author: Renate Hartog
-- Editor: Nathan T. Stevens
-- org: PNSN / AQMS-SWG
-- license: CC 1.0

 CREATE TABLE EVENT 
 (	EVID BIGINT, 
	PREFOR BIGINT, 
	PREFMAG BIGINT, 
	PREFMEC BIGINT, 
	COMMID BIGINT, 
	AUTH VARCHAR(15) NOT NULL , 
	SUBSOURCE VARCHAR(8), 
	ETYPE VARCHAR(2) NOT NULL , 
	SELECTFLAG SMALLINT, 
	VERSION BIGINT DEFAULT (0) NOT NULL , 
	LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'
       ), 
	CONSTRAINT EVENT02 CHECK (evid > 0) , 
	 CONSTRAINT EVKEY01 PRIMARY KEY (EVID)
 );
-- REMOVED FOR SIMPLIFIED INSTALLATION
-- 	CONSTRAINT EVKEY02 FOREIGN KEY (ETYPE) references EventType(etype) 
--  ); 