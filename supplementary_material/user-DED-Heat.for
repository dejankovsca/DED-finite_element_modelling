CC	user-subrutina v4.4 Heat
CC	authors: Dejan Kovšca, Nikolaj Mole, University of Ljubljana - Faculty of Mechanical Engineering
C-----------------------------------------------------------------------
C			1. USDFLD subrutina
C-----------------------------------------------------------------------
      SUBROUTINE USDFLD(FIELD,STATEV,PNEWDT,DIRECT,T,CELENT,
     1 TIME,DTIME,CMNAME,ORNAME,NFIELD,NSTATV,NOEL,NPT,LAYER,
     2 KSPT,KSTEP,KINC,NDI,NSHR,COORD,JMAC,JMATYP,MATLAYO,LACCFLA)
C
      INCLUDE 'ABA_PARAM.INC'
C
      CHARACTER*80 CMNAME,ORNAME
      CHARACTER*3  FLGRAY(15)
      DIMENSION FIELD(NFIELD),STATEV(NSTATV),DIRECT(3,3),
     1 T(3,3),TIME(2)
      DIMENSION ARRAY(15),JARRAY(15),JMAC(*),JMATYP(*),COORD(*)
C-----------------------------------------------------------------------
      REAL FIELD_VAL
      REAL AKT_TIME(180499)
C
      FIELD_VAL=1783.0D0
C
      CALL GETVRM('TEMP',ARRAY,JARRAY,FLGRAY,JRCD,JMAC,JMATYP,
     1 MATLAYO,LACCFLA)
C
      TEMP = ARRAY(1)
C
C
      IF ( AKT_TIME(NOEL) .LT. (TIME(2)+DTIME) ) THEN
                FIELD(1)=TEMP
                STATEV(1)=1
      ELSE
                FIELD(1)=FIELD_VAL
                STATEV(1)=0
      ENDIF
C
C
      RETURN
      END
C-----------------------------------------------------------------------
C			2. FILM subrutina
C-----------------------------------------------------------------------
      SUBROUTINE FILM(H,SINK,TEMP,KSTEP,KINC,TIME,NOEL,NPT,
     1 COORDS,JLTYP,FIELD,NFIELD,SNAME,NODE,AREA)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION H(2),TIME(2),COORDS(3), FIELD(NFIELD)
      CHARACTER*80 SNAME
C-----------------------------------------------------------------------
      REAL HMIZA, SINK_MIZA, HZRAK, SINK_ZRAK, EMS, HRAD
      REAL AKT_TIME(180499)
      INTEGER IS_ELE(180498,6)
C
      HMIZA=20.0D0
      SINK_MIZA=323.0D0
      HZRAK=35.0D0
      SINK_ZRAK = 323.0D0
      EMS=0.5D0
      HRAD=EMS*5.67D-8*(SINK_ZRAK*SINK_ZRAK+TEMP*TEMP)*(SINK_ZRAK+TEMP)
