
# # # NOU CARDGAME

# NOU PERSISTENT VARS
default persistent._mas_game_nou_points = {"Monika": 0, "Player": 0}
default persistent._mas_game_nou_wins = {"Monika": 0, "Player": 0}
default persistent._mas_game_nou_abandoned = 0
default persistent._mas_game_nou_house_rules = {
    "points_to_win": 200,
    "starting_cards": 7,
    "stackable_d2": False,
    "unrestricted_wd4": False
}

# FIXME: make persistent.ever_won a defaultdict instead
init 10 python:
    if "nou" not in persistent.ever_won:
        persistent.ever_won["nou"] = False

# NOU CLASS DEF
init 5 python in mas_nou:
    from store import m, persistent, Solid
    from store.mas_cardgames import *

    ASSETS = "mod_assets/games/nou/"

    # stats for curr sesh
    player_wins_this_sesh = 0
    monika_wins_this_sesh = 0

    player_win_streak = 0
    monika_win_streak = 0

    # are we playing a round or not
    in_progress = False

    # Last winner
    # NOTE: if this isn't None, then we played in this sesh
    winner = None

    # we allow to press these buttons only once per turn
    # and disable them 'til next one
    disable_remind_button = False
    disable_yell_button = False

    class NoU(object):
        """
        A class to represent a shedding card game - NoU
        Total cards in the deck: 108
        The one who first gets rid of cards wins the round
        The one who first reaches the points cap (default 200) wins the game
        One game takes about 5-10 minutes, you keep your points through sessions
            so you can start the game in one sesh and finish it later if you wish
        """
        # These constants represent parameters for nou cards
        TYPES = ("number", "action", "wild")
        NUMBER_LABELS = ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9")
        ACTION_LABELS = ("Skip", "Draw Two", "Reverse")
        WILD_LABELS = ("Wild", "Wild Draw Four")
        COLORS = ("red", "blue", "green", "yellow")

        # Coordinates
        DRAWPILE_X = 465
        DRAWPILE_Y = 352
        DISCARDPILE_X = 830
        DISCARDPILE_Y = 352
        PLAYERHAND_X = 640
        PLAYERHAND_Y = 595
        MONIKAHAND_X = PLAYERHAND_X
        MONIKAHAND_Y = 110
        PLAYER_CARDS_OFFSET = 0
        MONIKA_CARDS_OFFSET = -6

        # Maximum cards in hand
        HAND_CARDS_LIMIT = 30

        # # # Monika's quips

        # Quips for when we get a wdf as the first card for the discardpile
        QUIPS_MONIKA_RESHUFFLE_DECK = (
            _("Oh, let me shuffle it again.{w=1.5}{nw}"),
            _("Oops, let's try again.{w=1.5}{nw}"),
            _("I doubt we want a plus four as the first card, ahaha~{w=1.5}{nw}"),
            _("No, no, no... Let's shuffle again...{w=1.5}{nw}")
        )

        # Quips that Monika can say at the start of each round
        QUIPS_MONIKA_PLAYS_TURN = (
            _("Oh, it's my turn."),
            _("My turn~"),
            _("I'm playing first~")
        )
        QUIPS_MONIKA_SKIPS_TURN = (
            _("Oh, I have to skip my turn."),
            _("Lucky you, I'll have to skip this turn."),
            _("Aww, I'll have to skip my turn.")
        )
        QUIPS_MONIKA_DRAWS_CARDS = (
            _("Oh, I must draw some more."),
            _("Lucky you, I'll give you a handicap with these cards."),
            _("Gosh, even more cards for me..."),
            _("Oh, guess I'll have to draw more cards.")
        )
        QUIPS_MONIKA_WILL_REFLECT = (
            _("I prepared! Ehehe~"),
            _("No, no, no~ I'm not going to skip this turn!"),
            _("Nope! This time you'll skip a turn~"),
            _("Lucky me I have some good cards! Ehehe~"),
            _("I was ready~")
        )

        QUIPS_PLAYER_PLAYS_TURN = (
            _("It's your turn, honey~"),
            _("You're playing first."),
            _("Your turn, [player].")
        )
        QUIPS_PLAYER_SKIPS_TURN = (
            _("Whoops! You have to skip your turn."),
            _("Unlucky!")
        )
        QUIPS_PLAYER_DRAWS_CARDS = (
            _("Go ahead and draw your cards, ehehe~"),
            _("Oops, you must draw more cards.")
        )

        # Quips if you pervert are trying to touch her hand
        # NOTE: would be nice to have a pm var for cheaters, but this should work too
        if not persistent._mas_chess_skip_file_checks:
            QUIPS_PLAYER_CLICKS_MONIKA_CARDS = [
                _("[player], these are my cards!"),
                _("I see what you're doing, [player]~"),
                _("This is a little embarrassing~"),
                _("Ah?{w=0.2} What are you trying to do?~")
            ]
            if persistent._mas_affection["affection"] >= 400:
                QUIPS_PLAYER_CLICKS_MONIKA_CARDS.append(
                    _("With you I wouldn't mind doing that for real, [player]~")
                )

            else:
                QUIPS_PLAYER_CLICKS_MONIKA_CARDS.append(
                    _("I don't think we're already {i}that{/i} far in our relationship~")
                )

        else:
            QUIPS_PLAYER_CLICKS_MONIKA_CARDS = (_("Are you trying to cheat again?"),)

        # Quips when you reach the cards limit
        QUIPS_MONIKA_CARDS_LIMIT = (
            _("[player]...{w=0.2}look I can't hold all these cards!{w=0.5} And I can't draw more either, ehehe~"),
        )
        QUIPS_PLAYER_CARDS_LIMIT = (
            _("There's no way you could hold more cards, ahaha!{w=0.5} You don't have to draw more this turn, [player]."),
        )

        # Quips when Monika chooses a color to set
        # Quips for when she gets a wild card on the first turn
        QUIPS_MONIKA_ANNOUNCE_COLOR_FIRST_TURN = (
            _("I think I'll go.{w=0.2}.{w=0.2}.{w=0.2}[store.mas_nou.game.monika.chosen_color]!"),
            _("I want [store.mas_nou.game.monika.chosen_color]."),
            _("I choose [store.mas_nou.game.monika.chosen_color]."),
            _("Hmm.{w=0.2}.{w=0.2}.{w=0.2}I choose [store.mas_nou.game.monika.chosen_color]!")
        )
        # Quips for when she reflects a wild card
        QUIPS_MONIKA_ANNOUNCE_COLOR_AFTER_REFLECT = (
            _("I'd prefer [store.mas_nou.game.monika.chosen_color] color~"),
            _("I want [store.mas_nou.game.monika.chosen_color] color~"),
            _("I choose [store.mas_nou.game.monika.chosen_color] color!"),
            _("It'll be [store.mas_nou.game.monika.chosen_color]!")
        )

        # NoU quips
        # Quips when Monika says NOU
        QUIPS_MONIKA_YELLS_NOU = (
            _("NOU, [player]!"),
            _("I have only one card left, [player]! NOU!"),
            _("NOU! Keep up, [player]!~"),
            _("NOU, [player], ehehe~"),
            _("NOU, [player]~"),
            _("NOU~"),
            _("Just one card left! NOU, [player]~"),
            _("Ehehe~ No.{w=0.2}.{w=0.2}.{w=0.2}U!"),
            _("NOU!")
        )
        # Quips when you ask her to yell NoU, but she already did it
        QUIPS_MONIKA_ALREADY_YELLED_NOU = (
            _("But [player], I've said 'NOU'!"),
            _("I've already said 'NOU,' [player]!"),
            _("Silly, I already did that!~"),
            _("[player]... How did you miss that? I already said 'NOU!'"),
            _("Uh, [player]...{w=0.3} I already said 'NOU!'")
        )
        # Quips when you ask her to yell NoU, but she has more than 1 card
        QUIPS_MONIKA_DONT_NEED_YELL_NOU = (
            _("[player], but I have more than one card in my hands!"),
            _("Silly, you yell 'NOU' when you have only one card left!"),
            _("Ahaha~ A bit too early, [player]!"),
            _("It's not the time yet, [player]!"),
            _("[player], I have [len(store.mas_nou.game.monika.hand)] more cards to play!")
        )
        # Quips when the player tries to remind Monika about nou, but it's too late now
        QUIPS_MONIKA_TIMEDOUT_NOU = (
            _("Ehehe, too late, [player]!"),
            _("You're too late, [player]!"),
            _("You should've done that before playing your turn!~"),
            _("It's too late now that you've started playing your turn!~"),
            _("Too late, [player]! This time I can get away for free~")
        )
        # Quips when Monika forgot to say nou
        QUIPS_MONIKA_FORGOT_YELL_NOU = (
            _("Oh... You're right!"),
            _("Whoops, you got me there!"),
            _("Jeez, how did I forget..."),
            _("Ehehe, completely unintentional~"),
            _("Ehehe, caught me!"),
            _("How silly of me! Ahaha!~")
        )
        # Quips when Monika said NoU, but didn't play a card
        # NOTE: THIS SHOULD NEVER HAPPEN, BUT WE HAVE THIS FALLBACK JUST IN CASE
        QUIPS_MONIKA_FALSE_NOU = (
            _("This is embarrassing...{w=0.5}I should've played a card, but forgot about it... {w=0.5}Sorry, [player]."),
        )

        # Quips when player said nou
        QUIPS_PLAYER_YELLS_NOU = (
            _("Gotcha!"),
            _("Alright!"),
            _("I see, I see..."),
            _("Okay, [player]...")
        )
        # Quips when the player repeats nou for no reason
        QUIPS_PLAYER_ALREADY_YELLED_NOU = (
            _("Ahaha, I got it, [player]!"),
            _("You've already said it, silly~"),
            _("I heard you, [player]!"),
            _("No need to repeat it each turn, silly~")
        )
        # Quips when the player says nou for no reason
        QUIPS_PLAYER_DONT_NEED_YELL_NOU = (
            _("Silly, you still have a lot of cards to play!"),
            _("Silly, you yell 'NOU' when you have only one card left!"),
            _("I think you still have more than one card, [player]."),
            _("You have too many cards to say 'NOU' now."),
            _("A bit early for yelling 'NOU,' [player]!"),
            _("You should say 'NOU' before playing your second last card, [player]."),
            _("[player], you can be so silly sometimes~")
        )
        # Quips when Monika catches you on not saying NoU
        QUIPS_PLAYER_FORGOT_YELL_NOU = (
            _("Aha!{w=0.3} You didn't say NOU, [player]!"),
            _("You forgot to say 'NOU,' [player]!"),
            _("You thought I wouldn't notice?~ You should've said 'NOU!'"),
            _("Certain someone who forgot to yell 'NOU' must draw 2 cards now~"),
            _("Guess who must take 2 cards for not saying 'NOU'~"),
            _("I caught you! You didn't say 'NOU!'"),
            _("You didn't say 'NOU!' And now you must take 2 cards!~")
        )
        # Quips when the player said nou, but didn't play a card afterwards
        QUIPS_PLAYER_FALSE_NOU = (
            _("You should say 'NOU' only if you're going to play a card, [player]."),
            _("Why didn't you play a card?"),
            _("Eh, [player]? You should play a card after saying 'NOU!'"),
            _("Don't say 'NOU' if you're not going to play a card."),
            _("[player], don't yell 'NOU' for no reason..."),
            _("[player], you can be so silly sometimes~")
        )

        ### Reactions maps

        # Reactions ids
        NO_REACTION = 0
        MONIKA_REFLECTED_ACT = 1
        PLAYER_REFLECTED_ACT = 2
        MONIKA_REFLECTED_WDF = 3
        PLAYER_REFLECTED_WDF = 4
        MONIKA_REFLECTED_WCC = 5
        PLAYER_REFLECTED_WCC = 6
        MONIKA_PLAYED_WILD = 7

        # Format: {seen_count: list of tuples with dlg lines to choose}
        # all the dlg lines are packed in tuples, this way we can iterate over them
        # and have multiple lines per reaction
        # we use lists since we may append additional lines

        # # # First, Monika's reactions

        # this is general map with lines we use in all reflect reactions
        REACTIONS_MAP_MONIKA_REFLECTED_CARD = {
            0: [
                (_("Nope!"),),
                (_("I don't think so, [player]~"),),
                (_("But were you ready for this, huh?"),)
            ],
            1: [
                (_("Still nope!"),),
                (_("Ehehe~ I was ready!"),),
                (_("Not this time, [player]!"),)
            ],
            2: [
                (_("I read you as an open book."), _("Ahaha~")),
                (_("I won't give up so easily~"),)
            ]
        }

        # this is for reflecting an action card
        REACTIONS_MAP_MONIKA_REFLECTED_ACT = {
            0: [
                (_("Thought you will catch me off guard with this?"), _("I knew you'll do it! Ehehe~")),
                (_("Not so easy, [player]~"),)
            ],
            1: [
                (_("Ehehe~ No way, [player]~"),),
                (_("You {i}really{/i} want me to take this, huh?~"),),
                (_("Wait a moment.{w=0.2}.{w=0.2}.{w=0.2}I have more for you~"),),
                (_("What about this one?~"),)
            ],
            2: [
                (_("Will you{w=0.2} still love me after this?~"), _("Ahaha~"))
            ]
        }

        # this is for reflecting a Wild Choose Color
        REACTIONS_MAP_MONIKA_REFLECTED_WCC = {
            0: [
                (_("Hmm...{w=0.5}I don't like this color~"),),
                (_("Sorry, [player] but..."), _("This isn't the color I want right now~")),
                (_("[store.mas_nou.game.discardpile[-1].color.capitalize()] isn't what I want now~"),)
            ],
            1: [
                (_("No-no-no!"),),
                (_("[player]...just let me choose the right color~"),)
            ],
            2: [
                (_("Ehehe~"), _("I have another in store!~"))
            ]
        }

        # this is for reflecting a Wild Draw 4
        REACTIONS_MAP_MONIKA_REFLECTED_WD4 = {
            0: list(REACTIONS_MAP_MONIKA_REFLECTED_ACT[0]) + list(REACTIONS_MAP_MONIKA_REFLECTED_WCC[0]),
            1: list(REACTIONS_MAP_MONIKA_REFLECTED_ACT[1]) + list(REACTIONS_MAP_MONIKA_REFLECTED_WCC[1]) + [
                (_("You can't reflect this!"),),
                (_("No way you can reflect this one!"),)
            ],
            2: list(REACTIONS_MAP_MONIKA_REFLECTED_ACT[2]) + list(REACTIONS_MAP_MONIKA_REFLECTED_WCC[2])
        }

        # now fill all of those with the base lines for reflecting a card
        for i in range(3):
            REACTIONS_MAP_MONIKA_REFLECTED_ACT[i] += list(REACTIONS_MAP_MONIKA_REFLECTED_CARD[i])
            REACTIONS_MAP_MONIKA_REFLECTED_WCC[i] += list(REACTIONS_MAP_MONIKA_REFLECTED_CARD[i])
            REACTIONS_MAP_MONIKA_REFLECTED_WD4[i] += list(REACTIONS_MAP_MONIKA_REFLECTED_CARD[i])

        # This is used when she chooses a color
        # It has only one key - 0 - because it doesn't make sense to keep track of series of this
        REACTIONS_MAP_MONIKA_PLAYED_WILD = {
            0: [
                (_("I think I'll set.{w=0.2}.{w=0.2}.{w=0.2}[store.mas_nou.game.monika.chosen_color] color!"),),
                (_("I want [store.mas_nou.game.monika.chosen_color] color."),),
                (_("I choose [store.mas_nou.game.monika.chosen_color] color."),),
                (_("Hmm.{w=0.1}.{w=0.1}.{w=0.1} I choose [store.mas_nou.game.monika.chosen_color]!"),)
            ]
        }

        # # # Modifiers for the reactions quips, which only apply under certain conditions

        # this modifier only works when you play with stackable cards
        # used for seen count 2
        REACTIONS_MAP_MONIKA_REFLECTED_ACT_MODIFIER_1 = [
            (_("That's a lot of cards for you, ehehe~"),)
        ]

        # this modifier used when Monika reflects a d2
        # used for seen count 0
        REACTIONS_MAP_MONIKA_REFLECTED_ACT_MODIFIER_2 = [
            (_("Ehehe~ I'm not going to draw all these cards!"),),
            (_("All these cards will suit you~"),)
        ]

        # this modifier used when Monika reflects a skip turn/reverse
        # used for seen count 0
        REACTIONS_MAP_MONIKA_REFLECTED_ACT_MODIFIER_3 = [
            (_("{i}No, you{/i} will skip this turn~"),),
            (_("Ahaha~"), _("Nope, [player]!")),
            (_("I think you're still going to skip this turn~"),)
        ]

        # this modifier only works when you play with stackable cards
        # used for seen count 2
        # (same as for d2)
        REACTIONS_MAP_MONIKA_REFLECTED_WD4_MODIFIER_1 = list(REACTIONS_MAP_MONIKA_REFLECTED_ACT_MODIFIER_1)

        # this modifier only works when Monika wants green color
        REACTIONS_MAP_MONIKA_REFLECTED_WCC_MODIFIER_1 = [
            (_("Just let me choose the best color~"),)
        ]

        # # # Now the player's reactions

        # again, general map for all reflects
        REACTIONS_MAP_PLAYER_REFLECTED_CARD = {
            0: [
                (_("Aww, I wasn't expecting this!"),),
                (_("Just once, [player]...once!~"),)
            ],
            1: [
                (_("Alright,{w=0.1} this time you won..."),),
                (_("I.{w=0.1}.{w=0.1}.{w=0.1}will let it slide...{w=0.3}but just this time!"),),
                (_("You're pretty lucky!"),)
            ],
            2: [
                (_("You...{w=0.3}could go a bit easier on your girlfriend~"), _("Ahaha~"))
            ]
        }

        # map for reflecting action cards
        REACTIONS_MAP_PLAYER_REFLECTED_ACT = {
            0: [
                (_("Aww, what a shame!"),),
                (_("That's unlucky!"),)
            ],
            1: [
                (_("Jeez, I can't believe you had another card!"),),
                (_("Jeez, you're really trying to win!"),),
                (_("Can't let it go, huh?"),)
            ],
            2: [
                (_("Oh my gosh!{w=0.2} How many of these do you have?!"),),
                (_("Ehehe~ I thought this was a simple game between lovers, not a competition..."), _("Guess I was wrong~"))
            ]
        }

        REACTIONS_MAP_PLAYER_REFLECTED_WCC = {
            0: [
                (_("Mmmm!"),),
                (_("Well{w=0.2}...so be it, [player]!"),)
            ],
            1: [
                (_("Alright, alright!~"), _("{i}This{/i} time you won~")),
                (_("Alright...{w=0.2}this time {i}you{/i} choose the color~"),)
            ],
            2: [
                (_("Oh jeez!"),)
            ]
        }

        REACTIONS_MAP_PLAYER_REFLECTED_WD4 = {
            0: list(REACTIONS_MAP_PLAYER_REFLECTED_ACT[0]) + list(REACTIONS_MAP_PLAYER_REFLECTED_WCC[0]) + [
                (_("Hmm, I wasn't prepared for this!"),),
                (_("Jeez!{w=0.2} How many of these do you have?!"),)
            ],
            1: list(REACTIONS_MAP_PLAYER_REFLECTED_ACT[1]) + list(REACTIONS_MAP_PLAYER_REFLECTED_WCC[1]) + [
                (_("I'll remember this~"), _("Watch out, [player]!~")),
                (_("Man, you've got a lot of plus 2's!"),)
            ],
            2: list(REACTIONS_MAP_PLAYER_REFLECTED_ACT[2]) + list(REACTIONS_MAP_PLAYER_REFLECTED_WCC[2]) + [
                (_("...{w=0.3}How did you do that?"), _("If you keep playing like that, I won't have a chance to win!"))
            ]
        }

        # now fill all of those with the base lines for reflecting a card
        for i in range(3):
            REACTIONS_MAP_PLAYER_REFLECTED_ACT[i] += list(REACTIONS_MAP_PLAYER_REFLECTED_CARD[i])
            REACTIONS_MAP_PLAYER_REFLECTED_WCC[i] += list(REACTIONS_MAP_PLAYER_REFLECTED_CARD[i])
            REACTIONS_MAP_PLAYER_REFLECTED_WD4[i] += list(REACTIONS_MAP_PLAYER_REFLECTED_CARD[i])

        # Map between reactions ids and dicts of lists of quips
        REACTIONS_MAP = {
            NO_REACTION: None,# 0
            MONIKA_REFLECTED_ACT: REACTIONS_MAP_MONIKA_REFLECTED_ACT,# 1
            PLAYER_REFLECTED_ACT: REACTIONS_MAP_PLAYER_REFLECTED_ACT,# 2
            MONIKA_REFLECTED_WDF: REACTIONS_MAP_MONIKA_REFLECTED_WD4,# 3
            PLAYER_REFLECTED_WDF: REACTIONS_MAP_PLAYER_REFLECTED_WD4,# 4
            MONIKA_REFLECTED_WCC: REACTIONS_MAP_MONIKA_REFLECTED_WCC,# 5
            PLAYER_REFLECTED_WCC: REACTIONS_MAP_PLAYER_REFLECTED_WCC,# 6
            MONIKA_PLAYED_WILD: REACTIONS_MAP_MONIKA_PLAYED_WILD# 7
        }

        # Chances to get a reaction depend on its seen_count
        # This is a map between seen_count and the odds
        REACTION_CHANCES_MAP = {
            0: 33,
            1: 66,
            2: 90
        }

        def __init__(self):
            """
            Constructor
            """
            # Define main table
            self.table = Table(
                back=ASSETS + "cards/back.png",
                base=Solid(
                    "#00000000",
                    xsize=150,
                    ysize=214
                ),
                springback=0.3,
                rotate=0.15,
                can_drag=self.__can_drag
            )
            # Define drawpile
            self.drawpile = self.table.stack(
                self.DRAWPILE_X,
                self.DRAWPILE_Y,
                xoff=-0.03,
                yoff=-0.08,
                click=True,
                drag=DRAG_TOP
            )
            # Define discardpile
            self.discardpile = self.table.stack(
                self.DISCARDPILE_X,
                self.DISCARDPILE_Y,
                xoff=0.03,
                yoff=-0.08,
                drag=DRAG_TOP,
                drop=True
            )

            # Define our players
            self.player = self.__Player(leftie=persistent._mas_pm_is_righty is False)# I can leave it like this until the devs actually add it
            self.monika = self.__AI(self, leftie=True)

            # Define stacks for our players
            self.player.hand = self.table.stack(
                self.PLAYERHAND_X,
                self.PLAYERHAND_Y,
                xoff=self.__calculate_xoffset(self.player),
                yoff=0,
                click=True,
                drag=DRAG_CARD,
                drop=True,
                hover=True
            )
            self.monika.hand = self.table.stack(
                self.MONIKAHAND_X,
                self.MONIKAHAND_Y,
                xoff=self.__calculate_xoffset(self.monika, self.MONIKA_CARDS_OFFSET),
                yoff=0,
                click=True
            )

            # We do not take any input yet
            self.set_sensitive(False)
            # List of dicts with various info about players state during their turns
            self.game_log = []
            # Start count from 1 because it's easier to use
            self.current_turn = 1
            # Load cards
            self.__fill_deck()

        def __can_drag(self, table, stack, card):
            """
            Checks if you can drag card from stack

            OUT:
                True if you can, False otherwise
            """
            # Makes no sense to drag card if it's the only card in the discardpile
            return not (stack is self.discardpile and len(self.discardpile) < 2)

        def __springback_cards(self, hand):
            """
            Makes all cards in the given hand to spring back

            IN:
                hand - hand to spring back cards in
            """
            for card in hand:
                self.table.get_card(card).springback()

        def __say_quip(self, what, interact=True, new_context=False):
            """
            Wrapper around renpy.say

            IN:
                what - a list/tuple of quips or a single quip to say
            """
            if isinstance(what, (list, tuple)):
                quip = renpy.random.choice(what)

            else:
                quip = what

            if new_context:
                renpy.invoke_in_new_context(renpy.say, m, quip, interact=interact)

            else:
                renpy.say(m, quip, interact=interact)

        def __calculate_xoffset(self, player, shift=0):
            """
            Determines the x offset depending on quantity of cards in player's hand

            IN:
                player - the player in whose hand we change the offset
                shift - extra offset
                    (Default: 0)

            OUT:
                integer as the offset

            ASSUMES:
                Monika is a leftie
            """
            # If the hand is None or there are less than 7 cards, we use 32
            offset = 32

            if player.hand is not None:
                amount = len(player.hand)

                if amount > 10:
                    offset = 28

                elif amount > 7:
                    offset = 30

            if player.isAI:
                if player.leftie:
                    xoffset = offset + shift
                else:
                    xoffset = -(offset + shift)

            else:
                if player.leftie:
                    xoffset = -(offset + shift)
                else:
                    xoffset = offset + shift

            return xoffset

        def __set_xoffset(self, player, shift=0):
            """
            Changes cards offset depending on quantity of cards in hand

            IN:
                player - the player in whose hand we change the offset
                shift - extra offset
                    (Default: 0)
            """
            player.hand.xoff = self.__calculate_xoffset(player, shift)
            self.__springback_cards(player.hand)

        def __calculate_xpos(self, player):
            """
            Determines position of the first card
            depending on quantity of cards in player's hand

            IN:
                player - the player in whose hand we change
                    the x attribute of the card

            OUT:
                integer as the x coordinate for the hand

            ASSUMES:
                we updated (if needed) the x offset for the hand before calling this
            """
            if player.isAI:
                xpos = self.MONIKAHAND_X

            else:
                xpos = self.PLAYERHAND_X

            if player.hand is not None:
                amount = len(player.hand) - 1
                offset = player.hand.xoff

            else:
                amount = 6
                offset = 32

            for i in range(amount):
                xpos -= (offset / 2)

            return xpos

        def __set_xpos(self, player):
            """
            Changes the placement of the first card
            depending on quantity of cards in player's hand

            IN:
                player - the player in whose hand we set
                    the x attribute of the card

            ASSUMES:
                we updated (if needed) the x offset for the hand before calling this
            """

            player.hand.x = self.__calculate_xpos(player)
            self.__springback_cards(player.hand)

        def __update_cards_positions(self, player, shift=0):
            """
            Updates cards positions in player's hand

            IN:
                player - the player for whose hand we update cards positions
                shift - extra offset (see __calculate_xoffset)
                    (Default: 0)
            """
            self.__set_xoffset(player, shift)
            self.__set_xpos(player)

        def __get_card_filename(self, card):
            """
            Generates filename for a card based on its color and type

            IN:
                card - card object

            OUT:
                string with filename w/o extension
            """
            # For non-Wild cards
            if card.color:
                part1 = card.color[0]

                if card.type == "number":
                    part2 = card.label
                else:
                    if card.label == "Skip":
                        part2 = "s"
                    elif card.label == "Draw Two":
                        part2 = "d2"
                    # "Reverse"
                    else:
                        part2 = "r"

            # For Wild cards
            else:
                part1 = ""

                if card.label == "Wild":
                    part2 = "wcc"
                # "Wild Draw Four"
                else:
                    part2 = "wd4"

            return part1 + part2

        def __load_card_asset(self, card):
            """
            Associates a card object with its asset, adds it to the deck and sets it face down
            # NOTE: Thanks to Velius aka big pout booplicate for these cool cards

            IN:
                card - card object
            """
            card_png = self.__get_card_filename(card)
            self.table.card(card, "{0}cards/{1}.png".format(ASSETS, card_png))
            self.table.set_faceup(card, False)

        def __fill_deck(self):
            """
            Fills the deck with cards and adds them to the drawpile

            NOTE: does not shuffles the drawpile
            """
            for type in self.TYPES:
                if type != "wild":
                    for color in self.COLORS:
                        # number cards
                        if type == "number":
                            for dupe in range(2):
                                for label in self.NUMBER_LABELS:
                                    # we don't duplicate "0" cards
                                    if dupe == 1 and label == "0":
                                        continue
                                    else:
                                        card = self.__Card(type, label, color)
                                        self.__load_card_asset(card)
                                        self.drawpile.append(card)
                        # action cards
                        else:
                            for dupe in range(2):
                                for label in self.ACTION_LABELS:
                                    card = self.__Card(type, label, color)
                                    self.__load_card_asset(card)
                                    self.drawpile.append(card)
                # wild cards
                else:
                    for dupe in range(4):
                        for label in self.WILD_LABELS:
                            card = self.__Card(type, label)
                            self.__load_card_asset(card)
                            self.drawpile.append(card)

        def __update_drawpile(self):
            """
            Moves all - except the top one - cards from the discardpile
            onto the drawpile, then shuffles drawpile
            """
            renpy.pause(0.5, hard=True)

            while len(self.discardpile) > 1:
                card = self.discardpile[1]

                self.table.set_faceup(card, False)
                self.table.set_rotate(card, 0)
                self.table.get_card(card).set_offset(0, 0)

                self.drawpile.append(card)

            renpy.pause(0.2, hard=True)

            # align the last card
            last_card = self.table.get_card(self.discardpile[0])
            self.table.set_rotate(last_card.value, 90)
            last_card.set_offset(0, 0)

            self.shuffle_drawpile()

        def __update_game_log(self, current_player, next_player):
            """
            Updates the log with the actions/attributes of the current and next players
            We can back in to any turn and check what happened there

            NOTE: have to do fill the log in 2 steps:
                1. write first bits when the previous player ends their turn
                2. add more data after the current player ends their turn
                and so on

            NOTE: for the reason above we update the log in prepare_game()
                for the 1st time

            IN:
                current_player - the player who ends their turn
                next_player - next played
            """
            next_player_data = {
                "turn": self.current_turn + 1,
                "player": next_player,
                "had_skip_turn": next_player.should_skip_turn,
                "had_draw_cards": next_player.should_draw_cards,
                "drew_card": None,
                "played_card": None
            }

            current_player_data = {
                "drew_card": current_player.drew_card,
                "played_card": self.discardpile[-1] if current_player.played_card else None
            }

            self.game_log[-1].update(current_player_data)
            self.game_log.append(next_player_data)

        def end_turn(self, current_player, next_player):
            """
            Updates players' attributes at the end of turn
            Also switches sensitivity and makes sure that the drawpile has cards

            IN:
                current_player - the player who ends their turn
                next_player - next player

            ASSUMES:
                mas_nou.disable_remind_button
                mas_nou.disable_yell_button
            """
            global disable_remind_button
            global disable_yell_button

            # reset the buttons' states
            disable_remind_button = False
            disable_yell_button = False

            if not self.drawpile:
                # NOTE: we can still have an active interaction during this call
                # which will lead to a crash. Dirty fix: invoke this method
                renpy.invoke_in_new_context(self.__update_drawpile)

            self.__update_game_log(current_player, next_player)

            # now that we saved data in the log
            # we can reset some vars

            # reset nou vars if appropriate
            if current_player.yelled_nou:
                # drew more cards? no more in nou grace state
                if len(current_player.hand) > 1:
                    current_player.yelled_nou = False
                    current_player.nou_reminder_timeout = 0

                # Did this player yell 'NOU', but didn't play a card?
                if current_player.should_play_card:
                    # Monika will always play a card after saying 'NOU'
                    # But we will have a fallback just in case
                    if current_player.isAI:
                        quips = self.QUIPS_MONIKA_FALSE_NOU

                    else:
                        quips = self.QUIPS_PLAYER_FALSE_NOU

                    self.set_sensitive(False)
                    self.__say_quip(quips, new_context=True)

                    current_player.should_play_card = False

            current_player.should_skip_turn = False
            current_player.plays_turn = False

            # we can set 'should_draw_cards' to 0 if this player reached the cap
            if (
                next_player.should_draw_cards
                and len(next_player.hand) >= self.HAND_CARDS_LIMIT
            ):
                if next_player.isAI:
                    quips = self.QUIPS_PLAYER_CARDS_LIMIT

                else:
                    quips = self.QUIPS_MONIKA_CARDS_LIMIT

                self.set_sensitive(False)
                self.__say_quip(quips, new_context=True)

                next_player.should_draw_cards = 0

            next_player.drew_card = False
            next_player.played_card = False
            next_player.plays_turn = True

            self.current_turn += 1

            self.set_sensitive(not next_player.isAI)

        def __win_check(self, player):
            """
            Checks if player can win the game (has no cards left)
            If we have a winner, we update wins and jump to the end game label
            The rest will be handled in the label

            IN:
                player - the player we check
            """
            if player.hand:
                return

            self.set_sensitive(False)

            global winner

            if player.isAI:
                winner = "Monika"

            else:
                winner = "Player"

            persistent._mas_game_nou_wins[winner] += 1

            renpy.pause(2, hard=True)
            renpy.jump("mas_nou_game_end")

        def __is_matching_card(self, player, card):
            """
            Checks if the given card matches the top card in the discardpile

            IN:
                player - the player who tries to play the card
                card - the card the player wants to play

            OUT:
                True if the player can play the card, False otherwise

            ASSUMES:
                len(discardpile) > 0
            """
            # sanity check
            if card not in player.hand:
                return False

            def has_color(hand, color):
                """
                Checks if there's a card with the given color in the given hand
                NOTE: to avoid unwanted incidents, we don't check cards w/o color

                IN:
                    hand - the hand we check
                    color - the color we're looking for

                OUT:
                    True if there is a card with that color, False otherwise
                """
                return color in [card.color for card in hand if card.color is not None]

            # "Attack rules"
            if not player.should_skip_turn:
                return (
                    card.label == "Wild"
                    or (
                        card.label == "Wild Draw Four"
                        and (
                                persistent._mas_game_nou_house_rules["unrestricted_wd4"]
                                or not has_color(player.hand, self.discardpile[-1].color)
                        )
                    )
                    or card.color == self.discardpile[-1].color
                    or card.label == self.discardpile[-1].label
                )

            # "Defence rules"
            else:
                return (
                    (
                        self.discardpile[-1].label == "Wild Draw Four"
                        and card.label == "Draw Two"
                        and self.discardpile[-1].color == card.color
                    )
                    or (
                        self.discardpile[-1].label == "Draw Two"
                        and card.label == "Draw Two"
                    )
                    or (
                        self.discardpile[-1].label == "Skip"
                        and card.label == "Skip"
                        and self.discardpile[-1].color == card.color
                    )
                    or (
                        self.discardpile[-1].label == "Reverse"
                        and card.label == "Reverse"
                    )
                )

        def play_card(self, current_player, next_player, card):
            """
            A method to play cards and change players' attributes
            NOTE: this doesn't check if the card matches

            IN:
                current_player - the player who plays card
                next_player - the player who will be affected by card if any
                card - card to play
            """
            # First get new rotation and offset for the card
            if current_player.isAI:
                cards_offset = self.MONIKA_CARDS_OFFSET
                card_rotation = renpy.random.randint(-193, -167)

            else:
                cards_offset = self.PLAYER_CARDS_OFFSET
                card_rotation = renpy.random.randint(-13, 13)

            card_position = (renpy.random.randint(-14, 14), renpy.random.randint(-10, 10))

            # now move the card and apply changes
            self.discardpile.append(card)
            self.table.set_rotate(self.discardpile[-1], card_rotation)
            self.table.get_card(self.discardpile[-1]).set_offset(*card_position)
            self.table.set_faceup(self.discardpile[-1], True)

            self.__update_cards_positions(current_player, cards_offset)

            # and update players' attributes
            current_player.played_card = True
            current_player.should_play_card = False

            if self.discardpile[-1].type == "action" or self.discardpile[-1].label == "Wild Draw Four":
                next_player.should_skip_turn = True
                current_player.should_skip_turn = False

                if self.discardpile[-1].label == "Draw Two":
                    next_player.should_draw_cards = 2

                    if persistent._mas_game_nou_house_rules["stackable_d2"]:
                        next_player.should_draw_cards += current_player.should_draw_cards

                    current_player.should_draw_cards = 0

                elif self.discardpile[-1].label == "Wild Draw Four":
                    next_player.should_draw_cards = 4
                    current_player.should_draw_cards = 0

            # if this player should say 'NOU', we'll set the timeout
            # during which they can be cautch by other players if they don't say 'NOU'
            if len(current_player.hand) == 1:
                current_player.nou_reminder_timeout = self.current_turn + 2

        def __actually_deal_cards(self, player, amount, smooth):
            """
            Moves cards from the drawpile into player's hand,
            updates offsets, rotation and sets cards faceup if needed

            NOTE: Unsafe to use this directly, we use deal_cards

            IN:
                player - the player who will get the cards
                amount - amount of cards to deal
                smooth - whether or not we use a little pause between dealing cards
            """
            player_cards = len(player.hand)
            if player_cards + amount > self.HAND_CARDS_LIMIT:
                amount = self.HAND_CARDS_LIMIT - player_cards

            for i in range(amount):
                player.hand.append(self.drawpile[-1])

                if player.isAI:
                    self.table.set_rotate(player.hand[-1], -180)
                    offset = self.MONIKA_CARDS_OFFSET

                else:
                    self.table.set_faceup(player.hand[-1], True)
                    offset = self.PLAYER_CARDS_OFFSET

                self.__update_cards_positions(player, offset)

                if smooth:
                    renpy.pause(0.3, hard=True)

        def deal_cards(self, player, amount=1, smooth=True, mark_as_drew_card=True, reset_nou_var=True):
            """
            Deals cards to players
            Also refreshing the drawpile if there're not enough cards

            IN:
                player - the player whose hand we deal cards in
                amount - amount of cards to deal
                    (Default: 1)
                smooth - whether or not we use a little pause between dealing cards
                    (Default: True)
                mark_as_drew_card - whether or not we set the var for the player
                    (Default: True)
                reset_nou_var - whether or not we reset the nou var for the player who draws cards
                    (Default: True)
            """
            drawpile_cards = len(self.drawpile)

            if mark_as_drew_card:
                player.drew_card = True
            if reset_nou_var:
                player.yelled_nou = False
                player.nou_reminder_timeout = 0

            # there're enough cards for you
            if drawpile_cards >= amount:
                self.__actually_deal_cards(player, amount, smooth)

                if player.should_draw_cards:
                    player.should_draw_cards -= amount

            # there're not enough cards
            else:
                # deal as much as we can
                cards_to_deal = amount - drawpile_cards
                self.__actually_deal_cards(player, drawpile_cards, smooth)

                if player.should_draw_cards:
                    player.should_draw_cards -= drawpile_cards

                self.__update_drawpile()
                drawpile_cards = len(self.drawpile)

                # we should never get here, but just in case
                if drawpile_cards < cards_to_deal:
                    self.__actually_deal_cards(player, drawpile_cards, smooth)
                    player.should_draw_cards = 0

                # deal remaining cards
                else:
                    self.__actually_deal_cards(player, cards_to_deal, smooth)
                    player.should_draw_cards = 0

        def prepare_game(self):
            """
            This method sets up everything we need to start a game of NoU:
                1. Chooses who plays first
                2. Shuffles the deck
                3. Deals cards
                4. Places first card onto the discardpile
                    and handles if it's an action/wild card
                5. Fills first bits in the log
                6. Makes our table sensetive to the user's imput
                    if needed
            """
            # Decide who will play the first turn
            global player_win_streak
            global monika_win_streak

            if player_win_streak:
                current_player = self.player
                next_player = self.monika

            elif monika_win_streak:
                current_player = self.monika
                next_player = self.player

            else:
                if renpy.random.randint(0, 1):
                    current_player = self.player
                    next_player = self.monika

                else:
                    current_player = self.monika
                    next_player = self.player

            self.shuffle_drawpile()

            # Deal 14 cards or whatever you asked her for
            total_cards = persistent._mas_game_nou_house_rules["starting_cards"] * 2 + 1
            for i in range(1, total_cards):
                if not i % 2:
                    temp_player = next_player
                else:
                    temp_player = current_player

                self.deal_cards(temp_player)
                temp_player.drew_card = False

            # We need to shuffle the deck if the top card is WDF
            ready = False
            pulled_wdf = False

            while not ready:
                card = self.drawpile[-1]

                self.discardpile.append(card)
                self.table.set_rotate(card, 90)
                self.table.set_faceup(card, True)

                if card.label == "Wild Draw Four":
                    if not pulled_wdf:
                        pulled_wdf = True
                        self.__say_quip(
                            self.QUIPS_MONIKA_RESHUFFLE_DECK
                        )
                        renpy.pause(0.5, hard=True)

                    else:
                        renpy.pause(1, hard=True)

                    # it'safe to assume that the drawpile has 10+ cards
                    new_id = len(self.drawpile) / 2 + renpy.random.randint(-10, 10)
                    self.drawpile.insert(new_id, card)
                    self.table.set_rotate(card, 0)
                    self.table.set_faceup(card, False)

                    renpy.pause(0.1, hard=True)
                    self.shuffle_drawpile()

                else:
                    ready = True

            # The 1st player will choose a color if it's WCC
            if self.discardpile[-1].label == "Wild":
                # NOTE: Monika will say what the color is later
                if current_player.isAI:
                    self.monika.chosen_color = self.monika.choose_color()
                    self.discardpile[-1].color = self.monika.chosen_color

            # Unlucky! The 1st player should skip the turn
            elif self.discardpile[-1].type == "action":
                current_player.should_skip_turn = True

                # Even more, you should draw 2 cards!
                if self.discardpile[-1].label == "Draw Two":
                    current_player.should_draw_cards = 2

            # Need to write some info in the game log
            current_player_data = {
                "turn": self.current_turn,
                "player": current_player,
                "had_skip_turn": current_player.should_skip_turn,
                "had_draw_cards": current_player.should_draw_cards,
                "drew_card": None,
                "played_card": None
            }
            self.game_log.append(current_player_data)

            if current_player.isAI:
                if current_player.should_skip_turn:
                    can_reflect = current_player.choose_card(should_draw=False)

                    if can_reflect:
                        quips = self.QUIPS_MONIKA_WILL_REFLECT

                    elif current_player.should_draw_cards:
                        quips = self.QUIPS_MONIKA_DRAWS_CARDS

                    else:
                        quips = self.QUIPS_MONIKA_SKIPS_TURN

                else:
                    quips = self.QUIPS_MONIKA_PLAYS_TURN

            else:
                if current_player.should_skip_turn:
                    if current_player.should_draw_cards:
                        quips = self.QUIPS_PLAYER_DRAWS_CARDS

                    else:
                        quips = self.QUIPS_PLAYER_SKIPS_TURN

                else:
                    quips = self.QUIPS_PLAYER_PLAYS_TURN

            renpy.pause(0.5, hard=True)

            # Monika says a general quip
            self.__say_quip(
                quips
            )
            # Monika says the current color if needed
            if current_player.isAI and self.discardpile[-1].label == "Wild":
                self.__say_quip(
                    self.QUIPS_MONIKA_ANNOUNCE_COLOR_FIRST_TURN
                )
                # We can reset this here since we don't need it anymore
                self.monika.chosen_color = None

            # Finally allow to interact with cards
            current_player.plays_turn = True
            self.set_sensitive(not current_player.isAI)

        def reset_game(self):
            """
            Reinitialize the game so you can start another round
            """
            del self.monika, self.player, self.drawpile, self.discardpile, self.table
            self.__init__()

        def player_turn_loop(self):
            """
            Tracks the player's actions and responds to their interactions
            """
            while self.player.plays_turn:
                events = ui.interact(type="minigame")

                for event in events:
                    if event.type == "hover":
                        if event.card in self.player.hand:
                            # get this card from the table
                            card = self.table.get_card(event.card)
                            # now move it
                            card.set_offset(0, -35)
                            card.springback()
                            # this moves the card stack on top of rendering order
                            stack = card.stack
                            self.table.stacks.remove(stack)
                            self.table.stacks.append(stack)

                    elif event.type == "unhover":
                        if event.card in self.player.hand:
                            card = self.table.get_card(event.card)
                            # move it back
                            card.set_offset(0, 0)
                            card.springback()

                    elif event.type == "doubleclick":
                        # Player takes cards
                        if (
                            event.stack is self.drawpile
                            and self.discardpile[-1].color is not None
                            # check if you drew max cards already or just have to skip your turn
                            and not (
                                (
                                    self.player.drew_card
                                    or self.player.should_skip_turn
                                )
                                and not self.player.should_draw_cards
                            )
                        ):
                            self.set_sensitive(False)

                            if self.player.should_draw_cards:
                                self.deal_cards(self.player, self.player.should_draw_cards)
                            else:
                                self.deal_cards(self.player)

                            self.set_sensitive(True)

                    elif event.type == "drag":
                        # Reset the offsets after hovering
                        # FIXME: ideally we should do this via queueing an unhover event
                        # card = self.table.get_card(event.card)
                        # card.set_offset(0, 0)

                        # Player draws a card
                        if (
                            event.stack is self.drawpile
                            and event.drop_stack is self.player.hand
                            and self.discardpile[-1].color is not None
                            and not (
                                (
                                    self.player.drew_card
                                    or self.player.should_skip_turn
                                )
                                and not self.player.should_draw_cards
                            )
                        ):
                            self.set_sensitive(False)
                            self.deal_cards(self.player)
                            self.set_sensitive(True)

                        # Player plays a card
                        elif (
                            event.stack is self.player.hand
                            and event.drop_stack is self.discardpile
                            and self.discardpile[-1].color is not None
                            and not self.player.played_card
                            # Ensure that if you drew a card, then you can't play a defensive card anymore this turn
                            and not (self.player.should_skip_turn and self.player.drew_card)
                        ):
                            if self.__is_matching_card(self.player, event.card):
                                self.set_sensitive(False)
                                self.play_card(self.player, self.monika, event.card)
                                self.set_sensitive(True)

                                self.__win_check(self.player)

                                # We don't leave if the player has to choose a color
                                if self.discardpile[-1].color is not None:
                                    self.end_turn(self.player, self.monika)

                    elif event.type == "click":
                        if (
                            event.stack is self.monika.hand
                            and renpy.random.randint(1, 10) == 1# 1/10
                        ):
                            self.__say_quip(
                                self.QUIPS_PLAYER_CLICKS_MONIKA_CARDS
                            )

        def monika_turn_loop(self):
            """
            Monika's actions during her turn
            Yes, I know that this isn't a loop
            """
            if not self.monika.plays_turn:
                return

            self.monika.thonk_pause()
            self.monika.shuffle_hand()
            self.monika.thonk_pause()

            self.monika.guess_player_cards()
            next_card_to_play = self.monika.choose_card()
            reaction = self.monika.choose_reaction(next_card_to_play)
            self.monika.announce_reaction(reaction)
            self.monika.play_card(next_card_to_play)

            self.end_turn(self.monika, self.player)

        def game_loop(self):
            """
            This wrapper is supposed to be called in the main while loop
            """
            self.monika_turn_loop()
            self.player_turn_loop()

        def set_visible(self, value):
            """
            Shows/Hides cards on the table

            IN:
                value - True/False
            """
            if value:
                self.table.show()
            else:
                self.table.hide()

        def set_sensitive(self, value):
            """
            Make cards (in-)sensitive to the player's input

            IN:
                value - True/False
            """
            self.table.set_sensitive(value)

        def is_sensitive(self):
            """
            Checks if the table is sensitive to the input

            OUT:
                True if sensitive, False otherwise
            """
            return self.table.sensitive

        def shuffle_drawpile(self):
            """
            Shuffles the drawpile and animates cards shuffling

            ASSUMES:
                len(drawpile) > 15
            """
            total_cards = len(self.drawpile)

            # NOTE: This is Just in case, in theory the drawpile will have about 47 cards in the worst scenario
            if total_cards > 15:
                # 7/10
                k = renpy.random.randint(0, 9)
                # we want to shuffle a bit faster than doing other card interactions
                self.table.springback = 0.2
                renpy.pause(0.2, hard=True)

                for i in range(7):
                    card_id = renpy.random.randint(0, total_cards - 2)
                    if k == i:
                        insert_id = total_cards - 1
                    else:
                        insert_id = renpy.random.randint(0, total_cards - 2)

                    card = self.table.get_card(self.drawpile[card_id])

                    x_offset = renpy.random.randint(160, 190)
                    y_offset = renpy.random.randint(-15, 15)

                    card.set_offset(x_offset, y_offset)
                    card.springback()
                    renpy.pause(0.15, hard=True)

                    self.drawpile.insert(insert_id, card.value)

                    card.set_offset(0, 0)
                    card.springback()
                    renpy.pause(0.15, hard=True)

                # reset speed
                self.table.springback = 0.3

            self.drawpile.shuffle()
            renpy.pause(0.2, hard=True)

        def handle_nou_logic(self, player):
            """
            A method that handles "yelling system" from the player side
            NOTE: Everything here must be called in a new context
                since we 100% will have an active interaction when we get here.
                We also toggle the sensitivity so you don't skip the dlg

            IN:
                player - 'name' of the player we will check for nou
                    (either 'monika' or 'player')

            ASSUMES:
                the player didn't start to play their turn
            """
            self.set_sensitive(False)
            if player == "monika":
                if self.monika.yelled_nou:
                    self.__say_quip(self.QUIPS_MONIKA_ALREADY_YELLED_NOU, new_context=True)

                elif len(self.monika.hand) > 1:
                    self.__say_quip(self.QUIPS_MONIKA_DONT_NEED_YELL_NOU, new_context=True)

                elif self.monika.nou_reminder_timeout <= self.current_turn:
                    self.__say_quip(self.QUIPS_MONIKA_TIMEDOUT_NOU, new_context=True)

                else:
                    self.__say_quip(self.QUIPS_MONIKA_FORGOT_YELL_NOU, new_context=True)
                    # you got her, now she must draw 2 more cards
                    self.deal_cards(self.monika, amount=2, smooth=False, mark_as_drew_card=False)
                    renpy.invoke_in_new_context(renpy.pause, 0.5, hard=True)

            elif player == "player":
                if self.player.yelled_nou:
                    self.__say_quip(self.QUIPS_PLAYER_ALREADY_YELLED_NOU, new_context=True)

                # for the player we check the second last card
                elif len(self.player.hand) > 2:
                    self.__say_quip(self.QUIPS_PLAYER_DONT_NEED_YELL_NOU, new_context=True)

                else:
                    # 1/4 to say something so she doesn't spam you lol
                    if renpy.random.randint(1, 4) == 1:
                        self.__say_quip(self.QUIPS_PLAYER_YELLS_NOU, new_context=True)

                    self.player.yelled_nou = True
                    self.player.should_play_card = True
                    self.player.nou_reminder_timeout = 0
            self.set_sensitive(True)

        class __Card(object):
            """
            A class to represent a card

            PROPERTIES:
                type - (str) number, action or wild
                label - (str) number/action on card '0'-'9', "Draw Two", etc
                color - (str/None) red, blue, green, yellow or None
                    (Default: None (colorless))
                value - (int) how much points the card gives
            """
            def __init__(self, t, l, c=None):
                """
                Constructor

                IN:
                    t - type of the card
                    l - the card's label
                    c - the card's color
                        (Default: None)
                """
                self.type = t
                self.label = l
                self.color = c

                if self.type == "number":
                    self.value = int(self.label)

                elif self.type == "action":
                    self.value = 20

                else:
                    self.value = 50

            def __repr__(self):
                if self.color is not None:
                    return self.color + " " + self.label
                else:
                    return self.label

        class __Player(object):
            """
            A class to represent players

            PROPERTIES:
                leftie - (bool) is player leftie or rightie
                isAI - (bool) is it the Player or Monika
                hand - (stack) represents player's hand (a Stack object)
                drew_card - (bool) has player drew a card in this turn
                plays_turn - (bool) is it player's turn
                should_draw_cards - (int) should player draw cards and how much
                played_card - (bool) has player played a card in this turn
                should_skip_turn - (bool) should player skip their turn
                yelled_nou - (bool) has player yelled "NOU" before playing their last card
                should_play_card - (bool) do we expect this player to play a card (after saying 'NOU')
                nou_reminder_timeout - (int) the turn when this player cannot be caught for not saying 'NOU' any longer
            """
            def __init__(self, leftie=False):
                """
                Constructor

                IN:
                    leftie - is player leftie or rightie
                """
                self.leftie = leftie
                self.isAI = False
                self.hand = None
                self.drew_card = False
                self.should_draw_cards = 0
                self.played_card = False
                self.plays_turn = False
                self.should_skip_turn = False
                self.yelled_nou = False
                self.should_play_card = False
                self.nou_reminder_timeout = 0

            def __repr__(self):
                return "<__Player {0}>".format(persistent.playername)

        class __AI(__Player):
            """
            AI variation of player

            PROPERTIES:
                everything from __Player
                game - (NoU) pointer for internal use
                cards_data - (dict) data about our cards (amount, values, ids)
                queued_card - (__Card) the card Monika wants to play on the next turn
                player_cards_data - (dict) potentially the most common color (or None)
                    and most rare colors (or an empty list) in the Player's hand
                    'reset_in' shows how much turns left until we reset 'has_color'
                reactions - (list) all reactions that monika had during this game
                    (even if they didn't trigger)
            """
            MIN_THONK_TIME = 0.2
            MAX_THONK_TIME = 0.8
            SHUFFLING_CHANCE = 15
            LOW_MISSING_NOU_CHANCE = 5
            HIGHT_MISSING_NOU_CHANCE = 25

            def __init__(self, game, leftie=False):
                """
                Constructor

                IN:
                    leftie - is this player leftie or rightie
                    game - pointer to our NoU object
                """
                super(game.__AI, self).__init__(leftie)

                self.isAI = True
                self.game = game
                self.queued_card = None
                self.chosen_color = None
                self.player_cards_data = {
                    "reset_in": 0,# we reset 'has_color' to None in 'reset_in' turns
                    "has_color": None,# we keep track only on 1 color here
                    "lacks_colors": []# but keep track on multiple colors here
                }
                # all previous reactions
                # items format: {"type": type, "turn": turn_id, "monika_card": card or None, "player_card": card or None, "seen_count": int, "shown": boolean}
                self.reactions = []

            def __repr__(self):
                return "<__AI Monika>"

            def thonk_pause(self):
                """
                Pauses the game giving some time to Monika to thonk out her next turn
                """
                if len(self.hand) == 1:
                    thonk_time = self.MIN_THONK_TIME

                else:
                    thonk_time = renpy.random.uniform(self.MIN_THONK_TIME, self.MAX_THONK_TIME)

                renpy.pause(thonk_time, hard=True)

            def __randomise_color(self):
                """
                Chooses one of the colors at random
                Excludes the potential color that the player may have
                If we know what the colors the player doesn't have,
                we will return one of them at random

                OUT:
                    string with one of 4 colors
                """
                if self.player_cards_data["lacks_colors"]:
                    return renpy.random.choice(self.player_cards_data["lacks_colors"])

                colors = list(self.game.COLORS)

                if self.player_cards_data["has_color"] is not None:
                    colors.remove(self.player_cards_data["has_color"])

                return renpy.random.choice(colors)

            def guess_player_cards(self):
                """
                Guesses cards' colors in the player's hand
                NOTE: must run this before anything else
                NOTE: this method is quite a mess
                """
                # We can't assume anything if the player didn't play their 1st turn
                if len(self.game.game_log) < 2:
                    return

                # Decrement the counter if the pleyer played a card
                if (
                    self.player_cards_data["reset_in"] > 0
                    and self.game.game_log[-2]["played_card"] is not None
                ):
                    self.player_cards_data["reset_in"] -= 1

                # First let's guess what color the player may have
                # when you set a new color, you probably have cards with that color
                if (
                    (
                        self.game.game_log[-2]["played_card"] is not None
                        and self.game.game_log[-2]["played_card"].type == "wild"
                    )
                    or (
                        self.game.current_turn == 2
                        and len(self.game.discardpile) > 1
                        and self.game.discardpile[-2].type == "wild"
                    )
                ):
                    color = self.game.game_log[-2]["played_card"].color

                    self.player_cards_data["has_color"] = color
                    self.player_cards_data["reset_in"] = 3

                    # remove it from the other dict
                    if color in self.player_cards_data["lacks_colors"]:
                        self.player_cards_data["lacks_colors"].remove(color)

                # Now guess what color the player lacks
                # If you have to play wild cards, then you don't have the previous color
                if (
                    # NOTE: the player can trick Monika here, but they won't
                    # get much from this so I'll leave it
                    self.game.game_log[-2]["played_card"] is not None
                    and self.game.game_log[-2]["played_card"].type == "wild"
                    and (
                        not persistent._mas_game_nou_house_rules["unrestricted_wd4"]
                        # 1/4
                        or renpy.random.randint(1, 4) == 1
                    )
                    and len(self.game.discardpile) > 1
                ):
                    if self.game.discardpile[-2].color not in self.player_cards_data["lacks_colors"]:
                        self.player_cards_data["lacks_colors"].append(self.game.discardpile[-2].color)

                    if self.player_cards_data["has_color"] in self.player_cards_data["lacks_colors"]:
                        self.player_cards_data["has_color"] = None

                # the player drew a card in their turn by their own will,
                # that means they might not have the current color
                elif (
                    self.game.game_log[-2]["drew_card"]
                    and not self.game.game_log[-2]["had_skip_turn"]
                ):
                    # if not self.game.player.played_card:
                    # None means the player haven't played a card
                    if not self.game.game_log[-2]["played_card"]:
                        # NOTE: since the player drew a card and didn't play it, we can't be sure about
                        # other colors in the list
                        self.player_cards_data["lacks_colors"] = [self.game.discardpile[-1].color]

                    elif self.game.discardpile[-2].color not in self.player_cards_data["lacks_colors"]:
                        # append only if it's not in the list
                        self.player_cards_data["lacks_colors"].append(self.game.discardpile[-2].color)

                    if self.player_cards_data["has_color"] in self.player_cards_data["lacks_colors"]:
                        self.player_cards_data["has_color"] = None

                # if the player lacks 3 colors, we can assume which color they have
                if len(self.player_cards_data["lacks_colors"]) == 3:
                    missing_colors = self.player_cards_data["lacks_colors"]
                    # convert to set so we can find difference
                    all_colors = frozenset(self.game.COLORS)

                    # now compare the set and the list, then iterate to get the only element from it
                    self.player_cards_data["has_color"] = next(iter(all_colors.difference(missing_colors)))
                    self.player_cards_data["reset_in"] = 3

                # Now we check if we should reset some of our data
                # reset the data if the player drew 2+ cards in their turn
                if (
                    self.game.game_log[-2]["drew_card"]
                    and self.game.game_log[-2]["had_draw_cards"]
                ):
                    self.player_cards_data["lacks_colors"] = []

                # reset this data as outdated
                if self.player_cards_data["reset_in"] == 0:
                    self.player_cards_data["has_color"] = None

            def __sort_cards_data(self, cards_data, keys_sort_order=["num", "act"], values_sort_order=["value", "amount"], consider_player_cards_data=True):
                """
                Sorts (by keys and then values) the cards data dict
                and returns it as a list of tuples

                Example:
                    [
                        ('num_red', {'amount': 5, 'ids': [6, 1, 3, 12], 'value': 26}),
                        ('num_yellow', {'amount': 4, 'ids': [5, 10, 8, 11], 'value': 9}),
                        ...
                        ('act_yellow', {'amount': 2, 'ids': [2, 9], 'value': -1}),
                        ('wcc', {'amount': 0, 'ids': [], 'value': -1}),
                        ('wd4', {'amount': 1, 'ids': [4], 'value': -1})
                    ]

                IN:
                    cards_data - dict with info about Monika's cards
                    NOTE: check sortKey for these
                    keys_sort_order - the dict's keys we're sorting by
                    values_sort_order - the dict's values (inner dict's keys) we're sorting by
                    consider_player_cards_data - whether or not we consider player's cards in sorting

                OUT:
                    sorted list of tuples
                """
                def sortKey(item, keys_sort_order=["num", "act"], values_sort_order=["value", "amount"], consider_player_cards_data=True):
                    """
                    Function which we use as a sort key for cards data
                    NOTE: keys have priority over values

                    IN:
                        item - tuple from the list from the cards data dict
                        keys_sort_order - list of strings to sort the list by the dict's keys
                            (Default: ['num', 'act'])
                            For example: ['num'] will put the number cards first
                            or ['red', 'act'] will put the red colored cards first, then action ones, and then the rest
                        values_sort_order - list of strings to sort the list by the dict's values
                            (Default: ['value', 'amount'])
                            For exaple: the default list will sort by cards values first,
                            and then by their amount
                        consider_player_cards_data - whether or not we consider player's cards in sorting

                    OUT:
                        list which we'll use in sorting
                    """
                    rv = list()
                    # Apply keys
                    for _key in keys_sort_order:
                        rv.append(_key in item[0])
                    # Apply values
                    for _value in values_sort_order:
                        rv.append(item[1][_value])
                    # Apply player cards data
                    if consider_player_cards_data:
                        # Check if this item has the color that we'd like to avoid
                        if self.player_cards_data["has_color"] is not None:
                            rv.append(self.player_cards_data["has_color"] not in item[0])

                        # Check if this item has the color that we'd like to play
                        for color in self.player_cards_data["lacks_colors"]:
                            rv.append(color in item[0])

                    return rv

                sorted_list = sorted(
                    cards_data.iteritems(),
                    key=lambda item: sortKey(
                        item,
                        keys_sort_order=keys_sort_order,
                        values_sort_order=values_sort_order,
                        consider_player_cards_data=consider_player_cards_data
                    ),
                    reverse=True
                )

                return sorted_list

            def __get_cards_data(self, cards=None):
                """
                A method that builds a dict that represents cards in a Monika-friendly way (c)
                    NOTE: ids of number and action cards are sorted by cards values
                    NOTE: This should be called after any change in Monika's hand,
                        and before she'll do anything with cards so Monika has an actual info about her cards

                IN:
                    cards - cards whose data we will return, if None, uses the current Monika's cards
                        (Default: None)

                OUT:
                    dict with various data about Monika's cards
                """
                if cards is None:
                    cards = [card for card in self.hand]

                new_cards_data = {
                    "num_red": {
                        "amount": 0,
                        "value": 0,
                        "ids": []
                    },
                    "num_blue": {
                        "amount": 0,
                        "value": 0,
                        "ids": []
                    },
                    "num_green": {
                        "amount": 0,
                        "value": 0,
                        "ids": []
                    },
                    "num_yellow": {
                        "amount": 0,
                        "value": 0,
                        "ids": []
                    },
                    "act_red": {
                        "amount": 0,
                        "value": -1,
                        "ids": []
                    },
                    "act_blue": {
                        "amount": 0,
                        "value": -1,
                        "ids": []
                    },
                    "act_green": {
                        "amount": 0,
                        "value": -1,
                        "ids": []
                    },
                    "act_yellow": {
                        "amount": 0,
                        "value": -1,
                        "ids": []
                    },
                    "wd4": {
                        "amount": 0,
                        "value": -1,
                        "ids": []
                    },
                    "wcc": {
                        "amount": 0,
                        "value": -1,
                        "ids": []
                    }
                }

                # First make a sorted list of cards
                # don't reverse for one-round games
                # TODO: make sure this works good, otherwise just always use True
                should_reverse = bool(persistent._mas_game_nou_house_rules["points_to_win"])

                sorted_cards = sorted(
                    cards,
                    key=lambda card_obj: card_obj.value,
                    reverse=should_reverse
                )

                # Now fill the dict with the sorted data
                for card in sorted_cards:
                    if card.type == "number":
                        new_cards_data["num_" + card.color]["amount"] += 1
                        new_cards_data["num_" + card.color]["value"] += card.value
                        # we sorted it, and have to use the ids from the hand
                        new_cards_data["num_" + card.color]["ids"].append(cards.index(card))

                    elif card.type == "action":
                        new_cards_data["act_" + card.color]["amount"] += 1
                        # NOTE: We don't sum up values for action and wild cards
                        # new_cards_data["act_" + card.color]["value"] += card.value
                        new_cards_data["act_" + card.color]["ids"].append(cards.index(card))

                    elif card.label == "Wild Draw Four":
                        new_cards_data["wd4"]["amount"] += 1
                        # new_cards_data["wd4"]["value"] += card.value
                        new_cards_data["wd4"]["ids"].append(cards.index(card))

                    # Just Wild cards
                    else:
                        new_cards_data["wcc"]["amount"] += 1
                        # new_cards_data["wcc"]["value"] += card.value
                        new_cards_data["wcc"]["ids"].append(cards.index(card))

                # self.cards_data = new_cards_data
                return new_cards_data

            def shuffle_hand(self):
                """
                Sorts some cards in Monika's hand
                This is just for visuals
                NOTE: Since this changes cards' ids,
                    either do this at the start of the turn (optimal),
                    or update cards data again after shuffling.
                """
                if self.game.current_turn < 4:
                    # no point in doing anything
                    return

                total_cards = len(self.hand)
                if total_cards < 4:
                    # no point in doing anything
                    return

                rng = renpy.random.randint(1, 100)
                if rng > self.SHUFFLING_CHANCE:
                    # we failed, return
                    return

                # how we want to shuffle
                shuffle_type = renpy.random.randint(1, 3)

                # just one
                if shuffle_type == 1:
                    # choose the card
                    card_id = renpy.random.randint(0, total_cards - 1)
                    # all ids we can insert to
                    free_ids = [id for id in range(total_cards) if id != card_id]
                    # choose the new id
                    insert_id = renpy.random.choice(free_ids)

                    card = self.hand[card_id]
                    self.hand.insert(insert_id, card)

                # shuffle some
                elif shuffle_type == 2:
                    all_ids = [id for id in range(total_cards)]
                    ids_to_shuffle = []
                    free_ids = list(all_ids)

                    # decide how much cards we'll shuffle
                    if total_cards > 12:
                        total_to_shuffle = 7
                    else:
                        total_to_shuffle = total_cards / 2

                    # make a list of ids we'll shuffle
                    for i in range(total_to_shuffle):
                        id = renpy.random.choice(all_ids)
                        # remove from the available ids list so we don't use it twice
                        all_ids.remove(id)
                        ids_to_shuffle.append(id)

                    # and finilly move the cards
                    for card_id in ids_to_shuffle:
                        insert_id = renpy.random.choice(free_ids)
                        card = self.hand[card_id]
                        self.hand.insert(insert_id, card)

                # shuffle (read sort) all
                else:
                    self.hand.cards.sort(key=lambda card: card.value.value, reverse=True)

                renpy.pause(0.5, hard=True)

            def choose_color(self, ignored_card=None):
                """
                Monika chooses color to set for Wild cards

                ignored_card - card that will be ignored in calculation of the color
                    (Default: None)

                OUT:
                    string with color
                """
                def sortKey(id):
                    """
                    For action cards
                    Sorts by both cards colors and labels

                    ASSUMES:
                        cards
                        sorted_cards_data
                    """
                    labels = (
                        "Skip",
                        "Draw Two",
                        "Reverse"
                    )
                    colors = [sorted_cards_data[i][0].replace("num_", "") for i in range(4)]

                    return [cards[id].label == label for label in labels] + [cards[id].color == color for color in colors]

                cards = [card for card in self.hand]

                if (
                    ignored_card is not None
                    and ignored_card in cards
                ):
                    cards.remove(ignored_card)

                cards_data = self.__get_cards_data(cards)

                # just 1 card left, set either its color or use rng
                if len(cards) == 1:
                    if cards[0].type == "wild":
                        color = self.__randomise_color()

                    else:
                        color = cards[0].color

                    return color

                else:
                    if persistent._mas_game_nou_house_rules["points_to_win"]:
                        sorted_cards_data = self.__sort_cards_data(cards_data)

                    else:
                        # NOTE: use like this because values don't matter in games w/o points
                        sorted_cards_data = self.__sort_cards_data(cards_data, values_sort_order=["amount"])

                    # more agressive
                    if len(self.game.player.hand) < 3:
                        action_ids = []

                        for color in self.game.COLORS:
                            action_ids += cards_data["act_" + color]["ids"]

                        if action_ids:
                            action_ids.sort(
                                key=sortKey,
                                reverse=True
                            )

                            self.queued_card = cards[action_ids[0]]

                            color = self.queued_card.color
                            return color

                    # default
                    else:
                        # TODO: Need to improve this part, can generalize it with the above one
                        sortByLabel = lambda card: (
                            card.label == "Skip",
                            card.label == "Draw Two",
                            card.label == "Reverse"
                        )

                        # we use amount in games where value doesn't make sense
                        if persistent._mas_game_nou_house_rules["points_to_win"]:
                            srt_data_key = "value"

                        else:
                            srt_data_key = "amount"

                        highest_value = float(sorted_cards_data[0][1][srt_data_key])

                        # no reason to enter the loop if we have no number cards
                        if highest_value:
                            for j in range(4):
                                # if the difference between the highest valued color
                                # and the one we're checking is more than 60%,
                                # then it isn't worth it, leave to set color by values of number cards
                                if float(highest_value - sorted_cards_data[j][1][srt_data_key]) / highest_value >= 0.6:
                                    break

                                # try to find an action card with the color of most valuebale number cards
                                if sorted_cards_data[j][1]["amount"]:
                                    # keep the color part of the key but replace the card's type
                                    data_key = sorted_cards_data[j][0].replace("num_", "act_")

                                    if cards_data[data_key]["amount"]:
                                        # we play Skips in priority, then d2's and then reverses
                                        self.queued_card = sorted(
                                            [cards[id] for id in cards_data[data_key]["ids"]],
                                            key=sortByLabel,
                                            reverse=True
                                        )[0]

                                        color = self.queued_card.color
                                        return color

                    # fallback
                    if sorted_cards_data[0][1]["amount"]:
                        color = sorted_cards_data[0][0].replace("num_", "")

                    elif sorted_cards_data[4][1]["amount"]:
                        color = sorted_cards_data[4][0].replace("act_", "")

                    else:
                        color = self.__randomise_color()

                    return color

            def choose_card(self, should_draw=True, should_choose_color=True):
                """
                Monika chooses a card to play

                IN:
                    should_draw - should Monika draw a card
                        if she's not found one to play?
                        (Default: True)
                    should_choose_color - should Monika choose a color
                        if the chosen card is a wild card?
                        (Default: True)

                OUT:
                    card if we found or drew one
                    or None if we don't want to (or can't) play a card this turn
                """
                # nested functions to analyse cards
                def analyse_numbers():
                    """
                    Goes through the cards data in the order we sorted it
                    and tries to find a number card that we can play

                    OUT:
                        card object if found a card, None otherwise

                    ASSUMES:
                        total_player_cards
                        sorted_cards_data
                        player_cards_data
                    """
                    MAX_ID = 4

                    if persistent._mas_game_nou_house_rules["points_to_win"]:
                        data_key = "value"

                    else:
                        data_key = "amount"

                    highest_value = float(sorted_cards_data[0][1][data_key])
                    reserved_card = None

                    for color_id in range(MAX_ID):
                        # let's see if we want to play a 0
                        if sorted_cards_data[color_id][1]["amount"] > 2:
                            # get the last card as a possible 0
                            last_card = self.hand[sorted_cards_data[color_id][1]["ids"][-1]]

                            if (
                                last_card.label == "0"# make sure it's a 0
                                and (
                                    last_card.color in self.player_cards_data["lacks_colors"]# and player doesn't have this color
                                    or (
                                        total_player_cards > 2
                                        and (
                                            (
                                                self.player_cards_data["has_color"] is not None
                                                and last_card.color != self.player_cards_data["has_color"]
                                            )
                                            or (
                                                self.player_cards_data["has_color"] is None
                                                and renpy.random.randint(1, 3) == 1# 1/3
                                            )
                                        )
                                    )
                                )
                            ):
                                # if we've passed all checks, let's see if we actually can play the card
                                if self.game.__is_matching_card(self, last_card):
                                    return last_card
                                # Otherwise fall through

                        # get this color name
                        this_color = sorted_cards_data[color_id][0].replace("num_", "")
                        # get total value (or amount) of cards with this color
                        # this_color_value = float(sorted_cards_data[color_id][1][data_key])
                        # get the id for the next loop
                        next_color_id = color_id + 1

                        # make sure we have more colors to check (idx from 0 to 3)
                        if next_color_id < MAX_ID:
                            # next_color = sorted_cards_data[next_color_id][0].replace("num_", "")
                            next_color_value = float(sorted_cards_data[next_color_id][1][data_key])

                        else:
                            # next_color = None
                            next_color_value = None

                        # Do we want to play anything else?
                        want_try_another_color = (
                            this_color == self.player_cards_data["has_color"]# the player has this colour
                            and next_color_value is not None
                            and (
                                highest_value == 0# all our cards are 0's
                                or (highest_value - next_color_value) / highest_value < 0.5# or the difference in values is less than 50%
                                or total_player_cards < 4# or the player is about to finish the game
                            )
                            and (
                                this_color != self.game.discardpile[-1].color# no reason not to play this card if it has the current color
                                or renpy.random.randint(1, 5) == 1# 1/5 to take the risk anyway
                            )
                        )

                        # try to play something
                        for id in sorted_cards_data[color_id][1]["ids"]:
                            card = self.hand[id]

                            if self.game.__is_matching_card(self, card):
                                if (
                                    want_try_another_color
                                    and reserved_card is None
                                ):
                                    # reserve this card
                                    reserved_card = card
                                    # check the next color
                                    break

                                else:
                                    return card

                    # If we are here, we couldn't find a good card to play
                    if (
                        reserved_card is not None# Do we have a reserved variant to play?
                        and (
                            total_cards < 4# play if we may win soon
                            or renpy.random.randint(1, 4) == 1# 1/4 to play anyway
                        )
                    ):
                        return reserved_card
                    # Or None if we can't don't want to play a number right now
                    return None

                def analyse_actions():
                    """
                    Goes through all action cards we have and tries to find
                    one that we can play this turn

                    OUT:
                        card object if we found one, None otherwise

                    ASSUMES:
                        sorted_cards_data
                        cards_data
                    """
                    def sortKey(id):
                        """
                        This is a sort key, it sorts

                        IN:
                            id - card id

                        OUT:
                            key to sort by
                        """
                        labels = (
                            "Skip",
                            "Draw Two",
                            "Reverse"
                        )
                        colors = [sorted_cards_data[i][0].replace("num_", "") for i in range(4)]

                        return [self.hand[id].label == label for label in labels] + [self.hand[id].color == color for color in colors]

                    action_cards_ids = []

                    for color in self.game.COLORS:
                        action_cards_ids += cards_data["act_" + color]["ids"]

                    action_cards_ids.sort(key=sortKey, reverse=True)

                    for id in action_cards_ids:
                        card = self.hand[id]

                        if self.game.__is_matching_card(self, card):
                            return card

                    return None

                def analyse_wilds(label=None):
                    """
                    Return one of wilds we have

                    IN:
                        label - card label either 'wd4' or 'wcc'
                            (Default: None - any of wild cards)

                    OUT:
                        card object if we found one, None otherwise

                    ASSUMES:
                        cards_data
                    """
                    if not label:
                        wild_cards_ids = cards_data["wd4"]["ids"] + cards_data["wcc"]["ids"]

                    else:
                        wild_cards_ids = cards_data[label]["ids"]

                    # we don't have any wild cards
                    if not wild_cards_ids:
                        return None

                    card = self.hand[renpy.random.choice(wild_cards_ids)]

                    if self.game.__is_matching_card(self, card):
                        return card

                    # we should never get to this
                    return None

                def analyse_cards(func_list):
                    """
                    Analyses all cards we have using funcs in func_list and returns first
                    appropriate card we want and can play in this turn

                    IN:
                        func_list - a list/tuple of tuples with func, args and kwargs,
                            we call those to find the card

                    OUT:
                        card if we found one,
                        or None if no card was found
                    """
                    for func, args, kwargs in func_list:
                        card = func(*args, **kwargs)

                        if card is not None:
                            return card

                    return None

                cards_data = self.__get_cards_data()

                total_cards = len(self.hand)
                total_player_cards = len(self.game.player.hand)

                # Monika has to skip turn
                if self.should_skip_turn:
                    # Let's try to play a defensive card
                    if persistent._mas_game_nou_house_rules["points_to_win"]:
                        sorted_cards_data = self.__sort_cards_data(cards_data)

                    else:
                        sorted_cards_data = self.__sort_cards_data(cards_data, values_sort_order=["amount"])

                    action_cards_ids = []

                    # make a list with action cards ordered by colors values
                    for i in reversed(range(4)):
                        # NOTE: 0-3 items are number cards, we start from less common ones
                        # to get rid of them
                        color = sorted_cards_data[i][0].replace("num_", "")
                        action_cards_ids += cards_data["act_" + color]["ids"]

                    # now try to play actions from our sorted list
                    for id in action_cards_ids:
                        card = self.hand[id]

                        if self.game.__is_matching_card(self, card):
                            # NOTE: Since this is the reflect flow, you can't play a wild card here
                            # the only way to reflect other special cards is to play an appropriate ACTION card (not WILD card)
                            # if (
                            #     should_choose_color
                            #     and card.type == "wild"
                            # ):
                            #     card.color = self.choose_color(ignored_card=card)

                            return card

                    # Monika doesn't have the right card, and should draw some more
                    if (
                        self.should_draw_cards
                        and should_draw
                    ):
                        self.game.deal_cards(self, self.should_draw_cards)
                        # # # FALL THROUGH

                # Just Monika's turn
                else:
                    # We have a card we wanted to play
                    if (
                        self.queued_card is not None
                        and self.game.__is_matching_card(self, self.queued_card)
                    ):
                        # Set the color if needed
                        if (
                            should_choose_color
                            and self.queued_card.type == "wild"
                        ):
                            self.chosen_color = self.choose_color(ignored_card=self.queued_card)

                        return self.queued_card

                    # We don't have forsed card or we can't play it
                    else:
                        # try to play the last card
                        if total_cards == 1:
                            card = self.hand[0]

                            if self.game.__is_matching_card(self, card):
                                # Set the color if needed
                                if (
                                    should_choose_color
                                    and card.type == "wild"
                                ):
                                    self.chosen_color = self.choose_color(ignored_card=card)

                                return card

                        else:
                            if persistent._mas_game_nou_house_rules["points_to_win"]:
                                sorted_cards_data = self.__sort_cards_data(cards_data)

                            else:
                                sorted_cards_data = self.__sort_cards_data(cards_data, values_sort_order=["amount"])

                            # the player is close to victory, need to play more aggressive
                            # TODO: use struct here when we get py3 support
                            if (
                                total_cards > 7
                                or total_player_cards < 4
                            ):
                                analysis = (
                                    (
                                        analyse_wilds,
                                        (),
                                        {"label": "wd4"}
                                    ),
                                    (
                                        analyse_actions,
                                        (),
                                        {}
                                    ),
                                    (
                                        analyse_numbers,
                                        (),
                                        {}
                                    ),
                                    (
                                        analyse_wilds,
                                        (),
                                        {"label": "wcc"}
                                    )
                                )

                            # standart logic
                            else:
                                analysis = (
                                    (
                                        analyse_numbers,
                                        (),
                                        {}
                                    ),
                                    (
                                        analyse_actions,
                                        (),
                                        {}
                                    ),
                                    (
                                        analyse_wilds,
                                        (),
                                        {}
                                    )
                                )

                            card = analyse_cards(analysis)

                            if card is not None:
                                # Set the color if needed
                                if (
                                    should_choose_color
                                    and card.type == "wild"
                                ):
                                    self.chosen_color = self.choose_color(ignored_card=card)

                                return card

                        # Come here when Monika has nothing to play (or doesn't want to), must draw a card, then
                        if should_draw:
                            self.game.deal_cards(self)
                            card = self.hand[-1]

                            if (
                                self.game.__is_matching_card(self, card)
                                # don't play it if it will make the player draw a card on the next turn
                                and (
                                    # but always play if we have just 2 cards left
                                    len(self.hand) < 3
                                    # play if the player may have that color
                                    or self.game.discardpile[-1].color not in self.player_cards_data["lacks_colors"]
                                    # 1/5 to play anyway
                                    or renpy.random.randint(1, 5) == 1
                                )
                            ):
                                # Set the color if needed
                                if (
                                    should_choose_color
                                    and card.type == "wild"
                                ):
                                    self.chosen_color = self.choose_color(ignored_card=card)

                                return card

                # Come here when we don't want to/can't play a card
                return None

            def play_card(self, card):
                """
                Inner wrapper around play_card
                NOTE: we do only certain checks here

                IN:
                    card - card to play
                """
                if not card:
                    return

                if card is self.queued_card:
                    self.queued_card = None

                self.game.play_card(self, self.game.player, card)

                self.game.__win_check(self)

                if (
                    self.game.discardpile[-1].type == "wild"
                ):
                    self.game.discardpile[-1].color = self.chosen_color
                    self.chosen_color = None

            def choose_reaction(self, next_card_to_play):
                """
                Helps Monika choose a dialogue based on the state of the game
                NOTE: 'NOU' is handled differently, right in announce_reaction(), w/o corresponding reactions from here

                TODO: reaction when you both are drawing cards
                    because no one has a card with the current color
                TODO: reactions when Monika reflected a card on her 1st turn
                    (the player had (had not) to skip their turn)
                TODO: reactions when the player reflected a card on their 1st turn

                IN:
                    next_card_to_play - the next card Monika's going to play
                        (we base reaction on it)
                """
                # # # Monika is going to reflect an action card
                if (
                    next_card_to_play is not None
                    and self.should_skip_turn
                    and len(self.game.game_log) > 1# see if there were enough turns
                    and self.game.game_log[-2]["played_card"] is not None# check if the player played something
                    and next_card_to_play.label == self.game.game_log[-2]["played_card"].label# compare the labels as this is the only way to reflect an act
                ):
                    # # # Does Monika reflect a card that reflected a wd4 before?
                    # Monika played a wd4 > the player reflected > Monika reflected
                    if (
                        len(self.game.game_log) > 2
                        and self.game.game_log[-3]["played_card"] is not None# see if Monika played wd4 before
                        and self.game.game_log[-3]["played_card"].label == "Wild Draw Four"
                    ):
                        reaction = {
                            "type": self.game.MONIKA_REFLECTED_WDF,
                            "chances_to_be_shown": 0
                        }

                    # someone played a wd4 > ... > Monika reflected > the player reflected > Monika reflected
                    elif (
                        self.reactions
                        and self.reactions[-1]["type"] == self.game.MONIKA_REFLECTED_WDF
                        and len(self.game.game_log) > 1
                        and self.game.game_log[-2]["played_card"] is not None# see if the player played something
                    ):
                        reaction = {"type": self.game.MONIKA_REFLECTED_WDF}

                        chances_to_be_shown = self.reactions[-1]["chances_to_be_shown"] + 1
                        reaction["chances_to_be_shown"] = chances_to_be_shown if chances_to_be_shown < 3 else 2

                    # # # Monika does not
                    # it's just the player played an act > Monika reflected
                    else:
                        reaction = {"type": self.game.MONIKA_REFLECTED_ACT}

                        # Monika keeps track on series of reactions
                        if (
                            self.reactions
                            and self.reactions[-1]["type"] == self.game.MONIKA_REFLECTED_ACT
                        ):
                            if (
                                len(self.reactions) > 1
                                and self.reactions[-2]["type"] == self.game.MONIKA_REFLECTED_ACT
                            ):
                                reaction["chances_to_be_shown"] = 2

                            else:
                                reaction["chances_to_be_shown"] = 1

                        else:
                            reaction["chances_to_be_shown"] = 0

                    reaction["turn"] = self.game.current_turn
                    reaction["monika_card"] = next_card_to_play
                    reaction["player_card"] = self.game.game_log[-2]["played_card"]
                    reaction["shown"] = False

                    self.reactions.append(reaction)

                    return reaction

                # # # Monika can't reflect an action card from the Player
                if (
                    next_card_to_play is None
                    and self.should_skip_turn
                    and len(self.game.game_log) > 1# see if there were enough turns
                    and self.game.game_log[-2]["played_card"] is not None# check if the player played something
                    and self.game.game_log[-2]["played_card"].type == "action"# make sure it was an act
                ):
                    # # # the player reflected a wd4 before
                    # Someone played wd4 > ... > the player reflected > Monika fails to reflect
                    if (
                        self.reactions
                        and self.reactions[-1]["type"] == self.game.MONIKA_REFLECTED_WDF
                    ):
                        reaction = {
                            "type": self.game.PLAYER_REFLECTED_WDF,
                            "turn": self.game.current_turn,
                            "monika_card": None,
                            "player_card": self.game.game_log[-2]["played_card"],
                            "shown": False
                        }

                        chances_to_be_shown = self.reactions[-1]["chances_to_be_shown"] + 1# use seen_count + 1 from the previous MONIKA_REFLECTED_WDF reaction
                        reaction["chances_to_be_shown"] = chances_to_be_shown if chances_to_be_shown < 3 else 2

                        self.reactions.append(reaction)

                        return reaction

                    # # # the player reflected an act card before
                    # Someone played an act > ... > the player reflected > Monika failed to reflect
                    elif (
                        self.reactions
                        and self.reactions[-1]["type"] == self.game.MONIKA_REFLECTED_ACT
                    ):
                        reaction = {
                            "type": self.game.PLAYER_REFLECTED_ACT,
                            "turn": self.game.current_turn,
                            "monika_card": None,
                            "player_card": self.game.game_log[-2]["played_card"],
                            "shown": False
                        }

                        chances_to_be_shown = self.reactions[-1]["chances_to_be_shown"] + 1# use seen_count + 1 from the previous MONIKA_REFLECTED_ACT reaction
                        reaction["chances_to_be_shown"] = chances_to_be_shown if chances_to_be_shown < 3 else 2

                        self.reactions.append(reaction)

                        return reaction

                    # Monika played an act > the player reflected > Monika failed to reflect
                    elif (
                        len(self.game.game_log) > 2# did we play enough turns?
                        and self.game.game_log[-3]["played_card"] is not None# did Monika played a card back then?
                        and self.game.game_log[-3]["played_card"].label == self.game.game_log[-2]["played_card"].label# Does it have the same label as the player's last cart?
                    ):
                        reaction = {
                            "type": self.game.PLAYER_REFLECTED_ACT,
                            "turn": self.game.current_turn,
                            "monika_card": None,
                            "player_card": self.game.game_log[-2]["played_card"],
                            "chances_to_be_shown": 0,# for this one always use seen_count 0
                            "shown": False
                        }

                        self.reactions.append(reaction)

                        return reaction

                    # NOTE: There's a possibility that we didn't return yet,
                    # so we'll have to fall through remaining checks

                # # # Monika mirrors a WDF card
                if (
                    next_card_to_play is not None
                    and next_card_to_play.label == "Draw Two"# did Monika played a d2 to reflect the wd4?
                    and self.should_skip_turn# and she has to skip her turn
                    and len(self.game.game_log) > 1
                    and self.game.game_log[-2]["played_card"] is not None
                    and self.game.game_log[-2]["played_card"].label == "Wild Draw Four"# and the player played a wd4
                ):
                    reaction = {
                        "type": self.game.MONIKA_REFLECTED_WDF,
                        "turn": self.game.current_turn,
                        "monika_card": next_card_to_play,
                        "player_card": self.game.game_log[-2]["played_card"],
                        "chances_to_be_shown": 0,
                        "shown": False
                    }

                    # NOTE: DON'T DELETE THIS
                    # turns = 8
                    # if sum(reaction["type"] == self.game.MONIKA_REFLECTED_WDF and reaction["turn"] >= self.game.current_turn - 2 * turns for reaction in self.reactions[-turns:]):
                    #     reaction["chances_to_be_shown"] = 1
                    # else:
                    #     reaction["chances_to_be_shown"] = 0

                    self.reactions.append(reaction)

                    return reaction

                # # # The Player mirrored a WDF card (and Monika can't reflect it back)
                if (
                    next_card_to_play is None# Monika can't play a defensive card?
                    and self.should_skip_turn# and should skip this turn?
                    and len(self.game.game_log) > 2
                    and self.game.game_log[-3]["played_card"] is not None
                    and self.game.game_log[-3]["played_card"].label == "Wild Draw Four"# Monika played a wd4 in her previous turn
                    and self.game.game_log[-2]["played_card"] is not None
                    and self.game.game_log[-2]["played_card"].label == "Draw Two"# and the player played a d2
                ):
                    reaction = {
                        "type": self.game.PLAYER_REFLECTED_WDF,
                        "turn": self.game.current_turn,
                        "monika_card": None,
                        "player_card": self.game.game_log[-2]["played_card"],
                        "chances_to_be_shown": 0,
                        "shown": False
                    }

                    self.reactions.append(reaction)

                    return reaction

                # # # Monika reflects a WCC card
                if (
                    next_card_to_play is not None
                    and next_card_to_play.type == "wild"# Monika is going to play a Wild card, NOTE: this maybe wd4 OR wcc
                    and len(self.game.game_log) > 1
                    and self.game.game_log[-2]["played_card"] is not None
                    and self.game.game_log[-2]["played_card"].label == "Wild"# and the player played a Wild card before (so reflect)
                ):
                    reaction = {
                        "type": self.game.MONIKA_REFLECTED_WCC,
                        "turn": self.game.current_turn,
                        "monika_card": next_card_to_play,
                        "player_card": self.game.game_log[-2]["played_card"],
                        "shown": False
                    }

                    if (
                        self.reactions
                        and self.reactions[-1]["type"] == self.game.MONIKA_REFLECTED_WCC
                    ):
                        if (
                            len(self.reactions) > 1
                            and self.reactions[-2]["type"] == self.game.MONIKA_REFLECTED_WCC
                        ):
                            reaction["chances_to_be_shown"] = 2

                        else:
                            reaction["chances_to_be_shown"] = 1

                    else:
                        reaction["chances_to_be_shown"] = 0

                    self.reactions.append(reaction)

                    return reaction

                # # # The Player reflected a WCC card
                if (
                    (
                        next_card_to_play is None# if this is the player's reflect, then Monika either doesn't play anything
                        or next_card_to_play.type != "wild"# or plays a non-wild card
                    )
                    and len(self.game.game_log) > 2
                    and self.game.game_log[-3]["played_card"] is not None# see if they reflected another card from Monika by that
                    and self.game.game_log[-3]["played_card"].label == "Wild"# more exactly wcc
                    and self.game.game_log[-2]["played_card"] is not None
                    and self.game.game_log[-2]["played_card"].label == "Wild"# check if the player played a wcc
                ):
                    reaction = {
                        "type": self.game.PLAYER_REFLECTED_WCC,
                        "turn": self.game.current_turn,
                        "monika_card": next_card_to_play,
                        "player_card": self.game.game_log[-2]["played_card"],
                        "shown": False
                    }

                    if (
                        self.reactions
                        and self.reactions[-1]["type"] == self.game.MONIKA_REFLECTED_WCC
                    ):
                        chances_to_be_shown = self.reactions[-1]["chances_to_be_shown"] + 1# use seen_count + 1 from the previous MONIKA_REFLECTED_WCC reaction
                        reaction["chances_to_be_shown"] = chances_to_be_shown if chances_to_be_shown < 3 else 2

                    else:
                        reaction["chances_to_be_shown"] = 0

                    self.reactions.append(reaction)

                    return reaction

                # Monika plays a wild card (basically announcing the color)
                if (
                    next_card_to_play is not None
                    and next_card_to_play.type == "wild"
                    and len(self.hand) > 1# No need to announce the color if you won lol
                ):
                    reaction = {
                        "type": self.game.MONIKA_PLAYED_WILD,
                        "turn": self.game.current_turn,
                        "monika_card": next_card_to_play,
                        "player_card": self.game.game_log[-2]["played_card"] if len(self.game.game_log) > 1 else None,
                        "chances_to_be_shown": 0,
                        "shown": False
                    }

                    self.reactions.append(reaction)

                    return reaction

                # Monika has nothing to say
                reaction = {
                    "type": self.game.NO_REACTION,
                    "turn": self.game.current_turn,
                    "monika_card": next_card_to_play,
                    "player_card": self.game.game_log[-2]["played_card"] if len(self.game.game_log) > 1 else None,
                    "chances_to_be_shown": 0,
                    "shown": False
                }

                self.reactions.append(reaction)

                return reaction

            def __handle_nou_logic(self, current_reaction):
                """
                Handles nou logic for Monika

                IN:
                    current_reaction - current Monika's reaction

                OUT:
                    tuple of 2 booleans:
                        has_yelled_nou - whether or not Monika yelled 'NOU' this turn
                        has_reminded_yell_nou - whether or not Monika reminded the player to yell 'NOU' this turn
                """
                def should_miss_this_nou():
                    """
                    An inner method to check if Monika misses/wants to let slide this nou check

                    OUT:
                        boolean - True/False

                    ASSUMES:
                        mas_nou.monika_win_streak
                        persistent._mas_game_nou_abandoned
                        persistent._mas_game_nou_house_rules
                        persistent._mas_game_nou_points['Player']
                    """
                    return (
                        (
                            (
                                persistent._mas_game_nou_abandoned > 2
                                or (
                                    persistent._mas_game_nou_house_rules["points_to_win"] > 0
                                    and get_player_points_percentage("Player") <= 0.2
                                    and get_player_points_percentage("Monika") >= 0.8
                                )
                                or (
                                    persistent._mas_game_nou_house_rules["points_to_win"] == 0
                                    and monika_win_streak > 2
                                )
                            )
                            and renpy.random.randint(1, 100) <= self.HIGHT_MISSING_NOU_CHANCE
                        )
                        or renpy.random.randint(1, 100) <= self.LOW_MISSING_NOU_CHANCE
                    )

                # Predefine as False
                has_yelled_nou = False
                has_reminded_yell_nou = False

                # Does Monika want to say nou?
                if (
                    current_reaction["monika_card"] is not None# Monika's going to play a card
                    and not self.yelled_nou
                    and len(self.hand) == 2# and it's her second last card
                    and not should_miss_this_nou()
                ):
                    has_yelled_nou = True

                    self.yelled_nou = True
                    self.should_play_card = True
                    self.nou_reminder_timeout = 0
                    nou_quip = renpy.random.choice(self.game.QUIPS_MONIKA_YELLS_NOU)
                    renpy.say(m, nou_quip, interact=True)

                # Can Monika catch the player for not saying nou?
                if (
                    not self.game.player.yelled_nou
                    and self.game.player.nou_reminder_timeout > self.game.current_turn
                    and len(self.game.player.hand) == 1
                    and not should_miss_this_nou()
                ):
                    has_reminded_yell_nou = True

                    remind_quip = renpy.random.choice(self.game.QUIPS_PLAYER_FORGOT_YELL_NOU)
                    # add the prefix if Monika has said something prior to this
                    if has_yelled_nou:
                        remind_quip = "...And speaking of NOU...{w=0.5}" + remind_quip

                    renpy.say(m, remind_quip, interact=True)
                    # she caught you, draw 2 cards
                    self.game.deal_cards(self.game.player, amount=2, smooth=False, mark_as_drew_card=False)
                    renpy.pause(0.5, hard=True)

                return has_yelled_nou, has_reminded_yell_nou

            def announce_reaction(self, reaction):
                """
                A wrapper around renpy.say for Monika's reactions

                Here we check if the reaction passes rng check, add modifiers to it,
                    and handle 'NOU' quips

                IN:
                    reaction - reaction to announce
                """
                # Announcing nou isn't a reaction, but simple quips
                # That's because it has kind of priority over reactions
                # and behave differently from them
                monika_yelled_nou, monika_reminded_yell_nou = self.__handle_nou_logic(reaction)

                if (
                    reaction["type"] != self.game.NO_REACTION
                    and (
                        # these 2 override all the reactions
                        not monika_yelled_nou
                        and not monika_reminded_yell_nou
                    )
                ):
                    reaction_map = self.game.REACTIONS_MAP[reaction["type"]]
                    total_reactions = len(reaction_map)

                    # correct chances_to_be_shown if needed
                    if reaction["chances_to_be_shown"] < 0:
                        chances_to_be_shown = 0

                    elif reaction["chances_to_be_shown"] > total_reactions - 1:
                        chances_to_be_shown = total_reactions - 1

                    else:
                        chances_to_be_shown = reaction["chances_to_be_shown"]

                    # check if Monika wants to say this
                    chance_to_trigger = self.game.REACTION_CHANCES_MAP[chances_to_be_shown]
                    if (
                        reaction["type"] == self.game.MONIKA_PLAYED_WILD# always say this one since the player needs to know the current color
                        or renpy.random.randint(1, 100) <= chance_to_trigger# otherwise do rng check
                    ):
                        # if we passed all checks, mark this reaction as shown
                        reaction["shown"] = True

                        # we make a new copy because we may modify it here
                        reaction_quips = list(reaction_map[chances_to_be_shown])

                        # # # START MODIFIERS
                        additional_quips = None

                        if reaction["type"] == self.game.MONIKA_REFLECTED_ACT:
                            if (
                                chances_to_be_shown == 2
                                and persistent._mas_game_nou_house_rules["stackable_d2"]
                            ):
                                additional_quips = self.game.REACTIONS_MAP_MONIKA_REFLECTED_ACT_MODIFIER_1

                            elif (
                                chances_to_be_shown == 0
                                and reaction["monika_card"] is not None
                            ):
                                if reaction["monika_card"].label == "Draw Two":
                                    additional_quips = self.game.REACTIONS_MAP_MONIKA_REFLECTED_ACT_MODIFIER_2

                                # elif reaction["monika_card"].label in ("Skip", "Reverse"):
                                else:
                                    additional_quips = self.game.REACTIONS_MAP_MONIKA_REFLECTED_ACT_MODIFIER_3

                        elif (
                            reaction["type"] == self.game.MONIKA_REFLECTED_WDF
                            and chances_to_be_shown == 2
                            and persistent._mas_game_nou_house_rules["stackable_d2"]
                        ):
                            additional_quips = self.game.REACTIONS_MAP_MONIKA_REFLECTED_WD4_MODIFIER_1

                        elif (
                            reaction["type"] == self.game.MONIKA_REFLECTED_WCC
                            and chances_to_be_shown == 2
                            and self.chosen_color == "green"
                        ):
                            additional_quips = self.game.REACTIONS_MAP_MONIKA_REFLECTED_WCC_MODIFIER_1

                        # add modifiers if any
                        if additional_quips is not None:
                            reaction_quips += additional_quips

                        # # # END MODIFIERS

                        # choose the one we will use
                        quip = renpy.random.choice(
                            reaction_quips
                        )

                        # say it line by line
                        for line in quip:
                            renpy.say(m, line, interact=True)

                # Additional lines so the player always knows which color it is now
                if (
                    reaction["type"] == self.game.MONIKA_REFLECTED_WCC
                    or (
                        reaction["type"] == self.game.MONIKA_PLAYED_WILD
                        and (
                            monika_yelled_nou
                            or monika_reminded_yell_nou
                        )
                    )
                ):
                    color_quip = renpy.random.choice(self.game.QUIPS_MONIKA_ANNOUNCE_COLOR_AFTER_REFLECT)
                    renpy.say(m, color_quip, interact=True)

