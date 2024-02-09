#!/usr/bin/env python
# -*- coding: utf-8 -*-

def addBless(group=None, x=0, y=0):
    addBlessCurse(group, True)

def addCurse(group=None, x=0, y=0):
    addBlessCurse(group, False)

def removeBless(group=None, x=0, y=0):
    removeBlessCurse(group, True)

def removeCurse(group=None, x=0, y=0):
    removeBlessCurse(group, False)

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

def sealXBless(card, max = None):
    mute()
    if blessInCB() > 0 and card.markers[Bless] == 0: 
        count = askInteger("Seal how many Bless tokens from the chaos bag?", 5)
        if count is None or count <= 0 or count > blessInCB():
            whisper("Invalid Count")
            return
        if max and count > max:
            whisper("Invalid Count")
            return
        inc = 0
        notify("{} uses {} to seal {} Bless tokens".format(card.owner, card, count))
        card.markers[Bless] = count
        for t in shared.piles['Chaos Bag']:
            if t.Name != "Bless":
                continue
            if t.controller == me:
                doDiscard(me, t, chaosBag())
            else:
                remoteCall(t.controller, "doDiscard", [me, t, chaosBag()])
            inc += 1
            if inc == count:
                break
        updateBlessCurse()
        card.Subtype = "Locked"
    else: whisper("Not enough Bless tokens")
        
def sealXCurse(card, max = None):
    mute()
    if curseInCB() > 0 and card.markers[Curse] == 0: 
        count = askInteger("Seal how many Curse tokens from the chaos bag?", 5)
        if count is None or count <= 0 or count > curseInCB():
            whisper("Invalid Count")
            return
        if max and count > max:
            whisper("Invalid Count")
            return
        inc = 0
        notify("{} uses {} to seal {} Curse tokens".format(card.owner, card, count))
        card.markers[Curse] = count
        for t in shared.piles['Chaos Bag']:
            if t.Name != "Curse":
                continue
            if t.controller == me:
                doDiscard(me, t, chaosBag())
            else:
                remoteCall(t.controller, "doDiscard", [me, t, chaosBag()])
            inc += 1
            if inc == count:
                break
        updateBlessCurse()
        card.Subtype = "Locked"
    else: whisper("Not enough Curse tokens")

def countBless():
    mute() 
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
    mute()
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
    mute()
    b = 0
    for t in shared.piles['Chaos Bag']:
        if t.Name == "Bless":
            b += 1
    return b

def curseInCB():
    mute()
    c = 0
    for t in shared.piles['Chaos Bag']:
        if t.Name == "Curse":
            c += 1
    return c

def blessOnTable(): # For Nephthys automation
    mute()
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



def removeBlessCurse(group, isBless, who=me):
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
    if (countBless() == 0 and isBless) or ((countCurse() == 0) and not isBless):
        notify("There must be a Bless or Curse token in the chaos bag before it can be removed.")
        return

    if isBless:
        subToken(cb, Bless)
        for t in chaosBag():
            if t.Name == "Bless":
                t.delete()
                break
    else:
        subToken(cb, Curse)
        for t in chaosBag():
            if t.Name == "Curse":
                t.delete()
                break

    chaosBag().shuffle()
    updateBlessCurse()
