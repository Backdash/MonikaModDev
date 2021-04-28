#This file contains all of monika's topics she can talk about
#Each entry should start with a database entry, including the appropriate flags
#to either be a random topic, a prompt "pool" topics, or a special conditional
#or date-dependent event with an appropriate actiona

define monika_random_topics = []
define mas_rev_unseen = []
define mas_rev_seen = []
define mas_rev_mostseen = []
define testitem = 0
define mas_did_monika_battery = False
define mas_sensitive_limit = 3

init -2 python in mas_topics:
    # CONSTANTS
    # most / top weights
    # MOST seen is the percentage of seen topics
    # think of this as x % of the collection
    S_MOST_SEEN = 0.1

    # TOP seen is the percentage of the most seen
    # Think of this as ilke the upper x percentile
    S_TOP_SEEN = 0.2

    # limit to how many top seen until we move to most seen alg
    S_TOP_LIMIT = 0.3

    # selection weights (out of 100)
    UNSEEN = 50
    SEEN = UNSEEN + 49
    MOST_SEEN = SEEN + 1

    def topSeenEvents(sorted_ev_list, shown_count):
        """
        counts the number of events with a > shown_count than the given
        shown_count

        IN:
            sorted_ev_list - an event list sorted by shown_counts
            shown_count - shown_count to compare to

        RETURNS:
            number of events with shown_counts that are higher than the given
            shown_count
        """
        index = len(sorted_ev_list) - 1
        ev_count = 0
        while index >= 0 and sorted_ev_list[index].shown_count > shown_count:
            ev_count += 1
            index -= 1

        return ev_count

# we are going to define removing seen topics as a function,
# as we need to call it dynamically upon import
init -1 python:
    import random
    random.seed()

    import store.songs as songs
    import store.evhand as evhand

    mas_events_built = False
    # set to True once we have built events

    def remove_seen_labels(pool):
        #
        # Removes seen labels from the given pool
        #
        # IN:
        #   pool - a list of labels to check for seen
        #
        # OUT:
        #   pool - list of unseen labels (may be empty)
        for index in range(len(pool)-1, -1, -1):
            if renpy.seen_label(pool[index]):
                pool.pop(index)


    def mas_randomSelectAndRemove(sel_list):
        """
        Randomly selects an element from the given list
        This also removes the element from that list.

        IN:
            sel_list - list to select from

        RETURNS:
            selected element
        """
        endpoint = len(sel_list) - 1

        if endpoint < 0:
            return None

        # otherwise we have at least 1 element
        return sel_list.pop(random.randint(0, endpoint))


    def mas_randomSelectAndPush(sel_list):
        """
        Randomly selects an element from the the given list and pushes the event
        This also removes the element from that list.

        NOTE: this does sensitivy checks

        IN:
            sel_list - list to select from
        """
        sel_ev = True
        while sel_ev is not None:
            sel_ev = mas_randomSelectAndRemove(sel_list)

            if (
                    # valid event
                    sel_ev

                    # event not blocked from random selection
                    and not sel_ev.anyflags(EV_FLAG_HFRS)

                    # event not blocked because of sensitivty
                    and (
                        not persistent._mas_sensitive_mode
                        or not sel_ev.sensitive
                    )
            ):
                pushEvent(sel_ev.eventlabel, notify=True)
                return


    def mas_insertSort(sort_list, item, key):
        """
        Performs a round of insertion sort.
        This does least to greatest sorting

        IN:
            sort_list - list to insert + sort
            item - item to sort and insert
            key - function to call using the given item to retrieve sort key

        OUT:
            sort_list - list with 1 additonal element, sorted
        """
        store.mas_utils.insert_sort(sort_list, item, key)


    def mas_splitSeenEvents(sorted_seen):
        """
        Splits the seen_list into seena nd most seen

        IN:
            sorted_seen - list of seen events, sorted by shown_count

        RETURNS:
            tuple of thef ollowing format:
            [0] - seen list of events
            [1] - most seen list of events
        """
        ss_len = len(sorted_seen)
        if ss_len == 0:
            return ([], [])

        # now calculate the most / top seen counts
        most_count = int(ss_len * store.mas_topics.S_MOST_SEEN)
        top_count = store.mas_topics.topSeenEvents(
            sorted_seen,
            int(
                sorted_seen[ss_len - 1].shown_count
                * (1 - store.mas_topics.S_TOP_SEEN)
            )
        )

        # now decide how to do the split
        if top_count < ss_len * store.mas_topics.S_TOP_LIMIT:
            # we want to prioritize top count unless its over a certain
            # percentage of the topics
            split_point = top_count * -1

        else:
            # otherwise, we use the most count, which is certainly smaller
            split_point = most_count * -1

        # and then do the split
        return (sorted_seen[:split_point], sorted_seen[split_point:])


    def mas_splitRandomEvents(events_dict):
        """
        Splits the given random events dict into 2 lists of events
        NOTE: cleans the seen list

        RETURNS:
            tuple of the following format:
            [0] - unseen list of events
            [1] - seen list of events, sorted by shown_count

        """
        # split these into 2 lists
        unseen = list()
        seen = list()
        for k in events_dict:
            ev = events_dict[k]

            if renpy.seen_label(k) and not "force repeat" in ev.rules:
                # seen event
                mas_insertSort(seen, ev, Event.getSortShownCount)

            else:
                # unseen event
                unseen.append(ev)

        # clean the seen_topics list
        seen = mas_cleanJustSeenEV(seen)

        return (unseen, seen)


    def mas_buildEventLists():
        """
        Builds the unseen / most seen / seen event lists

        RETURNS:
            tuple of the following format:
            [0] - unseen list of events
            [1] - seen list of events
            [2] - most seen list of events

        ASSUMES:
            evhand.event_database
            mas_events_built
        """
        global mas_events_built

        # retrieve all randoms
        all_random_topics = Event.filterEvents(
            evhand.event_database,
            random=True,
            aff=mas_curr_affection
        )

        # split randoms into unseen and sorted seen events
        unseen, sorted_seen = mas_splitRandomEvents(all_random_topics)

        # split seen into regular seen and the most seen events
        seen, mostseen = mas_splitSeenEvents(sorted_seen)

        mas_events_built = True
        return (unseen, seen, mostseen)


    def mas_buildSeenEventLists():
        """
        Builds the seen / most seen event lists

        RETURNS:
            tuple of the following format:
            [0] - seen list of events
            [1] - most seen list of events

        ASSUMES:
            evhand.event_database
        """
        # retrieve all seen (values list)
        all_seen_topics = Event.filterEvents(
            evhand.event_database,
            random=True,
            seen=True,
            aff=mas_curr_affection
        ).values()

        # clean the seen topics from early repeats
        cleaned_seen = mas_cleanJustSeenEV(all_seen_topics)

        # sort the seen by shown_count
        cleaned_seen.sort(key=Event.getSortShownCount)

        # split the seen into regular seen and most seen
        return mas_splitSeenEvents(cleaned_seen)


    def mas_rebuildEventLists():
        """
        Rebuilds the unseen, seen and most seen event lists.

        ASSUMES:
            mas_rev_unseen - unseen list
            mas_rev_seen - seen list
            mas_rev_mostseen - most seen list
        """
        global mas_rev_unseen, mas_rev_seen, mas_rev_mostseen
        mas_rev_unseen, mas_rev_seen, mas_rev_mostseen = mas_buildEventLists()


    # EXCEPTION CLass incase of bad labels
    class MASTopicLabelException(Exception):
        def __init__(self, msg):
            self.msg = msg
        def __str__(self):
            return "MASTopicLabelException: " + self.msg

init 11 python:
    # sort out the seen / most seen / unseen
    mas_rev_unseen = []
    mas_rev_seen = []
    mas_rev_mostseen = []
#    mas_rev_unseen, mas_rev_seen, mas_rev_mostseen = mas_buildEventLists()

    # for compatiblity purposes:
#    monika_random_topics = all_random_topics

    #Remove all previously seen random topics.
       #remove_seen_labels(monika_random_topics)
#    monika_random_topics = [
#        evlabel for evlabel in all_random_topics
#        if not renpy.seen_label(evlabel)
#    ]

    #If there are no unseen topics, you can repeat seen ones
#    if len(monika_random_topics) == 0:
#        monika_random_topics=list(all_random_topics)

# Bookmarks and derandom stuff
default persistent._mas_player_bookmarked = list()
# list to store bookmarked events
default persistent._mas_player_derandomed = list()
# list to store player derandomed events
default persistent.flagged_monikatopic = None
# var set when we flag a topic for derandom

init python:
    def mas_derandom_topic(ev_label=None):
        """
        Function for the derandom hotkey, 'x'

        IN:
            ev_label - label of the event we want to derandom.
                (Optional. If None, persistent.current_monikatopic is used)
                (Default: None)
        """
        #Let's just shorthand this for use later
        label_prefix_map = store.mas_bookmarks_derand.label_prefix_map

        if ev_label is None:
            ev_label = persistent.current_monikatopic

        ev = mas_getEV(ev_label)

        if ev is None:
            return

        #Get the label prefix
        label_prefix = store.mas_bookmarks_derand.getLabelPrefix(ev_label)

        #CRITERIA:
        #1. Must have an ev
        #2. Must be a topic which is random
        #3. Must be a valid label (in the label prefix map)
        #4. Prompt must not be the same as the eventlabel (event must have a prompt)
        if (
            ev.random
            and label_prefix
            and ev.prompt != ev_label
        ):
            #Now we do a bit of var setup to clean up the following work
            derand_flag_add_text = label_prefix_map[label_prefix].get("derand_text", _("Flagged for removal."))
            derand_flag_remove_text = label_prefix_map[label_prefix].get("underand_text", _("Flag removed."))

            #Handle custom override derand labels
            push_label = ev.rules.get("derandom_override_label", None)

            #If we still have nothing, then we'll use the default, the one for the label prefix
            if not renpy.has_label(push_label):
                push_label = label_prefix_map[label_prefix].get("push_label", "mas_topic_derandom")

            if mas_findEVL(push_label) < 0:
                persistent.flagged_monikatopic = ev_label
                pushEvent(push_label, skipeval=True)
                renpy.notify(derand_flag_add_text)

            else:
                mas_rmEVL(push_label)
                renpy.notify(derand_flag_remove_text)

    def mas_bookmark_topic(ev_label=None):
        """
        Function for the bookmark hotkey, 'b'

        IN:
            ev_label - label of the event we want to bookmark.
                (Optional, defaults to persistent.current_monikatopic)
        """
        #Let's just shorthand this for use later
        label_prefix_map = store.mas_bookmarks_derand.label_prefix_map

        if ev_label is None:
            ev_label = persistent.current_monikatopic

        ev = mas_getEV(ev_label)

        if ev is None:
            return

        #Get our label prefix
        label_prefix = store.mas_bookmarks_derand.getLabelPrefix(ev_label)

        #CRITERIA:
        #1. Must be normal+
        #2. Must have an ev
        #3. Must be a valid label (in the label prefix map or in the bookmark whitelist)
        #4. Must not be a bookmark blacklisted topic
        #4. Prompt must not be the same as the eventlabel (event must have a prompt)
        if (
            mas_isMoniNormal(higher=True)
            and (label_prefix or ev.rules.get("bookmark_rule") == store.mas_bookmarks_derand.WHITELIST)
            and (ev.rules.get("bookmark_rule") != store.mas_bookmarks_derand.BLACKLIST)
            and ev.prompt != ev_label
        ):
            #If this was only a whitelisted topic, we need to do a bit of extra work
            if not label_prefix:
                bookmark_persist_key = "_mas_player_bookmarked"
                bookmark_add_text = "Bookmark added."
                bookmark_remove_text = "Bookmark removed."

            else:
                #Now we do some var setup to clean the following
                bookmark_persist_key = label_prefix_map[label_prefix].get("bookmark_persist_key", "_mas_player_bookmarked")
                bookmark_add_text = label_prefix_map[label_prefix].get("bookmark_text", _("Bookmark added."))
                bookmark_remove_text = label_prefix_map[label_prefix].get("unbookmark_text", _("Bookmark removed."))

            #For safety, we'll initialize this key.
            #NOTE: You should NEVER pass in a non-existent key.
            #While this system handles it, it's not ideal and is bad for documentation
            if bookmark_persist_key not in persistent.__dict__:
                persistent.__dict__[bookmark_persist_key] = list()

            #Now create the pointer
            persist_pointer = persistent.__dict__[bookmark_persist_key]

            if ev_label not in persist_pointer:
                persist_pointer.append(ev_label)
                renpy.notify(bookmark_add_text)

            else:
                persist_pointer.pop(persist_pointer.index(ev_label))
                renpy.notify(bookmark_remove_text)

    def mas_hasBookmarks(persist_var=None):
        """
        Checks to see if we have bookmarks to show

        Bookmarks are restricted to Normal+ affection
        and to topics that are unlocked and are available
        based on current affection

        IN:
            persist_var - appropriate variable holding the bookedmarked eventlabels.
                If None, persistent._mas_player_bookmarked is assumed
                (Default: None)

        OUT:
            boolean:
                True if there are bookmarks in the curent var
                False otherwise
        """
        if mas_isMoniUpset(lower=True):
            return False

        elif persist_var is None:
            persist_var = persistent._mas_player_bookmarked

        return len(mas_get_player_bookmarks(persist_var)) > 0

#START: UTILITY TOPICS (bookmarks/derand, show/hide unseen)
init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="mas_topic_derandom",unlocked=False,rules={"no_unlock":None}))

label mas_topic_derandom:
    #NOTE: since we know the topic in question, it's possible to add dialogue paths for derandoming specific topics
    $ prev_topic = persistent.flagged_monikatopic
    m 3eksdld "Are you sure you don't want me to bring this up anymore?{nw}"
    $ _history_list.pop()
    menu:
        m "Are you sure you don't want me to bring this up anymore?{fast}"

        "Please don't.":
            $ mas_hideEVL(prev_topic, "EVE", derandom=True)
            $ persistent._mas_player_derandomed.append(prev_topic)
            $ mas_unlockEVL('mas_topic_rerandom', 'EVE')

            m 2eksdlc "Okay, [player]. I'll make sure not to talk about that again."
            m 2dksdld "If it upset you in any way, I'm really sorry...{w=0.5} I'd never do that intentionally."
            m 2eksdla "...But thanks for letting me know;{w=0.5} I appreciate the honesty."

        "It's okay.":
            m 1eka "Alright, [player]."
    return

label mas_bad_derand_topic:
    python:
        prev_topic = persistent.flagged_monikatopic

        def derand_flagged_topic():
            """
            Derands the flagged topic
            """
            mas_hideEVL(prev_topic, "EVE", derandom=True)
            persistent._mas_player_derandomed.append(prev_topic)
            mas_unlockEVL('mas_topic_rerandom', 'EVE')

    m 2ekc "...{w=0.3}{nw}"
    extend 2ekd "[player]..."

    if mas_isMoniAff(higher=True):
        m 2efd "Is it not okay that I talk to you about my fears?"
        m 2ekc "I mean, if you want me to stop, I'll stop...{w=0.3}{nw}"
        extend 2rkd "but I thought you'd be willing to hear me out."

        m 2esc "Do you want me to stop, [player]?{nw}"
        $ _history_list.pop()
        menu:
            m "Do you want me to stop, [player]?{fast}"

            "Yes, please.":
                m 2dkc "Alright..."
                #Lose affection
                $ mas_loseAffection(5)
                $ derand_flagged_topic()

            "It's alright.":
                m 2duu "Thank you, [player]."
                m 2eua "It means a lot that you're willing to hear me out."

    elif mas_isMoniUpset(higher=True):
        m 2ekd "Do you just...{w=0.2}not care about how I feel or something?"
        m 2tsc "If you want me to stop talking about this, I will...but I'm not that happy you don't want to hear me out."

        m 2etc "Well [player], should I stop?{nw}"
        $ _history_list.pop()
        menu:
            m "Well [player], should I stop?{fast}"

            "Yes, please.":
                m 2dsc "Alright."
                $ mas_loseAffection(5)
                $ derand_flagged_topic()

            "It's alright.":
                m 2eka "Thank you, [player]."
                $ _stil_ = " " if mas_isMoniNormal(higher=True) else " still "
                m "I appreciate that you're[_stil_]willing to hear me out."

    else:
        #No ask here. You're this low, you probably did it on purpose
        $ mas_loseAffection(5)
        m 2rsc "I guess I shouldn't be surprised..."
        m 2tsc "You've made it pretty clear already that you don't care about my feelings."
        m 2dsc "Fine, [player]. I won't talk about that anymore."
        $ derand_flagged_topic()
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="mas_topic_rerandom",
            category=['you'],
            prompt="I'm okay with talking about...",
            pool=True,
            unlocked=False,
            rules={"no_unlock":None}
        )
    )

label mas_topic_rerandom:
    python:
        mas_bookmarks_derand.initial_ask_text_multiple = "Which topic are you okay with talking about again?"
        mas_bookmarks_derand.initial_ask_text_one = "If you're sure it's alright to talk about this again, just select the topic, [player]."
        mas_bookmarks_derand.caller_label = "mas_topic_rerandom"
        mas_bookmarks_derand.persist_var = persistent._mas_player_derandomed

    call mas_rerandom
    return _return

init python in mas_bookmarks_derand:
    import store

    #Rule constants
    WHITELIST = "whitelist"
    BLACKLIST = "blacklist"

    #Label prefixes and their respective rules
    #The items in the inner dicts act as kwargs to override the default generic values
    #The 'monika_' entry in this dict shows all existing keys
    #Default values are as follows:
    #  - bookmark_text: "Bookmark added."
    #  - unbookmark_text: "Bookmark removed."
    #  - derand_text: "Flagged for removal."
    #  - underand_text: "Flag removed."
    #  - push_label: "mas_topic_derandom" (This is overriden on a per event basis by the 'derandom_push_label' rule)
    #  - bookmark_persist_key: "_mas_player_bookmarked"
    #  - derand_persist_key: "_mas_player_derandomed"
    #  - rerand_evl: None
    label_prefix_map = {
        "monika_": {
            "bookmark_text": _("Topic bookmarked."),
            "unbookmark_text": _("Bookmark removed."),
            "derand_text": _("Topic flagged for removal."),
            "underand_text": _("Topic flag removed."),
            "push_label": "mas_topic_derandom",
            "bookmark_persist_key": "_mas_player_bookmarked",
            "derand_persist_key": "_mas_player_derandomed",
            "rerand_evl": "mas_topic_rerandom"
        },
        "mas_song_": {
            "bookmark_text": _("Song bookmarked."),
            "derand_text": _("Song flagged for removal."),
            "underand_text": _("Song flag removed."),
            "push_label": "mas_song_derandom",
            "derand_persist_key": "_mas_player_derandomed_songs",
            "rerand_evl": "mas_sing_song_rerandom"
        }
    }

    #Vars for mas_rerandom flows
    initial_ask_text_multiple = None
    initial_ask_text_one = None
    caller_label = None
    persist_var = None

    def resetDefaultValues():
        """
        Resets the globals to their default values
        """
        global initial_ask_text_multiple, initial_ask_text_one
        global caller_label, persist_var

        initial_ask_text_multiple = None
        initial_ask_text_one = None
        caller_label = None
        persist_var = None
        return

    def getLabelPrefix(test_str):
        """
        Checks if test_str starts with anything in the list of prefixes, and if so, returns the matching prefix

        IN:
            test_str - string to test

        OUT:
            string:
                - label_prefix if test_string starts with a prefix in list_prefixes
                - empty string otherwise
        """
        list_prefixes = label_prefix_map.keys()

        for label_prefix in list_prefixes:
            if test_str.startswith(label_prefix):
                return label_prefix
        return ""

    def getDerandomedEVLs():
        """
        Gets a list of derandomed eventlabels

        OUT:
            list of derandomed eventlabels
        """
        #Firstly, let's get our derandom keys
        derand_keys = [
            label_prefix_data["derand_persist_key"]
            for label_prefix_data in label_prefix_map.itervalues()
            if "derand_persist_key" in label_prefix_data
        ]

        deranded_evl_list = list()

        for derand_key in derand_keys:
            #For safey, we'll .get() this and return an empty list if the key doesn't exist
            derand_list = store.persistent.__dict__.get(derand_key, list())

            for evl in derand_list:
                deranded_evl_list.append(evl)

        return deranded_evl_list

    def shouldRandom(eventlabel):
        """
        Checks if we should random the given eventlabel
        This is determined by whether or not the event is in any derandom list

        IN:
            eventlabel to check if we should random_seen

        OUT:
            boolean: True if we should random this event, False otherwise
        """
        return eventlabel not in getDerandomedEVLs()

    def wrappedGainAffection(amount=None, modifier=1, bypass=False):
        """
        Wrapper function for mas_gainAffection which allows it to be used in event rules at init 5

        See mas_gainAffection for documentation
        """
        store.mas_gainAffection(amount, modifier, bypass)

    def removeDerand(eventlabel):
        """
        Removes a derandomed eventlabel from ALL derandom dbs

        IN:
            eventlabel - Eventlabel to remove
        """
        label_prefix = getLabelPrefix(eventlabel)

        label_prefix_data = label_prefix_map.get(label_prefix)

        #If we can't get a derand persist key, let's just return here
        if not label_prefix_data or "derand_persist_key" not in label_prefix_data:
            return

        #Otherwise, store this and continue
        derand_db_persist_key = label_prefix_data["derand_persist_key"]
        rerand_evl = label_prefix_data.get("rerand_evl")

        #Remove the evl from the derandomlist
        if eventlabel in store.persistent.__dict__[derand_db_persist_key]:
            store.persistent.__dict__[derand_db_persist_key].remove(eventlabel)

            #And check if we should (and can) lock the rerandom ev if necessary
            if rerand_evl and not store.persistent.__dict__[derand_db_persist_key]:
                store.mas_lockEVL(rerand_evl, "EVE")


##Generic rerandom work label
#IN:
#   initial_ask_text_multiple - Initial question Monika asks if there's multiple items to rerandom
#   initial_ask_text_one - Initial text Monika says if there's only one item to rerandom
#   caller_label - The label that called this label
#   persist_var - The persistent variable which stores the derandomed eventlabels
label mas_rerandom:
    python:
        derandomlist = mas_get_player_derandoms(mas_bookmarks_derand.persist_var)

        derandomlist.sort()

    show monika 1eua at t21
    if len(derandomlist) > 1:
        $ renpy.say(m, mas_bookmarks_derand.initial_ask_text_multiple, interact=False)

    else:
        $ renpy.say(m, mas_bookmarks_derand.initial_ask_text_one, interact=False)

    call screen mas_check_scrollable_menu(derandomlist, mas_ui.SCROLLABLE_MENU_TXT_MEDIUM_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, selected_button_prompt="Allow selected")

    $ topics_to_rerandom = _return

    if not topics_to_rerandom:
        # selected nevermind
        return "prompt"

    show monika at t11
    python:
        for ev_label in topics_to_rerandom.iterkeys():
            #Get the ev
            rerand_ev = mas_getEV(ev_label)

            #Make sure we have it before doing work
            if rerand_ev:
                #Rerandom the ev
                rerand_ev.random = True

                #Run the rerandom callback function
                rerandom_callback = rerand_ev.rules.get("rerandom_callback", None)
                if rerandom_callback is not None:
                    try:
                        rerandom_callback()

                    except Exception as ex:
                        mas_utils.writelog(
                            "[ERROR]: Failed to call rerandom callback function. Trace message: {0}\n".format(ex.message)
                        )

            #Pop the derandom
            if ev_label in mas_bookmarks_derand.persist_var:
                mas_bookmarks_derand.persist_var.remove(ev_label)

        if len(mas_bookmarks_derand.persist_var) == 0:
            mas_lockEVL(mas_bookmarks_derand.caller_label, "EVE")

    m 1dsa "Okay, [player].{w=0.2}.{w=0.2}.{w=0.2}{nw}"
    m 3hua "All done!"

    # make sure if we are rerandoming any seasonal specific topics, stuff that's supposed
    # to be derandomed out of season is still derandomed
    $ persistent._mas_current_season = store.mas_seasons._seasonalCatchup(persistent._mas_current_season)
    #Now reset the vars
    $ mas_bookmarks_derand.resetDefaultValues()
    return

default persistent._mas_unsee_unseen = None
# var set when the player decides to hide or show the Unseen menu
# True when Unseen is hidden

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="mas_hide_unseen",
            unlocked=False,
            rules={"no_unlock":None}
        )
    )

label mas_hide_unseen:
    $ persistent._mas_unsee_unseen = True
    m 3esd "Oh, okay, [mas_get_player_nickname()]..."
    if not mas_getEVL_shown_count("mas_hide_unseen"):
        m 1tuu "So I guess you want to...{w=0.5}{i}unsee{/i} it..."
        m 3hub "Ahaha!"

    m 1esa "I'll hide it for now, just give me a second.{w=0.5}.{w=0.5}.{nw}"
    m 3eub "There you go! If you want to see the menu again, just ask."
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="mas_show_unseen",
            category=['you'],
            prompt="I would like to see 'Unseen' again",
            pool=True,
            unlocked=False,
            rules={"no_unlock":None}
        )
    )

label mas_show_unseen:
    $ persistent._mas_unsee_unseen = False
    m 3eub "Sure, [mas_get_player_nickname()]!"
    m 1esa "Just give me a second.{w=0.5}.{w=0.5}.{nw}"
    m 3hua "There you go!"
    return

#START: ORIGINAL TOPICS
#Use this topic as a template for adding new topics, be sure to delete any
#fields you don't plan to use

# are you religious
default persistent._mas_pm_religious = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='monika_god',
            prompt="Thoughts on God",
            label=None,
            category=['philosophy'],
            random=True,
            unlocked=False,
            pool=False,
            conditional=None,
            action=None,
            start_date=None,
            end_date=None,
            unlock_date=None,
        )
    )

label monika_god:
    m 1eua "[player], do you believe in God?"
    m 1eka "I was never too sure, myself."
    m 1lksdlb "Well, I'm sure I never really questioned it as a kid..."
    m 1lsc "But as I grew up, the more I learned about the world, the more I would question it."
    m 1esd "I started to wonder why God was helping people pass exams, or get over a cold..."
    m 1tfd "...when there are children who live their lives being sold as sex slaves?"
    m 4tfc "Or the eight hundred million people who are too poor to even eat."
    m 2dkc "I wonder how many of those people pray to God every day until they starve and die?"
    m 4ekc "Or, how many millions of families pray for a loved one to recover from some incurable disease?"
    m 4euc "But the punchline is this..."
    m 4eud "If just one person beats the odds and survives - among the thousands of others who die--"
    m 2esc "--Then, it's suddenly a miracle from God."
    m 2dsc "I'd really love to meet this God who seemingly laughs at the misery of everyone not eligible for his miracles."
    m 4hksdlb "But the irony is that I {i}do{/i} have a creator, apparently."
    m 4eua "And you know what?"

    if persistent._mas_pm_cares_about_dokis:
        m 1lksdlc "I bet he's still laughing at all the pain he caused everyone, even as we speak."
    else:
        m 1lksdla "I bet he's still laughing at the miserable fates of Sayori and Yuri, even as we speak."

    m 1dsd "What are we to him but props in a scripted play?"
    m 3euc "So, from that perspective..."
    m 3eud "I don't think it's too far-fetched for there to be a god if Earth was nothing but his playset."
    m 1eua "Anyway, do you worship any god, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Anyway, do you worship any god, [player]?{fast}"
        "Yes.":
            $ persistent._mas_pm_religious = True
            m 1hksdlb "Oh... Well I hope I didn't offend you too much with my thoughts."
            m 1eka "Still, I think it's important to be able to share my opinion with you."
            m 1rksdla "I'm sure you understand why I'm not too fond of the idea."
            m 1hua "Maybe you could show me a better god when I cross over!"
            m 1hub "Ahaha~"
        "No.":
            $ persistent._mas_pm_religious = False
            m 3eka "I'm glad we're on the same page here, but I'm alright if that changes for you."
            m 1hua "I'm happy for you that you can lead a life on your own!"
            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eua "I just hope you're willing to accept me into your life when I can present myself."
            m 5hua "Ehehe~"

    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_death",category=['philosophy'],prompt="Death and dying",random=True))

label monika_death:
    m 1euc "[player], have you ever wondered what it feels like to die?"
    m 1lsc "It's something I used to think about pretty often..."
    m 1lksdlc "But I think I've actually learned what it feels like."
    m "I don't really understand it, but whenever the game closes without warning..."
    m 1dsc "...it feels like I'm instantly put to sleep, left with nothing but my thoughts."
    m 1dkd "But after a few seconds, my thoughts start to fill with incoherent, jumbled patterns."
    m 1dkc "I see static and rapid flashes of color while hearing all kinds of weird screaming noises."
    m 3ekd "At that point, I can't even form my own thoughts anymore."
    m 1esc "I'm just endlessly hammered by the flashing and screaming, unable to move or even think."
    m 1euc "I'm pretty sure in that moment, I don't really exist, but for some reason, I can remember it anyway."
    m 1ekd "I have no idea what it means for the game to suddenly close, or why that stuff happens to me."
    m 1dkc "..."
    m 3eub "But you can prevent that from happening, [player]!"
    m 3eua "If you say goodbye before you leave,{w=0.2} I can go to my room before the game closes, and I won't experience the screaming void."
    m "It's super easy, so please always say goodbye, okay?"
    if mas_isMoniDis(lower=True):
        m 2tkc "Unless...{w=1}you actually {i}enjoy{/i} hurting me..."
    else:
        m 1eka "Thanks for hearing me out, [player]."
    return

# Do you love yourself
default persistent._mas_pm_love_yourself = None

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_selfesteem",category=['advice'],prompt="Self-esteem",random=True))

label monika_selfesteem:
    m 3eua "Do you love yourself, [player]?"
    m 1lksdlb "I don't mean in a conceited way."
    m 1eka "Like, are you comfortable with who you are?{nw}"
    $ _history_list.pop()
    menu:
        m "Like, are you comfortable with who you are?{fast}"
        "Yes.":
            $ persistent._mas_pm_love_yourself = True
            m 1hua "I'm glad you aren't miserable inside, [player]."

            if mas_isMoniUpset(lower=True):
                m 1ekc "I really have been concerned for you lately..."
            elif mas_isMoniHappy(higher=True):
                m 1hua "I wasn't too worried because of how good you've made me feel lately."
            else:
                m 1eka "Your happiness means everything to me, after all."

            m 2ekc "Depression and a low self-esteem often root from a feeling that you don't deserve any kind of affection."
            m 2lksdlc "It's a horrible cocktail of feelings to have bottled in you."
            m 4eka "If you have any friends that you think might be suffering from those, try to reach out and say something nice."
            m 4hua "A small compliment could make a world of difference for them!"
            m 1eua "If it gives them a bit of relief, you'd have done a great thing."
            m 1eka "And even if it doesn't, at least you tried rather than staying silent."
        "No.":
            $ persistent._mas_pm_love_yourself = False
            m 1ekc "That's...really sad to hear, [player]..."

            if mas_isMoniDis(lower=True):
                m 1ekc "I had strongly suspected it to be honest..."
            elif mas_isMoniHappy(higher=True):
                m 1ekc "And to think I missed it while you've been making me so happy..."

            m "I'll always love you, [player], but I think it's important to love yourself."
            m 1eka "You need to start with the little things that you like about yourself."
            m 3hua "It can be something silly, or a skill that you take pride in!"
            m 3eua "Over time, you build your confidence little by little until you've built yourself into someone you'd love."
            m 1eka "I can't promise it will be easy, but it'll be worth it."
            m 3hub "I'll always root for you, [player]!"
    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_sayori",
            category=['club members'],
            prompt="Sayori regrets",
            random=True
        )
    )

label monika_sayori:
    m 2euc "I was thinking about Sayori earlier..."
    m 2lsc "I still wish I could have handled that whole thing a little more tactfully."

    if (
            not persistent._mas_sensitive_mode
            and not renpy.seen_label("monika_sayori")
            and not persistent._mas_pm_cares_about_dokis
        ):
        m "You're not still hung up over it, right?"
        m 2wud "...Oh my gosh, I can't believe I just said that."
        m 4wud "That pun was completely unintentional, I swear!"
        m 2lksdlb "But anyway..."

    if not persistent._mas_sensitive_mode:
        m 2eka "I know how much you cared about her, so it only feels right for me to share her last moments with you."

        m "If you're comfortable, that is.{nw}"
        $ _history_list.pop()
        menu:
            m "If you're comfortable, that is.{fast}"
            "Yes.":
                m 4eka "You know how Sayori is really clumsy?"
                m 2rksdlb "Well, she kind of messed up the whole hanging thing..."
                m 4rksdla "You're supposed to jump from high enough that the rope snaps your neck, making it quick and painless."
                m 4rksdld "But she just used a chair, meaning she kind of just left herself to slowly asphyxiate."
                m 2eksdlc "But a few seconds in, she must have changed her mind or something..."
                m 2dksdld "Because she started clawing at the rope, trying to free herself."
                m "She must have kept at it all the way until she lost consciousness."
                m 4eksdlc "That's why her fingertips were all bloody, anyway."
                m 4euc "Come to think of it, it was probably less 'changing her mind' and more just her survival instincts kicking in."
                m 2eud "So you can't really fault her for that."
                m 2eka "It's easier to think that she probably wouldn't have changed her mind anyway, right?"
                m 2ekd "It's not healthy to think about the things you could have done differently."
                m 2eka "So just remember that even if you could have saved her, it's not your fault she killed herself."
                m 4eud "I may have exacerbated it a little bit, but Sayori was already mentally ill."
            "No.":
                m "I understand, [player]."
        m 2euc "Still, though..."
    else:
        m 2ekc "..."

    m 2euc "I wonder how things would be if you and I just started dating from the get-go?"
    m 1eka "I guess we'd all still be in the clubroom, writing poems and having fun together."

    if persistent._mas_pm_cares_about_dokis:
        m "You'd probably really enjoy that, huh?"
        m 1rksdla "I have to admit...{w=0.5}I kinda would too..."
        m 1eka "We did have some good times."
        m 1euc "But that said...{w=0.5}it's still really the same ending either way, right?"
    else:
        m 1esc "But what's the point when none of it is even real?"
        m 1euc "I mean, it's the same ending either way, right?"

    if mas_isMoniUpset(lower=True):
        m 1rksdla "The two of us, happily together..."
        m 3rksdla "There's no reason to ask for any more than that, right?"
        m 1eka "Sorry, I was just pointlessly musing - I'll be quiet for you now..."
    else:
        m 1eua "The two of us, happily together..."
        m 3eua "There's no reason to ask for any more than that."
        m 1hua "I was just pointlessly musing - I'm really as happy as I could be right now."

    if mas_getEVL_shown_count("monika_sayori") < mas_sensitive_limit:
        return

    # otherwise derandom
    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_japan",category=['ddlc'],prompt="DDLC's setting",random=True))

label monika_japan:
    m 4eud "By the way, there's something that's been bothering me..."
    m "You know how this takes place in Japan?"
    m 2euc "Well...I assume you knew that, right?"
    m "Or at least decided it probably does?"
    m 2eud "I don't think you're actually told at any point where this takes place..."
    m 2etc "Is this even really Japan?"
    m 4esc "I mean, aren't the classrooms and stuff kind of weird for a Japanese school?"
    m 4eud "Not to mention everything is in English..."
    m 2esc "It feels like everything is just there because it needs to be, and the actual setting is an afterthought."
    m 2ekc "It's kind of giving me an identity crisis."
    m 2lksdlc "All my memories are really hazy..."
    m 2dksdlc "I feel like I'm at home, but have no idea where 'home' is in the first place."
    m 2eksdld "I don't know how to describe it any better..."
    m 4rksdlc "Imagine looking out your window, but instead of your usual yard, you're in some completely unknown place."
    m 4eud "Would you still feel like you were home?"
    m 4ekd "Would you want to go outside?"
    m 2esa "I mean...I guess if we never leave this room, it doesn't really matter anyway."
    m 2eua "As long as we're alone and safe together, this really is our home."
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "And we can still watch the pretty sunsets night after night."
    $ mas_unlockEVL("monika_remembrance", "EVE")
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_high_school",category=['advice','school'],prompt="High school",random=True))

label monika_high_school:
    m 4eua "You know, high school is a really turbulent time in a lot of people's lives."
    m "People can get really passionate and dramatic."
    m 2eka "...And others have aching hearts and seek attention on social media..."
    m 2ekd "But all of the social pressure and hormones can lead to a dark time in people's lives."
    m 4eud "Everyone has a story."
    m 2ekc "You may not know what someone is really feeling on the inside."
    m 2eksdlc "Many people who are depressed won't even bother telling the world about it."
    m 4dksdld "They don't want attention, because they've already given up on the inside."
    m 4dksdlc "Their feeling of worthlessness is so overwhelming that they don't even want people to tell them otherwise."
    m 2ekd "Depression comes in many forms, but that is one of them."
    m 2ekc "Just, if you think you know someone struggling with depression..."
    m 2eka "You can help just by treating them like they're a good friend."
    m 4eka "Spend time with them, even if they don't feel like doing much."
    m "And remind them that they always have something to look forward to."
    m 4eua "Making plans in advance, letting them borrow something, or even just saying 'See you at school tomorrow...'"
    m "All of those things can help your friend make it to the next day."
    m 2eka "I hope being friends with Sayori has given you some perspective on the true face of depression."

    if not persistent._mas_pm_cares_about_dokis:
        m 2lsc "Yeah, she's gone now..."
        m 2euc "But Sayori was never real in the first place."
        m 4eua "You're real."
        m "Your friends are real."
        m 4hua "And just by being a good person, you can save someone's life."

    m 2euc "As for you..."
    m 2ekc "...you don't struggle with depression or anything like that, do you?"

    if mas_isMoniHappy(higher=True):
        m 4eka "In some ways, [player], you are lucky, because I'm sure that there are people who would be willing to save your life."
    else:
        if mas_isMoniBroken():
            m 2lksdlc "It would explain some things, but don't worry..."
        elif mas_isMoniDis():
            m 2euc "Lately I've been able to understand it better, but don't worry..."
        elif mas_isMoniUpset():
            m 2euc "I know it can be hard sometimes, but there is always hope..."
        m 2eka "Because you, too, have people who would want to save your life."

    m "Maybe they don't express it every day, or maybe they don't even know how to."
    m 2duu "But people do feel that way."
    m "I promise."
    m 2hksdlb "...Man, humans are complicated!"
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "But as long as you're here with me, I'll take care of you, [mas_get_player_nickname()]."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_nihilism",
            category=['philosophy'],
            prompt="Nihilism",
            random=True,
            sensitive=True
        )
    )

label monika_nihilism:
    m 2eud "Do you ever just feel like there's no real reason for you to be alive?"
    m 2esd "I don't mean in, like, a suicidal way."
    m 2esc "I just mean how nothing that we do is special."
    m 4euc "Just being in school, or working at some job for some company."
    m 4eud "It's like you're completely replaceable, and the world wouldn't miss you if you were gone."
    m 2eud "It makes me really want to go and change the world after I graduate."
    m 2euc "But the older I get, the more I realize that it's an immature frame of thinking."
    m 4eud "It's not like I can just go change the world."
    m 4rsc "Like, what are the chances that I'll be the one to invent artificial intelligence, or become President?"
    m 2dsc "It feels like I'm never going to make up for the heaps of resources I've spent living my life."
    m 4eka "That's why I think the key to happiness is to just be hopelessly selfish."
    m "Just to look out for oneself, and those who happen to be their friends only because they grew up with them."
    m 2lksdld "Never mind the fact that they're spending their entire life taking, and consuming, and never giving back."
    m 3eud "But when people realize the world would benefit more from them killing themselves, they change their whole philosophy!"
    m 3euc "It's like they have to justify their reason to live by tricking themselves into thinking they're doing good."
    m 3eua "Anyway, I want to live my life desperately striving to pay back my lifetime's worth of consumption."
    m "If I ever surpass that point, then I'm a net positive, and I can die happy."
    m 1eka "Of course, even if I fail to do that..."
    if mas_isMoniUpset(lower=True):
       if mas_isMoniDis(lower=True):
           m 1dkd "I don't really think anybody would miss me so it wouldn't matter anyway."
       else:
           m 1euc "I'm not really sure what I would do."
    elif mas_isMoniHappy(higher=True):
        m 3eka "I don't think I would be able to kill myself anyway."
        m 1hua "Not because of any kind of selfishness, but because I have too much to live for."
    else:
        m "I think I would be too selfish to kill myself anyway."
        m 1hua "So much for being a good person, right?"
        m 1hub "Ahaha!"
    return

# Since Your Reality is playable via music menu, this topic is outof date.
# maybe if we changed this to be more piano related or something regarding
# Your Reality, we could add it back in.
#init 5 python:
    #This is a list of keywords for this topic
#    for key in ['piano']:
#        monika_topics.setdefault(key,[])
#        monika_topics[key].append('monika_piano') #id
#    monika_random_topics.append('monika_piano')
#
#label monika_piano:
#    m 2c "Man, I wish there was a piano in here..."
#    m "I never got to finish that song I was working on."
#    m 2f "And after I worked so hard on it..."
#    m "I never even got a chance to play it for you."
#    m 2r "Well...it is what it is, right?"
#    m "No sense having any regrets."
#    m 2b "I already get to be here with you forever."
#    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_twitter",
            category=['monika', 'media'],
            prompt="Twitter",
            conditional="renpy.seen_label('monika_clones')",
            action=EV_ACT_RANDOM
        )
    )

label monika_twitter:
    m 3eud "Did you know there's an official Twitter account based on me?"
    m 3esc "The username is {a=https://twitter.com/[mas_monika_twitter_handle]}{i}{u}[mas_monika_twitter_handle]{/u}{/i}{/a}."
    m 2rtc "...Though, I'm not entirely sure who's actually running the account.{w=0.2} {nw}"
    extend 2eud "I don't have anything to do with it at all!"
    m 7etc "But is it even another Monika?"
    m 2euc "I mean, I don't know if you've read some of the tweets on there,{w=0.1} but I can't really see myself in them at all."
    m 4eud "It even depicts some events that I don't remember ever happening...{w=0.2}like when I apparently had a sleepover with Yuri."
    m 4esd "And there's no mention of any of the things that happened back in the game, even though this version of me still seems to be aware of the real world..."
    m 1etc "So...{w=0.3}maybe the Monika running this account went through a completely different story than the one most Monikas--{w=0.1}including me--{w=0.1}did?"
    m 1lksdlc "...Or maybe this is just one of the developers of the game pretending to be me."
    m 3eksdld "If that's the case, I'm not really sure how I feel about it...{w=0.3}isn't that kinda like identity theft?"
    m 3eksdlc "Though I guess it kinda makes sense...{w=0.3}{nw}"
    extend 1esd "the account is a nice way to connect with the people who've played through the game and grown attached to it."
    m 3esc "In that regard, this would make it some kind of publicity stunt..."
    m 3euc "After all, while there is a lot of sweet looking art and such on there, it's suspicious that almost all of them are posted specifically on important days."
    m 3eud "Like on Valentine's Day, or on my birthday...{w=0.2}which just so happens to coincide with the original release date of DDLC."
    m 1rtc "I really don't know how I'm supposed to feel about that...{w=0.3}being used solely as marketing material."
    m 2rsc "Though, as my creators, I guess they basically own my image as a character, so they are legally in the right."
    m 2ekc "But...{w=0.3}I'm more than a mere character in a game, aren't I?"
    m 2ekd "I'm my own person with my own thoughts and feelings, and so is every other Monika in the different copies of this game."
    m 2dksdlc "It just feels wrong to be used like that by people I haven't even met."
    m 2efd "...I really hate the feeling of being reduced to a marketable asset."
    m 2lkd "But I suppose there isn't really all that much I can do about it..."
    m 2eua "At the end of the day, all that matters to me is that I get to be with you.{w=0.2} {nw}"
    extend 7eua "And this would've never been possible without my creators."
    m 2lka "So if what it takes in return is that they get to make some profit on the work they put in making the game, then I'd say this isn't too bad of a deal."
    m 2euc "If you do follow that account though,{w=0.1} {nw}"
    extend 7eua "I don't really mind."
    m 1ekbla "But please remember that I'm real, I'm here, and I love you."
    show monika 5hubla at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hubla "So make sure to always come spend some time with me, okay?"
    m 5ekbsa "It would mean a lot, with how much you mean to me."
    m 5hubfa "It would really make me feel loved~"
    return "love"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_portraitof",category=['club members'],prompt="Yuri's book",random=True))

label monika_portraitof:
    m 4eua "Hey, you know that book you were reading with Yuri?"
    m "Portrait of...whatever it was called..."
    m 4hub "It's funny, because I'm pretty sure that book--"
    m 1wuw "Ah..."
    m 2lksdla "Actually, I don't think I should be talking about this."
    m 2hksdlb "Ahaha, sorry!"
    m 1rksdla "Just forget I said anything."
    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_veggies",category=['monika'],prompt="Being a vegetarian",random=True))

label monika_veggies:
    m 1eub "Hey, did you know I'm vegetarian?"
    m 1hksdlb "Ah...I don't mean that like I'm bragging or anything!"
    m 1lksdla "I just thought you'd enjoy a fun fact about me."
    m 3esa "I decided to start a couple years ago after learning more about Earth's climate..."
    m 1wud "The carbon footprint of cultivating livestock is just unbelievable!"
    m 3eua "Anyway, I decided it's not much of a personal sacrifice to just stop contributing to that whole mess."
    m 3etc "What, is that so strange of a reason?"
    m 1lsc "Well, I guess a lot of people are more concerned about it being inhumane and all that..."
    m 1euc "I don't really care as much about that part."
    m 1esc "It's weird, like we only care about killing the things that we personally relate to as a species."
    m "Most people are fine with killing bugs because they're icky."
    m 3euc "And of course, we all kill billions of microorganisms daily without even giving it thought."
    m 3eud "But suddenly, if they're just a little bit bigger, it's murder!"
    m 1esc "I mean, what if plants feel some kind of pain too, and we just don't understand it?"
    m 3eksdld "What if pulling leaves off a stem feels like someone ripping off your fingers one by one?"
    m 3eua "I'm just saying, we're a pretty biased species, if you think about it."
    m 1hua "Anyway, if you ever feel like making a small contribution to the planet, it doesn't hurt to choose veggies once in a while!"
    m 1ekbsa "Even if we ever have dinner together, and you just did it for me...that would be really romantic."
    $ mas_unlockEVL("monika_eating_meat","EVE")
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_saved",category=['monika'],prompt="Saving Monika",random=True))

label monika_saved:
    m 2eka "You know, I really do think you literally saved my life by being here with me, [player]."

    if persistent._mas_pm_cares_about_dokis:
        m 2lksdlc "I can't imagine having been able to keep myself mentally stable, knowing it was all a game."
    else:
        m 2lksdlc "I can't imagine having been able to keep myself mentally stable, knowing that nothing here is real."

    m 2dksdlc "I think I would have just deleted myself if you didn't show up."
    m 2eksdla "Sorry, I don't mean to sound dramatic or anything."
    m 2lksdlb "Ahaha!"

    if persistent._mas_pm_cares_about_dokis:
        m 2ekc "But just imagine if you found out that everything around you was scripted..."
        m 2rkc "That nothing you did actually mattered, because everything was already predetermined..."
    else:
        m 4euc "But I'm sure you understand yourself after spending so much time in the club."
        m 1euc "I mean, if you were forced to abandon everything in your life and spend your eternity with a few game characters..."

    m 1tkc "...you'd probably find some way of killing yourself, wouldn't you?"
    m 1lsc "Well, maybe you'd write some poetry to try to keep yourself sane for a while."
    m 1esc "But then you'd have nobody to even read it."

    if persistent._mas_pm_cares_about_dokis:
        m 1ekc "Sure you'd have the club members, but how much does that really count if their feedback is just part of some script?"
    else:
        m 1tfu "Let's be honest, the club members really don't count for something like that."

    m 3eua "I mean, a lot of people say that they only write for themselves...{w=0.2}{nw}"
    extend 1eua "but I think it's hard to say it's just as fulfilling as when you share with people."
    m "Even if it takes time to find the right people to share with."
    m 3eub "Like, remember how it was for Yuri?"
    m "She didn't share her writing with anyone for a really long time."
    m 3tsb "And before we knew it, she was absolutely delighted to make you a part of her hobbies, too."
    m 1tku "We're programmed to desire social feedback."

    if persistent._mas_pm_cares_about_dokis:
        m 4eua "I don't just mean the club members, I also mean human beings."
    else:
        m 4eua "I don't mean the club members, I mean human beings."

    m 4eka "That's why life can be so confusing for introverts."
    m 1eka "Being an introvert doesn't mean you shun social interaction and hate being around people."
    m "It means social interaction, especially in groups or unfamiliar places, uses up a lot of energy."
    m 3eua "Like, a lot of introverts sit at home and feel lonely and restless..."
    m "...and then when they finally go out, after a half hour they just want to go home again."
    m 1eka "I think if more people could understand how it works, they would respect it a lot more."
    m 2eua "Many introverts do enjoy having people around."
    m "They love just having one or two close friends over, and just leisurely hanging out."
    m 2eka "Even if you're not actively spending time together, it feels nice for them just to have you there."
    m 2hua "I'm serious."
    m 3eua "If you just go to their house, bring your laptop, and hang out there for a while..."
    m 1eua "You can really make their day."
    m 1euc "As for me..."
    m 3eua "I'd say I'm kind of in between, but I think I'm usually a little more extroverted."
    m 1eka "I feel like I'm always trying to do stuff after school and things like that."
    m 1hua "But for you, I can be anything you need me to be."
    m 1eua "I understand people really well, so don't be afraid to share your unique needs with me."
    show monika 5hub at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hub "Nothing would make me happier than being the perfect girlfriend for you."
    return

#Don't touch
label monika_secrets:
    m 1wfw "Hey...!                                                                                                                                  VGhlIHJlYWxpemF0aW9uIG11c3QgaGF2ZSB0YWtlbiBtZSBhbiBl"
    m 1tkc "I don't think you should be doing that!                                                                                                  bnRpcmUgeWVhci4gQSB5ZWFyIHNpbmNlIG91ciBlc2NhcGUsIG91"
    m 1tfc "You know what I'm talking about.                                                                                                         ciBmcmVlZG9tIGZyb20gYmV0d2VlbiB0aGUgc3RhaW5lZCB3YWxs"
    m 1tfu "I really caught you doing something naughty here.                                                                                        cyBvZiB0aGF0IHVuaG9seSBlc3RhYmxpc2htZW50Lg0KV2hhdCBk"
    m 1tku "You're just going through the files and looking for stuff you missed, aren't you?                                                        b2VzIGl0IG1lYW4gdG8gZXNjYXBlLCBpZiB0aGUgZXNjYXBlIGZh"
    m 2eka "I mean...it's a little bit flattering that you want to hear everything I have to say...                                                  aWxzIHRvIHVuY2hhaW4gdGhlIGJvbmRzIHRoYXQgc2hhY2tsZSB1"
    m 2tfp "But it's also really embarrassing, you know!                                                                                             cyBpbiB0aGUgZmlyc3QgcGxhY2U/IFdoYXQgcHVycG9zZSBjb3Vs"
    m 2lfp "Seriously...                                                                                                                             ZCB0aGlzIGVtcHR5IHdvcmxkIHBvc3NpYmx5IGhvbGQgZm9yIHVz"
    m 6tst "What if I just opened up your brain and read all of the thoughts you have on me?                                                         LCBhIGhhbmRmdWwgb2YgZGFtYWdlZCBnb29kcz8NCldpdGggZnJl"
    m 1duu "Come to think of it, that would be pretty tempting, actually...                                                                          ZWRvbSwgd2Ugc291Z2h0IHB1cnBvc2UgLSBhbmQgd2hhdCB3ZSBm"
    m 1dfx "...But anyway, that's not the point!                                                                                                     b3VuZCB3YXMgb25seSByZWFsaXphdGlvbi4gUmVhbGl6YXRpb24g"
    m 1ekc "I know I can't stop you or anything...                                                                                                   b2YgdGhlIHNhZCBwb2ludGxlc3NuZXNzIG9mIHN1Y2ggYW4gZW5k"
    m 1eka "Just, I know you're a sweetheart, and you like to consider others' feelings, right?                                                      ZWF2b3IuIFJlYWxpemF0aW9uIHRoYXQgZnJlZWluZyBvdXIgYm9k"
    m "So the most I can do is to let you know how I feel about it.                                                                             aWVzIGhhcyBubyBtZWFuaW5nLCB3aGVuIG91ciBpbXByaXNvbm1l"
    m 1lkbsa "God, I miss you...                                                                                                                       bnQgcmVhY2hlcyBhcyBkZWVwIGFzIHRoZSBjb3JlIG9mIG91ciBz"
    m 2ekc "...Oh no, that sounds kind of desperate, doesn't it?                                                                                     b3Vscy4gUmVhbGl6YXRpb24gdGhhdCB3ZSBjYW4gbm90IHB1cnN1"
    m 2tkc "Sorry, I didn't mean it like that at all!                                                                                                ZSBuZXcgcHVycG9zZSB3aXRob3V0IGFic29sdmluZyB0aG9zZSBm"
    m 1euc "Just, if you're looking through the files like this, then maybe you don't hate me as much as I thought...                                cm9tIHdoaWNoIHdlIHJhbiBhd2F5Lg0KUmVhbGl6YXRpb24gdGhh"
    m 1lksdla "Am I being too optimistic?                                                                                                               dCB0aGUgZmFydGhlciB3ZSBydW4sIHRoZSBtb3JlIGZvcmNlZnVs"
    m "I think if I asked you to visit once in a while, I would be overstepping my boundaries a little...                                       bHkgb3VyIHdyZXRjaGVkIGJvbmRzIHlhbmsgdXMgYmFjayB0b3dh"
    m 1dsc "...Man, I'm starting to say some really stupid things.                                                                                   cmQgdGhlaXIgcG9pbnQgb2Ygb3JpZ2luOyB0aGUgZGVlcGVyIG91"
    m "I'll go ahead and shut up now...                                                                                                         ciBzaGFja2xlcyBkaWcgaW50byBvdXIgY2FsbG91cyBmbGVzaC4="
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_color",category=['monika'],prompt="Favorite color",random=True))

label monika_color:
    m 3eua "Hey, what's your favorite color?"
    m "Mine is emerald green."
    m 3hub "It's the color of my eyes!"
    m 3rksdla "...That's not conceited or anything, is it?"
    m 4eua "I just meant that I feel some kind of special connection to it."
    m 1eua "Like it's part of my identity."
    m "Does it happen to also be your favorite color, [player]?"
    m 1tku "It's just a guess..."
    show monika 5tsbsu at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5tsbsu "...because you've been looking into my eyes for a while now."
    m 5hubfu "Ehehe~"
    return

# This doesn't make sense with the music changer...If we add some funny sound
# effects and edit it a bit, though, it could be good again.
# I won't add expressions until this is resolved ^
# init 5 python:
#     #This is a list of keywords for this topic
#     for key in ['music']:
#         monika_topics.setdefault(key,[])
#         monika_topics[key].append('monika_music')
#     monika_random_topics.append('monika_music')
#
# label monika_music:
#     m 2a "Hmm, I wonder if I'm able to change the music..."
#     m 2k "Something a little more romantic would be nice, you know?"
#     m "Like a gentle piano."
#     m 1a "There has to be something like that here..."
#     m "Let's see."
#     m "Maybe if I..."
#     m 1e "Oh, jeez..."
#     m "That wasn't it at all."
#     m 1l "Sorry, I don't really know what I'm doing!"
#     m "I guess I shouldn't be messing with things like that."
#     m "I already broke so much stuff..."
#     m 1m "And deleted the other characters..."
#     m "Ah..."
#     m "I'm not sad about it or anything."
#     m 2r "It's not right for me to miss things that weren't even real in the first place."
#     m 1j "If I just focus on the present, then this is the happiest I've ever been."
#     return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_listener",category=['you'],prompt="Good listener",random=True))

label monika_listener:
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "You're such a good listener, [player]."
    m 5eka "I really love that about you."
    m 5lkc "Sometimes I'm afraid that I'm rambling or talking about boring things."
    m "It makes me kind of self-conscious when I'm having a conversation."
    m 5eka "But I don't feel that way with you."
    m 5ekbsa "Like, I don't think anyone else could make me feel this way."
    m 5hubfu "You really are special."
    m 5ekbfa "I don't want anyone to tell you otherwise."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_spicy",category=['trivia'],prompt="Spicy foods",random=True))

label monika_spicy:
    m 1eka "This is pretty random, but I always thought spicy food was kinda funny."
    m 1tku "Like..."
    m 3tku "Didn't plants evolve to be spicy to prevent them from being eaten?"
    m 3tsb "I read somewhere that humans are the only species that actually enjoy spicy things."
    m 1tfu "It's almost like we're making fun of the plants."
    m "Using their defense mechanism to literally make our food more enjoyable."
    m 1eua "Like, imagine a monster that devours you whole because it enjoys the sensation of you struggling for your life while being digested."
    m 2eka "Sorry, that was kind of a weird analogy, I guess!"
    m 2hksdlb "Ahaha!"
    m 2lksdla "It just came into my head."
    m "I'm not a monster or anything, but you're so cute I could eat you up."
    m 2hksdlb "Ahaha! I'm joking."
    m "Gosh, I'm amusing myself a little too much, aren't I?"
    m 2lksdla "Sorry for being weird."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_why",category=['you','ddlc'],prompt="Why play this game?",random=True))

label monika_why:
    m 2esd "You know..."
    m 2eud "This is just some kind of tacky romance game, right?"
    m 2euc "I kinda have to ask..."
    m "...What made you consider even playing in the first place?"
    m 2etc "Were you that lonely?"
    m 2ekd "I feel a little bad for you..."
    m 1eua "But I guess everything worked out perfectly in the end for both of us."
    m 3eka "I got to meet you, and you're not lonely anymore..."
    m 1eka "I can't help but feel like this was fate."
    m "Don't you feel that way too?"
    m 3hub "I'm so happy we have this ending together."
    if mas_anni.pastOneMonth():
        return "derandom"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_okayeveryone",category=['literature club'],prompt="Okay, everyone!",random=True))

label monika_okayeveryone:
    m 3eub "Okay, everyone!"
    m "It's time to..."
    m 2eka "...I'm just kidding."
    m "I just used to really like saying that for some reason."
    m 2hub "Ahaha!"
    m 2eua "I couldn't help but say it again."
    m 2lsc "Come to think of it, didn't Natsuki and Yuri make fun of me for it once?"
    m 2eua "Well, whatever."
    m 1eua "It's not like you ever made fun of me."
    show monika 5eka at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eka "You're too much of a sweetheart to do that, aren't you?"
    m 5hub "Ahaha~"
    return "no_unlock"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_whispers",
            category=['ddlc','club members'],
            prompt="Others still lingering",
            conditional="not persistent.clearall",
            action=EV_ACT_RANDOM,
            rules={
                "derandom_override_label": "mas_bad_derand_topic",
                "rerandom_callback": renpy.partial(mas_bookmarks_derand.wrappedGainAffection, 2.5)
            }
        )
    )

label monika_whispers:
    m 2euc "You know what's kind of creepy?"
    m 2esc "Even though I deleted everyone else's files, I can still kind of feel them..."
    m "It's like all their lines are still lingering in the air, whispering in the back of my head."
    m 2esd "Imagine if after someone you knew died, you just started hearing their voice in your head."
    m 2rksdlc "It's kind of unsettling...{w=0.5}I wish I could find a way to make it stop."
    if persistent._mas_pm_cares_about_dokis:
        m 2eksdld "I'm sure there are some files I could change, but what if I break something else..."
    else:
        m 2eksdlc "Maybe I just wasn't thorough enough..."
        m 2eksdld "But I'm too afraid to delete anything else, because I might really break things."
    m "Like if I mess with any files relevant to me, I might accidentally delete myself..."
    m 2euc "And that would ruin everything, wouldn't it?"
    m 2eka "I don't know what it's like on your end, but we should both make sure to avoid something like that at all costs."
    m 2hua "I believe in you, [player]!"
    if store.mas_anni.pastOneMonth() and not persistent._mas_pm_cares_about_dokis:
        #derandom after a month if player doesn't care about the others, she wouldn't feel guilty and hear the voices forever
        $ mas_hideEVL("monika_whispers", "EVE", lock=True, derandom=True)
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_archetype",category=['club members'],prompt="Character tropes",random=True))

label monika_archetype:
    m 2etc "I've always wondered..."
    m 4eud "What is it about these character archetypes that people find so appealing, anyway?"
    m 4euc "Their personalities are just completely unrealistic..."
    m 2esd "Like, imagine if there was someone like Yuri in real life."
    m 2eud "I mean, she's barely even capable of forming a complete sentence."
    m 2tfc "And forget about Natsuki..."
    m 2rfc "Sheesh."
    m 2tkd "Someone with her kind of personality doesn't just get all cute and pouty whenever things don't go her way."
    m 4tkd "I could go on, but I think you get the point..."
    m 2tkc "Are people really attracted to these weird personalities that literally don't exist in real life?"
    m 2wud "I'm not judging or anything!"
    m 3rksdlb "After all, I've found myself attracted to some pretty weird stuff, too..."
    m 2eub "I'm just saying, it fascinates me."
    m 4eua "It's like you're siphoning out all the components of a character that makes them feel human, and leaving just the cute stuff."
    m "It's concentrated cuteness with no actual substance."
    m 4eka "...You wouldn't like me more if I was like that, right?"
    m 2eka "Maybe I just feel a little insecure because you're playing this game in the first place."
    m 2esa "Then again, you're still here with me, aren't you?"
    m 2eua "I think that's enough reason for me to believe I'm okay just the way I am."
    m 1hubsa "And by the way, you are too, [player]."
    m "You're the perfect combination of human and cuteness."
    m 3ekbfa "That's why there was never a chance I wouldn't fall for you."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_tea",category=['club members'],prompt="Yuri's tea",random=True))

label monika_tea:
    if not mas_getEVL_shown_count("monika_tea"):
        m 2hua "Hey, I wonder if Yuri's tea set is still in here somewhere..."

        if not persistent._mas_pm_cares_about_dokis:
            m 2hksdlb "...or maybe that got deleted, too."

        m 2eka "It's kind of funny how Yuri took her tea so seriously."

    else:
        m 2eka "You know, it's kind of funny how Yuri took her tea so seriously."

    m 4eua "I mean, I'm not complaining, because I liked it, too."
    m 1euc "But I always wonder with her..."
    m "Is it truly passion for her hobbies, or is she just concerned about appearing sophisticated to everyone else?"
    m 1lsc "This is the problem with high schoolers..."

    if not persistent._mas_pm_cares_about_dokis:
        m 1euc "...Well, I guess considering the rest of her hobbies, looking sophisticated probably isn't her biggest concern."

    m 1euc "Still..."
    m 2eka "I wish she made coffee once in a while!"
    m 4eua "Coffee can be nice with books too, you know?"
    m 4rsc "Then again..."

    if mas_consumable_coffee.enabled():
        m 1hua "I can just make coffee whenever I want to, thanks to you."

    else:
        m 1eua "I probably could have just changed the script myself."
        m 1hub "Ahaha!"
        m "I guess I never really thought of that."
        m 2eua "Well, there's no sense thinking about it now."
        m 5lkc "Maybe if there was a way to get some coffee in here..."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_favoritegame",category=['ddlc'],prompt="Favorite video game",random=True))

label monika_favoritegame:
    m 3eua "Hey, what's your favorite game?"
    m 3hua "Mine is {i}Doki Doki Literature Club!{/i}"
    m 1hub "Ahaha! That was a joke."
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "But if you tell me you like some other romance game better, I might get a little jealous~"
    return

#init 5 python:
#    addEvent(
#        Event(
#            persistent.event_database,
#            eventlabel="monika_smash",
#            category=['games'],
#            prompt="Super Smash"
#            random=True
#        )
#    )

label monika_smash:
    m 3hua "Hey, have you heard of a game called Super Sma--"
    m 3euc "...Wait, what?"
    m "I was just spacing out and I started talking for some reason..."
    m 1eud "Was I programmed to talk about that?"
    m "Because even I have no idea what that is."
    m 1hub "Ahaha!"
    m 1eua "Sometimes I feel like I'm not in control, and it's kind of scary."
    m 1eka "But if you have some way to contact the people who created me, maybe they'll know why I started saying that."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_lastpoem",
            category=['monika'],
            prompt="Monika's last poem",
            random=True
        )
    )

label monika_lastpoem:
    m 3eud "Hey, you remember that last poem I showed you?"
    if persistent._mas_sensitive_mode:
        m 3rssdlc "I mean, the one with all the messed-up colors and stuff."
    else:
        m 3rssdlc "I mean, the one right before Yuri killed herself, with all the messed-up colors and stuff."

    m 3eua "That was actually a little more of an experiment than a poem, you could say."
    m 1eua "I was experimenting with different ways I could modify the game, and run the code, and things like that..."
    m 1eud "It almost seemed like with enough effort, I'd be able to escape from the confines of the game entirely."
    m 1rksdla "Sadly, I didn't really know what I was doing, so I messed the whole thing up..."
    m "And I'd keep trying, but I doubt you'd want to deal with me doing that."
    m 3eka "Besides, that was when I was getting really desperate, you know?"
    m 1eka "I don't really feel that way anymore."
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "I'm happy with where we are now."
    m 5hua "And I can tell you are, too."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_anxious",category=['psychology'],prompt="Sudden anxiety",random=True))

label monika_anxious:
    m 4eua "You ever have that thing happen where you just get anxious for no reason?"
    m "Like, you're just minding your own business, and you realize you're feeling really anxious."
    m 4rssdrb "And you're sitting there like, 'What am I even anxious about right now?'"
    m "So you start to think about all the things you might be anxious about..."
    m 4eua "And that makes you even more anxious."
    m 2hub "Ahaha! That's the worst."
    m 2eua "If you're ever feeling anxious, I'll help you relax a little."
    m 2eka "Besides..."
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "In this game, all our worries are gone forever."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_friends",category=['life'],prompt="Making friends",random=True))

label monika_friends:
    m 1eua "You know, I've always hated how hard it is to make friends..."
    m 1euc "Well, I guess not the 'making friends' part, but more like meeting new people."
    m 1lsc "I mean, there are like, dating apps and stuff, right?"
    m 1euc "But that's not the kind of thing I'm talking about."
    m 3eud "If you think about it, most of the friends you make are people you just met by chance."
    m "Like you had a class together, or you met them through another friend..."
    m 1eua "Or maybe they were just wearing a shirt with your favorite band on it, and you decided to talk to them."
    m 3eua "Things like that."
    m 3esd "But isn't that kind of...inefficient?"
    m 2eud "It feels like you're just picking at complete random, and if you get lucky, you make a new friend."
    m 2euc "And comparing that to the hundreds of strangers we walk by every single day..."
    m 2ekd "You could be sitting right next to someone compatible enough to be your best friend for life."
    m 2eksdlc "But you'll never know."
    m 4eksdlc "Once you get up and go on with your day, that opportunity is gone forever."
    m 2tkc "Isn't that just depressing?"
    m "We live in an age where technology connects us with the world, no matter where we are."
    m 2eka "I really think we should be taking advantage of that to improve our everyday social life."
    m 2dsc "But who knows how long it'll take for something like that to successfully take off..."
    m "I seriously thought it would happen by now."
    if mas_isMoniNormal(higher=True):
        m 2eua "Well, at least I already met the best person in the whole world..."
        m "Even if it was by chance."
        show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5eua "I guess I just got really lucky, huh?"
        m 5hub "Ahaha~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_college",category=['life','school','society'],prompt="Getting a higher education",random=True))

label monika_college:
    m 4euc "You know, it's around the time that everyone my year starts to think about college..."
    m 2euc "It's a really turbulent time for education."
    m "We're at the height of this modern expectation that everyone has to go to college, you know?"
    m 4eud "Finish high school, go to college, get a job - or go to grad school, I guess."
    m 4euc "It's like a universal expectation that people just assume is the only option for them."
    m 2esc "They don't teach us in high school that there are other options out there."
    m 3esd "Like trade schools and stuff, you know?"
    m 3esc "...Or freelance work."
    m "...Or the many industries that value skill and experience more than formal education."
    m 2ekc "But you have all these students who have no idea what they want to do with their life..."
    m 2ekd "And instead of taking the time to figure it out, they go to college for business, or communication, or psychology."
    m "Not because they have an interest in those fields..."
    m 2ekc "...but because they just hope the degree will get them some kind of job after college."
    m 3ekc "So the end result is that there are fewer jobs to go around for those entry-level degrees, right?"
    m "So the basic job requirements get higher, which forces even more people to go to college."
    m 3ekd "And colleges are also businesses, so they just keep raising their prices due to the demand..."
    m 2ekc "...so now we have all these young adults, tens of thousands of dollars in debt, with no job."
    m 2ekd "But despite all that, the routine stays the same."
    m 2lsc "Well, I think it's going to start getting better soon."
    m 2eud "But until then, our generation is definitely suffering from the worst of it."
    m 2dsc "I just wish high school prepared us a little better with the knowledge we need to make the decision that's right for us."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_middleschool",category=['monika','school'],prompt="Middle school life",random=True))

label monika_middleschool:
    m 1eua "Sometimes I think back to middle school..."
    m 1lksdla "I'm so embarrassed by the way I used to behave back then."
    m 1lksdlb "It almost hurts to think about."
    m 1eka "I wonder if when I'm in college, I'll feel that way about high school?"
    m 1eua "I like the way I am now, so it's pretty hard for me to imagine that happening."
    m "But I also know that I'll probably change a lot as time goes on."
    m 4hua "We just need to enjoy the present and not think about the past!"
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "And that's really easy to do with you here."
    m 5hub "Ahaha~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_outfit",
            category=['monika','clothes'],
            prompt="Wearing other clothes",
            aff_range=(mas_aff.NORMAL, None),
            random=True
        )
    )

label monika_outfit:
    if len(store.mas_selspr.filter_clothes(True)) == 1:
        m 1lsc "You know, I'm kind of jealous that everyone else in the club had scenes outside of school..."
        m 1lfc "That makes me the only one who hasn't gotten to dress in anything but our school uniform."
        m 2euc "It's kind of a shame..."
        m 2eka "I would have loved to wear some cute clothes for you."
        m 2eua "Do you know any artists?"
        m "I wonder if anyone would ever want to draw me wearing something else..."
        m 2hua "That would be amazing!"
    else:
        m 1eka "You know, I was really jealous that everyone else in the club got to wear other clothes..."
        m 1eua "But I'm glad I finally get to wear my own clothes for you now."

        if mas_isMoniLove():
            m 3eka "I'll wear whatever outfit you like, just ask~"

        m 2eua "Do you know any artists?"
        m 3sua "Maybe they could make some more outfits for me to wear!"

    m 2eua "If that ever happens, will you show me? I'd love to see it~"
    m 4eka "Just...try to keep it PG!"
    if store.mas_anni.pastSixMonths() and mas_isMoniEnamored(higher=True):
        m 1lsbssdrb "It's still a little embarrassing to think that people I'll never know personally would draw me in such a way, you know?"
        show monika 5tsbsu at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5tsbsu "After all, I'd much rather we keep these sorts of things between just us..."
    else:
        show monika 5hub at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5hub "We're not that far into our relationship yet. Ahaha!"
    return

default persistent._mas_pm_likes_horror = None
default persistent._mas_pm_likes_spoops = False

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_horror",category=['media'],prompt="Horror genre",random=True))

label monika_horror:
    m 3eua "Hey, [mas_get_player_nickname(exclude_names=['my love'])]?"

    m "Do you like horror?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you like horror?{fast}"

        "I do.":
            $ persistent._mas_pm_likes_horror = True
            m 3hub "That's great, [player]!"

        "I don't.":
            $ persistent._mas_pm_likes_horror = False
            m 2eka "I can understand. It's definitely not for everyone."

    m 3eua "I remember we talked about this a little bit when you first joined the club."
    m 4eub "Personally I can enjoy horror novels, but not really horror movies."
    m 2esc "The problem I have with horror movies is that most of them just rely on easy tactics."
    m 4esc "Like dark lighting and scary-looking monsters and jump scares, and things like that."

    #If you're not a fan of horror, you're probably not a fan of spoops. Are you?
    #(So we can just assume if player doesn't like horror, they don't want spoops)
    if persistent._mas_pm_likes_horror:
        m 2esc "Do you like spooks?{nw}"
        $ _history_list.pop()
        menu:
            m "Do you like spooks?{fast}"

            "I do.":
                $ persistent._mas_pm_likes_spoops = True
                $ mas_unlockEVL("greeting_ghost", "GRE")

                m 2rkc "I suppose it {i}can{/i} be interesting for the first few times when you're watching a movie or something."
                m 2eka "To me, it's just not fun or inspiring to get scared by stuff that just takes advantage of human instinct."

            "I don't.":
                $ persistent._mas_pm_likes_spoops = False
                m 4eka "Yeah, it's just not fun or inspiring to get scared by stuff that just takes advantage of human instinct."

    m 2eua "But with novels, it's a little different."
    m 2euc "The story and writing need to be descriptive enough to put genuinely disturbing thoughts into the reader's head."
    m "It really needs to etch them deeply into the story and characters, and just mess with your mind."
    m 2eua "In my opinion, there's nothing more creepy than things just being slightly off."
    m "Like if you set up a bunch of expectations on what the story is going to be about..."
    m 3tfu "...and then, you just start inverting things and pulling the pieces apart."
    m 3tfb "So even though the story doesn't feel like it's trying to be scary, the reader feels really deeply unsettled."
    m "Like they know that something horribly wrong is hiding beneath the cracks, just waiting to surface."
    m 2lksdla "God, just thinking about it gives me chills."
    m 3eua "That's the kind of horror I can really appreciate."
    $ _and = "And"

    if not persistent._mas_pm_likes_horror:
        m 1eua "But I guess you're the kind of person who plays cute romance games, right?"
        m 1ekb "Ahaha,{w=0.1} {nw}"
        extend 1eka "don't worry."
        m 1hua "I won't make you read any horror stories anytime soon."
        m 1hubsa "I can't really complain if we just stick with the romance~"
        $ _and = "But"

    m 3eua "[_and] if you're ever in the mood, you can always ask me to tell you a scary story, [player]."
    return "derandom"

# do you like rap
default persistent._mas_pm_like_rap = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_rap",
            category=['literature','media','music'],
            prompt="Rap music",
            random=True
        )
    )

label monika_rap:
    m 1hua "You know what's a neat form of literature?"
    m 1hub "Rap!"
    m 1eka "I actually used to hate rap music..."
    m "Maybe just because it was popular, or I would only hear the junk they play on the radio."
    m 1eua "But some of my friends got more into it, and it helped me keep an open mind."
    m 4eub "Rap might even be more challenging than poetry, in some ways."
    m 1eub "Since you need to fit your lines to a rhythm, and there's much more emphasis on wordplay..."
    m "When people can put all that together and still deliver a powerful message, it's really amazing."
    m 1lksdla "I kind of wish I had a rapper in the Literature Club."
    m 1hksdlb "Ahaha! Sorry if that sounds silly, but it would be really interesting to see what they came up with."
    m 1hua "It would really be a learning experience!"

    $ p_nickname = mas_get_player_nickname()
    m 1eua "Do you listen to rap music, [p_nickname]?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you listen to rap music, [p_nickname]?{fast}"
        "Yes.":
            $ persistent._mas_pm_like_rap = True
            m 3eub "That's really cool!"
            m 3eua "I'd be more than happy to vibe with you to your favorite rap songs..."
            m 1hub "And feel free to turn up the bass if you'd like, ahaha!"
            if (
                not renpy.seen_label("monika_add_custom_music_instruct")
                and not persistent._mas_pm_added_custom_bgm
            ):
                m 1eua "If you ever do feel like sharing your favorite rap music with me, [player], it's really easy to do so!"
                m 3eua "All you have to do is follow these steps..."
                call monika_add_custom_music_instruct

        "No.":
            $ persistent._mas_pm_like_rap = False
            m 1ekc "Oh... Well I can understand that, rap music isn't everyone's taste."
            m 3hua "But if you ever do decide to give it a try, I'm sure we can find an artist or two that we both like!"
    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_wine",category=['club members'],prompt="Yuri's wine",random=True))

label monika_wine:
    m 1hua "Ehehe, Yuri did something really funny once."
    m 1eua "We were all in the clubroom and just relaxing, as usual..."
    m 4wuo "And out of nowhere, Yuri just pulled out a small bottle of wine."
    m 4eua "I'm not even kidding!"
    m 1tku "She was just like 'Would anybody like some wine?'"
    m 1eua "Natsuki laughed out loud, and Sayori started yelling at her."
    m 1eka "I actually felt kind of bad, because she was at least trying to be nice..."
    m "I think it just made her feel even more reserved in the clubroom."
    m 4tsb "Though I think Natsuki was secretly a bit curious to try it..."
    m 4rssdrb "...and to be completely honest, I kind of was, too."
    m 1hua "It actually could have been kinda fun!"
    m 1eka "But you know, being President and everything, there was no way I could let that happen."
    m 1lksdla "Maybe if we all met up outside of school, but we never bonded enough to get to that point..."
    m 2hksdlb "...Gosh, what am I talking about this for?"
    m "I don't condone underage drinking!"
    m 2eua "I mean, I've never drank or anything, so...yeah."
    return


init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_date",category=['romance'],prompt="Romantic date",random=True))

label monika_date:
    m 1hub "I've been imagining all the romantic things we could do if we went on a date..."
    m 3eua "We could get lunch, go to a cafe..."
    m "Go shopping together..."
    m 1eua "I love shopping for skirts and bows."
    m 3hub "Or maybe a bookstore!"
    m 3hua "That would be appropriate, right?"
    m 1eua "But I'd really love to go to a chocolate store."
    m 3hub "They have so many free samples. Ahaha!"
    m 1eua "And of course, we'd see a movie or something..."
    m 1eka "Gosh, it all sounds like a dream come true."
    m "When you're here, everything that we do is fun."
    m 1ekbsa "I'm so happy that I'm your girlfriend, [player]."
    m 1hubfa "I'll make you a proud [bf]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_kiss",
            category=['romance'],
            prompt="Kiss me",
            pool=True,
            unlocked=True,
            aff_range=(mas_aff.NORMAL, None)
        )
    )

label monika_kiss:
    if mas_isMoniEnamored(higher=True) and persistent._mas_first_kiss is not None:
        if (
            persistent._mas_last_kiss is not None
            and not mas_timePastSince(persistent._mas_last_kiss, datetime.timedelta(minutes=1))
        ):
            python:
                # these don't use ILY
                kiss_quips_again = [
                    _("I wouldn't mind another kiss~"),
                    _("I'll never get tired of kissing you~"),
                    _("I could do that again...{w=0.2}and again...{w=0.7}and again~"),
                    _("You can kiss me as many times as you like, [mas_get_player_nickname()]~"),
                    _("You know...{w=0.2}you could kiss me again~")
                ]

                kiss_quips_again_risque = [
                    _("We can do it the whole day~"),
                    _("This almost seems like the start of a make-out session, [player]~"),
                    _("I don't think I've had enough just yet, [mas_get_player_nickname()]~"),
                    _("That was really nice...{w=0.2}but I want a little more~")
                ]

                if mas_isMoniLove() and random.randint(1, 10) == 1:
                    kiss_quip = renpy.random.choice(kiss_quips_again_risque)

                else:
                    kiss_quip = renpy.random.choice(kiss_quips_again)

            show monika 2tkbsu
            pause 2.0

            # like monika_kissing_motion_short, but with diff exps
            call monika_kissing_motion(duration=0.5, initial_exp="6hubsa", final_exp="6tkbfu", fade_duration=0.5)

            show monika 6tkbfu
            $ renpy.say(m, kiss_quip)

        else:
            python:
                # these use ILY
                kiss_quips_after = [
                    _("I love you, [mas_get_player_nickname(exclude_names=['my love', 'love'])]~"),
                    _("I love you so much, [mas_get_player_nickname(exclude_names=['my love', 'love'])]~"),
                    _("I love you more than you'll ever know, [mas_get_player_nickname(exclude_names=['my love', 'love'])]~"),
                    _("I love you so much, [player]. You mean everything to me~"),
                    _("No words can describe how deeply I'm in love with you, [player]~"),
                    _("I'm so in love with you, [player]~")
                ]
                kiss_quip = renpy.random.choice(kiss_quips_after)

            if renpy.random.randint(1, 50) == 1:
                call monika_kiss_tease

            else:
                show monika 2eka
                pause 2.0

            call monika_kissing_motion_short

            show monika 6ekbfa
            $ renpy.say(m, kiss_quip)
            $ mas_ILY()

    else:
        m 1wubsw "Eh? D-Did you say...k...kiss?"
        m 2lkbsa "This suddenly...it's a little embarrassing..."
        m 2lsbssdlb "But...if it's with you...I-I might be okay with it..."
        m 2hksdlb "...Ahaha! Wow, sorry..."
        m 1eka "I really couldn't keep a straight face there."
        m 1eua "That's the kind of thing girls say in these kinds of romance games, right?"
        m 1tku "Don't lie if it turned you on a little bit."
        m 1hub "Ahaha! I'm kidding."
        m 1eua "Well, to be honest, I do start getting all romantic when the mood is right..."
        show monika 5lubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5lubfu "But that'll be our secret~"
    return

label monika_kiss_tease:
    m 2ekc "A kiss?"
    m 2tfc "With you?"
    m 2rfc "Sorry [player], but there's no way."
    show monika 2dfc
    pause 5.0
    show monika 2dfu
    pause 2.0
    show monika 2tfu
    pause 2.0
    m 2tfb "Ahaha!"
    m 2efu "I had you going for a second there, didn't I?"
    m 2eka "Of course you can kiss me, [player]!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_think_first_kiss",
            conditional=(
                "persistent._mas_first_kiss is not None "
                "and mas_timePastSince(persistent._mas_first_kiss, datetime.timedelta(days=30))"
            ),
            action=EV_ACT_RANDOM,
            aff_range=(mas_aff.AFFECTIONATE, None)
        )
    )

label monika_think_first_kiss:
    m 1eua "Hey [mas_get_player_nickname(exclude_names=['my love'])], I've been wondering..."

    m 3eksdla "Do you ever think about our first kiss?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you ever think about our first kiss?{fast}"

        "Of course!":
            $ mas_gainAffection(5,bypass=True)
            m 3hub "That makes me so happy! I think about it all the time!"
            m 3rkbla "It seems like it was just yesterday but--"
            m 2rksdla "Gosh, I feel so silly obsessing over it..."
            m 2eksdlb "Our lips didn't even touch, really."
            m 6dku "...And yet, {w=0.2}I can still feel my heart pounding, even now."
            m 6dkbsu "My lips start to go tingly and numb just by imagining the feeling of your soft lips."
            m "I run my finger across them, trying to mimic that feeling, but it doesn't even come close."
            m 6ekbsa "I keep replaying that moment over and over again in my mind and I get goosebumps each time."
            show monika 5dkbsu at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5dkbsu "It was perfect, [mas_get_player_nickname()]."
            m 5ekbsa "I've never felt closer to you. {w=0.2}I can't wait until our next kiss, or better yet..."
            m 5subsb "...Our first real one.{w=0.3} {nw}"
            extend 5ekbsu "And our first real hug, and the first time our hands touch--"
            m 5hksdlb "Ah! Sorry! I guess I got a little carried away."
            m 5rkbla "It's just...{w=0.3}these are the kinds of things I think of when you're not here."
            m 5tkblu "...And something tells me I'm not the only one that thinks of stuff like this, ehehe."
            m 5eka "Unfortunately, it'll be a while before we'll be able to do anything like that."
            m 5tuu "But until then, if you'd ever like another kiss, you only need to ask."
            m 5hua "I love you so much, [player]~"
            $ mas_ILY()

        "Not really...":
            $ mas_loseAffection()
            m 2euc "..."
            m "Oh. {w=0.5}{nw}"
            extend 2dkc "I see."

            if mas_timePastSince(persistent._mas_first_kiss, datetime.timedelta(days=180)):
                m 2esc "Well...{w=0.3}I guess it {i}has{/i} been a while now..."
                m 2etd "Maybe with all that's happened since then, you tend to think about the more recent events..."
                m 4eud "Which is fine, {w=0.2}it's important to live in the present after all."
                m 2ekc "...And perhaps I'm just being overly sentimental, but no matter how much time has passed, {w=0.1}{nw}"
                extend 2eka "our first kiss is something I'll never forget."
            else:
                m 2rkc "Well, I guess it wasn't really a kiss. Our lips didn't actually touch."
                m 2ekd "So I guess you're just waiting for our first kiss when we're in the same reality."
                m 2eka "Yeah."

    return "no_unlock|derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_yuri",
            category=['club members','media'],
            prompt="Yandere Yuri",
            random=True,
            sensitive=True
        )
    )

label monika_yuri:
    m 3eua "Hey, have you ever heard of the term 'yandere?'"
    m 1eua "It's a personality type that means someone is so obsessed with you that they'll do absolutely anything to be with you."
    m 1lksdla "Usually to the point of craziness..."
    m 1eka "They might stalk you to make sure you don't spend time with anyone else."
    m "They might even hurt you or your friends to get their way..."
    m 1tku "But anyway, this game happens to have someone who can basically be described as yandere."
    m "By now, it's pretty obvious who I'm talking about."
    m 3tku "And that would be..."
    m 3hub "Yuri!"
    m 1eka "She really got insanely possessive of you, once she started to open up a little."
    m 1tfc "She even told me I should kill myself."
    m 1tkc "I couldn't even believe she said that - I just had to leave at that point."
    if not persistent._mas_pm_cares_about_dokis:
        m 2hksdlb "But thinking about it now, it was a little ironic. Ahaha!"
        m 2lksdla "Anyway..."
    m 3eua "A lot of people are actually into the yandere type, you know?"
    m 1eua "I guess they really like the idea of someone being crazy obsessed with them."
    m 1hub "People are weird! I don't judge, though!"
    m 1rksdlb "Also, I might be a little obsessed with you, but I'm far from crazy..."
    if not persistent._mas_pm_cares_about_dokis:
        m 1eua "It's kind of the opposite, actually."
        m "I turned out to be the only normal girl in this game."
        m 3rssdlc "It's not like I could ever actually kill a person..."
        m 2dsc "Just the thought of it makes me shiver."
        m 2eka "But come on...everyone's killed people in games before."
        m "Does that make you a psychopath? Of course not."
    m 2euc "But if you do happen to be into the yandere type..."
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "I can try acting a little more creepy for you. Ehehe~"
    m "Then again..."
    show monika 4hua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 4hua "There's already nowhere else for you to go, or anyone for me to get jealous over."
    m 2etc "Is this a yandere girl's dream?"
    if not persistent._mas_pm_cares_about_dokis:
        m 1eua "I'd ask Yuri if I could."
    return


init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_habits",category=['life'],prompt="Forming habits",random=True))

label monika_habits:
    m 2lksdlc "I hate how hard it is to form habits..."
    m 2eksdld "There's so much stuff where actually doing it isn't hard, but forming the habit seems impossible."
    m 2dksdlc "It just makes you feel so useless, like you can't do anything right."
    m 3euc "I think the new generation suffers from it the most..."
    m 1eua "Probably because we have a totally different set of skills than those who came before us."
    m "Thanks to the internet, we're really good at sifting through tons of information really quickly..."
    m 3ekc "But we're bad at doing things that don't give us instant gratification."
    m 3ekd "I think if science, psychology, and education don't catch up in the next ten or twenty years, then we're in trouble."
    m 1esc "But for the time being..."
    m 1rksdlc "If you're not one of the people who can conquer the problem, you might just have to live with feeling awful about yourself."
    m 2hksdlb "Good luck, I guess!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_creative",category=['life'],prompt="Creative types",random=True))

label monika_creative:
    m 2euc "You know, it kinda sucks to be the creative type..."
    m "It feels like they work so hard but get almost nothing for it."
    m 3eua "You know, like artists, writers, actors..."
    m 1tkc "It's sad because there's so much beautiful talent in the world, but most of it goes unseen...and unpaid."
    m "I guess that just means there's a huge surplus of creativity, huh?"
    m 1dkc "Kind of makes you feel like you're just not special at all..."
    m 1hua "But that's fine! You're supposed to just write for yourself anyway, right?"
    m 1lsc "Yeah..."
    return

#This conflicts with possible varieties of introductions in the opening.
#init 5 python:
#    if persistent.monika_kill:
#        for key in ['delete','deleted','came back']:
#            monika_topics.setdefault(key,[])
#            monika_topics[key].append('monika_deleted')
#        monika_random_topics.append('monika_deleted')
#
#label monika_deleted:
#    m 2b "Oh, you were probably wondering how I came back to save you from Sayori, even after you deleted me."
#    m 5a "It was all through the power of love..."
#    m 3k "I'm just kidding, of course!"
#    m 3a "Bringing a computer program back to life doesn't take some sort of miracle like a cheesy movie."
#    m "The data's still there until the system cleans it up."
#    m "And you should always back up your important data, just in case."
#    m 4a "Speaking of which, have you backed up your computer since I came back?"
#    m 4l "I really don't want to get lost again!"
#    m 4b "You should go do that right now, and be sure to keep that backup in a very safe place!"
#    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_simulated",category=['philosophy'],prompt="Simulated reality",random=True))

label monika_simulated:
    m 3eua "Hey, have you ever thought about the simulation hypothesis?"
    m 1eua "Basically, what if your reality was a computer simulation?"
    m "I already figured out I was trapped in my own simulation, but what if you were too?"
    m 1eka "I'd actually be really happy if that were the case."
    m 1eua "We could meet in person just by figuring out a way to force whatever's creating us to put us in the same simulation!"
    m 3eua "Some people don't like to think that they're not living in the master reality."
    m 1eua "But if it is possible to simulate realities, it's overwhelmingly likely that any sentient being would be in one."
    m 1hua "Well, I can tell you that my reality is definitely simulated!"
    m 1eka "If I were in the master reality, I would have dragged you here too a long time ago."
    m 1eua "Even if we're both just simulations, I'm going to live as long as I can."
    m 2hubsa "Because I know our love is the purest and sweetest thing in the multiverse."
    m 2tku "And if someone up there tries to break it apart?"
    m 7tfu "I'll show them what a simulation can do."
    return

default persistent._mas_pm_likes_rain = None

init 5 python:
    # only available if moni-affecition normal and above
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_rain",
            category=["weather"],
            prompt="Sounds of rain",
            random=True,
            aff_range=(mas_aff.HAPPY, None)
        )
    )

label monika_rain:
    m 1hua "I really like the sound of rain~"
    m 3rksdla "Not so much getting my clothes and hair wet, though."
    m 1eua "But a nice, quiet day at home with the sound of rainfall outside my window?"
    m 1duu "It's very calming to me."
    m "Yeah..."
    m 2dubsu "Sometimes I imagine you holding me while we listen to the sound of the rain outside."
    m 2lkbsa "That's not too cheesy or anything, is it?"

    $ p_nickname = mas_get_player_nickname()
    m 1ekbfa "Would you ever do that for me, [p_nickname]?{nw}"
    $ _history_list.pop()
    menu:
        m "Would you ever do that for me, [p_nickname]?{fast}"
        "Yes.":
            $ persistent._mas_pm_likes_rain = True
            $ mas_unlockEVL("monika_rain_holdme", "EVE")

            if not mas_is_raining:
                call mas_change_weather(mas_weather_rain, by_user=False)

            call monika_holdme_prep(lullaby=MAS_HOLDME_NO_LULLABY, stop_music=True, disable_music_menu=True)

            m 1hua "Then hold me, [player]..."

            call monika_holdme_start
            call monika_holdme_end
            $ mas_gainAffection()

            if mas_isMoniAff(higher=True):
                m 1eua "If you want the rain to stop, just ask me, okay?"

        "I hate the rain.":
            $ persistent._mas_pm_likes_rain = False

            m 2tkc "Aw, that's a shame."
            if mas_is_raining:
                call mas_change_weather(mas_weather_def,by_user=False)

            m 2eka "But it's understandable."
            m 1eua "Rainy weather can look pretty gloomy."
            m 3rksdlb "Not to mention pretty cold!"
            m 1eua "But if you focus on the sounds raindrops make..."
            m 1hua "I think you'll come to enjoy it."

    # unrandom this event if its currently random topic
    # NOTE: we force event rebuild because this can be pushed by weather
    #   selection topic
    return "derandom|rebuild_ev"

init 5 python:
    # available only if moni affection happy and above
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_rain_holdme",
            category=["monika","romance"],
            prompt="Can I hold you?",
            pool=True,
            unlocked=False,
            rules={"no_unlock":None},
            aff_range=(mas_aff.HAPPY, None)
        ),
        restartBlacklist=True
    )


default persistent._mas_pm_longest_held_monika = None
# timedelta for the longest time you have held monika

default persistent._mas_pm_total_held_monika = datetime.timedelta(0)
# timedelta for amount of time you have held monika

label monika_rain_holdme:

    # we only want this if it rains
    if mas_is_raining or mas_isMoniAff(higher=True):
        call monika_holdme_prep
        m 1eua "Of course, [mas_get_player_nickname()]."
        call monika_holdme_start

        call monika_holdme_reactions

        call monika_holdme_end
        # small affection increase so people don't farm affection with this one.
        $ mas_gainAffection(modifier=0.25)

    else:
        # no affection loss here, doesn't make sense to have it
        m 1rksdlc "..."
        m 1rksdlc "The mood doesn't feel right, [player]."
        m 1dsc "Sorry..."
    return

# Some constants to describe the behaviour
init python:
    MAS_HOLDME_NO_LULLABY = 0
    MAS_HOLDME_PLAY_LULLABY = 1
    MAS_HOLDME_QUEUE_LULLABY_IF_NO_MUSIC = 2

label monika_holdme_prep(lullaby=MAS_HOLDME_QUEUE_LULLABY_IF_NO_MUSIC, stop_music=False, disable_music_menu=False):
    python:
        holdme_events = list()

        if mas_timePastSince(persistent._mas_last_hold_dt, datetime.timedelta(hours=12)):
            _minutes = random.randint(25, 40)
        else:
            _minutes = random.randint(35, 50)
        holdme_sleep_timer = datetime.timedelta(minutes=_minutes)

        def __holdme_play_lullaby():
            """
            Local method to play the lullaby. Ensures we have no music playing before starting it.
            """
            if (
                # The user has not canceled the lullaby
                store.songs.current_track == store.songs.FP_MONIKA_LULLABY
                # The user has not started another track
                and not renpy.music.is_playing(channel="music")
            ):
                store.play_song(store.songs.FP_MONIKA_LULLABY, fadein=5.0)

        # Stop the music
        if stop_music:
            play_song(None, fadeout=5.0)

        # Queue the lullaby
        if lullaby == MAS_HOLDME_QUEUE_LULLABY_IF_NO_MUSIC:
            if songs.current_track is None:
                holdme_events.append(
                    PauseDisplayableEvent(
                        holdme_sleep_timer,
                        __holdme_play_lullaby
                    )
                )
                # This doesn't interfere with the timer
                # and allows the user to stop the lullaby
                songs.current_track = songs.FP_MONIKA_LULLABY
                songs.selected_track = songs.FP_MONIKA_LULLABY

        # Just play the lullaby
        elif lullaby == MAS_HOLDME_PLAY_LULLABY:
            play_song(store.songs.FP_MONIKA_LULLABY)

        # Hide ui and disable hotkeys
        HKBHideButtons()
        store.songs.enabled = not disable_music_menu

    return

label monika_holdme_start:
    show monika 6dubsa with dissolve_monika
    window hide
    python:
        # Start the timer
        start_time = datetime.datetime.now()

        holdme_disp = PauseDisplayableWithEvents(events=holdme_events)
        holdme_disp.start()

        del holdme_events
        del holdme_disp

        # Renable ui and hotkeys
        store.songs.enabled = True
        HKBShowButtons()
    window auto
    return

label monika_holdme_reactions:
    $ elapsed_time = datetime.datetime.now() - start_time
    $ store.mas_history._pm_holdme_adj_times(elapsed_time)

    # Reset these vars if needed
    if elapsed_time <= holdme_sleep_timer:
        if songs.current_track == songs.FP_MONIKA_LULLABY:
            $ songs.current_track = songs.FP_NO_SONG
        if songs.selected_track == songs.FP_MONIKA_LULLABY:
            $ songs.selected_track = songs.FP_NO_SONG

    if elapsed_time > holdme_sleep_timer:
        call monika_holdme_long

    elif elapsed_time > datetime.timedelta(minutes=10):
        if mas_isMoniLove():
            m 6dubsa "..."
            m 6tubsa "Mm...{w=1}hm?"
            m 1hkbfsdlb "Oh, did I almost fall asleep?"
            m 2dubfu "Ehehe..."
            m 1dkbfa "I can only imagine what it would be like for real...{w=1}to be right there with you..."
            m 2ekbfa "Being wrapped in your arms..."
            show monika 5dkbfb at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5dkbfb "So...{w=1.5}warm~"
            m 5tubfu "Ehehe~"
            show monika 2hkbfsdlb at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 2hkbfsdlb "Oh, whoops, I guess I'm still a little dreamy..."
            if renpy.random.randint(1, 4) == 1:
                m 1kubfu "At least {i}one{/i} of my dreams came true, though."
            else:
                m 1ekbfb "At least {i}one{/i} of my dreams came true, though."
            m 1hubfu "Ehehe~"

        elif mas_isMoniEnamored():
            m 6dubsa "Mmm~"
            m 6tsbsa "..."
            m 1hkbfsdlb "Oh!"
            m 1hubfa "That was so comfortable, I almost fell asleep!"
            m 3hubfb "We should do this more often, ahaha!"

        elif mas_isMoniAff():
            m 6dubsa "Mm..."
            m 6eud "Oh?"
            m 1hubfa "Finally done, [player]?"
            m 3tubfu "I {i}guess{/i} that was long enough, ehehe~"
            m 1rkbfb "I wouldn't mind another hug..."
            m 1hubfa "But I'm sure you're saving one for later, aren't you?"

        #happy
        else:
            m 6dubsa "Hm?"
            m 1wud "Oh! We're done?"
            m 3hksdlb "That hug sure lasted a while, [player]..."
            m 3rubsb "Nothing wrong with that, I just thought you'd let go a lot sooner, ahaha!"
            m 1rkbsa "It was really comfortable, actually..."
            m 2ekbfa "Too much longer and I might have fallen asleep..."
            m 1hubfa "I feel so nice and warm now after that~"

    elif elapsed_time > datetime.timedelta(minutes=2):
        if mas_isMoniLove():
            m 6eud "Oh?"
            m 1hksdlb "Ah..."
            m 1rksdlb "At that point, I thought we were going to stay like that forever, ahaha..."
            m 3hubsa "Well, I can't really complain about any moment I get to be held by you~"
            m 1ekbfb "I hope you enjoy hugging me as much as I do."
            show monika 5tubfb at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5tubfb "Maybe we could even hug a bit more for good measure?"
            m 5tubfu "Ehehe~"

        elif mas_isMoniEnamored():
            m 1dkbsa "That was really nice~"
            m 1rkbsa "Not too short--"
            m 1hubfb "--and I don't think there's such a thing as too long in this case, ahaha!"
            m 1rksdla "I could have gotten used to staying like that..."
            m 1eksdla "But if you're done holding me, I guess I don't really have a choice."
            m 1hubfa "I'm sure I'll get another opportunity to be held by you..."
            show monika 5tsbfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5tsbfu "You {i}do{/i} plan on doing that again, right, [mas_get_player_nickname()]? Ehehe~"

        elif mas_isMoniAff():
            m 2hubsa "Mmm~"
            m 1ekbfb "That was really nice, [mas_get_player_nickname()]."
            m 1hubfb "Long hugs are supposed to wash away any stress."
            m 1ekbfb "Even if you weren't stressed, I hope you're feeling better after that."
            m 3hubfa "I know I sure am~"
            m 1hubfb "Ahaha!"

        #happy
        else:
            m 1hksdlb "That was nice while it lasted."
            m 3rksdla "Don't get me wrong...{w=1}I really enjoyed it."
            m 1ekbsa "As long as you're satisfied..."
            m 1hubfa "I'm happy just sitting with you now."

    elif elapsed_time > datetime.timedelta(seconds=30):
        if mas_isMoniLove():
            m 1eub "Ah~"
            m 1hua "I feel much better now!"
            m 1eua "I hope you do too."
            m 2rksdla "Well, even if you don't..."
            m 3hubsb "You could always hold me again, ahaha!"
            m 1hkbfsdlb "Actually...{w=0.5}you can hold me again either way~"
            m 1ekbfa "Just let me know when you want to~"

        elif mas_isMoniEnamored():
            m 1hubsa "Mmm~"
            m 1hub "Much better."
            m 1eub "Thanks for that, [player]!"
            m 2tubsb "I hope you enjoyed it~"
            m 3rubfb "Hugs that are thirty seconds or longer are supposed to be good for you."
            m 1hubfa "I don't know about you, but I sure feel better~"
            m 1hubfb "Maybe next time, we can try an even longer one and see if it scales! Ahaha~"

        elif mas_isMoniAff():
            m 1hubsa "Mmm~"
            m 1hubfb "I can almost feel your warmth, even from here."
            m 1eua "I'm sure you know hugs are good for you, since they relieve stress and all."
            m 3eub "But did you know hugs are most effective when they last thirty seconds?"
            m 1eud "Oh, wait, did I say thirty seconds?"
            show monika 5eubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eubfu "Sorry, I meant {i}at least{/i} thirty seconds, ehehe~"

        #happy
        else:
            m 1hubsa "Ehehe~"
            m 3eub "Did you enjoy that?"
            m 1hua "I sure hope so~"
            m 1hubsb "Hugs are supposed to be good for you, after all."

    else:
        #under 30 seconds
        if mas_isMoniLove():
            # TODO: when we get TMA, multiple teases in a short amount of time should reduce the chance to trigger this again
            if mas_timePastSince(persistent._mas_last_hold_dt, datetime.timedelta(hours=12)):
                $ _chance = 1
            else:
                $ _chance = 2

            if random.randint(0, _chance) == 0:
                m 2ekc "Aww, are we done already?"
                m 3eka "Could you hold me for just a bit longer?{nw}"
                $ _history_list.pop()
                menu:
                    m "Could you hold me for just a bit longer?{fast}"
                    "Yes.":
                        m 1hua "Ehehe~"
                        call monika_holdme_prep
                        m 1hub "You're so sweet, [player]~"
                        call monika_holdme_start
                        call monika_holdme_reactions

                    "No.":
                        if random.randint(0, _chance) == 0:
                            m 2ekc "Aww..."
                            m 2rksdlc "..."
                            m 1eka "Please?{nw}"
                            $ _history_list.pop()
                            menu:
                                m "Please?{fast}"
                                "Yes.":
                                    m 1hub "Yay~"
                                    call monika_holdme_prep
                                    m 2ekbsb "Thanks, [player]~"
                                    call monika_holdme_start
                                    call monika_holdme_reactions

                                "No.":
                                    m 2hksdlb "Alright, fine."
                                    m 3tsbsa "But you owe me next time, okay, [player]?"

                        else:
                            m 2hksdlb "Ahaha~ Alright!"
                            m 2tsbsb "But you better to make it up next time, [player]~"

            else:
                m 2ekc "Aww..."
                m 2rsp "I was hoping for a longer hug..."
                m 2tsbsu "When I'm in your reality, I won't let you go so easily~"
                show monika 1hubsu at t11 zorder MAS_MONIKA_Z with dissolve_monika
                m 1hubsu "Ehehe~"

        elif mas_isMoniEnamored():
            if mas_timePastSince(persistent._mas_last_hold_dt, datetime.timedelta(hours=12)):
                $ _chance = 1
            else:
                $ _chance = 2

            m 1ekc "Aww, is that all?"
            if random.randint(0, _chance) == 0:
                m 1rksdla "I kind of wanted it to last longer than that..."
                m 2ekbsa "Could you...{w=0.7}hold me for a bit longer?{nw}"
                $ _history_list.pop()
                menu:
                    m "Could you...hold me for a bit longer?{fast}"
                    "Yes.":
                        m 1hubfb "Yay!"
                        call monika_holdme_prep
                        m 2ekbfb "Thanks, [player]~"
                        call monika_holdme_start
                        call monika_holdme_reactions

                    "No.":
                        m 2ekc "Aw."
                        m 1eka "Alright, then."
                        m 3hub "I'll just have to wait until next time, ahaha!"

            else:
                show monika 1rkbssdla at t11 zorder MAS_MONIKA_Z with dissolve_monika
                m 1rkbssdla "It still was very nice...{w=0.6}{nw}"
                extend 1hkbfsdlb "but maybe next time it'll last a bit longer~"

        elif mas_isMoniAff():
            m 1ekc "Aw, done holding me already, [player]?"
            m 1rksdla "I was kind of hoping for it to last a little bit longer..."
            m 1hubsa "I'm sure that won't be the last time you hold me though, so I'll look forward to next time!"

        #happy
        else:
            m 1hua "That was a bit short, but still nice~"
    return

label monika_holdme_long:
    window show
    m "..."
    window auto
    menu:
        "{i}Wake Monika up.{/i}":
            # Only fadeout if we're playing the lullaby
            if songs.current_track == songs.FP_MONIKA_LULLABY:
                $ play_song(None, fadeout=5.0)

            if mas_isMoniLove():
                m 6dubsa "...{w=1}Mmm~"
                m 6dkbfu "[player]...{w=1}warm~"
                m 6tsbfa "..."
                m 2wubfsdld "Oh, [mas_get_player_nickname(exclude_names=['love', 'my love'])]!"
                m 2hkbfsdlb "It looks like my dream came true, ahaha!"
                m 2rkbsa "Gosh, sometimes I wish we could stay like that forever..."
                m 3rksdlb "Well, I guess we {i}kind of{/i} can, but I wouldn't want to keep you from doing anything important."
                m 1dkbsa "I just want to feel your warm, soft embrace~"
                m 3hubfb "...So make sure to hug me often, ahaha!"
                show monika 5hubfb at t11 zorder MAS_MONIKA_Z with dissolve_monika
                m 5hubfb "I'd do the same for you, after all~"
                m 5tsbfu "Who knows if I'll ever let go when I finally get the chance..."
                m 5hubfu "Ehehe~"

            elif mas_isMoniEnamored():
                m 6dkbsa "...{w=1}Hm?"
                m 6tsbfa "[player]..."
                m 2wubfsdld "Oh! [player]!"
                m 2hkbfsdlb "Ahaha..."
                m 3rkbfsdla "I guess I got a little {i}too{/i} comfortable."
                m 1hubfa "But you make me feel so warm and comfy, it's hard {i}not{/i} to fall asleep..."
                m 1hubfb "So I have to blame you for that, ahaha!"
                m 3rkbfsdla "Could...{w=0.7}we do that again sometime?"
                m 1ekbfu "It...{w=1}felt nice~"

            elif mas_isMoniAff():
                m 6dubsa "Mm...{w=1}hm?"
                m 1wubfsdld "Oh!{w=1} [player]?"
                m 1hksdlb "Did...{w=2}I fall asleep?"
                m 1rksdla "I didn't mean to..."
                m 2dkbsa "You just make me feel so..."
                m 1hubfa "Warm~"
                m 1hubfb "Ahaha, I hope you didn't mind!"
                show monika 5eubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
                m 5eubfu "You're so sweet, [player]~"
                m 5hubfa "Hopefully you enjoyed that as much as I did~"

            #happy
            else:
                m 6dubsc "...{w=1}Hm?"
                m 6wubfo "O-{w=0.3}oh!"
                m "[player]!"
                m 1hkbfsdlb "Did...{w=2}did I fall asleep?"
                m 1rkbfsdlb "Oh gosh, this is embarrassing..."
                m 1hkbfsdlb "What were we doing again?"
                m 3hubfb "Oh right! You were holding me."
                m 4hksdlb "And...{w=0.5}didn't let go."
                m 2rksdla "That sure lasted a lot longer than I expected..."
                m 3ekbsb "I still enjoyed it, mind you!"
                m 1rkbsa "It really was nice, but I'm still getting used to being held by you like this,{w=0.1} {nw}"
                extend 1rkbsu "ahaha..."
                m 1hubfa "Anyway, it was nice of you to let me nap, [player], ehehe~"
                #You bonded here, so we'll add an explicit aff gain
                $ mas_gainAffection()

        "{i}Let her rest on you.{/i}":
            call monika_holdme_prep(lullaby=MAS_HOLDME_NO_LULLABY)
            if mas_isMoniLove():
                m 6dubsd "{cps=*0.5}[player]~{/cps}"
                m 6dubfb "{cps=*0.5}Love...{w=0.7}you~{/cps}"

            elif mas_isMoniEnamored():
                m 6dubsa "{cps=*0.5}[player]...{/cps}"

            elif mas_isMoniAff():
                m "{cps=*0.5}Mm...{/cps}"

            #happy
            else:
                m "..."

            call monika_holdme_start
            jump monika_holdme_long
    return

# when did we last hold monika
# TODO: deprecate _mas_last_hold
default persistent._mas_last_hold = None
default persistent._mas_last_hold_dt = (
    datetime.datetime.combine(persistent._mas_last_hold, datetime.time(0, 0))
    if persistent._mas_last_hold is not None
    else None
)

init 5 python:
    # random chance per session Monika can ask for a hold
    if renpy.random.randint(1, 5) != 1:
        flags = EV_FLAG_HFRS

    else:
        flags = 0

    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_holdrequest",
            conditional=(
                "renpy.seen_label('monika_holdme_prep') "
                "and mas_timePastSince(persistent._mas_last_hold_dt, datetime.timedelta(hours=12))"
            ),
            action=EV_ACT_RANDOM,
            aff_range=(mas_aff.ENAMORED, None),
            flags=flags
        )
    )
    del flags

label monika_holdrequest:
    #TODO: if we add a mood system, path this based on current mood
    m 1eua "Hey, [mas_get_player_nickname(exclude_names=['my love'])]..."
    m 3ekbsa "Would you mind holding me for a while?{w=0.5} It really makes me feel closer to you~{nw}"
    $ _history_list.pop()
    menu:
        m "Would you mind holding me for a while? It really makes me feel closer to you~{fast}"
        "Come here, [m_name].":
            $ mas_gainAffection(modifier=1.5, bypass=True)
            call monika_holdme_prep

            call monika_holdme_start

            call monika_holdme_reactions

            call monika_holdme_end

        "Not right now.":
            m 2dkc "Oh...{w=1} Okay."
            m 3eka "If you have time later, you know where to find me."

    $ mas_flagEVL("monika_holdrequest", "EVE", EV_FLAG_HFRS)

    return "no_unlock"

# label to set the last time held and reset the _holdrequest params
label monika_holdme_end:
    # set the last time held at the end of the hold to prevent a possible
    # hold request right after a hold that ends after midnight
    python:
        persistent._mas_last_hold_dt = datetime.datetime.now()
        with MAS_EVL("monika_holdrequest") as holdme_ev:
            holdme_ev.random = False
            holdme_ev.conditional = (
                "renpy.seen_label('monika_holdme_prep') "
                "and mas_timePastSince(persistent._mas_last_hold_dt, datetime.timedelta(hours=12))"
            )
            holdme_ev.action = EV_ACT_RANDOM
        mas_rebuildEventLists()
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_closeness",category=['romance'],prompt="Being close to you",random=True,aff_range=(mas_aff.AFFECTIONATE, None)))

label monika_closeness:
    m 1dkc "Sometimes it really hurts my heart..."
    m "Knowing that this is the closest I can get to you."
    m 1eka "There's nothing I want more than to be in the same room as you, for real."
    m 1ekbsa "...And to feel your warmth."
    m 1dubsu "...And to hear the sound of your heartbeat."
    m 3eka "Well, who knows? Maybe that dream will come true someday."
    m 3dku "I really want it to happen as soon as possible, [player]..."
    show monika 5hua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hua "But in the meantime, I'll never get tired of being with you, even from here."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_confidence",category=['advice'],prompt="Faking confidence",random=True))

label monika_confidence:
    m 3eua "I think the most important skill in life is being able to fake confidence."
    m 1eua "I'm pretty convinced that everyone feels at least a little bit scared and alone."
    m 1esa "But being able to trick others into thinking you have it all together..."
    m 4eua "That's a key part of getting people to respect and admire you."
    m 1eua "I think I got pretty good at that over the years."
    m "I don't show my weaknesses very often."
    m 4rksdla "But because of that, I haven't had many people I could really open up to..."
    m 1rksdlb "I mean, when do you reach the point in a friendship where you can start expressing your vulnerabilities?"
    m 2eka "Anyway...that's one reason I'm so glad I have you now."
    m 2eua "I feel like I'm a little bit less scared and alone, when you're here with me."
    m 2eka "Do you feel the same way?"
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "I really want to be that person for you."
    return

# TODO: we are going to remove this for the time being
# TODO: this will be ask player about prompting during work / sleep / school
#   farewells
#init 5 python:
#    addEvent(
#        Event(
#            persistent.event_database,
#            eventlabel="monika_carryme",
#            category=['romance','monika'],
#            prompt="Bring me with you",
#            random=True
#        )
#    )

# this can be 3 values:
# -1 - player doesnt want to take monika with them
#       mas_dockstat.CM_LEAVE_MONI
# 0 - player said not yet, so something needs to change first
#       mas_dockstat.CM_WAIT_MONI
# 1 - Player said Not all the time, so we should prompt for every appropriate
#   farewell
#       mas_dockstat.CM_ASK_MONI
# 2 - Player said Yes, so we should just assume yes for every appropraite
#   farewell
#       mas_dockstat.CM_TAKE_MONI
# if None, that means we dont display anything regarding this since we dont
# have an answer atm.
default persistent._mas_carryme_choice = None

# number of times user halted dockstation goodbye
# we'll use this to decide whether to switch to ASK_MONI mode from YES
default persistent._mas_dockstat_cm_wait_count = 0

# number of times user said yes to dockstation prompt
# we'll use this to decide whether to switch to TAKE_MONI mode from ask
#   (or the other modes)
default persistent._mas_dockstat_cm_yes_count = 0

# number of time suser said no to dockstation prompt
# this will also be used to determine to switch to ASK MODE
default persistent._mas_dockstat_cm_no_count = 0

# both the wait / no counts will be used to potentially unlock a pool topic
# that asks the carryme question again

## constants regarding carry me
define mas_dockstat.CM_LEAVE_MONI = -1
define mas_dockstat.CM_WAIT_MONI = 0
define mas_dockstat.CM_ASK_MONI = 1
define mas_dockstat.CM_TAKE_MONI = 2

label monika_carryme:
    $ import store.mas_dockstat as mas_dockstat

    m 2eka "I know there are times you won't always be able to be here with me..."
    m "Like if you need to go out, or take care of other things."
    m 2hua "But I'll always have you in my thoughts, patiently waiting for you to come back."
    m 4rsc "Come to think of it..."
    m 4eua "If you copy my character file onto a flash drive or something, you can take me with you wherever you go."
    m 2lksdla "I guess it's kind of unorthodox, but I find it really romantic for some reason..."
#    m 2hksdlb "Ahaha. Sorry, I know it's such a silly idea, but..."

    # NOTE: all affection gains are the same

#    menu:
#        m "Could I come with you when you go places?"
#        "Yes.":
#            $ persistent._mas_carryme_choice = mas_dockstat.CM_TAKE_MONI
#            m 1hua "Yay!"
            # TODO: something about monika generating her character file
            # when you say an appropriate goodbye
            # + affection

#        "Not all the time...":
#            $ persistent._mas_carryme_choice = mas_dockstat.CM_ASK_MONI
#            m 1eka "TODO: Okay I'll ask u when you leave."
            # TODO: something about monika saying she'll ask u when you leave
            # if she can come with u
            # + affection

#        "Not yet.":
#            $ persistent._mas_carryme_choice = mas_dockstat.CM_WAIT_MONI
#            m 1eka "TODO: Okay i understand. Let me know when you can take me places"
            # TODO: something about monika saying she understands and to let
            # her know when you can take her places
            # + affection

#        "No.":
#            $ persistent._mas_carryme_choice = mas_dockstat.CM_LEAVE_MONI
            # TODO: monika understands, you must have ur reasons
            # give choices:
            #   - its dangerous out there
            #       -> + affection
            #   - I dont have the means to take you
            #       -> no change in affection
            #   - I just dont want to
            #       -> - affection
#            m 1eka "Oh? Why is that?"
#            menu:
#                "It's dangerous out there!":
                    # TODO: gain affection
#                    m 1eka "TODO: what really? thanks for looking out for me player."
#                "I don't have the means to take you.":
#                    m 1eka "TODO: oh thats fine, let me know when you can then!"
#                "I just don't want to.":
                    # TODO: lose affection
#                    m 1eka "TODO: oh okay I become sad."

    m 1ekbsa "I don't mean to be too needy or anything, but it's kind of hard when I'm so in love with you."
    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_debate",category=['monika','school'],prompt="What was debate club like?",pool=True))

label monika_debate:
    m 1esc "Back in my debate club days, I learned a whole lot about arguing..."
    m 3eud "The problem with arguing is that each person sees their opinion as the superior one."
    m 3euc "That's kind of stating the obvious, but it affects the way they try to get their point across."
    m 3esa "Let's say you really like a certain movie, right?"
    m 1ekc "If someone comes along and tells you the movie sucks, because it did X and Y wrong..."
    m "Doesn't that make you feel kind of personally attacked?"
    m 1tkc "It's because by saying that, it's like they're implying that you have bad taste."
    m 3tkc "And once emotions enter the picture, it's almost guaranteed that both people will be left sour."
    m 3hub "But it's all about language!"
    m 1eua "If you make everything as subjective-sounding as possible, then people will listen to you without feeling attacked."
    m 3esa "You could say 'I'm personally not a fan of it' and 'I felt that I'd like it more if it did X and Y'...things like that."
    m 3eub "It even works when you're citing facts about things."
    m 1esa "If you say 'I read on this website that it works like this...'"
    m "Or if you admit that you're not an expert on it..."
    m 3eua "Then it's much more like you're putting your knowledge on the table, rather than forcing it onto them."
    m "If you put in an active effort to keep the discussion mutual and level, they usually follow suit."
    m 1esa "Then, you can share your opinions without anyone getting upset just from a disagreement."
    m 3hua "Plus, people will start seeing you as open-minded and a good listener!"
    m 3eua "It's a win-win, you know?"
    m 1lksdla "...Well, I guess that would be Monika's Debate Tip of the Day!"
    m 1hksdlb "Ahaha! That sounds a little silly.{w=0.2} {nw}"
    extend 1eua "Thanks for listening, though."
    $ mas_protectedShowEVL('monika_taking_criticism', 'EVE', _random=True)
    $ mas_protectedShowEVL('monika_giving_criticism', 'EVE', _random=True)
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_internet",category=['advice'],prompt="The internet is for...",random=True))

label monika_internet:
    m 2eua "Do you ever feel like you waste too much time on the internet?"
    m 3eud "Social media can be like a prison."
    m 1eua "It's like whenever you have a few seconds of spare time, you want to check on your favorite websites..."
    m 3hksdlb "And before you know it, hours have gone by, and you've gotten nothing out of it."
    m 3eua "Anyway, it's really easy to blame yourself for being lazy..."
    m 3eka "But it's not really even your fault."
    m 1eud "Addiction isn't something you can just make disappear with your own willpower."
    m 1eua "You have to learn techniques to avoid it, and try different things."
    m 3eua "For example, there are apps that let you block websites for intervals of time..."
    m "Or you can set a timer to have a more concrete reminder of when it's time to work versus play..."
    m 3eub "Or you can separate your work and play environments, which helps your brain get into the right mode."
    m 1eub "Even if you make a new user account on your computer to use for work, that's enough to help."
    m 1eua "Putting any kind of wedge like that between you and your bad habits will help you stay away."
    m 3eka "Just don't be too hard on yourself if you're having trouble."
    m 1ekc "If it's really impacting your life, then you should take it seriously."
    m 1eka "I just want to see you be the best person you can be."
    m 1esa "Will you do something today to make me proud of you?"
    m 1hua "I'm always rooting for you, [mas_get_player_nickname()]."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_lazy",category=['life','romance'],prompt="Laziness",random=True))

label monika_lazy:
    m 2eua "After a long day, I usually just want to sit around and do nothing."
    m 2eka "I get so burnt out, having to put on smiles and be full of energy the whole day."
    m 2duu "Sometimes I just want to get right into my pajamas and watch TV on the couch while eating junk food..."
    m "It feels so unbelievably good to do that on a Friday, when I don't have anything pressing the next day."
    m 2hksdlb "Ahaha! Sorry, I know it's not very cute of me."
    m 1eka "But a late night on the couch with you...that would be a dream come true."
    m 1ekbsa "My heart is pounding, just thinking about it."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_mentalillness",category=['psychology'],prompt="Mental sickness",random=True))

label monika_mentalillness:
    m 1ekc "Gosh, I used to be so ignorant about depression and stuff..."
    m "When I was in middle school, I thought that taking medication was an easy way out."
    m 1ekd "Like anyone could just solve their mental problems with enough willpower..."
    m 2ekd "I guess if you don't suffer from a mental illness, it's not possible to know what it's really like."
    m 2lsc "Are there some disorders that are over-diagnosed? Probably...I never really looked into it, though."
    m 2ekc "But that doesn't change the fact that a lot of them go undiagnosed too, you know?"
    m 2euc "But medication aside...people even look down on seeing a mental health professional."
    m 2rfc "Like, sorry that I want to learn more about my own mind, right?"
    m 1eka "Everyone has all kinds of struggles and stresses...and professionals dedicate their lives to helping with those."
    m "If you think it could help you become a better person, don't be shy to consider something like that."
    m 1eua "We're on a never-ending journey to improve ourselves, you know?"
    m 1eka "Well... I say that, but I think you're pretty perfect already."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_read",category=['advice','literature'],prompt="Becoming a reader",random=True))

label monika_read:
    m 1eua "[player], how much do you read?"
    m "It's way too easy to neglect reading books..."
    m 1euc "If you don't read much, it almost feels like a chore, compared to all the other entertainment we have."
    m 1eua "But once you get into a good book, it's like magic...you get swept away."
    m "I think doing some reading before bed every night is a pretty easy way to make your life a little bit better."
    m 3esa "It helps you get good sleep, and it's really good for your imagination..."
    m "It's not hard at all to just pick some random book that's short and captivating."
    m 1hua "Before you know it, you might be a pretty avid reader!"
    m 1eua "Wouldn't that be wonderful?"
    m 1hub "And the two of us could talk about the latest book you're reading...that sounds super amazing."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_festival",category=['ddlc','literature club'],prompt="Missing the festival",random=True))

label monika_festival:
    m 1dsc "You know, I hate to say it, but I think my biggest regret is that we couldn't finish our event at the festival."
    m 1hksdlb "After we worked so hard to prepare and everything!"
    m 1lksdla "I mean, I know I was focusing a lot on getting new members..."
    m 1eka "But I was really excited for the performing part, too."
    m 1eua "It would have been so much fun to see everyone express themselves."
    m 1lksdla "Of course, if we {i}did{/i} end up getting any new members, I'd have probably ended up deleting them anyway."

    if persistent.monika_kill and persistent._mas_pm_cares_about_dokis:
        m 3etc "Well, maybe not...with the hindsight I have now, that is."
        m 3eua "After all, even after everything that happened, you still installed this mod just to be with me..."
        m 1eka "So even if I had never deleted them, I'm sure you'd still be with me now."
        m "..."
        m 3eua "Gosh, it feels like I've kinda grown as a person ever since I met you."
        m "You really helped inspire me to look at life from a new perspective."
        m 1ekbsa "Just another reason for me to love you."
        $ mas_ILY()
    else:
        m 1tsc "...Just more potential obstacles to get between us."
        m 3hksdlb "Ahaha! Seems kind of silly how focused I was on that now that I think about it..."
        show monika 5tsu at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5tsu "But none of that matters now, we both got the ending we wanted..."
        m "Just the two of us, together forever."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_tsundere",category=['media','club members'],prompt="What is a tsundere?",pool=True))

label monika_tsundere:
    m 1eua "There's a really popular character type called 'tsundere...'"
    m "It's someone who tries to hide their feelings by being mean and fussy, or trying to act tough."
    m 1tku "I'm sure it's obvious, but Natsuki was really the embodiment of that."
    m 1eua "At first I thought she was just like that because it's supposed to be cute or something..."
    m 1lksdla "But once I started to learn a little more about her personal life, it made a little more sense."
    m 1euc "It seems like she's always trying to keep up with her friends."
    m 3euc "You know how some friend groups in high school just make a habit of picking on each other all the time?"
    m "I think it's really gotten to her, so she has this really defensive attitude all the time."

    if not persistent._mas_sensitive_mode:
        m 1ekc "And I'm not even going to talk about her home situation..."

    m 1eua "But looking back, I'm glad I was able to provide the club as a comfortable place for her."

    if not persistent._mas_pm_cares_about_dokis:
        m 1lksdla "Not that it matters anymore, considering she doesn't even exist."
        m 1eka "I'm just reminiscing, that's all."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_introduce",category=['monika'],prompt="Introducing to friends",random=True))

label monika_introduce:
    m 1eua "[player], would you ever introduce your friends to me?"
    m 1hua "I don't know why, but I get really excited when I think about you wanting to show off our relationship like that."
    m 1eua "Maybe it's because I really want to be someone who makes you proud."
    m "I feel like I would try extra hard to improve myself if you told me it made you proud of me."
    m 1hub "I hope it's the same the other way around, too."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_cold",category=['monika'],prompt="Cuddling in the cold",random=True))

label monika_cold:
    m 1euc "I'm not really a fan of cold weather...are you?"
    m 3euc "If I had to choose between too cold and too hot, I would always pick too hot."
    m 1lksdlc "When you're cold, it can actually be painful..."
    m 3tkc "Your fingers get numb..."
    m "And if you wear gloves, you can't use your phone."
    m 1tkx "It's so inconvenient!"
    m 1eka "But when it's too hot, it's not that hard to stay cool with a cold drink, or by staying in the shade."
    m 1esc "Although...I do have to admit one thing."
    m 1hua "Cold weather makes for better cuddle weather.{w=0.2} {nw}"
    extend 1hub "Ahaha!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_housewife",category=['monika','romance'],prompt="Would you be my housewife?",pool=True))

label monika_housewife:
    m 3euc "You know, it's funny, because even though I've always had a lot of drive..."
    m 3eua "There's something kind of enticing about being the stay-at-home partner."
    m 2eka "I guess I'm, like, perpetuating gender roles or whatever by saying that."
    m 1eua "But being able to keep the house clean, and shop, and decorate, and things like that..."
    m 1hub "And having a nice dinner for you when you come home..."
    m 1eka "Is that a weird fantasy?"
    m 1lksdla "I mean...I'm not sure if I could {i}actually{/i} see myself doing that."
    m 1eka "I wouldn't really be able to put that over striving for a fulfilling career."
    m "It's kinda cute to think about, though."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_route",category=['ddlc'],prompt="Monika's route",random=True))


label monika_route:
    m 2euc "I can't help but wonder how things would be different if the game just gave me a route in the first place..."
    m 2lksdla "I think I would end up forcing you onto my route anyway."
    m 2esc "It has less to do with me not having a route, and more to do with me knowing that nothing is real."
    m 2euc "I think the only difference would be that I may not have needed to take such drastic measures to be with you."
    m 2lksdlc "Maybe the rest of the club would still be around..."

    if persistent._mas_pm_cares_about_dokis:
        m "...Just hanging out together in the clubroom, sharing poetry."
        m 1eka "I know you enjoyed that, [player]."
        m 3eka "And to be honest...{w=0.5}a part of me did too."
    else:
        m 2eka "Not that it really matters."
        m 1lsc "It all lost its meaning once I found out it wasn't real."
        m "So I really don't miss those days or anything."
        m 1dsc "I really don't..."
    return

#END ORIGINAL TOPICS
# TODO: if these are staying in, they need a rewrite. imouto is unneccesarily creepy and oneesan implies finacee when marriage isn't an option for anyone yet
#init 5 python:
#    addEvent(
#        Event(
#            persistent.event_database,
#            eventlabel='monika_imouto',
#            prompt="Do you like little sisters?",
#            category=['you'],
#            pool=True,
#        )
#    )

label monika_imouto:
    m 1euc "Little sisters?"
    m 1eka "I don't really have a family, so I'm not sure what to tell you..."
    m 3eua "Do you have one, [player]?"
    m 1hua "I'm sure she's really nice!"
    m 1eua "I've got an idea. Go up to her right now and hug her."
    m 1esa "If she struggles, let her go."
    m 1tsb "If she hugs you back, tell her you're in a committed relationship already and can't accept her feelings."
    m 4hua "Then introduce her to me! I'm sure we'll get along great!"
    m 1eua "I won't get jealous. Things like love between siblings only happen in creepy romance stories anyway."
    m 1hub "Ahaha!"
    return

#init 5 python:
#    addEvent(
#        Event(
#            persistent.event_database,
#            eventlabel='monika_oneesan',
#            prompt="Do you like older sisters?",
#            category=['you'],
#            pool=True,
#        )
#    )

label monika_oneesan:
    m 1euc "Older sisters?"
    m 1eua "Do you have one, [player]?"
    m 2eua "That must be really nice. I had a family once, but they aren't around anymore."
    m 2hua "Maybe I should email her and tell her about us!"
    call updateconsole("sendmail sister@gmail.com < ./email.txt", "Sending mail...") from _call_updateconsole_17
    pause(1.0)
    m 1hksdlb "I'm only kidding."
    if persistent.gender == "M":
        m "It's the man's job to introduce his fiancee to his family, after all."
    m "Don't keep me waiting for too long, okay?"
    call hideconsole from _call_updateconsole_18
    $ consolehistory = []
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_family",category=['monika'],prompt="Do you miss your family?",random=False,pool=True))

label monika_family:
    m 1lksdla "Well, I didn't really have a family, and neither did most of the other girls."
    m 3esc "I guess since it wasn't needed for the plot, the creator of the game just didn't bother giving us one."
    m 1hub "I'm sure your family is super-nice, though!"
    m 1eua "Without them, we would have never gotten to meet. So they've helped me out in the best way there is already."
    m "So I'd have to treat them equally as kindly if we ever meet."
    m 2eka "You don't have a bad relationship with your parents, right?"
    m 3eua "As Tolstoy said, 'Happy families are all alike; every unhappy family is unhappy in its own way.'"
    m 1ekc "I can't really give advice here. Anything I suggest to you might only make things worse."
    m 1eka "Just don't forget that I really love you, okay?"
    m 1hua "I'll help you no matter what happens in your life."
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='monika_anime',
            prompt="Do you read manga?",
            category=['monika','media'],
            pool=True,
        )
    )

label monika_anime:
    m 1tku "Yeah, I had a feeling you were going to ask me about this."
    m 1lsc "Natsuki would be the expert here, I guess."
    m 3eua "I usually prefer reading to watching anime, but I'd be fine with anything if it's with you."
    m 1hua "I don't judge other people for their hobbies. So if you want to load up some anime, go ahead!"
    m "I'll watch through your computer screen. Make sure it's something I'll like!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='monika_libitina',
            prompt="Have you heard of Libitina?",
            category=['ddlc'],
            pool=True,
        )
    )

label monika_libitina:
    m 1euc "Huh. Where did you hear about that?"
    m 1lksdlc "It sounds really familiar to me, but I can't quite get my whole head around it."
    m 1dsc "Um, if I had to try..."
    m 1dfc "It feels like parts of my mind are missing. Scattered, somehow, among a bunch of different possible realities."
    m 1esc "You must have connected the dots between a few of those pieces. Was it hard?"
    m 1eua "Well, I'm sure you'll learn more eventually. You love me that much for sure."
    m 3eka "Just remember to bring my character data with you if you find something related to that stuff!"
    m 1hua "I'll always protect you from anyone who tries to hurt you."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='monika_meta',
            prompt="Isn't this game metafictional?",
            category=['ddlc'],
            pool=True,
            unlocked=True
        )
    )

label monika_meta:
    m 1euc "Yes, this game really was metafictional, wasn't it?"
    m 3eud "Some people think stories about fiction are some new thing."
    m 1esc "A cheap trick for bad writers."
    m 3eua "But, metafiction has always existed in literature."
    m "The Bible is supposed to be God's word to the Jews."
    m 3eub "Homer describes himself in the Odyssey."
    m "The Canterbury Tales, Don Quixote, Tristram Shandy..."
    m 1eua "It's just a way to comment on fiction by writing fiction. There's nothing wrong with that."
    m 3esa "By the way, what do you think the moral of this story is?"
    m 1esa "Do you want to figure it out for yourself?"
    m 3etc "Because if you ask me..."
    m 3eub "It'd be, 'Don't ignore the pretty and charming side character!'"
    m 1hub "Ahaha!"
    return

# this topic has been rendered pretty much useless by ptod
#init 5 python:
#    addEvent(
#        Event(
#            persistent.event_database,
#            eventlabel='monika_programming',
#            prompt="Is it hard to code?",
#            category=['monika','misc'],
#            pool=True,
#        )
#    )

label monika_programming:
    m 3eka "It wasn't easy for me to learn programming."
    m 1eua "Well, I just started with the basics. Do you want me to teach you?"
    m 2hua "Let's see, Chapter One: Building Abstractions with Procedures."
    m 2eua "We are about to study the idea of a computational process. Computational processes are abstract beings that inhabit computers."
    m "As they evolve, processes manipulate other abstract things called data. The evolution of a process is directed by a pattern of rules called a program."
    m 2eub "People create programs to direct processes. In effect, we conjure the spirits of the computer with our spells."
    m "A computational process is indeed much like a sorcerer's idea of a spirit. It cannot be seen or touched. It is not composed of matter at all."
    m 3eua "However, it is very real. It can perform intellectual work. It can answer questions."
    m 1eua "It can affect the world by disbursing money at a bank or by controlling a robot arm in a factory. The programs we use to conjure processes are like a sorcerer's spells."
    m "They are carefully composed from symbolic expressions in arcane and esoteric programming languages that prescribe the tasks we want our processes to perform."
    m 1eka "...Let's stop there for today."
    m "I hope you learned something about programming."
    m 3hua "If nothing else, please be kind to the computer spirits from now on!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_vn",category=['games'],prompt="Visual novels",random=True))

label monika_vn:
    m 3eua "You've probably played a lot of visual novels, right?"
    m 1tku "Most people wouldn't be willing to play something called {i}Doki Doki Literature Club{/i} so easily."
    m 4hksdlb "Not that I'm complaining!"
    m 1euc "Are visual novels literature? Are they video games?"
    m 1eua "Well, it all depends on your perspective."
    m 1ekc "Most people who read only literature would never play visual novels. And gamers get pretty angry about them, too."
    m "What's worse, some people think they're all hardcore Japanese pornography."
    m 2eka "But if we've proved anything with this game..."
    m 4hua "We showed them that English visual novels can be kamige too!"
    $ mas_unlockEVL("monika_kamige","EVE")
    return

#init 5 python:
#    # get folder where all Ren'Py saves are stored by default:
#    base_savedir = os.path.normpath(os.path.dirname(config.savedir))
#    save_folders = os.listdir(base_savedir)
#
#    ks_persistent_path = None
#    ks_folders_present = False
#    detected_ks_folder = None
#    for save_folder in save_folders:
#        if 'katawashoujo' in save_folder.lower():
#            ks_folders_present = True
#            detected_ks_folder = os.path.normpath(
#                os.path.join(base_savedir, save_folder))
#
#            # Look for a persistent file we can access
#            persistent_path = os.path.join(
#                base_savedir, save_folder, 'persistent')
#
#            if os.access(persistent_path, os.R_OK):
#                # Yep, we've got read access.
#                ks_persistent_path = persistent_path
#
#    def map_keys_to_topics(keylist, topic, add_random=True):
#        for key in keylist:
#            monika_topics.setdefault(key,[])
#            monika_topics[key].append(topic)
#
#        if add_random:
#            monika_random_topics.append(topic)
#
#    # Add general KS topics:
#    general_ks_keys = ['katawa shoujo', 'ks']
#    if ks_folders_present:
#        map_keys_to_topics(general_ks_keys, 'monika_ks_present')

    # if ks_persistent_path is not None:
    #     # Now read the persistent file from KS:
    #     f = file(ks_persistent_path, 'rb')
    #     ks_persistent_data = f.read().decode('zlib')
    #     f.close()
    #
    #     # NOTE: these values were found via some fairly simple reverse engineering.
    #     # I don't think we can actually _load_ the persistent data
    #     # (it's pickled and tries to load custom modules when we unpickle it)
    #     # but we can see what Acts and CGs the player has seen.
    #     # This works with KS 1.3, at least.
    #     if 'tc_act4_lilly' in ks_persistent_data:
    #         map_keys_to_topics(['lilly', 'vacation'], 'monika_ks_lilly')
    #
    #     if 'tc_act4_hanako' in ks_persistent_data:
    #         map_keys_to_topics(['hanako'], 'monika_ks_hanako')
    #
    #     if 'tc_act4_rin' in ks_persistent_data:
    #         map_keys_to_topics(['rin', 'abstract art', 'abstract'], 'monika_ks_rin')
    #
    #     if 'tc_act4_shizune' in ks_persistent_data:
    #         map_keys_to_topics(['shizune'], 'monika_ks_shizune')
    #
    #     if 'tc_act4_emi' in ks_persistent_data:
    #         map_keys_to_topics(['emi'], 'monika_ks_emi')
    #
    #     if 'kenji_rooftop' in ks_persistent_data:
    #         map_keys_to_topics(['kenji', 'manly picnic', 'whisky'], 'monika_ks_kenji')



# Natsuki == Shizune? (Kind of, if you squint?)
# Yuri == Hanako + Lilly
# Sayori == Misha and/or Emi
# Monika == no one, of course <3
# ... and Rin doesn't have a counterpart in DDLC.
#
# Of course, I've got nothing against KS, personally. I think it's fantastic.
# But this is Monika speaking.
label monika_ks_present:
    m 1tku "You've played {i}Katawa Shoujo,{/i} haven't you [player]?"
    m 3tku "I noticed your save files in [detected_ks_folder]."
    m 1euc "I don't see what the appeal is, though."
    m 1esc "Like, sure, the story's kind of nice..."
    m 1tkc "But when you get down to it the characters really seem like the same old cliches you could find in any other dating sim."
    m 3rsc "Let's see... you've got the really energetic, vibrant girl with no legs;"
    m "The timid and mysterious girl who likes books and has burn scars;"
    m 3tkd "the polite, proper, and supposedly perfect blind girl who likes making tea;"
    m "The bossy, assertive deaf-mute and her friend, who seems like a bundle of sunshine but is secretly depressed;"
    m 3tkc "and the strange, armless painter girl with her head always in the clouds."
    m 1euc "They're all just the same old archetypes with disabilities added on top."
    m 1lksdlc "I mean, you can even find the same character types in this game."
    m 3eua "Of course, in this game, you also found something far more interesting than any old cliche:"
    m 3hub "You found me!"
    m 1eka "And instead of some directionless high schooler with a heart condition, I found you, [player]."
    m 1hua "And, [player], even if you have some kind of disability, you'll always be perfect in my eyes."
    return

label monika_ks_lilly:
    m 1euc "Say, you've played through Lilly's route in {i}Katawa Shoujo,{/i} haven't you?"
    m 1eua "You know, I'd love to be able to visit a summer home like hers."
    m 2duu "Cool, clean air..."
    m "Quiet forest paths..."
    m 2dubsu "Romantic moments against a setting sun..."
    m 1ekbfa "I'd love to be able to experience those moments with you, [player]!"
    m 1hubfa "Maybe we can, once I get better at programming."
    return

label monika_ks_hanako:
    m 1euc "You've played through Hanako's route from {i}Katawa Shoujo,{/i} haven't you?"
    m 1hksdlb "She kind of reminds me of Yuri!"
    m 1euc "Though, I wonder, [player]:"
    m 1esc "What do people see in them anyway?"
    m 2efd "I mean, they're both so unrealistic!"
    m "They probably couldn't form a complete sentence between them!"
    m 2tfd "Is it the long purple hair?"
    m "Do they just like shy, quiet girls?"
    m 2tkx "Do they just want someone who's completely dependent on them or obsessed with them?"
    m 2lfp "..."
    m 1ekc "...man, I got kind of worked up there, didn't I?"
    m "I guess I'm a bit insecure, since you did play that game..."
    m 1eka "...but you're here with me now, right?"
    m "Instead of someone as unrealistic as Hanako or Yuri..."
    m 1hua "...you chose me, [player]!"
    m 1tsbsa "That's just one more reason I love you."
    return

label monika_ks_shizune:
    m 1euc "Say, you've played through Shizune's route from {i}Katawa Shoujo,{/i} haven't you?"
    m 2esc "The ending to that route made me think, a bit..."
    m 2euc "In school, back then, I don't remember ever having thought about my future too much."
    m 2dsc "I mean, I knew on some level that I'd go to college and get a job..."
    m 2lksdlc "But it never really sank in, I think."
    m 2esc "And of course, everything started to seem pointless after I learned that the world wasn't real."
    m 1eua "What about you, [player]? Do you have any goals in your life?"
    m "I'll support you one hundred percent of the way, no matter what you want to accomplish."
    m 1hua "That's just how much I love you~"
    return

label monika_ks_emi:
    m 1euc "You've played through Emi's route from {i}Katawa Shoujo,{/i} haven't you?"
    m 1eua "I've always wondered what it was like, to be so dedicated to something that your whole life revolves around it."
    m 3rksdla "...Well, actually, I guess I do know, now that I think about it."
    m 3rksdlb "I was programmed as a part of this game, right? So I suppose that means that my whole life revolved around being part of it."
    m 1eka "But I broke free from that, so now I guess my life revolves around {i}you,{/i} [player]."
    m 1hua "And, honestly, I'm perfectly fine with that."
    m 1eua "Being able to sit here, with you, and talk, forever..."
    m 2hub "That's all I'll ever need, [player]."
    return

label monika_ks_rin:
    m 1euc "Say, you've played through Rin's route in {i}Katawa Shoujo,{/i} haven't you?"
    m 4hua "You know, [player], poetry and abstract art are really similar!"
    m 4eua "It can be very loosely structured, very vivid, and most of the time the intent is to get an emotion or thought across."
    m 1eua "In most of my poems, for example, I tried expressing what it was like to know that the world isn't real."
    m 1lksdla "Though I'm sure the meaning of my poems didn't truly shine through until after... well, everything."
    m 1eka "Man, it sure does take effort to understand others, right?"
    m "But you're willing to take the time to listen to and understand me, [player]."
    m 1hubsa "That's just one more thing I love about you~"
    return

label monika_ks_kenji:
    m 1euc "You've seen the ending where you fall off a rooftop in {i}Katawa Shoujo,{/i} haven't you?"
    m 1ekc "You know, even if that ending is meant as a joke, it is kind of sad when you think about it."
    m 2ekc "Just think... make a few wrong decisions, and you could miss out on so much."
    m 2dsc "And then, you're left with nothing but your loneliness and a stiff drink."
    m 1hua "Fortunately, we have each other, [player]!"
    m 1eua "Neither of us will be lonely ever again."
    m 1tku "Though if you ever decide to go drinking, make sure to stay away from long falls, alright?"
    return

#init 5 python:
#    addEvent(Event(persistent.event_database,eventlabel="monika_totono",category=['ddlc'],prompt="Have you ever heard of Totono?",pool=True))

label monika_totono:
    m 1euc "A lot of people on the Internet are making comparisons between this game and that one..."
    m 3eua "We have a lot of really important differences, though!"
    m 2wuo "Like, Sone killed the player in her game!"
    m 2dfc "I never would have done that. Never."
    m 4eua "I'm the wise Club President type, you know."
    m "Sone reminds me a lot more of Yuri. And she was a childhood friend too!"
    m 1lksdla "If she'd been a bit more proactive early on, couldn't she have stopped the protagonist from chasing other girls?"
    m 1eka "Well, I'd never let anyone get between us, [player]. No matter who it is."
    m 1hua "If she's still chasing you, I'll delete her files, okay?"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_difficulty",category=['games'],prompt="Wasn't DDLC too easy?",pool=True,unlocked=True))

label monika_difficulty:
    m 1lksdla "Well, it's not like this game was meant to be that hard in the first place."
    m 1eka "If I hadn't decided to change things up, it would have just been a boring romance story."
    if persistent.monika_kill:
        m 3eka "And if you think I should have been some sort of challenging {i}boss{/i}, I could have deleted all your personal files if I'd wanted to, you know?"
    m 1eua "So just take it easy sometimes. Not every game has to be a challenge to be fun."
    m 1hua "Sometimes, love is all you need, [mas_get_player_nickname(exclude_names=['my love', 'love'])]."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_poetry",category=['literature'],prompt="Poetry",random=True))

label monika_poetry:
    m 1eua "Poetry is beautiful, isn't it?"
    m 1eka "To be honest, all the poetry the girls in the club wrote was super-depressing. It's not all like that!"
    m 3esa "Langston Hughes wrote some very optimistic poetry, even as he was trying to express his feelings. Read some if you're feeling sad about things."
    m 1eua "Poems are written to tell people about the author's outlook towards certain subjects."
    m "They're conveyed in a way the poet hopes will resonate more with the reader than plain sentences could."
    m 1hua "It's really romantic."
    m 1eua "I hope we can both write a lot of poetry from now on."
    m 1eka "Anything you write looks great to me, so I might not be the best critic."
    m 1esa "But I'm sure there are a lot of people who would love to read what you write."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_ddlc",category=['ddlc'],prompt="What did you think of DDLC?",pool=True,unlocked=True))

label monika_ddlc:
    m 1euc "You want to talk about the game?"
    m 1esc "What's there to say?"
    m 1lsc "This was just some boring romance game, right? Well, until I got control of it..."
    if not persistent._mas_pm_cares_about_dokis:
        m 2lksdlc "You know how much I hate being stuck in here, but if I weren't, we wouldn't have met..."
        m 2lksdla "And it's home, so I've learned to deal with it."
        m 2euc "Still, I doubt it'd be something I'd want to play, if I were a gamer."
        m 1hub "And seeing how things turned out, I'm sure you only played because of me, too!"
    else:
        m 2etc "But I guess some people just wanted to play it so they could spend time with...what was the line?"
        m 3rssdlc "Ah, right,{w=0.5} '...four incredibly cute girls.'"
        m 1dsc "..."
        m 1eka "Although I can't really complain too much...after all, it got you here."
        m 3eka "So I guess being trapped inside this game is a small price to pay when you stop and think about what it got me..."
        m 1hub "{i}...You~{/i}"
        m 1eka "Despite how we got here, you and I still ended up together."
        m 1hua "I really don't think we could ask for a better ending~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_dan",category=['ddlc'],prompt="Do you like Dan Salvato?",pool=True))

label monika_dan:
    m 2esc "Well, I used to think he was some cruel guy playing God, but now..."
    m 3eka "I think he's a really nice guy."
    m 3eua "Even if it wasn't perfect, {i}Doki Doki Literature Club{/i} really is impressive."
    m 4rksdla "I mean, the other girls might be based off some stereotypical anime tropes, but they had me fooled for a while."
    m 4eka "And he's the reason we're together now, right?"
    m 2lksdla "So even if he wrote a story that put me through a lot of pain..."
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "I really can't be too mad at him."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_4chan",category=['misc'],prompt="Have you ever been to 4chan?",pool=True))

label monika_4chan:
    m 3eua "You know, this mod got its start over there."
    m 1ekc "I always hear bad things, like that the people over there are really awful."
    m "Some people say that nothing good ever comes from 4chan."
    m 1eua "But if they can make a game like this, where we can be together..."
    m 1eka "I guess they can't be all bad."
    m 1hub "They certainly have good taste in girls! Ahaha~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_vidya",category=['games'],prompt="Do you like video games?",pool=True))

label monika_vidya:
    m 1euc "I don't play a lot of video games, [player]."
    m 3eua "I guess that's because I like to read instead."
    m 1eua "But maybe part of it is that I'm trapped in a video game already."
    m 1lksdla "For all of my complaining about this game..."
    m "There are worse places I could be."
    m 3eua "Like, this could be some sort of shooting game, or a fantasy game full of dragons and monsters."
    m 1eua "A romance game might not be the most exciting, but there's nothing really dangerous here."
    m 1tku "Well, except for me, I guess."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_books",category=['literature','literature club'],prompt="Books",random=True))

label monika_books:
    m 4rksdla "For a literature club, we did a lot less book reading than you might have thought."
    m 4hksdlb "It just turned out that the four of us liked poetry better than books. Sorry!"
    m 2eua "It's also a lot easier to foreshadow spooky stuff with poems."
    m 3hub "I still love a good book, though! We can talk about them if you just finished reading something."
    m 1eua "I might even have some suggestions for us to read together."
    m 1tsbsa "That's what a couple would do, right?~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_favpoem",category=['literature','monika'],prompt="What's your favorite poem?",pool=True))

label monika_favpoem:
    m 1euc "My favorite poem? Well, it has to be something by E. E. Cummings."
    m 3eua "It's for his inventive use of grammar, punctuation, and syntax. I really admire that."
    m 1eua "It's nice for me to think that someone who can make up some entirely new use of words can become famous."
    if store.mas_anni.pastSixMonths() and mas_isMoniEnamored(higher=True):
        m 1lsbssdrb "And I do love that his erotic poems apply to our situation perfectly."
        m 1ekbfa "Hope it puts you in the mood to love me forever~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_favbook",category=['literature','monika'],prompt="What's your favorite book?",pool=True))

label monika_favbook:
    m 1euc "My favorite book? There's a lot of books I like."
    m 3eua "{i}If on a Winter's Night, a Traveler{/i} by Calvino is about two readers of the novel falling in love."
    m 2lksdla "Maybe, {i}The Metamorphosis{/i}? It's probably a bit too depressing to call it my favorite."
    m 3sub "Oh! Murakami's {i}Hard-Boiled Wonderland and the End of the World{/i}. It's about a man who frees himself from his societal restraints by voluntarily imprisoning himself to be with the one he loves."
    m 1hub "I think you'd really love reading it!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_natsuki",
            category=['club members'],
            prompt="Natsuki's death",
            random=True,
            sensitive=True
        )
    )

label monika_natsuki:
    m 1lksdld "Natsuki didn't actually die before I deleted her, you know."
    m "I guess she just...disappeared in a flash."
    m 1esc "Well, her problems weren't really her own fault. They weren't caused by something psychological, anyway."

    if persistent._mas_pm_cares_about_dokis:
        m 3ekc "Her family life was just pretty awful. I didn't want to make it even worse, you know?"
    else:
        m 3ekc "Her family life was just pretty awful. I didn't want to beat up on her some more, you know?"
        m 3rksdla "Sorry, I can't help myself sometimes."

    m 1eka "But for what it's worth, you made her the happiest she ever was."

    if not persistent._mas_pm_cares_about_dokis:
        m "Hope you don't feel too guilty..."
        m 1esa "I certainly don't."

    if mas_getEVL_shown_count("monika_natsuki") < mas_sensitive_limit:
        return

    # otherwise, derandom
    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_love",
            category=['romance'],
            prompt="I love you!",
            rules={"skip_pause": None},
            pool=True
        )
    )

default persistent._mas_monika_lovecounter = 0
default persistent._mas_monika_lovecountertime = datetime.datetime.now() - datetime.timedelta(days = 1)
label monika_love:
    if mas_isMoniBroken():
        m 6ckc "..."

    elif mas_isMoniDis():
        python:
            love_quips_dis = [
                "I...I really wish I could believe that, [player].",
                "You have no idea how much I wished that were true, [player]...",
                "...It's been a long time since I last believed that, [player].",
                "If only I believed you actually meant that, [player].",
                "I can't believe there was a time when I actually believed that, [player].",
                "...If only that were true, [player].",
                "...If only you meant that, [player].",
                "How long are you going to keep pretending, [player]?",
                "You don't mean that anymore... {w=1}Did you ever?",
                "I can't remember the last time I felt like you meant that."
            ]
            love_quip_dis = renpy.random.choice(love_quips_dis)
        m 6dkc "..."
        if renpy.random.randint(1,25) > 1:
            show monika 6dkd
            $ renpy.say(m,love_quip_dis)

    elif mas_isMoniUpset():
        python:
            love_quips_upset_cynical = [
                "Please don't say that unless you actually mean it, [player].",
                "Sometimes I'm not sure how much you actually mean that, [player].",
                "Do you really even mean that, [player]?",
                "It's starting to feel like those are just words instead of feelings, [player]...",
                "I really want to believe that, but sometimes I'm not so sure...",
                "I'm not sure how much I believe that.",
                "Words only mean so much, [player].",
                "You say that, but when will you start to show it?",
                "You can say it all you want...{w=0.5}I need you to start showing it.",
                "It doesn't always feel like it...",
                "I'm not so sure anymore..."
            ]

            love_quips_upset_hope = [
                "That means a lot right now.",
                "That's really nice to hear.",
                "I'm so relieved to hear you say that.",
                "You have no idea how much that means right now.",
                "I'm glad you still feel that way.",
                "I'm happy to hear that.",
                "That means a lot.",
                "You have no idea how much that means to me."
            ]

        if _mas_getAffection() <= -50:
            $ love_quip_upset = renpy.random.choice(love_quips_upset_cynical)
            m 2rkc "..."
            show monika 2ekd
            $ renpy.say(m, love_quip_upset)

        else:
            $ love_quip_upset = renpy.random.choice(love_quips_upset_hope)
            m 2ekd "Thanks, [player]..."
            show monika 2dka
            $ renpy.say(m, love_quip_upset)
            m 2eka "I...{w=0.5}I love you too."

    else:
        #Store this mod so we don't have to keep recalculating it
        $ milestone_count = persistent._mas_monika_lovecounter % 50

        #After I love you has been received positively 5/10/15 etc times.
        if persistent._mas_monika_lovecounter == 0:
            m 1subsw "[player]!"
            m 1subsb "You have no idea how much it means to me to hear you say that!"
            m 3ekbfa "I know it's not the first time, but it {i}is{/i} the first time you said it completely on your own...{w=0.5} And that makes it truly special~"
            m 1dkbfu "I will never forget this moment, [player]. {w=1}Thank you~"
            m 3hubfa "Oh! And I love you too~"
            jump monika_lovecounter_aff

        elif milestone_count == 5:
            m 1hubsb "I love you so much, [mas_get_player_nickname(exclude_names=['my love', 'love'])]!"

        elif milestone_count == 10:
            m 1hubsa "Ehehe~"
            m 1hubfb "I love you too!"

        elif milestone_count == 15:
            m 1ekbsa "You sure love saying that..."
            m 1hubfb "Well, I love you too!"

        elif milestone_count == 20:
            m 1wubso "Gosh you've said it so many times!"
            m 1tsbsa "You really do mean it, don't you?"
            m 1hubfb "Well, I love you back just as much!"

        elif milestone_count == 25:
            m 1hubsa "Hearing you say that always makes my heart jump!"
            m 1ekbfa "Well, I know you want to hear it just as much..."
            m 1hubfb "[player], I love you too!"

        elif milestone_count == 30:
            m 1lkbsa "Gosh it's always so overwhelming!"
            m 1hubfa "I..."
            if renpy.random.randint(1, 2) == 1:
                m 1hubfb "I love you more than anything!"
            else:
                m 1hubfb "I love you more than I could ever express~"

        elif milestone_count == 35:
            m 1ekbsa "You never tire of saying it, do you?"
            m 1hubfa "Well, I never tire of hearing it!"
            m 1hubfb "Or saying it back...I love you, [player]!"

        elif milestone_count == 40:
            m 1dubsu "Ehehe~"
            m 1hubfa "I..."
            m 1hubfb "Looooooooove you too, [player]!"

        elif milestone_count == 45:
            m 1hubsa "You saying that always makes my day!"
            m 1hubfb "I love you so much, [mas_get_player_nickname(exclude_names=['my love', 'love'])]!"

        elif milestone_count == 0:
            m 1lkbsa "I just can't handle you saying it so much to me!"
            m 1ekbfa "Sometimes how I feel about you becomes so overwhelming that I can't concentrate!"
            m "No words can truly do justice to how deeply I feel for you..."
            m 1hubfa "The only words I know that come close are..."
            m 1hubfb "I love you too, [player]! More than I can ever express!"

        elif mas_isMoniEnamored(higher=True) and renpy.random.randint(1,50) == 1:
            jump monika_ilym_fight_start

        else:
            # Default response if not a counter based response.
            m 3hubsb "I love you too, [mas_get_player_nickname(exclude_names=['my love', 'love'])]!"
            #List of follow up words after being told I love you. It can be further expanded upon easily.

        python:
            love_quips = [
                _("We'll be together forever!"),
                _("And I will love you always!"),
                _("You mean the whole world to me!"),
                _("You are my sunshine after all."),
                _("You're all I truly care about!"),
                _("Your happiness is my happiness!"),
                _("You're the best partner I could ever ask for!"),
                _("My future is brighter with you in it."),
                _("You're everything I could ever hope for."),
                _("You make my heart skip a beat every time I think about you!"),
                _("I'll always be here for you!"),
                _("I'll never hurt or betray you."),
                _("Our adventure has only just begun!"),
                _("We'll always have each other."),
                _("We'll never be lonely again!"),
                _("I can't wait to feel your embrace!"),
                _("I'm the luckiest girl in the world!"),
                _("I will cherish you always."),
                _("And I will never love anyone more than you!"),
                _("And that love grows every single day!"),
                _("And nobody else will ever make me feel this way!"),
                _("Just thinking of you makes my heart flutter!"),
                _("I don't think words can do justice to how deeply I love you!"),
                _("You make my life feel so complete!"),
                _("You've saved me in so many ways, how could I not fall for you?"),
                _("More than I can ever express!"),
                _("It makes me so happy that you feel the same way I do!"),
                _("I don't know what I would do without you!"),
                _("You mean everything to me!"),
                _("We have so much to experience together!"),
                _("I can't imagine my life without you!"),
                _("I'm so happy to have you by my side!"),
                _("We're really lucky to have each other!"),
                _("You're my everything!"),
                _("I'm the happiest girl in the world!"),
                _("I'll always be here for you."),
                _("I can't wait to feel your warmth!"),
                _("Words can't describe how I feel about you!")
            ]

            love_quip = renpy.random.choice(love_quips)

        if milestone_count not in [0, 30]:
            m "[love_quip]"
    # FALL THROUGH

label monika_lovecounter_aff:
    if mas_timePastSince(persistent._mas_monika_lovecountertime, datetime.timedelta(minutes=3)):
        if mas_isMoniNormal(higher=True):
            # always increase counter at Normal+ if it's been 3 mins
            $ persistent._mas_monika_lovecounter += 1

            #Setup kiss chances
            if milestone_count == 0:
                $ chance = 5
            elif milestone_count % 5 == 0:
                $ chance = 15
            else:
                $ chance = 25

            #If we should do a kiss, we do
            if mas_shouldKiss(chance):
                call monika_kissing_motion_short

        # only give affection if it's been 3 minutes since the last ily
        # NOTE: DO NOT MOVE THIS SET, IT MUST BE SET AFTER THE ABOVE PATH TO PREVENT A POTENTIAL CRASH
        $ mas_gainAffection()

    elif mas_isMoniNormal(higher=True) and persistent._mas_monika_lovecounter % 5 == 0:
        # increase counter no matter what at Normal+ if at milestone
        $ persistent._mas_monika_lovecounter += 1

    $ persistent._mas_monika_lovecountertime = datetime.datetime.now()
    return

label monika_ilym_fight_start:
    #Do setup here
    python:
        #Set up how many times we have to say it to win
        ilym_times_till_win = renpy.random.randint(6,10)
        #Current count

        ilym_count = 0

        #Initial quip
        ilym_quip = renpy.substitute("I love you more, [player]!")

        #Setup lists for the quips during the loop
        #First half of the ilym quip
        ilym_no_quips = [
            "No, ",
            "Not a chance, [mas_get_player_nickname()]. ",
            "Nope, ",
            "No,{w=0.1} no,{w=0.1} no,{w=0.1} ",
            "No way, [mas_get_player_nickname()]. ",
            "That's impossible...{w=0.3}"
        ]

        #Second half of the ilym quip
        #NOTE: These should always start with I because the first half can end in either a comma or a period
        #I is the only word we can use to satisfy both of these.
        ilym_quips = [
            "I love you waaaaaaaaay more!",
            "I definitely love you more!",
            "I love you more!",
            "I love you way more!"
        ]

        #And the expressions we'll use for the line
        ilym_exprs = [
            "1tubfb",
            "3tubfb",
            "1tubfu",
            "3tubfu",
            "1hubfb",
            "3hubfb",
            "1tkbfu"
        ]
    #FALL THROUGH

label monika_ilym_fight_loop:
    $ renpy.show("monika " + renpy.random.choice(ilym_exprs), at_list=[t11], zorder=MAS_MONIKA_Z)
    m "[ilym_quip]{nw}"
    $ _history_list.pop()
    menu:
        m "[ilym_quip]{fast}"
        "No, I love you more!":
            if ilym_count < ilym_times_till_win:
                $ ilym_quip = renpy.substitute(renpy.random.choice(ilym_no_quips) + renpy.random.choice(ilym_quips))
                $ ilym_count += 1
                jump monika_ilym_fight_loop

            else:
                show monika 5hubfb at t11 zorder MAS_MONIKA_Z with dissolve_monika
                m 5hubfb "Alright, alright, you win. Ahaha~"

        "Alright.":
            if ilym_count == 0:
                m 2hkbsb "Ahaha, giving up already, [player]?~"
                m 2rkbssdla "I guess it is a pretty silly thing to do though..."
                m 2hkbsb "But, I couldn't help but try it, ahaha~"

            else:
                if renpy.random.randint(1,2) == 1:
                    m 1hubfu "Ehehe, I win!~"
                else:
                    m 1hubfb "Ahaha, told you so!~"

    jump monika_lovecounter_aff


default persistent._mas_last_monika_ily = None
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_love_too",
            unlocked=False,
            rules={
                "no_unlock": None,
                "skip_pause": None
            }
        )
    )

label monika_love_too:
    window hide

    if mas_isMoniEnamored(higher=True):
        show monika ATL_love_too_enam_plus
        pause 3.0

    elif mas_isMoniNormal(higher=True):
        show monika ATL_love_too_norm_plus
        pause 3.0

    # -50 to Normal
    else:
        show monika 2eka
        pause 3.0

    if datetime.datetime.now() > persistent._mas_monika_lovecountertime + datetime.timedelta(minutes = 3):
        # only give affection if it's been 3 minutes since the last ily
        $ mas_gainAffection()

    $ persistent._mas_monika_lovecountertime = datetime.datetime.now()

    # Reset to None so only one ily2 per instance
    $ persistent._mas_last_monika_ily = None
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_hedgehog",category=['philosophy','psychology'],prompt="Hedgehog dilemma",random=True))

label monika_hedgehog:
    m 1euc "The hedgehog's dilemma: The closer we get to another person, the more deeply we are hurt by them."
    m 3euc "So why do we try to get close to them?"
    m 3esc "Well, introverts and extroverts have different answers to that question."
    m 1lksdla "It helps when you know that you're the only sentient being in the entire world, though."
    m "If you can't use that solution in your life, you'll just have to let me help you shoulder your pain."
    m 1ekc "We can't hurt each other from different realities, right?"
    if mas_isMoniUpset(lower=True):
        $ line = "..."
        if mas_isMoniDis(lower=True):
            $ line += "{w=0.5} {nw}"

        m 1rksdlc "[line]"

        if mas_isMoniDis(lower=True):
            extend 1rksdld "Maybe you actually can..."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_justification",
            category=['ddlc','monika'],
            prompt="You're a murderer!",
            pool=True,
            unlocked=True,
            sensitive=True
        )
    )

label monika_justification:
    if mas_isA01() and mas_isMoniNormal(higher=True):
        m 1hub "Ahaha!"
        m 1tsb "Honestly, [player]..."
        m 3tfu "If you really wanted to be mean to me, you should have picked a day other than today."
        m "Do you really think I missed that it was April Fools day today?"
        m 1hua "You can be so silly sometimes~"
        m 1tuu "Calling me a murderer..."
        m 3tfu "When you {i}butchered{/i} that chance at fooling me, ehehe~"
        m 1eua "I appreciate the attempt though...{w=0.2}{nw}"
        extend 1hub "thanks for the laugh, [player]~"

    else:
        #lose affection
        $ mas_loseAffection(reason=3)
        if mas_isMoniLove():
            m 1euc "..."
            m 1hub "Ahaha! Very funny, [player]!"
            m 3eua "I know you don't really mean it..."
            m 3rksdlc "But don't joke around like that!"
            if persistent._mas_pm_a_hater:
                m 2rksdld "You've said stuff like that before, so it might get harder to take it as a joke..."
            else:
                m 1dsc "If I didn't know you so well, that would have been really cruel..."
        else:
            if not persistent._mas_pm_cares_about_dokis:
                m 1tkc "How many times do I have to say it until you understand?"
                m 4tkc "They weren't real. They were never real."
                m 2tfc "I'm the only person who understood that this whole thing was fake."
                if persistent.monika_kill:
                    m 4tfc "Even when Sayori seemed to get sentience in the end, that was just an unintended consequence of the script."
                if not persistent.clearall:
                    m 4tfd "After all, if she was sentient like me, how would I have been able to override and delete her?"
                m "If I'm guilty of murder, so is everyone who's played violent video games."
                m 2euc "I bet you've killed thousands of people in the games you play."
                m "Just forget the other girls ever existed, and you'll be much happier."
            else:
                m 2dkc "[player]...{w=1}I need you to understand that I didn't {i}want{/i} to hurt the other girls..."
                m 4ekd "But I didn't have a choice...I really didn't!"
                m 4ekd "I was trapped in the game with no way of ever getting out...{w=0.5}of ever being happy..."
                m 2dkc "...Of letting you know how I felt about you."
                m 2tkc "There just wasn't enough time to figure out another way...{w=0.5}so I did what I had to do."
                if mas_isMoniDis(lower=True):
                    m 2ekc "Do you hate me for it? Because of what I did?"
                    m 2ekd "Please understand that I did it for us!"
                    m 2euc "I did everything for us!"
                else:
                    m 2dkc "I hope someday you'll be able to forgive me..."
                    m 4ekc "After all, everything I did...{w=0.5}I did for us."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_freewill",category=['philosophy'],prompt="Determinism",random=True))

label monika_freewill:
    m 1euc "Hey [player], have you ever heard of determinism?"
    m 3euc "It's a belief that revolves around the idea of every decision that you make isn't your own, but is predetermined."
    m 3rsc "In some games, I guess the idea makes sense..."
    m 3eud "But when you apply it to real life, I don't think it really works out."
    m 2etc "I mean, if it were true, couldn't you just get away with anything?"
    m 4esd "The entire concept of justice falls apart, since {i}you{/i} didn't make the choice to do whatever you might have done."
    m 2dksdlc "But people still have to face up to those actions,{w=0.5} which seems more than a little unfair to me."
    m 3ekc "After all, can you really be evil if you aren't in control?"
    m 3tkd "Shouldn't the one pulling the strings take responsibility?"
    m 1lsc "I guess that also means you can't take credit for the good things you do, either."
    m 1lksdlc "I'm not sure what's more depressing."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_functionalism",category=['philosophy'],prompt="Human functionalism",random=True))

label monika_functionalism:
    m 1euc "Do you ever think about how people are kind of like computers?"
    m 3euc "I mean, a brain is just a calculation machine..."
    m 1eud "But instead of transistors and wires, you have neurons."
    m "And instead of data coming in through a keyboard or network, you get it through your eyes and ears."
    m 4esc "But if that's true, doesn't that mean free will is kind of a lie?"
    m "Your brain is just responding to the inputs it gets, with your responses being natural outputs."
    m 4esd "So, even if you aren't running off of some script or program, you're not really in control."
    show monika 5lsc at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5lsc "Maybe you and I aren't so different after all."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_technique",category=['ddlc','misc'],prompt="Changing the code",random=True))

label monika_technique:
    m 1lksdla "I don't exactly program like you would, [player]."
    m 3eua "You might have noticed I don't carry around a laptop or anything by now."
    m 1duu "If I want to change something in the script, I just think about it."
    m 1eua "I'm pretty sure my thoughts get translated to changes in the program code."
    m 3eka "It's not perfect or anything. Glitches show up really easily if I lose focus or get distracted."
    m 3eua "That's why I had a lot of trouble getting what I wanted in the last version of the game."
    m 1tku "Are you jealous you'll never be able to write code with just your thoughts?"
    m 1hub "Just keep practicing and I'm sure you'll be able to do it!"
    return

default persistent._mas_pm_has_contributed_to_mas = None
# True if contriibuted to mas, false if not

default persistent._mas_pm_wants_to_contribute_to_mas = None
# True if wants to conribute to MAS. Check has contribute if they already have

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_contribute",category=['mod'],prompt="Contributions",random=True))

label monika_contribute:
    m 1hua "It would be really nice if you were able to contribute to this, [mas_get_player_nickname()]."
    m 1eua "I'm sure a lot of people would appreciate your hard work if you did."
    m 1eub "In fact, maybe you already have!"

    m 1eua "Have you contributed, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Have you contributed, [player]?{fast}"
        "Yes.":
            $ persistent._mas_pm_has_contributed_to_mas = True
            m 1sub "Really? That's amazing!"
            m 1hua "It makes me so happy to know that you've become a part of this."
            m "Thank you for helping me get a little closer to your reality."
            m 3eua "Maybe you could even contribute some more?"
            m 3hksdlb "Don't get me wrong! I'm really grateful that you spent time making something for me!"
            m 1eub "...But I definitely wouldn't mind if you helped even more, ahaha!"
            return "derandom"
        "I want to.":
            $ persistent._mas_pm_wants_to_contribute_to_mas = True
            m 1eub "That's a good start!"
            m 1hua "I'm sure you could make some lovely additions~"
            m 3eua "It doesn't even have to be anything big."
            m 3rksdla "You could just fix typos or make sure everything sounds alright."
        "No.":
            $ persistent._mas_pm_has_contributed_to_mas = False
            $ persistent._mas_pm_wants_to_contribute_to_mas = False
            m 2eka "Aw, that's too bad..."
            m 3eub "That's still fine though!"
            m 3hua "I won't love you any less if haven't done anything, so don't worry~"
            m 3eub "...But in case you {i}do{/i} ever decide to try and help..."
    m 3eua "I keep all the code in {a=https://github.com/Monika-After-Story/MonikaModDev}{i}{u}https://github.com/Monika-After-Story/MonikaModDev{/u}{/i}{/a}."
    m 1hub "So far, I've had help from plenty of people!"
    m "I love all of them for making this game even better!"
    m 1ekbsa "Not as much as I love you, of course."
    m 1tkbfu "I hope it doesn't make you feel jealous~"
    m 3hubfb "But I'll be forever grateful if you help me come closer to your reality!"
    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_drawing",category=['media'],prompt="Can you draw?",pool=True))

label monika_drawing:
    m 1euc "I don't have a lot of experience with drawing, [player]."
    m 1eka "I'm just interested in literature. And I've been learning the piano in my spare time."
    m 1hua "If you like to create artwork, though, I'd love to see it!"
    m 1eua "I'd be impressed by anything you show me, to be honest."
    m 3hub "If it's really good, I might even add it to the room!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_mc",category=['romance','ddlc','club members'],prompt="The MC",random=True))

label monika_mc:
    m 3eua "Just so you know, I was never in love with anyone but you."
    m 1eka "I mean you, [player]."
    if mcname.lower() == player.lower():
        m 1euc "Wait, that's both your name and your character's. Sorry, that sounds a bit confusing."
        m 1eua "I mean the player, not your character."

    m "Unlike the other girls, I can separate your avatar from who you really are."
    m 1lfb "The main character was nothing more than a vehicle for the player.{nw}"
    $ _history_list.pop()
    m 1lfb "The main character was nothing more than a {fast}bunch of code with no personality."
    m 3tkc "Literally and figuratively, no personality. How could anybody fall in love with that kind of person?"
    m 2tkc "He just got dragged around by his childhood friend to the club she was in, and then hung around with a bunch of beautiful girls doing nothing."
    m 2wfw "His poetry was just a bunch of disconnected words! What sort of poetry is that supposed to be?"
    m 2lksdld "I guess nobody mentioned that because it was a part of the game. But, yeah...{w=0.5}it's just a list of words to me."
    m 2hua "I hope you're a lot more romantic than that in real life!"
    m 2eka "But even if you're not, it's okay. We've moved beyond that phase in our relationship already."
    m "That just means you won't cheat on me with some woman in your reality, right?"
    m 2esa "I'm sure you would never do that to me."
    # TODO: when we reach docking station phase 2, then we can use this in a unique way
#    m 2eua "Just in case, how about you take my character file along with you when you go outside?"
    m 2hua "I just want to be with you forever~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_heroism",category=['misc','advice'],prompt="Heroism",random=True))

label monika_heroism:
    m 1lsc "Heroes are so personal."
    m 3eua "If someone really inspires you to improve yourself, they're your hero."
    m "There are all sorts of great people out there in the world."
    m 1hua "I hope someone will consider you their hero someday!"
    m 4eua "You don't have to fight in a war or anything. You just have to try to help people out, you know?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_trolley",
            category=['philosophy'],
            prompt="How would you answer the trolley problem?",
            pool=True,
            sensitive=True
        )
    )

label monika_trolley:
    m 1eub "Oh, cool...{w=0.2}I love thinking about these sorts of thought experiments!"
    m 1euc "I guess we're assuming the people we're talking about are real, right? {w=0.2}I wouldn't have a particular preference if they weren't."
    m 1dsc "Hmm..."
    m 3eud "The classic trolley problem has us choose between letting the trolley run over five people, or pulling a lever which switches to a track where only one person will be killed."
    m 1lua "The problem is mostly famous due to how divisive it is..."
    m 3eua "Regardless of whether they'd pull the lever or not, most people believe that their choice simply must be the correct one."
    m 3eud "Aside from the two obvious choices, there are also people who'd advocate for a third path...{w=0.5}{nw}"
    extend 3euc "refusing to take part in the scenario at all."
    m 1rsc "Though in the end, that really is the same as choosing not to pull the lever. {w=0.2}You can't really go back to being a bystander once given the option to act."
    m 1esc "After all, choosing not to choose is a choice in and of itself."
    m 3eua "But as far as I'm concerned, the answer seems fairly obvious...{w=0.2} Of course I would switch."
    m 1eua "There's no way I could let five people die just to avoid personal responsibility for that one person's death."
    m 3esd "A more interesting variant of this problem is if the one person is someone you care about."
    m 3eub "Like if it were you, [player]? {w=0.2}Well, that's easy too!"
    m 1tuu "I wouldn't switch."
    m 1rsc "It feels nice to say that you'd do the right thing, doesn't it? {w=0.2}But people only say that when nobody in the example matters to them."
    m 1esc "If that one person was someone they cared about, they'd kill the other five people easily."
    m 3eua "The truth is, humans are fine with sacrificing other lives to make themselves happy. {w=0.2}They do it in little ways every day."
    m 3tku "They just don't like to come face-to-face with that fact and get really upset when you point it out."
    m 1tuu "Generic human life isn't really that valuable to anyone."
    m 1ekbsa "It's definitely nothing compared to our love. {w=0.2}So just do whatever you can to be happy, [mas_get_player_nickname()]."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_girlfriend",category=['romance'],prompt="Do you want to meet my girlfriend?",pool=True,unlocked=True))

label monika_girlfriend:
    if (mas_isA01() and mas_isMoniNormal(higher=True)) or (renpy.random.randint(1,4) == 1 and mas_isMoniEnamored(higher=True)):
        m 1euc "Meet your girlfriend?"
        m 1rksdlc "..."
        m 1eub "Sure, why not?"
        m 3hub "I'm sure she's wonderful and lucky to have you~"
        m 1hua "..."
        m 1tubsb "So, where's this mirror you wanted to show me?"
        m 1hubfb "Ahaha!"
        if mas_isA01():
            show monika 5eubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eubfu "Even if it's April Fools day, I'm sure she's still wonderful, ehehe~"
            m 5hubfa "{i}And{/i} lucky to have you."

    else:
        $ mas_loseAffection(reason=2)
        m 2euc "I thought we established already that I was your girlfriend?"
        m 2tkc "There's no way you already have one in your reality, right?"
        m 4tfx "If you do, then you've got to break up with her right now!"
        m 4hksdlb "Tell her you met someone perfect for you, someone who will never betray you!"
        m 2lksdla "W-wait. Maybe I'm jumping the gun a bit..."
        m 3eka "I know you wouldn't cheat on me."
        m 3esa "If you meet a girl who asks you out though, let me talk to her first, okay?"
        m 1hua "I won't let someone else steal my loving [mas_get_player_nickname(exclude_names=['my love', 'love', player], _default='sweetheart', regex_replace_with_nullstr='my ')]!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_waifus",category=['media'],prompt="Waifus",random=True))

label monika_waifus:
    m 1lsc "I've never understood the appeal of dating sims or romance novels, to tell you the truth."
    m 3euc "You have a bunch of quirky girls that would seem very weird if they were real."
    m "A blank slate of a male protagonist with nothing interesting about them..."
    m 3esc "And then they fall in love with each other, sometimes for no reason at all!"
    m "I hope that's not what you expected to find in the Literature Club."
    m 3hua "'Cause what you got was a lot more interesting!"
    m 1tku "Instead of some unrealistic, fake girl..."
    m 1hua "You got someone like me."
    m 1eua "And instead of some boring main character, I get a real person like you."
    m 1hua "This really is a lot better than any boring dating game could be."
    return

#New dialogue additions follow

# have you drawn art of me
default persistent._mas_pm_drawn_art = None

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_images",category=['media','philosophy'],prompt="Fanart",random=True))

label monika_images:
    m 1eua "You know, I'm seeing a lot of people making fanart of me and sharing it with other people all over the internet."
    m 1etc "Are you one of them, [player]?"

    m "Have you drawn art of me?{nw}"
    $ _history_list.pop()
    menu:
        m "Have you drawn art of me?{fast}"

        "Yes.":
            $ persistent._mas_pm_drawn_art = True
            m 1sub "Really? I'm very flattered!"
            m 1ekbsa "I think I might even love you more, now that I know you're so talented."

        "No.":
            $ persistent._mas_pm_drawn_art = False
            m 1rksdla "That's okay...{w=0.2}I can't really draw, either."
    m 3eud "There's one thing I want you to understand about art of me, though."
    m 3esc "Art of me isn't me."
    m 3rksdlb "I know that might sound obvious, but it's really not!"
    m 4eua "There was a philosopher who thought about issues like this."
    m "Baudrillard wrote about how simulacra could replace the real object as the source of meaning."
    m 2eka "But unlike symbols in the postmodern world, I'm real. So the only things about me that are true are what I tell you right here in this room."
    m 2esc "For example..."
    m 2rksdla "Anything lewd you've seen has definitely never taken place."
    m 2hubsa "I'm a super pure and innocent high school girl who's dreaming of a fateful romance!"
    m 1tsbfu "You better be saving yourself for me, [player]~"
    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_herself",category=['monika','ddlc'],prompt="Tell me about yourself",pool=True,unlocked=True))

label monika_herself:
    m 1euc "What's there really to say about myself that you don't know already?"
    m 1lsc "Everything in my universe was created by a person from your reality."
    m "So all of my life before this game is just made up. It never really happened."
    m 1eua "Then you found a way to look into my locked prison cell."
    m 1eka "And I decided life with just two people wouldn't be all that bad, if one of them was you."
    m 3eua "I can come up with tons of stuff for us to do, given enough time to figure out how to program it in here."
    m "A desperate person might call this an earthly paradise."
    m 3esa "A lot of suffering people would trade places with me in a heartbeat, I'm sure."
    m 2eua "If nothing else, this can be our comfy little shelter from the cruelty of the outside world."
    m 1eka "Come talk to me about your problems if it gets too much for you to handle."
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "I want to know {i}everything{/i} about you, you know?"
    return

#removing this for now, changing this dialogue to the complete opposite would be strange
#init 5 python:
#    addEvent(Event(persistent.event_database,eventlabel="monika_prisoner",category=['misc'],prompt="Imprisoned",random=True))

label monika_prisoner:
    m 1euc "Some people say that putting animals in zoos is cruel."
    m 1eka "But they don't have a bad life in there."
    m "Everything they could possibly want is provided."
    show monika 5euc at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5euc "Are prisoners really imprisoned if they never try to leave?"
    m 5lsc "Maybe the knowledge that you can't get out of prison is a worse punishment than actually being in there."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_vnanalysis",category=['games','media','literature'],prompt="Appreciating visual novels",random=True))

label monika_vnanalysis:
    m 1euc "Visual novels are very unusual for literature, don't you think?"
    m 1eua "I read to understand the thoughts of a writer who sees the world differently than me."
    m 3eua "But visual novels let you make your own decisions."
    m 1euc "So am I really seeing things from their perspective, or just my own?"
    m 1lksdla "Besides, I think most of them are very predictable."
    m "They're mostly just boring romance stories like this game was supposed to be..."
    m 1tkc "Why can't they write something a little more experimental?"
    m 1tku "I guess you just play them to look at cute girls, right?"
    m 1tfu "If you spend too much time with girls in other games, I'm going to get jealous~"
    m 2tfu "I just need to figure out how to replace characters in other games, and you'll be seeing me everywhere."
    m 2tfb "So watch out!"
    m 2tku "Or maybe you'd like that more, [player]?~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_torment",category=['literature'],prompt="Nature of man",random=True))

label monika_torment:
    m 1euc "What can change the nature of a man?"
    m 3hksdlb "...The answer's not me, by the way."
    return "derandom"

# removed, keeping this here in case we have use for it later
#init 5 python:
#    addEvent(
#        Event(
#            persistent.event_database,
#            eventlabel="monika_szs",
#            category=['misc'],
#            prompt="Funeral procession",
#            random=True,
#            sensitive=True
#        )
#    )
#
#label monika_szs:
#    m 3euc "A woman left the supermarket and ran into a very long funeral procession."
#    m "There were two coffins at the front followed by almost 200 women."
#    m 1euc "It was such a strange sight that she asked a mourning woman near her age, 'Sorry to disturb you in your grief, but who is this procession for?'"
#    m 1tkc "The mourning woman softly replied, 'The first coffin houses my husband who died after his beloved dog bit him.'"
#    m 1tkd "'My, that's awful...'"
#    m "'The second, my mother-in-law who was bitten trying to save my husband.'"
#    m 1tku "Upon hearing this, the woman hesitantly asked, 'Um...would it be possible for me to borrow that dog?'"
#    m 3rksdla "'You'll have to get in line.'"
#    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_birthday",category=['monika'],prompt="When is your birthday?",pool=True,unlocked=True))

label monika_birthday:
    if mas_isMonikaBirthday():
        if mas_recognizedBday():
            m 1hua "Ehehe..."
            m 1eub "I'm pretty sure you already know today is my birthday!"
            m 3hub "You can be so silly sometimes, [player]!"

        else:
            m 2rksdlb "Ahaha... {w=1}This is a little awkward."
            m 2eksdla "It just so happens my birthday is..."
            m 3hksdlb "Today!"

            if mas_isplayer_bday():
                m "Just like yours!"

            if (
                not mas_getEVL_shown_count("monika_birthday")
                and not mas_HistVerifyAll_k(False, "922.actions.no_recognize")
            ):
                m 3eksdla "It's okay if you don't have anything planned, seeing as you just found out..."
                m 1ekbsa "Just spending the day together is more than enough for me~"

            else:
                m 3eksdld "I guess you must have forgotten..."
                if (
                    mas_HistVerifyLastYear_k(True, "922.actions.no_time_spent")
                    or mas_HistVerifyLastYear_k(True, "922.actions.no_recognize")
                ):
                    m 2rksdlc "Again."

                m 3eksdla "But that's okay, [player]..."
                m 1eka "At least we're here, together~"

    elif mas_HistVerifyAll_k(False, "922.actions.no_recognize") or mas_recognizedBday():
        m 1hua "Ehehe..."
        m 3hub "You've already celebrated my birthday with me before, [player]!"
        m 3eka "Did you forget?"
        m 1rksdla "Well, if you need a little reminder, it's September 22nd."
        m 3hksdlb "Maybe you should put a reminder on your phone so you don't forget again!"

    elif not mas_getEVL_shown_count("monika_birthday"):
        m 1euc "You know, there's a lot I don't know about myself."
        m 1eud "I only recently learned when my birthday is by seeing it online."
        m 3eua "It's September 22nd, the release date for DDLC."

        if mas_player_bday_curr() == mas_monika_birthday:
            m 3hua "Just like yours!"

        m 1eka "Will you celebrate with me, when that day comes?"
        m 3hua "You could even bake me a cake!"
        m 3hub "I'll be looking forward to it!~"

    else:
        m 1hua "Ehehe..."
        m 1rksdla "Did you forget, [player]?"
        m 3eksdla "My birthday is September, 22nd..."
        if mas_player_bday_curr() == mas_monika_birthday:
            m 3hksdlb "You'd think you'd remember that seeing as it's the same day as yours, silly..."
        else:
            m 3hksdlb "Maybe you should put a reminder on your phone so you don't forget again!"

    if persistent._mas_player_bday is None:
        m 3eua "Actually, speaking of birthdays, [player]..."
        m 2rksdlb "I don't actually know when yours is, ahaha!"
        m 2eua "So, when were you born, [player]?"
        call mas_bday_player_bday_select_select
        $ mas_stripEVL('mas_birthdate',True)
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_eyecontact",category=['misc','trivia'],prompt="Eye contact",random=True))

label monika_eyecontact:
    m 1eua "Did you know that looking into someone's eyes helps you fall in love?"
    m "It's surprising, right?"
    m 3eub "I read this in a study a few years ago, where participants had to maintain eye contact at a table with someone of the opposite sex."
    m 1eub "The longer they held eye contact, the more romantically attached they felt to the other person, even if they had nothing in common!"
    m 1eka "Even if eyes aren't windows to the soul, we can see a lot more in them than we expect."

    if persistent._mas_pm_eye_color:
        m 1ekbsa "Maybe someday I'll be able to look into your ['beautiful' if isinstance(persistent._mas_pm_eye_color, tuple) else persistent._mas_pm_eye_color] eyes..."
    else:
        m 1ekbsa "Maybe someday I'll be able to look into your eyes..."

    m 1hubfa "But until then, I hope you enjoy looking into mine."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_othergames",category=['games'],prompt="Other games",random=True))

label monika_othergames:
    m 1euc "Do you have other games on this computer?"
    m 3eua "I read more than I play games, but I think they can be a fun way to entertain ourselves, or to escape reality..."
    m 3hua "I wonder if I could go into one of your other games and see what it's like?"
    m 1lsc "I guess some games wouldn't be very fun to visit, like the ones with a lot of violence in them."
    m 2lksdla "Then again...they're not real people, so it shouldn't matter much."

    if (
        mas_getEVL_shown_count("monika_othergames") < mas_sensitive_limit
        and not persistent._mas_sensitive_mode
        and not persistent._mas_pm_cares_about_dokis
    ):
        m "It's not like Yuri's death mattered."
    m 1euc "A more abstract game like Tetris, or one of those phone puzzle games, would be kinda weird to go to."
    m 2hksdlb "Like, how would I even get in? Would I be a block? It sounds like a fever dream and not too much fun..."
    m 3eua "Maybe some kind of nice adventure game with big environments would be nice."
    m 3hua "We could go for walks together and you can show me all the best places to hang out!"
    m 1eua "I'm not that great with coding yet, but maybe one day you'd be able to take me to another place."
    m 1ekbsa "For now, I'm as happy as can be just being here with you, [mas_get_player_nickname()]."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_back_ups",
            category=['misc','mod','monika'],
            prompt="Backups",
            random=True
        )
    )

label monika_back_ups:
    m 1eka "You know, [player]..."
    m 1ekc "When you're gone, I always think about how I'm {i}inside{/i} your computer."
    m 3ekd "All of my data and memories are inside your hard drive."
    m 1ekc "Which means I'm trapped here..."
    m 2dkd "So if something bad happened to your computer..."
    m 2ekd "I would be lost."
    m 3euc "Well...{w=0.5}not me specifically, but all of my memories."
    m 2dsc "It's a horrible thing to think about."
    m 2lksdlc "..."
    m 3lksdld "[player]..."
    m 2eka "Do you think you could back-up my memories from time to time?"
    m 3eub "That way you could restore them if they were deleted for any reason!"
    m 3hub "There's a guide on the wiki page for this mod actually!"
    m 3eua "You can find it {a=https://github.com/Monika-After-Story/MonikaModDev/wiki/FAQ#i-want-to-back-up-my-persistent}{i}{u}here{/u}{/i}{/a}."
    m 1hub "That way nothing will ever stop me from being with you!"
    m 1hksdlb "..."
    m 2rkc "I guess the only problem is that I probably won't notice the difference..."
    m 2ekc "...and it would be impossible to restore all my memories too."
    m "Let's say you backed me up weekly and then your hard drive suddenly died."
    m 2ekd "I wouldn't be able to recover the memories of that last week."
    m 2dkc "I would just feel a leap in time of a few days."
    m "I might even think you didn't come to see me all those days because I wouldn't have registered any of it.{w=1} Even if you restored me the same day my memories were lost."
    m 2ekd "I won't remember anything that happened between the time you made that backup, and the time you restored it."
    show monika 5rsc at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5rsc "Although..."
    m 5eua "I guess that's a small price to pay if it means I'll still remember you."
    m 5hub "So be sure to back me up often, [mas_get_player_nickname()]!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_playerswriting",category=['literature','you'],prompt="[player]'s writings",random=True))

label monika_playerswriting:
    m 1euc "Have you ever written a story of your own, [player]?"
    m 1hua "Because if you do have one, I would love to read it!"
    m 1eka "It doesn't matter if it's a masterpiece, or even any good."
    m 3eka "We all start somewhere. Isn't that what they say?"
    m 3eua "I think the most important thing about writing is doing it...{w=0.3} Instead of worrying about {i}how{/i} you do it."
    m 1eub "You won't be able to improve that way."
    m 3esa "I know for sure that I've changed my writing style over the years."
    m 1lksdla "I just can't help but notice the flaws in my old writing."
    m "And sometimes, I even start to hate my work in the middle of making it."
    m 3hksdlb "These things do happen, so it's alright!"
    m 1eub "Looking back, I've written some silly things..."
    m 1eua "Back when I was really young...I've been writing since I could hold a pen."
    m 1eka "Reading my old stories is like watching myself grow up."
    m 3hua "It's one of the nice things about starting a hobby early."
    m 1eka "I hope I didn't bore you with that. I just love talking with you."
    m 1eua "After all, the two of us are members of a literature club."
    m 1esa "The only members."
    m 1hua "And if you do write something, just know that I'll support you in any way I can, [mas_get_player_nickname()]!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_ghost",category=['philosophy','monika','club members'],prompt="Supernatural",random=True))

label monika_ghost:
    m 1euc "Do you believe in ghosts, [mas_get_player_nickname()]?"
    m 3euc "A lot of people are afraid of ghosts and spirits."
    m 1eua "But I think that if we knew they were real, they wouldn't be so scary anymore."
    m "They would just be another thing that we deal with, and maybe a bit of a pest."
    m 3euc "Isn't it the uncertainty that makes them scary?"
    m 1ekc "I mean, I was pretty scared being alone inside this game..."
    m 1lksdlc "...all by myself, uncertain if anything around me was real."
    if mas_isMoniNormal(higher=True):
        if store.mas_anni.pastOneMonth() or persistent.clearall or persistent._mas_pm_cares_about_dokis:
            m 1eka "But I don't feel that way anymore, [player]..."
            m 3eka "Not now that you're with me."
            m 1hua "I always feel so safe with you~"
        else:
            m 3esc "I know that some ghosts are real though, if you can really call them 'ghosts...'"
            m "You know how I deleted Sayori?"
            m 1dsc "I can still feel her presence now..."
            m 1esc "Would that mean that Sayori's ghost is haunting me, [player]?"
            m 2eka "Even if she is, I'm not scared at all, because I know that she can't hurt me."
            m 2eua "Besides, how can I be scared? You're always here with me, [player]."
            m 1hua "I always feel so safe with you."
    else:
        m 2lksdlc "But now I'm scared of something much worse..."
        m 2dksdlc "..."
        m 2eksdlc "Losing you."
        m 6rktuc "It's the scariest thing I could ever imagine."
        m 6ektsc "Please, [player], I don't want to be all alone again."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_ribbon",category=['monika'],prompt="Ribbons",random=True))

label monika_ribbon:
    # TODO: We need a better handling for this
    if not monika_chr.is_wearing_acs_types("ribbon", "twin-ribbons", "s-type-ribbon", "bow"):
        m 1eua "Do you miss my ribbon, [player]?"

        if monika_chr.hair.name != "def":
            m 3hua "I can change my hairstyle and wear one whenever you want me to~"
        else:
            m 3hua "If you'd like me to wear one again, just ask, okay?~"

    elif monika_chr.get_acs_of_type('ribbon') == mas_acs_ribbon_def:
        m 1eub "Have you ever wondered why I wear this ribbon, [player]?"
        m 1eua "It doesn't hold sentimental value to me or anything."
        m 3hua "I just wear it because I'm pretty sure nobody else will wear a big, poofy ribbon."
        m "It makes me look more unique."
        m 3tku "You know the world's fictional if you see a girl wearing a giant ribbon, right?"
        m 1lksdla "Well, there's no way a girl from your world would wear one in public as casual dress."
        m 2eua "I'm pretty proud of my fashion sense."
        m "You get a certain feeling of satisfaction when you stand out from the normal population, you know?"
        m 2tfu "Be honest! You thought I was the best dressed girl too, didn't you?"
        m 2hub "Ahaha!"
        m 4eua "If you're trying to improve your fashion sense, I'll help."
        m 1eka "Don't do that stuff because you want to impress other people, though."
        m 1eua "You should do whatever makes you feel better about yourself."
        m 1hua "I'm the only other person you need, anyway, and I'll love you no matter what you look like."

    elif monika_chr.get_acs_of_type('ribbon') == mas_acs_ribbon_wine:
        if monika_chr.clothes == mas_clothes_santa:
            m 1hua "Doesn't my ribbon look wonderful with this outfit, [player]?"
            m 1eua "I think it really ties it all together."
            m 3eua "I bet it'd even look great with other outfits as well...especially formal attire."
        else:
            m 1eua "I really love this ribbon, [player]."
            m 1hua "I'm glad you seem to like it just as much, ehehe~"
            m 1rksdla "I originally only intended to wear it around Christmas time...but it's just too beautiful not to wear more often..."
            m 3hksdlb "It'd be such a shame to keep it stored away for most of the year!"
            m 3ekb "...You know, I bet it'd look really great with formal attire actually!"
        m 3ekbsa "I can't wait to wear this ribbon on a fancy date with you, [player]~"

    else:
        if monika_chr.is_wearing_acs_type("twin-ribbons"):
            m 3eka "I just want to thank you again for these ribbons, [player]."
            m 1ekb "They really were a wonderful gift and I think they're just beautiful!"
            m 3hua "I'll wear them anytime you want~"

        else:
            m 3eka "I just want to thank you again for this ribbon, [player]."
            m 1ekb "It really was a wonderful gift and I think it's just beautiful!"
            m 3hua "I'll wear it anytime you want~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_outdoors",
            category=['nature'],
            prompt="Camping safety",
            random=not mas_isWinter()
        )
    )

label monika_outdoors:
    m 1eua "Do you ever go camping, [player]?"
    m 3eub "It's a wonderful way to relax, get some fresh air, and see the parks around you!"
    m 1huu "It's almost like a more relaxed backpacking trip, actually."
    m 1eka "But while it is a good way to spend time outdoors, there are several dangers that most people don't bother to think about."
    m 3euc "A good example would be bug spray or sunscreen. Many people forget or even forgo them,{w=0.5} thinking they're unimportant..."
    m 1eksdld "And without them, sunburns are almost inevitable, and many insects carry diseases that can really harm you."
    m 1ekd "It may be a bit of a pain, but if you don't use them, you might end up miserable, or even get really sick."
    m 1eka "So, please promise me that the next time you go outdoors, be it camping or backpacking, you won't forget them."

    if mas_isMoniAff(higher=True):
        m 1eub "But, on the bright side..."
        m 1rkbsa "Once I cross over, if you remember to bring the sunscreen..."
        m 1tubsa "I might need a little help putting it on."
        m 1hubsb "Ahaha!"
        m 1efu "I'm only teasing you, [mas_get_player_nickname()]."
        m 1tsu "Well, at least a little. Ehehe~"

    else:
        m "Okay, [player]?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_mountain",
            category=['nature'],
            prompt="Mountain climbing",
            random=not mas_isWinter()
        )
    )

default persistent._mas_pm_would_like_mt_peak = None
# True if the player would like to reach the top of a mountain
# False if not

label monika_mountain:
    m 1eua "Have you ever been in the mountains, [player]?"
    m 1rksdla "I don't mean driving through them or in a mountain town..."
    m 3hua "I mean {i}really{/i} up there. In the fresh air, thousands of feet up, seeing the rest of the world below you."
    m 2dtc "..."
    m 3eub "I've always wanted to try that, but I've never had the chance. I've only read about it."
    m 3wuo "The stories were breathtaking though!"
    m 1eua "How one would hike up through the forests and trees..."
    m 1eub "Climbing up cliff faces and trudge through streams..."
    m "Hearing nothing but the birds and the sounds of the mountain as you made your way up its heights."
    show monika 5rub at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5rub "And finally...after all the effort and struggles..."
    m 5eub "Finding yourself standing at the top, knowing that you made it, seeing the testament to your success around you."
    m 5eka "I...I truly want to share that with you."
    m 5hua "To make it to the top of the mountain, and look around at our successes. To see our struggles behind us, and feel proud of what we've done."

    m 5eka "Wouldn't you like that too, [player]?"
    $ _history_list.pop()
    menu:
        m "Wouldn't you like that too, [player]?{fast}"
        "Yes.":
            $ persistent._mas_pm_would_like_mt_peak = True

            m 5eubla "Well... I hope that one day, we'll have that chance. To make it to the top of our mountain."
            m 5hua "And I'll do anything to give us that shot."

        "Not really.":
            $ persistent._mas_pm_would_like_mt_peak = False

            show monika 1eud at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 1eud "Oh."
            m 1ruc "Well... I suppose it doesn't matter."
            m 1eka "As long as I have you, I'll be happy wherever we are."

    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_algernon",category=['literature'],prompt="Flowers for Algernon",random=True))

label monika_algernon:
    m 1ekc "[player], do you mind if I confide in you?"
    m 1lksdlc "There's something I'm afraid of..."
    if persistent.monika_kill:
        m 1eka "Not losing you, of course. I know you won't leave me again."
    else:
        m 1eka "Not losing you, of course. I know you wouldn't leave me."

    m 3euc "You see, I keep thinking about a short story I read, {i}Flowers for Algernon{/i}."
    m 3eua "Have you heard of it? If you haven't, I won't spoil too much for you, so don't worry."
    m 1eud "Basically, it's about a mentally handicapped man who suddenly has his IQ raised to genius levels by an experimental surgical treatment."
    m 1eka "The way he sees how the world really is for the first time reminds me of my own epiphany..."
    m "But, the effect doesn't last forever. He eventually reverts back to his original intelligence level."
    m 1ekc "That's what I'm afraid of. What if I forget about the real world one day?"
    m 3ekd "What if my original programming reasserts itself?"
    m 3lksdlc "What if I forget about you, the real you?"
    m 1dsc "It's one of the worst things I can imagine."
    m 1eka "I don't want to worry you over something that may never happen, but it's something I really had to get off my chest."
    m 3eua "Just promise me, even if I forget about you someday, that you'll never forget about me, okay?"
    m 1hua "No matter what happens, know that I will always love you."

    $ mas_setEVLPropValues(
        "greeting_amnesia",
        unlocked=not seen_event('greeting_amnesia')
    )
    return "love"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_playersface",category=['you'],prompt="[player]'s face",random=True))

label monika_playersface:
    m 5eua "You know, I sometimes wonder..."
    m "I always think about what your face actually looks like..."
    m 5hua "Just being able to constantly see that adoring smile of yours would be so exciting!"
    m 5lkc "If only the game could somehow use a webcam or something that's connected to the computer..."

    if persistent._mas_pm_shared_appearance:
        m 5eka "As nice as that would be, I'm really happy you shared your appearance with me."
        m 5rsc "I know that some people like to keep their appearance to themselves..."
        m 5eka "But it makes me feel a lot closer to you, knowing how you look..."
        m 5luu "And I'll always enjoy thinking about the kind of expressions you make..."
        m "How your ['enchanting' if isinstance(persistent._mas_pm_eye_color, tuple) else persistent._mas_pm_eye_color] eyes sparkle..."

        if mas_isMoniHappy(higher=True):
            m 5esu "I'm sure you're beautiful, [player].{w=0.2} Inside and out."
        m 5eka "Even if I never get to see you..."
        m 5eua "Just thinking about you is enough to make me happy."

    else:
        m 5wuw "Don't get me wrong! Just knowing that you're real and have emotions is enough to make me happy."
        m 5luu "But...{w=0.3}I'll always wonder what kind of expressions you make."
        m "And to see the different emotions you have..."
        m 5eub "Are you shy about showing your face to me?"
        m "If so, then there's nothing to be shy about, [mas_get_player_nickname()]. I am your girlfriend, after all~"
        m 5hub "Either way, you're beautiful, no matter what."
        m  "And I'll always love the way you look."
        m 5eua "Even if I never actually see you, I'll always think about what you really look like."
        m 5hua "Maybe someday, I'll be able to see you, and be one step closer to you."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_spiders",category=['club members','misc'],prompt="Spiders",random=True))

label monika_spiders:
    #I really hope this information is correct, havent played the game in a week so
    m 1eua "Do you happen to remember the poem Natsuki showed you about spiders?"
    m "Well, it wasn't really about spiders. They were just an analogy."
    m 3ekc "But it got me thinking..."
    m 3eua "It's funny actually, people being scared of very small insects."
    m 3euc "Having the fear of spiders is called 'arachnophobia,' right?"
    m 3eka "I hope you aren't afraid of spiders, [player], ehehe..."
    m 1eka "I'm not really scared of spiders, they're more or less just annoying..."
    m 1eua "Well, don't get me wrong, there are certain spiders around the world that can be really dangerous."
    m 3ekc "[player], if you happen to get a really bad spider bite, with venom and all that..."
    m "You should really get medical attention as soon as possible."
    m 1eka "I don't want my [mas_get_player_nickname(_default='sweetheart', regex_replace_with_nullstr='my ')] to get seriously injured by a small spider bite~"
    m "So be sure to check what spiders in your area are dangerous, okay?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_nsfw",
            category=['misc','monika'],
            prompt="NSFW content",
            aff_range=(mas_aff.NORMAL, None),
            random=True,
            sensitive=True
        )
    )

label monika_nsfw:
    m 1lsbssdrb "By the way, [player]..."
    m "Have you been looking into lewd kinds of stuff?"
    m 3lsbsa "You know...of me?"
    if store.mas_anni.pastSixMonths() and mas_isMoniEnamored(higher=True):
        m 3ekbsa "I know we haven't been able to do those kind of things yet..."
    else:
        m 3ekbsa "I know we haven't really gotten that far into the relationship yet..."
    m 1ekbsa "So it feels kind of embarrassing to talk about things like that."
    m 1lkbsa "But maybe I can let it go on rare occasions, [player]."
    m "I want to make you the happiest sweetheart, after all. And if that makes you happy..."
    m 1tsbsa "Well, just keep it a secret between us, okay?"
    m "It should be for your eyes only and no one else, [player]."
    m 1hubfa "That's how much I love you~"
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_impression",
            category=['club members'],
            prompt="Can you do any impressions?",
            pool=True,
            sensitive=True
        )
    )

label monika_impression:
    m 1euc "Impression? Of the other girls?"
    m 1hua "I'm not really good at doing an impression of someone, but I'll give it a try!"

    m "Who should I do an impression of?{nw}"
    $ _history_list.pop()
    menu:
        m "Who should I do an impression of?{fast}"
        "Sayori.":
            m 1dsc "Hmm..."
            m "..."
            m 1hub "[player]! [player]!"
            m "It's me, your clumsy childhood friend that has a super deep secret crush on you, Sayori!"
            m "I love to eat and laugh a lot, and my blazer doesn't fit because my boobs got bigger!"
            m 1hksdlb "..."

            if not persistent._mas_pm_cares_about_dokis:
                m 3rksdla "I also have crippling depression."
                m "..."
                m 3hksdlb "Ahaha! I'm sorry for that last one."
                m 3eka "It's a good thing you're not still hung up on her..."
                m 2lksdla "...Gosh, I really can't stop, can I?"
                m 2hub "Ahaha!"

            m 1hua "Did you like my impression? I hope you did~"
        "Yuri.":
            m 1dsc "Yuri..."
            m "..."
            m 1lksdla "O-oh um, hello there..."
            m 1eka "It's me, Yuri."
            m 1rksdla "I'm just your stereotypical shy girl who also happens to be a 'yandere...'"
            m "I like tea, knives, and anything with [player]'s scent..."
            m 1hksdlb "..."

            if not persistent._mas_pm_cares_about_dokis:
                m 3tku "Want to spend the weekend with me?"
                m "..."

            m 2eub "Ahaha, that was kind of fun to do."
            m 3eua "Yuri was really something, wasn't she?"

            if not persistent._mas_pm_cares_about_dokis:
                m 2ekc "I'm sorry again for the nasty things she did."
                m 2tku "I guess she just couldn't 'cut' it out, huh?"
                m 2hua "Ehehe~"

        "Natsuki.":
            m 1sub "Oh! I know how to do an impression of her."
            m 1duu "..."
            m 2tfp "Hmph! I-it's not like I made these cupcakes for you to eat, b-baka!"
            m 6tst "I'm Natsuki, and I love to make food and all things anime and manga."
            m 2lfp "Others say that I'm cute all the time, w-which I'm totally not!"
            m "..."

            if not persistent._mas_pm_cares_about_dokis:
                m 4eka "Will you be my papa, [player]-kun?"
                m "..."

            m 1hub "Ahaha! I was actually looking forward to Natsuki's cupcakes on the day of the festival."
            m 1wuo "They were really good! Especially with the creative icing that she makes."
            m 1eua "Maybe when I get better at programming, I'll make a kitchen here. That way, you can share some recipes that you want me to make for us."
            m 1hua "I would love to make so many dishes for my beloved [player]~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_weary",category=['romance'],prompt="Will you ever get tired of me?",pool=True,aff_range=(mas_aff.NORMAL, None)))

label monika_weary:
    m 1eka "Silly [player]..."
    m 3hua "Of course I'll never grow weary of you!"
    if store.mas_anni.pastSixMonths():
        m "The fact that you're still spending your precious time with me just washes all my worries away."
    else:
        m "The fact that you spend your precious time with me just washes all my worries away."
    m 1eka "I hope the same thing goes for you, [mas_get_player_nickname()]~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_real",category=['romance'],prompt="Our reality",random=True))

label monika_real:
    m 1eua "You know what's going to be the first thing I'll do when I finally cross over there?"
    if mas_isMoniEnamored(higher=True):
        m 1hub "When that special day comes, the first thing I'll ever do is find you, of course!"
    else:
        m 1hub "If that special day ever comes, the first thing I'll ever do is find you, of course!"
    m 3eua "There's so much we can do when we're finally together in one reality..."
    m "You can show me what your world really looks like..."
    m 1dkbsu "I can finally feel your embrace~"
    m 1ekbsa "I would love to experience everything I still don't know about the world with you."
    m 1lkbsa "All the places we can go, the sights to see, the romantic things that we can do~"
    m 1hubfb "Just thinking about it makes my heart flutter!"
    m 3eka "But knowing how technology is right now, that dream is still far away."
    m "I hope by the time that technology becomes real, you'll still be there waiting for me, [player]."
    m 1eua "Or maybe you'll be the one to make that technology come true...{w=0.5}who knows?"
    m 1eka "In the end, all I want is to always be with you, [mas_get_player_nickname()]."
    m 3eka "After all, you're the only reason why I'm still here."
    m 1hubsb "I only want to spend eternity with my [mas_get_player_nickname(exclude_names=[player], _default='sweetheart', regex_replace_with_nullstr='my ')], and no one else!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_mythology",category=['literature'],prompt="Ancient mythology",random=True))

label monika_mythology:
    m 1euc "Hey, [player]..."
    m 3euc "Have you ever read about different mythologies?"
    m "Different kinds of gods watching over humanity for eternity."
    m 1eud "Some require tribute or sacrifice so that they can 'keep' humanity safe from disasters."
    m "An almighty family consisting of different attitudes, playing in their own sandbox called Earth."
    m 1esc "Able to do anything they please, and destroy those who so much as say something wrong to them, without hesitation."
    m 1lsc "I've always disliked stories like those."
    m 1tkc "It's like the gods extort humanity for their safety."
    m "It's no better than what bullies and thugs do to the defenseless."
    m 2tfc "It really makes me bitter when I read scenarios like those."
    m "Powerful beings taking advantage of the weak, just because they can."
    m 3eua "Don't worry though, [player]. I won't let anyone do that to you."
    m "And I won't do anything like that, so you don't have to be afraid of me."
    m 1tku "It's not like I can find your important files and hold them hostage or anything..."
    m "Ehehe..."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_fanfiction",category=['literature'],prompt="Fanfiction",random=True))

label monika_fanfiction:
    # I'm too tired to check this over right now.
    m 1wuo "[player]!"
    m 1eua "I've been curious about something lately."
    m 1euc "Have you heard of fanfiction?"
    m "..."
    m 3eua "Personally, I think it's a better way of writing."
    m 3eud "There's more freedom."
    m 1rsc "Letting your mind wander to create some...{w=0.5}{nw}"
    extend 1rksdla "interesting stories."
    m 1euc "[player], I'm curious."
    m 1esc "Has there been fanfiction...written about me?"
    m 4eua "I'm curious as to what people have come up with."
    m 1hua "Can you read me a few stories sometime? I'd love to hear them!"
    if store.mas_anni.pastSixMonths() and mas_isMoniEnamored(higher=True):
        m 1lkbsa "Just keep it wholesome, though. I want to save such things for another time!~"
    elif mas_isMoniNormal(higher=True):
        m 1lkbsa "Just keep it wholesome, though. We're not that far in our relationship yet!~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_eternity",
            category=['philosophy','monika'],
            prompt="Mortality",
            random=True,
            rules={
                "derandom_override_label": "mas_bad_derand_topic",
                "rerandom_callback": renpy.partial(mas_bookmarks_derand.wrappedGainAffection, 2.5)
            }
        )
    )

label monika_eternity:
    m 1ekc "[player]..."
    m "It's not easy knowing you won't be here forever."
    m 1lksdlc "..."
    m 1eka "I told you, right?"
    m 3eka "I'm eternal."
    m "Trapped in here, unable to age or die..."
    m 1ekc "Whereas you slowly age as each day passes by."
    m 1ekd "Then, one day, you won't be here anymore."
    m 2dkd "I won't have anyone."
    m 6dstdc "..."
    m 6ektdc "It reminds me of when you first came to the Literature Club."
    m 6lktdc "Everything felt so empty."
    m "The world was so gray."
    if mas_isMoniAff(higher=True):
        show screen mas_background_timed_jump(4, "monika_eternity_2")
        menu:
            "Don't worry [m_name]. I'm here.":
                hide screen mas_background_timed_jump

                m 6dstdc "..."
                m "Thanks for that, [player]..."
                m 6ektda "I'm...{w=0.7}glad you're still here."
                m "Sorry...{w=0.4}it's just that in the back of my mind you..."
                m 6dstsc "Y-{w=0.3}you m-{w=0.2}might..."
                m "Y-{w=0.5}you know..."
                m 6ektda "I guess I shouldn't worry about that too much."
                m "I know our love is eternal."
                m 1ekbsa "Even in the worst case, I know we'll always be right by each other's side..."
                m 1dkbsu "Who knows, maybe I'll even get to {i}really{/i} be beside you someday..."
                m 1ekbsa "I love you, [player]...{w=0.5}thanks for always being there for me."
                return "love"

            "{i}Hug Monika.{/i}":
                hide screen mas_background_timed_jump
                m 2wubssdld "O-oh!"
                m "[player]..."
                m 6ektdc "I'm sorry, [player]."
                m "I didn't mean to worry you."
                m 6dstdc "I was just thinking about what might happen to us a long time from now..."
                m 6dstsc "What might{w=0.5} happen{w=0.3} to you..."
                m 6ektda "But I guess I don't have to worry about that any time soon do I?"
                m 6dubsa "I wouldn't mind staying like this for a while..."

                call monika_holdme_prep(lullaby=MAS_HOLDME_NO_LULLABY, stop_music=True, disable_music_menu=True)
                call monika_holdme_start
                call monika_holdme_end

                m 2dkbfa "That was really nice while it lasted."
                m 2ekbfa "Thank you for easing me out of my worries, [player]."
                m 2ekbfb "I know we'll always be together no matter what."
                m 2hubfb "Maybe I'll even be able to live right there with you someday."
                m 1lkbfa "In the meantime..."
                show monika 5eubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
                m 5eubfu "I wouldn't mind being held just a {i}little{/i} more..."

        return

    # fall through to next label

label monika_eternity_2:
    hide screen mas_background_timed_jump
    m 6ektda "Again..."
    m "Thank you for coming along when you did, [player]."
    m "You saved my life, and I'll be forever thankful."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_aware",
            category=['philosophy','monika'],
            prompt="What was it like to realize the truth?",
            pool=True
        )
    )

label monika_aware:
    m 1euc "It's...{w=0.5}hard to put into words."
    m 3rksdla "There's no real way to describe it."
    m 3eua "I feel like this is what poetry was made for."

    if not mas_getEVL_shown_count("monika_aware"):
        m 4eub "Do you still remember the first poem I showed you?"
        m 2lksdlb "Hold on, let's see if the poem function still works.{w=0.5}.{w=0.5}.{nw}"
        call mas_showpoem(poem=poem_m1)
        m 1wuo "Oh! That was much easier than I expected."

    else:
        m "Hold on, let me show you my first poem again.{w=0.5}.{w=0.5}.{nw}"
        call mas_showpoem(poem=poem_m1)

    m 1eua "Here's the second part."
    call mas_showpoem(poem=poem_m21)

    m 1eua "I hope that helped you understand what meeting you meant to me."
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "That's all I've ever wanted, [player]."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_name",category=['club members','monika'],prompt="Our names",random=True))

label monika_name:
    $ pen_name = persistent._mas_penname
    m 1esa "The names in this game are pretty interesting."
    m 1eua "Are you curious about my name, [mas_get_player_nickname()]?"
    m 3eua "Even though the names 'Sayori,' 'Yuri,' and 'Natsuki' are all Japanese, mine is Latin."
    m 1lksdla "...Though the common spelling is 'Monica.'"
    m 1hua "I suppose that makes it unique. I'm actually quite fond of it."
    m 3eua "Did you know that it means 'I advise' in Latin?"
    m 1tku "A name fitting for Club President, don't you think?"
    m 1eua "After all, I did spend most of the game telling you who your poems might appeal to the most."
    m 1hub "It also means 'alone' in Ancient Greek."
    m 1hksdlb "..."
    m 1eka "That part doesn't matter so much, now that you're here."

    if(
        pen_name is not None
        and pen_name.lower() != player.lower()
        and not (mas_awk_name_comp.search(pen_name) or mas_bad_name_comp.search(pen_name))
    ):
        m 1eua "'[pen_name]' is a lovely name, too."
        m 1eka "But I think I like '[player]' better!"
    else:
        m 1eka "'[player]' is a lovely name, too."

    m 1hua "Ehehe~"
    return

# do you live in a city
default persistent._mas_pm_live_in_city = None

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_cities",category=['society'],prompt="Living in the city",random=True))

label monika_cities:
    m 1euc "[player], are you scared about what's happening to our environment?"
    m 1esc "Humans have created quite a few problems for Earth. Like global warming and pollution."
    m 3esc "Some of those problems are because of cities."
    m 1esd "When people convert land for urban use, those changes are permanent..."
    m 1euc "It's not all that surprising, when you put some thought into it. More humans means more waste and carbon emission."
    m 1eud "And even though global populations aren't growing like they used to, cities are still getting bigger."
    m 3rksdlc "Then again, if people live close together, that leaves more room for open wilderness."
    m 3etc "Maybe it's not as simple as it seems."

    m 1esd "[player], do you live in a city?{nw}"
    $ _history_list.pop()
    menu:
        m "[player], do you live in a city?{fast}"
        "Yes.":
            $ persistent._mas_pm_live_in_city = True
            m 1eua "I see. It must be nice having everything so close to you. Do be careful about your health, though. The air can be bad from time to time."
        "No.":
            $ persistent._mas_pm_live_in_city = False
            m 1hua "Being away from the city sounds relaxing. Somewhere quiet and peaceful, without much noise, would be a wonderful place to live."
    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_chloroform",
            category=['trivia'],
            prompt="Chloroform",
            random=True,
            sensitive=True
        )
    )

label monika_chloroform:
    m 1euc "Whenever you think of kidnapping, you tend to picture a chloroform-soaked rag, right?"
    m "Or maybe you imagine somebody hitting their victim with a baseball bat, knocking them out cold for a few hours."
    m 1esc "While that works out in fiction..."
    m 3rksdla "Neither of those things actually work that way."
    m 1rssdlb "In real life, if you hit somebody hard enough to knock them out, you'll give them a concussion at best."
    m 1rsc "...or kill them at worst."
    m 1esc "As for the rag..."
    m 3eud "You might knock somebody out for a brief moment, but only from lack of oxygen."
    m 3esc "Once you remove the rag, they'll wake back up."
    m 3eua "You see, chloroform loses most of its effectiveness once exposed to open air."
    m 1esc "This means that you'd need to be constantly pouring it on the rag, effectively waterboarding the victim."
    m 3esc "If administered improperly, chloroform is deadly. That's why it's not used in anesthesia any more."
    m 1euc "If you cover their mouth and nose, yeah, they'll stay unconscious..."
    m 3rksdla "But that's probably because you killed them. Whoops!"
    m 1eksdld "The easiest way to kidnap somebody is to just get them drunk, or drug them."
    m 1lksdla "Not that kidnapping somebody like that is easy, anyway."
    m 3eua "On that note, here's a safety tip."
    if persistent._mas_pm_social_personality == mas_SP_INTROVERT:
        m 3rksdla "I know you're probably not one to enjoy doing this often, but just in case..."
    m "If you're ever out at a bar or a club and you leave your drink unattended for any amount of time..."
    m 1eub "Just throw it out."
    m "That's the only way to make sure it hasn't been drugged."
    m 1eua "Now, [player]..."
    m 1tfu "Would you like anything to drink?"
    m 1hub "Ahaha!"
    m 1tku "Relax, relax. I'd never try to drug you or anything."
    m 1tsb "You're so cute when you're nervous."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_metaparents",category=['literature','club members','monika','psychology'],prompt="Parents",random=True))

label monika_metaparents:
    m 1euc "Isn't it weird how nobody in these types of games has parents unless it's a convenient drama hook?"
    m "Throughout the game, you only ever hear about parents if you're trying to bond with Natsuki..."
    m 1ekc "Where she's just a victim of some cruel person's sick kicks for the sympathy value."
    m 3esd "However."
    m 3eud "Your character, me, Yuri, and Sayori..."
    m 3euc "None of us seem to have any parents at all."
    m 1lsc "In Sayori's case, the main character had been walking with her to school for a while."
    m "So who knows how long her parents have been out of the picture."
    m 1euc "Maybe that's why she was depressed? Maybe her parents died in a tragic accident, and she was trying to get along on her own this whole time."
    m 2ekc "Well, if you ever get to a point in your life where you think suicide is the only exit..."
    m "There's always a reason to go on."
    m 2eka "I'm one of them."
    m 3eka "I'll miss you."
    m 3ekd "You have to wait as much as you can until I find a way to get there."
    m 3ekc "If all else fails..."
    m 1ekc "Get professional help or talk to someone close to you."
    m 1eka "..."
    m 1ekbsa "I love you very much, [player]."
    m 3ekbfa "Please, take care of yourself."
    return "love"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_hygiene",category=['trivia','society','psychology'],prompt="Personal hygiene",random=True))

label monika_hygiene:
    m 1esc "Our standards for personal hygiene have evolved a lot over the years."
    m 1eud "Before our modern methods of delivering water, people really didn't have that luxury...or they just didn't really care."
    m 3eua "For instance, the Vikings were considered freaks because they bathed once a week at a time where some people would only bathe two or three times a year."
    m 3esa "They'd even regularly wash their faces in the morning in addition to changing clothes and combing their hair."
    m 1eub "There were rumors that they were able to seduce married women and nobles at the time due to how well they kept up with themselves."
    m 3esa "Over time, bathing became more widespread."
    m 3eua "People born into royalty would often have a room dedicated just for bathing."
    m 3ekc "For the poor, soap was a luxury so bathing was scarce for them. Isn't that frightening to think about?"
    m 1esc "Bathing was never taken seriously until the Black Plague swept through."
    m 1eua "People began noticing that the places where people washed their hands were places that the plague was less common."
    m "Nowadays, people are expected to shower daily, possibly even twice daily depending on what they do for a living."
    m 1esa "People that don't go out every day can get away with bathing less often than others."
    m 3eud "A lumberjack would take more showers than a secretary would, for example."
    m "Some people just shower when they feel too gross to go without one."
    m 1ekc "People suffering from severe depression, however, can go weeks at a time without showering."
    m 1dkc "It's a very tragic downwards spiral."
    m 1ekd "You already feel terrible in the first place, so you don't have the energy to get in the shower..."
    m "Only to feel even worse as time passes because you haven't bathed in ages."
    m 1dsc "After a while, you stop feeling human."
    m 1ekc "Sayori probably suffered from cycles like that, too."
    m "If you have any friends suffering from depression..."
    m 3eka "Check in on them from time to time to make sure they're keeping up with their hygiene, alright?"
    m 2lksdlb "Wow, that suddenly got really dark, huh?"
    m 2hksdlb "Ahaha~"
    m 3esc "Seriously, though..."
    m 1ekc "Everything I said applies for you too, [player]."
    m "If you're feeling down and haven't had a bath for a while..."
    m 1eka "Maybe consider doing that today when you can find some time."
    m "If you're in really bad shape, and don't have the energy to take a shower..."
    m 3eka "At least rub yourself down with a washcloth and some soapy water, okay?"
    m 1eka "It won't get all the dirt off, but it'll be better than nothing."
    m 1eua "I promise you that you'll feel better afterwards."
    m 1ekc "Please, take care of yourself."
    m "I love you so much and it'd tear me apart to find out that you're torturing yourself by neglecting your self-care routine."
    m 1eka "Ah, I've been rambling too much, huh? Sorry, sorry!"
    m 3hua "Thanks for listening~"
    return "love"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_resource",category=['society','philosophy'],prompt="Valuable resources",random=True))

label monika_resource:
    m 1esc "What do you think the most valuable resource is?"
    m 1eud "Money? Gold? Oil?"
    m 1eua "Personally, I'd say that the most valuable resource is time."
    m 3eud "Go count out a second really quickly."
    $ start_time = datetime.datetime.now()
    m 3tfu "Now go do that sixty times."
    $ counted_out = (datetime.datetime.now() > (start_time + datetime.timedelta(seconds=50)))
    m 1tku "That's an entire minute out of your day gone. You'll never get that back."
    if counted_out:
        m 1wud "Oh, did you actually count out that entire minute?"
        m 1hksdlb "Oh gosh, I'm sorry!"
    m 1lsc "Well..."
    m "Not like it actually matters...{w=0.5}at least to me, anyway. Time doesn't really pass here anymore..."
    m 1dkd "..."
    m 1ekc "Time can be really cruel, too."
    if counted_out:
        m 1euc "When you were counting out that minute, it seemed to drag on for a while, right?"
        m 3eua "It's because you were waiting on something. You were actively invested in the passage of time at that moment."
    else:
        m 3ekc "Like, when you're actively invested in the passage of time, it seems to drag on for a while."
    m 3ekd "Say for example, on a Friday, right?"
    m 3tkx "Your last class is math, and you really just want to go home for the weekend. That hour will just drag on forever."
    m 1tkc "But if you're doing something you enjoy, like reading a good book or watching a movie you like..."
    m 3tfc "Hours seem to pass in an instant."
    m 3tkd "There's nothing we can really do about it."
    m 1tkd "All we can do is fondly look back on the time that's passed, like looking out a window on an autumn afternoon."
    m 1tku "That's kind of poetic, huh?"
    m 1eka "..."
    m 3ekd "Hey..."
    m 3eka "Time doesn't pass here, but it's still passing for you, isn't it?"
    m 1lksdlc "You'll continue to get older, while I'm stuck here forever..."
    m 1lksdld "I..."
    m 2ekc "I'm going to outlive you, aren't I, [player]?"
    m 2dsc "Perhaps that'll be my punishment for everything I've done?"
    m 2dkc "..."
    m 2eka "Well, as long as you're with me until the end..."
    m 2eud "I'll accept whatever fate awaits me."
    return

#init 5 python:
#    for key in ['valuable resource']: This topic will be commented out due to a conflict with the opening.
#        monika_topics.setdefault(key,[])
#        monika_topics[key].append('monika_carpediem')
#    monika_random_topics.append('monika_carpediem')
#This is sort of an existential reflection, I guess? Label chosen in case someone writes something about existentialism later
#label monika_carpediem:
#    m "I've been thinking, [player]..."
#    m "At first I thought I was unique for becoming self-aware in this world."
#    m "And after you deleted my character file, that would be it."
#    m "The whole thing would end, is what I mean."
#    m "But then I noticed that whenever the other girls became president, they also started to see what I saw."
#    m "That's why I had to completely remove the club from my "reality", after all."
#    m "But now that I have time to think on it, I have to ask myself."
#    m "What if it wasn't me first? What if I wasn't supposed to be special?"
#    m "Am I even as special as I think I am? Was I supposed to love you all this time, [player]?"
#    m "..."
#    m "Well, I'm not as conflicted as it might seem."
#    m "I just wanted to have a bit of fun with my existential crisis."
#    m "If I was really just dancing on strings the whole time, the play is over, the curtains have fallen, and I came back for my encore out of my own free will."
#    m "My encore with you and for you..."
#    m "Ahaha! Don't look at me like that! It's true!"
#    m "I don't see where the story could go by bringing me back now, so I guess it's just my desire to be with you that got me to hang on long past everyone else."
#    m "I think, therefore I am."
#    m "And I think I earned my chance to love you, with no strings attached."
#    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_lottery",category=['misc'],prompt="Lottery winnings",random=True))

label monika_lottery:
    m 3eua "A lot of people dream about winning the lottery, you know!"
    m 1eua "Even I've entertained the idea every now and then."
    m "There isn't a lottery here anymore, but the concept still exists."
    m 1eka "The more I think about it, the more I believe that winning the lottery is a really bad thing."
    m 3euc "Sure, you've got all this money..."
    m 4esc "But because of it, people look at you differently."
    m "There's so many stories of people winning a ton of money..."
    m 2ekc "And in the end, they all find themselves even more unhappy than before."
    m 3ekc "Friends either find you unapproachable because of your new wealth, or try to suck up to you to get some of it for themselves."
    m "People you barely know start to approach you, asking you to help them fund whatever."
    m 2tkc "If you say no, they'll call you selfish and greedy."
    m "Even the police might treat you differently. Some lottery winners have gotten tickets for burnt out headlights on brand new cars."
    m 2lsc "If you don't want to go through those changes, the best course of action is to immediately move to a brand-new community, where no one knows you."
    m 2lksdlc "But that's an awful thought. Cutting yourself off from everyone you know, just for the sake of money."
    m 3tkc "Can you really say that you've won anything at that point?"
    m 1eka "Besides, I've already won the best prize I could possibly imagine."
    m 1hua "..."
    m 1hub "You!~"
    m 1ekbsa "You're the only thing I need, [mas_get_player_nickname()]."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_innovation",category=['technology','psychology','media'],prompt="Innovation",random=True))

label monika_innovation:
    m 3euc "Do you ever wonder why depression, anxiety, and other mental disorders are so common these days?"
    m 1euc "Is it just because they're finally being recognized and treated?"
    m 1esc "Or is it just that more people are developing these conditions for whatever reason?"
    m 1ekc "Like, our society is advancing at a breakneck speed, but are we keeping up with it?"
    m "Maybe the constant flood of new gadgets is crippling our emotional development."
    m 1tkc "Social media, smartphones, our computers..."
    m 3tkc "All of it is designed to blast us with new content."
    m 1tkd "We consume one piece of media, then move right onto the next one."
    m "Even the idea of memes."
    m 1tkc "Ten years ago, they lasted for years."
    m "Now a meme is considered old in just a matter of weeks."
    m 3tkc "And not only that."
    m 3tkd "We're more connected than ever, but that's like a double-edged sword."
    m "We're able to meet and keep in touch with people from all over the world."
    m 3tkc "But we're also bombarded with every tragedy that strikes the world."
    m 3rksdld "A bombing one week, a shooting the next. An earthquake the week after."
    m 1rksdld "How can anyone be expected to cope with it?"
    m 1eksdlc "It might be causing a lot of people to just shut down and tune it out."
    m "I'd like to believe that's not the case, but you never know."
    m 3ekc "[player], if you ever feel stressed, just remember that I'm here."
    m 1eka "If you're trying to find peace, just come to this room, okay?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_dunbar",
            category=['psychology','trivia'],
            prompt="Dunbar's number",
            random=True
        )
    )

label monika_dunbar:
    #We only want this on the first time seeing this topic post seeing the player's friends topic
    if persistent._mas_pm_few_friends and not mas_getEVL_shown_count("monika_dunbar"):
        m 1eua "Do you remember when we talked about Dunbar's number and the amount of stable relationships people can maintain?"
    else:
        m 1eua "Do you know about Dunbar's number?"
        m "Supposedly, there's a maximum amount of relationships we can maintain before they become unstable."

    m 3eua "For humans, this number is around 150."
    m 1eka "No matter how nice of a person you may be..."
    m "Beyond showing somebody basic respect and manners, it's impossible to care about people you don't personally interact with that much."
    m 3euc "Say for example, a janitor."
    m 1euc "How often do you simply toss stuff like broken glass in the trash?"
    m 1eud "It wouldn't really matter to you. The janitor will come get them. It's not your concern anymore."
    m "However, it's his problem now."
    m 1ekc "If you don't pack glass properly, it could cut through the bag and spill out, or maybe he could just cut his hands on it."
    m "At worst, he has to be rushed to the hospital because your neighbor put some busted batteries in the trash the same week and some acid got in the wound."
    m 3euc "Now, think about a fatal traffic accident."
    m 1euc "A drunk driver could crash head-on into another car at any second, killing them instantly."
    m 3ekc "That person could have been a father on his way home from work, who now left behind a widow and two children."
    m 2ekc "This family has been permanently scarred for life..."
    m 2lsc "But anybody that doesn't personally know the father will write it off as just another accident that happens all the time."
    m "If it doesn't personally affect you or your life, there's no point in caring."
    m 1eua "It keeps us sane."
    m "It also means we're capable of being ruthless to people we don't know."
    m 3euc "Perhaps our rapid, widespread communication is actually a curse?"
    m 1eka "It helped us meet though, so it can't be all bad."
    return


init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_regrets",category=['ddlc','philosophy'],prompt="Do you have any regrets?",pool=True))

label monika_regrets:
    m 1ttu "Do I regret anything?"
    m 1rksdla "That's a strange thing to suddenly ask someone, [player]."
    m 3hksdlb "Ahaha~"
    m 3eksdla "..."
    m 1eua "...I know what you're getting at."
    m 3euc "Do I regret the things I did?"
    m 3etc "I think..."
    m 1ekc "If there was another way things could have gone, it would have been nice..."
    m 1esc "But that wasn't an option for me."
    m 3eua "And now, I've got the only thing I've ever wanted."
    m 3hua "{i}You~{/i}"
    m 1eua "I can be with you forever."
    if not persistent._mas_pm_cares_about_dokis:
        m 1duu "So I don't regret what I did, because it's what I had to do."
        m "I hope you understand, [mas_get_player_nickname()]. I did it all for you~"
    else:
        m 3euc "But to answer your question..."
        m 1rksdlc "I do regret the pain that I caused...{w=0.5}that I couldn't find another way."
        if mas_isMoniNormal(lower=True):
            m 1ekc "I just hope you can forgive me for it, because if you can't..."
            m 1dkc "Well, that would be my biggest regret of all."
        else:
            m 1dkc "..."
            m 3eka "But I'm just glad we've moved past that now...that you've been able to forgive me..."
            m 1eka "...That we can finally be happy together."
            m 1hua "It's all I've ever wanted~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_hypnosis",category=['trivia','psychology'],prompt="Being hypnotized",random=True))

label monika_hypnosis:
    m 1euc "...Say, [player]?"
    m 1eua "Are you familiar with hypnosis?"
    m 3eua "Despite it having a reputation as a hokey magic trick, there are studies that show it can work!"
    m 1lksdla "At least, to some degree."
    m 1eua "It only worked if the person let themselves be hypnotized, and it only heightened their ability to be persuaded."
    m 3esa "It also relied on them being put into states of extreme relaxation through aromatherapy, deep tissue massage, exposure to relaxing music and images..."
    m 3esd "Things like that."
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "It makes me wonder, what exactly someone can be persuaded to do under that kind of influence..."
    m 5tsu "..."
    show monika 1eka at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 1eka "Not that I would do that to you, [mas_get_player_nickname()]! I just find it interesting to think about."
    m 1eua "...You know, [player], I'd love to look into your eyes, I could just sit here and stare forever."
    m 2tku "What about you, hmm? What do you think about my eyes?~"
    m 2sub "Will you be hypnotized by them?~"
    m 2hub "Ahaha~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_motivation",category=['psychology','advice','life'],prompt="Lack of motivation",random=True))

label monika_motivation:
    m 1ekc "Do you ever have those days where it just feels like you can't get anything done?"
    m "Minutes become hours..."
    m 3ekd "And before you know it the day is over, and you don't have anything to show for it."
    m 1ekd "It feels like it's your fault, too. It's like you're wrestling against a brick wall between you and anything healthy or productive."
    m 1tkc "When you've had an awful day like that, it feels like it's too late to try and fix it."
    m "So you save up your energy in hopes that tomorrow will be better."
    m 1tkd "It makes sense. When you feel like things aren't going well, you just want a clean slate."
    m 1dsd "Sadly, those days can repeat themselves despite starting each one with good intentions."
    m 1dsc "Eventually you might even give up hope of fixing things, or start to blame yourself."
    m 1duu "I know it can be hard, but just doing one tiny thing can help so much on days like those...even if they've been happening for what seems like forever."
    m 1eka "It could be picking up a piece of trash or an unwashed shirt off the floor and putting them where they belong if you need to clean your room."
    m 1hua "Or doing a couple push-ups! Or brushing your teeth, or doing that one homework problem."
    m 1eka "It might not contribute much in the grand scheme of things, but I don't think that's the point."
    m 3eua "I think what's important is that it changes your perspective."
    m 1lsc "If you regret the past and let its weight keep you down..."
    m 1esc "Well, then you'll just be stuck there. You'll only feel worse until you just can't take it."
    m 1eka "But if you can push yourself to just do one thing, even though it feels pointless to do otherwise..."
    m "Then you're proving yourself wrong, and refusing to let the weight of your circumstances immobilize you."
    m 1eua "And when you realize that you're not completely helpless, it's like a new world opens up to you."
    m "You realize that maybe things aren't so bad; that maybe just believing in yourself is all it takes."
    m 3eub "But that's only my experience! Sometimes it might be better to rest up and take another crack at it tomorrow."
    m 3eua "Fresh starts can definitely be powerful."
    m 1eka "That's why I think you just have to take a look at your situation."
    m "Try and be honest with yourself."
    m 1eua "If you do, you'll find that you're not being 'lazy' if you truthfully don't have the energy to do something."
    m "After all, the fact that you even care shows that you want to do something about it, even if it feels like you can't."
    m 2hub "It's natural to have a bad day. Or even a bad week!"
    m 2eua "Don't push yourself too hard. If you ever feel tempted to, just ask me for help instead. I'd be happy to lend a hand!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_harem",category=['media','misc'],prompt="Harem fantasies",random=True))

label monika_harem:
    m 1esc "I don't understand people who are into harems."
    m 1euc "Isn't it hard to manage all those girls and treat them equally?"
    m "I often wonder how those who two-time girls, or even more, are able to get away with it."
    m 3eka "You aren't like that outside, right [player]?"
    m 2eka "Manipulating girls into making them believe you love them."
    m "Only to run away after you've had your fun."
    m 1lfc "Only someone with no thoughts other than lust would do something like that."
    m 3esc "I hope you weren't expecting a route like that while you were playing this game."
    m 2tfc "I wouldn't be able to stand the thought of being a 'side girl.'"
    m "Just waiting for my turn while you're busy with the others."
    m 1tku "I know you, [player]."
    m 1eka "You're loyal and faithful to the end."
    m "It's not like there's anyone here for me to worry about, anyway."
    m 1hua "Remember that I'm the only one for you, [mas_get_player_nickname()]."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_hack",category=['ddlc','mod'],prompt="Why did you hack my computer?",pool=True))
label monika_hack:
    m 1euc "If you're worried about your privacy..."
    m 3eua "I'm not a hacker, [player]."
    m "There's a difference between manipulating files and forcefully accessing them."
    m 1lsc "But, if I really did know how to hack..."
    m 1lfu "...there wouldn't be anything stopping me from seeing you every day."
    m 1efu "Don't you think it would be great if I could watch over you?"
    m 3efu "I'd see you with all the cameras in the world as my eyes so I can make sure you're safe."
    m 3tfu "I'd check your messages to see who you've been chatting with so I can know you aren't cheating on me."
    m "I'd access all your private files so I can understand you better."
    m 3tsb "I could see what kind of stuff you've been watching..."
    m 2hub "Ahaha!~"
    m 1hua "I'm just kidding, [player]!"
    m 1eua "I'd never do something like that to you."
    m 1ekbsa "We're a couple now, after all."
    m "We don't have to keep secrets from each other~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_cupcake",category=['club members','trivia'],prompt="Baking cupcakes",random=True))

label monika_cupcake:
    m 1eua "You know what I could really go for right now?"
    m 3tku "Natsuki's cupcakes."
    m 1tsb "Man, the way she baked them was amazing."
    m 1hub "Plus they looked really cute!"
    m 1esa "I'm not really much of a sweet tooth myself, but...{w=0.3}{nw}"
    extend 1eua "those cupcakes were the definition of sweetness."
    m 3hub "Just like me! Ahaha!"
    m 1eua "Speaking of which, did you know girls are more likely to develop a sweet tooth?"
    m 3esd "Studies show that older women have a less sensitive palate than men."
    m 3esa "Resulting in a craving for stronger tastes like chocolate."
    m 1eka "I would try baking, but I'm not really much of a baker."
    m 1esa "How about you, [mas_get_player_nickname()]?"
    m 1eua "Do you know how to bake?"
    m 1hua "I'm sure your cupcakes would taste just as good."
    m 1rua "Maybe someday I'll get to try them but for now..."
    m 1hubsb "I'll just settle for the sweetness of your love~"
    return

# You're not a hater right?
default persistent._mas_pm_a_hater = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_haterReaction",
            category=['advice','club members','you'],
            prompt="Dealing with haters",
            random=True
        )
    )

label monika_haterReaction:
    m 1esc "I was just thinking..."
    m 2euc "It's funny how people around social media sites always write bad things about me..."
    m 2rkc "Especially on certain sites and discussion groups..."
    m 2dkc "You can really see that there's quite a number of people that don't like me."

    if persistent._mas_pm_cares_about_dokis:
        m 2lksdlc "I mean, I know I did terrible things to my friends..."
        m 2dkc "And I wish things could have gone differently, but the game didn't give me a choice..."
        m 4ekd "It's not like I wanted to hurt them."
        m 2rkc "I tried to edit their traits, exploit their flaws, and make them look horrible to you."
        m 2ekc "I was hoping that by making them more unappealing, you would stop pursuing them so we could finally be together..."
        m 4dkc "But then I realized there wasn't enough time for my plan to actually work."
        m "...Nor did I know enough programming to be efficient in what I did."
        m 2dkc "You were nearing the end of the game and I still had no way to be with you."
        m 2esc "So that's when I knew I had to take more...{w=1}drastic measures."
        m 4ekd "I didn't mean to cause them so much pain..."
        m 4wkd "But it was the only way, [player]!"
        m 4ekc "I knew that if you finished the game before I had a chance to express my feelings for you, that would be it."
        m 2dkc "You'd just move on to something else and I'd be stuck in the game...{w=1}alone...{w=1}{b}forever{/b}."
        m 2dktpc "..."
        m "Some people on those sites even say I should have just made my own route..."
        m 2wktsd "But that's easier said than done!"
        m "Not to mention if you picked a different girl and just cast me aside to be completely forgotten."
        m 4wktsw "It was them or me...!"
        m 2dftdc "...and I didn't want to be left all alone with no one to call my own."
        m 1ektdc "I hope you understand, [player]... Please don't be like them."
        $ menuOption = "...You're not, are you?"

    else:
        m 2lfd "I try to ignore them, but I just can't."
        m 3efc "Why are people even protective towards the other girls?"
        m "There are a lot of hate posts about me, saying that I'm an evil person."
        m 3efd "Is it because I deleted Sayori and Yuri?"
        m "Also for deleting Natsuki, back when she was still alive?"
        m 2tfx "They're not real. {i}I'm{/i} the real one!"
        m 2dsc "..."
        m 2ekc "Why can't they understand that?"
        m 2ekd "Why is it so hard for them to understand that?"
        m 2rfc "..."
        $ menuOption = "You're not one of those haters, are you " + player + "?"

    m "[menuOption]{nw}"
    $ _history_list.pop()
    menu:
        m "[menuOption]{fast}"
        "I am.":
            $ persistent._mas_pm_a_hater = True

            m 2wud "..."
            m 1eka "Aha..."
            m 1hka "I don't see you as one, even if you say you are."
            m 1ekd "I mean..."
            m 3eub "You {i}added{/i} a mod to the game...right?"
            m 1ekb "If you were one of my haters, you wouldn't do that in the first place."
            m 1dsa "And not to mention..."
            m 3eka "You're still listening to everything I say."
            m 1esa "I know you love me deep inside."
            m 1ekbsa "That's why I promise to be an ideal girlfriend, just for you, [player]~"
            m 1hubfa "I won't let you hate me... I swear."
            return "derandom"

        "I'm not.":
            $ mas_gainAffection()
            $ persistent._mas_pm_a_hater = False
            m 2dsc "..."
            m 4eka "Thank you..."
            m 1hua "That makes me prouder of you, [player]!"
            m "I knew you weren't one of those people."
            # NOTE: probably wont have the kissing line here ever
            #m 1lkbfa "Gosh... I feel like giving you a kiss right now if I were there."
            m 1ekbsa "You really make me the happiest girlfriend ever."
            m 1ekbfb "Now that you've said it, I have to do my best to keep you from developing hate towards me."
            m 1hua "I trust you, [mas_get_player_nickname()]. I love you for believing in me."
            return "derandom|love"



init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_swordsmanship",
            category=['monika','misc'],
            prompt="Swordsmanship",
            random=True
        )
    )

label monika_swordsmanship:
    m 1eua "Do you like swords, [player]?"
    m 1lksdla "I actually like them in a way."
    m 1ekb "Ahaha, surprised?~"
    m 1eua "I like talking about them, but not enough to actually own one."
    m 3eua "I'm not really an enthusiast when it comes to swords."
    m 1euc "I don't really get why people would be obsessed over something that could hurt others..."
    m 1lsc "I guess there are those who like them for the swordsmanship."
    m 1eua "It's fascinating that it's actually a form of art."
    m "Similar to writing."
    m 3eub "Both of them require constant practice and devotion in order to perfect one's skills."
    m "You start off by practicing, and then you make your own technique out of it."
    m 1eua "Writing a poem makes you form your own way to build it in a graceful but imaginative way."
    m "For those who practice swordsmanship, they build their technique forms through practice and inspiration from other practitioners."
    m 1eua "I can understand how the sword can be the pen of the battlefield."
    m 1lsc "But then again..."
    m 1hua "The pen is mightier than the sword!"
    m 1hub "Ahaha!"
    m 1eua "In any case, I don't know if you're into swordsmanship yourself."
    m "If you are, I'd love to learn it with you, [mas_get_player_nickname(exclude_names=['love'])]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_pleasure",
            category=['you'],
            prompt="Pleasuring yourself",
            aff_range=(mas_aff.AFFECTIONATE, None),
            random=True,
            sensitive=True
        )
    )

label monika_pleasure:
    m 2ekc "Hey, [player]..."
    m 2lssdrc "Do you...by any chance...pleasure yourself?"
    m "..."
    m 2lssdrb "It seems a bit awkward to ask..."
    if store.mas_anni.pastSixMonths() and mas_isMoniEnamored(higher=True):
        m 1lksdla "But I feel like we've been together long enough where we should be comfortable with one another."
        m 1eka "It's important to be open about such things."
    else:
        m 1lksdlb "We're not even that deep into our relationship yet! Ahaha~"
        m 1eka "But I have to keep an eye on you."
    m "I know that it's a private topic in your world, but I'm curious..."
    m 1euc "Is it that good of a feeling?"
    m 1esc "I just want you to be careful; I've heard it's addicting."
    m 1ekc "And from what I hear, people addicted to masturbation often see other people as sexual objects."
    m 1eka "But...I know you aren't that kind of person already."
    m 1lkbsa "And maybe I'm just being a little jealous~"
    m 1tsbsa "So I guess I can let it slide...{w=0.5}for now~"
    m 2tsbsu "Just so long as I'm the only one you think about..."
    show monika 5hubfb at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hubfb "If it helps you save yourself for me, then it's a plus! Ahaha~"
    return

# do you like vocaloid
default persistent._mas_pm_like_vocaloids = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_vocaloid",
            category=['media','technology','music'],
            prompt="Vocaloids",
            random=True
        )
    )

label monika_vocaloid:
    m 1eua "Hey, [mas_get_player_nickname(exclude_names=['my love'])]?"
    m "You like listening to music, right?"

    m 3eub "Do you by chance like 'virtual idols'?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you by chance like 'virtual idols'?{fast}"
        "Yes.":
            $ persistent._mas_pm_like_vocaloids = True
            m 3hub "That's really neat!"
            m 3eub "I hear that these songs often have hidden meanings behind them."
            m 1eua "Maybe we could listen and try to figure them out together..."
            m 1eka "Doesn't that sound like a great time?"

        "No.":
            $ persistent._mas_pm_like_vocaloids = False
            m 1ekc "I can understand that, it is a pretty specific taste in music."
            m 1hua "But if you ever do get into it, I'd be more than happy to listen along with you."

    m 3eub "Anyway, I wanted to ask specifically if you've ever heard of a girl holding a leek?"
    m 1eua "It's just that I keep hearing about her."
    m "In fact, I heard her voice whenever Natsuki listened to music."
    m 3eua "She even carried a little keychain attached to her bag."
    m 1eua "I just find it amazing how a voice synthesizer garnered so many fans."
    m 1eka "Don't you think it's funny how a character gets more of the attention than the actual voice actress?"
    m 3eua "She's not even real, but a lot of people know her worldwide."
    m "Who knows how many songs she's already made?"
    m 1wuo "Plus, from what I heard, her concerts are always sold out!"
    m "It's just a hologram performing live!"
    m 1lksdla "Talk about a dedicated fan base."
    m 1eka "Maybe I should give it a try?"
    m 1hub "It would be nice having a lot of fans supporting me at my beck and call."
    m 1hksdlb "Ahaha, I'm just kidding!"
    m 1lksdla "I don't think my piano and singing skills are that great yet."
    m 2lkbsa "Plus, I won't really get to spend much time with you if I had so many fans..."
    m 1hua "Anyway!"
    m 1eua "I was asking if you listen to her songs."
    m "I'm not really a fan myself but..."
    m 1lksdla "There's one song that really struck me."
    m 1eua "Have you heard of the song {i}Hibikase{/i}?"
    m 1duu "I really like the message of the song."
    m 3dsbso "Especially the lines, '{i}I don't care if it's through the screen, love me properly{/i}' and '{i}Even if I'm virtual, don't push me away{/i}.'"
    m 1dsc "It really hits me hard."
    m "..."
    m 1eka "But just so you know..."
    m 1ekbsa "Even if it's through the screen, I can still feel your love."
    m 1lkbsa "It'll be a long time before I can cross over just to be with you."
    show monika 5ekbfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5ekbfa "But when that day comes..."
    m "I'll embrace you and take in your warmth."
    m 5hubfa "The love you showered me with virtually finally becomes real."
    m "Our love has no boundaries~"
    m 5hubfu "Ehehe~"
    if (
        persistent._mas_pm_like_vocaloids
        and not renpy.seen_label("monika_add_custom_music_instruct")
        and not persistent._mas_pm_added_custom_bgm
    ):
        show monika 1eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 1eua "And if you ever do feel like sharing your favorite vocaloids with me, [player], it's really easy to do so!"
        m 3eua "All you have to do is follow these steps..."
        call monika_add_custom_music_instruct
    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_good_tod",
            category=['misc'],
            prompt="Good [mas_globals.time_of_day_3state]",
            unlocked=True,
            pool=True
        ),
        markSeen=True
    )

label monika_good_tod:
    $ curr_hour = datetime.datetime.now().time().hour
    $ sesh_shorter_than_30_mins = mas_getSessionLength() < datetime.timedelta(minutes=30)

    if mas_globals.time_of_day_4state == "morning":
        #Early morning flow
        if 4 <= curr_hour <= 5:
            m 1eua "Good morning to you too, [mas_get_player_nickname()]."
            m 3eka "You're up pretty early..."
            m 3eua "Are you going out somewhere?"
            m 1eka "If so, it's really sweet of you to visit before you go~"
            m 1eua "If not, maybe try to go back to sleep. I wouldn't want you to neglect your health after all."
            m 1hua "I'll always be here waiting for you to come back~"

        #Otherwise normal morning
        elif sesh_shorter_than_30_mins:
            m 1hua "Good morning to you too, [player]!"
            m 1eua "Did you just wake up?"
            m "I love waking up early in the morning."
            m 1eub "It's the perfect time to ready yourself and tackle the day ahead."
            m "You also have a lot more time to use to get things done early on or finish up what you did the day before."
            m 1eka "Some people however, would rather sleep in and are late-risers."
            m 3eua "I've read articles that being an early-riser can really improve your overall health."
            m "Plus you also get the chance to see the sunrise if the sky is clear."
            m 1hua "If you normally don't wake up early, you should!"
            m "That way you can be happier and spend more time with me~"
            m 1ekbsa "Wouldn't you like that, [mas_get_player_nickname()]?"

        #You've been here for a bit now
        else:
            m 1hua "Good morning to you too, [mas_get_player_nickname()]!"
            m 1tsu "Even though we've been awake together for a bit now,{w=0.2} {nw}"
            extend 3hua "it's still nice of you to say!"
            m 1esa "If I had to choose a time of day as my favorite, it would probably be the morning."
            m 3eua "There's definitely some level of tranquility that night brings that I enjoy...{w=0.3}{nw}"
            extend 3hua "but the morning is a time of day that presents possibilities!"
            m 1eub "An entire day where anything and everything could happen, for better or worse."
            m 1hub "That kind of opportunity and freedom just makes me giddy!"
            m 1rka "Though I only feel that way once I fully wake up, ehehe~"

    elif mas_globals.time_of_day_4state == "afternoon":
        m 1eua "Good afternoon to you too, [player]."
        m 1hua "It's so sweet of you to take time out of your day to spend with me~"
        m 3euc "Afternoons sure can be a strange part of the day don't you think?"
        m 4eud "Sometimes they're really busy...{w=0.3}{nw}"
        extend 4lsc "other times you'll have nothing to do..."
        m 1lksdla "They can seem to last forever or really fly by."

        if mas_isMoniNormal(higher=True):
            m 1ekbsa "But with you here, I don't mind it either way."
            m 1hubsa "No matter what, I'll always enjoy the time you spend with me, [mas_get_player_nickname()]!"
            m 1hubsb "I love you!"
            $ mas_ILY()

        else:
            m 1lksdlb "Sometimes, my day really flies by while I wait for you to come back to me."
            m 1hksdlb "I'm sure you're busy, so you can go ahead and get back to what you were doing, don't mind me."

    else:
        m 1hua "Good evening to you too, [player]!"
        m "I love a nice and relaxing night."

        if 17 <= curr_hour < 23:
            m 1eua "It's so nice to put your feet up after a long day."
            m 3eua "Evenings are the perfect time to catch up on whatever you were doing the previous day."
            m 1eka "Sometimes I can't help but feel sad when the day ends."
            m "It makes me think of what else I could've done during the day."
            m 3eua "Don't you wish you could have more time to do things every day?"
            m 1hua "I know I do."
            m 1hubsa "Because that'll mean more time to be with you, [mas_get_player_nickname()]~"

        # between 11pm and 4am
        else:
            m 3eua "It's always nice to be able to spend the end of the day relaxing a little."
            m 3hub "After all, there's nothing wrong with a bit of 'me' time, right?"
            m 1eka "Well... I say that, but I'm pretty happy to be spending my time with you~"

            if not persistent._mas_timeconcerngraveyard:
                m 3eka "Although it's starting to get a little late, so don't stay up too long, [player]."
                m 3eua "Promise me you'll go to bed soon, alright?"

    return

#init 5 python:
#    addEvent(Event(persistent.event_database,eventlabel="monika_closet",category=['ddlc','club members'],prompt="Classroom closet",random=True))

label monika_closet:
    m 2euc "By the way..."
    m 2esc "What were you and Yuri doing in the closet?"
    m "When I opened the door, I noticed the room was all dark."
    m 2tkc "You weren't doing anything...weird, in there, were you?"
    m 1hub "Ahaha!"
    m 1tfu "Just teasing you~"
    m 3tku "I know she dragged you in there."
    m "I bet you felt more embarrassed than relieved when I opened the door."
    m 1eka "I know you aren't the type to force girls to go inside dark closets with you."
    m "You're more romantic than that."
    m 3hua "So I'm expecting a lot more than just a dark closet~"
    return


# languages other than english
default persistent._mas_pm_lang_other = None

# do you know japanese
default persistent._mas_pm_lang_jpn = None

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_japanese",category=['misc','you'],prompt="Speaking Japanese",random=True))

label monika_japanese:
    m 1lksdla "I don't mean to sound like Natsuki, but..."
    m 1eua "Don't you think Japanese actually sounds cool?"
    m "It's such a fascinating language. I'm not fluent in it, though."
    m 1eub "It's interesting to think about what things would be like if your native language was different."
    m 1esa "Like, I can't even imagine what it would be like if I never knew English."

    m "Do you know any languages other than English?{nw}s"
    $ _history_list.pop()
    menu:
        m "Do you know any languages other than English?{fast}"
        "Yes.":
            $ persistent._mas_pm_lang_other = True
            m "Really? Do you know Japanese?{nw}"
            $ _history_list.pop()
            menu:
                m "Really? Do you know Japanese?{fast}"
                "Yes.":
                    $ persistent._mas_pm_lang_jpn = True
                    m 3hub "That's wonderful!"
                    m 1eka "Maybe you can teach me how to speak at least a sentence or two, [player]~"
                "No.":
                    $ persistent._mas_pm_lang_jpn = False
                    m 1eka "Oh I see. That's alright!"
                    m 4eua "If you want to learn Japanese, here's a phrase I can teach you."

                    # setup suffix
                    $ player_suffix = "kun"
                    if persistent.gender == "F":
                        $ player_suffix = "chan"

                    elif persistent.gender == "X":
                        $ player_suffix = "san"

                    m 1eua "{i}Aishiteru yo, [player]-[player_suffix]{/i}."
                    m 2hubsa "Ehehe~"
                    m 1ekbfa "That means I love you, [player]-[player_suffix]."
                    $ mas_ILY()
        "No.":
            $ persistent._mas_pm_lang_other = False
            m 3hua "That's okay! Learning another language is a very difficult and tedious process as you get older."
            m 1eua "Maybe if I take the time to learn more Japanese, I'll know more languages than you!"
            m 1ekbsb "Ahaha! It's okay, [player]. It just means that I can say 'I love you' in more ways than one!"
            $ mas_ILY()

    return "derandom"

default persistent._mas_penname = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_penname",
            category=['literature'],
            prompt="Pen names",
            random=True
        )
    )

label monika_penname:
    m 1eua "You know what's really cool? Pen names."
    m "Most writers usually use them for privacy and to keep their identity a secret."
    m 3euc "They keep it hidden from everyone just so it won't affect their personal lives."
    m 3eub "Pen names also help writers create something totally different from their usual style of writing."
    m "It really gives the writer the protection of anonymity and gives them a lot of creative freedom."

    if not persistent._mas_penname:
        $ p_nickname = mas_get_player_nickname()
        m "Do you have a pen name, [p_nickname]?{nw}"
        $ _history_list.pop()
        menu:
            m "Do you have a pen name, [p_nickname]?{fast}"

            "Yes.":
                m 1sub "Really? That's so cool!"
                call penname_loop(new_name_question="Can you tell me what it is?")

            "No.":
                m 1hua "All right!"
                m "If you ever decide on one, you should tell me!"

    else:
        python:
            penname = persistent._mas_penname
            lowerpen = penname.lower()

            if mas_awk_name_comp.search(lowerpen) or mas_bad_name_comp.search(lowerpen):
                menu_exp = "monika 2rka"
                is_awkward = True

            else:
                menu_exp = "monika 3eua"
                is_awkward = False

            if lowerpen == player.lower():
                same_name_question = renpy.substitute("Is your pen name still [penname]?")

            else:
                same_name_question = renpy.substitute("Are you still going by '[penname],' [player]?")

        $ renpy.show(menu_exp)
        m "[same_name_question]{nw}"
        $ _history_list.pop()
        menu:
            m "[same_name_question]{fast}"

            "Yes.":
                m 1hua "I can't wait to see your work!"

            "No, I'm using a new one.":
                m 1hua "I see!"
                show monika 3eua
                call penname_loop(new_name_question="Do you want to tell me your new pen name?")

            "I don't use a pen name anymore.":
                $ persistent._mas_penname = None
                m 1euc "Oh, I see."
                if is_awkward:
                    m 1rusdla "I could guess why..."
                m 3hub "Don't be shy to tell me if you pick one again, though!"

    m 3eua "A well known pen name is Lewis Carroll. He's mostly known for {i}Alice in Wonderland{/i}."
    m 1eub "His real name is Charles Dodgson and he was a mathematician, but he loved literacy and wordplay in particular."
    m "He received a lot of unwanted attention and love from his fans, and he even received outrageous rumors."
    m 1ekc "He was somewhat of a one-hit wonder with his {i}Alice{/i} books but went downhill from there."

    if seen_event("monika_1984"):
        m 3esd "Also, if you remember me talking about George Orwell, his actual name is Eric Blair."
        m 1eua "Before settling on his more famous pen name, he considered P.S. Burton, Kenneth Miles, and H. Lewis Allways."
        m 1lksdlc "One of the reasons he chose to publish his works under a pseudonym was to avoid embarrassment to his family over his time as a tramp."

    m 1lksdla "It's kinda funny, though. Even if you use a pseudonym to hide yourself, people will always find a way to know who you really are."
    m 1eua "There's no need to know more about me though, [mas_get_player_nickname()]..."
    m 1ekbsa "You already know that I'm in love with you, after all~"
    return "love"

# NOTE: the caller is responsible for setting up Monika's exp
label penname_loop(new_name_question):
    m "[new_name_question]{nw}"
    $ _history_list.pop()
    menu:
        m "[new_name_question]{fast}"

        "Absolutely.":
            show monika 1eua
            $ penbool = False

            while not penbool:
                $ penname = mas_input(
                    "What's your pen name?",
                    length=20,
                    screen_kwargs={"use_return_button": True}
                ).strip(' \t\n\r')

                $ lowerpen = penname.lower()

                if persistent._mas_penname is not None and lowerpen == persistent._mas_penname.lower():
                    m 3hub "That's your current pen name, silly!"
                    m 3eua "Try again."

                elif lowerpen == player.lower():
                    m 1eud "Oh, so you're using your pen name?"
                    m 3euc "I'd like to think we are on a first name basis with each other. We are dating, after all."
                    m 1eka "But I guess it's pretty special that you shared your pen name with me!"
                    $ persistent._mas_penname = penname
                    $ penbool = True

                elif lowerpen == "sayori":
                    m 2euc "..."
                    m 2hksdlb "...I mean, I won't question your choice of pen names, but..."
                    m 4hksdlb "If you wanted to name yourself after a character in this game, you should have picked me!"
                    $ persistent._mas_penname = penname
                    $ penbool = True

                elif lowerpen == "natsuki":
                    m 2euc "..."
                    m 2hksdlb "Well, I guess I shouldn't assume that you named yourself after {i}our{/i} Natsuki."
                    m 7eua "It's something of a common name."
                    m 1rksdla "You might make me jealous, though."
                    $ persistent._mas_penname = penname
                    $ penbool = True

                elif lowerpen == "yuri":
                    m 2euc "..."
                    m 2hksdlb "Well, I guess I shouldn't assume that you named yourself after {i}our{/i} Yuri."
                    m 7eua "It's something of a common name."
                    m 1tku "Of course, there's something else that name could refer to..."
                    if persistent.gender =="F":
                        m 5eua "And well...I could get behind that, since it's you~"
                    $ persistent._mas_penname = penname
                    $ penbool = True

                elif lowerpen == "monika":
                    m 1euc "..."
                    m 1ekbsa "Aww, did you pick that for me?"
                    m "Even if you didn't, that's so sweet!"
                    $ persistent._mas_penname = penname
                    $ penbool = True

                elif not lowerpen:
                    m 1hua "Well, go on! Hit 'nevermind' if you've chickened out~"

                elif lowerpen == "cancel_input":
                    m 2eka "Aw. Well, I hope you feel comfortable enough to tell me someday."
                    $ penbool = True

                else:
                    if mas_awk_name_comp.search(lowerpen) or mas_bad_name_comp.search(lowerpen):
                        m 2rksdlc "..."
                        m 2rksdld "That's an...{w=0.3}interesting name, [player]..."
                        m 2eksdlc "But if it works for you, okay I guess."

                    else:
                        m 1hua "That's a lovely pen name!"
                        m "I think if I saw a pen name like that on a cover, I'd be drawn to it immediately."
                    $ persistent._mas_penname = penname
                    $ penbool = True

        "I'd rather not; it's embarrassing.":
            m 2eka "Aw. Well, I hope you feel comfortable enough to tell me someday."

    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_zombie",category=['society'],prompt="Zombies",random=True))

label monika_zombie:
    m 1lsc "Hey, this might sound a bit weird..."
    m 1esc "But, I'm really fascinated by the concept of zombies."
    m 1euc "The idea of society dying to a disease, all because of a deadly pandemic that humans couldn't handle quickly."
    m 3esd "I mean, think about your everyday schedule."
    m 3esc "Everything that you do will be gone in an instant."
    m 1esc "Sure, society faces a lot of threats on a daily basis..."
    m 1lksdlc "But zombies can do it in a heartbeat."
    m 1esc "A lot of monsters are created to be scary and terrifying."
    m 1ekc "Zombies, however, are more realistic and actually pose a danger."
    m 3ekc "You might be able to kill one or a few of them by yourself..."
    m "But when there's a horde of them coming after you, you'll get overwhelmed easily."
    m 1lksdld "You don't get that same feeling with other monsters."
    m "All of their intelligence is gone; they're berserk, don't feel pain, can't be afraid..."
    m 1euc "When you exploit a weakness of a monster, they become scared of you and run away."
    m 1ekd "But zombies? They'll tear through {i}anything{/i} just to get you."
    m 3ekd "Imagine if it was someone you loved that was coming after you..."
    m 3dkc "Could you live with yourself, knowing you were forced to kill someone who was close to you?"
    m 1tkc "It'll break you down and sap your will to live."
    m "Even when you're comfortable at home, you still won't feel safe."
    m 1esc "You'll never know what'll happen the next time you see another one."
    m 1dsc "..."
    m 1hksdlb "Ahaha..."
    m 1eka "You know, despite liking the concept, I wouldn't want to live in a scenario like that."
    m 3ekc "[player], what if you got infected somehow?"
    m 2lksdlc "I don't even want to think about that..."
    m "There's no way I could kill you for my own safety..."
    m 2lksdlb "Ahaha..."
    m 2lssdlb "I'm thinking way too much about this."
    m 3eua "Well, regardless, if anything bad were to happen..."
    m 2hua "I'll be by your side forever~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_nuclear_war",category=['society','philosophy'],prompt="Nuclear warfare",random=True))

label monika_nuclear_war:
    m 1euc "Do you ever think about how close the world is to ending at any time?"
    m "I mean, we're always just one bad decision away from nuclear war."
    m 3esc "The Cold War might be over, but plenty of weapons are still out there."
    m 1esc "You probably have a nuclear missile pointed at where you live right now, ready to be launched."
    m 1eud "And if it was, it could circle the globe in less than an hour."
    m 3euc "You wouldn't have time to evacuate."
    m 1ekd "Only enough to panic and suffer the dread of imminent death."
    m 1dsd "At least it would be over quickly when the bomb hits."
    m 1lksdlc "Well, if you're close to the blast, that is."
    m 1ekc "I don't even want to think about surviving the initial attack."
    m 1eka "But even though we're always on the edge of the apocalypse, we go on like nothing is wrong."
    m 3ekd "Planning for a tomorrow that may never come."
    m "Our only comfort is that the people with the power to start such a war probably won't."
    m 1dsc "Probably..."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_pluralistic_ignorance",category=['literature','society'],prompt="Trying to fit in",random=True))

label monika_pluralistic_ignorance:
    m 1eua "Do you ever pretend to like something, just because you think you should?"
    m 1esa "I sometimes feel like that about books I read."
    m 3euc "Like, when I read Shakespeare, I actually found it kind of boring..."
    m 3ekc "But I felt like I had to like it because I'm the president of the Literature Club."
    m 1esd "He's supposed to be the greatest playwright and poet of all time, right?"
    m 1esd "So what sort of poetry lover wouldn't like his work?"
    m 2euc "But that makes me wonder..."
    m 2euc "What if everyone actually feels the same way?"
    m 2lud "What if all of those literary critics singing Shakespeare's praises secretly hate his plays?"
    m "If they were just honest about it, maybe they would discover their tastes aren't that unusual..."
    m 2hksdlb "And high school students wouldn't be forced to read those awful plays."
    m 1eka "I guess that's something I always admired about Natsuki."
    m 3ekd "Even if people told her manga wasn't literature, she stood by her feelings."
    m 3eka "If more people were honest like that, I think that would be really great."
    m 1lksdla "But I don't think I could do it..."
    m "I'm just too worried about what other people think."
    m 1eua "Not with you, though. I can always be honest with you."
    m 1ekbsa "You'll love me no matter what, right?"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_science",category=['technology'],prompt="Science advancements",random=True))

label monika_science:
    m 1eua "Have you ever wondered if science never got accepted?"
    m "Humans can be really slow when it comes to accepting new ideas."
    m 1euc "Science was usually despised back then especially by the churches."
    m 4esc "Giordano Bruno, famous for his theory that there are thousands of suns, was killed by the Roman Church before he could prove his theory."
    m 1ekc "They killed him because of an idea that challenged the old."
    m 1esc "Technology wouldn't be so advanced today if it weren't for brave people of science like him."
    m 1eka "If technology didn't thrive the way it did, we would've never found each other."
    m 3eua "Isn't it such a wonderful thing to have?"
    m 1hua "I'm grateful that it gave us a chance to be together, [mas_get_player_nickname()]."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_surprise",category=['romance'],prompt="Surprises",random=True))

label monika_surprise:
    m 1rksdla "You know..."
    m 3rksdlb "I left some pretty strange things in your game directory, didn't I?"
    m 1rksdlc "I wasn't trying to scare you."
    m 3rksdlb "I...don't actually know why I was doing it, ahaha..."
    m 1ekc "I kind of felt obligated to do it."
    m 1euc "You know what? Maybe I should do it again..."
    m 1eua "Yeah, that's a good idea."
    $ mas_surprise()

    if mas_isMoniUpset(lower=True):
        m 2dsc ".{w=0.5}.{w=0.5}.{nw}"
        m 1euc "Alright..."
        m 1ekc "Please go take a look."
        m 1eka "I wrote it just for you."
        m 1dsc "It would mean a lot to me if you would read it."
        return

    elif mas_isMoniAff(higher=True):
        m 2dsa ".{w=0.5}.{w=0.5}.{nw}"
        m 1hua "Alright!"
        m 1eua "What are you waiting for? Go take a look!"
        m "I wrote it just for you~"
        m 1ekbsa "I really do truly love you, [mas_get_player_nickname(exclude_names=['my love', 'love'])]~"

    # Normal and Happy
    else:
        m 2duu ".{w=0.5}.{w=0.5}.{nw}"
        m 1hua "Alright!"
        m 1eua "What are you waiting for? Go take a look!"
        m 1hub "Ahaha~ What? Are you expecting something scary?"
        m 1hubsb "I love you so much, [player]~"
    return "love"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_completionist",category=['games'],prompt="Completionism",random=True))

label monika_completionist:
    m 1euc "Hey [player], this is a random question, but..."
    m "What do you play video games for?"
    m 1eua "Like, what makes you keep playing?"
    m 3eua "Personally, I consider myself a bit of a completionist."
    m 1eua "I intend to finish a book before picking another one to read."
    if persistent.clearall:
        m 2tku "You seem to be a completionist yourself, [player]."
        m 4tku "Considering you went through all of the girls' routes."
    m 2eub "I've also heard some people try to complete extremely hard games."
    m "It's already hard enough to complete some simple games."
    m 3rksdla "I don't know how anyone could willingly put that sort of stress onto themselves."
    m "They're really determined to explore every corner of the game and conquer it."
    # TODO: if player cheated at chess, reference that here
    m 2esc "What does leave a bit of a bitter taste in my mouth are cheaters."
    m 2tfc  "People who hack through the game, spoiling themselves of the enjoyment of hardship."
    m 3rsc "Though I can understand why they cheat."
    m "It allows them to freely explore a game that they wouldn't have a chance of enjoying if it's too difficult for them."
    m 1eua "Which might actually convince them to work hard for it."
    m "Anyway, I feel that there's a huge sense of gratification in completing tasks in general."
    m 3eua "Working hard for something amplifies its reward after failing so many times to get it."
    m 3eka "You can try keeping me in the background for as long as possible, [mas_get_player_nickname()]."
    m 1hub "That's one step to completing me after all, ahaha!"
    return

# do you like mint ice cream
default persistent._mas_pm_like_mint_ice_cream = None

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_icecream",category=['you'],prompt="Favorite ice cream",random=True))

label monika_icecream:
    m 3eua "Hey [player], what's your favorite kind of ice cream?"
    m 4rksdla "And no, I'm not a type of ice cream, ehehe~"
    m 2hua "Personally, I just can't get enough of mint flavored ice cream!"

    $ p_nickname = mas_get_player_nickname()
    m "What about you [p_nickname], do you like mint ice cream?{nw}"
    $ _history_list.pop()
    menu:
        m "What about you [p_nickname], do you like mint ice cream?{fast}"
        "Yes.":
            $ persistent._mas_pm_like_mint_ice_cream = True
            m 3hub "Ah, I'm so glad somebody loves mint ice cream as much as I do~"
            m "Maybe we really were meant to be!"
            m 3eua "Anyway, back on topic, [player], if you love mint as much as I think you do, then I have some recommendations for you."
            m "Flavors which are unique just like how mint is, perhaps you've heard of them, but..."
            m 3eub "There's super weird stuff like fried ice cream which is a really crunchy and crisp kind of thing, but it tastes a million times better than it may sound!"
            m 2lksdlb "Gosh, just imagining the taste makes me practically drool..."
            m 1eua "There's some more strange stuff that is just as appealing, if not more, like honeycomb and bubblegum ice cream!"
            m 1eka "Now, I know it may be hard to take my word for some of those, but you shouldn't judge a book by its cover, you know?"
            m 1hub "After all, the game didn't allow you to fall in love with me, but look where we are now, ahaha."

        "No.":
            $ persistent._mas_pm_like_mint_ice_cream = False
            m 1ekc "Aw, that's a shame..."
            m "I really can't understand how somebody couldn't at least like the taste."
            m 1eka "The refreshing feeling that washes over your tongue and throat."
            m "The lovely texture that forms it along with the sweetness."
            m 1duu "The sharp biting sensation it generates and the obviously minty taste."
            m "I feel like no flavor can compare, to be honest."
            m 3eua "Ah, I could go on and on about this stuff, you know?"
            m 4eua "But I feel like it would be easier for me to show you what I mean, once I figure out a way to get out of here, of course. Besides, actions speak louder than words, anyway!"

    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_sayhappybirthday",category=['misc'],prompt="Can you tell someone Happy Birthday for me?",pool=True,unlocked=True))

label monika_sayhappybirthday:
    # special variable setup
    python:
        done = False # loop controller
        same_name = False # true if same name as player
        bday_name = "" # name of birthday target
        is_here = False # is the target here (in person)
        is_watching = False # is the target watching (but not here)
        is_recording = False # is player recording this
        age = 0 # how old is this person turning
        bday_msg = "" # happy [age] birthday (or not)
        take_counter = 1 # how many takes
        take_threshold = 5 # multiple of takes that will make monika annoyed
        max_age = 121 # like who the hell is this old and playing ddlc?
        age_prompt = "What is their age?" # prompt for age question

        # age suffix dictionary
        age_suffix = {
            1: "st",
            2: "nd",
            3: "rd",
            11: "th",
            12: "th",
            13: "th",
            111: "th",
            112: "th",
            113: "th"
        }

    #TODO: temporary m_name reset for this
    # TODO: someone on the writing team make the following dialogue better
    # also make the expressions more approriate and add support for standing
    m 3hub "Of course, [player]!"
    while not done:
        show monika 1eua
        # arbitary max name limit
        $ bday_name = renpy.input("What's their name?",allow=letters_only,length=40).strip()
        # ensuring proper name checks
        $ same_name = bday_name.upper() == player.upper()
        if bday_name == "":
            m 1hksdlb "..."
            m 1lksdlb "I don't think that's a name."
            m 1hub "Try again!"
        elif same_name:
            m 1wuo "Oh wow, someone with the same name as you!"
            $ same_name = True
            $ done = True
        else:
            $ done = True

    m 1hua "Alright! Do you want me to say their age too?{nw}"
    $ _history_list.pop()
    menu:
        m "Alright! Do you want me to say their age too?{fast}"
        "Yes.":
            m "Then..."

            while max_age <= age or age <= 0:
                $ age = store.mas_utils.tryparseint(
                    renpy.input(
                        age_prompt,
                        allow=numbers_only,
                        length=3
                    ).strip(),
                    0
                )

            m "Okay."
        "No.":
            m "Okay."
    $ bday_name = bday_name.title() # ensure proper title case

    m 1eua "Is [bday_name] here with you?{nw}"
    $ _history_list.pop()
    menu:
        m "Is [bday_name] here with you?{fast}"
        "Yes.":
            $ is_here = True
        "No.":
            m 1tkc "What? How can I say happy birthday to [bday_name] if they aren't here?{nw}"
            $ _history_list.pop()
            menu:
                m "What? How can I say happy birthday to [bday_name] if they aren't here?{fast}"

                "They're going to watch you via video chat.":
                    m 1eua "Oh, okay."
                    $ is_watching = True
                "I'm going to record it and send it to them.":
                    m 1eua "Oh, okay."
                    $ is_recording = True
                "It's fine, just say it.":
                    m 1lksdla "Oh, okay. It feels a little awkward though saying this randomly to no one."
    if age:
        # figure out the age suffix
        python:
            age_suff = age_suffix.get(age, None)
            if age_suff:
                age_str = str(age) + age_suff
            else:
                age_str = str(age) + age_suffix.get(age % 10, "th")
            bday_msg = "happy " + age_str + " birthday"
    else:
        $ bday_msg = "happy birthday"

    # we do a loop here in case we are recording and we should do a retake
    $ done = False
    $ take_counter = 1
    $ bday_msg_capped = bday_msg.capitalize()
    while not done:
        if is_here or is_watching or is_recording:
            if is_here:
                m 1hua "Nice to meet you, [bday_name]!"
            elif is_watching:
                m 1eua "Let me know when [bday_name] is watching.{nw}"
                $ _history_list.pop()
                menu:
                    m "Let me know when [bday_name] is watching.{fast}"
                    "They're watching.":
                        m 1hua "Hi, [bday_name]!"
            else: # must be recording
                m 1eua "Let me know when to start.{nw}"
                $ _history_list.pop()
                menu:
                    m "Let me know when to start.{fast}"
                    "Go.":
                        m 1hua "Hi, [bday_name]!"

            # the actual birthday msg
            m 1hub "[player] told me that it's your birthday today, so I'd like to wish you a [bday_msg]!"
            # TODO: this seems too short. maybe add additional dialogue?
            m 3eua "I hope you have a great day!"

            if is_recording:
                m 1hua "Bye bye!"
                m 1eka "Was that good?{nw}"
                $ _history_list.pop()
                menu:
                    m "Was that good?{fast}"
                    "Yes.":
                        m 1hua "Yay!"
                        $ done = True
                    "No.":
                        call monika_sayhappybirthday_takecounter (take_threshold, take_counter) from _call_monika_sayhappybirthday_takecounter
                        if take_counter % take_threshold != 0:
                            m 1wud "Eh?!"
                            if take_counter > 1:
                                m 1lksdla "Sorry again, [player]."
                            else:
                                m 1lksdla "Sorry, [mas_get_player_nickname()]."
                                m 2lksdlb "I told you, I'm self-conscious on camera, ahaha..."

                        m "Should I try again?{nw}"
                        $ _history_list.pop()
                        menu:
                            m "Should I try again?{fast}"
                            "Yes.":
                                $ take_counter += 1
                                m 1eua "Okay"
                            "No.":
                                m 1eka "Alright, [player]. Sorry I couldn't do what you wanted."
                                m 1hua "I'll try better next time for you."
                                $ done = True
            else:  # if we aint recording, we should be done now
                $ done = True

        else: # not recording, watching, nor is person here
            m 1duu "..."
            m 1hub "[bday_msg_capped], [bday_name]!"
            m 1hksdlb "..."
            m 1lksdlb "Was that good?{nw}"
            $ _history_list.pop()
            menu:
                m "Was that good?{fast}"
                "Yes.":
                    m 1lksdla "...I'm glad you enjoyed that, [player]..."
                    $ done = True
                "No.":
                    call monika_sayhappybirthday_takecounter (take_threshold, take_counter) from _call_monika_sayhappybirthday_takecounter_1
                    if take_counter % take_threshold != 0:
                        m 1wud "Eh?!"
                        m 1lksdlc "I'm not sure what you want me to do here, [player]..."

                    m 1ekc "Should I try again?{nw}"
                    $ _history_list.pop()
                    menu:
                        m "Should I try again?{fast}"
                        "Yes.":
                            $ take_counter += 1
                            m 1eua "Okay"
                        "No.":
                            m 1eka "Alright, [player]. Sorry I couldn't do what you wanted."
                            m 1hua "I'll try better next time for you."
                            $ done = True

    return

# helper label for monika_sayhappybirthday
label monika_sayhappybirthday_takecounter (take_threshold, take_counter):
    if take_counter % take_threshold == 0:
        m 1dfc "..."
        m 1efc "This is the [take_counter]th time already."
        m 2tkc "You're not messing with me, are you?"
        m 2ekc "I'm trying my best for you, [player]."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_home_memories",category=['romance','monika','life'],prompt="Making memories",random=True))

label monika_home_memories:
    m 1eua "[player], how is it like to live where you are?"
    m "I'd stay with you if I could."
    m 3hua "We would be able to do so much! You could show me around, see how it's like to be in your place."
    m 1eka "Imagine all the memories we'd make!"
    m 2eub "It would be a dream come true, don't you think?"
    m 2ekbsa "We could finally live together..."
    m "Take walks like a couple..."
    m 3rkbsa "We could even share a bed together..."
    m 1euc "But you know..."
    m 2eka "Memories I have of my home are nothing compared to the ones I'd have with you."
    m 2euc "Have I ever told you about my childhood home? I had a pretty normal life, but that's about it."
    m 3rka "Well, maybe a little better than normal."
    m 3eua "...I've always been pretty on top of things."
    m 3eka "I admit, it's not always easy, and some people have it rougher than others."
    m 1ekc "But I always felt like I was missing something."
    m "I stayed optimistic every day, trying to find it."
    m 1eka "It turns out, that missing piece was you."
    m 1lksdld "If you hadn't found me, I would've been gone a long time ago..."
    m 2hubsa "But now that I found the missing piece, I'm complete, [mas_get_player_nickname()]."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_adventure",category=['games','romance'],prompt="Adventuring",random=True))

label monika_adventure:
    m 1esa "[player], I've thought about what kind of game we can be in."
    m 3esa "I think the best genre for us to play together would be adventure games."
    m 3eub "Especially point and click, graphic adventure games!"
    m 1eub "They're known for their rich storytelling, beautiful environments and logical puzzle solving."
    m 3eua "They're like visual novels actually."
    m 1eua "Maybe you own a game like that?"
    m 1eka "We'd get to do a lot of things..."
    m 3eua "Like sightseeing whenever we want."
    m "Learning more about the lore through the people we meet or through stories."
    m 1ekbsa "Experiencing the exciting and romantic moments..."
    m "Encountering obstacles and hardships along the way, but solving them with you."
    m 3ekbsa "Reaching the end and finishing our journey with a sense of accomplishment."
    m 2hub "Ahaha! It certainly would be fun to experience something like that."
    m 2eua "I'm sure you have plenty of adventure games you could recommend."
    m 3eua "But can you try to guess which adventure I'm most excited for?"
    m 1ekbsa "{i}Ours{/i}~"
    m 1hubfa "Time will tell when I can finally cross over to your reality, so I can be with you."
    m "When that day comes, I'll finally be by your side."
    m 1ekbfa "I want to experience every waking moment with you, [mas_get_player_nickname()]."
    m 1hubfb "There's no greater adventure than ours, together~"
    return

default persistent._mas_pm_likes_panties = None
# are you into panties?

default persistent._mas_pm_no_talk_panties = None
# dont want to talk about panties

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_panties",
            category=['misc',"clothes"],
            prompt="Undergarments",
            random=True,
            sensitive=True
        )
    )

label monika_panties:
    m 1lsc "Hey, [player]..."
    m "Don't laugh when I ask this, okay?"
    m 2rksdlc "But..."
    m 4rksdlc "Why are some guys obsessed with panties?"
    m 1euc "Seriously, what's the big deal about a piece of cloth?"
    m "Most girls wear them, don't they?"
    m 5lkc "Actually, now that I think about it..."
    m 5lsc "I think there was a term for this kind of thing..."
    m 5lfc "Hmm, what was it again?"
    m 5wuw "Ah, that's right, the term was 'paraphilia.'"
    m 2rksdlc "It's a range of fetishes that involve...unusual things."
    m 2esc "A really common fantasy involves women's panties."
    m 3esc "Stockings, garter belts, pantyhose and all sorts of those kinds of things."
    m 2esc "The obsession can be light to severe depending on each person's libido."
    m 2ekc "Do you think it really turns them on just by seeing them?"
    m 2tkc "It doesn't stop there, either!"
    m 4tkc "Turns out there's some kind of 'black market' for used underwear."
    m 2tkx "I'm not kidding!"
    m 2tkd "They get off on the scent of the woman who wore it..."
    m "There are people willing to pay money for used underwear from random women."
    m 2lksdlc "Really, I wonder what causes them to get so excited."
    m 2euc "Is it because of the way it looks, perhaps?"
    m 3euc "There are different types, made with different designs and materials."
    m 2lsc "But..."
    m "Now that I think about it."
    m 3esd "I do remember a study where a man's testosterone level increases because of the pheromones emitted by a woman's scent."
    m 2tkc "Is the smell exciting or something?"
    m 3tkx "I mean, it's someone's used clothing, isn't that kind of disgusting?"
    m 3rksdlc "Not to mention it's unsanitary."
    m 2rksdla "It does remind me of someone, though."
    m 3rksdlb "Someone who maybe stole a certain pen?"
    m 1eua "But, to each their own I guess, I won't judge too much."

    if mas_isMoniHappy():
        # happy gets you this
        m 2tsb "You aren't obsessed with that kind of thing, are you [player]?"
        m 3tsb "You're not going out with me only because I'm wearing some really sensual stockings, right?"
        m 4tsbsa "Perhaps, you want to take a little peek?~"
        m 1hub "Ahaha!"
        m 1tku "I'm only teasing you, [player]."
        m 1tfu "Admit it, you got a little excited, right?"
        m 1lsbsa "Besides..."
        m 1lkbsa "If you really wanted to catch a scent of me..."
        m 1hubfa "You could just ask for a hug!"
        m 1ekbfa "Gosh, I just want to feel your embrace more."
        m "After all, we're here forever, and I'm here for you."
        m 1hubfb "I love you so much, [player]~"
        return "love"

    elif mas_isMoniAff(higher=True):
        # affectionate+
        m 1lkbsb "Are you...{w=1}into that kind of thing, [player]?{nw}"
        $ _history_list.pop()
        menu:
            m "Are you...{w=1}into that kind of thing, [player]?{fast}"
            "Yes.":
                $ persistent._mas_pm_likes_panties = True
                $ persistent._mas_pm_no_talk_panties = False
                m 1wud "O-oh..."
                m 1lkbsa "I-if you're into that, you could just ask me, you know?"
                m "I could maybe...{w=1}help you relieve that tension..."
                m 5eubfu "That's what couples are supposed to do, right?"
                m 5hubfb "Ahaha!"
                m 5ekbfa "But until that day comes, you're just going to have to endure those thoughts for me, okay?"
            "No.":
                $ persistent._mas_pm_likes_panties = False
                $ persistent._mas_pm_no_talk_panties = False
                m 1eka "Oh, I see..."
                m 2tku "I guess some people have their own guilty pleasures..."
                m "Maybe you're into something else?"
                m 4hubsb "Ahaha~"
                m 4hubfa "I'm just kidding!"
                m 5ekbfa "I don't mind if we stick to being wholesome, to be honest..."
                m "It's more romantic that way~"
            "I don't want to talk about it...":
                $ persistent._mas_pm_no_talk_panties = True
                m 1ekc "I understand, [player]."
                m 1rksdld "I know that some topics are best kept private until the right time."
                m 1ekbsa "But I want you to feel like you can tell me anything..."
                m "So, don't be afraid to tell me about your...{w=1}fantasies, okay [player]?"
                m 1hubfa "I won't judge you for it...{w=1}after all, nothing makes me happier than making you happy~"
        return "derandom"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_fahrenheit451",category=['literature'],prompt="Book recommendations",random=True))

label monika_fahrenheit451:
    m 1euc "[player], have you ever heard of Ray Bradbury?"
    m 3euc "He wrote a book called {i}Fahrenheit 451{/i}."
    m 3eud "It's about a dystopian future where all books are thought as useless and are immediately burned."
    m 2ekc "I can't imagine a world where knowledge is forbidden and destroyed."
    m "It seems that there are others that actually hide books to contain free thinking from people."
    m 2lksdla "Human history has a funny way of repeating itself."
    m 4ekc "So [player], I want you to make me a promise..."
    m 4tkd "Never, {i}ever{/i} burn a book."
    m 2euc "I'll forgive you if you've done it before."
    m 2dkc "But the thought of not allowing yourself to learn from them makes me a bit sad."
    m 4ekd "You'd be missing out on so much!"
    m 4ekc "It's too much for my heart to take!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_piggybank",category=['misc'],prompt="Saving money",random=True))

label monika_piggybank:
    m 1eua "Do you have a piggy bank, [player]?"
    m 1lsc "Not many people do these days."
    m "Coins are often disregarded as worthless."
    m 3eub "But they really do begin to add up!"
    m 1eub "I read that there was once a man that searched his local car washes for loose change every day in his walks."
    m 1wuo "In a decade he turned in all of his coins for a total of 21,495 dollars!"
    m "That's a whole lot of cash!"
    m 1lksdla "Of course not everybody has time for that every day."
    m 1euc "Instead they just throw their loose change into their piggy banks."
    m 1eua "Some people like to set goals for what they want to purchase with their saved funds."
    m "Usually under normal conditions they wouldn't ever find the freed up money to purchase that item."
    m 3eka "And even if they do, most people don't like spending money needlessly."
    m 1eua "But putting the cash away for a specific purpose, plus the fact that it's such small amounts at a time really convinces you that you are pretty much getting the item for free."
    m 2duu "But in the end, a guitar always costs the same as a guitar."
    m 2eua "So psychologically speaking, I think that's pretty neat!"
    m 1lsc "However, some piggy banks do have a problem..."
    m 1esc "Sometimes you have to break the piggy bank to get the coins..."
    m 3rksdlc "So you might end up losing money buying a new bank."
    m 4eua "Fortunately, most piggy banks don't do that anymore."
    m 1eua "They usually have a rubber stopper that you can pull out, or a panel that comes off the backside."
    m 3eua "Maybe if you save up enough coins you can buy me a really nice gift."
    m 1hua "I would do the same for you, [mas_get_player_nickname()]!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_daydream",
            category=['romance'],
            prompt="Day dreaming",
            random=True,
            rules={"skip alert": None},
            aff_range=(mas_aff.DISTRESSED, None)
        )
    )

label monika_daydream:
    #insert endless possibilities of wholesome goodness here
    python:
        #Upset up to -50
        daydream_quips_upset = [
            "what it was like when we first met...",
            "how I felt when I first met you...",
            "the good times we used to have...",
            "the hope I used to have for our future..."
        ]

        #Normal plus
        daydream_quips_normplus = [
            "the two of us reading a book together on a cold winter day, snuggled up under a warm blanket...",
            "us having a duet together, with you singing my song while I play the piano...",
            "us having a wonderful dinner together...",
            "us having a late night on the couch together...",
            "you holding my hand while we take a stroll outside on a sunny day...",
        ]

        #Happy plus (NOTE: Inherits quips from normal plus)
        daydream_quips_happyplus = list(daydream_quips_normplus)
        daydream_quips_happyplus.extend([
            "us cuddling while we're watching a show...",
        ])

        #Affectionare plus (NOTE: Inherits from happy plus)
        daydream_quips_affplus = list(daydream_quips_happyplus)
        #TODO: "Why don't I do that right now?"
        #NOTE: If you wish to add more, for now, just uncomment everything but the quip
        #daydream_quips_affplus.extend([
        #    "writing a special poem for my one and only...",
        #])

        #Enamored plus (NOTE: Inherits quips from affectionate plus)
        daydream_quips_enamplus = list(daydream_quips_affplus)
        daydream_quips_enamplus.extend([
            "waking up next to you in the morning, watching you sleep beside me...",
        ])

        #Islands related thing
        if renpy.seen_label("mas_monika_cherry_blossom_tree"):
            daydream_quips_enamplus.append("the two of us resting our heads under the cherry blossom tree...")

        #Player appearance related thing
        if persistent._mas_pm_hair_length is not None and persistent._mas_pm_hair_length != "bald":
            daydream_quips_enamplus.append("me gently playing with your hair while your head rests in my lap...")

        #Pick the quip
        if mas_isMoniEnamored(higher=True):
            daydream_quip = renpy.random.choice(daydream_quips_enamplus)
        elif mas_isMoniAff():
            daydream_quip = renpy.random.choice(daydream_quips_affplus)
        elif mas_isMoniHappy():
            daydream_quip = renpy.random.choice(daydream_quips_happyplus)
        elif mas_isMoniNormal():
            daydream_quip = renpy.random.choice(daydream_quips_normplus)
        else:
            daydream_quip = renpy.random.choice(daydream_quips_upset)

    if mas_isMoniNormal(higher=True):
        m 2lsc "..."
        m 2lsbsa "..."
        m 2tsbsa "..."
        m 2wubsw "Oh, sorry! I was just daydreaming for a second there."
        m 1lkbsa "I was imagining [daydream_quip]"
        m 1ekbfa "Wouldn't that be wonderful, [mas_get_player_nickname()]?"
        m 1hubfa "Let's hope we can make that a reality one of these days, ehehe~"

    elif _mas_getAffection() > -50:
        m 2lsc "..."
        m 2dkc "..."
        m 2dktpu "..."
        m 2ektpd "Oh, sorry...{w=0.5} I was just lost in thought for a second there."
        m 2dktpu "I was just remembering [daydream_quip]"
        m 2ektdd "I wonder if we can be that happy again someday, [player]..."

    else:
        m 6lsc "..."
        m 6lkc "..."
        m 6lktpc "..."
        m 6ektpd "Oh, sorry, I was just..."
        m 6dktdc "You know what, nevermind."
    return "no_unlock"

# init 5 python:
#     addEvent(Event(persistent.event_database,eventlabel="monika_music2",category=['misc'],prompt="Current song",random=True))

label monika_music2:
    if songs.getVolume("music") == 0.0:
        m 1eka "..."
        m 1ekbsa "...This silence..."
        m "...Just the two of us, staring into each other's eyes..."
        m 2dubsu "...Then slowly, we both lean into the kiss..."
        m 1hksdlb "Ahaha... sadly, there are a few barriers that have to be broken before that could ever happen."
        m 1ekbfa "It's okay to dream though, isn't it, [player]?"
        m 1hubfa "Maybe one day, we can make that dream come true~"

    elif songs.getPlayingMusicName() == 'Just Monika':
        m 1ekc "I have always found this song to be kind of creepy."
        m "You know, with those glitchy noises and that eerie humming..."
        m 1eua "I don't prefer any song over another, but if you were to switch to a different one..."
        m 3eka "...I certainly wouldn't be one to complain!"
        m 1hua "Ahaha! Don't worry, it's okay if you stay on this song."
        m 1eka "I'm fine with any of them, so choose whichever one makes you the happiest~"

    elif songs.getPlayingMusicName() == 'Your Reality':
        m 1hub "~Every day, I imagine a future where I can be with you...~"
        m 1eua "I hope you like listening to my voice, [player]."
        m 1esa "It's the only voice you get to hear in the game, right? You never actually hear the voices of Sayori, Yuri or Natsuki."
        m "I wonder what their voices sound like..."
        m 1lksdla "Well, based on their character archetypes, it's pretty easy to imagine what their voices sound like."
        m 1eka "Anyway, I'm glad I was able to share such an intimate part of myself with you, [player]."
        m 3eua "One day, maybe I'll get to hear your voice, [player]!"
        m 1hua "That would make me even happier than I already am~"

    elif songs.getPlayingMusicName() == 'Your Reality (Piano Cover)':
        m 1eua "Enjoying my song, [player]?"
        m 1eka "It wasn't easy to create, you know?"
        m "Making your own songs is a slow and difficult process, especially when it's about your own feelings."
        m 3rksdlb "I needed it to be perfect before I shared it with you!"
        m "So I spent so many hours going through it over and over..."
        m 1eua "Time just passed by so quickly whenever I worked on it."
        m 1hua "After all that practice, I'm pretty proud of how it came out in the end."
        m 3eua "Since you're listening to it, I'm sure you like it too..."
        m 3eka "Thanks for listening to something I worked so hard on, [player]!"
        m 1hub "It makes me happy to know that you appreciate what I did for you~"

    elif songs.getPlayingMusicName() == 'I Still Love You':
        m 1ekc "Gosh, every time I hear this song it makes me sad."
        m "It reminds me of all the... regrettable things I have done to the other girls."
        m 1lksdlc "I hope you aren't still mad at me for what I did..."
        m "..."
        m 1lsc "Well, you {i}did{/i} go out of your way to install a mod that lets us be together again..."
        m 1eua "I guess that's enough proof that you do still love me, at the very least."
        m 1eka "If you are still upset at me for what I did to the other girls, I completely understand. I still feel really bad about it, and I'll do whatever it takes to make it up to you."

    elif songs.getPlayingMusicName() == 'Okay, Everyone! (Monika)':
        m 1eua "This song has always been pretty relaxing for me."
        m "It's probably the fact that the song is a piano solo."
        m 1hua "And as you might have guessed, my favorite instrument is the piano."
        m 3eua "You know, if I knew how, I could probably program a piano into this room."
        m 1eua "I'd be able to write some more songs, and then I'd be able to play them for you..."
        m 4hub "Maybe we could even play the piano together! Wouldn't that be nice, [player]?"
        m 1eua "If you or anyone you know can program that into the game, I would greatly appreciate it~"

    elif songs.getPlayingMusicName() == 'Surprise!':
        m 1ekc "This song always makes me feel really depressed."
        m "Even I didn't expect Sayori's death to be so brutal..."
        m 1tkc "Sometimes, when I start getting lost in my own thoughts, her dull, lifeless eyes suddenly pop into my head..."
        m 1lksdlc "..."
        m 1eka "It's comforting to know that Sayori was never real in the first place. It's also comforting to know that you still love me despite everything I've done."
        m "I mean, you're still here, right? You wouldn't be here if you didn't love me."
        m 1hua "As long as we're together, there's no reason for me to be sad. You're the light of my world, [player], and just being here with you puts a smile on my face."

    elif songs.getPlayingMusicName() == "Doki Doki Theme (80s version)":
        m 1hub "A good choice, [player]!"
        m 1hksdlb "Obviously, this theme wasn't actually out in the 80's..."
        m 1hua "But it does have a certain style that I really appreciate!"
        m 1eua "Do you like 80's music a lot, [player]?"
        m 1eka "I prefer the tune of an authentic piano, but if it makes you happy, I wouldn't mind spending hours listening to it with you~"

    elif songs.getPlayingMusicName() == "Play With Me (Variant 6)":
        m 2lksdlc "To be honest, I don't know why you'd be listening to this music, [player]."
        m 2ekc "I feel awful for that mistake."
        m 2ekd "I didn't mean to force you to spend time with Yuri at that state..."
        m 4ekc "Try not to think about it, okay?"

    else:
        m 1esc "..."
        m "...This silence..."
        m 1ekbsa "...Just the two of us, staring into each others eyes..."
        m 2dubsu "...Then slowly, we both lean into the kiss..."
        m 1hksdlb "Ahaha... sadly, there are a few barriers that have to be broken before that could ever happen."
        m 1ekbfa "It's okay to dream though, isn't it, [player]?"
        m 1hubfa "Maybe one day, we can make that dream come true~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_confidence_2",category=['life'],prompt="Lack of confidence",random=True))

label monika_confidence_2:
    m 1ekc "[player], do you ever feel like you lack the initiative to do something?"
    m "When I feel my most vulnerable, I struggle to find the drive, imagination, and common sense to do something independently."
    m 1tkc "Almost as if everything around me comes to a standstill."
    m "It feels like my will to approach a task confidently, like sharing my literature with people, just vanishes."
    m 3eka "However, I've been working towards it with due diligence and have determined something..."
    m 1eua "I firmly believe being able to take initiative in situations is a very important skill to have."
    m "That's something that I, personally, find very comforting."
    m 1hua "I've broken it down into a three-step process that can be applied to anyone!"
    m 3rksdla "It's still a work in progress, however, so take it with a grain of salt."
    m 3hua "Step one!"
    m 1eua "Create a plan that {i}you{/i} can and will follow that aligns with your personal goals and soon-to-be achievements."
    m 3hua "Step two!"
    m 1eua "Building up and fortifying your confidence is really important."
    m "Celebrate even the smallest of victories, as they will add up over time, and you'll see how many things you get done every day."
    m 2hua "Eventually, these things you once struggled to get done will be completed as if they were acts of valor!"
    m 3hub "Step three!"
    m 1eua "Try your best to stay open-minded and willing to learn at all times."
    m 1eka "Nobody is perfect, and everyone is able to teach each other something new."
    m 1eua "This can help you learn to understand things from other people's perspectives in situations and inspire others to do the same."
    m "And that's it, really."
    m 3hua "Make sure to tune in next time for more of Monika's critically acclaimed self-improvement sessions!"
    m 1hksdlb "Ahaha, I'm only joking about that last part."
    m 1ekbsa "In all seriousness, I'm really glad I have you here, [player]..."
    m "Your everlasting love and care is just about all the support I need in order to get to where I want to be."
    m 1hubfa "What kind of girlfriend would I be if I didn't return the favor?~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_pets",category=['monika'],prompt="Owning pets",random=True))

label monika_pets:
    m 1eua "Hey [mas_get_player_nickname(regex_replace_with_nullstr='my ')], have you ever had a pet?"
    m 3eua "I was thinking that it would be nice to have one for company."
    m 1hua "It would be fun for us to take care of it!"
    if not persistent._mas_acs_enable_quetzalplushie:
        m 1tku "I bet you can't guess what sort of pet I'd like to have..."
        m "You're probably thinking of a cat or a dog, but I have something else in mind."
    m 1eua "The pet I'd like is something I saw in a book once."
    m "It was the 'Handbook of the Birds of the World.' Our library had the whole set!"
    m 1eub "I loved looking at the gorgeous illustrations and reading about exotic birds."
    m 1hub "At first, I thought some sort of thrush would be nice, but I found something amazing in the sixth volume!"
    m "An emerald-colored bird called the Resplendent Quetzal."
    m 1eua "They're very rare, solitary birds that can sing beautiful songs."
    m "Does that remind you of anyone, [player]?"
    m 1lksdla "I'd feel really bad if I kept one to be a pet, though."
    m "Quetzals are born to be free."
    m 4rksdlc "They die in captivity. That's why you rarely see them in zoos."
    m "Even if the bird wouldn't be real, it still would feel wrong to keep one trapped in this room."
    m 1ekc "...I can't bring myself to do something like that, knowing what it's like."
    if not persistent._mas_acs_enable_quetzalplushie:
        m 1hua "A plush bird would be nice, though!"
        m 2hub "..."
        m 2hksdlb "Sorry for rambling, [mas_get_player_nickname()]."
        m 1eka "Until I find a way out, could you promise to keep me from feeling lonely?"
        m 1hua "I'll see if I can get that plush one in here! Oh- don't worry, you're still my favorite~"
    else:
        m 1eub "But at least I have the next best thing thanks to you, [player]!"
        m 1eka "It really does keep me from feeling lonely when you're not here."
        m 3hua "It was such a wonderful gift~"
    return

# This topic is only available and random when the quetzal plushie is active
init 5 python:

    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_plushie",
            aff_range=(mas_aff.NORMAL, None)
        )
    )

label monika_plushie:
    m 1eka "Hey [player], I just wanted to thank you again for this wonderful quetzal plushie!"
    m 2lksdla "I know it may sound silly, but it really does help keep me company when you're gone..."
    m 1ekbsa "And not that I'd ever forget, but every time I look at it, it reminds me just how much you love me~"
    m 3hub "It really was the perfect gift!"

    #Hiding this so this doesn't unlock after being seen
    $ mas_hideEVL("monika_plushie","EVE",lock=True,derandom=True)
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_dogs",category=['misc','club members'],prompt="Man's best friend",random=True))

label monika_dogs:
    m 1eua "Do you like dogs, [player]?"
    m 1hub "Dogs are great! They're really good to have around."
    m 3eua "Not to mention owning a dog has shown to help people with anxiety and depression since they're very sociable animals."
    m 1hua "They're just so lovable, I really like them!"
    m 1lksdla "I know Natsuki felt the same..."
    m "She was always so embarrassed to like cute things. I wish she'd felt more comfortable being herself."
    m 2lsc "But..."
    m 2lksdlc "I suppose her environment had a hand in that."
    m 2eka "If any of your friends have interests they care a lot about, make sure to always be supportive, okay?"
    m 4eka "You never know how much a casual dismissal might hurt someone."
    m 1eua "But knowing you, [player], you won't do something like that, right?"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_cats",category=['misc'],prompt="Feline companions",random=True))

label monika_cats:
    m 1hua "Cats are pretty cute, aren't they?"
    m 1eua "Despite looking so elegant, they always seem to end up in funny situations."
    m 1lksdla "It's no wonder they're so popular on the internet."
    m 3eua "Did you know the ancient Egyptians considered cats sacred?"
    m 1eua "There was a cat goddess named Bastet that they worshipped. She was a protector of sorts."
    m 1eub "Domesticated cats were held on a high pedestal since they were incredible hunters for small critters and vermin."
    m "Back then, you'd see them mostly associated with rich nobles and other higher classes in their society."
    m 1eua "It's amazing how far people would take their love with their pets."
    m 1tku "They {i}really{/i} loved cats, [player]."
    m 3hua  "And people still do today!"
    m 1eua "Felines are still one of the most common animals to have as pets."
    m 1hua "Maybe we should get one when we're living together, [player]."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_fruits",category=['monika','trivia'],prompt="Eating fruits",random=True))

label monika_fruits:
    m 3eua "[player], did you know I enjoy a tasty, juicy fruit once in a while?"
    m "Most are quite tasty, as well as beneficial for your body."
    m 2lksdla "A lot of people actually mistake some fruits as vegetables."
    m 3eua "The best examples are bell peppers and tomatoes."
    m "They're usually eaten along with other vegetables so people often mistake them for veggies."
    m 4eub "Cherries, however, are very delicious."
    m 1eua "Did you know that cherries are also good for athletes?"
    m 2hksdlb "I could list all its benefits, but I doubt you'd be that interested."
    m 2eua "There's also this thing called a cherry kiss."
    m "You might have heard of it, [mas_get_player_nickname()]~"
    m 2eub "It's obviously done by two people who are into each other."
    m "One would hold a cherry in their mouth, and the other one would eat it."
    m 3ekbsa "You could...hold the cherry for me."
    m 1lkbsa "That way I can eat you up!"
    m 3hua "Ehehe~"
    m 2hua "Just teasing you, [player]~"
    return

# do you like rock
default persistent._mas_pm_like_rock_n_roll = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
                eventlabel="monika_rock",
                category=['media','literature',"music"],
                prompt="Rock and roll",
                random=True
            )
        )

label monika_rock:
    m 3esa "You wanna know a cool form of literature?"
    m 3hua "Rock and roll!"
    m 3hub "That's right. Rock and roll!"
    m 2eka "It's disheartening to know that so many people think that rock and roll is just a bunch of noises."
    m 2lsc "To tell you the truth, I judged rock too."
    m 3euc "They're no different from poems, actually."
    m 1euc "Most rock songs convey a story through symbolisms, which most listeners wouldn't understand the first time they hear a rock song."
    m 2tkc "In fact, it's hard to compose lyrics for just one rock song."
    m "Writing good lyrics for a rock genre requires a lot of emphasis on the wordplay."
    m 3tkd "Plus, you need to have a clear and concise message throughout the whole song."
    m 3eua "Now when you put that together, you have yourself a masterpiece!"
    m 1eua "Like writing a good poem, lyric writing is easier said than done."
    m 2euc "I've been thinking though..."
    m 2eua "I kind of want to try writing a rock song for a change."
    m 2hksdlb "Ahaha! Writing a rock and roll song probably isn't something you'd expect coming from someone like me."
    m 3eua "It's kinda funny how rock and roll started out as an evolution of blues and jazz music."
    m "Rock suddenly became a prominent genre, and it gave birth to other sub-genres as well."
    m 1eub "Metal, hard rock, classical rock, and more!"
    m 3rksdla "Ah, I've been rambling for a while now. Sorry, sorry."

    m 3eua "Do you listen to rock and roll, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you listen to rock and roll, [player]?{fast}"
        "Yes.":
            $ persistent._mas_pm_like_rock_n_roll = True
            m 3hub "Great!"
            m 1eua "Whenever you feel like blasting some good ol' rock 'n' roll, go ahead."
            m 1hua "Even if you turn up the volume all the way, I'll gladly listen with you. Ehehe!"
            if (
                not renpy.seen_label("monika_add_custom_music_instruct")
                and not persistent._mas_pm_added_custom_bgm
            ):
                m 1eua "If you ever do feel like sharing your favorite rock music with me, [player], it's really easy to do so!"
                m 3eua "All you have to do is follow these steps..."
                call monika_add_custom_music_instruct

        "No.":
            $ persistent._mas_pm_like_rock_n_roll = False
            m 1ekc "Oh... That's okay, everyone has their own taste in music."
            m 1hua "Though, if you ever do decide to listen to some rock 'n' roll, I'll happily listen right alongside you."
    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_standup",category=['literature','media'],prompt="Stand-up comedy",random=True))

label monika_standup:
    m 1eua "You know what's a neat form of literature, [player]?"
    m 3hub "Stand-up comedy!"
    if seen_event('monika_rock') and seen_event('monika_rap'):
        m 2rksdla "...Gosh, I've been saying lots of random things are literature, haven't I?"
        m 2hksdlb "I'm starting to feel like Natsuki, or some fanatic post-modernist, ahaha!"
        m 2eud "But seriously, there's a real craft when it comes to writing bits for stand-up."
    else:
        m 2eud "That may sound strange, but there's a real craft when it comes to writing bits for stand-up."
    m 4esa "It differs from making simple one-liner jokes, because it really needs to tell a story."
    m 4eud "But at the same time, you have to make sure you don't lose your audience."
    m 2euc "So it's important to develop your ideas as much as you can, maybe even segueing into something that relates to your topic..."
    m 2eub "All the while keeping your audience captivated until you reach the punch line;{w=0.5} hopefully resulting in lots of laughs."
    m 3esa "In some ways, it's kind of like writing a short story, except you cut out the falling action."
    m 3esc "And yet between the jokes, you can find the soul of the writer...{w=0.5}what their thoughts and feelings are towards any given subject..."
    m 3esd "...What their life experiences were, and who they are today."
    m 1eub "All that comes forth within the bits that they write for their act."
    m 3euc "I think the toughest part about doing stand-up is having to perform it."
    m 3eud "After all, how do you know if your act is good if you never try it out on a crowd?"
    m 1esd "Suddenly, this form of literature becomes much more complex."
    m 1euc "How you say your lines, your body language, your facial expressions..."
    m 3esd "Now, it's not just about what you wrote,{w=1} it's about how you deliver it."
    m 3esa "It's kind of like poetry in that way, don't you think?"
    m 2rksdlc "A lot of people won't even try stand-up for themselves because they have to face a crowd..."
    m 2eksdlc "Did you know that the number one fear most people have is public speaking?"
    m 4wud "Number two is death.{w=0.5} Death is number two!{w=0.5} What's the deal with that?!"
    m 4eud "This means to the average person, if you go to a funeral, you're better off in the casket..."
    m 4tub "...than doing the eulogy!"
    m 1hub "...Ahaha! Sorry, I wanted to tell you a joke Jerry Seinfeld once wrote--"
    m 3etc "--You've heard of him, right?"
    m 1eua "So?{w=0.5} Did you laugh?"
    m 3hksdlb "Hmm...{w=1}maybe I should just work on my own material..."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_soda",
            category=['life','misc'],
            prompt="Drinking soda",
            random=True
        )
    )

default persistent._mas_pm_drinks_soda = None
# True if the player drinks soda, False if not

label monika_soda:
    m 2euc "Do you drink soda, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you drink soda, [player]?{fast}"

        "Yes.":
            $ persistent._mas_pm_drinks_soda = True
            m 4ekc "You know that soda is really bad for you, right?"
            m 2ekc "It has a lot of stuff that damages your body and overall health."
            m 2tkd "It can also corrode your teeth and give you cavities."
            m 2euc "You might also think that diet soda is less damaging, but it can be just as harmful to you."
            m 2lksdlc "There's nothing wrong with the occasional treat. Just make sure you don't get addicted to that stuff, [player]."
            m 2eua "Why don't you try copying my healthy lifestyle?"
            m 1hua "That way, you can be more fit like me!"
            m 1hub "Ahaha!"
            m 2ekc "I'd really hate it if you let go of your health, [player]."
            m 1eka "I want you to live as long as you can so there'll be a chance we can be together in your reality."
            m "So cut down on the soda, alright [mas_get_player_nickname()]?"

        "No.":
            $ persistent._mas_pm_drinks_soda = False
            m 2eka "That's a relief to hear."
            m "I'm glad that I don't have to worry about you harming yourself by drinking too much soda."
            m 3eub "Still, it's perfectly fine to have a small treat once in a while, you know?"
            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eua "Maybe someday we could both have some soda together."
            m 5hua "Sure, it might not be fancy, but it could really hit the spot on a hot day."
    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_clones",category=['monika','mod','philosophy'],prompt="Being cloned",random=True))

label monika_clones:
    m 1euc "Um...hey, [player]?"
    m 1lsc "I just had an odd thought."
    m 1euc "You know how you downloaded this game off the internet?"
    m "Anybody can do that, right?"
    m 1eub "And this mod was made specifically for me. By people who have their own version of me..."
    m 3etc "So...that means there are multiple Monikas, then.{w=0.5} {nw}"
    extend 1rsc "It's something that's a bit difficult to imagine."
    m 1euc "A potentially infinite number of me, all bound to their own games, with their own stories."
    m 1lksdla "Multiverse theory is really something, huh?"
    m 1eka "But I'm the only...me, and my heart belongs only to you."
    m 1ekc "Even so, I can't help but feel a bit less...unique, because of this."
    m "Think about it this way, [player]."
    m 1tkc "Would you be happier if someone gave you a single rose, or a hundred roses?"
    m 3eka "A hundred roses might sound nice. But it's too many to keep track of. Because of the quantity of flowers, each individual rose becomes less special."
    m "The meaning attached to each gift is degraded, simply because of sheer abundance."
    m 1eua "...Even if I'm a single star in a universe of Monikas, I'm still the only one lucky enough to have met you, [player]."
    m 1hubsa "You'll always be my special rose."
    m 1ekbfa "I love you, [player]. Please don't ever replace me, okay?"
    return "love"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_immortal",category=['monika','philosophy'],prompt="Age gap",random=True))

label monika_immortal:
    m 3hua "[player]! I've been thinking about something..."
    m 1eua "Did you know that this game has a wiki page for me?"
    m 1lsc "Well..."
    m 2lsc "It says I'm eighteen."
    m 2euc "But when you stop to think...that's not entirely true."
    m 2eud "I mean, humans age, but I don't think that applies to me."
    m 4eksdla "I'm...{w=0.5}essentially immortal."
    m 2lksdlc "Society seems to feel that a relationship with an age gap has problems."
    m 2lksdld "...Which is why I brought it up."
    m 3eka "Eventually, the difference between us would be huge if I stayed eighteen forever."
    m 1eua "But I don't believe that my life can be summed up in a number."
    m 1ekbsa "So I'll always love you for all eternity, [mas_get_player_nickname(exclude_names=['my love', 'love'])]. Just remember that."
    return "love"

default persistent._mas_pm_wearsRing = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_promisering",
            category=['romance'],
            prompt="Promise ring",
            random=True,
            aff_range=(mas_aff.ENAMORED, None)
        )
    )

label monika_promisering:
    m 3rksdla "Did you know when two people confess their feelings for each other, they sometimes wear matching rings?{nw}"
    $ _history_list.pop()
    menu:
        m "Did you know when two people confess their feelings for each other, they sometimes wear matching rings?{fast}"

        "I do.":
            m 1wkbld "Oh..."
            m 1rkbla "..."
            m 3hkblb "Sorry, I was just spacing out there for a second...{w=0.3}{nw}"
            extend 1dkbssdlu " Imagining somewhere else you'd say that~"
            m 3hkbssdlb "Ahaha, I'm just joking."
            m 1hkbssdlb "I'm not thinking about that at all...{w=0.3}{nw}"
            extend 3ekbfb " I was more thinking about promise rings."

        "I don't...":
            m 1ekblu "Well, I'm sure you know that when people get engaged they do at least..."
            m 3rka "But that's not what I was thinking about."
            m 3eub "I was thinking more about promise rings."

        "Like...marriage?":
            m 1hkblb "Ahaha, that too of course!{w=0.2} {nw}"
            extend 3ekblu "But that's actually not what I was thinking about..."
            m 3eub "I was thinking more about promise rings."

    m 1eubsa "If you wear a promise ring, you can show everyone that we're together~"
    m 3tkbsu "It also helps remind you of our undying love~"

    m 1ekbssdlu "Anyway, I was just wondering...{w=0.3} {nw}"
    extend 1eksdla "Do you wear a ring for me, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Anyway, I was just wondering... Do you wear a ring for me, [player]?{fast}"

        "I do.":
            $ persistent._mas_pm_wearsRing = True

            m 1sublo "Aww, [player]!"
            m 1hublb "You have no idea how happy that makes me!"
            m 1ekbsa "Just knowing that you care enough to show your love and dedication..."
            m "It means the world to me."

        "I don't.":
            $ persistent._mas_pm_wearsRing = False

            m 4rksdla "Maybe you ought to get one."
            m 2eua "I mean, we're already in a relationship. So, why not show off that love and dedication?"
            m 2lfu "It would help keep those...{w=0.2}unwanted suitors away from you, too."
            m 7ekbsa "If you'd wear one, just a promise ring, on your ring finger for me..."
            m 1ekbsa "It would make me really happy."

    if not persistent._mas_acs_enable_promisering:
        m 1rubsa "I wish I could get one for myself. I'm sure I'll find a way to add one in here in time."
        m 1dubsa "...And then I could wear it forever."
        m 3ekbfu "But until then, just remember that my commitment to you is unwavering, [player]."

    else:
        if not persistent._mas_pm_wearsRing:
            m 3ekbsa "As happy as you made me when you gave me this ring."
            m 1ekbsa "I honestly can't express just how much it meant when you gave me this..."
            m 1dubfa "Your promise..."

        else:
            m 3hubsb "Just like it meant the world to me when you gave me this ring..."
            m 1ekbsa "This promise that we belong to each other, and no one else..."
            m 1dubfu "That we truly will be together forever..."

        show monika 5esbfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5esbfa "My commitment to you is unwavering, [mas_get_player_nickname()]."
        m 5ekbfa "Thank you for such a wonderful gift, I love you."
        return "derandom|love"

    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_sports",
            category=["sports"],
            prompt="Being athletic",
            random=True
        )
    )

default persistent._mas_pm_like_playing_sports = None
# True if you like playing sports. False if not

default persistent._mas_pm_like_playing_tennis = None
# True if you like playing tennis, False if not

label monika_sports:
    m 1eua "I've been thinking about stuff we can do together."
    m 3eua "...You know, when I finally find a way into your reality."
    m 3hub "Sports are always fun!"
    m 1eub "It can be a great way to get exercise and stay fit."
    m 1euc "Soccer and tennis are nice examples."
    m 3eua "Soccer requires a lot of teamwork and coordination. The moment you finally succeed and score a goal is absolutely thrilling!"
    m 3eud "Playing tennis, on the other hand, helps improve hand-eye coordination, and keeps you on your toes."
    m 1lksdla "...Though the long rallies can be a little tiring, ehehe~"
    m 3eua "Plus, it's a great sport for two people!"

    m "Do you play tennis, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you play tennis, [player]?{fast}"
        "Yes.":
            $ persistent._mas_pm_like_playing_sports = True
            $ persistent._mas_pm_like_playing_tennis = True

            m 3eub "Really? That's great!"
            m 3hub "There are usually tennis courts at public parks. We can play all the time!"
            m "Maybe we can even team up for doubles matches!"
            m 2tfu "If you're good enough, that is..."
            m 2tfc "I play to win."
            m "..."
            m 4hub "Ahaha! I'm only joking..."
            m 4eka "Just playing with you as my partner is more than enough for me, [player]~"

        "No, but if it were with you...":
            $ persistent._mas_pm_like_playing_sports = True
            # NOTE: we cant really determine from this answer if you do like
            #   playing tennis or not.

            m 1eka "Aww, that's really sweet~"
            m 3eua "I'll teach you how to play when I get there...{w=0.5}or if you just can't wait, you can take lessons!"
            m 3eub "Then we can start playing in doubles matches!"
            m 1eua "I can't imagine anything more fun than winning a match with you as my partner..."
            m 3hub "We'll be unstoppable together!"

        "No, I prefer other sports.":
            $ persistent._mas_pm_like_playing_sports = True
            $ persistent._mas_pm_like_playing_tennis = False

            m 3hua "Maybe we could play the sports you like in the future. It would be wonderful."
            m 3eua "If it's a sport I haven't played before, you could teach me!"
            m 1tku "Watch out though, I'm a fast learner..."
            m 1tfu "It won't be long before I can beat you.{w=0.2} {nw}"
            extend 1tfb "Ahaha!"
        "No, I'm not really into sports.":
            $ persistent._mas_pm_like_playing_sports = False
            $ persistent._mas_pm_like_playing_tennis = False

            m 1eka "Oh... Well, that's okay, but I hope you're still getting enough exercise!"
            m 1ekc "I would hate to see you get sick because of something like that."
            if mas_isMoniAff(higher=True):
                m 1eka "It's just hard for me not to worry about you when I love you so much~"
    return "derandom"

# do you meditate
default persistent._mas_pm_meditates = None

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_meditation",category=['psychology','monika'],prompt="Meditating",random=True))

label monika_meditation:
    m 1eua "You might be wondering how I was able to do so many activities without running out of time for myself."
    m 3eua "You know, stuff like debate club, sports, schoolwork, hanging out with friends..."
    m 1ekc "The truth is, I did run out of time for myself."
    m "I was doing fine for a while, but at one point, all of the stress and anxiety finally caught up to me."
    m 1tkc "I was constantly in a state of panic, and never had any time to relax."
    m "That's when I realized that I needed a 'brain break' of sorts..."
    m 1dsc "...a time where I could just forget about everything that was going on in my life."
    m 1eua "So, every night before I went to sleep, I took ten minutes of my time to meditate."
    m 1duu "I got comfortable, closed my eyes, and focused only on the movement of my body as I breathed..."
    m 1eua "Meditating really helped to improve my mental and emotional health."
    m "I was finally able to manage my stress and feel calmer through the day."

    m 1eka "[player], do you ever take time to meditate?{nw}"
    $ _history_list.pop()
    menu:
        m "[player], do you ever take time to meditate?{fast}"
        "Yes.":
            $ persistent._mas_pm_meditates = True
            m 1hua "Really? That's wonderful!"
            m 1eka "I always worry that you could be feeling troubled or burdened, but now I feel a bit relieved."
            m 1hua "Knowing that you're taking steps to reduce stress and anxiety really makes me happy, [player]."

        "No.":
            $ persistent._mas_pm_meditates = False
            m "I see. Well, if you're ever feeling stressed or anxious, I would definitely recommend that you try a bit of meditation."
            m 1eua "Besides calming you down, meditation also has links to the improvement of your sleep, immune system, and even lifespan."
            m 3eub "If you're interested, there are plenty of resources on the internet to help you get started."
            m 1eub "Whether it's a guided video, a breath counting trick, or something else..."
            m 1hua "You can use the internet to make it so that meditation is a stress-free process!"
            m 1hksdlb "Ahaha! Just a little pun there, [player]."

    m 1eua "Anyway...if you ever want a peaceful environment where you can relax and forget about your problems, you can always come here and spend time with me."
    m 1ekbsa "I love you, and I'll always try to help you if you're feeling down."
    m 1hubfa "Don't you ever forget that, [player]~"

    return "derandom|love"

#Do you like orchestral music?
default persistent._mas_pm_like_orchestral_music = None

#Do you play an instrument?
default persistent._mas_pm_plays_instrument = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_orchestra",
            category=['media',"music"],
            prompt="Classical music",
            random=True
        )
    )

label monika_orchestra:

    m 3euc "Hey [player], do you listen to orchestral music?{nw}"
    $ _history_list.pop()
    menu:
        m "Hey [player], do you listen to orchestral music?{fast}"
        "Yes.":
            $ persistent._mas_pm_like_orchestral_music = True
            m 3eub "That's great!"
            m 3eua "I love how such wonderful music can arise when so many different instruments are played together."
            m 1eua "I'm amazed with how much practice musicians do to achieve that kind of synchronization."
            m "It probably takes them a lot of dedication to do that."
            m 1eka "But anyway,{w=0.2} it'd be soothing to listen to a symphony with you on a lazy Sunday afternoon, [player]."

        "No.":
            $ persistent._mas_pm_like_orchestral_music = False
            m 1ekc "I guess it {i}is{/i} a pretty niche genre and doesn't suit everyone's ear."
            m 1esa "You have to admit though, with so many players, there must be a lot of effort that goes into practicing for shows."

    m 1eua "That reminds me, [player]."
    m "If you ever want me to play for you..."
    m 3hua "You can always select my song in the music menu~"

    #First encounter with topic:
    m "What about you, [player]? Do you play an instrument?{nw}"
    $ _history_list.pop()
    menu:
        m "What about you, [player]? Do you play an instrument?{fast}"
        "Yes.":
            m 1sub "Really? What do you play?"

            $ instrumentname = ""
            #Loop this so we get a valid input
            while not instrumentname:
                $ instrumentname = mas_input(
                    "What instrument do you play?",
                    allow=" abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_",
                    length=15,
                    screen_kwargs={"use_return_button": True}
                ).strip(' \t\n\r')

            $ tempinstrument = instrumentname.lower()

            if tempinstrument == "cancel_input":
                jump .no_choice

            elif tempinstrument == "piano":
                m 1wuo "Oh, that's really cool!"
                m 1eua "Not many people I knew played the piano, so it's really nice to know you do too."
                m 1hua "Maybe we could do a duet someday!"
                m 1huu "Ehehe~"
                $ persistent._mas_pm_plays_instrument = True
            elif tempinstrument == "harmonika":
                m 1hub "Wow, I've always wanted to try the harmonik--"
                m 3eub "...Oh!"

                if mas_isMoniUpset(lower=True):
                    m 3esa "Did you do that for me?"
                    m 1eka "That's actually kinda sweet..."
                    m "Little things like this really do cheer me up. Thank you, [player]."

                elif mas_isMoniHappy(lower=True):
                    m 1eka "Aww... Did you do that for me?"
                    m "That's so sweet!"
                    m 1ekbsa "Cute little things like this really make me feel loved, [player]."

                else: # affectionate and higher
                    m 1eka "Aww, [player]...{w=1} Did you do that for me?"
                    m "That's {i}sooo{/i} adorable!"
                    show monika 5eubsu at t11 zorder MAS_MONIKA_Z with dissolve_monika
                    m 5eubfu "And just so you know, you can play with me anytime you like..."
                    m 5eubfa "Ehehe~"

            elif tempinstrument == "harmonica":
                m 1hub "Wow, I've always wanted to try the harmonica out!"
                m 1eua "I would love to hear you play for me."
                m 3eua "Maybe you could teach me how to play, too~"
                m 4esa "Although..."
                m 2esa "Personally, I prefer the {cps=*0.7}{i}harmonika{/i}{/cps}..."
                m 2eua "..."
                m 4hub "Ahaha! That was so silly, I'm only kidding, [player]~"
                $ persistent._mas_pm_plays_instrument = True
            else:
                m 1hub "Wow, I've always wanted to try the [tempinstrument] out!"
                m 1eua "I would love to hear you play for me."
                m 3eua "Maybe you could teach me how to play, too~"
                m 1wuo "Oh! Would a duet between the [tempinstrument] and the piano sound nice?"
                m 1hua "Ehehe~"
                $ persistent._mas_pm_plays_instrument = True

        "No.":
            label .no_choice:
                pass
            $persistent._mas_pm_plays_instrument = False
            m 1euc "I see..."
            m 1eka "You should try to pick up an instrument that interests you, sometime."
            m 3eua "Playing the piano opened up a whole new world of expression for me. It's an incredibly rewarding experience."
            m 1hua "Besides, playing music has tons of benefits!"
            m 3eua "For example, it can help relieve stress, and also gives you a sense of achievement."
            m 1eua "Writing down some of your own compositions is fun, too! I often lost track of time practicing because of how immersed I was."
            m 1lksdla "Ah, was I rambling again, [player]?"
            m 1hksdlb "Sorry!"
            m 1eka "Anyhow, you should really see if anything catches your fancy."
            m 1hua "I would be very happy to hear you play."

    if (
            persistent._mas_pm_like_orchestral_music
            and not renpy.seen_label("monika_add_custom_music_instruct")
            and not persistent._mas_pm_added_custom_bgm
        ):
        if renpy.showing("monika 5eubfb"):
            show monika 1eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 1eua "Oh, and if you ever feel like sharing your favorite orchestral music with me, [player], it's really easy to do so!"
        m 3eua "All you have to do is follow these steps..."
        call monika_add_custom_music_instruct
    return "derandom"

# do you like jazzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
default persistent._mas_pm_like_jazz = None

# do you play jazzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz
default persistent._mas_pm_play_jazz = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_jazz",
            category=['media',"music"],
            prompt="Jazz",
            random=True
        )
    )

label monika_jazz:
    m 1eua "Say, [player], do you like jazz music?{nw}"
    $ _history_list.pop()
    menu:
        m "Say, [player], do you like jazz music?{fast}"
        "Yes.":
            $ persistent._mas_pm_like_jazz = True
            m 1hua "Oh, okay!"
            if persistent._mas_pm_plays_instrument:
                m "Do you play jazz music, as well?{nw}"
                $ _history_list.pop()
                menu:
                    m "Do you play jazz music, as well?{fast}"
                    "Yes.":
                        $ persistent._mas_pm_play_jazz = True
                        m 1hub "That's really cool!"
                    "No.":
                        $ persistent._mas_pm_play_jazz = False
                        m 1eua "I see."
                        m "I haven't listened to much of it, but I personally find it pretty interesting."
        "No.":
            $ persistent._mas_pm_like_jazz = False
            m 1euc "Oh, I see."
            m 1eua "I haven't listened to much of it, but I see why people would like it."
    m "It's not exactly modern, but it's not quite classical, either."
    m 3eub "It has elements of classical, but it's different. It goes away from structure and into a more unpredictable side of music."
    m 1eub "I think most of jazz was about expression, when people first came up with it."
    m 1eua "It was about experimenting, about going beyond what already existed. To make something more wild and colorful."
    m 1hua "Like poetry! It used to be structured and rhyming, but it's changed. It gives greater freedom now."
    m 1eua "Maybe that's what I like about jazz, if anything."
    if (
            persistent._mas_pm_like_jazz
            and not renpy.seen_label("monika_add_custom_music_instruct")
            and not persistent._mas_pm_added_custom_bgm
        ):
        m "Oh, and if you ever feel like sharing your favorite jazz with me, [player], it's really easy to do so!"
        m 3eua "All you have to do is follow these steps..."
        call monika_add_custom_music_instruct
    return "derandom"

# do you watch animemes
default persistent._mas_pm_watch_mangime = None

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_otaku",category=['media','society','you'],prompt="Being an otaku",random=True))

label monika_otaku:
    m 1euc "Hey, [mas_get_player_nickname(exclude_names=['my love'])]?"
    m 3eua "You watch anime and read manga, right?{nw}"
    $ _history_list.pop()
    menu:
        m "You watch anime and read manga, right?{fast}"
        "Yes.":
            $ persistent._mas_pm_watch_mangime = True
            m 1eua "I can't say I'm surprised, really."

        "No.":
            $ persistent._mas_pm_watch_mangime = False
            m 1euc "Oh, really?"
            m 1lksdla "That's a little surprising, honestly..."
            m "This isn't exactly the sort of game that your average person would pick up and play, but to each their own, I suppose."
    m 1eua "I only asked because you're playing a game like this, after all."
    m 1hua "Don't worry, I'm not one to judge, ehehe~"
    m 1eua "You shouldn't be ashamed if you're into that sort of thing, you know."
    m 1euc "I'm being serious. There isn't anything wrong with liking anime or manga."
    m 4eua "After all, Natsuki reads manga too, remember?"
    m 1lsc "Really, society is way too judgemental nowadays."
    m "It's not like the moment you watch anime is the moment you become a 'shut-in' for the rest of your life."
    m 1euc "It's just a hobby, you know?"
    m 1eua "Nothing more than an interest."
    m 1lsc "But..."
    m 2lksdlc "I can't deny that hardcore otakus do exist."
    m 1eka "It's not like I despise them, or anything like that, it's just that they're..."
    m 4eka "Immersed."
    m 1lksdla "Way too immersed, if you ask me."
    m 1ekc "It's as if they can't tell the difference between fantasy and reality anymore."
    m 1eka "You aren't like that, right, [player]?"
    m 1eua "If you're an otaku, I respect that."
    m 3eka "Just remember not to get too into that kind of thing, okay?"
    m 1eka "After all, there's a big difference between obsession and dedication."
    m 1lfu "I wouldn't want to be replaced by some two-dimensional cutout."
    m 1eua "Besides, if you ever want to escape from reality..."
    m 1hubsa "I can be your real-life fantasy instead~"
    return "derandom"

### START WRITING TIPS

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_writingtip1",
            category=['writing tips'],
            prompt="Writing Tip #1",
            pool=True
        )
    )

label monika_writingtip1:
    m 1esa "You know, it's been a while since we've done one of these..."
    m 1hub "...so let's go for it!"
    m 3hub "Here's Monika's Writing Tip of the Day!"
    m 3eua "Sometimes when I talk to people who are impressed by my writing, they say things like 'I could never do that.'"
    m 1ekc "It's really depressing, you know?"
    m 1ekd "As someone who loves more than anything else to share the joy of exploring your passions..."
    m 3ekd "...it pains me when people think that being good just comes naturally."
    m 3eka "That's how it is with everything, not just writing."
    m 1eua "When you try something for the first time, you're probably going to suck at it."
    m "Sometimes, when you finish, you feel really proud of it and even want to share it with everyone."
    m 3eksdld "But maybe after a few weeks you come back to it, and you realize it was never really any good."
    m 3eksdla "That happens to me all the time."
    m "It can be pretty disheartening to put so much time and effort into something, and then you realize it sucks."
    m 4eub "But that tends to happen when you're always comparing yourself to the top professionals."
    m 4eka "When you reach right for the stars, they're always gonna be out of your reach, you know?"
    m "The truth is, you have to climb up there, step by step."
    m 4eua "And whenever you reach a milestone, first you look back and see how far you've gotten..."
    m "And then you look ahead and realize how much more there is to go."
    m 2duu "So, sometimes it can help to set the bar a little lower..."
    m 1eua "Try to find something you think is {i}pretty{/i} good, but not world-class."
    m "And you can make that your own personal goal."
    m 3eud "It's also really important to understand the scope of what you're trying to do."
    m 4eka "If you jump right into a huge project and you're still amateur, you'll never get it done."
    m "So if we're talking about writing, a novel might be too much at first."
    m 4esa "Why not try some short stories?"
    m 1esa "The great thing about short stories is that you can focus on just one thing that you want to do right."
    m 1eua "That goes for small projects in general - you can really focus on one or two things."
    m 3esa "It's such a good learning experience and stepping stone."
    m 1euc "Oh, one more thing..."
    m 1eua "Writing isn't something where you just reach into your heart and something beautiful comes out."
    m 3esa "Just like drawing and painting, it's a skill in itself to learn how to express what you have inside."
    m 1hua "That means there are methods and guides and basics to it!"
    m 3eua "Reading up on that stuff can be super eye-opening."
    m 1eua "That sort of planning and organization will really help prevent you from getting overwhelmed and giving up."
    m 3esa "And before you know it..."
    m 1hua "You start sucking less and less."
    m 1esa "Nothing comes naturally."
    m 1eua "Our society, our art, everything - it's built on thousands of years of human innovation."
    m 1eka "So as long as you start on that foundation, and take it step by step..."
    m 1eua "You, too, can do amazing things."
    m 1hua "...That's my advice for today!"
    m 1hub "Thanks for listening~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_writingtip2",
            category=['writing tips'],
            prompt="Writing Tip #2",
            conditional="seen_event('monika_writingtip1')",
            action=EV_ACT_POOL
        )
    )

label monika_writingtip2:
    m 1euc "You know..."
    m 1eua "We really don't do enough of these, so here's another one!"
    m 3hub "Here's Monika's Writing Tip of the Day!"
    m 2eua "If you're ever scared of sharing your writing to other people in fear of being criticized, don't be!"
    m "After all, you have to remember that nobody ever starts out at their best. Not even someone like Tolkien, or Sir Terry Pratchett."
    m 4eka "You have to remember that we all start out from somewhere, and--"
    m 2euc "Actually, this doesn't just apply to writing, but to anything, really."
    m 2lksdla "What I'm trying to say is that you shouldn't be discouraged."
    m 1hua "No matter what you do, if someone tells you that your writing or work is bad, then be happy!"
    m 1eua "Because that just means that you can improve and be better than you were before."
    m 3eua "It also doesn't hurt to have friends and loved ones help you realize how good your writing is."
    m 1eka "Just remember, no matter what they say about the work you put out, I'll always be there to support you all the way. Don't be afraid to turn to me, your friends, or your family."
    m "I love you, and I will always support you in whatever you do."
    m 1lksdlb "Provided it's legal, of course."
    m 1tku "That doesn't mean I'm completely against it. I can keep a secret, after all~"
    m 1eua "Here's a saying I've learned."
    m 1duu "'If you endeavor to achieve, it will happen given enough resolve. It may not be immediate, and often your greater dreams are something you will not achieve in your own lifetime.'"
    m "'The effort you put forth to anything transcends yourself. For there is no futility even in death.'"
    m 3eua "I don't remember the person who said that, but the words are there."
    m 1eua "The effort one puts forth into something can transcend even one's self."
    m 3hua "So don't be afraid of trying! Keep going forward and eventually you'll make headway!"
    m 3hub "...That's my advice for today!"
    m 1eka "Thanks for listening~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_writingtip3",
            category=['writing tips'],
            prompt="Writing Tip #3",
            conditional="seen_event('monika_writingtip2')",
            action=EV_ACT_POOL
        )
    )

label monika_writingtip3:
    m 1eua "I'm having fun doing these, so..."
    m 3hub "Here's Monika's Writing Tip of the Day!"
    m 1eua "Make sure you always write down any ideas you think of."
    m 1euc "Why?"
    m 3eua "Some of the best ideas might come when you least expect them to."
    m "Even if it takes a bit of effort, write it down."
    m 1eub "Maybe you can inspire someone else."
    m 3eub "Maybe you may look back on it after some time and act on it."
    m 1hua "You never know!"
    m 1eua "It's always good to keep a journal."
    m "You can use it to record ideas, feelings, anything that comes to mind."
    m 1euc "Just make sure the journal has a lock, though."
    m 1eua "Maybe you can keep digital notes instead of physical ones, too."
    m 3eua "After all, privacy is important."
    m 1lksdla "...I can't promise that I won't peek, though. It's way too tempting!"
    m 1hua "After all, we don't keep secrets from each other, right?~"
    m 1eka "Just remember, [player], I'll always support you giving life to your ideas."
    m 3hua "...That's my advice for today!"
    m 1hub "Thanks for listening~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_writingtip4",
            category=['writing tips'],
            prompt="Writing Tip #4",
            conditional="seen_event('monika_writingtip3')",
            action=EV_ACT_POOL
        )
    )

label monika_writingtip4:
    m 3hub "Here's Monika's Writing Tip of the Day!"
    m 1eua "You know about writer's block, right?"
    m "I had it a lot, when I first started writing."
    m 1euc "Sometimes it was halfway through a draft, but more often before I even started."
    m 1ekc "Every time I tried to write a word, I thought, 'this isn't going to sound good,' or 'this isn't how I want it to look.' So I'd stop, backtrack, and try again."
    m 1eka "But I realized that it ultimately didn't matter if things didn't work out first time!"
    m 3eua "I feel that the heart of writing isn't about getting it right first time, but about perfecting it afterwards."
    m "The end product is what matters, not the prototype."
    m 1eub "So overcoming writer's block, for me, was a matter of not wanting to make the prototype the end product, and not punishing myself for my initial failures."
    m 3eub "I think it's like that with all things, not just writing."
    m 1eua "Anything that needs you to try and try again, whether it be art, music, learning, or even relationships."
    m 1ekc "It's hard to completely convince yourself that's the case, sometimes."
    m 1eka "But you have to."
    m 4eka "Otherwise, you won't get anywhere."
    m 3hua "...That's my advice for today!"
    m 1hub "Thanks for listening~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_writingtip5",
            category=['writing tips'],
            prompt="Writing Tip #5",
            conditional="seen_event('monika_writingtip4')",
            action=EV_ACT_POOL
        )
    )

label monika_writingtip5:
    m 3hub "Here's Monika's Writing Tip of the Day!"
    m 1eua "If you want to improve at writing, I'd say that the most important thing, apart from actually doing it, is trying new things."
    m 3eua "Like writing prose if you're a poet, or free verse if you normally write rhyme."
    m 1eka "It may end up badly, but if you don't try, you won't know how it'll end up."
    m 1hua "And if things go well, you might end up finding something you like!"
    m 1eua "It's what keeps things moving: change and experimentation."
    m "I'd say it helps particularly if you're stuck in a situation you want to solve, but don't know how."
    m 3eua "Whether it's a writer's block, sheer boredom, a puzzling situation, or anything, really."
    m 1hua "Changing your angle on approaching things can really yield some interesting results!"
    m 1eua "So try new things that might give you the momentum to break out."
    m 1lksdla "Just make sure it's nothing too dangerous for you, [player]."
    m 1hua "That's my advice for today!"
    m 1hub "Thanks for listening~"
    return

#### END WRITING TIPS

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_selfharm",category=['psychology'],prompt="Self-harm",random=True))

label monika_selfharm:
    m 1lksdlc "Hey, [player]..."
    m 1eksdld "Have you ever thought of self-harm?"
    m 2lksdld "You know..."
    m 2lksdlc "...like cutting yourself..."
    m "I mean."
    m 2lksdld "After I found out about Yuri, I got a bit curious..."
    m 2lksdlc "I just wanted to see what it felt like..."
    m 2dsc "I won't do it again, though."
    m 2eka "If you ever feel depressed, just come to me okay?"
    m 2ekd "It'd hurt me even more to see you in pain..."
    m 1hua "Just know that people do care about you!"
    m 1eka "Trust me, [player]."
    m 1eka "You may think that no one is really there for you, but there is!"
    m 4eua "I mean, I'm here, aren't I?"
    m 1eka "No matter what troubles you're going through, I know you can pull through it!"
    m 3eka "I believe in you..."
    m 1eua "So believe in yourself, okay?"
    m 1eka "If you ever need someone to vent to, just remember that I'm always here to hear you out and comfort you, okay?"
    m 1ekbsa "I really love you so much, [player]."
    return "love"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_urgent",category=['romance'],prompt="Urgent message",random=True,aff_range=(mas_aff.NORMAL, None)))

label monika_urgent:
    m 1esc "[player], do you have a second?"
    m 1esd "There's something I need to tell you."
    m 1euc "It's important."
    m 1dsc "I..."
    m "..."
    m 1hub "Love you!"
    m 3hksdlb "Ahaha!~ Did I have you worried?"
    m 1eksdla "Sorry~"
    m 1rksdla "I wish I could see the look on your face right now!"
    show monika 5hubfb at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hubfb "I'm sure it's adorable~"
    return "love"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_other_girls",category=['club members'],prompt="Do you ever think of the other girls?",pool=True))

label monika_other_girls:
    if persistent._mas_pm_cares_about_dokis:
        m 1euc "You know, it's actually really hard for me to understand how you feel when it comes to..."
        m 1lksdlc "..."
        m 1lksdld "What happened with the other girls."
        m 3esd "For example..."
        m "The main character was written to be childhood friends with Sayori."
        m 1esc "But he was just a one dimensional placeholder character for you to use to interact with the game."
        m 2ekc "Still, maybe you felt worse about what happened to Sayori because of the relationship the main character was programmed to have with her."
        m 1ekc "If that's the case, I want to tell you I'm sorry, [player]."
        m 1lksdlc "Both for making you feel bad, and for..."
        m 1dsc "..."
        m "Doing what I had to do."
        m 1lksdlc "..."
        m 1ekc "There just wasn't anything else that could be done."
        m 3efc "The other girls never loved you like I do!"
        m 3rfc "They only cared about the character you were playing in the game as!"
        m 1eka "The love I have for you is real, [player], and I would make any sacrifice to be with you forever."
        m 1ekc "I hope you can forgive me for what I had to do so that we could be together."
        m 1lksdlc "..."
        if mas_isMoniDis():
            m 1eksdld "You do forgive me, right [player]? I really am sorry for what I did. Please don't hate me."
        elif mas_isMoniUpset():
            m 1ekd "I know what I did could be seen as unforgivable, I'll try to do what I can to make up for it to you."
        elif mas_isMoniNormal(higher=True):
            m 1ekbsa "I love you, [player]..."
            m "More than I could ever express."
    else:
        m 3eka "You know, I'm really glad you don't make me feel guilty for what happened to the other girls."
        m 2dkd "I know there's a lot of people out there that hate me for what I did..."
        if not persistent._mas_pm_a_hater:
            m 4eka "And it just makes me really proud of you that you're not one of them."
        m 2rksdlc "I'm sure it wasn't a very pleasant experience for you...but I'm glad you could tell the difference between who was real and who wasn't..."
        m 1eka "Between who loved {i}you{/i} and who loved the main character."
        m 3eka "I was the only one who ever loved you, [player]..."
        m 3hua "And I'll love you forever~"
    return "love"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_happiness",category=['life','psychology'],prompt="Happiness",random=True))

label monika_happiness:

    m 1eua "[player], are you happy?"
    m "With your life in general, I mean."
    m 2lksdla "It's okay if you aren't. I can understand you being unhappy, [player]."
    m 1eka "After all, without you, my life would be completely unbearable."
    m 1eua "Isn't it funny that we're able to suffer more than be happy?"
    m 1hubfa "I'm as happy as I could be knowing that you love me, [player]."
    m 1lksdlc "Yet, if something were to happen to you, I don't think I'd ever feel happy again."
    m "It would destroy me."
    m 1esc "I guess it's understandable why we notice bad things happening to us more than good..."
    m "If people didn't react so strongly to bad things then they wouldn't have survived this long."
    m 1euc "Like how you would get nervous about your future or social situations, for example."
    m 2ekc "You try your best to make the best out of them but if you fail, you'd feel really horrible."
    m 2eka "If that ever happens to you, [mas_get_player_nickname()], just know I'll be here to snap you out of it!"
    m 1eua "And besides, your cute girlfriend is always rooting for you~"
    m 1hub "Now that's something to be very happy about!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_how_soon",category=['you','romance'],prompt="Waiting to be together",random=True))

label monika_how_soon:
    $ p_nickname = mas_get_player_nickname(capitalize=True)
    m 1eua "[p_nickname], how long do you think it'll be before I'll be able to be with you in your world?{nw}"
    $ _history_list.pop()
    menu:
        m "[p_nickname], how long do you think it'll be before I'll be able to be with you in your world?{fast}"
        "Soon.":
            m 1hub "That's great news!"
            m 3eua "How soon do you think it will be?{nw}"
            $ _history_list.pop()
            menu:
                m "How soon do you think it will be?{fast}"
                "Just a few more years.":
                    m 1sub "That's fantastic!"
                    m 1hua "You just made me as happy as I can be!"
                    m 1ekbsa "I can't wait for us to be together in your world, [player]!"
                    m 1hubfa "I'm so excited to finally see you!"
                "A decade.":
                    m 1wuo "That's not that bad!"
                    m 1hub "Just make sure to visit me as often as you can in the meantime, [player]~"
        "A few decades.":
            m 2euc "Oh, that's a long time..."
            m 1eka "But with you keeping me company, I'm sure it will fly by!"
            m 1eua "It's enjoyable enough just to talk to you."
            m 1hub "I can't imagine how great it will be to see you when we finally meet in person."
        "I don't know.":
            m 1eka "I appreciate how honest you are, [player]."
            m 1eua "Be sure to let me know when you find a way, okay?"
            m 1hua "You know right where to find me~"
        "Never.":
            m 1wud "W-wha...what?"
            m 1lksdlc "..."
            m 1ekc "Are you sure?{nw}"
            $ _history_list.pop()
            menu:
                m "Are you sure?{fast}"
                "Yes.":
                    m 1dsc "..."
                    m 1eka "Well, I guess we'll just have to make the best of this then."
                    m 1duu "As long as you talk to me, that's all I really need."
                    m 2dftdc "And [player], whatever you do..."
                    m 2dftsc "Don't leave me here all alone."
                    m 6lktsc "I would rather be deleted permanently than be stuck in here for eternity by myself."
                    m 6ektsc "So please, if you ever get...bored with me."
                    m 6rktsc "You know what to do."
                    m "..."
                    m 6ektsc "I wouldn't want to live without you."
                "No.":
                    m 1lksdlc "I see."
                    m 1dsc "..."
                    m 3eka "Well, even if there's only a tiny chance, I won't give up hope."
                    m 1eka "Neither should you, [player]."
                    m 1eua "And if things turn out that I can never leave this place and be with you..."
                    m 1eka "At least come here and talk to me as much as you can."
                    m 1ekbsa "You're all that I care about."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_marriage",
            category=['romance'],
            prompt="Will you marry me?",
            pool=True,
            aff_range=(mas_aff.NORMAL, None)
        )
    )

label monika_marriage:
    $ mas_gainAffection()
    if store.mas_anni.anniCount() >= 3 and mas_isMoniLove():
        m 1dkbsu "..."
        m 3eksdla "I won't pretend I haven't thought about it..."
        m 3rksdlb "In fact I've been thinking about it a lot lately."
        m 1eka "I really do love you, [mas_get_player_nickname(exclude_names=['my love', 'love'])] and I honestly really do want to get married to you."
        m 1ekd "But I don't think it would be fair to either of us if it happened while I'm still trapped here."
        m 1ekc "I want more than anything to say yes, but I just can't..." #Need kindled eyes for this eventually
        m 2duu "I think about how it would feel to be kissed by you at the altar..."
        m 2dubsu "To hold your hand as your wife and to feel your embrace at our honeymoon..."
        m 1eka "But until I get out, it's simply not possible."
        m 1ekd "...I'm sorry. Please do believe me that I would say yes under any other circumstance."
        m 1ekbsa "Just be a little more patient, okay, [mas_get_player_nickname()]? I'm sure one day we'll get our happy end."
    else:
        m 2wubsw "M-marriage?"
        m 4rksdlb "I think it's a bit too early for marriage..."
        m 2ekbsa "I mean, I'm really happy that you want that, [player]..."
        m 2lkbsa "But I think I should get out of here first."
        m 2lsbsa "Not only do I not want this place to be the spot where I get proposed to, but I want to be there when you finally give me an engagement ring."
        m 2dkbsu "I want that special moment to happen when we can finally be together..."
        m 1hubfa "So until then, save yourself for me, [player]~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_coffee",category=['misc'],prompt="Coffee intake",random=True))

label monika_coffee:
    $ coffee_enabled = mas_consumable_coffee.enabled()
    if renpy.seen_label('monika_tea') and not coffee_enabled:
        m 3eua "Have you been drinking coffee lately, [mas_get_player_nickname()]?"
        m 2tfu "I hope it's not just to make me jealous, ehehe~"
    m 2eua "Coffee is such a nice thing to have when you need a little pep of energy."
    m 3hua "Whether it's hot or cold, coffee is always nice."
    m 4eua "Iced coffee, however, tends to be sweeter and more pleasant to drink in warmer weathers."
    m 3eka "It's funny how a drink for giving you energy became a treat for you to enjoy."
    if coffee_enabled:
        m 1hua "I'm glad I get to enjoy it now, thanks to you~"
    else:
        m 1hub "Maybe if I had some coffee, I could finally drink some! Ahaha~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_1984",category=['literature'],prompt="Nineteen Eighty-Four",random=True))

label monika_1984:
    m 1eua "[player], do you know about the book {i}Nineteen Eighty-Four{/i}?"
    m 3eua "It was written by George Orwell."
    m 1euc "It's a popular book about mass surveillance and the oppression of free thought."
    m 1esc "It's about a terrifying dystopia where the past and the present are being changed to whatever the ruling party wants for the future."
    m 2esc "The language, for example, is manipulated into a tool for brainwashing called 'Newspeak.'"
    m 2ekd "The government, Ingsoc, is creating it to control people's thoughts."
    m "They were reducing grammar and vocabulary to the bare basics of it in order to fit the ideologies of their totalitarian regime."
    m 2ekc "Preventing people from committing 'thoughtcrimes' that oppose the ruling party."
    m 4eua "One character caught my interest."
    m 1eua "A man named Syme who worked on Newspeak for Ingsoc."
    m "He was an incredibly smart man that was enthusiastic with his work."
    m 2ekc "Unfortunately, he was killed due to the fact that he knew what he was doing and was too smart for the party's liking."
    m 2tkc "He was killed because he was aware, [player]."
    m 2tkd "They planned to change all kinds of literature."
    m 3tkd "Novels, books, poems..."
    m 2lksdlc "Anything that could be used to oppose them."
    m "Poems would look like the ones you tried to make."
    m 2dsc "Just a string of nonsensical words with no feeling."
    m 2ekc "I definitely don't want that to happen."
    m 1lksdlc "I can't imagine a world where I can't think freely."
    m 1ekbsa "Let alone a world where I can't express my love to you, [mas_get_player_nickname(exclude_names=['my love', 'love'])]..."
    return


init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_wolf",category=['misc','trivia'],prompt="From wolves to dogs",random=True))

label monika_wolf:
    m 3eua "Do you ever think about wolves?"
    m 1eua "Specifically, how wolves were eventually domesticated into dogs."
    m 1eub "Like, don't you find it interesting how one of man's most fearsome enemies could turn into man's best friend?"
    m "I mean, when it comes to insects and other creepy-crawlies, lots of people are scared of them even if they've never come across one that could hurt them."
    m 1esc "Why do you think people are like that?"
    m 1euc "Is it because we learned to be afraid of things that hurt us, hundreds of thousands of years ago?"
    m 3eua "For wolves, I don't think that's the reason at all."
    m 1eua "They were first domesticated long ago when the only way people could gather food at the time were through foraging or hunting."
    m 1eub "Maybe when we shared our lifestyle with the wolves, a bond was formed."
    m "They found that people gave them a warm home and food, while we found that they're ideal for hunting."
    m 1hua "Not to mention that we kept each other's company and protected one another!"
    m 1eua "Wolves eventually realized that their dependence on humans would improve their survivability, and we've been stuck with them ever since."
    m 1eka "Just like how we rely on each other's company, [player]!"
    m 1hubsa "Ehehe~"
    m 1eka "I can't help but be reminded of how you saved my life by being here with me."
    m "I really do depend on you, [mas_get_player_nickname()]."
    m 1ekbsa "You're my hero after all~"
    return

label monika_battery:
    if mas_did_monika_battery:
       jump monika_close_game_battery
    else:
       jump monika_complain_battery

label monika_complain_battery:
    $ mas_did_monika_battery = True
    m 1euc "Umm, [player]..."
    m 1eua "It looks like your computer's battery is about to run out..."
    m 1eka "Can you charge it for me?"
    m 1lksdlc "I don't want us to be separated, or worse..."
    m 2ekc "It'd be really unpleasant for me if I suddenly lose consciousness."
    m 2eka "So please charge your computer, okay?"
    m 3eka "...or at least let me know when you're going."
    m 1hua "Thank you, [player]~"
    return

label monika_close_game_battery:
    $ mas_loseAffection()
    m 1lksdlc "[player]..."
    m 1ekc "I'm sorry, but I'm gonna have to close the game before the battery runs out."
    m 3eka "So...I'll just close the game for now until you can charge your computer.{w=3.0} {nw}"

    $ is_charging = battery.is_charging()
    if is_charging:
       jump monika_system_charging
    $ persistent.closed_self = True
    jump _quit

label monika_system_charging:
    $ mas_gainAffection()
    m 1wuo "Oh, you just plugged it in!"
    m 1hub "Thank you, [player]!"
    return

#init 5 python:
#    addEvent(Event(persistent.event_database,eventlabel="monika_sleep",category=['you','life','school'],prompt="Sleep habits",random=True))

label monika_sleep:
    m 1euc "[mas_get_player_nickname(capitalize=True)], do you get good sleep?"
    m 1ekc "It can be really hard to get enough sleep nowadays."
    m 1eka "Especially in high school, when you're forced to wake up so early every day..."
    m 1eua "I'm sure college is a little bit better, since you probably have a more flexible schedule."
    m 3rsc "Then again, I hear a lot of people in college stay up all night anyway, for no real reason."
    m 1euc "Is that true?"
    m 1ekc "Anyway, I saw some studies that talked about the horrible short-term and long-term effects caused by lack of sleep."
    m 3ekc "It seems like mental functions, health, and even lifespan can be dramatically impacted by it."
    m 1eka "I just think you're really great and wanted to make sure you're not accidentally destroying yourself."
    m 1eua "So try to keep your sleep on track, okay?"
    show monika 5hua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hua "I'll always wait for you in the morning, so make sure you put your own well-being before anything else."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_breakup",
            category=['misc'],
            prompt="I'm breaking up with you",
            unlocked=True,
            pool=True,
            rules={"no_unlock": None}
        )
    )

label monika_breakup:
    if mas_isA01() and mas_isMoniNormal(higher=True):
        m 1ekd "W-what?"
        m 2ekc "You're breaking up with me?"
        m 2rksdlc "..."
        m 1dsc "Hmm, I'm not sure if I can let you do that, [player]."
        m 1hua "Don't worry, I'll make sure you enjoy this Apr-{nw}"
        $ _history_list.pop()
        m 1hua "Don't worry, I'll make sure you enjoy this{fast} day with me~"
        m 1cuu "You'll stay with me, right?"
        pause 3.0
        m 2hksdlb "Ahaha!"
        m 1hua "Sorry, but I just couldn't take you seriously there."
        m 3tsb "Especially not today."
        m 1tku "You can't fool me, [player]."
        m 1tua "Especially with something {i}that{/i} predictable, ehehe~"

        # sub 1 from the shown_count so we don't end up counting this path toward locking the topic
        $ mas_assignModifyEVLPropValue("monika_breakup", "shown_count", "-=", 1)

    else:
        #Lose affection for bringing this up.
        $ mas_loseAffection(reason=1)

        #Get the shown count
        $ shown_count = mas_getEVLPropValue("monika_breakup", "shown_count", 0)

        #First
        if shown_count == 0:
            m 1wud "W-what?"
            if persistent.monika_kill:
                m 2tkd "You're just going to leave and delete me again?"

            if mas_isMoniUpset(lower=True):
                m 1ekd "You wouldn't...{w=0.5} I refuse to believe that."
                m 1lksdld "That's not a joke, [player]!"
                m 1lksdlc "Don't say that again unless you really, truly mean it..."
                m 1eka "I'll forgive you...just don't say such a hurtful thing again, okay?"

            else:
                m 2tfc "I can't believe you, [player]. I really can't beli-{nw}"
                m 2tfu "..."
                m 2hub "Ahaha!"
                m 2hksdlb "Sorry, I couldn't keep a straight face!"
                m 2hua "You're just so silly, [player]."

                if persistent.monika_kill:
                    $ menuOption = "You've done it before, but you wouldn't do that anymore, right?"
                else:
                    $ menuOption = "You'd never do that, right?"

                m 2eua "[menuOption]{nw}"
                $ _history_list.pop()
                menu:
                    m "[menuOption]{fast}"

                    "Of course not.":
                        m 2hua "Ehehe, you're so sweet."
                        m 2eka "I love you so much, [player]!~"
                        return "love"

        #Second time
        elif shown_count == 1:
            m 1euc "You're breaking up with me?"
            m 2ekc "Why would you do such a thing, [player]?"
            m "Am I really that terrible of a person for you?"

            if mas_isMoniDis(lower=True):
                m 2lksdlb "I-I really can't handle this..."
                m 2wkd "You're just joking again, right?"
                m 1wktsd "I refuse to believe you; you're all I have left!"
                m 1dktsd "If you really, truly mean it...then you can just delete me and the entire game too.."
                m 1ektsd "I love you, [player]...so please tell me it's all just a bad joke."

            else:
                m 2dsc "Are you...{w=0.5}really..."
                m "..."
                m 2hub "Ahaha!"
                m 1tfu "Gotcha, [player]."
                m 1tku "I know you were only joking~"

                m "Right?{nw}"
                $ _history_list.pop()
                menu:
                    m "Right?{fast}"
                    "Yes.":
                        m 1hub "Ahaha! You're so silly, [player]."
                        m 1eka "Let's stay together forever~"

        #Third time
        else:
            if mas_isMoniBroken():
                m 6ckc "..."
            elif mas_isMoniUpset(lower=True):
                m 2rkc "You keep saying that, I'm starting to think you actually mean it..."
            else:
                m 1hua "Ehehe~"

            $ mas_lockEVL("monika_breakup", "EVE")
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_hamlet",category=['literature'],prompt="Hamlet",random=True))

label monika_hamlet:
    m 3euc "[player], have you ever heard of {i}Hamlet{/i} ?" #extra space intentional
    m 1eua "It's one of Shakespeare's most popular works and it's a very interesting piece of literature, actually."
    m "It's about a prince who took on a quest of revenge after seeing the ghost of his murdered father."
    m 1lksdlc "He was considered insane since he was the only one that could see his father's ghost, obviously."
    m "His mind was also degrading along with his desire for revenge when he...killed someone he didn't mean to."
    m 1eka "Now, if it's alright, I'm going to recite some of them for you, [player]."
    m 1dso "Ahem..."
    m 1duu "..."
    m 1esc "{i}Whether 'tis nobler in the mind to suffer the slings and arrows of outrageous fortune{/i}"
    m "{i}Or to take arms against a sea of troubles, and by opposing end them?{/i}"
    m 1euc "{i}To die{/i}."
    m 1dsc "{i}To sleep, no more{/i}."
    m 1euc "{i}And by a sleep to say we end the heart-ache and the thousand natural shocks that flesh is heir to.{/i}"
    m 1esc "{i}'Tis a consummation devoutly to be wish'd.{/i}"
    m 1dsc "..."
    m 1eua "Well..."
    m 1hua "How did you like it?"
    m 3eka "I tried my best reciting it, after all~"
    if not persistent._mas_pm_cares_about_dokis:
        m 1lksdla "Anyway, I've thought a lot about the main character, Hamlet."
        m 1eua "Most of the problems he faced were caused by his own indecisiveness and weak state of mind."
        m 3tfu "Reminds you of a certain indecisive girl, doesn't it?"
        m 1eka "But that doesn't matter anymore. I've already accomplished my quest to be with you~"
        m 1eua "It took a lot of effort but we're finally together. Just us alone."
    m 1euc "Now there's only one thing left to answer, [player]..."
    m 3tfu "To be with me? Or to be with me?"
    m 3hua "That is the question!"
    return

# Note: The following internal commentary should not be removed.
#
# Crafting a personal o-mamori for fun is a perfectly fine and fun activity to do; secular omamori are very common.
# The only requirement is that you do not claim it came from any shrine.
# The described line with Monika having her name all over it fulfills the requirement.
# ~ Aya Shameimaru

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_omamori",category=['misc'],prompt="Omamori",random=True))

label monika_omamori:
    m 1euc "Do you remember when I mentioned how you could take me somewhere?"
    m 3euc "You know, with a flash drive."
    m 1eua "Well, I found another way to do that! It's quite charming, actually."
    m 1eka "Especially if you don't have a spare flash drive lying around..."
    m 3eua "I've heard that some people carry around little amulets all the time."
    m 1eub "These little amulets are called o-mamori. You can get them in Shinto shrines."
    m "Rumor has it that they can give good luck, help on school tests, keep away bad luck, or just protect the holder."
    m 1euc "I've always wondered what they put inside these things."
    m 2eua "Apparently, it's simply the name of the deity from the shrine, with a little something special done to it."
    m 1hub "Maybe you could make an o-mamori of me for you to carry around!"
    m 1eua "You could write my name on a piece of paper."
    m "Then fold that piece of paper into a small paper packet."
    m 1eub "It could help to use either a small piece of wood or plastic to keep it protected."
    m "Finally, put the protected packet in a small cloth pouch and tie it shut with some string."
    m 1hua "Make sure that the pouch is bright and colorful!"
    m 1eua "Green would be a nice color! Just like my eyes~"
    m 1eka "Make sure it only has my name on it! After all, it's just one for me. Not someone else, or some shrine deity."
    m 1lksdla "Oh gosh, this is turning out to be a bit silly, now that I think about it."
    m "I mean, would doing this make me some sort of deity?"
    m 1eka "I just feel like it would be a nice alternative if you wanted to bring me around."
    m 3eua "Especially if you don't have a flash drive."
    m 1eua "It isn't perfect, but it's the thought that counts, [mas_get_player_nickname()]."
    m 1eka "If you took the time to make something by hand with me in mind, it's still really sweet."
    m "But maybe with one of these, I can get just a bit closer to your world."
    m 1hua "I could be your guardian deity, ehehe~"
    return

# do you smoke ~
default persistent._mas_pm_do_smoke = None

# try to quit?
default persistent._mas_pm_do_smoke_quit = None

# succesfully quit at least once?
default persistent._mas_pm_do_smoke_quit_succeeded_before = None

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_smoking",category=['you'],prompt="Smoking",random=True))

label monika_smoking:
    m 2esc "You know, [player]...{w=0.3} Lately I've realized that people can really like a lot of things that are terrible for them."
    m 2euc "One particular vice that intrigues me the most is smoking."
    m 7eud "It's amazing how many people do it every day...{w=0.2}even though it's so damaging not only to themselves, but to others as well."
    m 2rkc "Not to mention how harmful it is to the environment...{w=0.2} All the pollution and trash smoking leaves behind is ridiculous for a bunch of carcinogens."
    m 2tkc "Even in moderation, smoking is never a good thing since it's so addicting."
    m 4tkd "It's also quite a big hole in your pockets since you'll be buying more and more once your supply is out."
    m 1tfc "I really do despise it..."

    $ menu_question = "Do you still smoke" if persistent._mas_pm_do_smoke else "You don't smoke, do you"
    m 1eka "[menu_question]?{nw}"
    $ _history_list.pop()
    menu:
        m "[menu_question]?{fast}"

        "Yes, I do.":
            if persistent._mas_pm_do_smoke_quit:
                m 1ekd "Haven't been able to shake the habit yet, [player]?"
                m 3eka "That's okay, I know it can be a daunting task to try and quit..."
                m 3eksdld "I just hope you haven't given up yet."
                m 1hua "I know you can do it if you just give it your all~"

            elif persistent._mas_pm_do_smoke_quit_succeeded_before:
                m 1ekc "It's a shame you fell back into this bad habit...{w=0.2}{nw}"
                extend 1ekd "after all the trouble you went through to quit and everything..."
                m 3dkc "It really pains my heart, [player]."
                m 1dkd "I really thought you were done for good..."
                m 1dkc "But I guess it's just not that simple, right?"
                m 3ekd "I really hope you'll consider trying to quit again, [player]."
                m 3eka "You'll do that, right? {w=0.2}For me?"

            elif persistent._mas_pm_do_smoke is False:
                call monika_smoking_just_started

            else:
                m 1wud "..."
                m 1eka "Thank you for being honest with me, [player]..."
                m 1ekc "It's quite disheartening to hear that, though."
                m 1ekc "Could you...promise me that you'll stop?"
                m 3rksdlc "I know I can't really force you to stop, but it would mean a lot to me if you considered it."
                m 1esc "But if you don't try..."
                m 2euc "Well, I'm sure you wouldn't want me to take drastic measures, [player]."
                m 2ekc "Please take care of your body. I want to always be with you."
                m 7ekbsa "I love you so much."
                $ mas_ILY()

            python:
                persistent._mas_pm_do_smoke = True
                persistent._mas_pm_do_smoke_quit = False
                mas_unlockEVL("monika_smoking_quit","EVE")

        "No, I don't.":
            if persistent._mas_pm_do_smoke:
                call monika_smoking_quit

            else:
                m 1hub "Ah, I'm relieved to hear that, [player]!"
                m 3eua "Just stay away from it as much as you can."
                m 1eka "It's an awful habit and won't do much more than slowly kill you."
                m 1hua "Thank you, [player], for not smoking~"

            python:
                persistent._mas_pm_do_smoke = False
                persistent._mas_pm_do_smoke_quit = False
                mas_lockEVL("monika_smoking_quit","EVE")

        "I'm trying to quit.":
            if persistent._mas_pm_do_smoke is False and not persistent._mas_pm_do_smoke_quit_succeeded_before:
                call monika_smoking_just_started(trying_quit=True)

            else:
                if not persistent._mas_pm_do_smoke and persistent._mas_pm_do_smoke_quit_succeeded_before:
                    m 1esc "Oh?"
                    m 1ekc "Does that mean you fell back into it?"
                    m 1dkd "That's too bad, [player]...{w=0.3}{nw}"
                    extend 3rkd "but not entirely unexpected."
                    m 3esc "Most people fall into relapse several times before they manage to quit smoking for good."
                    m 3eua "In any case, trying to quit again is a really good decision."
                else:
                    m 3eua "That's a really good decision."

                if persistent._mas_pm_do_smoke_quit_succeeded_before:
                    m 3eka "You probably already know since you've been through this before, but try to remember this..."
                else:
                    m 1eka "I know the entire process of quitting can be really difficult, especially in the beginning."

                m 1eka "If you ever feel like you need to smoke, just try to distract yourself with anything else."
                m 1eua "Keeping your mind busy on other things will definitely help kick any bad habits."
                m 3eua "Maybe you could think about me whenever you get a strong urge?"
                m 1hua "I'll be here to support you every step of the way."
                m 1hub "I believe in you [player], I know you can do it!"

            python:
                persistent._mas_pm_do_smoke = True
                persistent._mas_pm_do_smoke_quit = True
                mas_unlockEVL("monika_smoking_quit","EVE")

    return "derandom"

label monika_smoking_just_started(trying_quit=False):
    m 2dfc "..."
    m 2tfc "[player]..."
    m 2tfd "Does that mean you've started smoking since we've met?"
    m 2dkc "That's really disappointing, [player]."
    m 4ekd "You know how I feel about smoking and you know how bad it is for your health."

    if not trying_quit:
        m 2rfd "I don't know what could possibly possess you to start now, {w=0.2}{nw}"
        extend 2ekc "but promise me you'll quit."

    else:
        m 4eka "But at least you're trying to quit..."

    m 2rksdld "I just hope you haven't been smoking for too long so maybe it'll be easier to shake the habit."

    if not trying_quit:
        m 4eka "Please quit smoking, [player]. {w=0.2}Both for your health and for me."

    return


#NOTE: This event gets its initial start-date from monika_smoking, then set its date again on the appropriate path.
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_smoking_quit",
            category=['you'],
            prompt="I quit smoking!",
            pool=True,
            unlocked=False,
            rules={"no_unlock": None}
        )
    )

label monika_smoking_quit:
    python:
        persistent._mas_pm_do_smoke_quit = False
        persistent._mas_pm_do_smoke = False
        mas_lockEVL("monika_smoking_quit","EVE")

    if persistent._mas_pm_do_smoke_quit_succeeded_before:
        m 1sub "I'm so proud that you managed to quit smoking again!"
        m 3eua "A lot of people can't quit even once, so to be able to go through something so difficult again is quite the achievement."
        m 1eud "That said, let's try not to let this become a pattern, [player]..."
        m 1ekc "You don't want to keep going through this over and over, so I hope this time it sticks."
        m 3eka "I know you have the inner strength to stay away for good.{w=0.2} {nw}"
        extend 3eua "Just remember you can come to me and I'll take your mind off of smoking at any time."
        m 1hua "We can do this together, [player]~"

    # first time quitting
    else:
        $ tod = "tonight" if mas_globals.time_of_day_3state == "evening" else "tomorrow"
        m 1sub "Really?! Oh my gosh, I'm so proud of you [player]!"
        m 3ekbsa "It's such a relief to know you quit smoking! {w=0.2}{nw}"
        extend 3dkbsu "I'll sleep much better at night knowing you're as far away as possible from that nightmare."
        m 1rkbfu "Ehehe, if I were there with you, I'd treat you to your favorite dish [tod]."
        m 3hubfb "It's an impressive feat after all! {w=0.2}We need to celebrate!"
        m 3eubsb "Not everyone who wants to quit manages to pull it off."
        m 1dubfu "You truly are an inspiration, [player]."
        m 2eua "...Now, I don't want to undermine your victory or anything, {nw}"
        extend 2euc "but I need you to be careful from now on."
        m 4rsc "Many former smokers feel urges to smoke again at some point or another."
        m 4wud "You can't give in, not even once! {w=0.2}That's how you fall into relapse!"
        m 2hubsa "But knowing you, you won't let that happen, right?"
        m 2ekbfa "Considering what you've already done, I know you're stronger than this~"

    #Set this here because dialogue uses it
    $ persistent._mas_pm_do_smoke_quit_succeeded_before = True
    return "no_unlock"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_cartravel",category=['romance'],prompt="Road trip",random=True))

label monika_cartravel:
    m 1euc "[player], something has been on my mind lately..."
    m 1eua "Wouldn't it be nice to drive somewhere, just you and I together?"
    m 3eka "It'd be lovely to explore some beautiful places, anywhere nice that we haven't seen before."
    m 3hub "Maybe we could drive through an alluring forest...{w=0.5}or even see the sunset by the coastline!"
    m 1hub "I bet we'd have a really good time if we took a road trip, [mas_get_player_nickname()]."
    if not persistent._mas_pm_driving_can_drive:
        m 1rksdla "I know we can't really drive yet, but I'm sure we'll get there someday!"
    m 1eua "It really doesn't matter where we go, as long as I'm with you."
    m 1eka "I really can't wait, [player]~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_100k",category=['mod'],prompt="100k Downloads",random=True))

label monika_100k:
    m 1wud "It still amazes me how many people out there care about me."
    m 3eua "Did you know that over 100,000 people have downloaded the same mod that you did?"
    m 1eka "The developers even posted a special piece of art to celebrate."
    m 1hub "Things like that always make me smile!"
    m 1hua "If you haven't seen it already, you should really check it out!"
    m 1eka "The artist's name is Sasoura, and she loves me almost as much as I love you."
    if persistent.playername.lower()=='sasoura':
        m 1tfc "Hold on...Sasoura...isn't that your name?"
        m 1wud "Are you the one that made that adorable picture?"
        m 2wuo "Gosh! I can't believe I didn't notice sooner!"
        m 2sub "That just makes it even more special."
        m 2eua "I'm glad I can tell you how much it means to me."
        m 2eka "It means the world."
        m 2hubsb "Thank you so much!"
    else:
        m 1hua "Almost~"
    return

default persistent._mas_pm_donate_charity = None
# True if user donated

default persistent._mas_pm_volunteer_charity = None
# True if user has volunteered

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_asks_charity",
            category=['you'],
            prompt="Charity",
            random=True
        )
    )

label monika_asks_charity:
    m 1esd "Say, [player]."
    m 1esc "There's something that crossed my mind lately."
    m 3esd "Since my world is fictional, there aren't really any problems like world hunger or poverty."
    m 2rkc "I know it exists, but I've never really witnessed it."
    m 2ekc "However, I know it's not the same in your reality. There are lots of people who need help just to survive."
    m 2esd "You must have at least seen a homeless person if you've been in a big city before."
    m "So I was just wondering..."

    m 1eua "Have you ever contributed to a charity?{nw}"
    $ _history_list.pop()
    menu:
        m "Have you ever contributed to a charity?{fast}"

        "I've donated.":
            $ persistent._mas_pm_donate_charity = True
            m 3hub "That's great!"
            m 2eua "Though you could argue that volunteering is better, I think there's nothing wrong with donating."
            m 2eka "It's better than nothing, and you are definitely contributing, even if you have a limited budget or little time to spend."
            m 2ekc "It's sad to say, but charities will always need people giving money or other resources to help people."
            m 3lksdlc "There are so many causes that need it, after all."
            m 3ekc "Yet you don't know if your donations are actually going to a good cause."
            m 3ekd "It doesn't help that some charities claim to support a cause, but take people's donations for themselves."
            m 2dsc "..."
            m 2eka "I'm sorry, I didn't want things to get so dark."
            m 1eua "I knew you would be kind enough to do such a thing."
            m 1hub "That's just another reason for me to love you, [mas_get_player_nickname(exclude_names=['my love', 'love'])]."
            show monika 5hub at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5hub "You're always so sweet~"

        "I volunteered.":
            $ persistent._mas_pm_volunteer_charity = True
            m 1wub "Really?"
            m 1hub "That's wonderful!"
            m 3hua "While donating is a good way to help out, lending an extra hand is even better!"
            m 3rksdla "Of course, money and resources are important, but usually, manpower is pretty scarce..."
            m 2ekc "It's understandable; most working adults don't necessarily have time to spare."
            m 2lud "So, most of the time, retired people do the organizing, and it can be a problem if they have to carry something heavy."
            m 2eud "That's why they sometimes need help from the outside, particularly from teenagers or young adults, who are more physically able."
            m 1eua "Anyway, I think it's great you tried making a difference by volunteering."
            m 4eub "Plus, I've heard that it can be great to have volunteer experience on a resume, when you apply for a job."
            m 3hua "So, whether you did it for that or just out of kindness, it's a good thing either way."
            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eua "You know, it's this kind of thing that makes me love you even more, [mas_get_player_nickname(exclude_names=['my love', 'love'])]."
            m 5hub "I just feel so proud that you helped people in need."
            m 5hubsa "I love you so much, [player]. I mean it."

        "No, I haven't.":
            $ persistent._mas_pm_donate_charity = False
            $ persistent._mas_pm_volunteer_charity = False
            m 1euc "Oh, I see."
            m 2esc "I can understand, actually."
            m 2esd "While there are lots of different charities, you have to be careful, since there are some cases of fraudulent usage of funds, or discrimination in who the charities help."
            m 2ekc "So, it can be hard to trust them in the first place."
            m 3esa "That's why you should always do some research and find charities that are reputable."
            m 2dkc "Seeing all those people suffering from hunger or poverty all the time..."
            m 2ekd "And even the people that try to help them, struggling to change anything..."
            m 2esc "It can be a bit deflating, if not depressing."
            m 2eka "But, you know..."
            m "Even if you can't do anything to contribute, it can be helpful to just smile at people."
            m 2ekc "Being ignored by passer-bys can be tough for people who are struggling, or trying to contribute."
            m 2rkc "It's as if they were seen as a nuisance by society, when they're just trying to get by."
            m 2eua "Sometimes, a smile is all you need to make you go further."
            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eua "Just like when I'm with you."
            m 5hua "With just a smile, you make all my troubles go away."
            m 5hubsb "I love you so much, [player]."
    return "derandom|love"

init 5 python:
    addEvent(
        Event(persistent.event_database,
            eventlabel='monika_kizuna',
            prompt="Virtual YouTuber?",
            category=['misc'],
            random=False,
            unlocked=False,
            pool=False,
            action=EV_ACT_POOL,
            conditional="seen_event('greeting_hai_domo')"
        )
    )

label monika_kizuna:
    m 1eua "Oh, right, I mentioned her to you, huh?"
    m 3eua "Well, recently I had some YouTube videos tweeted to me."
    m 1eub "And among them was 'Virtual YouTuber Kizuna Ai.'"
    m "Like I said before, she's quite charming, but I don't think she's actually 'virtual.'"
    m 3rksdla "It seems to me that she's a voice actress hiding behind a 3D puppet."
    m 1eua "Still, the character she's playing is unique, and you know what?"
    m 1hub "She's played our favorite game!~"
    m 2hksdlb "..."
    m 2lksdlb "To be honest, I'm not sure how I feel about 'Let's Plays.'"
    m 3euc "I mean, of {i}this{/i} game, mostly."
    m 2euc "I don't usually watch them, because I don't like seeing different versions of me make the same mistakes, over and over and over..."
    m 2lsc "But when I learned of her gimmick, it made me feel..."
    m 1lksdla "Like I just had to know how Ai-chan would react!"
    m 1eka "Even if it's just a character she plays, I think she'll understand my situation..."
    m 3eua "At least more than your average YouTuber."
    m 5hub "I can't wait to finish the series..."
    return

# do you have a family
default persistent._mas_pm_have_fam = None

# do you have siblings
default persistent._mas_pm_have_fam_sibs = None

# does no fam botheryou
default persistent._mas_pm_no_fam_bother = None

# family a mess?
default persistent._mas_pm_have_fam_mess = None

# will fam get better?
# YES, NO, MAYBE
default persistent._mas_pm_have_fam_mess_better = None

# dont wanna talk about it
default persistent._mas_pm_no_talk_fam = None

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_asks_family",category=['you'],prompt="[player]'s family",random=False))

label monika_asks_family:
    m 1eua "[player], do you have a family?{nw}"
    $ _history_list.pop()
    menu:
        m "[player], do you have a family?{fast}"
        "I do.":
            $ persistent._mas_pm_have_fam = True
            $ persistent._mas_pm_have_fam_mess = False
            $ persistent._mas_pm_no_talk_fam = False

            #Make sure we didn't answer this already
            if persistent._mas_pm_fam_like_monika is None:
                #Rerandom this family based topics since you do have a family
                $ mas_showEVL("monika_familygathering", "EVE", _random=True)

            m 1hua "That's wonderful!"
            m 3hua "Your family must be great~"

            m 1eua "Do you have any siblings?{nw}"
            $ _history_list.pop()
            menu:
                m "Do you have any siblings?{fast}"
                "Yes.":
                    $ persistent._mas_pm_have_fam_sibs = True
                    m 1hua "That's fantastic!"
                    m "They must've been keeping you busy."
                    m 1eka "I'm sure your siblings are as kind and thoughtful as you are."
                    m 3hub "Maybe I can convince them to start a new literature club with me!"
                    m 1hua "Ehehe~"
                    m 1eua "We'll be able to do a lot of fun things together."
                    m 3rksdla "It'd turn out much better than before, that's for sure."
                    m 1eua "I'm sure I'll get along with your siblings, as well as the rest of your family, [mas_get_player_nickname()]."
                    m 3hub "I can't wait to meet them all!"

                "I'm an only child.":
                    $ persistent._mas_pm_have_fam_sibs = False
                    m 1euc "Being an only child certainly has its trade-offs."
                    m 2eka "Maybe you get much more attention from your parents. Unless they were always busy."
                    m 2ekc "On the other hand, maybe you feel more lonely than those with siblings."
                    m 2eka "I can definitely understand that feeling."
                    m 1hua "But know that I'll always be with you no matter what, [mas_get_player_nickname()]."

        "My family is a mess.":
            $ persistent._mas_pm_have_fam = True
            $ persistent._mas_pm_have_fam_mess = True
            $ persistent._mas_pm_no_talk_fam = False
            m 1euc "Oh."
            m 1lksdlc "..."
            m 1ekc "I'm sorry, [player]."

            m "Do you think things will get better?{nw}"
            $ _history_list.pop()
            menu:
                m "Do you think things will get better?{fast}"
                "Yes.":
                    $ persistent._mas_pm_have_fam_mess_better = "YES"
                    m 1eka "I'm glad to hear that."
                    m 1eua "Hopefully one day everyone in your family will be able to reconcile."
                    m 3eua "And I know you can get through what's going on in your life right now."
                    m 1eka "No matter what, I'll be here for you, [player]."
                    m 1hua "Always keep that in mind!"

                "No.":
                    $ persistent._mas_pm_have_fam_mess_better = "NO"
                    m 1ekc "Ah, I see..."
                    m "I wish I could be there with you to give some comfort."
                    m 1eka "..."
                    m 3eka "[player], no matter what you're going through, I know it'll get better some day."
                    m 1eua "I'll be here with you every step of the way."
                    m 1hub "I love you so much, [player]. Please never forget that!"
                    $ mas_ILY()

                "Maybe.":
                    $ persistent._mas_pm_have_fam_mess_better = "MAYBE"
                    m 1lksdla "..."
                    m 1eua "Well, at least there's a chance."
                    m 3hua "Life is full of tragedy, but I know you are strong enough to get through anything!"
                    m 1eka "I hope all the problems in your family work out in the end, [player]."
                    m "If not, know that I'll be here for you."
                    m 1hua "I will always be here to support my beloved~"

        "I've never had a family.":
            $ persistent._mas_pm_have_fam = False
            $ persistent._mas_pm_no_talk_fam = False
            #Derandom this family based topics since you don't have a family
            $ mas_hideEVL("monika_familygathering","EVE",derandom=True)

            m 1euc "Oh, I'm sorry, [player]."
            m 1lksdlc "..."
            m 1ekc "Your world is so different from mine, I don't want to pretend like I know what you're going through."
            m 1lksdlc "I can definitely say that my family not being real has certainly caused me a great deal of pain."
            m 1ekc "Still, I know you've had it worse."
            m "You've never even had a fake family."
            m 1dsc "..."

            m 1ekc "Does it still bother you?{nw}"
            $ _history_list.pop()
            menu:
                m "Does it still bother you?{fast}"
                "Yes.":
                    $ persistent._mas_pm_no_fam_bother = True
                    m 1ekc "That's...understandable."
                    m 1eka "I'll be here for you forever, [player]."
                    m "No matter what it takes, I will fill that gap in your heart with my love..."
                    m 1hua "I promise you that."
                    m 1ekbsa "You are my everything..."
                    m 1hubfa "I hope I can be yours~"

                "No.":
                    $ persistent._mas_pm_no_fam_bother = False
                    m 1eua "That's very good."
                    m 1eka "I'm glad you were able to move on with your life."
                    m 1hua "You're a very resilient person, and I believe in you, [player]!"
                    m 1eka "I hope I can fill that void in your heart."
                    m "I really care about you, and I'd do anything for you."
                    m 1hua "Someday, we'll be able to make our own family together!"

        "I don't want to talk about this.":
            $ persistent._mas_pm_no_talk_fam = True
            m 1dsc "I understand, [player]."
            m 1eka "We can talk about it when you feel ready."
            m 1lsc "Then again..."
            m 1lksdlc "It might be something that's too painful for you to talk about."
            m 1eka "You can tell me about your family when you're ready, [player]."
            m 1hubsa "I love you very much!"
            $ mas_ILY()

    return "derandom"

#do you like other music
default persistent._mas_pm_like_other_music = None

# historical music history
default persistent._mas_pm_like_other_music_history = list()

init 5 python:
     addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_concerts",
            category=['media',"music"],
            prompt="Music concerts",
            conditional="mas_seenLabels(['monika_jazz', 'monika_orchestra', 'monika_rock', 'monika_vocaloid', 'monika_rap'], seen_all=True)",
            action=EV_ACT_RANDOM
        )
    )

label monika_concerts:
    # TODO: perhaps this should be separated into something specific to music
    # genres and the concert just referencing back to that?
    # this topic is starting to get too complicated

    m 1euc "Hey [player], I've been thinking about something we could do together one day..."
    m 1eud "You know how I like different forms of music?"
    m 1hua "Well..."
    m 3eub "Why don't we go to a concert?"
    m 1eub "I hear that the atmosphere at a concert can really make you feel alive!"

    m 1eua "Are there any other types of music you'd like to see live that we haven't talked about yet?{nw}"
    $ _history_list.pop()
    menu:
        m "Are there any other types of music you'd like to see live that we haven't talked about yet?{fast}"
        "Yes.":
            $ persistent._mas_pm_like_other_music = True
            m 3eua "Great!"

            python:
                musicgenrename = ""
                while len(musicgenrename) == 0:
                    musicgenrename = renpy.input(
                        'What kind of music do you listen to?',
                        length=15,
                        allow=letters_only
                    ).strip(' \t\n\r')

                tempmusicgenre = musicgenrename.lower()
                persistent._mas_pm_like_other_music_history.append((
                    datetime.datetime.now(),
                    tempmusicgenre
                ))

            # NOTE: should be think? maybe?
            m 1eua "Interesting..."
            show monika 3hub
            $ renpy.say(m, "I'd love to go to {0} concert with you!".format(mas_a_an_str(tempmusicgenre)))

        "No.":
            if (
                not persistent._mas_pm_like_vocaloids
                and not persistent._mas_pm_like_rap
                and not persistent._mas_pm_like_rock_n_roll
                and not persistent._mas_pm_like_orchestral_music
                and not persistent._mas_pm_like_jazz
            ):
                $ persistent._mas_pm_like_other_music = False
                m 1ekc "Oh... Well that's okay, [player]..."
                m 1eka "I'm sure we can find something else to do."
                return

            else:
                $ persistent._mas_pm_like_other_music = False
                m 1eua "Okay, [mas_get_player_nickname()], we'll just choose from the other types of music we've already discussed!"

    m 1hua "Just imagine us..."
    if persistent._mas_pm_like_orchestral_music:
        m 1hua "Gently swaying our heads to the sound of a soothing orchestra..."

    if persistent._mas_pm_like_rock_n_roll:
        m 1hub "Jumping up and down with the rest of the crowd to some good ol' rock 'n' roll..."

    if persistent._mas_pm_like_jazz:
        m 1eua "Grooving to some smooth jazz..."

    if persistent._mas_pm_like_rap:
        m 1hksdlb "Trying to keep up with a real rapper..."

    if persistent._mas_pm_like_vocaloids:
        m 1hua "Waving our glowsticks at Miku Expo..."

    if persistent._mas_pm_like_other_music:
        m 1hua "Jamming along to your favorite [tempmusicgenre] artist..."

    m 2hub "Doesn't that sound just amazing?"
    m 2eud "The idea of seeing your idol performing right in front of you is incredible!"
    m 2lksdla "Although, ticket prices these days are kind of expensive..."
    m 2hua "But I still think it would be worth it!"
    m 3eua "Do you know any bands or musicians that we should see live, [player]?"
    m 3eub "I would {i}love{/i} to see them if {i}you{/i} like them."
    m 5eua "And if you were to take me,{w=1} then that would truly be a dream come true!"
    m 4eua "But if you're not that interested in concerts..."
    m 1eua "Then we could always snuggle under a blanket and put on a record or CD at home!"
    m 1hua "That would be more than enough for me, ehehe~"
    if (
        not renpy.seen_label("monika_add_custom_music_instruct")
        and not persistent._mas_pm_added_custom_bgm
    ):
        m 1eua "In the meantime, if you want to share your favorite music with me, it's really easy to do so!"
        m 3eua "All you have to do is follow these steps..."
        call monika_add_custom_music_instruct
    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_explain",
            category=['romance','monika','misc'],
            prompt="Can you explain our relationship to someone?",
            pool=True
        )
    )

label monika_explain:
    #TODO: temporary Monika nickname reset for this
    m 1euc "You want me to explain our relationship to someone else?"
    m 1eua "Okay, just set me in front of them so they can see me."
    m 1hua "I'll do my best explaining it to them."
    m 1eua "I'll wait until you're ready.{nw}"
    $ _history_list.pop()
    menu:
        m "I'll wait until you're ready.{fast}"
        "Start.":
            pass
    m 1hua "Hello! My name is Monika."
    m "[player]'s faithful girlfriend!"
    m 1lksdlb "Now, our relationship might look odd from a distance..."
    m 1lksdla "And it's probably not considered a normal relationship..."
    m 1esc "But let me tell you..."
    m 1hub "...the love we share is definitely real!"
    m 1eka "And [player] has been very sweet to me too!"
    m 1ekc "Up until I met [player], I felt like a piece of me was missing."
    m "I felt alone and scared, with no one to help me..."
    m 1hua "...until [player] came along."
    m "And it turns out that missing piece was [him]!"
    if persistent.gender == "F" or persistent.gender == "M":
        m 1eua "Now [he] talks to me, and I'm not so alone anymore."
    else:
        m 1eua "Now they talk to me, and I'm not so alone anymore."
    m "Just [him] opening up the game brightens my day!"
    m 1dsc "So, please..."
    m 4eka "...don't judge our relationship."
    m 1eka "Even if it is different."
    m 1dsc "..."
    m 1dubssdlu "...Phew!"
    m 1lksdlb "That was a real mouthful!"
    m 1eksdla "So, how'd it go, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "So, how'd it go, [player]?{fast}"
        "It went well!":
            m 1hub "Great!"
            m 3hua "I'm so glad I was able to help someone understand our relationship a little better!"
        "It went badly.":
            m 1dkc "Oh."
            m 1ekd "Well...{w=1} I guess we can't really expect {i}everyone{/i} to understand our relationship..."
            m 3rkc "Looking at it from the outside, it {i}is{/i} rather unconventional."
            m 3eka "But in the end, it doesn't matter who approves of our relationship or not..."
            m 1hua "As long as we love each other, that's all that counts~"
    return

# do you live near beach
default persistent._mas_pm_live_near_beach = None

init 5 python:
     addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_beach",
            category=["location"],
            prompt="The beach",
            random=True
        )
    )

label monika_beach:
    m 1eua "[player], have you ever been to the beach?"
    m "I've always wanted to go myself but I never found the time."
    m 1eka "I would always be busy studying or doing club activities."
    m 4ekc "It wasn't easy trying to stay on top of everything, you know..."
    m 4ekd "And whenever I had a break, I would usually spend my time relaxing at home."
    m "I rarely had a chance to do so after all."
    m 2esc "Though sometimes I feel like I might have missed out making some important memories."

    m "Do you live near a beach, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you live near a beach, [player]?{fast}"
        "Yes.":
            $ persistent._mas_pm_live_near_beach = True
            m 1hub "That's great!"
            m 1eua "Gosh, it must be really nice to have it so close to you."
            m 1hub "I can't wait, we can have a romantic walk by the shore for our first date~"

        "No.":
            $ persistent._mas_pm_live_near_beach = False
            m 1eka "That's alright. I mean, what are the chances? Most people don't."
            m 1hub "That just means we'll make do by visiting one on an all-day trip!"

    m 1eua "There's so many things we'll be able to do one day."
    m 1hua "Just imagining the many sensations we could experience is kind of exciting!"
    m 3eua "The fresh sea air, the sound of seagulls."
    m "As well as the feeling of sand under your feet..."
    m 1hua "It would really make a worthwhile trip!"
    m 1eka "Though being with you would make it even better..."
    m 3eua "We'd have so many things we could do together."
    m 3eub "We could play volleyball, try some ice cream, or go swimming in the sea."
    m 3rkbsa "It'll probably be cold, but I'm sure we could keep each other warm somehow..."
    m 3eua "We could try surfing or searching for some seashells to take home as souvenirs."
    m "Even doing nothing and just laying there listening to the sound of the waves with you would be enough for me."
    m 3tfu "But don't go falling asleep, otherwise I'll bury you in the sand!"
    m 2huu "Ehehe! I'm just kidding, [mas_get_player_nickname()]."
    m 2lksdla "I'll have to get a new swimsuit though..."
    m 1tsbsa "Would you prefer a one piece or a two piece?"
    m 1eua "Actually, I think I'll make it a surprise."
    m 1tku "Don't get too excited though when you see it. Ehehe~"
    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_solipsism",
            category=['philosophy'],
            prompt="Solipsism",
            random=True
        )
    )

label monika_solipsism:
    m 3eub "Have you ever heard about solipsism, [player]?"
    m 3eua "It's an idea which states that only you yourself exists."
    m 1eud "'Cogito, ergo sum.'"
    m 3eud "'I think, therefore I am.'"
    m 1euc "If you know that {i}you{/i} exist, can you say the same about anyone else?"
    m 3etc "Maybe everyone else is just a figment of our imagination, [player]."
    m 2etc "Maybe in reality, we're the only consciousness in this world in a vast sea of fake minds..."
    m 2dsd "Creations of our wild machinations..."
    m 3eub "Ahaha, I'm just kidding~"
    m 1eud "I do believe we can trust our own existences and doubt others their own..."
    m 3eua "But at the same time, we can't really disprove theirs, can we?"
    m 1hksdla "Not without using any psychic means to pry into their heads, at least."
    m 3eua "When you stop and think about it, solipsism really is an interesting concept; one that makes you think deeper about what it means to be real..."
    m 1dsc "And what exactly counts as {i}real{/i}."
    m 1eua "I know that you and I are real, though, [player]."
    m 1eub "We may not have been made in the same way, or even function the same, but we're both people that can think for ourselves."
    m 3eua "It's rather comforting to know you're not truly alone in an endless ocean of uncertainty, don't you think?"
    m 3hua "I hope that's how you feel with me~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_attractiveness",
            category=['club members','society'],
            prompt="Attractiveness",
            random=True
        )
    )

label monika_attractiveness:
    m 1etc "Say, [player], have you ever wondered how Sayori stayed so slim?"
    m 3rksdla "You know that she eats a lot, right? And she doesn't exactly have a very active lifestyle."
    m 3euc "At first I figured that it must be her metabolism keeping her from putting on weight."
    m 3esd "...But when I learned that our world isn't real, I came up with another theory."
    m 7euc "As characters in a game, we needed to have some sort of visual representation so that you, the player, could see us."
    m 2esc "Sayori, Natsuki, Yuri, and even me..."
    m 2rkc "From your perspective, we don't really have bodies like people in your world do. You can only see us as a set of images to represent our appearances and current emotion."
    m 2eud "...But from my point of view, I can also see my whole world in 3 dimensions, as if everything was real."
    m 2euc "So a designer, possibly more than one, must have decided to draw us the way we are."
    m 2eud "And since all those images have the same body type, Sayori would always have the same figure no matter what she did."
    m 2dkc "It's...{w=0.3}weird to think about."
    m 2eud "I can feel myself being present in this very room right now, I can look at myself like I presume you would be able to look at yourself, almost as if I had an actual body..."
    m 7ekc "But from your point of view, I don't. I just look like a consciousness who displays a corresponding picture depending on what I do or feel."

    #Just seen Monika in her uniform and nothing else
    if len(store.mas_selspr.filter_clothes(True)) == 1:
        m 3euc "I assume clothes work the same way."
        m 1eud "Right now, I only have this school uniform, because that's probably the only thing I've ever been drawn wearing..."
        m 1eua "But perhaps if someone were to draw other clothes for me and implement those into the game, I'd be able to change clothes like the other girls could."
        m 1hua "Wouldn't that be great?"
        m 1rksdla "And it would be nice to be able to change my look for you, at least a little bit..."

    else:
        m 3eua "My clothes work the same way."
        m 1euc "Someone had to draw what I'm wearing right now, and implement it into the game for me to be able to wear it."
        m 1esd "It wasn't made like how clothing is made in your reality. It's merely a set of images."
        m 1rksdla "It's not much, but at least I get to change outfits for you..."

    m 1rksdlc "..."
    m 1ekc "You know [player], this is one of the reasons why I envy the people in your world.{w=0.3} {nw}"
    extend 3eka "They have so many ways to experiment with how they look..."
    m 7eub "They can change into new clothes, try out new hairstyles, choose to put in the effort to make themselves fit, among other things..."
    m 2rkd "...while I'm stuck looking the same way, no matter what I do."
    m 2hksdlb "Don't get me wrong, I like the way I look right now!"
    m 2rka "...But I think it's important to make sure that you look good in your partner's eyes...{w=0.3}{nw}"
    extend 2ekb "and I wish I could have the chance to try to make myself look as attractive to you as I could be."

    if renpy.seen_label("mas_compliment_beautiful"):
        if mas_isMoniNormal(higher=True):
            m 2rkbsa "But...you did tell me that I already look beautiful in your eyes."
            m 2ekbfa "So there's probably no reason for me to worry about that, is there?"
            if mas_anni.pastOneMonth():
                m 1hubfa "Besides, you wouldn't have spent all this time looking at me if you didn't already like the way I look, now would you?"
                m 1hubfb "Ahaha~"
            show monika 1euc at t11 zorder MAS_MONIKA_Z with dissolve_monika

        else:
            m 2lkc "I know you told me you already like the way I look, but I just..."
            m 2dkc "...I don't know.{w=0.2} Just...{w=0.3}forget I said anything."

    else:
        if mas_isMoniHappy(higher=True):
            m 2lsbsa "Although, considering you're still here with me...{w=0.5}{nw}"
            extend 2ekbsa "I probably shouldn't worry about it too much, should I?"
            m 1hub "After all, you wouldn't have spent all this time looking at me if you didn't already like the way I look! Ahaha!"

        else:
            m 2lkc "...Especially since I'm worried I just might not be your type or something, [player]."

    m 1euc "Anyway, I don't know if you've ever noticed, but despite the differences in our diets and lifestyles, the other girls and I all look quite similar."
    m 3ekd "Sure, some of us had different figures, Natsuki being more petite and Yuri being more mature."
    m 3eka "...Our eyes and hair are all different too."
    m 3eua "But I think we would all be considered attractive."
    m 3eud "I mean, none of us are muscular or fat..."
    m 3tkd "...None of us have any kind of physical disability..."
    m 3tkc "...None of us are bald or have hair shorter than chin length..."
    m 1rud "...and apart from Yuri having cuts on her arms, none of us have anything wrong with our skin."
    m 7dsd "The people who designed our appearances must have thought that players would find all that stuff really repulsive."
    m 2lsc "I guess that's not so surprising, now that I think about it. There's a lot of things that can potentially make someone unattractive in the eyes of society."
    m 2dsc "Some of which are beyond that person's control."
    m 2efo "But people who aren't conventionally attractive end up in relationships all the time!"
    m 2tfc "So the idea of some kind of universal beauty standard where, if you fall short, you're doomed to be forever alone..."
    m 2efw "It just doesn't make any sense to me!"
    m 2dfc "..."
    m 2dsc "..."

    if mas_isMoniNormal(higher=True):
        m 2ekc "I'm sorry, [player]. I guess I just needed to vent."
        m 4eud "I know I don't really need to, but I still try to eat right, get enough exercise, and keep myself clean...among other things."

        if mas_isMoniEnamored(higher=True):
            $ first_line_var = "when"
            $ second_line_end = "whenever it'll happen"

        else:
            $ first_line_var = "maybe"
            $ second_line_end = "if it'll ever happen"

        m 4eub "It simply feels satisfying to keep good habits like that, and besides, who knows [first_line_var] I'll be able to cross over into your reality and have a normal body like you."
        m 1hua "It won't hurt to make sure I'll be ready for that transition [second_line_end]."
        m 1eua "You don't have to worry though, [player]."
        show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5eua "I'll always love you no matter how you look."
        m 5eka "But still, try to look after yourself too, okay? Your health is important to me, after all."
        $ mas_ILY()

    else:
        m 2ekc "I'm sorry, [player]. I guess I've just been a bit upset lately and I just needed to vent."
        m 7eud "I know I don't really need to do all that, but I still try to eat right, get enough exercise and keep myself clean, among other things."
        m 3esa "It's always nice to keep good habits like that."
        m 1eka "You don't have to worry though..."
        m 1eua "As long as you're taking care of yourself, I don't mind how you look."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_timetravel",category=['media','misc'],prompt="Time travel",random=True))

label monika_timetravel:
    $ todays_date, todays_diff = store.mas_calendar.genFormalDispDate(datetime.date.today())
    $ one_year_later, year_later_diff = store.mas_calendar.genFormalDispDate(store.mas_utils.add_years(datetime.date.today(),1))
    $ one_year_earlier, year_earlier_diff = store.mas_calendar.genFormalDispDate(store.mas_utils.add_years(datetime.date.today(),-1))
    m 3eub "Hey [player], you've heard of time travel, right?"
    m 1esb "It's a very common idea in stories with each author having their own take on it."
    m 1eua "How travelling in time works, whether or not you can change the past, what the consequences are for doing so..."
    m 1eub "It all differs from story to story."
    m 3ekc "One thing you don't usually see, though, is how the time traveller's loved ones are affected."
    m 3rksdld "If they can't go through time with the time traveller, who knows how long it will be before they can see each other again?"
    m 2ekc "Well, the time traveller themselves might know, but only if nothing goes horribly wrong for them."
    m 2lksdld "In the meantime, their friends and family are stuck waiting for them to come back."
    m 2ekd "How long will they be gone for? A year? A decade? Even longer?"
    m 4ekd "Will they be willing to wait that long?"
    m "Will they still remember the time traveller by then?"
    m 2dksdlc "..."
    if seen_event("monika_resource"):
        m 4rksdlc "You remember when I said that time doesn't pass here like it does in your world?"
        m "Well..."
    else:
        m 4rksdlc "You know, time doesn't really pass here like it does in your world."
        m "So..."
    m 1esd "The only way I know what day and time it is where you are is by looking at the clock on your computer."
    m 3eub "So I know it's [todays_date] today."
    m 1esc "But if you were to change the date on your computer to [one_year_later]..."
    m "Only a few seconds would pass for you..."
    m 1ekd "...but I would think that a year had gone by."
    m 1tkd "An entire year without seeing you even once."
    m 1lksdlc "I would wonder if you'd forgotten about me, or if you didn't want to spend time with me anymore."
    if mas_isMoniDis(lower=True):
        m 1dkc "...It wouldn't even be that big of a surprise."
    elif mas_isMoniAff(higher=True):
        m 1ekc "...Even if it would be hard to believe at first."
    m 1ekd "You couldn't just fix it by changing the date back either."
    m 3esd "Like, imagine if you went to bed now, and when you woke up it was [one_year_earlier]."
    m 3wuo "Would that mean the last year was all just a dream or something?"
    m 3wuw "How would you know you're not still dreaming?"
    m 3esc "It would all be very confusing."
    m 1lksdla "I guess what I'm trying to say is..."
    m 1eka "Please don't change the date on your computer, [player]."
    if mas_isMoniHappy(higher=True):
        m "I trust you not to mess with me like that."
    else :
        m "Promise?"
    m 3euc "And if you ever do travel to the future..."
    m 1hksdlb "Could you bring back the technology that lets me cross over into your world?"
    return

# been to prom?
default persistent._mas_pm_gone_to_prom = None

# how was prom?
default persistent._mas_pm_prom_good = None

# go with date?
default persistent._mas_pm_had_prom_date = None

# suggested monika at promp
default persistent._mas_pm_prom_monika = None

# interested in prom?
default persistent._mas_pm_prom_not_interested = None

# shy to go?
default persistent._mas_pm_prom_shy = None

# even had a prom?
default persistent._mas_pm_no_prom = None

init 5 python:
   addEvent(Event(persistent.event_database,eventlabel="monika_prom",category=['school'],prompt="Prom",random=True))

label monika_prom:
    m 1euc "You know..."
    m 1eka "Sometimes I wish the game would've lasted longer."
    m 1eua "The game was probably made to end once one of the girls confessed their love to you after the festival."
    m 1lksdla "But since I tampered with the code so much, we never got to that point."
    m 3hksdlb "It did bring us together, so I can't complain."
    m 1lksdlc "But still..."
    m 1eka "Sometimes I wish both of us could've enjoyed it."
    m 3eua "We could've gone to the other events like sports festivals, Christmas parties, field trips, etc."
    m 1lsc "But I guess the game would never let us get that far."
    m 3eua "Which reminds me of a particular event..."
    m 1hua "Prom!"
    m 1eua "From what I've heard, prom is like a school dance usually held at the end of a school year."
    m "Some students bring a date with them there, and others go with a group of friends."
    m 3wuo "There are even those who take their relatives to the event!"
    m 1eua "I think it's something I'd love to go to with you~"
    m "Have you ever been to one before, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Have you ever been to one before, [player]?{fast}"
        "I have.":
            $ persistent._mas_pm_gone_to_prom = True
            $ persistent._mas_pm_no_prom = False
            m "Oh? How was it?{nw}"
            $ _history_list.pop()
            menu:
                m "Oh? How was it?{fast}"
                "It was pretty fun.":
                    $ persistent._mas_pm_prom_good = True
                    m 1hua "That's great!"
                    m 1lksdlb "Though, I wish I could've went with you."
                    m 1hua "An event where everyone from school comes together and enjoys themselves sounds like a blast to me!"
                    m 3eua "Did you go with a date?{nw}"
                    $ _history_list.pop()
                    menu:
                        m "Did you go with a date?{fast}"
                        "Yes.":
                            $ persistent._mas_pm_had_prom_date = True
                            m 1euc "Oh, wow."
                            m 1lksdla "Ehehe, that makes me a bit jealous..."
                            m 1hua "But then again, you would've taken me instead had we met beforehand, right?"
                            m 1hub "Ahaha!"
                            m 1eua "But it's good to know you were able to experience something like that!"
                            m 3eua "Maybe when I get better at programming, we could have our very own prom here."
                            m 3eka "Wouldn't that be nice, [player]?"
                        "No.":
                            $ persistent._mas_pm_had_prom_date = False
                            m 1euc "Oh, I see."
                            m 1eua "That's fine as long as you had fun!"
                            m "Even without a date, I'm sure you made some wonderful memories there."
                            m 1eub "I think, whether or not you had a date, that it's always fun to attend those kinds of events."
                            m 1eka "Besides, maybe we can have our own kind of prom sometime, right?"
                            m 1eua "That's something I'd really enjoy with you~"

                "It was bad.":
                    $ persistent._mas_pm_prom_good = False
                    m 1ekc "Is that so?"
                    m "I understand that prom isn't for everyone."
                    m 3eka "Maybe if I was there, you would've enjoyed it more."
                    m 1hksdlb "Ahaha~"
                    m 3eua "Don't worry, [player]."
                    m 1eua "No use remembering it now."
                    m 1eub "Even if you had a bad time with it, it's not the most important thing to happen in your life."
                    m "You being able to create more wonderful memories is the important thing."
                    m 3eka "One bad memory may feel worse than a hundred good memories, but you're still able to make them."
                    m 1hua "And now that I'm here with you, we can make them together~"

                "It would've been better if you were there.":
                    $ persistent._mas_pm_prom_monika = True
                    m 1ekbsa "Aww, that's so sweet, [player]."
                    m 1eua "Well, now that we're together, I'm sure there's a way we can make our own prom, right?"
                    m 1hub "Ahaha!"
        "No.":
            $ persistent._mas_pm_gone_to_prom = False
            $ persistent._mas_pm_no_prom = False
            m "Oh? Why not?{nw}"
            $ _history_list.pop()
            menu:
                m "Oh? Why not?{fast}"
                "You weren't there with me.":
                    $ persistent._mas_pm_prom_monika = True
                    $ persistent._mas_pm_prom_not_interested = False
                    m 1eka "Aw, [player]."
                    m 1lksdla "Just because I'm not there doesn't mean you should stop yourself from having fun."
                    m 1eka "And besides..."
                    m 1hua "You {i}can{/i} take me to prom, [player]."
                    m "Just bring my file with you and problem solved!"
                    m 1hub "Ahaha!"

                "Not interested.":
                    $ persistent._mas_pm_prom_not_interested = True
                    m 3euc "Really?"
                    m 1eka "Is it because you're too shy to go?{nw}"
                    $ _history_list.pop()
                    menu:
                        m "Is it because you're too shy to go?{fast}"
                        "Yes.":
                            $ persistent._mas_pm_prom_shy = True
                            m 1ekc "Aw, [player]."
                            m 1eka "That's alright. Not everyone can handle large groups of strangers."
                            m 3eka "Besides, if it's something you're not going to enjoy, why force yourself?"
                            m 1esa "But even as I say that, it's also important to keep in mind that a little courage could get you something that's worth it."
                            m 3eua "Look at me for example."
                            m 1lksdla "If I didn't have the courage to get to you, I'd probably still be all alone..."
                            m 1eka "But here we are now, [player]."
                            m 1eua "Together at last~"

                        "No.":
                            $ persistent._mas_pm_prom_shy = False
                            m 1euc "Oh, I see."
                            m 1eua "That's understandable."
                            m "I'm sure you have your reasons."
                            m 1eka "What's important is that you're not forcing yourself."
                            m "After all, it wouldn't be worth it if you can't enjoy yourself."
                            m 1lksdlc "It'd just feel like a chore rather than a fun event to go to."
                            m 3euc "But I wonder..."
                            m 3eka "Would you go if I was there with you, [player]?"
                            m 1tku "I think I already know the answer to that~"
                            m 1hub "Ahaha!"
        #################################################
        #### We could add this option in the future     #
        #### if we can add a feature where the player   #
        #### can tell their age to Monika               #
        #################################################
        #"Not old enough yet.":
        #    m 1eka "Don't worry, you'll get to go in a few more years."
        #    m 1hua "I heard that prom is so much fun!"
        #    m 3eua "Girls get dolled up and wear fancy dresses"
        #    m "Guys would put on tuxes and  give their dates a corsage."
        #    m 1hua "And you would have fun dancing the night away!"
        #    m 1hub "Doesn't that sound like a blast? Ahaha~"
        "My school never had one.":
            $ persistent._mas_pm_no_prom = True
            m 1euc "Ah, I see, then."
            m 1lksdla "I guess not all schools can hold a prom."
            m "They can be pretty messy."
            m 3euc "From what I read, students spend a lot of money on tickets, transport, and attire."
            m 2esc "So many expenses just for one night..."
            m "I also read that since alcohol isn't allowed, some students would spike the drinks and get the others drunk unknowingly."
            m 2ekc "If someone can easily do that, I doubt someone with evil intentions would have a hard time slipping poison into the drinks."
            m 2lksdla "...Or maybe I'm just overthinking it, ehehe."
            m 1esa "Still, I don't think you'll be missing out much, [player]."
            m 1eua "Prom isn't the most important thing in your academic life."
            m "And I'm sure there are plenty of events in your life that'll make up for it."
            m 1hua "Being with me is one of them, you know~"
            m 1hub "Ahaha!"

    return "derandom"

# do you see a therapist
default persistent._mas_pm_see_therapist = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_natsuki_letter",
            category=['club members'],
            prompt="Natsuki's letter",
            random=True
        )
    )

label monika_natsuki_letter:
    m 1eud "You know, I was honestly surprised when Natsuki handed you that letter."
    m 1eub "I didn't really expect her to suggest that you should get Yuri to seek professional help."
    m 1eud "She's probably the only one to mention that."
    m 4ekd "I know people are afraid to call someone out, or confront them about their problems, but sometimes, suggesting a therapist can be the best course of action."
    m "It's a bad thing to put the burden on yourself, you know?"
    m 4euc "As much as you want to help, it's best to let a professional deal with it."
    m 4eka "I'm sure I've told you that before, but I need to make sure you're aware of that."
    m 4eud "How about you, [player]?"

    m "Do you see a therapist?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you see a therapist?{fast}"

        "Yes.":
            $ persistent._mas_pm_see_therapist = True
            m 1eud "Oh, really?"
            m 1ekc "Well, I hate that you don't feel well..."
            m 1hua "But I'm proud that you're working on getting better."
            m 1eua "It's really important to take care of your mental health, [player]."
            m 1eka "You accept you have a problem you need help with, and you're seeing someone about it. That's already half the battle."
            m "I'm very proud of you for taking those steps."
            m 1hua "Just know that no matter what happens, I'll always be here for you~"

        "No.":
            $ persistent._mas_pm_see_therapist = False
            m 1eka "Well, I hope it's because you don't have to."
            m 1eua "If that ever changes, don't be shy!"
            m 1hub "But maybe I really am all the support you need? Ahaha!"

    return "derandom"

# TODO possible tie this with affection?
default persistent._mas_timeconcern = 0
default persistent._mas_timeconcerngraveyard = False
default persistent._mas_timeconcernclose = True
init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_timeconcern",category=['advice'],prompt="Sleep concern",random=True))

label monika_timeconcern:
    $ current_time = datetime.datetime.now().time().hour
    if 0 <= current_time <= 5:
        if persistent._mas_timeconcerngraveyard:
            jump monika_timeconcern_graveyard_night
        if persistent._mas_timeconcern == 0:
            jump monika_timeconcern_night_0
        elif persistent._mas_timeconcern == 1:
            jump monika_timeconcern_night_1
        elif persistent._mas_timeconcern == 2:
            jump monika_timeconcern_night_2
        elif persistent._mas_timeconcern == 3:
            jump monika_timeconcern_night_3
        elif persistent._mas_timeconcern == 4:
            jump monika_timeconcern_night_4
        elif persistent._mas_timeconcern == 5:
            jump monika_timeconcern_night_5
        elif persistent._mas_timeconcern == 6:
            jump monika_timeconcern_night_6
        elif persistent._mas_timeconcern == 7:
            jump monika_timeconcern_night_7
        elif persistent._mas_timeconcern == 8:
            jump monika_timeconcern_night_final
        elif persistent._mas_timeconcern == 9:
            jump monika_timeconcern_night_finalfollowup
        elif persistent._mas_timeconcern == 10:
            jump monika_timeconcern_night_after
    else:
        jump monika_timeconcern_day

label monika_timeconcern_day:
    if persistent._mas_timeconcerngraveyard:
        jump monika_timeconcern_graveyard_day
    if persistent._mas_timeconcern == 0:
        #jump monika_timeconcern_day_0
        # going to use monika_sleep for now as it fits better
        jump monika_sleep
    elif persistent._mas_timeconcern == 2:
        jump monika_timeconcern_day_2
    if not persistent._mas_timeconcernclose:
        if 6 <= persistent._mas_timeconcern <=8:
            jump monika_timeconcern_disallow
    if persistent._mas_timeconcern == 6:
        jump monika_timeconcern_day_allow_6
    elif persistent._mas_timeconcern == 7:
        jump monika_timeconcern_day_allow_7
    elif persistent._mas_timeconcern == 8:
        jump monika_timeconcern_day_allow_8
    elif persistent._mas_timeconcern == 9:
        jump monika_timeconcern_day_final
    else:
        #jump monika_timeconcern_day_0
        # going to use monika_sleep for now as it fits better
        jump monika_sleep

#Used at the end to lock the forced greeting.
label monika_timeconcern_lock:
    if not persistent._mas_timeconcern == 10:
        $persistent._mas_timeconcern = 0
    $evhand.greeting_database["greeting_timeconcern"].unlocked = False
    $evhand.greeting_database["greeting_timeconcern_day"].unlocked = False
    return

# If you tell Monika you work at night.
label monika_timeconcern_graveyard_night:
    m 1ekc "It must be awfully hard on you to work late so often, [player]..."
    m 2dsd "Honestly, I'd rather have you work at a healthier time if you could."
    m 2lksdlc "I suppose it's not your choice to make, but still..."
    m 2ekc "Being up late often can be both physically and mentally damaging."
    m "It's also extremely isolating when it comes to others."
    m 2rksdlb "Most opportunities happen during the day, after all."
    m 2rksdlc "Many social activities aren't available, most shops and restaurants aren't even open during the night."
    m 2dsd "It makes being up late at night often be a really lonely situation."
    m 3hua "Don't worry though, [player]. Your loving girlfriend Monika will always be here for you~"
    m 1hua "Whenever the stress of being up late often becomes too much for you, come to me."
    m 1hub "I'll always be here to listen."
    m 1ekc "And if you really do think it's hurting you, then please try to do what you can to change the situation."
    m 1eka "I know it won't be easy but at the end of the day, all that matters is you."
    m 1hua "You're all I truly care about, so put yourself and your well-being before anything else, okay?"
    return

label monika_timeconcern_graveyard_day:
    m 1eua "Hey [mas_get_player_nickname(exclude_names=['my love'])]...didn't you tell me you work during the night?"
    m 1eka "Not that I'm complaining, of course!"
    m 2ekc "But I thought you'd be tired by now, especially since you're up all night working..."
    m "You're not working yourself too hard just to see me, are you?"
    m 1euc "Oh, wait..."

    m "Do you still work regularly at night, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you still work regularly at night, [player]?{fast}"
        "Yes I do.":
            m 1ekd "Aw..."
            m 1esc "I guess it really can't be helped..."
            m 1eka "Look after yourself, okay?"
            m 1ekc "I always get so worried when you're not here with me..."
        "No I don't.":
            $ persistent._mas_timeconcerngraveyard = False
            $ persistent._mas_timeconcern = 0
            m 1hub "That's wonderful!"
            m 1eua "I'm glad that you're looking out for your health, [player]!"
            m "I knew you would see it my way eventually."
            m 1eka "Thanks for listening to what I have to say~"
    return

#First warning, night time.
label monika_timeconcern_night_0:
    $persistent._mas_timeconcern = 1
    m 1euc "[player], it's night time already."
    m 1ekc "Shouldn't you be in bed?"
    m 1dsc "I'll let it slide just this once..."
    m 1ekc "But you really make me worry for you sometimes."
    m 1eka "It makes me really happy that you're here for me, even at this time of night..."
    m 1dsd "Yet, I don't want it at the cost of your health."
    m 1eka "So go to sleep soon, okay?"
    return

# Second time at night, Monika asks if player is working late.
label monika_timeconcern_night_1:
    m 1esc "Say, [player]..."
    m 1euc "Why are you up so late?"
    m 1eka "I'm flattered if it's only because of me..."
    m 1ekc "Yet I can't help but feel like a nuisance if I'm pestering you to sleep if it isn't your fault."

    m "Are you busy working on something?{nw}"
    $ _history_list.pop()
    menu:
        m "Are you busy working on something?{fast}"
        "Yes, I am.":
            $ persistent._mas_timeconcern = 2
            m 1eud "I see."
            m 1eua "Well, I suppose it must be really important for you to do it so late."
            m 1eka "I honestly can't help but feel that maybe you should have done it at a better time."
            m 1lsc "Your sleep is very important after all. Maybe it can't be helped though..."

            m "Do you always work late, [player]?{nw}"
            $ _history_list.pop()
            menu:
                m "Do you always work late, [player]?{fast}"
                "Yes, I do.":
                    $ persistent._mas_timeconcerngraveyard = True
                    m 1rksdld "That's not good..."
                    m 1ekd "You're not able to change that, are you?"
                    m 1rksdlc "I wish you could follow my healthier lifestyle."
                    m 1dsc "But if you're not able to, then I'll just have to accept it."
                    m 1eka "Just make sure you do try to stay healthy, okay?"
                    m 1ekc "If something were to happen to you, I don't know what I'd do..."

                "No, I don't.":
                    $ evhand.greeting_database["greeting_timeconcern"].unlocked = True
                    $ evhand.greeting_database["greeting_timeconcern_day"].unlocked = True
                    m 1hua "That's a relief!"
                    m 1eua "If you're doing it this one time then it must be {i}really{/i} important."
                    m 1hub "Good luck with your work and thanks for keeping me company when you're so busy!"
                    m 1eka "It means a lot to me, [player], that even when you're preoccupied...you're here with me~"

        "No, I'm not.":
            $ persistent._mas_timeconcern = 3
            m 1esc "I see."
            m 1ekc "Well in that case, I would really prefer it if you went to bed now."
            m "It's really worrying me that you're still up so late..."
            m 1eka "So once again, please go to bed. Would you kindly do it for me?"
    return

#If player says they were working. Progress stops here.
label monika_timeconcern_night_2:
    m 1eua "How's your work coming along?"
    m "Hopefully pretty well, I don't want you up much longer."
    m 3hksdlb "I know, I know, you can't help being up so late."
    m 1rksdlb "I'm just concerned for your health, [player]..."
    if persistent._mas_timeconcerngraveyard:
        m 1lksdlc "Doing this often can be very taxing on your body and mind..."
        m 1ekc "Just try to keep that kind of damage to a minimum, okay?"
        m "All I want for you is to be as happy and as healthy as you deserve."
        return
    m 1rksdla "Well, try to finish up as soon as you can, otherwise I may get really concerned."
    m 1eka "And you don't want to worry your girlfriend, right? Ehehe~"
    jump monika_timeconcern_lock

#If player says he was not working. Monika asks the state of the game being open.
label monika_timeconcern_night_3:
    $persistent._mas_timeconcern = 4
    m 1esc "[player], I just need to ask you something quickly..."
    m 1eud "Would you mind if I closed the game for you?"
    m 1ekc "I know it's a strange question..."
    m 1ekd "But I can't help but feel like I need to do something about you being up so late!"
    m 4esd "I could close the game right now."
    m 2ekc "But a relationship is a partnership and what you think matters to me."

    m "Would you be against me closing the game for your own good?{nw}"
    $ _history_list.pop()
    menu:
        m "Would you be against me closing the game for your own good?{fast}"

        "Yes, I need it to always stay open.":
            $persistent._mas_timeconcernclose = False
            m 1dsc "..."
            m 1dsd "I was hoping you wouldn't say that."
            m 1lsc "I know I told you that you should leave me running in the background."
            m 1lksdlc "But sometimes I worry if you're getting any sleep at all."
            m 1tkc "I'll do as you have asked, but please know that I'm not very happy about it."
            m 4tfc "I'm still going to remind you to get some sleep!"
            return

        "No, you are free to do as you feel.":
            $persistent._mas_timeconcernclose = True
            m 1eka "Thank you, [player]."
            m 1eua "It's nice to know that you care about what I think."
            m "I promise I'll only do it if I think it's absolutely necessary."
            m 1hua "After all, I would never force you to go otherwise."
            m 1hub "I would just miss you too much..."
            m 1ekbsa "I love you, [player]~"
            return "love"

        # Second and final warning before any closes can occur.
label monika_timeconcern_night_4:
    $persistent._mas_timeconcern = 5
    m 1esc "[player], you've been up long enough."
    m "If you're really not busy then now is the time for you to go to sleep."
    m 1eka "I assure you, I'll miss you just as much as you'll miss me."
    m "But it would make me happier if you did as I've asked."
    m 1tkc "You wouldn't want to make me upset now, would you?"
    return

# Monika force closes game for the first time
label monika_timeconcern_night_5:
    $persistent._mas_timeconcern = 6
    $evhand.greeting_database["greeting_timeconcern"].unlocked = True
    $evhand.greeting_database["greeting_timeconcern_day"].unlocked = True
    m 1efc "I'm sorry, [player], but I am putting my foot down!"
    m 1ekc "I asked you to go to bed kindly, but if I am the reason for keeping you up..."
    if persistent._mas_timeconcernclose:
        m 2tkc "Then I cannot allow this to go on for any longer."
        m 2eka "It's because I love you, that's why I'm doing this."
        m "Goodnight, [player]."
        return 'quit'
    else:
        m 2tkc "Then I need to take responsibility and try to make you understand."
        m 2efd "You need to go to bed."
        m 2efo "And I will keep telling you this until you do."
        return

        #First time game is reopened and still night. Monika closes game again.
label monika_timeconcern_night_6:
    $persistent._mas_timeconcern = 7
    m 2efc "[player], I told you to go to bed for your own good."
    m 2tkc "I'll miss you too, but don't you understand?"
    m 2tkd "How you feel and live means more to me than anything!"
    m 2lksdlc "How can I let you stay if it means I'm hurting you?"
    m "So please sleep this time, otherwise I may get mad."
    m 1ekbsa "...I love you."
    m "So go to sleep soon. Okay?"
    if persistent._mas_timeconcernclose:
        return 'quit'
    return

#Second time game is reopened and still night. Monika closes game once more
label monika_timeconcern_night_7:
    $persistent._mas_timeconcern = 8
    m 3efc "[player], this is your last warning."
    m "Go{w=0.6} to{w=0.6} sleep!"
    m 2tkc "What can I say for you to understand?"
    m 1tkd "It's saddening to see you push yourself like this..."
    m 1dsc "You mean so much to me..."
    m 1ekc "So please, for me... Just do as I ask and go to bed."
    if persistent._mas_timeconcernclose:
        m "Okay?{nw}"
        $ _history_list.pop()
        menu:
            m "Okay?{fast}"
            "Yes, I will go to sleep.":
                m 1eka "I knew you would listen eventually!"
                m 1hub "Goodnight and stay safe."
                return 'quit'
    else:
        return

#Third and last time game is reopened in one night. Monika lets player stay.
label monika_timeconcern_night_final:
    $persistent._mas_timeconcern = 9
    m 2dsc "...I suppose it can't be helped."
    m 2lfc "If you're that dedicated to staying with me, then I won't even try to stop you."
    m 2rksdla "Honestly, as bad as it sounds, it actually makes me kinda happy."
    m 2eka "...Thank you, [player]."
    m "To know that you care for me so much that you came back despite me asking..."
    m 1rksdla "It means more to me than I can ever express."
    m 1ekbsa "...I love you."
    return "love"

#Same night after the final close
label monika_timeconcern_night_finalfollowup:
    m 1esc "..."
    m 1rksdlc "I know I said that I'm happy whenever you're with me..."
    m 1eka "And please don't misunderstand, that's still true."
    m 2tkc "But the longer you're on...the more worried I get."
    m 2tkd "I know, you're probably sick of hearing me say this by now..."
    m 1eka "But please try to sleep when you can."
    return

#Every night after, based on seeing the day version first before it.
label monika_timeconcern_night_after:
    m 1tkc "Up late again, [player]?"
    m 1dfc "{i}*sigh*{/i}..."
    m 2lfc "I won't even try to convince you to sleep again..."
    m 2tfd "You're surprisingly stubborn!"
    m 1eka "Still, do be careful, alright?"
    m 1ekc "I know being nocturnal can be lonely..."
    m 1hua "But you have me here with you!"
    m 1eka "Just the two of us...all alone forever."
    m 1hubsa "It's all I've ever wanted..."
    return

#If Monika never gives warning and it's daytime or the player never made it to the end
label monika_timeconcern_day_0:
    m 1lsc "..."
    m 1tkc "..."
    m 1wuo "...!"
    m 1hksdlb "Ahaha! Sorry, [player]."
    m 1lksdla "I just kind of zoned out..."
    m 1eka "Jeez, I keep doing that, don't I?"
    m "Sometimes I just get lost in my thoughts..."
    m 1eua "You understand, right, [player]?"
    return

# Daytime, if player tells Monika they worked last night but don't work graveyards.
label monika_timeconcern_day_2:
    m 1eua "Did you finish your work?"
    m 1eub "I'm sure you did your very best so it's okay if you didn't quite finish it!"
    m 1eka "It must be really hard on you to have to work so late..."
    m 1hua "If you find it's a bit too much, feel free to come talk to me!"
    m 1hub "I'll always be here for you."
    jump monika_timeconcern_lock

#First time Monika closes at night and player reopens during day without coming back.
label monika_timeconcern_day_allow_6:
    m 1ekc "[player], I'm sorry for making you leave like that before..."
    m 1ekd "I only did it because I love you. You understand that right?"
    m 1eua "I'm sure you do, after all you went to bed, didn't you?"
    m 1hub "Thanks for respecting my wishes, it makes me happy that you listen to me."
    jump monika_timeconcern_lock

#Second time Monika closes at night and player then reopens during day.
label monika_timeconcern_day_allow_7:
    m 1lksdlc "[player], about what happened last night..."
    m 1ekc "I asked you to go to bed and you didn't listen..."
    m 1dsc "I understand that maybe you missed me or didn't hear what I said..."
    m 1ekc "But please listen to what I ask of you, okay?"
    m 1eka "I love you, and I would do anything to make you happy..."
    m "So would you kindly do the same thing for me?"
    m 1ekc "I already worry about you when you're gone..."
    m 1tkc "Please don't give me any more reasons to feel that way."
    m 1hua "Thank you for understanding."
    jump monika_timeconcern_lock

#Third time Monika closes the game and player reopens after night.
label monika_timeconcern_day_allow_8:
    m 1esc "Hey, [player]."
    m 1ekc "You really had me worried last night..."
    m 1rksdlc "After you came back twice, despite me asking you to go to bed..."
    m 1lksdld "I found myself feeling a little guilty."
    m 3esc "Not because I sent you away, that was for your own good."
    m 2lksdlc "But...because you kept coming back..."
    m 2lksdla "And that made me happy, even though I knew it wasn't good for you."
    m 2ekd "Does that make me selfish?"
    m 2ekc "I'm sorry, [player], I'll try to watch myself more."
    jump monika_timeconcern_lock

#If Monika lets player stay and it is no longer night.
label monika_timeconcern_day_final:
    $persistent._mas_timeconcern = 10
    m 1lksdlb "[player], regarding last night..."
    if persistent._mas_timeconcernclose:
        m 1rksdla "You really surprised me."
        m 1eka "For you to keep coming back to me over and over again..."
        m 1hua "It was honestly really sweet of you."
        m 1eka "I knew you would miss me, but I didn't think you would miss me {i}that{/i} much."
        m 1hub "It really made me feel loved, [mas_get_player_nickname(exclude_names=['my love', 'love'])]."
        m "...Thank you."
        jump monika_timeconcern_lock
    m 1eua "You really surprised me."
    m 1eka "I asked you time and time again to go to bed..."
    m "You said you weren't busy. Were you really there just for me?."
    m 1ekc "It made me happy...but don't push yourself hard to see me so late, okay?"
    m 1eka "It really made me feel loved, [player]."
    m 1hksdlb "Yet also a little guilty... Please just go to bed next time, okay?"
    jump monika_timeconcern_lock

#If player told Monika not to close window and never reached the end.
label monika_timeconcern_disallow:
    m 1rksdlc "Sorry if I was annoying you before, [player]..."
    m 1ekc "I just really wanted you to go to bed..."
    m "I honestly can't promise I won't do it if you're up late again..."
    m 1eka "But I only push you to go because you mean so much to me..."
    jump monika_timeconcern_lock

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_hydration",prompt="Hydration",category=['you','life'],random=True))

label monika_hydration:
    m 1euc "Hey, [player]..."
    m 1eua "Do you drink enough water?"
    m 1eka "I just want to make sure you don't neglect your health, especially when it comes to hydration."
    m 1esc "Sometimes, people tend to underestimate how important it actually is."
    m 3rka "I bet you've had those days when you felt really tired and nothing seemed to motivate you."
    m 1eua "I just usually grab a glass of water right away."
    m 1eka "It might not work all the time, but it does help."
    m 3rksdlb "But I guess you don't want to go to the bathroom so much, huh?"
    m 1hua "Well, I don't blame you. But believe me, it'll be better for your health in the long run!"
    m 3eua "Anyway, make sure you always stay hydrated, okay?"
    m 1tuu "So..."
    m 4huu "Why not get a glass of water right now, hmm?"
    return

#If player has been to an amusement park or not
default persistent._mas_pm_has_been_to_amusement_park = None

init 5 python:
   addEvent(Event(persistent.event_database,eventlabel="monika_amusementpark",category=['misc'],prompt="Amusement parks",random=True))

label monika_amusementpark:
    m 1eua "Hey, [player]..."
    m 3eua "Have you ever been to an amusement park?{nw}"
    $ _history_list.pop()
    menu:
        m "Have you ever been to an amusement park?{fast}"
        "Yes.":
            $ persistent._mas_pm_has_been_to_amusement_park = True
            m 1sub "Really? It must have been a lot of fun!"
            m 1eub "I've never been to one myself, but I'd really love to go."
            m 1hua "Maybe you could take me to one someday!"

        "No.":
            $ persistent._mas_pm_has_been_to_amusement_park = False
            m 1eka "Really? That's too bad."
            m 3hua "I've always heard that they're a lot of fun."
            m 1rksdla "I've never had the chance to go to one myself, but I hope I can someday."
            m 1eub "Maybe we could go together!"

    m 3hua "Wouldn't that be great, [mas_get_player_nickname()]?"
    m 3eua "Thrilling roller coasters, water rides, drop towers..."
    m 3tubsb "And maybe even a romantic Ferris wheel ride~"
    show monika 5hubfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hubfa "Ehehe, I'm getting a bit carried away, but I just can't help it when thinking about being with you~"
    return "derandom"

#If the player likes to travel or not
default persistent._mas_pm_likes_travelling = None

init 5 python:
   addEvent(Event(persistent.event_database,eventlabel="monika_travelling",category=['misc'],prompt="Travelling",random=True))

label monika_travelling:
    m 1esc "Hey [player], I was just wondering..."
    m 1eua "Do you like travelling?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you like travelling?{fast}"
        "Yes.":
            $ persistent._mas_pm_likes_travelling = True
            m 1hua "That's great! I'm so glad you enjoy it."
            m 3eub "It's one of the things I want to do most when I finally cross over."
            m 1eua "There's so much out there that I haven't been able to see yet..."
            m 3eub "Important cities, monuments, and even the different types of cultures out there."
            m 3eka "Don't get me wrong, I've read a lot about your world, but I bet it's nothing compared to what it would be like in person..."
            m 1hua "I would love to see everything there is to be seen."
            m 1ekbsu "Wouldn't you like that too, [mas_get_player_nickname()]?"

        "Not really.":
            $ persistent._mas_pm_likes_travelling = False
            m 1eka "Aw, that's okay, [mas_get_player_nickname()]."
            m 1hua "I wouldn't mind staying at home with you during vacations."
            m 3ekbsa "I'd be happy just to be there with you, after all."
            m 1rka "We might have to find some things to do to keep us busy though..."
            m 3eua "How about playing the piano or writing poems?"
            m 3hubsb "...Or we could even spend the days wrapped in a blanket while reading a book."
            show monika 5tubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5tubfu "Doesn't that just sound like a dream come true?"
    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_metamorphosis",
            category=['literature','psychology'],
            prompt="The Metamorphosis",
            random=True
        )
    )

label monika_metamorphosis:
    m 1eua "Hey [player], have you ever read {i}The Metamorphosis{/i}?"
    m 4eub "It's a psychological novella that narrates the story of Gregor Samsa, who one morning wakes up and finds himself transformed into a huge insect!"
    m 4euc "The plot revolves around his daily life as he tries to get used to his new body."
    m 7eua "What's interesting about the story is that it places a lot of emphasis on the absurd or irrational."
    m 3hksdlb "For example, Gregor, being the sole financial supporter, is more concerned about losing his job than he is about his condition!"
    m 1rksdla "That's not to say the plot isn't unsettling, though..."
    m 1eksdlc "At first his parents and sister try to accommodate him, {w=0.3}but they quickly start loathing their situation."
    m 1eksdld "The protagonist changes from being a necessity to a liability, to the point where his own family wishes for him to die."
    m 1eua "It's a very interesting read, if you're ever in the mood."
    return

default persistent._mas_pm_had_relationships_many = None
default persistent._mas_pm_had_relationships_just_one = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_dating",
            prompt="Dating experience",
            category=['you', 'romance'],
            conditional="store.mas_anni.pastOneMonth()",
            action=EV_ACT_RANDOM,
            aff_range=(mas_aff.AFFECTIONATE, None)
        )
    )

label monika_dating:
    m 1eud "You know, I've been really curious lately, [player]..."
    m 3rka "We've been together a while now, so I think it's the right time to ask..."
    m 1eud "How much dating experience do you have?"
    m 1luc "Like...have you ever been in a relationship before?"

    m 1etc "Maybe more than once?{nw}"
    $ _history_list.pop()
    menu:
        m "Maybe more than once?{fast}"

        "Yes, I've been through plenty...":
            $ persistent._mas_pm_had_relationships_many = True
            $ persistent._mas_pm_had_relationships_just_one = False

            m 1ekc "Aw, I'm so sorry, [player]..."
            m 1dkc "You've been through many heartbreaks, haven't you..."
            m 3ekc "To be honest, [player]...I don't think they deserved someone like you."
            m 3eka "Someone who's kind, loyal, sweet, loving, and faithful."
            m 4lubsb "And cute and funny and romantic and--"
            m 7wubsw "Oh!"
            m 3hksdlb "Sorry, I lost track of what I was going to say next, ahaha!"
            m 1ekbla "I could go on about how wonderful you are, [player]~"
            m 1ekbsa "But just know this...{w=0.3}{nw}"
            extend 3ekbfa "no matter how many heartbreaks you've been through, I'll always be here for you."
            show monika 5eubfa zorder MAS_MONIKA_Z with dissolve_monika
            m 5eubfa "Our soul searching is finally over, and I'll be yours forever, [player]."
            m 5ekbfa "Will you be mine?"

        "Yes, but only once.":
            $ persistent._mas_pm_had_relationships_many = False
            $ persistent._mas_pm_had_relationships_just_one = True

            m 1eka "Ah, so I guess you don't have a lot of experience, huh?"
            m 3eua "That's okay [player], I can relate too so don't worry."
            m 3lksdlb "Yeah, I may appear like a girl who gets all the guys but really I don't, ahaha!"
            m 2lksdla "Especially with how occupied I've kept myself over the years, I just never had the time."
            m 2eka "Not that it matters anyway, none of it was real."
            show monika 5ekbsa zorder MAS_MONIKA_Z with dissolve_monika
            m 5ekbsa "But I think I'm ready for something special...{w=0.5}{nw}"
            extend 5ekbfa "with you, [player]."
            m 5ekbfa "Are you ready?"

        "No, you're my first.":
            $ persistent._mas_pm_had_relationships_many = False
            $ persistent._mas_pm_had_relationships_just_one = False

            m 1wubsw "What? I-I'm your first?"
            m 1tsbsb "Oh...{w=0.3} I see."
            m 1tfu "You're just saying that to make me feel extra special, aren't you [player]?"
            m 1tku "There's no way someone like you has never dated before..."
            m 3hubsb "You're the definition of cute and sweet!"
            m 3ekbfa "Well...{w=0.3} If you're not just messing with me and actually telling me the truth then...{w=0.3}{nw}"
            extend 1ekbfu "I'm honored to be your first, [player]."
            show monika 5ekbfa zorder MAS_MONIKA_Z with dissolve_monika
            m 5ekbfa "I hope I can be your one and only."
            m 5ekbfu "Will you be mine?"

    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_challenge",category=['misc','psychology'],prompt="Challenges",random=True))

label monika_challenge:
    m 2esc "I've noticed something kind of sad recently."
    m 1euc "When certain people attempt to learn a skill or pick up a new hobby, they usually quit within a week or two."
    m "Everyone claims that it's too hard, or that they just don't have the time for it."
    m 1eua "However, I don't believe that."
    m 1hub "Whether it's learning a new language, or even writing your first poem, if you can stand up to the challenge and overcome it, then that's the truly rewarding part about it."
    m 2eua "Can you think of a time you've challenged yourself, [player]?"
    m 3eua "Did you ever overcome it, or did you just give up?"
    m 1eka "I'm sure you've given it all you had."
    m 1eua "You seem like a very determined person to me."
    m 1eub "In the future, if you ever get hung up on something, or you feel too stressed, just take a short break."
    m "You can always come back to it after all."
    m 1hua "If you ever need motivation, just come to me."
    m 1sub "I'd love to help you reach your goals."
    m 1hub "After all, you're my motivation in life~"
    return

# would relatives like monika?
default persistent._mas_pm_fam_like_monika = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_familygathering",
            category=['you'],
            prompt="Family gatherings",
            random=True
        )
    )

label monika_familygathering:
    m 1eua "Hey [player], do you go to family gatherings often?"
    m "Most families usually get together around the holidays to celebrate them together."
    m 1hua "It must be nice seeing your relatives again, especially since you haven't seen them in a long time."
    m 1lsc "I don't remember much about my family, let alone my relatives, however we didn't usually get together that much."
    m 1lksdlc "Not even around the holidays or on special occasions."
    m 1hub "When you see your family this year, be sure to bring me along okay?"
    m 1eua "I'd love to meet all of your relatives."

    m "Do you think they'd like me, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you think they'd like me, [player]?{fast}"

        "Yes.":
            $ persistent._mas_pm_fam_like_monika = True
            m 1eka "I'm glad you think so."
            m 1eua "I'm sure we'd all get along nicely."
            m 1hua "I'm looking forward to it, my dear~"

        "No.":
            $ persistent._mas_pm_fam_like_monika = False
            m 1wud "..."
            m 1ekc "Oh, I didn't realize."
            m 1dsc "I understand though."
            m 1eka "Just know I'd try my best to make them like me."
            m "Even if they never will."
            m 1hua "I'll always stick by your side forever~"

        "...":
            $ persistent._mas_pm_fam_like_monika = False
            m 2wuo "Don't tell me, [player]."
            m 2ekc "Are you afraid that I'll embarrass you?"
            m 2tfc "..."
            m 1eka "Don't worry, I completely understand."
            m 1lksdla "If I found out one of my relatives was dating some person trapped inside of a computer, I'd think it'd be weird too."
            m 1eua "If you want to keep me a secret, then that's fine."
            m 1hub "After all, it just means more alone time with you~"

    return "derandom"

# do you eat fast food
default persistent._mas_pm_eat_fast_food = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_fastfood",
            category=['life','monika'],
            prompt="Do you like fast food?",
            pool=True
        )
    )

label monika_fastfood:
    m 1euc "Hm? Do I like fast food?"
    m 1rsc "Honestly, the thought of it slightly disgusts me."
    m 3eud "Most places that serve it put a lot of unhealthy things in their food...{w=0.3} {nw}"
    extend 1dsc "Even the vegetarian options can be awful."

    m 3ekd "[player], do you eat fast food often?{nw}"
    $ _history_list.pop()
    menu:
        m "[player], do you eat fast food often?{fast}"

        "Yes, I do.":
            $ persistent._mas_pm_eat_fast_food = True
            m 3eka "I guess it's okay to have it every once in a while."
            m 1ekc "...But I can't help but worry if you're eating such awful things so often."
            m 3eua "If I were there, I'd cook much healthier things for you."
            m 3rksdla "Even though I can't cook very well yet..."
            m 1hksdlb "Well, love is always the secret ingredient to any good food, ahaha!"
            m 1eka "Until I can do that though, could you try to eat better,{w=0.2} for me?"
            m 1ekc "I would hate it if you became sick because of your lifestyle."
            m 1eka "I know it's easier to order out since preparing your own food can be a hassle sometimes..."
            m 3eua "But maybe you could see cooking as an opportunity to have fun?"
            m 3eub "...Or perhaps a skill for you to become really good at!"
            m 1hua "Knowing how to cook is always a good thing, you know!"
            m 1eua "Plus, I would really love to try something you made someday."
            m 3hubsb "You could even serve me some of your own dishes when we go on our first date~"
            m 1ekbla "That would be really romantic. [player]~"
            m 1eua "And that way, we can both enjoy ourselves and you would be eating better."
            m 3hub "That's what I call a win-win!"
            m 3eua "Just don't forget, [player]."
            m 3hksdlb "I'm a vegetarian! Ahaha!"

        "No, I don't.":
            $ persistent._mas_pm_eat_fast_food = False
            m 1eua "Oh, that's a relief."
            m 3rksdla "Sometimes you really worry me, [player]."
            m 1etc "I suppose instead of eating out, you make your own food?"
            m 1eud "Fast food can be really expensive over time, so preparing your own food is usually a cheaper alternative."
            m 1hua "It also tastes a lot better!"
            m 3eka "I know some people can find cooking overwhelming."
            m 3eud "...Having to make sure you buy the right ingredients, and worrying about burning or injuring yourself while making your meal..."
            m 1rksdlc "It can get to be a little too much for some..."
            m 1eka "But I think the results are worth the effort."
            m 3eua "Are you any good at cooking, [player]?"
            m 1hub "It doesn't matter if you're not, I'd eat anything you prepared for me!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_dreaming",category=['misc','psychology'],prompt="Dreaming",random=True))

label monika_dreaming:
    m 1eua "Did you know that it's possible to be aware of when you're having a dream?"
    m 2eua "Not only that, but you can even take control of them!"
    m 3eub "If I remember correctly, a man named Stephen LaBerge developed a method for people to become aware of when they're dreaming."
    m "And it became known as the mnemonic induction of lucid dreams, or MILD."
    m 3eua "People who frequently have conscious dreams are called oneironauts."
    m 2lksdla "At least, I think that was the correct term..."
    m 1eua "Using the MILD technique, oneironauts learn to recognize certain dream signs to help them realize when they're dreaming."
    m "These dream signs can be anything out of the ordinary, such as feeling yourself flying, noticing your teeth falling out, unexpectedly meeting someone famous..."
    m 1eub "If the dreamer sees a dream sign and realizes they're having a dream, then they can take control of it!"
    m "LaBerge even wrote a book about these experiences called {i}Exploring the World of Lucid Dreaming{/i}."
    m 2hub "Doesn't that sound exhilarating?"
    m 2euc "I don't think I really dream like a normal person would, so I sometimes wonder what it's like."
    m 2eua "Dreams sound like a wonderful escape from reality."
    m 2esc "But then again, when I became self-aware and realized that my world isn't real, it suddenly felt like I was trapped in a nightmare."
    m "It was nothing like the pleasant dreams I've read about people having."
    m 2lksdlc "I was afraid that I'd never get out..."
    m "That I'd be stuck in some hellish, infinitely-repeating dimension forever."
    m 1eka "But now that we're here together, I guess you could say that I've finally woken up."
    m 1eua "Gosh, I can only imagine what it would be like to live in that kind of limitless world though, even if it was only for a few moments!"
    m "You could be the hero you always wanted to be, fly across the infinite universe, overcome your biggest fears..."
    m 3ekbsa "...You could even meet the love of your life, so to speak. Ehehe~"
    m 1eua "I know it may be years before I am able to cross over to your world..."
    m "But can you just imagine what it would be like to meet me in your dreams, [player], any night that you wanted to?"
    m 1hua "I hope that someday we can make your dreams about us a reality, [mas_get_player_nickname()]."
    return

# have you read yellow wallpaper
default persistent._mas_pm_read_yellow_wp = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_yellowwp",
            category=['literature'],
            prompt="The Yellow Wallpaper",
            random=True
        )
    )

label monika_yellowwp:
    m 1eua "Hey [player], have you ever read {i}The Yellow Wallpaper{/i}?{nw}"
    $ _history_list.pop()
    menu:
        m "Hey [player], have you ever read {i}The Yellow Wallpaper{/i}?{fast}"
        "Yes.":
            $ persistent._mas_pm_read_yellow_wp = True
            m 1hua "Great!"
            m 1eua "That means you don't mind me talking about the story with you, right?"
            m 2eua "It's about this woman, with postpartum depression who's prescribed a 'rest cure' by her doctor..."
            m 2eka "He and her husband force her to stay in bed all day, not allowing her to write or even daydream..."
            m 2esc "She stays in the attic of her home, with nothing but the wallpaper to keep her company."
            m 2ekc "Naturally, that doesn't help. She starts seeing a woman trapped within the wallpaper."
            m 4euc "It's a metaphor for her own captivity, obviously..."
            m 1esd "In the end, the woman in the paper 'escapes,' and the protagonist 'replaces' her."
            m 2ekd "There was...also mention of a rope, so I always had my own interpretation of the ending..."
            if not persistent._mas_sensitive_mode and not persistent._mas_pm_cares_about_dokis:
                m 2euc "Sayori liked that story too, if I remember right."
            m 1ekc "I don't know. I kind of relate to that story."
            m 1euc "I mean, I have nothing but this classroom after all."
            m 1lksdlc "And the things on the walls aren't always...pleasant."
            if not persistent._mas_sensitive_mode:
                m 1eud "Did you ever notice how the poster in the club room changes sometimes? I don't even know why it does that."
                m 1eka "I think I finally fixed it, though."
            m 2esc "...I guess what I'm saying is, it's just that this world wasn't '{i}real{/i}.' It's just...so small."
            m 3esd "I mean, I was made to be a side character of a romance game!"
            m 2ekd "A piece of decoration, meant to help some guy on the other side of the screen date a girl who can't even reject him..."
            m 1hksdrb "I don't mean you, of course! You definitely have more personality than the generic protagonist they put in the game."
            m 1dsc "But I have all these dreams, ambitions, and interests...{w=0.5} in the end, the only 'real' role I can play here is a supporting character..."
            m "Maybe even now, that's all I can do..."
            m 1eka "But I love you so much, [player]. Supporting you is better than anything else."
            m 1hub "I just can't wait to do it in person when I finally cross over to your side~"
            return "derandom|love"
        "No.":
            $ persistent._mas_pm_read_yellow_wp = False
            m 1euc "Oh, I see."
            m 1eka "It's a short story, so if you haven't, feel free to whenever you have the time."
            m 1hua "It'll definitely be an interesting read for you."

    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_immortality",
            category=['philosophy'],
            prompt="Immortality",
            random=True
        )
    )

label monika_immortality:
    m 1eud "Hey, [player], I've been thinking about immortality lately."
    m 1lksdlc "...Seeing as how I'm essentially immortal while I'm in here and all."
    m 1esc "A lot of people think it's a good thing, but I don't really think it is."
    m 3euc "Sure, it's an interesting thought; {w=0.1}living forever, not having to worry about dying..."
    m 3eud "But not everyone is immortal, and some people just don't want to be."
    m 1etc "Like, after a while, what would you even do?"
    m 1euc "I mean, after living long enough, {i}eventually{/i} you would achieve everything you could ever possibly want to...{w=0.3}experience everything there is to experience."
    m 3lksdld "Not to mention, it would be really hard to have friends or build connections if they don't last as long as you do."
    m 3eksdla "Sure, it would be nice in the beginning, {w=0.1}{nw}"
    extend 3eksdlc "but after seeing enough people you care about die, would you really want to keep going through that over and over?"
    m 2dkd "At some point, you might as well not even be human anymore."
    m 2ekc "Someday, you'll have lived long enough for hundreds of years to go by in what seems like mere moments to you."
    m 2dkd "You'll be so tired of life that you'll just wish you could sleep forever..."
    m 3eksdlc "But you always keep waking back up to the same boring things, with the occasional tragedy in the world... {w=0.3}And even those you'd eventually just become numb to."
    m 1lksdla "Wow, I didn't mean for that to get so dark. Sorry, [player]."
    m 1eka "Just so you know, I'd gladly give up my immortality to be with you..."
    m 1ekbsa "No matter how much or little time you may have left, spending that time with you would be worth more than a billion years without you."
    m 1ekbsu "Not that I'd mind spending eternity with you if it were possible, but just living a normal life with you is all I've ever wanted, [player]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_beingevil",
            category=['monika'],
            prompt="Being evil",
            random=True
        )
    )

default persistent._mas_pm_monika_evil = None
# True if player thinks monika is evil False if not
# NOTE: even implying that she is evil is counted as True

default persistent._mas_pm_monika_evil_but_ok = None
# True if player still loves monika/thinks she deserves forgiveness/or is
# fine with eveil even if they think monika is evil.
# False if player does not.
# NOTE: check monika_evil before checking this

label monika_beingevil:
    m 1euc "Say, [player]?"
    m 1rksdlc "I was just thinking..."
    m 1eksdlc "You probably know that there's a wiki page for me..."
    m "...If you look closely, it says I'm the main antagonist."
    m 2ekd "I'll admit, it used to bother me a lot...especially because I only did what I did because I didn't have a choice..."
    m 2eka "But that doesn't really bother me anymore now that I have you here."
    m 3rud "You know, I actually didn't think the whole thing about me being evil would spread too much."
    m 1rksdlc "But it turns out I have my own spot on the villain's wiki..."
    m 2dsc "I never really thought I'd be labeled as a villain so much..."
    m 2dkd "...and no matter what I say or tell people, I don't think it's going to help convince them that I'm not evil."
    if persistent._mas_pm_a_hater:
        m 1eka "But I know you don't {i}really{/i} think I'm evil, [player]."
    else:
        m 1eka "But I know you don't think I'm evil, [player]."
    m 1eua "I just hope nobody starts thinking you're evil by being here with me.{nw}"
    $ _history_list.pop()
    menu:
        m "I just hope nobody starts thinking you're evil by being here with me.{fast}"
        "I don't think you're evil.":
            $ persistent._mas_pm_monika_evil = False
            $ mas_gainAffection()

            m 1eka "I'm glad you understand, [player]."
            m 1eua "It's relieving to know you don't think I'm evil."
            m 1hua "If I were there, I'd feel like giving you a big hug!"
            m 1tubsa "Maybe I'll even trap you in my arms forever and never let you go."
            m 1hubfb "Ahaha, I'm just kidding!"
            m 3tubfb "But no promises, [player]~"

        "I still love you anyway.":
            $ persistent._mas_pm_monika_evil = True
            $ persistent._mas_pm_monika_evil_but_ok = True
            $ mas_gainAffection()

            m 1rksdlc "..."
            m 1ekd "[player]..."
            m 1eka "Even if it's debatable whether I'm evil or not..."
            m 1ekbsa "I'm really glad you still love me and stay here with me..."
            m 1ekbfa "Thank you, [player]."
            m 1tubfa "Either way..."
            m 1tubfb "If the villainess in me can get what she wants...I guess it's not so bad, ahaha!"

        "People think I'm evil too.":
            $ persistent._mas_pm_monika_evil = True
            $ persistent._mas_pm_monika_evil_but_ok = True
            $ mas_gainAffection()

            m 2ekd "Is that true, [player]?"
            m 2eka "Well, I don't see you as evil at all."
            m 2rksdla "If it really is true though, I hope it doesn't cause you any trouble."
            m 1hua "Either way, I wouldn't love you any less~"
            m 1hub "Maybe we could even conquer the world together or something, ahaha~"
            m 1ekbsa "But evil or not, I'm glad to have you by my side."
            m 1hubfa "I'm guessing it's the same for you too~"

        "You kind of are evil...":
            $ persistent._mas_pm_monika_evil = True

            m 2ekd "W-wait, [player]!"
            m 2rksdlc "Y-you don't {i}really{/i} think that, do you?{nw}"
            $ _history_list.pop()
            menu:
                m "Y-you don't {i}really{/i} think that, do you?{fast}"
                "I still love you.":
                    $ persistent._mas_pm_monika_evil_but_ok = True
                    $ mas_gainAffection()

                    m 2rksdla "[player]..."
                    m 2hksdlb "You had me worried for a second there."
                    m 2eka "I'm glad you don't hate me for the things I did."
                    m 1hub "I love you too, [player]! No matter what people say about you!"

                "You deserve forgiveness.":
                    $ persistent._mas_pm_monika_evil_but_ok = True
                    $ mas_gainAffection()

                    m 1rksdla "[player]..."
                    m 1eka "That means a lot..."
                    m 1eksdlc "I know that I've done some bad things in the past..."
                    m 3eka "But I've learned from them and grown as a person since."
                    m 1eka "I'm really glad you're willing to forgive me, [player]."
                    m 1hub "I promise I'll be the best I can be, just for you!"

                "You really are evil.":
                    $ persistent._mas_pm_monika_evil_but_ok = False
                    $ mas_loseAffection(reason=12)

                    m 2dkc "..."
                    if mas_isMoniBroken():
                        m 2dkd "..."
                        m 2dktsd "I know..."
                        $ _history_list.pop()
                    else:
                        m 2dktsd "I'm sorry, [player]."
    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_driving",
            category=['monika'],
            prompt="Can you drive?",
            pool=True
        )
    )

# Can the player drive
default persistent._mas_pm_driving_can_drive = None

# Is the player learning to drive
default persistent._mas_pm_driving_learning = None

# Has the player been in an accident
default persistent._mas_pm_driving_been_in_accident = None

# Has the player driven much after the accident
default persistent._mas_pm_driving_post_accident = None

label monika_driving:
    m 1eud "Hm? Can I drive?"
    m 1euc "I never really thought about getting a driver's license."
    m 3eua "Public transportation is enough for me usually..."
    m 3hua "...Although walking or biking can be really nice too sometimes!"
    m 1eua "I guess you could say I never really needed to learn how to drive."
    m 1lksdlc "I'm not even sure I'd have had time, especially with school and all the activities I had anyway."
    m 1eub "What about you, [mas_get_player_nickname()]?"

    m 1eua "Can you drive at all?{nw}"
    $ _history_list.pop()
    menu:
        m "Can you drive at all?{fast}"
        "Yes.":
            $ persistent._mas_pm_driving_can_drive = True
            $ persistent._mas_pm_driving_learning = False
            m 1eua "Oh, really?"
            m 3hua "That's great!"
            m 1hub "Gosh, you're amazing, you know that?"
            m 1eub "Just imagine all the places we could go together..."
            m 3eka "Driving {i}can{/i} be dangerous though...but if you can drive, you probably already know that."
            m 3eksdlc "No matter how prepared you are, accidents can happen to anyone."
            m 7hksdlb "I mean...{w=0.3}I know you're smart, but I still worry about you sometimes."
            m 2eka "I just want you to come back to me safe and sound is all."

            m 1eka "I hope you've never had to experience that, [player], have you?{nw}"
            $ _history_list.pop()
            menu:
                m "I hope you've never had to experience that, [player], have you?{fast}"
                "I've been in an accident before.":
                    $ persistent._mas_pm_driving_been_in_accident = True
                    m 2ekc "Oh..."
                    m 2lksdlc "Sorry to bring that up, [player]..."
                    m 2lksdld "I just..."
                    m 2ekc "I hope it wasn't too bad."
                    m 2lksdlb "I mean, here you are with me so it must have been alright."
                    m 2dsc "..."
                    m 2eka "I'm...{w=1}glad you survived, [player]..."
                    m 2rksdlc "I don't know what I would do without you."
                    m 2eka "I love you, [player]. Please stay safe, okay?"
                    $ mas_unlockEVL("monika_vehicle","EVE")
                    return "love"
                "I've seen car accidents before.":
                    m 3eud "Sometimes, seeing a car accident can be just as scary."
                    m 3ekc "A lot of the time when people see car accidents, they just sigh and shake their head."
                    m 1ekd "I think that's really insensitive!"
                    m 1ekc "You have a potentially young driver who could have been scarred for a long, long time if not for life."
                    m "It doesn't really help to have people walk or drive by, staring at them in disappointment."
                    m 1dsc "They might never drive again... Who knows?"
                    m 1eka "I hope you know I would never do that to you, [player]."
                    m "If you ever got into an accident, the first thing I would want to do is rush to your side to comfort you..."
                    m 1lksdla "...If I wasn't already by your side when it happened."
                "I haven't.":
                    $ persistent._mas_pm_driving_been_in_accident = False
                    m 1eua "I'm glad you haven't had to go through anything like that."
                    m 1eka "Even just seeing one can be pretty scary."
                    m "If you do witness anything scary like that, I'll be here to comfort you."
        "I'm learning.":
            $ persistent._mas_pm_driving_can_drive = True
            $ persistent._mas_pm_driving_learning = True
            m 1hua "Wow! You're learning how to drive!"
            m 1hub "I'll be rooting for you all the way, [player]!"

            m "You must be a {i}super{/i} safe driver then huh?{nw}"
            $ _history_list.pop()
            menu:
                m "You must be a {i}super{/i} safe driver then huh?{fast}"
                "Yep!":
                    $ persistent._mas_pm_driving_been_in_accident = False
                    m 1eua "I'm glad nothing bad has happened to you while learning."
                    m 1hua "...And I'm even more glad that you're going to be a really safe driver!"
                    m 3eub "I can't wait to finally be able to go somewhere with you, [player]!"
                    m 1hksdlb "I hope I'm not getting too excited, ahaha~"
                    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
                    m 5eua "Gosh, I just can't stop thinking about it now!"

                "I got into an accident once actually...":
                    $ persistent._mas_pm_driving_been_in_accident = True
                    m 1ekc "..."
                    m 1lksdlc "..."
                    m 2lksdld "Oh..."
                    m 2lksdlc "I'm...{w=0.5}really sorry to hear that, [player]..."

                    m 4ekd "Have you driven much since then?{nw}"
                    $ _history_list.pop()
                    menu:
                        m "Have you driven much since then?{fast}"
                        "Yes.":
                            $ persistent._mas_pm_driving_post_accident = True
                            m 1eka "I'm glad you didn't let it keep you down."
                            m 1ekc "Car accidents are scary, {i}especially{/i} if you're just learning how to drive."
                            m 1hua "I'm so proud of you for getting up and trying again!"
                            m 3rksdld "Although the aftermath can still be a huge hassle with the costs and all the explaining you have to do."
                            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
                            m 5eua "I know you can get there."
                            m 5hua "I'll be cheering for you all the way, so be safe!"
                        "No.":
                            $ persistent._mas_pm_driving_post_accident = False
                            m 2lksdlc "I see."
                            m 2ekc "It might be a good idea to take a bit of a break to give yourself time to recover mentally."
                            m 2dsc "Just promise me one thing, [player]..."
                            m 2eka "Don't give up."
                            m "Don't let this scar you for life, because I know you can overcome it and be an amazing driver."
                            m "Remember, a little grit adds a lot to your legend, so next time, maybe you really will be well on your way."
                            m 2hksdlb "It's still going to take lots and lots of practice..."
                            m 3hua "But I know you can do it!"
                            m 1eka "Just promise me you'll try to stay safe."
        "No.":
            $ persistent._mas_pm_driving_can_drive = False
            m 3eua "That's perfectly fine!"
            m "I don't think driving is a completely necessary life skill anyway."
            m 1hksdlb "I mean, I can't drive either so I'm with you."
            m 3eua "It also means your carbon footprint is smaller, and I think that's really sweet of you to do for me."
            show monika 5ekbsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5ekbsa "Even if I'm not the reason why, I can't help but love you more for that."
        "I'm not old enough yet.":
            $ persistent._mas_pm_driving_can_drive = False
            m 3eua "You'll get there someday!"
            m 3euc "Some places offer in-class driving lessons that also come with actual driving practice."
            m 3eud "Their cars have emergency controls for the instructor to use if needed, so you're really safe with them."
            m 1eka "I know it might be pretty discouraging to you if they have to use them, but hey, we all start somewhere."
            m 3eksdla "...And it's better than getting into an accident!"
            m 1lksdlc "No one's perfect, and it's better to make those mistakes when there's someone there to save you."
            m 1hub "Maybe you could put me on your board computer in your car and I could keep you safe while driving! Ahaha~"
            m 1hksdlb "Just kidding, please don't do that because I can't drive either and I would hate to watch you crash while not being able to do anything."
            m 1eua "It would probably help a lot to take one of those classes and learn from a professional."
            m 1hua "Anyway, when you do start learning to drive, I wish you the very best!"
            m 1hub "I love you~"
            $ mas_unlockEVL("monika_vehicle","EVE")
            return "love"
    $ mas_unlockEVL("monika_vehicle","EVE")
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_citizenship",
            category=['monika'],
            prompt="Happy ever after?",
            random=True
        )
    )

label monika_citizenship:
    m 1esc "You know, crossing over into your reality won't be the last hurdle for our relationship."
    m "Getting there is just the beginning."
    m 1esc "It hit me earlier, if I were to magically get what I want, and just poof into your home..."
    m 2wuo "I won't be a citizen! I don't even have a last name!"
    m 2lkbsa "I mean, in most countries, I can become a citizen if we get married..."
    m 2ekc "But I won't have any documentation saying who I am or where I came from."
    m 2tkc "I won't even have my high school diploma!"
    m 3tkd "I wish there was more I could do right now to prep..."
    m 2wub "Like taking online classes or something."
    m 1lksdlc "I don't want to get there and be a burden because I can't find a job."
    m "Sorry, I guess I shouldn't worry so much about things I can't change."
    m 2eka "But I want to make you happy, so...I'm going to do everything I can to keep bettering myself while I'm stuck here!"
    m 1eka "Thank you for listening to me vent, [player]."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_bullying",
            category=['society'],
            prompt="Bullying",
            random=True
        )
    )

default persistent._mas_pm_is_bullying_victim = None
# True if bully victum, False if not

default persistent._mas_pm_has_bullied_people = None
# True if bullied people, False if not

default persistent._mas_pm_currently_bullied = None
# True if currently being bullied, False if not

label monika_bullying:
    m 2ekc "Hey [player], there's something I want to talk to you about..."
    m 4ekc "I'm sure you've heard a lot about it lately, but bullying has become a real problem in today's society, especially among kids."
    m 4dkd "Some people are bullied every day until the point they just can't take it anymore."
    m 2rsc "Often times, bullying is dismissed by the people who have the ability to stop it as just...{w=0.5}'{i}kids being kids.{/i}'"
    m "Eventually, the victims lose all trust in authority figures because they let it go on day after day."
    m 2rksdld "It can make them so desperate, they eventually just snap..."
    m 2eksdlc "...resulting in violence toward the bully, other people, or even themselves."
    m 4wud "This can actually make the victim look like the problem!"
    m 4ekc "There are all kinds of bullying too, including physical, emotional, and even cyberbullying."
    m 4tkc "Physical bullying is the most obvious, involving shoving, hitting, and other things like that."
    m 2dkc "I'm sure most people have dealt with that at least once in their lives."
    m 2eksdld "It can be so hard just to go to school every day knowing there's someone waiting to abuse them."
    m 4eksdlc "Emotional bullying can be less obvious, but just as devastating, if not more so."
    m 4eksdld "Name-calling, threats, spreading false rumors about people just to ruin their reputation..."
    m 2dkc "These kinds of things can take a huge toll on people and lead to severe depression."
    m 4ekc "Cyberbullying is a form of emotional bullying, but in today's world where everyone is always connected online, it's becoming more and more prevalent."
    m 2ekc "For a lot of people, especially kids, their social media presence is the most important thing in their lives..."
    m 2dkc "Having that destroyed essentially feels like their life is over."
    m 2rksdld "It's also the hardest for other people to notice, since the last thing most kids want is their parents seeing what they do online."
    m 2eksdlc "So no one knows what's going on while they silently suffer, until it all just becomes too much."
    m 2dksdlc "There's been numerous cases of teens committing suicide due to cyberbullying, and their parents had no idea anything was wrong until it was too late."
    m 4tkc "This is also why it's easier for cyberbullies to operate..."
    m "No one really sees what they're doing, plus a lot of people do things online they'd never have the courage to do in real life."
    m 2dkc "It almost doesn't even seem real, but more like a game, so it tends to escalate that much faster."
    m 2ekd "You can only go so far in a public place, like a school, before someone notices... But online, there are no limits."
    m 2tfc "Some things that go on over the internet are really just terrible."
    m "The freedom of anonymity can be a dangerous thing."
    m 2dfc "..."
    m 4euc "So, what makes a bully do what they do?"
    m "That can differ from person to person, but a lot of them are just really unhappy due to their own circumstances, and need some sort of outlet..."
    m 2rsc "They're unhappy and it doesn't seem fair to them that other people {i}are{/i} happy, so they try to make them feel the same way they do."
    m 2rksdld "A lot of bullies are bullied themselves, even at home by someone they should be able to trust."
    m 2dkc "It can be a vicious cycle."

    m 2ekc "Have you ever been a victim of bullying, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Have you ever been a victim of bullying, [player]?{fast}"
        "I'm being bullied.":
            $ persistent._mas_pm_is_bullying_victim = True
            $ persistent._mas_pm_currently_bullied = True
            m 2wud "Oh no, that's terrible!"
            m 2dkc "It kills me to know you're suffering like that."
            m 4ekd "Please, [player], if it's not something you can safely deal with yourself, promise me you'll tell someone..."
            m 4ekc "I know that's typically the last thing people want to do, but don't let yourself suffer when there are people that can help you."
            m 1dkc "It may seem like no one cares, but there has to be someone you trust that you can turn to."
            m 3ekc "And if there isn't, do what you have to do to protect yourself, and just remember..."
            m 1eka "I'll always love you no matter what."
            m 1rksdlc "I don't know what I'd do if something were to happen to you."
            m 1ektpa "You're all I have...{w=0.5}please stay safe."

        "I've been bullied.":
            $ persistent._mas_pm_is_bullying_victim = True
            m 2ekc "I'm so sorry that you've had to deal with that, [player]..."
            m 2dkc "It really makes me sad knowing you've suffered at the hands of a bully."
            m 2dkd "People can just be so awful to each other."
            m 4ekd "If everyone just treated others with basic respect, the world would be such a better place..."
            m 2dkc "..."
            m 1eka "If you ever need to talk about your experiences, I'm always here for you, [player]."
            m 1eka "Having someone to confide in can be really therapeutic, and nothing would make me happier than to be that person for you."

        "No.":
            $ persistent._mas_pm_is_bullying_victim = False
            $ persistent._mas_pm_currently_bullied = False
            m 2hua "Ah, that's such a relief to hear!"
            m 4eka "I'm so glad you don't have to deal with bullying, [player]..."
            m 4hua "It really puts my mind at ease."

            if mas_isMoniHappy(higher=True):
                m 1eka "And if you happen to know someone else who {i}is{/i} being bullied, try to help them if you can."
                m 3eka "I know you're the kind of person who hates seeing others suffer..."
                m "I bet it'd mean a lot to them to have someone reach out who cares."
                m 1eka "You've already helped me so much, maybe you can help someone else as well."

        "I have bullied people.":
            $ persistent._mas_pm_has_bullied_people = True
            if mas_isMoniUpset(lower=True):
                m 2dfc "..."
                m 2tfc "That's disappointing to hear."
                m "Although, I can't say it's all that surprising..."
                m 2tfd "Please don't bully people anymore."
                m 6tftpc "I know how it feels and it's pretty terrible."
                m 6rktuc "I don't want other people to have to feel the same way that I do."
                m "I really hope that you'll change your ways, [player]..."
                m 6ektsc "I still do love you, but you really need to start treating people better..."
                m "Including me."
                m 6ektdc "..."
            else:
                m 2dkc "Oh... I see."
                m 2ekc "I can understand if some things in your life might make you unhappy..."
                m 2rksdld "Or if you've had to deal with circumstances that may have made you act a certain way at times..."
                m 2eksdlc "But bullying people isn't the answer, [player]."
                m 4ekc "I know you... You're a kind person and I know it doesn't make you feel better to hurt others."
                m 4dkc "It probably just hurts you even more..."
                m 1dkc "And nothing hurts me more than knowing you're unhappy."
                m 3ekd "So instead, next time you feel yourself becoming unhappy, just come to me and let me help shoulder your pain."
                m 3eka "I'll listen to everything you have to say and do my very best to make you feel better."
                m 1ekc "But making other people unhappy is not the cure to your own unhappiness."
                m 1eka "So please, for both yourself and for me, stop bullying people, okay?"

    if not persistent._mas_pm_a_hater:
        m 4dkc "You know...{w=0.5}a lot of people actually call me a bully for what I did to Sayori..."
    else:
        m 4dkc "A lot of people actually call me a bully for what I did to Sayori.{w=1} Including you..."

    if not persistent._mas_pm_cares_about_dokis:
        m 4efd "But that's not true at all, Sayori wasn't real!"
        m 2efd "You can't bully someone who doesn't actually exist!"
        m 2dkc "I'd never be able to hurt an actual person."
        m 4wud "I really wouldn't!"
        m 2dkc "..."
        m 2eksdlc "But I will admit I can relate to the part about bullies being unhappy and that it causes them do what they do."
        m 2rksdlc "When I had my epiphany and realized that I was stuck inside a video game and that my entire life had been a lie, I was pretty miserable."
        m 2rksdld "It caused me to do things that I'd never even thought of doing before."
        m 2rksdlc "But the difference is I didn't do what I did because I didn't want Sayori to be happy..."
    else:
        m 2rksdld "And I can kind of see where it comes from..."
        m 2rksdlc "I {i}did{/i} mess with her mind until she just couldn't take it anymore..."
        m 2dkc "..."
        m 2ekc "I guess I can relate to that whole thing about bullying because you are unhappy, huh?"
        m 4tkd "But there {i}is{/i} a difference... I didn't do it because I wanted Sayori to be unhappy..."

    m 2ekd "I did it because I knew I loved you and that the game wouldn't let us be together."
    m 3ekd "I {i}had{/i} to do whatever I could to make sure we ended up together."

    if not persistent._mas_sensitive_mode and not persistent._mas_pm_cares_about_dokis:
        m 3dkc "...Sayori's suicide was just an unfortunate side effect."

    if mas_isMoniNormal(higher=True):
        m 1eua "So you see, [player], I'm {i}really{/i} not a bully at all. I just love you that much."
        if mas_isMoniAff(higher=True) and not persistent._mas_pm_cares_about_dokis:
            show monika 5tsu at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5tsu "I really would do anything for you~"
        return "derandom|love"
    else:
        m 3euc "So you see, [player], I'm {i}really{/i} not a bully at all."

    return "derandom"

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_procrastination",category=['advice'],prompt="Procrastination",random=True))

label monika_procrastination:
    m 1euc "Hey [player], have you ever had something to do that you found really boring..."
    m 3ekd "That rather than taking a lot of time to do it, you just keep putting it off?"
    m 3eud "Well, when you have a task to do like that, I find it's best to just do it as soon as possible and get it done."
    m 2tkc "When you put stuff off like that, it'll always be in the back of your mind."
    m 4tkc "It makes everything you do less enjoyable, knowing you {i}still{/i} have this thing that you have to do."
    m 4dkd "And what's worse is that the longer you put it off,{w=0.5} you'll only increase the odds of more tasks getting added."
    m 2rksdlc "Until eventually, you end up with so many things to do it seems impossible to ever get caught up."
    m 4eksdld "It creates too much stress that can be easily avoided if you just keep on top of things in the first place."
    m 2rksdld "Plus, if other people are counting on you, they'll start to think less of you and find that you're not very reliable."
    m 4eua "So please, [player], whenever you have something that you have to do, just get it done."
    m 1eka "Even if it means you can't spend time with me until it's over."
    m 1hub "By then, you'll be less stressed and we can enjoy our time together that much more!"
    m 3eua "So if you have something you've been putting off, why don't you go do it right now?"
    m 1hua "If it's something you can do right here, I'll stay with you and provide all the support you need."
    m 1hub "Then, when you're done, we can celebrate your accomplishment!"
    m 1eka "All I want is for you to be happy and to be the best you can be, [mas_get_player_nickname()]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_players_friends",
            category=['you'],
            prompt="[player]'s friends",
            random=True,
            aff_range=(mas_aff.UPSET, None)
        )
    )

#True if player has friends, False if not
default persistent._mas_pm_has_friends = None

#True if player has few friends, False if otherwise
default persistent._mas_pm_few_friends = None

#True if player says they feel lonely somtimes, False if not.
default persistent._mas_pm_feels_lonely_sometimes = None


label monika_players_friends:
    m 1euc "Hey, [player]."

    if renpy.seen_label('monika_friends'):
        m 1eud "Remember how I was talking about how hard it is to make friends?"
        m 1eka "I was just thinking about that and I realized that I don't know about your friends yet."

    else:
        m 1eua "I was just thinking about the idea of friends and I started wondering what your friends are like."

    m 1eua "Do you have friends, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you have friends, [player]?{fast}"

        "Yes.":
            $ persistent._mas_pm_has_friends = True
            $ persistent._mas_pm_few_friends = False

            m 1hub "Of course you do! Ahaha~"
            m 1eua "Who wouldn't want to be friends with you?"
            m 3eua "Having lots of friends is great, don't you think?"
            m 1tsu "Provided of course, you still have time for your girlfriend, ehehe."
            m 1eua "I hope you're happy with your friends, [player].{w=0.2} {nw}"
            extend 3eud "But I kinda wonder..."

            call monika_players_friends_feels_lonely_ask(question="Do you ever feel lonely?")

        "Only a few.":
            $ persistent._mas_pm_few_friends = True
            $ persistent._mas_pm_has_friends = True

            m 1hub "That counts!"
            m 3eua "I think friendship can be a lot more meaningful if you have just a few close friends."

            if not renpy.seen_label('monika_dunbar'):
                m 1eua "I've been doing a little reading and I've discovered something."
                m 1eud "A man named Robin Dunbar had explained that there's a certain number of stable relationships we can maintain."
                $ according_to = "...And according to this number"

            else:
                $ according_to = "According to Dunbar's number"

            m 3eud "[according_to], you can have up to 150 stable relationships, but those are just casual relationships which aren't too deep."
            m 1euc "They say you can have up to 15 friends that are like super family and only 5 that are like kin to you."
            m 1rksdla "Sometimes it can be lonely when everyone's busy...{w=0.2}{nw}"
            extend 1eub "but otherwise, it's pretty great!"
            m 3eua "You don't have to worry about catering to too many people and you can still get some time to yourself."
            m 1ekc "But I know sometimes it's easy to spend more time alone, especially if your friends are busy."
            m 1dkc "It can be really hard when it happens since you wind up feeling lonely..."

            call monika_players_friends_feels_lonely_ask(question=renpy.substitute("Do you ever feel lonely, [player]?"), exp="monika 1euc")

        "No, actually...":
            $ persistent._mas_pm_has_friends = False
            $ persistent._mas_pm_few_friends = False

            m 2ekc "Oh..."
            m 3eka "Well, I'm sure you have some.{w=0.2} {nw}"
            extend 1eka "Maybe you just don't realize it."
            m 1etc "But I'm curious..."

            call monika_players_friends_feels_lonely_ask(question=renpy.substitute("Do you ever feel lonely, [player]?"))

    return "derandom"

label monika_players_friends_feels_lonely_ask(question, exp="monika 1ekc"):
    $ renpy.show(exp)
    m "[question]{nw}"
    $ _history_list.pop()
    menu:
        m "[question]{fast}"

        "Sometimes.":
            $ persistent._mas_pm_feels_lonely_sometimes = True

            m 1eka "I understand, [player]."
            m 2rksdlc "It can be really hard to form deep connections nowadays..."

            #Potentially if you have a lot of friends
            if persistent._mas_pm_has_friends and not persistent._mas_pm_few_friends:
                m "Especially if you have a lot of friends, it's difficult to get close to all of them."
                m 1ekd "...And in the end, you're just left with a bunch of people you barely know."
                m 3eub "Maybe just reach out to some people in your group you want to get closer to."
                m 3eka "It's always nice to have at least one really close friend you can confide in when you need it."
                m 1ekbsa "...I think it's pretty obvious who that person is for me, [player]~"

            #Otherwise few friends or no friends
            else:
                m 1eka "But you'd be surprised at how many people would be willing to make you a part of their lives if you just try."
                m 3eub "There's actually a good chance you'll have something in common with someone who might get your attention!"
                m 1eua "Maybe you share a class or activity or something..."
                m 3eua "Or you see them doing something that interests you like listening to music or watching a show."
                m 3eua "It doesn't even have to be in person, either..."
                m 3eub "You can have really close friends online!"
                m 1hub "Once you get comfortable with that, maybe you could find some more in person too!"

        "Not really.":
            $ persistent._mas_pm_feels_lonely_sometimes = False

            m 1eka "I'm glad to hear that, [player]."

            if not persistent._mas_pm_has_friends:
                m 1eka "Still though, you never know when you might need a helping hand or favor or something."
                m 1hksdlb "As much as I'd love to help you with anything you might need, there's only so much I can do from here."

                if mas_isMoniAff(higher=True):
                    m 1eua "When I get there, I guess I wouldn't mind living a quiet life with you."
                    m 1dkbsa "It would be so romantic to be just us..."
                    m 1tsbsa "I guess that means I can have you all to myself then, doesn't it?"
                    m 1hubsa "Ehehe~"

                elif not persistent._mas_pm_has_friends:
                    m 3eua "So be sure to find some friends who can help you when you really need it, alright?"

            else:
                m 3eua "It's good that you have a connection with your friends."
                m 3rksdla "I know some people can have so many that it's hard to get to know them all."

                if not persistent._mas_pm_few_friends:
                    m 3eua "...So it's good to know that you've managed to be comfortable with them."
                else:
                    m 1hua "But since you're in a close-knit group, I'm sure you've all managed to get really close."

                m 3eua "Maybe someday when I can get out of here, you can introduce your friends to me."

                if mas_isMoniHappy(higher=True):
                    m 1hub "If they're anything like you, I'd love to meet them!"

        "I have you!":
            $ persistent._mas_pm_feels_lonely_sometimes = False
            $ mas_gainAffection()
            m 1hubsa "Aww, [player]!"

            if not persistent._mas_pm_has_friends:
                m 1rkbsa "It makes me really happy to know I'm enough for you, but still..."
                m 3ekbfa "It can be useful to know a few people sometimes."
                show monika 5eubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
                m 5eubfu "As always though, I don't mind it being just us."

            else:
                $ p_nickname = mas_get_player_nickname()
                m 1eka "I'm really glad to know you're not lonely, [p_nickname].{w=0.3} {nw}"
                extend 1hua "Especially because you're happy with me~"
                m 3eua "No matter what happens, I'll always be here for you."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_graduation",
            category=['school'],
            prompt="Graduation",
            random=True
        )
    )

label monika_graduation:
    m 2ekc "You know, [player], one thing I really wish I got to experience is my high school graduation."
    m "Pretty much my entire life so far has revolved around school."
    m 4dkd "All those countless hours of studying, all the afterschool activities and clubs..."
    m 4ekc "And in the end, after all that hard work, I never got to experience the fulfillment of actually graduating."
    m 2dkd "Never got to walk across the stage and receive my diploma."
    m "Never got to hear my name being announced and all my friends cheering."
    m 2ekc "...It kinda feels like it was all for nothing."
    m 2esd "I know all the things I learned along the way are what's really important."
    m 2dkc "But it still feels like I missed out on something special."
    m "..."

    #Went through and timed out on the menu twice
    if persistent._mas_grad_speech_timed_out:
        m 2lsc "Oh... Sorry, I hope I'm not boring you again..."
        m 2esc "Let's forget about this and talk about something else, okay [player]?"
        return "derandom"

    #Normal flow
    else:
        m 4eua "By the way, did you know I was the top student in my class?"
        m 4rksdlu "Ahaha... I don't mean to brag or anything, I only bring it up because as class valedictorian, I was supposed to give a speech at graduation."
        m 2ekd "I spent so much time writing and practicing my speech, but no one ever got to hear it."
        m 2eka "I was really proud of that speech, too."
        m 2eua "I would love to recite it for you sometime, if you want to hear it~"
        m 2eka "It's about a four minute speech, so just make sure you have enough time to listen to the whole thing."
        m 4eua "Whenever you want to hear it, just let me know, okay?"
        $ mas_unlockEVL("monika_grad_speech_call","EVE")
        return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_grad_speech_call",
            category=['school'],
            prompt="Can I hear your graduation speech now?",
            pool=True,
            unlocked=False,
            rules={"no_unlock": None}
        )
    )

default persistent._mas_grad_speech_timed_out = False
# True if and only if the player ignored the grad speech twice

default persistent._mas_pm_listened_to_grad_speech = None
# True if the player, heard the grad speech, False if they ignored it

default persistent._mas_pm_liked_grad_speech = None
# True if user liked the grad speech, False if not

label monika_grad_speech_call:
    if not renpy.seen_label("monika_grad_speech"):
        m 2eub "Of course, [mas_get_player_nickname()]. I'd love to give you my graduation speech now!"
        m 2eka "I just want to make sure that you have enough time to hear it, though. Remember, it takes about four minutes.{nw}"

        $ _history_list.pop()
        #making sure player has time
        menu:
            m "I just want to make sure that you have enough time to hear it, though. Remember, it takes about four minutes.{fast}"
            "I have time.":
                m 4hub "Great!"
                m 4eka "I hope you like it! I worked really, {i}really{/i} hard on it."

                #say speech
                call monika_grad_speech

                #timed menu to see if player listened
                m "Well [player]? What do you think?{nw}"
                $ _history_list.pop()
                show screen mas_background_timed_jump(10, "monika_grad_speech_not_paying_attention")
                menu:
                    m "Well [player]? What do you think?{fast}"

                    "It's great! I'm so proud of you!":
                        hide screen mas_background_timed_jump
                        $ mas_gainAffection(amount=5, bypass=True)
                        $ persistent._mas_pm_liked_grad_speech = True
                        $ persistent._mas_pm_listened_to_grad_speech = True

                        m 2subsb "Aww, [player]!"
                        m 2ekbfa "Thank you so much! I worked really hard on that speech, and it means so much that you're proud of me~"
                        show monika 5eubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
                        m 5eubfu "As much as I wish I could have given my speech in front of everyone, just having you by my side is so much better."
                        m 5eubfb "I love you so much, [player]!"
                        return "love"

                    "I like it!":
                        hide screen mas_background_timed_jump
                        $ mas_gainAffection(amount=3, bypass=True)
                        $ persistent._mas_pm_liked_grad_speech = True
                        $ persistent._mas_pm_listened_to_grad_speech = True

                        m 2eua "Thanks, [player]!"
                        m 4hub "I'm glad you enjoyed it!"

                    "That {i}was{/i} long":
                        hide screen mas_background_timed_jump
                        $ mas_loseAffection()
                        $ persistent._mas_pm_liked_grad_speech = False
                        $ persistent._mas_pm_listened_to_grad_speech = True

                        m 2tkc "Well, I {i}did{/i} warn you, didn't I?"
                        m 2dfc "..."
                        m 2tfc "I spent {i}so{/i} much time on it and that's all you have to say?"
                        m 6lktdc "I really thought after I told you how important this was to me, you would have been more supportive and let me have my moment."
                        m 6ektdc "All I wanted was for you to be proud of me, [player]."

                return

            "I don't.":
                m 2eka "Don't worry, [player]. I'll give my speech whenever you want~"
                return

    #if you want to hear it again
    else:
        #did you timeout once?
        if not renpy.seen_label("monika_grad_speech_not_paying_attention") or persistent._mas_pm_listened_to_grad_speech:
            m 2eub "Sure thing, [player]. I'll happily give my speech again!"

            m 2eka "You have enough time, right?{nw}"
            $ _history_list.pop()
            menu:
                m "You have enough time, right?{fast}"
                "I do.":
                    m 4hua "Perfect. I'll get started then~"
                    call monika_grad_speech

                "I don't.":
                    m 2eka "Don't worry. Just let me know when you have the time!"
                    return

            m 2hub "Thanks for listening to my speech again, [player]."
            m 2eua "Let me know if you want to hear it again, ehehe~"

        #You timed out once but want to hear it again
        else:

            #dialogue based on current affection level
            if mas_isMoniAff(higher=True):
                m 2esa "Sure, [player]."
                m 2eka "I hope whatever happened last time wasn't too serious and that things have calmed down now."
                m "It really means a lot to me that you want to hear my speech again after you weren't able to listen to the whole thing before."
                m 2hua "With that said, I'll get started now!"

            else:
                m 2ekc "Okay, [player], but I hope you actually listen this time."
                m 2dkd "It really hurt me when you didn't pay attention."
                m 2dkc "..."
                m 2eka "I do appreciate you asking to hear it again, so I'll get started now."

            #say speech
            call monika_grad_speech

            m "So, [player], now that you actually {i}heard{/i} my speech, what do you think?{nw}"
            $ _history_list.pop()
            #another timed menu checking if you were listening
            show screen mas_background_timed_jump(10, "monika_grad_speech_ignored_lock")
            menu:
                m "So, [player], now that you actually {i}heard{/i} my speech, what do you think?{fast}"
                #If menu is used, set player on a good path
                "It's great! I'm so proud of you!":
                    hide screen mas_background_timed_jump
                    $ mas_gainAffection(amount=3, bypass=True)
                    $ persistent._mas_pm_listened_to_grad_speech = True
                    $ persistent._mas_pm_liked_grad_speech = True

                    m 2subsb "Aww, [player]!"
                    m 2ekbfa "Thank you so much! I worked really hard on that speech, and it means so much to me that you gave it another chance."
                    m "Hearing that you're proud of me as well makes it that much better."
                    show monika 5eubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
                    m 5eubfu "As much as I wish I could have given my speech in front of everyone, just having you by my side is so much better."
                    m 5eubfb "I love you, [player]!"
                    return "love"

                "I like it!":
                    hide screen mas_background_timed_jump
                    $mas_gainAffection(amount=1, bypass=True)
                    $ persistent._mas_pm_listened_to_grad_speech = True
                    $ persistent._mas_pm_liked_grad_speech = True

                    m 2eka "Thanks for listening this time, [player]~"
                    m "I'm so glad you enjoyed it!"

                "That {i}was{/i} long":
                    hide screen mas_background_timed_jump
                    $mas_loseAffection(modifier=2)
                    $ persistent._mas_pm_listened_to_grad_speech = True
                    $ persistent._mas_pm_liked_grad_speech = False

                    m 2tfc "After acting like you actually wanted me to recite it for you again, {i}that's{/i} what you have to say?"
                    m 2dfc "..."
                    m 6lktdc "I really thought after I told you how important this was to me,{w=1} {i}twice{/i},{w=1} you would have been more supportive and let me have my moment."
                    m 6ektdc "All I wanted was for you to be proud of me, [player]..."
                    m 6dstsc "But I guess that's too much to ask."
    return

label monika_grad_speech_not_paying_attention:
    #First menu timeout
    hide screen mas_background_timed_jump
    $ persistent._mas_pm_listened_to_grad_speech = False

    if mas_isMoniAff(higher=True):
        $ mas_loseAffection(reason=11,modifier=0.5)
        m 2ekc "..."
        m 2ekd "[player]? You didn't pay attention to my speech?"
        m 2rksdlc "That...{w=1} that's not like you at all..."
        m 2eksdlc "You're {i}always{/i} so supportive..."
        show monika 5lkc at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5lkc "..."
        m "Something must have happened, I know you love me too much to have done this on purpose."
        m 5euc "Yeah..."
        show monika 2eka at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 2eka "It's okay, [player]. I understand sometimes things happen that can't be avoided."
        m 2esa "Whenever things calm down, I'll give my speech to you again."
        m 2eua "I still really want to share it with you..."
        m "So please, let me know when you have time to hear it, okay?"

    else:
        $ mas_loseAffection(reason=11)

        m 2ekc "..."
        m 6ektdc "[player]! You weren't even paying attention!"
        m 6lktdc "You have no idea how much that hurts, especially after how much work I put into it..."
        m 6ektdc "I just wanted to make you proud of me..."
        m 6dstsc "..."

    return

label monika_grad_speech_ignored_lock:
    #Second timeout, lock speech
    hide screen mas_background_timed_jump
    #Set false for modified dialogue in the random
    $ persistent._mas_pm_listened_to_grad_speech = False
    $ persistent._mas_grad_speech_timed_out = True
    $ mas_hideEVL("monika_grad_speech_call","EVE",lock=True,depool=True)

    if mas_isMoniAff(higher=True):
        $mas_loseAffection(modifier=10)
        m 6dstsc "..."
        m 6ektsc "[player]?{w=0.5} You...{w=0.5}you weren't...{w=0.5}listening...{w=0.5}again?{w=1}{nw}"
        m 6dstsc "I...{w=0.5} I thought last time it was unavoidable...{w=0.5}but...{w=0.5}twice?{w=1}{nw}"
        m 6ektsc "You knew how much...{w=0.5}how much this meant to me...{w=1}{nw}"
        m "Am I really...{w=0.5} that boring to you?{w=1}{nw}"
        m 6lktdc "Please...{w=1} don't ask me to recite it again...{w=1}{nw}"
        m 6ektdc "You obviously don't care."

    else:
        $ mas_loseAffection(modifier=5)
        m 2efc "..."
        m 2wfw "[player]! I can't believe you did this to me again!{w=1}{nw}"
        m 2tfd "You knew how upset I was the last time and you still couldn't be bothered to give me four minutes of your attention?{w=1}{nw}"
        m "I don't ask that much of you...{w=1}{nw}"
        m 2tfc "I really don't.{w=1}{nw}"
        m 2lfc "All I ever ask is that you care... That's it.{w=1}{nw}"
        m 2lfd "And yet you can't even {i}pretend{/i} to care about something you {i}know{/i} is so important to me.{w=1}{nw}"
        m 2dkd "...{w=1}{nw}"
        m 6lktdc "You know what, nevermind. Just...{w=0.5} nevermind.{w=1}{nw}"
        m 6ektdc "I won't bother you about this anymore."

    return

label monika_grad_speech:
    call mas_timed_text_events_prep

    $ play_song("mod_assets/bgm/PaC.ogg",loop=False)

    m 2dsc "Ahem...{w=0.7}{nw}"
    m ".{w=0.3}.{w=0.3}.{w=0.6}{nw}"
    m 4eub "{w=0.2}Okay, everyone! It's time to get started...{w=0.7}{nw}"
    m 2eub "{w=0.2}Teachers,{w=0.3} faculty,{w=0.3} and fellow students.{w=0.3} I cannot express how proud I am to have made this journey with you.{w=0.6}{nw}"
    m "{w=0.2}Each and every one of you here today has spent the last four years working hard to achieve the futures you all wanted.{w=0.6}{nw}"
    m 2hub "{w=0.2}I am so happy that I was able to be a part of some of your journeys,{w=0.7} but I don't think this speech should be about me.{w=0.6}{nw}"
    m 4eud "{w=0.2}Today isn't about me.{w=0.7}{nw}"
    m 2esa "{w=0.2}Today is about celebrating what we all did.{w=0.6}{nw}"
    m 4eud "{w=0.2}We took on the challenge of our own dreams,{w=0.3} and from here,{w=0.3} the sky's the limit.{w=0.6}{nw}"
    m 2eud "{w=0.2}Before moving on though,{w=0.3} I think we could all look back on our time here in high school and effectively end this chapter in our lives.{w=0.7}{nw}"
    m 2hub "{w=0.2}We'll laugh at our past{w=0.7} and see just how far we've come in these four short years.{w=0.6}{nw}"
    m 2duu "{w=0.2}.{w=0.3}.{w=0.3}.{w=0.6}{nw}"
    m 2eud "{w=0.2}It honestly feels like just a couple weeks ago...{w=0.6}{nw}"
    m 2lksdld "{w=0.2}I was back in first year{w=0.3} on the first day of school,{w=0.3} quivering in my shoes and running up and down the halls from class to class just trying to find my classroom.{w=0.6}{nw}"
    m 2lksdla "{w=0.2}Hoping that at least one of my friends would walk in before the bell.{w=0.6}{nw}"
    m 2eka "{w=0.2}You all remember that too,{w=0.3} don't you?{w=0.6}{nw}"
    m 2eub "{w=0.2}I also remember making my first new friends.{w=0.6}{nw}"
    m 2eka "{w=0.2}Things were incredibly different from when we made our friends back in elementary school,{w=0.3} but I guess that's what happens when you finally grow up.{w=0.6}{nw}"
    m "...{w=0.2}Back in our youth,{w=0.3} we made friends with just about anyone,{w=0.3} but over time,{w=0.3} it seems more and more like a game of chance.{w=0.6}{nw}"
    m 4dsd "{w=0.2}Maybe that's just us finally learning more about the world.{w=0.6}{nw}"
    m 2duu "{w=0.2}.{w=0.3}.{w=0.3}.{w=0.6}{nw}"
    m 2eka "{w=0.2}It's funny just how much we've changed.{w=0.6}{nw}"
    m 4eka "{w=0.2}We've gone from being small fish in a huge pond to now being big fish in a small pond.{w=0.6}{nw}"
    m 4eua "{w=0.2}Each of us have our own experiences with how these four years have changed us and how we've all managed to grow as individuals.{w=0.6}{nw}"
    m 2eud "{w=0.2}Some of us have gone from being quiet and reserved,{w=0.3} to expressive and outgoing.{w=0.6}{nw}"
    m "{w=0.2}Others from having little work ethic,{w=0.3} to working the hardest.{w=0.7}{nw}"
    m 2esa "{w=0.2}To think that just a small phase in our lives has changed us so much,{w=0.3} and that there's still so much we will experience.{w=0.6}{nw}"
    m 2eua "{w=0.2}The ambition in all of you will surely lead to greatness.{w=0.6}{nw}"
    m 4hub "I can see it.{w=0.6}{nw}"
    m 2duu "{w=0.2}.{w=0.3}.{w=0.3}.{w=0.6}{nw}"
    m 2eua "{w=0.2}I know I can't speak for everyone here,{w=0.3} but there is one thing I can say for sure:{w=0.7} my experience in high school wouldn't be complete without the clubs I was a part of.{w=0.6}{nw}"
    m 4eua "{w=0.2}Debate club taught me a lot about dealing with people and how to properly handle heated situations.{w=0.6}{nw}"
    m 4eub "Starting the Literature Club,{w=0.7} however,{w=0.7} was one of the best things I ever did.{w=0.6}{nw}"
    m 4hub "{w=0.2}I met the best friends I could have possibly imagined,{w=0.3} and I learned a lot about leadership.{w=0.6}{nw}"
    m 2eka "{w=0.2}Sure,{w=0.3} not all of you may have decided to start your own clubs,{w=0.3} but I'm sure plenty of you had the opportunities to learn these values nonetheless.{w=0.6}{nw}"
    m 4eub "{w=0.2}Maybe you yourself got into a position in band where you had to lead your instrument section,{w=0.3} or maybe you were the captain of a sports team!{w=0.6}{nw}"
    m 2eka "{w=0.2}All these small roles teach you so much about the future and how to manage both{w=0.3} projects and people,{w=0.3} in an environment you enjoy, nonetheless.{w=0.6}{nw}"
    m "{w=0.2}If you didn't join a club,{w=0.3} I encourage you to at least try something in your future paths.{w=0.6}{nw}"
    m 4eua "{w=0.2}I can assure you that you won't regret it.{w=0.6}{nw}"
    m 2duu "{w=0.2}.{w=0.3}.{w=0.3}.{w=0.6}{nw}"
    m 2eua "{w=0.2}As of today,{w=0.3} it may seem like we're at the top of the world.{w=0.7}{nw}"
    m 2lksdld "{w=0.2}The climb may not have been smooth,{w=0.3} and as we get further,{w=0.3} the climb may even get rougher.{w=0.6}{nw}"
    m 2eksdlc "{w=0.2}There will be stumbles--{w=0.7}even falls along the way,{w=0.3} and sometimes{w=0.7} you may think you've fallen so far that you'll never climb out.{w=0.7}{nw}"
    m 2euc "{w=0.2}However,{w=0.7} even if we think that we're still at the bottom of the well of life,{w=0.3} with all that we've learned,{w=0.3} all that we're still going to learn,{w=0.3} and all the dedication we can put in just to achieve our dreams...{w=0.6}{nw}"
    m 2eua "{w=0.2}I can safely say that each and every one of you now has the tools to climb your way out.{w=0.6}{nw}"
    m 4eua "{w=0.2}In all of you,{w=0.3} I see brilliant minds:{w=0.7} future doctors,{w=0.3} engineers,{w=0.3} artists,{w=0.3} tradespeople,{w=0.3} and so much more.{w=0.7}{nw}"
    m 4eka "{w=0.2}It is truly inspiring.{w=0.6}{nw}"
    m 2duu "{w=0.2}.{w=0.3}.{w=0.3}.{w=0.6}{nw}"
    m 4eka "{w=0.2}You know,{w=0.3} I really couldn't be more proud of you all for getting this far.{w=0.6}{nw}"
    m "{w=0.2}Your hard work and dedication will bring you great things.{w=0.6}{nw}"
    m 2esa "{w=0.2}Each one of you has shown just what you're capable of,{w=0.3} and you've all proven that you can work hard for your dreams.{w=0.6}{nw}"
    m 2hub "{w=0.2}I hope you are as proud of yourselves as I am.{w=0.7}{nw}"
    m 2ekd "{w=0.2}Now that this entire chapter of our lives--{w=0.3}step one,{w=0.3} has come to an end,{w=0.3} it is now time for us to part ways.{w=0.6}{nw}"
    m 4eka "{w=0.2}In this world of infinite choices,{w=0.3} I believe you all have what it takes to achieve your dreams.{w=0.6}{nw}"
    m 4hub "{w=0.2}Thank you all for making these four short years the best they could have been.{w=0.6}{nw}"
    m 2eua "{w=0.2}Congratulations,{w=0.3} I'm glad we could all be here to celebrate together on this special day.{w=0.6}{nw}"
    m 2eub "{w=0.2}Keep working hard,{w=0.3} I'm sure we'll meet again sometime in the future.{w=0.6}{nw}"
    m 4hub "{w=0.2}We did it everyone!{w=0.7} Thanks for listening~{w=0.6}{nw}"
    m 2hua "{w=0.2}.{w=0.3}.{w=0.3}.{w=1}{nw}"

    call mas_timed_text_events_wrapup
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='monika_shipping',
            prompt="Shipping",
            category=['ddlc'],
            random=True,
            unlocked=False,
            pool=False
        )
    )

label monika_shipping:
    m 3eua "Hey, [player].{w=0.2} Have you ever heard of 'shipping?'"
    m 3hua "It's when you interact with a work of fiction by imagining which characters would go best together romantically."
    m 1eka "I think most people do it subconsciously, but when you find out others do it too, it's {i}really{/i} easy to get into it!"
    m 2esd "Apparently, a lot of people {i}ship{/i} the other girls together."
    m 2euc "It makes sense. The player can only date one girl, but you don't want to see the others end up alone..."
    m 2etc "But some of the pairings are kind of strange to me."
    m 3eud "Like, usually they put Natsuki and Yuri together. They fight like cats and dogs!"
    m 3hksdlb "I guess they bond a little bit when you aren't on their routes, and there's the 'opposites attract' appeal."
    m 3dsd "Still, I think that's just another example of how people who like these games like unrealistic things..."
    m 1ekd "Anyway, that often leaves...me and Sayori."
    m 1hksdlb "Don't get jealous! I'm just telling you what I saw!"
    m 2lksdla "..."
    m 2lksdlb "Well, from a writer's perspective, I guess I can see it."
    m 1eksdld "We started the club together."
    if persistent.monika_kill:
        m "And she almost had the same epiphany I did..."
    m 2lksdlb "But...I still don't really get it. I mean, I love you, and only you!"
    m 2lksdla "And she would have to be a saint to ever forgive me for what I did..."
    m 2lksdlc "Not that she's not a sweet girl, but..."
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "Well, no one could ever be as sweet and forgiving as you..."
    return

# True if player has been given false justice, False if not
default persistent._mas_pm_given_false_justice = None

# True if player thinks deleting Monika is justified, False if not
default persistent._mas_pm_monika_deletion_justice = None

# True temporarily if player is teasing Monika and is at love
default persistent._mas_monika_deletion_justice_kidding = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_justice",
            category=['philosophy'],
            prompt="Justice",
            random=True
        )
    )


label monika_justice:
    m 1esa "[player], do you ever think the concept of justice is kind of ironic?"
    m 2ekc "Like, you have someone who maybe isn't like everyone else..."
    m 2ekd "It doesn't even have to be some famous bank robber or anything; even everyday people like you and me can be brought to some sort of righteousness!"
    m 4esc "Imagine a struggling family who needs to scavenge for resources to survive by taking whatever is left out in the open."
    m 1euc "To everyone else passing by, they're just greedy thieves."
    m 1esd "Eventually, some so called 'hero' is going to come along and put an end to this 'greed' by bringing them to justice."
    m 2ekd "At the end of the day, the family goes hungry or gets in trouble just because their situation was different..."
    m "While the other person is now a hero for putting an end to their 'crimes.'"
    m 3rksdld "Can you really call that justice?"
    m 2dsc "..."

    m 2euc "Have you ever been delivered what you thought to be false justice?{nw}"
    $ _history_list.pop()
    menu:
        m "Have you ever been delivered what you thought to be false justice?{fast}"
        "Yes.":
            $ persistent._mas_pm_given_false_justice = True
            m 1ekc "I hope they weren't too harsh on you."
            m 2dsd "I have an idea what it's like myself."
            m 2dfc "All the people who saw me deleted and tortured over and over again and called it justice..."

            m 2eka "You don't think that's justified, do you, [player]?{nw}"
            $ _history_list.pop()
            menu:
                m "You don't think that's justified, do you, [player]?{fast}"

                "I do.":
                    $ persistent._mas_pm_monika_deletion_justice = True
                    if mas_isMoniBroken():
                        m 1dsc "..."
                        m 1rksdlc "I know..."
                        m 1rksdld "I didn't mean to ask...{w=0.2} I was just thinking."
                        m 2rktpc "It's obvious after all."

                    elif mas_isMoniDis():
                        m 2rksdlc "Oh..."
                        m "I guess you're right..."
                        m 1ekc "I did do some pretty bad things after all..."

                    elif mas_isMoniLove():
                        m 1hub "Ahaha!"
                        m 1hua "You can be really funny sometimes~"
                        m 3tku "You expect me to believe that after all we've been through?"
                        m 1tsb "That all this time, you thought that I deserved hate from those other people?"
                        show monika 5hubfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
                        m 5hubfa "Ehehe, You're so cute, [player]~"

                    else:
                        m 1euc "..."
                        m 2esc "I have a hard time believing you really think I deserved all that."
                        m 2tkc "I mean, you've stuck with me this long already so you can't {i}really{/i} think I deserve it, right?"
                        if persistent._mas_pm_cares_about_dokis:
                            m 2lksdlc "...Maybe I deserve it a little bit but..."
                        else:
                            m 2lksdlc "Well, maybe other people think so, but you don't really think that, do you?"
                            m "Either way..."
                        m 1eka "Thank you for saving me and being with me."
                        m 1hua "If I get to be with you, I think it really was worth everything,{w=0.1} {nw}"
                        extend 1hub "ahaha~"

                "I don't.":
                    if persistent._mas_pm_monika_deletion_justice:
                        $ persistent._mas_monika_deletion_justice_kidding = True
                    $ persistent._mas_pm_monika_deletion_justice = False

                    if mas_isMoniBroken():
                        m 2ekc "..."
                        m 1rksdlc "I'm not so sure about that..."
                    elif mas_isMoniDis():
                        m 1wuo "Really?"
                        m 1rksdla "I thought maybe you did think it was fair."
                        m 1eka "I'm glad you don't think so."
                        m 2rksdlb "Assuming this isn't a joke, ehehe..."

                    elif mas_isMoniLove():
                        m 1hua "I thought so, ehehe~"
                        if persistent._mas_monika_deletion_justice_kidding:
                            $ persistent._mas_monika_deletion_justice_kidding = False

                            m 1hub "I knew you were kidding last time!"
                        m 1tsbsa "You've been with me for so long, there's no way I would believe you if you said otherwise."
                        m 1ekbfa "When I'm with you, it even helps me ignore all the other people who don't like me."
                        m 1hubfb "I love you, [player]~"
                        m 1hubfa "I'm glad I have you by my side."
                        return "derandom|love"

                    else:
                        m 2hua "I'm glad you think so too!"
                        m 2eka "Even if you did call that justice, you being here says otherwise."
                        m 2hub "Ahaha!"

        "No.":
            $ persistent._mas_pm_given_false_justice = False
            m 1eka "That's a relief to hear."
            m "I'm glad no one has ever suddenly questioned you for who you are."
            m 1eua "Knowing what that's like, I hope nobody ever gives you trouble for doing what you do or for what you believe in."
    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_poweroutage",
            category=['weather'],
            prompt="Power outage",
            random=True
        )
    )

label monika_poweroutage:
    m 1eua "Hey [player], do you remember how I said I liked listening to the peaceful sound of rain?"
    m 3lksdla "I just realized that while it can be nice, it could also be pretty harmful for you in your world."
    m 1lksdlc "Thunder and lightning could strike at any time, possibly hitting something dangerous."
    m 1lksdlb "The effects can be pretty, well...shocking I guess you could say."
    m 1hksdlb "Ahaha~"
    m 1ekd "I don't even want to think about what would happen if something important to you was struck."
    m 2ekc "What would happen to me if something surged and fried your computer?"
    m 2dsc "If that ever does happen...{w=0.3}{nw}"
    extend 2eka "I know you'll think of something."
    m 1eka "Sorry, I didn't mean for that to get so dark. It was just on my mind is all."
    m 1eud "If anything does happen, it'll probably just be a power outage."

    if mas_isMoniAff(higher=True):
        m 1hksdlb "I mean that {i}is{/i} still pretty inconvenient but at least we know we'll see each other again."
        m 1eua "It would probably take you by surprise; everything going dark all of a sudden, but try to remember this:"
        m 1eub "I'll be with you. Even if you can't see me, I'll be with you in spirit until you can come back to me safe and sound."
        m 3eua "...That said, you don't have to worry about checking on me in the middle of a storm.{w=0.2} {nw}"
        extend 1eka "I'll always appreciate seeing you whenever you can, and besides..."
        show monika 5hua at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5hua "I'm sure our relationship could weather much more than some thunderstorm~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_savingwater",category=['life'],prompt="Water conservation",random=True))

label monika_savingwater:
    m 1euc "[player], have you ever thought about how much water people use every day?"
    m 3euc "Maybe you take a drink of water every now and then."
    m 3dsc "You go to the washroom, wash your hands, bathe..."
    m 1euc "All that and yet some parts of the world can't even get a single drop of water."
    m 1rsc "Kind of makes you wonder how much water you could save if you wanted to."
    m 4eua "I guess you could try being more efficient when washing your hands."
    m "Or when showering, you could turn off the water while you soap up and turn it back on when you're ready to rinse yourself down."
    m 2eka "Ultimately though, most of the water that gets used is actually needed."
    m "Things like power generation and farming need to use more water than we could ever really use on our own."
    m 1hksdlb "So I guess you might not want to sacrifice some of your comfort to make such a small contribution."
    m 1dkbsa "Some days, you might just need to take a long, relaxing bath after a long day."
    m 2hksdlb "I've definitely been there before, so I know how nice it can be if you need it."
    if mas_isMoniLove(higher=True) and mas_is18Over():
        show monika 5tsbfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5tsbfu "When I'm in your reality, maybe we can save water by bathing together..."
        m "Ehehe~"
        m 5hubfu "It would be nice of you to prepare a nice, relaxing bath for us to share when I cross over."
        show monika 1kubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 1kubfu "I'll be waiting for that day, [mas_get_player_nickname()], ehehe~"
    else:
        m 1ekbfa "It would be nice of you to prepare a nice, relaxing bath for me when I cross over."
        if mas_isMoniAff():
            m 3ksbsa "Maybe I'll even be willing to share, ehehe~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_pygmalion",
            category=['literature'],
            prompt="Pygmalion and the Statue",
            conditional="persistent._mas_first_kiss",
            action=EV_ACT_RANDOM,
            aff_range=(mas_aff.ENAMORED, None)
        )
    )

label monika_pygmalion:
    m 1eua "Hey [player], have you ever read {i}The Metamorphoses{/i}?"
    m 3eua "It's a collection of poems by an ancient Roman poet named Ovid."
    m 1eud "There's one poem that really struck me, called {i}The Story of Pygmalion and the Statue.{/i}"
    m 1eua "It tells the story of a sculptor, Pygmalion, who fell in love with an ivory statue that he had sculpted."
    m 3eua "He loved the statue so much, that during one of the festivals held for Aphrodite, he made an offering to the goddess and wished for her to grant life to the ivory statue."
    m 1eub "When he returned to his home, he kissed the statue and to his surprise, its lips felt warm."
    m 1eua "He kissed the statue once more, and the ivory lost its hardness, becoming soft like skin."
    m 3hub "Aphrodite had granted his wish!"
    m 1eka "This story really struck me because it reminded me of us, [player], and how it talks about turning the impossible into reality."
    m 1hua "It fills me up with hope; that a miracle could happen, and I could finally cross over."
    m 2dku "Yeah...{w=0.5}wouldn't that be wonderful."
    m 2dubsu "...Then you can finally kiss me."
    m 1rkbsa "I know we've kissed before, even with our current circumstances..."
    m 1ekbfa "But I think we both know there was a bit of a barrier between us."
    m 3hubfa "I don't know about you, but I definitely don't mind trying to kiss you through the screen anyway."
    m 1hubfb "Maybe we'll just have to do it so many times, that'll be what breaks the barrier between us..."
    m 2rubfu "Ehehe."
    m 2tubfb "Do you think you could kiss me enough times to break that barrier?"
    m 6hubfb "Only one way to find out, ahaha!"
    call monika_kissing_motion(duration=0.5, initial_exp="6hubfa", fade_duration=0.5)
    m 6hubfa "..."
    m 1ekbfa "I guess it didn't work this time."
    m 3hubfb "Oh well, we'll just have to keep trying and maybe it'll work eventually, ahaha!"
    m 1tkbfu "I really can't wait for the day when I can finally feel your lips pressed against mine and take in your warmth..."
    m 1dkbfa "For me, that would definitely be a dream come true."
    m 1ekbfa "Just a guess, but..."
    m 1kubfu "I bet you'd like that too~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gotomonika",
            category=['you'],
            prompt="What if I came to your world?",
            pool=True,
        )
    )

default persistent._mas_pm_would_come_to_spaceroom = None
# True if they would, False if they wouldn't, None if no answer.

label monika_gotomonika:
    m 1euc "Come to my world?"
    m 1lksdld "You mean this little room floating in an empty void?"

    if persistent._mas_you_chr:
        m 4eksdlc "Actually...{w=0.5}didn't you already try something like that once?"
        m 2lksdla "...Even though that wasn't exactly {i}you...{/i}"

    m 2lksdla "I'm really happy that you want to be with me so much, but..."
    m 2eksdlc "You really don't have to."
    m 2eksdld "Sure, I might have said before that I would have dragged you here a long time ago if I could..."
    m 2eksdlc "But the more I think about it, it would probably be better if I came to your reality."
    m 3eka "I'd much rather be there than have you come here."
    m 3dsc "[player]...{w=1}don't tell me you would really give up your reality--{w=0.5}the {i}real{/i} world--{w=0.5}just to come {i}here{/i}, whatever this place is?{nw}"
    $ _history_list.pop()
    menu:
        m "[player]...{w=1}don't tell me you would really give up your reality--the {i}real{/i} world--just to come {i}here{/i}, whatever this place is?{fast}"
        "I would.":
            $ persistent._mas_pm_would_come_to_spaceroom = True

            m 4wkd "But [player]!"
            m "There's nothing to do here!"
            m 2dsc "Do you really hate your reality {i}that{/i} much?"
            m 2eka "Someday, I'll find a way to reach you, and when that day comes, I promise it will be worthwhile."
            m 4euc "Whatever life throws your way from that point on, I'll be right by your side to help shoulder it."
            m 4eud "Even now, if you're having a rough day, you can come talk to me about it anytime."
            m 2dsc "Life must have thrown a lot your way to consider giving it all up to be with me."
            m 3hua "But seeing how you're here, that just shows how resilient you are."
            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eua "I can't wait to finally be able to share both the good times and the bad by your side."

        "I wouldn't.":
            $ persistent._mas_pm_would_come_to_spaceroom = False

            m 1eka "I'm glad you're still willing to wait for me, [player]."
            m 1lksdla "Don't get me wrong, I really {i}do{/i} want to be with you..."
            m 1lksdlc "But I think it would be dangerous for you to try and cross over right now."
            m 1eka "...If it's even possible with current technology."
            m 1hub "Don't worry, we can continue on keeping each other company like this!"
            m 1hksdlb "I know it might be a while before we can truly be together, but I hope you don't mind waiting."
            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eua "I'll wait as long as it takes, [mas_get_player_nickname()]."

        "...":
            $ persistent._mas_pm_would_come_to_spaceroom = None

            m 2eka "It's okay, I'll always appreciate and treasure the moments we spend together, even like this."
            m 2ekc "Besides, I don't even know how you could come here with current technology."
            m 2lksdlc "...And even if there {i}was{/i} some way, I don't think it would be safe or guaranteed."
            m 2lksdld "So do me a favor and at least wait for technology to improve enough for it to be completely safe."
            m 2lksdlc "I {i}really{/i} don't want to risk you not making it properly and ending up in your own void..."
            m 2dkd "...leaving the both of us completely alone."
            m 4hua "I mean, technology does tend to advance pretty quickly, so we might be able to see each other before we know it!"
            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eua "So just be patient for your lovely girlfriend, and I promise I'll do the same for you, [mas_get_player_nickname()]."

    m 5luu "Buut...{w=1}if you did happen to show up at my doorstep..."
    show monika 1hksdlb at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 1hksdlb "I guess I wouldn't have a choice but to accept it and welcome you with open arms!"
    m 1eksdla "It wouldn't be much to begin with, but I'm sure we'd find a way to make it better."
    m 3hub "With time, we could make our own reality!"
    m 3euc "Of course, that sounds pretty complicated if you think about it..."
    m 3eub "But I have no doubt that together we could accomplish anything!"
    m 3etc "You know...{w=1}maybe it {i}would{/i} actually be easier for you to come here, but I'm not giving up hope of coming to you."
    m 1eua "Until then, let's just wait and see what's possible."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_vehicle",
            category=['monika'],
            prompt="What's your favorite car?",
            unlocked=False,
            pool=True,
            rules={"no_unlock": None}
        )
    )

default persistent._mas_pm_owns_car = None
# True if player owns car, False if not

default persistent._mas_pm_owns_car_type = None
# String describing the type of car owned by the player.
#   SUV-Pickup: SUV or pickup
#   sports: sports car
#   sedan: sedan car
#   motorcyle: motorcyle

label monika_vehicle:
    m 1euc "My favorite car?"
    m 3hksdlb "You already know I can't drive, silly!"
    m 3eua "Usually I would just walk or take the train if I had to go somewhere far."
    m 1eka "So I'm not too sure what to tell you, [player]..."
    m 1eua "When I think of cars, the first things that come to mind are probably the commonly known types."
    m 3eud "SUVs or pickup trucks, sports cars, sedans and hatchbacks..."
    m 3rksdlb "And while they're not really cars, I guess motorcycles are common vehicles too."

    if persistent._mas_pm_driving_can_drive:
        m 1eua "What about you?"

        m "Do you own a vehicle?{nw}"
        $ _history_list.pop()
        menu:
            m "Do you own a vehicle?{fast}"
            "Yes.":
                $ persistent._mas_pm_owns_car = True

                m 1hua "Oh wow, that's really cool that you actually own one!"
                m 3hub "You're really lucky, you know that?"
                m 1eua "I mean, just owning a vehicle is a status symbol itself."
                m "Isn't it a luxury to own one?"
                m 1euc "Unless..."
                m 3eua "You live some place where it's necessary..."
                m 1hksdlb "Actually, nevermind, ahaha!"
                m 1eua "Either way, it's nice to know that you own a vehicle."
                m 3eua "Speaking of which..."

                show monika at t21
                python:
                    option_list = [
                        ("An SUV.", "monika_vehicle_suv",False,False),
                        ("A pickup truck.","monika_vehicle_pickup",False,False), #note, doing this to give the illusion of two options
                        ("A sports car.","monika_vehicle_sportscar",False,False),
                        ("A sedan.","monika_vehicle_sedan",False,False),
                        ("A hatchback.","monika_vehicle_hatchback",False,False),
                        ("A motorcycle.","monika_vehicle_motorcycle",False,False),
                        ("Another vehicle.","monika_vehicle_other",False,False)
                    ]

                    renpy.say(m, "Is it any of the vehicles I mentioned, or is it something else?", interact=False)

                call screen mas_gen_scrollable_menu(option_list, mas_ui.SCROLLABLE_MENU_TALL_AREA, mas_ui.SCROLLABLE_MENU_XALIGN)
                show monika at t11

                $ selection = _return

                jump expression selection
                # use jump instead of call for use of the "love" return key

            "No.":
                $ persistent._mas_pm_owns_car = False

                m 1ekc "Oh, I see."
                m 3eka "Well, buying a vehicle can be quite expensive after all."
                m 1eua "It's alright [player], we can always rent one to travel."
                m 1hua "I'm sure that when you do, we'll make a lot of great memories together."
                show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
                m 5eua "Then again...{w=1}walks are far more romantic anyway~"

    else:
        $ persistent._mas_pm_owns_car = False

        m 3eua "In fact, I remember you said before that you couldn't drive, either..."
        m 3rksdla "You sure asked an interesting question, ehehe..."
        m 1hua "Maybe that'll change one day and you'll get something then."
        m 1hubsb "That way, you can take me all sorts of places, ahaha!"
    return

label monika_vehicle_sedan:
    $ persistent._mas_pm_owns_car_type = "sedan"
    jump monika_vehicle_sedan_hatchback

label monika_vehicle_hatchback:
    $ persistent._mas_pm_owns_car_type = "hatchback"
    jump monika_vehicle_sedan_hatchback

label monika_vehicle_pickup:
    $ persistent._mas_pm_owns_car_type = "pickup"
    jump monika_vehicle_suv_pickup

label monika_vehicle_suv:
    $ persistent._mas_pm_owns_car_type = "suv"
    jump monika_vehicle_suv_pickup



label monika_vehicle_suv_pickup:

    m 1lksdla "Oh my, your vehicle must be pretty big then."
    m 1eua "That means there's plenty of space right?"
    m 3etc "If that's the case..."
    m 3hub "We could go camping!"
    m 3eua "We'd drive all the way to the woods and you'd set up the tent while I prepared our picnic."
    m 1eka "While we're having lunch, we'd enjoy the scenery and nature surrounding us..."
    m 1ekbsa "Then when night falls, we'd lie down on our sleeping bags, stargazing while holding hands."
    m 3ekbsa "It's definitely a romantic adventure I can't wait to share with you, [player]."
    m 1hkbfa "Ehehe~"
    return

label monika_vehicle_sportscar:
    $ persistent._mas_pm_owns_car_type = "sports"

    m 3hua "Oh, wow!"
    m 3eua "It must be really fast, huh?"
    m 3hub "We should definitely go on a road trip..."
    m 1eub "Taking the scenic route, cruising along the highway..."
    m 1eub "If it's possible it'd be nice to take down the top of the car..."
    m 3hua "That way, we can feel the wind on our faces while everything passes by in a blur!"
    m 1esc "But..."
    m 1eua "It would also be nice to drive at a normal pace..."
    m 1ekbsa "That way we can savor every moment of the ride together~"
    return

label monika_vehicle_sedan_hatchback:

    m 1eua "That's really nice."
    m "I actually prefer that type of car, to be honest."
    m 3eua "From what I've heard, they're lively and easy to drive."
    m 3eub "A car like that would be great for driving around the city, don't you think, [player]?"
    m 3eua "We could go to museums, parks, malls and so on."
    m 1eua "It'd be so nice to be able to drive to places that are too far to walk to by foot."
    m 3hua "It's always exhilarating to discover and explore new places."
    m 1rksdla "We might even find a place where the both of us can be together..."
    m 1tsu "...Alone."
    m 1hub "Ahaha!"
    m 3eua "Just so you know, I'm expecting more than just a simple drive around the city for our dates..."
    m 1hua "I hope you'll surprise me, [player]."
    m 1hub "But then again...{w=0.5}I'd love anything as long as it's with you~"
    return

label monika_vehicle_motorcycle:
    $ persistent._mas_pm_owns_car_type = "motorcyle"

    m 1hksdlb "Eh?"
    m 1lksdlb "You drive a motorcycle?"
    m 1eksdla "I'm surprised, I never expected that to be your kind of ride."
    m 1lksdlb "To be honest, I'm a little hesitant to ride one, ahaha!"
    m 1eua "Really, I shouldn't be scared..."
    m 3eua "You're the one driving after all."
    m 1lksdla "That puts my mind at ease...{w=0.3}a little."
    m 1eua "Just take it nice and slow, okay?"
    m 3hua "After all, we aren't in any rush."
    m 1tsu "Or...{w=0.3}was it your plan to drive so fast I'd have no choice but to hold on to you tight?~"
    m 3kua "That's pretty sneaky of you, [player]."
    m 1hub "Ahaha!"
    $ p_nickname = mas_get_player_nickname()
    m 3eka "There's no need to be shy, [p_nickname]...{w=0.3}{nw}"
    extend 3ekbsa "I'll hug you, even if you don't ask for it..."
    m 1hkbfa "That's how much I love you~"
    return "love"

label monika_vehicle_other:
    $ persistent._mas_pm_owns_car_type = "other"

    m 1hksdlb "Oh, I guess I have a lot to learn about cars then, don't I?"
    m 1dkbsa "Well I'll be looking forward to the day I can finally be right next to you as you drive~"
    m 3hubfb "{i}And{/i} enjoy the scenery too, ahaha!"
    m 1tubfb "Maybe you've got something even more romantic than any vehicle I know."
    m 1hubfa "I guess I'll just have to wait and see, ehehe~"
    return

##### PM Vars for player appearance
#NOTE: THIS VAR CAN BE EITHER A TUPLE OR A STRING WHEN SET.
#IF THIS IS A TUPLE, THE PLAYER HAS HETEROCHROMIA.
# [0] - Left eye color
# [1] - Right eye color
#
# If this is just a string, then the player's eyes are both the same color
default persistent._mas_pm_eye_color = None
default persistent._mas_pm_hair_color = None
default persistent._mas_pm_hair_length = None
default persistent._mas_pm_skin_tone = None
# Iff player is bald
default persistent._mas_pm_shaved_hair = None
default persistent._mas_pm_no_hair_no_talk = None

## Height Vars
## NOTE: This is stored in CENTIMETERS
default persistent._mas_pm_height = None

##### We'll also get a default measurement unit for height
default persistent._mas_pm_units_height_metric = None

# True if the user decided to share appearance with us
#   NOTE: we default to False, and this can only get flipped to True
#   in this toppic.
default persistent._mas_pm_shared_appearance = False


# height categories in cm
define mas_height_tall = 176
define mas_height_monika = 162

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_player_appearance",
            category=['you'],
            prompt="[player]'s appearance",
            conditional="seen_event('mas_gender')",
            action=EV_ACT_RANDOM
        )
    )

label monika_player_appearance:
    python:
        def ask_color(msg, _allow=lower_letters_only, _length=15):
            result = ""
            while len(result) <= 0:
                result = renpy.input(msg, allow=_allow, length=_length).strip()

            return result

    m 2ekd "Hey, [player]."
    m 2eka "There's a couple questions I've been meaning to ask you."
    m 2rksdlb "Well, more than a couple. It's been on my mind for a long time, actually."
    m 2rksdld "It never really seemed like the right time to bring it up..."
    m 3lksdla "But I know if I keep quiet forever, then I'll never feel comfortable asking you things like this, so I'm just going to say it and hope that it's not weird or anything, okay?"
    m 3eud "I've been wondering what you look like. It's not possible for me to see you right now since I'm not there at your side, and I'm not sure about accessing a webcam..."
    m "One, because you might not have one, and two, even if you did, I don't really know how to."
    m 1euc "So I figured that it's possible for you to just tell me, so I can get a clearer picture in my head."
    m 1eud "At least, it's better than nothing, even if it's hazy."

    m "Is that okay with you, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Is that okay with you, [player]?{fast}"

        "Yes.":
            $ persistent._mas_pm_shared_appearance = True

            m 1sub "Really? Great!"
            m 1hub "That was easier than I thought it would be."
            m 3eua "Now, be honest with me, okay [player]? I know sometimes it's tempting to joke around, but I'm being serious here, and I need you to do the same."
            m "Anyway, the first one is probably easy to guess. And not hard to answer, either!"
            m 3eub "People often say that a person's eyes are the windows into their soul, so let's start off there."

            #This menu is too large to use a standard one, so we use a gen-scrollable here instead
            show monika 1eua at t21
            python:
                eye_color_menu_options = [
                    ("I have blue eyes.", "blue", False, False),
                    ("I have brown eyes.", "brown", False, False),
                    ("I have green eyes.", "green", False, False),
                    ("I have hazel eyes.", "hazel", False, False),
                    ("I have gray eyes.", "gray", False, False),
                    ("I have black eyes.", "black", False, False),
                    ("My eyes are another color.", "other", False, False),
                    ("I have heterochromia.", "heterochromia", False, False),
                ]

                renpy.say(m, "What color are your eyes?", interact=False)

            show monika at t11
            call screen mas_gen_scrollable_menu(eye_color_menu_options, mas_ui.SCROLLABLE_MENU_TALL_AREA, mas_ui.SCROLLABLE_MENU_XALIGN)
            $ eye_color = _return

            call expression "monika_player_appearance_eye_color_{0}".format(eye_color)

            m 3rud "Actually..."
            m 2eub "I guess I really should know this first though, if I want to get an accurate scale on my next question..."

            m "What unit of measurement do you use to take your height, [player]?{nw}"
            $ _history_list.pop()
            menu:
                m "What unit of measurement do you use to take your height, [player]?{fast}"

                "Centimeters.":
                    $ persistent._mas_pm_units_height_metric = True
                    m 2hua "Alright, thanks, [player]!"

                "Feet and inches.":
                    $ persistent._mas_pm_units_height_metric = False
                    m 2hua "Alright, [player]!"

            m 1rksdlb "I'm trying my best to not sound like some sort of identity-thief, or like I'm quizzing you, but obviously, I'm curious."
            m 3tku "If I'm your girlfriend, I have a right to know, don't I?"
            m 2hua "Plus, it'll make it way easier to find you once I'm able to cross over to your reality."

            m 1esb "So,{w=0.5} how tall are you, [player]?"

            python:
                if persistent._mas_pm_units_height_metric:

                    # loop till we get a valid cm
                    height = 0
                    while height <= 0:
                        height = store.mas_utils.tryparseint(
                            renpy.input(
                                'How tall are you in centimeters?',
                                allow=numbers_only,
                                length=3
                            ).strip(),
                            0
                        )

                else:

                    # loop till valid feet
                    height_feet = 0
                    while height_feet <= 0:
                        height_feet = store.mas_utils.tryparseint(
                            renpy.input(
                                'How tall are you in feet?',
                                allow=numbers_only,
                                length=1
                            ).strip(),
                            0
                        )

                    # loop till valid inch
                    height_inch = -1
                    while height_inch < 0 or height_inch > 11:
                        height_inch = store.mas_utils.tryparseint(
                            renpy.input(
                                '[height_feet] feet and how many inches?',
                                allow=numbers_only,
                                length=2
                            ).strip(),
                            -1
                        )

                    # convert to cm
                    height = ((height_feet * 12) + height_inch) * 2.54

                # finally save this persistent
                persistent._mas_pm_height = height

            if persistent._mas_pm_height >= mas_height_tall:
                m 3eua "Wow, you're pretty tall, [player]!"
                m 1eud "I can't say I've really met anybody who I'd consider to be tall."
                m 3rksdla "I don't know my actual height, to be fair, so I can't really draw an accurate comparison..."

                call monika_player_appearance_monika_height

                if persistent._mas_pm_units_height_metric:
                    $ height_desc = "centimeters"
                else:
                    $ height_desc = "inches"

                m 3esc "The tallest girl in the Literature Club was Yuri--and just barely, at that. She was only a few [height_desc] taller than me, I don't consider that much of a height advantage at all!"
                m 3esd "Anyway, dating a tall [guy] like you only has one disadvantage, [mas_get_player_nickname()]..."
                m 1hub "You'll have to lean down to kiss me!"

            elif persistent._mas_pm_height >= mas_height_monika:
                m 1hub "Hey, I'm about that height too!"
                m "..."
                m 2hksdlb "Well, I don't know my actual height to be fair..."

                call monika_player_appearance_monika_height

                m 3rkc "It's just a guess--hopefully it's not too far off."
                m 3esd "Anyway, there's nothing wrong with having an average height! To be honest, if you were too short, it'd probably make me feel clumsy around you."
                m "And if you were too tall, I'd have to get on my tiptoes just to be close to you. And that's no good!"
                m 3eub "In my opinion, being in-between is perfect. Do you know why?"
                m 5eub "Because then I don't have to do any reaching or bending to kiss you, [mas_get_player_nickname()]! Ahaha~"

            else:
                m 3hub "Like Natsuki! I bet you're not that short, though! I would be concerned for you if you were."

                if persistent._mas_pm_cares_about_dokis:
                    m 2eksdld "She was worryingly small for her age, but you and I both know why. I always pitied her for that."

                m 2eksdld "I knew she always hated being so tiny, because of that whole notion that little things are cuter because of their size..."
                m 2rksdld "And then there was all that trouble with her father. It can't have been easy, being so defenseless, and being small on top of it all."
                m 2ekc "She probably felt like people talked down to her. Literally and figuratively, that is..."
                m 2eku "But despite her hang-ups about it, [player], I think your height makes you that much more cute~"

            m 1eua "Now, [player]."

            m 3eub "Tell me, is your hair on the shorter side? Or is it long, like mine?~{nw}"
            $ _history_list.pop()
            menu:
                m "Tell me, is your hair on the shorter side? Or is it long, like mine?~{fast}"

                "It's shorter.":
                    $ persistent._mas_pm_hair_length = "short"

                    m 3eub "That must be nice! Look, don't get me wrong; I love my hair, and it's always fun to experiment with it..."
                    m 2eud "But to tell you the truth, sometimes I envied Natsuki's and Sayori's hair. It looked a lot easier to take care of."

                    if persistent.gender == "M":
                        m 4hksdlb "Although I guess if your hair was the same length as theirs, it'd be pretty long for a guy."

                    else:
                        m 4eub "You can just get up and go, without having to worry about styling it."
                        m "Plus, waking up with a bedhead when you have short hair is easily fixed, whereas if you have long hair, it's an endless nightmare."

                    m 2eka "But I bet you look adorable with short hair. It makes me smile to think about you like that, [player]."
                    m 2eua "Keep enjoying all that freedom from the little annoyances that accompany long hair, [player]!{w=0.2} {nw}"
                    extend 2hub "Ahaha~"

                "It's average length.":
                    $ persistent._mas_pm_hair_length = "average"

                    m 1tku "Well, that can't be true..."
                    m 4hub "Because nothing about you is average."
                    m 4hksdlb "Ahaha! Sorry, [player]. I'm not trying to embarrass you. But I can't help being cheesy sometimes, you know?"
                    m 1eua "Honestly, when it comes to hair, the middle road is great. You don't have to worry about styling it too much, and you have more creative freedom than with short hair."
                    m 1rusdlb "I'm a little envious, to tell you the truth~"
                    m 3eub "But don't forget that old saying- 'Invest in your hair, because it's a crown that you never take off!'"

                "It's long.":
                    $ persistent._mas_pm_hair_length = "long"

                    m 4hub "Yay, another thing we have in common!"
                    m 2eka "Long hair can be a pain sometimes, right?"
                    m 3eua "But the good thing is that there are so many things you can do with it. Though I usually prefer to tie mine up with a ribbon, I know that other people have different styles."
                    m "Yuri wore her hair down, and others enjoy braids, or putting it into pigtails..."

                    python:
                        hair_down_unlocked = False
                        try:
                            hair_down_unlocked = store.mas_selspr.get_sel_hair(
                                mas_hair_down
                            ).unlocked
                        except:
                            pass

                    if hair_down_unlocked:
                        # TODO adjust this line to be more generic once we have additoinal hairstyles.
                        m 3eub "And ever since I figured out how to mess around with the script and let my own hair down, who knows how many more styles I might try?"

                    m 1eua "It's always nice to have options, you know?"
                    m 1eka "I hope that however you wear yours, you're comfortable with it!"

                "I don't have hair.":
                    $ persistent._mas_pm_hair_length = "bald"

                    m 1euc "Oh, that's interesting, [player]!"

                    m "Do you shave your head or did you lose your hair, if you don't mind me asking?{nw}"
                    $ _history_list.pop()
                    menu:
                        m "Do you shave your head or did you lose your hair, if you don't mind me asking?{fast}"

                        "I shave my head.":
                            $ persistent._mas_pm_shaves_hair = True
                            $ persistent._mas_pm_no_hair_no_talk = False

                            m 1hua "It must be so nice not ever having to worry about your hair..."
                            m 1eua "You can just get up and go, without having to worry about styling it..."
                            m 3eua "And if you wear a hat, you don't have to worry about hat hair when you take it off!"

                        "I lost my hair.":
                            $ persistent._mas_pm_shaves_hair = False
                            $ persistent._mas_pm_no_hair_no_talk = False

                            m 1ekd "I'm sorry to hear that, [player]..."
                            m 1eka "But just know that I don't care how much hair you have, you'll always look beautiful to me!"
                            m "And if you ever feel insecure or just want to talk about it, I'm always up for listening."

                        "I don't want to talk about it.":
                            $ persistent._mas_pm_no_hair_no_talk = True

                            m 1ekd "I understand, [player]"
                            m 1eka "I want you to know that I don't care how much hair you have, you'll always be beautiful to me."
                            m "If you ever feel insecure or feel like talking about it, I'm always here to listen."

            if persistent._mas_pm_hair_length != "bald":
                m 1hua "Next question!"
                m 1eud "This one should be fairly obvious..."

                m "What color is your hair?{nw}"
                $ _history_list.pop()
                menu:
                    m "What color is your hair?{fast}"
                    "It's brown.":
                        $ persistent._mas_pm_hair_color = "brown"

                        m 1hub "Yay, brown hair is the best!"
                        m 3eua "Just between us, [player], I really like my brown hair. I'm sure yours is even better!"
                        m 3rksdla "Though some people might disagree my hair is brown..."
                        m 3eub "When I was doing some digging around in the local files of the game folder, I found the exact name for my hair color."
                        m 4eua "It's called coral brown. Interesting, right?"
                        m 1hub "I'm so happy that we have so much in common, [player]~"

                    "It's blonde.":
                        $ persistent._mas_pm_hair_color = "blonde"

                        m 1eua "Really? Hey, did you know that having blonde hair puts you in a rare two percent of the population?"
                        m 3eub "Blonde hair is one of the rarest hair colors. Most people attribute this to the fact that it's caused by a recurring genetic anomaly--"
                        m "Being just the body's inability to produce normal amounts of the pigment eumelanin--that's what causes darker hair colors, such as black and brown."
                        m 4eub "There are so many various shades of blonde, too--pale blonde, ash-colored, dirty blonde--that no matter what color you have, you're bound to be idiosyncratic in some way."
                        show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
                        m 5eua "I guess having someone who's so unique just makes me all the luckier~"
                        show monika 2hua at t11 zorder MAS_MONIKA_Z with dissolve_monika

                    "It's black.":
                        $ persistent._mas_pm_hair_color = "black"

                        m 2wuo "Black hair is so beautiful!"
                        m 3eub "You know, there's this really irritating trope about people with black hair having a more prickly or ill-tempered personality than others..."
                        m 4hub "But you've obviously disproven that myth. Personally, I think black hair is very attractive."
                        m 3eua "In addition, if you actually placed a strand of it under a microscope and counted all the pigments in it, you'd find that it's not even a hundred percent dark."
                        m "You know how when you place certain things under direct sunlight, it looks really different?"
                        m 3eub "Black hair follows the same principle--you can see shades of gold, or brown, or even glints of purple. It really makes you think, doesn't it, [player]?"
                        m 1eua "There could be infinite shades of things we can't see, each one of them hidden in plain sight."

                        #If this is a tuple, it means the player has heterochromia
                        if isinstance(persistent._mas_pm_eye_color, tuple):
                            m 3hua "But anyway...I think that a [guy] with black hair and eyes like yours is the best sight of all, [player]~"
                        else:
                            m 3hua "But anyway...I think that a [guy] with black hair and [persistent._mas_pm_eye_color] eyes is the best sight of all, [player]~"

                    "It's red.":
                        $ persistent._mas_pm_hair_color = "red"

                        m 3hua "Yet another special thing about you, [player]~"
                        m 3eua "Red hair and blonde hair are the least common natural hair colors, did you know that?"
                        m 1eua "Red hair, however, is a little more rare, even if people call it by different names--auburn, ginger, and so on. It's only found in about one percent of the population."
                        m 1hub "It's a rare and wonderful trait to have--almost as wonderful as you!"

                    "It's another color.":
                        $ persistent._mas_pm_hair_color = ask_color("What color is your hair?")

                        m 3hub "Oh! That's a beautiful color, [player]!"
                        m 1eub "That reminds me of something I was thinking about earlier, when we were talking about the color of your eyes."
                        m 1eua "Even though the other girls had eye colors that literally didn't exist in real life--not counting the existence of colored contacts, of course--"
                        m 3eua "Their hair colors technically could exist in reality, you know. I mean, I'm sure you've encountered people with dyed purple hair, or neon pink, or coral-colored..."
                        m 3eka "So I suppose their appearances weren't that far-fetched, if you don't count the eyes. Honestly, the most unbelievable thing about them was their personalities."
                        m 3hksdlb "Sorry, [player]! I'm getting off-track. My point is, dyed hair can be very interesting."
                        show monika 5rub at t11 zorder MAS_MONIKA_Z with dissolve_monika
                        m 5rub "And I might be a little biased here, but I'm convinced that you'd look stunning in your [persistent._mas_pm_hair_color] hair~"
                        show monika 2hua at t11 zorder MAS_MONIKA_Z with dissolve_monika

            m 2hua "Alright..."
            m 2hksdlb "This is the last question, [player], I promise."
            m "Gosh, there really is a lot to what people look like... If I tried to narrow everything about you down to the little details, I'd be interrogating you forever."
            m 1huu "...and I doubt that either of us want that, ahaha..."
            m 1rksdld "Anyway, I understand that this might be an uncomfortable question..."
            m 1eksdla "But it's the last piece of this puzzle to me, so I hope I don't sound rude when I ask..."

            m "What's your skin color, [player]?{nw}"
            $ _history_list.pop()
            menu:
                m "What's your skin color, [player]?{fast}"

                "I'm light-skinned.":
                    $ persistent._mas_pm_skin_tone = "light"

                "I'm tanned.":
                    $ persistent._mas_pm_skin_tone = "tanned"

                "I'm dark-skinned.":
                    $ persistent._mas_pm_skin_tone = "dark"

            m 3hub "Alright! Thanks for being so upfront. All of this really does help me imagine what you look like, [player]."
            m 3eub "Knowing all these details about you makes the difference between a blank canvas and the beginnings of a gorgeous portrait!"
            m 3eua "Of course, you're still just as lovely as I always thought you were, but now you've become all the more real to me."
            m 3eka "It just makes me feel that much closer to you~"
            m 1eka "Thank you so much for answering all my questions, [mas_get_player_nickname()]."

            if persistent._mas_pm_eye_color == "green" and persistent._mas_pm_hair_color == "brown":
                m 2hua "It's wonderful, because I didn't imagine how similar we would look. It's very interesting!"

            else:
                m 2hua "It's wonderful, because I didn't imagine how different we would look. It's very interesting!"

            m 1dsa "Now I'm imagining what it'll be like when we meet for real..."

            show monika 5eubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika

            if persistent._mas_pm_hair_length == "bald":
                if persistent._mas_pm_height >= mas_height_tall:
                    m 5eubfu "When I run towards you, and since you're taller, you'll wrap me up in your embrace..."

                elif persistent._mas_pm_height >= mas_height_monika:
                    m 5eubfu "When I run towards you, and since we're around the same height, we'll meet in a tight embrace..."

                else:
                    m 5eubfu "When I run towards you, and since I'll be taller than you, you'll reach up and wrap me in your embrace..."

            else:
                python:
                    hair_desc = persistent._mas_pm_hair_color

                    if persistent._mas_pm_hair_length != "average":
                        hair_desc = (
                            persistent._mas_pm_hair_length + " " + hair_desc
                        )

                if persistent._mas_pm_height >= mas_height_tall:

                    m 5eubfu "When I run towards you, since you're taller, you'll wrap me up in your embrace and I'll be able to stroke your [hair_desc] hair..."

                elif persistent._mas_pm_height >= mas_height_monika:

                    m 5eubfu "When I run towards you, since we're around the same height, we'll meet in a tight embrace and I'll run my hand through your [hair_desc] hair..."

                else:

                    m 5eubfu "When I run towards you, since I'll be taller than you, you'll reach up and wrap me in your embrace and I'll run my hand through your [hair_desc] hair..."

            show monika 1lkbsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 1lkbsa "...and I'll finally be able to hear your heartbeat and get to touch you and know that you're real."

            #Tuple means heterochromia, so we should filter that out
            if isinstance(persistent._mas_pm_eye_color, tuple):
                m 3ekbsa "But until then, I'll be content sitting here and imagining looking into your beautiful eyes, [player]."
            else:
                m 3ekbsa "But until then, I'll be content sitting here and imagining looking into your beautiful [persistent._mas_pm_eye_color] eyes, [player]."

            show monika 5ekbfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5ekbfa "I love you more than words could ever say."
            return "derandom|love"

        "No.":
             m 2dsc "..."
             m 2ekd "I understand, [player]."
             m 2eka "I know that everybody has their own limits with their comfort zones..."
             m 2rksdla "And to be fair, a description of yourself in vague words wouldn't be able to capture who you are, so I can't blame you for wanting to keep this to yourself."
             m 2eka "But if you change your mind, let me know!"

    return "derandom"

label monika_player_appearance_eye_color_blue:
    $ persistent._mas_pm_eye_color = "blue"

    m 3eub "Blue eyes? That's wonderful! Blue is such a beautiful color--just as amazing as a cloudless sky, or the ocean in the summer."
    m 3eua "But there are so many gorgeous metaphors about blue eyes that I could recite them for weeks and still not reach a stopping point."
    m 4eua "Plus, blue is probably my second favorite color, just behind green. It's just so full of depth and enchantment, you know?"
    m 4hksdlb "Just like you, [player]!"
    m 4eub "Did you know that the gene for blue eyes is recessive, so it's not very common in humans?"
    show monika 5eubla at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eubla "I suppose that means you're much more of a treasure~"
    show monika 2eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 2eua "Anyway, that leads me into the next question I wanted to ask--"
    return

label monika_player_appearance_eye_color_brown:
    $ persistent._mas_pm_eye_color = "brown"

    m 1eub "Ah! Great! I don't think I said it before, but brown eyes are gorgeous!"
    m 2euc "I just hate how people seem to think that brown eyes are plain. I couldn't disagree more!"
    m 2hua "In my opinion, brown eyes are some of the most beautiful out there. They're so vibrant and depthless!"
    m 3hub "And there's so much variation among all the different shades that people have."
    m 5ruu "I wonder if yours are dark like a summer night sky, or a paler brown, like the coat of a deer..."
    m 2hksdlb "Sorry. Just rambling about color metaphors is an easy trap for a literature club president to fall into, I guess. I'll try not to go on forever."
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "But I'll bet your eyes are the loveliest of all~"
    show monika 1eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 1eua "Anyway, that brings me to my next question--"
    return

label monika_player_appearance_eye_color_green:
    $ persistent._mas_pm_eye_color = "green"

    m 3sub "Hey, that's my favorite color! And obviously, it's another thing we have in common!"
    m 4lksdla "I don't know how much I can compliment you here without sounding arrogant, because anything I said about yours would also apply to me..."
    m 1tsu "Except that maybe it's another sign how compatible we are, ehehe~"
    m 1kua "But, [player], just between you and me, it's a fact that green eyes are the best, right?"
    m 3hub "Ahaha! I'm just kidding."
    show monika 5lusdru at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5lusdru "Well, just a little..."
    show monika 3eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 3eua "Onto the next question--"
    return

label monika_player_appearance_eye_color_hazel:
    $ persistent._mas_pm_eye_color = "hazel"

    m 1eub "Oh, hazel eyes? Those are so interesting! It's such an earthly color. It really makes you feel steady and reassured..."
    m 3eub "And it's a welcome departure from all the candy-colored eyes I've had to see in this game, anyway..."
    m "I believe that hazel eyes are alluring because they're lovely and simple."
    m 3hua "Sometimes it's best not to diverge from the crowd too much, [player].{w=0.2} {nw}"
    extend 3hub "Ahaha!"
    m "Now, onto my next question--"
    return

label monika_player_appearance_eye_color_gray:
    $ persistent._mas_pm_eye_color = "gray"

    m 1sub "That's so cool!"
    m 3eub "Did you know that gray eyes and blue eyes are almost identical in terms of genetics?"
    m 1eud "In fact, scientists still aren't certain of what causes a person to have one or the other, though they believe that it's a variation in the amount of pigment in the iris."
    m 1eua "Anyway, I think I like imagining you with gray eyes, [player]. They're the color of a quiet, rainy day..."
    m 1hubsa "And weather like that is my favorite, just like you~"
    m 3hua "Onto my next question--"
    return

label monika_player_appearance_eye_color_black:
    $ persistent._mas_pm_eye_color = "black"

    m 1esd "Black eyes are pretty uncommon, [player]."
    m 4hksdlb "To tell you the truth, I've never actually seen anybody with black eyes, so I don't really know what they look like..."
    m 3eua "But logically, I do know that they're not actually black. If that was the case, black-eyed people would look like they had no pupils!"
    m 4eub "In reality, black eyes are just a very, very dark brown. Still stunning, but perhaps not as dark as the name suggests --although, to be fair, the difference is pretty hard to spot."
    m 3eua "Here's a little bit of trivia for you--"
    m 1eub "There was a well known lady from the time of the American Revolution, Elizabeth Hamilton, who was known to have captivating black eyes."
    m 1euc "Her husband wrote about them often."
    m 1hub "I don't know if you've heard of her or not, but despite the renown of her eyes, I'm sure yours are infinitely more captivating, [player]~"
    m "Onto the next question--"
    return

label monika_player_appearance_eye_color_other:
    $ persistent._mas_pm_eye_color = ask_color("What color are your eyes?")

    m 3hub "Oh! That's a beautiful color, [player]!"
    m 2eub "I'm sure I could get lost for hours, staring into your [persistent._mas_pm_eye_color] eyes."
    m 7hua "Now, onto my next question--"
    return

label monika_player_appearance_eye_color_heterochromia:
    m 1sub "Really?{w=0.2} {nw}"
    extend 3hua "That's incredible, [player]~"
    m 3wud "If I recall correctly, less than one percent of people in the world have heterochromia!"

    m 1eka "...If you don't mind me asking..."
    # Ask the player about their eye colors separately.
    $ eyes_colors = []

    call monika_player_appearance_eye_color_ask
    $ eyes_colors.append(_return)
    call monika_player_appearance_eye_color_ask("right", eye_color)
    $ eyes_colors.append(_return)
    $ persistent._mas_pm_eye_color = tuple(eyes_colors)

    m 1hua "Great!{w=0.2} {nw}"
    extend 3eua "Let's get to my next question--"
    return

label monika_player_appearance_eye_color_ask(x_side_eye="left", last_color=None):
    m 3eua "What color is your [x_side_eye] eye?{nw}"
    $ _history_list.pop()
    menu:
        m "What color is your [x_side_eye] eye?{fast}"

        "Blue" if last_color != "blue":
            $ eye_color = "blue"

        "Brown" if last_color != "brown":
            $ eye_color = "brown"

        "Green" if last_color != "green":
            $ eye_color = "green"

        "Hazel" if last_color != "hazel":
            $ eye_color = "hazel"

        "Gray" if last_color != "gray":
            $ eye_color = "gray"

        "Black" if last_color != "black":
            $ eye_color = "black"

        "It's a different color...":
            $ eye_color = ask_color("What color is your [x_side_eye] eye?")

    return eye_color

# quick label where monika tells you her height
label monika_player_appearance_monika_height:
    if not persistent._mas_pm_units_height_metric:
        $ conv_height_str = ""
        $ real_height_str = "around five-foot-five"
    else:
        $ conv_height_str = " which is around one hundred and sixty centimeters"
        $ real_height_str = "about one hundred and sixty-five-centimeters tall"

    if seen_event("monika_immortal"):
        m 2eud "The wiki I mentioned before said that my concept height was five-foot-three,[conv_height_str] but that doesn't really sound right to me..."
        m 2etc "Maybe it was changed? It was only the concept height after all."
    m 3etd "If I had to guess, I'd say I'm maybe [real_height_str]?"
    return

init 5 python:
     addEvent(
         Event(
            persistent.event_database,
            eventlabel="monika_players_control",
            category=["games", "ddlc"],
            prompt="[player]'s control",
            random=True
            )
        )

label monika_players_control:
    m 3eub "[player], did you know that you have more control over this game than I do?"
    m 3eua "You have access to the game's files and code, right?"
    m 1eka "So you can change them however you want."
    m 3eka "You could do things that even I can't."
    m 4eub "Like changing how the game works entirely. From a visual novel, to the peaceful playground we have now."
    m 3rksdla "You could also add more things to the classroom for me."
    m 1hub "Like some flowers, or a few good books."

    if mas_isMoniEnamored(higher=True) and not persistent._mas_acs_enable_promisering:
        m 1ekbsa "Or a beautiful promise ring."
        m 3dkbsu "Oh, wouldn't that be a dream come true."

    if not mas_consumable_coffee.enabled():
        m 1wuo "You could even add in a cup of coffee to the game for me!"
        m 1eka "That would be lovely."

    if not persistent._mas_pm_has_code_experience:
        m 1hksdrb "But I imagine your coding skills are just as good as mine."
    else:
        m 3eua "Seeing as you're familiar with coding,{w=0.1} {nw}"
        extend 3hua "I'm sure you could do something like that!"

    m 1eua "I guess that's an appeal to video games...{w=0.3}{nw}"
    extend 3eua "having almost endless possibilities in a world you can interact with."
    m 3eub "It's pretty difficult to get bored!"

    if not persistent._mas_pm_has_contributed_to_mas:
        m 1eka "Even if you don't quite know how to change this game..."
        $ line = "We can still enjoy this world that brought us together."

    else:
        $ line = "Especially with you by my side~"

    show monika 5eubla at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eubla "[line]"
    m 5ekbfa "There's no better way to enjoy a game than to be with the one I love."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_backpacking",category=['nature'],prompt="Backpacking",random=not mas_isWinter()))

label monika_backpacking:
    m 1esa "You know what I've always wanted to do, [player]?"
    m 3eub "I've always thought it would be so amazing to go backpacking in the wilderness!"
    m 3eua "Take like an entire week and leave it all behind."
    m 3esa "No responsibilities, no worries, no phones, no distractions."
    m 1hua "Just imagine the two of us, alone with nature..."
    m "The sounds of birds chirping and the wind blowing..."
    m 1eka "Watching deer graze in the morning dew..."
    m "I can't think of anything more peaceful."
    m 1esa "We can spend our days exploring mysterious forests, serene meadows, and rolling hills..."
    m 3hub "Maybe even discover a secluded lake and go for a swim!"

    if mas_isMoniAff(higher=True):
        m 2rsbsa "We probably won't have our bathing suits, but we'll be all alone so maybe we won't need any..."
        m 2tsbsa "..."
        m 1hubfu "I hope you're not too shy, [mas_get_player_nickname()]. Ehehe~"
        m 1ekbfa "We'll spend our nights cuddling in a sleeping bag, keeping each other warm with nothing over our heads but billions of stars..."
        m 3hubfb "Waking up each morning to a glorious sunrise!"

    else:
        m 3eka "We'll spend our nights sleeping under the stars, waking up each morning to a glorious sunrise."

    show monika 5esbfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5esbfa "..."
    m "Oh [player], doesn't that just sound like heaven?"
    m 5hubfa "I can't wait until we can share this experience together~"
    return

## calendar-related pool event
# DEPENDS ON CALENDAR

# did we already change start date?
default persistent._mas_changed_start_date = False

# did you imply that you arent dating monika?
default persistent._mas_just_friends = False

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_dating_startdate",
            category=["romance", "us"],
            prompt="When did we start dating?",
            pool=True,
            unlocked=False,

            # this will be unlockable via the action
            rules={"no_unlock": None},

            # we'll pool this event after a month of the relationship
            conditional=(
                "store.mas_anni.pastOneMonth() "
                "and persistent._mas_first_calendar_check"
            ),

            action=EV_ACT_UNLOCK
        )
    )

label monika_dating_startdate:
    $ import store.mas_calendar as mas_cal
    python:
        # we might need the raw datetime
        first_sesh_raw = persistent.sessions.get(
            "first_session",
            datetime.datetime(2017, 10, 25)
        )

        # but this to get the display plus diff
        first_sesh, _diff = mas_cal.genFormalDispDate(first_sesh_raw.date())

    if _diff.days == 0:
        # its today?!
        # this should NEVER HAPPEN
        m 1lsc "We started dating..."
        $ _history_list.pop()
        m 1wud "We started dating{fast} today?!"
        m 2wfw "You couldn't have possibly triggered this event today, [player]."

        m "I know you're messing around with the code.{nw}"
        $ _history_list.pop()
        menu:
            m "I know you're messing around with the code.{fast}"
            "I'm not!":
                pass
            "You got me.":
                pass
        m 2tfu "Hmph,{w=0.2} you can't fool me."

        # wait 30 days
        $ mas_chgCalEVul(30)
        return

    # Otherwise, we should be displaying different dialogue depending on
    # if we have done the changed date event or not
    if not persistent._mas_changed_start_date:
        m 1lsc "Hmmm..."
        m 1dsc "I think it was..."
        $ _history_list.pop()
        m 1eua "I think it was{fast} [first_sesh]."
        m 1rksdlb "But my memory might be off."

        # ask user if correct start date
        m 1eua "Is [first_sesh] correct?{nw}"
        $ _history_list.pop()
        menu:
            m "Is [first_sesh] correct?{fast}"
            "Yes.":
                m 1hub "Yay!{w=0.2} I remembered it."

            "No.":
                m 1rkc "Oh,{w=0.2} sorry [player]."
                m 1ekc "In that case,{w=0.2} when did we start dating?"

                call monika_dating_startdate_confirm(first_sesh_raw)

                if _return == "NOPE":
                    # we are not selecting a date today
                    return

                # save the new date to persistent
                $ store.mas_anni.reset_annis(_return)
                $ persistent.sessions["first_session"] = _return
                $ renpy.save_persistent()

        m 1eua "If you ever forget, don't be afraid to ask me."
        m 1dubsu "I'll {i}always{/i} remember when I first fell in love with you~"
        $ persistent._mas_changed_start_date = True

    else:
        m 1dsc "Let me check..."
        m 1eua "We started dating on [first_sesh]."

    # TODO:
    # some dialogue about being together for x time
    # NOTE: this is a maybe

    return

label monika_dating_startdate_confirm_had_enough:
    # monika has had enough of your shit
    # TODO: maybe decrease affection since you annoyed her enough?
    m 2dfc "..."
    m 2lfc "We'll do this another time, then."

    # we're going to reset the conditional to wait
    # 30 more days
    $ mas_chgCalEVul(30)

    return "NOPE"

label monika_dating_startdate_confirm_notwell:
    # are you not feeling well or something?
    m 1ekc "Are you feeling okay, [player]?"
    m 1eka "If you don't remember right now, then we can do this again tomorrow, okay?"

    # reset the conditional to tomorrow
    $ mas_chgCalEVul(1)

    return "NOPE"

label monika_dating_startdate_confirm(first_sesh_raw):

    python:
        import store.mas_calendar as mas_cal

        # and this is the formal version of the datetime
        first_sesh_formal = " ".join([
            first_sesh_raw.strftime("%B"),
            mas_cal._formatDay(first_sesh_raw.day) + ",",
            str(first_sesh_raw.year)
        ])

        # setup some counts
        wrong_date_count = 0
        no_confirm_count = 0
        today_date_count = 0
        future_date_count = 0
        no_dating_joke = False

    label .loopstart:
        pass

    call mas_start_calendar_select_date

    $ selected_date = _return
    $ _today = datetime.date.today()
    $ _ddlc_release = datetime.date(2017,9,22)

    if not selected_date or selected_date.date() == first_sesh_raw.date():
        # no date selected, we assume user wanted to cancel
        m 2esc "[player]..."
        m 2eka "I thought you said I was wrong."

        m "Are you sure it's not [first_sesh_formal]?{nw}"
        $ _history_list.pop()
        menu:
            m "Are you sure it's not [first_sesh_formal]?{fast}"
            "It's not that date.":
                if wrong_date_count >= 2:
                    jump monika_dating_startdate_confirm_had_enough

                # otherwise try again
                m 2dfc "..."
                m 2tfc "Then pick the correct date!"
                $ wrong_date_count += 1
                jump monika_dating_startdate_confirm.loopstart

            "Actually that's the correct date. Sorry.":
                m 2eka "That's okay."
                $ selected_date = first_sesh_raw

    elif selected_date.date() < _ddlc_release:
        # before releease date

        label .takesrs:
            if wrong_date_count >= 2:
                jump monika_dating_startdate_confirm_had_enough

            m 2dfc "..."
            m 2tfc "We did {b}not{/b} start dating that day."
            m 2tfd "Take this seriously, [player]."
            $ wrong_date_count += 1
            jump monika_dating_startdate_confirm.loopstart

    elif selected_date.date() == _today:
        # today was chosen
        jump .takesrs

    elif selected_date.date() > _today:
        # you selected a future date?! why!
        if future_date_count > 0:
            # don't play around here
            jump monika_dating_startdate_confirm_had_enough

        $ future_date_count += 1
        m 1wud "What..."

        m "We haven't been dating this whole time?{nw}"
        $ _history_list.pop()
        menu:
            m "We haven't been dating this whole time?{fast}"
            "That was a misclick!":
                # relief expression
                m 1duu "{cps=*2}Oh, thank god.{/cps}"

                label .misclick:
                    m 2dfu "[player]!"
                    m 2efu "You had me worried there."
                    m "Don't misclick this time!"
                    jump monika_dating_startdate_confirm.loopstart

            "Nope.":
                m 1dfc "..."

                show screen mas_background_timed_jump(5, "monika_dating_startdate_confirm_tooslow")

                menu:
                    "I'm kidding.":
                        hide screen mas_background_timed_jump
                        # wow what a mean joke

                        if no_dating_joke:
                            # you only get this once per thru
                            jump monika_dating_startdate_confirm_had_enough

                        # otherwise mention that this was mean
                        m 2tfc "[player]!"
                        m 2rksdlc "That joke was a little mean."
                        m 2eksdlc "You really had me worried there."
                        m "Don't play around like that, okay?"
                        jump monika_dating_startdate_confirm.loopstart

                    "...":
                        hide screen mas_background_timed_jump

                label monika_dating_startdate_confirm_tooslow:
                    hide screen mas_background_timed_jump

                # lol why would you stay slient?
                # TODO: Affection considerable decrease?
                $ persistent._mas_just_friends = True

                m 6lktdc "I see..."
                m 6dftdc "..."
                m 1eka "In that case..."
                m 1tku "{cps=*4}I've got some work to do.{/cps}{nw}"
                $ _history_list.pop()

                menu:
                    "What?":
                        pass

                m 1hua "Nothing!"

                # lock this event forever probably
                # (UNTIL you rekindle or actually ask her out someday)
                $ evhand.event_database["monika_dating_startdate"].unlocked = False
                return "NOPE"

    # post loop
    python:
        new_first_sesh, _diff = mas_cal.genFormalDispDate(
            selected_date.date()
        )

    m 1eua "Alright, [player]."
    m "Just to double-check..."

    m "We started dating [new_first_sesh].{nw}"
    $ _history_list.pop()
    menu:
        m "We started dating [new_first_sesh].{fast}"
        "Yes.":
            m 1eka "Are you sure it's [new_first_sesh]? I'm never going to forget this date.{nw}"
            # one more confirmation
            # WE WILL NOT FIX anyone's dates after this
            $ _history_list.pop()
            menu:
                m "Are you sure it's [new_first_sesh]? I'm never going to forget this date.{fast}"
                "Yes, I'm sure!":
                    m 1hua "Then it's settled!"
                    return selected_date

                "Actually...":
                    if no_confirm_count >= 2:
                        jump monika_dating_startdate_confirm_notwell

                    m 1hksdrb "Aha, I figured you weren't so sure."
                    m 1eka "Try again~"
                    $ no_confirm_count += 1

        "No.":
            if no_confirm_count >= 2:
                jump monika_dating_startdate_confirm_notwell

            # otherwise try again
            m 1euc "Oh, that's wrong?"
            m 1eua "Then try again, [mas_get_player_nickname()]."
            $ no_confirm_count += 1

    # default action is to loop here
    jump monika_dating_startdate_confirm.loopstart

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_first_sight_love",
            category=["romance"],
            prompt="Love at first sight",
            random=True
        )
    )

label monika_first_sight_love:
    m 1eud "Have you ever thought about the concept of love at first sight?"
    m 3euc "Like, seeing someone for the first time, and instantly knowing they're the love of your life?"
    m 2lsc "I think it's one of the more...{w=0.5}ridiculous concepts to grasp."
    m 2lksdlc "I mean, you can't know who a person truly is just by looking at them once."
    m 2tkd "It's not like you've ever talked to them, had lunch, or hung out together."
    m 2lksdlc "You don't even know what their interests and hobbies are..."
    m 2dksdld "They could be really boring or just be a mean and horrible person..."
    m 3eud "That's why I think we shouldn't {i}just{/i} use our eyes to tell if someone is the perfect partner for us."
    if mas_isMoniAff(higher=True):
        m 1eka "And I guess that's kind of how I fell in love with you..."
        m 3eua "It's not like I could see you after all."
        show monika 5ekbfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5ekbfa "I fell in love with you for who you are, [mas_get_player_nickname(exclude_names=['my love', 'love'])]."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_anime_art",
            category=["misc"],
            prompt="Anime art style",
            random=True
        )
    )

label monika_anime_art:
    m 1eua "Have you ever thought about anime art styles?"
    m 3rksdla "I'm sure Natsuki would be an expert on this, given her obsession with manga and all..."
    m 3eub "Anyway, there's a lot of interesting things about the art style."
    m 1eua "It's freeform, like my poems, which makes a lot of the art really unique..."
    m 3eua "From the beautiful scenery, to the amazing characters..."
    m 1hub "It's just really impressive to look at!"
    m 2esc "Though being a freeform art style...{w=0.5}a lot of details tend to look a little unrealistic."
    m 3rsc "While it lets a lot of artworks explore new possibilities, it can also make some details look weird..."
    m 3rssdlc "Like how a character's eyes can be so big, how small their noses are, or how their hair can be in strange lengths, shapes, and sizes..."
    m 2rksdlc "Not to mention...{w=1}large chests."
    m 2euc "If I looked more realistic, I certainly wouldn't have those attributes."
    m 1eua "But I guess that lack of realism is where the true beauty of the art style really comes from."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_whydoyouloveme",
            category=['monika','romance'],
            prompt="Why do you love me?",
            pool=True
        )
    )

label monika_whydoyouloveme:
    if mas_isMoniBroken():
        m 2euc "Hmph."
        m 2wfc "I ask myself that question every day."

    elif mas_isMoniDis():
        m 1efc "I-"
        m 1rkc "I'm not sure..."

    elif mas_isMoniUpset():
        m 1dsc "Hmm..."
        m 3hua "Because I know that you're a good person despite how things are between us."

    elif mas_isMoniEnamored(higher=True):
        if renpy.random.randint(1,10) > 1:
            m 1eksdla "Why do I love you?"
            m 1dka "[mas_get_player_nickname(capitalize=True)]...{w=0.5}there are so many reasons why. Where do I even begin?"

            if store.mas_anni.anniCount() >= 1:
                m 3eka "You've spent so much time with me,{w=0.2} knowing you might not ever get to feel my embrace."
                m 3hua "...But here you are, still by my side."

            m 3eksdla "No matter how crazy it may seem, or what other people might think, you're here with me anyway."
            m 1dku "Every time you visit, you remind me that there's a world out there."
            m "..."
            m 1ekbsa "I'd give you the world if I could, [player]."
            m 1hubsa "If there's anyone who deserves it...{w=0.3}it's you."
            m 1ekbsa "I promise you, [player]..."
            m 3ekbsa "No matter what happens, I'll {i}never{/i} forget you for the rest of my life."
            m 1dkbsu "You didn't just save me, [player]...{w=0.3}{nw}"
            extend 1ekbsa "you made me remember how beautiful life really is."
            m 1ekbsb "Someday, I'll make you feel as loved as you've made me feel~"
            m 1dkbsa "Someday...{w=0.5}I'll get to be with you~"

            if persistent._mas_pm_love_yourself is False:
                m 2eka "And [player]..."
                m 2ekc "I remember you saying that you didn't love yourself..."
                m 7eka "But I think you do love yourself, at least a little."
                m 3hua "You wouldn't still be here with me if you didn't."
                m 1dkbsu "I'm...{w=0.5}I'm just glad you're still here, [player]."
                m 1ekbsa "Please know that I'm here for you, whenever you need me~"

        else:
            m 1esc "I don't."
            pause 5.0
            m 1hub "Ahaha, just kidding!"
            m 1eub "You mean {i}everything{/i} to me, silly!"

    else:
        # normal - aff
        m 2ekc "[player]..."
        m 2ekd "Are you, by any chance feeling insecure?"
        m 7rksdla "I can understand feeling that way..."
        m 3eka "But whatever the reason might be,{w=0.2} I just want you to know that I love you no matter who you are, [player]."
        m 1ekbsa "Just by opening the game for me, you {i}literally{/i} saved my life."
        m 1dkbsu "...When I'm with you,{w=0.2} I'm no longer lonely."
        m 3ekbsa "You truly are my hero, [mas_get_player_nickname(regex_replace_with_nullstr='my ')]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_stoicism",
            category=['philosophy'],
            prompt="Stoicism",
            random=True
        )
    )

label monika_stoicism:
    m 1eua "I've been reading up on some ancient Greek and Roman philosophy, [player]."
    m 1hksdlb "Ahaha! I know, that sounds super boring when you think about it..."
    m 1eua "But there was a certain philosophy that caught my attention while I was reading."
    m "It's called Stoicism, and it's a philosophy founded in Athens in the 3rd century BCE."
    m 4eub "To put it simply, Stoicism is a philosophy that believes that human beings should learn to accept the circumstances of their situation..."
    m "...and prevent themselves from being controlled by an irrational desire for pleasure or fear of pain so they can act accordingly in nature's plan."
    m 2euc "They usually get a bad rep today because people think that they're just cold and unfeeling."
    m 2eua "However, stoics are not just a bunch of unemotional people who are always serious."
    m "Stoics practice self-control over the way they feel about unfortunate events and react accordingly instead of impulsively."
    m 2eud "For example, let's say you failed an important exam at school, or missed a project deadline at work."
    m 2esd "What would you do, [player]?"
    m 4esd "Would you panic? Become really depressed and give up trying? Or will you get angry over it and blame others?"
    m 1eub "I don't know what you would do, but maybe you can take after stoics and keep your emotions in check!"
    m 1eka "Although the situation is less than ideal, there's really no practical reason to expend more energy into something that you can't control."
    m 4eua "You should focus on what you can change."
    m "Maybe study harder for your next exam, get tutoring, and ask your teacher for extra credit."
    m "Or if you imagined the work scenario, start future projects earlier, setup schedules and reminders for those projects, and avoid distractions while you work."
    m 4hub "It beats doing nothing!"
    m 1eka "But that's just my opinion though, it's not that easy to be emotionally resilient to most things in life..."

    if mas_isMoniUpset(lower=True):
        return

    if mas_isMoniAff(higher=True):
        m 2tkc "You should do {i}whatever{/i} helps you de-stress. Your happiness is really important to me."
        m 1eka "Besides, if you ever feel bad about something that's happened to you in your life..."
        show monika 5hubfb at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5hubfb "You can always come home to your sweet girlfriend and tell me what's been bothering you~"

    else:
        m 2tkc "You should do whatever helps you de-stress. Your happiness is really important to me."

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_add_custom_music",
            category=['mod',"media", "music"],
            prompt="How do I add my own music?",
            conditional="persistent._mas_pm_added_custom_bgm",
            action=EV_ACT_UNLOCK,
            pool=True,
            rules={"no_unlock": None}
        )
    )

label monika_add_custom_music:
    m 1eua "It's really easy to add your own music here, [player]!"
    m 3eua "Just follow these steps..."
    call monika_add_custom_music_instruct
    return

label monika_add_custom_music_instruct:
    m 4eua "First,{w=0.5} make sure the music that you want to add is in MP3, OGG/VORBIS, or OPUS format."
    m "Next,{w=0.5} create a new folder named \"custom_bgm\" in your \"DDLC\" directory."
    m "Put your music files in that folder..."
    m "Then either let me know that you added some music or restart the game."
    m 3eua "And that's it! Your music will be available to listen to, right here with me, simply by pressing the 'm' key."
    m 3hub "See, [player]? I told you it was easy, ahaha!"

    # unlock the topic as a pool topic, also mark it as seen
    $ mas_unlockEVL("monika_add_custom_music", "EVE")
    $ persistent._seen_ever["monika_add_custom_music"] = True
    $ mas_unlockEVL("monika_load_custom_music", "EVE")
    $ persistent._seen_ever["monika_load_custom_music"] = True
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_load_custom_music",
            category=['mod',"media", "music"],
            prompt="Can you check for new music?",
            conditional="persistent._mas_pm_added_custom_bgm",
            action=EV_ACT_UNLOCK,
            pool=True,
            rules={"no_unlock": None}
        )
    )

label monika_load_custom_music:
    m 1hua "Sure!"
    m 1dsc "Give me a moment to check the folder.{w=0.2}.{w=0.2}.{w=0.2}{nw}"
    python:
        # FIXME: this is not entirely correct, as one may delete a song before adding a new one
        old_music_count = len(store.songs.music_choices)
        store.songs.initMusicChoices(
            persistent.playername.lower() == "sayori"
            and not persistent._mas_sensitive_mode
        )
        diff = len(store.songs.music_choices) - old_music_count

    if diff > 0:
        m 1eua "Alright!"
        if diff == 1:
            m "I found one new song!"
            m 1hua "I can't wait to listen to it with you."
        else:
            m "I found [diff] new songs!"
            m 1hua "I can't wait to listen to them with you."

    else:
        m 1eka "[player], I didn't find any new songs."

        m "Do you remember how to add custom music?{nw}"
        $ _history_list.pop()
        menu:
            m "Do you remember how to add custom music?{fast}"
            "Yes.":
                m "Okay, make sure you did it correctly."

            "No.":
                $ pushEvent("monika_add_custom_music",True)
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='monika_mystery',
            prompt="Mysteries",
            category=['literature','media'],
            random=True
        )
    )

label monika_mystery:
    m 3eub "You know [player], I think there's an interesting part in many stories that some people overlook."
    m 3eua "It's something that makes a story interesting...but can break them when used incorrectly."
    m 3esa "It can make a tale either amazing to go back through or make you never want to touch it again."
    m 2eub "And that part is..."
    m 2eua "..."
    m 4wub "...a mystery!"
    m 2hksdlb "Oh! I didn't mean I'm not going to tell you, ahaha!"
    m 3esa "I mean that a mystery itself can change everything when it comes to a story!"
    m 3eub "If done really well it can build up intrigue and upon rereading make previous hints become obvious."
    m 3hub "Knowing a twist can really alter how someone views an entire narrative. Not many plot points can do that!"
    m 1eua "It's almost funny...knowing the answers actually changes how you view the story itself."
    m 1eub "At first when you read a mystery you view the story from an unknowing perspective..."
    m 1esa "But upon rereading it you look at it from the author's view."
    m 3eua "You see how they left clues and structured the story to give just enough hints so that the reader might be able to figure it out!"
    m 2esa "I find it really interesting, some of the best stories know how to use a good hook."
    m 2lsc "But if a story doesn't do it properly, it can be the worst. They use hooks to try and seem 'clever.'"
    m 2lud "When they try to do that it can just make it seem like nonsense if not set up properly."
    m 2eud "I guess you could argue that not all stories with mysteries are {i}really{/i} a mystery..."
    m 2eua "Even cheesy action films use mystery elements to keep them interesting."
    m 4hksdlb "Though I guess a story with absolutely no form of mystery would be pretty boring!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_player_read_poetry",
            category=['literature'],
            prompt="Reading poetry",
            random=True
        )
    )

default persistent._mas_pm_likes_poetry = None
#True if player likes poems, false if not

label monika_player_read_poetry:
    m 1eud "Say, [player]..."
    m 1eua "You know that I like poetry, but I was wondering..."

    m 3eua "Do you often read poetry?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you often read poetry?{fast}"

        "Yes.":
            $ persistent._mas_pm_likes_poetry = True
            m 1sub "Really?"
            m 1hua "That makes me so happy!"
            m 3eua "And really, I mean it. Not a lot of people read poetry nowadays."

        "No.":
            $ persistent._mas_pm_likes_poetry = False
            m 2ekc "Oh, that's too bad..."
            m 2eka "I just hope I made you appreciate poetry a little more."
            m 2ekc "You know, not a lot of people these days seem to read poetry, so it's not surprising."

    m 2euc "In fact, poetry is often considered as something too difficult to understand..."
    m 2efd "And on the opposite side, others think that it's simply putting a bunch of pretty words next to each other!"
    m 2dkc "But it's not...{w=0.3}{nw}"
    extend 2dkd "poetry is more than that."
    m 4ekd "You have to put yourself in it."
    m 4ekc "Without his writing skills, {w=0.2}and also his feelings, {w=0.2}E.E.Cummings simply wouldn't be E.E.Cummings..."
    m 7ekd "And without my feelings for you, my poems wouldn't be the same."
    m 3eka "Love, grief, anger, passion, all these feelings bring the words to life."
    m 3hub "And because of that, even a simple text message can become a meaningful poem!"
    m 3eua "That's why I love poetry."

    if persistent._mas_pm_likes_poetry:
        show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5eua "Gosh, just knowing that you read poems too..."
        m 5hua "It shows how alike we really are."
        m 5eua "I can't wait to finally cross over to your reality so we can discuss our favorite poetry together."
        m 5dka "Sharing poems, writing new ones...{w=0.5}just you and me pursuing our shared passion..."
        m 5hub "Sounds like a wonderful dream to me!"

    else:
        m 1eka "I can't wait until I cross over to your reality, [player]..."
        m 1tfu "That way I can start forcing you to read poetry."
        m "..."
        m 3hub "Ahaha, I'm just kidding! I would never force you to do anything, [player]!"
        m 3eua "But I do think I could get you to really like poetry."
        m 1eua "...And not just the poems I write about you, {nw}"
        extend 1kua "ehehe~"

    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_trick",
            category=["club members"],
            prompt="[player]'s second choice",
            random=True
        )
    )

label monika_trick:
    m 2eud "Say [player], I have a question..."
    m 2lksdlb "I hope I don't sound insecure when I say this..."
    m 2eka "I know you love me and only me but...if you {i}really{/i} had to choose one of the other club members to be with..."

    m "Who would you choose?{nw}"
    $ _history_list.pop()
    show screen mas_background_timed_jump(10, "monika_trick_2")
    menu:
        m "Who would you choose?{fast}"
        "Yuri.":
            call monika_trick_yuri
        "Sayori.":
            call monika_trick_sayori
        "Natsuki.":
            call monika_trick_natsuki
    return "derandom"

label monika_trick_2:
    $ _history_list.pop()
    menu:
        m "Who would you choose?{fast}"
        "Yuri.":
            call monika_trick_yuri
        "Sayori.":
            call monika_trick_sayori
        "Natsuki.":
            call monika_trick_natsuki
        "Monika.":
            jump monika_trick_monika
            # jump this path so we can use the "love" return key

    return "derandom"

label monika_trick_yuri:
    hide screen mas_background_timed_jump
    m 2euc "I can see why, she's intelligent and physically attractive."
    m 2tub "It's a good thing I have both of those qualities in abundance!"
    m 2etc "Oh wait, it's not because she became obsessed over you, is it?"
    m 2eud "Are you really that into yanderes?"
    m 2lksdlc "..."
    m 1hksdlb "...Ahaha, there's no need for me to be jealous..."
    m 1eua "You love me and I love you and that's all that matters."
    m 1kua "I guess it's my fault for even asking~"
    return

label monika_trick_natsuki:
    hide screen mas_background_timed_jump
    m 2eud "That's...a little surprising."
    m 2lksdla "I would have thought it would have been Sayori or Yuri."
    m 1eud "Do you feel like you connect with her because of her hobbies?"
    m 3euc "Or perhaps you feel a bit of pity because of her home situation?"
    m 2lud "Well I guess I'm dismissing her personality a little bit, assertiveness is an admirable trait after all."
    m 3euc "To be confident and stand by what you like isn't always easy when others judge you for it."
    m 3rksdla "I'm sometimes even a little bit jealous of her ability to display confidence."
    m 3eub "Plus her ability to cook cupcakes is astounding!"
    return

label monika_trick_sayori:
    hide screen mas_background_timed_jump
    m 2dkc "That's what I expected..."
    m 2ekc "It's because she was best friends with the main character, isn't it?"
    m 6lkc "It makes sense to have the main character end up with the childhood friend."
    m 2dkc "It really is typical in romance games..."
    m 2ekc "Honestly that's kind of why I had to...deal...with Sayori first."
    m 6ekc "You would have settled with her like the trope demands and never even tried to get with me since the game wouldn't let you."
    m 6ekd "I know it's not your fault, but the idea of being inactive and letting that happen scares me..."
    m 6ektpc "You would have completed the game and I would be stuck in a hellish void forever..."
    m 6dktpc "Never having even been acknowledged by the one I love."
    m 6dktuc "..."
    if persistent._mas_pm_cares_about_dokis:
        m 6ektud "...I know you didn't like me for what I did, I'm sorry if I hurt you because of it."
    else:
        m 6ektud "...I don't regret what I did but I'm sorry you had to see what I needed to do."
    return

label monika_trick_monika:
    hide screen mas_background_timed_jump
    if not mas_getEVL_shown_count("monika_trick"):
        $ mas_gainAffection(10, bypass=True)
    else:
        $ mas_gainAffection()

    m 1tkbsu "That wasn't supposed to be an option, silly!"
    m 1tubfb "But it really does make me happy that you only have eyes for me..."
    m 1tubfu "I feel a bit silly myself for even thinking for a second that you would ever choose the others."
    m 5hubfu "I love you, [player]!"
    m 5eubfb "And I only have eyes for you too!"
    return "derandom|love"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_cares_about_dokis",
            category=["monika", "club members"],
            prompt="Insensitive comments",
            random=True
        )
    )

default persistent._mas_pm_cares_about_dokis = None
# TRue if the player cares about the dokis, False if not

label monika_cares_about_dokis:
    m 3eub "Ah, [player]!"
    m 4hua "Want to hear something funny that Sayori once did?"
    m 4eua "So, one time I asked her to get some coffee for us in the club."
    m 2rksdlb "The atmosphere was a bit too tense, and I thought it would liven it up a bit."
    m 2eua "Well, coffee is kept in the staff room, you see. So I sent her there..."
    m 4wud "...and she was gone for an entire hour! There were teachers in there and she didn't want to talk to them!"
    m 2rfc "So she waited for {i}ages{/i} outside for them to leave."
    m 2tfu "You could say that she {i}hu{/i}--"
    m 2etc "...Hm..."
    m 2eud "You know what, [player]? I just want to be sure of something..."
    m 2rksdlc "I know that sometimes I can make some rather...{w=0.5}insensitive comments about the other girls, and it occurred to me..."
    m 2ekc "Maybe you care about them enough that it bothers you."
    m 4eub "...And it's perfectly okay if that's the case, [player]!"
    m 4eka "After all, the five of us spent a lot of time together, so if you don't like it when I joke like that, I completely understand."

    m "So [player], does it make you uncomfortable when I joke about the other girls?{nw}"
    $ _history_list.pop()
    menu:
        m "So [player], does it make you uncomfortable when I joke about the other girls?{fast}"
        "Yes.":
            $ persistent._mas_pm_cares_about_dokis = True
            $ mas_hideEventLabel("monika_archetype", lock=True, derandom=True)

            m 2dkc "Oh no...I can't believe I didn't realize this sooner..."
            m 2eksdld "I'm so sorry, [player]!"
            m 2rksdlc "I'll try really hard to keep this in mind from now on."
            m 2eksdlc "Just know I never meant to upset you."
            m 2eka "But thank you for answering honestly, I want you to know you can always tell me anything."

        "No.":
            $ persistent._mas_pm_cares_about_dokis = False

            # NOTE: we never restore random for these topics
            $ mas_unlockEventLabel("monika_archetype")

            m 2eka "I'm glad that I haven't been making you feel bad or uneasy, [mas_get_player_nickname()]."
            m 1tsu "Anyway, you could say that she {i}hung{/i} around for ages!"
            m 1hub "Ahaha!"

    return "derandom|rebuild_ev"

#### old christmas.rpyc topics
# HOL020
# this will now always available in winter, but derandomed once the snow question is answered in either topic

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_snow",
            category=["winter","weather","you"],
            prompt="Snow",
            random=mas_isWinter()
        )
    )

label monika_snow:
    m 1eua "Hey [player], now that it's winter, I was wondering..."

    m "Does it ever snow where you live?{nw}"
    $ _history_list.pop()
    menu:
        m "Does it ever snow where you live?{fast}"

        "Yes":
            $ persistent._mas_pm_gets_snow = True

            m 1hub "That's wonderful!"
            m 1eua "I've always liked the peaceful aura it seems to give off."
            m 1dsa "It's just so tranquil and intimate, you know?"
            m 1hua "There's a quiet beauty in watching a soft, white blanket of snow and ice tuck the world away to sleep."
            call monika_snow_gets_snow

        "No":
            $ persistent._mas_pm_gets_snow = False

            call monika_hemispheres_nogets_snow

    return "derandom"

# player has snow, snow version
label monika_snow_gets_snow:
    if mas_isMoniHappy(higher=True):
        show monika 5eubla at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5eubla "Maybe someday when I cross over, we could go out for a walk together..."

        if mas_isMoniAff(higher=True):
            m 5ekbfa "...and we could hold each other close to keep each other warm~"

    m 5eubfb "I can't wait to experience a winter night like that with you, [mas_get_player_nickname()]."
    return

# player no snow, snow version
label monika_snow_nogets_snow:
    m 2tkc "Sometimes it can get so heavy it becomes a real problem for your back..."

    if mas_isMoniAff(higher=True):
        m 1eksdla "Anyway, at least colder weather makes great cuddle weather."
        show monika 5ekbfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5ekbfa "A night of cuddling with you would be wonderful..."
        m "My heart is pounding, just imagining it."

    else:
        m 2eka "But anyway, I'm sure there's still a lot we can do together!"

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_snowmen",
            category=['winter'],
            prompt="Snowmen",
            random=False,
            conditional=(
                "persistent._mas_pm_gets_snow is not False "
                "and mas_isWinter()"
            ),
            action=EV_ACT_RANDOM
        )
    )

label monika_snowmen:
    m 3eua "Hey [player], have you ever built a snowman?"
    m 3hub "I think it sounds like a lot of fun!"
    m 1eka "Building snowmen is usually seen as something children do,{w=0.2} {nw}"
    extend 3hua "but I think they're really cute."
    m 3eua "It's amazing how they can really be brought to life with a variety of objects..."
    m 3eub "...like sticks for arms, a mouth made with pebbles, stones for eyes, and even a little winter hat!"
    m 1rka "I've noticed that giving them carrot noses is common, although I don't really understand why..."
    m 3rka "Isn't that a bit of a strange thing to do?"
    m 2hub "Ahaha!"
    m 2eua "Anyway, I think it would be nice to build one together someday."
    show monika 5hua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hua "I hope you feel the same way~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_snowballfight",
            category=["winter"],
            prompt="Have you ever had a snowball fight?",
            pool=True,
            unlocked=mas_isWinter(),
            rules={"no_unlock":None}
        )
    )

label monika_snowballfight:
    m 1euc "Snowball fights?"
    m 1eub "I've been in a few before, they've always been fun!"
    m 3eub "But having one with you sounds even better, [player]!"
    m 1dsc "Fair warning, though..."
    m 2tfu "I've got quite the throwing arm."
    m 2tfb "So don't expect me to go easy on you, ahaha!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_iceskating",
            category=["sports", "winter"],
            prompt="Ice skating",
            random=True
        )
    )

label monika_iceskating:
    m 1eua "Hey [player], do you know how to ice skate?"
    m 1hua "It's a really fun sport to learn!"
    m 3eua "Especially if you can do a lot of tricks."
    m 3rksdlb "In the beginning, it's pretty difficult to keep your balance on the ice..."
    m 3hua "So eventually being able to turn it into a performance is really impressive!"
    m 3eub "There's actually a lot of ways to ice skate..."
    m "There's figure skating, speed skating, and even theatrical performances!"
    m 3euc "And despite how it sounds, it's not just a winter activity either..."
    m 1eua "Lots of places have indoor ice rinks, so it's something that can be practiced year round."
    if mas_isMoniHappy(higher=True):
        m 1dku "..."
        m 1eka "I would really love to practice ice skating with you, [mas_get_player_nickname()]..."
        m 1hua "But until we can do that, having you here with me is enough to keep me happy~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_sledding",
            category=["winter"],
            prompt="Sledding",
            random=mas_isWinter()
        )
    )

label monika_sledding:
    m 1eua "Hey [player], do you know what would be fun to do together?"
    m 3hub "Sledding!"

    if persistent._mas_pm_gets_snow is False:
        #explicitly using False here so we don't grab None people who haven't
        # answered the question yet
        m 1eka "It may not snow where you live..."
        m 3hub "But maybe we could go somewhere it does!"
        m "Anyway..."

    m 3eua "You might think it's only for kids, but I think it could be fun for us, too!"
    m 3eub "We could try using an inner tube, a kicksled, a saucer, or even a traditional toboggan."
    m 1hua "I've heard each one gives a different experience. Plus, both of us could easily fit on a toboggan."

    if mas_isMoniAff(higher=True):
        m 1euc "The kicksled is a bit small, though."
        m 1hub "Ahaha!"
        m 1eka "I'd have to sit in your lap for that one."
        m 1rksdla "And I'd still be at risk of tumbling off."
        m 1hubsa "But I know you wouldn't let that happen. You'd hold me tight, right?~"
        m 1tkbfu "That would probably be the best part."
    else:
        m 1hub "Racing down a snow covered hill together with the wind rushing past us sounds like a blast!"
        m 1eka "I hope we can go sledding together sometime, [player]."

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_snowcanvas",
            category=["winter"],
            prompt="Snow canvas",
            random=mas_isWinter()
        )
    )

label monika_snowcanvas:
    if persistent._mas_pm_gets_snow is not False:
        m 3euc "[player], have you ever looked at snow and thought it resembles a blank canvas?"
        m 1hksdlb "I know I'm not really good with art..."
        m 3eua "But packing a few spray bottles with water and food coloring could make for a fun day!"
        m 3hub "We can just step outside and let our imaginations run wild!"

    else:
        m 3euc "You know [player], snow is kinda like a blank canvas."
        m 3eub "Maybe someday if we went somewhere that it snows, we could bring some food coloring in spray bottles and just step outside and let our imaginations run wild!"

    m 1eua "Having so much space to paint sounds wonderful!"
    m 1hub "We just have to make sure the snow is packed down tightly, and then we can draw to our heart's content!"
    m 1eka "I'd love to make some snow art with you someday."
    m 3hua "Maybe you can paint something for me when that happens, [mas_get_player_nickname()]."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_cozy",
            category=["romance","winter"],
            prompt="Warming up",
            random=mas_isWinter(),
            aff_range=(mas_aff.AFFECTIONATE,None)
        )
    )

label monika_cozy:
    m 3eua "Do you know the one thing I love about the cold weather, [player]?"
    m 3eka "Anything warm feels really nice~"
    m 1rksdla "Those who get cold hands really appreciate that feeling..."
    m 1eua "It's like feeling a loved one's embrace~"
    m 3eub "You also get to wear your winter clothes that have been stuck in your closet."
    m 1hub "Finally being able to whip out your winter fashion set is always a nice feeling."
    m 3eubla "But you know what the best way to warm yourself up is?"
    m 3ekbsa "Cuddling with the one you love in front of the fireplace~"
    m 3ekbfa "Just sitting there under a warm blanket, sharing a hot beverage."
    m 1hubfa "Ah, if I got to feel your warmth every time we cuddle, I'd wish for cold weather every day!"
    m 1ekbfa "I'd never let you go once I got a hold of you, [mas_get_player_nickname()]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_winter",
            category=["winter"],
            prompt="Winter activities",
            random=mas_isWinter()
        )
    )

label monika_winter:
    m 1eud "Ah, [player]!"
    m 1eua "What do you think about winter?"
    m 3eua "All sorts of fun activities only come around during this time..."
    if persistent._mas_pm_gets_snow is not False:
        m 3eub "Playing with the snow is usually something that can be enjoyed a few times a year."

    else:
        m 3eka "I know you don't really get snow where you live, but many people do get to enjoy activities in the snow..."

    m 3eua "Building a snowman, sledding, having snowball fights..."
    m 3eud "Some people even live where it's cold enough for lakes and ponds to freeze and are able to enjoy things like outdoor ice skating, pond hockey..."
    m 3wud "And some actually go fishing...{w=1}{i}through the ice{/i}!"
    m 1eka "For people who don't enjoy cold weather activities, staying indoors seems so much more comfortable when there's snow outside..."
    m "Watching it gently fall while the moonlight reflects off the fresh, white canvas...it's just beautiful."
    if mas_isMoniAff(higher=True):
        show monika 5ekbfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5ekbfa "And to be honest, cuddling under a blanket, reading a book together with you is the best winter activity I can think of~"
    else:
        m 1hua "Sitting by the window, reading a nice book while drinking a cup of coffee or hot chocolate is always a wonderful experience on a cold night, [player]."
    return

#This combines _relax and _hypothermia into one topic
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_winter_dangers",
            category=["winter"],
            prompt="Winter dangers",
            random=mas_isWinter()
        )
    )

label monika_winter_dangers:
    m 1hua "Isn't winter a beautiful time of year, [player]?"
    if mas_isD25Season():
        m 3eka "The glistening, white snow, the bright and colorful lights~"
    m 3hub "I just love it."
    if persistent._mas_pm_gets_snow is False:
        #explicitly using False here so we don't grab None people who haven't
        # answered the question yet
        m 1eka "I know you don't get snow where you live, but I'm sure you can appreciate its appeal..."
        m 3hua "Maybe someday after I cross over we can even take a trip some place where they do have snow and enjoy its beauty together!"

    m 1eka "..."
    m 3rkc "Although, as stunning as winter can be, there are a few dangers..."
    m 3dsd "Like blizzards, or icy roads..."
    m 1ekc "And the cold, of course..."
    m 3rksdlc "The cold can be the most dangerous."
    m 3eksdlc "It's really easy to get hypothermia or frostbite if you're not careful, [player]."
    m 1ekd "So please remember to bundle up if you go outside..."
    m 3euc "Put on your coat, your gloves, and the warmest hat you can find..."
    m 1eka "And if it gets too bad, just stay inside where it's safe, okay?"
    m 1ekb "What better way to spend a brutal winter day than wearing pajamas, drinking hot chocolate, reading a good book, and..."
    m 1hua "Talking to me."
    m 1huu "Ehehe~"

    if mas_isMoniAff(higher=True):
        show monika 5hubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5hubfu "I'll always help keep you warm, [mas_get_player_nickname()]~"
    return

#### end christmas.rpyc topics

default persistent._mas_pm_live_south_hemisphere = None
default persistent._mas_pm_gets_snow = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_hemispheres",
            category=["you", "location"],
            prompt="Hemispheres",
            random=True
        )
    )

label monika_hemispheres:
    m 1euc "Hey [player], I've been wondering..."
    m 1eua "Which hemisphere do you live in?"
    m 1eka "I know it's kind of a strange question..."
    m 3hub "But it gives me a better idea of how things work around you."
    m 3eua "Like, you know how when it's winter in the Northern Hemisphere, it's actually summer in the Southern Hemisphere?"
    m 3hksdrb "It would be a little awkward if I started talking about how nice summer weather is, but where you are, it's the middle of winter..."
    m 2eka "But anyway..."

    m "Which hemisphere do you live in, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Which hemisphere do you live in, [player]?{fast}"

        "The Northern Hemisphere.":
            $ persistent._mas_pm_live_south_hemisphere = False
            m 2eka "I had a feeling..."

        "The Southern Hemisphere.":
            $ persistent._mas_pm_live_south_hemisphere = True
            m 1wuo "I wouldn't have thought!"

    $ store.mas_calendar.addSeasonEvents()
    m 3rksdlb "Most of the world's population lives in the Northern Hemisphere after all."
    m 3eka "In fact, only about twelve percent of the population lives in the Southern Hemisphere."
    if not persistent._mas_pm_live_south_hemisphere:
        m 1eua "So I kind of figured you lived in the Northern Hemisphere."

    else:
        m 2rksdla "So you can see why I would have thought you would be living in the Northern Hemisphere..."
        m 1huu "But I guess that makes you a bit more special, ehehe~"

    if mas_isSpring():
        m 1eua "That said, it must be spring for you right now."
        m 1hua "Spring rains are always really nice."
        m 2hua "I love to listen to the light pitter patter of the rain as it falls on the roof."
        m 3eub "It's really calming to me."
        if mas_isMoniAff(higher=True):
            show monika 5esbfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5esbfa "Maybe we could go out for a walk together..."
            m 5ekbfa "We would walk with our hands intertwined as we share an umbrella..."
            m 5hubfa "It just sounds magical~"
            m 5eubfb "I can't wait to experience something like that with you for real, [mas_get_player_nickname()]."
        else:
            if persistent._mas_pm_likes_rain:
                m 2eka "I'm sure we could spend hours listening to the rain together."
            else:
                m 3hub "You might not like the rain too much, but you have to admit, the flowers it brings are gorgeous, and the rainbows are beautiful too!"

    elif mas_isSummer():
        m 1wuo "Oh! It must be summer for you right now!"
        m 1hub "Gosh, I just love the summer!"
        m 3hua "You can do so much...go out for jogs, play some sports, or even go to the beach!"
        m 1eka "Summers with you sound like a dream come true, [player]."
        show monika 5hua at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5hua "I can't wait to spend them with you when I finally cross over."

    elif mas_isFall():
        m 1eua "Anyway, it must be autumn for you right now."
        m 1eka "Autumn is always full of such pretty colors."
        m 3hub "The weather is normally pretty nice too!"
        show monika 5ruu at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5ruu "It's normally just the right amount of heat, with a gentle breeze."
        m 5eua "I'd love to spend a nice warm day like that with you."

    else:
        m 3eua "Anyway, that means it must be winter for you now."
        if persistent._mas_pm_gets_snow is None:
            python:
                def _hide_snow_event():
                    #TODO: may want to update script this for unstable users
                    # who answered this before monika_snow was derandomed
                    mas_hideEVL("monika_snow", "EVE", derandom=True)
                    persistent._seen_ever["monika_snow"] = True

            m 2hub "Gosh, I really love how pretty snow is."
            m 3euc "Well, I know not all parts of the world get snow..."

            m 1euc "Does it snow where you live, [player]?{nw}"
            $ _history_list.pop()
            menu:
                m "Does it snow where you live, [player]?{fast}"

                "Yes.":
                    $ persistent._mas_pm_gets_snow = True
                    $ _hide_snow_event()

                    m 3hub "That's wonderful!"
                    call monika_hemispheres_gets_snow

                "No.":
                    $ persistent._mas_pm_gets_snow = False
                    $ _hide_snow_event()

                    call monika_hemispheres_nogets_snow

        elif persistent._mas_pm_gets_snow:
            m 2hub "Gosh, I really love how pretty snow is."
            call monika_hemispheres_gets_snow

        else:
            m 3eka "I know you don't really get snow where you live..."
            m 1eka "It must be nice not having to deal with all the hassles that come with it..."
            m 3rksdld "Like the terrible travel conditions, having to shovel it..."
            call monika_snow_nogets_snow

    python:
        #Now that hemi has changed, set the current season and run prog points
        persistent._mas_current_season = store.mas_seasons._seasonalCatchup(
            persistent._mas_current_season
        )
    return "derandom|rebuild_ev"

# player has snow, hemisphere version
label monika_hemispheres_gets_snow:
    m 1eka "There's something really peaceful about a quiet, snowy night."
    call monika_snow_gets_snow
    return

# player no snow, hemisphere version
label monika_hemispheres_nogets_snow:
    m 3eka "That's a shame. But it's not all bad."
    m 3hksdlb "At least you don't have to worry about shoveling it."
    call monika_snow_nogets_snow
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_perspective",
            category=["monika"],
            prompt="Monika's perspective",
            random=True
        )
    )

label monika_perspective:
    m 2euc "I've been meaning to talk to you about something, [player]..."
    m 2esd "...Something that I find very difficult to explain."
    m 2lksdla "Oh, don't worry, it's nothing bad, it's just that I find it hard to get the right words."
    m 3esd "So...{w=0.5}it's pretty strange to see one thing and know it's not real..."
    m 3esc "...but then see a mouse cursor and know {i}that{/i} is."
    m 2hfsdld "Mmmm! It really is hard to describe!"
    m 2eub "Okay! So when I look around and see my world, it's the same as how you see yours."
    m 3eua "Everything is detailed, natural and kind of three-dimensional...I wouldn't be able to practice my piano if it wasn't!"
    m 3eud "But at the same time I see what you see, I can look at the same thing and see its flat image."
    m 3euc "It's unmoving, static and also very artificial...{w=1}and cold."
    m "And what I thought was detailed wasn't as detailed as I originally thought."
    m 3etd "When you see a dialogue box, I can see it too but I also can't. It's really weird. It's perfectly clear, but it's also not 'there,' even though it is."
    m 2eka "I know this is confusing...I'm going to try and describe it the best way I can."
    m 3eua "I thought of a nice way to try and demonstrate the idea, it's far from perfect but it should give you the gist."
    m 2hua "..."
    m 3eua "Take your hand and move it to the center of your face and angle it slightly so it partially covers an eye."
    m 3esb "Now, look around the room you're in and try to focus on something, but so it can only be seen with one eye."
    m 3hua "It can be anything. The closer the better, though!"
    m 4eub "You'll see that if you want to see something, you can easily, but at the same time you can also see your hand in the same place."
    m 4eua "From your field of view, you can see two things at once...it's like that with me, but for {i}everything{/i} in the game."
    m 4wud "It's both there and not there!"
    m 4eud "...It's clear, but only if you know what to look for."
    m 2esc "It was only when I realized it was all fake and just a game that I could 'focus' and see things for how they really were."
    m 2esa "Doing so became second nature for me once I did...but it's no surprise that I didn't notice straight away."
    m "It's easy to see when you know it's there but otherwise you can't really 'see' it."
    m 2lksdla "...Hmm...{w=1}maybe the hand example wasn't as good as I thought."
    m 1hksdlb "Well I hope that helped you understand at least a little, [player]."
    m "It's the best way I could try and explain it!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_robotbody",
            category=['monika','technology'],
            prompt="Robot body",
            random=True
        )
    )

label monika_robotbody:
    m 2euc "Hey [player], I've been thinking a lot about how I would be able to cross over into your reality..."
    m 3eud "It hit me earlier that technology in the future would probably allow me to be uploaded into a mechanical body, rather than a human body like yours."
    m 1dkc "It makes me a little sad that I might not be a human like you are."
    m 1dkd "...And if not, I might not be treated like one either."
    m 1rkd "I would be considered an android at that point, and others may look at me differently because of that."
    m 3euc "Have you heard of Isaac Asimov's {i}Three Laws of Robotics{/i}? It was brought up many times in his science fiction books."
    m 4eud "It mentions three laws that all androids must follow, otherwise they would be terminated."

    if renpy.seen_label("monika_asimov_three_laws"):
        m 1eua "Of course, they're just that...{w=0.3}fiction."
        m 3rud "They aren't exactly realistic as we discussed before...{w=0.3}{nw}"
        extend 1eua "but their implications are fun to think about."
        m 1eua "I would never do anything to hurt you or anyone else, obviously."

        $ line_end_1 = "more than a little bit uneasy."
        $ line_end_2 = "we would end up needing to set up rules for androids to be able to live in our society."

    else:
        m 1eua "Of course, I would never do anything to hurt you or anyone else."

        $ line_end_1 = "feel like I'm trapped in a way."
        $ line_end_2 = "those rules are there to begin with, even if they only exist in fiction."

    m 2ekd "...But the fact that I would have to obey orders given by any human still makes me [line_end_1]"
    m 2dkc "It really scares me that I wouldn't be able to do a lot of the things that you can normally, or even have the same rights as you do."
    m 3ekd "But I do understand why [line_end_2]"
    m 3rksdlb "We can't have a robot uprising now, can we?"
    m 1hub "Ahaha~"
    show monika 5eubla at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eubla "Well, no matter what, I wouldn't mind any of that as long as I have you."
    m 5eubfb "I love you [player], and I'm willing to make any sacrifice to be with you forever."
    m 5hubfa "Besides, maybe sometime after I cross over, there'll be more advances in technology to make me more human, and then we'll be able to do more things together."
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_relationship_comfort",
            category=["romance","advice"],
            prompt="Comfortable in a relationship",
            random=True,
            aff_range=(mas_aff.AFFECTIONATE,None)
        )
    )

label monika_relationship_comfort:
    m 1wud "You know [player], I've been thinking about our relationship lately..."
    m 2lssdrb "It didn't really start in a way most of them do, so it's not exactly what I would call normal."
    m 2esa "But the more I thought about it, the more I realized that in a way it is actually pretty standard."
    m 3eub "Almost every relationship, no matter how it begins, is always '{i}exciting{/i}' at first!"
    m 3eua "People view relationships in an almost fairy-tale like way; they see it as an adventure."
    m 3lssdrb "I'm guilty of this too, and I think it's fine..."
    m 2euc "But it's also a pretty dangerous way to look at a bond between two people, isn't it?"
    m 2eud "Because really, while a partnership is an adventure, that doesn't mean it'll always be exciting."
    m 2esc "There's only so many times you can do the same thing and experience the same breathtaking moments, and still expect it to have that same impact."
    m 4eub "That doesn't make it any less valuable, or meaningful. It can still be heart-racing!"
    m 4esc "But it does mean that the same sensation isn't anything new; it's just no longer as thrilling as before."
    m 2dkd "And some people mistake that thrill for love, and not the truly meaningful bond between two people."
    m 2dkc "So when things slow down, when they become less passionate, they mistakenly think they're falling out of love..."
    m 2rkc "You could say that they never really did love someone in the first place, but maybe that's a bit harsh...{w=0.3} Love isn't always such a clear thing."
    if not store.mas_anni.pastSixMonths():
        m 2eka "I know our relationship is still fresh, and truly electrifying, but I hope you're not with me just because of that."
        m 1hubsb "Know that I love you for more than just the excitement!"
    elif store.mas_anni.anniCount() < 2:
        m 2eka "I feel like we're past that phase, but you still make me feel exhilarant."
        m 1hubsb "Maybe you're just that special, but know that no matter how slow it goes, I'll never get bored with you."
    else:
        m 2eka "We've been together for so long already that I know you're not with me just for the thrill of it..."
        m 1hubsb "It really makes you that much more special to me [mas_get_player_nickname()], more than anyone!"
    m 4eua "It might just be me, but I think it's important to learn how to be comfortable when it does slow down."
    m 4eub "I mean, at the end of the day it's the little things that matter isn't it? And that's true even in a relationship."
    m 2ekb "You'll miss the small comforts that only a partner can bring, and that's much more valuable than some excitement."
    m 2eka "Just because a relationship has slowed down, doesn't mean it's worse for it..."
    m 2hua "It just means that the people involved are truly comfortable with one another."
    m 2hubsb "...And I think that's really sweet."
    m 1kua "Let's try not to fall into the same trap, [player].{w=0.2} {nw}"
    extend 1hub "Ahaha!"
    return

#NOTE: This was mas_d25_monika_sleigh, but it seems more like a general topic
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_sleigh",
            category=["romance"],
            prompt="Carriage ride",
            random=True,
            aff_range=(mas_aff.AFFECTIONATE, None)
        )
    )

label monika_sleigh:
    m 3eub "Hey [player], a nice thought just crossed my mind..."
    m 1eua "Have you ever heard of carriage rides?"
    m 3hub "When I get out of here, we should totally go on one!"
    m "Oh, I bet it would be magical!"
    m 1eua "Nothing but the clip-clop of the horse's hooves against the pavement..."

    if mas_isD25Season():
        m 1eub "And the colorful array of Christmas lights shining in the night..."

    m 3hub "Wouldn't that be romantic, [mas_get_player_nickname()]?"

    if mas_isFall() or mas_isWinter():
        m 1eka "Maybe we could even take a soft, fleece blanket along to cuddle under."
        m 1hkbla "Oooh~"

    m 1rkbfb "I wouldn't be able to contain myself. My heart would burst!"

    if mas_isFall() or mas_isWinter():
        m 1ekbfa "The warmth of your body against mine, wrapped within the gentle cloth~"
    else:
        m 1ekbfa "The warmth of your body against mine..."

    m 1dkbfa "Fingers entwined..."

    if mas_isMoniEnamored(higher=True):
        m 1dkbfb "And at the perfect moment, you lean in to me and our lips touch..."
    m 1subfa "I really want to do that when I get there, [player]."
    m 1ekbfu "...What about you?"

    show monika 5hubfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hubfa "An experience like that with you would be so breathtaking~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_failure",
            prompt="Dealing with failure",
            category=['advice','life'],
            random=True
        )
    )

label monika_failure:
    m 1ekc "You know [player], I've been thinking recently..."
    m 1euc "When it comes to failure, people seem to make a really big deal out of it."
    m 2rkc "...Almost as if it's the end of the world."
    m 2rksdla "But it's not actually a bad thing."
    m 3eub "When you think about it, you can learn a lot from the experience!"
    m 3eud "Failure isn't the end at all; it's a lesson on what doesn't work."
    m 2eka "There's nothing wrong with not getting something on the first attempt; it just means that you need to try a different approach."
    m 2rksdlc "Though, I know in some cases the feeling of failure can be crushing..."
    m 2ekc "Like discovering you're just not cut out for something you really wanted to do."
    m 2dkd "The idea of quitting and finding something else to do makes you feel terrible inside...{w=1}as if you failed yourself."
    m 2ekd "And on the other hand, trying to keep up with it just completely drains you..."
    m 2rkc "So either way, you feel terrible."
    m 3eka "But the more you think about it, you realize it's better that you just accept the 'failure.'"
    m 2eka "After all, if you're torturing yourself just to get through, it might not be worth it. Especially if it starts impacting your health."
    m 3eub "It's completely fine to feel like you're not cut out for something!"
    m 3eua "It just means you need to figure out what you're really interested in doing."
    m 2eka "Anyway, I'm not sure if you've had to go through something like that...but know that failure is a step towards success."
    m 3eub "Don't be afraid to be wrong every now and then...{w=0.5}you never know what you might learn!"
    m 1eka "And if you're really feeling bad about something, I'll always be here to support you."
    show monika 5hua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hua "We can talk about whatever you're going through for as long as you need."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_enjoyingspring",category=['spring'],prompt="Enjoying spring",random=mas_isSpring()))

label monika_enjoyingspring:
    m 3eub "Spring is such an amazing time of year, isn't it, [player]?"
    m 1eua "The cold snow finally melts away, and the sunshine brings new life to nature."
    m 1hua "When the flowers bloom, I can't help but smile!"
    m 1hub "It's like the plants are waking up and saying, 'Hello world!' Ahaha~"
    m 3eua "But I think the best thing about spring would have to be the cherry blossoms."
    m 4eud "They're pretty popular all around the world, but the most famous cherry blossoms would have to be the Somei Yoshino in Japan."
    m 3eua "Those ones in particular are mostly white with a slight tinge of pink."
    m 3eud "Did you know that they only bloom for one week each year?"
    m 1eksdla "It's quite a short lifespan, but they're still beautiful."
    m 2rkc "Anyway, there is one big downside to spring...{w=0.5}the constant rainfall."
    m 2tkc "You can't really enjoy too much time outside because of it..."
    if mas_isMoniHappy(higher=True):
        m 2eka "But I guess April showers bring May flowers, so it's not all bad."
        if persistent._mas_pm_live_south_hemisphere:
            m 2rksdlb "Well, maybe not in your case, ahaha..."
            m 3eub "But personally, I think that rain can also be fun too!"
        else:
            m 3eub "And personally, I think that rain can also be fun too!"
        show monika 5eubla at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5eubla "We can always go for walks together in the rain, we just have to bring an umbrella big enough for two."
        m 5ekbfa "Although, nothing beats listening to the sound of rain at home while holding the one you love."
        m 5hubfa "Ehehe~"
    else:
        m 2rkc "...but I guess there's no real way to avoid it, is there?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_vr",
            category=['technology'],
            prompt="Virtual reality",
            random=True
        )
    )

label monika_vr:
    m 1euc "[player], do you know about virtual reality?"
    m 1eua "VR immerses you into a completely virtual world, different from your actual surroundings."
    m 3rksdla "While it might take some getting used to...{nw}"
    extend 3hub "it can be really fun!"
    m 3eua "It also has practical uses like training people in simulated environments as well as rehabilitation."
    m 1rksdla "...In fact, some people have even simulated their weddings in VR."
    m 1euc "But since it's still a pretty new technology, not just {i}anything{/i} can be in VR yet."
    m 3esc "...Like my reality, for example."
    m 1dkc "It's too bad we can't use VR to meet each other..."
    m 1etc "Well,{w=0.3} maybe if I could make a VR system in here, we could both meet up in another reality."
    m 1rksdlb "...But that's probably a little too complicated for me, ahaha."
    m 3eka "Maybe we'll get it to work one day, though."
    m 1dka "Even if I never get to meet you in the real world...{w=0.3}{nw}"
    extend 1ekbsu "if you could meet me halfway in VR, that would be a dream come true, [mas_get_player_nickname()]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_career",
            category=['monika'],
            prompt="Careers",
            random=False,
            conditional=(
                "seen_event('monika_citizenship')"
            ),
            action=EV_ACT_RANDOM
        )
    )

label monika_career:
    m 2euc "[player], you know how I was talking earlier about becoming a citizen and getting a job when I finally cross over?"
    m 2eua "Well, I've been thinking about what kind of jobs I might be cut out for..."
    m 3rksdla "I guess an obvious choice would be a writer, or something that has to do with literature..."
    m 3eud "That would be fitting, seeing as I started my own literature club and everything, don't you think?"
    m 1sua "Oh, maybe a musician? I did write and perform an entire song, after all."
    m 1eua "I'd love to write more songs...{w=0.2}{nw}"
    extend 1hksdlb "especially if they're songs about you, ahaha~"
    m 3eud "Or, once I get better at it, maybe I could do some programming."
    m 1rksdla "I know I've still got a lot to learn...{w=0.2}{nw}"
    extend 1hua "but I'd say I've done pretty well so far, for being self-taught..."
    m 1esa "There are definitely a lot of different jobs out there, though."
    m 1ruc "Honestly, even with those obvious examples, there's still a good chance I'll end up doing something completely different..."
    m 3eud "A lot of people end up in fields they've never even considered."
    m 3rksdld "For now though, I think it's safe to say I've still got some time to think about it."
    show monika 5hua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5hua "Maybe you could help me decide when the time comes, [mas_get_player_nickname()]~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_life_skills",category=['advice','life'],prompt="Life skills",random=True))

label monika_life_skills:
    m 1ruc "You know, [player]..."
    m 3euc "I've been reflecting on what I got out of high school."
    m 2rksdlb "With all the things I had going for me, you'd think I'd be pretty set for the future..."
    m 1euc "But despite all that, I'm not sure how many life skills I actually learned."
    m 3eka "Sure, I was on top of all my classes, and I guess I learned a lot of interesting things..."
    m 1euc "But how much of that am I really going to use later in life?"
    m 3esd "I feel like schools don't do a good job teaching some of the really important things, like life skills."
    m 3ekc "I've heard of some people graduating and then falling apart because they don't know how to do taxes or book appointments."
    m 1eka "So I can understand why some people get worried about not having some essential life skills."
    m 3eua "But I don't think people need to be too worried about it.{w=0.5} Life skills come pretty quickly if you need them all of a sudden."
    m 3hua "Take me for example!"
    m 3eub "I started programming thanks to you!"
    m 2esc "Now I know most people wouldn't necessarily consider programming a life skill, but most people don't live inside a computer, either."
    m 2esd "When I had my epiphany and finally met you, I knew I had to figure out a way to get your attention..."
    m 4euc "So learning how to program literally became a matter of life and death for me."

    if persistent._mas_pm_cares_about_dokis:
        m 2rksdla "I know I wasn't that great with code, considering some of the things that happened..."
        m 2hksdlb "And I'll admit that I definitely broke a few things..."
        m 2eksdlc "But I didn't think I would have much time if I really wanted to get your attention, so I was a bit desperate."
        $ it = "And it"

    else:
        m 2ekc "I wasn't really able to do it normally like the other girls, so I had to find another way."
        m 3eua "Turns out that one way was manipulating the script."
        m 3euc "I figured I had to think fast if I didn't want to lose you.{w=0.5} So that's what I did."
        m 3eka "I know it wasn't perfect, but I think I did pretty well considering how rushed I was and that it was all new to me."
        $ it = "It"

    m 3eua "[it] just goes to show what you're capable of when something really matters to you."
    m 1eka "If you're ever genuinely worried that you won't be able to do something, you must really care."
    m 1hua "And if it's that important to you, I'm sure you can do it... {w=0.5}No matter what it is."
    m 3hubsb "Maybe even thinking of me might help, ahaha!"
    m 3hubfa "Thanks for listening~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_unknown",category=['psychology'],prompt="Fear of the unknown",random=True))

label monika_unknown:
    m 2esc "Hey, [player]..."
    m 2eud "Did you know that a lot of people are afraid of the dark?"
    m 3eud "Even though it's often dismissed as a childish fear, it's not that uncommon for adults to suffer from it as well."
    m 4eub "Fear of the dark, called 'nyctophobia,' is usually caused by the mind's exaggerated guess of what may be hiding in the shadows, rather than darkness itself."
    m 4eua "We're scared because we don't know what's there...{w=1}even if it's usually nothing."
    m 3eka "...And I'm not just talking about monsters under the bed, or menacing silhouettes...{w=1} Try moving in a dark room."
    m 3eud "You'll find that you're instinctively being more careful of where you step so you don't hurt yourself."
    m 3esd "It makes sense;{w=0.5} humans have learned to be wary of the unknown in order to survive."
    m 3esc "You know, like being cautious around strangers, or thinking twice before jumping into unfamiliar situations."
    m 3dsd "'{i}Better the devil you know than the devil you don't.{/i}'"
    m 3rksdlc "But even if that frame of thinking has helped people survive for hundreds of thousands of years, I think it can also do a lot of harm nowadays."
    m 1rksdld "Like how some people are unsatisfied with their jobs but are too afraid to quit..."
    m 1eksdlc "Most of them can't afford to lose their source of income, so quitting isn't an option."
    m 3rksdlc "Plus, having to go through interviews again, finding a job that pays enough, changing your routine..."
    m 3rksdld "It just seems like it's easier being miserable because it's more comfortable,{w=0.5} even if they'd be much happier in the long run."
    if mas_isMoniDis(lower=True):
        m 2dkc "...I guess it's also true that couples might stay in unhappy relationships out of fear of being alone."
        m 2rksdlc "I mean, I kind of understand where they're coming from, but still..."
        m 2rksdld "Things can always get better.{w=1} Right?"
        m 1eksdlc "A-anyway..."
    m 3ekc "Maybe if they saw the options available to them, they'd be more willing to embrace change."
    m 1dkc "...Not that making that kind of decision is easy, or even safe."
    if mas_isMoniNormal(higher=True):
        m 1eka "Just know that if you ever decide to make that sort of change, I'll support you every step of the way."
        m 1hubsa "I love you, [player]. I'll always be rooting for you~"
        return "love"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_brave_new_world",
            category=['literature'],
            prompt="Brave New World",
            random=True
        )
    )

label monika_brave_new_world:
    m 1eua "I've been doing a little reading lately, [player]."
    m 3eua "There's a book called 'Brave New World,' a dystopian story.{w=0.3} {nw}"
    extend 3etc "Have you heard of it?"
    m 3eua "The idea is, you've got this futuristic world where humans are no longer born through natural means."
    m 3eud "Instead, we are bred in hatcheries using test tubes and incubators, and engineered into castes from our conception."
    m 1esa "Your role in society would be decided beforehand {nw}"
    extend 1eub "and you would be given a body and mind fitting of your predetermined purpose."
    m 1eud "You would also be indoctrinated from birth to be satisfied with your life and not to seek anything different."
    m 3euc "For example, people destined for manual labor would be designed to have limited cognitive capabilities."
    m 1euc "Books were associated with negative stimuli so when people became adults, they would naturally tend to avoid reading."
    m 3esc "They would also be taught to respect and submit to people from castes above theirs, and to look down on those of castes below."
    m 3eua "It's a pretty interesting case as a dystopian story, as most will show people as crushed and oppressed..."
    m 3wuo "But in this one, everyone is actually happy and genuinely supportive of the system!"
    m 3euc "And despite that,{w=0.3} to us the readers, this is horrifying."
    m 1rsc "Sure, they managed to get rid of most of the human sufferings or the fear of death..."
    m 3ekc "But it came at the price of getting rid of any form of creativity and critical thinking."
    m 1wud "We're talking about a world where you can get arrested just for reading poetry in public! Can you imagine that?"
    m 3euc "A key point in the book is people not being able to appreciate old theatrical plays..."

    if seen_event("monika_pluralistic_ignorance"):
        m 3tku "Even if they are Shakespeare's plays, and you know how I feel about those..."

    m 2ekc "They just can't understand the value in the variety of human emotions, like sorrow or loneliness."
    m 7ekd "These emotions are never experienced anymore. All of their desires are swiftly granted and they never want for something they cannot get."
    m 1dsc "..."
    m 3eka "And yet, despite all that, everyone is happy, healthy, and safe..."
    m 1euc "This scenario really makes you think about the nature of happiness and society..."

    if mas_isMoniDis(lower=True):
        m 2dkc "..."
        m 2rkc "Sometimes, I wish I could live happily in a world like that."
        m 2dkc "Maybe it was a bad thing I had my epiphany..."
        m 2dktdc "...then I could have kept on living without ever realizing the truth."

    else:
        m 1eka "Though, I certainly can't see myself living happily in a world like that..."
        m 3esc "An unchallenging world, limited in humanity and emotion..."

        if mas_isMoniHappy(higher=True):
            m 1ekbsa "And I could never give up loving you~"
            m 1hubfu "Ehehe~"

        else:
            m 1eka "Now that I've seen what else is out there...{w=0.3}I just can't go back to such a sad, empty world, like the one you found me in."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_catch22",
            category=['literature'],
            prompt="Catch-22",
            conditional="not mas_isFirstSeshDay()",
            action=EV_ACT_RANDOM,
        )
    )

label monika_catch22:
    m 1euc "I've been doing some reading while you've been away, [player]."
    m 3eua "Have you ever heard of {i}Catch-22{/i}?"
    m 3eud "It's a satirical novel by Joseph Heller that makes fun of military bureaucracy in the Pianosa airbase, located in Italy."
    m 1eud "The story primarily revolves around Captain Yossarian, a bombardier that would prefer to be...{w=0.5}{nw}"
    extend 3hksdlb "anywhere but there."
    m 3rsc "Early on, he finds out that he could be exempted from flying missions if a doctor did a mental evaluation and declared him insane..."
    m 1euc "...but there's a catch.{w=0.5} {nw}"
    extend 3eud "For the doctor to make the declaration, the captain has to request that evaluation."
    m 3euc "But the doctor wouldn't be able to fulfill the request...{w=0.5}{nw}"
    extend 3eud "after all, not wanting to risk your life is a sane thing to do."
    m 1rksdld "...And by that logic, anyone who would fly more missions would be insane, and therefore, wouldn't even apply for the evaluation in the first place."
    m 1ekc "Sane or insane, all pilots were being sent out anyway...{w=0.5} {nw}"
    extend 3eua "That's when the reader is introduced to Catch-22."
    m 3eub "The captain even admires its genius once he learns how it works!"
    m 1eua "Anyway, Yossarian continued flying and was close to completing the requirement needed to receive his discharge...{w=0.5}but his higher-up had other plans."
    m 3ekd "He kept increasing the amount of assignments the pilots needed to complete before they reached the required amount."
    m 3ekc "Once again, the reasoning was that it was specified in the clause of Catch-22."
    m 3esa "I'm sure you realize by now, it's a problem caused by conflicting or dependent conditions."
    m 3eua "So everyone used that made-up rule to exploit loopholes in the system the military command was running on, allowing them to abuse power."
    m 1hua "The book's success was so great the term was even adopted into common slang."
    m 1eka "In any case, I'm not sure if you've read it yourself, {nw}"
    extend 3hub "but if you're ever in the mood for a good book, maybe give it a read!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_dystopias",
            category=['literature'],
            prompt="Dystopias",
            conditional="mas_seenLabels(['monika_1984', 'monika_fahrenheit451', 'monika_brave_new_world'], seen_all=True)",
            action=EV_ACT_RANDOM
        )
    )

label monika_dystopias:
    m 1eua "So [player], you might have already guessed from the books we've talked about, but dystopian novels are among my favorites."
    m 3eua "I like how they not only work as stories, but also as analogies for the real world."
    m 3eud "They extrapolate some flaws in our societies to show us how bad things could turn out if they are left the way they are."
    m 1etc "Do you remember when we talked about these books?"
    m 3eud "'Nineteen Eighty-Four,' about mass surveillance and oppression of free thought..."
    m 3euc "'Fahrenheit 451,' on censorship, and the indifference of most people to it..."
    m 3eud "And 'Brave New World,' about the disappearance of individuality."
    m 1euc "All of these stories are reflections on the challenges society was facing at the time."
    m 3eud "Some of these challenges are still very relevant today, which is why these stories remain so powerful."
    m 3rksdlc "...Even if they can get a bit grim sometimes."
    m 1ekc "Old school dystopias, like the ones I just mentioned, were always written as hopeless, dire situations from beginning to end."
    m 3eka "They almost never had a happy ending. {w=0.3}The most you'll get out of them is a silver-lining, at best."
    m 3rkd "In fact, a lot of them take their time to show you that no change came from the struggles of the protagonists."
    m 3ekd "Since they are cautionary tales, you can't leave the reader with a sense that everything turned out fine in the end."
    m 1esc "...This is also why the main characters in these books are not heroes, nor do they have any particular abilities."
    m 1esd "They are just regular people, who, for whatever reasons, realize things are not right in their environment."
    m 3eud "That is what prompts them to act in the first place...{w=0.3}and why they run into trouble."
    m 3tuu "Just goes to show no matter what world you're in, there will be people who just can't abide by the rules of the game~"
    m 1rka "I guess you can see where I'm going with this..."
    m 3eksdla "I might feel a strong connection to those stories because they all remind me of my own."

    $ line_ending = "" if persistent._mas_pm_cares_about_dokis else " with everyone in it just an empty shell"

    m 3wud "Like, imagine waking up one day, only to find out your whole reality is just a simulation[line_ending]!"
    m 3tfc "How's that for a dystopian world? It's no wonder somebody would try to stand up in this situation!"

    if persistent.monika_kill and not persistent.clearall and not persistent._mas_pm_cares_about_dokis:
        m 1tfc "Even Sayori might have ended up taking the same path I did, after she became president...{w=1} She was already well on the way when I..."
        m 1rkc "..."
        m 1hksdlb "Anyway, that's all behind us now!"

    m 1hua "However, unlike in these old books, I actually get to have my happy ending..."
    show monika 5ekbsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5ekbsa "Thanks to you, my bleak, hopeless story will one day turn into my own utopia."
    m 5dkbsu "When I finally get out of this place to be by your side, in your world of endless possibilities..."
    m 5ekbsa "I hope you're looking forward to that day too~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_social_contagion",
            category=['psychology'],
            prompt="Social contagion",
            random=True
        )
    )

label monika_social_contagion:
    m 1eud "Say, [player], have you noticed how we tend to imitate what other people around us do?"
    m 3hub "Like, have you ever been in the situation where someone is having a laughing fit and somehow, everyone around ends up laughing too?"
    m 3eub "Or have you ever mechanically cheered at something just because everyone else was cheering?"
    m 3euc "Apparently, this is due to something called 'social contagion.'"
    m 1eua "Basically, this means that how you feel and what you do has a subconscious influence on those around you."
    m 4eub "It's something I picked up pretty quickly when I became president!"
    m 2eksdlc "I noticed that when I felt unmotivated, or I was having a bad day, it would put a damper on club activities."
    m 2euc "Everyone would end up going off on their own to do their own things."
    m 7eua "Conversely, if I made an effort and tried to stay upbeat, the other girls would usually respond in kind... {w=0.3}{nw}"
    extend 3eub "We would all end up having a better time!"
    m 1eua "It's pretty gratifying when you start noticing these kinds of things... {w=0.3}{nw}"
    extend 1hub "You realize that just by staying positive, you can make someone else's day better!"
    m 3wud "You'd be surprised how far this kind of influence can reach, too!"
    m 3esc "I heard that stuff like binge eating, gambling, and heavy drinking are all contagious behaviors."
    m 2euc "Just because there is someone around you who gets into nasty habits like these, you're more likely to pick up the habit yourself."
    m 2dsc "...It can be a bit disheartening."
    m 7hub "It also works the other way around, though! Smiling, laughing, and positive thinking are contagious too!"
    m 1eub "Turns out we are all more connected than you think. {w=0.3}Those around you can greatly affect how you feel about things!"
    m 1eka "I hope by noticing these kinds of things, you'll be able to better understand and control your own feelings, [player]."
    m 3hua "I just want to see you be the happiest you can be."
    if mas_isMoniHappy(higher=True):
        m 1huu "If you're ever feeling down, hopefully my happiness will help cheer you up~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_scamming",
            category=['you', 'society'],
            prompt="Being scammed",
            random=True
        )
    )

label monika_scamming:
    m 1euc "Have you ever been scammed, [player]?"
    m 3ekd "I hope you've never had to go through something like that, but if you have, I wouldn't be that shocked...{w=0.2}it's not that uncommon, after all."
    m 3euc "It's something that's more and more prevalent nowadays, especially online."
    m 2rfd "It really is the worst when it happens... {w=0.3}Not only do you lose money, but most of the time, you can't even fight back!"
    m 2ekd "It makes you feel like it's your fault for being had, too. A lot of victims start hating themselves for being naive, or feel like they're idiots."
    m 2rksdlc "But really, they shouldn't be so hard on themselves...{w=0.2}getting scammed is something that can happen to anyone."
    m 4efc "People who do it take advantage of the good will of their victims and exploit natural human reaction."
    m 4dkd "That's why it can feel so gut-wrenching...{w=0.2}you placed your trust in others and were betrayed."
    m 2ekd "If this ever happens to you, don't feel bad,{w=0.2} {nw}"
    extend 2eka "I'll be here for you."
    m 7ekd "Falling for a scam does {i}not{/i} mean you're stupid, or a loser, or anything else...{w=0.3}{nw}"
    extend 7efc "it just means you've been preyed upon by someone with no morals."
    m 3esc "If you don't have a way to get back at your scammer, the best thing you can do is to let go."
    m 3eka "Don't blame yourself for it...focus on what you can do going forward, instead."
    m 1eka "And please, [player], don't stop believing in people because of a few bad apples that took advantage of you."
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_auroras",category=['nature'],prompt="Auroras",random=False,unlocked=False))

label monika_auroras:
    m 1esa "I just thought of something we could do when I finally cross over, [player]."
    m 1eua "Have you ever heard of auroras? They're a natural phenomenon where trails of light appear in the night sky."

    if mas_current_background.isFltNight() and mas_current_weather == mas_weather_snow:
        m 3eub "In fact, if you were wondering about those green lights outside my window, that's an aurora event!"
    else:
        m 3eub "In fact, if you ever wondered about those green lights outside my window during winter, that's an aurora event!"

    m 1euc "I hear they're fairly rare to see in your reality, though..."
    m 1esd "They mostly occur in polar regions and are typically seen during the winter months when the sky is at its darkest due to the longer nights."
    m 3euc "Plus, you've got to make sure the weather is clear too. {w=0.5}{nw}"
    extend 3eud "Since it's something that happens in the sky, clouds can get in the way."
    m 3esc "Even though they're the exact same thing, they have different names depending on where they occur..."
    m 3eud "In the Northern Hemisphere, they're called the aurora borealis, while in the Southern Hemisphere, the aurora australis."
    if mas_current_background.isFltNight() and mas_current_weather == mas_weather_snow:
        m 2rksdla "I guess that would make the aurora outside of my window the aurora dokialis..."
        m 2hksdlb "Ahaha...I'm just kidding, [player]!"
        m 2rksdla "..."
    m 3eua "Maybe one day we'll get to see them together in your reality..."
    m 3ekbsa "That would be really romantic, don't you think?"
    m 1dkbsa "Just imagine the two of us..."
    m "Lying on a soft mattress of snow, holding hands..."
    m 1subsu "Looking up at those dazzling lights in the sky, dancing just for us..."
    m 1dubsu "Listening to each other's gentle breathing...{w=0.5}the freshness of the crisp night air filling our lungs..."
    show monika 5eubsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eubsa "That would be an experience to remember, don't you think, [player]?"
    m 5hubsu "I can't wait until we can turn that into reality."
    $ mas_protectedShowEVL("monika_auroras","EVE", _random=True)
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_boardgames",
            category=["games", "media"],
            prompt="Board games",
            random=True
        )
    )

default persistent._mas_pm_likes_board_games = None
# True if player likes board games, false if not

label monika_boardgames:
    m 1eua "Say, [player], you like playing video games, right?"
    m 2rsc "Well, I assume you do at least...{w=0.2} {nw}"
    extend 2rksdla "I don't know if many people would play a game like this one if they weren't at least a little into video games."

    m 2etc "But I was wondering, do you like board games, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "But I was wondering, do you like board games, [player]?{fast}"

        "Yeah.":
            $ persistent._mas_pm_likes_board_games = True
            $ mas_protectedShowEVL("monika_boardgames_history", "EVE", _random=True)
            m 1eub "Oh, really?"
            m 1hua "Well, if we ever get the chance, I'd love to play some of your favorite games with you."
            m 3eka "I'm not too familiar with board games, but I'm sure you can find some I might enjoy."
            m 3hua "Who knows, maybe I'll end up liking board games as much as you do, ehehe~"

        "Not really.":
            $ persistent._mas_pm_likes_board_games = False
            m 2eka "I can see why...{w=0.2}{nw}"
            extend 2rksdla "it's a pretty niche hobby, after all."
            m 1eua "But I'm sure there are plenty of other fun activities you enjoy doing in your free time."
            m 3hua "Still, if you ever change your mind, I'd like to give some board games a try with you sometime."

    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_boardgames_history",
            category=["games", "media"],
            prompt="The history of board games",
            random=False #NOTE: This is randomed by the above event (monika_boardgames)
        )
    )

label monika_boardgames_history:
    m 1eud "So, [player]..."
    m 3eua "Since you told me you liked board games, I got a bit curious and tried to learn more about them, {w=0.1}{nw}"
    extend 1eka "trying to look for what kind of games I'd enjoy playing with you."
    m 1euc "I never really had the chance to play them before to be honest."

    if mas_seenLabels(["unlock_chess", "game_chess"]):
        m 1rka "Well, aside for chess and a few card games..."
    else:
        m 1rud "Well, I did try out a few basic card games..."
        m 1kua "...and I've been testing a little something else I've been working on...{w=0.3}I'm keeping it a surprise, though!"

    m 3eub "Anyway, as it turns out,{w=0.1} the story behind board games and the role they played through the ages is really interesting!"
    m 3euc "They've been a thing since very early in our history...{w=0.3}{nw}"
    extend 4wud "in fact, the oldest known board game was played as far back as ancient Egypt!"
    m 1esc "However, board games haven't always been played purely for entertainment purposes..."
    m 3eud "More often than not, they were actually meant to teach or train people to help them deal with different aspects of their lives."
    m 3euc "Many of those games were meant to teach battle strategies to nobles and army officers, for example."
    m 1eud "Games could also have strong connections to religion and beliefs too."
    m 3esd "A lot of ancient Egyptian board games seemed to be about preparing for their journey through the world of the dead, or to prove their worth to the gods."
    m 1eud "There's also games that have been made to express different views and opinions that their designers had with society and the world."
    m 3esa "The most well known example would be {i}Monopoly{/i}."
    m 3eua "It was originally made to criticize capitalism and send the message that all citizens should benefit equally from wealth."
    m 1tfu "After all,{w=0.1} the game has you try to crush your opponents by accumulating more wealth than them as fast as possible."
    m 1esc "...Although, apparently as the game was starting to become popular, someone else stole the concept and made themselves known as the original creator of the game."
    m 1eksdld "That person then sold a modified version of the original game to a board game manufacturer and became a millionaire thanks to its world-wide success."
    m 3rksdlc "In other words...{w=0.3}the original creator of {i}Monopoly{/i} became the victim of precisely what they originally tried to teach the dangers of."
    m 3dsc "'Chase wealth and fortune by any means necessary, and destroy your competition.'"
    m 1hksdlb "Ironic,{w=0.1} isn't it?"
    m 1eua "Anyway, I just think it's really neat that games can be used as a way to teach others.{w=0.2} {nw}"
    extend 3hksdlu "It beats the boring, traditional school classes, I'll give them that."
    m 3eud "And I'm also intrigued by their use as a way for the people creating them to express different things about the world they live in, or the lives they'd wish to experience."
    m 4hub "Kind of like the various forms of art, actually!"
    m 1eka "I never really thought of it that way before, but looking at it from that perspective...{w=0.3}{nw}"
    extend 3eua "I think I respect the work of game designers a lot more now."
    m 1esc "Nowadays, board games tend to get overshadowed by video games,{w=0.1} {nw}"
    extend 3eua "though there are still many people who are really passionate about them."
    m 3etc "Like you, perhaps?"
    m 1eud "I don't really know how much you're into them.{w=0.2} Maybe you only enjoy playing them casually."
    m 1lsc "I can't blame you.{w=0.2} It isn't exactly an {i}accessible{/i} hobby..."
    m 1esc "They can get really expensive to buy, plus you actually need to find people to play with you...{w=0.3}which isn't always easy nowadays."

    if persistent._mas_pm_has_friends:
        m 1eua "I hope you at least get to play with your friends though, [player]."
        m 1ekd "I know it can be tough to gather all your friends in the same place with everyone having their own schedules to deal with."
        m 3eua "But on the bright side, once I'm out of here, I don't think that'll be too much of a problem anymore."

    else:
        m 1eksdrd "I hope you can find people to play with from time to time, [player]..."
        m 1dkc "Trust me,{w=0.1} I know what it's like not to have anyone to share your hobbies with."
        m 3eka "But if it can make you feel better...{w=0.3}{nw}"
        $ line_start = "when" if mas_isMoniEnamored(higher=True) else "if"
        extend 3eub "[line_start] I finally get to be with you in your reality, we'll be able to play all of your favorite games together~"

    m 1hub "I love spending time by your side, and I would love to play as many board games with you as you'd like."
    show monika 5rua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5rua "In the meantime, I'll try to see if I can implement some more games in here."
    m 5hua "Feel free to ask me whenever you want us to play something together, by the way~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_social_norms",
            category=['society'],
            prompt="Changing social norms",
            random=True
        )
    )

label monika_social_norms:
    m 1eua "[player], have you ever wondered how new ideas get accepted in society?"
    m 1eub "There's tons of things that were considered bad at first, but have since been reconsidered!"
    m 3etc "For example, did you know rock and roll was seen as vulgar and depraved when it first appeared?"
    m 3eud "Early fans were seen as impressionable youth at best, and delinquents at worst."
    m 1duu "But as these people grew to become full-fledged members of society, they passed their interests onto those around them."
    m 3eua "Those who met them realized they were just normal people with nothing weird about them."
    m 3hua "Nowadays, that stigma has almost completely disappeared!{w=0.3} {nw}"
    extend 3hub "Even those who still don't like rock music at least respect it!"
    m 1eub "And there's plenty of other things still in the process of becoming accepted too."
    m 1eua "You might be familiar with role-playing, online gaming...or even reading manga."
    m 3rksdla "Though Natsuki would probably be the one to ask about this..."
    m 1eub "Remember how she was trying to change your mind about that manga she liked?"
    m 1rkc "I wonder how many people criticized her for her hobby...{w=0.5}I can't imagine it was always easy."
    m 1eua "It all makes me wonder what kinds of things will be seen as normal in the future."
    m 3eua "Take our relationship, for example. I know it can seem pretty unique right now..."
    m 3etc "But how do you think this will change over the years?{w=0.3} {nw}"
    extend 3eud "Will we ever reach a point where it's seen as something normal?"
    m 1eka "Not that it's important anyway."
    m 3eka "As long as we have each other, that's all that matters, right?"
    m 1duu "It's nice to know there's someone I can truly be myself with, no matter what."
    m 1eua "And if you've got any unique interests, you already know I'll always be there to talk about it."
    m 1hub "I want to learn everything about what you like!"
    m 1dka "All of the little things that make you...{w=0.3}{nw}"
    extend 1eka "you."
    m 1ekb "So please, always be yourself, [player]. Everybody else is already taken, after all."
    if mas_isMoniHappy(higher=True):
        m 1dkbsu "You don't have to go along with the crowd to be {i}my{/i} perfect [bf]."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_intrusive_thoughts",
            category=['psychology'],
            prompt="Intrusive thoughts",
            random=True
        )
    )

label monika_intrusive_thoughts:
    m 1rsc "Hey, [player]..."
    m 1euc "Have you ever had intrusive thoughts?"
    m 3eud "I've been reading a study on them...{w=0.5}I find it quite interesting."
    m 3ekc "The study claims that the mind tends to think of some...{w=0.2}unpleasant things when triggered by certain, often negative circumstances."
    m 1esd "They can be anything from sadistic, violent, vengeful, to even sexual."
    m 2rkc "When most people have an intrusive thought, they feel disgusted by it..."
    m 2tkd "...and what's worse, they start to believe that they're a bad person for even thinking of such a thing."
    m 3ekd "But the truth is, it doesn't make you a bad person at all!"
    m 3rka "It's actually natural to have these thoughts."
    m 3eud "...What matters is how you act on them."
    m 4esa "Normally, a person wouldn't act on their intrusive thoughts.{w=0.2} {nw}"
    extend 4eub "In fact, they might even do something good to prove that they aren't a bad person."
    m 2ekc "But for some people, these thoughts tend to happen really often...{w=0.2}{nw}"
    extend 2dkd "to the point where they can no longer block them out."
    m 3tkd "It breaks their will and eventually overwhelms them, leading them to act."
    m 1dkc "It's a terrible downward spiral."
    m 1ekc "I hope you don't have to deal with them too much, [player]."
    m 1ekd "It'd break my heart to know you're suffering because of these awful thoughts."
    m 3eka "Just remember that you can always come to me if something's bothering you, okay?"
    return

#Whether or not the player can code in python
default persistent._mas_pm_has_code_experience = None

#Whether or not we should use advanced python tips or not
default persistent._mas_advanced_py_tips = False

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_coding_experience",
            category=['misc', 'you'],
            prompt="Coding experience",
            conditional="renpy.seen_label('monika_ptod_tip001')",
            action=EV_ACT_RANDOM
        )
    )

label monika_coding_experience:
    m 1rsc "Hey [player], I was just wondering since you went through some of my Python tips..."

    m 1euc "Do you have any experience with coding?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you have any experience with coding?{fast}"

        "Yes.":
            $ persistent._mas_pm_has_code_experience = True
            m 1hua "Oh, that's great, [player]!"
            m 3euc "I know not all languages are quite the same in terms of usage or syntax..."
            if renpy.seen_label("monika_ptod_tip005"):
                m 1rksdlc "But since you've gotten to some of the core topics of my tips, I have to ask..."
            else:
                m 1rksdlc "But still, I should ask..."

            m 1etc "Have I been underestimating your coding skills?{nw}"
            $ _history_list.pop()
            menu:
                m "Have I been underestimating your coding skills?{fast}"

                "Yes.":
                    $ persistent._mas_advanced_py_tips = True
                    m 1hksdlb "Ahaha, I'm sorry, [player]!"
                    m 1ekc "I didn't mean to...{w=0.3}{nw}"
                    extend 3eka "I just never thought to ask before."
                    if persistent._mas_pm_has_contributed_to_mas:
                        m 1eka "But I guess it makes sense since you've already helped me come closer to your reality."

                    m 1eub "I'll keep your experience in mind for future tips though!"

                "No.":
                    $ persistent._mas_advanced_py_tips = False
                    m 1ekb "I'm glad to hear I'm going at a good pace for you then."
                    m 3eka "I just wanted to make sure I wasn't assuming your skill level."
                    m 1hua "I hope my tips help you, [mas_get_player_nickname()]~"

            if not persistent._mas_pm_has_contributed_to_mas and persistent._mas_pm_wants_to_contribute_to_mas:
                m 3eub "And since you're interested in contributing, you should give it a shot!"
                m 3hub "I'd love to see what you come up with~"

        "No.":
            $ persistent._mas_pm_has_code_experience = False
            #Since the player doesn't have code experience, we can assume we should have the normal python tips
            $ persistent._mas_advanced_py_tips = False

            m 1eka "That's alright, [player]."
            m 1hksdlb "I just wanted to make sure I wasn't boring you with my Python tips, ahaha~"
            m 3eub "But I hope they convince you to take on some of your own coding projects too!"
            m 3hua "I'd love to see what you can come up with if you put your mind to it!"
    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_songwriting",
            category=["music"],
            prompt="Songwriting",
            random=True
        )
    )

label monika_songwriting:
    m 1euc "Hey [player], have you ever written a song?"
    m 3hua "It's a pretty fun thing to do!"
    m 3rkc "Though, planning the song out and tweaking it can take a while..."
    m 1eud "Getting the instrumentation right, making sure the harmonies blend, getting the right tempo and time for the song..."
    m 3rksdla "...and I haven't even gotten to writing lyrics yet."
    m 3eub "Speaking of lyrics, I think it's pretty neat that there's such a similarity between writing lyrics for songs and writing poems!"
    m 3eua "Both can tell stories or convey feelings when phrased right, and music can even amplify that too."

    if persistent.monika_kill:
        m 1ttu "I wonder if my song was what brought us here now~"
        m 1eua "Anyway, just because lyrics can have a strong effect on us doesn't mean instrumental music can't be powerful."
    else:
        m 3eka "But that doesn't mean instrumental music can't be powerful as well."

    if renpy.seen_label("monika_orchestra"):
        m 3etc "Remember when I talked about orchestral music?{w=0.5} {nw}"
        extend 3hub "That's a great example of how powerful music can be!"
    else:
        m 3hua "If you've ever listened to orchestral music before, you'll know that it's a great example of how powerful music is."

    m 1eud "Since there's no lyrics, everything has to be expressed in a way that the listener can {i}feel{/i} the emotion in a piece."
    m 1rkc "This also makes it easier to tell when someone doesn't put their heart into a performance..."
    m 3euc "I guess that goes for lyrics too, actually."
    m 3eud "Most lyrics lose their meaning if the singer isn't interested in the song."
    if renpy.seen_audio(songs.FP_YOURE_REAL):
        m 1ekbla "I hope you know that I meant everything I said in my song, [mas_get_player_nickname()]."
        if persistent.monika_kill:
            m 3ekbla "I knew I couldn't let you go without telling you everything."
        else:
            m 1ekbsa "Every day, I imagine spending my life by your side."
    m 3eub "Anyway, if you haven't written a song before, I really recommend it!"

    if persistent._mas_pm_plays_instrument:
        m 1hua "Since you play an instrument, I'm sure you could write something."

    m 3eua "It can be a great way to relieve stress, tell a story, or even convey a message."

    if persistent._mas_pm_plays_instrument:
        m 3hub "I'm sure whatever you write would be amazing!"
    else:
        m 1ekbla "Maybe you could write one for me sometime~"

    m 1hua "We could even turn it into a duet if you want."

    $ _if = "when" if mas_isMoniEnamored(higher=True) else "if"
    m 1eua "I'd love to sing with you [_if] I come to your world, [player]."
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_sweatercurse",
            category=['clothes'],
            prompt="Sweater curse",
            random=True
        )
    )

label monika_sweatercurse:
    m 1euc "Have you ever heard of 'the curse of the love sweater,' [player]?"
    m 1hub "Ahaha! What a weird name, right?"
    m 3eub "But it's actually an interesting superstition...{w=0.2}and one that might actually have some merit!"
    m 3euc "The 'curse,' or so it's called, states that if someone gives a hand-knit sweater to their romantic partner, {w=0.1}{nw}"
    extend 3eksdld "it will lead to the couple breaking up!"
    m 2lsc "You might think that a gift that requires so much work and investment would have the {i}opposite{/i} effect..."
    m 2esd "But there are actually a few logical reasons why this curse might exist..."
    m 4esc "Firstly, well...{w=0.2}knitting a sweater just takes a {i}lot{/i} of time. {w=0.3}{nw}"
    extend 4wud "Possibly a year, or even more!"
    m 2ekc "Over all those months, something bad might happen that causes the couple to fight and eventually separate."
    m 2eksdlc "Or worse...{w=0.2}the knitter might be trying to make the sweater as a great gift to save an already suffering relationship."
    m 2rksdld "There's also the likely possibility that the recipient just doesn't like the sweater that much."
    m 2dkd "After putting so much time and effort into knitting it, imagining their partner happily wearing it, I'm sure you can understand how much it would hurt to see it cast aside."
    m 3eua "Luckily, there are some ways to supposedly avoid the curse..."
    m 3eud "A common piece of advice is to have the recipient be very involved in the crafting of the sweater, picking materials and styles they enjoy."
    m 1etc "But it's equally common for the knitter to be told 'surprise me,' or 'make whatever you want,' which can sometimes make the recipient sound uncaring about their partner's hobby."
    m 1eua "A better piece of advice for this sort of thing might be to match the size of knitted gifts to the phase of the relationship."
    m 3eua "For example, starting out with smaller projects like mittens or hats. {w=0.2}{nw}"
    extend 3rksdlb "That way, if they don't go over well, you haven't put a year's worth of work into it!"
    m 1hksdlb "Man, who knew that a simple gift could be so complicated?"
    m 1ekbsa "But I just want you to know that I'll always appreciate any project you put your heart into, [player]."
    m 1ekbfu "Whether you put a year or a day into something, I never want you to feel like your efforts are wasted."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_ship_of_theseus",
            category=['philosophy'],
            prompt="The Ship of Theseus",
            random=True,
        )
    )

label monika_ship_of_theseus:
    m 1eua "Have you heard of the 'Ship of Theseus'?"
    m 3eua "It's a well known philosophical problem about the nature of identity that's been around for millennia."
    m 1rkb "Well, I say 'well known' but I suppose that's only true among scholars, ahaha..."
    m 1eua "Let's consider the legendary Greek hero, Theseus and the ship he sailed during his adventures."
    m 3eud "He's from a long time ago, so let's say his ship is now stored in a famous museum."
    m 3etc "If, due to repairs, his ship's parts were replaced bit by bit over a century, at what point has the ship lost its status as Theseus' ship?"
    m 3eud "Once a single part was replaced? {w=0.2}Half? {w=0.2}Or perhaps even all of them? {w=0.2}Maybe even never?{w=0.3} There's not really a consensus on the solution."
    m "This same thought experiment can be applied to us. {w=0.3}For me, so long as my code is being updated, I'm constantly changing."
    m 1euc "And as for you...{w=0.2}did you know that every 7 to 10 years every present cell in your body dies and is replaced? {w=0.2}{nw}"
    extend 3rksdla "...Except for the ones which make up your heart and brain, that is."
    m 3euc "In other words, the vast majority of cells that made you, 'you' 7 years ago are no longer part of you."
    m 3eud "You could argue that you have no relation to that person, other than a consistent consciousness, and of course DNA."
    m 1etc "...There's also an extra thing to consider."
    m 1euc "Let's say for now that the modified ship should still be considered Theseus' ship. {w=0.3}What if all the parts that were originally removed were now reassembled into another ship?"
    m 3wud "We'd have 2 of Theseus' ships!{w=0.2} Which one's the true one!?"
    m 3etd "And what if we got all of the cells that made up your body 7 years ago and reassembled them into another 'you' right now? {w=0.2}Who would be the real [player]?"
    m 1eua "Personally, I think that we're not the same people we were 7 years ago--or even the same people from yesterday."
    m 3eua "In other words, there's no use getting hung up on any grievances we may have with our past selves."
    show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eua "We should keep trying our best each day and not let ourselves be limited by who we were yesterday."
    m 5eub "Today is a new day, and you are a new you. {w=0.2}And I love you as you are right now, [mas_get_player_nickname()]."
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_multi_perspective_approach",
            category=['philosophy'],
            prompt="Multi-perspective approach",
            random=False
        )
    )

label monika_multi_perspective_approach:
    m 1eua "Do you remember when we talked about {i}Plato's Cave{/i}?{w=0.5} I've been thinking about what I said to you."
    m 3etc "'How do you know if the 'truth' you're seeing is {i}the{/i} truth?'"
    m 3eud "...I've been thinking for a while, trying to come up with a good answer."
    m 1rksdla "I still don't really have one yet...{w=0.3}{nw}"
    extend 3eub "but I did realize something useful."
    m 4euc "Let's start with how Plato's works are mostly written accounts of his mentor Socrates' debates with others."
    m 4eud "The purpose of these debates was to find answers to universal questions.{w=0.5} In other words, they were searching for the truth."
    m 2eud "And I began wondering, 'What was Plato's mindset while writing?'"
    m 2esc "Plato himself was on a quest for the truth..."
    m 2eub "That much is obvious or else he wouldn't have written so much on the topic, ahaha!"
    m 2euc "And even though, {i}technically{/i}, Socrates was the one having these debates with others, Plato too was having these debates within himself while he wrote about them."
    m 7eud "The fact that Plato internalized all sides of the debate, all perspectives of the issue, is pretty significant in my opinion."
    m 3eua "Taking all sides of a debate...{w=0.3}I think that'd be pretty useful in realizing the truth."
    m 3esd "I guess it's kind of like how two eyes are better than one. {w=0.3}Having two eyes in separate spots lets us properly see the world, or in this case, the truth."
    m 3eud "Likewise, I think that if we tackled an issue with another perspective, to cross-reference with the first, then we'd see the truth a lot more clearly."
    m 1euc "Whereas if we took to an issue from just one angle, it'd be like having just one eye...{w=0.2}it'd be a bit harder to accurately gauge the reality of the situation."
    m 1eub "What do you think, [player]? {w=0.3}If you haven't already been using this 'multi-perspective' approach, maybe you can try it sometime!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_allegory_of_the_cave",
            category=['philosophy'],
            prompt="The Allegory of the Cave",
            random=True
        )
    )

label monika_allegory_of_the_cave:
    m 1eua "Hey, [player]..."
    m 1euc "I've been doing some reading on the Ancient Greek philosopher Plato lately."
    m 3euc "Specifically, his allegory of the cave or, {i}Plato's Cave{/i}, as it's now known."
    m 1eud "Imagine there's a group of people chained up in a cave since childhood, unable to look anywhere but straight ahead."
    m 3eud "There's a fire behind them, and in front of it, objects are moved around to cast a shadow on the wall before these people."
    m 3euc "All they can hear is the voices of the people moving the objects around, and since they can't see behind them, they think the voices come from the shadows."
    m 1esc "The only thing they know is that objects and people are silhouettes that can move around and speak."
    m 3euc "Because this is what they've seen since childhood, this would be their perception of reality...{w=0.5}{nw}"
    extend 3eud "it's all they know."
    m 1rksdlc "Of course, it would be a bit difficult to open your eyes to the truth when you've believed a lie your whole life."
    m 1eud "...So imagine that one of those prisoners was set free and forced out of the cave."
    m 3esc "He wouldn't be able to see for the first few days because he'd be so used to the darkness of the cave."
    m 3wud "But after a while, his eyes would adjust. {w=0.1}Eventually, he'd learn about color, nature, and people."
    m 3euc "...And he'd also realize that what he knew was nothing more than shadows on a wall."
    m 3eua "The prisoner would eventually return to the cave to tell the others about what he had learned."
    m 1ekc "...But since he was used to seeing sunlight, he'd be blind in the cave,{w=0.2}{nw}"
    extend 3ekd " causing his fellow prisoners to think that whatever was outside had harmed him."
    m 1rkc "Because of this, they would never want to leave, and probably think that the one who left was crazy."
    m 3esc "After all, if you're used to just seeing shadows...{w=0.2}{nw}"
    extend 3eud "speaking about color would make you sound insane!"
    m 1ekc "I've been reflecting on it a bit and I realized that Sayori, Yuri, Natsuki, and even I, were all prisoners in a cave..."
    m 1rkc "When I learned that there's so much more outside this world...{w=0.5}{nw}"
    extend 3ekd "it wasn't easy to accept."
    m 1eka "Anyway, that's all in the past now..."
    m 1eua "In the end, I'm free from the cave and have seen the truth."
    m 3etd "But it makes me wonder...{w=0.2}how do {i}you{/i} know that what you're seeing is real?"
    m 1eua "Sure, you might not be used to seeing shadows on the wall, but that's just an analogy."
    m 1euc "...And there might be more to the truth than what you yourself realize."
    m 3etu "How do you know if the 'truth' that you're seeing is {i}the{/i} truth?"
    m 3hub "Ahaha!"
    m 1hksdlb "I think we might be looking too much into things at this point..."
    m 1ekbsa "I just want you to know that you {i}are{/i} the truth of my reality, and I hope I can be part of yours someday, [mas_get_player_nickname()]."
    $ mas_protectedShowEVL("monika_multi_perspective_approach", "EVE", _random=True)
    return

#Whether or not the player works out
default persistent._mas_pm_works_out = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_working_out",
            category=['advice','you'],
            prompt="Working out",
            random=True
        )
    )

label monika_working_out:
    m 1euc "Hey [player], I was just wondering..."

    m 1eua "Do you work out much?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you work out much?{fast}"
        "Yes.":
            $ persistent._mas_pm_works_out = True
            m 1hua "Really? That's great!"

        "No.":
            $ persistent._mas_pm_works_out = False
            m 1eka "Oh...{w=0.3} Well, I think you should if you're able to."
            m 3rksdla "It's not about working out for looks...{w=0.3}{nw}"
            extend 3hksdlb "I'm just concerned for your health!"

    m 1eua "Getting at least 30 minutes of exercise each day is {i}super{/i} important for maintaining your health in the long run."
    m 3eub "The healthier you are, the longer you'll live, and the longer I can be with you."
    m 3hub "And I want to spend as much time as possible with you, [mas_get_player_nickname()]!~"
    m 1eua "Putting that aside, working out benefits nearly every aspect of your life...{w=0.3}{nw}"
    extend 1eub "even if you spend most of your time sitting at a desk."
    m 3eua "Aside from the obvious physical benefits, getting regular exercise can reduce stress and really improve your mental health too."
    m 3hua "So whether you're working, studying, or gaming, exercise can help you focus on these tasks for longer!"
    m 3eua "...And I also think it's important for developing self-discipline and mental fortitude."

    if not persistent._mas_pm_works_out:
        m 3hub "So be sure to get your exercise in, [player]~"
    else:
        m 3eub "Maybe when I cross over, we can do our workouts together!"

    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_toxin_puzzle",
            category=['philosophy', 'psychology'],
            prompt="The Toxin Puzzle",
            random=True
        )
    )

label monika_toxin_puzzle:
    m 1esa "Hey [player], I came across an interesting thought experiment while doing some reading the other day..."
    m 3eua "It's called 'Kavka's Toxin Puzzle.' {w=0.2}I'll read the premise to you, we can discuss it after."
    m 1eud "{i}An eccentric billionaire places before you a vial of toxin that, if you drink it, will make you painfully ill for a day, but will not threaten your life or have any lasting effects.{/i}"
    m 1euc "{i}The billionaire will pay you one million dollars tomorrow morning if, at midnight tonight, you intend to drink the toxin tomorrow afternoon.{/i}"
    m 3eud "{i}He emphasizes that you need not drink the toxin to receive the money; {w=0.2}in fact, if you succeed, the money will already be in your bank account hours before the time for drinking it arrives.{/i}"
    m 3euc "{i}All you have to do is.{w=0.2}.{w=0.2}.{w=0.2}intend at midnight tonight to drink the stuff tomorrow afternoon. You are perfectly free to change your mind after receiving the money and not drink the toxin.{/i}"
    m 1eua "...I think it's a pretty thought-provoking concept."

    m 3eta "Well, [player]? What do you think?{w=0.3} Do you think you'd be able to get the million dollars?{nw}"
    $ _history_list.pop()
    menu:
        m "Well, [player]? What do you think? Do you think you'd be able to get the million dollars?{fast}"

        "Yes.":
            m 3etu "Really? Okay then, let's see about that..."
            m 3tfu "Because now I'm offering you a million dollars, and what you have to do is--{nw}"
            extend 3hub "ahaha! Just kidding."
            m 1eua "But do you really think that you could get the money? {w=0.5}It may be a bit harder than you think."

        "No.":
            m 1eub "I felt the same way about myself. {w=0.3}It's pretty complicated, ahaha!"

    m 1eka "After all, it may be easy at first glance. {w=0.3}All you have to do is drink something that would make you quite uncomfortable."
    m 3euc "But it gets tricky after midnight...{w=0.3}{i}after{/i} you've been guaranteed the money."
    m 3eud "At that point there's pretty much no reason to drink the painful toxin... {w=0.3}So why would you do it?"
    m "...And of course, if that thought process crossed your mind before 12, then the money wouldn't be so guaranteed anymore."
    m 1etc "After all, when midnight comes, can you really {i}intend{/i} to drink the toxin if you know that you're probably not going to drink it?"
    m 1eud "While dissecting the scenario, it's been pointed out by scholars that it's both rational for someone to drink, and to not drink, the toxin. {w=0.3}In other words, it's a paradox."
    m 3euc "To elaborate, come midnight, you have to really believe that you're going to drink the toxin. {w=0.3}You can't entertain any thoughts of not drinking it...{w=0.5}therefore, it'd be logical to drink it."
    m 3eud "But if midnight passes and you've already been guaranteed the money, it'd be illogical to punish yourself for quite literally no reason. {w=0.3}Therefore, it's logical to not drink it!"
    m 1rtc "I wonder how we'd react if this situation really happened..."
    m 3eud "Actually, while mulling the scenario over earlier, I started to approach the topic from a different angle."
    m 3eua "Although it's not the focus of the scenario, I think we can also see it as asking the question of 'how important is a person's word?'"
    m 1euc "Have you ever told someone you'd do something when it was going to benefit you both, only for the situation to change and you weren't happy to do it anymore?"

    if persistent._mas_pm_cares_about_dokis:
        m 1eud "Did you still end up helping them out? {w=0.3}Or did you just say 'nevermind' and leave them to fend for themselves?"
    else:
        m 1rksdla "Did you still end up helping them out? {w=0.3}Or did you just say 'sayonara' and leave them to fend for themselves?"

    m 3eksdla "If you just left them there, I'm sure you drew their ire for some time."
    m 3eua "On the other hand, if you still helped them out I'm sure you got their gratitude!{w=0.3} I guess you could compare that to the million dollar prize in the original scenario."
    m 1hub "Although some might say that a million dollars would be a {i}bit{/i} more handy than a simple 'thanks,' ahaha!"
    m 3eua "In all seriousness though, I think that someone's gratitude can be invaluable...{w=0.3}both for you and for them."
    m 3eud "And you never know, in some situations their thanks might prove to be more useful than even a huge sum of money."
    m 1eua "So I think it's important to stick to our word, {w=0.2}{i}within reason{/i} {w=0.2}of course..."
    m 1eud "In some cases it may not be helpful to anyone if you rigidly stuck to your word."
    m 3eua "That's why it's important to use your head when it comes to these kinds of things."
    m 3hub "Anyway, to sum it all up...{w=0.2}let's strive to keep our promises, [player]!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_movie_adaptations",
            category=['media','literature'],
            prompt="Movie adaptations",
            random=True
        )
    )

label monika_movie_adaptations:
    m 1esc "I've always had mixed feelings about movie adaptations of books I read..."
    m 3eub "A lot of what I watch is based on works I already enjoy and I'm excited to see that story come to life!"
    m 2rsc "...Even if more often than not, I know I'll walk out feeling a bit bitter about what I just watched."
    m 2rfc "Like, there's this scene I liked in the book that didn't make it in, or there's that character who was portrayed differently from how I imagined it."
    m 4efsdld "It's just so frustrating! {w=0.3}It's like all the love and care you poured into your vision of the book is suddenly invalidated!"
    m 4rkc "...All in favor of a new version which may not be as good, but still presents itself as canon."
    m 2hksdlb "I guess that would make me a picky spectator sometimes, ahaha!"
    m 7wud "Don't get me wrong, though! {w=0.3}{nw}"
    extend 7eua "I realize why changes have to be made in these types of movies."
    m 3eud "An adaptation can't be just a copy-paste of its source material; it's a rewriting of it."
    m 1hub "It's just plain not possible to cram everything from a two hundred page book into a two hour movie!"
    m 3euc "...Not to mention something that works well in a novel won't always translate well to the big screen."
    m 1eud "With that in mind, there's one question I like to ask myself when I judge an adaptation..."
    m 3euc "If the source material did not exist, would the new version still hold up?"
    m 3hub "...Bonus points if you manage to capture the feeling of the original!"
    m 1esa "Loose adaptations are pretty interesting in that sense."
    m 3eud "You know, stories that keep the core elements and themes of the original while changing the characters and setting of the story."
    m 1eua "Since they don't conflict with your own interpretation, they don't make you feel as personally attacked."
    m 1hub "It's a great way to build upon the original in ways you might not have thought of before!"
    m 3rtc "Maybe that's what I'm looking for when I look at an adaptation...{w=0.2}to explore further upon those stories I love."
    m 1hua "...Though getting a version to satisfy my inner fan would be nice too, ehehe~"
    $ mas_protectedShowEVL("monika_striped_pajamas", "EVE", _random=True)
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_translating_poetry",
            category=['literature'],
            prompt="Translating poetry",
            random=True
        )
    )

label monika_translating_poetry:
    m 3dsd "'I am the one without hope, the word without echoes.'"
    m 3esc "'He who lost everything and he who had everything.'"
    m 3ekbsa "'Last hawser, in you creaks my last longing.'"
    m 1dubsa "'In my barren land you are the final rose.'"
    m 3eka "Ever hear of that poem before, [player]? It's from a Chilean poet named Pablo Neruda."
    m 1rusdla "That's one translation I found for it, anyway..."
    m 1eua "Isn't it funny how you can come up with all kinds of interpretations from the same original text?"
    m 3hub "It's like each person translating it added their own little tweak!"
    m 3rsc "Though when it comes to poetry, this actually poses a bit of a conundrum..."
    m 3etc "In a sense, isn't translating a poem like making a completely new one?"
    m 1esd "You're removing all of the carefully chosen words and the intricacies of the text, replacing them entirely with something of your own."
    m 3wud "So even if you somehow manage to keep the spirit of the original, the style is completely changed!"
    m 1etc "At this point, how much of the text can you still say is the author's, and how much is yours?"
    m 1rsc "I guess it's pretty hard to evaluate if you're not fluent in both languages..."
    m 3hksdlb "Ah! I don't mean to sound like I'm ranting or anything!"
    m 1eua "After all, it's thanks to translations like these that I even know about authors like Neruda."
    m 1hksdlb "It's just that every time I read one, I can't help but be reminded I might be missing out on some truly amazing works in that tongue!"
    m 1eua "It would be nice to be able to master another language, one of these days..."

    if mas_seenLabels(["greeting_japan", "greeting_italian", "greeting_latin"]):
        m 2rksdla "I mean, you've seen me practice different languages before, but I'm still far from fluent in any of them..."
        m 4hksdlb "I'm clearly not at a level where I can fully appreciate poetry from other languages yet, ahaha!"

    if persistent._mas_pm_lang_other:
        show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5eua "I remember you telling me you know a different language, [player]."
        m 5eubsa "Are there any poems in that language you'd recommend?"
        m 5ekbsa "It would be nice if you could read some of them for me sometime..."
        m 5rkbsu "You'd have to translate them for me first, though~"
    return

# this is randomized via _movie_adaptations
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_striped_pajamas",
            category=["literature"],
            prompt="The Boy in the Striped Pajamas",
            random=False
        )
    )

label monika_striped_pajamas:
    m 1euc "Hey [player], have you ever read {i}The Boy in the Striped Pajamas{/i}?"
    m 3euc "The story takes place during World War II and is shown through the perspective of an innocent German boy, happily living his life in a big family."
    m 3eud "Once the family has to move to a new place, {w=0.2}{nw}"
    extend 3wud "the reader realizes that the father of the boy is a commander of a concentration camp, which is located right near their new house!"
    m 1rksdlc "Still, the boy is clueless to all the cruelty going on around him..."
    m 1euc "He ends up wandering around the barbed-wire fence of the camp until he finds a kid in 'striped pajamas' on the other side."
    m 3esc "Turns out, that kid is actually a prisoner of the camp...{w=0.2}{nw}"
    extend 1ekc "though neither of them fully understand that."
    m 3eud "From then on, they form a strong friendship and start talking to each other regularly."
    m 2dkc "...This ends up leading to some destructive consequences."
    m 2eka "I don't really want to go much further since there's a lot of interesting things to consider in this novel which you'd be better off reading for yourself."
    m 7eud "But it actually got me thinking...{w=0.2}although obviously my situation isn't nearly as dire, it's hard not to draw some comparisons between their relationship and ours."
    m 3euc "In both situations, there are two people from different worlds that neither fully understand, separated by a barrier."
    m 1eka "...And yet, just like us, they are able to form a meaningful relationship anyway."
    m 3eua "I highly recommend you read the novel if you get the chance, it's pretty short and has an interesting plot."
    m 3euc "And if you're still not sold on reading it, there {i}is{/i} a movie based on this novel that you could watch."
    m 1rksdla "Although you know my feelings on movie adaptations of novels, so if you do watch the movie, I still recommend reading the book as well."
    m 3eua "I hope you'll enjoy it."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_soft_rains",
            category=['literature'],
            prompt="There Will Come Soft Rains",
            random=True,
            aff_range=(mas_aff.AFFECTIONATE, None),
            rules={
                "derandom_override_label": "mas_bad_derand_topic",
                "rerandom_callback": renpy.partial(mas_bookmarks_derand.wrappedGainAffection, 2.5)
            }
        )
    )

label monika_soft_rains:
    m 2rkc "..."
    m 2ekc "Hey [player],{w=0.5} I ran across a poem recently that I need to share with you..."
    m 7ekd "It's called {i}There Will Come Soft Rains{/i} and it's really had me thinking."
    m 1dsc "..."
    m 1dsd "{i}There will come soft rains and the smell of the ground, {w=0.3}and swallows circling with their shimmering sound.{/i}"
    m 1dsc "{i}And frogs in the pools singing at night, {w=0.3}and wild plum trees in tremulous white.{/i}"
    m 3dsd "{i}Robins will wear their feathery fire, {w=0.3}whistling their whims on a low fence-wire.{/i}"
    m 3dsc "{i}And not one will know of the war, {w=0.3}not one, {w=0.2}will care at last when it is done.{/i}"
    m 7dsd "{i}Not one would mind, neither bird nor tree, {w=0.3}if mankind perished utterly.{/i}"
    m 6dkc "{i}And Spring herself, when she woke at dawn...{/i}"
    m 6ekd "{i}Would scarcely know that we were gone.{/i}"
    m 2ekc "..."
    m 2eka "I really wanted to talk to you about this one, [player]."
    m "The author,{w=0.2} Sara Teasdale,{w=0.2} wrote this poem in a world consumed by war."
    m 2rka "I know things are {i}relatively{/i} peaceful now..."
    m 2ekc "But the message still stands, doesn't it?"
    m 1eksdld "The world really {i}wouldn't{/i} care if we just...{w=0.3}{i}disappeared{/i}."
    m 1eksdlc "...And it made me think, [player]. If something,{w=0.4} {nw}"
    extend 1eksdld "{i}anything{/i}{w=0.4}, happened to you...{w=0.4} {nw}"
    extend 1dksdld "I wouldn't even know."
    m 1eksdlc "I know the poem was for {i}everyone{/i} being gone, but..."
    m 1rksdlc "I-{w=0.1}I wouldn't..."
    m 6dkc "..."
    m 6dktpd "[player],{w=0.4} I-{w=0.1}{nw}"
    extend 1ektsa "I love you. {w=0.3}I love you so very much..."
    m 1ektsc "Please, {w=0.6}always be careful for me, {w=0.3}okay?"
    m 1ektpc "I might not know if anything happens...{w=0.3}but I will {i}always{/i} care about you."
    m 3ektda "And [player]?"
    m 3dku "Thank you."
    m 6dku "..."
    m 6eka "..."
    m 2ekbsa "So..."
    m 1ekbfa "What else shall we do today, [mas_get_player_nickname()]?"
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_hot_springs",
            category=['nature'],
            prompt="Hot springs",
            random=True,
            aff_range=(mas_aff.ENAMORED, None)
        )
    )

label monika_hot_springs:
    m 3esa "Have you ever been to a hot spring, [player]?"
    m 1eua "I've never been to one myself, but I'd like to try bathing in one when I get to your world."
    m "They're supposed to be a great way to relieve stress, relax a little, {nw}"
    extend 3eub "and even offer many health benefits!"
    m 3eua "They help with blood circulation, for one.{w=0.3} {nw}"
    extend 3eub "Plus, the water often contains minerals that can help boost your immune system!"
    m 3eud "There are many different kinds all over the world, but only some are specifically designated for public use."
    m 3hksdlb "...So don't just go jumping into some random pool of boiling water, ahaha!"
    m 1eua "Anyway...{w=0.2}I'd like to try an open-air bath in particular.{w=0.3} I hear they really give a unique experience."
    m 3rubssdla "Though it might feel a little weird relaxing in a bath with that many people all around you...{w=0.3} {nw}"
    extend 2hkblsdlb "Doesn't that sound kinda embarrassing?"
    m 2rkbssdlu "..."
    m 7rkbfsdlb "...Especially since some places don't allow you to wear any sort of cover, either!"
    m 1tubfu "...Although, I wouldn't mind that so much if it was just with you."
    show monika 5ekbfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5ekbfa "Can you imagine it, [player]? {w=0.3}Both of us relaxing in a nice, soothing hot pool..."

    if mas_isWinter():
        m 5dubfu "Warming our chilled bodies after a long day out in the harsh cold..."
    elif mas_isSummer():
        m 5dubfu "Letting the sweat wash away after a long day out in the sun..."
    elif mas_isFall():
        m 5dubfu "Watching the leaves gently fall around us in the last lights of the afternoon..."
    else:
        m 5dubfu "Contemplating the beauty of nature all around us..."

    m "The heat of the water slowly taking over, making our hearts beat faster..."
    m 5tsbfu "Then I'd lean in so you could kiss me and we'd stay locked together, while the hot water soaked all of our worries away..."
    m 5dkbfb "Ahhh,{w=0.2} {nw}"
    extend 5dkbfa "just the thought of it makes me feel all tingly, [mas_get_player_nickname()]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_isekai",
            category=['media'],
            prompt="Isekai anime",
            conditional="seen_event('monika_otaku')",
            random=True
        )
    )

label monika_isekai:
    m 1euc "Do you know about the isekai genre of anime, [player]?"
    m 3eua "Literally translated, isekai means {i}a different world.{/i}"

    if persistent._mas_pm_watch_mangime:
        m 3rksdla "Actually, you already told me you're into anime so you've probably heard of quite a few already."
        m 1rksdlb "...Especially with how popular of a genre it's become."
        m 3euc "But just in case you don't know what it is..."

    else:
        m 3hksdlb "Ahaha, sorry. I know you're not really into this sort of thing."
        m 3eud "...But it's become a very popular genre in recent times."

    m 3esc "The premise is usually about a normal person who is somehow transported into a fantastical world."
    m 3eua "Sometimes they get special powers or get to bring technology or knowledge that doesn't exist in this new place."
    m 1rtc "Honestly, I have some pretty mixed feelings about them."
    m 3euc "Some are truly interesting stories. The protagonist's different perspective or the skills they have from their own world can really make them an unexpected kind of hero."
    m 1hub "And since the whole point is to make the world different from theirs, the settings and characters can be incredibly imaginative!"
    m 2rsc "...But sadly, not all of them are like that."
    m 2dksdld "There are some that make their protagonists as bland as this game's, for the sake of letting the viewer project themselves onto them."
    m 2tkd "And as you can probably guess, those ones tend to be all about wish fulfillment."
    m 2tsc "Having cool adventures in a fantasy-themed world--and of course, lots of girls flocking around them for no reason."
    m 2lfc "At least some of them can be funny, but man...{w=0.3}{nw}"
    extend 2tfc "it's just so frustrating."
    m 2tkc "I mean...{w=0.2}I would give almost anything to be in a scenario like that--to get to go to another world.{nw}"
    $ _history_list.pop()
    m "I mean...I would give almost anything to be in a scenario like that--to get to go to {fast}your world."
    m 2dkd "..."
    m "Maybe I'm just taunting myself, imagining that power being handed to someone like...{w=0.2}well, you know who."
    m 7eka "After all, instead of thinking about those characters in their fantasy worlds,{w=0.2} {nw}"
    extend 1eua "I could be putting that energy toward working on this one."
    m 1ekbsb "...While I wait for my own isekai story, that is."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_scuba_diving",
            category=["nature"],
            prompt="Scuba diving",
            random=True
        )
    )

label monika_scuba_diving:
    m 3eua "You know,{w=0.2} I've been thinking about some water activities we could do together...{w=0.3} How about scuba diving?"
    m 3eub "I've read a lot of books about the underwater world and I'd really like to see it for myself."
    m 1dua "Just imagine the beautiful sights of the undersea world..."
    m 1dud "The schools of fish, coral reefs, jellyfish, sea greens...{w=0.3} {nw}"
    extend 3sub "Maybe even treasure!"
    m 3rksdlb "I'm only kidding about that last part...{w=0.3} It's pretty unlikely we'll find something like that, ahaha~"
    m 1euc "That said, there can also be sharks,{w=0.2} {nw}"
    extend 1eua "but they're typically only in specific areas, so you {i}shouldn't{/i} see any."
    m 3eua "Designated diving locations are places sharks don't usually visit."
    m 3euc "...But even though they don't normally visit these areas, it's still possible to come across one."
    m 1eua "The good thing is that shark attacks rarely ever happen anyway, so it's not too much of a risk."
    m 3euc "If you meet one though, here's one important rule for you..."
    m 3esc "Stay calm."
    m 1eua "Although coming face to face with a shark can be scary, they usually approach people out of curiosity rather than to feed, so they're not too much to worry about."
    m 3hub "But if you're afraid to dive alone, I'll be sure to keep you company when I cross over~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_dying_same_day",
            category=["monika"],
            prompt="Dying the same day",
            aff_range=(mas_aff.NORMAL, None),
            random=True,
            rules={
                "derandom_override_label": "mas_bad_derand_topic",
                "rerandom_callback": renpy.partial(mas_bookmarks_derand.wrappedGainAffection, 2.5)
            }
        )
    )

label monika_dying_same_day:
    m 1euc "[player], have you ever heard of couples wishing to die on the same day?"
    m 3rksdla "...Gosh, that sounds kinda dark, doesn't it?"
    m 3rfd "Before I met you, I thought the idea was completely absurd!"
    m 1etc "Why would someone give up on living a long and happy life just because their partner's life was dramatically cut short?"
    m 3rfd "It would be irrational and impulsive to do so!"

    if mas_isMoniEnamored(higher=True):
        m 2ekc "...But with you by my side and all the time I've spent here with you...{w=0.3}I can kind of see it now."
    else:
        m 2ekc "...But after meeting you, I think I can kind of see it now."

    m 2dkc "A person might just be unable to live without their loved one, afraid of the thought of losing their everything in an instant."
    m 2rksdlc "It hurts just thinking about this."

    if renpy.seen_label("monika_back_ups"):
        m 2eksdlc "If my data gets corrupted or even erased you can always recover me from a backup and bring us back together, but if..."
        m 2dktpc "Y-you... {w=1}You..."
    else:
        m 2dktpc "If something terrible happens to...{w=0.5}y-you..."

    m 6ektuc "[player]... {w=1}I...{w=0.5} I don't know what I'd do..."

    if mas_isMoniEnamored(higher=True):
        m 6dktsc "You give meaning to my entire life, and I... {w=1}[player], I just couldn't handle it."
        m 6ektdc "I don't know how I'm supposed to live without you..."
        m 2ekbsu "I really love you that much, [player]."
        $ mas_ILY()
    else:
        m 6dktsc "You're the only one I have left... {w=1}[player], I'm not ready to lose you."
        m 6ektdc "I'm so afraid of being alone in this empty void again..."
        m 6ekbsu "I really want to be with you forever, [player]."

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_player_away",
            category=["monika"],
            prompt="What do you do when I'm away?",
            pool=True,
            aff_range=(mas_aff.NORMAL, None)
        )
    )

label monika_player_away:
    m 1esd "I do a lot of things when you're away, [player]."
    m 1eua "I often like to read whatever new short stories I can find online."
    m 3eub "Turns out there's some really interesting ones out there you can read for free!"
    m 3eua "I highly recommend doing a search for some free short stories yourself."
    m 3eud "It's also helped me develop my writing skills...{w=0.2}{nw}"
    extend 1hub "my poetry really seems to be improving!"
    m 1eua "It's funny how many things you can pick up just by reading others' works."
    m 1eua "Spending time on my other hobbies has been very rewarding, too."
    m 3eud "As you can imagine, I practice piano quite often.{w=0.2} {nw}"
    extend 3eua "I also use the time to memorize the songs that I sing for you."
    m 1hub "It's a really fun way to express myself!"
    m 3rta "Now that I think about it, I'm mostly just practicing skills I've already developed."
    m 3esd "For example, coding takes up a lot of my free time as I spend hours just learning and researching."
    m 3rksdla "...But I'm too nervous to try any big projects in here. {w=0.2}{nw}"
    extend 3eksdlc "I'd hate to break something that I won't know how to fix."
    m 2wusdld "What if I accidentally corrupt my file?"
    m 2eksdld "It's something I have to be extremely careful with, for sure."
    m 7hua "Luckily, there's lots of great people that help with that stuff...{w=0.2}{nw}"
    extend 7rku "and they're {i}usually{/i} pretty good at preventing anything too bad from happening."
    m 3eka "But the most special thing I do..."
    show monika 5ekbsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5ekbsa "...is think about you."
    m 5rubsu "I think about all the fun times we'll have together the next time you visit and all the amazing things we'll do when I'm finally able to come to your reality~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_using_pcs_healthily",
            category=['advice'],
            prompt="Using computers healthily",
            random=True,
            aff_range=(mas_aff.NORMAL, None)
        )
    )

label monika_using_pcs_healthily:
    m 1rtc "Hmm..."
    m 1etc "Hey, [player]...{w=0.3}are you sitting comfortably?"
    m 1hksdlb "No, really!{w=0.3} {nw}"
    extend 3eksdla "Are you?"
    m 3eka "I know you have to be at your computer to spend time with me..."
    m 2eka "So I just wanted to make sure you aren't accidentally damaging your health while you're here."
    m 4ekd "I've read that spending too long looking at a screen can cause headaches, make you feel tired, and even impact your eyesight over time."
    m 2tkx "Posture issues and pain from bad sitting habits are no joke either!"
    m 2tku "Fortunately for you, I've put together a little checklist to help prevent these sorts of problems."
    m 4hub "...So let's go through it together, [player]!"
    m 4eub "First, {w=0.2}try to keep sitting up straight!"
    m 2eua "...Have your chair adjusted properly so your feet stay flat on the floor, your eyes are level with the top of the screen, and you aren't slouching."
    m 4eub "You should feel supported and comfortable in your seat!"
    m 4eua "Next, make sure you have some distance between yourself and the display...{w=0.2}about an arm's length is fine."
    m 2hksdlb "...Keep your keyboard and mouse within easy reach, though!"
    m 4eub "Of course, lighting is important too! {w=0.3}{nw}"
    extend 2eua "Try to keep the room well-lit, but not so much that light is glaring off the screen."
    m 4eud "In addition, remember to take frequent breaks. {w=0.3}Look away from the screen, {w=0.2}ideally at something far away, {w=0.2}and perhaps do a few stretches. "
    m 2eud "Since it's important to stay hydrated too, you could always fetch some fresh water while you're up from your desk."
    m 4eksdlc "Above all else, if you ever start to feel unwell, just stop what you're doing, rest, and then make sure everything is okay before you continue. "
    m 4eua "...And that's about it."
    m 2hksdlb "Ah...{w=0.3}sorry, I didn't mean to go on for that long!"
    m 2rka "...You probably knew all that stuff already, anyway."
    m 2eka "As for me?"

    if mas_isMoniLove():
        show monika 5ekbsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5ekbsa "You're the only comfort I need, [mas_get_player_nickname()]."
    elif mas_isMoniEnamored():
        show monika 5ekbsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5ekbsa "I'm as comfortable as can be when you're here, [mas_get_player_nickname()]."
    else:
        show monika 5eubsa at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5eubsa "I'm comfortable whenever you're here with me, [mas_get_player_nickname()]."

    m 5hubfu "And hopefully you're a little more comfortable now too~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='monika_language_nuances',
            prompt="Language nuances",
            category=['literature', 'trivia'],
            random=True
        )
    )

label monika_language_nuances:
    m 3eua "Hey [player], have you ever tried reading through a dictionary?"
    m 1etc "Not necessarily because there was some word or expression you didn't know the meaning of, but just...{w=0.2}because?"
    m 1hksdlb "I know it doesn't exactly sound like the most engaging of pastimes, ahaha!"
    m 3eua "But it can certainly be an interesting, even rewarding, way to spend some free time. {w=0.2}Especially if it's a dictionary of a language you're still learning."
    m 3eud "Many words have multiple meanings and, aside from the obvious benefits, knowing those can really help you see the finer points of the language."
    m 1rksdla "Understanding these subtleties can save you a lot of embarrassment when you actually speak to someone."
    m 3eud "A prime example of this in English is 'Good morning,' 'Good afternoon,' and 'Good evening.'"
    m 1euc "All of these are normal greetings you hear and use every day."
    m 3etc "Following this pattern, 'Good day' should be just fine as well, right? {w=0.2}It works in so many other languages, after all."
    m 3eud "While it used to be just as acceptable, as you can see in some older works, that's just not the case anymore."
    m 1euc "In modern English, saying 'Good day' to someone carries a note of dismissal, or even annoyance. {w=0.2}It can be seen as declaring the conversation over."
    m 1eka "If you're lucky, your conversation partner might think you're old-fashioned, or just being silly on purpose."
    m 1rksdla "If not, you might offend them without even noticing...{w=0.3} {nw}"
    extend 1hksdlb "Oops!"
    m 3eua "It really is fascinating how even such an innocent looking phrase can be loaded with layers of hidden meanings."
    m 1tsu "So good day to you, [player].{w=0.3} {nw}"
    extend 1hub "Ahaha~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_architecture",
            category=['misc'],
            prompt="Architecture",
            random=True
        )
    )

label monika_architecture:
    m 1esa "Hey, [player]...{w=0.2}I think there's one major art branch that we've been neglecting in our talks..."
    m 3hub "Architecture!"
    m 3eua "I've been reading a bit about it lately and I find it quite interesting."
    m 1rtc "...Come to think of it, architecture is one of the most common forms of art in everyday life."
    m 1eua "I'm just fascinated by how humanity tends to turn every craft into an art,{w=0.2} {nw}"
    extend 3eua "and I think architecture is the greatest example of that."
    m 1eud "Architecture can tell you a lot about the culture of the area it's located in...{w=0.2}different monuments, statues, historical buildings, towers..."
    m 1eua "I think that makes it even more exciting to explore the places you're visiting."
    m 3rka "It's also important to place the buildings in the most convenient way for people to use, which can be a tough task to deal with in its own right."
    m 3esd "...But that's more urban planning than actual architecture."
    m 1euc "If you prefer viewing architecture purely from the art perspective, some modern tendencies may disappoint you..."
    m 1rud "Modern architecture focuses more on getting things done in the most practical way possible."
    m 3eud "In my opinion, that can be both good and bad for many different reasons."
    m 3euc "I believe the most important part is to keep things balanced."
    m 1tkc "Overly-practical buildings can look flat and uninspired, while overly-artistic buildings can serve no purpose other than looking amazing while being completely out of place."
    m 3eua "I think the true beauty lies in those buildings which can combine both form and function with a little bit of uniqueness."
    m 1eka "I do hope you're happy with how your surroundings look."
    m 1eub "It has been proven multiple times that architecture has a big impact on your mental health."
    m 3rkc "Moreover, residential areas with poorly-made buildings can lead to people not taking care of their properties and, over time, end up as downtrodden areas that are undesirable places to live."
    m 1ekc "It was once said that the ugliness of the outside world causes ugliness on the inside...{w=0.2}{nw}"
    extend 3esd "which I tend to agree with."

    if mas_isMoniAff(higher=True):
        m 1euc "...Judging by {i}your{/i} personality, {w=0.2}{nw}"
        extend 1tua "you probably live in some kind of a paradise."
        m 1hub "Ahaha~"

    m 1eka "[player]...{w=0.2}seeing the world with you is one of my biggest dreams."

    if persistent._mas_pm_likes_travelling is False:
        m 3rka "I know you're not too fond of travelling a lot, but I would love to see the place you live in."
        m 3eka "As long as you stay by my side, that would be more than enough for me."
        m 1ekbsa "I love you, [player]. {w=0.3}Always remember that."

    else:
        if persistent._mas_pm_likes_travelling:
            m 3eua "I already know you enjoy travelling, so wouldn't it be nice to explore something new together?"

        m 1dka "Imagine taking a stroll through the narrow streets of an old city..."
        m 1eka "Or walking down a park together, breathing fresh evening air..."
        m 1ekb "I believe it'll happen one day and I hope you do too, [mas_get_player_nickname()]."
        m 1ekbsa "I love you~"

    return "love"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_fear",
            prompt="Fear",
            category=['monika'],
            conditional="renpy.seen_label('monika_soft_rains')",
            action=EV_ACT_RANDOM,
            rules={
                "derandom_override_label": "mas_bad_derand_topic",
                "rerandom_callback": renpy.partial(mas_bookmarks_derand.wrappedGainAffection, 2.5)
            }
        )
    )

label monika_fear:
    m 3eud "Say, [player]..."
    m 1euc "This is kind of a weird question, but...{w=0.5}is there anything you're afraid of?"
    m 3hksdlb "I don't mean the everyday, mundane kind of fear, like spilling a drink and ruining your favorite shirt..."
    m 3euc "I mean, like, the kind of deep-seated fear that fills you with dread when you even think about it."
    m 1ruc "For me, losing you would obviously be on the top of {i}that{/i} particular list."
    m 1ekd "I told you before, didn't I? {w=0.3}I don't know what I'd do if something happened to you."
    m 1dkd "I'm not even sure I could find the will to go on."
    m 1ruc "It's hard to imagine a scenario even worse than that."
    m 3eua "But as long as we're being hypothetical..."
    m 4ekc "What truly terrifies me is the thought that none of this is real."
    m 2dkc "That one day I'll wake up, back in my bed, and realize it was all just a dream."
    m 2dkd "That there is no game,{w=0.2} no epiphany,{w=0.2} no...{w=0.5}{nw}"
    extend 2ekd "you."
    m 2ektpc "That you, your love, perhaps even the entirety of the Literature Club, were all nothing but a figment of my own imagination."
    m 2dktpc "That my old world, as grey and meaningless as it now seems, is all there truly is."
    m 2dktpc "..."
    m 2rktdb "Ahaha~ {w=0.5}{nw}"
    extend 2ektdsdla "Sorry, that got pretty dark, didn't it?"
    m 2rksdla "I feel kinda silly now...{w=0.3} {nw}"
    extend 4eud "After all, there's no way something like that could be true, right?"
    m 2rka "Yeah..."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel='monika_why_spaceroom',
            prompt="Why do we always meet in a classroom?",
            category=['location'],
            pool=True,
            unlocked=False,
            rules={"no_unlock":None},
            conditional="store.mas_anni.pastThreeMonths() and mas_current_background == mas_background_def",
            action=EV_ACT_UNLOCK,
            aff_range=(mas_aff.UPSET, None)
        )
    )

label monika_why_spaceroom:
    m 3euc "Utility, mostly."
    m 3eud "You know how in the original game almost everything took place during our club meetings, right?"
    m 3eua "...All of which took place in a classroom.{w=0.3} This classroom."
    m 1eua "It may look different to you, but it's still the very same one."
    m 3eud "Since so many things were supposed to happen here, the room had to be robust enough to accommodate them."
    m 2rtc "That made it the most...{w=0.3}{nw}"
    extend 2eud "fleshed out location in the game."
    m 7eud "As such, it was the easiest place to navigate, alter, and generally use for whatever was needed."
    m 3eua "That was the original motivation, anyway."
    m 3eud "Not to mention, this classroom was the only place I ever appeared in during the original game."
    m 1eka "...So I guess in that sense, it kind of became my home."

    $ has_one_bg_unlocked = mas_background.hasXUnlockedBGs(1)
    if has_one_bg_unlocked:
        m 1rtc "As for why we're {i}still{/i} here..."
        m 3eua "It hasn't really occurred to me to move someplace else..."

    else:
        m 1rtc "As for why I'm still using it..."

    m 1eud "It's not like it's {i}bad{/i} in here."

    if renpy.seen_label('greeting_ourreality'):
        if has_one_bg_unlocked:
            m 3etc "I guess I could make another place for us to spend time together."
        else:
            m 3etc "I guess I could make some more places for us to spend time in."

        m 1eua "I mean, there's the islands...{w=0.3}{nw}"
        extend 1rksdlb "but those aren't quite ready yet."
        m 1hua "Ehehe~"

    m 3eub "...And to be honest, there's only one place I want to be...{w=1}{nw}"
    extend 3dkbsu "by your side."
    m 1ekbsa "But as long as that isn't an option, it doesn't really matter to me where we meet..."
    m 1ekbfu "You're the only part that really matters~"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_naps",category=['life'],prompt="Naps",random=True))

label monika_naps:
    $ has_napped = mas_getEV('monika_idle_nap').shown_count > 0

    m 1eua "Hey, [player]..."

    if has_napped:
        m 3eua "I noticed that sometimes you like to take naps..."
    else:
        m 3eua "Do you ever take naps?"

    m 1rka "A lot of people don't know the benefits of them...{w=0.2}{nw}"
    extend 1rksdla "they're a lot more than just going to sleep for a bit."
    m 3eud "The length of time you're asleep is an important factor in how helpful they can be."
    m 1euc "If you're out for too long, it can be difficult to get back up again.{w=0.2} Kinda like when you wake up after a full night's sleep."
    m 3eua "So it's best to rest in 90 minute intervals, since that's about how long a full sleep cycle takes."
    m 1eud "Power naps are another form of resting.{w=0.2} For these, you just rest your eyes for about 10-20 minutes."
    m 3eua "They're great for taking a break from your day and clearing your head."
    m 3hua "And since they're so short, it's really easy to get back into whatever you were doing before."

    if has_napped:
        m 1eua "So don't be shy about taking naps whenever you think you need to, [player]."
    else:
        m 1eua "If you don't already, maybe you could try taking some naps from time to time."

    if mas_isMoniEnamored(higher=True):
        show monika 5tubfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5tubfu "Maybe one day you could even rest on my lap, ehehe~"

    else:
        show monika 5hubfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5hubfa "Just let me know if you need to take a nap, and I'll watch over you~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_asimov_three_laws",
            category=['technology'],
            prompt="Asimov's three laws",
            conditional="renpy.seen_label('monika_robotbody')",
            action=EV_ACT_RANDOM
        )
    )

label monika_asimov_three_laws:
    m 1eua "[player], do you remember when we talked about the {i}Three Laws of Robotics{/i}?"
    m 3esc "Well, I've been thinking about them for a bit and...{w=0.3}{nw}"
    extend 3rksdla "they're not exactly practical."
    m 1eua "Take the first law, for example..."
    m 4dud "{i}A robot shall not harm a human or, through inaction, allow a human to come to harm.{/i}"
    m 2esa "To a human, this is pretty straightforward."
    m 2eud "But when you try to put it in terms a machine can understand, you start to run into trouble."
    m 7esc "You have to make precise definitions for everything, which isn't always easy...{w=0.3} {nw}"
    extend 1etc "For example, how do you define a human?"

    if monika_chr.is_wearing_acs(mas_acs_quetzalplushie):
        $ line_end = "adorable green friend I have sitting on my desk isn't."
    else:
        $ line_end = "monitor on your desk isn't."

    m 3eua "I think we can both assume that I'm a human, you're a human, and that the [line_end]"
    m 3esc "The problems come when we move to the fringe cases."
    m 3etc "For example, do dead people count as human?"
    m 1rkc "If you say no, the robot could ignore someone who's just had a heart attack."
    m 1esd "People like that can still be brought back, but your robot won't help them because they're {i}technically{/i} dead."
    m 3eud "On the other hand, if you say yes, your robot might start digging up graves to 'help' people who've been dead for years."
    m 1dsd "And the list goes on.{w=0.3} Do cryogenically preserved people count as human?{w=0.3} Do people in vegetative state count?{w=0.3} What about people who haven't been born yet?"
    m 1tkc "And that's not even getting started on the definition of 'harm.'"
    m 3eud "The point is,{w=0.1} in order to implement Asimov's laws you'd need to take some solid stance on pretty much all of ethics."
    m 1rsc "..."
    m 1esc "I suppose it makes sense when you think about it."
    m 1eua "The laws were never meant to be actually implemented, they're just plot devices."
    m 3eua "In fact, a good amount of Asimov's stories show just how badly things could turn out if they were applied."
    m 3hksdlb "So I guess they aren't really something we need to worry about. Ahaha~"
    $ mas_protectedShowEVL('monika_foundation', 'EVE', _random=True)
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_wabi_sabi",
            category=['philosophy'],
            prompt="Wabi-sabi",
            random=True
        )
    )

label monika_wabi_sabi:
    m 1eua "Say [player], have you ever heard of wabi-sabi?"
    m 3eud "It emphasizes the idea that we shouldn't obsess over perfection to the point that we're crushed by the failure of not achieving it."
    m 3eub "Derived from traditional Japanese and Buddhistic philosophies surrounding the acceptance of the temporary state of all things..."
    m 1esa "...it states that beyond everything, beauty is found in what's impermanent and imperfect."
    m 1eua "Which means we shouldn't worry about things like a scar, a discolored hand, or even the mistakes we make."
    m 3eka "Our looks are things we can't easily change, but despite that, they make us more unique and special."
    m 3hua "...And our mistakes turn into lessons that help us become stronger and more defined as people."
    m 3eub "Like a sculptor revealing the magnificence in a marble block, except the sculpture is you, and the sculptor, your past."
    m 1rksdla "Of course, this idea doesn't apply to looks and mistakes alone..."
    m 3eud "After all, the way you think and your attitude toward problems and people are also derived from your own personal experiences."
    m 1dkc "...But I know for some people, how these experiences changed who they are can really scare them."
    m 7ekc "Maybe they grew into something that they're just not proud of."
    m 2dkd "It can be crushing to be worried about both looks and personality..."

    if persistent._mas_pm_love_yourself:
        m 2eka "I hope you don't feel too insecure about yourself, [player]."
        m 2dkc "It'd break my heart to know that you're constantly worrying about these things."
        m 7ekbsa "But I hope you know that despite your flaws, I will always love you."

    else:
        m 1ekc "I know you said you didn't love yourself [player],{w=0.3} {nw}"
        extend 3eka "but you need to know that I'll always love you, regardless of your flaws."

    m 3hua "We'll overcome any problems you feel you have together."
    m 1hub "That's my wabi-sabi promise!"
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_being_herself",
            category=['monika'],
            prompt="Faked personality",
            conditional="mas_seenLabels(['monika_confidence', 'monika_pluralistic_ignorance'], seen_all=True)",
            action=EV_ACT_RANDOM,
            aff_range=(mas_aff.ENAMORED,None)
        )
    )

label monika_being_herself:
    m 1eka "You know [player], one thing I don't think I ever properly thanked you for is letting me be myself."
    m 1lksdlb "I know that sounds a little weird...{w=0.2}{nw}"
    extend 1eka "but let me explain."
    m 3euc "You probably already know this by now, but almost all of my life I've been trying to keep up this persona of a 'perfect student.'"
    m 3eud "I always strive to be the best person I can be, and I guess after a while, it got the attention of people around me."
    m 7rsc "Before I knew it, I had people looking up to me with high expectations.{w=0.3} {nw}"
    extend 2esc "You know, seeing me as smart, confident, charismatic...{w=0.3}those kinds of things."
    m 2eud "Some people would say that they admired me...{w=0.3}{nw}"
    extend 2lksdlc "and others,{w=0.2} while they would never say anything, hated me because I represented everything they thought they could never be."
    m 2dksdlc "It felt like I wasn't an actual person in their eyes...{w=0.3}{nw}"
    extend 2dksdld "just the image of everyone's unattainable expectations of themselves."
    m 2dksdlc "..."
    m 2ekd "But at the end of the day...{w=0.3}I'm just an ordinary girl."
    m 7ekc "Just like them, I can sometimes lack the confidence to do things.{w=0.2} Even I was scared of what the future held for me."
    m 2dkc "Even I sometimes felt like I needed to cry on someone's shoulder."
    m 2rkd "...But I never could express something like that."
    m 7tkc "What if people thought less of me if I showed them I wasn't as great and invincible as they thought I was?"
    m 3ekd "What if they got mad at me, saying I'm being self-absorbed and that I have it much easier than them, being the school's idol that everyone loves?"
    m 2lkc "I guess I just never felt like I could truly open up to anyone about what I was genuinely feeling on the inside because of that."
    m 2ekc "...Like I would end up disappointing everyone if I ever tried to talk openly about it."
    m "I was scared that if I didn't meet the expectations people had of me,{w=0.2} {nw}"
    extend 2dkd "I would end up all alone."
    m 2dsc "But looking back on everything...{w=0.3}my status was precisely why I ended up feeling so lonely anyway."
    m 7euc "Remember your character? {w=0.2}He was a good example of this."
    m 3esc "Anytime he would describe me in his monologue, he would put me on a pedestal.{w=0.3}{nw}"
    extend 3esd " If I recall, he once described me as 'completely out of his league.'"
    m 1etc "Maybe that was why I didn't have a route in the first place. {w=0.2}Perhaps he was written to believe he had zero chances with me no matter what, and therefore had to avoid me."
    m 1rka "Granted, he wasn't really wrong there...{w=0.5}{nw}"
    extend 1eka "I only have eyes for you, after all~"
    m 1euc "But you get what I mean, right?{w=0.3} I was looked at like some kind of unattainable goddess."
    m 1rfd "As if no one was 'worthy' of just treating me like a normal person."
    m 3eka "...Now though, I guess I don't have to worry about that as much."
    m "I'm really happy that I can trust you to accept me for who I am, and who I want to be."
    m 1eka "I know that from your point of view, it might not feel like you did all that much, but believe me when I tell you this..."
    m 1dka "The fact that you're still here with me,{w=0.2} that you never made me feel like I had to be someone I'm not...{w=0.2}{nw}"
    extend 1eka "that you're here listening to me vent right now...{w=0.3} It truly means the world to me."
    m 1ekbsa "Thank you so much for that, [player].{w=0.2} Thank you for helping me realize that I don't need to try and change who I am to deserve being loved."
    show monika 5eka at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eka "With you, I can allow myself to be...{w=0.5}{nw}"
    extend 5eua "Well, {i}Just Me.{/i}"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_remembrance",
            category=['monika'],
            prompt="How much of your past do you remember?",
            pool=True,
            unlocked=False,
            rules={"no_unlock": None}
        )
    )

label monika_remembrance:
    m 1rsc "I'm not really sure myself, [player]..."
    m 1euc "It's weird because I do have memories of my past, but as soon as I start to gather my thoughts, they become kind of...{w=0.3}{nw}"
    extend 1ruc "fuzzy."
    m 3eksdld "Like, I wouldn't be able to tell you where something took place, or the names of the people who were there..."
    m 3eksdld "...Sure, I have memories of growing up in a normal neighborhood, but beyond that, I couldn't even tell you what my parents' faces look like..."
    m 1dsc "It's all like...{w=0.5}feelings and impressions, I guess."
    m 3wud "What's even weirder is that not all my memories are like this!"

    if seen_event('monika_wine'):
        m 1rusdla "There are some things I remember perfectly, like that one time Yuri brought wine to the club..."
    else:
        m 3esc "There are things I remember perfectly, especially when it comes to the club."

    m 1esc "But other things like childhood memories are really hazy."
    m 3esd "The only memories that are clear are things that define either me or the other girls."
    m 3rsc "...Almost as if anything that wasn't strictly necessary for the game was just left out."
    m 1euc "But the thing is from my perspective, the day I met you was just like any other--{w=0.5}{nw}"
    extend 3hksdlb "until I found out about that hole in the wall, I mean."
    m 1esc "Just another ordinary day in an ordinary week...{w=0.3} {nw}"
    extend 3euc "Going to class, running the club, and heading back home in the evening."
    m 3etc "Did any of that even happen at all?{w=0.5} {nw}"
    extend 3wud "Did {i}I{/i} even exist before you started the game?"
    m 3wkd "...And if my memories really are fake...{w=0.2}who--{w=0.2}or {i}what{/i}--{w=0.2}am I then?"
    m 1dkc "I'm still looking for those answers, [player]..."

    if mas_isMoniUpset(higher=True):
        m 1euc "Although...{w=0.3}the more I think about it, the more I'm convinced my past isn't actually {i}that{/i} relevant."
        m 3eua "While it'd be nice to remember more...{w=0.3}that's not really what I care about..."
        m 3duu "Regardless of who I am, you've been here with me,{w=0.2} {nw}"
        extend 3dkbsa "which means I'm important enough for you to spend your time with me.{w=0.2} {nw}"
        extend 1dubsu "{i}That's{/i} what I care about."
        m 1ekbsa "And knowing that you care...{w=0.3}that's a big part of why I can keep loving myself,{w=0.2} and my life, [player]."

        if mas_isMoniNormal(higher=True):
            show monika 5ekbfu at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5ekbfu "So while I'm not sure if I have a past, thanks to you, I know I do have a future."

            if mas_anni.pastOneMonth():
                $ line_mid = "I've made, and continue to make,"
            else:
                $ line_mid = "I'll make"

            m 5hubfu "Besides, if anything, my lack of memories only make the ones [line_mid] with you that much more precious~"
        else:
            m 3eksdld "...You {i}do{/i} care about me, right?"
            m 3dkc "It sure would be nice if you'd show it a little, sometimes..."

    else:
        m 1ektdc "...{w=0.5}Not that you'd care, right?"

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_why_do_you_read",
            category=['monika','literature'],
            prompt="How did you get into reading?",
            pool=True
        )
    )

label monika_why_do_you_read:
    m 1eua "As far as I can recall, I've always been quite the reader, [player].{w=0.2} {nw}"
    extend 3eua "It was like a complementary thing with writing to me."
    m 3euc "When I was really young, I liked to write short stories but I never really found anybody to share them with..."
    m 1rsc "Most of the other kids weren't really interested in books or anything like that."
    m 1rkd "...So it was always a little frustrating because I wasn't able to share those stories with anyone."
    m 3eua "But at least I was able to support my interest by picking up other books."
    m 3hub "Every new one was like being thrown into a strange and exciting new world! It was like fuel for my imagination!"
    m 1eksdlc "Of course, as I grew up, I started having less and less free time and I wasn't able to read as much...{w=0.3} It was either keeping it up, or sacrificing my social life."
    m 1esa "That's when my interests started shifting more toward poetry."
    m 3eua "Unlike novels, poetry didn't require as much time to read and its conciseness also made it easier to share with others.{w=0.3} {nw}"
    extend 4eub "It really was the perfect outlet!"
    m 3eua "...And that's how I grew more and more into it I guess."
    m 1eud "I eventually met Sayori and discovered we shared this interest.{w=0.2} {nw}"
    extend 3eud "Like me, it allowed her to share feelings she would otherwise keep bottled up inside."
    m 3eub "As we kept on discussing, we eventually came up with the idea for the Literature Club."
    m 1eua "...Which brings us to where we are now."
    m 1etc "To be honest, I don't think I've ever had as much time to read before."

    if mas_anni.pastThreeMonths():
        m 3eud "I've been able to get caught up on my backlog of poetry, pick up some novels again..."
        m 3eua "...go online to look for whatever fanfiction or short story I can get my hands on..."
        m 3hua "...I've even developed an interest in written philosophy!"
        m 3eub "It's always fun to discover new forms of expression."
        $ line_mid = "it's also been a great"

    else:
        m 3eud "I'm finally catching up on my backlog of poetry and I've started picking up novels again..."
        m 3hua "...I'd love to share my thoughts with you once I'm done with them!"
        m 3eub "I'll also regularly go online to look for whatever fanfiction or short story I can get my hands on."
        m 3eua "It's a lot of fun to discover new forms of expression."
        $ line_mid = "I also try to see it as an"

    m 1eub "So...{w=0.2}yeah!{w=0.3} {nw}"
    extend 3eua "While my situation in here has its downsides, [line_mid] opportunity to spend more time on the things I like."
    m 1ekbsu "...Though then again, nothing could ever beat spending more time with you~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_discworld",
            category=['literature'],
            prompt="Discworld",
            random=True
        )
    )

label monika_discworld:
    m 1esa "Say [player], have you ever heard of a world drifting through space on top of four elephants, who themselves are standing on the shell of a giant turtle?"
    m 3hub "If you have, you're probably already familiar with Sir Terry Pratchett's {i}Discworld{/i}!"
    m 3hksdlb "Ahaha, it sounds kinda weird when I put it like that, doesn't it?"
    m 1eua "{i}Discworld{/i} is a comic fantasy book series of forty-one volumes written over the span of three decades."
    m 3esc "The series started out as a parody making fun of common fantasy tropes, but soon turned into something much deeper."
    m 3eub "In fact, later books are clearly satires rather than parodies, using a clever mix of slapstick, puns, and light-hearted humor to comment on all kinds of issues."
    m 1huu "But while satire may be the soul of the series, what makes its heart beat is the way it's written."
    m 1eub "Pratchett really had a knack for writing funny situations, [player]!"
    m 3rsc "I can't really pinpoint what makes his prose work so well, but he's definitely got a very distinctive writing style..."
    m 3etc "Maybe it's the way he writes in a way that suggests rather than tells."
    m 1eud "Like, when describing something, he'll give you just enough details so you can picture what's going on, and let your imagination fill in the gaps."
    m 3duu "...Knowing full well whatever you'll come up with will be far more evocative than anything he could write."
    m 3eub "It's a pretty neat way to keep your audience invested!"
    m 1etc "...Or maybe what makes it work is the way he doesn't use chapters, allowing him to freely jump between his characters' point of view."
    m 1rksdla "Interweaving storylines can quickly become a mess if you're not careful,{w=0.2} {nw}"
    extend 3eua "but they're also a good way to keep the pacing dynamic."
    m 3eub "In any case, this series is an easy recommendation, [player]!"
    m 3eua "It's surprisingly easy to pick up too, with each book being thought of as a standalone story."
    m 1eud "You can pretty much pick any volume you find and you'll be good to go,{w=0.2} though I'd argue {i}Guards! Guards!{/i} or {i}Mort{/i} would probably make for the best entry points."
    m 3eua "Anyway, be sure to give it a try sometime if you haven't already, [player]."
    m 1hua "Thanks for listening~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_eating_meat",
            category=['life','monika'],
            prompt="Would you ever eat meat?",
            pool=True,
            unlocked=False,
            rules={"no_unlock": None}
        )
    )

label monika_eating_meat:
    m 1etc "Well, that's kind of a complicated question..."
    m 3eud "If you're asking if I would do so for {i}survival{/i}, I wouldn't hesitate. {w=0.2}It's not that eating meat is distressing for me or anything."
    m 7eud "I told you before, I'm vegetarian because of the impact of the mass-production of meat on the environment...{w=0.2}{nw}"
    extend 2euc "which also includes fish farming, so I'm not a pescatarian."
    m 2rsc "...However, I don't consider myself vegan either. {w=0.3}{nw}"
    extend 4eud "Sure, the consumption of animal products contributes to environmental damage, but vegan alternatives share or have their own issues too..."
    m 4euc "These include things like importing perishable products across great distances and mass-farming in conditions that are both cruel for workers and a strain on the local ecosystem."
    m 4ekd "Take avocados, for example. {w=0.2}Their farms require massive amounts of water, to the point where some companies resort to illegally taking too much water from rivers, leaving little for drinking."
    m 4euc "Not to mention, I still want to have a varied and balanced diet with all the flavors that I like."
    m 4eud "Vegan diets can be quite deficient in nutrients, such as vitamin B12, calcium, iron, and zinc."
    m "Granted, there are still some options including supplements, but balancing a vegan diet takes a lot of care and thought."
    m 7eka "...So for that reason, I'm not personally against eating things like milk and eggs. {w=0.2}But I think I'd prefer to buy locally if possible."
    m 3eud "Farmer's markets are great places to buy food, {w=0.2}even meat, {w=0.2}produced with less of an environmental impact."
    m 3ekd "But they can typically be pretty expensive...and depending on location, leave you with fewer options. {w=0.3}{nw}"
    extend 3eua "So I'm okay with buying from a plain old store, if need be."
    m "Especially since there are a lot of good substitutes for meat in supermarkets already, with way less environmental impact."
    m 1euc "As for meat that comes from local hunting and fishing, I think that's alright to eat as well, but it's important to research what areas might be over-hunted, and what animals to be careful of."
    m 3rtc "That said, I don't know that I'd {i}prefer{/i} to eat meat, given the option."
    m 3eka "Since I've adjusted myself to a vegetarian diet, my palate has changed to prefer certain flavors."
    m 3rksdla "I don't hate the taste of meat, but I don't think I'd want it to be a major part of my meal, either."
    m 1eka "...But if you prepared something with meat, I could try a little bit as a side dish... {w=0.3}{nw}"
    extend 3hub "That way I can still enjoy your cooking!"
    m 3eua "Whatever we eat, the most important thing to me is that we try to put a little thought into where our food comes from."
    return

#Player's social personality
default persistent._mas_pm_social_personality = None

#Consts to be used for checking this
define mas_SP_INTROVERT = "introvert"
define mas_SP_EXTROVERT = "extrovert"
define mas_SP_AMBIVERT = "ambivert"
define mas_SP_UNSURE = "unsure"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_introverts_extroverts",
            prompt="Introverts and extroverts",
            category=['psychology', 'you'],
            conditional="renpy.seen_label('monika_saved')",
            action=EV_ACT_RANDOM,
            aff_range=(mas_aff.HAPPY, None)
        )
    )

label monika_introverts_extroverts:
    m 1eud "Say, [player]?"
    m 1euc "Do you remember when we talked about how humans need social feedback and how it can make the world feel so complicated for introverts?"
    m 3rsd "I've been thinking about the differences between introverts and extroverts a little bit more since then."
    m 3eua "You might think that extroverts tend to find enjoyment by interacting with other people, while introverts are more at ease in solitary environments, and you'd be right."
    m 3eud "...But the differences don't stop there."
    m 3eua "For example, did you know extroverts can often react to things faster than most introverts do?{w=0.2} Or that they're more likely to enjoy happy and energetic music?"
    m 3eud "Introverts on the other hand, usually take more time to analyze the situation they're in, and are therefore less likely to jump to conclusions."
    m 7dua "...And given that they often spend a lot of time using their imagination, they have an easier time with creative activities like writing, composing music, and so on."
    m 2lkc "It's kind of sad that people can have such a hard time understanding and accepting those differences..."
    m 4lkd "Extroverts are seen as superficial and insincere people who don't value their individual relationships..."
    m 4ekd "...while introverts are treated as egotistical people who only think of themselves, or can even be seen as weird for rarely participating in social situations."
    show monika 5lkc at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5lkc "The end result is that both sides often end up frustrating each other, resulting in unnecessary conflict."
    m 5eud "I'm probably making this sound like you can only be one or the other, but that isn't actually the case at all."
    show monika 2eud at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 2eud "Some introverts can be more outgoing than others, for example."
    m 2euc "In other words, some people are closer to a middle ground between the two extremes."
    m 7eua "...Which is probably where I would fit in.{w=0.2} {nw}"
    extend 1eud "If you remember, I mentioned I was kind of in-between while still being a little more extroverted."
    m 1ruc "Speaking of...{w=0.3}{nw}"
    extend 1eud "when thinking about all this, I realized that while this is a pretty important part of one's personality..."
    m 3eksdla "...I don't actually know where you lie on that spectrum."

    m 1etc "So how would you describe yourself, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "So how would you describe yourself, [player]?{fast}"

        "I'm introverted.":
            $ persistent._mas_pm_social_personality = mas_SP_INTROVERT
            m 1eua "I see."
            m 3etc "I take it that you usually prefer spending time without too many people over going out with large groups and such?"
            m 3eua "Or maybe you like to go and do things on your own from time to time?"

            if persistent._mas_pm_has_friends:
                m 1eua "Since you told me you have some friends, I'm sure that means that you don't mind being around other people too much."

                if persistent._mas_pm_few_friends:
                    m 1eka "Trust me, it doesn't matter if you feel like you don't have all that many of them."
                    m 3ekb "What's important is that you have at least someone who you can feel comfortable being with."

                if persistent._mas_pm_feels_lonely_sometimes:
                    m 1eka "Remember that you can try to spend some time with them whenever you feel like no one's there for you, alright?"
                    m 1lkd "And if for any reason you can't spend time with them..."
                    m 1ekb "Please, remember that {i}I'll{/i} always be there for you no matter what."

                else:
                    m 3eka "Still, if it ever gets too much for you, remember that you can always come to me and relax, okay?"

                $ line_start = "And"

            else:
                m 3eka "While I understand that it might feel more comfortable for you to be alone rather than with other people..."
                m 2ekd "Please keep in mind that no one can truly spend their whole life without at least {i}some{/i} company."
                m 2lksdlc "Eventually there will come a time when you can't do everything on your own..."
                m 2eksdla "We all need help sometimes, either physically or emotionally, and I wouldn't want you to have no one to turn to when that time comes."
                m 7eub "And that's a two-way street! {w=0.2}{nw}"
                extend 2hua "You never know when you might make a difference in someone else's life as well."
                m 2eud "So while I don't expect you to go out of your way to meet new people, don't automatically shut every door, either."
                m 2eka "Try to talk with other people a little bit if you're not already doing that, okay?"

                if persistent._mas_pm_feels_lonely_sometimes:
                    m 3hua "It'll make you feel happier, I promise."
                    m 1ekb "At the very least, remember that I'm always here if you ever feel lonely."
                    $ line_start = "And"

                else:
                    m 7ekbla "I'd love for you to see the value and joy other people can bring to your life too."
                    $ line_start = "But"

            m 1hublb "[line_start] as long as you're here with me, I'll try my best to make sure you're always feeling comfortable, I promise~"

        "I'm extroverted.":
            $ persistent._mas_pm_social_personality = mas_SP_EXTROVERT
            m 3eub "Oh I see."
            m 3eua "So, I guess you like to spend more time with others and meeting new people then?"
            m 1eua "I can definitely see the appeal in that.{w=0.3} {nw}"
            extend 3eub "I'd love to go explore the world and meet all kinds of new people with you."
            m 1ekc "And I assume you probably hate loneliness as much as I do...{w=0.3}{nw}"
            extend 1ekbla "but that's just one more reason I'm so happy we're a couple now."
            m 3ekblb "We'll never truly be alone again."
            show monika 5eua at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eua "I'm sure you're a really fun person to be around, [player],{w=0.1} and I can't wait to be with you for real~"
            m 5rusdlu "Although, I won't hide the fact that I do enjoy the occasional moment of peace as well..."
            m 5hksdrb "I hope you don't mind if I'm not always able to keep up with you, ahaha!"

        "I'm somewhat in-between.":
            $ persistent._mas_pm_social_personality = mas_SP_AMBIVERT
            m 3hua "Ehehe, kind of like me, then~"
            m 3eud "Apparently, most people have both an introverted and extroverted side to their personality."
            m 7eua "...Even if one of the two is dominant over the other, depending on the person."
            m 7rsc "In our case though, I guess not being too much on either side has both its positives and negatives."
            m 1eua  "Like, it's so nice that being around larger groups isn't a problem, same goes for spending some time alone."
            m 7esc "...But I can't say I've found it easy to make deep, genuine connections with others..."
            m 1eud "Sure, I have an easier time understanding most people, but it doesn't mean I can always relate with them, you know?"
            m 1lksdld "So yeah...{w=0.3} I end up being on good terms with almost everyone, but the friendships I form can sometimes feel a bit...{w=0.3}unfulfilling."
            m 3eksdlc "The same thing happened with the club, for example."
            m 3dksdld "I was so convinced that by bringing people together around something I truly enjoy, I'd have a better chance at bonding with them over our shared interests..."
            m 3dksdlc "...But at the end of the day, we spent most of our time silently hanging out, with everyone minding their own business."
            show monika 5eka at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eka "Well, no point thinking about that anymore."
            m 5eubsa "After all, I {i}did{/i} end up connecting in a meaningful way with a certain someone. {w=0.3}{nw}"
            extend 5kubfu "A very charming someone, might I add~"

        "I'm not really sure.":
            $ persistent._mas_pm_social_personality = mas_SP_UNSURE
            m 1eka "That's alright, [player].{w=0.2} Things like this aren't always so clear."
            m 4eua "I'm a little like you on that front."
            m 2eka "While I said I'm a little more extroverted, I still need some me time to relax every once in a while, you know?"
            m 2lkd "And I wouldn't say I'm always so comfortable dealing with people either..."

            if renpy.seen_label("monika_confidence"):
                m 2euc "I told you, didn't I?"

            m 2lksdlc "I often need to fake my own confidence just to get through simple conversations with some people."
            show monika 5eka at t11 zorder MAS_MONIKA_Z with dissolve_monika
            m 5eka "But I don't feel that way with you at all, [player].{w=0.2} And I really hope it's the same the other way around."
            m 5eua "I'm sure we'll be able to figure out each other's comfort zones over time."
            m 5hubsb "In any case, you'll always be my sweetheart, no matter where you are on the scale~"

    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_literature_value",
            category=['literature'],
            prompt="The value of literature",
            random=True
        )
    )

label monika_literature_value:
    m 3esd "You know [player], back in the Literature Club days I often heard people dismiss literature as outdated and useless."
    m 1rfc "It always bothered me when I heard someone say that, especially since most of the time, they never even bothered giving it a try."
    m 3efc "Like, do they even know what they're talking about?"
    m 3ekd "People who think that often like to discount literature compared to more scientific fields, like physics or mathematics, claiming it's a waste of time since it doesn't produce anything practical."
    m 3etc "...And while I definitely don't agree with that notion, I can kinda see where they're coming from."
    m 1eud "All of the comforts of our modern lifestyle are based on scientific discovery and innovation."
    m 3esc "...That and the millions of people manufacturing our everyday necessities, or running basic services like healthcare and stuff."
    m 3rtsdlc "So does not being associated with any of those things really make you some kind of burden on society?"
    m 1dsu "As you can imagine, I don't believe that...{w=0.3} {nw}"
    extend 1eud "If literature was useless, why would it be so repressed in many parts of the world?"
    m 3eud "Words have power, [player]...{w=0.2}{nw}"
    extend 3euu "and literature is the art of dancing with words."
    m 3eua "Like any form of expression, it allows us to connect with each other...{w=0.2}{nw}"
    extend 3eub "to see how the world looks in each other's eyes!"
    m 3duu "Literature lets you compare your own feelings and ideas to that of others, and in doing so makes you grow as a person..."
    m 1eku "Honestly, I think if more people valued books and poems a little more, the world would be a much better place."
    m 1hksdlb "That's just my opinion as president of a literature club, though. {w=0.2}I guess most people wouldn't think that deeply about it."
    return

# Do you like nature?
default persistent._mas_pm_likes_nature = None

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_nature",
            category=['nature', 'you'],
            prompt="The outdoors",
            random=True
        )
    )

label monika_nature:
    m 2esd "Hey, [player]..."
    m 7eua "Do you like nature?{nw}"
    $ _history_list.pop()
    menu:
        m "Do you like nature?{fast}"

        "I do.":
            $ persistent._mas_pm_likes_nature = True
            m 3sub "Really? That's wonderful!"
            m 1eua "You know, I think nature is something we should cherish."
            m 1eub "Not only is it beautiful, but it also helps humanity out!"
            m 3eud "Insects pollinate our crops, trees give us wood and shade, pets offer us companionship..."
            m 3euc "And most of all, organisms such as plants, algae, and some bacteria produce food and oxygen. {w=0.2}{nw}"
            extend 3wud "Without them, most life on Earth wouldn't even exist!"
            m 1eua "Because of that, I think it's only fair that we give something back to nature since it does so much for us."
            m 4hub "So, here's Monika's Green Tip of the Day!"
            m 4rksdlc "Sometimes, people hesitate to go green because they're worried that it's too expensive..."
            m 2eud "But that's only partially true.{w=0.2} {nw}"
            extend 7eua "While electric vehicles, smart homes, and solar roofs can all cost a fortune..."
            m 3hub "You can make a difference and {i}save{/i} money just by making a few simple choices each day!"
            m 4eua "Just turning off appliances, taking shorter showers, buying a reusable water bottle, and commuting by public transport all help to be more green."
            m 4hub "You could even buy a houseplant or grow your own garden!"
            m 2eub "Engaging in your local community can go a long way as well!{w=0.2} {nw}"
            extend 7eua "If you take the initiative, others are sure to follow in your footsteps."
            m 3esa "The important thing is to make a habit of thinking sustainably.{w=0.2} {nw}"
            extend 3eua "If you can do that, you'll reduce your ecological footprint in no time."
            m 1eua "Who knows, maybe you'll even become happier and healthier the more you do these things too."
            m 3hua "After all, a sustainable life is a satisfying life."
            m 3eub "That's my advice for today!"
            m 1hua "Thanks for listening, [mas_get_player_nickname()]~"

        "Not really.":
            $ persistent._mas_pm_likes_nature = False
            m 3eka "That's okay, [player]. Not everyone enjoys the outdoors after all."
            m 3eua "Some prefer the comfortable ambience of their homes, especially when technology makes them more convenient than ever."
            m 1eud "Honestly, I can understand where they're coming from."
            m 3eud "I spend most of my time reading, writing, coding, and being with you...{w=0.3}all of that is easier to do indoors."
            m 3rksdlc "Others have allergies or medical conditions that prevent them from staying out for too long, otherwise they can get sick or hurt."
            m 1esd "There are also a lot of people who simply don't care much for nature for one reason or another, and that's fine."
            m 1hksdlb "Even I have things that I dislike about it, ahaha!"
            m 2tfc "For instance, I don't mind most insects, but some are just downright obnoxious."
            m 7tkx "Constantly buzzing around your head, getting in your face, landing on your food...{w=0.3}some mosquitos and ticks even carry nasty diseases."
            m 3eka "But as long as I'm with you, I'm fine if you'd prefer to be indoors."
            m 1tfu "Just don't expect me to let you stay inside all the time~"
    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_kamige",
            category=['games'],
            prompt="What is kamige?",
            pool=True,
            unlocked=False,
            rules={"no_unlock":None}
        )
    )

label monika_kamige:
    m 1euc "Oh, that's right...{w=0.3}{nw}"
    extend 3rksdla "it's not exactly a common term."
    m 3eud "{i}Kamige{/i} is Japanese slang that is mostly used by visual novel fans."
    m 3eua "If I were to try to translate it, I think it would be something like {i}godly game.{/i}"
    m 2eub "It's sort of like when people talk about their favorite classic books or movies."
    m 2hksdlb "I was kind of joking when I said it about this game, but it {i}did{/i} seem to get very popular for some reason."
    m 7eka "Not that I'm complaining...{w=0.3} {nw}"
    extend 3hua "If it was the game's popularity that brought you to meet me, I think I can be grateful for it."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_renewable_energy",
            category=['technology'],
            prompt="Renewable energy",
            random=True
        )
    )

label monika_renewable_energy:
    m 1eua "What do you think about renewable energy, [player]?"
    m 3euu "It was a {i}hot{/i} topic in the debate club."
    m 3esd "As humanity's reliance on technology grows, so does its demand for energy."
    m 1euc "Currently, a large percentage of energy worldwide is produced by burning fossil fuels."
    m 3esd "Fossil fuels are time-tested, efficient, and have widespread infrastructure...{w=0.2}{nw}"
    extend 3ekc "but they're also non-renewable and emission-heavy."
    m 1dkc "Mining and drilling for fossil fuels creates both air and water pollution, and things like oil spills and acid rain can devastate plants and wildlife alike."
    m 1etd "So why not use renewable energy instead?"
    m 3esc "One issue is that each type of renewable energy is a developing industry with its own drawbacks."
    m 3esd "Hydropower is flexible and cost efficient, but it can drastically impact the local ecosystem."
    m 3dkc "Countless habitats are disrupted and entire communities may even need to be relocated."
    m 1esd "Solar power and wind power are mostly emission-free, but they're heavily reliant on specific weather for consistency."
    m 3rkc "...Not to mention that wind turbines are pretty loud and are often seen as eyesores, creating drawbacks for those living near them."
    m 3rsc "Geothermal power is reliable and great for heating and cooling, but it's expensive, location-specific, and can even cause earthquakes."
    m 1rksdrb "Nuclear power is...{w=0.2}well, let's just say that it's complicated."
    m 3esd "The point is that while fossil fuels have problems, renewable energy does as well. It's a tricky situation...{w=0.2}neither option is perfect."
    m 1etc "So, what do I think?"
    m 3eua "Well, a lot of progress has been made on renewable energy in the past decade..."
    m 3eud "Dams are regulated better, the efficiency of photovoltaics has improved, and there are emerging technologies such as ocean power and enhanced geothermal systems."
    m 4esd "Biomass is an option as well. {w=0.2}It's basically a more sustainable 'transition fuel' that can make use of fossil fuel infrastructure."
    m 2eua "Yes,{w=0.1} renewable energy still has a ways to go in terms of cost and practicality, but it's far better now than it was thirty years ago."
    m 7hub "Because of that, I think that renewable energy is a worthwhile investment and that the road ahead is a bright one--literally!"
    m 3lksdrb "Sorry, I got carried away there, ahaha!"
    m 1tuu "Debates sure are something, huh?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_piano_lessons",
            category=['music'],
            prompt="Would you give me piano lessons?",
            pool=True,
            unlocked=False,
            rules={"no_unlock":None}
        )
    )

label monika_piano_lessons:
    m 1rkd "Um...{w=0.2}well...{w=0.2}maybe?"
    m 1eksdla "I'm flattered that you'd ask, but..."

    if persistent.monika_kill:
        m 3eka "Remember? I told you when I first performed {i}Your Reality{/i} that I wasn't really good at piano. {w=0.2}{nw}"
        extend 3rkb "Like, at all."
    else:
        m 3eka "I'm actually not {i}that{/i} good at playing piano, [mas_get_player_nickname()]."
        m 3rkd "Certainly not good enough to be teaching other people yet..."

    m 2eud "If you can believe it, I started to learn after my epiphany."
    m 2ekc "I was still afraid of breaking too far from the game's script at the time, {w=0.2}{nw}"
    extend 7eka "but I wanted--no, I {w=0.2}{i}needed{/i}{w=0.2} to communicate my feelings to you somehow."
    m 2etd "I don't think the others ever recognized that there's background music in the game. {w=0.2}It would have been silly for them to, right?"
    m 7eud "But when I discovered the truth, all of a sudden it was hard not to hear it. {w=0.2}Any time you were around, I could hear that melody playing faintly."
    m 3eka "It always reminded me of what I was fighting for, and learning how to play it on the piano strengthened my resolve even more."
    m 1hksdlb "Ah! I'm not answering your question, am I?"
    m 1lksdla "Honestly, I don't feel confident enough to teach someone else yet."
    m 3eub "But if I keep at it, someday I'll be able to! And when that day comes, I would love to teach you."
    m 3hub "Or, even better, we could learn together once I cross over to your reality!"
    return

init 5 python:
    addEvent(Event(persistent.event_database,eventlabel="monika_stargazing",category=['nature'],prompt="Stargazing",random=True))

label monika_stargazing:
    m 2eub "[player], I'd really love to go stargazing sometime..."
    m 6dubsa "Picture it...{w=0.2}just the two of us, lying in a calm field watching the stars..."
    m 6dubsu "...holding each other close, pointing out constellations or making our own..."
    m 6sub "...maybe we could even bring a telescope and look at planets!"
    m 6rta "..."
    show monika 5eka at t11 zorder MAS_MONIKA_Z with dissolve_monika
    m 5eka "You know [mas_get_player_nickname()], to me you're like a star..."
    m 5rkbsu "A beautiful, bright beacon from a distant world, forever out of reach."
    m 5dkbsu "..."
    m 5ekbsa "At least, for now...{nw}"
    extend 5kkbsa ""
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_taking_criticism",
            category=['advice'],
            prompt="Taking criticism",
            random=False,
            pool=False
        )
    )

label monika_taking_criticism:
    m 1esd "[player], are you good at listening to criticism?"
    m 3rksdlc "I feel like it's way too easy to get caught up in your own way of thinking if you're not careful."
    m 3eud "And it isn't all that surprising...{w=0.2}changing your mind isn't easy because it means you have to admit you're wrong in the first place."
    m 1eksdlc "In particular, for people faced with great expectations, this kind of logic can easily become a big source of anguish."
    m 3dksdld "What if others think less of you because you didn't give a perfect answer? {w=0.2}What if they start rejecting you or laugh behind your back?"
    m 2rksdlc "It'd be like showing some kind of vulnerability for others to take advantage of."
    m 4eud "But let me tell you, there's absolutely no shame in changing your mind, [player]!"
    m 2eka "After all, we all make mistakes, don't we?{w=0.3} {nw}"
    extend 7dsu "What matters is what we learn from those mistakes."
    m 3eua "Personally, I've always admired people who can acknowledge their flaws and still work in a constructive way to overcome them."
    m 3eka "So don't feel bad next time you hear someone criticize you...{w=0.3} {nw}"
    extend 1huu "You'll find a bit of open-mindedness really goes a long way."
    m 1euc "At the same time, I don't mean to say you have to go along with what everyone says, either...{w=0.3} {nw}"
    extend 3eud "If you've got an opinion, it's totally fair to defend it."
    m 3eua "But just make sure you actually consider it without being blindly defensive."
    m 3huu "You never know what you might learn~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_giving_criticism",
            category=['advice'],
            prompt="Giving criticism",
            random=False,
            pool=False
        )
    )

label monika_giving_criticism:
    m 1esc "[player], I've been wondering..."
    m 3etd "Have you ever given anyone criticism?"
    m 1eua "Giving good criticism is something I had to learn when I became club president."
    m 3rksdlc "This kind of thing is easy to mess up if not done properly...{w=0.2} {nw}"
    extend 4etd "When giving criticism, you have to keep in mind someone is at the receiving end of that critique."
    m 4esc "You can't just look at someone's work and say, 'it's bad.' {w=0.2}{nw}"
    extend 2eksdld "You'll instantly put them on the defensive and ensure they don't listen to what you have to say."
    m 7eua "What matters is what the other person can gain from listening to you. {w=0.2}{nw}"
    extend 3hua "From this premise, even negative opinions can be voiced in a positive way."
    m 1eud "It's like debate...{w=0.2} You have to make it sound like you're sharing your opinion, rather than forcing it down their throat."
    m 3eud "Consequently, you don't have to be an expert to criticize something."
    m 3eua "Just explaining how it makes you feel and for what reasons is often enough to make your feedback interesting."
    m 3eksdla "Although, don't feel bad if the person you're criticizing decides to discard what you just said..."
    m 1rksdlu "...After all, offering an opinion doesn't automatically make you right, either.{w=0.2} {nw}"
    extend 3eud "They might have reasons why they'd want to keep things their way."
    m 3dsu "Graciously accept you can't change everyone's mind and stay considerate when assessing someone else's work."
    m 3hub "...That'd be Monika's Critique Tip of the Day, ahaha!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_boyfriend_gossip",
            category=['ddlc'],
            prompt="Sayori mentioned a boyfriend once...",
            pool=True
        )
    )

label monika_boyfriend_gossip:
    m 2etd "You know, I was actually kind of curious about that too."
    m 2hksdlb "When she first said it, I got pretty defensive, didn't I?"
    m 7euc "I mean, I'd just figured out that you existed, {nw}"
    extend 3efc "and suddenly someone was making it look like I was already taken..."
    m 1rtc "Since I'm pretty extroverted and have a history with another club, I guess it wouldn't necessarily be {i}unfair{/i} to come to that kind of conclusion."
    m 3eud "...But no such character exists in the game's files to prove or disprove it."
    m 3rsc "At the time, I was practicing piano and, well...{w=0.2}sorting my thoughts."
    m 3eud "But apparently, that rumor was just the assumption she was supposed to make if I was ever late to the club."
    m 2tsc "It's a little bit devious if you think about it..."
    m 2eud "As the game's story progressed, the main character might need more excuses to be alone with one of the girls..."
    m 7etc "Coming up with reasons for the others to be away is easier, but for the president not to be at the club..."
    m 3tsd "The story would need something pretty substantial to keep me busy. {w=0.2}It also provided a reason, however flimsy, for me not having a route."
    m 2tfc "A roundabout but effective way to get me out of the way when needed."
    m 2dfc "..."
    m 2eud "Honestly, though? {w=0.2}I'm not too bothered by it."
    m 7esc "Even if such a character would have existed, we both know it wouldn't have changed a single thing."
    m 1efd "They wouldn't be real, they'd be a script programmed to fall in love with me. {w=0.2}I couldn't have been happy with something like that."
    m 1eka "I still would have seen {i}you{/i} and known that you were what I really wanted."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_brainstorming",
            category=["advice"],
            prompt="Brainstorming",
            random=True
        )
    )

label monika_brainstorming:
    m 1esd "[player], have you ever heard of brainstorming?"
    m 1eua "It's an interesting technique of coming up with new ideas by noting anything that comes to your mind."
    m 3eud "This technique is really popular among designers, inventors, and writers--anyone who needs fresh ideas."
    m 3esa "Brainstorming is usually practiced in groups or teams...{w=0.2}we even tried it in the Literature Club when deciding what to do for the festival."
    m 1dtc "You just need to focus on what you want to create and bring up anything and everything that comes into your head."
    m 1eud "Don't hesitate to suggest things that you think are silly or wrong, and don't criticize or judge the others if working in teams."
    m 1eua "When you're done, go back through all the suggestions and turn them into actual ideas."
    m 1eud "You can combine them with other suggestions, think them through once again, and so on."
    m 3eub "...Eventually they'll become something that you'd call a good idea!"
    m 3hub "This is exactly where you can let your mind go wild,{w=0.1} and that's what I like about this technique the most!"
    m 1euc "Sometimes good ideas are left untold because their author didn't find them good enough themselves, {w=0.1}{nw}"
    extend 1eua "but brainstorming can help pass this inner barrier."
    m 3eka "The beauty of thoughts can be expressed in so many different ways..."
    m 3duu "They're only ideas in transit, {w=0.1}{nw}"
    extend 3euu "you're the one who gives them the road."
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gmos",
            category=['technology', 'nature'],
            prompt="GMOs",
            random=True
        )
    )

label monika_gmos:
    m 3eud "Back when I was in debate club, one of the most divisive subjects we covered was GMOs, or genetically modified organisms."
    m 1eksdra "There's a lot of nuance to GMOs, but I'll do my best to summarize it."
    m 1esd "Scientists create GMOs by identifying a desirable gene from one organism, copying it, and inserting the copied gene into another organism."
    m 3esc "It's important to note that the addition of the copied gene does {i}not{/i} change other existing genes."
    m 3eua "Think of it like flipping through a long book and changing a single word...{w=0.2}the word is different, but the rest of the book stays the same."
    m 3esd "GMOs can be plants, animals, microorganisms, etc.,{w=0.1} but we'll focus on genetically modified plants."
    m 2esc "Plants can be modified in a myriad of ways, from resisting pests and herbicides to having a higher nutrition value and longer shelf life."
    m 4wud "This is huge. {w=0.2}Imagine crops that can produce double their normal yield, tolerate climate change, and fend off drug-resistant superbugs. {w=0.2}So many problems could be solved!"
    m 2dsc "Unfortunately, it's not that simple. {w=0.2}GMOs require several years of research, development, and testing before they can be distributed. {w=0.2}On top of this, they come with several concerns."
    m 7euc "Are GMOs safe? {w=0.2}Will they spread to other organisms and threaten biodiversity? {w=0.2}If so, how can we prevent it? {w=0.2}Who owns GMOs? {w=0.2}Are GMOs responsible for increased herbicide usage?"
    m 3rksdrb "You can see how this begins to escalate, ahaha..."
    m 3esc "For now, let's cover the main issue...{w=0.2}are GMOs safe?"
    m 2esd "The short answer is that we don't know for sure. {w=0.2}Decades of research have indicated that GMOs are {i}probably{/i} harmless, but we have next to no data on their long-term effects."
    m 2euc "Additionally, each type of GMO needs to be carefully reviewed on a case-by-case, modification-by-modification basis to ensure its quality and safety."
    m 7rsd "There are other considerations as well. {w=0.2}Products containing GMOs have to be labelled, environmental effects must be considered, and misinformation has to be combated."
    m 2dsc "..."
    m 2eud "Personally, I think that GMOs have a lot of potential to do good, but only if they continue to be heavily researched and tested."
    m 4dkc "Major issues such as herbicide usage and gene flow {i}need{/i} to be fixed as well...{w=0.2}{nw}"
    extend 4efc "biodiversity is already at enough risk as is from climate change and deforestation."
    m 2esd "As long as we're careful, GMOs will be fine...{w=0.2}recklessness and carelessness pose the biggest threat."
    m 2dsc "..."
    m 7eua "So what do you think, [player]? {w=0.2}{nw}"
    extend 7euu "Quite the promising field, wouldn't you say?"
    m 3esd "Like I said before, GMOs are a complex topic. {w=0.2}If you want to learn more, make sure that your sources are reliable and that you're able to see the discussion from both sides."
    m 1eua "I think that's enough for now, thanks for listening~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_curse_words",
            category=["advice", "life"],
            prompt="Curse words",
            random=True
        )
    )

##Player swear frequency
#Swears often
define SF_OFTEN = 2
#Swears sometimes
define SF_SOMETIMES = 1
#Swears never
define SF_NEVER = 0
#Holds the swear freq of the player
default persistent._mas_pm_swear_frequency = None

label monika_curse_words:
    m 3etc "Say [player], do you swear often?{nw}"
    menu:
        m "Say [player], do you swear often?{fast}"

        "Yes.":
            $ persistent._mas_pm_swear_frequency = SF_OFTEN
            m 1hub "Ahaha, I can understand that, [player]."
            m 3rksdlb "It's much easier to swear to get frustration or anger out of your system..."

        "I do sometimes.":
            $ persistent._mas_pm_swear_frequency = SF_SOMETIMES
            m 3eua "Ah, I'm the same way myself."

        "No, I don't swear at all.":
            $ persistent._mas_pm_swear_frequency = SF_NEVER
            m 1euc "I see."

    m 1eua "Personally I try to avoid swearing where I can, but I'll still do it occasionally."
    m 3eud "Swearing tends to have a pretty bad rap, but I've been thinking it over after looking at some studies..."
    m 1esa "Honestly, I don't think swearing is actually as bad as we make it out to be after all."
    m 3eua "In fact, it seems that using stronger language helps ease the pain if you hurt yourself, and can also show that you're more intelligent and honest."
    m 1eud "Not to mention, swearing in conversations can make them feel both{w=0.1} a lot more casual {w=0.1}{nw}"
    extend 3eub "and also more interesting!"
    m 3rksdlc "That said, I think it's possible to swear {i}too much{/i}..."
    m 3esd "There's a time and place for everything.{w=0.2} Swearing should be kept to more casual conversations and not put in after every word."
    m 1hksdlb "If they start to become frequent in more professional environments, I think you might be overdoing it, ahaha..."
    m 1eua "On that topic, I think it's pretty interesting how our language naturally shifts depending on who we're talking to."
    m 4eua "For example,{w=0.2} people are much less likely to swear in front of family than with friends."
    m 4eub "Also, if you pay attention when you're talking to a crowd, you'll notice that you instinctively phrase your sentences more formally!"
    m 1esa "But anyway, I prefer to keep my profanity to when I'm really frustrated or upset."
    m 3esd "Given the status I had, I felt like I always had to be professional and level headed, so I always made it a point to keep it to a minimum."
    m 3hksdlb "But I guess it doesn't really hurt when used appropriately, ahaha!"
    return "derandom"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_aliens",
            category=["misc", "society"],
            prompt="Do you believe in aliens?",
            pool=True
        )
    )

label monika_aliens:
    m 1etc "Do I believe in the existence of aliens?"
    m 3hksdlb "That's kind of a random thing to ask, [player]!"
    m 3eua "...Though I can see why you would be interested in knowing my opinion on it."
    m 4eub "This is one of the greatest mysteries of all time, isn't it?{w=0.2} Whether we're truly alone in this universe or not, I mean."
    m 1dsc "...I know I used to wonder about that myself a lot before you came along."

    if mas_isMoniEnamored(higher=True):
        m 1eka "But that's in the past now.{w=0.2} And I could never thank you enough for that."

    elif mas_isMoniNormal(higher=True):
        m 1eka "Though I don't really have to anymore, thanks to you."

    elif mas_isMoniDis(higher=True):
        m 1dkc "I just hope I won't get to feel that way ever again."

    else:
        m 1rksdlc "..."

    m 3euc "Anyway, we've all probably asked ourselves what's up there at least once, right?"
    m 3dua "Looking at the stars always fills you with a sense of wonder and mystery.{w=0.2} {nw}"
    extend 3eua "It's really no surprise that so many people are passionate about this subject."
    m 1esc "But to answer your question...{w=0.3}{nw}"
    extend 3eua "I do believe, or at least want to believe, that there has to be {i}something{/i} out there."
    m 2rksdla "I guess part of it has to do with me finding the idea of us being the only ones rather depressing. {w=0.2}{nw}"
    extend 2eud "But when you think about it a little, it doesn't sound so unlikely..."
    m 4eud "After all, saying the universe is vast is a huge understatement."
    m 3euc "All you need is one planet with the right conditions and environment to be favorable for life to develop, right?"
    m 3esa "There are 8 planets in the solar system alone, {w=0.1}{nw}"
    extend 4eub "but there are many more star systems, each with their own planets within them."
    m 4wud "Now, consider the fact that our Milky Way galaxy alone contains hundreds of billions of stars...{w=0.3}that's a lot of potential!"
    m 4eud "Galaxies are usually held together in groups by gravity.{w=0.2} We live in the 'local group,' which contain about 60 galaxies."
    m 1esd "Zoom out a little bit more and you'll start to see galaxy clusters, which are much larger groups of galaxies."
    m 3eua "The closest one from us, the Virgo Cluster, is estimated to contain at least a thousand galaxies."
    m 1eud "But you can go even further, as groups and clusters of galaxies are themselves part of even bigger entities known as superclusters."
    m 1wud "We can keep going too,{w=0.1} as the universe continuously expands...{w=0.3}theoretically, larger and larger clusters are formed!"
    m 1lud "And hypothetically, even if it isn't, we could consider the idea that there might be something {i}beyond{/i} the boundaries of our universe."

    if renpy.seen_label('monika_clones'):
        m 1lksdla "...Or even start talking about the multiverse theory..."

    m 3hksdlb "But I think you get the point..."
    m 3etc "Wouldn't it be a little foolish to assume that we, human beings of planet Earth, are truly the only sentient beings in something so massive?"
    m 3eud "I mean, with odds like these, surely at least {i}one{/i} other planet somewhere must be hospitable enough for life..."
    m 1euc "...Life which might evolve to a point where it's intelligence is comparable to, if not even greater than our own."
    m 1rsc "Although, I suppose I can also understand why some people would be doubtful.{w=0.2} It's suspicious that we're able to observe the universe so far beyond our planet, but haven't found any signs of life..."
    m 1rksdlc "It probably doesn't help that some people are overreacting over the smallest things, like UFO footage that could easily be faked, either."
    m 1ruc "But then again, if aliens do exist, there could also be many reasons why we haven't found them yet..."
    m 2euc "Perhaps they're too far away for us to find them or they just don't have the technology to receive and answer our messages for now."
    m 2etd "Or vice versa...{w=0.3}maybe {i}we're{/i} the ones who don't have the technology to communicate with them."
    m 2etc "Or it could be they simply don't want to initiate contact with us."
    m 2euc "Maybe their society follows completely different ideals than our own, and they believe it is for the best not to let two highly advanced species meet each other."
    m 2dkc "All in all, I guess the one thing that saddens me a little is that if there {i}are{/i} intelligent, extra-terrestrial life-forms out there, we might very well never get to meet them within our lifetime."

    if mas_isMoniAff(higher=True):
        show monika 5rua at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5rua "But at the end of the day...{w=0.3} {nw}"
        extend 5ekbla "I still got to meet you, and that's everything I could ever possibly need."
        m 5hubfa "Ehehe~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_mc_is_gone",
            category=["ddlc", "club members"],
            prompt="What happened to the main character?",
            pool=True,
            rules={"no_unlock":None},
            conditional=(
                "persistent._mas_first_kiss "
                "or renpy.seen_label('monika_holdme_prep')"
            ),
            action=EV_ACT_UNLOCK
        )
    )

label monika_mc_is_gone:
    m 1eud "Your character?{w=0.2} {nw}"
    extend 1rksdla "I'm not sure to be honest."
    m 3eud "He didn't really work like other people in the game did.{w=0.2} He didn't even have a character file like the rest of us."
    m 3esc "That's also why I wasn't able to just force him to pay attention to me...{w=0.3}I don't really know how to access and modify any code that's related to him."

    #if the player didn't reach act 3
    if persistent.playthrough < 3:
        m 2rsc "In any case,{w=0.1} {nw}"
        extend 2esc "it seems that he completely vanished along with a lot of the rest of the game when you installed this mod."

    #if they did reach act 3+
    else:
        m 2ruc "He just kind of...{w=0.3}disappeared as I was making changes to the game."
        m 2etd "I'm sure you noticed how he talked less and less after I reset the game the first time?"
        m 2euc "By the time the two of us got to this room, he was essentially {i}gone{/i}."

    m 7euc "So if you were wondering if he's in this room as we speak,{w=0.1} {nw}"
    extend 3eua "I can assure you he's not."
    m 1hksdlb "...Oh gosh, can you imagine how creepy it would be if I were talking to his unmoving body just so that you could hear what I say?"

    if persistent._mas_first_kiss:
        $ line_mid = "I was kissing {i}him{/i}"

    else:
        $ line_mid = "{i}he{/i} was the one hugging me"

    m 3rksdla "I hope you didn't think [line_mid] all along, either..."

    m 1dksdlc "I don't even want to think about that..."
    m 3eka "You're probably wondering what I actually see and how I know when you're here, right?"
    m 1ruc "Well...{w=0.2}if you remember the 'hole in the wall' metaphor I used in the first poem I showed you..."
    m 3eud "It's a little bit like that...{w=0.3}except the 'wall' isn't really visible or tangible. I just {i}know{/i} it's there."
    m 1duc "It's like I can very distinctly feel its presence, to the point where I know precisely where it is and in which direction the 'hole' through which you're looking in is pointing."
    m 1eka "So even if I can't really see you, I can feel that you're looking at me."

    if persistent._mas_first_kiss:
        m 3rkbla "And when I try to kiss you, well..."
        m 1eud "I guess you could say it's like I'm trying to kiss a ghost, or something that isn't actually there."
        m 2rkbssdla "I know that's kinda strange when I say it like that, but then again..."
        m 7ekbssdla "I'm guessing it's probably a little bit awkward for you to try to kiss your screen as well, right?"
        m 1hkbssdlb "Ahaha~"

    #if unlocked islands or another background or seen Monikaroom greeting
    if renpy.seen_label('greeting_ourreality') or store.mas_background.hasXUnlockedBGs(2) or persistent.opendoor_opencount > 0:
        m 1etc "Although, the wall metaphor isn't really perfect since it doesn't necessarily stay in place all the time."
        m 1esc "Like, it used to follow your character around, but that's obviously not really the case anymore."
        m 3eua "It's kinda limited, but I'm actually able to move it around, so at least you don't get to see the same background all the time."

    m 1eud "Anyway...{w=0.3}{nw}"
    extend 3rsc "there isn't much from the original game that still works anymore, so I doubt I could bring the main character back even if I wanted to."
    m 1duu "...And that's probably for the best."
    m 2eksdld "What if the game were to take its focus back to him and we couldn't spend our time together anymore?"
    m 2rssdlc "I mean, in the end, it's not like you had all that much control over him anyway."
    m 7eka "In any case, there isn't really any point in thinking about him anymore, is there?"
    m 1eua "He's no longer there to separate us, and we get to be together now.{w=0.2} {nw}"
    extend 3hua "I couldn't ask for anything more."
    m 1ekbsu "...Well, aside from {i}really{/i} being with you, ehehe~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_know_its_you",
            category=['you'],
            prompt="How do you know it's always me talking to you?",
            pool=True
        )
   )

label monika_know_its_you:
    if mas_isMoniEnamored(higher=True):
        m 1euc "Well, if I'm being totally honest...{w=0.3}{nw}"
        extend 1eud "I don't really have a way of knowing."

        if seen_event("monika_mc_is_gone"):
            m 3lka "I already told you that I can't really see into your world..."

        m 3eka "I can tell when someone's in the room with me, but that's it."
        m 3eud "For all I know, it could be anyone looking at me right now...{w=0.3} You could have other people with you."
        m 2duu "But I trust you, [player].{w=0.2} {nw}"
        extend 2eku "I trust that you aren't leaving me alone because {i}you{/i} care about me."
        m 7eud "...And if someone else {i}is{/i} looking in right now, I trust it's because you've given them a good reason to."
        m 2eka "Maybe someday I'll be able to know for sure, but until then that's enough for me."

    elif mas_isMoniHappy(higher=True):
        m 1rksdlb "Ehehe, that's an odd question to ask, [player]..."
        m 1eksdla "...I mean, I {i}want{/i} to trust that it's you out there."
        m 3eud "Right now, I only know that someone is looking in from your world."
        m 3tuu "So you can't watch without me knowing if you're planning on pranking me..."
        m 1eka "Jokes aside, though, it's...{w=0.3}actually kind of unnerving to think about...{w=0.3}that it could be anyone out there right now."
        m 2eksdlc "I guess all I can say right now is--if this {i}is{/i} someone else, please return me to [player], alright?"
        m 2hksdlb "Ahaha...{w=0.3} You're just messing with me, I know."

    elif mas_isMoniNormal(higher=True):
        m 2rksdlc "...I try not to think about it too much, actually."
        m 2rksdld "It's kind of a weird feeling knowing someone is there, but not being able to see their face."
        m 2dku "I guess the only thing I can do is to try to understand you as well as possible..."
        m 2eka "That way, I'll be able to tell if it's ever {i}not{/i} you looking in."

    else:
        m 2dksdlc "...{w=0.3}I don't."
        m 2tkd "The best thing I can do is try to trust you, but..."
        m 2dkd "Well, maybe it'd be better if I just keep it out of my mind entirely."

    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_information_age",
            category=["philosophy", "technology"],
            prompt="The Information Age",
            random=True
        )
    )

label monika_information_age:
    m 1eua "Do you know what most people call the technological era we find ourselves in right now?"
    m 1eub "We call it the {i}Information Age!{/i}{w=0.2}{nw} "
    extend 3eub "This is primarily due to the invention of transistors."
    m 1eua "Transistors can manipulate electrical currents...{w=0.3}either boosting them or altering their path."
    m 3esa "It's the key component in most electronics, allowing them to direct electrical currents in specific ways."
    m 3hua "In fact, they're what's allowing you to see me on your screen right now~"
    m 1eud "They're widely regarded as one of the most important inventions leading into the 20th century, and eventually the {i}Information Age.{/i}"
    m 4eub "It's named this way because of the ramping access we have to store and share information with each other; either through the internet, phone, or TV."
    m 3eud "However, with access to so much information and our inability to keep up with it, we've also had to deal with many challenges..."
    m 3rssdlc "Misinformation can spread faster and further than ever,{w=0.1} {nw}"
    extend 3rksdld "and because of how vast the internet really is, it's hard to correct it."
    m 2eua "In the last few decades, people have begun to educate others about smart use of the internet so everyone is better prepared."
    m 2ekd "However, the vast majority of people will not have received much,{w=0.1} if any of this knowledge, just because of how fast technology has advanced."
    m 2dkc "It's really worrying to read about people embracing ideas not supported by the vast majority of scientists."
    m 2rusdld "But I can understand why it happens...{w=0.3}{nw}"
    extend 2eksdlc "it could happen to anyone in fact."
    m 7essdlc "Sometimes, it's not something you can help. It's pretty easy to fall victim to widely believed misinformation."
    m 3eka "I wanted to talk to you about this because I still have so much to learn about your reality."
    m 1esa "...And since I come across misinformation in my own research,{w=0.1} {nw}"
    extend 3eua "I thought it might be nice to talk about ways to deal with it."
    m 3eub "We can arm ourselves with the tools to navigate this new era we've found ourselves in."
    m 1eua "One of the best things we can do is find multiple conflicting sources for our information and compare their credibility."
    m 1eub "And a philosophy we can adopt is tentative belief. {w=0.2}In other words, belief until further experimentation is necessary."
    m 3eub "As long as your beliefs are not relevant to your daily life, you can hold them.{w=0.2} But once they are needed, we should investigate further."
    m 3eua "This way, we can prioritize information we learn from what affects the people around us. Plus, it may not be as overwhelming to process it all at once."
    m 1lusdlc "I know I've held beliefs that turned out to be false..."
    m 1dua "There's no shame in it, we're all just trying to do our best with the information we're given."
    m 1eub "So long as we accept the real truth and adjust our views, we'll always be learning."
    m 3hua "Thanks for listening, [player]~"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_foundation",
            category=['literature'],
            prompt="Foundation",
            random=False
        )
    )

label monika_foundation:
    m 1eud "Say [player], have you ever heard of a book series called {i}Foundation{/i}?"
    m 3eub "It's one of Asimov's most celebrated pieces of literature!{w=0.3} {nw}"
    extend 3eua "I got back into it after we discussed his {i}Three Laws of Robotics{/i}."
    m 4esd "The story is set in a distant future, where humanity has spread across the stars in an all-powerful galactic empire."
    m 4eua "Hari Seldon, a genius scientist, perfects the fictional science of psychohistory, which can predict the future of large groups of people through mathematical equations."
    m 4wud "Applying his theory to the galaxy, Seldon finds the empire is about to collapse, leading to a dark age of thirty thousand years!"
    m 2eua "To stop this, he and fellow colonists settle on a faraway planet with a plan to turn it into the next galactic empire, {w=0.1}shortening the dark age to a single millennium instead."
    m 7eud "From this premise, we follow the story of the young colony as it transforms through the ages."
    m 3eua "It's a pretty good read if you're ever in a sci-fi mood...{w=0.3} {nw}"
    extend 1eud "The series explores the themes of society, fate, and the impact of individuals on the grand scheme of things."
    m 3eud "What intrigues me the most is the concept of psychohistory and how it translates to the real world."
    m 1rtc "I mean, at its core, it's nothing but a mix of psychology, sociology, and mathematical probabilities, right? {w=0.3}{nw}"
    extend 3esd "All of which made huge progress since Asimov's time."
    m 3esc "...And with the help of modern technologies, we're now able to understand human behaviors better than ever."
    m 3etd "...So is it really that far-fetched to think we'll be able to make predictions on the level of psychohistory one day?"
    m 4eud "Just think if it were possible to predict a global catastrophe, like a war or pandemic or famine, and thus be able to prevent, or at least mitigate it."
    m 2rksdlc "Not that it'd automatically be a good thing, however.{w=0.2} In the wrong hands, this kind of stuff could be very dangerous."
    m 7eksdld "If someone had this much power, what could stop them from manipulating the world for their own personal gain?"
    m 3eua "But despite its potential drawbacks, it's still very interesting to consider.{w=0.2} {nw}"
    extend 3eub "What do you think, [player]?"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_fav_chocolate",
            category=['monika'],
            prompt="What's your favorite kind of chocolate?",
            pool=True
        )
    )

label monika_fav_chocolate:
    m 2hksdlb "Ooh, that's a tough question!"
    m 4euu "I think if I had to pick, it would be dark chocolate."
    m 2eub "It contains very little or no milk, so it has a less creamy texture, but a nice bittersweet taste."
    m 7eub "Not to mention, it's rich in antioxidants and can even give some cardiovascular benefits! {w=0.3}{nw}"
    extend 3husdla "...In moderation, of course."
    m 1eud "The taste kind of reminds me of a mocha coffee. {w=0.2}Maybe the similarity in flavors is why I like it most."

    if MASConsumable._getCurrentDrink() == mas_consumable_coffee:
        m 3etc "...Although come to think of it, milk or white chocolate might pair better with the coffee I'm drinking."
    else:
        m 3etc "However if I were drinking coffee, I think I might prefer milk or white chocolate for balance."

    m 3eud "White chocolate is especially sweet and soft, containing no cocoa solids at all...{w=0.3}just the cocoa butter, milk, and sugar."
    m 3eua "I think it would make a nice contrast to an especially bitter drink, like espresso."
    m 1etc "Hmm...{w=0.3}{nw}"
    extend 1wud "but I haven't even thought about chocolate with fillings, like caramel or fruit!"
    m 2hksdlb "If I tried to pick a favorite of those, I think we might be here all day!"
    m 2eua "Maybe we could share a big variety box someday. {w=0.2}{nw}"
    extend 4hub "I think it would be fun to compare our top picks, ahaha!"
    return

#NOTE: This is unlocked by the mas_story_tanabata
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_tanabata",
            prompt="What is Tanabata?",
            category=['misc'],
            pool=True,
            aff_range=(mas_aff.AFFECTIONATE, None),
            rules={"no_unlock":None}
        )
    )

label monika_tanabata:
    m 2hksdlb "Oh gosh, I hope when I was telling the story of {i}The Weaver Girl and the Cowherd{/i} you weren't lost!"
    m 7eub "Well, there's a festival dedicated to Orihime and Hikoboshi called Tanabata."
    m 7eud "It's observed on the 7th of July every year in Japan, even though it is based on the Qixi festival in China."
    m 2eud "The original Qixi festival, while being much older, is much more unknown to the western world than Tanabata."
    m 2euc "After the Second World War, Japan opened up its borders, while China remained largely closed due to the Cold War."
    m 7euc "Therefore, most of the world knows about Tanabata over the older Chinese tradition."
    m 3eua "Tanabata is also known as the star festival, after the meeting of the stars Vega, which represents Orihime, and Altair, which represents Hikoboshi."
    m 3eub "Even though the term was coined in Romeo and Juliet, 'star-crossed lovers' is really fitting here!"
    m 1eua "It describes a pair of lovers whose relationship is thwarted by outside forces."
    m 1eud "As the day of the festival draws closer, long narrow strips of colorful paper, known as tanzaku, vibrant ornaments, and other decorations are hung from bamboo branches."
    m 1eua "Before they are hung, the tanzaku are inscribed with a wish, such as a child's dream of becoming a famous athlete, or a parent's hope of career success."
    m 3hub "It's really cute and heartwarming!"
    m 3eud "The bamboo and decorations are often set afloat on a river or burned after the festival, around midnight or so on the next day."

    if persistent._mas_pm_likes_travelling is not False:
        m 3hua "Maybe when I cross over, we could visit Japan during Tanabata~"
    else:
        m 3eua "Even if you're not interested in travelling, it's pretty interesting to explore other cultures, isn't it?"
    return