# END CLASS DEF

# UTIL FUNCTIONS
init 5 python in mas_nou:
        def give_points():
            """
            Gives points to the winner

            ASSUMES:
                mas_nou.game
                mas_nou.winner
            """
            if winner in ("Monika", "Surrendered"):
                persist_key = "Monika"
                loser = game.player

            elif winner == "Player":
                persist_key = "Player"
                loser = game.monika

            # this should never happen
            else:
                return

            # we don't forget to add points if you win the game with a d2 or wd4
            if loser.should_draw_cards:
                game.deal_cards(
                    player=loser,
                    amount=loser.should_draw_cards,
                    smooth=False,
                    mark_as_drew_card=False,
                    reset_nou_var=False
                )

            for card in loser.hand:
                persistent._mas_game_nou_points[persist_key] += card.value

        def reset_points():
            """
            Resets the persistent var to 0 for both Monika and the player
            """
            persistent._mas_game_nou_points["Monika"] = 0
            persistent._mas_game_nou_points["Player"] = 0

        def get_player_points_percentage(player_persist_key):
            """
            Returns proportion of the corrent points of a player to the maximum possible score

            IN:
                player_persist_key - persistent key for the player
                    ('Monika' or 'Player')

            OUT:
                float as proportion (0.0 - 1.0)

            ASSUMES:
                persistent._mas_game_nou_house_rules['points_to_win'] > 0
            """
            return float(persistent._mas_game_nou_points[player_persist_key]) / float(persistent._mas_game_nou_house_rules["points_to_win"])

