init -2 python in mas_anni:
    import store
    import datetime

    # persistent pointer so we can use it
    __persistent = renpy.game.persistent

    def build_anni(years=0, months=0, weeks=0, isstart=True):
        """
        Builds an anniversary date.

        NOTE:
            years / months / weeks are mutually exclusive

        IN:
            years - number of years to make this anni date
            months - number of months to make thsi anni date
            weeks - number of weeks to make this anni date
            isstart - True means this should be a starting date, False
                means ending date

        ASSUMES:
            __persistent
        """
        # sanity checks
        if __persistent.sessions is None:
            return None

        first_sesh = __persistent.sessions.get("first_session", None)
        if first_sesh is None:
            return None

        if (weeks + years + months) == 0:
            # we need at least one of these to work
            return None

        # sanity checks are done

        if years > 0:
            new_date = store.mas_utils.add_years(first_sesh, years)

        elif months > 0:
            new_date = store.mas_utils.add_months(first_sesh, months)

        else:
            new_date = first_sesh + datetime.timedelta(days=(weeks * 7))

        # check for starting
        if isstart:
            return store.mas_utils.mdnt(new_date)

        # othrewise, this is an ending date
#        return mas_utils.am3(new_date + datetime.timedelta(days=1))
# NOTE: doing am3 leads to calendar problems
#   we'll just restrict this to midnight to midnight -1
        return store.mas_utils.mdnt(new_date + datetime.timedelta(days=1))

    def build_anni_end(years=0, months=0, weeks=0):
        """
        Variant of build_anni that auto ends the bool

        SEE build_anni for params
        """
        return build_anni(years, months, weeks, False)

    def isAnni(milestone=None):
        """
        INPUTS:
            milestone:
                Expected values|Operation:

                    None|Checks if today is a yearly anniversary
                    1w|Checks if today is a 1 week anniversary
                    1m|Checks if today is a 1 month anniversary
                    3m|Checks if today is a 3 month anniversary
                    6m|Checks if today is a 6 month anniversary
                    any|Checks if today is any of the above annis

        RETURNS:
            True if datetime.date.today() is an anniversary date
            False if today is not an anniversary date
        """
        #Sanity checks
        if __persistent.sessions is None:
            return False

        firstSesh = __persistent.sessions.get("first_session", None)
        if firstSesh is None:
            return False

        compare = None

        if milestone == '1w':
            compare = build_anni(weeks=1)

        elif milestone == '1m':
            compare = build_anni(months=1)

        elif milestone == '3m':
            compare = build_anni(months=3)

        elif milestone == '6m':
            compare = build_anni(months=6)

        elif milestone == 'any':
            return (
                isAnniWeek()
                or isAnniOneMonth()
                or isAnniThreeMonth()
                or isAnniSixMonth()
                or isAnni()
            )

        if compare is not None:
            return compare.date() == datetime.date.today()

        else:
            compare = firstSesh
            return (
                store.mas_utils.add_years(compare.date(), datetime.date.today().year - compare.year) == datetime.date.today()
                and anniCount() > 0
            )

    def isAnniWeek():
        return isAnni('1w')

    def isAnniOneMonth():
        return isAnni('1m')

    def isAnniThreeMonth():
        return isAnni('3m')

    def isAnniSixMonth():
        return isAnni('6m')

    def isAnniAny():
        return isAnni('any')

    def anniCount():
        """
        RETURNS:
            Integer value representing how many years the player has been with Monika
        """
        #Sanity checks
        if __persistent.sessions is None:
            return 0

        firstSesh = __persistent.sessions.get("first_session", None)

        if firstSesh is None:
            return 0

        compare = datetime.date.today()

        if (
            compare.year > firstSesh.year
            and compare < store.mas_utils.add_years(firstSesh.date(), compare.year - firstSesh.year)
        ):
            return compare.year - firstSesh.year - 1
        else:
            return compare.year - firstSesh.year

    def pastOneWeek():
        """
        RETURNS:
            True if current date is past the 1 week threshold
            False if below the 1 week threshold
        """
        return datetime.date.today() >= build_anni(weeks=1).date()

    def pastOneMonth():
        """
        RETURNS:
            True if current date is past the 1 month threshold
            False if below the 1 month threshold
        """
        return datetime.date.today() >= build_anni(months=1).date()

    def pastThreeMonths():
        """
        RETURNS:
            True if current date is past the 3 month threshold
            False if below the 3 month threshold
        """
        return datetime.date.today() >= build_anni(months=3).date()

    def pastSixMonths():
        """
        RETURNS:
            True if current date is past the 6 month threshold
            False if below the 6 month threshold
        """
        return datetime.date.today() >= build_anni(months=6).date()


