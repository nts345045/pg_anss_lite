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
    TEID BIGINT,
    WFPID BIGINT,
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
    CONSTRAINT DETECTIONKEY02 FOREIGN KEY (TEID) REFERENCES template(teid),
    CONSTRAINT DETECTIONKEY03 FOREIGN KEY (WFPID) REFERENCES wfproc(wfpid)
);

COMMENT ON TABLE DETECTION IS "Matched filter candidate event detection table encapsulating an EQcorrscan 'detection' object";
COMMENT ON COLUMN DETECTION.DEID IS "Unique numerical identifier for each detection (PRIMARY KEY)";
COMMENT ON COLUMN DETECTION.TEID IS "Numercal identifier for the parent template for this detection (FOREIGN KEY)";
COMMENT ON COLUMN DETECTION.WFPID IS "Numerical identifier for the waveform preprocessing workflow for this detection (FORIEGN KEY)"
COMMENT ON COLUMN DETECTION.NAME IS "Name of the detection";
COMMENT ON COLUMN DETECTION.DATETIME IS "Detection origin time (differs from detection time)";
COMMENT ON COLUMN DETECTION.NBC IS "Number of channels in the detection";
COMMENT ON COLUMN DETECTION.DVAL IS "Detection value";
COMMENT ON COLUMN DETECTION.THRESH IS "Detection threshold";
COMMENT ON COLUMN DETECTION.DTYPE IS "Detection type";
COMMENT ON COLUMN DETECTION.TTYPE IS "Threshold type";
COMMENT ON COLUMN DETECTION.THRESH_IN IS "Input threshold value";
COMMENT ON COLUMN DETECTION.DT_D0 IS "Detection time minus detection origin time (DATETIME)";
COMMENT ON COLUMN DETECTION.DT_T0 IS "DATETIME minus origin time of the detection's parent template";
COMMENT ON 