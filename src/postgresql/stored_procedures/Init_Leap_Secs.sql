
--  /***********************************************************************
--  * Init_Leap_Secs.sql ---> PL/SQL Script for initialization of the	   *
--  *			      Leap seconds table.			   *
--  *									   *
--  * Stephane Zuzlewski @1998-2014					   *
--  *	Ported to PostgreSQL 2016 by ISTI				   * 
--  * Copied to this repository by Nathan T. Stevens (AQMS-SWG member)
--  * Accessed: 2025/10/01
--  * License: Distributed here under a Creative Commons 1.0 license
--  ***********************************************************************/


-- /***********************************************************************
-- * The table leap_seconds_tmp is a temporary table needed to populate	  *
-- * the leap_seconds table.						  *
-- ***********************************************************************/

-- DROP TABLE leap_seconds_tmp;

CREATE TABLE leap_seconds_tmp (
s_nominal	BIGINT,	/* Start nominal epoch time */
e_nominal	BIGINT,	/* End nominal epoch time   */
s_true		BIGINT,	/* Start true epoch time    */
e_true		BIGINT,	/* End true epoch time      */
ls_count	BIGINT		/* Leap seconds count       */
);

-- /***********************************************************************
-- * Deleting all the rows in the leap_seconds table	  		  *
-- ***********************************************************************/

DELETE FROM leap_seconds;


--  /************************************
--  * Populating the leap_seconds table *
--  ************************************/

create function ls_init() RETURNS integer AS $$
DECLARE
--  /* Leap seconds in nominal epoch time */
n0	BIGINT;
n1	BIGINT;
n2	BIGINT;
n3	BIGINT;
n4      BIGINT;
n5      BIGINT;
n6      BIGINT;
n7      BIGINT;
n8      BIGINT;
n9      BIGINT;
n10	BIGINT;
n11     BIGINT;
n12     BIGINT;
n13     BIGINT;
n14     BIGINT;
n15     BIGINT;
n16     BIGINT;
n17     BIGINT;
n18     BIGINT;
n19     BIGINT;
n20     BIGINT;
n21     BIGINT;
n22	BIGINT;
n23	BIGINT;
n24	BIGINT;
n25	BIGINT;
n26	BIGINT;
n27     BIGINT;
n99	BIGINT;

--  /* Leap seconds in true epoch time */
t0	BIGINT;
t1	BIGINT;
t2	BIGINT;
t3	BIGINT;
t4      BIGINT;
t5      BIGINT;
t6      BIGINT;
t7      BIGINT;
t8      BIGINT;
t9      BIGINT;
t10	BIGINT;
t11     BIGINT;
t12     BIGINT;
t13     BIGINT;
t14     BIGINT;
t15     BIGINT;
t16     BIGINT;
t17     BIGINT;
t18     BIGINT;
t19     BIGINT;
t20     BIGINT;
t21     BIGINT;
t22	BIGINT;
t23	BIGINT;
t24	BIGINT;
t25	BIGINT;
t26	BIGINT;
t27     BIGINT;
t99	BIGINT;

tt1	BIGINT;
tt2	BIGINT;
tt3	BIGINT;
tt4     BIGINT;
tt5     BIGINT;
tt6     BIGINT;
tt7     BIGINT;
tt8     BIGINT;
tt9     BIGINT;
tt10	BIGINT;
tt11    BIGINT;
tt12    BIGINT;
tt13    BIGINT;
tt14    BIGINT;
tt15    BIGINT;
tt16    BIGINT;
tt17    BIGINT;
tt18    BIGINT;
tt19    BIGINT;
tt20    BIGINT;
tt21    BIGINT;
tt22	BIGINT;
tt23	BIGINT;
tt24	BIGINT;
tt25	BIGINT;
tt26	BIGINT;
tt27    BIGINT;

