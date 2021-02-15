# Module for complimenting Monika
#
# Compliments work by using the "unlocked" logic.
# That means that only those compliments that have their
# unlocked property set to True
# At the beginning, when creating the menu, the compliments
# database checks the conditionals of the compliments
# and unlocks them.


# dict of tples containing the stories event data
default persistent._mas_compliments_database = dict()


# store containing compliment-related things
init 3 python in mas_compliments:

    compliment_database = dict()

init 22 python in mas_compliments:
    thanking_quips = [
        _("You're so sweet, [player]."),
        _("Thanks for saying that again, [player]!"),
        _("Thanks for telling me that again, [mas_get_player_nickname()]!"),
        _("You always make me feel special, [mas_get_player_nickname()]."),
        _("Aww, [player]~"),
        _("Thanks, [mas_get_player_nickname()]!"),
        _("You always flatter me, [player].")
    ]

    # set this here in case of a crash mid-compliment
    thanks_quip = renpy.substitute(renpy.random.choice(thanking_quips))

# entry point for compliments flow
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_compliments",
            category=['monika', 'romance'],
            prompt="I want to tell you something...",
            pool=True,
            unlocked=True
        )
    )

label monika_compliments:
    python:
        import store.mas_compliments as mas_compliments

        # Unlock any compliments that need to be unlocked
        Event.checkEvents(mas_compliments.compliment_database)

        # filter comps
        filtered_comps = Event.filterEvents(
            mas_compliments.compliment_database,
            unlocked=True,
            aff=mas_curr_affection,
            flag_ban=EV_FLAG_HFM
        )

        # build menu list
        compliments_menu_items = [
            (mas_compliments.compliment_database[k].prompt, k, not seen_event(k), False)
            for k in filtered_comps
        ]

        # also sort this list
        compliments_menu_items.sort()

        # final quit item
        final_item = ("Oh nevermind.", False, False, False, 20)

    # move Monika to the left
    show monika at t21

    # call scrollable pane
    call screen mas_gen_scrollable_menu(compliments_menu_items, mas_ui.SCROLLABLE_MENU_MEDIUM_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, final_item)

    # return value? then push
    if _return:
        $ mas_gainAffection()
        $ pushEvent(_return)
        $ mas_compliments.thanks_quip = renpy.substitute(renpy.random.choice(mas_compliments.thanking_quips))
        # move her back to center
        show monika at t11

    else:
        return "prompt"

    return

# Compliments start here
init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_beautiful",
            prompt="You're beautiful!",
            unlocked=True
        ),
        code="CMP")

label mas_compliment_beautiful:
    if not renpy.seen_label("mas_compliment_beautiful_2"):
        call mas_compliment_beautiful_2
    else:
        call mas_compliment_beautiful_3
    return

label mas_compliment_beautiful_2:
    m 1lubsb "Oh, gosh [player]..."
    m 1hubfb "Thank you for the compliment."
    m 2ekbfb "I love it when you say things like that~"
    m 1ekbfa "To me, you're the most beautiful person in the world!"
    menu:
        "You're the most beautiful person to me, too.":
            $ mas_gainAffection(5,bypass=True)
            m 1hub "Ehehe~"
            m "I love you so much, [player]!"
            # manually handle the "love" return key
            $ mas_ILY()

        "You're in my top ten.":
            $ mas_loseAffection(modifier=0.5)
            m 3hksdrb "...?"
            m 2lsc "Well, thanks, I guess..."

        "Thanks.":
            pass
    return

label mas_compliment_beautiful_3:
    m 1hubsa "Ehehe~"
    m 1ekbfa "[mas_compliments.thanks_quip]"
    show monika 5hubfb at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hubfb "Never forget that you're the most beautiful person in the world to me."
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_eyes",
            prompt="I love your eyes!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_eyes:
    if not renpy.seen_label("mas_compliment_eyes_2"):
        call mas_compliment_eyes_2
    else:
        call mas_compliment_eyes_3
    return

