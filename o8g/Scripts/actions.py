import time
import re
from itertools import repeat

Resource = ("Resource", "6eb6d990-007a-4f4d-b76c-b35685922b22")
Damage = ("Damage", "3abb22bb-b259-4857-ae8f-f2cdf93de5e0")
Clue = ("Clue", "33d9ed22-458b-4c7f-9901-5daf2fa43a23")
Horror = ("Horror", "9461c5e5-1aa8-4286-88f1-01661a8aaa02")
Doom = ("Doom", "a6605071-57d2-4e7f-b6b4-7809147a565a")
Lock = ("Lock", "62d688a4-46ef-45be-9414-2257a1221351")
Action = ("Action", "654ac64a-ff25-42dd-946f-cc15c03448cf")

BoardWidth = 1100
Spacing = 92
InvestigatorSpacing = 10
InvestigatorY = 175
StagingStart = -515
StagingWidth = 619
StagingY = -222
StagingSpace = 82
AgendaX = 221
AgendaY = -222
ActX = 309
ActY = -222
EncounterX = 147
EncounterY = -234.75
ScenarioX = 408.5
ScenarioY = -234.75
CampaignX = 500
CampaignY = -234.75
ChaosTokenX = 94
ChaosTokenY = -211
ChaosBagX = 0
ChaosBagY = -234.75
DoneColour = "#D8D8D8" # Grey
WaitingColour = "#FACC2E" # Orange
ActiveColour = "#82FA58" # Green
EliminatedColour = "#FF0000" # Red
showDebug = False #Can be changed to turn on debug - we don't care about the value on game reconnect so it is safe to use a python global

def debug(str):
    if showDebug:
        whisper(str)

def toggleDebug(group, x=0, y=0):
    global showDebug
    showDebug = not showDebug
    if showDebug:
        notify("{} turns on debug".format(me))
    else:
        notify("{} turns off debug".format(me))


def phasePassed(args):
    mute()
    thisPhase = currentPhase()
    newPhase = thisPhase[1]
    
    if newPhase == 1:
        if turnNumber() != 1 and getGlobalVariable("allowMythosPhase") == "True":
            doMythosPhase(False)
            setGlobalVariable("allowMythosPhase", "False")
    elif newPhase == 2:
        # Investigation Phase
        mute()
    elif newPhase == 3:
        # Enemy
        mute()
    elif newPhase == 4 and getGlobalVariable("allowUpkeepPhase") == "True":
        # Upkeep
        remoteCall(me, "doUpkeepPhase", [False])
        
        setGlobalVariable("allowUpkeepPhase", "False")


def turnPassed(args):
    setGlobalVariable("allowMythosPhase", "True")
    setGlobalVariable("allowUpkeepPhase", "True")
    
    if turnNumber() == 1:
        setPhase(2)
    else:
        setPhase(1)
    

def advancePhase(group = None, x = 0, y = 0):
    if turnNumber() == 0:
        me.setActive()
    else:
        thisPhase = currentPhase()
        nextPhase = thisPhase[1] + 1
        if nextPhase > 4:
            me.setActive()
        else:
            setPhase(nextPhase)

        
#Return the default x coordinate of the players investigator
def investigatorX(player):
    return (BoardWidth * player / len(getPlayers())) - (BoardWidth / 2)

def num(s):
   if not s: return 0
   try:
      return int(s)
   except ValueError:
      return 0

def moveCard(model, x, y):
    for c in table:
        if c.model == model:
            c.moveToTable(x, y)
            return c
    return table.create(model, x, y)

#Find and return this players left most hero card
def firstInvestigator(player):
    first = None
    for h in table:
        if h.controller == player and h.Type == "Investigator" and h.isFaceUp:
            if first is None:
                first = h
            else:
                x,y = h.position
                minx, miny = first.position
                if x < minx:
                    first = h
    return first

def getPlayer(id):
    for p in getPlayers():
        if playerID(p) == id:
            return p
    return None

def countInvestigators(p):
    investigators = 0
    for card in table:
        if card.controller == p and card.Type == "Investigator":
            investigators += 1
    return investigators

#Work out if the player is still in the game (threat < 50 and has heroes on the table)
def eliminated(p):
    if not p:
        return False
#
#   if p.counters['Threat_Level'].value >= 50:
#       debug("eliminated({}) = True (Threat)".format(p))
#       return True
#
#   heroes = countHeroes(p)
#   if heroes == 0:
#       debug("eliminated({}) = True (No Heroes)".format(p))
#       return True
#
#   return False

def cardDoubleClicked(args):
    # args = card, mouseButton, keysDown
    mute()
    card = args.card
    if hasattr(card, 'Type'):
        if card.Type == "Chaos Bag": # Draw Chaos Token
            drawChaosTokenForPlayer(me, [])
        elif card.Type == "Chaos Token": # Discard Chaos Token
            if card.controller == me:
                doDiscard(me, card, chaosBag())
            else:
                remoteCall(card.controller, "doDiscard", [me, card, chaosBag()])
        elif card.Type == "Encounter Draw": # Draw Encounter Card
            addEncounter(table)
        elif card.Type == "Path": # Rotate Path cards
            rotateRight(card)

def activePlayers():
    count=0
    for p in getPlayers():
        count+=1
#       if not eliminated(p):
#           count+=1
    return count

#def nextPlayer(current):
#   if not eliminated(me):
#       fp = getFirstPlayerToken()
#       if fp is not None and isLocked(fp):
#           return me
#
#   np = me
#   tries = 0
#   while tries < len(getPlayers()):
#       current = (current + 1) % len(getPlayers())
#       p = getPlayer(current)
#       if not eliminated(p):
#           np = p
#           break
#       tries += 1
#   return np

def agendaCount(group):
    count = 0
    for c in group:
        if c.Type == "Agenda":
            count += 1
    return (count)

def actCount(group):
    count = 0
    for c in group:
        if c.Type == "Act":
            count += 1
    return (count)

#Check see if a card at x1,y1 overlaps a card at x2,y2
def overlaps(x1, y1, x2, y2, w1, h1, w2 = 0, h2 = 0):
    # if no width/height specified for card 2, assumed card 2 has the same dimensions as card 1
    if w2 == 0:
        w2 = w1
    if h2 == 0:
        h2 = h1
    #Four checks, one for each corner
    if int(x1) >= int(x2) and int(x1) <= int(x2) + int(w2) and int(y1) >= int(y2) and int(y1) <= int(y2) + int(h2): return True
    if int(x1) + int(w1) >= int(x2) and int(x1) <= int(x2) and int(y1) >= int(y2) and int(y1) <= int(y2) + int(h2): return True
    if int(x1) >= int(x2) and int(x1) <= int(x2) + int(w2) and int(y1) + int(h1) >= int(y2) and int(y1) <= int(y2): return True
    if int(x1) + int(w1) >= int(x2) and int(x1) <= int(x2) and int(y1) + int(h1) >= int(y2) and int(y1) <= int(y2): return True
    return False

def overlapPartialCard(x, y):
    cw = 0
    ch = 0
    for c in table:
        cx, cy = c.position
        if overlaps(x, y, cx, cy, cw, ch):
            return c
    return None

# check if the card with specified dimension being inserted at
# position x, y overlaps with any existing card
def overlapCard(x, y, width, height, ignoreChaosToken = True):
    for existingCard in table:
        if overlaps(x, y, cardX(existingCard), cardY(existingCard), width, height, existingCard.width, existingCard.height):
            if not ignoreChaosToken:
                return existingCard
            elif existingCard.Type != 'Chaos Token':
                return existingCard

    return None