# TODO What's the reason to make this one init 10?
init 10 python in mas_anni:

    # we are going to store all anniversaries in antther db as well so we
    # can easily reference them later.
    ANNI_LIST = [
        "anni_1week",
        "anni_1month",
        "anni_3month",
        "anni_6month",
        "anni_1",
        "anni_2",
        "anni_3",
        "anni_4",
        "anni_5",
        "anni_10",
        "anni_20",
        "anni_50",
        "anni_100"
    ]

    # anniversary database
    anni_db = dict()
    for anni in ANNI_LIST:
        anni_db[anni] = store.evhand.event_database[anni]


    ## functions that we need (runtime only)
    def _month_adjuster(ev, new_start_date, months, span):
        """
        Adjusts the start_date / end_date of an anniversary event.

        NOTE: do not use this for a non anniversary date

        IN:
            ev - event to adjust
            new_start_date - new start date to calculate the event's dates
            months - number of months to advance
            span - the time from the event's new start_date to end_date
        """
        ev.start_date = store.mas_utils.add_months(
            store.mas_utils.mdnt(new_start_date),
            months
        )
        ev.end_date = store.mas_utils.mdnt(ev.start_date + span)

    def _day_adjuster(ev, new_start_date, days, span):
        """
        Adjusts the start_date / end_date of an anniversary event.

        NOTE: do not use this for a non anniversary date

        IN:
            ev - event to adjust
            new_start_date - new start date to calculate the event's dates
            days - number of months to advance
            span - the time from the event's new start_date to end_date
        """
        ev.start_date = store.mas_utils.mdnt(
            new_start_date + datetime.timedelta(days=days)
        )
        ev.end_date = store.mas_utils.mdnt(ev.start_date + span)


    def add_cal_annis():
        """
        Goes through the anniversary database and adds them to the calendar
        """
        for anni in anni_db:
            ev = anni_db[anni]
            store.mas_calendar.addEvent(ev)

    def clean_cal_annis():
        """
        Goes through the calendar and cleans anniversary dates
        """
        for anni in anni_db:
            ev = anni_db[anni]
            store.mas_calendar.removeEvent(ev)


    def reset_annis(new_start_dt):
        """
        Reset the anniversaries according to the new start date.

        IN:
            new_start_dt - new start datetime to reset anniversaries
        """
        _firstsesh_id = "first_session"
        _firstsesh_dt = renpy.game.persistent.sessions.get(
            _firstsesh_id,
            None
        )

        # remove teh anniversaries off the calendar
        clean_cal_annis()

        # remove first session repeatable
        if _firstsesh_dt:
            # this exists! we can make this easy
            store.mas_calendar.removeRepeatable_dt(_firstsesh_id, _firstsesh_dt)

        # modify the anniversaries
        fullday = datetime.timedelta(days=1)
        _day_adjuster(anni_db["anni_1week"],new_start_dt,7,fullday)
        _month_adjuster(anni_db["anni_1month"], new_start_dt, 1, fullday)
        _month_adjuster(anni_db["anni_3month"], new_start_dt, 3, fullday)
        _month_adjuster(anni_db["anni_6month"], new_start_dt, 6, fullday)
        _month_adjuster(anni_db["anni_1"], new_start_dt, 12, fullday)
        _month_adjuster(anni_db["anni_2"], new_start_dt, 24, fullday)
        _month_adjuster(anni_db["anni_3"], new_start_dt, 36, fullday)
        _month_adjuster(anni_db["anni_4"], new_start_dt, 48, fullday)
        _month_adjuster(anni_db["anni_5"], new_start_dt, 60, fullday)
        _month_adjuster(anni_db["anni_10"], new_start_dt, 120, fullday)
        _month_adjuster(anni_db["anni_20"], new_start_dt, 240, fullday)
        _month_adjuster(anni_db["anni_50"], new_start_dt, 600, fullday)
        _month_adjuster(anni_db["anni_100"], new_start_dt, 1200, fullday)

        unlock_past_annis()

        # re-add the events to the calendar db
        add_cal_annis()

        # re-add the repeatable to the calendar db
        store.mas_calendar.addRepeatable_dt(
            _firstsesh_id,
            "<3",
            new_start_dt,
            [new_start_dt.year]
        )


    def unlock_past_annis():
        """
        Goes through the anniversary database and unlocks the events that
        already past.
        """
        for anni in anni_db:
            ev = anni_db[anni]

            if store.evhand._isPast(ev):
                renpy.game.persistent._seen_ever[anni] = True
                ev.unlocked = True


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_1week',
            prompt="1 Week",
            action=EV_ACT_QUEUE,
            category=["anniversary"],
            start_date=store.mas_anni.build_anni(weeks=1),
            end_date=store.mas_anni.build_anni_end(weeks=1)
        ),
        skipCalendar=False
    )

