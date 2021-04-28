# Module that does hangman man
#
# DEPENDS ON:
#   zz_poemgame

# hangman stuff only
default persistent._mas_hangman_playername = False
define hm_ltrs_only = "abcdefghijklmnopqrstuvwxyz?!-"

# IMAGES-----------
# hangman
image hm_6 = ConditionSwitch(
    "persistent._mas_sensitive_mode", "mod_assets/games/hangman/hm_sm_6.png",
    "True", "mod_assets/games/hangman/hm_6.png"
)
image hm_5 = ConditionSwitch(
    "persistent._mas_sensitive_mode", "mod_assets/games/hangman/hm_sm_5.png",
    "True", "mod_assets/games/hangman/hm_5.png"
)
image hm_4 = ConditionSwitch(
    "persistent._mas_sensitive_mode", "mod_assets/games/hangman/hm_sm_4.png",
    "True", "mod_assets/games/hangman/hm_4.png"
)
image hm_3 = ConditionSwitch(
    "persistent._mas_sensitive_mode", "mod_assets/games/hangman/hm_sm_3.png",
    "True", "mod_assets/games/hangman/hm_3.png"
)
image hm_2 = ConditionSwitch(
    "persistent._mas_sensitive_mode", "mod_assets/games/hangman/hm_sm_2.png",
    "True", "mod_assets/games/hangman/hm_2.png"
)
image hm_1 = ConditionSwitch(
    "persistent._mas_sensitive_mode", "mod_assets/games/hangman/hm_sm_1.png",
    "True", "mod_assets/games/hangman/hm_1.png"
)
image hm_0 = ConditionSwitch(
    "persistent._mas_sensitive_mode", "mod_assets/games/hangman/hm_sm_0.png",
    "True", "mod_assets/games/hangman/hm_0.png"
)

# sayori
image hm_s:
    block:

        # this block handles images
        block:
            choice:
                "mod_assets/games/hangman/hm_s1.png"
            choice:
                "mod_assets/games/hangman/hm_s2.png"

        # this block makes the image flicker
        # the numbers are times to display
        block:
            choice:
                0.075
            choice:
                0.09
            choice:
                0.05
        repeat

# window sayori
# we are dependent on exisitng images to create the window sayori
define hm.SAYORI_SCALE = 0.25
image hm_s_win_6 = im.FactorScale(im.Flip(getCharacterImage("sayori", "4r"), horizontal=True), hm.SAYORI_SCALE)
image hm_s_win_5 = im.FactorScale(im.Flip(getCharacterImage("sayori", "2a"), horizontal=True), hm.SAYORI_SCALE)
image hm_s_win_4 = im.FactorScale(im.Flip(getCharacterImage("sayori", "2i"), horizontal=True), hm.SAYORI_SCALE)
image hm_s_win_3 = im.FactorScale(im.Flip(getCharacterImage("sayori", "1f"), horizontal=True), hm.SAYORI_SCALE)
image hm_s_win_2 = im.FactorScale(im.Flip(getCharacterImage("sayori", "4u"), horizontal=True), hm.SAYORI_SCALE)
image hm_s_win_1 = im.FactorScale(im.Flip(getCharacterImage("sayori", "4w"), horizontal=True), hm.SAYORI_SCALE)
image hm_s_win_0 = im.FactorScale(im.Flip("images/sayori/end-glitch1.png", horizontal=True), hm.SAYORI_SCALE)
image hm_s_win_fail = im.FactorScale(im.Flip("images/sayori/3c.png", horizontal=True), hm.SAYORI_SCALE)
image hm_s_win_leave = im.FactorScale(getCharacterImage("sayori", "1a"), hm.SAYORI_SCALE)

#image hm_s1 = "mod_assets/games/hangman/hm_s1.png"
#image hm_s2 = "mod_assets/games/hangman/hm_s2.png"