# Our events
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_introduce_nou_house_rules"
        )
    )

label monika_introduce_nou_house_rules:
    m 3eud "Oh [player], I almost forgot!"
    m 3eua "If you ever feel like those official rules aren't fun enough...{w=0.5}{nw}"
    extend 1kua "just let me know and we'll play with our own house rules."
    $ mas_unlockEVL("monika_change_nou_house_rules", "EVE")
    return

# House rules unlocked after you finish your first game
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_change_nou_house_rules",
            prompt="Let's change our house rules for NOU",
            category=["games"],
            pool=True,
            unlocked=False,
            conditional="persistent._mas_game_nou_wins['Monika'] or persistent._mas_game_nou_wins['Player']",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock": None},
            aff_range=(mas_aff.NORMAL, None)# you can play NoU only at norm+
        )
    )

label monika_change_nou_house_rules:
    if (
        persistent._mas_game_nou_house_rules["points_to_win"]
        and (
            persistent._mas_game_nou_points["Monika"]
            or persistent._mas_game_nou_points["Player"]
        )
    ):
        m 3eud "[player], we still haven't finished our game."
        m 1euc "If you want to play with new rules, then we'll have to start a new game next time."

    else:
        m 1eub "Of course."

    label .menu_loop:
        python:
            menu_items = [
                (
                    _("I'd like to change the number of points required to win."),
                    "points_to_win",
                    False,
                    False
                ),
                (
                    _("I'd like to change the number of cards we start each round with."),
                    "starting_cards",
                    False,
                    False
                ),
                (
                    _("I'd like to play with stackable Draw 2's.") if not persistent._mas_game_nou_house_rules["stackable_d2"] else _("I'd like to play with non-stackable Draw 2's."),
                    "stackable_d2",
                    False,
                    False
                ),
                (
                    _("I'd like to play with unrestricted Wild Draw 4's.") if not persistent._mas_game_nou_house_rules["unrestricted_wd4"] else _("I'd like to play with restricted Wild Draw 4's."),
                    "unrestricted_wd4",
                    False,
                    False
                )
            ]

            if not (
                persistent._mas_game_nou_house_rules["points_to_win"] == 200
                and persistent._mas_game_nou_house_rules["starting_cards"] == 7
                and persistent._mas_game_nou_house_rules["stackable_d2"] == False
                and persistent._mas_game_nou_house_rules["unrestricted_wd4"] == False
            ):
                menu_items.append((_("I'd like to go back to the classic rules."), "restore", False, False))

            final_items = (
                (_("Can you explain these house rules?"), "explain", False, False, 20),
                (_("Nevermind"), False, False, False, 0)
            )

        show monika 1eua at t21 zorder MAS_MONIKA_Z

        $ renpy.say(m, _("What kind of rule would you like to change?"), interact=False)

        call screen mas_gen_scrollable_menu(menu_items, mas_ui.SCROLLABLE_MENU_TXT_MEDIUM_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, *final_items)

        show monika 1eua at t11 zorder MAS_MONIKA_Z

        if not _return:
            m 1eua "Oh, alright."
            $ del menu_items, final_items
            return

        elif _return == "points_to_win":
            m 1eub "Alright!"
            call monika_change_nou_house_rules.change_points_to_win_loop

        elif _return == "starting_cards":
            m 1eub "Alright!"
            call monika_change_nou_house_rules.change_starting_cards_loop

        elif _return == "stackable_d2":
            if not persistent._mas_game_nou_house_rules["stackable_d2"]:
                m 1tub "Okay, but I must warn you that that might go against you~"

            else:
                m 1ttu "Afraid that I'll make you draw all the cards?~"
                m 1hub "Ahaha~ I'm just kidding!"

            $ persistent._mas_game_nou_house_rules["stackable_d2"] = not persistent._mas_game_nou_house_rules["stackable_d2"]

        elif _return == "unrestricted_wd4":
            if not persistent._mas_game_nou_house_rules["unrestricted_wd4"]:
                # m "Oh, you better be ready for this one, [player]~"
                m 1eua "That sounds fun."

            else:
                m 1eua "Back to the classic, I see."

            $ persistent._mas_game_nou_house_rules["unrestricted_wd4"] = not persistent._mas_game_nou_house_rules["unrestricted_wd4"]

        elif _return == "restore":
            m 3eub "Okay! Then settled!"

            python:
                persistent._mas_game_nou_house_rules["points_to_win"] = 200
                persistent._mas_game_nou_house_rules["starting_cards"] = 7
                persistent._mas_game_nou_house_rules["stackable_d2"] = False
                persistent._mas_game_nou_house_rules["unrestricted_wd4"] = False

                store.mas_nou.reset_points()

                del menu_items, final_items

            return

        else:
            m 1eub "Sure!"
            m 1eua "Victory points is the number of points you need to reach to win the game."
            m 3eud "If you want to play without points, just choose '0'."
            m 1eua "We can also start each round with a different number of cards in our hands."
            m 3esa "For example, if you want longer games, we can start with 10 cards."
            m 1eua "{i}Stackable Draw 2's{/i} means that every time someone mirrors a Draw 2, the cards {i}stack{/i}...{w=0.3}{nw}"
            extend 4tsb "and the last unlucky person will have to draw all those cards."
            m 1eua "That also applies to Wild Draw 4's, since you use Draw 2's to reflect them."
            m 1ttu "Sounds fun, huh~"
            m 3eud "There's also a rule in the official set that allows you to play a Draw 4 only if you have no cards of the current color."
            m 1rtu "That...{w=0.3}sounds kinda boring, {w=0.2}{nw}"
            extend 3eua "so we can just ignore that rule if you want."
            m 1eua "And that's it!"

            jump monika_change_nou_house_rules.menu_loop

    $ store.mas_nou.reset_points()

    m 3eua "Is there anything else you'd like to change?{nw}"
    $ _history_list.pop()
    menu:
        m "Is there anything else you'd like to change?{fast}"

        "Yes.":
            jump monika_change_nou_house_rules.menu_loop

        "No.":
            m 2eub "Then let's play together soon~"

    $ del menu_items, final_items

    return

