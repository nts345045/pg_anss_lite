 -- MECCHANNEL TABLE PARAMETRIC SCHEMA
 -- Focal mechanism channel information table schema
 -- auth: Renate Hartog
 -- editor: Nathan T. Stevens
 -- orgs: PNSN / AQMS-SWG
 -- license: CC-1.0
CREATE TABLE MecChannel (
   mecdataid      BIGINT    NOT NULL,
   net            VARCHAR(8)     NOT NULL,
   sta            VARCHAR(6)     NOT NULL,
   seedchan       VARCHAR(3)     NOT NULL,
   location       VARCHAR(2)     NOT NULL,
   CONSTRAINT MecChannel_PK PRIMARY KEY (mecdataid, net, sta, seedchan, location),
   CONSTRAINT MecChannel_FK01 FOREIGN KEY (mecdataid) REFERENCES MecData(mecdataid)
);

