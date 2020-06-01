#
# Routines for writing out updated decks based on either the player piles or the shared piles
#
from datetime import datetime as dt
import collections
import clr
clr.AddReference('System.Web.Extensions')
from System.Web.Script.Serialization import JavaScriptSerializer as json #since .net 3.5?

PLAYER_DECK = ['Investigator', 'Special', 'Asset', 'Event', 'Skill', 'Weakness', 'Sideboard', 'Basic Weaknesses']

def takeControlGlobal(group, x=0, y=0):
    notify( me.name + " takes control of shared cards")
    mute()
	#Take control of each not player card on table
    for card in table:
        if not isPlayerCard(card):
            card.controller = me
	#Take control of each shared pile			
	for p in shared.piles:
            if shared.piles[p].controller != me:
                shared.piles[p].controller = me

def saveTable(group, x=0, y=0):
	mute()
	
	if 1 != askChoice('You are about to SAVE the table states including the elements on the table, shared deck and each player\'s hand and piles.\nThis option should be execute on the a game host.'
		, ['I am the Host!', 'I am not...'], ['#dd3737', '#d0d0d0']):
		return
	
	if not getLock():
		whisper("Others players are saving, please try manual saving again")
		return
	
	try:
		tab = {"table":[], "shared": {}, 'counters': None, "players": None}
		
		# loop and retrieve cards from the table
		for card in table:
			tab['table'].append(serializeCard(card))
		
		# loop and retrieve item from the shared decks
		for p in shared.piles :
			if p == 'Trash':
				continue
			for card in shared.piles[p]:
				if p not in tab['shared']:
					tab['shared'].update({p: []})
				tab['shared'][p].append(serializeCard(card))
				
		tab['counters'] = serializeCounters(shared.counters)
		
		# loop each player
		players = sorted(getPlayers(), key=lambda x: x._id, reverse=False)
		tab['players'] = [serializePlayer(pl) for pl in players]
	
		dir = wd('table-state-{}.json'.format('{:%Y%m%d%H%M%S}'.format(dt.now())))
		if 'GameDatabase' in dir:
			filename = dir.replace('GameDatabase','Decks').replace('a6d114c7-2e2a-4896-ad8c-0330605c90bf','Arkham Horror - The Card Game')
		else:
			filename = "Decks\Arkham Horror - The Card Game".join(dir.rsplit('OCTGN',1))
		
		filename = askString('Please input the path to save the game state', filename)
		
		if filename == None:
			return
		
		with open(filename, 'w+') as f:
			f.write(json().Serialize(tab))
		
		notify("Table state saves to {}".format(filename))
	finally:
		clearLock()

def loadTable(group, x=0, y=0):
	mute()
	
	if 1 != askChoice('You are about to LOAD the table states including the elements on the table, shared deck and each player\'s hand and piles.\nThis option should be execute on the a game host.'
		, ['I am the Host!', 'I am not...'], ['#dd3737', '#d0d0d0']):
		return
	
	if not getLock():
		whisper("Others players are locking the table, please try again")
		return
	
	try:
		dir = wd('table-state.json')
		if 'GameDatabase' in dir:
			filename = dir.replace('GameDatabase','Decks').replace('a6d114c7-2e2a-4896-ad8c-0330605c90bf','Arkham Horror - The Card Game')
		else:
			filename = "Decks\Arkham Horror - The Card Game".join(dir.rsplit('OCTGN',1))

		filename = askString('Please provide the file path to load the table states', filename)
		
		if filename == None:
			return
		
		with open(filename, 'r') as f:
			tab = json().DeserializeObject(f.read())
		
		deserializeTable(tab['table'])
		
		if tab['counters'] is not None and len(tab['counters']) > 0:
			deserializeCounters(tab['counters'], shared)
		
		if tab['shared'] is not None and len(tab['shared']) > 0:
			for k in tab['shared'].Keys:
				if k not in shared.piles:
					continue
				deserializePile(tab['shared'][k], shared.piles[k])
		
		if tab['counters'] is not None and len(tab['counters']) > 0:
			deserializeCounters(tab['counters'], shared)

		if tab['players'] is not None and len(tab['players']) > 0:
			for player in tab['players']:
				deserializePlayer(player)

		notify("Successfully load table state from {}".format(filename))
	finally:
		clearLock()

