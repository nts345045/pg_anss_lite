-- AMPSET TABLE PARAMETRIC SCHEMA
-- Amplitude Set Table Schema for the ANSS/CISN database parametric schema table
-- auth: Renate Hartog
-- editor: Nathan T. Stevens
-- orgs: PNSN / AQMS-SWG
-- license: CC-1.0

create table AMPSET 
(AMPSETID  BIGINT not null,
AMPID BIGINT not null
);

alter table AMPSET add constraint ampsetkey01 primary key
(ampsetid, ampid);

alter table AMPSET add constraint ampsetkey02 foreign key (ampid) references amp(ampid);

comment on table AMPSET is 'This table associates amplitudes with an amplitude set';
comment on column AMPSET.AMPSETID is 'The unique numerical identifier of an amp set';
comment on column AMPSET.AMPID is 'The unique numerical identifier of an amplitude record in AMP table.';

-- create or replace public synonym ampset for ampset;
-- grant select on ampset to trinetdb_read, code;
-- grant insert, update, delete on ampset to trinetdb_write, code;
