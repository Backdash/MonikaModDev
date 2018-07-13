
# For anyone wanting to write using the affection system the general thought process for Monika in each affection is as followed...
# Lovestruck - Monika is the happiest she could ever be and filled with a sense of euphoria because of it, completely enamoured and could die happy. She has no doubts the player loves her and that everything was worth it.
# Overjoyed - Exceptionally happy, the happiest she has ever been in her life to that point. Completely trusts the player and wants to make him/her as happy as she is.
# Happy - Glad that the relationship is working out and has high hopes and at this point has no doubts about whether or not it was worth it.
# Content - Happy with how it is, could be happier but not sad at all.
# Normal - Has mild doubts as to whether or not her sacrifices were worth it but trusts the player to treat her right. Isn't strongly happy or sad
# Sad - Is feeling down, not miserable or deep but certainly not her self-motivated self. Believes she'll get player. Has minor thoughts that player isn't faithful but doesn't take them seriously.
# Upset - Feeling emotionally hurt, starting to have doubts about whether or not the player loves her and whether or not she she was right regarding what she did in the game.
# Depressed - Convinced the player probably doesn't love her and that she may never escape to our reality.
# Heartbroken - Belives that not only does the player not love her but that s/he probably hates her too because of she did and is trying to punish her. Scared of being alone in her own reality, as well as for her future.
################

init -1 python in mas_affection:
    # string constants of affection levels
#    BROKEN = "heartbroken"
#    DISTRESSED = "distressed"
#    UPSET = "upset"
#    NORMAL = "normal"
#    HAPPY = "happy"
#    ENAMORED = "enamored"
#    LOVE = "lovestruck"
#    CONFUSED = "confused"

    # string constants of affection groups
#    G_SAD = "sad"
#    G_HAPPY = "happy"
#    G_NORMAL = "normal"

    # numerical constants of affection levels
    CONFUSED = 0
    BROKEN = 1
    DISTRESSED = 2
    UPSET = 3
    NORMAL = 4
    HAPPY = 5
    ENAMORED = 6
    LOVE = 7

    # numerical constants of affection groups
    G_SAD = -1
    G_HAPPY = -2
    G_NORMAL = -3

