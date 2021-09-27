def searchTopDeck(group, target, count = None, trait = None, trait2 = None):
    mute()
    if len(group) == 0: return
    if count == None:
        count = len(group)
    else:
        MandyonTable = filter(lambda c: (c.Name == "Mandy Thompson" and c.Type == "Investigator"), table)
        if not count == len(group):  #No +3 option to search count if searching the whole deck
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
    if trait != None: #if trait is specified
        if trait2 == None:
            cardsToShow = [card for card in group.top(count)
                if (trait in card.Traits) or (trait in card.Type) or (card.Name == "Astounding Revelation") or (card.Name == "Occult Evidence" )or (card.Name == "Surprising Find") or (card.Name == "Shocking Discovery")]
        else:
            cardsToShow = [card for card in group.top(count)
                if (trait in card.Traits) or (trait2 in card.Traits) or (trait in card.Type) or (card.Name == "Astounding Revelation") or (card.Name == "Occult Evidence" )or (card.Name == "Surprising Find") or (card.Name == "Shocking Discovery")]
        if len(cardsToShow) == 0:
            notify("No relevant card found")
            shuffle(group)
            return
    else: 
        cardsToShow = [c for c in group.top(count)]
    for c in cardsToShow: #Shocking Discovery
        if c.Name == "Shocking Discovery":
            c.moveTo(table)
            c.highlight = RedColour   
            notify("Shocking Discovery!")
            shuffle(group)
            return
    dlg = cardDlg(cardsToShow)
    dlg.title = "Search the top "+ str(count) +" cards."
    dlg.text = "Select the cards:"
    dlg.min = 1
    dlg.max = count #adding this for multiple possible cards draw like astounding revelation
    cardsSelected = dlg.show()
    if cardsSelected != None:
        for card in cardsSelected:
             card.moveTo(target)
    shuffle(group)

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
    elif card.Name == "Arcane Initiate" and card.controller == me:
        exhaust(card, x, y)
        searchTopDeck(card.owner.deck, card.owner.hand, 3, "Spell")
    elif card.Name == "Stargazing":
        if len(encounterDeck()) > 9:
            stop = False
            for c in card.owner.piles['Sideboard']:
                if c.Name == "The Stars Are Right" and stop is not True:
                    shuffleIntoTop(c, 0, 0, me, encounterDeck(),10)
                    stop = True
        else: 
            whisper("There are not enough cards in the encounter Deck")
    elif card.Name == "Prepared for the Worst" and card.controller == me:
        searchTopDeck(card.owner.deck, card.owner.hand, 9, "Weapon")
    elif card.Name == "Backpack" and card.controller == me and card.Level == "0":
        searchTopDeck(card.owner.deck, table, 6, "Item", "Supply")
    elif card.Name == "Backpack" and card.controller == me and card.Level == "2":
        searchTopDeck(card.owner.deck, table, 12, "Item", "Supply")
    elif card.Name == "Boxing Gloves" and card.controller == me and card.Level == "0":
        exhaust (card, x, y)
        searchTopDeck(card.owner.deck, card.owner.hand, 6, "Spirit")
    elif card.Name == "Boxing Gloves" and card.controller == me and card.Level == "3":
        exhaust (card, x, y)
        searchTopDeck(card.owner.deck, card.owner.hand, 9, "Spirit")
    elif card.Name == "Calling in Favors" and card.controller == me:
        searchTopDeck(card.owner.deck, table, 9, "Ally")
    elif card.Name == "Research Librarian" and card.controller == me:
        searchTopDeck(card.owner.deck, card.owner.hand)
    elif card.Name == "Anna Kaslow" and card.controller == me:
        searchTopDeck(card.owner.deck, card.owner.hand, len(card.owner.deck), "Tarot")
    elif card.Name == "Stick to the Plan" and card.controller == me:
        searchTopDeck(card.owner.deck, card.owner.hand, len(card.owner.deck), "Supply", "Tactic")
    elif card.Name == "Lucid Dreaming" and card.controller == me:
        searchTopDeck(card.owner.deck, card.owner.hand)
    elif card.Name == "Word of Command" and card.controller == me:
        searchTopDeck(card.owner.deck, card.owner.hand, len(card.owner.deck), Spell)
    elif card.Name == "Dr. Elli Horowitz" and card.controller == me:
        searchTopDeck(card.owner.deck, table, 9, "Relic")
    elif card.Name == "Whitton Greene" and card.controller == me and card.Level == "0":
        exhaust (card, x, y)
        searchTopDeck(card.owner.deck, card.owner.hand, 6, "Tome", "Relic")
    elif card.Name == "Whitton Greene" and card.controller == me and card.Level == "2":
        exhaust (card, x, y)
        searchTopDeck(card.owner.deck, card.owner.hand, 9, "Tome", "Relic")
    elif card.Name == "On the Hunt" and card.controller == me and card.Level == "0":
        searchTopDeck(encounterDeck(), table, 9, "Enemy")
    elif card.Name == "On the Hunt" and card.controller == me and card.Level == "3":
        searchTopDeck(encounterDeck(), table, len(encounterDeck()), "Enemy")
    elif card.Name == "Otherworld Codex" and card.controller == me:
        exhaust(card, x, y)
        subResource(card, x, y)
        searchTopDeck(encounterDeck(), encounterDiscard(), 9)
    elif card.Name == "Practice Makes Perfect" and card.controller == me:
        searchTopDeck(card.owner.deck, table, 9, "Practiced")
    elif card.Name == "Eureka!":
        searchTopDeck(me.deck, me.hand, 3)
    elif card.Name == "Mr. “Rook”" and card.controller == me:
        exhaust(card, x, y)
        subResource(card, x, y)
        count = 0
        MandyonTable = filter(lambda card: (card.Name == "Mandy Thompson" and card.Type == "Investigator"), table)
        choice_list = ['3', '6', '9']
        color_list = ['#000000','#000000','#000000']
        if MandyonTable:
            choice_list.append('12 (Mandy)')
            color_list.append('#F4BB2F')
        sets = askChoice("Search how many cards ?", choice_list, color_list)
        if sets == 0:
            return
        if sets == 1:
            count = 3    
        if sets == 2:
            count = 6
        if sets == 3:
            count = 9
        if sets == 4:
            count = 12
        for c in card.owner.deck.top(count):
            if c.Name == "Shocking Discovery":
                c.moveTo(table)
                c.highlight = RedColour   
                notify("Shocking Discovery!")
                shuffle(card.owner.deck)
                return
        dlg = cardDlg(card.owner.deck.top(count))
        dlg.title = "Search the top "+ str(count) +" cards."
        dlg.text = "Select the cards:"
        dlg.min = 1
        dlg.max = count
        cardsSelected = dlg.show()
        if cardsSelected != None:
            for card in cardsSelected:
                 card.moveTo(card.owner.hand)
        shuffle(card.owner.deck)      
    else:
        exhaust(card, x, y)