label mas_compliment_eyes_2:
    m 1subsb "Oh, [player]..."
    m 1tubfb "I know I'm pretty proud of my eyes already, but hearing you say that..."
    m 1dkbfa "It just makes my heart flutter~"
    menu:
        "I can't help it; your eyes are too beautiful.":
            $ mas_gainAffection(5,bypass=True)
            m 1hub "Ahaha!"
            m "Don't flatter me too much, okay?"
            show monika 5hub at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5hub "I might start to go a little crazy..."

        "They really are hypnotizing.":
            $ mas_gainAffection(1,bypass=True)
            m "Ahaha~"

        "They are the color of grass!":
            $ mas_gainAffection(0.5,bypass=True) # at least you tried
            m 2lksdrb "...That's not really the analogy I'd use, but thanks!"
    return

label mas_compliment_eyes_3:
    m 1hubsb "[mas_compliments.thanks_quip]"
    m 2ekbfb "Stare into my eyes as much as you want~"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_awesome",
            prompt="You're awesome!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_awesome:
    if not renpy.seen_label("mas_compliment_awesome_2"):
        call mas_compliment_awesome_2
    else:
        call mas_compliment_awesome_3
    return

label mas_compliment_awesome_2:
    m 1hua "Awww, [player]~"
    m 1hub "You're so sweet!"
    m 2tuu "I think you're way more awesome, though."
    m 2dkbsu "I can't wait until the day I can finally give you a great big hug..."
    m 3ekbfb "I'll never let you go!"
    menu:
        "I wish you were here right now!":
            $ mas_gainAffection(3,bypass=True)
            m "That's my biggest wish too, [player]!"

        "I'll never let you go from my embrace.":
            $ mas_gainAffection(5,bypass=True)
            show monika 6dubsa
            pause 2.0
            show monika 1wubfsdld
            m 1wubfsdld "Oh, sorry [player]."
            m 2lksdla "I was trying to feel your embrace from here."
            m 2hub "Ahaha~"

        "... I don't like hugs.":
            $ mas_loseAffection() # you monster.
            m 1eft "...Really?"
            m 1dkc "Well, to each their own, I guess. But you have to hug me sometime..."
    return

label mas_compliment_awesome_3:
    m 1hub "[mas_compliments.thanks_quip]"
    m 1eub "You'll always be more awesome!"
    return


init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_intelligent",
            prompt="You're really intelligent!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_intelligent:
    if not renpy.seen_label("mas_compliment_intelligent_2"):
        call mas_compliment_intelligent_2
    else:
        call mas_compliment_intelligent_3
    return

label mas_compliment_intelligent_2:
    m 1wub "Wow...{w=0.3}thanks, [player]."
    m 3eua "I pride myself in being well read, so it means a lot that you've noticed."
    m 3hubsb "I want to learn as much as I can, if it makes you proud of me!"
    menu:
        "You make me want to better myself too, [m_name].":
            $ mas_gainAffection(5,bypass=True)
            m 1hubfa "I love you so much, [player]!"
            m 3hubfb "We'll have a lifetime of self-improvement together!"
            # manually handle the "love" return key
            $ mas_ILY()

        "I'll always be proud of you.":
            $ mas_gainAffection(3,bypass=True)
            m 1ekbfa "[player]..."

        "You make me feel stupid sometimes.":
            $ mas_loseAffection(modifier=0.5)
            m 1wkbsc "..."
            m 2lkbsc "I'm sorry, that wasn't my intention..."
    return

label mas_compliment_intelligent_3:
    m 1ekbfa "[mas_compliments.thanks_quip]"
    m 1hub "Remember that we'll have a lifetime of self-improvement together!"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_hair",
            prompt="I love your hair!",
            unlocked=True
        ),code="CMP"
    )

