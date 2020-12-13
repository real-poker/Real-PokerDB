class HandHistory:   
    
    num_hands = 0
    
    def __init__(self, realID, handID, datestamp, site, game, users, username, usercards, oppcards, userpos, stacks, preflopTree, flopTree, turnTree, riverTree, brd, rake, showdown, flag):
        HandHistory.num_hands += 1
        self.realID = HandHistory.num_hands
        self.handID = handID
        self.datestamp = datestamp
        self.site = site
        self.users = users
        self.username = username
        self.usercards = usercards
        self.userpos = userpos
        self.preflopTree = preflopTree
        self.flopTree = flopTree     
        self.turnTree = turnTree 
        self.riverTree = riverTree 
        self.brd = brd 
        self.rake = rake
        self.game = game
        self.oppcards = oppcards
        self.showdown = showdown
        self.stacks = stacks
        self.flag = flag

    @classmethod
    def from_string(cls, h_str, username):
        import re
        # define required variables, etc.
        supportedSites = ['PokerStars','RunItOnce']
        supportedGames = ['Zoom']
        supportedStakes = ['$0.01/$0.02','$0.02/$0.05','$0.05/$0.10','$0.12/$0.25','$0.25/$0.50']
        deck = {0: "2",
             1: "3",
             2: "4",
             3: "5",
             4: "6",
             5: "7",
             6: "8",
             7: "9",
             8: "T",
             9: "J",
             10: "Q",
             11: "K",
             12: "A"}
        inv_deck = {v: k for k, v in deck.items()}
        
        # set error flag empty
        flag = ''
        
        # split hand history line by line
        datalines = h_str.split('\n')
        
        # assign realID for ordering purposes
        HandHistory.num_hands += 1
        realID = HandHistory.num_hands
        
        # find handID
        match = re.search(r'\#\d+(?:\.\d+)?', datalines[0])
        handID = int(match.group()[1:])
        
        # find hand datetime
        match = re.search(r'(\d{4}/\d{2}/\d{2} \d+:\d+:\d+)', datalines[0])
        datestamp = match.group().replace('/','-')
        
        # detect site
        site = next((x for x in supportedSites if x in datalines[0]), 'Unknown')
        
        # detect game type and stakes
        gamematch = next((x for x in supportedGames if x in datalines[0]), 'Unknown')
        stakematch = next((x for x in supportedStakes if x in datalines[0]), 'Unknown')
        game = gamematch + ' ' + stakematch
        
        # parse hand history and scalp trees and other variables
        preDeal, preFlop, onFlop, onTurn, onRiver, endHand = True, False, False, False, False, False
        
        seats, userpos = 0, 0
        users, stacks, oppcards = [], [], []
        preflopTree, flopTree, turnTree, riverTree, brd, rake, usercards = '', '', '', '', '', '0', ''
        showdown = False

        for line in datalines:
            
            if preDeal:
                linedata = line.split(' ')
                if linedata[0] == 'Seat':
                    seats += 1
                    userstring = re.findall('(?<=\:)(.*)(?=\(\$)', line)[0].strip()
                    users.append(userstring)
                    if userstring == username:
                        userpos = seats
                    match = re.search(r'\$\d+(?:\.\d+)?',line)
                    stacks.append(match.group()[1:])
                elif 'small blind' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    preflopTree += str(currentPos) + 'P' + linedata[-1][1:] + ','
                elif 'big blind' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    preflopTree += str(currentPos) + 'P' + linedata[-1][1:] + ','
                elif linedata[0] == '***':
                    preDeal, preFlop = False, True
                    
            elif preFlop:
                if 'Dealt ' in line:
                    handstring = re.findall('\[([^]]+)', line)[-1]
                    handstring = handstring.replace(" ","")
                    
                    handnums = []
                    suits = []
                    for char in handstring:
                        if char in inv_deck:
                            handnums.append(inv_deck[char]) 
                        else:
                            suits.append(char)
                    handnums, suits = zip(*sorted(zip(handnums, suits),reverse=True))
                    
                    for index, idx in enumerate(handnums):
                        usercards += deck[idx]
                        usercards += suits[index]
                        
                elif ' folds ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    preflopTree += str(currentPos) + 'F,'
                    
                elif ' calls ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    preflopTree += str(currentPos) + 'C' + match[-1][1:] + ','
                    
                elif ' raises ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    preflopTree += str(currentPos) + 'R' + match[-1][1:] + ','
                
                elif ' bets ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    preflopTree += str(currentPos) + 'B' + match[-1][1:] + ','
                    
                elif ': checks' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    preflopTree += str(currentPos) + 'X,'
                
                elif ' returned ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    preflopTree += str(currentPos) + 'U' + match[0][1:] + ','
                                      
                elif '*** SUMMARY ***' in line:   
                    endHand = True
                    
                elif '*** FLOP ***' in line:
                    flopstring = re.findall('\[([^]]+)', line)[0]
                    flopstring = flopstring.replace(" ","")
                    flopnums = []
                    suits = []
                    for char in flopstring:
                        if char in inv_deck:
                            flopnums.append(inv_deck[char]) 
                        else:
                            suits.append(char)
                    flopnums, suits = zip(*sorted(zip(flopnums, suits),reverse=True))

                    for index, idx in enumerate(flopnums):
                        brd += deck[idx]
                        brd += suits[index]
    
                    preFlop, onFlop = False, True
                    
                elif ' Rake ' in line:
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    rake = match[-1][1:]
                    
                elif endHand:
                    if any(y in line for y in ['won', 'collected']):
                        usermatch = next((x for x in users if x in line), 'Unknown')
                        currentPos = users.index(usermatch) % seats + 1
                        match = re.findall(r'\(\$([^)]+)',line)
                        for entry in match:
                            preflopTree += str(currentPos) + 'W' + entry + ','
                                
            elif onFlop:    
                if ' folds ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    flopTree += str(currentPos) + 'F,'
                    
                elif ' calls ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    flopTree += str(currentPos) + 'C' + match[-1][1:] + ','
                    
                elif ' raises ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    flopTree += str(currentPos) + 'R' + match[-1][1:] + ','
                
                elif ' bets ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    flopTree += str(currentPos) + 'B' + match[-1][1:] + ','
                    
                elif ': checks' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    flopTree += str(currentPos) + 'X,'
                
                elif ' returned ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    flopTree += str(currentPos) + 'U' + match[0][1:] + ','      
                    
                elif '*** SUMMARY ***' in line:   
                    endHand = True
                    
                elif '*** TURN ***' in line:
                    turnstring = re.findall('\[([^]]+)', line)[1]
                    brd += turnstring    
                    onFlop, onTurn = False, True
                    
                elif ' Rake ' in line:
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    rake = match[-1][1:] 
                    
                elif endHand:
                    if any(y in line for y in ['won', 'collected']):
                        usermatch = next((x for x in users if x in line), 'Unknown')
                        currentPos = users.index(usermatch) % seats + 1
                        match = re.findall(r'\(\$([^)]+)',line)
                        for entry in match:
                            flopTree += str(currentPos) + 'W' + entry + ','
                    
            elif onTurn:
                if ' folds ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    turnTree += str(currentPos) + 'F,'
                    
                elif ' calls ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    turnTree += str(currentPos) + 'C' + match[-1][1:] + ','
                    
                elif ' raises ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    turnTree += str(currentPos) + 'R' + match[-1][1:] + ','
                
                elif ' bets ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    turnTree += str(currentPos) + 'B' + match[-1][1:] + ','
                    
                elif ': checks' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    turnTree += str(currentPos) + 'X,'
                
                elif ' returned ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    turnTree += str(currentPos) + 'U' + match[0][1:] + ','
                    
                    
                elif '*** SUMMARY ***' in line:   
                    endHand = True
                    
                elif '*** RIVER ***' in line:
                    riverstring = re.findall('\[([^]]+)', line)[1]
                    brd += riverstring    
                    onTurn, onRiver = False, True
                    
                elif ' Rake ' in line:
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    rake = match[-1][1:] 
                    
                elif endHand:
                    if any(y in line for y in ['won', 'collected']):
                        usermatch = next((x for x in users if x in line), 'Unknown')
                        currentPos = users.index(usermatch) % seats + 1
                        match = re.findall(r'\(\$([^)]+)',line)
                        for entry in match:
                            turnTree += str(currentPos) + 'W' + entry + ','
                    
            elif onRiver:
                if ' folds ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    riverTree += str(currentPos) + 'F,'
                    
                elif ' calls ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    riverTree += str(currentPos) + 'C' + match[-1][1:] + ','
                    
                elif ' raises ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    riverTree += str(currentPos) + 'R' + match[-1][1:] + ','
                
                elif ' bets ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    riverTree += str(currentPos) + 'B' + match[-1][1:] + ','
                    
                elif ': checks' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    riverTree += str(currentPos) + 'X,'
                
                elif ' returned ' in line:
                    usermatch = next((x for x in users if x in line), 'Unknown')
                    currentPos = users.index(usermatch) % seats + 1
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    riverTree += str(currentPos) + 'U' + match[0][1:] + ','
                                       
                elif '*** SHOW DOWN ***' in line:   
                    showdown = True
                    
                elif '*** SUMMARY ***' in line:   
                    endHand = True
                    
                elif ' Rake ' in line:
                    match = re.findall(r'\$\d+(?:\.\d+)?',line)
                    rake = match[-1][1:]
                    
                elif endHand:
                    if any(y in line for y in ['won', 'collected']):
                        usermatch = next((x for x in users if x in line), 'Unknown')
                        currentPos = users.index(usermatch) % seats + 1
                        match = re.findall(r'\(\$([^)]+)',line)
                        for entry in match:
                            riverTree += str(currentPos) + 'W' + entry + ','
                            
                    if any(y in line for y in [' showed ', ' mucked ']):
                        usermatch = next((x for x in users if x in line), 'Unknown')
                        currentPos = users.index(usermatch) % seats + 1
                        
                        handstring = re.findall('\[([^]]+)', line)[-1]
                        handstring = handstring.replace(" ","")
                        
                        handnums = []
                        suits = []
                        for char in handstring:
                            if char in inv_deck:
                                handnums.append(inv_deck[char]) 
                            else:
                                suits.append(char)
                        handnums, suits = zip(*sorted(zip(handnums, suits),reverse=True))
                        
                        cards = ''
                        for index, idx in enumerate(handnums):
                            cards += deck[idx]
                            cards += suits[index]

                        oppcards.append(str(currentPos) + ':' + cards)
        
        if not endHand:
            flag = 'hand_incomplete'
            
        return cls(realID, handID, datestamp, site, game, users, username, usercards, oppcards, userpos, stacks, preflopTree, flopTree, turnTree, riverTree, brd, rake, showdown, flag)
    
    
    def heroSD(self):
        # returns whether user was at the showdown
        opphands = []
        for entry in self.oppcards:
            opphands.append(entry.split(':')[-1])
            
        if self.usercards in opphands:
            return True
        return False
    
    def preDecision(self):
        # returns string indication preflop decision
        import re
        treestring = self.preflopTree 
        upos = self.userpos
        
        playeractions = []
        positionkey = ['BN','SB','BB','EP','MP','CO']  
        
        opened = False
        openflat = False
        open3bet = False
        open3betflat = False
        open4bet = False
        limped = False
        useropened = False
        userisolated = False
        userlimped = False
        userflat = False
        user3bet = False
        usercoldflat3bet = False
        userflat3bet = False
        user4bet = False
        userflat4bet = False
        user5bet = False
        usercoldflat4bet = False
        userfolded = False
        was3bet = False
        was4bet = False
        was5bet = False
        userlastaction = ''
        
        sit = 0
        opppos = 0
        count = 0
        for action in treestring.split(','):
            if not not action:
                useridxstr = re.search(r'\d+',action).group()
                action = action[len(useridxstr):]
                useridx = int(useridxstr)
                
                # disregard blind postings and opponenent fold actions
                if action[0] == 'P':
                    pass
                elif action[0] == 'F' and useridx != upos:
                    pass
                
                # preflop action until hero is reached
                elif count == 0:
                    if useridx != upos:
                        if not opened and not limped:
                            if action[0] == 'C':
                                limped = True
                                limppos = useridx   
                        if not opened:
                            if action[0] == 'R':
                                opened = True
                                openpos = useridx    
                        elif open3bet:   
                            if action[0] == 'R':
                                open4bet = True
                                open4betpos = useridx
                            elif action[0] == 'C':
                                open3betflat = True
                                open3betflatpos = useridx       
                        elif opened:
                            if action[0] == 'R':
                                open3bet = True
                                open3betpos = useridx
                            elif action[0] == 'C':
                                openflat = True
                                openflatpos = useridx
                                
                    # hero 1st action decision
                    elif useridx == upos:
                        if open4bet:
                            opppos = open4betpos
                            if action[0] == 'C':
                                usercoldflat4bet = True
                                playeractions.append('Cold Called 4bet-' + positionkey[upos-1] + 'vs' + positionkey[open4betpos-1])
                            elif action[0] == 'R':
                                user5bet = True
                                playeractions.append('Cold 5bet-' + positionkey[upos-1] + 'vs' + positionkey[open4betpos-1])
                            elif action[0] == 'F':
                                playeractions.append('Folded-' + positionkey[upos-1] + 'vs' + positionkey[open4betpos-1] + ' Cold 4bet')
                        elif open3bet:
                            opppos = open3betpos
                            if action[0] == 'C':
                                usercoldflat3bet = True
                                playeractions.append('Cold Called 3bet-' + positionkey[upos-1] + 'vs' + positionkey[open3betpos-1] + 'vs' + positionkey[openpos-1])
                            elif action[0] == 'R':
                                user4bet = True
                                playeractions.append('Cold 4bet-' + positionkey[upos-1] + 'vs' + positionkey[open3betpos-1] + 'vs' + positionkey[openpos-1])
                            elif action[0] == 'F':
                                playeractions.append('Folded-' + positionkey[upos-1] + 'vs' + positionkey[open3betpos-1] + ' 3bet vs' + positionkey[openpos-1])
                        elif opened:
                            sit = 2
                            opppos = openpos
                            if openflat:
                                if action[0] == 'F':
                                    playeractions.append('Folded-' + positionkey[upos-1] + 'vs' + positionkey[openpos-1] + ' Open ' + positionkey[openflatpos-1] + ' Flat')
                                elif action[0] == 'C':
                                    playeractions.append('Flat-' + positionkey[upos-1] + 'vs' + positionkey[openpos-1] + ' Open ' + positionkey[openflatpos-1] + ' Flat')
                                    userflat = True
                                elif action[0] == 'R':
                                    playeractions.append('Squeezed-' + positionkey[upos-1] + 'vs' + positionkey[openpos-1] + ' Open ' + positionkey[openflatpos-1] + ' Flat')
                                    user3bet = True
                            else:
                                if action[0] == 'F':
                                    playeractions.append('Folded-' + positionkey[upos-1] + 'vs' + positionkey[openpos-1] + ' Open')
                                elif action[0] == 'C':
                                    playeractions.append('Flat-' + positionkey[upos-1] + 'vs' + positionkey[openpos-1] + ' Open')
                                    userflat = True
                                elif action[0] == 'R':
                                    playeractions.append('3bet-' + positionkey[upos-1] + 'vs' + positionkey[openpos-1] + ' Open')
                                    user3bet = True
                        elif limped:
                            sit = 0
                            if action[0] == 'C':
                                userlimped = True
                                playeractions.append('Over Limped-' + positionkey[upos-1] + 'vs' + positionkey[limppos-1])
                            elif action[0] == 'R':
                                userisolated = True
                                playeractions.append('Isolated Limper-' + positionkey[upos-1] + 'vs' + positionkey[limppos-1])
                            elif action[0] == 'F':
                                playeractions.append('Folded-' + positionkey[upos-1])
                            else:
                                playeractions.append('Checked-' + positionkey[upos-1])
                        else:
                            sit = 1
                            if action[0] == 'C':
                                userlimped = True
                                playeractions.append('Limped-' + positionkey[upos-1])
                            elif action[0] == 'R':
                                useropened = True
                                playeractions.append('Opened-' + positionkey[upos-1])
                            elif action[0] == 'F':
                                playeractions.append('Folded-' + positionkey[upos-1])
                            else:
                                playeractions.append('Checked-' + positionkey[upos-1])
                                           
                        if action[0] == 'F':
                            userfolded = True
                            userlastaction = 'F'
                        elif action[0] == 'C':
                            userlastaction = 'C'
                        elif action[0] == 'R':
                            userlastaction = 'R'
                        elif action[0] == 'X':
                            userlastaction = 'X'
                        count += 1
                        
           
                # preflop action after heros 1st action
                elif count == 1 and not userfolded:
                    
                    # preflop action until hero is reached
                    if useropened and action[0] == 'R' and useridx != upos:
                        if was4bet:
                            was5bet = True
                            a5betpos = useridx 
                        elif was3bet:
                            was4bet = True
                            a4betpos = useridx  
                        else:
                            was3bet = True
                            a3betpos = useridx          
                    elif user3bet and action[0] == 'R' and useridx != upos:
                        if was4bet:
                            was5bet = True
                            a5betpos = useridx  
                        else:
                            was4bet == True
                            a4betpos = useridx  
                            
                    # hero 2nd action decision
                    elif useridx == upos:
                        if useropened:
                            if was5bet:
                                opppos = a5betpos
                                if action[0] == 'F':
                                    playeractions.append('Folded-' + positionkey[upos-1] + 'vs' + positionkey[a5betpos-1] + ' Cold 5bet')
                                if action[0] == 'C':
                                    playeractions.append('CalledCold5bet-' + positionkey[upos-1] + 'vs' + positionkey[a5betpos-1])
                                if action[0] == 'R':
                                    playeractions.append('6bet-' + positionkey[upos-1] + 'vs' + positionkey[a5betpos-1] + ' Cold 5bet')
                            elif was4bet:
                                opppos = a4betpos
                                if action[0] == 'F':
                                    playeractions.append('Folded-' + positionkey[upos-1] + 'vs' + positionkey[a4betpos-1] + ' Cold 4bet')
                                if action[0] == 'C':
                                    playeractions.append('CalledCold4bet-' + positionkey[upos-1] + 'vs' + positionkey[a4betpos-1])
                                if action[0] == 'R':
                                    playeractions.append('5bet-' + positionkey[upos-1] + 'vs' + positionkey[a4betpos-1] + ' Cold 4bet')
                            elif was3bet:
                                opppos = a3betpos
                                sit = 3
                                if action[0] == 'C':
                                    playeractions.append('Called3bet-' + positionkey[upos-1] + 'vs' + positionkey[a3betpos-1])
                                    userflat3bet = True
                                elif action[0] == 'R':
                                    playeractions.append('4bet-' + positionkey[upos-1] + 'vs' + positionkey[a3betpos-1])
                                    user4bet = True
                                elif action[0] == 'F':
                                    playeractions.append('Folded-' + positionkey[upos-1] + 'vs' + positionkey[a3betpos-1] + ' 3bet')
                        elif user3bet:
                            if was5bet:
                                opppos = a5betpos
                                if action[0] == 'F':
                                    playeractions.append('Folded-' + positionkey[upos-1] + 'vs' + positionkey[a5betpos-1] + ' Cold 5bet')
                                elif action[0] == 'C':
                                    playeractions.append('CalledCold5bet-' + positionkey[upos-1] + 'vs' + positionkey[a5betpos-1])
                                elif action[0] == 'R':
                                    playeractions.append('6bet-' + positionkey[upos-1] + 'vs' + positionkey[a5betpos-1] + ' Cold 5bet')
                            elif was4bet:
                                sit = 4
                                opppos = a4betpos
                                if action[0] == 'C':
                                    userflat4bet = True
                                    playeractions.append('Called4bet-' + positionkey[upos-1] + 'vs' + positionkey[a4betpos-1])
                                elif action[0] == 'R':
                                    playeractions.append('5bet-' + positionkey[upos-1] + 'vs' + positionkey[a4betpos-1])
                                    user5bet = True
                                elif action[0] == 'F':
                                    playeractions.append('Folded-' + positionkey[upos-1] + 'vs' + positionkey[a4betpos-1] + ' 4bet')
                            
                        if action[0] == 'F':
                            userfolded = True
                            userlastaction = 'F'
                        elif action[0] == 'C':
                            userlastaction = 'C'
                        elif action[0] == 'R':
                            userlastaction = 'R'
                        elif action[0] == 'X':
                            userlastaction = 'X'
                        count += 1   
           
        return playeractions, userlastaction, sit, opppos
                    
                    
    def result(self):
        # returns the net winnings/losings of each player in the hand
        import re
        
        # initialize players net winnings/losings on each street
        netcashpre, netcashflop, netcashturn, netcashriver, netcash = [], [], [], [], []
        for players in self.users:
            netcashpre.append(0)
            netcashflop.append(0)
            netcashturn.append(0)
            netcashriver.append(0)
            netcash.append(0)
            
        if self.flag:
            return netcash
        
        # preflop betting
        treestring = self.preflopTree    
        tableval = 0
        for action in treestring.split(','):
            if not not action:
                useridx = re.search(r'\d+',action).group()
                action = action[len(useridx):]
                if action[0] == 'P':
                    postblind = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashpre[int(useridx)-1] = -postblind
                    tableval = max(tableval, postblind)
                elif action[0] == 'C':
                    callamount = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashpre[int(useridx)-1] = netcashpre[int(useridx)-1] - callamount
                elif action[0] == 'R':
                    raisesize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashpre[int(useridx)-1] = -raisesize
                    tableval = max(tableval, raisesize)
                elif action[0] == 'B':
                    betsize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashpre[int(useridx)-1] = -betsize
                    tableval = max(tableval, betsize)
                elif action[0] == 'U':
                    uncalledsize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashpre[int(useridx)-1] = netcashpre[int(useridx)-1] + uncalledsize
                elif action[0] == 'W':
                    winsize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashpre[int(useridx)-1] = netcashpre[int(useridx)-1] + winsize
                    
        # flop betting
        treestring = self.flopTree    
        tableval = 0
        for action in treestring.split(','):
            if not not action:
                useridx = re.search(r'\d+',action).group()
                action = action[len(useridx):]
                if action[0] == 'C':
                    callamount = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashflop[int(useridx)-1] = netcashflop[int(useridx)-1] - callamount
                elif action[0] == 'R':
                    raisesize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashflop[int(useridx)-1] = -raisesize
                    tableval = max(tableval, raisesize)
                elif action[0] == 'B':
                    betsize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashflop[int(useridx)-1] = -betsize
                    tableval = max(tableval, betsize)
                elif action[0] == 'U':
                    uncalledsize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashflop[int(useridx)-1] = netcashflop[int(useridx)-1] + uncalledsize
                elif action[0] == 'W':
                    winsize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashflop[int(useridx)-1] = netcashflop[int(useridx)-1] + winsize
        
        # turn betting
        treestring = self.turnTree    
        tableval = 0
        for action in treestring.split(','):
            if not not action:
                useridx = re.search(r'\d+',action).group()
                action = action[len(useridx):]
                if action[0] == 'C':
                    callamount = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashturn[int(useridx)-1] = netcashturn[int(useridx)-1] - callamount
                elif action[0] == 'R':
                    raisesize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashturn[int(useridx)-1] = -raisesize
                    tableval = max(tableval, raisesize)
                elif action[0] == 'B':
                    betsize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashturn[int(useridx)-1] = -betsize
                    tableval = max(tableval, betsize)
                elif action[0] == 'U':
                    uncalledsize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashturn[int(useridx)-1] = netcashturn[int(useridx)-1] + uncalledsize
                elif action[0] == 'W':
                    winsize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashturn[int(useridx)-1] = netcashturn[int(useridx)-1] + winsize
                    
        # river betting
        treestring = self.riverTree    
        tableval = 0
        for action in treestring.split(','):
            if not not action:
                useridx = re.search(r'\d+',action).group()
                action = action[len(useridx):]
                if action[0] == 'C':
                    callamount = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashriver[int(useridx)-1] = netcashriver[int(useridx)-1] - callamount
                elif action[0] == 'R':
                    raisesize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashriver[int(useridx)-1] = -raisesize
                    tableval = max(tableval, raisesize)
                elif action[0] == 'B':
                    betsize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashriver[int(useridx)-1] = -betsize
                    tableval = max(tableval, betsize)
                elif action[0] == 'U':
                    uncalledsize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashriver[int(useridx)-1] = netcashriver[int(useridx)-1] + uncalledsize
                elif action[0] == 'W':
                    winsize = float(re.search(r'\d+(\.\d+)?',action).group())
                    netcashriver[int(useridx)-1] = netcashriver[int(useridx)-1] + winsize
        
        for index, val in enumerate(netcash):
            netcash[index] = round(netcashpre[index] + netcashflop[index] + netcashturn[index] + netcashriver[index], 2)
            
        return netcash
    
    def __repr__(self):
        return "HandHistory('{}', '{}', {})".format(self.realID, self.datestamp, self.username)
