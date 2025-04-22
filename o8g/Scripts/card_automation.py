#!/usr/bin/env python
# -*- coding: utf-8 -*-

cardToAttachTo =  None
cardsFound = []
attached = {}

def attachCard(host, card):
    mute()
    global attached
    if not host._id in attached:
        attached[host._id] = []
    attached[host._id].append(card._id)
    
def detachCard(card):
    mute()
    global attached
    for value in attached.values():
        if card._id in value:
            value.remove(card._id)
            break
            
def isAttached(card):
    mute()
    for value in attached.values():
        if card in value:
            return True
    return False

def InvestigatorColor(player):
    mute()
    for card in table:
        if card.Type == "Investigator" and card.controller == player:
            if card.Class == "Guardian":
                return "#2F99F4"
            elif card.Class == "Seeker":
                return "#F4CB2F"
            elif card.Class == "Mystic":
                return "#AF2FF4"
            elif card.Class == "Rogue":
                return "#22A827"
            elif card.Class == "Survivor":
                return "#D43A2E"
            else:
                return "#999999"
            

def InvestigatorName(player):
    for card in table:
        if card.Type == "Investigator" and card.controller == player:
            return card.Name

def moveCardToBottom(card, group):
    card.moveToBottom(group)

def lookToBottom(group): # Alyssa Graham automation
    global cardsFound
    cardsFound = []
    mute()
    if len(group) == 0: return
    if group != encounterDeck() and deckLocked(group.player):
        whisper("{}'s deck is locked and cannot be looked at".format(group.player))
        return
    dlg = cardDlg(group.top(1))
    dlg.title = "Looking at cards"
    dlg.text = "Select a card:"
    cardsSelected = dlg.show()
    if cardsSelected:
        remoteCall(group.controller, "moveCardToBottom", [cardsSelected[0], group])
        cardsFound.append(cardsSelected[0])
        notify("{} is moved at the bottom of {}".format(cardsSelected[0], group.name))

# Typically use this to find a specific card in the discard pile such
# as "Word of Woe"
def searchInPile(group, name):
    if len(group) == 0: return
    for c in group:
        if (c.Name == name):
            return c
    # Nothing was found.
    return

def attachTo(card):
    global cardToAttachTo
    cardToAttachTo = card.offset(card.position[0], card.position[1])

def searchTopDeck(group, target, count = None, **kwargs):
    mute()
    global cardsFound
    global cardToAttachTo
    cardsFound = []
    cardsToShow = []
    if len(group) == 0: return
    if group != encounterDeck():
        if deckLocked(group.player):
            notify("{}'s deck is locked and cannot be searched".format(group.player))
            return
    if count == None:
        count = len(group)
    else:
        MandyonTable = filter(lambda c: (c.Name == "Mandy Thompson" and c.Type == "Investigator"), table)
        if not count == len(group):
            if MandyonTable:
                option1 = count
                option2 = count + 3
                choice_list = [str(option1), str(option2)]
                color_list = ['#000000','#F4BB2F']
                sets = askChoice("Search how many cards ?", choice_list, color_list)
                if sets == 0:
                    return
                if sets == 1:
                    count = count
                if sets == 2:
                    count = option2
    if "traits" in kwargs:
        traits = kwargs.get("traits").split(',')
        cardsToShow = [card for card in group.top(count)
                if (any((t in card.Traits) or (t in card.Type) for t in traits)) or (card.Name == "Astounding Revelation") or (card.Name == "Occult Evidence" )or (card.Name == "Surprising Find") or (card.Name == "Shocking Discovery" and group == card.controller.deck)]
        if len(cardsToShow) == 0:
            whisper("No relevant card found")
            if group.name != "Discard Pile":
                shuffle(group)
            cardToAttachTo = None
            return
    else: 
        cardsToShow = [c for c in group.top(count)]
    for c in cardsToShow:
        if c.Name == "Shocking Discovery" and group == c.controller.deck:
            c.moveTo(table)
            c.highlight = RedColour   
            notify("{} found ! Search cancelled !".format(c))
            cardToAttachTo = None
            shuffle(group)
            return
    dlg = cardDlg(cardsToShow)
    dlg.title = "Search the top "+ str(count) +" cards."
    dlg.text = "Select the cards:"
    dlg.min = 1
    dlg.max = count
    cardsSelected = dlg.show()
    if cardsSelected != None:
        inc = 0
        for card in cardsSelected:
             cardsFound.append(card)
             if cardToAttachTo is None:
                card.moveTo(target)
                if isPlayerCard(card):
                    if target == card.controller.hand:
                        serumDoubleCheck(card)
                if target == table:
                    card.select()
             else: 
                card.moveToTable(cardToAttachTo[0], cardToAttachTo[1])
                card.sendToBack()
                if len(cardsSelected) == 1:
                    cardToAttachTo = None
                else:
                    attachTo(card)
                    inc += 1
                    if inc == len(cardsSelected):
                        cardToAttachTo = None
    if group.name != "Discard Pile":
        shuffle(group)

def InvestigatorList():
    choice_list = []
    color_list = []
    for i in range(0, len(getPlayers())):
        # Add player names to the list
        if InvestigatorName(getPlayers()[i]):
            choice_list.append(str(InvestigatorName(getPlayers()[i])))
        # Add players investigator color to the list
        if InvestigatorColor(getPlayers()[i]):
            color_list.append(InvestigatorColor(getPlayers()[i]))
    return choice_list, color_list
    
def defaultAction(card, x = 0, y = 0):
    mute()
    global cardToAttachTo
    global AmandaCard
    global Premonition
    # Default for Done button is playerDone
    if not card.isFaceUp: #Face down card - flip
        flipcard(card, x, y)
    elif card.Type == "Path" or card.Type == "Tarot": # Action handled in OnCardDoubleClicked
        # Do nothing
        mute()
    elif card.orientation & Rot90 == Rot90: #Rotated card - refresh
        exhaust(card, x, y)
    elif card.Type == "Location": #Add a progress token
        flipcard(card, x, y)
    elif card.Type == "Tarot": #Rotate 180
        card.orientation = (card.orientation + 2) % 4
    elif card.Type == "Enemy": #Add damage
        addDamage(card, x, y)
    elif card.Type == "Chaos Bag": # Action handled in OnCardDoubleClicked
        # Do nothing
        mute()
    elif card.Type == "Chaos Token": # Action handled in OnCardDoubleClicked
        # Do nothing
        mute()
    elif card.Type == "Encounter Draw" or card.Type == "Encounter2 Draw": # Action handled in OnCardDoubleClicked
        # Do nothing
        mute()
    elif card.Type == "nextAct" or card.Type == "nextAgenda": # Action handled in OnCardDoubleClicked
        # Do nothing
        mute()
    elif card.Type == "Mini": #Add action token
        addToken(card, Action)
    elif card.Type == "Campaign": #Add a progress token
        flipcard(card, x, y)
    elif card.Name == "Flood Token": #Flip flood token
        flipcard(card, x, y)
