# -*- coding: utf-8 -*-
"""
ReaL HUD main code YEE BOI 69
"""
# imports
import os
import matplotlib
from matplotlib.figure import Figure
import matplotlib.animation as animation
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib import style
from HandHistory import HandHistory
from configparser import ConfigParser
import tkinter as tk

# load in saved user settings
parser = ConfigParser()
parser.read('ReaLsettings.ini')

autoUpdate = parser.getboolean('settings','autoUpdate')
updateTimeSeconds = parser.getint('settings','updateTimeSeconds')
dir_pstarsHH = os.path.normpath(parser.get('settings','dir_pstarsHH'))
cur_username = parser.get('settings','cur_username')
cur_database = parser.get('settings','cur_database')
dir_priors = parser.get('settings','dir_priors')
dir_ranges = parser.get('settings','dir_ranges')
theme = parser.get('settings','theme')
fontin =  parser.get('settings','font')
plotalpha = parser.getfloat('settings','plotalpha')
handdepth = parser.getint('settings','handdepth')

# set settings
BTN_COLOR = "#214DB3"
CASH_COLOR = "#35f338"
#CASH_COLOR = "#8800ff"
#SD_COLOR = "#36a3e8"
SD_COLOR = "#007bff"
NONSD_COLOR ='#f34f4f'
EV_COLOR = '#fe9832'
suits = {"c": "#00A318",
         "s": "#000000",
         "h": "#FF3333",
         "d": "#0093FB"}    
lightsuits = {"c": "#BFFFC7",
             "s": "#DBDBDB",
             "h": "#FFCCCC",
             "d": "#CCEDFF"}
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
             
DIR_FONT = (fontin, 10)
CARD_FONT = (fontin, 10, 'bold')
if theme == 'dark':
    style.use("dark_background")
    FONT_COLOR = "white"
    BG_COLOR = "black"
    BG_COLOR2 = "white"
    font = {'family': fontin, 'color':  'white', 'weight': 'normal', 'size': 12}
elif theme == 'grey':
    style.use("dark_background")
    FONT_COLOR = "white"
    BG_COLOR = "#202225"
    BG_COLOR2 = "#333333"
    font = {'family': fontin, 'color':  'white', 'weight': 'normal', 'size': 12}
elif theme == 'white':
    style.use("default")
    FONT_COLOR = "black"
    BG_COLOR = "white"
    BG_COLOR2 = "#333333"
    font = {'family': fontin, 'color':  'black', 'weight': 'normal', 'size': 12}
    
pstarsSplit = '\n\n\n\n'

# animation variables
f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)
f.set_facecolor(BG_COLOR)
a.set_facecolor(BG_COLOR)
filelist, fileBytePos = [], []
sdwin, nonsdwin, win, handnum = [0], [0], [0], [0]
importnum = 0
BBScale = 0.05

# hand reporting browser global lists of depth handdepth
handdactionstr = [''] * handdepth
handcrdstr = [['','']] * handdepth
handnetstr = [''] * handdepth
handbrdstr = [['','','','','']] * handdepth
handoptstr = [''] * handdepth

# functions
def sethanddepth(depth):
    global handdactionstr, handcrdstr, handnetstr, handbrdstr, handoptstr
    handdepth = depth
    handdactionstr = [''] * handdepth
    handcrdstr = [['','']] * handdepth
    handnetstr = [''] * handdepth
    handbrdstr = [['','','','','']] * handdepth
    handoptstr = [''] * handdepth
    
def BB2USD(x):
    global BBScale
    return x*BBScale

def USD2BB(x):
    global BBScale
    return x/BBScale

def formathand(hand):
    # convert to general hand format
    if len(hand) != 4 or type(hand) != str:
        print('Input hand is in the wrong format')
        return -1
    if hand[1] == hand[3]:
        newhand = hand[0] + hand[2] + 's'
    elif hand[0] == hand[2]:
        newhand = hand[0] + hand[2]
    else:
        newhand = hand[0] + hand[2] + 'o'
    return newhand
        