BEGIN
-- 	 /* Computing nominal epoch times */
        n0	:= truetime.string2nominal ('0001/01/01 00:00:00');
	n1	:= truetime.string2nominal ('1972/06/30 23:59:59');
	n2	:= truetime.string2nominal ('1972/12/31 23:59:59');
	n3	:= truetime.string2nominal ('1973/12/31 23:59:59');
        n4	:= truetime.string2nominal ('1974/12/31 23:59:59');
        n5	:= truetime.string2nominal ('1975/12/31 23:59:59');
        n6	:= truetime.string2nominal ('1976/12/31 23:59:59');
        n7	:= truetime.string2nominal ('1977/12/31 23:59:59');
        n8	:= truetime.string2nominal ('1978/12/31 23:59:59');
        n9	:= truetime.string2nominal ('1979/12/31 23:59:59');
        n10	:= truetime.string2nominal ('1981/06/30 23:59:59');
        n11	:= truetime.string2nominal ('1982/06/30 23:59:59');
        n12	:= truetime.string2nominal ('1983/06/30 23:59:59');
        n13	:= truetime.string2nominal ('1985/06/30 23:59:59');
        n14	:= truetime.string2nominal ('1987/12/31 23:59:59');
        n15	:= truetime.string2nominal ('1989/12/31 23:59:59');
        n16	:= truetime.string2nominal ('1990/12/31 23:59:59');
        n17	:= truetime.string2nominal ('1992/06/30 23:59:59');
        n18	:= truetime.string2nominal ('1993/06/30 23:59:59');
        n19	:= truetime.string2nominal ('1994/06/30 23:59:59');
        n20	:= truetime.string2nominal ('1995/12/31 23:59:59');
        n21	:= truetime.string2nominal ('1997/06/30 23:59:59');
        n22	:= truetime.string2nominal ('1998/12/31 23:59:59');
	n23	:= truetime.string2nominal ('2005/12/31 23:59:59');
	n24	:= truetime.string2nominal ('2008/12/31 23:59:59');
	n25     := truetime.string2nominal ('2012/06/30 23:59:59');
	n26     := truetime.string2nominal ('2015/06/30 23:59:59');
	n27     := truetime.string2nominal ('2016/12/31 23:59:59');
        n99	:= truetime.string2nominal ('3000/01/01 00:00:00');


-- 	 /* Populating the leap_seconds table */
	INSERT INTO leap_seconds VALUES (n0, n1, NULL, NULL, 0);
        INSERT INTO leap_seconds VALUES (n1+1, n2, NULL, NULL, 1);
        INSERT INTO leap_seconds VALUES (n2+1, n3, NULL, NULL, 2);
        INSERT INTO leap_seconds VALUES (n3+1, n4, NULL, NULL, 3);
        INSERT INTO leap_seconds VALUES (n4+1, n5, NULL, NULL, 4);
        INSERT INTO leap_seconds VALUES (n5+1, n6, NULL, NULL, 5);
        INSERT INTO leap_seconds VALUES (n6+1, n7, NULL, NULL, 6);
        INSERT INTO leap_seconds VALUES (n7+1, n8, NULL, NULL, 7);
        INSERT INTO leap_seconds VALUES (n8+1, n9, NULL, NULL, 8);
        INSERT INTO leap_seconds VALUES (n9+1, n10, NULL, NULL, 9);
        INSERT INTO leap_seconds VALUES (n10+1, n11, NULL, NULL, 10);
        INSERT INTO leap_seconds VALUES (n11+1, n12, NULL, NULL, 11);
        INSERT INTO leap_seconds VALUES (n12+1, n13, NULL, NULL, 12);
        INSERT INTO leap_seconds VALUES (n13+1, n14, NULL, NULL, 13);
        INSERT INTO leap_seconds VALUES (n14+1, n15, NULL, NULL, 14);
        INSERT INTO leap_seconds VALUES (n15+1, n16, NULL, NULL, 15);
        INSERT INTO leap_seconds VALUES (n16+1, n17, NULL, NULL, 16);
        INSERT INTO leap_seconds VALUES (n17+1, n18, NULL, NULL, 17);
        INSERT INTO leap_seconds VALUES (n18+1, n19, NULL, NULL, 18);
        INSERT INTO leap_seconds VALUES (n19+1, n20, NULL, NULL, 19);
        INSERT INTO leap_seconds VALUES (n20+1, n21, NULL, NULL, 20);
        INSERT INTO leap_seconds VALUES (n21+1, n22, NULL, NULL, 21);
        INSERT INTO leap_seconds VALUES (n22+1, n23, NULL, NULL, 22);
        INSERT INTO leap_seconds VALUES (n23+1, n24, NULL, NULL, 23);
	INSERT INTO leap_seconds VALUES (n24+1, n25, NULL, NULL, 24);
	INSERT INTO leap_seconds VALUES (n25+1, n26, NULL, NULL, 25);
	INSERT INTO leap_seconds VALUES (n26+1, n27, NULL, NULL, 26);
        INSERT INTO leap_seconds VALUES (n27+1, n99, NULL, NULL, 27);
