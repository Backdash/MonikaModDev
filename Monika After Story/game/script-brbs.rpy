## This script file holds all of the brb topics
# Some conventions:
#   - All brbs should have their markSeen set to True so they don't show up in unseen
#   - Brbs should return "idle" to move into idle mode
#   - Brbs should be short and sweet. Nothing long which makes it feel like an actual topic or is keeping you away
#       A good practice for these should be no more than 10 lines will be said before you go into idle mode.
init 10 python in mas_brbs:
    import store

    def get_wb_quip():
        """
        Picks a random welcome back quip and returns it
        Should be used for normal+ quips

        OUT:
            A randomly selected quip for coming back to the spaceroom
        """

        return renpy.substitute(renpy.random.choice([
            _("So, what else did you want to do today?"),
            _("What else did you want to do today?"),
            _("Is there anything else you wanted to do today?"),
            _("What else should we do today?"),
        ]))

    def was_idle_for_at_least(idle_time, brb_evl):
        """
        Checks if the user was idle (from the brb_evl provided) for at least idle_time

        IN:
            idle_time - Minimum amount of time the user should have been idle for in order to return True
            brb_evl - Eventlabel of the brb to use for the start time

        OUT:
            boolean:
                - True if it has been at least idle_time since seeing the brb_evl
                - False otherwise
        """
        brb_ev = store.mas_getEV(brb_evl)
        return brb_ev and brb_ev.timePassedSinceLastSeen_dt(idle_time)

# label to use if we want to get back into idle from a callback
label mas_brb_back_to_idle:
    # sanity check
    if globals().get("brb_label", -1) == -1:
        return

    python:
        mas_idle_mailbox.send_idle_cb(brb_label + "_callback")
        persistent._mas_idle_data[brb_label] = True
        mas_globals.in_idle_mode = True
        persistent._mas_in_idle_mode = True
        renpy.save_persistent()
        mas_dlgToIdleShield()

    return "idle"