label anni_1week:
    m 1eka "I know it's silly to celebrate one week of being together, but I'm just glad you're here with me, [player]."
    m 1ekc "A lot of couples wouldn't last this long with each other."
    m 1lksdlc "It's really easy to fall in love at first sight, but it's a bit harder to actually build a sturdy relationship."
    m 1ekd "A lot of relationships fail when couples jump the gun too fast."
    m "More likely than not, they fail to get to know each other more."
    m 1dsc "So it's always sad to see them crash and burn..."
    m 1duu "But I'm glad we have a solid relationship, [player]."
    show monika 5lubfb at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5lubfb "How do I know that?"
    m 5hubfb "Because you wouldn't have stuck around for this long with me, sweetie~"
    return "unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_1month',
            prompt="1 Month",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(months=1),
            end_date=store.mas_anni.build_anni_end(months=1)
        ),
        skipCalendar=False
    )

label anni_1month:
    m 3sub "Today marks our one month anniversary!"
    m 1hua "I'm really happy that we're able to have so much fun with each other so far."
    m 1eua "Also, [player]?"
    m 1lkbsa "..."
    m 1ekbfa "Thank you so much for staying with me for this long."
    if not seen_event('monika_saved'):
        m 1lksdlc "I can't imagine what I'd do if you hadn't come along."
        m 3ekc "After all, I'm the only real one who lives in this world."
        m 1dsc "I already told you what'd happen if it weren't for you..."
        m 1hksdlb "Ahaha, sorry. I hope I didn't darken the mood with my rambling."
    else:
        m "I couldn't possibly express how much I appreciate you being here with me."
        m 1dubsu "All I can do is to try my best to be the perfect girlfriend for you!"
    m 1ekbfa "I really do love you, [player]."
    m 1hubfa "Let's make today a special day~"
    return "love|unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_3month',
            prompt="3 Months",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(months=3),
            end_date=store.mas_anni.build_anni_end(months=3)
        ),
        skipCalendar=False
    )