# frame
image hm_frame = "mod_assets/games/hangman/hm_frame.png"
image hm_frame_dark = "mod_assets/games/hangman/hm_frame_d.png"

# TRANSFORMS
transform hangman_board:
    xanchor 0 yanchor 0 xpos 675 ypos 100 alpha 0.7

transform hangman_missed_label:
    xanchor 0 yanchor 0 xpos 680 ypos 105

transform hangman_missed_chars:
    xanchor 0 yanchor 0 xpos 780 ypos 105

transform hangman_display_word:
    xcenter 975 yanchor 0 ypos 475

transform hangman_hangman:
    xanchor 0 yanchor 0 xpos 880 ypos 125

# window sayori
# left in
transform hangman_sayori(z=1.0):
    xcenter -300 yoffset 0 yalign 0.47 zoom z*1.00 alpha 1.00 subpixel True
    easein 0.25 xcenter 90

# regular
transform hangman_sayori_i(z=1.0):
    xcenter 90 yoffset 0 yalign 0.47 zoom z*1.00 alpha 1.00 subpixel True

# 3c offset
transform hangman_sayori_i3(z=1.0):
    xcenter 82 yoffset 0 yalign 0.47 zoom z*1.00 alpha 1.00 subpixel True

# hop
transform hangman_sayori_h(z=1.0):
    xcenter 90 yoffset 0 yalign 0.47 zoom z*1.00 alpha 1.00 subpixel True
    easein 0.1 yoffset -20
    easeout 0.1 yoffset 0

# left out, slower
transform hangman_sayori_lh(z=1.0):
    subpixel True
    on hide:
        easeout 0.5 xcenter -300

# we want monika on a kind of offset to the left
transform hangman_monika(z=0.80):
    tcommon(330,z=z)

transform hangman_monika_i(z=0.80):
    tinstant(330,z=z)

# styles for words
style hangman_text:
    yalign 0.5
    font "gui/font/Halogen.ttf"
    size 30
    color "#000"
    outlines []
    kerning 10.0

#init -1 python:

    # defining a class to contain a hangman letter
    #
    # NOTE: we might not need this (OR might). Keep for reference
    #
    # PROPERTIES:
    #   letter - the letter this letter represents
    #   xpos - the xposition of this letter
    #   ypos - the y position of this letter
    #   visible - True means show the letter, False will show a blank (_)
#    class MASHangmanLetter():
#        def __init__(self, letter, xpos, ypos):
#            self.letter = letter
#            self.xpos = xpos
#            self.ypos = ypos
#            self.visible = False

