Bonded = [
#1 card = 3 bonded
    {"sourceCard":"Hallowed Mirror","bondedCard":"Soothing Melody x3","bondedCode":["13901510-7669-4e5c-ac27-71646b359818","13901510-7669-4e5c-ac27-71646b359818","13901510-7669-4e5c-ac27-71646b359818"]},
    {"sourceCard":"Occult Lexicon","bondedCard":"Blood-Rite x3","bondedCode":["d0f4baa1-b066-47a0-a43f-9160efe57818","d0f4baa1-b066-47a0-a43f-9160efe57818","d0f4baa1-b066-47a0-a43f-9160efe57818"]},
    {"sourceCard":"The Hungering Blade","bondedCard":"Bloodlust x3","bondedCode":["e3011174-2b79-4108-855a-ff1d2bbe8b08","e3011174-2b79-4108-855a-ff1d2bbe8b08","e3011174-2b79-4108-855a-ff1d2bbe8b08"]},
    {"sourceCard":"Nightmare Bauble","bondedCard":"Dream Parasite x3","bondedCode":["c5cb7f4a-968f-484c-860d-c8fcef53014b","c5cb7f4a-968f-484c-860d-c8fcef53014b","c5cb7f4a-968f-484c-860d-c8fcef53014b"]},
    {"sourceCard":"Miss Doyle","bondedCard":"Hope,Zeal,Augur","bondedCode":["9440540e-4099-44c4-b999-e967418b6a65","03c6452b-0fec-4a36-a460-7cf77fae1c55","61dba09d-09af-4b1e-932e-7f6cbb9df9fa"]},
    #1 source card = 1 bonded card
    {"sourceCard":"Gate Box","bondedCard":"Dream-Gate","bondedCode":["3330e3db-e28a-4901-a3bd-077c7aceeb7f"]},
    {"sourceCard":"Crystallizer of Dreams","bondedCard":"Guardian of the Crystallizer ","bondedCode":["fdc478bd-9fd5-4f4a-8af1-5531118133d3"]}, 
    {"sourceCard":"Empty Vessel","bondedCard":"Wish Eater","bondedCode":["cc7a738c-f3dd-4871-a929-6fedf37cb854"]},
    {"sourceCard":"Stargazing","bondedCard":"The Stars Are Right","bondedCode":["a5a49067-7af2-48bd-9389-f2a45e0dded8"]},
    {"sourceCard":"Summoned Hound","bondedCard":"Unbound Beast","bondedCode":["f03e3511-0a6c-4a83-8de9-2dda716d7775"]},
    #X source card = 1 bonded card
    {"sourceCard":"Dream Diary","bondedCard":"Essence of the Dream","bondedCode":["0481911c-f906-40ee-acef-d4ad39c2d767"]},
    {"sourceCard":"Segment of Onyx","bondedCard":"Pendant of the Queen","bondedCode":["dc7600e3-a132-42b0-b96b-67ca0cee4aff"]}
    ]

limitedOneBondedCode =[
    "0481911c-f906-40ee-acef-d4ad39c2d767",
    "dc7600e3-a132-42b0-b96b-67ca0cee4aff"
    ]

#Special Case Only 1 Version of Dream Diary have bonded card
DreamDiary = {"name" : "Dream Diary", "subtitle" : "Untranslated"}

def makeListBonded(deck):
    mute()
    listBonded = []
    for deckcard in deck:
        for dic in Bonded:
            if dic["sourceCard"] == deckcard.Name:
                #Filter Dream Diary with wrong subtitle
                if deckcard.Name == DreamDiary["name"] and deckcard.Subtitle != DreamDiary["subtitle"]:
                    continue              
                listBonded.extend(dic["bondedCode"])
    #Remove useless multiple bonded card and add only 1 bonded card
    for idOne in limitedOneBondedCode:
        if idOne in listBonded:
            listBonded = filter(lambda card: card != idOne, listBonded)
            listBonded.append(idOne)
    return listBonded
    