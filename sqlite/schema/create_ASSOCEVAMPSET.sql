-- ASSOCEVAMPSET TABLE PARAMETRIC SCHEMA
-- Association of events and amplitude sets in the ANSS/CISN database parametric schema
-- edited to conform with the structuring of the majority of table defitions
-- lightly adapted for SQLite by removing explicit time-zone declaration for LDDATE and 
-- commenting out `comment on` lines-- auth: Renate Hartog
-- editor: Nathan T. Stevens
-- orgs: PNSN / AQMS-SWG
-- license: CC-1.0
create table ASSOCEVAMPSET 
(
AMPSETID  BIGINT not null,
AMPSETTYPE  VARCHAR(20) not null,
EVID BIGINT not null,
SUBSOURCE VARCHAR(8) not null,
ISVALID SMALLINT not null,
LDDATE TIMESTAMP default (CURRENT_TIMESTAMP),
CONSTRAINT ASSOCEVAMPSETKEY01 PRIMARY KEY (ampsetid, ampsettype),
CONSTRAINT ASSOCEVAMPSETKEY02 FOREIGN KEY (ampsettype) REFERENCES ampsettypes(ampsettypes),
CONSTRAINT ASSOCEVAMPSETKEY03 FOREIGN KEY (evid) REFERENCES event(evid)
);


-- comment on table ASSOCEVAMPSET is 'This table associates amplitude sets with an event';
-- comment on column ASSOCEVAMPSET.AMPSETID is 'References ampset.ampsetid.';
-- comment on column ASSOCEVAMPSET.AMPSETTYPE is 'References ampset.ampsettype.';
-- comment on column ASSOCEVAMPSET.EVID is 'References event.evid.';
-- comment on column ASSOCEVAMPSET.ISVALID is 'Has value 1 if preferred set, 0 otherwise ';
-- comment on column ASSOCEVAMPSET.SUBSOURCE is 'Name tag of the application creating the set (e.g. AmpGen AmpGenPp Gmp2Db)';
-- comment on column ASSOCEVAMPSET.LDDATE is 'Date record created in UTC';


-- create or replace public synonym ASSOCEVAMPSET for ASSOCEVAMPSET;
-- grant select on ASSOCEVAMPSET to trinetdb_read, code;
-- grant insert,update, delete on ASSOCEVAMPSET to trinetdb_write, code;
