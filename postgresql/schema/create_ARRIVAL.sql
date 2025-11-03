-- ARRIVAL TABLE PARAMETRIC SCHEMA
-- Arrival table copied directly from the CISN/AQMS parametric scheama implemented
-- for PostgreSQL database backed AQMS installations. Editor added this header block.
-- Author: Renate Hartog
-- Editor: Nathan T. Stevens
-- org: PNSN / AQMS-SWG
-- license: CC 1.0

 CREATE TABLE ARRIVAL                         
 (	ARID BIGINT,                           
	COMMID BIGINT,                            
	DATETIME DOUBLE PRECISION NOT NULL ,                       
	STA VARCHAR(6) NOT NULL ,                         
	NET VARCHAR(8),                             
	AUTH VARCHAR(15) NOT NULL ,                            
	SUBSOURCE VARCHAR(8),                           
	CHANNEL VARCHAR(8),                            
	CHANNELSRC VARCHAR(8),                           
	SEEDCHAN VARCHAR(3),                           
	LOCATION VARCHAR(2),                           
	IPHASE VARCHAR(8),                            
	QUAL VARCHAR(1),                            
	CLOCKQUAL VARCHAR(1),                           
	CLOCKCORR BIGINT,                           
	CCSET SMALLINT,                            
	FM VARCHAR(2),                             
	EMA DOUBLE PRECISION,                             
	AZIMUTH DOUBLE PRECISION,                            
	SLOW DOUBLE PRECISION,                            
	DELTIM DOUBLE PRECISION,                            
	DELINC DOUBLE PRECISION,                            
	DELAZ DOUBLE PRECISION,                            
	DELSLO DOUBLE PRECISION,                            
	QUALITY DOUBLE PRECISION,                            
	SNR DOUBLE PRECISION,                             
	RFLAG VARCHAR(2),                            
	LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'
),                         
	 CONSTRAINT ARRIVAL01 CHECK (arid > 0) ,                     
	 CONSTRAINT ARRIVAL02 CHECK (azimuth >= 0.0 and azimuth <= 360.0) ,              
	 CONSTRAINT ARRIVAL03 CHECK (delaz > 0.0) ,                    
	 CONSTRAINT ARRIVAL04 CHECK (delinc >= 0.0) ,                    
	 CONSTRAINT ARRIVAL05 CHECK (delslo > 0.0) ,                    
	 CONSTRAINT ARRIVAL06 CHECK (deltim >= 0.0) ,                    
	 CONSTRAINT ARRIVAL07 CHECK (ema >= 0.0 and ema <= 90.0) ,                 
	CONSTRAINT ARRIVAL09 CHECK (qual in ('i','e','w','I','E','W')) ,               
	 CONSTRAINT ARRIVAL10 CHECK (slow >= 0.0) ,                    
	 CONSTRAINT ARRIVAL11 CHECK (snr > 0.0) ,                     
	 CONSTRAINT ARRIVAL12 CHECK (quality >=0.0 and quality <=1.0) ,
	CONSTRAINT ARRIVAL13 CHECK (ccset < 1) ,                     
	 CONSTRAINT ARRIVAL14 CHECK (rflag in ('a','h','f','A','H','F')) ,
	 CONSTRAINT ARKEY01 PRIMARY KEY (ARID) 
 );