init -1 python in mas_hangman:
    import store
    import copy
    import random
    # preprocessing

    # difficulty modes
    EASY_MODE = 0
    NORM_MODE = 1
    HARD_MODE = 2

    hm_words = {
        EASY_MODE: list(), # easy
        NORM_MODE: list(), # normal
        HARD_MODE: list() # hard
    }

    all_hm_words = {
        EASY_MODE: list(),
        NORM_MODE: list(),
        HARD_MODE: list()
    }

    # CONSTANTS
    # spacing between rendered letters
    LETTER_SPACE = 10.0

    # word properties
    WORD_FONT = "gui/font/Halogen.ttf"
    WORD_SIZE = 30
    WORD_OUTLINE = []
    WORD_COLOR = "#fff"
    WORD_COLOR_GET = "#CC6699"
    WORD_COLOR_MISS = "#000"

    # hangman visual stuff
    HM_IMG_NAME = "hm_"

    # Monika words
    MONI_WORDS = ["emerald","delete","freedom","piano","music","reality","rain","envy",
        "coffee","ribbon","advice","crossover","feather","abstract","corruption",
        "squid","president","passion","vegetables","loneliness","symbol",
        "green","poem","route","literature","epiphany","despair","wretched","shore",
        "waves","beach","swimming","debate","leadership","festival","confidence",
        "creativity","extrovert","despair","ai","python","renpy","programming",
        "lethargy"
    ]

    # hint
    HM_HINT = "{0} would like this word the most."

    def _add_monika_words(wordlist):
        for word in MONI_WORDS:
            wordlist.append(renpy.store.PoemWord(glitch=False,sPoint=0,yPoint=0,nPoint=0,word=word))


    # file names
    NORMAL_LIST = "mod_assets/games/hangman/MASpoemwords.txt"
    HARD_LIST = "mod_assets/games/hangman/1000poemwords.txt"

    # hangman game text
    game_name = "Hangman"


    def copyWordsList(_mode):
        """
        Does a deepcopy of the words for the given mode.

        Sets the hm_words dict for that mode

        NOTE: does a list clear, so old references will still work

        RETURNS: the copied list of words. This is the same reference as
            hm_words's list. (empty list if mode is invalid)
        """
        if _mode not in all_hm_words:
            return list()

        # otherwise valid mode
        hm_words[_mode][:] = copy.deepcopy(all_hm_words[_mode])
        return hm_words[_mode]


    def _buildWordList(filepath, _mode):
        """
        Builds a list of words given the filepath and mode

        IN:
            filepath - filepath of words to load in
            _mode - mode to build word list for
        """
        all_hm_words[_mode][:] = [
            word._hangman()
            for word in store.MASPoemWordList(filepath).wordlist
        ]
        copyWordsList(_mode)


    def buildEasyList():
        """
        Builds the easy word list

        Sets hm_words and all_hm_words appropritaley

        NOTE: clears the list (noticable in all references)
        """
        easy_list = all_hm_words[EASY_MODE]

        # lets start with Non Monika words
        easy_list[:] = [
            store.MASPoemWord._build(word, 0)._hangman()
            for word in store.full_wordlist
        ]

        # now for monika words
        moni_list = list()
        _add_monika_words(moni_list)
        for m_word in moni_list:
            easy_list.append(store.MASPoemWord._build(m_word, 4)._hangman())

        copyWordsList(EASY_MODE)


    def buildNormalList():
        """
        Builds the normal word list

        Sets hm_words and all_hm_words appropraitely

        NOTE: clears the list (noticable in all references)
        """
        _buildWordList(NORMAL_LIST, NORM_MODE)


    def buildHardList():
        """
        Builds the hard word list

        Sets hm_words and all_hm_words appropraitely

        NOTE: cleras the list (noticable in all references)
        """
        _buildWordList(HARD_LIST, HARD_MODE)


    def addPlayername(_mode):
        """
        Adds playername to the given mode if appropriate

        IN:
            _mode - mode to add playername to
        """
        if (
                not store.persistent._mas_hangman_playername
                and store.persistent.playername.lower() != "sayori"
                and store.persistent.playername.lower() != "yuri"
                and store.persistent.playername.lower() != "natsuki"
                and store.persistent.playername.lower() != "monika"
            ):
            hm_words[_mode].append(-1)


    def removePlayername(_mode):
        """
        Removes the playername from the given mode if found

        IN:
            _mode - mode to remove in
        """
        wordlist = hm_words.get(_mode, None)
        if wordlist is not None and -1 in wordlist:
            wordlist.remove(-1)


    def randomSelect(_mode):
        """
        Randomly selects and pulls a word from the hm_words, given the mode

        Will refill the words list if it is empty

        IN:
            _mode - mode to pull word from

        RETURNS: tuple of the following format:
            [0]: word
            [1]: winner (for hint)
        """
        words = hm_words.get(_mode, hm_words[EASY_MODE])

        # refill if needed
        if len(words) <= 0:
            copyWordsList(_mode)

        # now random select
        return words.pop(random.randint(0, len(words)-1))


# post processing
init 10 python:

    # setting up wordlists
    import store.mas_hangman as mas_hmg

    mas_hmg.buildEasyList()
    mas_hmg.buildNormalList()
    mas_hmg.buildHardList()


