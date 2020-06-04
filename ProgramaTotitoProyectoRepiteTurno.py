#-----
# Luis Delgado 17187
# Inteligencia Artificial Seccion 10
# Seccion 10
# Game playing program for dots and boxes
# Minimax with 4-look-ahead and alpha-beta prunning
#-------------------------
#Que yo sepa tiene todo lo necesario para 100 jeje

import socketio, random, math
#imports

sio = socketio.Client()
#b: username
b=""
#n: tournament id
n=0
#a: direccion ip + socket ej. http://192.162.0.1:4000
a=""

#Connect
@sio.event
def connect():
    global b
    global n
    #Pide y establece username y tournament id y completa la conexion al server
    b=input("Ingrese su username: ")
    n=input("Ingrese el id del torneo: ")
    sio.emit('signin',{
    'user_name': b,
    'tournament_id': n,
    'user_role': 'player'})
    
@sio.event
def disconnect():
    print('Disconnected from server')

@sio.on('ok_signin')
def ok_signin():
    print('Successfully signed in!')
#on ready
@sio.on('ready')
def ready(data):
    global n
    print('data of ready received:', data)
    board=data['board']
    #o es la orientación del movimiento (0 o 1)
    #u es la posición del movimiento a lanzar (0 a 29 en el caso de una cuadricula
    #de 5x5 cuadros)
    o,u=minimaxStar(board,data['player_turn_id'])
    #lanza la jugada
    sio.emit('play',{
        'tournament_id' : n,
        'player_turn_id' : data['player_turn_id'],
        'game_id' : data['game_id'],
        'movement' : [o,u]})

    #Logica para movimientos random
    '''
    if (len(hd)==0):
        sio.emit('play', {
        'tournament_id': n,
        'player_turn_id': data['player_turn_id'],
        'game_id': data['game_id'],
        'movement': [1, vd[random.randint(0,len(vd)-1)]] })
    elif (len(vd)==0):
        sio.emit('play', {
        'tournament_id': n,
        'player_turn_id': data['player_turn_id'],
        'game_id': data['game_id'],
        'movement': [0, hd[random.randint(0,len(hd)-1)]] })
    else:
        if(random.randint(0,1)==0):
            sio.emit('play', {
            'tournament_id': n,
            'player_turn_id': data['player_turn_id'],
            'game_id': data['game_id'],
            'movement': [0, hd[random.randint(0,len(hd)-1)]] })
        else:
            sio.emit('play', {
            'tournament_id': n,
            'player_turn_id': data['player_turn_id'],
            'game_id': data['game_id'],
            'movement': [1, vd[random.randint(0,len(vd)-1)]] })
        
        '''
    # AI logic
    #print("enviando la info del juego ,",n)
    #sio.emit('play', {
    #'tournament_id': n,
    #'player_turn_id': data['player_turn_id'],
    #'game_id': data['game_id'],
    #'movement': [random.randint(0,1), random.randint(0,29)] })


@sio.on('finish')
def finish(data):
    global n
    print('game is over', data)
    gameID = data["game_id"]
    playerTurnID = data["player_turn_id"]
    winnerTurnID = data["winner_turn_id"]
    board = data["board"]
    sio.emit('player_ready', {
        'tournament_id': n,
        'player_turn_id': playerTurnID,
        'game_id': gameID
    })
    
