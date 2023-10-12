CC	authors: Dejan Kovšca, Nikolaj Mole, University of Ljubljana - Faculty of Mechanical Engineering
C-----------------------------------------------------------------------
SUBROUTINE SELE(N_ELE, ELE, S_ELE)
    INTEGER, INTENT(IN) :: N_ELE
    INTEGER, INTENT(IN) :: ELE(N_ELE,8)
    INTEGER, INTENT(OUT) :: S_ELE(N_ELE,6) 
    INTEGER :: SFACE(6,4)
    LOGICAL :: SOSEDNJI(4)
   
    S_ELE=N_ELE+1
    DO 10 I=1,N_ELE
        SFACE = reshape((/ELE(I,1),ELE(I,2),ELE(I,3),ELE(I,4), &
                      ELE(I,5),ELE(I,8),ELE(I,7),ELE(I,6), &
                      ELE(I,1),ELE(I,5),ELE(I,6),ELE(I,2), &
                      ELE(I,2),ELE(I,6),ELE(I,7),ELE(I,3), &
                      ELE(I,3),ELE(I,7),ELE(I,8),ELE(I,4), &
                      ELE(I,4),ELE(I,8),ELE(I,5),ELE(I,1)/), &
                    shape(SFACE), order=(/2,1/))
        
        DO 20 J=1,N_ELE
            DO 30 K=1,6
                DO 40 L=1,4
                    SOSEDNJI(L)=ANY(SFACE(K,L).EQ.ELE(J,:))
40              CONTINUE
                IF (ALL(SOSEDNJI) .AND. I.NE.J) THEN
                    S_ELE(I,K)=J
                END IF
30          CONTINUE                   
            IF (ALL(N_ELE+1.NE.S_ELE(I,:))) THEN
                EXIT
            ENDIF            
20      CONTINUE
10  CONTINUE

END SUBROUTINE SELE
