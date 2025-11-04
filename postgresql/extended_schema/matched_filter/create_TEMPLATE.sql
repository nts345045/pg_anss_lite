-- TEMPLATE TABLE PARAMETRIC SCHEMA
-- Author: Nathan T. Stevens
-- Org: PNSN
-- License: CC-1.0
--
-- This table extends the CISN parametric schema to describe all relevant
-- parameters used to create EQcorrscan templates used for template matching.

-- PARAMETERS
-- TEID - TEmplate IDentifier (PRIMARY KEY)
-- ORID - ORigin IDentifier from which this template was generated
-- NAME - Name given to the template
-- SAMP_RATE - sampling rate used for this template
-- LOWCUT - Filter lowcut frequency [Hz]
-- HIGHCUT - Filter highcut frequency [Hz]
-- FILT_ORDER - Filter order
-- LENGTH - Length of the template including PREPICK [sec]
-- PREPICK - Amount of reference-time data to include in template [sec]
-- PROC_LEN - processing length for waveforms prior to template construction
--     and the lenght of waveform chunks to preprocess prior to matched filter detections
-- SNR_MIN - minimum SNR (simple ratio, not deciBells) for template elements
-- DELAYED - Are template elements referenced to the origin time (0) or pick time (1)
-- SSC - Shorthand for skip_short_channels (True = 1 / False = 0)
-- IBD - Shorthand for ignore_bad_data (True = 1 / False = 0)
-- SNR_MIN_AUTO - Additional SNR check (simple ratio) for picks that are not
--     human reviewed (i.e., not arrival.rflag = 'H')
-- FPATH - file path to template *.tgz archive
-- FNAME - file name of the *.tgz archive containing this template
-- LDDATE - datetime this entry was loaded into the database

CREATE TABLE TEMPLATE
(   TEID BIGINT,
    EVID BIGINT,
    ORID BIGINT,
    NAME VARCHAR(40),
    SAMP_RATE REAL,
    LOWCUT REAL,
    HIGHCUT REAL,
    FILT_ORDER SMALLINT,
    LENGTH REAL,
    PREPICK REAL,
    PROC_LEN REAL,
    SNR_MIN REAL,
    DELAYED SMALLINT DEFAULT (1) NOT NULL,
    SSC SMALLINT DEFAULT (1) NOT NULL,
    IBD SMALLINT DEFAULT (1) NOT NULL,
    SNR_MIN_AUTO REAL,
    FPATH VARCHAR(120),
    FNAME VARCHAR(80),
    LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'
),
    CONSTRAINT TEMPLATE01 CHECK (teid > 0),
    CONSTRAINT TEMPLATE02 CHECK (orid > 0),
    CONSTRAINT TEMPLATEKEY01 PRIMARY KEY (TEID),
    CONSTRAINT TEMPLATEKEY02 FOREIGN KEY (EVID) REFERENCE event(evid)
    CONSTRAINT TEMPLATEKEY03 FOREIGN KEY (ORID) REFERENCE origin(orid)
);