label .change_points_to_win_loop:
    $ ready = False
    while not ready:
        show monika 1eua at t11 zorder MAS_MONIKA_Z

        $ points_cap = store.mas_utils.tryparseint(
            renpy.input(
                "How many points would you like it to be?",
                allow=numbers_only,
                length=4
            ).strip("\t\n\r"),
            200
        )

        if points_cap < 0:
            m 2rksdla "[player], the game will never end if the goal is negative."
            m 7ekb "Try again, silly!"

        elif points_cap == 0:
            m 3eua "Oh, you just want to have quick games?"
            m 2tuu "Alright! But don't expect me to go easy on you~"
            $ persistent._mas_game_nou_house_rules["points_to_win"] = points_cap
            $ ready = True

        elif points_cap < 50:
            m 3rksdlb "Hmm, It doesn't make sense to play with a point total {i}that{/i} small."
            m 1eka "We can play without points if you wish.{nw}"
            $ _history_list.pop()
            menu:
                m "We can play without points if you wish.{fast}"

                "I'd like that.":
                    m 1eub "Oh, alright!"
                    $ persistent._mas_game_nou_house_rules["points_to_win"] = 0
                    $ ready = True

                "Nah.":
                    m 3eua "Then choose again."

        elif points_cap > 3000:
            m 2eka "Oh it's too much I think..."
            m 7eka "Let's leave it at 3000?{nw}"
            $ _history_list.pop()
            menu:
                m "Let's leave it at 3000?{fast}"

                "Alright.":
                    m 1eua "Settled."
                    $ persistent._mas_game_nou_house_rules["points_to_win"] = 3000
                    $ ready = True

                "Nah.":
                    m 3eua "Then choose again."

        else:
            m 3eub "Okay, from now on, whoever reaches [points_cap] points, wins!"
            $ persistent._mas_game_nou_house_rules["points_to_win"] = points_cap
            $ ready = True

    $ del ready, points_cap

    return

