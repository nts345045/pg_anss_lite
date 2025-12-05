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
    REVID BIGINT,
    RARID BIGINT,
    RCHANID BIGINT,
    RNSLC VARCHAR(27),
    RPROCCOMMID BIGINT,
    RSCALAR DOUBLE PRECISION,
    XEVID BIGINT,
    XARID BIGINT,
    XCHANID BIGINT,
    XNSLC VARCHAR(27),
    XPROCCOMMID BIGINT,
    XSCALAR DOUBLE PRECISION,
    CC_VAL REAL,
    CC_SHIFT REAL,
    SHMAX REAL NOT NULL,
    LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    CONSTRAINT XCORR01 CHECK (cc_val >= -1 AND cc_val <= 1),
    CONSTRAINT XCORR02 CHECK (ABS(cc_shift) <= shmax),
    CONSTRAINT XCORR03 CHECK (samp_rate > 0),
    CONSTRAINT XCORRKEY01 FOREIGN KEY (revid) REFERENCES event(evid),
    CONSTRAINT XCORRKEY02 FOREIGN KEY (xevid) REFERENCES event(evid),
    CONSTRAINT XCORRKEY03 FOREIGN KEY (rarid) REFERENCES arrival(arid),
    CONSTRAINT XCORRKEY04 FOREIGN KEY (xarid) REFERENCES arrival(arid),
    CONSTRAINT XCORRKEY05 FOREIGN KEY (rchanid) REFERENCES stachan(chanid),
    CONSTRAINT XCORRKEY06 FOREIGN KEY (xchanid) REFERENCES stachan(chanid));
    -- CONSTRAINT XCORRKEY07 FOREIGN KEY (rproccommid) REFERENCES remark(commid),
    -- CONSTRAINT XCORRKEY08 FOREIGN KEY (xproccommid) REFERENCES remark(commid)
-- );

-- COMMENT ON TABLE XCORR IS "Cross correlation table";
-- COMMENT ON COLUMN XCORR.REVID IS "Event ID for the reference waveform trace (R)";
-- COMMENT ON COLUMN XCORR.RARID IS "Arrival ID for the reference waveform trace (R)";
-- COMMENT ON COLUMN XCORR.RCHANID IS "Station Channel ID for the reference waveform trace (R)";
-- COMMENT ON COLUMN XCORR.RNSLC IS "SEED stream code, including periods, for the reference waveform trace (R)";
-- COMMENT ON COLUMN XCORR.RSCALAR IS "Normalization scalar for the reference waveform trace (R)";
-- COMMENT ON COLUMN XCORR.XEVID IS "Event ID for the correlated waveform trace (X)";
-- COMMENT ON COLUMN XCORR.XARID IS "Arrival ID for the correlated waveform trace (X)";
-- COMMENT ON COLUMN XCORR.XCHANID IS "Station Channel ID for the correlated waveform trace (X)";
-- COMMENT ON COLUMN XCORR.XNSLC IS "SEED stream code, including periods, for the correlated waveform trace (X)";
-- COMMENT ON COLUMN XCORR.XSCALAR IS "Normalization scalar for the correlated waveform trace (X)";
-- COMMENT ON COLUMN XCORR.SAMP_RATE IS "Common sampling rate for both waveform traces in samples per second";
-- COMMENT ON COLUMN XCORR.CC_VAL IS "Cross correlation value (signed) ";
-- COMMENT ON COLUMN XCORR.CC_SHIFT IS "Cross correlation shift in samples corresponding to CC_VAL";
-- COMMENT ON COLUMN XCORR.SHMAX IS "Maximum cross correlation shift in samples (unsigned) tested";
-- COMMENT ON COLUMN XCORR.LDDATE IS "Load date of this entry into the database in true time at tz UTC";



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