def cardX(card):
    x, y = card.position
    return x

def cardY(card):
    x, y = card.position
    return y

#Move the given card in the staging area to the first available space on the left of the Staging Area
#If there is no room then we compress all the cards in the staging area to make room
def layoutStage(card):
    x = StagingStart
    y = StagingY
    s = StagingSpace
    while x < StagingStart + StagingWidth - s:
        if overlapCard(x, y, cardX(card), cardY(card)) is None:
            card.moveToTable(x, y)
            return
        x += s
    card.moveToTable(x - s, y)
    #There was no room - we neeed to move all the cards to make space
    staged = []
    for c in table:
        if c.Type != 'Chaos Token' and overlaps(cardX(c), cardY(c), StagingStart, StagingY, StagingWidth, 100):
            staged.append(c)

    for c in staged:
        cx, cy = c.position
        shift = (cx - StagingStart) // len(staged)
        c.moveToTable(cx - shift, cy)

def clearTargets(group=table, x=0, y=0):
    for c in group:
        if c.controller == me or (c.targetedBy is not None and c.targetedBy == me):
            c.target(False)

def clearHighlights(group=table, x=0, y=0):
    for c in group: # Safe to do on all cards, not just ones we control
        c.highlight = None

def findCard(group, model):
    for c in group:
        if c.model == model:
            return c
    return None

def encounterDeck():
    return shared.piles['Encounter']

def encounterDiscard():
    return shared.piles['Encounter Discard Pile']

def specialDeck():
    return shared.piles['Special']

def specialDiscard():
    return shared.piles['Special Discard Pile']

def agendaDeck():
    return shared.piles['Agenda']

def agendaDiscard():
    return shared.piles['Agenda Discard Pile']

def actDeck():
    return shared.piles['Act']

def actDiscard():
    return shared.piles['Act Discard Pile']

def locationDeck():
    return shared.piles['Location']

def locationDiscard():
    return shared.piles['Location Discard Pile']

def chaosBag():
    return shared.piles['Chaos Bag']

def setupDeck():
    return shared.piles['Setup']

def isPlayerCard(card):
    return card.owner in getPlayers()

def isLocationCard(card):
    return card.Type == 'Location'

def isChaosToken(card):
    return card.Type == 'Chaos Token'

#------------------------------------------------------------
# Global variable manipulations function
#------------------------------------------------------------

def getLock():
    lock = getGlobalVariable("lock")
    if lock == str(me._id):
        return True

    if len(lock) > 0: #Someone else has the lock
        return False

    setGlobalVariable("lock", str(me._id))
    if len(getPlayers()) > 1:
        update()
    return getGlobalVariable("lock") == str(me._id)

def clearLock():
    lock = getGlobalVariable("lock")
    if lock == str(me._id):
        setGlobalVariable("lock", "")
        update()
        return True
    debug("{} id {} failed to clear lock id {}".format(me, me._id, lock))
    return False


#Store this player's starting position (his ID for this game)
#The first player is 0, the second 1 ....
#These routines set global variables so should be called within getLock() and clearLock()
#After a reset, the game count will be updated by the first player to setup again which invalidates all current IDs
def myID():
    if me.getGlobalVariable("game") == getGlobalVariable("game") and len(me.getGlobalVariable("playerID")) > 0:
        return playerID(me) # We already have a valid ID for this game
        
    g = getGlobalVariable("playersSetup")
    if len(g) == 0:
        id = 0
    else:
        id = num(g)
    me.setGlobalVariable("playerID", str(id))
    game = getGlobalVariable("game")
    me.setGlobalVariable("game", game)
    setGlobalVariable("playersSetup", str(id+1))
    update()
    debug("Player {} sits in position {} for game {}".format(me, id, game))
    return id

def playerID(p):    
    return num(p.getGlobalVariable("playerID"))

#In phase management this represents the player highlighted in green
def setActivePlayer(p):
   if p is None:
       setGlobalVariable("activePlayer", "-1")
   else:
       setGlobalVariable("activePlayer", str(playerID(p)))
   update()

def setPlayerDone():
    done = getGlobalVariable("done")
    if done:
        playersDone = eval(done)
    else:
        playersDone = set()
    playersDone.add(me._id)
    setGlobalVariable("done", str(playersDone))
    #notify("done {}".format(str(playersDone)))
    update()

def deckLocked():
    return me.getGlobalVariable("deckLocked") == "1"

def lockDeck():
    me.setGlobalVariable("deckLocked", "1")
    
def unlockDeck():
    me.setGlobalVariable("deckLocked", "0")
        
#---------------------------------------------------------------------------
# Workflow routines
#---------------------------------------------------------------------------

#Triggered event OnGameStart
def startOfGame(): 
    unlockDeck()
    setActivePlayer(None)   
    if me._id == 1:
        setGlobalVariable("playersSetup", "")       
        setGlobalVariable("game", str(num(getGlobalVariable("game"))+1))
        notify("Starting Game {}".format(getGlobalVariable("game")))

    #---------------------------------------------------------------------------
    # NEW
    #---------------------------------------------------------------------------
    setGlobalVariable("currentPlayers",str([]))
    
  

#Triggered event OnLoadDeck
# args: player, groups
def deckLoaded(args):
    mute()
    if args.player != me:
        return
    
    isShared = False
    isPlayer = False
    for g in args.groups:
        if (g.name == 'Hand') or (g.name in me.piles):
            isPlayer = True
        elif g.name in shared.piles:
            isShared = True
    
    #If we are loading into the shared piles we need to become the controller of all the shared piles   
    if isShared:
        notify("{} Takes control of the encounter deck".format(me))
        for p in shared.piles:
            if shared.piles[p].controller != me:
                shared.piles[p].controller = me
        #rnd(1,2) # This causes OCTGN to sync the controller changes!
        update()
            
    #Cards for the encounter deck and player deck are loaded into the discard pile because this has visibility="all"    
    #Check for cards with a Setup effects and move other cards back into the correct pile
    for pile in args.groups:
        for card in pile:
            if card.Setup == 't' and card.Type not in [ 'Agenda' , 'Act', 'Scenario' ]:
                addToTable(card)
            elif card.Setup == 's' and card.Type not in [ 'Agenda' , 'Act', 'Scenario' ]:
                addToStagingArea(card)
            elif pile == shared.piles['Encounter Discard Pile']:
                card.moveTo(shared.piles['Encounter'])
            elif pile == me.piles['Discard Pile']:
                card.moveTo(me.deck)
        if pile.name == "Chaos Bag":
            createChaosBag(table)
        elif pile.name == "Encounter Discard Pile":
            createEncounterCardClicky(table)


    update()
    playerSetup(table, 0, 0, isPlayer, isShared)
    #if automate():         <-----Turning off Automation by default for ScriptVersion updates, but still want playerSetup to run
    #   playerSetup(table, 0, 0, isPlayer, isShared)

def loadBasicWeaknesses(group, x = 0, y = 0):
    basic_weakness_pile = me.piles[BasicWeakness.PILE_NAME]
    if len(basic_weakness_pile) == 0:
        choice_list = ['all', 'core']
        color_list = ['#0000FF', '#00FF00']
        sets = askChoice("Which sets to load?", choice_list, color_list)
        # load all sets if window is closed
        if sets == 0:
            sets = 1
        bw = BasicWeakness(me, choice_list[sets - 1])
        bw.create_deck()
        basic_weakness_pile.shuffle()
        notify("{} loaded Basic Weakness Deck".format(me))
    else:
        notify("{}'s Basic Weakness Deck already loaded.".format(me))
        