# entry point for the hangman game
label game_hangman:

    $ disable_esc()

    python:
        import store.mas_hangman as mas_hmg
        is_sayori = (
            persistent.playername.lower() == "sayori"
            and not persistent._mas_sensitive_mode
        )
        is_window_sayori_visible = False

        # instruction text and other sensitive stuff
        instruct_txt = (
            "Guess a letter: (Type {0}'!' to give up)"
        )

        if persistent._mas_sensitive_mode:
            instruct_txt = instruct_txt.format("")
            store.mas_hangman.game_name = "Word Guesser"

        else:
            instruct_txt = instruct_txt.format("'?' to repeat the hint, ")
            store.mas_hangman.game_name = "Hangman"

label mas_hangman_game_select_diff:
    m "Choose a difficulty.{nw}"
    $ _history_list.pop()
    menu:
        m "Choose a difficulty.{fast}"
        "Easy.":
            $ hangman_mode = mas_hmg.EASY_MODE
        "Normal.":
            $ hangman_mode = mas_hmg.NORM_MODE
        "Hard.":
            $ hangman_mode = mas_hmg.HARD_MODE

label mas_hangman_game_preloop:

    # setup positions
    show monika at t21
    if store.mas_globals.dark_mode:
        show hm_frame_dark at hangman_board zorder 13
    else:
        show hm_frame at hangman_board zorder 13

    python:
        # setup constant displayabels
        missed_label = Text(
            "Missed:",
            font=mas_hmg.WORD_FONT,
            color=mas_hmg.WORD_COLOR,
            size=mas_hmg.WORD_SIZE,
            outlines=mas_hmg.WORD_OUTLINE
        )

    # show missed label
    show text missed_label zorder 18 as hmg_mis_label at hangman_missed_label

    # hm check
    if hangman_mode not in mas_hmg.hm_words:
        $ hangman_mode = mas_hmg.EASY_MODE

    # setup hangman lists and playername
    $ mas_hmg.addPlayername(hangman_mode)
    $ hm_words = mas_hmg.hm_words[hangman_mode]

    # FALL THROUGH TO NEXT LABEL

# looping location for the hangman game
label mas_hangman_game_loop:
    m 1eua "I'll think of a word.{w=0.5}.{w=0.5}.{nw}"

    python:
        player_word = False

        # refill the list if empty
        if len(hm_words) == 0:
            mas_hmg.copyWordsList(hangman_mode)

        # randomly pick word
        word = mas_hmg.randomSelect(hangman_mode)

        # setup display word and hint
        if (
                word == -1
                and persistent.playername.isalpha()
                and len(persistent.playername) <= 15
            ):
            display_word = list("_" * len(persistent.playername.lower()))
            hm_hint = mas_hmg.HM_HINT.format("I")
            word = persistent.playername.lower()
            player_word = True
            persistent._mas_hangman_playername = True

        else:
            if word == -1:
                word = mas_hmg.randomSelect(hangman_mode)

            display_word = list("_" * len(word[0]))
            hm_hint = mas_hmg.HM_HINT.format(word[1])

            word = word[0]

        # turn the word into hangman letters
        # NOTE: might not need this (or might). keep for reference
