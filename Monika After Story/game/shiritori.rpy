
# holds words the player has told Monika are real despite not being in the dictionary
default persistent._mas_shiritori_extra_words = set()

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_shiritori_rules",
            category=["games"],
            prompt="Rules of shiritori",
            conditional="renpy.seen_label('mas_unlock_shiritori')",
            action=EV_ACT_UNLOCK,
            pool=True,
            rules={"no unlock": None}
        )
    )

label monika_shiritori_rules:
    m "Shiritori is a word game. The rules are very simple."
    m "The players take turns saying words in a certain pattern."
    m "The pattern being that the first letter of a new word must be the same as the last letter of the last word said."
    m "The losing conditions are:"
    m "Using a word that fails to follow the pattern."
    m "Trying to use something that isn't a word."
    m "Using a word that's already been used."
    m "And failing to answer within a given time limit."
    m "Note: also add allowed word types here once we're clear on that - no proper nouns, no abrreviations, no one-letters, etc."
    return

label player_loss(reason=""):
    if reason == "letter":
        m "That's the wrong letter, you know."

    elif reason == "invalid":
        if game_variant == "cities":
            $ word = "city"
        else:
            $ word = "word"
        m "I don't think that's a real [word]."

        # add the invalid word to persistent dictionary if the player insists it's real
        # not for cities
        if game_variant != "cities":
            $ _history_list.pop()
            menu:
                m "I don't think that's a real [word].{fast}"

                "Actually, it is.":
                    m "Wait, really?"
                    m "I never heard that one before."
                    m "But I guess I'll believe you."
                    m "It's not like you'd lie to me just to win a silly little game, would you?"
                    m "Anyway...{w=0.3}{nw}"
                    extend "[last_word_p_raw], was it?"
                    $ persistent._mas_shiritori_extra_words.add(last_word_p)
                    $ shiritori_loop = True

                "Yeah, you're right.":
                    pass



    elif reason == "used":
        m "Wait a second, [last_word_p_raw]?"
        if last_word_p in shiritori_recent_words:
            m "That one was played just a second ago!"
        else:
            m "I'm pretty sure one of us already used that one."

    elif reason == "timeout":
        m "...And you're out of time."

    else:
        m "This isn't supposed to happen."

    $ loss_quips = [
    "Sorry, but it's your loss.",
    "Your loss, [player].",
    "Looks like I win, ahaha~",
    "It's my win, [player]."
    ]
    $ loss_quip = renpy.substitute(renpy.random.choice(loss_quips))
    m "[loss_quip]" # smug expression
    return


label monika_loss(reason = ""):
    # Monika can only lose via word repetition or turn exhaustion (ie time limit rule), the other two are silly
    if reason == "used":
        m "Wait, [last_word_m]? That one already got used, didn't it?"
        m "Silly me, ahaha~"

    elif reason == "timeout":
        m "I...{w=1}can't think of anything."
        m "This is embarrassing, ahaha~"

    else:
        m "This isn't supposed to happen either."

    $ win_quips = [
    "Guess it's my loss then.",
    "Looks like you win, [player].",
    "You won, [player]. Congratulations.",
    "You won, well done.",
    "gg no re"
    ]
    $ win_quip = renpy.substitute(renpy.random.choice(win_quips))
    m "[win_quip]"
    return

screen shiritori_input(prompt, timeout, use_return_button=False, return_button_prompt="Nevermind.", return_button_value="cancel_input"):
    # this is literally just the input screen with a timer slapped on it
    style_prefix "input"

    window:
        if use_return_button:
            textbutton return_button_prompt:
                style "choice_button"
                align (0.5, 0.5)
                ypos -263
                action Return(return_button_value)

        vbox:
            align (0.5, 0.5)
            spacing 30

            text prompt style "input_prompt"
            input id "input"

    timer timeout action Return("_timeout")