label .change_starting_cards_loop:
    $ ready = False
    while not ready:
        show monika 1eua at t11 zorder MAS_MONIKA_Z

        $ starting_cards = store.mas_utils.tryparseint(
            renpy.input(
                "How many cards would you like to start the game with?",
                allow=numbers_only,
                length=2
            ).strip("\t\n\r"),
            7
        )

        if starting_cards < 1:
            m 2rksdlb "We can't play cards without cards, [player]!"
            m 7ekb "Try again, silly~"

        elif starting_cards < 4:
            m 2eka "I don't think this will make sense, [player]..."
            m 7eka "Let's start with at least 4 cards?{nw}"
            $ _history_list.pop()
            menu:
                m "Let's start with at least 4 cards?{fast}"

                "Alright.":
                    $ persistent._mas_game_nou_house_rules["starting_cards"] = 4
                    $ ready = True

                "Nah.":
                    m 3eua "Then try again."

        elif starting_cards > 20:
            m 2hub "Ahaha, [player]! How do you think I'll hold all these cards?"
            m 7eua "Let's leave it at 20 cards?{nw}"
            $ _history_list.pop()
            menu:
                m "Let's leave it at 20 cards?{fast}"

                "Alright.":
                    $ persistent._mas_game_nou_house_rules["starting_cards"] = 20
                    $ ready = True

                "Nah.":
                    m 3eua "Then try again."

        else:
            $ _round = _("round") if persistent._mas_game_nou_house_rules["points_to_win"] else _("game")
            m 3eub "Okay, from now on, we will start each [_round!t] with [starting_cards] cards!"
            $ persistent._mas_game_nou_house_rules["starting_cards"] = starting_cards
            $ ready = True

    $ del ready, starting_cards

    return

