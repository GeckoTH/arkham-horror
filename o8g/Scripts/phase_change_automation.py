#!/usr/bin/env python
# -*- coding: utf-8 -*-

HunchCard = None
AmandaCard = None

def doMythosPhase(setPhaseVar = True):
    mute()
    debug("doMythosPhase()")
    
    if setPhaseVar:
        setGlobalVariable("phase", "Mythos")

    for card in table:
    # Auto-replenish
        if ("Replenish" and "at the start of each round" in card.Text) and card.owner == me and not isLocked(card):
            #Capture text between "Uses (..)"
            description_search = re.search('.*([U|u]ses\s\(.*?\)).*', card.properties["Text"], re.IGNORECASE)
            if description_search:
                strCharges = description_search.group(1)
                #Capture text between "(...)""
                strCharges = re.search('.*\((.*)\).*',strCharges).group(1)
                # Check if not only 1 numeric
                if not strCharges.isnumeric():
                    word = re.search('(\d|X)(.*)',strCharges).group(2)
                    strCharges = re.search('(\d|X)(.*)',strCharges).group(1)
                    strCharges = strCharges.replace(" ", "")
                    if strCharges.isnumeric():
                            for i in range(0, int(strCharges)):
                                if card.markers[Resource] < int(strCharges):
                                    addResource(card)
        if card.Type == "Agenda" and card.controller == me and not isLocked(card) and card.isFaceUp:
            addDoom(card)

    shared.counters['Round'].value += 1

def doInvestigationPhase():
    global AmandaCard
    global HunchCard
    isAmanda = filter(lambda card: (card.Name == "Amanda Sharpe" and card.Type == "Investigator" and card.owner == me and not isLocked(card) and inGame(card.owner)), table)
    isJoe = filter(lambda card: (card.Name == "Joe Diamond" and card.Type == "Investigator" and card.owner == me and not isLocked(card) and inGame(card.owner)) , table)
    if isAmanda:
        for c in table: #Find Amanda on table
            if c.name == "Amanda Sharpe" and c.type == "Investigator":
                amanda = c
                x, y = c.position
                break
        if inGame(amanda.owner):
            draw(amanda.owner.deck)
            if AmandaCard: # Discard card under Amanda
                discard(AmandaCard)
            WftD = filter(lambda card: (card.Name == "Whispers from the Deep"), amanda.owner.hand)
            if not WftD:
                dlg = cardDlg(amanda.owner.hand)
                dlg.title = "Amanda Sharpe"
                dlg.text = "Select 1 card to put beneath Amanda:"
                dlg.min = 1
                dlg.max = 1
                cardsSelected = dlg.show()
            else:
                cardsSelected = WftD
            if cardsSelected is not None:
                c = cardsSelected[0]
                c.moveToTable(x + 15, y - 50)
                c.sendToBack()
                AmandaCard = c
                if WftD:
                    c.highlight = RedColour
                else: c.highlight = WhiteColour
                notify("{} places {} under {}".format(c.owner,AmandaCard,amanda))
    if isJoe:
        if len(me.piles['Secondary Deck']) > 0:
            HunchCard = me.piles['Secondary Deck'].top()
            flipcard(HunchCard) # Show the first Hunch Card
        else: HunchCard = None

def doEnemyPhase(): # Also End of the Investigation Phase
    global HunchCard
    if HunchCard:
        if HunchCard.group == HunchCard.owner.piles['Secondary Deck']: # Checks if Hunch Card is still in the Hunch Deck
            HunchCard.owner.piles['Secondary Deck'].visibility = "none" # Removes Visibility
            HunchCard.owner.piles['Secondary Deck'].shuffle() # Shuffle Hunch Deck
    for c in table: # Targets Hunter Enemies
        if c.Type == "Enemy" and "Hunter." in c.Text and c.orientation & Rot90 != Rot90 and c.isFaceUp:
            c.target()

def doUpkeepPhase(setPhaseVar = True):
    mute()
    debug("doUpkeepPhase()")
    if setPhaseVar:
        setGlobalVariable("phase", "Upkeep")

    if activePlayers() == 0:
        whisper("All players have been eliminated: You have lost the game")
        return

    clearTargets()
    doRestoreAll()

    if not inGame(me):
        whisper("You have been eliminated from the game.")
        return

    for card in table:
        #If Patrice, Discard all cards but weaknesses and draw to 5
        if card.Name == "Patrice Hathaway" and card.owner == me and card.Type == "Investigator" and not isLocked(card):
            for card in filter(lambda card: not card.Subtype in ["Weakness", "Basic Weakness"], card.owner.hand):
                notify("{} discards '{}'".format(me, card))
                card.moveTo(card.owner.piles['Discard Pile'])
            cardToDraw = 5 - len(card.owner.hand)
            for i in range(0, cardToDraw):
                draw(card.owner.deck)
            break
        #Else draw cards equal to selected value
        elif card.owner == me and card.Type == "Investigator":
            if card.owner.counters['Card Draw'].value == 1:
                draw(card.owner.deck)
            elif card.owner.counters['Card Draw'].value > 1:
                for i in range(0, card.owner.counters['Card Draw'].value):
                    draw(card.owner.deck)
            break
    
    # Check for hand size!
    sizeHand = me.counters['Maximum Hand Size'].value
    #Checks if player has Dream-enhancing Serum on the table or Forced Learning
    haveSerum = filter(lambda card: card.Name == "Dream-Enhancing Serum" and card.owner == me and not isLocked(card), table)
    forcedLearning = filter(lambda card: card.Name == "Forced Learning" and card.owner == me and not isLocked(card), table)
    if forcedLearning and len(me.hand) > 1:
        forcedCards = [me.hand[0],me.hand[1]] #Last two cards drawn
        dlg = cardDlg(forcedCards)
        dlg.title = "Forcead Learning"
        dlg.text = "Select 1 card:"
        dlg.min = 1
        dlg.max = 1
        cardsSelected = dlg.show()
        if cardsSelected is not None:
            discard(cardsSelected[0])
    if haveSerum:
        inHands = []
        duplicates = 0
        for c in me.hand:
            if c.Name in inHands:
                duplicates += 1
            inHands.append(c.Name)
        cardsInHand = len(me.hand) - duplicates
    else: cardsInHand = len(me.hand)
    if cardsInHand > sizeHand:
        discardCount = cardsInHand - sizeHand
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
        if card.Type == "Investigator" and card.owner == me and card.isFaceUp:
            if (me.counters['Ressource per upkeep'].value > 0):
                for i in repeat(None, me.counters['Ressource per upkeep'].value):
                    addResource(card)
            if card.name == "Sister Mary":
                if countBless() < 10:
                    if 1 == askChoice('Add a Bless Token to the Chaos Bag ?', ['Yes', 'No'], ['#dd3737', '#d0d0d0']):
                        addBless()
        elif card.Type == "Mini" and card.owner == me:
            card.markers[Action] = 0
            if card.alternates is not None and "" in card.alternates:
                card.alternate = ''