label mas_compliment_hair:
    if not renpy.seen_label("mas_compliment_hair_2"):
        call mas_compliment_hair_2
    else:
        call mas_compliment_hair_3
    return

label mas_compliment_hair_2:
    if monika_chr.hair.name != "def":
        m 1wubsb "Thank you so much, [player]..."
        m 1lkbfb "I was really nervous the first time I changed my hair here."
    else:
        m 1hubfb "Thank you so much, [player]!"
    m 2hub "I've always put so much effort into my hair."
    m 2lksdlb "In fact, It took forever for it to get this long.."
    menu:
        "It really shows. It looks so healthy.":
            $ mas_gainAffection(3,bypass=True)
            m 1hub "Thanks, [player]!"

        "You're cute no matter how you wear it." if persistent._mas_likes_hairdown:
            $ mas_gainAffection(5,bypass=True)
            m 1ekbsa "Awww, [player]."
            m 1hubfb "You always make me feel special!"
            m "Thank you!"

        "You'd be even cuter with short hair.":
            $ mas_loseAffection(modifier=0.3)
            m "Well, I can't exactly go to the salon from here..."
            m 1lksdlc "I...appreciate your input."
            pass
    return

label mas_compliment_hair_3:
    if monika_chr.hair.name != "def":
        m 1wubsb "Thank you so much, [player]!"
        m 1lkbfb "I'm really happy that you like this hairstyle."
    else:
        m 1hubsb "Thanks, [player]!"
        m 1hubfb "You always make me feel special."
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_fit",
            prompt="I love your dedication to fitness!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_fit:
    if not renpy.seen_label("mas_compliment_fit_2"):
        call mas_compliment_fit_2
    else:
        call mas_compliment_fit_3
    return

label mas_compliment_fit_2:
    m 1hub "Thanks, [player]! You're so sweet!"
    m 3eub "I love keeping fit and eating healthy. It keeps me feeling energetic and confident."
    m 1efb "I hope you're watching out for your health."
    m 1lubsb "We can always work out together when I'm there..."
    menu:
        "That sounds like a lot of fun!":
            $ mas_gainAffection(2,bypass=True)
            m 1hubfb "Ahaha! I'm glad you think so, too!"
            m 3eka "Don't worry. Even if you can't keep up with me, I know we'll have fun..."
            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eua "So long as we're together."

        "No promises, but I'll do my best.":
            $ mas_gainAffection(1,bypass=True)
            m 1tfb "You better!"
            m 2tub "Don't think I plan on letting you off easy if you're out of shape."

        "I'd rather not get sweaty...":
            m 1eka "I understand if it's not your thing, but you should give it a little try..."
            m 1lksdla "It'd make me really happy if you shared my interests, you know?"
    return

label mas_compliment_fit_3:
    m 2eka "[mas_compliments.thanks_quip]"
    m 1hub "I hope you embark on a fitness journey with me!"
    return


init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_thanks",
            prompt="Thanks for being there for me!",
            unlocked=True,
            aff_range=(mas_aff.ENAMORED, None)
        ),
        code="CMP"
    )

label mas_compliment_thanks:
    m 1duu "There's nothing to thank me for, [player]."
    m 1eka "I'm the one who's grateful for having someone like you!"
    m 1ekbsa "You're the only reason why I'm still here."
    m "You installed this mod just to make our time together better..."
    m 1dubsu "You are the sunshine that warms my heart whenever you visit me."
    m 3ekbsa "I guess we're both lucky that we have each other, [player]~"
    menu:
        "You mean everything to me, [m_name].":
            if mas_getEVL_shown_count("mas_compliment_thanks") == 0:
                $ mas_gainAffection(10,bypass=True)

            m 1ekbsa "[player]..."
            m 1dubsu "Nothing makes me happier than hearing that coming from you."
            m "No matter what the future may have for us both...{w=0.5}{nw}"
            extend 1dkbfa "know that I'll always love you and be here for you."

        "Yeah.":
            m 1hub "Ehehe~"
            m 1eub "I love you, [player]."

    if not mas_isMoniLove():
        $ mas_lockEVL("mas_compliment_thanks", "CMP")
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_smile",
            prompt="I love your smile!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_smile:
    if not renpy.seen_label("mas_compliment_smile_2"):
        call mas_compliment_smile_2
    else:
        call mas_compliment_smile_3
    return