# label for generic reactions for low affection callback paths
# to be used if a specific reaction isn't needed or provided
label mas_brb_generic_low_aff_callback:
    if mas_isMoniDis(higher=True):
        python:
            cb_line = renpy.substitute(renpy.random.choice([
                _("Oh...{w=0.3}you're back."),
                _("Oh...{w=0.3}welcome back."),
                _("All done?"),
                _("Welcome back."),
                _("Oh...{w=0.3}there you are."),
            ]))

        m 2ekc "[cb_line]"

    else:
        m 6ckc "..."

    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_brb_idle",
            prompt="I'll be right back",
            category=['be right back'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_brb_idle:
    if mas_isMoniAff(higher=True):
        m 1eua "Alright, [player]."

        show monika 1eta at t21
        python:
            #For options that can basically be an extension of generics and don't need much specification
            brb_reason_options = [
                (_("I'm going to get something."), True, False, False),
                (_("I'm going to do something."), True, False, False),
                (_("I'm going to make something."), True, False, False),
                (_("I have to check something."), True, False, False),
                (_("Someone's at the door."), True, False, False),
                (_("Nope."), None, False, False),
            ]

            renpy.say(m, "Doing anything specific?", interact=False)
        call screen mas_gen_scrollable_menu(brb_reason_options, mas_ui.SCROLLABLE_MENU_TALL_AREA, mas_ui.SCROLLABLE_MENU_XALIGN)
        show monika at t11

        if _return:
            m 1eua "Oh alright.{w=0.2} {nw}"
            extend 3hub "Hurry back, I'll be waiting here for you~"

        else:
            m 1hub "Hurry back, I'll be waiting here for you~"

    elif mas_isMoniNormal(higher=True):
        m 1hub "Hurry back, [player]!"

    elif mas_isMoniDis(higher=True):
        m 2rsc "Oh...{w=0.5}okay."

    else:
        m 6ckc "..."

    #Set up the callback label
    $ mas_idle_mailbox.send_idle_cb("monika_brb_idle_callback")
    #Then the idle data
    $ persistent._mas_idle_data["monika_idle_brb"] = True
    return "idle"

label monika_brb_idle_callback:
    $ wb_quip = mas_brbs.get_wb_quip()

    if mas_isMoniAff(higher=True):
        m 1hub "Welcome back, [player]. I missed you~"
        m 1eua "[wb_quip]"

    elif mas_isMoniNormal(higher=True):
        m 1hub "Welcome back, [player]!"
        m 1eua "[wb_quip]"

    else:
        call mas_brb_generic_low_aff_callback

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_writing_idle",
            prompt="I'm going to write for a bit",
            category=['be right back'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_writing_idle:
    if mas_isMoniNormal(higher=True):
        if (
            mas_isMoniHappy(higher=True)
            and random.randint(1,5) == 1
        ):
            m 1eub "Oh! You're going to{cps=*2} write me a love letter, [player]?{/cps}{nw}"
            $ _history_list.pop()
            m "Oh! You're going to{fast} go write something?"

        else:
            m 1eub "Oh! You're going to go write something?"

        m 1hua "That makes me so glad!"
        m 3eua "Maybe someday you could share it with me...{w=0.3} {nw}"
        extend 3hua "I'd love to read your work, [player]!"
        m 3eua "Anyway, just let me know when you're done."
        m 1hua "I'll be waiting right here for you~"

    elif mas_isMoniUpset():
        m 2esc "Alright."

    elif mas_isMoniDis():
        m 6lkc "I wonder what you have on your mind..."
        m 6ekd "Don't forget to come back when you're done..."

    else:
        m 6ckc "..."

    #Set up the callback label
    $ mas_idle_mailbox.send_idle_cb("monika_writing_idle_callback")
    #Then the idle data
    $ persistent._mas_idle_data["monika_idle_writing"] = True
    return "idle"

label monika_writing_idle_callback:

    if mas_isMoniNormal(higher=True):
        $ wb_quip = mas_brbs.get_wb_quip()
        m 1eua "Done writing, [player]?"
        m 1eub "[wb_quip]"

    else:
        call mas_brb_generic_low_aff_callback

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_shower",
            prompt="I'm going to take a shower",
            category=['be right back'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_shower:
    if mas_isMoniLove():
        m 1eua "Going to go shower?"

        if renpy.random.randint(1, 50) == 1:
            m 3tub "Can I come with you?{nw}"
            $ _history_list.pop()
            show screen mas_background_timed_jump(2, "bye_brb_shower_timeout")
            menu:
                m "Can I come with you?{fast}"

                "Yes.":
                    hide screen mas_background_timed_jump
                    m 2wubsd "Oh, uh...{w=0.5}you sure answered that fast."
                    m 2hkbfsdlb "You...{w=0.5}sure seem eager to let me tag along, huh?"
                    m 2rkbfa "Well..."
                    m 7tubfu "I'm afraid you'll just have to go without me while I'm stuck here."
                    m 7hubfb "Sorry, [player], ahaha!"
                    show monika 5kubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
                    m 5kubfu "Maybe another time~"

                "No.":
                    hide screen mas_background_timed_jump
                    m 2eka "Aw, you rejected me so fast."
                    m 3tubsb "Are you shy, [player]?"
                    m 1hubfb "Ahaha!"
                    show monika 5tubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
                    m 5tubfu "Alright, I won't follow you this time, ehehe~"

        else:
            m 1hua "I'm glad you're keeping yourself clean, [player]."
            m 1eua "Have a nice shower~"

    elif mas_isMoniNormal(higher=True):
        m 1eub "Going to go shower? Alright."
        m 1eua "See you when you're done~"

    elif mas_isMoniUpset():
        m 2esd "Enjoy your shower, [player]..."
        m 2rkc "Hopefully it'll help you clear your mind."

    elif mas_isMoniDis():
        m 6ekc "Hmm?{w=0.5} Have a nice shower, [player]."

    else:
        m 6ckc "..."

    #Set up the callback label
    $ mas_idle_mailbox.send_idle_cb("monika_idle_shower_callback")
    #Then the idle data
    $ persistent._mas_idle_data["monika_idle_shower"] = True
    return "idle"

label monika_idle_shower_callback:
    if mas_isMoniNormal(higher=True):
        m 1eua "Welcome back, [player]."

        if (
            mas_isMoniLove()
            and renpy.seen_label("monikaroom_greeting_ear_bathdinnerme")
            and mas_getEVL_shown_count("monika_idle_shower") != 1 #Since the else block has a one-time only line, we force it on first use
            and renpy.random.randint(1,20) == 1
        ):
            m 3tubsb "Now that you've had your shower, would you like your dinner, or maybe{w=0.5}.{w=0.5}.{w=0.5}."
            m 1hubsa "You could just relax with me some more~"
            m 1hub "Ahaha!"

        else:
            m 1hua "I hope you had a nice shower."
            if mas_getEVL_shown_count("monika_idle_shower") == 1:
                m 3eub "Now we can get back to having some good, {i}clean{/i} fun together..."
                m 1hub "Ahaha!"

    elif mas_isMoniUpset():
        m 2esc "I hope you enjoyed your shower. {w=0.2}Welcome back, [player]."

    else:
        call mas_brb_generic_low_aff_callback

    return

label bye_brb_shower_timeout:
    hide screen mas_background_timed_jump
    $ _history_list.pop()
    m 1hubsa "Ehehe~"
    m 3tubfu "Nevermind that, [player]."
    m 1hubfb "I hope you have a nice shower!"

    #Set up the callback label
    $ mas_idle_mailbox.send_idle_cb("monika_idle_shower_callback")
    #Then the idle data
    $ persistent._mas_idle_data["monika_idle_shower"] = True
    return "idle"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_game",
            category=['be right back'],
            prompt="I'm going to game for a bit",
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_game:
    if mas_isMoniNormal(higher=True):
        m 1eud "Oh, you're going to play another game?"
        m 1eka "That's alright, [player]."

        label .skip_intro:
        python:
            gaming_quips = [
                _("Good luck, have fun!"),
                _("Enjoy your game!"),
                _("I'll be cheering you on!"),
                _("Do your best!")
            ]
            gaming_quip=renpy.random.choice(gaming_quips)

        m 3hub "[gaming_quip]"

    elif mas_isMoniUpset():
        m 2tsc "Enjoy your other games."

    elif mas_isMoniDis():
        m 6ekc "Please...{w=0.5}{nw}"
        extend 6dkc "don't forget about me..."

    else:
        m 6ckc "..."

    $ mas_idle_mailbox.send_idle_cb("monika_idle_game_callback")
    $ persistent._mas_idle_data["monika_idle_game"] = True
    return "idle"

label monika_idle_game_callback:
    if mas_isMoniNormal(higher=True):
        m 1eub "Welcome back, [player]!"
        m 1eua "I hope you had fun with your game."
        m 1hua "Ready to spend some more time together? Ehehe~"

    elif mas_isMoniUpset():
        m 2tsc "Had fun, [player]?"

    elif mas_isMoniDis():
        m 6ekd "Oh...{w=0.5} You actually came back to me..."

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_coding",
            prompt="I'm going to code for a bit",
            category=['be right back'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_coding:
    if mas_isMoniNormal(higher=True):
        m 1eua "Oh! Going to code something?"

        if persistent._mas_pm_has_code_experience is False:
            m 1etc "I thought you didn't do that."
            m 1eub "Did you pick up programming since we talked about it last time?"

        elif persistent._mas_pm_has_contributed_to_mas or persistent._mas_pm_wants_to_contribute_to_mas:
            m 1tua "Something for me, perhaps?"
            m 1hub "Ahaha~"

        else:
            m 3eub "Do your best to keep your code clean and easy to read."
            m 3hksdlb "...You'll thank yourself later!"

        m 1eua "Anyway, just let me know when you're done."
        m 1hua "I'll be right here, waiting for you~"

    elif mas_isMoniUpset():
        m 2euc "Oh, you're going to code?"
        m 2tsc "Well, don't let me stop you."

    elif mas_isMoniDis():
        m 6ekc "Alright."

    else:
        m 6ckc "..."

    $ mas_idle_mailbox.send_idle_cb("monika_idle_coding_callback")
    $ persistent._mas_idle_data["monika_idle_coding"] = True
    return "idle"

label monika_idle_coding_callback:
    if mas_isMoniNormal(higher=True):
        $ wb_quip = mas_brbs.get_wb_quip()
        if mas_brbs.was_idle_for_at_least(datetime.timedelta(minutes=20), "monika_idle_coding"):
            m 1eua "Done for now, [player]?"
        else:
            m 1eua "Oh, done already, [player]?"

        m 3eub "[wb_quip]"

    else:
        call mas_brb_generic_low_aff_callback

    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_workout",
            prompt="I'm going to work out for a bit",
            category=['be right back'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_workout:
    if mas_isMoniNormal(higher=True):
        m 1hub "Okay, [player]!"
        if persistent._mas_pm_works_out is False:
            m 3eub "Working out is a great way to take care of yourself!"
            m 1eka "I know it might be hard to start out,{w=0.2}{nw}"
            extend 3hua " but it's definitely a habit worth forming."
        else:
            m 1eub "It's good to know you're taking care of your body!"
        m 3esa "You know how the saying goes, 'A healthy mind in a healthy body.'"
        m 3hua "So go work up a good sweat, [player]~"
        m 1tub "Just let me know when you've had enough."

    elif mas_isMoniUpset():
        m 2esc "Good to know you're taking care of{cps=*2} something, at least.{/cps}{nw}"
        $ _history_list.pop()
        m "Good to know you're taking care of{fast} yourself, [player]."
        m 2euc "I'll be waiting for you to get back."

    elif mas_isMoniDis():
        m 6ekc "Alright."

    else:
        m 6ckc "..."

    $ mas_idle_mailbox.send_idle_cb("monika_idle_workout_callback")
    $ persistent._mas_idle_data["monika_idle_workout"] = True
    return "idle"

label monika_idle_workout_callback:
    if mas_isMoniNormal(higher=True):
        $ wb_quip = mas_brbs.get_wb_quip()
        if mas_brbs.was_idle_for_at_least(datetime.timedelta(minutes=60), "monika_idle_workout"):
            # TODO: In the future add another topic which would
            # unlock once the player has seen this specific path some number of times.

            m 2esa "You sure took your time, [player].{w=0.3}{nw}"
            extend 2eub " That must've been one heck of a workout."
            m 2eka "It's good to push your limits, but you shouldn't overdo it."

        elif mas_brbs.was_idle_for_at_least(datetime.timedelta(minutes=10), "monika_idle_workout"):
            m 1esa "Done with your workout, [player]?"

        else:
            m 1euc "Back already, [player]?"
            m 1eka "I'm sure you can go on for a bit longer if you try."
            m 3eka "Taking breaks is fine, but you shouldn't leave your workouts unfinished."
            m 3ekb "Are you sure you can't keep going?{nw}"
            $ _history_list.pop()
            menu:
                m "Are you sure you can't keep going?{fast}"

                "I'm sure.":
                    m 1eka "That's okay."
                    m 1hua "I'm sure you did your best, [player]~"

                "I'll try to keep going.":
                    # continue workout and return Monika to idle state
                    m 1hub "That's the spirit!"

                    $ brb_label = "monika_idle_workout"
                    $ pushEvent("mas_brb_back_to_idle",skipeval=True)
                    return

        m 7eua "Make sure to rest properly and maybe get a snack to get some energy back."
        m 7eub "[wb_quip]"

    elif mas_isMoniUpset():
        m 2euc "Done with your workout, [player]?"

    else:
        call mas_brb_generic_low_aff_callback

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_nap",
            prompt="I'm going to take a nap",
            category=['be right back'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_nap:
    if mas_isMoniNormal(higher=True):
        m 1eua "Going to take a nap, [player]?"
        m 3eua "They're a healthy way to rest during the day if you're feeling tired."
        m 3hua "I'll watch over you, don't worry~"
        m 1hub "Sweet dreams!"

    elif mas_isMoniUpset():
        m 2eud "Alright, I hope you feel rested afterwards."
        m 2euc "I hear naps are good for you, [player]."

    elif mas_isMoniDis():
        m 6ekc "Alright."

    else:
        m 6ckc "..."

    $ mas_idle_mailbox.send_idle_cb("monika_idle_nap_callback")
    $ persistent._mas_idle_data["monika_idle_nap"] = True
    return "idle"

label monika_idle_nap_callback:
    if mas_isMoniNormal(higher=True):
        $ wb_quip = mas_brbs.get_wb_quip()
        if mas_brbs.was_idle_for_at_least(datetime.timedelta(hours=5), "monika_idle_nap"):
            m 2hksdlb "Oh, [player]! You're finally awake!"
            m 7rksdlb "When you said you were going to take a nap, I was expecting you take maybe an hour or two..."
            m 1hksdlb "I guess you must have been really tired, ahaha..."
            m 3eua "But at least after sleeping for so long, you'll be here with me for a while, right?"
            m 1hua "Ehehe~"

        elif mas_brbs.was_idle_for_at_least(datetime.timedelta(hours=1), "monika_idle_nap"):
            m 1hua "Welcome back, [player]!"
            m 1eua "Did you have a nice nap?"
            m 3hua "You were out for some time, so I hope you're feeling rested~"
            m 1eua "[wb_quip]"

        elif mas_brbs.was_idle_for_at_least(datetime.timedelta(minutes=5), "monika_idle_nap"):
            m 1hua "Welcome back, [player]~"
            m 1eub "I hope you had a nice little nap."
            m 3eua "[wb_quip]"

        else:
            m 1eud "Oh, back already?"
            m 1euc "Did you change your mind?"
            m 3eka "Well, I'm not complaining, but you should take a nap if you feel like it later."
            m 1eua "I wouldn't want you to be too tired, after all."

    elif mas_isMoniUpset():
        m 2euc "Done with your nap, [player]?"

    else:
        call mas_brb_generic_low_aff_callback

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_homework",
            prompt="I'm going to do some homework",
            category=['be right back'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_homework:
    if mas_isMoniNormal(higher=True):
        m 1eub "Oh, okay!"
        m 1hua "I'm proud of you for taking your studies seriously."
        m 1eka "Don't forget to come back to me when you're done~"

    elif mas_isMoniDis(higher=True):
        m 2euc "Alright...{w=0.5}"
        if random.randint(1,5) == 1:
            m 2rkc "...Good luck with your homework, [player]."

    else:
        m 6ckc "..."

    #Set up the callback label
    $ mas_idle_mailbox.send_idle_cb("monika_idle_homework_callback")
    #Then the idle data
    $ persistent._mas_idle_data["monika_idle_homework"] = True
    return "idle"

label monika_idle_homework_callback:
    if mas_isMoniDis(higher=True):
        m 2esa "All done, [player]?"

        if mas_isMoniNormal(higher=True):
            m 2ekc "I wish I could've been there to help you, but there isn't much I can do about that just yet, sadly."
            m 7eua "I'm sure we could both be a lot more efficient doing homework if we could work together."

            if mas_isMoniAff(higher=True) and random.randint(1,5) == 1:
                m 3rkbla "...Although, that's assuming we don't get {i}too{/i} distracted, ehehe..."

            m 1eua "But anyway,{w=0.2} {nw}"
            extend 3hua "now that you're done, let's enjoy some more time together."

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_working",
            prompt="I'm going to work on something",
            category=['be right back'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_working:
    if mas_isMoniNormal(higher=True):
        m 1eua "Alright, [player]."
        m 1eub "Don't forget to take a break every now and then!"

        if mas_isMoniAff(higher=True):
            m 3rkb "I wouldn't want my sweetheart to spend more time on [his] work than with me~"

        m 1hua "Good luck with your work!"

    elif mas_isMoniDis(higher=True):
        m 2euc "Okay, [player]."

        if random.randint(1,5) == 1:
            m 2rkc "...Please come back soon..."

    else:
        m 6ckc "..."

    #Set up the callback label
    $ mas_idle_mailbox.send_idle_cb("monika_idle_working_callback")
    #Then the idle data
    $ persistent._mas_idle_data["monika_idle_working"] = True
    return "idle"

label monika_idle_working_callback:
    if mas_isMoniNormal(higher=True):
        m 1eub "Finished with your work, [player]?"
        show monika 5hua at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5hua "Then let's relax together, you've earned it~"

    elif mas_isMoniDis(higher=True):
        m 2euc "Oh, you're back..."
        m 2eud "...Was there anything else you wanted to do, now that you're done with your work?"

    else:
        m 6ckc "..."

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_screen_break",
            prompt="My eyes need a break from the screen",
            category=['be right back'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_screen_break:
    if mas_isMoniNormal(higher=True):
        if mas_timePastSince(mas_getEVL_last_seen("monika_idle_screen_break"), mas_getSessionLength()):

            if mas_getSessionLength() < datetime.timedelta(minutes=40):
                m 1esc "Oh,{w=0.3} okay."
                m 3eka "You haven't been here for that long but if you say you need a break, then you need a break."

            elif mas_getSessionLength() < datetime.timedelta(hours=2, minutes=30):
                m 1eua "Going to rest your eyes for a bit?"

            else:
                m 1lksdla "Yeah, you probably need that, don't you?"

            m 1hub "I'm glad you're taking care of your health, [player]."

            if not persistent._mas_pm_works_out and random.randint(1,3) == 1:
                m 3eua "Why not take the opportunity to do a few stretches as well, hmm?"
                m 1eub "Anyway, come back soon!~"

            else:
                m 1eub "Come back soon!~"

        else:
            m 1eua "Taking another break, [player]?"
            m 1hua "Come back soon!~"

    elif mas_isMoniUpset():
        m 2esc "Oh...{w=0.5} {nw}"
        extend 2rsc "Okay."

    elif mas_isMoniDis():
        m 6ekc "Alright."

    else:
        m 6ckc "..."

    $ mas_idle_mailbox.send_idle_cb("monika_idle_screen_break_callback")
    $ persistent._mas_idle_data["monika_idle_screen_break"] = True
    return "idle"

label monika_idle_screen_break_callback:
    if mas_isMoniNormal(higher=True):
        $ wb_quip = mas_brbs.get_wb_quip()
        m 1eub "Welcome back, [player]."

        if mas_brbs.was_idle_for_at_least(datetime.timedelta(minutes=30), "monika_idle_screen_break"):
            m 1hksdlb "You must've really needed that break, considering how long you were gone."
            m 1eka "I hope you're feeling a little better now."
        else:
            m 1hua "I hope you're feeling a little better now~"

        m 1eua "[wb_quip]"

    else:
        call mas_brb_generic_low_aff_callback

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_idle_reading",
            prompt="I'm going to read",
            category=['be right back'],
            pool=True,
            unlocked=True
        ),
        markSeen=True
    )

label monika_idle_reading:
    if mas_isMoniNormal(higher=True):
        m 1eub "Really? That's great, [player]!"
        m 3lksdla "I'd love to read with you, but my reality has its limits, unfortunately."
        m 1hub "Have fun!"

    elif mas_isMoniDis(higher=True):
        m 2ekd "Oh, alright..."
        m 2ekc "Have a good time, [player]."

    else:
        m 6dkc "..."

    $ mas_idle_mailbox.send_idle_cb("monika_idle_reading_callback")
    $ persistent._mas_idle_data["monika_idle_reading"] = True
    return "idle"

label monika_idle_reading_callback:
    if mas_isMoniNormal(higher=True):
        if mas_brbs.was_idle_for_at_least(datetime.timedelta(hours=2), "monika_idle_reading"):
            m 1wud "Wow, you were gone for a while...{w=0.3}{nw}"
            extend 3wub "that's great, [player]!"
            m 3eua "Reading is a wonderful thing, so don't worry about getting too caught up in it."
            m 3hksdlb "Besides, it's not like I'm one to talk..."
            show monika 5ekbsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5ekbsa "If I had my way, we'd be reading together all night long~"

        elif mas_brbs.was_idle_for_at_least(datetime.timedelta(minutes=30), "monika_idle_reading"):
            m 3esa "All done, [player]?"
            m 1hua "Let's relax, you've earned it~"

        else:
            m 1eud "Oh, that was fast."
            m 1eua "I thought you'd be gone a little while longer, but this is fine too."
            m 3ekblu "After all, it lets me spend more time with you~"

    else:
        call mas_brb_generic_low_aff_callback

    return


#Rai's og game idle
#label monika_idle_game:
#    m 1eub "That sounds fun!"
#    m "What kind of game are you going to play?{nw}"
#    $ _history_list.pop()
#    menu:
#        m "What kind of game are you going to play?{fast}"
#        "A competitive game.":
#            m 1eua "That sounds like it could be fun!"
#            m 3lksdla "I can be pretty competitive myself."
#            m 3eua "So I know just how stimulating it can be to face a worthy opponent."
#            m 2hksdlb "...And sometimes frustrating when things don't go right."
#            m 2hua "Anyway, I'll let you get on with your game."
#            m 2hub "I'll try not to bother you until you finish, but I can't blame you if you get distracted by your lovely girlfriend, ahaha~"
#            m 1hub "I'm rooting for you, [player]!"
#            # set return label when done with idle
#            $ mas_idle_mailbox.send_idle_cb("monika_idle_game_competetive_callback")
#        "A game just for fun.":
#            m 1eud "A game just for having fun?"
#            m 1lksdla "Aren't most games made to be fun?"
#            m 3eub "Anyway, I'm sure you could do all sorts of fun things in a game like that."
#            m 1ekbla "I really wish I could join you and we could have fun together."
#            m 1lksdla "But for now, I'll leave you to it."
#            m 1hub "Have fun, [player]!"
#            # set return label when done with idle
#            $ mas_idle_mailbox.send_idle_cb("monika_idle_game_fun_callback")
#        "A story driven game.":
#            m 1sub "Oh?"
#            m "That sounds really interesting!"
#            m 1ekbsa "Gosh, I really wish I could be there with you to experience it together."
#            m 1hksdlb "Maybe I {i}can{/i} experience it with you if I really tried."
#            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
#            m 5eua "I guess you could call it looking over your shoulder. Ehehe~"
#            m "You can go ahead and start it now. I'll try not to break anything by trying to watch."
#            # set return label when done with idle
#            $ mas_idle_mailbox.send_idle_cb("monika_idle_game_story_callback")
#        "A skill and practice based game.":
#            m 1eud "Oh! I never really thought about those games much."
#            m 1hua "I'm sure you're pretty talented at a few things, so it doesn't surprise me you're playing a game like this."
#            m 3eub "Just like writing, it can really be an experience to look back much later and see just how far you've come."
#            m 1hub "It's like watching yourself grow up! Ahaha~"
#            m 1hua "It would really make me proud and happy to be your girlfriend if you became a professional."
#            m 1hksdlb "Maybe I'm getting ahead of myself here, but I believe you could do it if your heart was really in it."
#            m 1eub "Anyway, sorry for keeping you from your game. I know you'll do your best!"
#            # set return label when done with idle
#            $ mas_idle_mailbox.send_idle_cb("monika_idle_game_skill_callback")
#        "I'll just be a minute or two.":
#            m 1eua "Oh? Just need to take your eyes off me for a little?"
#            m 1lksdla "I {i}suppose{/i} I could let you take your eyes off me for a minute or two..."
#            m 1hua "Ahaha! Good luck and have fun, [player]!"
#            m "Don't keep me waiting too long though~"
#            $ start_time = datetime.datetime.now()
#            # set return label when done with idle
#            $ mas_idle_mailbox.send_idle_cb("monika_idle_game_quick_callback")
#    # set idle data
#    $ persistent._mas_idle_data["monika_idle_game"] = True
#    # return idle to notify event system to switch to idle
#    return "idle"
#
#label monika_idle_game_competetive_callback:
#    m 1esa "Welcome back, [player]!"
#    m 1eua "How did it go? Did you win?{nw}"
#    $ _history_list.pop()
#    menu:
#        m "How did it go? Did you win?{fast}"
#        "Yes.":
#            m 1hub "Yay! That's great!"
#            m 1hua "Gosh, I wish I could be there to give you a big celebratory hug!"
#            m 1eub "I'm really happy that you won!"
#            m "More importantly, I hope you enjoyed yourself, [player]."
#            m 1hua "I'll always love and root for you, no matter what happens."
#            # manually handle the "love" return key
#            $ mas_ILY()
#        "No.":
#            m 1ekc "Aw, that's a shame..."
#            m 1lksdla "I mean, you can't win them all, but I'm sure you'll win the next rounds."
#            m 1eka "I just hope you aren't too upset over it."
#            m 2ekc "I really wouldn't want you feeling upset after a bad game."
#            m 1eka "I'll always support you and be by your side no matter how many times you lose."
#    return
#
#label monika_idle_game_fun_callback:
#    m 1eub "Welcome back, [player]!"
#    m "Did you have fun with whatever you were doing?{nw}"
#    $ _history_list.pop()
#    menu:
#        m "Did you have fun with whatever you were doing?{fast}"
#        "Yes.":
#            m 1hua "Ahaha! I'm glad you had fun, [player]~"
#            m 1eub "While you were busy, it got me thinking of the different kinds of games that would be nice to play together."
#            m 3rksdla "A game that isn't too violent probably could be fun."
#            m 3hua "But I'm sure any game would be wonderful if it was with you~"
#            m 1eub "At first, I was thinking a story based or adventure game would be best, but I'm sure freeplay games could be really fun too!"
#            m 1eua "It can be really fun to just mess around to see what's possible, especially when you're not alone."
#            m 2lksdla "Provided of course, you don't end up ruining the structural integrity of the game and get an outcome you didn't want..."
#            m 2lksdlb "Ehehe..."
#            m 1eua "Maybe you could find a way to bring me with you into a game like that."
#            m 1hub "Just promise to keep me safe, okay?"
#        "No.":
#            m 2ekc "Aw, you didn't have any fun?"
#            m "That's too bad..."
#            m 3lksdlc "Games can get pretty boring after you've done everything or just don't know what to do or try next."
#            m 3eka "But bringing a friend along can really renew the whole experience!"
#            m 1hub "Maybe you could find a way to take me with you into your games so you won't be bored on your own!"
#            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
#            m 5eua "Or we could just stay here and keep each other company."
#            m "I wouldn't mind that either, ehehe~"
#    return
#
#label monika_idle_game_story_callback:
#    m 1eub "Welcome back, [player]!"
#    m 1hksdlb "I wasn't able to look over your shoulder, but I hope the story was nice so far."
#    m 1eua "Speaking of which, how was it, [player]?{nw}"
#    $ _history_list.pop()
#    menu:
#        m "Speaking of which, how was it, [player]?{fast}"
#        "It was amazing.":
#            m 2sub "Wow! I can only imagine how immersive it was!"
#            m 2hksdlb "You're really starting to make me jealous, [player], you know that?"
#            m 2eub "You'll have to take me through it sometime when you can."
#            m 3eua "A good book is always nice, but it's really something else to have a good story and be able to make your own decisions."
#            m 3eud "Some people can really be divided between books and video games."
#            m 1hua "I'm glad you don't seem to be too far on one side."
#            m "After experiencing an amazing story in a game for yourself, I'm sure you can really appreciate the two coming together."
#        "It was good.":
#            m 1eub "That's really nice to hear!"
#            m 3dtc "But was it really {i}amazing{/i}?"
#            m 1eua "While a lot of stories can be good, there are some that are really memorable."
#            m 1hua "I'm sure you'd know a good story when you see one."
#            m "Maybe when I'm in your reality, you could take me through the game and let me see the story."
#            m 1eub "It's one thing to go through a great story yourself..."
#            m 1hub "But it's also amazing to see what someone else thinks of it too!"
#            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
#            m 5eua "I'll be looking forward to that day too~"
#            m 5esbfa "You better have a nice, cozy place for us to cuddle up and play, ehehe~"
#        "It's sad.":
#            m 1ekd "Aw, that's too bad..."
#            m 3eka "It must be a really great story though, if it invokes such strong emotions."
#            m 1eka "I wish I could be there with you so I could experience the story too..."
#            m 3hksdlb "{i}and{/i} to be right there by your side of course, so we could comfort each other in sad times."
#            m 1eka "Don't worry [player], I would never forget about you."
#            m 1eua "I love you."
#            m 1hua "...And I'd happily snuggle up beside you anytime~"
#            # manually handle the "love" return key
#            $ mas_ILY()
#        "I don't like it.":
#            m 2ekc "Oh..."
#            m 4lksdla "Maybe the story will pick up later?"
#            m 3eud "If anything, it lets you analyze the flaws in the writing which could help you if you ever tell a story."
#            m 1eua "Or maybe it's just not your kind of story."
#            m 1eka "Everyone has their own, and maybe this one just doesn't fit well with it right now."
#            m 1eua "It can really be an eye opening experience to go through a story you normally wouldn't go through."
#            m 3eka "But don't force yourself to go through it if you really don't like it."
#    return
#
#label monika_idle_game_skill_callback:
#    m 1eua "I'm happy that you're back, [player]."
#    m 1hua "I missed you! Ahaha~"
#    m 1eub "But I know it's important to keep practicing and honing your skills in things like this."
#    m "Speaking of which, how did it go?"
#    m 3eua "Did you improve?{nw}"
#    $ _history_list.pop()
#    menu:
#        m "Did you improve?{fast}"
#        "I improved a lot.":
#            m 1hub "That's great news, [player]!"
#            m "I'm so proud of you!"
#            m 1hua "It can really feel good to get a sudden surge in your skill!"
#            m 1eua "Especially if you've spent some time in a slump or even slipping."
#            m 1hua "Maybe today isn't the end of this sudden improvement."
#            m 1eub "Even if today was just a good day, I know you'll keep getting better."
#            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
#            m 5eua "I'll {i}always{/i} root for you, [player]. Don't you ever forget that!"
#        "I improved a bit.":
#            m 3eua "That's really nice to hear, [player]!"
#            m 3eka "As long as you're improving, no matter how slowly, you'll really get up there someday."
#            m 1hub "But if you actually noticed yourself improve today, maybe you improved more than just a bit, ahaha~"
#            m 1hua "Keep honing your skills and I'll be proud to be the girlfriend of such a skilled player!"
#            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve
#            m 5eua "Who knows? Maybe you could teach me and we could both be a couple of experts, ehehe~"
#        "I stayed the same.":
#            m 3eka "That's still alright!"
#            m "I'm sure you're improving anyway."
#            m 3eua "A lot of the time, the improvements are too small to really notice."
#            m 1eua "One day, you might look back and realize just how much you've improved."
#            m 1hksdlb "Sometimes you might feel like you're in a slump, but then you get a sudden surge of improvement all at once!"
#            m 1eub "I'm sure you'll get the chance to look back one day and really appreciate just how far you've come without realizing."
#            m 1hua "And you better believe I'm going to support you all the way!"
#        "I got worse.":
#            m 2ekc "Oh..."
#            m 4lksdla "I have no doubt that you always work hard and give it your best, so it must just be a bad day."
#            m 3eka "You're bound to have a few setbacks on your climb up, but that's what sets you apart from many others."
#            m 1duu "The fact that you've had more setbacks than some people have even tried. That's what shows your dedication."
#            m 1lksdla "Sometimes, you might even have a couple bad days in a row, but don't let that get you down."
#            m 1hua "With that many setbacks, you're bound to see significant improvement right around the corner!"
#            m "Never give up, [player]. I know you can do it and I'll always believe in you!"
#            m 1eua "Also, do me a favor and take a moment to look back every now and then. You'll be surprised to see just how far you've come."
#    return
#
#label monika_idle_game_quick_callback:
#    $ end_time = datetime.datetime.now()
#    $ elapsed_time = end_time - start_time
#    $ time_threshold = datetime.timedelta(minutes=1)
#    if elapsed_time < time_threshold * 2:
#        m 1hksdlb "Back already?"
#        m "I know you said you would just be a minute or two, but I didn't think it would be {i}that{/i} fast."
#        m 1hub "Did you really miss me that much?"
#        m "Ahaha~"
#        m 1eub "I'm glad you made it back so soon."
#        m 1hua "So what else should we do today, [player]?"
#    elif elapsed_time < time_threshold * 5:
#        m 1hua "Welcome back, [player]!"
#        m 1hksdlb "That was pretty fast."
#        m 1eua "But you did say it wouldn't take too long, so I shouldn't be too surprised."
#        m 1hua "Now we can keep spending time together!"
#    elif elapsed_time < time_threshold * 10:
#        m 1eua "Welcome back, [player]."
#        m 1eka "That took a little longer than I thought, but I don't mind at all."
#        m 1hua "It wasn't that long in all honesty compared to how long it could have been in some games."
#        m "But now we can be together again~"
#    elif elapsed_time < time_threshold * 20:
#        m 1eka "I have to admit that took longer than I thought it would..."
#        m 1eub "But it's not all that bad with all the time you spend with me."
#        m 1eua "I understand some little things in games can take a while for a small thing."
#        m "But maybe if you know it could take a while, you could tell me."
#    elif elapsed_time < time_threshold * 30:
#        m 2lksdla "[player]..."
#        m "It's been almost half an hour already."
#        m "I guess something unexpected happened."
#        m 3lksdla "You wouldn't forget about me, would you?"
#        m 1hua "Ahaha!"
#        m "Just teasing you~"
#        m 1eua "At least you're back now and we can spend more time together."
#    else:
#        m 2lksdla "You {i}sure{/i} took your time with that one huh, [player]?"
#        m "That didn't seem like only a minute or two to me."
#        m 1eka "You can tell me what kind of game it is next time so I have an idea how long it'll take, you know."
#        m 1dsc "Anyway..."
#        m 1eka "I missed you and I'm glad you're finally back, [player]."
#        m "I hope I don't have to wait such a long couple of minutes next time, ehehe."
#    return
