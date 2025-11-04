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
-- CCP: Maximum positive cross-correlation value
-- CCN: Maximum negative cross-correlation value
-- SHP: Shift in samples corresponding to CCP (signed)
-- SHN: Shift in samples corresponding to CCN (signed)
-- SHMAX: Maximum shift tested in samples (unsigned)
-- LDDATE: Date loaded into database

CREATE TABLE XCORR (
    IEVID BIGINT,
    IARID BIGINT,
    JEVID BIGINT,
    JARID BIGINT,
    SAMP_RATE REAL NOT NULL,
    CCP REAL,
    CCN REAL,
    SHP INTEGER,
    SHN INTEGER,
    SHMAX INTEGER NOT NULL,
    LDDATE DATETIME DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    CONSTRAINT XCORR01 CHECK (ccp >= 0 AND ccp <= 1),
    CONSTRAINT XCORR02 CHECK (ccn <= 0 AND ccn >= -1),
    CONSTRAINT XCORR03 CHECK (ABS(shp) <= shmax),
    CONSTRAINT XCORR04 CHECK (ABS(shn) <= shmax),
    CONSTRAINT XCORRKEY01 PRIMARY KEY (ievid, iarid, jevid, jarid),
    CONSTRAINT XCORRKEY02 FOREIGN KEY (ievid) REFERENCES event(evid),
    CONSTRAINT XCORRKEY03 FOREIGN KEY (iarid) REFERENCES arrival(arid),
    CONSTRAINT XCORRKEY04 FOREIGN KEY (jevid) REFERENCES event(evid),
    CONSTRAINT XCORRKEY05 FOREIGN KEY (jarid) REFERENCES arrival(arid),


)