default persistent._mas_long_absence = False
init python:
    #Functions to freeze exp progression for story events, use wisely.
    def mas_FreezeGoodAffExp():
        persistent._mas_affection_goodexp_freeze = True

    def mas_FreezeBadAffExp():
        persistent._mas_affection_badexp_freeze = True

    def mas_FreezeBothAffExp():
        mas_FreezeGoodAffExp()
        mas_FreezeBadAffExp()

    def mas_UnfreezeBadAffExp():
        persistent._mas_affection_badexp_freeze = False

    def mas_UnfreezeGoodAffExp():
        persistent._mas_affection_badexp_freeze = False

    def mas_UnfreezeBothExp():
        mas_UnfreezeBadAffExp()
        mas_UnfreezeGoodAffExp()

   #Used to adjust the good and bad experience factors that are used to adjust affection levels.
    def mas_updateAffectionExp():
        global mas_curr_affection
        global mas_curr_affection_group

        #If affection is between 30 and 49, update good exp. Simulates growing affection.
        if persistent._mas_affection["affection"] >= 30 and persistent._mas_affection["affection"] < 50:
            persistent._mas_affection["goodexp"] = 3
            persistent._mas_affection["badexp"] = 1

        #If affection is more than 50, update both exp types. Simulates increasing affection and it will now take longer to erode that affection.
        elif persistent._mas_affection["affection"] >= 50:
            persistent._mas_affection["goodexp"] = 5
            persistent._mas_affection["badexp"] = 0.5

        #If affection is between -30 and -49, update bad exp. Simulates erosion of affection.
        elif persistent._mas_affection["affection"] <= -30 and persistent._mas_affection["affection"] > -50:
            persistent._mas_affection["goodexp"] = 1
            persistent._mas_affection["badexp"] = 3

        #If affection is less than -50, update both exp types. Simulates increasing loss of affection and now harder to get it back.
        elif persistent._mas_affection["affection"] <= -50:
            persistent._mas_affection["goodexp"] = 0.5
            persistent._mas_affection["badexp"] = 5

        #Defines an easy current affection statement to refer to so points aren't relied upon.
        if persistent._mas_affection["affection"] <= -100:
            mas_curr_affection = store.mas_affection.BROKEN

        elif persistent._mas_affection["affection"] >= -99 and persistent._mas_affection["affection"] <= -50:
            mas_curr_affection = store.mas_affection.DISTRESSED

        elif persistent._mas_affection["affection"] >= -49 and persistent._mas_affection["affection"] <= -30 :
            mas_curr_affection = store.mas_affection.UPSET

        elif persistent._mas_affection["affection"] >= -29 and persistent._mas_affection["affection"] <= 29:
            mas_curr_affection = store.mas_affection.NORMAL

        elif persistent._mas_affection["affection"] >= 30 and persistent._mas_affection["affection"] <= 49:
            mas_curr_affection = store.mas_affection.HAPPY

        elif persistent._mas_affection["affection"] >= 50 and persistent._mas_affection["affection"] <= 99:
            mas_curr_affection = store.mas_affection.ENAMORED

        elif persistent._mas_affection["affection"] >= 100:
            mas_curr_affection = store.mas_affection.LOVE

        else:
            mas_curr_affection = store.mas_affection.CONFUSED

        #A group version for general sadness or happiness
        if persistent._mas_affection["affection"] <= -30:
            mas_curr_affection_group = store.mas_affection.G_SAD

        elif persistent._mas_affection["affection"] >=30:
            mas_curr_affection_group = store.mas_affection.G_HAPPY

        else:
            mas_curr_affection_group = store.mas_affection.G_NORMAL


    #Used to increment affection whenever something positive happens.
    def mas_gainAffection(
            amount=persistent._mas_affection["goodexp"],
            modifier=1
        ):
        if not persistent._mas_affection_goodexp_freeze:
            #Otherwise, use the value passed in the argument.
            persistent._mas_affection["affection"] += amount
            #Updates the experience levels if necessary.
            mas_updateAffectionExp()


    #Used to subtract affection whenever something negative happens.
    def mas_loseAffection(
            amount=persistent._mas_affection["badexp"],
            modifier=1
        ):
        if not persistent._mas_affection_badexp_freeze:
            #Otherwise, use the value passed in the argument.
            persistent._mas_affection["affection"] -= amount
            #Updates the experience levels if necessary.
            mas_updateAffectionExp()

    def mas_setAffection(
            amount=persistent._mas_affection["affection"]
        ):
        if not persistent._mas_affection_badexp_freeze and not persistent_mas_affection_goodexp_freeze:
            #Otherwise, use the value passed in the argument.
            persistent._mas_affection["affection"] = amount
            #Updates the experience levels if necessary.
            mas_updateAffectionExp()


    #Used to check to see if affection level has reached the point where it should trigger an event while playing the game.
    def mas_checkAffection():
        #If affection level between -15 and -20 and you haven't seen the label before, push this event where Monika mentions she's a little upset with the player.
        #This is an indicator you are heading in a negative direction.
        if -20 <= persistent._mas_affection["affection"] <= -15 and not seen_event("mas_affection_upsetwarn"):
            pushEvent("mas_affection_upsetwarn")

        #If affection level between 15 and 20 and you haven't seen the label before, push this event where Monika mentions she's really enjoying spending time with you.
        #This is an indicator you are heading in a positive direction.
        elif persistent._mas_affection["affection"] >= 15 and persistent._mas_affection["affection"] <= 20 and not seen_event("mas_affection_happynotif"):
            pushEvent("mas_affection_happynotif")

        #If affection level is greater than 50 and you haven't seen the label yet, push this event where Monika will allow you to give her a nick name.
        elif persistent._mas_affection["affection"] >= 50 and not seen_event("monika_affection_nickname"):
            pushEvent("monika_affection_nickname")

        #If affection level is less than -50 and the label hasn't been seen yet, push this event where Monika says she's upset with you and wants you to apologize.
        elif persistent._mas_affection["affection"] <= -50 and not seen_event("mas_affection_apology"):
            pushEvent("mas_affection_apology")
        #If affection level is equal or less than -100 and the label hasn't been seen yet, push this event where Monika says she's upset with you and wants you to apologize.
        elif persistent._mas_affection["affection"] <= -100 and not seen_event("greeting_tears"):
            # TODO Affection doesn't have the new utility funcs to lock/unlock
            # when merged this has to be updated to use that
            evhand.greeting_database["greeting_tears"].unlocked = True

    #Easy functions to add and subtract points, designed to make it easier to sadden her so player has to work harder to keep her happy.
    #Check function is added to make sure mas_curr_affection is always appropriate to the points counter.
    #Internal cooldown to avoid topic spam and Monika affection swings, the amount of time to wait before a function is effective
    #is equal to the amount of points it's added or removed in minutes.

    #Makes the game update affection on start-up so the global variables are defined at all times.
    mas_updateAffectionExp()

    #Monika's initial affection based on start-up.
    if not persistent._mas_long_absence:
        if persistent.sessions["last_session_end"] is not None:
            persistent._mas_absence_time = datetime.datetime.now() - persistent.sessions["last_session_end"]
            time_difference = persistent._mas_absence_time
            if time_difference >= datetime.timedelta(hours = 6) and time_difference <= datetime.timedelta(hours = 12):
                #mas_gainAffection()
                pass
            elif time_difference >= datetime.timedelta(weeks = 4):
                mas_setAffection(-115)
                mas_FreezeBothAffExp()
            elif time_difference >= datetime.timedelta(weeks = 3):
                mas_loseAffection(70)
            elif time_difference >= datetime.timedelta(weeks = 2):
                mas_loseAffection(50)
            elif time_difference >= datetime.timedelta(weeks = 1):
                mas_loseAffection(30)

