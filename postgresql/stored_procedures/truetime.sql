-- script: postgresql/stored_procedures/truetime.sql
-- auth: Paul Friberg
-- org: ISTI / AQMS Software Working Group
-- retrieved: 
-- editor: Nathan T. Stevens
-- license: None provided in source repository. Provided here
--      under a Creative Commons 1.0 license at the expressed permission
--      of Renate Hartog as a member of the AQMS Software Working Group
-- purpose: This script installs a suite of TrueTime stored procedures
--  into an initialized PostgreSQL database
--  It provides functions that can be called during sessions with an
--  AQMS PostgreSQL database for converting between nominal time (no leap seconds)
--  and true time (UTC time / with leap seconds).


create schema if not exists truetime; -- authorization code;
-- grant usage on schema truetime to trinetdb_read, trinetdb_execute;


DROP FUNCTION IF EXISTS truetime.getPkgId();
CREATE OR REPLACE FUNCTION truetime.getPkgId() RETURNS VARCHAR as $$
  DECLARE
    v_id VARCHAR = 'truetime.sql 2018-10-27 postgresql $';
  BEGIN
    RETURN v_id;
  END
$$ LANGUAGE plpgsql; 


--  /***********************************************************************
--  * The function returns 1 if the native timebase of the dbase is "true"
--  * that is, UTC time including leap seconds. Otherwise, returns 0
--  * meaning the native timebase is UNIX (aka POSIX) time without leap seconds.
--  * This is intended for INTERNAL DATABASE use only. 
--  * Calling applications should NEVER care.
--  ***********************************************************************/
create or replace FUNCTION truetime.timeBaseIsTrue()  RETURNS integer AS $$
DECLARE
    pkg_base varchar;
BEGIN
    SELECT base INTO pkg_base FROM EpochTimeBase WHERE offdate > current_timestamp;
    IF (pkg_base = 'N') THEN
      RETURN 0; --  default for SCEDC
    END IF;
    --
    RETURN 1;   -- default TRUE for NCEDC 
    --
END
$$ LANGUAGE plpgsql;

--  /***********************************************************************
--  * The function nominal2true converts a nominal epoch time to a true    *
--  * epoch time.                                                          *
--  *                                                                      *
--  * Returns NULL if the time is a leap second.                           *
--  ***********************************************************************/
DROP FUNCTION IF EXISTS truetime.nominal2true(n bigint);
create or replace function truetime.nominal2true(n bigint) RETURNS bigint AS $$
DECLARE
	true_time bigint := 1;
	lsec_count bigint := 0;
BEGIN
	SELECT ls_count INTO lsec_count FROM leap_seconds
	WHERE   s_nominal <= n
	AND     e_nominal >= n;
	true_time = n + lsec_count;
--	RAISE NOTICE 'true is %', true_time;
	RETURN true_time;
END
$$ LANGUAGE plpgsql;


--  /***********************************************************************
--  * The function nominal2truef converts a nominal epoch time to a true   *
--  * epoch time (including 1/10000 of seconds).                           *
--  ***********************************************************************/
DROP FUNCTION IF EXISTS truetime.nominal2truef(n FLOAT);
create or replace function truetime.nominal2truef (n FLOAT) RETURNS FLOAT AS $$
DECLARE
        true_secs       FLOAT;
        diff            FLOAT;
	nom_int		bigint;
BEGIN
	nom_int 	:= FLOOR (n);
        diff            := n - nom_int;
        true_secs       := truetime.nominal2true (nom_int) + diff;
--	RAISE NOTICE 'true is %', true_secs;
--
        RETURN (true_secs);
END 
$$ LANGUAGE plpgsql;

--  /***********************************************************************
--  * The function true2nominal converts a true epoch time to a nominal    *
--  * epoch time.                                                          *
--  *                                                                      *
--  * Returns NULL if the time is a leap second.                           *
--  ***********************************************************************/
DROP FUNCTION IF EXISTS truetime.true2nominal(t bigint);
create or replace function truetime.true2nominal(t bigint) RETURNS bigint AS $$
DECLARE
	nominal_time bigint := 1;
	lsec_count bigint := 0;
BEGIN
	SELECT ls_count INTO lsec_count FROM leap_seconds
	WHERE   s_true <= t
	AND     e_true >= t;
	nominal_time = t - lsec_count;
	RETURN nominal_time;
END
$$ LANGUAGE plpgsql;

