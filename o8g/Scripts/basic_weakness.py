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
        ],
        "dunwich_legacy": [
            "1ecf4d84-da04-4c69-8fac-aa11bdc4171f", # 2x Indebted
            "1ecf4d84-da04-4c69-8fac-aa11bdc4171f",
            "ee9ed7fb-bd73-4a10-88ce-0617321ebecd", # 2x Internal Injury
            "ee9ed7fb-bd73-4a10-88ce-0617321ebecd",
            "bd089e8f-e3f0-4fd3-9bf2-e7de8832da73", # 2x Chronophobia
            "bd089e8f-e3f0-4fd3-9bf2-e7de8832da73",
        ]
    }
    PILE_NAME = 'Basic Weaknesses'
    SUBTYPE_NAME = 'Basic Weakness'

    def __init__(self, player, sets = "all"):
        self.player = player
        self.cards = self._build_deck(sets)

    # based on the known Basic Weaknesses guids, construct the deck
    def create_deck(self):
        for guid in self.cards:
            card = self.player.piles[self.PILE_NAME].create(guid)

    # build a set of guids of Basic Weaknesses removing ones already in use by the player
    # pass in the list of sets of Basic Weaknesses to include
    def _build_deck(self, sets):
        deck = []
        used = self._used_weaknesses()

        if sets == "all":
            for name, cards in self.CARDS.iteritems():
                deck += cards
        else:
            for cards in (cards for name, cards in self.CARDS.iteritems() if name in sets):
                deck += cards

        for card in used:
            face_up = card.isFaceUp
            # peek() doesn't seem to be working
            if not card.isFaceUp:
                card.isFaceUp = True

            dupe = next((dupe for dupe in deck if dupe == card.model), None)
            if dupe:
                deck.remove(dupe)

            if not face_up:
                card.isFaceUp = face_up

        return deck

    # check for weaknesses already taken and remove them
    def _used_weaknesses(self):
        table_cards = [card for card in table
                       if card.controller == self.player]
        discard_cards = [card for card in self.player.piles['Discard Pile']]
        deck_cards = [card for card in self.player.piles['Deck']]
        hand_cards = [card for card in self.player.hand]
        return [card for card in table_cards + discard_cards + deck_cards + hand_cards
                if card.Subtype == self.SUBTYPE_NAME]