def getFreq(directory, presit, hand):
    # gets frequencies from preflop range
    hand = formathand(hand)
    
    with open(os.path.join(directory, presit + '.txt'), 'r') as f:
        contents = f.read()
    split_contents = contents.split(",") 
    
    for entry in split_contents:
        if entry:
            if len(entry) < 4:
                if len(entry) == 3:
                    if entry == hand:
                        return 100
                elif entry[0] == hand[0] and entry[1] == hand[1]:
                    return 100
            else:
                if entry[2] == ':':
                    if entry[0:2] == hand[0:2]:
                        return round(float(entry[3:])*100)
                elif entry[0:3] == hand:
                    return round(float(entry[4:])*100)
    return 0

def handImport(i): 
    # auto imports hands from specified directories
    global importnum, BBScale, handdepth
    global handdactionstr, handcrdstr, handnetstr, handbrdstr, handoptstr
    hands = [] 
    if autoUpdate:
        # grabs new hand writes from the txt files in the specified directory
        index = 0
        for subdir, dirs, files in os.walk(dir_pstarsHH):
            for file in (file for file in files if file.endswith(".txt")):
                if file not in filelist:
                    filelist.append(file) 
                # opening files
                    
                with open(os.path.join(subdir, file), 'r', encoding="utf8") as fd:
                    if len(fileBytePos) > index:
                        fd.seek(fileBytePos[index])
                        
                    handdata = fd.read().split(pstarsSplit)
                    
                    if len(fileBytePos) > index:
                        fileBytePos[index] = fd.tell()
                    else:
                        fileBytePos.append(fd.tell())
                        
                    for hand in (hand for hand in handdata if len(hand) > 10):
                        hands.append(hand) 
                index += 1
                
        # new hands to add to database
        Hands2database = []
        for htext in hands:
            try:
                Hands2database.append(HandHistory.from_string(htext, cur_username))
            except:
                print('Error in reading hand history to HandHistory class:')
                print(htext[0:25])
        
        # check if hands are valid
        flaggedhands = []
        for index, hand in enumerate(Hands2database):
            error = abs(float(hand.rake) + sum(hand.result()))
            tol = 0.01
            
            if hand.flag == 'hand_incomplete':
                print('Hand ' + str(index) + ' still in progress.')
                flaggedhands.append(index)
            elif error > tol:
                print('Hand import error: result checksum: $' + str(error) + ' Board: ' + hand.brd + ' UserCards: ' + hand.usercards + ' Result: ' + str(hand.result()) + ' Tree: ' + hand.preflopTree)
                flaggedhands.append(index)
            
            # keep track of session results
            if index not in flaggedhands:
                importnum += 1
                handnum.append(importnum)
                sd = hand.heroSD()
                useridx = hand.userpos - 1   
                hresult = hand.result()[useridx]
                
                if importnum == 1:
                    sdwin.append(hresult*sd)
                    nonsdwin.append(hresult*(not(sd)))
                    win.append(hresult)
                else:
                    sdwin.append(sdwin[-1] + hresult*sd)
                    nonsdwin.append(nonsdwin[-1] + hresult*(not(sd)))
                    win.append(win[-1] + hresult)
        
        # update hand reporting global lists for active session
        #try:
        for idx in range(len(Hands2database)):
            handdactionstr.pop(-1)
            handdactionstr.insert(0,' | ' + Hands2database[idx].datestamp + ' | ' + Hands2database[idx].preDecision()[0][-1] + ' | ' + Hands2database[idx].preDecision()[1] + ' | ')
            
            handcrdstr.pop(-1)
            handcrdstr.insert(0,[Hands2database[idx].usercards[0:2], Hands2database[idx].usercards[2:4] + ' | '])

            handbrdstr.pop(-1)
            cur_brd = ['','','','','']
            for index in range(int(len(Hands2database[idx].brd)/2)):
                cur_brd[index] = Hands2database[idx].brd[index*2:index*2+2]  
            handbrdstr.insert(0, cur_brd)
            
            handnetstr.pop(-1)
            handnetstr.insert(0, Hands2database[idx].result()[Hands2database[idx].userpos - 1])
            
            # check for errors relative to defined ranges
            sit = Hands2database[idx].preDecision()[2]
            lastaction = Hands2database[idx].preDecision()[1]
            opp_pos = Hands2database[idx].preDecision()[3]
            positionkey = ['BN','SB','BB','EP','MP','CO']
            callfreq, raisefreq, foldfreq = 0,0,0
            if sit == 1:
                raisefreq = getFreq(dir_ranges,'Open-' + positionkey[Hands2database[idx].userpos-1], Hands2database[idx].usercards)
                callfreq = getFreq(dir_ranges,'Call-' + positionkey[Hands2database[idx].userpos-1], Hands2database[idx].usercards)
                foldfreq = 100 - raisefreq - callfreq
            elif sit == 2:
                raisefreq = getFreq(dir_ranges,'3bet-' + positionkey[Hands2database[idx].userpos-1] + 'vs' + positionkey[opp_pos-1], Hands2database[idx].usercards)
                callfreq = getFreq(dir_ranges,'Flat-' + positionkey[Hands2database[idx].userpos-1] + 'vs' + positionkey[opp_pos-1], Hands2database[idx].usercards)
                foldfreq = 100 - raisefreq - callfreq
            elif sit == 3:
                raisefreq = getFreq(dir_ranges,'4bet-' + positionkey[Hands2database[idx].userpos-1] + 'vs' + positionkey[opp_pos-1], Hands2database[idx].usercards)
                callfreq = getFreq(dir_ranges,'Call3bet-' + positionkey[Hands2database[idx].userpos-1] + 'vs' + positionkey[opp_pos-1], Hands2database[idx].usercards)
                foldfreq = 100 - raisefreq - callfreq
            elif sit == 4:
                raisefreq = getFreq(dir_ranges,'5bet-' + positionkey[Hands2database[idx].userpos-1] + 'vs' + positionkey[opp_pos-1], Hands2database[idx].usercards)
                callfreq = getFreq(dir_ranges,'Call4bet-' + positionkey[Hands2database[idx].userpos-1] + 'vs' + positionkey[opp_pos-1], Hands2database[idx].usercards)
                foldfreq = 100 - raisefreq - callfreq
            
            handoptstr.pop(-1)
            if sit != 0:
                if lastaction == 'F':
                    if foldfreq > 0:
                        handoptstr.insert(0,'Y: ' + str(foldfreq) + ' | ' + str(callfreq) + ' | ' + str(raisefreq))
                    else:
                        handoptstr.insert(0,'N: ' + str(foldfreq) + ' | ' + str(callfreq) + ' | ' + str(raisefreq))  
                elif lastaction == 'C':
                    if callfreq > 0:
                        handoptstr.insert(0,'Y: ' + str(foldfreq) + ' | ' + str(callfreq) + ' | ' + str(raisefreq))
                    else:
                        handoptstr.insert(0,'N: ' + str(foldfreq) + ' | ' + str(callfreq) + ' | ' + str(raisefreq))
                elif lastaction == 'R':
                    if raisefreq > 0:
                        handoptstr.insert(0,'Y: ' + str(foldfreq) + ' | ' + str(callfreq) + ' | ' + str(raisefreq))
                    else:
                        handoptstr.insert(0,'N: ' + str(foldfreq) + ' | ' + str(callfreq) + ' | ' + str(raisefreq))
                else:
                    handoptstr.insert(0,'U')
            else:
                handoptstr.insert(0,'U')
                       
        #except:
        #    print('Hand reporting list update error in active session')
        
        # update sessionpage widgets
        app.frames[SessionPage].updateHandslist()
        print('Successfully imported ' + str(len(Hands2database)) + ' hands')      
        hands = []
        
        # update sessionpage graph
        a.clear()
        a.plot([-100,1000000], [0, 0], color=FONT_COLOR)
        a.plot(handnum, nonsdwin, color=NONSD_COLOR, linewidth=3, alpha=plotalpha)
        a.plot(handnum, sdwin, color=SD_COLOR, linewidth=3, alpha=plotalpha)
        a.plot(handnum, win, color=CASH_COLOR, linewidth=3)  
        a.plot(handnum[-1], win[-1], color=CASH_COLOR, marker='o', markersize=8, markerfacecolor=CASH_COLOR, markeredgecolor=CASH_COLOR)
        
        if handnum[-1] == 0:
            title = "Winrate: " + str(round(0, 2)) + " bb/100"
            a.set_title(title, fontsize=14, color=FONT_COLOR, fontdict=font, loc='right')
        elif win[-1] > 0:
            title = "Winrate: " + str(round(100*win[-1]/(handnum[-1]*BBScale), 2)) + " bb/100"
            a.set_title(title, fontsize=14, color=CASH_COLOR, fontdict=font, loc='right')
        else:
            title = "Winrate: " + str(round(100*win[-1]/(handnum[-1]*BBScale), 2)) + " bb/100"
            a.set_title(title, fontsize=14, color=NONSD_COLOR, fontdict=font, loc='right')
                        
        a.set_xlabel('Hands', fontsize=14, fontdict=font)
        a.set_ylabel('Winnings ($USD)', fontsize=14, fontdict=font)
        a.tick_params(labelsize=12)
        a.minorticks_on()
        a.grid(which='major', linestyle=":", linewidth = '0.5', color='grey')
        a.grid(which='minor', linestyle=':', linewidth='0.5', color='grey')
        a.set_xlim(0,round((handnum[-1]+10)*1.05))
        secax = a.secondary_yaxis('right', functions=(USD2BB,BB2USD))
        secax.set_ylabel('Winnings (bb)', fontsize=14, fontdict=font)
        secax.tick_params(labelsize=12)
        for tick in a.get_xticklabels():
            tick.set_fontname(fontin)
        for tick in a.get_yticklabels():
            tick.set_fontname(fontin)
        for tick in secax.get_yticklabels():
            tick.set_fontname(fontin)
        f.tight_layout()
    