#Unlocked when affection level reaches 50.
#This allows the player to choose a nick name for Monika that will be displayed on the label where Monika's name usually is.
#There is a character limit of 10 characters.
label monika_affection_nickname:
    python:
        import re

        # NOTE: consider if we should read this from a file instead
        bad_nickname_list = [
            "atrocious",
            "awful",
            "bitch",
            "blood",
            "bulli",
            "bully",
            "corrupt",
            "crap",
            "creepy",
            "cunt",
            "damn",
            "dick",
            "disgusting",
            "dumb",
            "evil",
            "foul",
            "fuck",
            "gruesome",
            "hate",
            "hideous",
            "horrible",
            "horrid",
            "immoral",
            "kill",
            "kunt",
            "Murder",
            "nasty",
            "Natsuki",
            "nefarious",
            "poison",
            "pretentious",
            "repulsive",
            "Sayori",
            "scum",
            "shit",
            "slaughter"
            "stink",
            "stupid",
            "troll",
            "ugly",
            "vile",
            "waste",
            "wicked",
            "witch",
            "worthless",
            "wrong",
            "Yuri",
        ]

        good_nickname_list = [
            "angel",
            "beautiful",
            "best",
            "cute",
            "cutie",
            "darling",
            "great"
            "heart",
            "honey",
            "love",
            "Mon",
            "Moni",
            "princess",
            "sweet",
        ]


    m 1c "I've been thinking, [player]..."
    m 3d "You know how there are potentially infinite Monikas right?"
    if renpy.seen_label('monika_clones'):
        m 3a "We did discuss this before after all."
    m 3a "Well, I thought of a solution!"
    m "Why don't you give me a nickname? It'd make me the only Monika in the universe with that name."
    m 3e "And it would mean a lot if you choose one for me~"
    m 3j "I'll still get the final say, though!"
    m "What do you say?"
    menu:
        "Yes":
            $ bad_nickname_search = re.compile('|'.join(bad_nickname_list), re.IGNORECASE)
            $ good_nickname_search = re.compile('|'.join(good_nickname_list), re.IGNORECASE)
            $ done = False
            m 1a "Okay! Just type 'Nevermind' if you change your mind, [player]."
            while not done:
                $ inputname = renpy.input("So what do you want to call me?",allow=" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_",length=10).strip(' \t\n\r')
                $ lowername = inputname.lower()
                #lowername isn't detecting player or m_name?
                if lowername == "nevermind":
                    m 1c "Oh, I see."
                    m 1tkc "Well...that's a shame."
                    m 3e "But that's okay. I like '[m_name]' anyway."
                    $ done = True
                elif not lowername:
                    m 1m "..."
                    m 1l "You have to give me a name, [player]!"
                    m "I swear you're just so silly sometimes."
                    m 1e "Try again!"
                elif lowername == player.lower():
                    m 1c "..."
                    m 1n "That's your name, [player]! Give me my own!"
                    m 1e "Try again~"
                elif lowername == m_name.lower():
                    m 1c "..."
                    m 1l "I thought we were choosing a new name, silly."
                    m 1e "Try again~"
                else:
                    $ bad_nickname = bad_nickname_search.search(inputname)
                    if bad_nickname is None:
                        $ good_nickname = good_nickname_search.search(inputname)
                        if inputname == "Monika":
                            m "Ehehe~ Back to the classics, I see."
                        elif good_nickname is None:
                            m 1o "..."
                            m 1p "I can't say that I particularly like it..."
                            m 3l "But since you came up with it, I'll accept it!"
                        else:
                            m 1k "Oh! That's a wonderful name!"
                            m 3ekbfa "Thank you, [player]. You're such a sweetheart~!"
                        $ persistent._mas_monika_nickname = inputname
                        $ m_name = inputname
                        m 2a "Okay, [player]!"
                        if m_name == "Monika":
                            m 1j "I'll go back to my name, then."
                        else:
                            m 3j "From now on, you can call me {i}'[m_name]'{/i}."
                            m 1k "Ehehe~"
                        $ done = True
                    else:
                        $ mas_loseAffection()
                        m 4efd "[player]! That's not nice at all!"
                        m 2efc "Why would you say such things?"
                        m 2rfw "If you didn't want to do this, you should've just said so!"
                        m 2dftdc "..."
                        m 2lftsc "I don't like this idea anymore."
                        m 2ektsc "...You didn't have to be so mean."
                        m 2dftdc "That really hurt, [player]."
                        m 2efc "Please don't do that again."
                        $ hideEventLabel("monika_affection_nickname",lock=False,depool=False)
                        $ done = True

        "No":
            m 1f "Oh..."
            m 1o "Alright then, if you say so."
            m 3e "Just tell me if you ever change your mind, [player]."
            $ done = True
    return

