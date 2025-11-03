-- AMP TABLE PARAMETRIC SCHEMA
-- Database table schema for seismic amplitude observations for the ANSS/CISN parametric schema
-- auth: Renate Hartog
-- editor: Nathan T. Stevens
-- orgs: PNSN / AQMS-SWG
-- license: CC-1.0
 
 CREATE TABLE AMP
 (	AMPID BIGINT, 
	COMMID BIGINT,
	DATETIME DOUBLE PRECISION, 
	STA VARCHAR(6) NOT NULL , 
	NET VARCHAR(8), 
	AUTH VARCHAR(15) NOT NULL ,
	SUBSOURCE VARCHAR(8), 
	CHANNEL VARCHAR(8),
	CHANNELSRC VARCHAR(8), 
	SEEDCHAN VARCHAR(3), 
	LOCATION VARCHAR(2), 
	IPHASE VARCHAR(8),
	AMPLITUDE DOUBLE PRECISION NOT NULL , 
	AMPTYPE VARCHAR(8),
	UNITS VARCHAR(4) NOT NULL ,
	AMPMEAS VARCHAR(1),
	ERAMP DOUBLE PRECISION,
	FLAGAMP VARCHAR(4),
	PER DOUBLE PRECISION,
	SNR DOUBLE PRECISION, 
	TAU DOUBLE PRECISION, 
	QUALITY DOUBLE PRECISION,
	RFLAG VARCHAR(2),
	CFLAG VARCHAR(2),
	WSTART DOUBLE PRECISION NOT NULL ,
	DURATION DOUBLE PRECISION,
	LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'), 
	 CONSTRAINT AMP02 CHECK (amplitude >0) , 
	 CONSTRAINT AMP04 CHECK (AMPTYPE IN ('C','WA','WAS','PGA','PGV','PGD','WAC','WAU','IV2','SP.3','SP1.0','SP3.0', 'ML100','ME100','EGY','HEL','WASF','M0')) ,
	 CONSTRAINT AMP01 CHECK (ampid > 0) ,
	 CONSTRAINT AMP03 CHECK (ampmeas in ('0','1')) ,
	 CONSTRAINT AMP06 CHECK (eramp >= 0.0) ,
	 CONSTRAINT AMP07 CHECK (flagamp in ('P','S','R','PP','ALL','SUR')) ,
	 CONSTRAINT AMP08 CHECK (per > 0.0) ,
	 CONSTRAINT AMP09 CHECK (tau > 0.0) ,
	 CONSTRAINT AMP10 CHECK (units in ('c','s','mm','cm','m','ms','mss','cms','cmss','cmcms','mms','mmss','mc','nm','e','iovs','spa','none','dycm')) ,
	 CONSTRAINT AMP11 CHECK (quality >=0.0 and quality <=1.0) ,
	 CONSTRAINT AMP12 CHECK (rflag in ('a','h','f','A','H','F')) ,
	 CONSTRAINT AMP13 CHECK (cflag in ('bn', 'os','cl','BN','OS','CL')) ,
	 CONSTRAINT AMPKEY01 PRIMARY KEY (AMPID)
	);

COMMENT ON TABLE AMP IS 'Amplitude Measurements';
COMMENT ON COLUMN AMP.AMPID IS 'Unique numerical identifier of amplitude measurement (primary key)';
COMMENT ON COLUMN AMP.COMMID IS 'implied foreign key to the REMARK table';
COMMENT ON COLUMN AMP.DATETIME IS 'Timestamp for amplitude measurement';
COMMENT ON COLUMN AMP.STA IS 'Station code';
COMMENT ON COLUMN AMP.NET IS 'Network code';
COMMENT ON COLUMN AMP.AUTH IS 'Authority code (usually same as PDL source code)';
COMMENT ON COLUMN AMP.SUBSOURCE IS 'source of amplitude measurement, e.g. RT1, or Jiggle'