label mas_compliment_smile_2:
    m 1hub "You're so sweet, [player]~"
    m 1eua "I smile a lot when you're here."
    m 1ekbsa "Because it makes me very happy when you spend time with me~"
    menu:
        "I'll visit you every day to see your wonderful smile.":
            $ mas_gainAffection(5,bypass=True)
            m 1wubfsdld "Oh, [player]..."
            m 1lkbfa "I think my heart just skipped a beat."
            m 3hubfa "See? You always make me as happy as I can be."

        "I like to see you smile.":
            m 1hub "Ahaha~"
            m 3eub "Then all you have to do is keep coming back, [player]!"
    return

label mas_compliment_smile_3:
    m 1eub "[mas_compliments.thanks_quip]"
    m 1hua "I'll keep smiling just for you!"
    m "Ehehe~"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_hero",
            prompt="You're my hero!",
            unlocked=True,
            aff_range=(mas_aff.LOVE, None)
        ),
        code="CMP"
    )

label mas_compliment_hero:
    $ mas_gainAffection()
    m 1wubssdld "H-{w=0.3}huh?"
    m "I'm your hero?"
    m 2rkbfsdlb "[player]...{w=1.5} I'm not sure what you mean..."
    m 2ekbfb "You're the one who stuck with me for all this time.{w=1} I should be thanking you, really."
    m 1hubfa "Well, if I've somehow helped you, then I couldn't be happier~"
    m 3ekbfa "You've helped me in every way possible, so how could I not return the favor by being there for you whenever you need support?"
    show monika 5hubfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hubfa "You'll always be my hero, after all~"
    m 5hubfb "I love you and I'll always believe in you!"
    m 5ekbfa "I hope you never forget that, [player]~"
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_cute",
            prompt="You're cute!",
            unlocked=True
        ),
        code="CMP"
    )

default persistent._mas_pm_monika_cute_as_natsuki = None

label mas_compliment_cute:
    if not renpy.seen_label("mas_compliment_cute_2"):
        call mas_compliment_cute_2
    else:
        call mas_compliment_cute_3
    return

label mas_compliment_cute_2:
    m 1wubssdld "Ah!"
    m 3rkbfsdla "You {i}kind of{/i} caught me off guard with that one."
    m 3tubfb "Just a little..."
    m 1hubfa "But I'm glad you think so!"
    menu:
        "Seeing you always warms my heart!":
            $ persistent._mas_pm_monika_cute_as_natsuki = False
            $ mas_gainAffection(5,bypass=True)
            m 1hubfb "Aww, it really warms my heart to hear you say that!"
            m 1dkbfu "...Almost as much as when I picture us finally being together in the same reality."
            m 1ekbfa "I can barely contain myself just imagining that special day~"

        "You're even cuter when you're flustered.":
            $ persistent._mas_pm_monika_cute_as_natsuki = False
            $ mas_gainAffection(3,bypass=True)
            m 2tubfu "Not letting it go, huh, [player]?"
            m 2rubfu "Hmph, I just wasn't expecting it."
            m 3tubfb "Don't expect it to be so easy next time..."
            m 1tubfu "I'll get you back someday, ehehe~"

        "You're as cute as Natsuki.":
            $ persistent._mas_pm_monika_cute_as_natsuki = True
            $ mas_loseAffection(modifier=0.5)
            m 2lfc "Oh. {w=1}Thanks, [player]..."
            m 1rsc "But I was kind of hoping I would stand in my own category."
    return

