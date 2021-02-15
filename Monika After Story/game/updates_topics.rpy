# Module that defines changed topics between versions
# this should run before updates.rpy

init -1 python in mas_db_merging:
    import store

    def merge_db(source, dest):
        """
        Merges the given source database into the given destination db

        IN:
            source - source database to merge from
            dest - destination database to merge into
        """
        dest.update(source)


    def merge_post0810():
        """
        Runs a specific set of merges, particularly for the merge that
        happend after version 0.8.10.
        """

        # compliments
        if store.persistent._mas_compliments_database is not None:
            merge_db(
                store.persistent._mas_compliments_database,
                store.persistent.event_database
            )


# preeerything
init -1 python:
    def clearUpdateStructs():
        """DEPRECATED
        Use mas_versions.clear instead
        """
        store.mas_versions.clear()


init 9 python:
    store.mas_versions.init()

# NOTE: these are now just ptrs to the actual store values.
# NOTE: DO NOT CHANGE THE init LEVEL of THESE LINES
define updates.version_updates = mas_versions.version_updates
define updates.topics = mas_versions.topics


init -2 python in mas_versions:
    import store
    import store.mas_utils as mas_utils
    from store.mas_ev_data_ver import _verify_str

    # start by initalization version update dict
    version_updates = {}

    # key:version number -> v:changedIDs
    # changedIDs structure:
    #   k:oldId -> v:newId
    topics = {}


    def add_steps(version_struct):
        """
        Adds versions to the version updates dict.

        IN:
            version_struct - dict with versions in special version notation.
                Keys: version to update to, as string
                Vals: versions to update from, as string or tuple of strings
        """
        for to_ver, from_vers in version_struct.items(): # using items for py3
            to_ver_str = _vdot2vstr(to_ver)
            if _verify_str(from_vers, False):
                version_updates[_vdot2vstr(from_vers)] = to_ver_str
            else:
                # must be tuple
                for from_ver in from_vers:
                    version_updates[_vdot2vstr(from_ver)] = to_ver_str


    def clear():
        """
        Clears the update data structures
        """
        version_updates.clear()
        topics.clear()


    def init():
        """
        Initializes the update data structures
        """
        # use the notation:
        #   new version: old version
        # OR
        #   new version: (old version 1, old version 2, ...)
        #
        # use dot notation to separate the parts of a version

        add_steps({
            #"0.12.0.1": "0.12.0",
            "0.12.0": "0.11.9.3",
            "0.11.9.3": ("0.11.9.2", "0.11.9.1"),
            "0.11.9.1": "0.11.9",
            "0.11.9": ("0.11.8", "0.11.7"),
            "0.11.7": "0.11.6",
            "0.11.6": "0.11.5",
            "0.11.5": "0.11.4",
            "0.11.4": "0.11.3",
            "0.11.3": ("0.11.2", "0.11.1"),
            "0.11.1": "0.11.0",
            "0.11.0": "0.10.7",

            "0.10.7": "0.10.6",
            "0.10.6": "0.10.5",
            "0.10.5": "0.10.4",
            "0.10.4": "0.10.3",
            "0.10.3": "0.10.2",
            "0.10.2": "0.10.1",
            "0.10.1": "0.10.0",
            "0.10.0": "0.9.5",

            "0.9.5": "0.9.4",
            "0.9.4": ("0.9.3", "0.9.2"),
            "0.9.2": "0.9.1",
            "0.9.1": "0.9.0",
            "0.9.0": "0.8.14",

            "0.8.14": "0.8.13",
            "0.8.13": ("0.8.12", "0.8.11"),
            "0.8.11": "0.8.10",
            "0.8.10": "0.8.9",
            "0.8.9": ("0.8.8", "0.8.7", "0.8.6"),
            "0.8.6": ("0.8.5", "0.8.4"),
            "0.8.4": "0.8.3",
            "0.8.3": "0.8.2",
            "0.8.2": "0.8.1",
            "0.8.1": "0.8.0",
            "0.8.0": "0.7.4",

            "0.7.4": ("0.7.3", "0.7.2"),
            "0.7.2": "0.7.1",
            "0.7.1": "0.7.0",
            "0.7.0": ("0.6.3", "0.6.2", "0.6.1"),
            "0.6.1": ("0.6.0", "0.5.1"),
            "0.5.1": ("0.5.0", "0.4.0", "0.3.3"),
            "0.3.3": "0.3.2",
            "0.3.2": "0.3.1",
            "0.3.1": "0.3.0",
            "0.3.0": "0.2.2",
        })

        # NOTE: we are no longer going to use this:
        #
        # version structures:
        # if a version has changed / removed IDS, then add it as a dict
        # here
        # k:oldID -> v:newID
        # if newID is None, the topic is considered removed
        #
        # NOTE: If a potential conflict may occur (removing one topic,
        # changing name of another topic to the one that was removed),
        # do NOT use this to update the IDs
        # All conflicts should be handled in an individual script block in
        # updates.rpy. (SEE updates.rpy)
        updates = store.updates

        # (0.8.4 - 0.8.10) -> 0.8.11
        updates.topics[_vdot2vstr("0.8.11")] = {
            "monika_snowman": None,
            "monika_relax": None,
            "monika_hypothermia": None,
            "monika_whatiwant": None
        }

        # (0.8.1 - 0.8.3) -> 0.8.4
        updates.topics[_vdot2vstr("0.8.4")] = {
            "monika_bestgirl": "mas_compliment_bestgirl"
        }

        # 0.8.0 -> 0.8.1
        updates.topics[_vdot2vstr("0.8.1")] = {
            "monika_write": "monika_writingtip3",
            "mas_random_ask": None,
            "monika_ravel": "mas_story_ravel"
        }

        # 0.7.4 -> 0.8.0
        updates.topics[_vdot2vstr("0.8.0")] = {
            "monika_love2": None
        }

        # (0.7.0 - 0.7.3) -> 0.7.4
        updates.topics[_vdot2vstr("0.7.4")] = {
            "monika_playerhappy": None,
            "monika_bad_day": None
        }

        # (0.6.1 - 0.6.3) -> 0.7.0
        changedIDs = {
            "monika_deleted": None,
            "monika_whatever": None,
            "monika_games": None,
            "monika_chess": None,
            "monika_pong": None,
            "monika_vulgarity": None,
            "monika_goodbye": None,
            "monika_night": None
        }
        updates.topics[_vdot2vstr("0.7.0")] = changedIDs

        # (0.5.1 - 0.6.0) -> 0.6.1
        changedIDs = {
            "monika_piano": None
        }
        updates.topics[_vdot2vstr("0.6.1")] = changedIDs

        # (0.3.3 - 0.5.0) -> 0.5.1
        changedIDs = dict()
        changedIDs["monika_music"] = None
        changedIDs["monika_keitai"] = None
        changedIDs["monika_subahibi"] = None
        changedIDs["monika_reddit"] = None
        changedIDs["monika_shill"] = None
        changedIDs["monika_dracula"] = None
        changedIDs["monika_undertale"] = None
        changedIDs["monika_recursion"] = None
        changedIDs["monika_lain"] = None
        changedIDs["monika_kyon"] = None
        changedIDs["monika_water"] = None
        changedIDs["monika_computer"] = None
        updates.topics[_vdot2vstr("0.5.1")] = changedIDs

        # 0.3.1 -> 0.3.2
        changedIDs = dict()
        changedIDs["monika_monika"] = None
        updates.topics[_vdot2vstr("0.3.2")] = changedIDs

        # 0.3.0 -> 0.3.1
        changedIDs = dict()
        changedIDs["monika_ghosts"] = "monika_whispers"
        updates.topics[_vdot2vstr("0.3.1")] = changedIDs

        # 0.2.2 -> 0.3.0
        # this is a long list...
        # no_topics_list is defined / checked in updates.rpy
        changedIDs = None
        changedIDs = dict()
        changedIDs["ch30_1"] = "monika_god"
        changedIDs["ch30_2"] = "monika_death"
        changedIDs["ch30_3"] = "monika_bad_day"
        changedIDs["ch30_4"] = "monika_sleep"
        changedIDs["ch30_5"] = "monika_sayori"
        changedIDs["ch30_6"] = "monika_japan"
        changedIDs["ch30_7"] = "monika_high_school"
        changedIDs["ch30_8"] = "monika_nihilism"
        changedIDs["ch30_9"] = "monika_piano"
        changedIDs["ch30_10"] = "monika_twitter"
        changedIDs["ch30_11"] = "monika_portraitof"
        changedIDs["ch30_12"] = "monika_veggies"
        changedIDs["ch30_13"] = "monika_saved"
        changedIDs["ch30_14"] = "monika_secrets"
        changedIDs["ch30_15"] = "monika_color"
        changedIDs["ch30_16"] = "monika_music"
        changedIDs["ch30_17"] = "monika_listener"
        changedIDs["ch30_18"] = "monika_spicy"
        changedIDs["ch30_19"] = "monika_why"
        changedIDs["ch30_20"] = "monika_okayeveryone"
        changedIDs["ch30_21"] = "monika_ghosts"
        changedIDs["ch30_22"] = "monika_archetype"
        changedIDs["ch30_23"] = "monika_tea"
        changedIDs["ch30_24"] = "monika_favoritegame"
        changedIDs["ch30_25"] = "monika_smash"
