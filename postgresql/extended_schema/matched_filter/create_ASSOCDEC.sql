-- ASSOCEC TABLE PARAMETRIC SCHEMA
-- Association of DETECTION and DCLUSTER table entries
-- auth: Nathan T. Stevens
-- org: PNSN
-- license: CC-1.0
--
-- fields
-- CLID: Cluster ID
-- DEID: Detection ID
-- DEV: array containing n-dim deviation of this feature from the
--  cluster centroid
-- SELECTFLAG: is this the preferred detection of the cluster
-- LDDATE: datetime this entry was added to the database 
CREATE TABLE ASSOCDEC
(   CLID BIGINT,
    DEID BIGINT,
    DEV DOUBLE PRECISION ARRAY,
    SELECTFLAG SMALLINT DEFAULT (0) NOT NULL,
    LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    CONSTRAINT ASSOCDECKEY01 PRIMARY KEY (CLID, DEID),
    CONSTRAINT ASSOCDECKEY02 FOREIGN KEY (CLID) REFERENCES dcluster(clid),
    CONSTRAINT ASSOCDECKEY03 FOREIGN KEY (DEID) REFERENCES detection(deid));