#############################################
#                                           #
#           Mystic Cards                    #
#                                           #
#############################################
    elif card.Name == "Arcane Initiate":
        exhaust(card, x, y)
        notify("{} uses {} to search their deck for a Spell card to draw.".format(card.controller, card))
        searchTopDeck(card.controller.deck, card.controller.hand, 3, traits="Spell")
    elif card.Name == "Stargazing":
        if len(encounterDeck()) > 9:
            stop = False
            for c in card.controller.piles['Sideboard']:
                if c.Name == "The Stars Are Right" and stop is not True:
                    shuffleIntoTop(c, 0, 0, me, encounterDeck(),10)
                    stop = True
            notify("{} uses {} to shuffle {} in the encounter deck top 10 cards.".format(card.controller, card, c))
        else: 
            whisper("There are not enough cards in the encounter Deck")
    elif card.Name == "Word of Command":
        notify("{} uses {} to search their deck for a Spell card to draw.".format(card.controller, card))
        searchTopDeck(card.controller.deck, card.controller.hand, traits="Spell")
    elif card.Name == "Prescient":
        notify("{} uses {} to move back a Spell from the discard pile to their hand.".format(card.controller, card))
        searchTopDeck(card.controller.piles['Discard Pile'], card.controller.hand, traits="Spell")
    elif card.Name == "Olive McBride":
        exhaust (card, x, y)
        drawXChaosTokens(chaosBag(), x = 0, y = 0)
        notify("{} uses {} to reveal 3 chaos tokens and choose 2 of them to resolve.".format(card.controller, card))
    elif card.Name == "Alyssa Graham":
        exhaust (card, x, y)
        choice_list = ['Encounter Deck']
        color_list = ['#46453E']
        for i in range(0, len(getPlayers())):
            # Add player names to the list
            choice_list.append(str(InvestigatorName(getPlayers()[i])))
            # Add players investigator color to the list
            color_list.append(InvestigatorColor(getPlayers()[i]))
        sets = askChoice("Choose a deck to look at:", choice_list, color_list)
        if sets == 0:
            return
        #Encounter Deck
        elif sets == 1:
            notify("{} uses {} to look at the top card of the encounter deck".format(card.controller, card))
            lookToBottom(encounterDeck())
        else:
            chosenPlayer = getPlayers()[sets - 2]
            if deckLocked(chosenPlayer):
                notify("{}'s deck is locked and cannot be looked at".format(chosenPlayer))
                return
            notify("{} uses {} to look at the top card of {}'s deck".format(card.controller, card, chosenPlayer))
            lookToBottom(chosenPlayer.deck)
        if cardsFound: #if a card was moved to the bottom, add a Doom to Alyssa
            addDoom(card)
    elif card.Name == "Scroll of Secrets" and card.Level == "0":
        exhaust (card, x, y)
        subResource(card)
        choice_list = ['Encounter Deck']
        color_list = ['#46453E']
        for i in range(0, len(getPlayers())):
            # Add player names to the list
            choice_list.append(str(InvestigatorName(getPlayers()[i])))
            # Add players investigator color to the list
            color_list.append(InvestigatorColor(getPlayers()[i]))
        sets = askChoice("Choose a deck to look at:", choice_list, color_list)
        if sets == 0:
            return
        #Encounter Deck
        elif sets == 1:
            notify("{} uses {} to look at the bottom card of the encounter deck".format(card.controller, card))
            deckToCheck = encounterDeck()
        else:
            chosenPlayer = getPlayers()[sets - 2]
            deckToCheck = chosenPlayer.deck
            if deckLocked(chosenPlayer):
                notify("{}'s deck is locked and cannot be looked at".format(chosenPlayer))
                return
            notify("{} uses {} to look at the bottom card of {}'s deck".format(card.controller, card, chosenPlayer))
            if deckToCheck.controller != me and deckToCheck != encounterDeck():
                for p in chosenPlayer.piles:
                    chosenPlayer.piles[p].controller = me
        dlg = cardDlg(deckToCheck.bottom(1))
        dlg.title = "Scroll of Secrets"
        dlg.text = "Choose a card"
        dlg.min = 1
        dlg.max = 1
        cardsSelected = dlg.show()
        choice_list = ['Discard the card',"Leave it at the bottom","Place it on top of its owner's deck"]
        color_list = ['#46453E','#46453E','#46453E',]
        if deckToCheck != encounterDeck():
            choice_list.append("Add the card to its owner's hand")
            color_list.append('#46453E')
        sets = askChoice("Choose an option:", choice_list, color_list)
        if sets == 0:
            return
        elif sets == 1:
            if deckToCheck == encounterDeck():
                cardsSelected[0].moveTo(encounterDiscard())
            else:
                cardsSelected[0].moveTo(chosenPlayer.piles['Discard Pile'])
            notify("{} discards {}.".format(card.controller, cardsSelected[0]))
        elif sets == 2:
            notify("{} leaves the card at the bottom of the deck.".format(card.controller))
            return
        elif sets == 3:
            cardsSelected[0].moveTo(deckToCheck)
            notify("{} moves the card at the top of the deck.".format(card.controller))
        elif sets == 4:
            cardsSelected[0].moveTo(deckToCheck.player.hand)
            notify("{} adds the card to {}'s hand".format(card.controller,chosenPlayer))
        if deckToCheck.player != me and deckToCheck != encounterDeck():
            for p in chosenPlayer.piles:
                chosenPlayer.piles[p].controller = chosenPlayer
    elif card.Name == "Crystalline Elder Sign":
        attachTo(card)
        card.sendToBack()
        list = [card for card in table
                    if (card.Type == 'Chaos Token') and (card.Subtype != 'Sealed')]
        for card in chaosBag():
            if card.name == "+1" or card.name == "Elder Sign":
                list.append(card)
        dlg = cardDlg(list)
        dlg.title = "Seal Chaos Token"
        dlg.text = "Select a chaos token to seal"
        dlg.min = 1
        dlg.max = 1
        tokensSelected = dlg.show()
        if tokensSelected:
            remoteCall(tokensSelected[0].controller, "sealTokenToTable",[tokensSelected[0], cardToAttachTo[0], cardToAttachTo[1], me])
            card.Subtype = "Locked"
            cardToAttachTo = None

    elif card.Name == "Astronomical Atlas":
            if card.controller.deck:
                if 1 == askChoice("Look at the top card and attach a non-weakness ?", ["Yes","No"],["#000000","#000000"]):
                    if card._id in attached and len(attached[card._id]) == 5:
                        whisper("5 cards already attached to {}".format(card))
                        return
                    if deckLocked(card.controller):
                        whisper("Your deck is locked and cannot be looked at")
                        return
                    exhaust(card, x, y)
                    topCard = card.controller.deck.top()
                    if topCard.Subtype != "Weakness" and topCard.subType != "Basic Weakness":
                        attachCard(card, topCard) # attaches to Atlas
                        notify("{} uses {} to attach the top card of their deck".format(card.controller, card))
                        inc = 1
                        topCard.moveToTable(card.position[0], card.position[1], True)
                        for c in table:
                            if c._id in attached[card._id]: # if card is attached to Atlas
                                c.moveToTable(card.position[0] + (inc * 5), card.position[1] + (inc * 5), True)
                                c.sendToBack()
                                c.peek()
                                inc += 1
                                if inc - 1 == len(attached[card._id]):
                                    break
                    else:
                        topCard.peek()
                        notify("{} sees a forecoming weakness!".format(card.controller))
            else: whisper("Your deck is empty.")
    elif card.Name == "Shards of the Void":
        if card.Subtype != "Locked":
            if len(chaosBag()):
                for cT in chaosBag():
                    if cT.Name != "0":
                        continue
                    zero = cT
                    break
                if zero:
                    card.markers[Zero] = 1
                    removeChaosTokenFromBag("0")
                    notify("{} uses {} to seal a 0 token".format(card.controller, card))
                    card.Subtype = "Locked"
                else:
                    whisper("No 0 tokens in the Chaos Bag")
                    return
        else:
            sets = askChoice("Shards of the Void", ["Release a 0 token","Seal revealed 0 tokens here"],["#000000","#000000"])
            if sets == 0: return
            elif sets == 1:
                if card.markers[Zero]:
                    card.markers[Zero] -= 1
                    createChaosTokenInBag('35137ccc-db2b-4fdd-b0a8-a5d91f453a43')
                    notify("{} uses {} to release a 0 token".format(card.controller, card))
                else: whisper("No Zero tokens sealed on {}".format(card))
            elif sets == 2:
                inc = 0
                for cT in table:
                    if cT.name == "0" and cT.Subtype != "Sealed":
                        if cT.controller == me:
                            cT.delete()
                        else:
                            remoteCall(cT.controller, "deleteChaosToken", [cT])
                        card.markers[Zero] += 1
                        inc += 1
                if inc:
                    notify("{} uses {} to seal {} revealed 0 tokens".format(card.controller, card, inc))
                else: whisper("No revealed 0 to seal")

    elif card.Name == "Premonition":
        if chaosBag().controller != card.controller:
            chaosBag().controller = card.controller
            update()
        if card.Subtype != "Locked":
            attachTo(card)
            chaosBag().shuffle()
            for cT in chaosBag():
                cT.moveToTable(cardToAttachTo[0], cardToAttachTo[1])
                cT.Subtype = 'Sealed'
                cT.filter = "#99999999"
                notify("{} randomly seals {} on {}.".format(card.controller, cT, card))
                Premonition.append(cT)
                break
            card.Subtype = "Locked"
            updateBlessCurse()
            cardToAttachTo = None
        elif 1 == askChoice("Trigger Premonition ?", ["Yes","No"],["#000000","#000000"]):
            Premonition[0].SubType = ""
            Premonition[0].filter = None
            Premonition[0].moveToTable(ChaosTokenX, ChaosTokenY)
            Premonition = []
            discard(card)
    elif card.Name == "Flute of the Outer Gods":
        if card.Subtype != "Locked":
            sealXCurse(card)
        elif 1 == askChoice("Trigger Flute of the Outer Gods ?", ["Yes","No"],["#000000","#000000"]) and card.markers[Curse] > 0:
            exhaust(card, x=0,y=0)
            card.markers[Curse] -= 1
            addCurse()
    elif card.Name == "Protective Incantation":
        if card.Subtype != "Locked":
            attachTo(card)
            list = [cT for cT in chaosBag()
        if not ("Auto Fail" in cT.Name)]
            dlg = cardDlg(list)
            dlg.title = "Protective Incantation"
            dlg.text = "Select a Chaos Token to seal:"
            dlg.min = 1
            dlg.max = 1
            cT = dlg.show()
            if cT:
                remoteCall(cT[0].controller, "sealTokenToTable",[cT[0], cardToAttachTo[0], cardToAttachTo[1], me])
                card.Subtype = "Locked"
                cardToAttachTo = None

    elif card.Name == "Seal of the Seventh Sign":
        if card.Subtype != "Locked":
            attachTo(card)
            autoFail = [cT for cT in chaosBag()
        if "Auto Fail" in cT.Name]
            if autoFail:
                remoteCall(autoFail[0].controller, "sealTokenToTable",[autoFail[0], cardToAttachTo[0], cardToAttachTo[1], me])
                card.Subtype = "Locked"
                cardToAttachTo = None

    elif card.Name == "The Chthonian Stone":
        if card.Subtype != "Locked":
            attachTo(card)
            list = [cT for cT in chaosBag()
        if "Elder One" in cT.Name or "Skull" in cT.Name or "Cultist" in cT.Name or "Tablet" in cT.Name]
            if list:
                dlg = cardDlg(list)
                dlg.title = "The Chthonian Stone"
                dlg.text = "Select a Chaos Token to seal:"
                dlg.min = 1
                dlg.max = 1
                cT = dlg.show()
                if cT:
                    remoteCall(cT[0].controller, "sealTokenToTable",[cT[0], cardToAttachTo[0], cardToAttachTo[1], me])
                    card.Subtype = "Locked"
                    cardToAttachTo = None

    elif card.Name == "The Codex of Ages":
        if card.Subtype != "Locked":
            attachTo(card)
            elderSign = [cT for cT in chaosBag()
        if "Elder Sign" in cT.Name]
            if elderSign:
                remoteCall(elderSign[0].controller, "sealTokenToTable",[elderSign[0], cardToAttachTo[0], cardToAttachTo[1], me])
                card.Subtype = "Locked"
                cardToAttachTo = None

    
    elif card.Name == "Kōhaku Narukami" and card.Type == "Investigator":
        choice_list = ["Remove 2 Bless and 2 Curse for an action","Add 1 Bless or 1 Curse to the Chaos Bag"]
        color_list = ["#000000","#000000"]
        sets = askChoice("Kôhaku Narukami", choice_list, color_list)
        if sets == 0:
            return
        elif sets == 1: # Remove 2 Bless and 2 Curse
            if blessInCB() >= 2 and curseInCB() >= 2:
                for _ in range(2):
                    removeChaosTokenFromBag("Bless")
                    removeChaosTokenFromBag("Curse")
                updateBlessCurse()
                notify("{} uses {} to remove 2 bless and 2 curse tokens from the chaos bag to take an additional action".format(card.owner, card))
            else:
                whisper("Not enough bless and curse tokens in the chaos bag.")
        elif sets == 2:
            if curseInCB() > blessInCB():
                addBless()
            elif curseInCB() < blessInCB():
                addCurse()
            elif curseInCB() == blessInCB():
                choice_list = ["Add Bless","Add Curse"]
                color_list = ["#000000","#000000"]
                sets = askChoice("Kôhaku Narukami", choice_list, color_list)
                if sets == 0:
                    return
                elif sets == 1: 
                    addBless()
                elif sets == 2:
                    addCurse()

    elif card.Name == "Book of Living Myths":
        if blessInCB() or curseInCB():
            exhaust (card, x, y)
            if blessInCB() > curseInCB():
                removeChaosTokenFromBag("Bless")
                table.create('360db0ee-c362-4bbe-9554-b1fbf101d9ab', ChaosTokenX, ChaosTokenY, quantity = 1, persist = False)
                notify("{} uses {} to reveal a Bless token".format(card.owner, card))
            elif blessInCB() < curseInCB():
                removeChaosTokenFromBag("Curse")
                table.create('81df3f18-e341-401d-a6bb-528940a9c39e', ChaosTokenX, ChaosTokenY, quantity = 1, persist = False)
                notify("{} uses {} to reveal a Curse token".format(card.owner, card))
            elif blessInCB() == curseInCB():
                choice_list = ["Resolve A Bless Token","Resolve a Curse Token"]
                color_list = ["#000000","#000000"]
                sets = askChoice("Book of Living Myths", choice_list, color_list)
                if sets == 0:
                    return
                elif sets == 1: 
                    removeChaosTokenFromBag("Bless")
                    table.create('360db0ee-c362-4bbe-9554-b1fbf101d9ab', ChaosTokenX, ChaosTokenY, quantity = 1, persist = False)
                    notify("{} uses {} to reveal a Bless token".format(card.owner, card))
                elif sets == 2:
                    removeChaosTokenFromBag("Curse")
                    table.create('81df3f18-e341-401d-a6bb-528940a9c39e', ChaosTokenX, ChaosTokenY, quantity = 1, persist = False)
                    notify("{} uses {} to reveal a Curse token".format(card.owner, card))
            updateBlessCurse()
        else:
            whisper("Not enough Bless/Curse tokens in the Chaos Bag")
