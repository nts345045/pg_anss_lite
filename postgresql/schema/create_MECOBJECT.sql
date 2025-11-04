 -- MECOBJECT TABLE PARAMETRIC SCHEMA
 -- Focal mechanism object table schema
 -- auth: Renate Hartog
 -- editor: Nathan T. Stevens
 -- orgs: PNSN / AQMS-SWG
 -- license: CC-1.0
CREATE TABLE MecObject (
    mecid         BIGINT      NOT NULL,
    dataid        BIGINT      NOT NULL,
    mimetype      VARCHAR(20),
    data          BYTEA,
    meta          VARCHAR(128),
    CONSTRAINT MecObject_PK PRIMARY KEY (mecid, dataid),
    CONSTRAINT MecObject_FK01 FOREIGN KEY (mecid) REFERENCES MEC(mecid) 
);

