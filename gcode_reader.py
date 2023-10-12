##	authors: Dejan Kovšca, Nikolaj Mole, University of Ljubljana - Faculty of Mechanical Engineering
#-----------------------------------------------------------------------
class gcode_reader:
    coords = [0,0,0] #mm 
    time = 0.0 #s 
    delta_t = 0.125 #s
    smer_tiska = 1
    xysmer_tiska = [0,1,2]
    beam_type="square" 
    zbeam_type="square" 
    a_beam = 6 
    l_beam = 2 
    h_beam = 6
    rotacija = True
    last_gline = 'G0'
    g0_feed = False
    g0_feed_on = 0
    nozzle_offset = 0.0
    gcode_pos_str = 'top'
    gcode_pos = [0,0]
    v0 = 0 #mm/s hitrost g0
    v1 = 0 #mm/s hitrost g1
    pomik0 = [0,0,0] #mm
    pomik1 = [0,0,0]
    coord_sys = 'G90'
    ukaz = 'G0'
    miza = False
    miza_value = 0.0
    tisk_part = [0]
    ele_i = [0]
    nactive_count = 1
    error1 = 0
    error2 = 0
    error3 = 0
    MC = False #Model_change
    MC_ukaz = 'every'
    MC_value = 1
    MC_count = -1
    layer = 0
    layer_n = 1
    MC_Elset = []
    MC_mesto = 0
    MC_step = []
    step_time = [0] 
    Goldak = True
    beam_pos = [] 
    Goldak_xy_off = 0
    Goldak_z_off_val = 0 
    Goldak_z_off = [0,0,0]
    Goldak_namizi = True
    h_layer = 1.0 
    layer_pause = 0
    #advanced
    large_time = 1e5
    vklop_time = 1e-8
    large_pos = 1e5
    round_time = 0.05
    round_coords = 3 
    err_epsilon = 0.0001 
    min_pomik = 0.005
    #
    seznam_casov = []
    seznam_neaktiviranih = []
    seznam_sredisc = []
    in_rnd_time = 1
    n_ele = 0


    def __init__(self, delta_t=0.125, smer_tiska='Y', g0_feed=False):
        self.delta_t = delta_t
        self.g0_feed = g0_feed
        if smer_tiska == 'X': self.smer_tiska = 0
        elif smer_tiska == 'Y': self.smer_tiska = 1
        elif smer_tiska == 'Z': self.smer_tiska = 2
        self.xysmer_tiska = [0,1,2]
        self.xysmer_tiska.remove(self.smer_tiska)

            
    def set_Zoffset(self,gcode_pos='top', nozzle_offset=0.0, h_layer=1.0):
        self.nozzle_offset = nozzle_offset
        self.gcode_pos_str = gcode_pos
        self.h_layer = h_layer

  
    def set_beam(self, beam_type="square", a_beam=6, zbeam_type="square", h_beam=6, rotacija=True):
        self.beam_type = beam_type
        self.zbeam_type = zbeam_type
        self.a_beam = a_beam
        self.h_beam = h_beam
        self.rotacija = rotacija
                
    def square_beam(self, l_beam=2, tri_fill=True, osc_filter=True, osc_len=0.5):
        self.l_beam = l_beam
        self.tri_fill = tri_fill
        self.osc_filter = osc_filter
        self.osc_len = osc_len
    
    
    def set_Goldak(self, Goldak=True, Goldak_xy_off=0, Goldak_z_off=0, Goldak_namizi=True):
        self.Goldak = Goldak
        self.Goldak_xy_off = Goldak_xy_off
        if Goldak_xy_off=='default' and self.beam_type=="square":
            self.Goldak_xy_off = self.l_beam/2
        elif Goldak_xy_off=='default' and self.beam_type=="circle":
            self.Goldak_xy_off = self.a_beam/2
        self.Goldak_z_off_val = Goldak_z_off 
        self.Goldak_namizi = Goldak_namizi
        
    
    def set_else(self, layer_pause=0):
        self.layer_pause = layer_pause
    
    
    def set_advanced(self, large_time=1e5, vklop_time=1e-8, large_pos = 1e5, round_time=0.05, round_coords=3, err_epsilon=0.0001):
        self.large_time = large_time
        self.vklop_time = vklop_time
        self.large_pos = large_pos
        self.round_time = round_time
        self.round_coords = round_coords
        self.err_epsilon = err_epsilon
        if '.' in str(a):
            self.in_rnd_time = len(str(round_time).split('.')[1])
        else:
            self.in_rnd_time=1  
     
    
    def build_plate(self, izbira=False, value=0.0):
        self.miza = izbira
        self.miza_value = value
        
        
    def tisk_part(self, tisk_part, ele_i):
        self.tisk_part = tisk_part
        self.ele_i = ele_i
        
        
    def model_change(self, izbira=False, ukaz='every', value=1): 
        self.step_time = [0]
        self.MC = izbira
        self.MC_ukaz = ukaz
        self.MC_value = value
        
        
    def auto_in(self, min_pomik=0.005):
        self.min_pomik = min_pomik
   

    def read_line(self, line):
        line_str = line
        line = line.split(' ')
        self.pomik0 = self.coords.copy()  #G90 absolute
        self.pomik1 = [0,0,0]             #G91 relative
        self.ukaz = line[0]
        if self.ukaz in ['G90','G91','G0','G00','G1','G01','G4','G04']:
            for i in line:
                if 'X' in i: self.pomik0[0] = self.pomik1[0] = float(i.replace('X',''))
                elif 'Y' in i: self.pomik0[1] = self.pomik1[1] = float(i.replace('Y',''))
                elif 'Z' in i: self.pomik0[2] = self.pomik1[2] = float(i.replace('Z',''))
                elif (self.ukaz=='G4' or self.ukaz=='G04') and ('P' in i): self.ukaz = i
                elif (self.ukaz=='G4' or self.ukaz=='G04') and ('S' in i): self.ukaz = i
                elif 'F' in i:
                    if self.ukaz == 'G0' or self.ukaz == 'G00': self.v0 = float(i.replace('F',''))/60
                    elif self.ukaz == 'G1' or self.ukaz == 'G01': self.v1 = float(i.replace('F',''))/60
                elif self.ukaz == 'G90' or self.ukaz == 'G91': pass
        elif ';LAYER_COUNT:' in self.ukaz or ';LAYER:' in self.ukaz: pass
        elif ';Layer height:' in line_str: self.ukaz=line_str
        else: self.ukaz = False
 

    def izvedi(self):
        if self.ukaz == False:
            self.status.append('Opozorilo: Neveljaven ukaz')
            self.error2+=1
            return
        #------------------------------------------------------
        elif self.ukaz == 'G90':
            self.coord_sys = 'G90'
            self.status.append('prebrano')
            return
        elif self.ukaz == 'G91':
            self.coord_sys = 'G91'
            self.status.append('prebrano')
            return
        elif 'P' in self.ukaz:#pause v [ms]
            self.beam_pos.append([rnd.round_nearest(self.time,self.round_time),[self.large_pos]*3])
            self.time += float(self.ukaz.replace('P',''))/1000
        elif 'S' in self.ukaz:#pause v [s]
            self.beam_pos.append([rnd.round_nearest(self.time,self.round_time),[self.large_pos]*3])
            self.time += float(self.ukaz.replace('S',''))
        #G0_ukaz:------------------------------------------------------  
        elif (self.g0_feed==False or self.g0_feed_on==0) and (self.ukaz == 'G0' or self.ukaz == 'G00') : #premik g0 se izvede v trenutku
            if self.coord_sys == 'G90': #absolute
                self.coords = self.pomik0
            elif self.coord_sys == 'G91': #relative
                self.coords = [a+b for a,b in zip(self.coords,self.pomik1)]
        elif self.g0_feed and (self.ukaz == 'G0' or self.ukaz == 'G00') :
            if self.v0==0:
                self.status.append('Napaka: Hitrost v0=0')
                self.error1 += 1
                if self.coord_sys == 'G90': #absolute
                    self.coords = self.pomik0
                elif self.coord_sys == 'G91': #relative
                    self.coords = [a+b for a,b in zip(self.coords,self.pomik1)]
            else:
                if self.coord_sys == 'G90': #absolute
                    rel_pomik = [b-a for a,b in zip(self.coords,self.pomik0)]
                elif self.coord_sys == 'G91': #relative
                    rel_pomik = self.pomik1
                if sum([k**2 for k in rel_pomik])**(1/2) <= self.min_pomik:
                    self.status.append('Opozorilo: Pomik gkode manjši od dovoljenega!')
                    self.error3 += 1
                    return 
                smer_pomika = [i/sum([k**2 for k in rel_pomik])**(1/2) for i in rel_pomik]
                cas_pomika = sum([k**2 for k in rel_pomik])**(1/2)/self.v0
                ti = 1
                self.beam_pos.append([rnd.round_nearest(self.time,self.round_time),[self.large_pos]*3])
                while ti <= int(cas_pomika/self.delta_t) :
                    ti += 1
                    self.time += self.delta_t
                    self.coords = [a+self.v0*self.delta_t*b for a,b in zip(self.coords,smer_pomika)]
                    self.beam_pos.append([rnd.round_nearest(self.time,self.round_time),[self.large_pos]*3])
                self.time += cas_pomika-int(cas_pomika/self.delta_t)*self.delta_t
                self.coords = [a+self.v0*(cas_pomika-int(cas_pomika/self.delta_t)*self.delta_t)*b for a,b in zip(self.coords,smer_pomika)]
            self.last_gline = 'G0'
        #G1_ukaz:------------------------------------------------------                
        elif self.ukaz == 'G1' or self.ukaz == 'G01':
            if self.g0_feed_on==0: self.g0_feed_on=1
            if self.v1==0:
                self.status.append('Napaka: Hitrost v1=0')
                self.error1 += 1
                if self.coord_sys == 'G90': #absolute
                    self.coords = self.pomik0
                elif self.coord_sys == 'G91': #relative
                    self.coords = [a+b for a,b in zip(self.coords,self.pomik1)]
            else:
                if self.coord_sys == 'G90': #absolute
                    rel_pomik = [b-a for a,b in zip(self.coords,self.pomik0)]
                elif self.coord_sys == 'G91': #relative
                    rel_pomik = self.pomik1
                if sum([k**2 for k in rel_pomik])**(1/2) <= self.min_pomik:
                    self.status.append('Opozorilo: Pomik gkode manjši od dovoljenega!')
                    self.error3 += 1
                    return 
                smer_pomika = [i/sum([k**2 for k in rel_pomik])**(1/2) for i in rel_pomik]
                cas_pomika = sum([k**2 for k in rel_pomik])**(1/2)/self.v1
                ti = 1
                self.aktivacija(smer_pomika)
                self.beam_pos.append([rnd.round_nearest(self.time,self.round_time),[round(k,self.round_coords) for k in self.coords+np.array(smer_pomika)*self.Goldak_xy_off+self.Goldak_z_off]])
                while ti <= int(cas_pomika/self.delta_t) :
                    ti += 1
                    self.time += self.delta_t
                    self.coords = [a+self.v1*self.delta_t*b for a,b in zip(self.coords,smer_pomika)]
                    self.aktivacija(smer_pomika)
                    self.beam_pos.append([rnd.round_nearest(self.time,self.round_time),[round(k,self.round_coords) for k in self.coords+np.array(smer_pomika)*self.Goldak_xy_off+self.Goldak_z_off]])
                self.time += cas_pomika-int(cas_pomika/self.delta_t)*self.delta_t #dopolni mankajoč čas
                self.coords = [a+self.v1*(cas_pomika-int(cas_pomika/self.delta_t)*self.delta_t)*b for a,b in zip(self.coords,smer_pomika)] #dopolni pomik
                self.aktivacija(smer_pomika)
            self.last_gline = 'G1'
        #LAYER_ukaz:-------------------------------------------
        elif ';LAYER_COUNT:' in self.ukaz: 
            self.layer_n = int(self.ukaz.replace(';LAYER_COUNT:',''))
            self.status.append('prebrano')
            if self.MC and self.MC_ukaz=='every':
                dodatna = 0
                if self.layer_n-int(self.layer_n/self.MC_value)*self.MC_value: dodatna = 1 
                self.MC_Elset = [[] for k in range(int(self.layer_n/self.MC_value) + dodatna)]
            elif self.MC and self.MC_ukaz=='interactions':
                self.MC_Elset = [[] for k in range(self.MC_value)] 
                self.MC_value = int(self.layer_n/self.MC_value) 
            return
        elif ';LAYER:' in self.ukaz:
            self.layer = int(self.ukaz.replace(';LAYER:',''))
            self.status.append('prebrano')
            self.MC_count += 1
            self.beam_pos.append([rnd.round_nearest(self.time,self.round_time),[self.large_pos]*3])
            if self.layer_pause and self.layer>0:
                self.time += self.layer_pause
            return
        elif ';Layer height:' in self.ukaz:
            self.h_layer = float(self.ukaz.replace(';Layer height: ',''))
            if self.gcode_pos_str == 'top': Goldak_val = self.Goldak_z_off_val-(self.h_layer-self.nozzle_offset)
            elif self.gcode_pos_str == 'bottom': Goldak_val = self.Goldak_z_off_val-(self.h_layer-(self.h_beam+self.nozzle_offset))
            elif self.gcode_pos_str == 'middle': Goldak_val = self.Goldak_z_off_val-(self.h_layer-(self.h_beam/2+self.nozzle_offset))
            self.Goldak_z_off = [Goldak_val if i==self.smer_tiska else 0 for i in range(3)]
            self.status.append('prebrano')
            return
        #------------------------------------------------------
        else: 
            self.status.append('Opozorilo: Neveljaven ukaz.')
            self.error2+=1
            return
        #------------------------------------------------------
        self.coords = [round(k,self.round_coords) for k in self.coords]
        self.time = round(self.time,self.in_rnd_time+3)
        self.status.append(f'time: {round(self.time,self.in_rnd_time)}')
        self.status.append(f'coords: {self.coords}')
        self.status.append(f'Aktiviranih KE: {self.nactive_count-self.seznam_casov.count(self.large_time)}')
        self.nactive_count=self.seznam_casov.count(self.large_time)


    def aktivacija(self,smer_pomika):
        if len(self.seznam_neaktiviranih)==0: return
        self.seznam_casov,odstrani = GCODE_AKTIVACIJA.aktivacija(self.smer_tiska,self.xysmer_tiska,smer_pomika,self.seznam_sredisc,self.beam_type,self.zbeam_type,self.rotacija,self.a_beam,self.l_beam,self.h_beam,self.osc_filter,self.osc_len,self.err_epsilon,self.coords,self.gcode_pos,self.nozzle_offset,self.time,self.large_time,self.seznam_casov,self.seznam_neaktiviranih)
        self.seznam_casov = self.seznam_casov.tolist()
        odstrani = odstrani.tolist()
        odstrani = [i for i in odstrani if i!=-1]
        for n,i in enumerate(odstrani): self.seznam_neaktiviranih.pop(i-n); self.seznam_sredisc.pop(i-n)
    

    def main(self,lines,sredisca):
        '''
        return: seznam_casov
        '''
        print(f'Branje gkode v teku: 0.0%')
        self.status = []
        self.status.append(f'Vozlišča vzeta iz \'{pot_input}\'')
        self.status.append(f'Začetek branja \'{pot_gcode}\' at: '+datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.status.append(f'---------------------------------------------------------------------------------------------------')
        self.status.append(f'Glavni parametri: delta_t={self.delta_t}, smer_tiska={self.smer_tiska+1}, g0_feed={self.g0_feed}, miza={self.miza}, miza_value={self.miza_value}')
        self.status.append(f'Navarek: beam_type={self.beam_type}, zbeam_type={self.zbeam_type}, a_beam={self.a_beam}, l_beam={self.l_beam}, h_beam={self.h_beam}, rotacija={self.rotacija}')
        self.status.append(f'---------------------------------------------------------------------------------------------------\n')
        
        self.coords = [0,0,0] #mm
        self.time = 0.0
        self.last_gline = 'G0'
        self.g0_feed_on = 0
        self.n_ele = len(sredisca)
        self.seznam_sredisc = sredisca.copy() 
        self.seznam_neaktiviranih = [i for i in range(self.n_ele)]
        self.seznam_casov = [self.large_time]*(self.n_ele)
        self.MC_count = -1
        self.MC_mesto = 0
        self.MC_step = [-1]*self.n_ele 
        self.beam_pos = []
        
        #definiranje_delovne_mize:
        for i in range(len(self.ele_i)-1):
            if i not in self.tisk_part: self.seznam_casov[self.ele_i[i]:self.ele_i[i+1]] = [-1.0]*(self.ele_i[i+1]-self.ele_i[i]) 
        if self.miza == True:
            odstrani=[]
            for i,element in enumerate(sredisca):
                if element[self.smer_tiska] <= self.miza_value:
                    self.seznam_casov[i] = -1.0
                    odstrani.append(i)
            self.status.append(f'V delovni mizi je aktivnih {self.seznam_casov.count(-1.0)} elementov.\n')
            for n,i in enumerate(odstrani): self.seznam_neaktiviranih.pop(i-n); self.seznam_sredisc.pop(i-n) 
        self.nactive_count=self.seznam_casov.count(self.large_time) 

        #izvedi_gkodo:
        if self.zbeam_type == "square" :
            if self.gcode_pos_str == 'top': self.gcode_pos = [0,-self.h_beam]
            elif self.gcode_pos_str == 'bottom': self.gcode_pos = [self.h_beam,0]
            elif self.gcode_pos_str == 'middle': self.gcode_pos = [self.h_beam/2,-self.h_beam/2]
        elif self.zbeam_type == "circle":
            if self.gcode_pos_str == 'top': self.gcode_pos = [-self.h_beam/2]*2
            elif self.gcode_pos_str == 'bottom': self.gcode_pos = [self.h_beam/2]*2
            elif self.gcode_pos_str == 'middle': self.gcode_pos = [0]*2
        #-----       
        if self.gcode_pos_str == 'top': Goldak_val = self.Goldak_z_off_val-(self.h_layer-self.nozzle_offset)
        elif self.gcode_pos_str == 'bottom': Goldak_val = self.Goldak_z_off_val-(self.h_layer-(self.h_beam+self.nozzle_offset))
        elif self.gcode_pos_str == 'middle': Goldak_val = self.Goldak_z_off_val-(self.h_layer-(self.h_beam/2+self.nozzle_offset))
        self.Goldak_z_off = [Goldak_val if i==self.smer_tiska else 0 for i in range(3)]
        #-----  
        for i,line in enumerate(lines):
            self.status.append('*****\n'+f'ukaz: {i+1} | {line}')
            gcode.read_line(line)
            gcode.izvedi()
            datoteka.write(self.status,pot=pot_status)
                
        clear_output()
        print(f'Postprocessing...')
        #ATIME postprocessing
        self.seznam_casov = [rnd.round_nearest(i,self.round_time) for i in self.seznam_casov]
        for n in range(self.n_ele):
            if self.MC_step[i] != -1 and self.seznam_casov[n] == self.step_time[self.MC_step[i]]:
                self.seznam_casov[n]+=self.vklop_time*2
        self.seznam_casov.append(0.0) 

            
        return self.seznam_casov, self.beam_pos