#############################################
#                                           #
#           Guardian Cards                  #
#                                           #
#############################################        
    elif card.Name == "Prepared for the Worst":
        notify("{} uses {} to search their deck for a Weapon card to draw.".format(card.controller, card))
        searchTopDeck(card.controller.deck, card.controller.hand, 9, traits="Weapon")
    elif card.Name == "Rite of Sanctification":
        if card.Subtype != "Locked":
            sealXBless(card, 5)
        elif card.markers[Bless]:
            if 1 == askChoice('Release a sealed bless token ?', ['Yes', 'Not now'], ['#dd3737', '#d0d0d0']):
                exhaust (card, x, y)
                card.markers[Bless] -= 1
                addBless()
                if not card.markers[Bless]:
                    notify("{} has no sealed Bless tokens left and is discarded".format(card))
                    discard(card)
    elif card.Name == "Tetsuo Mori":
        choice_list, color_list = InvestigatorList()
        sets = askChoice("Choose a player at your location:", choice_list, color_list)
        if sets == 0:
            return
        else:
            chosenPlayer = getPlayers()[sets - 1]
            choice_list = ['Search the discard pile','Search the top 9 cards of the deck']
            color_list = ['#46453E','#46453E']
            sets = askChoice("Tetsuo Mori", choice_list, color_list)
            if sets == 0:
                return
            if sets == 1: # Discard Pile
                remoteCall(chosenPlayer,"searchTopDeck",[chosenPlayer.piles['Discard Pile'],chosenPlayer.hand])
            if sets == 2: # Top 9
                remoteCall(chosenPlayer,"searchTopDeck",[chosenPlayer.deck,chosenPlayer.hand,9])
    elif card.Name == "Nephthys":
        choice_list = ['Seal a Bless token on Nephthys']
        color_list = ['#000000']
        if card.markers[Bless] >= 3:
            choice_list.append('Release 3 Bless Tokens')
            choice_list.append('Return 3 Bless Tokens to deal 2 damage')
            color_list.append('#000000')
            color_list.append('#000000')
        if len(choice_list) == 1:
            if blessOnTable() > 0:
                card.markers[Bless] += 1
                for t in table:
                    if t.name != "Bless":
                        continue
                    if t.SubType != "Sealed":
                        if t.controller == me:
                            doDiscard(me, t, chaosBag())
                        else:
                            remoteCall(t.controller, "doDiscard", [me, t, chaosBag()])
                        break
                notify("{} uses {} to seal a Bless token".format(card.controller, card))
        else:
            sets = askChoice("Nephthys", choice_list, color_list)
            if sets == 0:
                return
            if sets == 1: 
                if blessOnTable() > 0:
                    card.markers[Bless] += 1
                    for t in table:
                        if t.name != "Bless":
                            continue
                        if t.SubType != "Sealed":
                            if t.controller == me:
                                doDiscard(me, t, chaosBag())
                            else:
                                remoteCall(t.controller, "doDiscard", [me, t, chaosBag()])
                        break
                    notify("{} uses {} to seal a Bless token".format(card.controller, card))
            if sets == 2:
                exhaust (card, x, y)
                card.markers[Bless] -= 3
                notify("{} uses {} to release 3 Bless Tokens".format(card.controller, card))
                for i in range(0, 3):
                    addBless()
            if sets == 3:
                exhaust (card, x, y)
                card.markers[Bless] -= 3
                notify("{} uses {} to return 3 Bless tokens to the token pool and deal 2 damage to an enemy".format(card.controller, card))
    elif card.Name == "Holy Spear":
        choice_list = ["Release a token sealed here"]
        color_list = ['#000000']
        if blessInCB() >= 2:
            choice_list.append("Seal 2 Bless tokens here")
            color_list.append('#000000')
        sets = askChoice("Holy Spear", choice_list, color_list)
        if sets == 0:
            return
        if sets == 1: 
            if card.markers[Bless] == 0:
                return
            else:
                card.markers[Bless] -= 1
                notify("{} uses {} to release 1 Bless token".format(card.controller, card))
                addBless()
        if sets == 2: # Seal 2 Bless Tokens from CB
            BlessTokensRemoved = 0
            for t in shared.piles["Chaos Bag"]:
                if t.name == "Bless":
                    if t.controller == me:
                        doDiscard(me, t, chaosBag())
                    else:
                        remoteCall(t.controller, "doDiscard", [me, t, chaosBag()])
                    BlessTokensRemoved += 1
                    if BlessTokensRemoved == 2:
                        break
            card.markers[Bless] += 2
            notify("{} uses {} to seal 2 Bless tokens".format(card.controller, card))
            updateBlessCurse()
    elif card.Name == "Hallowed Mirror" and not isLocked(card):
        stop = False
        for c in card.controller.piles['Sideboard']:
            if stop is not True and c.Name == "Soothing Melody":
                c.moveTo(c.controller.hand)
                stop = True
            else:
                if c.Name == "Soothing Melody":
                    c.moveTo(c.controller.deck)
        notify("{} uses {} to draw {} and shuffle 2 other copies in their deck.".format(card.controller, card, c))
        shuffle(card.controller.deck)
    elif card.Name == "Boxing Gloves" and card.Level == "0":
        exhaust (card, x, y)
        notify("{} uses {} to search their deck for a Spirit card to draw.".format(card.controller, card))
        searchTopDeck(card.controller.deck, card.controller.hand, 6, traits="Spirit")
    elif card.Name == "Boxing Gloves" and card.Level == "3":
        exhaust (card, x, y)
        notify("{} uses {} to search their deck for a Spirit card to draw.".format(card.controller, card))
        searchTopDeck(card.controller.deck, card.controller.hand, 9, traits="Spirit")
    elif card.Name == "Stick to the Plan" and not isLocked(card) and not card.Subtype == "Locked": # Locking to prevent an additional trigger
        attachTo(card)
        unfilteredEvents = [c for c in card.controller.deck
                if c.Type == "Event" and ("Tactic" in c.Traits or "Supply" in c.Traits)]
        filteredEvents = []
        duplicate = []
        for c in unfilteredEvents:
            if c.name not in duplicate:
                duplicate.append(c.name)
                filteredEvents.append(c)
        dlg = cardDlg(filteredEvents)
        dlg.title = "Stick to the Plan"
        dlg.text = "Select up to 3 Tactic/Supply:"
        dlg.min = 0
        dlg.max = 3
        cardsSelected = dlg.show()
        if cardsSelected != None:
            inc = 0
            for c in cardsSelected:
                c.moveToTable(cardToAttachTo[0], cardToAttachTo[1], True)
                c.sendToBack()
                c.peek()
                if len(cardsSelected) == 1:
                    cardToAttachTo = None
                else:
                    attachTo(c)
                    inc += 1
                    if inc == len(cardsSelected): # Resets cardToAttachTo
                        cardToAttachTo = None
            card.Subtype = 'Locked'
            cardToAttachTo = None
            notify("{} uses {} to attach {} Supply or Tactic events to it.".format(card.controller, card, len(cardsSelected)))
        shuffle(card.controller.deck)
        if 1 == askChoice('Draw opening hand ?'
			, ['Yes', 'Not now'], ['#dd3737', '#d0d0d0']):
            drawOpeningHand()
    elif card.Name == "On the Hunt" and card.Level == "0":
        notify("{} uses {} to search the encounter deck for an Enemy to draw.".format(card.controller, card))
        searchTopDeck(encounterDeck(), table, 9, traits="Enemy")
    elif card.Name == "On the Hunt" and card.Level == "3":
        notify("{} uses {} to search the encounter deck for an Enemy to draw.".format(card.controller, card))
        searchTopDeck(encounterDeck(), table, traits="Enemy")
    elif card.Name == "Radiant Smite":
        if card.Subtype != "Locked":
            sealXBless(card, 3)
        elif card.Subtype == "Locked":
            if 1 == askChoice("Radiant Smite Bless Tokens", ["Return to Token Pool","Release in Chaos Bag"],["#000000","#000000"]):
                card.markers[Bless] = 0
            else: 
                b = card.markers[Bless]
                card.markers[Bless] = 0
                for _ in range(b):
                    addBless()
    elif card.Name == "Shield of Faith":
        if card.Subtype != "Locked":
            sealXBless(card, 5)
        else:
            if 1 == askChoice("Release a Bless token ?", ["Yes","No"],["#000000","#000000"]):
                if card.markers[Bless]:
                    exhaust(card, x=0,y=0)
                    card.markers[Bless] -= 1
                    addBless()
                    if not card.markers[Bless]:
                        notify("{} has no Bless tokens left and is discarded.".format(card))
                        discard(card)
                else: whisper("No Bless Tokens sealed")
    elif card.Name == "Nathaniel Cho" and card.Type == "Investigator":
        if 1 == askChoice("Trigger Elder Sign ?", ["Yes","No"],["#000000","#000000"]):
            Events = [c for c in card.controller.piles['Discard Pile']
                if c.Type == "Event"]
            dlg = cardDlg(Events)
            dlg.title = "Nathaniel Cho"
            dlg.text = "Select 1 card:"
            dlg.min = 1
            dlg.max = 1
            cardsSelected = dlg.show()
            if cardsSelected != None:
                cardsSelected[0].moveTo(card.controller.hand)
    elif card.Name == "Leo Anderson" and card.Type == "Investigator":
        if 1 == askChoice("Trigger Elder Sign ?", ["Yes","No"],["#000000","#000000"]):
            searchTopDeck(card.controller.deck, card.controller.hand, 3, traits="Ally")
