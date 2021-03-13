def setupHelper():
    #Look for Scenario cards
    cards = []
    for c in setupDeck():
        if c.Type == "Scenario":
            cards.append(c)

    s = cards[0].model
    if s == '0d7300da-ddb1-4d9b-81b0-ceab0a459f54': #Black Stars Rise
        stacks = [['fada603a-e868-4c93-9ada-1a2d61e9b43c','6b5e4477-4b8f-4913-b799-1d2e2b497f6c',
                   'ee818778-2024-4969-b030-0e5855802f96','2caaba71-47a4-4c07-b60f-298b7a9d7e87'],
                  ['255c32f0-5c83-41c1-adb6-50c0dddc5fb7','a4ad2173-5ec7-44ea-af72-a00d99a072bb',
                   'e5af2b0f-1c64-4419-bc1d-4f6b49b027fb','330ea796-9967-4d58-9331-c52a88235d66']]
        r = rnd(0,1)
        if r:
            use = stacks[1]
            rm = stacks[0]
        else:
            use = stacks[0]
            rm = stacks[1]

        for c in setupDeck():
            if c.model in rm:
                c.delete()
            elif c.model in use and c.Type == "Agenda":
                if c.name == "Let The Storm Rage":
                    c.moveTo(agendaDeck(), 1)
                else:
                    c.moveTo(actDeck(), 1)

    elif s == '3e01c1d4-8e5c-472b-b803-357c6474ca01': #Threads of Fate
        ab = [['c8d55c59-96cd-438b-afaa-366bfe19730c','896613e6-b4a2-488a-8460-929df1a72bf4'],
              ['c6b3c676-8d25-46d4-a43c-898324bbd6e0','d2aff041-a1f8-4b31-a630-651661ac22fc'],
              ['da71f372-8c2b-4616-aae2-008483386f6a','da71f372-8c2b-4616-aae2-008483386f6a'],
              ['71fc4500-eaf7-43b1-b6b4-165248055cdf','aa707a76-33be-4960-9a91-ce58e22b7728']]

        a = askChoice("Check Campaign Log",
                      ["Alejandro recovered the Relic of Ages","The investigators gave custody of the relic to Alejandro","The investigators gave custody of the relic to Harlan Earnstone"],
                      ["#000000","#000000","#000000"])
        if not a:
            return
        if a < 3:
            a = 0
        else:
            a = 1

        r = rnd(0,1)
        for c in actDeck():
            if c.model == ab[0][a] or c.model in ab[a+1]:
                c.delete()
            if a and c.model == ab[1][r]:
                c.delete
            if not a and c.model == ab[2][r]:
                c.delete
            if c.model == ab[3][r]:
                c.delete

        cd = [['7a75e4c5-445e-4159-925f-957163e47e29','1a414a99-25cc-4ec4-8463-c7301a87e6e9'],
              ['a5a42d27-9725-4218-b8d3-eccb2523cd7c','4d53700c-093c-40fe-8019-4f88be99fe4e'],
              ['c18e7c75-2d45-4e81-9df6-2d4a738c0992','10a58a3d-9813-4947-8737-88f77b3e7a9a'],
              ['a67d45ac-5e24-4742-878c-4a5abab74085','7dbfd611-3f62-4dca-ad0d-2613b1ce58a7']]

        a = askChoice("Choose one",
                      ["Go to the Police to inform them about Alejandro's disappearance","Look for Alejandro on your own"],
                      ["#000000","#000000"])
        if not a:
            return
        a -= 1
        r = rnd(0,1)
        for c in actDeck():
            if c.model == cd[0][a] or c.model in cd[a+1]:
                c.delete()
            if a and c.model == cd[1][r]:
                c.delete
            if not a and c.model == cd[2][r]:
                c.delete
            if c.model == cd[3][r]:
                c.delete

        ef = [['9055bfa1-1073-4150-8106-3a7de023f891','219d4017-96f6-4196-a72b-18330def361a'],
              ['1e0e7df5-4c67-42e4-b1c6-74f4805da1fd','dfd302e9-57ac-44ae-a817-54d195dc167f'],
              ['74372f0c-0743-4e05-a8bc-18502b57c988','9ce3c434-b63a-42d7-b986-4f502bbd5c52'],
              ['41c0621d-986b-454f-983a-868dc9d21330','e5189103-fa67-4b13-8d55-673260fa4d8a']]

        a = askChoice("Ichtaca's tale",
                      ["You listened to Ichtaca's tale","Ichtaca left without you"],
                      ["#000000","#000000"])
        if not a:
            return
        a -= 1
        r = rnd(0,1)
        for c in actDeck():
            if c.model == ef[0][a] or c.model in ef[a+1]:
                c.delete()
            if a and c.model == ef[1][r]:
                c.delete
            if not a and c.model == ef[2][r]:
                c.delete
            if c.model == ef[3][r]:
                c.delete

        if len(cards) == 1:
            return #no Return To
        #Otherwise we are playing Return to Threads
        gh = [['3faf9ca8-2d4a-4327-b365-2332cbf76401','6986f0ca-fc8e-420e-ae92-6410fab73785'],
              ['33b24489-91a6-4eae-9164-082b357abd14','24bf56dc-3b0f-45db-b633-6428a5ffd784'],
              ['af6113e6-6f03-4685-824f-11016b51b50f','2ac2cfc8-aa2b-406b-a950-1a273d7cb1cf'],
              ['0d36127e-b441-4f49-af22-7bf13aaa0253','9b2376a8-7317-4652-9f61-ff31c7d15e0b']]

        a = askChoice("Choose one",
                      ["Find the Source named in the Advertiser's story","Find the root of the problem"],
                      ["#000000","#000000"])
        if not a:
            return
        a -= 1
        r = rnd(0,1)
        for c in actDeck():
            if c.model == gh[0][a] or c.model in gh[a+1]:
                c.delete()
            if a and c.model == gh[1][r]:
                c.delete
            if not a and c.model == gh[2][r]:
                c.delete
            if c.model == gh[3][r]:
                c.delete
                
        
