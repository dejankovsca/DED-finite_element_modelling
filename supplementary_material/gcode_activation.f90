CC	authors: Dejan Kovšca, Nikolaj Mole, University of Ljubljana - Faculty of Mechanical Engineering
C-----------------------------------------------------------------------
SUBROUTINE AKTIVACIJA(N_ELE,N_CASOV,SMER_TISKA_IN,XYSMER_IN, &
        SMER_POMIKA,SEZNAM_SREDISC,BEAM_TYPE,ZBEAM_TYPE, &
        ROTACIJA,A_BEAM,L_BEAM,H_BEAM,OSC,OSC_LEN,ERR_EPS,COORDS, &
        GCODE_POS,NOZZLE_OFF,SELF_TIME,LARGE_TIME,SEZNAM_CASOV_IN, &
        SEZNAM_CASOV,SEZNAM_NEAKTIVIRANIH_IN,ODSTRANI)    
    INTEGER, INTENT(IN) :: N_ELE, N_CASOV
    INTEGER, INTENT(IN) :: SMER_TISKA_IN, XYSMER_IN(2)
    INTEGER, INTENT(IN) :: SEZNAM_NEAKTIVIRANIH_IN(N_ELE)
    INTEGER, INTENT(OUT) :: ODSTRANI(N_ELE)
    REAL, INTENT(IN) :: A_BEAM, H_BEAM, L_BEAM
    REAL, INTENT(IN) :: COORDS(3), SMER_POMIKA(3)
    REAL, INTENT(IN) :: SEZNAM_SREDISC(N_ELE,3)
    REAL, INTENT(IN) :: GCODE_POS(2), NOZZLE_OFF
    REAL, INTENT(IN) :: SELF_TIME, LARGE_TIME,OSC_LEN,ERR_EPS
    REAL, INTENT(IN) :: SEZNAM_CASOV_IN(N_CASOV)
    REAL, INTENT(OUT) :: SEZNAM_CASOV(N_CASOV)
    CHARACTER(LEN=15), INTENT(IN) :: BEAM_TYPE
    CHARACTER(LEN=15), INTENT(IN) :: ZBEAM_TYPE
    LOGICAL, INTENT(IN) :: ROTACIJA, OSC
           
    REAL :: FI, VISINA, R(2,2)
    REAL :: ZBEAM_CENTER(3), BEAM_CENTER(2), POINT(3)
    REAL :: XYPOINT(2), ZYPOINT(2)
    INTEGER :: m, SMER_TISKA, XYSMER(2)
    INTEGER :: SEZNAM_NEAKTIVIRANIH(N_ELE)
    LOGICAL :: P1(N_ELE), P2(N_ELE), P_OSC(3)
         
    SMER_TISKA = SMER_TISKA_IN+1
    XYSMER = XYSMER_IN+1
    SEZNAM_NEAKTIVIRANIH=SEZNAM_NEAKTIVIRANIH_IN+1
    SEZNAM_CASOV = SEZNAM_CASOV_IN
    ODSTRANI = -1
    P1 = .FALSE.
    P2 = .FALSE.
 
    IF (BEAM_TYPE .EQ. "front_square") THEN        
        BEAM_CENTER = (/ COORDS(XYSMER(1)),COORDS(XYSMER(2)) /)
        FI=-ATAN2(SMER_POMIKA(XYSMER(2)),SMER_POMIKA(XYSMER(1)))
        IF (ROTACIJA .EQV. .FALSE.) THEN
            FI=0
        END IF
        R = reshape((/COS(FI),-SIN(FI),SIN(FI),COS(FI)/), &
                  shape(R), order=(/2,1/))
        DO 12 i=1,N_ELE
            XYPOINT = (/ SEZNAM_SREDISC(i,XYSMER(1)), &
                SEZNAM_SREDISC(i,XYSMER(2)) /) - BEAM_CENTER 
            XYPOINT = MATMUL(R,XYPOINT)
            IF ( (XYPOINT(1) .LE. (L_BEAM+ERR_EPS)) &
                .AND. (XYPOINT(1) .GE. (0+ERR_EPS)) &
                .AND. (ABS(XYPOINT(2)) .LE. (A_BEAM/2+ERR_EPS)) ) THEN
                P1(i) = .TRUE.
            ELSE
                P1(i) = .FALSE.
            ENDIF
12      CONTINUE
    END IF

    IF (ZBEAM_TYPE .EQ. "circle") THEN
        ZBEAM_CENTER = COORDS
        ZBEAM_CENTER(SMER_TISKA) = COORDS(SMER_TISKA)+GCODE_POS(1)+NOZZLE_OFF
        FI=-ATAN2(SMER_POMIKA(XYSMER(2)),SMER_POMIKA(XYSMER(1)))
        R = reshape((/COS(FI),-SIN(FI),SIN(FI),COS(FI)/), &
                  shape(R), order=(/2,1/))       
        DO 21 i=1,N_ELE
            POINT = SEZNAM_SREDISC(i,:) - ZBEAM_CENTER
            POINT = POINT-DOT_PRODUCT(POINT,SMER_POMIKA)*SMER_POMIKA
            XYPOINT = (/POINT(XYSMER(1)),POINT(XYSMER(2))/)
            XYPOINT = MATMUL(R,XYPOINT)
            ZYPOINT = (/XYPOINT(2),POINT(SMER_TISKA)/)
            IF ( ((ZYPOINT(1)/(A_BEAM/2+ERR_EPS))**2 &
                +(ZYPOINT(2)/(H_BEAM/2+ERR_EPS))**2) .LE. 1 ) THEN
                P2(i) = .TRUE.
            ELSE
                P2(i) = .FALSE.
            ENDIF
21      CONTINUE
    ENDIF

    DO 30 i=1,N_ELE
        m = SEZNAM_NEAKTIVIRANIH(i)
        IF (P1(i) .AND. P2(i) .AND. SEZNAM_CASOV(m).EQ.LARGE_TIME) THEN
            SEZNAM_CASOV(m) = SELF_TIME
            ODSTRANI(i) = i-1
        ENDIF
30  CONTINUE
    
END SUBROUTINE AKTIVACIJA