# #Triggered event OnPlayerGlobalVariableChanged
# #We use this to manage turn and phase management by tracking changes to the player "done" variable            
def globalChanged(args):
    debug("globalChanged(Variable {}, from {}, to {})".format(args.name, args.oldValue, args.value))
    if args.name == "done":
        checkPlayersDone()
    elif args.name == "phase":
        notify("Phase: {}".format(args.value))
        
# calculate the number of plays that are Done
def numDone():
    done = getGlobalVariable("done")
    if done:
        return len(eval(done))
    else:
        return 0
    
def highlightPlayer(p, state):
    if len(getPlayers()) <= 1:
        return
    debug("highlightPlayer {} = {}".format(p, state))
    for card in table:
        if card.Type == "Investigator" and card.controller == p and card.isFaceUp:
            card.highlight = state

#Called when the "done" global variable is changed by one of the players
#We use this check to see if all players are ready to advance to the next phase 
#Note - all players get called whenever any player changes state. To ensure we don't all do the same thing multiple times
#       only the Encounter player is allowed to change the phase or step and only the player triggering the event is allowed to change the highlights   
def checkPlayersDone():
    mute()
    if not turnManagement():
        return

    #notify("done updated: {} {}".format(numDone(), len(getPlayers())))
    if numDone() == len(getPlayers()):
        doUpkeepPhase()
        doMythosPhase()
        setGlobalVariable("phase", "Investigator")
        setGlobalVariable("done", str(set()))

#---------------------------------------------------------------------------
# Table menu options
#---------------------------------------------------------------------------
def isLocation(cards):
    for c in cards:
        if c.Type != 'Location':
            return False
    return True
    
def isEnemy(cards):
    for c in cards:
        if c.isFaceUp and (c.type != "Enemy" or c.orientation == Rot90):
            return False
    return True
    
# def isFirstPlayerToken(cards):
#   for c in cards:
#       if c.model != "15e40d4f-b763-4dcc-aa52-e32b64a992dd":
#           return False
#   return True
    
#---------------------------------------------------------------------------
# Table group actions
#---------------------------------------------------------------------------

def turnManagementOn(group, x=0, y=0):
    mute()
    setGlobalVariable("Automation", "Turn")
    clearHighlights(group)
    
def automationOff(group, x = 0, y = 0):
    mute()
    setGlobalVariable("Automation", "Off")
    clearHighlights(group)
    notify("{} disables all turn management".format(me))
    
def turnManagement():
    mute()
    auto = getGlobalVariable("Automation")
    return auto == "Turn" or len(auto) == 0

def createChaosBag(group, x=0, y=0):
    for c in group:
        if c.owner == me and c.model == "faa82643-1dda-4af7-96ad-298bc2d5b2dd":
            c.moveToTable(x, y)
            return
    group.create("faa82643-1dda-4af7-96ad-298bc2d5b2dd", ChaosBagX, ChaosBagY, 1, False)

def createEncounterCardClicky(group, x=0, y=0):
    group.create("f4633a2e-0102-452d-8387-678b5aa17878", EncounterX, EncounterY, 1, False)

def flipCoin(group, x = 0, y = 0):
    mute()
    n = rnd(1, 2)
    if n == 1:
        notify("{} flips heads.".format(me))
    else:
        notify("{} flips tails.".format(me))

def randomPlayer(group, x=0, y=0):
    mute()
    players = getPlayers()
    if len(players) <= 1:
        notify("{} randomly selects {}".format(me, me))
    else:
        n = rnd(0, len(players)-1)
        notify("{} randomly selects {}".format(me, players[n]))

def randomAsset(group, x=0, y=0):
    mute()
    randomCard(table, "Asset")

def randomHero(group, x=0, y=0):
    mute()
    randomCard(table, "Investigator")
    
def randomCard(group, type):
    n = 0
    for card in group:
        if card.controller == me and card.Type == type:
            n = n + 1
    if n == 0:
        whisper("You have no cards of that type")
    else:
        c = rnd(1, n)
        n = 0
        for card in group:
            if card.controller == me and card.Type == type:
                n = n + 1
                if n == c:
                    notify("{} randomly selects {}".format(me, card))
                    card.select()

def randomNumber(group, x=0, y=0):
    mute()
    max = askInteger("Random number range (1 to ....)", 6)
    if max == None: return
    notify("{} randomly selects {} (1 to {})".format(me, rnd(1,max), max))

def readyForRefresh(group, x = 0, y = 0):
    mute()
    if turnManagement():
        highlightPlayer(me, WaitingColour)
    doRestoreAll()
    
def doRestoreAll(group=table): 
    mute()
        
    debug("doRestoreAll({})".format(group)) 
    myCards = (card for card in group
                if card.controller == me)
    for card in myCards:
        if not isLocked(card) and not card.anchor:
            card.orientation &= ~Rot90
    notify("{} readies all their cards.".format(me))

def resetEncounterDeck(group):
    if group == specialDeck():
        discard = specialDiscard()
    else:
        discard = encounterDiscard()
    if len(discard) == 0: return
    for c in discard:
        c.moveTo(group)
    notify("{} moves all cards from {} to {}".format(me, discard.name, group.name))
    shuffle(group)

def addHidden(group=None, x=0, y=0):
    nextEncounter(encounterDeck(), x, y, True)

def addHiddenSpecial(group, x=0, y=0):
    nextEncounter(specialDeck(), x, y, True)
    
def addEncounter(group=None, x=0, y=0):
    nextEncounter(encounterDeck(), x, y, False)
    
def addEncounterSpecial(group=None, x=0, y=0):
    nextEncounter(specialDeck(), x, y, False)

def addLocation(group=None, x=0, y=0):
    nextLocation(locationDeck(), x, y)

def addToStagingArea(card, facedown=False, who=me):
    #Check to see if there is already an encounter card here.
    #If so shuffle it left to make room
    ex = StagingStart + StagingWidth - card.width
    ey = StagingY
    move = overlapCard(ex, ey, card.width, card.height)
    while move is not None:
        layoutStage(move)
        move = overlapCard(ex, ey, card.width, card.height)
    card.moveToTable(ex, ey, facedown)          
    layoutStage(card)
    notify("{} adds '{}' to the staging area.".format(who, card))
    
def nextEncounter(group, x, y, facedown, who=me):
    mute()

    if group.controller != me:
        remoteCall(group.controller, "nextEncounter", [group, x, y, facedown, me])
        return
        
    if len(group) == 0:
        resetEncounterDeck(group)
    if len(group) == 0: # No cards
        return
        
    clearTargets()
    card = group.top()
    if x == 0 and y == 0:  #Move to default position in the staging area
        #addToStagingArea(card, facedown, who)   
        card.moveToTable(EncounterX, EncounterY, facedown)
        notify("{} places '{}' on the table.".format(who, card))    
    else:
        card.moveToTable(x, y, facedown)
        notify("{} places '{}' on the table.".format(who, card))
    card.controller = who
    if len(group) == 0:
        resetEncounterDeck(group)

def nextLocation(group, x, y, who=me):
    mute()

    if group.controller != me:
        remoteCall(group.controller, "nextLocation", [group, x, y, me])
        return

    if len(group) == 0:
        notify("No more location cards")
        return

    card = group.top()
    if x == 0 and y == 0:  #Move to default position in the staging area
        addToStagingArea(card, False, who)
    else:
        card.moveToTable(x-card.width()/2, y-card.height()/2, facedown)
        notify("{} places '{}' on the table.".format(who, card))
    card.controller = who
    
