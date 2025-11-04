 -- MECFREQ TABLE PARAMETRIC SCHEMA
 -- Focal mechanism frequency metadata table schema
 -- lightly modified for SQLite syntax
 -- auth: Renate Hartog
 -- editor: Nathan T. Stevens
 -- orgs: PNSN / AQMS-SWG
 -- license: CC-1.0
CREATE TABLE MecFreq (
   mecfreqid      BIGINT      NOT NULL,
   mecalgo        VARCHAR(15),
   lddate         TIMESTAMP            DEFAULT (CURRENT_TIMESTAMP),
   CONSTRAINT MecFreq_PK PRIMARY KEY (mecfreqid)
);