def changeDatabase():
    pass
def changeUser():
    pass
def genSettings():
    pass
    
# main tkinter app
class ReaLHUD(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        
        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, "icon.ico")
        tk.Tk.wm_title(self, "ReaL HUD")
        
        container = tk.Frame(self)     
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        menubar = tk.Menu(container)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Change Database", command = changeDatabase())
        filemenu.add_command(label="Change User", command = changeUser())
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.onExit)
        menubar.add_cascade(label="File", menu=filemenu)
        
        optionmenu = tk.Menu(menubar, tearoff=0)
        optionmenu.add_checkbutton(label="General", command = genSettings())
        menubar.add_cascade(label="Settings", menu=optionmenu)
        
        tk.Tk.config(self, menu=menubar)

        self.frames = {}
        
        for F in (StartPage, ReportsPage, SessionPage):
            
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(StartPage)
               
    def show_frame(self, cont):
        
        frame = self.frames[cont]
        frame.tkraise()
    
    def onExit(self):
        self.quit()
        self.destroy()
        
class StartPage(tk.Frame):
    
    def __init__(self, parent, controller): 
        
        tk.Frame.__init__(self, parent)
        self.configure(bg=BG_COLOR)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # frame navigation
        switchframe = tk.Frame(self, bd=0, bg=BG_COLOR, highlightbackground=BG_COLOR, highlightcolor=BG_COLOR, highlightthickness=0)
        labelborder = tk.Frame(switchframe, bd=0, highlightbackground=BG_COLOR, highlightcolor=BTN_COLOR, highlightthickness=1)    
        label = tk.Button(labelborder, text=' Home ', font=DIR_FONT, fg=FONT_COLOR, bg=BG_COLOR, activebackground=BTN_COLOR, bd=0)
        label.pack(side = tk.LEFT)
        labelborder.pack(side=tk.LEFT) 
        switchbutton = tk.Button(switchframe, text=' Reports ', font=DIR_FONT, fg=FONT_COLOR, bg=BG_COLOR, activebackground=BTN_COLOR, command=lambda: controller.show_frame(ReportsPage))
        switchbutton.pack(side = tk.LEFT)
        switchbutton2 = tk.Button(switchframe, text=' Active Session ', font=DIR_FONT, fg=FONT_COLOR, bg=BG_COLOR, activebackground=BTN_COLOR, command=lambda: controller.show_frame(SessionPage))
        switchbutton2.pack(side = tk.LEFT)
        switchframe.grid(row=0,column=0,sticky='NW')
        
