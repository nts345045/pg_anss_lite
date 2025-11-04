-- XCORR TABLE PARAMETRIC SCHEMA
-- Cross Correlation Table Parametric Schema
-- auth: Nathan T. Stevens
-- org: PNSN
-- license: CC-1.0
--
-- fields
-- IEVID: Reference event ID (i^th)
-- IARID: Reference arrival ID
-- JEVID: Test event ID (j^th)
-- JARID: Test arrival ID
-- SAMP_RATE: sampling rate of vectors cross correlated
-- CC_VAL: Cross correlation coefficient value
-- CC_SHIFT: Cross correlation shift of test data corresponding to CC_VAL in samples
-- SHMAX: Unsigned maximum shift of test data assessed in samples 
-- LDDATE: Date loaded into database

CREATE TABLE XCORR (
    IEVID BIGINT,
    IARID BIGINT,
    JEVID BIGINT,
    JARID BIGINT,
    SAMP_RATE REAL NOT NULL,
    CC_VAL REAL,
    CC_SHIFT INTEGER,
    SHMAX INTEGER NOT NULL,
    LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    CONSTRAINT XCORR01 CHECK (cc_val >= -1 AND cc_val <= 1),
    CONSTRAINT XCORR02 CHECK (ABS(cc_shift) <= shmax),
    CONSTRAINT XCORR03 CHECK (samp_rate > 0),
    CONSTRAINT XCORRKEY02 FOREIGN KEY (ievid) REFERENCES event(evid),
    CONSTRAINT XCORRKEY03 FOREIGN KEY (iarid) REFERENCES arrival(arid),
    CONSTRAINT XCORRKEY04 FOREIGN KEY (jevid) REFERENCES event(evid),
    CONSTRAINT XCORRKEY05 FOREIGN KEY (jarid) REFERENCES arrival(arid)
);




    -- EXPERIMENTAL CONSTRAINTS

-- CCP: Maximum positive cross-correlation value
-- CCN: Maximum negative cross-correlation value
-- SHP: Shift in samples corresponding to CCP (signed)
-- SHN: Shift in samples corresponding to CCN (signed)
-- SHMAX: Maximum shift tested in samples (unsigned)
-- TODO

    -- CONSTRAINT XCORR01 CHECK (array_ndims(cc_vals) = 1),
    -- CONSTRAINT XCORR02 CHECK (array_ndims(cc_shifts) = 1),
    -- CONSTRAINT XCORR03 CHECK (array_length(cc_vals, 1) = array_length(cc_shifts,1)),
    -- CONSTRAINT XCORRKEY01 PRIMARY KEY (ievid, iarid, jevid, jarid),