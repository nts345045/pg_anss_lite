-- DCLUSTER TABLE PARAMETRIC SCHEMA
-- Detection Cluster Table schema
-- auth: Nathan T. Stevens
-- org: PNSN
-- license: CC-1.0
-- purpose: This table schema supports an organizing scheme
-- similar to that of the EVENT table for DETECTION table 
-- entries (analogus to ORIGIN entries) for a one-to-many
-- mapping. 

-- fields
-- CLID: CLuster IDentification number (PRIMARY KEY)
-- PCLID: Parent CLID, used to indicate if a cluster was
--    refined from an already-existing DCLUSTER table entry
--    TODO: Find a way to enforce (P)CLID exists
-- PREFDET: PREferred DETection ID (FOREIGN KEY)
-- SELECTFLAG: If this cluster is preferred (1) or not (0)
-- NMEMBERS: Number of features in this cluster
-- METHOD: Clustering method name
-- THRESHOLD: Clustering threshold value
-- CENTROID: n-dimensional centroid cordinate vector for the cluster
-- RMSD: n-dimensional root mean squared deviance for each basis
--      vector of the cluster
-- MAXDEV: n-dimensional coordinates of the most-distant member
--      of this cluster
-- BNAMES: array of strings providing names for each basis vector
-- BUNITS: array of strings providing units for each basis vector
-- COMMID: comment ID (FOREIGN KEY)
-- LDDATE: Datetime this entry was loaded into database
CREATE TABLE DCLUSTER
(   CLID BIGINT,
    PCLID BIGINT,
    PREFDET BIGINT,
    SELECTFLAG SMALLINT DEFAULT(0) NOT NULL,
    NMEMBERS BIGINT,
    METHOD VARCHAR(80),
    METRIC VARCHAR(80),
    THRESH DOUBLE PRECISION NOT NULL,
    CENTROID DOUBLE PRECISION ARRAY,
    RMSD DOUBLE PRECISION ARRAY,
    MAXDEV DOUBLE PRECISION ARRAY,
    BNAMES VARCHAR(20) ARRAY,
    BUNITS VARCHAR(20) ARRAY,
    COMMID BIGINT,
    LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    CONSTRAINT CLUSTER01 CHECK (clid > 0),
    CONSTRAINT CLUSTER02 CHECK (array_ndims(centroid) = 1),
    CONSTRAINT CLUSTER03 CHECK (array_ndims(rmsd) = 1),
    CONSTRAINT CLUSTER04 CHECK (array_ndims(maxdev) = 1),
    CONSTRAINT CLUSTER05 CHECK (array_ndims(bnames) = 1),
    CONSTRAINT CLUSTER06 CHECK (array_ndims(bunits) = 1),
    CONSTRAINT CLUSTER07 CHECK (array_length(centroid,1) = array_length(rmsd, 1)),
    CONSTRAINT CLUSTER08 CHECK (array_length(centroid,1) = array_length(maxdev, 1)),
    CONSTRAINT CLUSTER09 CHECK (array_length(centroid,1) = array_length(bnames, 1)),
    CONSTRAINT CLUSTER10 CHECK (array_length(centroid,1) = array_length(bunits, 1)),
    CONSTRAINT CLUSTERKEY01 PRIMARY KEY (clid),
    CONSTRAINT CLUSTERKEY02 FOREIGN KEY (prefdet) REFERENCES detection(deid)
--    CONSTRAINT CLUSTERKEY03 FOREIGN KEY (commid) REFERENCES remark(commid)
);