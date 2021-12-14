#!/usr/bin/env python
# -*- coding: utf-8 -*-

def addBless(group=None, x=0, y=0):
    addBlessCurse(group, True)

def addCurse(group=None, x=0, y=0):
    addBlessCurse(group, False)

def updateBlessCurse():
    c = 0
    b = 0
    for t in chaosBag():
        if t.Name == "Bless":
            b += 1
        elif t.Name == "Curse":
            c += 1
    cb = None
    for card in table:
        if card.name != "ChaosBag":
            continue
        cb = card
        break
    if (cb == None): return
    cb.markers[Curse] = c
    cb.markers[Bless] = b

def countBless(): 
    if len(shared.piles['Chaos Bag']) == 0:
        return
    b = 0
    for t in table:
        if t.Name == "Bless":
            b += 1
        if t.markers[Bless] > 0:
            b += t.markers[Bless]
    return b

def countCurse():
    if len(shared.piles['Chaos Bag']) == 0:
        return
    c = 0
    for t in table:
        if t.Name == "Curse":
            c += 1
        if t.markers[Curse] > 0:
            c += t.markers[Curse]
    return c

def blessInCB(): # For Holy Spear automation
    b = 0
    for t in shared.piles['Chaos Bag']:
        if t.Name == "Bless":
            b += 1
    return b

def blessOnTable(): # For Nephthys automation
    b = 0
    for t in table:
        if t.Name == "Bless" and t.Type != "Sealed":
            b += 1
    return b

def addBlessCurse(group, isBless, who=me):
    mute()
    if chaosBag().controller != me:
        remoteCall(chaosBag().controller, "addBlessCurse", [group, isBless, me])
        return

    #Find ChaosBag
    cb = None
    for card in table:
        if card.name != "ChaosBag":
            continue
        cb = card
        break

    if cb == None:
        notify("You need a Chaos Bag first.")
        return

    #check current Tokens in Bag
    if (countBless() >= 10 and isBless) or ((countCurse() >= 10) and not isBless):
        notify("There are only 10 Bless and Curse tokens each allowed.")
        return

    if isBless:
        token = table.create(BlessID, 0, 0, 1, True)
        addToken(cb, Bless)
    else:
        token = table.create(CurseID, 0, 0, 1, True)
        addToken(cb, Curse)

    token.Subtype = "Blurse"
    token.moveTo(chaosBag())
    chaosBag().shuffle()
    updateBlessCurse()