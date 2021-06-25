import winsound

def soundDir():
    with open("data.path", 'r') as f:
            return f.readline() + "\\GameDatabase\\a6d114c7-2e2a-4896-ad8c-0330605c90bf\\Sound\\"
   
def moveCardsSound(args):
    mute()
    
    #Only for move card from Table to Table
    if isinstance(args.fromGroups[0],Table) and isinstance(args.toGroups[0],Table):
        folderGeneric = "Generic\\moveCard\\"
        folderSpecific = "Specific\\moveCard\\"
    #Only if move mini Investigator card
        if len(args.cards) == 1:
            card = args.cards[0]
            if card.isFaceUp:
                if card.properties["Type"] == "Mini":
                    winsound.PlaySound(soundDir() + "Generic\\Mini\\" + "Mini ("+ str(rnd(1,5)) +").wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)  
                if "Monster." in card.properties["Traits"]:
                    winsound.PlaySound(soundDir() + "Generic\\Monster\\" + "Monster ("+ str(rnd(1,14)) +").wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)      
                if "Humanoid." in card.properties["Traits"]:
                    winsound.PlaySound(soundDir() + folderGeneric + "Humanoid.wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)
                if "Cultist." in card.properties["Traits"]:
                    winsound.PlaySound(soundDir() + "Generic\\Cultist\\" + "Cultist ("+ str(rnd(1,13)) +").wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)
                playSpecificCard(card,folderSpecific)
    #Only for move card from Pile to Table
    if isinstance(args.fromGroups[0],Pile) and isinstance(args.toGroups[0],Table):
        folderGeneric = "Generic\\playCard\\"
        folderSpecific = "Specific\\playCard\\"
        if len(args.cards) == 1:
            card = args.cards[0]
            if card.isFaceUp:       
                #Search generic sound with name (if multiple trait found, we play only last in this list)
                searchGenericSound(card,folderGeneric)
                playSpecificCard(card,folderSpecific)

def modifyMarkerSound(args):
    card = args.card
    #Compare Old value on new value
    oldValue = args.value
    if args.marker == "Resource":
        newValue = card.markers[Resource]
        if oldValue > newValue :
            subTokenSound(card, args.marker)
    
def subTokenSound(card, tokenType):
    mute()  
    if tokenType == "Resource":
        #On remove token
        folderGeneric = "Generic\\removeResourceCard\\"
        folderSpecific = "Specific\\removeResourceCard\\"
        #Search generic sound with name (if multiple trait found, we play only last in this list)
        if card.isFaceUp and card.Type != "Investigator":
            searchGenericSound(card,folderGeneric)
            playSpecificCard(card,folderSpecific)

def exhaustCardsSound(card):
    mute()
    folderSpecific = "Specific\\exhaustCard\\"
    playSpecificCard(card,folderSpecific)

def discardCardsSound(card):
    mute()
    folderSpecific = "Specific\\discardCard\\"
    playSpecificCard(card,folderSpecific)

def flipCardsSound(card):
    mute()
    folderSpecific = "Specific\\flipCard\\"
    playSpecificCard(card,folderSpecific)

def revealEncounterSound(card):
    mute()  
    folderGeneric = "Generic\\revealEncounterCard\\"
    folderSpecific = "Specific\\revealEncounterCard\\"
    if card.isFaceUp: 
        if "Monster." in card.properties["Traits"]:
            winsound.PlaySound(soundDir() + "Generic\\Monster\\" + "Monster ("+ str(rnd(1,14)) +").wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        if "Ghoul." in card.properties["Traits"]:
            winsound.PlaySound(soundDir() + folderGeneric + "Ghoul.wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        if "Cultist." in card.properties["Traits"]:
            winsound.PlaySound(soundDir() + "Generic\\Cultist\\" + "Cultist ("+ str(rnd(1,13)) +").wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        playSpecificCard(card,folderSpecific)


def playSpecificCard(card,folder):
    #Try open specific sound with name 
    name =  card.name.replace('"', '')
    file_sound = name + ".wav"
    winsound.PlaySound(soundDir() + folder + file_sound, winsound.SND_ASYNC | winsound.SND_NODEFAULT) 

def searchGenericSound(card,folderGeneric):
    if "Tool." in card.properties["Traits"]:
        winsound.PlaySound(soundDir() + folderGeneric + "Tool.wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    if "Relic." in card.properties["Traits"]:
        winsound.PlaySound(soundDir() + folderGeneric + "Relic.wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT) 
    if "Tome." in card.properties["Traits"]:
        winsound.PlaySound(soundDir() + folderGeneric + "Tome.wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT) 
    if "Spell." in card.properties["Traits"]:
        winsound.PlaySound(soundDir() + folderGeneric + "Spell.wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)  
    if "Firearm." in card.properties["Traits"]:
        winsound.PlaySound(soundDir() + folderGeneric + "Firearm.wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    if "Melee." in card.properties["Traits"]:
        winsound.PlaySound(soundDir() + folderGeneric + "Melee.wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    if "Tarot." in card.properties["Traits"]:
        winsound.PlaySound(soundDir() + folderGeneric + "Tarot.wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    if "Blessed." in card.properties["Traits"]:
        winsound.PlaySound(soundDir() + folderGeneric + "Blessed.wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    if "Cursed." in card.properties["Traits"]:
        winsound.PlaySound(soundDir() + folderGeneric + "Cursed.wav", winsound.SND_ASYNC | winsound.SND_NODEFAULT)

        