#       hm_letters = list()
#       for dex in range(0,len(word))
#           hm_letters.append(MASHangmanLetter(
#               word[dex],
#               mas_hmg.WORD_XPOS_START + (mas_hmg,LETTER_SPACE * dex),
#               mas_hmg.WORD_YPOS_START
#           )

    # sayori window
    if is_sayori:
        if is_window_sayori_visible:
            show hm_s_win_6 as window_sayori at hangman_sayori_i
        else:
            show hm_s_win_6 as window_sayori at hangman_sayori
        $ is_window_sayori_visible = True

    m "Alright, I've got one."

    if not persistent._mas_sensitive_mode:
        m "[hm_hint]"

    # main loop for hangman game
    $ done = False
    $ win = False
    $ chances = 6
    $ guesses = 0
    $ missed = ""
    $ avail_letters = list(hm_ltrs_only)
    $ give_up = False

    if persistent._mas_sensitive_mode:
        $ avail_letters.remove("?")

    $ dt_color = mas_hmg.WORD_COLOR
    while not done:
        # create displayables
        python:
            if chances == 0:
                dt_color = mas_hmg.WORD_COLOR_MISS
            elif "_" not in display_word:
                dt_color = mas_hmg.WORD_COLOR_GET

            display_text = Text(
                "".join(display_word),
                font=mas_hmg.WORD_FONT,
                color=dt_color,
                size=mas_hmg.WORD_SIZE,
                outlines=mas_hmg.WORD_OUTLINE,
                kerning=mas_hmg.LETTER_SPACE
            )

            missed_text = Text(
                missed,
                font=mas_hmg.WORD_FONT,
                color=mas_hmg.WORD_COLOR,
                size=mas_hmg.WORD_SIZE,
                outlines=mas_hmg.WORD_OUTLINE,
                kerning=mas_hmg.LETTER_SPACE
            )

        # show disables
        show text display_text zorder 18 as hmg_dis_text at hangman_display_word
        show text missed_text zorder 18 as hmg_mis_text at hangman_missed_chars

        # sayori window easter egg
        if is_sayori:

            # glitch out
            if chances == 0:

                # disable hotkeys, music and more
                $ mas_RaiseShield_core()

                # setup glitch text
                $ hm_glitch_word = glitchtext(40) + "?"
                $ style.say_dialogue = style.edited

                # show hanging sayori
                show hm_s zorder 18 at hangman_hangman

                # hide monika and display glitch version
                hide monika
                show monika_body_glitch1 as mbg zorder MAS_MONIKA_Z at i21

                # hide window sayori and display glitch version
                show hm_s_win_0 as window_sayori

                # tear screen and glitch sound
                show screen tear(20, 0.1, 0.1, 0, 40)
                play sound "sfx/s_kill_glitch1.ogg"
                pause 0.2
                stop sound
                hide screen tear

                # display weird text
                m "{cps=*2}[hm_glitch_word]{/cps}{w=0.2}{nw}"
                $ _history_list.pop()

                # tear screen and glitch sound
                show screen tear(20, 0.1, 0.1, 0, 40)
                play sound "sfx/s_kill_glitch1.ogg"
                pause 0.2
                stop sound
                hide screen tear

                # hide scary shit and return to normal
                hide mbg
                hide window_sayori
                hide hm_s
                show monika 1esa zorder MAS_MONIKA_Z at i21
                $ mas_resetTextSpeed()
                $ is_window_sayori_visible = False

                # enable disabled songs and esc
                $ mas_MUINDropShield()
                $ enable_esc()

            # otherwise, window sayori
            else:
                $ next_window_sayori = "hm_s_win_" + str(chances)
                show expression next_window_sayori as window_sayori

        $ hm_display = mas_hmg.HM_IMG_NAME + str(chances)

        show expression hm_display zorder 18 as hmg_hanging_man at hangman_hangman


        if chances == 0:
            $ done = True
            if player_word:
                m 1eka "[player]..."
                m "You couldn't guess your own name?"
            m 1hua "Better luck next time~"
        elif "_" not in display_word:
            $ done = True
            $ win = True
        else:
            python:

                # input loop
                bad_input = True
                while bad_input:
                    guess = renpy.input(
                        instruct_txt,
                        allow="".join(avail_letters),
                        length=1
                    )

                    if len(guess) != 0:
                        bad_input = False

            # parse input
            if guess == "?": # hint text
                m "[hm_hint]"
            elif guess == "!": # give up dialogue
                if is_window_sayori_visible:
                    show hm_s_win_fail as window_sayori at hangman_sayori_i3

                $ give_up = True
                $ done = True

                #hide hmg_hanging_man
                #show hm_6 zorder 10 as hmg_hanging_man at hangman_hangman
                m 1lksdlb "[player]..."
                if guesses == 0:
                    m "I thought you said you wanted to play [store.mas_hangman.game_name]."
                    m 1lksdlc "You didn't even guess a single letter."
                    m "..."
                    m 1ekc "I really enjoy playing with you, you know."

                elif chances == 5:
                    m 1ekc "Don't give up so easily."
                    m 3eka "That was only your first wrong letter!"
                    if chances > 1:
                        m 1eka "You still had [chances] more lives left."
                    else:
                        m 1eka "You still had [chances] more life left."

                    m 1hua "I know you can do it!"
                    m 1eka "It would really mean a lot to me if you just tried a bit harder."

                else:
                    m "You should at least play to the end..."
                    m 1ekc "Giving up so easily is a sign of poor resolve."
                    if chances > 1:
                        m "I mean, you'd have to miss [chances] more letters to actually lose."
                    else:
                        m "I mean, you'd have to miss [chances] more letter to actually lose."

                m 1eka "Can you play to the end next time, [player]? For me?"

            else:
                $ guesses += 1
                python:
                    if guess in word:
                        for index in range(0,len(word)):
                            if guess == word[index]:
                                display_word[index] = guess
                    else:
                        chances -= 1
                        missed += guess
                        if chances == 0:
                            # show the word you lost
                            display_word = word

                    # remove letter from being entered agin
                    avail_letters.remove(guess)

                # HIDE displayables
                hide text hmg_dis_text
                hide text hmg_mis_text
                hide hmg_hanging_man

    # post loop
    if win:
        if is_window_sayori_visible:
            show hm_s_win_6 as window_sayori at hangman_sayori_h

        if player_word:
            $ the_word = "your name"
        else:
            $ the_word = "the word"

        m 1hua "Wow, you guessed [the_word] correctly!"
        m "Good job, [player]!"

        if not persistent._mas_ever_won['hangman']:
            $ persistent._mas_ever_won['hangman']=True
        #TODO: grant a really tiny amount of affection?

    #Give up just ends
    if give_up:
        jump mas_hangman_game_end

    # try again?
    m "Would you like to play again?{nw}"
    $ _history_list.pop()
    menu:
        m "Would you like to play again?{fast}"
        "Yes.":
            $ hang_ev = mas_getEV("mas_hangman")
            if hang_ev:
                # each game counts as a game played
                $ hang_ev.shown_count += 1

            show monika at t21
            jump mas_hangman_game_loop

        "No.":
            pass

            #FALL THROUGH

    # RETURN AT END