#############################################
#                                           #
#           Seeker Cards                    #
#                                           #
#############################################      
    elif card.Name == "Captivating Discovery":
        searchTopDeck(card.controller.deck, card.controller.hand, 6)
    elif card.Name == "Ancestral Knowledge" and not card.Subtype == "Locked": # Using Locked to prevent an additional trigger
        shuffle(card.controller.deck)
        notify("{} uses {} to attach 5 random skills to it.".format(card.controller, card))
        attachTo(card)
        AncestralCards = []
        skills = [c for c in card.controller.deck
                if c.Type == "Skill" and not "Weakness" in c.Subtype]
        for i in range(0, 5):  
            AncestralCards.append(skills[i])
        for c in AncestralCards:
            c.moveToTable(cardToAttachTo[0], cardToAttachTo[1], True)
            c.sendToBack()
            c.peek()
            attachTo(c)
        card.Subtype = 'Locked'
        cardToAttachTo = None
        shuffle(card.controller.deck)
        if 1 == askChoice('Draw opening hand ?'
        , ['Yes', 'Not now'], ['#dd3737', '#d0d0d0']):
            drawOpeningHand()
    elif card.Name == "Occult Lexicon" and not isLocked(card):
        stop = False
        for c in card.controller.piles['Sideboard']:
            if stop is not True and c.Name == "Blood-Rite":
                c.moveTo(c.controller.hand)
                stop = True
            else:
                if c.Name == "Blood-Rite":
                    c.moveTo(c.controller.deck)
        notify("{} uses {} to draw {} and shuffle 2 other copies in their deck.".format(card.controller, card, c))
        shuffle(card.controller.deck)
    elif card.Name == "Old Book of Lore": # Automation doesn't account for location
        exhaust (card, x, y)
        if len(getPlayers()) == 1: # Solo
            searchTopDeck(me.deck, me.hand, 3)
        else:
            choice_list, color_list = InvestigatorList()
            sets = askChoice("Choose a player at your location:", choice_list, color_list)
            if sets == 0:
                return
            else:
                chosenPlayer = getPlayers()[sets - 1]
                notify("{} uses {} to let {} search their deck for a card to draw.".format(card.controller, card, chosenPlayer))
                # Two handed solo option
                if chosenPlayer.deck.controller == me:
                    searchTopDeck(chosenPlayer.deck,chosenPlayer.hand,3)
                else:
                    remoteCall(chosenPlayer,"searchTopDeck",[chosenPlayer.deck,chosenPlayer.hand,3])
    elif card.Name == "Cryptic Research": # Automation doesn't account for location
        if len(getPlayers()) == 1: # Solo
            drawMany(me.deck, 3)
        else:
            choice_list, color_list = InvestigatorList()
            sets = askChoice("Choose an investigator at your location to draw 3 cards:", choice_list, color_list)
            if sets == 0:
                return
            else:
                chosenPlayer = getPlayers()[sets - 1]
                if deckLocked(chosenPlayer):
                    whisper("{}'s deck is locked.".format(chosenPlayer))
                    return
                notify("{} uses {} to make {} draw 3 cards.".format(card.controller, card, chosenPlayer))
                remoteCall(chosenPlayer,"drawMany",[chosenPlayer.deck,3])
    elif card.Name == "No Stone Unturned" and card.Level == "0": # Automation doesn't account for location
        if len(getPlayers()) == 1: # Solo
            searchTopDeck(me.deck, me.hand, 6)
        else:
            choice_list, color_list = InvestigatorList()
            sets = askChoice("Choose an investigator at your location:", choice_list, color_list)
            if sets == 0:
                return
            else:
                chosenPlayer = getPlayers()[sets - 1]
                notify("{} uses {} to make {} search the top 6 cards of their deck.".format(card.controller, card, chosenPlayer))
                remoteCall(chosenPlayer,"searchTopDeck",[chosenPlayer.deck, chosenPlayer.hand, 6])
    elif card.Name == "No Stone Unturned" and card.Level == "5": # Automation doesn't account for location
        if len(getPlayers()) == 1: # Solo
            searchTopDeck(me.deck, me.hand)
        else:
            choice_list, color_list = InvestigatorList()
            sets = askChoice("Choose an investigator at your location:", choice_list, color_list)
            if sets == 0:
                return
            else:
                chosenPlayer = getPlayers()[sets - 1]
                notify("{} uses {} to make {} search their deck for a card to draw.".format(card.controller, card, chosenPlayer))
                remoteCall(chosenPlayer,"searchTopDeck",[chosenPlayer.deck, chosenPlayer.hand])
    elif card.Name == "Research Librarian":
        notify("{} uses {} to search their deck for a Tome to draw.".format(card.controller, card))
        searchTopDeck(card.controller.deck, card.controller.hand,traits="Tome")
    elif card.Name == "Guided by the Unseen":
        # Solo
        if len(getPlayers()) == 1:
            searchTopDeck(me.deck, table, 3)
        else:
            choice_list, color_list = InvestigatorList()
            sets = askChoice("Choose an investigator at your location:", choice_list, color_list)
            if sets == 0:
                return
            else:
                chosenPlayer = getPlayers()[sets - 1]
                notify("{} uses {} to make {} search their deck for a card commit to the test.".format(card.controller, card, chosenPlayer))
                remoteCall(chosenPlayer,"searchTopDeck",[chosenPlayer.deck, table, 3])
    elif card.Name == "Dr. Elli Horowitz":
        attachTo(card)
        notify("{} uses {} to search their deck for a Relic to attach to {}.".format(card.controller, card, card))
        searchTopDeck(card.controller.deck, table, 9, traits="Relic")
    elif card.Name == "Whitton Greene" and card.Level == "0":
        exhaust (card, x, y)
        notify("{} uses {} to search their deck for a Tome or Relic to draw.".format(card.controller, card))
        searchTopDeck(card.controller.deck, card.controller.hand, 6, traits="Tome,Relic")
    elif card.Name == "Whitton Greene" and card.Level == "2":
        exhaust (card, x, y)
        notify("{} uses {} to search their deck for a Tome or Relic to draw.".format(card.controller, card))
        searchTopDeck(card.controller.deck, card.controller.hand, 9, traits="Tome,Relic")
    elif card.Name == "Otherworld Codex":
        exhaust(card, x, y)
        subResource(card, x, y)
        searchTopDeck(encounterDeck(), encounterDiscard(), 9)
        notify("{} uses {} to look at the top 9 cards of the encounter deck and discards {}.".format(card.controller, card, cardsFound[0]))
    elif card.Name == "Practice Makes Perfect":
        notify("{} uses {} to search their deck for a Practiced card to commit to the test.".format(card.controller, card))
        searchTopDeck(card.controller.deck, table, 9, traits="Practiced")
    elif card.Name == "Eureka!":
        # Solo
        if len(getPlayers()) == 1:
            searchTopDeck(me.deck, me.hand, 3)
        else:
            choice_list, color_list = InvestigatorList()
            sets = askChoice("Choose a player:", choice_list, color_list)
            if sets == 0:
                return
            else:
                chosenPlayer = getPlayers()[sets - 1]
                # Two handed solo option
                if chosenPlayer.deck.controller == me:
                    notify("{} uses {} to search their deck for a card to draw.".format(card.controller, card))
                    searchTopDeck(chosenPlayer.deck,chosenPlayer.hand,3)
                else:
                    notify("{} uses {} to let {} search their deck for a card to draw.".format(card.controller, card, chosenPlayer))
                    remoteCall(chosenPlayer,"searchTopDeck",[chosenPlayer.deck,chosenPlayer.hand,3])
                
    elif card.Name == "Mr. “Rook”":
        exhaust(card, x, y)
        subResource(card, x, y)
        choice_list = ['3', '6', '9']
        color_list = ['#000000','#000000','#000000']
        sets = askChoice("Search how many cards ?", choice_list, color_list)
        if sets == 0:
            return
        else:
            count = sets * 3
            searchTopDeck(card.controller.deck, card.controller.hand, count)
    elif card.Name == "Obscure Studies":
        if AmandaCard:
            x, y = AmandaCard.position
            AmandaCard.moveTo(card.controller.hand)
            card.moveToTable(x, y)
            card.sendToBack()
            card.highlight = WhiteColour
            AmandaCard = card

    elif card.Name == "Professor William Webb" and card.Level == "0":
        sets = askChoice("William Webb", ["Return an Item","Discover a connecting clue (manual)"],["#000000","#000000"])
        if sets == 1:
                if len(card.controller.piles['Discard Pile']):
                    exhaust(card, x, y)
                    card.markers[Resource] -= 1
                    notify("{} uses {} to return an Item from the discard pile.".format(card.controller, card))
                    searchTopDeck(card.controller.piles['Discard Pile'], card.controller.hand, traits="Item")
                else: notify("Discard Pile is Empty")
        elif sets == 2:
                exhaust(card, x, y)
                card.markers[Resource] -= 1
                notify("{} uses {} to discover a clue at a connecting location.".format(card.controller, card))
        
    elif card.Name == "Professor William Webb" and card.Level == "2":
        if len(card.controller.piles['Discard Pile']):
            exhaust(card, x, y)
            card.markers[Resource] -= 1
            notify("{} uses {} to return an Item from the discard pile and discover a clue at a connecting location.".format(card.controller, card))
            searchTopDeck(card.controller.piles['Discard Pile'], card.controller.hand, traits="Item")
        else: notify("Discard Pile is Empty")
    elif card.Name == "Mandy Thompson" and card.Type == "Investigator":
        if 1 == askChoice("Trigger Elder Sign ?", ["Yes","No"],["#000000","#000000"]):
            notify("Commit or draw is manual")
            searchTopDeck(card.controller.deck, table, 3)
    elif card.Name == "Joe Diamond" and card.Type == "Investigator":
        if 1 == askChoice("Trigger Elder Sign ?", ["Yes","No"],["#000000","#000000"]):
            Insights = [card for card in card.controller.piles['Discard Pile']
            if "Insight." in card.Traits and card.Type == "Event"]
            dlg = cardDlg(Insights)
            dlg.title = "Joe Diamond"
            dlg.text = "Select 1 card to move back to the Hunch Deck:"
            dlg.min = 1
            dlg.max = 1
            cardsSelected = dlg.show()
            if cardsSelected != None:
                cardsSelected[0].moveToBottom(card.controller.piles['Secondary Deck'])
    elif card.Name == "Livre d'Eibon":
        if card.controller.hand:
            sets = askChoice("Livre d'Eibon", ["Swap cards","Commit a card(manual)"],["#000000","#000000"])
            if sets == 0: return
            exhaust(card, x, y)
            if sets == 1:
                dlg = cardDlg(card.controller.hand)
                dlg.title = "Livre d'Eibon"
                dlg.text = "Select a card to swap with the top card of your deck"
                dlg.min = 1
                dlg.max = 1
                c = dlg.show()
                if c:
                    swapCard(c[0])
        else: whisper("No cards in hand")