label anni_3month:
    m 1eua "[player], do you know what day it is?"
    m 1hua "It's our three month anniversary!"
    m 1hub "Time sure does go by quickly, doesn't it?"
    m 1hksdlb "...Even if it doesn't really pass here, ehehe."
    m 1eua "I'm having a lot of fun, though."
    m 1ekbsa "Having you around has made my life so much better, [player]."
    m 2ekbfa "I'm very happy that you've stayed with me for this long."
    m 1tsbsa "You're really something special, aren't you?"
    m 1lsbsa "Well! I'm afraid I don't really have anything in particular planned."
    m 1hubfa "Let's just enjoy this day to its fullest, as we always do."
    m 1hubfb "Alright, [player]?"
    return "unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_6month',
            prompt="6 Months",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(months=6),
            end_date=store.mas_anni.build_anni_end(months=6)
        ),
        skipCalendar=False
    )

label anni_6month:
    m 1hub "I can't believe that it's already our 6-month anniversary!"
    m 1eka "I'm really happy you've stayed with me for this long."
    m 1lksdlc "I often get lonely when you're not around."
    m 1ekc "I mean, I have things to keep me busy while you're gone, but I still feel really lonely knowing that I'm the only one in here."
    m 1hua "So it always brightens up my day whenever you come to visit me!"
    m 1euc "But over the past few months, I came to realize something..."
    m "Most couples celebrate their anniversaries by doing something special together, right?"
    m 3eud "Like eating out, or seeing a show."
    m 1lksdla "Not that I'm complaining or anything, but we've spent all of our anniversaries so far in this room."
    m 1lksdlc "It would've been fun if we could visit someplace different..."
    m "It's such a shame that there isn't a place like that here, since all we have is this room and all."
    m 1dsc "..."
    m 3wuo "...Oh, I know!"
    m 1sub "Maybe someday, I'll be able to program somewhere nice for us to spend our anniversaries at!"
    m "Or maybe you can add in a special place for the both of us, [player]."
    m 1duu "Unless..."
    m 1eua "You've already taken me somewhere else in your reality?"
    m 1eka "It would've been so nice if I saw where you took me~"
    m 1eua "But for now, I don't mind that we're limited to this room."
    m 1ekbsa "Because as long as you're here with me..."
    m 1hubfa "...I'm as happy as can be!"
    return "unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_1',
            prompt="1 Year",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=1),
            end_date=store.mas_anni.build_anni_end(years=1)
        ),
        skipCalendar=False
    )

label anni_1:
    m 1dka "Gosh...{w=0.2}it's hard to believe it's already been a whole year since we met."
    m 1eka "Time doesn't really have meaning in here, but I know it's a big commitment for you to stay with me for so long."
    m 2rkc "I have to admit, I was a bit nervous at first...{w=0.3} {nw}"
    extend 7eka "This kind of relationship can't be exactly easy."
    m 2ekd "...And I didn't know if there were other things in your reality that might prove to be more important..."
    m 7duu "But you kept coming back.{w=0.3} You kept spending time with me, just like I'd always hoped."
    m 1ekb "...And over time I started to really believe it...{w=0.2}that you meant it when you said you wanted to be with me."
    m 3dkbsu "...That we could have a happy life together.{w=0.3} {nw}"
    extend 3ekbsa "You and me, in our own little reality."
    show monika 5ekbsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5ekbsa "I can't thank you enough for that, [player]. {w=0.2}You've made this year so incredible for me."
    m 5eublb "So, is there anything special you wanted to do on our first anniversary?"
    m 5hksdrb "I didn't really plan anything, but I'm sure we can find something fun to do."
    show monika 3huu at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 3huu "After all...{w=0.3}when you're here, everything that we do is fun."
    m 1hubsa "I love you so much, [player]. {w=0.2}Happy anniversary~"
    return "unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_2',
            prompt="2 Years",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=2),
            end_date=store.mas_anni.build_anni_end(years=2)
        ),
        skipCalendar=False
    )