class ReportsPage(tk.Frame):
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg=BG_COLOR) 
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # frame navigation
        switchframe = tk.Frame(self, bd=0, bg=BG_COLOR, highlightbackground=BG_COLOR, highlightcolor=BG_COLOR, highlightthickness=0)
        switchbutton = tk.Button(switchframe, text=' Home ', font=DIR_FONT, fg=FONT_COLOR, bg=BG_COLOR, activebackground=BTN_COLOR, command=lambda: controller.show_frame(StartPage))
        switchbutton.pack(side = tk.LEFT)
        labelborder = tk.Frame(switchframe, bd=0, highlightbackground=BG_COLOR, highlightcolor=BTN_COLOR, highlightthickness=1)    
        label = tk.Button(labelborder, text=' Reports ', font=DIR_FONT, fg=FONT_COLOR, background=BG_COLOR, activebackground=BTN_COLOR, bd=0)
        label.pack(side = tk.LEFT)
        labelborder.pack(side=tk.LEFT) 
        switchbutton2 = tk.Button(switchframe, text=' Active Session ', font=DIR_FONT, fg=FONT_COLOR, background=BG_COLOR, activebackground = BTN_COLOR, command=lambda: controller.show_frame(SessionPage))
        switchbutton2.pack(side = tk.LEFT)
        switchframe.grid(row=0,column=0,sticky='NW',columnspan=2)
        