def saveDeck(group, x=0, y=0):
	mute()
	
	if not getLock():
		whisper("Others players are saving, please try manual saving again")
		return

	try:
		suffix = '{:%Y%m%d%H%M%S}'.format(dt.now())
		suffix = askString('Please provide a filename suffix (e.g. current scenerio name)', suffix)
		if suffix == None:
			whisper("Failed to save deck, missing file suffix")
			return
		
		investigators = {}
		lookForInvestigator(table, investigators)
		
		for pl in getPlayers():
			lookForInvestigator(pl.hand, investigators)
		
		if len(investigators) == 0:
			whisper("No investigators you are controlling, save is cancelled")
			return
			
		for key in investigators:
			savePlayerDeck(me, investigators[key], suffix)
	finally:
		clearLock()

def lookForInvestigator(cardList, investigators):
	for card in cardList:
		if card.owner == me:
			if card.Type == 'Investigator':
				if card.name not in investigators:
					investigators.update({card.name:[]})
				investigators[card.name].append(card)
			if card.Type == 'Mini':
				if card.name not in investigators:
					investigators.update({card.name:[]})
				investigators[card.name].append(card)

#Save the player deck - it is named after the character 	
def savePlayerDeck(player, invCards, suffix): #me.hand or table
	sections = { p : {} for p in PLAYER_DECK}

	#Add in the character sheet card (from the table)
	investigator = None
	for card in invCards:
		investigator = card
		sections["Investigator"][(card.name, card.model)] = 1
	
	if investigator is None:
		whisper("Failed to find investigator to save")
		return

	piles = [ me.piles[p] for p in me.piles if p != 'Basic Weaknesses']
	piles.append(me.hand)
	filename = savePiles('{}-saved-{}.o8d'.format("".join(c for c in investigator.name if c not in ('!','.',':', '"', "'")), suffix), sections, piles, True, False)
	if filename is None:
		whisper("Failed to save deck")
	else:
		notify("{} saves deck to {}".format(me, filename))

# Generic deck saver
# Loops through the piles and count how many cards there are of each type in each section
# Calls the routine getSection (passed as a parameter) to determine which section a card should be stored in	
def savePiles(name, sections, piles, skipInvestigator, isShared):
	for p in piles:
		if len(p) > 0:
			for card in p:
				s = getSection(sections, card)
				if s is None:
					continue
				if skipInvestigator and s == 'Investigator':
					continue
				if (card.name, card.model) in sections[s]:
					sections[s][(card.name, card.model)] += 1
				else:
					sections[s][(card.name, card.model)] = 1
	dir = wd(name)
	if 'GameDatabase' in dir:
		filename = dir.replace('GameDatabase','Decks').replace('a6d114c7-2e2a-4896-ad8c-0330605c90bf','Arkham Horror - The Card Game')
	else:
		filename = "Decks\Arkham Horror - The Card Game".join(dir.rsplit('OCTGN',1))
	with open(filename, 'w+') as f:
		f.write('<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n')
		f.write('<deck game="a6d114c7-2e2a-4896-ad8c-0330605c90bf">\n')
		for s in sections:
			if len(sections[s]) > 0:
				f.write(" <section name=\"{}\" shared=\"{}\">\n".format(s, isShared))
				count = 0
				for t in sorted(sections[s].keys()):
					#whisper("  <card qty=\"{}\" id=\"{}\">{}</card>\n".format(sections[s][t], t[1], t[0]))
					f.write("  <card qty=\"{}\" id=\"{}\">{}</card>\n".format(sections[s][t], t[1], t[0]))
					count += sections[s][t]
				f.write(" </section>\n")
				#whisper("{} - {}".format(s, count))
		f.write("</deck>\n")
		return filename
	return None