def nextAgendaStage(group=None, x=0, y=0):
    mute()
    
    #We need a new Agenda card
    if group is None or group == table:
        group = agendaDeck()
    if len(group) == 0: return
    
    if group.controller != me:
        remoteCall(group.controller, "nextAgendaStage", [group, x, y])
        return
        
    if x == 0 and y == 0: #The keyboard shortcut was used
        #Count Agenda cards already on table to work out where to put this one
        #n, count = questCount(table)
        #x = QuestStartX + 89*(count // 2) + 64*n
        #y = QuestStartY + 64*(count % 2)   
        x = AgendaX
        y = AgendaY
            
    card = group.top()
    card.moveToTable(x, y)
    
    agendaSetup(card)
    notify("{} advances agenda to '{}'".format(me, card))

    
def nextActStage(group=None, x=0, y=0):
    mute()
    
    #We need a new Act card
    if group is None or group == table:
        group = actDeck()
    if len(group) == 0: return
    
    if group.controller != me:
        remoteCall(group.controller, "nextActStage", [group, x, y])
        return
        
    if x == 0 and y == 0: #The keyboard shortcut was used
        #Count Agenda cards already on table to work out where to put this one
        #n, count = questCount(table)
        #x = QuestStartX + 89*(count // 2) + 64*n
        #y = QuestStartY + 64*(count % 2)   
        x = ActX
        y = ActY
            
    card = group.top()
    card.moveToTable(x, y)
    
    notify("{} advances act to '{}'".format(me, card))	
	
	
def addToTable(card):
    x = AgendaX - 45.5
    y = -96
    blocked = overlapPartialCard(x, y)
    while blocked is not None:
        x += 16
        blocked = overlapPartialCard(x, y)
    card.moveToTable(x, y)  
    
def agendaSetup(card):
    if len(card.Setup) + len(setupDeck()) > 0:
        cardsToStage = card.Setup.count('s')
        i = 0
        for c in setupDeck():
            if c.Type == "Scenario":
                c.moveToTable(ScenarioX, ScenarioY)
            elif c.Type == "Campaign":
                c.moveToTable(CampaignX, CampaignY)
            elif i >= len(card.Setup) or card.Setup[i] == 't':
                addToTable(c)
            elif card.Setup[i] == 's':
                addToStagingArea(c)
                setReminders(c)
            # elif card.Setup[i] == 'l':
            #   makeActive(c)
            #   setReminders(c)
            i += 1
def nextAgenda(group = None, x = 0, y = 0):
    nextAgendaStage(group, x, y)

def nextActStage(group=None, x=0, y=0):
    mute()
    
    #If the current Act card has side A showing it is simply flipped and we are done
    for c in table:
        if c.Type in ("Act") and c.alternates is not None and "B" in c.alternates and c.alternate != "B":
            flipcard(c)
            return
    
    #We need a new Act card
    if group is None or group == table:
        group = actDeck()
    if len(group) == 0: return
    
    if group.controller != me:
        remoteCall(group.controller, "nextActStage", [group, x, y])
        return
        
    if x == 0 and y == 0: #The keyboard shortcut was used
        #Count Act cards already on table to work out where to put this one
        #n, count = questCount(table)
        #x = QuestStartX + 89*(count // 2) + 64*n
        #y = QuestStartY + 64*(count % 2)   
        x = ActX
        y = ActY
            
    card = group.top()
    card.moveToTable(x, y)
    
#   actSetup(card)
    notify("{} advances act to '{}'".format(me, card))

def nextAct(group = None, x = 0, y = 0):
    nextActStage(group, x, y)

def setAbilityCounters(investigatorCard):
    me.counters['Willpower'].value = num(investigatorCard.Willpower)
    me.counters['Intellect'].value = num(investigatorCard.Intellect)
    me.counters['Combat'].value = num(investigatorCard.Combat)
    me.counters['Agility'].value = num(investigatorCard.Agility)
    me.counters['Maximum Hand Size'].value = num("8")
    
    
def readyForNextRound(group=table, x=0, y=0):
    mute()
    #notify("readyForNextRound {}".format(turnManagement()))
    if turnManagement():
        highlightPlayer(me, DoneColour)
        setPlayerDone()

def doUpkeepPhase(setPhaseVar = True):
    mute()
    debug("doUpkeepPhase()")
    
    if setPhaseVar:
        setGlobalVariable("phase", "Upkeep")

    if activePlayers() == 0:
        whisper("All players have been eliminated: You have lost the game")
        return
    if eliminated(me):
        whisper("You have been eliminated from the game")
        return

    clearTargets()
    doRestoreAll()
    draw(me.deck)
    
    # Check for hand size!
    sizeHand = me.counters['Maximum Hand Size'].value
    if len(me.hand) > sizeHand:
        discardCount = len(me.hand) - sizeHand
        dlg = cardDlg(me.hand)
        dlg.title = "You have more than the allowed "+ str(sizeHand) +" cards in hand."
        dlg.text = "Select " + str(discardCount) + " Card(s):"
        dlg.min = 0
        dlg.max = discardCount
        cardsSelected = dlg.show()
        if cardsSelected is not None:
            for card in cardsSelected:
                discard(card)
    
    for card in table:
        if card.Type == "Investigator" and card.controller == me and not isLocked(card) and card.isFaceUp:
            addResource(card)
        elif card.Type == "Mini" and card.controller == me:
            card.markers[Action] = 0
            if card.alternates is not None and "" in card.alternates:
                card.alternate = ''

    shared.counters['Round'].value += 1
    clearHighlights()

def doMythosPhase(setPhaseVar = True):
    mute()
    debug("doMythosPhase()")
    
    if setPhaseVar:
        setGlobalVariable("phase", "Mythos")

    for card in table:
        if card.Type == "Agenda" and card.controller == me and not isLocked(card) and card.isFaceUp:
            addDoom(card)

def playerSetup(group=table, x=0, y=0, doPlayer=True, doEncounter=False):
    mute()

    if not getLock():
        whisper("Others players are setting up, please try manual setup again (Ctrl+Shift+S)")
        return
        
    unlockDeck()
    if doPlayer:
        id = myID() # This ensures we have a unique ID based on our position in the setup order
        investigatorCount = countInvestigators(me)
        
        # Find any Permanent cards
        permanents = filter(lambda card: "Permanent" in card.Keywords or "Permanent." in card.Text, me.deck)
        
        # Move Investigators to the table
        newInvestigator = False
        investigator = filter(lambda card: card.Type == "Investigator", me.hand)
        mini = filter(lambda card: card.Type == "Mini", me.hand)
        miniX = 0
        miniWidth = 0
        if investigator and mini:
            investigatorCount += 1
            newInvestigator = True
            investigatorCard = investigator[0]
            setAbilityCounters(investigatorCard)
            miniCard = mini[0]
            investigatorCard.moveToTable(investigatorX(id), InvestigatorY)
            miniX = cardX(investigatorCard) + investigatorCard.width + InvestigatorSpacing
            miniCard.moveToTable(miniX, cardY(investigatorCard))
            miniWidth = miniCard.width
            notify("{} places his Investigator on the table".format(me))
        
        # Move any Permanents found to the table
        permX = miniX + miniWidth + InvestigatorSpacing
        for card in permanents:
            card.moveToTable(permX, cardY(investigatorCard))
            permX = permX + card.width + InvestigatorSpacing
            notify("{} places the Permanent card {} on the table".format(me, card))
        
        if newInvestigator:
            if len(me.hand) == 0:
                drawOpeningHand()
            for i in repeat(None, 5):
                addResource(investigatorCard)
        
        
    # If we loaded the encounter deck - add the first Agenda & Act card to the table
    if doEncounter or encounterDeck().controller == me:
        count = agendaCount(table)
        if count == 0:
            nextAgendaStage()
            nextActStage()
            shuffle(locationDeck())
            shuffle(encounterDeck())
            shuffle(specialDeck())  
        
    if not clearLock():
        notify("Players performed setup at the same time causing problems, please reset and try again")