#Cabeza de minimax
#borad: tablero
#turn: si el jugador que inicia el minimax es 1 o 2
def minimaxStar(board,turn):
    h,v=board
    lh=len(h)
    lv=len(v)
    hd=[]
    vd=[]
    #alpha beta
    alpha=-99
    beta=99
    #Encuentra todos los espacios vacíos
    #Guarda los horizontales en hd y verticales en vd
    for i in range(0,len(h)):
        if(h[i]==99):
            hd.append(i)
    for i in range(0,len(v)):
        if(v[i]==99):
            vd.append(i)
    #Elije entre 4 o la cantidad de movimientos restantes
    levels=min([4,(lh+lv)])
    c=0
    moves=[]
    values=[]
    #Evalua todos los movimientos que puede hacer horizontalmente
    for i in hd:
        moves.append([0,i])
        a=minimaxrecurs(board,turn,levels,0,i,alpha,beta)
        values.append(a)
        #pruning alpha beta
        if (turn==1):
            alpha=max(alpha,a)
        else:
            beta=min(beta,a)
        if beta<=alpha:
            break
    #Evalia todos los movimientos que puede hacer verticalmente
    for i in vd:
        moves.append([1,i])
        a=minimaxrecurs(board,turn,levels,1,i,alpha,beta)
        values.append(a)
        #pruning alpha beta
        if (turn==1):
            alpha=max(alpha,a)
        else:
            beta=min(beta,a)
        if beta<=alpha:
            break
    #Decide si es el minimizador o el maximizador y devuelve
    #el movimiento a realizar
    #hace un random entre los movimientos con el mismo valor para que siempre
    #juegue de manera diferente
    if turn==1:
        listnums=[]
        val=max(values)
        print ("Values:\n",values)
        print ("Val:\n",val)
        for i in range(0,len(values)):
            if (values[i]==val):
                listnums.append(i)
        print("listnums",listnums)
        return moves[listnums[random.randint(0,len(listnums)-1)]]
    else:
        listnums=[]
        val=min(values)
        print ("Values:\n",values)
        print ("Val:\n",val)
        for i in range(0,len(values)):
            if (values[i]==val):
                listnums.append(i)
        print("listnums",listnums)
        return moves[listnums[random.randint(0,len(listnums)-1)]]
    
    
    
#La recursion del minimax
#b: tablero
#turn: si es jugador 1 o 2
#level: cantidad de niveles
#orientacion: Si el movimiento es horizontal o vertical
#pos: Posicion a colocar la linea
#alpha: alpha para alpha-beta pruning
#beta: beta para el alpha-beta pruning
def minimaxrecurs(b,turn,level,orientacion,pos,alpha=-99,beta=99):
    f,g=b
    h=f[:]
    v=g[:]
    board=[h,v]
    level-=1
    turno=1
    #aqui genera el tablero con los movimientos ya realizados y tambien evalua
    #si ese moviiento hace un punto lo cual si lo hace no cambia de turno    
    board,putPoint=calculalrMov(board,orientacion,pos,turn)
    if (putPoint):
        turno=turn
    else:
        turno=1
        if turn==1:
            turno=2
    #Si es el nivel 0 evalúa cuantos puntos hay en el tablero y devuelve los
    #puntos
    if level==0:
        v,h=board
        hd=[]
        vd=[]
        for i in h:
            if(i!=99):
                hd.append(i)
        for i in v:
            if(i!=99):
                vd.append(i)
        return (sum(vd)+sum(hd))
    #Si no es nivel 0 repite el minimax para todos los movimientos disponibles
    else:
        h,v=board
        lh=len(h)
        lv=len(v)
        hd=[]
        vd=[]
        for i in range(0,len(h)):
            if(h[i]==99):
                hd.append(i)
        for i in range(0,len(v)):
            if(v[i]==99):
                vd.append(i)
        values=[]
        for i in hd:
            a=minimaxrecurs(board,turno,level,0,i,alpha,beta)
            values.append(a)
            #pruning alpha-beta
            if (turn==1):
                alpha=max(alpha,a)
            else:
                beta=min(beta,a)
            if beta<=alpha:
                break
        for i in vd:
            a=minimaxrecurs(board,turno,level,0,i,alpha,beta)
            values.append(a)
            #pruning alpha-beta
            if (turn==1):
                alpha=max(alpha,a)
            else:
                beta=min(beta,a)
            if beta<=alpha:
                break
        #devuelve el maximo o minimo dependiendo de que jugador sea
        #--------------------Por que try except?
        #el try-except esta porque cuando falta 2 movimientos el programa falla
        #pero como por logica esos ultimos 2 siempre generan puntos no afectan
        #a la logica general
        if turn==1:
            try:
                return max(values)
            except:
                return 0
        else:
            try:
                return min(values)
            except:
                return 0
        
        