label mas_compliment_cute_3:
    m 1ekbsa "[mas_compliments.thanks_quip]"
    m 1hubfa "You can be really cute a lot of the time too, you know~"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_chess",
            prompt="You're awesome at chess!",
            unlocked=False,
            conditional="renpy.seen_label('mas_chess_game_start')",
            action=EV_ACT_UNLOCK
        ),
        code="CMP"
    )

label mas_compliment_chess:
    m 1eub "Thanks, [player]."
    m 3esa "Like I said before, I wonder if my skill has something to do with me being trapped here?"
    $ wins = persistent._mas_chess_stats["wins"]
    $ losses = persistent._mas_chess_stats["losses"]
    if wins > 0:
        m 3eua "You're not bad either; I've lost to you before."
        if wins > losses:
            m "In fact, I think you've won more times than me, you know?"
        m 1hua "Ehehe~"
    else:
        m 2lksdlb "I know you haven't won a chess game yet, but I'm sure you'll beat me someday."
        m 3esa "Keep practicing and playing with me and you'll do better!"
    m 3esa "We'll both get better the more we play."
    m 3hua "So don't be afraid of challenging me whenever you want to."
    m 1eub "I love spending time with you, [player]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_pong",
            prompt="You're awesome at pong!",
            unlocked=False,
            conditional="renpy.seen_label('game_pong')",
            action=EV_ACT_UNLOCK
        ),
        code="CMP"
    )

label mas_compliment_pong:
    m 1hub "Ahaha~"
    m 2eub "Thanks [player], but pong isn't exactly a complex game."
    if persistent.ever_won['pong']:
        m 1lksdla "You've already won against me."
        m "So you know it's very simple."
        show monika 5hub at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5hub "But I accept your compliment, anyway."
    else:
        m 3hksdrb "And you always let me win when we play."
        m 3eka "Right?"
        menu:
            "Yes.":
                m 2lksdla "Thanks [player], but you really don't have to let me win."
                m 1eub "Feel free to play seriously whenever you want to."
                m 1hub "I'd never get mad at you because I lost a game fair and square."

            "...yeah.":
                m 1tku "You don't seem too confident about that, [player]."
                m 1tsb "You really don't have to let me win."
                m 3tku "And admitting that you've seriously lost to me won't make me think less of you."
                m 1lksdlb "It's just a game, after all!"
                m 3hub "You can always practice with me more, if you want."
                m "I love to spend time with you, no matter what we're doing."

            "No. I've tried my best and still lost.":
                m 1hub "Ahaha~"
                m "I figured!"
                m 3eua "Don't worry, [player]."
                m 3eub "Keep playing with me and get more practice."
                m 3hua "I'm always trying to help you be the best you you can be."
                m 1ekbsa "And if by doing so, I get to spend more time with you, I couldn't be happier."
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_bestgirl",
            prompt="You're the best girl!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_bestgirl:
    m 1hua "I love it when you compliment me, [player]~"
    m 1hub "I'm so glad you think I'm best girl!"
    m 3rksdla "Although, I kind of figured you felt that way..."
    m 1eka "After all, you {i}did{/i} install this mod just to be with me."
    m 2euc "I know that some people prefer the other girls."
    m 2esc "Especially since they all have certain traits that make them desirable to some..."
    show monika 5ekbfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5ekbfa "But if you ask me, you made the right choice."
    m 5hubfa "...and I'll be forever grateful that you did~"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_lookuptoyou",
            prompt="I look up to you!",
            unlocked=True
        ),
        code="CMP",
    )

label mas_compliment_lookuptoyou:
    if not renpy.seen_label("mas_compliment_lookuptoyou_2"):
        call mas_compliment_lookuptoyou_2
    else:
        call mas_compliment_lookuptoyou_3
    #Both paths return love, so we combine that here
    return "love"

