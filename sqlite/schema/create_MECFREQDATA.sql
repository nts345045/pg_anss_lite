 -- MECFREQDATA TABLE PARAMETRIC SCHEMA
 -- Focal mechanism frequency data table schema
 -- auth: Renate Hartog
 -- editor: Nathan T. Stevens
 -- orgs: PNSN / AQMS-SWG
 -- license: CC-1.0
CREATE TABLE MecFreqData (
   mecfreqid      BIGINT      NOT NULL,
   type           VARCHAR(15)    NOT NULL,
   freq           DOUBLE PRECISION    NOT NULL,
   CONSTRAINT MecFreqData_PK PRIMARY KEY (mecfreqid, type),
   CONSTRAINT MecFreqData_FK01 FOREIGN KEY (mecfreqid) REFERENCES MecFreq(mecfreqid),
   CONSTRAINT MecFreqData01 CHECK (type IN ('LP','HP','SF'))
);

