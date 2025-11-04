-- ASSOCARD TABLE PARAMETRIC SCHEMA
-- Author: Nathan T. Stevens
-- Org: PNSN
-- License: CC-1.0
--
-- ASSOCiation of the ARrival and DEtection tables
-- that provides a condensed representation of 
-- detection phase arrivals inherited from their 
-- parent template. Additional fields are provided
-- for documenting correlation re-alignment for
-- individual records.

-- FIELDS
-- DEID - DEtection record IDentifier
-- ARID - ARrival record IDentifier
-- DAOFF - offset in seconds to add to the ARID record to
--     re-constitute the detection pick time
-- CHAN_DET_VAL - channel detection value
-- CC_VAL - correlation re-alignment correlation coefficient
-- CC_SHIFT - corelation re-alignemnt shift in seconds. 
--     This is added to OFFSET.
-- SHIFTMAX - maximum shift length assessed in determining CC_VAL and CC_SHIFT
-- LDDATE - datetime this record was added to the database

-- TODO: add some way to quickly distinguish base detection, ML detection, and 
CREATE TABLE ASSOCARD
(   DEID BIGINT,
    ARID BIGINT,
    DAOFF DOUBLE PRECISION NOT NULL,
    CHAN_DET_VAL DOUBLE PRECISION NOT NULL,
    CC_VAL DOUBLE PRECISION,
    CC_SHIFT DOUBLE PRECISION,
    SHIFTMAX DOUBLE PRECISION,
    LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    
    CONSTRAINT ASSOCARD01 CHECK (CC_VAL >= -1.0 AND CC_VAL <= 1.0),
    CONSTRAINT ASSOCARDKEY01 PRIMARY KEY (DEID, ARID)
);