--  /***********************************************************************
--  * The function true2nominalf converts a true epoch time to a nominal   *
--  * epoch time (including 1/10000 of seconds).                           *
--  *                                                                      *
--  * Returns NULL if the time is a leap second.                           *
--  ***********************************************************************/
DROP FUNCTION IF EXISTS truetime.true2nominalf (t FLOAT);
create or replace function truetime.true2nominalf (t FLOAT) RETURNS FLOAT AS $$
DECLARE
        nominal         FLOAT;
        diff            FLOAT;
	nominal_int	bigint;
BEGIN
        diff            := t - FLOOR (t);
	nominal_int 	:= FLOOR(t);
        nominal         := truetime.true2nominal (nominal_int) + diff;
--
        RETURN (nominal);
END 
$$ LANGUAGE plpgsql;

--  /***********************************************************************
--  * The function string2nominal converts a string format time to a       *
--  * nominal epoch time.                                                  *
--  * Input string must have format of 'YYYY/MM/DD HH24:MI:SS' where the
--  * field delimiters are optional or other punctuation can be substituted.
--  * Returns NULL if the time is a leap second.                           *
--  ***********************************************************************/
--  STRING2NOMINAL function - uses database tools to compute bigint seconds
DROP FUNCTION IF EXISTS truetime.string2nominal(d varchar);
create or replace function truetime.string2nominal(d varchar) RETURNS bigint AS $$
DECLARE
        origin_days     bigint;
        d_days          bigint;
        diff_days       bigint;
        nominal         bigint;
        secs_in_day     bigint;
        d2              VARCHAR(20);
        d3              VARCHAR(20);
        secs            VARCHAR(3);
       v_pkg_origin  TIMESTAMP := TO_TIMESTAMP('1970/01/01 00:00:00', 'YYYY/MM/DD HH24:MI:SS');
BEGIN
	d2 := d;
	secs := SUBSTR(d, 17, 3);
	IF (secs LIKE ':60' OR  secs LIKE ':61') THEN
		d2  := SUBSTR(d, 1, 16) || ':59';
	END IF;
--
	origin_days     := TO_CHAR (v_pkg_origin, 'J');
	d_days          := TO_CHAR (TO_DATE (d2, 'YYYY/MM/DD HH24:MI:SS'), 'J');
--
	diff_days       := d_days - origin_days;
	secs_in_day     := TO_CHAR (TO_TIMESTAMP (d2, 'YYYY/MM/DD HH24:MI:SS'), 'SSSS');
--                                  secs since epoch start for this day + secs since midnight
	nominal         := (diff_days*86400) +  secs_in_day;
--
	RETURN (nominal);
END
$$ LANGUAGE plpgsql;

--  /***********************************************************************
--  * The function string2true converts a string format time to a true     *
--  * Input string must have format of 'YYYY/MM/DD HH24:MI:SS' but the field
--  * element delimiters are optional or other punctuation can be substituted.
--  * epoch time.                                                          *
--  ***********************************************************************/
DROP FUNCTION IF EXISTS truetime.string2true(d varchar);
DROP FUNCTION IF EXISTS truetime.string2true(d varchar(20));
create or replace FUNCTION truetime.string2true (d VARCHAR) RETURNS BIGINT AS $$
DECLARE
        v_true          BIGINT;
        leap            BIGINT := 0;
        d2              VARCHAR(20);
        d3              VARCHAR(20);
        d4              VARCHAR;
BEGIN
        d2              := REPLACE (d, ':60', ':59');
        d3              := REPLACE (d, ':61', ':59');
--
        IF      d != d2 THEN
                d4      := d2;
                leap    := 1;
        ELSIF   d != d3 THEN
                d4      := d3;
                leap    := 2;
        ELSE
                d4      := d;
                leap    := 0;
        END IF;
--
--
        v_true            := truetime.nominal2true(truetime.string2nominal(d4)) + leap;
--
        RETURN (v_true);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION truetime.string2truef (d VARCHAR) RETURNS FLOAT AS $$
DECLARE
	diff		VARCHAR(5);
	dd		VARCHAR(20);
	t		FLOAT;
BEGIN
	dd		:= SUBSTR(d, 1, 19);
	diff		:= SUBSTR(d, 20);
	t		:= truetime.string2true(dd) + CAST(diff AS DECIMAL );
--
	RETURN (t);
END;

$$ LANGUAGE plpgsql; 

--  /***********************************************************************
--  * The function nominal2string converts a nominal epoch time to a       *
--  * string format time.                                                  *
--  ***********************************************************************/
DROP FUNCTION IF EXISTS truetime.nominal2string(n BIGINT);
create or replace FUNCTION truetime.nominal2string (n BIGINT) RETURNS VARCHAR(20) AS $$
DECLARE
   v_pkg_origin TIMESTAMP := TO_TIMESTAMP('1970/01/01 00:00:00+00', 'YYYY/MM/DD HH24:MI:SS');
   v_time TIMESTAMP := v_pkg_origin + make_interval( secs => CAST(n AS double precision) );