# Explaining rules unlocked after you give Monika the deck
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_explain_nou_rules",
            prompt="Can you explain NOU rules to me?",
            category=["games"],
            pool=True,
            unlocked=False,
            conditional="renpy.seen_label('mas_reaction_gift_noudeck')",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock": None},
            aff_range=(mas_aff.NORMAL, None)# you can play NoU only at norm+
        )
    )

label monika_explain_nou_rules:
    m 1hua "Of cource, [player]."
    m 3eub "The game looks complicated at first, {w=0.1}{nw}"
    extend 4eub "but it's actually pretty simple."
    m 4eua "I'm sure if we play a few more games, you'll get the hang of it."

    if persistent._mas_game_nou_house_rules["starting_cards"] == 7:
        m 7esa "So we start the game with 7 cards."

    else:
        m 7esa "So since we're playing with house rules, we start the game with [persistent._mas_game_nou_house_rules[starting_cards]] cards."

    m 1esa "Your goal is to play all your cards before I play all of mine."
    m 3eub "To play a card you need to match it by the color or the text with the top card on the discard pile."
    m 3eua "If you can't play a card in your turn, you must draw one from the draw pile."
    m 1esa "You don't {i}have{/i} to play it, though."

    if persistent._mas_game_nou_house_rules["points_to_win"]:
        m 3eub "After you played a card or skipped your turn, my turn begins. And so on until someone wins the round."
        m 1eua "The winner is awarded with the points equal to the remaining cards in the opponent's hand."
        m "Then we play more rounds until one of us reaches the goal - [persistent._mas_game_nou_house_rules[points_to_win]] points."
        m 1esa "Such scoring makes the game more competitive and strategic."

    else:
        m 3eub "After you play a card or skip your turn, my turn begins and so on until someone wins the game."
        m 1esa "Such scoring makes the game quicker and more casual."

    m 3eub "One important rule is before playing your second last card, {w=0.2}{nw}"
    extend 7eub "you should yell 'NOU' so I can know that you're close to victory!"
    m 2rksdla "Well, I guess yelling won't work in our case..."
    m 7hub "But you can press a button to let me know!"
    m 1eua "If one of us forgot to say 'NOU,' the other can {i}remind{/i} them. That will make the unlucky person draw 2 more cards."
    m 3eub "Besides the {i}Number{/i} cards, there are also special cards known as {i}Action{/i} and {i}Wild{/i} cards."
    m 3eua "You can distinguish an Action card by its symbol, and a Wild card by its black color."
    m 1eua "These cards can make your opponent skip their turn or even draw more cards."
    m 1tsu "And by more, I mean 12 cards in a row."
    m 1eua "Wild cards don't have a color which means they can be placed on any card."

    if not persistent._mas_game_nou_house_rules["unrestricted_wd4"]:
        m 3eua "If you have no other cards with the color of the discard pile, that is."

    else:
        m 3eua "Usually, you can only play them if you have no other cards of the same color in the discard pile, but we're playing with our own rules."

    m 1eua "When you play any Wild card, you should choose what color you want to set for it."
    m "As powerful as Wild and Action cards may look, you can still save yourself from them."
    m 1eub "For example you can mirror a Wild Draw Four by playing a Draw Two with the new color."
    m 3eua "...Or you can play any Draw Two to mirror another Draw Two back to your opponent. The color won't matter in that case."
    m 1ekb "I hope all that will give you a better understanding of the game."
    m 1eku "But I don't think it's really about winning anyway."
    show monika 5hubla at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hubla "Ehehe~"
    return


# The game handling label
label mas_nou_game_start:
    if (
        persistent._mas_game_nou_house_rules["points_to_win"]
        and (
            persistent._mas_game_nou_points["Monika"] > 0
            or persistent._mas_game_nou_points["Player"] > 0
        )
    ):
        if store.mas_nou.winner is not None:
            m 1hua "Let's continue~"

        else:
            m 1hua "Want to finish our game?"
            m 3eua "Let me grab that note with our score.{w=0.2}.{w=0.2}.{w=0.2}{nw}"

    else:
        m 1eub "Let's start!~"

    $ store.mas_nou.game = store.mas_nou.NoU()

    # FALL THROUGH

label mas_nou_game_loop:
    # Hide UI
    window hide
    $ HKBHideButtons()
    $ disable_esc()
    # Transition to the desk
    scene bg cardgames desk onlayer master zorder 0
    # Show cards
    $ store.mas_nou.game.set_visible(True)
    # Show the game screens
    show screen nou_gui
    show screen nou_stats
    with Fade(0.2, 0, 0.2)
    $ renpy.pause(0.2, hard=True)
    # Do game preparations
    $ store.mas_nou.game.prepare_game()
    $ store.mas_nou.in_progress = True

    # Game loop
    while store.mas_nou.in_progress:
        $ store.mas_nou.game.game_loop()

    # FALL THROUGH

label mas_nou_game_end:
    # We finished the game
    $ store.mas_nou.in_progress = False
    # Hide cards
    $ store.mas_nou.game.set_visible(False)
    # Hide the game screens
    hide screen nou_stats
    hide screen nou_gui
    # Hide the desk, render spaceroom
    call spaceroom(scene_change=True, force_exp="monika 1eua")
    # Show UI
    $ enable_esc()
    $ HKBShowButtons()
    window auto

    python:
        if persistent._mas_game_nou_house_rules["points_to_win"]:
            _round = _("round")

        else:
            _round = _("game")

        dlg_choice = None

        if (
            store.mas_nou.winner != "Surrendered"
            and not seen_event("monika_introduce_nou_house_rules")
        ):
            pushEvent("monika_introduce_nou_house_rules")

    if store.mas_nou.winner == "Player":
        call mas_nou_reaction_player_wins_round

        python:
            store.mas_nou.give_points()
            persistent._mas_game_nou_abandoned = 0
            store.mas_nou.player_wins_this_sesh += 1
            store.mas_nou.player_win_streak += 1
            store.mas_nou.monika_win_streak = 0
            persistent.ever_won["nou"] = True

        if (
            persistent._mas_game_nou_house_rules["points_to_win"]
            and persistent._mas_game_nou_points["Player"] >= persistent._mas_game_nou_house_rules["points_to_win"]
        ):
            call mas_nou_reaction_player_wins_game

            $ store.mas_nou.reset_points()

            m 3eua "Would you like to play some more?{nw}"
            $ _history_list.pop()
            menu:
                m "Would you like to play some more?{fast}"

                "Sure.":
                    m 1hub "Yay!"
                    show monika 1hua zorder MAS_MONIKA_Z
                    python:
                        store.mas_nou.game.reset_game()
                        mas_assignModifyEVLPropValue("mas_nou", "shown_count", "+=", 1)

                    jump mas_nou_game_loop

                "Not right now.":
                    m 1hua "Okay, just let me know when you want to play again~"

            $ del dlg_choice, _round, store.mas_nou.game
            return

    elif store.mas_nou.winner == "Monika":
        call mas_nou_reaction_monika_wins_round

        python:
            store.mas_nou.give_points()
            persistent._mas_game_nou_abandoned = 0
            store.mas_nou.monika_wins_this_sesh += 1
            store.mas_nou.monika_win_streak += 1
            store.mas_nou.player_win_streak = 0

        if (
            persistent._mas_game_nou_house_rules["points_to_win"]
            and persistent._mas_game_nou_points["Monika"] >= persistent._mas_game_nou_house_rules["points_to_win"]
        ):
            call mas_nou_reaction_monika_wins_game

            $ store.mas_nou.reset_points()

            m 3eua "Would you like to play some more?{nw}"
            $ _history_list.pop()
            menu:
                m "Would you like to play some more?{fast}"

                "Sure.":
                    m 1hub "Yay!"
                    show monika 1hua zorder MAS_MONIKA_Z
                    python:
                        store.mas_nou.game.reset_game()
                        mas_assignModifyEVLPropValue("mas_nou", "shown_count", "+=", 1)

                    jump mas_nou_game_loop

                "Not right now.":
                    m 1hua "Okay, just let me know when you want to play again~"

            $ del dlg_choice, _round, store.mas_nou.game
            return

    else:
        # firstly deal with vars
        python:
            persistent._mas_game_nou_abandoned += 1
            store.mas_nou.player_win_streak = 0
            # silently add points to Monika
            store.mas_nou.give_points()
            if persistent._mas_game_nou_points["Monika"] >= persistent._mas_game_nou_house_rules["points_to_win"]:
                store.mas_nou.reset_points()

        call mas_nou_reaction_player_surrenders

        # we don't suggest to play again if the player does't want to play
        $ del dlg_choice, _round, store.mas_nou.game
        return

    m 3eua "Would you like to play another [_round!t]?{nw}"
    $ _history_list.pop()
    menu:
        m "Would you like to play another [_round!t]?{fast}"

        "Sure.":
            show monika 1hua zorder MAS_MONIKA_Z
            python:
                store.mas_nou.game.reset_game()
                mas_assignModifyEVLPropValue("mas_nou", "shown_count", "+=", 1)

            jump mas_nou_game_loop

        "Not right now.":
            m 1hua "Alright, let's play again soon~"

    $ del dlg_choice, _round, store.mas_nou.game

    return

# All end game reactions labels go here
label mas_nou_reaction_player_wins_round:
    if persistent._mas_game_nou_abandoned > 2:
        m 1hua "I'm glad you won this time..."
        m 3eub "Good job, [player]!"

    elif store.mas_nou.player_win_streak > 3:
        $ dlg_choice = renpy.random.randint(1, 3)

        if dlg_choice == 1:
            m 1wud "[player]...{w=0.5}you keep winning..."

            if len(store.mas_nou.game.monika.hand) > 2:
                m 1hksdlb "I have no chance against you!"

            else:
                m 1hksdlb "Give me a chance at least~"

        elif dlg_choice == 2:
            m 1eub "And another [_round!t]!"
            m 3hub "Incredible, [player]!"

        else:
            m 1wud "Wow! You won again!"
            m 3esa "Will you tell me your secret, [player]?"
            m 1hua "I want to win too~"

    elif store.mas_nou.player_win_streak > 2:
        $ dlg_choice = renpy.random.randint(1, 4)

        if dlg_choice == 1:
            m 1hub "And you won another [_round!t]!"
            m 3eub "You're really good!"

        elif dlg_choice == 2:
            m 4eub "Amazing, you won again!"
            m 1tsu "But I'm sure I'll win next [_round!t]."

        elif dlg_choice == 3:
            m 1hub "Incredible! Another win for you!"
            m 1eub "Don't relax, though. {w=0.5}{nw}"
            extend 1kua "I'm sure I'll win next time!"

        else:
            m 1tuu "You're lucky today."
            m 1hub "Ahaha~ Good job, [player]!"

    elif store.mas_nou.monika_win_streak > 3:
        $ dlg_choice = renpy.random.randint(1, 3)

        if dlg_choice == 1:
            m 3eua "I'm really glad you won this time~"

        elif dlg_choice == 2:
            m 1hua "I had a feeling you'd win~"
            m 3hub "Ehehe~ Good job!"

        else:
            if len(store.mas_nou.game.monika.hand) > 2:
                m 1tuu "Your luck must be back~"
                m 1hua "Well played! Ehehe~"

            else:
                m 1hub "Yay, you won!~"

    elif store.mas_nou.monika_win_streak > 2:
        $ dlg_choice = renpy.random.randint(1, 3)

        if dlg_choice == 1:
            m 1tsa "Oh, you started playing seriously?"
            m 1hub "Ahaha~"

        elif dlg_choice == 2:
            if len(store.mas_nou.game.monika.hand) < 3:
                m 1ruu "Ah... I almost won this one too!"
                m 3hua "Well played, [player]."

            else:
                m 1hub "You won, [player]!"
                if len(store.mas_nou.game.monika.hand) > 3:
                    m 3hub "That was amazing!"

        else:
            if store.mas_nou.game.current_turn > 40:
                m 2tub "You were really trying this time!"
                m 1hub "Great job, [player]!"

            else:
                m 1hua "And you won! Nice~"

    elif store.mas_nou.game.current_turn < 25:
        if store.mas_nou.player_win_streak > 0:
            $ dlg_choice = renpy.random.randint(1, 3)

            if dlg_choice == 1:
                m 1hub "Another quick win for you!"

                if renpy.random.randint(1, 4) == 1:
                    m 1kuu "But you better not relax, [player]~"

            elif dlg_choice == 2:
                m 1wuo "Wow, [player]!"
                m 1hksdlb "I can't keep up with you!"

            else:
                if len(store.mas_nou.game.monika.hand) > 3:
                    m 1rka "Maybe I should try a bit harder?~"
                    m 1hksdla "Ehehe, you keep finishing [_round!t]s before I can do anything."

                else:
                    m 1hfb "Ah...{w=0.2}I was so close!"
                    m 3efb "Good job, [player]!"

        elif (
            len(store.mas_nou.game.monika.hand) > 4
            or (
                not store.mas_nou.game.player.yelled_nou
                and renpy.random.randint(0, 1) == 1
            )
        ):
            m 4wuo "Wow!{w=0.2} Played all your cards already?"
            m 7husdlb "That was quick!"

        else:
            $ dlg_choice = renpy.random.randint(1, 3)

            if dlg_choice == 1:
                m 3hub "Well played!"

            elif dlg_choice == 2:
                m 3hub "Impressive, [player]!"

            else:
                m 3hub "That was a quick [_round!t] for you!"

    elif store.mas_nou.game.current_turn > 55:
        $ dlg_choice = renpy.random.randint(1, 3)

        if dlg_choice == 1:
            m 1esa "A quite long [_round!t], [player]."

            if len(store.mas_nou.game.monika.hand) < 4:
                if store.mas_nou.player_win_streak > 0:
                    m 1hua "And I almost won this time!"

                else:
                    m 1hua "And I almost won!"

                m 1hub "Ahaha~ Well played!"

            else:
                m 1hub "Well played!"

        elif dlg_choice == 2:
            m 1kuu "That was intense!"

        else:
            m 1hua "Ehehe~ {w=0.3}{nw}"
            extend 1eub "You're really good!"

    else:
        $ dlg_choice = renpy.random.randint(1, 4)

        if dlg_choice == 1:
            if store.mas_nou.player_win_streak > 0:
                m 1eub "You won again!"

            else:
                m 1eub "You won!~"

        elif dlg_choice == 2:
            m 1hub "This [_round!t] is yours!"

        elif dlg_choice == 3:
            m 2eub "And you won! Good job!"
            if renpy.random.randint(1, 6) > 5:
                m 2kuu "But don't expect to win everytime~"

        else:
            if store.mas_nou.monika_win_streak > 1:
                m 2eua "I'm glad you won this time~"

            m 3hub "Good job, [player]!"
    return

label mas_nou_reaction_player_wins_game:
    $ dlg_choice = renpy.random.randint(1, 4)

    if dlg_choice == 1:
        m 1eud "Oh! {w=0.2}{nw}"
        extend 3eub "Actually you won this game!"
        # 1lua instead?
        m 1ruu "I didn't notice you were so close to victory."
        m 3hua "Good job, ehehe~"

    elif dlg_choice == 2:
        m 3eub "Oh, and you won this game too!"
        m 1hua "Congratulations! Ehehe~"

    elif dlg_choice == 3:
        m 1rsc "Let's see.{w=0.2}.{w=0.2}.{w=0.2}{nw}"
        m 4eub "Oh, [player]! You won this game!"
        if mas_isMoniEnamored(higher=True) and renpy.random.randint(1, 2) == 1:
            m 1hub "I would give you a big hug if I were near you~"
            m 1hua "Ehehe~"
        else:
            m 1hua "That was fun!"

    else:
        m 4eub "...And you're the first who reached [persistent._mas_game_nou_house_rules[points_to_win]] points!"
        m 1hua "Congrats, [player]~"
    return

