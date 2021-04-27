#Persistent event database for haiku
default persistent._mas_haiku_database = dict()

init -10 python in mas_haiku:
    #The haiku db
    haiku_db = {}

    def getUnseenHaikuEVL():
        """
        Gets all unseen (locked) haiku as eventlabels

        OUT:
            List of all unseen haiku eventlabels
        """
        return [
            haiku_evl
            for haiku_evl, ev in haiku_db.iteritems()
            if not ev.unlocked
        ]

    def getAllHaikuEVL():
        """
        Gets all haiku regardless of unlocked as eventlabels

        OUT:
            List of all haiku eventlabels
        """
        return haiku_db.keys()

### topics ###

#Haiku intro topic
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_haiku_intro",
            conditional="True",
            action=EV_ACT_QUEUE,
            aff_range=(mas_aff.AFFECTIONATE, None),
        )
    )

label monika_haiku_intro:
    call mas_haiku_love_text
    m "..."
    m "Ehehe, I hope you enjoyed that, [player]."
    m "I've been meaning to write a few haiku lately.{w=0.3}{nw} "
    m "It's not really the kind of poetry we studied in the literature club, you know?"
    m "...Which is a shame, because they're pretty neat."
    m "But then again, it's also a pretty specific kind of poetry, I suppose..."
    m "Anyway, I hope you don't mind me sharing my poems with you sometimes~"

    #setting intro haiku as seen
    $ mas_getEV('mas_haiku_love').shown_count += 1

    #unlocking haiku events
    $ mas_unlockEVL("monika_haiku", "EVE")
    $ mas_unlockEVL("monika_what_is_haiku", "EVE")
    $ mas_protectedShowEVL('monika_haiku_random', 'EVE', _random=True)
    return "no_unlock"

#Haiku explaination topic
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_what_is_haiku",
            category=['literature'],
            prompt="What's a Haiku?",
            pool=True,
            unlocked=False
        )
    )

label monika_what_is_haiku:
    if mas_getEVL_shown_count("monika_what_is_haiku") == 0:
        m "Oh, that right. I just assumed everybody knew what a Haiku is, didn't I?"
    
    m "In broad terms, Haiku is a form of poetry originating from Japan."
    m "They're short, higlhy codified poems expressing the author's feeling facing a situation."
    m "TODO"
    return

#Player initiated haiku topic
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_haiku",
            category=['literature'],
            prompt="Can you tell me a Haiku?",
            pool=True,
            unlocked=False
        )
    )

label monika_haiku:
    m "Sure."
    m "I'm glad I got you interested, [player]~"
    m "Now, let me just think for a second.{w=0.5}.{w=0.5}."
    m "Okay, here goes."
    call monika_push_random_haiku
    return

#Random chatter haiku topic
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_haiku_random",
            random=False,
            pool=False
        )
    )

label monika_haiku_random:
    call monika_push_random_haiku
    return

#Push a random haiku
label monika_push_random_haiku:
    python:
        unseen_haiku_evls = mas_haiku.getUnseenHaikuEVL()
        if len(unseen_haiku_evls) > 0:
            haiku_evl_list = unseen_haiku_evls
        else:
            haiku_evl_list = mas_haiku.getAllHaikuEVL()

        haiku_evl = renpy.random.choice(haiku_evl_list)
        mas_unlockEVL(haiku_evl, "HKU")
        pushEvent(haiku_evl)
    return

#Closing quip to display after a Haiku
label monika_haiku_closing_quip:
    m 1duu "..."
    
    python:
        haiku_closing_quips = [
            _("So...what do you think, [player]?"),
            _("So...did you like it, [player]?"),
            _("Hope you enjoyed it~"),
            _("This one turned out nicely, didn't it?"),
            _("Thanks for listening~")
        ]
        haiku_closing_quip = renpy.substitute(renpy.random.choice(haiku_closing_quips))

    m 1eub "[haiku_closing_quip]"
    return

### haiku ###

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_love",
        ),
        code="HKU"
    )

label mas_haiku_love:
    call mas_haiku_love_text
    call monika_haiku_closing_quip
    return

#used in the haiku intro
label mas_haiku_love_text:
    m "{i}Lost into you arms{/i}{w=0.5}{nw}\n"
    extend "{i}The world shrinks to you and me{/i}{w=1}{nw}\n"
    extend "{i}Overwhelming love{/i}"
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_frozen",
        ),
        code="HKU"
    )