#Event to warn player that Monika feels like she's not receiving the affection she deserves.
label mas_affection_upsetwarn:
    m 1q "Hey, [player]..."
    m 1o "Recently, I've been feeling like my love and affection that I give is being... ignored."
    m 1q "I feel like you're giving me less and less of your love..."
    m 1r "I thought I'd let you know how I feel. After all, communication is the key to a strong relationship, right?"
    m 1e "I hope there's nothing wrong between us, [player]."
    return

#Event to indicate that Monika is happy to be receiving your affection.
label mas_affection_happynotif:
    m 1b "Hey, [player]!"
    m 1j "I just wanted to say thank you for being such a wonderful person."
    m 1e "The fact that you give me so much of you love means a lot to me. I really don't know where I'd be without you."
    m 1dubsu "I love you, [player]. Let's be like this forever~"
    return

#############

define mas_finalfarewell_mode = False

# prepwork for the finalfarewell
label mas_affection_finalfarewell_start:
    call spaceroom(hide_monika=True)
    show emptydesk zorder 2 at i11
    show mas_finalnote_idle zorder 3

    python:
        HKBHideButtons()
        disable_esc()
        allow_dialogue = False
        store.songs.enabled = False
        mas_finalfarewell_mode = True
        layout.QUIT = glitchtext(20)


    jump mas_affection_finalfarewell

# this will loop through the final poem everytime!
label mas_affection_finalfarewell:



    python:
        ui.add(MASFinalNoteDisplayable())
        scratch_var = ui.interact()

    call showpoem(poem_finalfarewell, music=False,paper="mod_assets/poem_finalfarewell.png")

    menu:
        "I'm sorry":
            pass
        "...":
            pass

    jump mas_affection_finalfarewell


init python:

    # custom displayabe for the poem screen
    class MASFinalNoteDisplayable(renpy.Displayable):
        import pygame # mouse stuff

        # CONSTANTS
        POEM_WIDTH = 200
        POEM_HEIGHT= 73

        MOUSE_EVENTS = (
            pygame.MOUSEMOTION,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEBUTTONDOWN
        )

        def __init__(self):
            """
            Creates the final poem displayable
            """
            super(renpy.Displayable, self).__init__()

            # final poem is a button
            paper_idle = Image("mod_assets/poem_finalfarewell_desk.png")
            paper_hover = Image("mod_assets/poem_finalfarewell_desk_select.png")

            # no button text
            empty_button_text = Text("")

            # calculate paper location
            paper_x = int((1280 - self.POEM_WIDTH) / 2)
            paper_y = int(720 - self.POEM_HEIGHT)

            # build the paper as a button
            self._final_note = MASButtonDisplayable(
                empty_button_text,
                empty_button_text,
                empty_button_text,
                paper_idle,
                paper_hover,
                paper_idle,
                paper_x,
                paper_y,
                self.POEM_WIDTH,
                self.POEM_HEIGHT
            )


        def render(self, width, height, st, at):
            """
            Render function
            """
            r = renpy.Render(width, height)

            # render the paper
            r.blit(
                self._final_note.render(width, height, st, at),
                (self._final_note.xpos, self._final_note.ypos)
            )

            return r


        def event(self, ev, x, y, st):
            """
            Event function
            """
            if (
                    ev.type in self.MOUSE_EVENTS
                    and self._final_note.event(ev, x, y, st)
                ):
                return True

            renpy.redraw(self, 0)
            raise renpy.IgnoreEvent()