BEGIN
        RETURN TO_CHAR(v_time, 'YYYY/MM/DD HH24:MI:SS');
END;
$$ LANGUAGE plpgsql;

--  /***********************************************************************
--  * The function true2string converts a true epoch time to a string      *
--  * format time.                                                         *
--  ***********************************************************************/
DROP FUNCTION IF EXISTS truetime.true2string(t BIGINT);
create or replace FUNCTION truetime.true2string (t BIGINT) RETURNS VARCHAR(20) AS $$
<< mainblock >>
DECLARE
        d               VARCHAR(20);
        lp_secs1        BIGINT;
        lp_secs2        BIGINT;
        lp_secs3        BIGINT;
BEGIN
--
        BEGIN
        SELECT ls_count INTO mainblock.lp_secs1 FROM leap_seconds
        WHERE   s_true <= t
        AND     e_true >= t;
        EXCEPTION WHEN NO_DATA_FOUND THEN mainblock.lp_secs1 := -1;
        END;
--
        IF      lp_secs1 >= 0   THEN
                d       := truetime.nominal2string (t - lp_secs1);
        ELSE
                BEGIN
                SELECT ls_count INTO mainblock.lp_secs2 FROM leap_seconds
                WHERE   s_true <= t-1
                AND     e_true >= t-1;
                EXCEPTION WHEN NO_DATA_FOUND THEN mainblock.lp_secs2 := -1;
                END;
--
                IF      lp_secs2 >= 0   THEN
                        d       := truetime.nominal2string (t - lp_secs2 - 2);
                        d       := REPLACE (d, ':58', ':60');
                ELSE
                        BEGIN
                        SELECT ls_count INTO mainblock.lp_secs3 FROM leap_seconds
                        WHERE   s_true <= t-2
                        AND     e_true >= t-2;
                        END;
--
                        d       := truetime.nominal2string (t - lp_secs3 - 3);
                        d       := REPLACE (d, ':58', ':61');
                END IF;
        END IF;
--
--
        RETURN (d);
END mainblock;
$$ LANGUAGE plpgsql;

--  /***********************************************************************
--  * The function true2stringf converts a true epoch time to a string     *
--  * format time (including 1/10000 of seconds).			   *
--  ***********************************************************************/
CREATE OR REPLACE FUNCTION truetime.true2stringf (t DOUBLE PRECISION) RETURNS VARCHAR(26) AS $$
DECLARE
--
	d1	VARCHAR(26);
	dd	VARCHAR(20);
	diff	DOUBLE PRECISION;
	idiff	BIGINT;
--
BEGIN
	dd	:= truetime.true2string (CAST (FLOOR (t) AS BIGINT));
	diff	:= t - FLOOR (t);
	idiff	:= diff*10000;
--
	d1	:= CONCAT (dd, '.');
--
	IF	diff != 0	THEN
		IF idiff < 10 THEN
			d1 := CONCAT (d1, '000');
		ELSE
			IF idiff < 100 THEN
				d1 := CONCAT (d1, '00');
			ELSE
				IF idiff < 1000 THEN
					d1	:= CONCAT (d1, '0');
				END IF;
			END IF;
		END IF;
--
		d1 := CONCAT (d1, idiff);
	ELSE
		d1 := CONCAT (d1, '0000');
	END IF;
--
--
	RETURN (d1);
END
$$ LANGUAGE plpgsql;

--   
--  /***********************************************************************
--  * Given an epoch time 't' in the timebase specified by 'baseIn' returns the 
--  * equivalent epoch time in the dbase's native timebase.
--  * Use in INSERT or UPDATE statements.
--  * Valid epoch type values: ('UTC', 'TRUE') and ('POSIX', 'UNIX', 'NOMINAL')
--  * Lower case or mixed case strings are OK (will be upcased internally)
--  * Example: Update origin set datetime = TrueTime.putEpoch(myUtcTime, 'UTC')
--  *             where Origin = 123456;
--  ***********************************************************************/


create or replace FUNCTION truetime.putEpoch (t DOUBLE PRECISION, baseIn VARCHAR) RETURNS DOUBLE PRECISION AS $$
DECLARE
--
      isTrue  INTEGER;
      secs    DOUBLE PRECISION; 
      base    VARCHAR(8);