def drawOpeningHand():
    me.deck.shuffle()
    drawMany(me.deck, shared.OpeningHandSize)
    removeWeaknessCards()

def removeWeaknessCards():
    weaknesses = []
    for card in filter(lambda card: card.Subtype in ["Weakness", "Basic Weakness"], me.hand):
        weaknesses.append(card)
        notify("{} replacing weakness '{}'".format(me, card))

    if not weaknesses: return None

    drawMany(me.deck, len(weaknesses))
    for card in weaknesses:
        card.moveTo(me.deck)

    return removeWeaknessCards()
    
def toggleLock(group, x=0, y=0):
    if deckLocked():
        unlockDeck()
        if len(me.deck) > 0:
            if isLocked(me.deck.top()):
                lockCard(me.deck.top())
        notify("{} Unlocks his deck".format(me))
    else:
        lockDeck()
        if len(me.deck) > 0:
            lockCard(me.deck.top())
        notify("{} Locks his deck".format(me))
    
#---------------------------------------------------------------------------
# Table card actions
#---------------------------------------------------------------------------

def defaultAction(card, x = 0, y = 0):
    mute()
    # Default for Done button is playerDone
    if not card.isFaceUp: #Face down card - flip
        flipcard(card, x, y)
    elif card.Type == "Path": # Action handled in OnCardDoubleClicked
        # Do nothing
        mute()
    elif card.orientation & Rot90 == Rot90: #Rotated card - refresh
        exhaust(card, x, y)
    elif card.Type == "Agenda":
        addDoom(card, x, y)
    elif card.Type == "Act":
        addClue(card, x, y)
    elif card.Type == "Location": #Add a progress token
        flipcard(card, x, y)
    elif card.Type == "Enemy": #Add damage
        addDamage(card, x, y)
    elif card.Type == "Chaos Bag": # Action handled in OnCardDoubleClicked
        # Do nothing
        mute()
    elif card.Type == "Chaos Token": # Action handled in OnCardDoubleClicked
        # Do nothing
        mute()
    elif card.Type == "Encounter Draw": # Action handled in OnCardDoubleClicked
        # Do nothing
        mute()
    elif card.Type == "Mini": #Add action token
        addToken(card, Action)
    elif card.Type == "Campaign": #Add a progress token
        flipcard(card, x, y)
    else:
        exhaust(card, x, y)
        
def exhaust(card, x = 0, y = 0):
    mute()
    card.orientation ^= Rot90
    if card.orientation & Rot90 == Rot90:
        notify("{} exhausts '{}'".format(me, card))
    else:
        notify("{} readies '{}'".format(me, card))

def inspectCard(card, x = 0, y = 0):
    whisper("{} - model {}".format(card, card.model))
    for k in card.properties:
        if len(card.properties[k]) > 0:
            whisper("{}: {}".format(k, card.properties[k]))
                                
def flipcard(card, x = 0, y = 0):
    mute()
    
    if card.controller != me:
        notify("{} gets {} to flip card".format(me, card.controller()))
        remoteCall(card.controller, "flipcard", card)
        return

    cardx, cardy = card.position

    #Card Alternate Flip
    if card.alternates is not None and "B" in card.alternates:
        if card.alternate == "B":
            card.alternate = ''
        else:
            card.alternate = 'B'
        #if card.Type != "Location": questSetup(card) #Don't do setup for double-sided locations
        notify("{} turns '{}' face up.".format(me, card))
    elif card.isFaceUp:
        card.isFaceUp = False
        notify("{} turns '{}' face down.".format(me, card))        
    else:
        card.isFaceUp = True
        notify("{} turns '{}' face up.".format(me, card))


def rotateRight(card, x = 0, y = 0):
    # Rot90, Rot180, etc. are just aliases for the numbers 0-3
    mute()
    if card.controller == me:
        card.orientation = (card.orientation + 1) % 4
        if card.isFaceUp:
            notify("{} Rotates '{}'".format(me, card.Name))
        else:
            notify("{} Rotates a card".format(me))
    #mute()
    #if card.orientation == Rot0:
    #   card.orientation = Rot90
    #elif card.orientation == Rot90:
    #   card.orientation = Rot180
    #elif card.orientation == Rot180:
    #   card.orientation = Rot270
    #else:
    #   card.orientation = Rot0

def rotateLeft(card, x = 0, y = 0):
    # Rot90, Rot180, etc. are just aliases for the numbers 0-3
    mute()
    if card.controller == me:
        card.orientation = (card.orientation - 1) % 4
        if card.isFaceUp:
            notify("{} Rotates '{}'".format(me, card.Name))
        else:
            notify("{} Rotates a card".format(me))
    #mute()
    #if card.orientation == Rot0:
    #   card.orientation = Rot270
    #elif card.orientation  == Rot270:
    #   card.orientation = Rot180
    #elif card.orientation == Rot180:
    #   card.orientation = Rot90
    #else:
    #   card.orientation = Rot0

# def makeActive(card, x=0, y=0):
#   mute()
#   if card.Type != "Location": return
#   card.moveToTable(252, -229)
        
def addResource(card, x = 0, y = 0):
    addToken(card, Resource)
    
def addClue(card, x = 0, y = 0):
    addToken(card, Clue)

def addDoom(card, x = 0, y = 0):
    addToken(card, Doom)  

def addDamage(card, x = 0, y = 0):
    addToken(card, Damage)

def addHorror(card, x = 0, y = 0):
    addToken(card, Horror)

def addAction(card, x = 0, y = 0):
    addToken(card, Action)



# def addAttack(card, x = 0, y = 0):
#     addToken(card, AttackToken)  

# def addDefense(card, x = 0, y = 0):
#     addToken(card, DefenseToken)  

# def addThreat(card, x = 0, y = 0):
#     addToken(card, ThreatToken)
    
# def addTime(card, x=0, y=0):
#     addToken(card, TimeToken)

# def addTurn(card, x=0, y=0):
#   if isFirstPlayerToken([card]):
#       shared.counters['Round'].value += 1

def addToken(card, tokenType):
    mute()
    card.markers[tokenType] += 1
    notify("{} adds a {} to '{}'".format(me, tokenType[0], card))
    

def subResource(card, x = 0, y = 0):
    subToken(card, Resource)
    
def subClue(card, x = 0, y = 0):
    subToken(card, Clue)

def subDoom(card, x = 0, y = 0):
    subToken(card, Doom)  

def subDamage(card, x = 0, y = 0):
    subToken(card, Damage)

def subHorror(card, x = 0, y = 0):
    subToken(card, Horror)  

def subAction(card, x = 0, y = 0):
    subToken(card, Action)  


def subToken(card, tokenType):
    mute()
    card.markers[tokenType] -= 1
    notify("{} removes a {} from '{}'".format(me, tokenType[0], card))

def markerChanged(args):
    card = args.card
    
    thisPhase = currentPhase()
    
    inMythosPhase = False
    if getGlobalVariable("phase") == "Mythos" or thisPhase[1] == 1:
        inMythosPhase = True
    
    if card.Type == "Agenda" and args.marker == Doom[0] and inMythosPhase == True and card.properties[Doom[0]] != "":
        if card.markers[Doom] >= int(card.properties[Doom[0]]):
            card.highlight = EliminatedColour
        else:
            card.highlight = None
    else:
        card.highlight = None

