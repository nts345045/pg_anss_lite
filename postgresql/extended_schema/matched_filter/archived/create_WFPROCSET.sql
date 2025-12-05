CREATE TABLE WFPROCSET (
    WFPSETID BIGINT,
    NAME VARCHAR(80),
    STEPNO BIGINT,
    WFPID BIGINT,
    LDDATE TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC'),
    CONSTRAINT WFPROCKEY01 PRIMARY KEY (wfpid, stepno),
    CONSTRAINT WFPROCKEY02 FOREIGN KEY (commid) REFERNCES remark(commid)
);

COMMENT ON TABLE WFPROC IS "WaveForm PROCessing summary table";
COMMENT ON COLUMN WFPROC.WFPSETID IS "Unique numerical identifier of each processing sequence";
COMMENT ON COLUMN WFPROCSET.NAME IS "Name of the processing sequence";
COMMENT ON COLUMN WFPROC.STEPNO IS "Step number within the processing sequence";
COMMENT ON COLUMN WFPROCSET.WFPID IS "Unique numerical identifier of a processing step in the WFPROC table"
COMMENT ON COLUMN WFPROC.INTERPRETER IS "Name of the interpreter language for this processing step. E.g., 'python'";
COMMENT ON COLUMN WFPROC.LIBRARY IS "Name of the library providing the processing step method. E.g., 'obspy'";
COMMENT ON COLUMN WFPROC.METHOD IS "Name of the function/method for this processing step. E.g., 'filter'";
COMMENT ON COLUMN WFPROC.KWARGS IS "Method argument {key,value} pairs in TEXT format. E.g., {{'type','bandpass'},{'freqmin','1'},{'freqmax','45.0'}}";
COMMENT ON COLUMN WFPROC.COMMID IS "Comment identifier tied to the REMARK table";
COMMENT ON COLUMN WFPROC.LDDATE IS 'Load date of this entry into database in true time at tz UTC';