# entry point
label game_shiritori:
    m "You wanna play shiritori? Okay~"
    m "Cities only or full dictionary?"
    $ _history_list.pop()
    menu:
        m "Cities only or full dictionary?{fast}"

        "Cities only":
            m "Cities it is."
            $ game_variant = "cities"

        "Full":
            m "The whole vocabulary then."
            $ game_variant = "full"

    # difficulty choice
    #   time limit in seconds
    #   maximal number of turns Monika can play across all letters
    #   chance Monika will use the full vocabulary
    m "What difficulty would you like?"
    $ _history_list.pop()
    menu:
        m "What difficulty would you like?{fast}"

        "Easy":
            $ timelimit = 20
            $ turnmax_monika = 250
            $ full_dict_chance = 2

        "Normal":
            $ timelimit = 10
            $ turnmax_monika = 500
            $ full_dict_chance = 5

        "Hard":
            $ timelimit = 5
            $ turnmax_monika = 1000
            $ full_dict_chance = 10

    # 1st turn decision
    m "Do you want to start or should I?"
    $ _history_list.pop()
    menu:
        m "Do you want to start or should I?{fast}"

        "I'll start":
            m "Okay, go ahead."
            $ monika_first = False
        "You start":
            m "Okay then, I'll start."
            $ monika_first = True
        "Random":
            if random.randint(1,2) == 1:
                m "Okay, you go first."
                $ monika_first = False
            else:
                m "Okay, I'll start."
                $ monika_first = True

    python:
        if game_variant == "full":
            with open("game/shiritori_dictionary_full.json") as dff:
                dictionary_full = json.load(dff)
            with open("game/shiritori_dictionary_monika.json") as dmf:
                dictionary_monika = json.load(dmf)

        elif game_variant == "cities":
            with open("game/shiritori_dictionary_cities_decap.json") as dff:
                dictionary_full = json.load(dff)
            with open("game/shiritori_dictionary_cities.json") as dmf:
                dictionary_monika = json.load(dmf)

        # counting dictionary cardinality
        dict_cardinality = {}
        dict_cardinality_total = 0
        for letter in dictionary_full:
            dict_cardinality[letter] = len(dictionary_full[letter])
            dict_cardinality_total += dict_cardinality[letter]

        # getting Monika's turn count
        # TODO: maybe add some additional transform to decrease spread instead of direct proportionality
        shiritori_turn_scaling_factor = turnmax_monika / dict_cardinality_total
        shiritori_monika_turnsleft = {}
        for letter in dict_cardinality:
            shiritori_monika_turnsleft[letter] = int(shiritori_turn_scaling_factor * dict_cardinality[letter])


        shiritori_loop = True
        # all the words used in current game
        shiritori_used_words = set()
        # last 10 words - serves as Monika's short-term memory to avoid immediately repeating a word
        shiritori_mem_size = 10
        shiritori_recent_words = set()

    # if Monika has the first turn
    if monika_first:
        python:
            # get a random word from Monika's pool
            first_letter = renpy.random.choice("abcdefghijklmnopqrstuvwxyz")
            last_word_m = renpy.random.choice(dictionary_monika[first_letter])
            # add first word to used and recent
            shiritori_used_words.add(last_word_m.lower())
            shiritori_recent_words.add(last_word_m.lower())
        m "[last_word_m]"
    else:
        $ last_word_m = "_none"

    # main loop
    while shiritori_loop:
        python:
        # get player input
            if last_word_m == "_none":
                input_prompt = "Choose your first word"
            else:
                input_prompt = last_word_m

            last_word_p_raw = mas_input(
                input_prompt,
                allow = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .'-",
                length=20,
                screen = "shiritori_input",
                screen_kwargs = {"timeout":timelimit}
                ).strip(' \t\n\r').lower()
            last_word_p = last_word_p_raw.lower()

        # check for timeout
        if last_word_p == "_timeout":
            $ shiritori_loop = False
            call player_loss(reason = "timeout")

        # check if starting with correct letter - ignore on first turn if player starts
        elif not last_word_m == "_none" and last_word_p[0] != last_word_m[-1]:
            $ shiritori_loop = False
            call player_loss(reason = "letter")

        # check against dictionary
        elif ((last_word_p not in dictionary_full[last_word_p[0]])
            and
            (last_word_p not in persistent._mas_shiritori_extra_words)):

            $ shiritori_loop = False
            call player_loss(reason = "invalid")

        # check against used words
        elif last_word_p in shiritori_used_words:
            $ shiritori_loop = False
            call player_loss(reason = "used")

        else:
            # update used word sets
            python:
                shiritori_used_words.add(last_word_p)
                shiritori_recent_words.add(last_word_p)
                if len(shiritori_recent_words) > shiritori_mem_size:
                    shiritori_recent_words.pop()

            # Monika's turn
            m "Hmm...{w=1}{nw}"

            # checking for turn exhaustion or if Monika has no valid words to play
            # valid word check allows for arbitrarily small word dictionaries/large shiritori_recent_words without an infinite loop occurring
            if (
                    (shiritori_monika_turnsleft[last_word_p[-1]] <= 0)
                    or
                    (
                        (shiritori_recent_words.intersection(dictionary_full[last_word_p[-1]]) != set(dictionary_full[last_word_p[-1]]))
                        and
                        (shiritori_recent_words.intersection(dictionary_monika[last_word_p[-1]]) != set(dictionary_monika[last_word_p[-1]]))
                    )
                ):
                pause (timelimit/4)
                call monika_loss(reason = "timeout")
                $ shiritori_loop = False

            else:
                # getting Monika's next word
                $ last_word_m_invalid = True
                while last_word_m_invalid:
                    if renpy.random.randint(1,100) <= full_dict_chance  and game_variant != "cities":
                        # small chance to have Monika pull from the full vocab
                        # not in cities mode - the dicts are the same, just decapitalized
                        $ last_word_m = renpy.random.choice(dictionary_full[last_word_p[-1]])
                    else:
                        $ last_word_m = renpy.random.choice(dictionary_monika[last_word_p[-1]])

                    # TODO: Add bad word filter here - Monika should be able to recognize them, but not use them herself
                    # checking if recently played
                    if last_word_m not in shiritori_recent_words:
                        $ last_word_m_invalid = False

                extend " [last_word_m]{w=1}{nw}"
                # checking if used
                if last_word_m.lower() in shiritori_used_words:
                    call monika_loss(reason = "used")
                    $ shiritori_loop = False

                else:
                    # update used word sets and remaining turns
                    python:
                        shiritori_monika_turnsleft[last_word_p[-1]] -= 1
                        shiritori_used_words.add(last_word_m.lower())
                        shiritori_recent_words.add(last_word_m.lower())
                        if len(shiritori_recent_words) > 10:
                            shiritori_recent_words.pop()

    return
