 -- MECDATA TABLE PARAMETRIC SCHEMA
 -- Focal mechanism station observation data table
 -- lightly modified for SQLite syntax
 -- auth: Renate Hartog
 -- editor: Nathan T. Stevens
 -- orgs: PNSN / AQMS-SWG
 -- license: CC-1.0
CREATE TABLE MecData (
   mecdataid      BIGINT      NOT NULL,
   mecid          BIGINT      NOT NULL,
   mecfreqid      BIGINT,
   polarity       VARCHAR(2),
   discrepancy    VARCHAR(1),
   orientation    VARCHAR(1),
   quality        DOUBLE PRECISION,
   amplitude      DOUBLE PRECISION,
   phase          DOUBLE PRECISION,
   time1          DOUBLE PRECISION,
   time2          DOUBLE PRECISION,
   model          VARCHAR(10),
   zcor           INTEGER,
   corlen         INTEGER,
   dt             DOUBLE PRECISION,
   varred         DOUBLE PRECISION,
   lddate         TIMESTAMP            DEFAULT (CURRENT_TIMESTAMP),
   CONSTRAINT MecData_PK PRIMARY KEY (mecdataid),
   CONSTRAINT MecData_FK01 FOREIGN KEY (mecid) REFERENCES MEC(mecid),
   CONSTRAINT MecData_FK02 FOREIGN KEY (mecfreqid) REFERENCES MecFreq(mecfreqid),
   CONSTRAINT MecData01 CHECK (discrepancy IN ('T','F')),
   CONSTRAINT MecData02 CHECK (orientation IN ('C','R','T','H','3','L','E','N','Z','A','I',' ')),
   CONSTRAINT MecData03 CHECK (quality BETWEEN 0 AND 1),
   CONSTRAINT MecData04 CHECK (model IN ('mend1_','socal','gil7_'))
);