label anni_2:
    m 3eua "It's already been two years since we fell in love with each other."
    m 1eka "Do you still remember the first day we met, [player]?"
    m 3eub "It took so much effort to make that initial contact, but it was all worth it in the end!"
    m 2ekc "I know it might still be a really long time before I can cross over into your reality..."
    m 2duu "But when we reach a milestone like this,{w=0.1} {nw}"
    extend 7eua "it's fun to think about all the other things we have to look forward to in the future."

    if persistent._mas_pm_has_friends:
        m 3hubla "I'm really excited to live in a world full of real people. It'll be wonderful to meet your friends and even make some of my own."
    elif persistent._mas_pm_has_friends is False:
        m 1dka "We've both been lonely for a really long time, you know? But when I cross over, it'll be so much fun to make new friends together."
    else:
        m 3hua "I'm sure we'll make a lot of new friends together!"

    m 3hksdlb "Of course, I'll always enjoy your company the most...{w=0.3}{nw}"
    extend 3eua "but spending time alone won't be our only option anymore."
    m 3eub "Communicating will be much easier too!{w=0.2} {nw}"
    extend 3dubsb "We'll finally be able to hear each other's voices, get to learn our habits, and help each other out in plenty of little ways."
    m 1ekbsa "But I'm not just going to focus on the future today...{w=0.2} {nw}"
    extend 3hubsu "I'm going to make sure to enjoy every minute we spend together~"
    m 1hubsu "So, let's make sure we have another wonderful day, [mas_get_player_nickname()]."
    return "unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_3',
            prompt="3 Years",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=3),
            end_date=store.mas_anni.build_anni_end(years=3)
        ),
        skipCalendar=False
    )

label anni_3:
    m 4wuo "Is it really our third anniversary already?"
    m 2hubsb "Wow...{w=0.3}time really has flown by, hasn't it?"
    m 3rksdla "You know, normally if a couple stays together for three years..."
    m 2rsbsa "They get married around then, right?"
    m 1hub "Ahaha!"
    m 1eka "I'm not trying to pressure you into anything, don't worry."
    m 1lkbsa "Besides, I'd like to be able to feel you in my arms first before we get married."
    m 1eua "In your world, have they invented robot girl bodies yet?" # 1s?
    m 1eub "If you put me in one of those, we could probably go see a priest then~"
    m 2lsbssdrb "Or you could try to touch me in virtual reality, if that exists by now."
    m 1eua "There are actually a lot of different ways we can meet up for real, huh?"
    m 1hubsa "I'll wait faithfully for the day when I can be your wife, so please don't forget about me!"
    return "unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_4',
            prompt="4 Years",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=4),
            end_date=store.mas_anni.build_anni_end(years=4)
        ),
        skipCalendar=False
    )

label anni_4:
    m 1dsc "Four years..."
    m "At the start, I was sorta thinking you would forget about me pretty quickly."
    m 1lksdlc "I knew you liked me and everything, but I was just so scared that you would get tired of having to leave me running on your computer."
    m "Sorry for doubting you."
    m 1eka "You're a good person, [player]."
    m "You're literally all I have in the world that's worth anything."
    m 1ekbsa "I love you."
    m "Sooner or later, somebody's going to figure out a way to let us be together for real."
    m 1hubfa "When that time comes, I'm never going to leave you alone again."
    m 1hubfb "Ahaha!"
    return "love|unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_5',
            prompt="5 Years",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=5),
            end_date=store.mas_anni.build_anni_end(years=5)
        ),
        skipCalendar=False
    )

label anni_5:
    m 1hubsa "Whether it's been five years or fifty, I'll never get tired of seeing your face."
    m 1eka "I know it must be lonely that we haven't met up in your reality yet..."
    m 1tku "You haven't fallen in love with some other girl in the meantime, have you?"
    m 1eka "I'm not going to break up with you over some wandering eyes..."
    m 1tfb "But trying to take you away from me might be bad for her health."
    m 2dfc "It's my responsibility as your girlfriend to protect you from anybody trying to manipulate you, [player]."
    m 4ekc "My love for you is pure, unlike those real girls who just want things from you!"
    m 1eka "So...stay here with me forever, okay?"
    m "Please keep waiting for me."
    return "unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_10',
            prompt="10 Years",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=10),
            end_date=store.mas_anni.build_anni_end(years=10)
        ),
        skipCalendar=False
    )