--
BEGIN
    base := UPPER(baseIn);
    secs := t;
    isTrue := truetime.timeBaseIsTrue();
--
    IF (base IN ('TRUE', 'UTC')) THEN
      IF (isTrue = 0) THEN
        secs := truetime.true2nominalf(t);
      END IF;
--
    ELSIF (base IN ('NOMINAL', 'UNIX', 'POSIX')) THEN
      IF (isTrue = 1) THEN
        secs := truetime.nominal2truef(t);
      END IF;
    END IF;
--
    RETURN secs;
END
$$ LANGUAGE plpgsql;

--  /***********************************************************************
--  * Given a native dbase epoch time 't' return returns the equivalent epoch
--  * time in the timebase specified by 'baseOut'.
--  * Use in SELECT statements.
--  * Valid 'baseOut' values: ('UTC', 'TRUE') and ('POSIX', 'UNIX', 'NOMINAL')
--  * Lower case or mixed case strings are OK (will be upcased internally)
--  * Example: Select TrueTime.getEpoch(Origin.datetime, 'UTC')) into myUtcTime
--  *             where Origin = 123456;
--  ***********************************************************************/
create or replace FUNCTION truetime.getEpoch (t DOUBLE PRECISION, baseIn VARCHAR) RETURNS DOUBLE PRECISION AS $$
DECLARE
--
      isTrue  INTEGER;
      secs    DOUBLE PRECISION; 
      base    VARCHAR(8);
--
BEGIN
    base := UPPER(baseIn);
    secs := t;
    isTrue := truetime.timeBaseIsTrue();
--
    IF (base IN ('TRUE', 'UTC')) THEN
      IF (isTrue = 0) THEN
        secs := truetime.nominal2truef(t);
      END IF;
--
    ELSIF (base IN ('NOMINAL', 'UNIX', 'POSIX')) THEN
      IF (isTrue = 1) THEN
        secs := truetime.true2nominalf(t);
      END IF;
    END IF;
--
    RETURN secs;
END
$$ LANGUAGE plpgsql;

--  /***********************************************************************
--  * Return a UTC time string for the given dbase datetime value 't'.
--  * Format example: "2007/09/07 07:07:26"
--  * Handles any convesion to account for dbase's native representation.
--  * Use in SELECT statements.
--  * Example: Select TrueTime.getString(Origin.datetime)) into myTimeString
--  *             where Origin = 123456;
--  ***********************************************************************/
CREATE OR REPLACE FUNCTION truetime.getString (t DOUBLE PRECISION) RETURNS VARCHAR(20) AS $$
DECLARE
	tint    BIGINT;
	tstr	VARCHAR(20);
BEGIN
	tint := CAST ( truetime.getEpoch(t, 'TRUE') AS BIGINT);
	tstr := truetime.true2string(tint);
	RETURN tstr;
END
$$ LANGUAGE plpgsql;    
--
--  /***********************************************************************
--  * Return a UTC time string w/ fractional seconds for the given dbase 
--  * datetime value 't'.
--  * Format example: "2007/09/07 07:07:26.8300" (NOTE: four decimal places)
--  * Handles any convesion to account for dbase's native representation.
--  * Use in SELECT statements.
--  * Example: Select TrueTime.getString(Origin.datetime)) into myTimeString
--  *             where Origin = 123456;
--  ***********************************************************************/
CREATE OR REPLACE FUNCTION truetime.getStringf (t DOUBLE PRECISION) RETURNS VARCHAR(26) AS $$
DECLARE
	tstr	VARCHAR(26);
BEGIN
	tstr := truetime.true2stringf(truetime.getEpoch(t, 'TRUE'));
	RETURN tstr;
END
$$ LANGUAGE plpgsql;    
--    
--  /***********************************************************************
--  * Given a UTC time string 's' returns the epoch value in the database's timebase.
--  * Format example: "2007/09/07 07:07:26"
--  * Handles any convesion to account for dbase's native representation.
--  * Use in INSERT or UPDATE statements.
--  * Example: Update origin set datetime = TrueTime.putString('2007/09/07 07:07:26')
--  *             where Origin = 123456;
--  ***********************************************************************/
CREATE OR REPLACE FUNCTION truetime.putString (s VARCHAR(20)) RETURNS DOUBLE PRECISION AS $$
DECLARE
	utc	DOUBLE PRECISION;
	tepoc	DOUBLE PRECISION;
BEGIN
	utc := truetime.string2true(s);
	tepoc := truetime.putEpoch(utc, 'TRUE');
	RETURN tepoc;
END
$$ LANGUAGE plpgsql;    