class SessionPage(tk.Frame):
    
    def __init__(self, parent, controller):
        global handdactionstr, handcrdstr, handnetstr, handbrdstr, handdepth
        tk.Frame.__init__(self, parent)
        self.configure(bg=BG_COLOR)
        self.grid_columnconfigure(0, weight=5)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=5)
        
        # frame navigation
        switchframe = tk.Frame(self, bd=0, bg=BG_COLOR, highlightbackground=BG_COLOR, highlightcolor=BG_COLOR, highlightthickness=0)
        switchbutton = tk.Button(switchframe, text=' Home ', font=DIR_FONT, fg=FONT_COLOR, background=BG_COLOR, activebackground = BTN_COLOR, command=lambda: controller.show_frame(StartPage))
        switchbutton.pack(side = tk.LEFT)
        switchbutton2 = tk.Button(switchframe, text=' Reports ', font=DIR_FONT, fg=FONT_COLOR, background=BG_COLOR, activebackground = BTN_COLOR, command=lambda: controller.show_frame(ReportsPage))
        switchbutton2.pack(side = tk.LEFT)
        labelborder = tk.Frame(switchframe, bd=0, highlightbackground=BG_COLOR, highlightcolor=BTN_COLOR, highlightthickness=1)  
        label = tk.Label(labelborder, text=' Active Session ', font=DIR_FONT, fg=FONT_COLOR, background=BG_COLOR, activebackground=BTN_COLOR, bd=0)
        label.pack(side = tk.LEFT)
        labelborder.pack(side=tk.LEFT) 
        switchframe.grid(row=0,column=0,sticky='NW')     
        
        # paned window
        panedwindow = tk.PanedWindow(self, bd=4, bg=BG_COLOR, showhandle=True, relief="raised")
        panedwindow.grid(row=1,column=0,sticky='NSEW', pady=5, padx=5)
        
        # active session graph
        plotframe = tk.Frame(panedwindow, bd=0, bg=BG_COLOR, highlightbackground=BG_COLOR, highlightcolor=BG_COLOR, highlightthickness=0)
        canvas = FigureCanvasTkAgg(f, plotframe)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5, padx=5)
        #toolbar = NavigationToolbar2Tk(canvas, plotframe)
        #toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=15, padx=15)
        #plotframe.grid(row=1,column=0,sticky='NSEW', pady=5, padx=5)
        panedwindow.add(plotframe)
        
        # update button for hand reporting browser
        updateBtnframe = tk.Frame(panedwindow, bd=1,highlightbackground=FONT_COLOR, highlightcolor=BTN_COLOR,highlightthickness=1)    
        updateBtn = tk.Button(updateBtnframe, text="Force Hand Refresh", command=self.updateHandslist, font=DIR_FONT, fg=FONT_COLOR, bg=BG_COLOR2, activebackground=BTN_COLOR,bd=0, padx=20, pady=20)
        updateBtn.pack(side=tk.TOP, fill='both', expand=True)
        #updateBtnframe.grid(row=0,column=1,sticky='NSEW', padx=20, pady=20)
        #panedwindow.add(updateBtnframe)
        
        # hand reporting browser for active session
        handsframe = tk.Frame(panedwindow, bd=0, bg=BG_COLOR, highlightbackground=BG_COLOR, highlightcolor=BG_COLOR, highlightthickness=0)
              
        self.handdaction = []
        self.handcrd0 = []
        self.handcrd1 = []
        self.handbrd0 = []
        self.handbrd1 = []
        self.handbrd2 = []
        self.handbrd3 = []
        self.handbrd4 = []
        self.handnet = []
        self.handopt = []
        handframes = []
        self.handcrd0labels = []
        self.handcrd1labels = []
        self.handdactionlabels = []
        self.handbrd0labels = []
        self.handbrd1labels = []
        self.handbrd2labels = []
        self.handbrd3labels = []
        self.handbrd4labels = []
        self.handnetlabels = []
        self.handoptlabels = []
        
        handtitleframe = tk.Frame(handsframe, bd=0, bg=BG_COLOR, highlightbackground=BG_COLOR, highlightcolor=BG_COLOR, highlightthickness=0)
        
        handcrdtitle = tk.Label(handtitleframe, text ='Crds', fg=FONT_COLOR, font=DIR_FONT, bg=BG_COLOR)
        handcrdtitle.grid(row=0,column=0, columnspan=2, padx=1, pady=1, sticky='NW') 
        handdactiontitle = tk.Label(handtitleframe, text = '|        Date         | Preflop | Action | ', fg=FONT_COLOR, font=DIR_FONT, bg=BG_COLOR, width=55, anchor = 'nw')
        handdactiontitle.grid(row=0,column=2, padx=1, pady=1, sticky='NW')    
        handbrdtitle = tk.Label(handtitleframe, text='Board', fg=FONT_COLOR, font=DIR_FONT, bg=BG_COLOR, width=7, anchor = 'nw')
        handbrdtitle.grid(row=0,column=3, columnspan=5, padx=1, pady=1, sticky='NW') 
        handnettitle = tk.Label(handtitleframe, text='Net Won', fg=FONT_COLOR, font=DIR_FONT, bg=BG_COLOR, width=7)
        handnettitle.grid(row=0,column=8, padx=5, pady=1, sticky='NW') 
        handopttitle = tk.Label(handtitleframe, text='Errors f|c|r', fg=FONT_COLOR, font=DIR_FONT, bg=BG_COLOR)
        handopttitle.grid(row=0,column=9, padx=5, pady=1, sticky='NW') 
                
        handtitleframe.pack(side = tk.TOP, pady=2, padx=2, anchor = 'nw')
        
        for idx in range(handdepth):
            self.handdaction.append(tk.StringVar())
            self.handcrd0.append(tk.StringVar())
            self.handcrd1.append(tk.StringVar())
            self.handbrd0.append(tk.StringVar())
            self.handbrd1.append(tk.StringVar())
            self.handbrd2.append(tk.StringVar())
            self.handbrd3.append(tk.StringVar())
            self.handbrd4.append(tk.StringVar())
            self.handnet.append(tk.StringVar())
            self.handopt.append(tk.StringVar())
            
            handframes.append(tk.Frame(handsframe, bd=0, bg=BG_COLOR, highlightbackground=BG_COLOR, highlightcolor=BG_COLOR, highlightthickness=0))
            
            self.handcrd0labels.append(tk.Label(handframes[idx], textvariable=self.handcrd0[idx], fg=FONT_COLOR, font=CARD_FONT, bg=BG_COLOR, borderwidth=1,relief="solid"))
            self.handcrd0labels[idx].grid(row=0,column=0, padx=1, pady=1, sticky='NW') 
            self.handcrd1labels.append(tk.Label(handframes[idx], textvariable=self.handcrd1[idx], fg=FONT_COLOR, font=CARD_FONT, bg=BG_COLOR, borderwidth=1,relief="solid"))
            self.handcrd1labels[idx].grid(row=0,column=1, padx=1, pady=1, sticky='NW') 
            self.handdactionlabels.append(tk.Label(handframes[idx], textvariable = self.handdaction[idx], fg=FONT_COLOR, font=DIR_FONT, bg=BG_COLOR, width=55, anchor = 'nw'))
            self.handdactionlabels[idx].grid(row=0,column=2, padx=1, pady=1, sticky='NW') 
            self.handbrd0labels.append(tk.Label(handframes[idx], textvariable=self.handbrd0[idx], fg=FONT_COLOR, font=CARD_FONT, bg=BG_COLOR, width=1, anchor = 'nw', borderwidth=1,relief="solid"))
            self.handbrd0labels[idx].grid(row=0,column=3, padx=1, pady=1, sticky='NW') 
            self.handbrd1labels.append(tk.Label(handframes[idx], textvariable=self.handbrd1[idx], fg=FONT_COLOR, font=CARD_FONT, bg=BG_COLOR, width=1, anchor = 'nw', borderwidth=1,relief="solid"))
            self.handbrd1labels[idx].grid(row=0,column=4, padx=1, pady=1, sticky='NW') 
            self.handbrd2labels.append(tk.Label(handframes[idx], textvariable=self.handbrd2[idx], fg=FONT_COLOR, font=CARD_FONT, bg=BG_COLOR, width=1, anchor = 'nw', borderwidth=1,relief="solid"))
            self.handbrd2labels[idx].grid(row=0,column=5, padx=1, pady=1, sticky='NW') 
            self.handbrd3labels.append(tk.Label(handframes[idx], textvariable=self.handbrd3[idx], fg=FONT_COLOR, font=CARD_FONT, bg=BG_COLOR, width=1, anchor = 'nw', borderwidth=1,relief="solid"))
            self.handbrd3labels[idx].grid(row=0,column=6, padx=1, pady=1, sticky='NW') 
            self.handbrd4labels.append(tk.Label(handframes[idx], textvariable=self.handbrd4[idx], fg=FONT_COLOR, font=CARD_FONT, bg=BG_COLOR, width=1, anchor = 'nw', borderwidth=1,relief="solid"))
            self.handbrd4labels[idx].grid(row=0,column=7, padx=1, pady=1, sticky='NW') 
            self.handnetlabels.append(tk.Label(handframes[idx], textvariable=self.handnet[idx], fg=FONT_COLOR, font=DIR_FONT, bg=BG_COLOR, width=7))
            self.handnetlabels[idx].grid(row=0,column=8, padx=5, pady=1, sticky='NW') 
            self.handoptlabels.append(tk.Label(handframes[idx], textvariable=self.handopt[idx], fg=FONT_COLOR, font=DIR_FONT, bg=BG_COLOR))
            self.handoptlabels[idx].grid(row=0,column=9, padx=5, pady=1, sticky='NW') 
            
            handframes[idx].pack(side = tk.TOP, pady=2, padx=2, anchor = 'nw')

        #handsframe.grid(row=1,column=1,sticky='NSEW',pady=5, padx=5)
        panedwindow.add(handsframe)
        
    def updateHandslist(self):
                     
        for idx in range(handdepth):     
            self.handdaction[idx].set(handdactionstr[idx])
            if handoptstr[idx]:
                if handoptstr[idx][0] == 'N':
                    self.handdactionlabels[idx].config(fg=FONT_COLOR,bg=NONSD_COLOR)
                    
            if handcrdstr[idx][0]:
                self.handcrd0[idx].set(handcrdstr[idx][0][0])
                self.handcrd0labels[idx].config(fg = suits[handcrdstr[idx][0][1]], bg = lightsuits[handcrdstr[idx][0][1]])
                self.handcrd1[idx].set(handcrdstr[idx][1][0])
                self.handcrd1labels[idx].config(fg = suits[handcrdstr[idx][1][1]], bg = lightsuits[handcrdstr[idx][1][1]])
                
            if handbrdstr[idx][0]:
                self.handbrd0[idx].set(handbrdstr[idx][0][0])
                self.handbrd0labels[idx].config(fg = suits[handbrdstr[idx][0][1]], bg = lightsuits[handbrdstr[idx][0][1]])
                self.handbrd1[idx].set(handbrdstr[idx][1][0])
                self.handbrd1labels[idx].config(fg = suits[handbrdstr[idx][1][1]], bg = lightsuits[handbrdstr[idx][1][1]])
                self.handbrd2[idx].set(handbrdstr[idx][2][0])
                self.handbrd2labels[idx].config(fg = suits[handbrdstr[idx][2][1]], bg = lightsuits[handbrdstr[idx][2][1]])
            else:
                self.handbrd0labels[idx].config(bg = BG_COLOR2)
                self.handbrd1labels[idx].config(bg = BG_COLOR2)
                self.handbrd2labels[idx].config(bg = BG_COLOR2)
                
            if handbrdstr[idx][3]:
                self.handbrd3[idx].set(handbrdstr[idx][3][0])
                self.handbrd3labels[idx].config(fg = suits[handbrdstr[idx][3][1]], bg = lightsuits[handbrdstr[idx][3][1]])
            else:
                self.handbrd3labels[idx].config(bg = BG_COLOR2)
            if handbrdstr[idx][4]:
                self.handbrd4[idx].set(handbrdstr[idx][4][0])
                self.handbrd4labels[idx].config(fg = suits[handbrdstr[idx][4][1]], bg = lightsuits[handbrdstr[idx][4][1]])
            else:
                self.handbrd4labels[idx].config(bg = BG_COLOR2)
            self.handnet[idx].set(handnetstr[idx])
            
            if handnetstr[idx]:
                if handnetstr[idx] == 0:
                    self.handnetlabels[idx].config(fg=FONT_COLOR, bg=BG_COLOR)
                elif float(handnetstr[idx]) > 0:
                    self.handnetlabels[idx].config(fg=FONT_COLOR, bg=CASH_COLOR)
                else:
                    self.handnetlabels[idx].config(fg=FONT_COLOR, bg=NONSD_COLOR)         
            
            self.handopt[idx].set(handoptstr[idx])
            if handoptstr[idx]:
                if handoptstr[idx][0] == 'Y':
                    self.handoptlabels[idx].config(fg=FONT_COLOR,bg=CASH_COLOR)
                elif handoptstr[idx][0] == 'N':
                    self.handoptlabels[idx].config(fg=FONT_COLOR,bg=NONSD_COLOR)
app = ReaLHUD()
app.geometry("1600x900+160+70")
ani = animation.FuncAnimation(f, handImport, interval=5000)
app.mainloop()