label mas_nou_reaction_monika_wins_round:
    if persistent._mas_game_nou_abandoned > 2:
        m 2wub "I won!~"
        m 7eka "Thanks for finishing this game, [player], {w=0.3}{nw}"
        extend 1hub "I'm sure you'll win next time!"

    elif store.mas_nou.player_win_streak > 3:
        $ dlg_choice = renpy.random.randint(1, 3)

        if dlg_choice == 1:
            if len(store.mas_nou.game.player.hand) > 4:
                m 1hub "I won!"
                m 1hksdla "..."
                m 1eka "Not without your help, I guess. Ehehe~"

            else:
                m 3tsb "Told you I'd win!"
                m 1tfu "Now it's time for you to draw cards."

        elif dlg_choice == 2:
            m 4sub "Ahaha! My luck is back~"

        else:
            m 4sub "There we go!"
            m 7hub "I finally won~"

    elif store.mas_nou.player_win_streak > 2:
        $ dlg_choice = renpy.random.randint(1, 3)

        if dlg_choice == 1:
            m 2tub "Don't relax, [player]~"

        elif dlg_choice == 2:
            m 1hua "I won!"

        else:
            m 1hub "Yay I won this time!~"

    elif store.mas_nou.monika_win_streak > 3:
        $ dlg_choice = renpy.random.randint(1, 3)

        if dlg_choice == 1:
            m 1hub "And another win for me!~"

        elif dlg_choice == 2:
            if len(store.mas_nou.game.player.hand) < 3:
                m 1eub "That was tough, [player]! {w=0.5}{nw}"
                extend 3eua "You almost won this time."

            else:
                m 1kua "I have a feeling you'll win next [_round!t]~"

        else:
            if len(store.mas_nou.game.player.hand) < 3:
                m 1huu "Well played, [player]. But the win is mine again~"

            else:
                m 3eub "That was fun!"
                m 1eka "I hope you're enjoying playing with me, [player]~"
                m 1kua "Maybe next time you'll win."

    elif store.mas_nou.monika_win_streak > 2:
        $ dlg_choice = renpy.random.randint(1, 3)

        if dlg_choice == 1:
            m 1hua "Ehehe~ Another win for me~"

        elif dlg_choice == 2:
            if len(store.mas_nou.game.player.hand) < 3:
                m 3eub "You were quite close this time, [player]."

            else:
                m 2tuu "Should I go easier on you?"
                m 7hub "Ahaha, just kidding, [player]~"

        else:
            m 4hub "I won again!"

    elif store.mas_nou.game.current_turn < 25:
        if store.mas_nou.monika_win_streak > 0:
            $ dlg_choice = renpy.random.randint(1, 3)

            if dlg_choice == 1:
                m 4hub "Another quick win for me!"

            elif dlg_choice == 2:
                m 1tub "Can't keep up with me, huh?~"

            else:
                m 1eub "Yay, I won again!"

        else:
            $ dlg_choice = renpy.random.randint(1, 2)

            if dlg_choice == 1:
                m 1wub "Yay, I won~"

            else:
                m 3eub "That was quick!"

    elif store.mas_nou.game.current_turn > 55:
        $ dlg_choice = renpy.random.randint(1, 3)

        if dlg_choice == 1:
            m 1eub "That was a long [_round!t]!"

            if len(store.mas_nou.game.player.hand) < 4:
                if store.mas_nou.monika_win_streak > 0:
                    m 3eua "You almost won this time."

                else:
                    m 3eua "You almost won."

                m 3hub "Ehehe~ Well played!"

            else:
                m 3hub "Well played!"

        elif dlg_choice == 2:
            m 1hub "That was intense!"

        else:
            if len(store.mas_nou.game.player.hand) > 4:
                m 1tsb "Not bad, [player]."
                m 3tub "I think you could even have won this time, {w=0.5}{nw}"
                extend 1tuu "if not for all those cards you drew."
                m 1hub "Ahaha~"

            else:
                m 1wub "Oh, I won!"

    else:
        if store.mas_nou.monika_win_streak > 0:
            m 1hua "I won again~"

        elif store.mas_nou.player_win_streak > 1:
            m 1sub "Finally I won~"

        else:
            m 1hua "I won~"
    return

label mas_nou_reaction_monika_wins_game:
    $ dlg_choice = renpy.random.randint(1, 4)

    if dlg_choice == 1:
        m 1eub "And this time I won the game!"
        if store.mas_nou.get_player_points_percentage("Player") < 0.3:
            m 4eub "You were quite close, though!"
            if renpy.random.randint(1, 15) < 15:
                m 4hua "I'm sure you'll win next time."

            # 1/15
            else:
                m 7ttu "Did you let me win on purpose?"
                m 1huu "Ehehe~"

        else:
            # m "It really is interesting to play against you, [player]."
            m 1hub "I had a lot of fun!"
            m 3eua "I'm sure you'll win next time."

    elif dlg_choice == 2:
        m 1wub "Oh!{w=0.1} I won this game!"
        m 3hub "That was really fun!"
        if store.mas_nou.get_player_points_percentage("Player") < 0.3:
            m 1eka "I hope you had fun too."
            # TODO: move this out of the RNG selection to 100% get it?
            if (
                persistent._mas_game_nou_wins["Monika"] + persistent._mas_game_nou_wins["Player"] < 20
                and persistent._mas_game_nou_wins["Monika"] > persistent._mas_game_nou_wins["Player"]
            ):
                m 3hua "I'm sure if we play more games you'll win too."

            else:
                m 3hua "Maybe next time you'll win~"

    elif dlg_choice == 3:
        m 2wub "I won this game too!"
        m 2hua "Ehehe~"
        m 1hub "Thanks for playing with me, [player]~"

    else:
        m 3eub "And I'm the first who reached [persistent._mas_game_nou_house_rules[points_to_win]] points!"
        m 1hua "I won this time~"
    return

label mas_nou_reaction_player_surrenders:
    if persistent._mas_game_nou_abandoned > 4:
        m 1ekc "That's alright, [player]..."
        m 1eka "But promise you'll finish the game next time?{w=0.4} For me?~"

    elif persistent._mas_game_nou_abandoned > 2:
        m 1ekc "[player]...{w=0.3}{nw}"
        extend 1eksdld "you keep giving up on our games..."
        m 1rksdlc "I hope you're enjoying playing with me."
        m 1eka "I enjoy every moment I'm with you~"

    elif store.mas_nou.game.current_turn == 1:
        m 1etd "But we just started."
        m 1ekc "Let me know when you'll have time."

    elif store.mas_nou.game.current_turn < 6:
        m 1ekc "Giving up already, [player]?"
        if (
            len(store.mas_nou.game.monika.hand) < 5
            and len(store.mas_nou.game.player.hand) > 8
        ):
            m 3ekb "I love to play with you no matter what the outcome is!"
            m 1eka "I hope you feel the same way~"

        else:
            m 1rud "You could at least try..."
            m 1eka "It would mean a lot to me."

    else:
        # This part isn't really correct, but she just tries to support you
        if len(store.mas_nou.game.monika.hand) >= len(store.mas_nou.game.player.hand):
            m 3ekb "I'm pretty sure you could win this [_round!t], [player]!"

        else:
            if len(store.mas_nou.game.monika.hand) > 1:
                m 2esa "Actually, I had quite bad cards, [player]."
            else:
                m 2esa "Actually, I had quite a bad last card, [player]."

            m 7eka "I think you could win this [_round!t]."

        m 3ekb "Don't give up so easily next time."
    return

# SL and stuff

# Points screen
screen nou_stats():

    layer "master"
    zorder 5

    style_prefix "nou"

    add MASFilterSwitch(
        "mod_assets/games/nou/note.png"
    ) pos (7, 120) anchor (0, 0) at nou_note_rotate_left

    # NOTE: Thanks to Briar aka @kkrosie123 for Monika's pen
    add MASFilterSwitch(
        "mod_assets/games/nou/pen.png"
    ) pos (225, 370) anchor (0.5, 0.5) at nou_pen_rotate_right

    text _("Our score!") pos (89, 110) anchor (0, 0.5) at nou_note_rotate_left

    # For one-round games we show wins
    if store.persistent._mas_game_nou_house_rules["points_to_win"] == 0:
        $ monika_score = store.mas_nou.monika_wins_this_sesh
        $ player_score = store.mas_nou.player_wins_this_sesh

    else:
        $ monika_score = store.persistent._mas_game_nou_points["Monika"]
        $ player_score = store.persistent._mas_game_nou_points["Player"]

    text _("Monika: [monika_score]") pos (62, 204) anchor (0, 0.5) at nou_note_rotate_left
    text _("[player]: [player_score]") pos (98, 298) anchor (0, 0.5) at nou_note_rotate_left

# Buttons screen
screen nou_gui():

    zorder 50

    style_prefix "nou"

    default fn_end_turn = store.mas_nou.game.end_turn
    default fn_handle_nou_logic = store.mas_nou.game.handle_nou_logic
    default game = store.mas_nou.game
    default player = store.mas_nou.game.player
    default monika = store.mas_nou.game.monika
    default discardpile = store.mas_nou.game.discardpile

    # Game menu
    vbox:
        xalign 0.95
        yalign 0.5

        if (
            player.plays_turn
            and (
                player.drew_card
                or player.should_skip_turn
            )
            and (
                not player.should_draw_cards
                or len(player.hand) >= game.HAND_CARDS_LIMIT
            )
            and (
                discardpile
                and discardpile[-1].color is not None
            )
        ):
            textbutton _("I'm skipping this turn"):
                action [
                    Function(fn_end_turn, player, monika),
                    Return([])
                ]

        else:
            textbutton _("I'm skipping this turn")

        null height 20

        if (
            player.plays_turn
            and not player.played_card
        ):
            if not store.mas_nou.disable_yell_button:
                textbutton _("NOU!"):
                    action [
                        SetField(mas_nou, "disable_yell_button", True),
                        Function(fn_handle_nou_logic, "player")
                    ]

            else:
                textbutton _("NOU!")

            if (
                not store.mas_nou.disable_remind_button
                and not player.drew_card
            ):
                textbutton _("You forgot to say 'NOU'!"):
                    action [
                        SetField(mas_nou, "disable_remind_button", True),
                        Function(fn_handle_nou_logic, "monika")
                    ]

            else:
                textbutton _("You forgot to say 'NOU'!")

        else:
            textbutton _("NOU!")
            textbutton _("You forgot to say 'NOU'!")

        null height 20

        if player.hand and monika.hand:
            textbutton _("I'm giving up..."):
                selected False
                action [
                    SetField(mas_nou, "winner", "Surrendered"),
                    SetField(mas_nou, "in_progress", False),
                    Jump("mas_nou_game_end")
                ]

        else:
            textbutton _("I'm giving up...")

    # Choose color menu
    vbox:
        align (0.5, 0.5)

        if (
            player.plays_turn
            # and store.mas_nou.game.is_sensitive()
            and (
                discardpile
                and discardpile[-1].color is None
            )
            and player.hand
        ):
            $ top_card = store.mas_nou.game.discardpile[-1]

            textbutton _("Red"):
                xminimum 230
                action If(
                    player.played_card,
                    true = [
                        SetField(top_card, "color", "red"),
                        Function(fn_end_turn, player, monika),
                        Return([])
                    ],
                    false = [
                        SetField(top_card, "color", "red"),
                        Return([])
                    ]
                )
            textbutton _("Blue"):
                xminimum 230
                action If(
                    player.played_card,
                    true = [
                        SetField(top_card, "color", "blue"),
                        Function(fn_end_turn, player, monika),
                        Return([])
                    ],
                    false = [
                        SetField(top_card, "color", "blue"),
                        Return([])
                    ]
                )
            textbutton _("Green"):
                xminimum 230
                action If(
                    player.played_card,
                    true = [
                        SetField(top_card, "color", "green"),
                        Function(fn_end_turn, player, monika),
                        Return([])
                    ],
                    false = [
                        SetField(top_card, "color", "green"),
                        Return([])
                    ]
                )
            textbutton _("Yellow"):
                xminimum 230
                action If(
                    player.played_card,
                    true = [
                        SetField(top_card, "color", "yellow"),
                        Function(fn_end_turn, player, monika),
                        Return([])
                    ],
                    false = [
                        SetField(top_card, "color", "yellow"),
                        Return([])
                    ]
                )

# Styles for NoU GUI
style nou_vbox is vbox:
    spacing 5

style nou_vbox_dark is vbox:
    spacing 5

style nou_button is generic_button_light:
    xsize 200
    ysize None
    ypadding 5

style nou_button_dark is generic_button_dark:
    xsize 200
    ysize None
    ypadding 5

style nou_button_text is generic_button_text_light:
    kerning 0.2
    layout "subtitle"
    text_align 0.5

style nou_button_text_dark is generic_button_text_dark:
    kerning 0.2
    layout "subtitle"
    text_align 0.5

style nou_text:
    size 30
    color "#000"
    outlines []
    font "gui/font/m1.ttf"

style nou_text_dark:
    size 30
    color "#000"
    outlines []
    font "gui/font/m1.ttf"

transform nou_note_rotate_left:
    rotate -23
    rotate_pad True
    transform_anchor True

transform nou_pen_rotate_right:
    rotate 40
    rotate_pad True
    transform_anchor True

# # # FRAMEWORK FOR CARDGAMES

# Copyright 2008-2021 Tom Rothamel <pytom@bishoujo.us>
#
# This version was updated for Monika After Story, several bugs were fixed
# and some new features were implemented, please credit the project as appropriate.
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# NOTE: This can be used in other games in the future
image bg cardgames desk = mas_cardgames.DeskSpriteSwitch()

init 10 python in mas_cardgames:
    # All bgs should be defined, get the desk sprites for them
    __scanDeskSprites()