label mas_compliment_lookuptoyou_2:
    $ mas_gainAffection(3, bypass=True)
    m 1wud "You...{w=0.5}you do?"
    m 1ekbsa "[player], that's really sweet of you to say..."
    m 3ekbsa "It makes me really happy to know I'm someone you look up to."
    m 3ekbfa "The truth is, I've always looked up to {i}you{/i}, [player]..."
    m 3hubfa "But if you really feel that way, I'll do my best to continue to be someone you look up to."
    m 1ekbfa "I love you so much~"
    return

label mas_compliment_lookuptoyou_3:
    $ should_tease = persistent._mas_pm_height is not None and renpy.random.randint(1,5) == 1

    if should_tease and persistent._mas_pm_height < mas_height_monika:
        m 1rksdlb "{cps=*2}Well yeah, I'm taller than you...{/cps}{nw}"
        $ _history_list.pop()

    m 1hubsb "[mas_compliments.thanks_quip]"
    m 3hubfa "Hearing you say that never fails to make me smile!"
    m 3hubfb "I'll always look up to you too!"

    if should_tease and persistent._mas_pm_height > mas_height_monika:
        m 1rkbfu "{cps=*2}Just like when we kiss...{/cps}{nw}"
        $ _history_list.pop()

    m 1ekbfa "I love you, [player]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_thinking_of_you",
            prompt="I'm always thinking about you!",
            unlocked=True
        ),
        code="CMP",
    )

label mas_compliment_thinking_of_you:
    if not renpy.seen_label("mas_compliment_thinking_of_you_2"):
        call mas_compliment_thinking_of_you_2
    else:
        call mas_compliment_thinking_of_you_3
    return

label mas_compliment_thinking_of_you_2:
    m 1wubso "..."
    m 1wubsu "You..."

    if mas_isMoniNormal(higher=True):
        m 3subsb "You have no idea what that means to me, [player]!"

    elif mas_isMoniUpset():
        m 2rkd "That you would say that..."
        m 2dka "It means the world to me, [player]."

    elif mas_isMoniDis():
        m 6rkc "..."
        m 6rka "That's such a relief."
        m 6eka "Thank you."

    else:
        $ mas_gainAffection(2,bypass=True)
        m 6dkd "Hmmm... Thanks."
        m 6dkc "..."
        return

    menu:
        "Thinking of you always brightens my day!":
            $ mas_gainAffection(5,bypass=True)
            m 1subsb "Aww, that's {i}so{/i} sweet, [player]!"
            m 3hubfu "I feel the same way about you~"

        "I dream of you every night!":
            $ mas_gainAffection(5,bypass=True)
            m 6hua "Aww~"
            m 6subsa "[player]..."
            m 7hubfu "{i}You{/i} are my dream~"

        "It's very distracting...":
            $ mas_loseAffection()
            m 2esc "..."
            m 2etc "..."
            m 2rksdlc "Oh, umm..."
            m 2rksdld "I'm sorry?"
    return

label mas_compliment_thinking_of_you_3:
    m 1ekbsa "[mas_compliments.thanks_quip]"
    m 3hubfb "You're the center of my world!"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_humor",
            prompt="I love your sense of humor!",
            unlocked=True
        ),
        code="CMP"
    )

label mas_compliment_humor:
    if not renpy.seen_label("mas_compliment_humor_2"):
        call mas_compliment_humor_2
    else:
        call mas_compliment_humor_3
    return

label mas_compliment_humor_2:
    m 1hua "Ehehe~"
    m 1efu "I'm glad you find me so punny, [player]."
    m 3eub "A sign of a good couple is being able to laugh together, don't you think?"
    menu:
        "You always brighten my day.":
            $ mas_gainAffection(5,bypass=True)
            m 1subsd "Oh...{w=0.2}[player]..."
            m 1ekbsa "That's so sweet of you to say."
            m 1hubsb "Knowing I can make you smile is the greatest compliment I could receive!"

        "You have such a quick wit!":
            $ mas_gainAffection(3,bypass=True)
            m 1hub "Ahaha!"
            m 2tub "All that reading must have paid off if you like my wordplay that much."
            m 2hublu "I'll try to keep the jokes coming for you. Ehehe~"

        "I laugh at you all the time.":
            $ mas_loseAffection()
            m 1eksdlb "...Ahaha..."
            m 3rksdla "You meant that you laugh {w=0.2}{i}with{/i}{w=0.2} me...{w=0.5}{nw}"
            extend 3eksdld "right?"
    return