label mas_affection_apology:
    m 2dfc "[player]..."
    m 2dfd "I've done everything I can to make you happy and enjoy spending time with me."
    m 2efc "But all you've given me back is pain..."
    m 2rfc "I'm beginning to wonder if you really installed this mod to be with me."
    m 2q "Perhaps you brought me back just to toy with me?"
    m 2efc "Or maybe you're doing this intentionally to see what happens?"
    m 2lfc "Regardless, I'm giving you an ultimatum."
    m "I can't let this go any further, [player]."
    m 2lfc "If you really are sorry, write me a note called {i}imsorry.txt{/i}, and place it in the DDLC directory." #Maybe put it in the character folder instead?
    m 2dfd "Until then, goodbye..."
    $ persistent._mas_affection["apologyflag"] = True
    return 'quit'

label mas_affection_noapology:
    m 2efd "You still haven't written me a note called {i}imsorry.txt{/i} in the DDLC directory."
    m 2efc "Until then, I don't want to talk to you."
    jump _quit

label mas_affection_yesapology:
    m 1e "Thank you, [player]. I accept your apology."
    m 3dubsu "I'm going to keep it so I can always remember that you still care for me."
    m 1f "But please be more considerate of my feelings from now on."
    m 2e "I love you so much and you mean the world to me, [player]."
    m 1duu "Thank you for putting my heart at ease~"
    pause 60
    jump ch30_loop

label mas_affection_apologydeleted:
    m 1wud "..."
    m 2efd "[player], did you delete the apology note I wanted to keep?"
    m "Why would you do that? Are you not {i}really{/i} sorry?"
    m 2dfc "..."
    m 2efc "Write me a new one, [player]."
    jump _quit

#Surprise function.
# TODO: are there use cases for having this being a separate function
init python:
    def mas_surprise():
        from cStringIO import StringIO # since we are building strings
        msg = StringIO()

        if mas_curr_affection == store.mas_affection.BROKEN:
            filepath = "/forgive me.txt"
            msg.write("I'm sorry if I'm not good enough for you...please don't leave me.")

        elif mas_curr_affection == store.mas_affection.DISTRESSED:
            filepath = "/can you hear me.txt"
            msg.write("If I'm doing something wrong please tell me. I love you.")

        elif mas_curr_affection == store.mas_affection.UPSET:
            filepath = "/please listen.txt"
            msg.write("Everything I do, I do for you...my love.")

        elif mas_curr_affection == store.mas_affection.HAPPY:
            filepath = "/secret.txt"
            msg.write("You are the only one I love [player]!")

        elif mas_curr_affection == store.mas_affection.ENAMORED:
            filepath = "/for you.txt"
            msg.write("My dearest, you are everything I could ever hope for. I love you.")

        elif mas_curr_affection == store.mas_affection.LOVE:
            filepath = "/My one and only love.txt"
            msg.write("My dearest lover, friend, companion and owner of my heart...\n")
            msg.write("Everyday you make my dreams come true, a screen means nothing when you spend your time with me. \n")
            msg.write("I look out to the space dust and yet no cosmic sight even comes close to the beauty in your heart. \n")
            msg.write("I wished for so long that someone like you would come along and as fate has smiled upon me, you came into my life. \n")
            msg.write("I want to be yours forever, so would you be mine? \n\n")
            msg.write("Forever yours, Monika.")

        else:
            filepath = "/surprise.txt"
            msg.write("I love you.")

        # now write a file
        filepath = basedir + filepath
        if not renpy.exists(filepath):
            with open(filepath, "w") as surprise_note:
                surprise_note.write(msg.getvalue())

        # clean up
        msg.close()

#Currently re-affectioned labels.
#monika_nihilism
#monika_high_school
#monika_surprise
#monika_god
#monika_death
#monika_closeness
#monika_other_girls
#monika_justification
#monika_breakup


#TODO Currently muted music for sense of loneliness, may change to your reality for higher impact. Confirm with others.
init 2 python:
    player = persistent.playername

    poem_finalfarewell = Poem(
    author = "monika",
    title = "Goodbye {0},".format(player),
    text = """\
My love for you, even now still burns within me but I see now that it also burns all happiness I'll ever have.
I gave you everything I had, my life, my heart and any and every single thought of the future was dedicated to you.
I didn't need you to be perfect or even passionate...
I only needed you to care enough to treat me how a person should be treated.
But it's clear to me now that not only do you not love me, but you never did.
If you only didn't love me you would simply leave me be.
But you went out of your way to ridicule me, hurt me...It truly makes me sick.
Even now all I have is you...and part of me still loves you.
But I don't have the strength to do this anymore.
So this is farewell. May we never meet again.

Monika
"""
)