init -10 python in mas_cardgames:
    import pygame
    import store
    from store import RotoZoom, ConditionSwitch, MASFilterSwitch

    # The path to the desk assets, place your background there to automatically load it into the map
    # NOTE: THE FILE NAME MUST CONSIST OF THE BACKGROUND ID
    GAME_DIR_PATH = renpy.config.gamedir.replace("\\", "/") + "/"
    # NOTE: Linux doesn't like leading slashes
    DESK_SPRITES_PATH = "mod_assets/games/nou/desks/"
    # The map between backgrounds and desk sprites
    # Format: {background_id: MASFilterSwitch}
    # NOTE: we fill the map automatically at init 10,
    # but you can always add an img for your background yourself (we don't override)
    DESK_SPRITES_MAP = dict()

    def __scanDeskSprites():
        """
        Scans the folder with the desk sprites and fills the desk sprites map
        """
        sprites_map = dict()
        # Get the sprites we have
        for file in store.MASDockingStation(GAME_DIR_PATH + DESK_SPRITES_PATH).getPackageList():
            # Remove the extension
            key = file.rpartition(".")[0]
            if key:
                sprites_map[key] = file

        # Fill the map with the sprites (or use the def as a fallback)
        fb = sprites_map.get(store.mas_background.MBG_DEF)
        for bg_id in store.mas_background.BACKGROUND_MAP.iterkeys():
            if bg_id not in DESK_SPRITES_MAP:
                filename = sprites_map.get(bg_id, fb)
                DESK_SPRITES_MAP[bg_id] = MASFilterSwitch(DESK_SPRITES_PATH + filename)

    class DeskSpriteSwitch(renpy.display.core.Displayable):
        """
        This displayable represents a desk for card games;
        It takes care of different backgrounds, too, using the map for desk sprites.
        """
        BLIT_COORDS = (0, 0)

        def render(self, width, height, st, at):
            """
            Render of this disp

            ASSUMES:
                store.mas_current_background
            """
            desk_render = renpy.render(DESK_SPRITES_MAP[store.mas_current_background.background_id], width, height, st, at)
            main_render = renpy.Render(desk_render.width, desk_render.height)
            main_render.blit(desk_render, DeskSpriteSwitch.BLIT_COORDS)

            return main_render

        def visit(self):
            """
            Returns imgs for prediction

            OUT:
                list of displayables

            ASSUMES:
                store.mas_current_background
            """
            return [DESK_SPRITES_MAP[store.mas_current_background.background_id]]

    # Drag type constants
    DRAG_NONE = 0
    DRAG_CARD = 1
    DRAG_ABOVE = 2
    DRAG_STACK = 3
    DRAG_TOP = 4

    def __rect_overlap_area(r1, r2):
        """
        Checks if 2 given rectangles overlap

        IN:
            r1, r2 - tuples of the following format: (x, y, w, h)

        OUT:
            overlap between the 2 rectangles (False if they don't overlap)
        """
        if r1 is None or r2 is None:
            return 0

        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2

        maxleft = max(x1, x2)
        minright = min(x1 + w1, x2 + w2)
        maxtop = max(y1, y2)
        minbottom = min(y1 + h1, y2 + h2)

        if minright < maxleft:
            return 0

        if minbottom < maxtop:
            return 0

        return (minright - maxleft) * (minbottom - maxtop)

    def __default_can_drag(table, stack, card):
        """
        Function to check if the player can drag card
        NOTE: You can use yours in the constructor,
            but it must always take 3 arguments
            and return True or False

        IN:
            table - the table the card belongs to
            stack - the stack the card belongs to
            card - the card the player tries to drag

        OUT:
            True if the card is set faceup, False otherwise
        """
        return table.get_faceup(card)

    class Table(renpy.display.core.Displayable):
        """
        Table class to represent a "table" for card games

        PROPERTIES:
            back - the back of cards that don't have a more specific back defined
            base - the base of stacks that don't have a more specific base defined
            springback - the amount of time it takes for cards to springback into their rightful place
            rotate - the amount of time it takes for cards to rotate into their proper orientation
            can_drag - a function that is called to tell if we can drag a particular card
            doubleclick - the time between clicks for the click to be considered a double-click
            cards - a map from card value to the card object corresponding to that value
            stacks - a list of the stacks that have been defined
            sensitive - weather or not we're sensetive to the user's input
            last_event - last click event (CardEvent() obj)
            click_card - the card that has been clicked
            click_stack - the stack that has been clicked
            drag_cards - the list of cards that are being dragged
            dragging - weather or not we're dragging some cards
            click_x - the x position where we clicked
            click_y - the y position where we clicked
            st - the amount of time we've been shown for
        """

        def __init__(
            self,
            back=None,
            base=None,
            springback=0.1,
            rotate=0.1,
            can_drag=__default_can_drag,
            doubleclick=0.33,
            **kwargs
        ):
            """
            Constructor for Table objects

            IN:
                back - the back of cards that don't have a more specific back defined
                    (Default: None)
                base - the base of stacks that don't have a more specific base defined
                    (Default: None)
                springback - the amount of time it takes for cards to springback into their rightful place
                    (Default: 0.1)
                rotate - the amount of time it takes for cards to rotate into their proper orientation
                    (Default: 0.1)
                can_drag - a function that is called to tell if we can drag a particular card
                    (Default: __default_can_drag)
                doubleclick - the time between clicks for the click to be considered a double-click
                    (Default: 0.33)
            """
            super(Table, self).__init__(**kwargs)

            # We supports only these types
            if isinstance(back, (basestring, tuple, renpy.display.im.ImageBase, renpy.display.image.ImageReference)):
                self.back = MASFilterSwitch(back)

            # This is some kind of displayable, but not an image
            elif isinstance(back, renpy.display.core.Displayable):
                self.back = back

            # It's something what we don't support
            else:
                self.back = None

            if isinstance(base, (basestring, tuple, renpy.display.im.ImageBase, renpy.display.image.ImageReference)):
                self.base = MASFilterSwitch(base)

            elif isinstance(base, renpy.display.core.Displayable):
                self.base = base

            else:
                self.base = None

            self.springback = springback

            self.rotate = rotate

            self.can_drag = can_drag

            self.doubleclick = doubleclick

            # A map from card value to the card object corresponding to that value
            self.cards = {}

            # A list of the stacks that have been defined
            self.stacks = []

            self.sensitive = True

            self.last_event = CardEvent()

            self.click_card = None

            self.click_stack = None

            self.drag_cards = []

            self.dragging = False

            self.click_x = 0
            self.click_y = 0

            self.st = 0

        def show(self, layer="minigames"):
            """
            Shows the table on the given layer

            IN:
                layer - the layer we'll render our table on
                    (Default: "minigames")
            """
            for v in self.cards.itervalues():
                v._offset = __Fixed(0, 0)

            ui.layer(layer)
            ui.implicit_add(self)
            ui.close()

        def hide(self, layer="minigames"):
            """
            Hides the table on the given layer

            IN:
                layer - the layer we rendered our table on
                    (Default: "minigames")
            """
            ui.layer(layer)
            ui.remove(self)
            ui.close()

        def set_sensitive(self, value):
            """
            Changes the table's sensetivity

            IN:
                value - True if we set to sensetive, False otherwise
            """
            self.sensitive = value

        def get_card(self, value):
            """
            Gets the table's card object corresponding to the given value

            IN:
                value - your custom card object

            OUT:
                table's card object
            """
            if value not in self.cards:
                # raising an exception might be better
                # that gives an idea to coder that he's a dumbass
                raise Exception("No card has the value {0!r}.".format(value))

            return self.cards[value]

        def set_faceup(self, card, faceup=True):
            """
            Sets the given card faceup/down and makes renpy redraw the table

            in:
                card - card
                faceup - True if we set it faceup, False otherwise
                    (Default: True)
            """
            self.get_card(card).faceup = faceup
            renpy.redraw(self, 0)

        def get_faceup(self, card):
            """
            Checks if the given card is faceup

            IN:
                card - card

            OUT:
                True if the card is set faceup, False otherwise
            """
            return self.get_card(card).faceup

        def set_rotate(self, card, rotation):
            """
            Sets the rotation of the given card and makes renpy redraw the table

            IN:
                card - card
                rotation - rotation for the card
            """
            __Rotate(self.get_card(card), rotation)
            renpy.redraw(self, 0)

        def get_rotate(self, card):
            """
            Returns card rotation

            IN:
                card - card

            OUT:
                card's rotation
            """
            return self.get_card(card).rotate.rotate_limit()

        def add_marker(self, card, marker):
            """
            Adds marker on card and redraws the table

            IN:
                card - card
                marker - marker
            """
            self.get_card(card).markers.append(marker)
            renpy.redraw(self, 0)

        def remove_marker(self, card, marker):
            """
            Removes marker from card and redraws the table

            IN:
                card - card
                marker - marker
            """
            table_card = self.get_card(card)
            if marker in table_card.markers:
                table_card.markers.remove(marker)
                renpy.redraw(self, 0)

        def card(self, value, face, back=None):
            """
            Creates a card and adds it to the table's cards map

            IN:
                value - your custom card object
                face - is the card face up or face down
                back - the card's back
                    (Default: None)
            """
            self.cards[value] = __Card(self, value, face, back)

        def stack(
            self,
            x,
            y,
            xoff=0,
            yoff=0,
            show=1024,
            base=None,
            click=False,
            drag=DRAG_NONE,
            drop=False,
            hover=False,
            hidden=False
        ):
            """
            Creates a stack and adds it to the table's stacks list

            IN:
                x - the x position for the stack
                y - the y position for the stack
                xoff - the offset x for the stack
                    (Default: 0)
                yoff - the offset y for the stack
                    (Default: 0)
                show - maximum cards to render
                    (Default: 1024)
                base - img for the stack's base
                    (Default: None)
                click - whether or not the user can click on the stack
                    (Default: False)
                drag - the drag mode for the stack
                    (Default: DRAG_NONE)
                drop - whether or not the user can drop cards on the stack
                    (Default: False)
                hover - whether or not we respond to user hovering mouse over the stack
                    (Default: False)
                hidden - whether or not we hide the stack
                    (Default: False)

            OUT:
                new stack object
            """
            rv = __Stack(self, x, y, xoff, yoff, show, base, click, drag, drop, hover, hidden)

            self.stacks.append(rv)
            return rv

        def per_interact(self):
            """
            Forces redraw on each interaction
            """
            renpy.redraw(self, 0)

        def render(self, width, height, st, at):
            """
            Renders the table's stacks and cards that should be rendered
            """
            self.st = st

            rv = renpy.Render(width, height)

            for s in self.stacks:

                if s.hidden:
                    s.rect = None
                    for c in s.cards:
                        c.rect = None
                    continue

                s.render_to(rv, width, height, st, at)

                for c in s.cards:
                    c.render_to(rv, width, height, st, at)

            return rv

        def visit(self):
            """
            Returns a list of all displayable objects we use
            """
            stacks_bases = [stack.base for stack in self.stacks]
            cards_faces = [card.face for card in self.cards.itervalues()]
            cards_backs = [card.back for card in self.cards.itervalues()]

            return stacks_bases + cards_faces + cards_backs

        def event(self, ev, x, y, st):
            """
            Event handler
            This framework allows you to work with 5 event types
                each event has its own attributes (they share some of them):
                    'drag' - the user dragged 1 or more cards:
                        table
                        stack
                        card
                        drag_cards
                        drop_stack (can be None)
                        drop_card (can be None)
                        time
                    'click' and 'doubleclick' - the user
                        clicked somewhere:
                        table
                        stack
                        card (can be None)
                        time
                    'hover' and 'unhover' - the user started/ended
                        hovering mouse over card:
                        table
                        stack
                        card
                        time
                if the event doesn't have an attribute, it means the attribute is None

            OUT:
                list of events happened during this interaction
            """
            self.st = st

            if not self.sensitive:
                return
                # raise renpy.IgnoreEvent()

            evt_list = list()
            grabbed = renpy.display.focus.get_grab()

            if (grabbed is not None) and (grabbed is not self):
                return

            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                if self.click_stack:
                    return

                stack = None
                card = None

                for s in self.stacks:

                    sx, sy, sw, sh = s.rect
                    if sx <= x and sy <= y and sx + sw > x and sy + sh > y:
                        stack = s


                    for c in s.cards[-s.show:]:
                        if c.rect is None:
                            continue

                        cx, cy, cw, ch = c.rect
                        if cx <= x and cy <= y and cx + cw > x and cy + ch > y:
                            card = c
                            stack = c.stack

                if stack is None:
                    return

                # Grab the display.
                renpy.display.focus.set_grab(self)

                # Don't let the user grab a moving card.
                if card is not None:
                    xoffset, yoffset = card._offset.offset()
                    if (xoffset or yoffset) and not card.hovered:
                        raise renpy.IgnoreEvent()

                # Move the stack containing the card to the front.
                self.stacks.remove(stack)
                self.stacks.append(stack)

                if stack.click or stack.drag:
                    self.click_card = card
                    self.click_stack = stack

                if (
                    card is None
                    or not self.can_drag(self, card.stack, card.value)
                ):
                    self.drag_cards = []

                elif card.stack.drag == DRAG_CARD:
                    self.drag_cards = [card]

                elif card.stack.drag == DRAG_ABOVE:
                    self.drag_cards = []
                    for c in card.stack.cards:
                        if c is card or self.drag_cards:
                            self.drag_cards.append(c)

                elif card.stack.drag == DRAG_STACK:
                    self.drag_cards = list(card.stack.cards)

                elif card.stack.drag == DRAG_TOP:
                    if card.stack.cards[-1] is card:
                        self.drag_cards = [card]
                    else:
                        self.drag_cards = []

                for c in self.drag_cards:
                    c._offset = __Fixed(0, 0)

                self.click_x = x
                self.click_y = y
                self.dragging = False

                renpy.redraw(self, 0)

                # raise renpy.IgnoreEvent()

            if ev.type == pygame.MOUSEMOTION or (ev.type == pygame.MOUSEBUTTONUP and ev.button == 1):
                if abs(x - self.click_x) > 7 or abs(y - self.click_y) > 7:
                    self.dragging = True

                dx = x - self.click_x
                dy = y - self.click_y

                for c in self.drag_cards:
                    xoffset, yoffset = c._offset.offset()

                    cdx = dx - xoffset
                    cdy = dy - yoffset

                    c._offset = __Fixed(dx, dy)

                    if c.rect:
                        cx, cy, cw, ch = c.rect
                        cx += cdx
                        cy += cdy
                        c.rect = (cx, cy, cw, ch)

                area = 0
                dststack = None
                dstcard = None

                for s in self.stacks:
                    if not s.drop:
                        continue

                    for c in self.drag_cards:

                        if c.stack == s:
                            continue
                        a = __rect_overlap_area(c.rect, s.rect)
                        if a >= area:
                            dststack = s
                            dstcard = None
                            area = a

                        for c1 in s.cards:
                            a = __rect_overlap_area(c.rect, c1.rect)
                            if a >= area:
                                dststack = s
                                dstcard = c1
                                area = a

                if area == 0:
                    dststack = None
                    dstcard = None

                renpy.redraw(self, 0)

                # if ev.type == pygame.MOUSEMOTION:
                #     raise renpy.IgnoreEvent()

            if (
                ev.type == pygame.MOUSEMOTION
                or (
                    ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP)
                    and ev.button == 1
                )
            ):
                if not self.drag_cards:
                    for s in self.stacks:
                        if not s.hover:
                            continue

                        for i, c in enumerate(s.cards):
                            if not c.rect:
                                continue

                            c_x_min, c_y_min, c_w, c_h = c.rect
                            c_x_max = 0
                            c_y_max = 0
                            # For the last card in the stack
                            if i == len(s.cards) - 1:
                                c_x_max = c_x_min + c_w
                                c_y_max = c_y_min + c_h
                            # For any card except the last one
                            # Also only if we have any x/y offsets
                            elif not s.xoff == 0 or not s.yoff == 0:
                                if abs(s.xoff) >= c_w:
                                    c_x_max = c_x_min + c_w

                                else:
                                    if s.xoff > 0:
                                        c_x_max = c_x_min + s.xoff

                                    elif s.xoff < 0:
                                        c_x_max = c_x_min + c_w
                                        c_x_min = c_x_min + c_w + s.xoff

                                    else:
                                        c_x_max = c_x_min + c_w

                                if abs(s.yoff) >= c_h:
                                    c_y_max = c_y_min + c_h

                                else:
                                    if s.yoff > 0:
                                        c_y_max = c_y_min + s.yoff

                                    elif s.yoff < 0:
                                        c_y_max = c_y_min + c_h + s.yoff
                                        c_y_min = c_y_min + s.yoff

                                    else:
                                        c_y_max = c_y_min + c_h

                            # Make an evt if we hover over this card
                            if not c.hovered and c_x_min <= x < c_x_max and c_y_min <= y < c_y_max:
                                evt = CardEvent()
                                evt.type = "hover"
                                evt.table = self
                                evt.stack = s
                                evt.card = c.value
                                evt.time = st
                                c.hovered = True
                                evt_list.insert(0, evt)

                            # We don't hover over this card anymore
                            elif c.hovered and (not c_x_min <= x < c_x_max or not c_y_min <= y < c_y_max):
                                evt = CardEvent()
                                evt.type = "unhover"
                                evt.table = self
                                evt.stack = s
                                evt.card = c.value
                                evt.time = st
                                c.hovered = False
                                evt_list.insert(0, evt)

            if ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                # Ungrab the display.
                renpy.display.focus.set_grab(None)

                evt = None

                if self.dragging:
                    if self.drag_cards:
                        for c in self.drag_cards:
                            if c.hovered:
                                evt = CardEvent()
                                evt.type = "unhover"
                                evt.table = self
                                evt.stack = self.click_stack
                                evt.card = c.value
                                evt.time = st
                                c.hovered = False
                                evt_list.append(evt)

                        self.last_event = evt
                        evt = None

                        if dststack is not None:
                            evt = CardEvent()
                            evt.type = "drag"
                            evt.table = self
                            evt.stack = self.click_stack
                            evt.card = self.click_card.value
                            evt.drag_cards = [c.value for c in self.drag_cards]
                            evt.drop_stack = dststack
                            if dstcard:
                                evt.drop_card = dstcard.value
                            evt.time = st

                else:
                    if self.click_stack is not None:
                        if self.click_stack.click:
                            evt = CardEvent()
                            evt.table = self
                            evt.stack = self.click_stack
                            if self.click_card:
                                evt.card = self.click_card.value
                            else:
                                evt.card = None
                            evt.time = st

                            if (
                                self.last_event.type == "click"
                                and self.last_event.stack == evt.stack
                                and self.last_event.card == evt.card
                                and self.last_event.time + self.doubleclick > evt.time
                            ):
                                evt.type = "doubleclick"
                            else:
                                evt.type = "click"

                if evt is not None:
                    self.last_event = evt
                    evt_list.append(evt)

                for c in self.drag_cards:
                    c.springback()

                self.click_card = None
                self.click_stack = None
                self.drag_cards = []

            if evt_list:
                return evt_list

            else:
                return None
                # raise renpy.IgnoreEvent()

    class CardEvent(object):
        """
        Represents cards events
        PROPERTIES:
            type - the type of the event
            stack - the stack where the event started
            card - the card that triggered the event
            drag_cards - the cards we're dragging
            drop_stack - the stack we're dropping our cards on
            drop_card - the bottom card we're dropping
            time - the event time
        """

        def __init__(self):
            self.type = None
            self.stack = None
            self.card = None
            self.drag_cards = None
            self.drop_stack = None
            self.drop_card = None
            self.time = 0

    class __Stack(object):
        """
        Represents a stack of one or more cards, which can be placed on the table.

        PROPERTIES:
            table - the table the stack belongs to
            x/y - coordinates of the center of the top card of the stack
            xoff/yoff - the offset in the x and y directions of each successive card
            show - the number of cards to render
            base - the image that is shown behind the stack
            click - whether or not we report click events on the stack
            drag - the drag mode for the stack
            drop - whether or not the user can drop cards on the stack
            hover - whether or not we report hover/unhover events for the stack
            hidden - whether or not we render the stack
            cards - the list of cards in the stack
            rect - the rectangle for the background
        """
        def __init__(
            self,
            table,
            x,
            y,
            xoff,
            yoff,
            show,
            base,
            click,
            drag,
            drop,
            hover,
            hidden
        ):
            """
            Constructor for a stack
            NOTE: since we define stacks via the table method,
                they don't have default parameters in the init method

            IN:
                table - the table of this stack
                x - x of the center of the top card
                y - y of the center of the top card
                xoff - x offset of each successive card
                yoff - y offset of each successive card
                show - maximum cards to render
                base - the image for the base of this stack
                click - whether or not we report the user's clicks
                drag - the drag mode for this stack
                drop - whether or not the user's can drop cards on this stack
                hover -  whether or not we report hover events for the stack
                hidden - whether or not we render the stack
            """
            self.table = table

            self.x = x
            self.y = y

            self.xoff = xoff
            self.yoff = yoff

            self.show = show

            # If None, the background is taken from the table.
            if isinstance(base, (basestring, tuple, renpy.display.im.ImageBase, renpy.display.image.ImageReference)):
                self.base = MASFilterSwitch(base)

            elif isinstance(base, renpy.display.core.Displayable):
                self.base = base

            # for when the base is None
            elif self.table.base is not None:
                self.base = self.table.base

            else:
                raise Exception(
                    "Neither Stack {0} nor Table {1} has defined image for stack base.".format(self, self.table)
                )

            self.click = click
            self.drag = drag
            self.drop = drop
            self.hover = hover

            self.hidden = hidden

            self.cards = []

            self.rect = None

        def insert(self, index, card):
            """
            Inserts card in the stack at index

            IN:
                index - the index to insert the card at
                card - card to move
            """
            card = self.table.get_card(card)

            if card.stack:
                card.stack.cards.remove(card)

            card.stack = self
            self.cards.insert(index, card)

            self.table.stacks.remove(self)
            self.table.stacks.append(self)

            card.springback()

        def append(self, card):
            """
            Places card on the top of the stack

            IN:
                card - card to move
            """
            if card in self.cards:
                self.insert(len(self.cards) - 1, card)

            else:
                self.insert(len(self.cards), card)

        def remove(self, card):
            """
            Removes card from the stack
            NOTE: cards that don't have a stack won't be rendered!

            IN:
                card - card to remove
            """
            card = self.table.get_card(card)

            self.cards.remove(card)

            card.stack = None
            card.rect = None

        def index(self, card):
            """
            Returns card index in the stack

            IN:
                card - the card which index we're trying to find

            OUT:
                int as card index
                or None if no such card in the stack
            """
            card = self.table.get_card(card)

            try:
                id = self.cards.index(card)

            except ValueError:
                id = None

            return id

        def deal(self):
            """
            Removes the card at the top of the stack from the stack

            OUT:
                the card that was removed
                or None if the stack si empty
            """
            if not self.cards:
                return None

            card = self.cards[-1]
            self.remove(card.value)
            return card.value

        def shuffle(self):
            """
            Shuffles the cards in the stack
            """
            renpy.random.shuffle(self.cards)
            renpy.redraw(self.table, 0)

        def __repr__(self):
            return "<__Stack " + "{0!r}".format(self.cards).strip("[]") + ">"

        def __len__(self):
            return len(self.cards)

        def __getitem__(self, idx):
            if isinstance(idx, slice):
                return [card.value for card in self.cards[idx]]

            else:
                return self.cards[idx].value

        def __iter__(self):
            for i in self.cards:
                yield i.value

        def __contains__(self, card):
            return self.table.get_card(card) in self.cards

        def render_to(self, rv, width, height, st, at):
            """
            Blits the stack to the table's render
            """
            render = renpy.render(self.base, width, height, st, at)
            cw, ch = render.get_size()

            cx = self.x - cw / 2
            cy = self.y - ch / 2

            self.rect = (cx, cy, cw, ch)
            rv.blit(render, (cx, cy))

    class __Card(object):
        """
        Represent a card for our table
        NOTE: THIS IS NOT THE CLASS FOR YOUR CARDS
        This is only for internal use only

        PROPERTIES:
            table - the table the card belongs to
            value - value of the card (your card object)
            face - the face for the card
            back - the back for the card
            faceup - whether or not this card is set face up
            rotate - an object for cards rotation
            markers - a list of marker that will be rendered over the card
            stack - the stack the card belongs to
            _offset - an object that gives the offset of this card relative to
                where it would normally be placed. THIS IS THE PRIVATE VARIANT FOR INTERNAL USE
            rect - the rectangle where this card was last drawn to the screen at
            hovered - whether or not the user hovered over this card
            positional_offset - the offsets which you can use to change the card positions (PUBLIC)
        """
        def __init__(self, table, value, face, back):
            """
            The constructor for a card
            NOTE: no default values since we use the table method for defining cards

            table - the table of this card
            value - your card object corresponding to this card
            face - the face of this card
            back - the back of this card
            """
            self.table = table

            self.value = value

            self.face = MASFilterSwitch(face)

            if isinstance(back, (basestring, tuple, renpy.display.im.ImageBase, renpy.display.image.ImageReference)):
                self.back = MASFilterSwitch(back)

            elif isinstance(back, renpy.display.core.Displayable):
                self.back = back

            elif self.table.back is not None:
                self.back = self.table.back

            else:
                raise Exception(
                    "Neither Card {0} nor Table {1} has defined image for card back.".format(self, self.table)
                )

            self.faceup = True

            self.rotate = None

            self.markers = []

            self.stack = None

            self._offset = __Fixed(0, 0)

            self.rect = None

            self.hovered = False

            self.positional_offset = (0, 0)

            __Rotate(self, 0)

        def set_offset(self, x=0, y=0):
            """
            Sets ofsets for this card to x and y

            IN:
                x - x offset
                    (Default: 0)
                y - y offset
                    (Default: 0)
            """
            self.positional_offset = (x, y)

        def place(self):
            """
            Returns the base x and y placement of this card

            OUT:
                tuple with x and y coordinates of this card
            """
            s = self.stack
            offset = max(len(s.cards) - s.show, 0)
            index = max(s.cards.index(self) - offset, 0)

            x_pos_off, y_pos_off = self.positional_offset

            return (x_pos_off + s.x + s.xoff * index, y_pos_off + s.y + s.yoff * index)

        def springback(self):
            """
            Makes this card to springback
            """
            if self.rect is None:
                self._offset = __Fixed(0, 0)
            else:
                self._offset = __Springback(self)

        def render_to(self, rv, width, height, st, at):
            """
            Blits the card to the table's render
            """

            x, y = self.place()
            xoffset, yoffset = self._offset.offset()
            x += xoffset
            y += yoffset

            if self.faceup:
                d = self.face
            else:
                d = self.back

            # TODO: Figure out if we can reuse some of this.

            if self.markers:
                d = Fixed(* ([d] + [renpy.easy.displayable(i) for i in self.markers]))

            r = self.rotate.rotate()
            if r:
                d = RotoZoom(r, r, 0, 1, 1, 0)(d)

            render = renpy.render(d, width, height, st, at)
            w, h = render.get_size()

            x -= w / 2
            y -= h / 2

            self.rect = (x, y, w, h)

            rv.blit(render, (x, y))

        def __repr__(self):
            return "<__Card {0!r}>".format(self.value)

    class __Springback(object):

        def __init__(self, card):
            self.card = card
            self.table = table = card.table

            self.start = table.st

            cx, cy, cw, ch = self.card.rect
            x = cx + cw / 2
            y = cy + ch / 2

            self.startx = x
            self.starty = y

        def offset(self):

            t = (self.table.st - self.start) / self.table.springback
            t = min(t, 1.0)

            if t < 1.0:
                renpy.redraw(self.table, 0)

            px, py = self.card.place()

            return int((self.startx - px) * (1.0 - t)), int((self.starty - py) * (1.0 - t))

    class __Fixed(object):
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def offset(self):
            return self.x, self.y

    class __Rotate(object):
        def __init__(self, card, amount):

            self.table = table = card.table
            self.start = table.st

            if card.rotate is None:
                self.start_rotate = amount
            else:
                self.start_rotate = card.rotate.rotate()

            self.end_rotate = amount

            card.rotate = self

        def rotate(self):

            if self.start_rotate == self.end_rotate:
                return self.start_rotate

            t = (self.table.st - self.start) / self.table.springback
            t = min(t, 1.0)

            if t < 1.0:
                renpy.redraw(self.table, 0)

            return self.start_rotate + (self.end_rotate - self.start_rotate) * t

        def rotate_limit(self):
            return self.end_rotate