--
-- 	 /* Computing true epoch times */
	t0	:= truetime.nominal2true (n0);
	t1	:= truetime.nominal2true (n1);
	t2	:= truetime.nominal2true (n2);
	t3	:= truetime.nominal2true (n3);
	t4	:= truetime.nominal2true (n4);
	t5	:= truetime.nominal2true (n5);
	t6	:= truetime.nominal2true (n6);
	t7	:= truetime.nominal2true (n7);
	t8	:= truetime.nominal2true (n8);
	t9	:= truetime.nominal2true (n9);
	t10	:= truetime.nominal2true (n10);
	t11	:= truetime.nominal2true (n11);
	t12	:= truetime.nominal2true (n12);
	t13	:= truetime.nominal2true (n13);
	t14	:= truetime.nominal2true (n14);
	t15	:= truetime.nominal2true (n15);
	t16	:= truetime.nominal2true (n16);
	t17	:= truetime.nominal2true (n17);
	t18	:= truetime.nominal2true (n18);
	t19	:= truetime.nominal2true (n19);
	t20	:= truetime.nominal2true (n20);
	t21	:= truetime.nominal2true (n21);
	t22	:= truetime.nominal2true (n22);
	t23	:= truetime.nominal2true (n23);
	t24	:= truetime.nominal2true (n24);
	t25     := truetime.nominal2true (n25);
	t26     := truetime.nominal2true (n26);
	t27     := truetime.nominal2true (n27);
	t99	:= truetime.nominal2true (n99);

	tt1	:= truetime.nominal2true (n1+1);
	tt2	:= truetime.nominal2true (n2+1);
	tt3	:= truetime.nominal2true (n3+1);
	tt4	:= truetime.nominal2true (n4+1);
	tt5	:= truetime.nominal2true (n5+1);
	tt6	:= truetime.nominal2true (n6+1);
	tt7	:= truetime.nominal2true (n7+1);
	tt8	:= truetime.nominal2true (n8+1);
	tt9	:= truetime.nominal2true (n9+1);
	tt10	:= truetime.nominal2true (n10+1);
	tt11	:= truetime.nominal2true (n11+1);
	tt12	:= truetime.nominal2true (n12+1);
	tt13	:= truetime.nominal2true (n13+1);
	tt14	:= truetime.nominal2true (n14+1);
	tt15	:= truetime.nominal2true (n15+1);
	tt16	:= truetime.nominal2true (n16+1);
	tt17	:= truetime.nominal2true (n17+1);
	tt18	:= truetime.nominal2true (n18+1);
	tt19	:= truetime.nominal2true (n19+1);
	tt20	:= truetime.nominal2true (n20+1);
	tt21	:= truetime.nominal2true (n21+1);
	tt22	:= truetime.nominal2true (n22+1);
	tt23	:= truetime.nominal2true (n23+1);
	tt24	:= truetime.nominal2true (n24+1);
	tt25    := truetime.nominal2true (n25+1);
	tt26    := truetime.nominal2true (n26+1);
	tt27    := truetime.nominal2true (n27+1);


 	 /* Populating the leap_seconds_tmp table */
	INSERT INTO leap_seconds_tmp VALUES (n0,    n1,  t0,   t1,   0);
        INSERT INTO leap_seconds_tmp VALUES (n1+1,  n2,  tt1,  t2,   1);
        INSERT INTO leap_seconds_tmp VALUES (n2+1,  n3,  tt2,  t3,   2);
        INSERT INTO leap_seconds_tmp VALUES (n3+1,  n4,  tt3,  t4,   3);
        INSERT INTO leap_seconds_tmp VALUES (n4+1,  n5,  tt4,  t5,   4);
        INSERT INTO leap_seconds_tmp VALUES (n5+1,  n6,  tt5,  t6,   5);
        INSERT INTO leap_seconds_tmp VALUES (n6+1,  n7,  tt6,  t7,   6);
        INSERT INTO leap_seconds_tmp VALUES (n7+1,  n8,  tt7,  t8,   7);
        INSERT INTO leap_seconds_tmp VALUES (n8+1,  n9,  tt8,  t9,   8);
        INSERT INTO leap_seconds_tmp VALUES (n9+1,  n10, tt9,  t10,  9);
        INSERT INTO leap_seconds_tmp VALUES (n10+1, n11, tt10, t11, 10);
        INSERT INTO leap_seconds_tmp VALUES (n11+1, n12, tt11, t12, 11);
        INSERT INTO leap_seconds_tmp VALUES (n12+1, n13, tt12, t13, 12);
        INSERT INTO leap_seconds_tmp VALUES (n13+1, n14, tt13, t14, 13);
        INSERT INTO leap_seconds_tmp VALUES (n14+1, n15, tt14, t15, 14);
        INSERT INTO leap_seconds_tmp VALUES (n15+1, n16, tt15, t16, 15);
        INSERT INTO leap_seconds_tmp VALUES (n16+1, n17, tt16, t17, 16);
        INSERT INTO leap_seconds_tmp VALUES (n17+1, n18, tt17, t18, 17);
        INSERT INTO leap_seconds_tmp VALUES (n18+1, n19, tt18, t19, 18);
        INSERT INTO leap_seconds_tmp VALUES (n19+1, n20, tt19, t20, 19);
        INSERT INTO leap_seconds_tmp VALUES (n20+1, n21, tt20, t21, 20);
        INSERT INTO leap_seconds_tmp VALUES (n21+1, n22, tt21, t22, 21);
        INSERT INTO leap_seconds_tmp VALUES (n22+1, n23, tt22, t23, 22);
        INSERT INTO leap_seconds_tmp VALUES (n23+1, n24, tt23, t24, 23);
	INSERT INTO leap_seconds_tmp VALUES (n24+1, n25, tt24, t25, 24);
	INSERT INTO leap_seconds_tmp VALUES (n25+1, n26, tt25, t26, 25);
	INSERT INTO leap_seconds_tmp VALUES (n26+1, n27, tt26, t27, 26);
        INSERT INTO leap_seconds_tmp VALUES (n27+1, n99, tt27, t99, 27);
 	return(1);

END;
$$ LANGUAGE plpgsql;

select ls_init();

--  /* Deleting all the rows in the leap_seconds table */
DELETE FROM leap_seconds;

--  /* Inserting rows in the leap_seconds table from the leap_seconds_tmp table */
INSERT INTO leap_seconds SELECT * FROM leap_seconds_tmp;
--
--  /* Destroying the leap_seconds_tmp table */
DROP TABLE leap_seconds_tmp;

drop function ls_init();