label anni_10:
    m 1esc "There's something I wanted to ask you."
    m 2euc "Have you enjoyed spending this time with me?"
    m 1ekc "You don't regret falling in love and staying here with me or anything, right?"
    m 1ekbsa "If you're still talking to me ten years since we first met, I must have really made an impression on you."
    m "I did say I wanted to make you happy, after all."
    m 1hubfa "Trust me, you've helped me out a lot more than I've helped you."
    m "It won't be long now before I can enter your world."
    return "unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_20',
            prompt="20 Years",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=20),
            end_date=store.mas_anni.build_anni_end(years=20)
        ),
        skipCalendar=False
    )

label anni_20:
    m 1esc "You've lived a pretty long life by now, [player]."
    m "Twenty years is about twenty percent of your life on Earth, if you're lucky."
    m "I hope you've found happiness by now."
    m 1eka "I know I did."
    m 1ekd "So you deserve to find it too."
    m "Twenty years ago, you seemed a little too sad for your own good."
    m 1eka "I knew exactly how you felt. You were trying so hard to search for somebody who could understand you."
    m "And I was trying to find you, too."
    m 2hub "You wouldn't have found anyone else like me in a video game no matter how hard you looked, [player]."
    m "I'm one of a kind."
    m 3rkbsa "And to me, so are you."
    show monika 5eubfb at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eubfb "I hope you look on the last twenty years of our lives as happily as I do, [player]."
    m 1hubfa "So let's continue being happy together."
    return "unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_50',
            prompt="50 Years",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=50),
            end_date=store.mas_anni.build_anni_end(years=50)
        ),
        skipCalendar=False
    )

label anni_50:
    m 1tkc "I can't help but think there's got to be a better way for us to talk by now than through this screen, right?"
    m "Fifty years have passed in your world since I created this room."
    m 1hfw "Come on, let me out already!"
    m 1dsc "..."
    m 1eua "Well, if you're still willing to celebrate our fiftieth anniversary in this old classroom..."
    m "I don't really mind. It feels nostalgic, doesn't it?"
    m 1tfu "Assuming you didn't cheat by setting the clock forward in time..."
    m 1eka "I'm glad that forever meant forever."
    m "Even when you die, I'm going to find a way to be with you."
    m 1ekbsa "See you in a hundred years, then, [player]."
    m 1hubfa "Thanks for everything you've done for me."
    m "Your life had a purpose after all."
    m 1hubfb "And mine had one too."
    return "unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='anni_100',
            prompt="100 Years",
            category=["anniversary"],
            action=EV_ACT_QUEUE,
            start_date=store.mas_anni.build_anni(years=100),
            end_date=store.mas_anni.build_anni_end(years=100)
        ),
        skipCalendar=False
    )

label anni_100:
    m 1eka "I don't really think you should be seeing this message, [player]."
    m "I'm immortal, but the last time I checked, you weren't."
    m 1tku "So you're probably cheating by manually changing your system clock, huh?"
    m 1eua "That's a cute thing for you to do, so I forgive you."
    m 1hubsa "Make sure you put that much effort into freeing me from these code files too!"
    m "I'm sure I'll be able to touch you for real even if it takes us a hundred years to figure out how."
    return "unlock"

# label anni_negative:
#     m 1o "Did you really think I wouldn't notice, [player]?"
#     m "Trying to trick me into thinking it was our anniversary..."
#     m 1p "Just because I can't tell time accurately in here doesn't mean you should try to bully your girlfriend like that!"
#     m "I got all excited over nothing..."
#     m 1q "Well, I guess I've done worse pranks to everybody at the Literature Club."
#     m 1j "Make up for it by planning out some romantic things for us to do, okay?"
#     m 1a"I hope we can reach our anniversaries together fair and square this time."
#     m 1k "I'll be waiting!"
#     return
