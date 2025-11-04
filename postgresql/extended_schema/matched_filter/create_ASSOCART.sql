-- ASSOCART TABLE PARAMETRIC SCHEMA
-- Author: Nathan T. Stevens
-- Org: PNSN
-- License: CC-1.0
--
-- ASSOCiation of the ARrival and Template tables
-- Basic mapping to indicate which arrival data were used in a given template
CREATE TABLE ASSOCART
(   TEID BIGINT,
    ARID BIGINT,
    LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    CONSTRAINT ASSOCARTKEY01 PRIMARY KEY (TEID, ARID)
);