#############################################
#                                           #
#           Rogue Cards                     #
#                                           #
############################################# 
    elif card.Name == "Underworld Market" and not isLocked(card) and not card.Subtype == "Locked": # Locking to prevent an additional trigger
        illicits = [c for c in card.controller.deck if "Illicit" in c.Traits]
        dlg = cardDlg(illicits)
        dlg.title = "Underworld Market"
        dlg.text = "Select 10 Illicit cards:"
        dlg.min = 10
        dlg.max = 10
        cardsSelected = dlg.show()
        if cardsSelected != None:
            for c in cardsSelected:
                c.moveTo(card.controller.piles['Secondary Deck'])
            card.Subtype = 'Locked'
            notify("{} uses {} to put {} Illicit cards in secondary deck.".format(card.controller, card, len(cardsSelected)))
            shuffle(card.controller.piles['Secondary Deck'])
        shuffle(card.controller.deck)
        if 1 == askChoice('Draw opening hand ?'
			, ['Yes', 'Not now'], ['#dd3737', '#d0d0d0']):
            drawOpeningHand()
    elif card.Name == "Lucky Cigarette Case" and card.Level == "0":
        exhaust (card, x, y)
        draw(card.controller.deck)
    elif card.Name == "Pickpocketing":
        exhaust (card, x, y)
        draw(card.controller.deck)
    elif card.Name == "Lucky Cigarette Case" and card.Level == "3":
        exhaust (card, x, y)
        count = askInteger("Succeeded by how much ?", 2)
        if count is None or count <= 0:
            whisper("Lucky Cigarette Case: invalid card count")
            return
        else:
            notify("{} uses {} to search the top {} cards of their deck for a card to draw.".format(card.controller, card, count))
            searchTopDeck(card.controller.deck, card.controller.hand, count)

    elif card.Name == "Dark Ritual":
        sealXCurse(card, 5)