def lockCard(card, x=0, y=0):
    mute()
    if isLocked(card):
        card.markers[Lock] = 0
    else:
        card.markers[Lock] = 1

def isLocked(card):
    return card.markers[Lock] > 0
    
def setControllerRemote (card, player):
		card.controller=player
    
def discard(card, x=0, y=0):
    mute()
    if card.controller != me:
        whisper("{} does not control '{}' - discard cancelled".format(me, card))
        remoteCall (card.controller, "setControllerRemote", [card, me])
        
        
    if card.Type == "Agenda": #If we remove the only Agenda card then we reveal the next one
        card.moveToBottom(agendaDiscard())
        notify("{} discards '{}'".format(me, card))
        nextAgendaStage()
        return
        
    if card.Type == "Act": #If we remove the only Act card then we reveal the next one
        card.moveToBottom(actDiscard())
        notify("{} discards '{}'".format(me, card))
        nextActStage()
        return
		
    if isPlayerCard(card):
        pile = card.owner.piles['Discard Pile']
    elif isLocationCard(card):
        pile = locationDiscard()
    elif isChaosToken(card):
        pile = chaosBag()
    else:
        pile = encounterDiscard()
        
    who = pile.controller
    notify("{} discards '{}'".format(me, card))
    if who != me:
        card.controller = who     
        remoteCall(who, "doDiscard", [me, card, pile])
    else:
        doDiscard(who, card, pile)

def discardSpecial(card, x=0, y=0):
    mute()
    if card.controller != me:
        whisper("{} does not control '{}' - discard cancelled".format(me, card))
        return
        
    if card.Type == "Agenda": #If we remove the only quest card then we reveal the next one
        card.moveToBottom(agendaDiscard())
        notify("{} discards '{}'".format(me, card))
        n, c = agendaCount(table)
        if c == 0:
            nextAgendaStage()
        return

    if isPlayerCard(card):
        pile = specialDiscard()
    else:
        pile = specialDiscard()
        
    who = pile.controller
    notify("{} discards '{}'".format(me, card))
    if who != me:
        card.controller = who    
        remoteCall(who, "doDiscard", [me, card, pile])
    else:
        doDiscard(who, card, pile)


def doDiscard(player, card, pile):
    mute()
    if (card.Subtype == "Sealed") and (pile == chaosBag()):
        card.Subtype = ""
    card.moveTo(pile)

def shuffleIntoDeck(card, x=0, y=0, player=me):
    mute()
    if card.controller != me:
        whisper("{} does not control '{}' - shuffle cancelled".format(me, card))
        return
        
    if card.Type == "Agenda":
        whisper("Invalid operation on a {} card".format(card.Type))
        return
    if card.Type == "Act":
        whisper("Invalid operation on a {} card".format(card.Type))
        return


    if isPlayerCard(card):
        pile = card.owner.deck
    else:
        pile = encounterDeck()

    who=pile.controller
    notify("{} moves '{}' to '{}'".format(me, card, pile.name))     
    if who != me:
        card.controller = who
        remoteCall(who, "doMoveShuffle", [me, card, pile])
    else:
        doMoveShuffle(me, card, pile)
        
def doMoveShuffle(player, card, pile):
    mute()
    card.moveTo(pile)
    shuffle(pile)
    
def playCard(card, x=0, y=0):
    if x == 0 and y == 0 and not eliminated(me):
        x, y = firstInvestigator(me).position
        x += Spacing
        y += Spacing
    card.moveToTable(x, y)
    card.select()

def swapCard(card):
    draw(me.deck)
    card.moveTo(me.deck)
    notify("{} returns {} to the top of the deck.".format(me, card))

def sumVictory():
    v = 0
    for c in shared.piles['Victory Display']:
        v += num(c.properties['Victory Points'])
    shared.VictoryPoints = v
    
def moveToVictory(card, x=0, y=0):
    mute()
    card.moveTo(shared.piles['Victory Display'])
    v = num(card.properties['Victory Points'])
    sumVictory()
    notify("{} adds '{}' (+{}) to the Global Victory Display (Total = {})".format(me, card, v, shared.VictoryPoints))

    
#---------------------------
#movement actions
#---------------------------

#------------------------------------------------------------------------------
# Hand Actions
#------------------------------------------------------------------------------

def randomDiscard(group):
    mute()
    card = group.random()
    if card is None: return
    notify("{} randomly discards '{}'.".format(me, card))
    card.moveTo(me.piles['Discard Pile'])
 
def mulligan(group, x = 0, y = 0):
    mute()
    
    dlg = cardDlg(me.hand)
    dlg.title = "Mulligan!"
    dlg.text = "Select the cards you wish to replace:"
    dlg.min = 1
    dlg.max = len(me.hand)
    cardsSelected = dlg.show()
    if cardsSelected is not None:
        notify("{} declares a Mulligan, and replaces {} card(s).".format(me, len(cardsSelected)))
        for card in cardsSelected:
            notify("{} replaces {}.".format(me, card))
            card.moveToBottom(me.deck)
            draw(me.deck)
        
        shuffle(me.deck)


#------------------------------------------------------------------------------
# Pile Actions
#------------------------------------------------------------------------------

def draw(group, x = 0, y = 0):
    mute()
    if len(group) == 0: return
    if deckLocked():
        whisper("Your deck is locked, you cannot draw a card at this time")
        return
    card = group[0]
    card.moveTo(me.hand)
    notify("{} draws '{}'".format(me, card))

def shuffle(group):
    mute()
    if len(group) > 0:
        update()
        group.shuffle()
        notify("{} shuffles {}".format(me, group.name))

def drawMany(group, count = None):
    mute()
    if len(group) == 0: return
    if deckLocked():
        whisper("Your deck is locked, you cannot draw cards at this time")
        return
    if count is None:
        count = askInteger("Draw how many cards?", 4)
    if count is None or count <= 0:
        whisper("drawMany: invalid card count")
        return
    for c in group.top(count):
        c.moveTo(me.hand)
        notify("{} draws '{}'".format(me, c))

def search(group, count = None):
    mute()
    if len(group) == 0: return
    if count is None:
        count = askInteger("Search how many cards?", 5)
    if count is None or count <= 0:
        whisper("search: invalid card count")
        return
        
    notify("{} searches top {} cards".format(me, count))    
    moved = 0
    for c in group.top(count):
        c.moveTo(me.piles['Discard Pile'])
        moved += 1
    me.piles['Discard Pile'].lookAt(moved)
    
def moveMany(group, count = None):
    if len(group) == 0: return
    mute()
    if count is None:
        count = askInteger("Move how many cards to secondary deck?", 1)
        if count is None or count <= 0: return
    
    moved = 0
    
    if group == me.deck:
        pile = me.piles['Secondary Deck']
    else:
        pile = specialDeck()
    
    for c in group.top(count):
        c.moveTo(pile)
        moved += 1
    notify("{} moves {} cards to the secondary deck".format(me, moved))
    if pile.collapsed:
        pile.collapsed = False

def discardMany(group, count = None):
    if len(group) == 0: return
    mute()
    if count is None:
        count = askInteger("Discard how many cards?", 1)
        if count is None or count <= 0: return
        
    if group == me.deck:
        pile = me.piles['Discard Pile']
        fr = "his deck"
    else:
        pile = encounterDiscard()
        fr = "the Encounter Deck"

    for c in group.top(count):
        c.moveTo(pile)
        notify("{} discards '{}' from {}".format(me, c, fr))