C
C_4
C
      IF ( AKT_TIME(NOEL) .LT. TIME(2) ) THEN
		IF ( SNAME .EQ. 'ASSEMBLY_NOTRANJA_POVRSINA_S1' ) THEN
			IF ( AKT_TIME( IS_ELE(NOEL,1) ) .LT. TIME(2) ) THEN
				H(1)=0
			ELSE
				H(1)=HZRAK+HRAD
				SINK=SINK_ZRAK
			ENDIF
		ELSEIF ( SNAME .EQ. 'ASSEMBLY_NOTRANJA_POVRSINA_S2' ) THEN
			IF ( AKT_TIME( IS_ELE(NOEL,2) ) .LT. TIME(2) ) THEN
				H(1)=0
			ELSE
				H(1)=HZRAK+HRAD
				SINK=SINK_ZRAK
			ENDIF
		ELSEIF ( SNAME .EQ. 'ASSEMBLY_NOTRANJA_POVRSINA_S3' ) THEN
			IF ( AKT_TIME( IS_ELE(NOEL,3) ) .LT. TIME(2) ) THEN
				H(1)=0
			ELSE
				H(1)=HZRAK+HRAD
				SINK=SINK_ZRAK
			ENDIF
		ELSEIF ( SNAME .EQ. 'ASSEMBLY_NOTRANJA_POVRSINA_S4' ) THEN
			IF ( AKT_TIME( IS_ELE(NOEL,4) ) .LT. TIME(2) ) THEN
				H(1)=0
			ELSE
				H(1)=HZRAK+HRAD
				SINK=SINK_ZRAK
			ENDIF
		ELSEIF ( SNAME .EQ. 'ASSEMBLY_NOTRANJA_POVRSINA_S5' ) THEN
			IF ( AKT_TIME( IS_ELE(NOEL,5) ) .LT. TIME(2) ) THEN
				H(1)=0
			ELSE
				H(1)=HZRAK+HRAD
				SINK=SINK_ZRAK
			ENDIF
		ELSEIF ( SNAME .EQ. 'ASSEMBLY_NOTRANJA_POVRSINA_S6' ) THEN
			IF ( AKT_TIME( IS_ELE(NOEL,6) ) .LT. TIME(2) ) THEN
				H(1)=0
			ELSE
				H(1)=HZRAK+HRAD
				SINK=SINK_ZRAK
			ENDIF
C_5
		ELSEIF ( SNAME .EQ. 'ASSEMBLY_ZUNANJA_POVRSINA' ) THEN
			H(1)=HZRAK+HRAD
			SINK=SINK_ZRAK
C_6
		ENDIF
      ELSE
		H(1)=0
		SINK=1773
      ENDIF
C
C
      RETURN
      END
C
C-----------------------------------------------------------------------
C			3. DFLUX subrutina (Goldak izvor)
C-----------------------------------------------------------------------
      SUBROUTINE DFLUX(FLUX,SOL,KSTEP,KINC,TIME,NOEL,NPT,COORDS,
     1 JLTYP,TEMP,PRESS,SNAME)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION FLUX(2), TIME(2), COORDS(3)
      CHARACTER*80 SNAME
C-----------------------------------------------------------------------
      REAL PWR, FAKT, PI, QVOL, TIME_ZAMIK, BEAM(3), DIST(3), POS_ZAMIK(3)
      REAL RAZ, RAZ1, RAZ2, RAZ3
      REAL AKT_TIME(180499)
      REAL BEAM_POS(10030,4)
      INTEGER INC
C
      PWR=975000.0
      FAKT=1.0
      PI=3.14159265D0
      BEAM(1)=2.1D0 !x
      BEAM(2)=1.5D0 !y
      BEAM(3)=2.1D0 !z
C_8
      DO WHILE ( TIME(2) .GT. BEAM_POS(INC+1,1) )
		INC=INC+1
      END DO
C
      DIST(1)=COORDS(1)-BEAM_POS(INC,2)		
      DIST(2)=COORDS(2)-BEAM_POS(INC,3)		
      DIST(3)=COORDS(3)-BEAM_POS(INC,4)	
      RAZ1=DIST(1)/BEAM(1)
      RAZ2=DIST(2)/BEAM(2)
      RAZ3=DIST(3)/BEAM(3)
      RAZ=RAZ1*RAZ1+RAZ2*RAZ2+RAZ3*RAZ3
C
      QVOL=(6.D0*DSQRT(3.0D0)*PWR*FAKT)/(BEAM(1)*BEAM(2)*BEAM(3)
     & *(PI**(3.D0/2.D0)))*DEXP(-3.0D0*RAZ)
C
      IF ( AKT_TIME(NOEL) .LT. TIME(2)-TIME(1) ) THEN		
		FLUX(1) = QVOL
      ELSE
		FLUX(1) = 0
      ENDIF
C
C
      RETURN
      END
C-----------------------------------------------------------------------