#############################################
#                                           #
#           Survivor Cards                  #
#                                           #
############################################# 
    elif card.Name == "Salvage":
        searchTopDeck(card.controller.piles['Discard Pile'], card.controller.hand, traits="Item")
    elif card.Name == "Rabbit's Foot" and card.Level == "0":
        exhaust (card, x, y)
        draw(card.controller.deck)
    elif card.Name == "Resourceful":
        list = [c for c in card.controller.piles['Discard Pile']
                    if "Survivor" in c.Class and c.Name != "Resourceful"]
        if list:
            dlg = cardDlg(list)
            dlg.title = "Resourceful"
            dlg.text = "Select a card to return to your hand"
            dlg.min = 1
            dlg.max = 1
            c = dlg.show()
            if c:
                c[0].moveTo(card.controller.hand)
                notify("{} uses {} to return a card to their hand".format(card.controller, card))
        else: whisper("No relevant cards in the discard pile")
    elif card.Name == "Rabbit's Foot" and card.Level == "3":
        exhaust (card, x, y)
        count = askInteger("Failed by how much ?", 2)
        if count is None or count <= 0:
            whisper("Rabbit's Foot: invalid card count")
            return
        else:
            notify("{} uses {} to search the top {} cards of their deck for a card to draw.".format(card.controller, card, count))
            searchTopDeck(card.controller.deck, card.controller.hand, count)        
    elif card.Name == "Scavenging":
        exhaust (card, x, y)
        searchTopDeck(card.controller.piles['Discard Pile'], card.controller.hand, traits="Item")
    elif card.Name == "A Chance Encounter":
        # Solo
        if len(getPlayers()) == 1:
            searchTopDeck(card.controller.piles['Discard Pile'], table, traits="Ally")
            if len(cardsFound) > 0:
                notify("{} puts {} into play".format(card.controller, cardsFound[0]))
        else:
            choice_list, color_list = InvestigatorList()
            sets = askChoice("Choose a player:", choice_list, color_list)
            if sets == 0:
                return
            else:
                chosenPlayer = getPlayers()[sets - 1]
                notify("{} uses {} to search {}'s discard pile for an Ally to put in play.".format(card.controller, card, chosenPlayer.name))
                #Two-Handed solo option
                if chosenPlayer.piles['Discard Pile'].controller == me:
                    searchTopDeck(chosenPlayer.piles['Discard Pile'], table, traits="Ally")
                    if len(cardsFound) > 0:
                        notify("{} puts {} into play".format(card.controller, cardsFound[0]))
                else:
                    chosenPlayer.piles['Discard Pile'].controller = me
                    searchTopDeck(chosenPlayer.piles['Discard Pile'], table, traits="Ally")
                    if len(cardsFound) > 0:
                        notify("{} puts {} into play".format(card.controller, cardsFound[0]))
                    chosenPlayer.piles['Discard Pile'].controller = chosenPlayer
    elif card.Name == "Unrelenting":
        attachTo(card)
        card.sendToBack()
        if chaosBag().controller != card.controller:
            chaosBag().controller = card.controller
        list = [card for card in table
                    if (card.Type == 'Chaos Token') and (card.Subtype != 'Sealed')]
        for card in chaosBag():
            list.append(card)
        dlg = cardDlg(list)
        dlg.title = "Seal Chaos Token"
        dlg.text = "Select up to 3 Chaos Token to seal"
        dlg.min = 0
        dlg.max = 3
        tokensSelected = dlg.show()
        if tokensSelected == None:
            return
        else:
            for cT in tokensSelected:
                cT.moveToTable(cardToAttachTo[0], cardToAttachTo[1])
                cT.Subtype = 'Sealed'
                cT.filter = "#99999999"
                notify("{} seals {}.".format(card.owner, cT))
                attachTo(cT)
            cardToAttachTo = None
            updateBlessCurse()
    elif card.Name == "True Survivor":
        if len(card.controller.piles['Discard Pile']):
            searchTopDeck(card.controller.piles['Discard Pile'], card.controller.hand, traits="Innate")
    elif card.Name == "Scrounge for Supplies":
        list = [c for c in card.controller.piles['Discard Pile']
                    if c.Level == "0"]
        if list:
            dlg = cardDlg(list)
            dlg.title = "Scrounge for Supplies"
            dlg.text = "Select a card to return to your hand"
            dlg.min = 1
            dlg.max = 1
            c = dlg.show()
            if c:
                c[0].moveTo(card.controller.hand)
    elif card.Name == "Wendy's Amulet":
        Events = [e for e in card.controller.piles['Discard Pile']
        if e.Type == "Event"]
        if Events:
            if not "Advanced." in card.Text:
                topMostEvent = str(Events[0].name)
                whisper("Topmost event is {}.".format(Events[0]))
                if 1 == askChoice("Play the topmost event of your discard pile ?", ["Yes","No"],["#000000","#000000"], customButtons = [topMostEvent]):
                    Events[0].moveToTable(card.position[0], card.position[1] + 50)
                    notify("{} uses {} to play the topmost event from their discard pile".format(card.controller, card))
            elif 1 == askChoice("Play an event from your discard pile ?", ["Yes","No"],["#000000","#000000"]):
                dlg = cardDlg(Events)
                dlg.title = "Wendy's Amulet"
                dlg.text = "Select an Event:"
                dlg.min = 1
                dlg.max = 1
                event = dlg.show()
                if event is not None:
                    event[0].moveToTable(card.position[0], card.position[1] + 50)
                    notify("{} uses {} to play an event from their discard pile".format(card.controller, card))
        else: whisper("No events in the Discard Pile")
    elif card.Name == "Patrice Hathaway" and card.Type == "Investigator":
        if 1 == askChoice("Trigger Elder Sign ?", ["Yes","No"],["#000000","#000000"]):
            dlg = cardDlg(card.controller.piles['Discard Pile'])
            dlg.title = "Patrice Hathaway"
            dlg.text = "Choose 1 card to leave in the discard:"
            dlg.min = 1
            dlg.max = 1
            leave = dlg.show()
            if leave is not None:
                for c in card.controller.piles['Discard Pile']:
                    if c != leave[0]:
                        c.moveTo(card.controller.deck)
                shuffle(card.controller.deck)
    elif card.Name == "Silas Marsh" and card.Type == "Investigator":
        if 1 == askChoice("Trigger Elder Sign ?", ["Yes","No"],["#000000","#000000"]):
            skills = [c for c in card.controller.piles['Discard Pile']
            if c.Type == "Skill"]
            dlg = cardDlg(skills)
            dlg.title = "Silas Marsh"
            dlg.text = "Choose 1 skill card to commit:"
            dlg.min = 1
            dlg.max = 1
            skill = dlg.show()
            if skill is not None:
                skill[0].moveToTable(card.position[0], card.position[1] - 100)
                skill[0].select()
    elif card.Name == "Short Supply":
        discardedCardCount = 0
        for i in range(0, 10):
            if len(card.controller.deck) > 0 :
                discardedCardCount += 1 
                c = card.controller.deck[0]
                c.moveTo(card.controller.piles['Discard Pile'])
            else:
                break
        notify("{} discards the top {} cards of their deck due to Short Supply.".format(card.controller, discardedCardCount))
    elif card.Name == "William Yorick":
        result = askChoice("Perform:", ["Trigger Elder Sign?", "Trigger investigator ability?"], ["#000000","#000000"])
        if result == 1:
            anyCard = [c for c in card.controller.piles['Discard Pile']]
            dlg = cardDlg(anyCard)
            dlg.title = "William Yorick"
            dlg.text = "Select 1 card to add to hand:"
            dlg.min = 1
            dlg.max = 1
            cardsSelected = dlg.show()
            if cardsSelected != None:
                cardsSelected[0].moveTo(card.controller.hand)
        elif result == 2:
            assets = [c for c in card.controller.piles['Discard Pile'] if c.Type == "Asset"]
            dlg = cardDlg(assets)
            dlg.title = "William Yorick"
            dlg.text = "Choose 1 asset to put into play:"
            dlg.min = 1
            dlg.max = 1
            cardsSelected = dlg.show()
            if cardsSelected is not None:
                cardsSelected[0].moveToTable(card.position[0], card.position[1] - 100)
                cardsSelected[0].select()