def moveAllToEncounter(group):
    mute()
    if confirm("Shuffle all cards from {} to Encounter Deck?".format(group.name)):
        for c in group:
            c.moveTo(encounterDeck())
        notify("{} moves all cards from {} to the Encounter Deck".format(me, group.name))
        shuffle(encounterDeck())
        
def moveAllToEncounterBottom(group):
    mute()
    if confirm("Move all cards from {} to the bottom of the Encounter Deck?".format(group.name)):
        for c in group:
            c.moveToBottom(encounterDeck())
        notify("{} moves all cards from {} to the bottom of the Encounter Deck".format(me, group.name))


def moveAllToSpecial(group):
    mute()
    if confirm("Shuffle all cards from {} to Special Deck?".format(group.name)):
        for c in group:
            c.moveTo(specialDeck())
        notify("{} moves all cards from {} to the Special Deck".format(me, group.name))
        shuffle(specialDeck())

def moveAllToPlayer(group):
    mute()
    if confirm("Shuffle all cards from {} to Player Deck?".format(group.name)):
        for c in group:
            if len(c.Setup) == 0:
                c.moveTo(c.owner.piles['Deck'])
        notify("{} moves all cards from {} to the Player Deck".format(me, group.name))
        shuffle(me.piles['Deck'])

def shuffleCardsIntoDeck(group):
    mute()
    owners = set()
    for card in group:
        if len(card.Setup) == 0:
            card.moveTo(card.owner.deck)
            owners.add(card.owner)
    for owner in owners:
        owner.deck.shuffle()

def swapWithEncounter(group):
    mute()
    if confirm("Swap all cards from {} with those in Encounter Deck?".format(group.name)):
      deck = encounterDeck()
      size = len(deck)
      for c in group:
          c.moveToBottom(deck)
      for c in deck.top(size):
          c.moveToBottom(group)
      notify("{} swaps {} and Encounter Deck.".format(me, group.name))

def drawPileToTable(player, group, x, y):
    mute()
    if len(group) == 0:
        notify("{} is empty.".format(group.name))
        return

    card = group[0]
    card.moveToTable(x, y)
    #failsave for sealed attribute
    if card.Type == "Chaos Token" and card.Subtype == "Sealed":
        card.Subtype = ""
    notify("{} draws {} from the {}.".format(player, card.name, group.name))
    return card
    
def drawChaosToken(group, x = 0, y = 0):
    drawChaosTokenForPlayer(me, group, x, y)  


def drawChaosTokenForPlayer(player, group, x = 0, y = 0, replace = True, xMod = 0, yMod = 0):
    mute()
    if chaosBag().controller == me:
        if replace:
            # check for existing chaos token on table
            table_chaos_tokens = [card for card in table
                if (card.Type == 'Chaos Token') and (card.Subtype != 'Sealed')]
            for token in table_chaos_tokens:
                if token.controller == me:
                    token.moveTo(chaosBag())
                else:
                    remoteCall(token.controller, "moveToRemote", [token, chaosBag()])
            chaosBag().shuffle()
  
        drawPileToTable(player, chaosBag(), ChaosTokenX + xMod, ChaosTokenY + yMod)
        
    else:
        remoteCall(chaosBag().controller, "drawChaosTokenForPlayer", [me, chaosBag(), x, y, replace])
    
def moveToRemote (token, pile):
   token.moveTo(pile)	
	
    
def drawXChaosTokens(player, group, x = 0, y = 0):
    mute()
    xChaosTokens = askInteger("Draw how many Chaos Tokens?", 1)
    if xChaosTokens == None: return
    
    for xTokens in range(0, xChaosTokens):
        replace = False
        if xTokens == 0: replace = True
        if chaosBag().controller == me:
                drawChaosTokenForPlayer(me, chaosBag(), x, y, replace, (xTokens * 10), (xTokens * 10))  
        else:
            remoteCall(chaosBag().controller, "drawChaosTokenForPlayer", [me,  chaosBag(), x, y, replace, (xTokens * 10), (xTokens * 10)])

def drawAddChaosToken(player, group, x = 0, y = 0):
    mute()
    num = 0
    for card in table: #find out how many Tokens there already are
        if card.Type == "Chaos Token":
            num += 1

    if chaosBag().controller == me:
        drawChaosTokenForPlayer(me, chaosBag(), x, y, False, num*10, num*10)
    else:
        remoteCall(chaosBag().controller, "drawChaosTokenForPlayer", [me,  chaosBag(), x, y, False, num*10, num*10])

def sealTokenCard(card, x = 0, y = 0, player = None):
    if card.controller != me:
        remoteCall(card.controller, "sealTokenCard", [card, x, y, me])
        return

    if player == None:
        player = me

    #failsave
    if card == None:
        return

    card.Subtype = 'Sealed'
    card.filter = "#99999999"
    card.controller = player
    notify("{} seals {}.".format(player, card.name))

def sealToken(group, x = 0, y = 0, player = None):
    mute()

    if chaosBag().controller != me:
        remoteCall(chaosBag().controller, "sealToken", [group, x, y, me])
        return

    if player == None:
        player = me

    list = [card for card in table
                if (card.Type == 'Chaos Token') and (card.Subtype != 'Sealed')]
    for card in chaosBag():
        list.append(card)
    dlg = cardDlg(list)
    dlg.title = "Seal Chaos Token"
    dlg.text = "Select a Chaos Token to seal"
    card = dlg.show()
    if card == None:
        return
    card = card[0]
    card.moveToTable(ChaosTokenX, ChaosTokenY)
    card.Subtype = 'Sealed'
    card.filter = "#99999999"
    card.controller = player
    notify("{} seals {}.".format(player, card.name))

def drawBasicWeakness(group, x = 0, y = 0):
    mute()

    loadBasicWeaknesses(group, x, y)

    bw_cards = me.piles[BasicWeakness.PILE_NAME]
    bw_cards_count = len(bw_cards)
    if (bw_cards_count == 0):
        notify("There are no Basic Weakness cards left!")
        return

    card = bw_cards.top()

    return card

def drawBasicWeaknessToDeck(group, x = 0, y = 0):
    mute()

    card = drawBasicWeakness(group, x, y)
    card.moveTo(me.deck)
    # do we notify players of what the basic weakness card that was shuffled in?
    notify("{} shuffles a random Basic Weakness into deck".format(me))
    me.deck.shuffle()


def drawBasicWeaknessToHand(group, x = 0, y = 0):
    card = drawBasicWeakness(group, x, y)
    card.moveTo(me.hand)
    notify("{} draws the Basic Weakness '{}' into their hand.".format(me, card))
    

def createCard(group=None, x=0, y=0):
	cardID, quantity = askCard()
	cards = table.create(cardID, x, y, quantity, True)
	try:
		iterator = iter(cards)
	except TypeError:
		# not iterable
		notify("{} created {}.".format(me, cards))
	else:
		# iterable	
		for card in cards:
			notify("{} created {}.".format(me, card))


def drawUnrevealed(group=None, x=0, y=0):
    mute()
    if len(group) == 0:
        notify("{} is empty.".format(group.name))
        return

    card = group[0]
    card.moveToTable(EncounterX, EncounterY, True)
    notify("{} draws an unrevealed card from the {}.".format(me, card.name, group.name))
    return card
    