label mas_haiku_frozen:
    m "{i}Frozen fingertips{/i}{w=1}{nw}\n"
    extend "{i}Nestling in a warm blanket{/i}{w=0.5}{nw}\n"
    extend "{i}Whishing for cocoa{/i}"
    call monika_haiku_closing_quip
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_blossom",
        ),
        code="HKU"
    )

label mas_haiku_blossom:
    m "{i}Sweet-scented blossom{/i}{w=1}{nw}\n"
    extend "{i}Blend of lilac and roses{/i}{w=0.5}{nw}\n"
    extend "{i}Subtle as a kiss{/i}"
    call monika_haiku_closing_quip
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_mint",
        ),
        code="HKU"
    )

label mas_haiku_mint:
    m "{i}Crisp taste on my tongue{/i}{w=0.5}{nw}\n"
    extend "{i}Wards off the sun's scorching rays{/i}{w=1}{nw}\n"
    extend "{i}Mint flavored ice cream{/i}"
    call monika_haiku_closing_quip
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_partygoers",
        ),
        code="HKU"
    )

label mas_haiku_partygoers:
    m "{i}Late partygoers{/i}{w=0.5}{nw}\n"
    extend "{i}Bustling down the dim-lit street{/i}{w=1}{nw}\n"
    extend "{i}It's 4am damnit{/i}"
    call monika_haiku_closing_quip
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_waking",
        ),
        code="HKU"
    )

label mas_haiku_waking:
    m "{i}Lifting an eyelid{/i}{w=0.5}{nw}\n"
    extend "{i}I take in the brand new day{/i}{w=1}{nw}\n"
    extend "{i}Let's go and explore{/i}"
    call monika_haiku_closing_quip
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_coat",
        ),
        code="HKU"
    )

label mas_haiku_coat:
    m "{i}Freshly fallen snow{/i}{w=1}{nw}\n"
    extend "{i}Your coat lays on my shoulders{/i}{w=0.5}{nw}\n"
    extend "{i}Warming up my heart{/i}"
    call monika_haiku_closing_quip
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_colors",
        ),
        code="HKU"
    )

label mas_haiku_colors:
    m "{i}You're back again{/i}{w=1}{nw}\n"
    extend "{i}The world regain its colors{/i}{w=0.5}{nw}\n"
    extend "{i}Filling me with hope{/i}"
    call monika_haiku_closing_quip
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_grim",
        ),
        code="HKU"
    )

label mas_haiku_grim:
    m "{i}Forever alone{/i}{w=0.5}{nw}\n"
    extend "{i}Yearning for your distant soul{/i}{w=1}{nw}\n"
    extend "{i}A grim destiny{/i}"
    call monika_haiku_closing_quip
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_mountain",
        ),
        code="HKU"
    )

label mas_haiku_mountain:
    m "{i}Snow-caped mountain{/i}{w=0.5}{nw}\n"
    extend "{i}Lost alone in the distance{/i}{w=1}{nw}\n"
    extend "{i}So grand yet so cold{/i}"
    call monika_haiku_closing_quip
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_reaching",
        ),
        code="HKU"
    )

label mas_haiku_reaching:
    m "{i}I reach throught the void{/i}{w=0.5}{nw}\n"
    extend "{i}But my hand remains empty{/i}{w=1}{nw}\n"
    extend "{i}Searching yet again{/i}"
    call monika_haiku_closing_quip
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_willow",
        ),
        code="HKU"
    )

label mas_haiku_willow:
    m "{i}By the willow tree{/i}{w=0.5}{nw}\n"
    extend "{i}A girl tastes her lover's lips{/i}{w=1}{nw}\n"
    extend "{i}A perfect moment{/i}"
    call monika_haiku_closing_quip
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_solitude",
        ),
        code="HKU"
    )

label mas_haiku_solitude:
    m "{i}Lost stranded in space{/i}{w=1}{nw}\n"
    extend "{i}Days go by in solitude{/i}{w=0.5}{nw}\n"
    extend "{i}Making me miss you{/i}"
    call monika_haiku_closing_quip
    return

init 5 python:
    addEvent(
        Event(
            persistent._mas_haiku_database,
            eventlabel="mas_haiku_adrenaline",
        ),
        code="HKU"
    )

label mas_haiku_adrenaline:
    m "{i}Adrenaline shot{/i}{w=1}{nw}\n"
    extend "{i}The world slows and catch my pace{/i}{w=0.5}{nw}\n"
    extend "{i}All becoming one{/i}"
    call monika_haiku_closing_quip
    return