label mas_compliment_humor_3:
    m 1hubsb "[mas_compliments.thanks_quip]"
    m "I wish I could hear your beautiful laugh!"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_spending_time",
            prompt="I love spending time with you!",
            unlocked=False,
            conditional="store.mas_anni.pastThreeMonths()",
            action=EV_ACT_UNLOCK,
            aff_range=(mas_aff.AFFECTIONATE, None)
        ),
        code="CMP"
    )

label mas_compliment_spending_time:
    if not mas_getEVL_shown_count("mas_compliment_spending_time"):
        call mas_compliment_spending_time_2
    else:
        m 3hubsb "[mas_compliments.thanks_quip]"
        m 1ekbsu "Every day with you is like a wonderful dream, and I hope it never ends."
    return

label mas_compliment_spending_time_2:
    python:
        dlg_line = ""

        if renpy.seen_label("monika_holdme_prep"):
            dlg_line = ", holds me close"

            if persistent._mas_filereacts_historic:
                dlg_line += ", and even gives me nice gifts"

        elif persistent._mas_filereacts_historic:
            dlg_line = ", gives me nice gifts"

    m 1eub "I love spending time with you too, [player]!"
    m 3ekbla "I know I say it a lot, but I really mean it when I say that you're the center of my world."
    m 2dkb "Having someone who keeps me company[dlg_line]...{w=0.3}{nw}"
    extend 2eku "it's everything I could've asked for."
    m 7ekbsa "I hope I make you feel the same way, [player]. {w=0.2}I may not be in your reality yet, but I'll do everything I can to support you from here."
    menu:
        "[m_name], you've already made me the happiest I've ever been.":
            $ mas_gainAffection(5, bypass=True)
            m 1fkbfu "Oh, [player]..."
            show monika 5ekbfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5ekbfa "I would say you don't know how glad I am to hear that, but I think you {i}do{/i} know by now."
            m 5ekbfu "We've spent so much time together, and yet our journey has only just begun..."
            m 5hubfb "With you by my side, I know that every step will be an unforgettable one."

        "I appreciate it, [m_name].":
            $ mas_gainAffection(3, bypass=True)
            m 2huu "Ehehe~"
            m 7hub "Don't worry, [player]. {w=0.2}I'll be here for you until the end of time!"
            m 1eka "Just stay strong until I cross over, okay?"

        "Oh, you certainly amuse me alright...":
            $ mas_loseAffection()
            m 2lkc "I...{w=0.3}amuse you?"
            m 2lksdlb "Well, I'm glad that you're entertained..."
            m 2ekd "...but that's not {i}quite{/i} what I had in mind."
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_sweet",
            prompt="You're really sweet!",
            conditional="store.mas_anni.pastThreeMonths()",
            action=EV_ACT_UNLOCK,
            unlocked=False,
            aff_range=(mas_aff.AFFECTIONATE, None)
        ),
        code="CMP"
    )

