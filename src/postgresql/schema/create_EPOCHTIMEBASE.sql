-- EPOCHTIMEBASE TABLE PARAMETRIC SCHEMA
-- Time bounds for epochs data
-- Direct copy from the CISN / AQMS parametric schema for PostgreSQL database backed AQMS installations. 
-- Editor added this header block and commented out the last 2 `grant` commands for the simplified version
-- of the AQMS PostgreSQL schema
-- Author: Renate Hartog
-- Editor: Nathan T. Stevens
-- org: PNSN / AQMS-SWG
-- license: CC 1.0

create table EpochTimeBase (
  base      VARCHAR(1)  NOT NULL,
  ondate   TIMESTAMP         NOT NULL,
  offdate   TIMESTAMP,
  PRIMARY KEY (base, ondate),
  CONSTRAINT  timebasechk CHECK (base IN ('T','N'))
) 
;
insert into epochtimebase values ('T', to_date('1900/01/01','YYYY/MM/DD'), to_date('3000/01/01','YYYY/MM/DD'));
--grant select on all tables in schema trinetdb to trinetdb_read, code;
--grant insert, update, delete on all tables in schema trinetdb to trinetdb_write, code;