#############################################
#                                           #
#           Neutral Cards                   #
#                                           #
#############################################      
    elif card.Name == "Word of Weal": 
        wow = searchInPile(card.controller.piles['Discard Pile'], "Word of Woe")
        if wow is not None :
            wow.moveTo(wow.controller.deck)
            notify("{} shuffles {} into their deck.".format(card.controller, wow.Name))
            shuffle(card.controller.deck)
        discard(card)
    elif card.Name == "Word of Woe":
        wow = searchInPile(card.controller.piles['Discard Pile'], "Word of Weal")
        if wow is not None :
            wow.moveTo(wow.controller.deck)
            notify("{} shuffles {} into their deck.".format(card.controller, wow.Name))
            shuffle(card.controller.deck)
        discard(card)
    elif card.Name == "Backpack" and card.Level == "0":
        attachTo(card)        
        searchTopDeck(card.controller.deck, table, 6, traits="Item,Supply")
    elif card.Name == "Backpack" and card.Level == "2":
        attachTo(card)    
        searchTopDeck(card.controller.deck, table, 12, traits="Item,Supply")
    elif card.Name == "Calling in Favors":
        notify("{} uses {} to search their deck for an Ally and play it.".format(card.controller, card))        
        searchTopDeck(card.controller.deck, table, 9, traits="Ally")
    elif card.Name == "Anna Kaslow":
        notify("{} uses {} to search their deck for a Tarot and put it in play.".format(card.controller, card))        
        searchTopDeck(card.controller.deck, table, traits="Tarot")
    elif card.Name == "Lucid Dreaming":
        searchTopDeck(card.controller.deck, card.controller.hand)
    elif card.Name == "Tekeli-li":
        card.moveToBottom(specialDeck())
        notify("{} is placed on the bottom of the Tekeli-li deck".format(card.name))
    elif card.Name == "Favor of the Moon":
        if card.Subtype != "Locked":
            sealXCurse(card, 3)
        elif 1 == askChoice("Trigger Favor of the Moon ?", ["Yes","No"],["#000000","#000000"]):
            exhaust(card, x=0,y=0)
            table.create('81df3f18-e341-401d-a6bb-528940a9c39e', ChaosTokenX, ChaosTokenY, quantity = 1, persist = True)
            card.markers[Curse] -= 1
            if not card.markers[Curse]:
                notify("{} has no Curse tokens left and is discarded.".format(card))
                discard(card)
            firstInvestigator(card.controller).markers[Resource] += 1
    elif card.Name == "Favor of the Sun":
        if card.Subtype != "Locked":
            sealXBless(card, 3)
        elif 1 == askChoice("Trigger Favor of the Sun ?", ["Yes","No"],["#000000","#000000"]):
            exhaust(card, x=0,y=0)
            table.create('360db0ee-c362-4bbe-9554-b1fbf101d9ab', ChaosTokenX, ChaosTokenY, quantity = 1, persist = False)
            card.markers[Bless] -= 1
            if not card.markers[Bless]:
                notify("{} has no Bless tokens left and is discarded.".format(card))
                discard(card)
    elif card.Name == "Day of Reckoning":
        if card.Subtype != "Locked":
            attachTo(card)
            elderSign = [cT for cT in chaosBag() if "Elder Sign" in cT.Name]
            if elderSign:
                remoteCall(elderSign[0].controller, "sealTokenToTable",[elderSign[0], cardToAttachTo[0], cardToAttachTo[1], me])
                card.Subtype = "Locked"
                cardToAttachTo = None
    else:
        if ("Exhaust " + str(card.Name) in card.Text) or (" exhaust " + str(card.Name) in card.Text):
            exhaust(card, x, y)
    