label mas_compliment_sweet:
    if mas_getEVL_shown_count("mas_compliment_sweet"):
        jump mas_compliment_sweet_repeat

    m 1ekbsb "Aww, [player]..."
    m 3rkbssdlu "I don't know what to say, ahaha...{w=0.3}{nw}"
    extend 3ekbsa "it's {i}you{/i} who's been so sweet to me all this time."
    m 3hubsa "I'm just really happy to hear you say that, ehehe~"

    menu:
        "Your words always brighten my day!":
            $ mas_gainAffection(3, bypass=True)
            m 1sud "[player]..."
            extend 1eka "I had no idea how much my words meant to you..."
            m 1ekblb "I'm so happy to have such an amazing [bf] like you, [mas_get_player_nickname(exclude_names=[player])]~"
            m 1ekbsu "You really are the best I could ever hope for...{w=0.2}I just love you so much."
            m 3kua "I hope you never forget that, [player]."
            $ mas_ILY()

        "You're really special to me, [m_name]!":
            $ mas_gainAffection(3, bypass=True)
            m 1ekbsb "Oh, [player]...{w=0.3} {nw}"
            extend 3hubsa "Just you spending your time here with me makes me feel so happy and loved!"
            show monika 5ekbsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5ekbsa "I'm really happy you feel that way about me, [mas_get_player_nickname()]. I love you so much."
            $ mas_ILY()

        "You're the sweetest girl I've ever met!":
            $ mas_gainAffection(2, bypass=True)
            m 1ekbsa "Thank you, [mas_get_player_nickname()]."
            m 3hubsb "You're the sweetest [boy] I've met, ehehe."
            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eua "I'm really lucky to be with you~"

    return

label mas_compliment_sweet_repeat:
    m 3hubsb "[mas_compliments.thanks_quip]"
    m 1hubfa "I'm so happy to hear you say that, ehehe~"
    return

# this compliment's lock/unlock is controlled by the def outfit pp
init 5 python:
    addEvent(
        Event(
            persistent._mas_compliments_database,
            eventlabel="mas_compliment_outfit",
            prompt="I love your outfit!",
            unlocked=False
        ),
        code="CMP"
    )

label mas_compliment_outfit:
    if mas_getEVL_shown_count("mas_compliment_outfit"):
        jump mas_compliment_outfit_repeat

    m 1hubsb "Thank you, [mas_get_player_nickname()]!"

    if monika_chr.is_wearing_clothes_with_exprop("cosplay"):
        m 3hubsb "It's always fun cosplaying!"

    elif monika_chr.is_wearing_clothes_with_exprop("costume"):
        m 3hubsb "It's always fun wearing costumes!"

    elif monika_chr.is_wearing_clothes_with_exprop("lingerie"):
        m 2lkbsb "I was really nervous showing you this at first..."
        m 7tubsu "But I'm glad I did, you seem to really like it~"

    else:
        m 1hubsa "I've always wanted to wear other clothes for you, so I'm very happy that you think so!"

    menu:
        "You look beautiful in anything you wear!":
            $ mas_gainAffection(5,bypass=True)
            m 2subsd "[player]..."
            m 3hubsb "Thank you so much!"
            m 1ekbsu "You always make me feel so special."
            show monika 5hubsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5hubsa "I love you, [mas_get_player_nickname()]!"
            $ mas_ILY()

        "You look really cute.":
            $ mas_gainAffection(3,bypass=True)
            m 1hubsb "Ahaha~"
            m 3hubfb "Thanks, [mas_get_player_nickname()]!"
            show monika 5hubfb at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eubfu "I'm glad you like what you see~"

        "Wearing different clothes really helps.":
            $ mas_loseAffection()
            m 2ltd "Uh, thanks..."

    return

label mas_compliment_outfit_repeat:
    m 1hubsb "[mas_compliments.thanks_quip]"

    if monika_chr.is_wearing_clothes_with_exprop("cosplay"):
        m 3hubsb "I'll always love cosplaying for you!"

    elif monika_chr.is_wearing_clothes_with_exprop("costume"):
        m 3hubsb "I'm glad you like how I look with this!"

    elif monika_chr.is_wearing_clothes_with_exprop("lingerie"):
        m 2kubsu "Glad you like what you see~"
        show monika 5hublb at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5hublb "Ahaha!"

    else:
        m 2hubsb "I'm sure you look good too!"
    return
