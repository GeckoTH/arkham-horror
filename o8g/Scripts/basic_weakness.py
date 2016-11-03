class BasicWeakness:
    CARDS = {
        "core": [
            "9ca5f0a3-e74f-4068-bf67-9fe003cf17c0", # 2 x Paranoia,
            "9ca5f0a3-e74f-4068-bf67-9fe003cf17c0",
            "8398d095-9e12-45dd-8242-838ed636ba1d", # 2 x Amnesia,
            "8398d095-9e12-45dd-8242-838ed636ba1d",
            "76d61a65-4c3a-486c-b507-c4b0a109d65f", # Haunted
            "f8c80be5-04a4-4546-8d16-6d6c6a0d21ec", # Psychosis
            "5f5c0fc7-34ce-45ce-a609-f2b4f4fc6e5a", # Hypochondria
            "22a5a1f6-cc50-47a9-9374-76204c97cf0a", # Mob Enforcer
            "9b1de9f2-b050-41c4-bfdc-16a40974a3fb", # Silver Twilight Acolyte
            "d5b68cab-54f1-488c-ba9f-68d8830cf2d0", # Stubborn Detective
        ]
    }

    @classmethod
    def draw(cls, sets = "all"):
        picked_weaknesses = []

        if sets == "all":
            for name, cards in cls.CARDS.iteritems():
                picked_weaknesses += cards
        else:
            for cards in (cards for name, cards in cls.CARDS.iteritems() if name in sets):
                picked_weaknesses += cards

        return picked_weaknesses[rnd(0, len(picked_weaknesses) - 1)]