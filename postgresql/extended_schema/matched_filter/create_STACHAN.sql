CREATE TABLE STACHAN (
    CHANID BIGINT,
    NETWORK VARCHAR(6) NOT NULL,
    STATION VARCHAR(8) NOT NULL,
    LOCATION VARCHAR(2) DEFAULT '  ' NOT NULL,
    CHANNEL VARCHAR(6) NOT NULL,
    LAT DOUBLE PRECISION NOT NULL,
    LON DOUBLE PRECISION NOT NULL,
    ELEV DOUBLE PRECISION NOT NULL,
    DEPTH DOUBLE PRECISION,
    AZI DOUBLE PRECISION,
    DIP DOUBLE PRECISION
    ONTIME DOUBLE PRECISION,
    OFFTIME DOUBLE PRECISION,
    SAMP_RATE REAL NOT NULL,
    COMMID BIGINT,
    LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    CONSTRAINT STACHANKEY01 PRIMARY KEY (chanid),
    CONSTRAINT STACHAN01 CHECK (samp_rate > 0)
);

COMMENT ON TABLE STACHAN IS 'Station Channel (Meta)Data';
COMMENT ON COLUMN STACHAN.CHANID IS 'Unique numerical identifier of each station-channel';
COMMENT ON COLUMN STACHAN.NETWORK IS 'Network code for the station-channel entry';
COMMENT ON COLUMN STACHAN.STATION IS 'Station code for the station-channel entry';
COMMENT ON COLUMN STACHAN.LOCATION IS 'Location code for the station-channel';
COMMENT ON COLUMN STACHAN.LAT IS 'Latitude of the station-channel in degrees North';
COMMENT ON COLUMN STACHAN.LON IS 'Longitude of the station-channel in degrees East';
COMMENT ON COLUMN STACHAN.ELEV IS 'Elevation of the station-channel in kilometers';
COMMENT ON COLUMN STACHAN.DEPTH IS 'Depth of the station-channel in meters';
COMMENT ON COLUMN STACHAN.AZI IS 'Azimuth of the station-channel in degrees East of North';
COMMENT ON COLUMN STACHAN.DIP IS 'Inclination of the station-channel in degrees down from horizontal';
COMMENT ON COLUMN STACHAN.ONTIME IS 'Station-channel recording start datetime in nominal time';
COMMENT ON COLUMN STACHAN.OFFTIME IS 'Station-channel recording end datetime in nominal time';
COMMENT ON COLUMN STACHAN.SAMP_RATE IS 'Sampling rate for this station-channel in samples per second';
COMMENT ON COLUMN STACHAN.COMMID IS 'Implied foreign key to the REMARK table';
COMMENT ON COLUMN STACHAN.LDDATE IS 'Load date of this entry into database in true time at tz UTC';