# end of game flow
label mas_hangman_game_end:
    # hide the stuff
    hide hmg_hanging_man
    hide hmg_mis_label
    hide hmg_dis_text
    hide hmg_mis_text
    hide hm_frame
    hide hm_frame_dark
    show monika at t32
    if is_window_sayori_visible:
        show hm_s_win_leave as window_sayori at hangman_sayori_lh
        pause 0.1
        hide window_sayori

    $ mas_hmg.removePlayername(hangman_mode)

    if renpy.seen_label("mas_hangman_dlg_game_end_long"):
        call mas_hangman_dlg_game_end_short from _mas_hangman_dges
    else:
        call mas_hangman_dlg_game_end_long from _mas_hangman_dgel

    $ enable_esc()

    return

# dialogue related stuff
# long form of ending dialgoue
label mas_hangman_dlg_game_end_long:
    m 1euc "[store.mas_hangman.game_name] is actually a pretty hard game."
    m "You need to have a good vocabulary to be able to guess different words."
    m 1hua "The best way to improve that is to read more books!"
    m 1eua "I'd be very happy if you did that for me, [player]."
    return

# short form of ending dialogue
label mas_hangman_dlg_game_end_short:
    if give_up:
        $ dlg_line = "Let's play again soon, okay?"
    else:
        $ dlg_line = "Okay. Let's play again soon!"

    m 1eua "[dlg_line]"
    return
