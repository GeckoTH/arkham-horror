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
        ],
        "path_to_carcosa": [
            "6c7f104b-f07c-423e-b221-5218affead2b", # 2x Overzealous
            "6c7f104b-f07c-423e-b221-5218affead2b",
            "d73c20b0-f661-4d33-a932-9db730708916", # Drawing the Sign
            "74c2e15a-6d3b-42d1-8c07-e9330d50bc43", # The Thing That Follows
        ],
        "the_forgotten_age": [
            "d2a6e29c-05d8-44d1-8359-87eee3f68597", # Dark Pact
            "14254816-3365-4c12-bb9f-02ba35920333", # Doomed
        ],
        "return_to_dunwich_legacy": [
            "49b96c05-175b-4727-b9d0-8bbfdc22d608", # x2 Through the Gates
            "49b96c05-175b-4727-b9d0-8bbfdc22d608",
        ],
        "the_circle_undone": [
            "479a3456-8e6c-4df7-a778-dad99d0a0f9d", # x2 The Thirteenth Vision
            "479a3456-8e6c-4df7-a778-dad99d0a0f9d",
            "46163897-b6a8-4c6e-86ef-27c5eeb7f443", # x2 The Tower XVI
            "46163897-b6a8-4c6e-86ef-27c5eeb7f443",
        ],
        "return_to_the_path_to_carcosa": [
            "58a1eddf-4958-4e7f-aea0-30c045452688", # Unspeakable Oath (Bloodthirst)
            "3a95f99d-79f5-45d3-b1e9-f1bd0159e116", # Unspeakable Oath (Curiosity)
            "83f6bbac-9c75-444b-b923-afed2c67532f", # Unspeakable Oath (Cowardice)
        ],
        "the_dream-eaters": [
            "600c6b88-339f-4f10-98b3-02536aec7b92", # Self-Centered
            "1e1b819a-4bc3-4954-bea4-752fce9858bc", # Kleptomania
            "97a9fa53-3c9e-444e-9c21-24e52354ed6c", # Narcolepsy
            "2ecb16b4-a4db-4832-8e78-d3527b8c1bd6", # Your Worst Nightmare
        ],
        "investigator_starter_decks": [
            "2f20aca0-a61a-4623-9d6d-4825fe73aa26", # Self-Destructive
            "ab48b372-c8d2-4c3e-b97d-5bdd42e78b27", # Obsessive
            "76f173ef-2c26-4d7e-b55e-2d1a27a77793", # Reckless
            "21e8b71b-751c-461a-8514-e001d1ed5bda", # Nihilism
            "c1464011-1ebf-48b9-b1c1-291b8fc7b4cf", # Atychiphobia
        ],
        "return_to_the_forgotten_age": [
            "d5591fb8-20d3-4a01-899e-147edb197e89", # Dendromorphosis
            "8513832c-d3d7-4f95-a829-1ea3eab40ebe", # Offer You Cannot Refuse
        ],
        "the_innsmouth_conspiracy": [
            "652a06aa-92ac-45d2-a07f-dcbad6e92e12", # x2 Accursed Follower
            "652a06aa-92ac-45d2-a07f-dcbad6e92e12",
            "fd0e9977-6338-4fa5-836f-74271d423ccf", # x2 Dread Curse
            "fd0e9977-6338-4fa5-836f-74271d423ccf",
            "b455d3cc-34f7-4a7c-8e02-179088edb6e3", # Day of Reckoning
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