#############################################
#                                           #
#           Mythos Cards                    #
#                                           #
#############################################   
def shuffleTekelili(group=None, x=0, y=0):
    if len(specialDeck()) > 0:
        if len(getPlayers()) > 1:
            choice_list, color_list = InvestigatorList()
            sets = askChoice("Tekeli-li shuffle into:", choice_list, color_list)
            if sets == 0:
                return
            specialDeck().controller = getPlayers()[sets - 1]
            remoteCall(getPlayers()[sets - 1],"moveTekelili",[getPlayers()[sets - 1]])
        else:
            moveTekelili(me)
    else:
        whisper("The Tekeli-li deck is empty!")

def moveTekelili(player):
    specialDeck()[0].moveToBottom(player.deck)
    shuffle(player.deck)
    notify("{} shuffles a Tekeli-li card into their deck.".format(player))

#############################################
#                                           #
#           Character Cards                 #
#                                           #
#############################################      
def SefinaOpening(player):
    global cardToAttachTo
    drawMany(player.deck, 13)
    removeWeaknessCards()
    Sefina = [card for card in table
            if card.Name == "Sefina Rousseau" and card.Type == "Investigator" and card.controller == player]
    attachTo(Sefina[0])
    eventsToShow = [card for card in player.hand
            if card.Type == "Event"]
    dlg = cardDlg(eventsToShow)
    dlg.title = "Sefina Rousseau"
    dlg.text = "Select up to 5 events to attach to place under Sefina:"
    dlg.min = 0
    dlg.max = 5
    cardsSelected = dlg.show()
    if cardsSelected != None:
        inc = 0
        for card in cardsSelected:
            card.moveToTable(cardToAttachTo[0], cardToAttachTo[1])
            card.sendToBack()
            if len(cardsSelected) == 1:
                cardToAttachTo = None
            else:
                attachTo(card)
                inc += 1
                if inc == len(cardsSelected): # Resets cardToAttachTo
                    cardToAttachTo = None
    sizeHand = card.controller.counters['Maximum Hand Size'].value
    cardsInHand = len(card.controller.hand)
    if cardsInHand > sizeHand: #Hand Size Check
        discardCount = cardsInHand - sizeHand
        dlg = cardDlg(player.hand)
        dlg.title = "You have more than the allowed "+ str(sizeHand) +" cards in hand."
        dlg.text = "Select " + str(discardCount) + " Card(s):"
        dlg.min = 0
        dlg.max = discardCount
        cardsSelected = dlg.show()
        if cardsSelected is not None:
            for card in cardsSelected:
                discard(card)

def JoeOpening(player):
    for c in player.deck:
        if c.Name == "Unsolved Case":
            c.moveTo(player.piles['Secondary Deck'])
            break
    Insights = [card for card in player.deck
            if "Insight." in card.Traits and card.Type == "Event"]
    if len(Insights) < 10:
        whisper("Invalid Deck ! Not enough Insight events !")
        return
    dlg = cardDlg(Insights)
    dlg.title = "Hunch Deck"
    dlg.text = "Select 10 Insight events for your hunch deck:"
    dlg.min = 10
    dlg.max = 10
    cardsSelected = dlg.show()
    if cardsSelected is not None:
        for c in cardsSelected:
            c.moveTo(player.piles['Secondary Deck'])
        shuffle(player.piles['Secondary Deck'])
    player.piles['Secondary Deck'].viewState = "pile"