#Actualiza el tablero dentro del minimax para calcular los puntos
def calculalrMov(board,ori,pos,player):
    h,v=board
    lh=len(h)
    lv=len(v)
    l=False
    #menor num horizontal
    anchoH=int(math.isqrt(lh))
    #mayor num horizontal
    altoH=lh/anchoH
    #menor num vertical
    altoV=int(math.isqrt(lv))
    #mayor num vertical
    anchoV=lv/altoV
    if ori==0:
        if (pos % altoH)==0:
            if h[pos+1]!=99:
                if v[int(pos/anchoV)]!=99:
                    if v[int(pos/anchoV)]!=99:
                        l=True
                        if player==1:
                            h[pos]=1
                        else:
                            h[pos]=-1
                    else:
                        h[pos]=0
                else:
                    h[pos]=0
            else:
                h[pos]=0
        elif ((pos+1) % altoH)==0:
            if h[pos-1]!=99:
                f=int(pos/anchoV+lh-anchoV)
                if v[int(f)]!=99:
                    if v[int(f+1)]!=99:
                        l=True
                        if player==1:
                            h[pos]=1
                        else:
                            h[pos]=-1
                    else:
                        h[pos]=0
                else:
                    h[pos]=0
            else:
                h[pos]=0         
        else:
            a=0
            if h[pos-1]!=99:
                r=pos%anchoV
                t=int(pos/anchoV)
                u=int((r-1)*anchoV+t)
                if v[int(u)]!=99:
                    if v[int(u+1)]!=99:
                        l=True
                        a+=1
            if h[pos+1]!=99:
                r=pos%anchoV
                t=int(pos/anchoV)
                u=int(r*anchoV+t)
                if v[int(u)]!=99:
                    if v[int(u+1)]!=99:
                        l=True
                        a+=1
            if player==2:
                a=a*-1
            h[pos]=a
    if ori==1:
        if (pos % anchoV)==0:
            if v[pos+1]!=99:
                if h[int(pos/altoH)]!=99:
                    if h[int(pos/altoH)]!=99:
                        l=True
                        if player==1:
                            v[pos]=1
                        else:
                            v[pos]=-1
                    else:
                        v[pos]=0
                else:
                    v[pos]=0
            else:
                v[pos]=0
        elif ((pos+1) % anchoV)==0:
            if v[pos-1]!=99:
                f=int(pos/altoH)+lv-altoH
                if h[int(f)]!=99:
                    if h[int(f+1)]!=99:
                        l=True
                        if player==1:
                            v[pos]=1
                        else:
                            v[pos]=-1
                    else:
                        v[pos]=0
                else:
                    v[pos]=0
            else:
                v[pos]=0         
        else:
            a=0
            if v[pos-1]!=99:
                r=pos%altoH
                t=int(pos/altoH)
                u=int((r-1)*altoH+t)
                if h[int(u)]!=99:
                    if h[int(u+1)]!=99:
                        l=True
                        a+=1
            if v[pos+1]!=99:
                r=pos%altoH
                t=int(pos/altoH)
                u=int(r*altoH+t)
                if h[int(u)]!=99:
                    if h[int(u+1)]!=99:
                        l=True
                        a+=1
            if player==2:
                a=a*-1
            v[pos]=a
    a=[h,v]
    return a,l
    
    
#Pide el ingreso de la dirección del server    
a=input("Ingrese la direccion del server: ")
#se conecta a la dirección específicada
sio.connect(a)
#Espera respuestas del servidor
sio.wait()