def placeLongPath(group, x=0, y=0):
    pathCard = group.create("7f4029c8-1cee-406a-9913-9fbc6e341bed", x, y, 1, False)
    pathCard.sendToBack()

def placeMediumPath(group, x=0, y=0):
    pathCard = group.create("cf3d8bd6-354a-4284-b716-109e7040c3e9", x, y, 1, False)
    pathCard.sendToBack()

def placeShortPath(group, x=0, y=0):
    pathCard = group.create("2e964666-fa5a-40e4-a7f5-bf66c625d783", x, y, 1, False)
    pathCard.sendToBack()

def placeElbowPath(group, x=0, y=0):
    pathCard = group.create("3d9c7266-d4d0-46e0-b8b3-560fbcf1b294", x, y, 1, False)
    pathCard.sendToBack()

def placeCrossPath(group, x=0, y=0):
    pathCard = group.create("8ea6845b-b9bb-4f11-a814-e94b16e50629", x, y, 1, False)
    pathCard.sendToBack()

def placeThreeWayPath(group, x=0, y=0):
    pathCard = group.create("1b1493eb-cf9f-4709-9b50-f8f343f7a607", x, y, 1, False)
    pathCard.sendToBack()

def placeDiagonalConnectionPath(group, x=0, y=0):
    pathCard = group.create("d2ddabd3-b7b1-427e-8ca2-b7dbe272fce5", x, y, 1, False)
    pathCard.sendToBack()

def placeDirectionalMarker(group, x=0, y=0):
    pathCard = group.create("10bd7039-10f4-44c9-8be4-61bf182e1d9d", x, y, 1, False)
    pathCard.sendToBack()

def lockAllPaths(group, x=0, y=0):
    for card in table:
        if card.Type == "Path":
            if not hasattr(card, 'Subtype'):
                card.sendToBack()
            card.anchor = True

def unlockAllPaths(group, x=0, y=0):
    for card in table:
        if card.Type == "Path":
            card.anchor = False    




# def captureDeck(group):
#   if len(group) == 0: return
#   mute()
#   if group == me.deck:
#       pile = me.piles['Secondary Deck']
#   else: return        
#   if confirm("Create your capture deck?"):
#       for c in group:
#           if c.Type == "Ally":
#               c.moveTo(pile)
#           if c.Type == "Attachment":
#               if "Item." in c.Traits or "Mount." in c.Traits or "Artifact." in c.Traits:
#                   c.moveTo(pile)
#   notify("{} creates their Capture Deck".format(me))
#   if pile.collapsed:
#       pile.collapsed = False

# def setupTotDMap(group):
#   group.shuffle()
#   MapStartX = 350
#   MapStartY = -90
#   i = 0
#   j = 0 
#   for c in group:
#       c.moveToTable(MapStartX,MapStartX)
#       if c.name == "Lost Island":
#           x = MapStartX + 64*(i // 3)
#           y = MapStartY + 89*(i % 3)
#           c.moveToTable(x,y)
#           if i==0 or i==2:
#               flipcard(c)
#           i=i+1
#       if c.name == "Temple of the Deceived":
#           c.moveToTable(MapStartX+64*4,MapStartY+89*j)
#           j=j+1

        
# Reminders

# def enableReminders(group, x=0, y=0):
#   setGlobalVariable("Reminders", "On")
#   whisper("Reminders enabled.")
# def disableReminders(group, x=0, y=0):
#   setGlobalVariable("Reminders", "Off")
#   whisper("Reminders disabled.")
    
# def isTextInCard(text,card):
#   match = re.search(text,card.Text)
#   if match: return True
#   match = re.search(text,card.alternateProperty("B","Text"))
#   if match: return True
    
# def setReminders(card):
#   match = re.search('Time ([0-9]+)',card.Text)
#   if match:
#       for i in range(num(match.group(1))):
#           addTime(card)
#   match = re.search('Time ([0-9]+)',card.alternateProperty("B","Text"))
#   if match:
#       for i in range(num(match.group(1))):
#           addTime(card)
    
#   if isTextInCard('resource phase',card): setReminderResource(card)
#   if isTextInCard('quest phase',card): setReminderQuest(card)
#   if isTextInCard('staging step',card): setReminderQuest(card)
#   if isTextInCard('combat phase',card): setReminderCombat(card)
#   if isTextInCard('refresh phase',card): setReminderRefresh(card)
#   if isTextInCard('t the end of the round',card): setReminderRefresh(card)

# def resourceReminders():
#   if getGlobalVariable("Reminders") == "Off": return;
#   clearTargets()
#   reminder = getGlobalVariable("reminderResource")
#   for c in table:
#       if str(c._id) in reminder:
#           c.target(True)  

# def questReminders():
#   if getGlobalVariable("Reminders") == "Off": return;
#   reminder = getGlobalVariable("reminderQuest")
#   for c in table:
#       if str(c._id) in reminder:
#           c.target(True)
            
# def combatReminders():
#   if getGlobalVariable("Reminders") == "Off": return;
#   reminder = getGlobalVariable("reminderCombat")
#   for c in table:
#       if str(c._id) in reminder:
#           c.target(True)
            
# def refreshReminders():
#   if getGlobalVariable("Reminders") == "Off": return;
#   clearTargets()
#   reminder = getGlobalVariable("reminderRefresh")
#   for c in table:
#       if c.markers[TimeToken] >= 1:
#           c.target(True)
#       if str(c._id) in reminder:
#           c.target(True)

# def setReminderResource(card,x=0,y=0):
#   reminder = getGlobalVariable("reminderResource")
#   if not str(card._id) in reminder:
#       reminder += str(card._id) + ","
#   setGlobalVariable("reminderResource",reminder)
# def removeReminderResource(card,x=0,y=0):
#   reminder = getGlobalVariable("reminderResource")
#   reminder = reminder.replace(str(card._id) + ",","")
#   setGlobalVariable("reminderResource",reminder)

# def setReminderQuest(card,x=0,y=0):
#   reminder = getGlobalVariable("reminderQuest")
#   if not str(card._id) in reminder:
#       reminder += str(card._id) + ","
#   setGlobalVariable("reminderQuest",reminder)
# def removeReminderQuest(card,x=0,y=0):
#   reminder = getGlobalVariable("reminderQuest")
#   reminder = reminder.replace(str(card._id) + ",","")
#   setGlobalVariable("reminderQuest",reminder) 

# def setReminderCombat(card,x=0,y=0):
#   reminder = getGlobalVariable("reminderCombat")
#   if not str(card._id) in reminder:
#       reminder += str(card._id) + ","
#   setGlobalVariable("reminderCombat",reminder)
# def removeReminderCombat(card,x=0,y=0):
#   reminder = getGlobalVariable("reminderCombat")
#   reminder = reminder.replace(str(card._id) + ",","")
#   setGlobalVariable("reminderCombat",reminder)    
    
# def setReminderRefresh(card,x=0,y=0):
#   reminder = getGlobalVariable("reminderRefresh")
#   if not str(card._id) in reminder:
#       reminder += str(card._id) + ","
#   setGlobalVariable("reminderRefresh",reminder)
# def removeReminderRefresh(card,x=0,y=0):
#   reminder = getGlobalVariable("reminderRefresh")
#   reminder = reminder.replace(str(card._id) + ",","")
#   setGlobalVariable("reminderRefresh",reminder)   
    
# def setGlobalReminders():
#   setGlobalVariable("Reminders", "Off")
#   setGlobalVariable("reminderResource","")
#   setGlobalVariable("reminderQuest","")
#   setGlobalVariable("reminderCombat","")
#   setGlobalVariable("reminderRefresh","")