#        changedIDs["ch30_26"] = ""
        changedIDs["ch30_27"] = "monika_lastpoem"
        changedIDs["ch30_28"] = "monika_anxious"
        changedIDs["ch30_29"] = "monika_friends"
        changedIDs["ch30_30"] = "monika_college"
        changedIDs["ch30_31"] = "monika_middleschool"
        changedIDs["ch30_32"] = "monika_outfit"
        changedIDs["ch30_33"] = "monika_horror"
        changedIDs["ch30_34"] = "monika_rap"
        changedIDs["ch30_35"] = "monika_wine"
        changedIDs["ch30_36"] = "monika_date"
        changedIDs["ch30_37"] = "monika_kiss"
        changedIDs["ch30_38"] = "monika_yuri"
        changedIDs["ch30_39"] = "monika_writingtip"
        changedIDs["ch30_40"] = "monika_habits"
        changedIDs["ch30_41"] = "monika_creative"
        changedIDs["ch30_42"] = "monika_deleted"
        changedIDs["ch30_43"] = "monika_keitai"
        changedIDs["ch30_44"] = "monika_simulated"
        changedIDs["ch30_45"] = "monika_rain"
        changedIDs["ch30_46"] = "monika_closeness"
        changedIDs["ch30_47"] = "monika_confidence"
        changedIDs["ch30_48"] = "monika_carryme"
        changedIDs["ch30_49"] = "monika_debate"
        changedIDs["ch30_50"] = "monika_internet"
        changedIDs["ch30_51"] = "monika_lazy"
        changedIDs["ch30_52"] = "monika_mentalillness"
        changedIDs["ch30_53"] = "monika_read"
        changedIDs["ch30_54"] = "monika_festival"
        changedIDs["ch30_55"] = "monika_tsundere"
        changedIDs["ch30_56"] = "monika_introduce"
        changedIDs["ch30_57"] = "monika_cold"
        changedIDs["ch30_58"] = "monika_housewife"
        changedIDs["ch30_59"] = "monika_route"
        changedIDs["monika_literatureclub"] = "monika_ddlc"
        changedIDs["monika_religion"] = None

            # here is a list of new ids, for reference. These are automatically
            # handled via new topic generation.
            # monika_credits_song
            # monika_whatever (special topic launcher)

            # here is a list of IDS present in v0.2.2, again for reference
            # monika_imouto
            # monika_oneesan
            # monika_family
            # monika_anime
            # monika_libitina
            # monika_meta
            # monika_programming
            # monika_vn
            # monika_totono
            # monika_subahibi
            # monika_difficulty
            # monika_poetry
            # monika_dan
            # monika_4chan
            # monika_reddit
            # monika_vidya
            # monika_books
            # monika_favpoem
            # monika_favbook
            # monika_natsuki
            # monika_love
            # monika_hedgehog
            # monika_justification
            # monika_freewill
            # monika_shill
            # monika_technique
            # monika_contribute
            # monika_drawing
            # monika_mc
            # monika_heroism
            # monika_dracula
            # monika_undertale
            # monika_bestgrill
            # monika_trolley
            # monika_girlfriend
            # monika_waifus

            # CONFLICTING CHANGES ALERT
            # the following ids have been changed/removed and conflict with
            # changedIDs dict (these must be handled in updates.rpy)
            # monika_piano
            # monika_college was pointing to ch30_31 (monika_middleschool)
        updates.topics[_vdot2vstr("0.3.0")] = changedIDs

        # ensuring no refs to old dicts
        changedIDs = None


    def _vdot2vstr(version_str):
        """
        Converts a version string that uses dots to the v#_#_# notation

        IN:
            version_str - version string with dots #.#.#.#

        RETURNS: version string in the standard version notation:
            v#_#_#_#
        """
        return "v" + "_".join(version_str.split("."))
