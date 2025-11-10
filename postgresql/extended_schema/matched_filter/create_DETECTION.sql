-- DETECTION TABLE PARAMETRIC SCHEMA
-- Author: Nathan T. Stevens
-- Org: PNSN
-- License: CC-1.0
--
-- This table contains all the necessary information to reconstitute
-- an EQcorrscan `Detection` object in conjunction with data contained
-- on the TEMPLATE and DETARR tables
--
-- FIELDS
-- DEID - DEtection IDentifier
-- TEID - TEmplate IDentifier
-- NAME - Given name of the template from detection processing
-- DATETIME - Detection origin time (DIFFERS FROM DETECTION TIME - see DT_D0)
-- NBC - Number of channels in the detection
-- DVAL - detection value
-- THRESH - detection threshold value
-- DTYPE - type of detection
-- TTYPE - type of threshold
-- THRESH_IN - input threshold value
-- DT_D0 - time offset of the detection origin time and the detection time (det_time - DATETIME)
-- DT_T0 - time offset of the detection origin time and template origin time (detection(DATETIME) - template(DATETME))
-- FPATH - detection file path
-- FNAME - detection file name
-- LDDATE - datetime that this entry was first loaded into the database

CREATE TABLE DETECTION
(   DEID BIGINT,
    TEID BIGINT NOT NULL,
    NAME VARCHAR(30),
    DATETIME DOUBLE PRECISION NOT NULL,
    NBC SMALLINT,
    DVAL DOUBLE PRECISION NOT NULL,
    THRESH DOUBLE PRECISION,
    DTYPE VARCHAR(12),
    TTYPE VARCHAR(12),
    THRESH_IN DOUBLE PRECISION NOT NULL,
    DT_D0 DOUBLE PRECISION NOT NULL,
    DT_T0 DOUBLE PRECISION NOT NULL,
    FPATH VARCHAR(120),
    FNAME VARCHAR(100),
    LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    CONSTRAINT DETECTION01 CHECK (DEID > 0), 
    CONSTRAINT DETECTIONKEY01 PRIMARY KEY (DEID),
    CONSTRAINT DETECTIONKEY02 FOREIGN KEY (TEID) REFERENCES template(teid)
);