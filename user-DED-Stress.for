CC	user-subrutina v4.4 Stress
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
      REAL FIELD_VAL, FAKT
	  REAL AKT_TIME(180499)
	  REAL T_AKT(180498)
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
            IF ( AKT_TIME(NOEL) .EQ. -1.0 ) THEN
                FIELD(1)=TEMP       
                FIELD(2)=TEMP
            ELSE
                IF (TIME(2).LT.(AKT_TIME(NOEL)+0.020)) THEN
                   FAKT=1.0-(TIME(2)-AKT_TIME(NOEL))/0.020
                ELSE
                   FAKT=0.00
                ENDIF
C
                FIELD(1)=TEMP       
                FIELD(2)=TEMP+(FIELD_VAL-T_AKT(NOEL))*FAKT
            ENDIF
                STATEV(1)=1
      ELSE
                T_AKT(NOEL)=TEMP
                FIELD(1)=FIELD_VAL
                FIELD(2)=FIELD_VAL
                STATEV(1)=0
      ENDIF
C
C
      RETURN
      END
C
C-----------------------------------------------------------------------