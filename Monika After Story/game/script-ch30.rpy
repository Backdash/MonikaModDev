default persistent.monika_reload = 0
default persistent.tried_skip = False
default persistent.monika_kill = True #Assume non-merging players killed monika.
default persistent.rejected_monika = None
default initial_monika_file_check = None
define modoorg.CHANCE = 20
define mas_battery_supported = False
define mas_in_intro_flow = False

# True means disable animations, False means enable
default persistent._mas_disable_animations = False

init -998 python:
    #We need to flow hijack here if we're running unstable mode files but on a fresh persistent
    if "unstable" in config.version and not persistent.sessions:
        raise Exception(
            _("Unstable mode files in install on first session. This can cause issues.\n"
            "Please reinstall the latest stable version of Monika After Story to ensure that there will be no data issues.")
        )

init -890 python in mas_globals:
    import datetime
    import store

    # we set the time travel global here
    tt_detected = (
        store.mas_getLastSeshEnd() - datetime.datetime.now()
            > datetime.timedelta(hours=30)
    )

    if tt_detected:
        store.persistent._mas_pm_has_went_back_in_time = True

    #Internal renpy version check
    is_r7 = renpy.version(True)[0] == 7

    # Check whether or not the user uses a steam install
    is_steam = "steamapps" in renpy.config.basedir.lower()

init -1 python in mas_globals:
    # global that are not actually globals.

    # True means we are in the dialogue workflow. False means not
    dlg_workflow = False

    show_vignette = False
    # TRue means show the vignette mask, False means no show

    show_lightning = False
    # True means show lightning, False means do not

    lightning_chance = 16
    lightning_s_chance = 10
    # lightning chances

    show_s_light = False
    # set to True to show s easter egg.

    text_speed_enabled = False
    # set to True if text speed is enabled

    in_idle_mode = False
    # set to True if in idle mode

    late_farewell = False
    # set to True if we had a late farewell

    last_minute_dt = datetime.datetime.now()
    # last minute datetime (replaces calendar_last_chcked)

    last_hour = last_minute_dt.hour
    # number of the hour we last ran ch30_hour

    last_day = last_minute_dt.day
    # numbr of the day we last ran ch30_day

    time_of_day_4state = None
    #Time of day, basically either morning, afternoon, evening, night. Set by ch30_hour, used in dlg

    time_of_day_3state = None
    #Time of day broken into 3 states. morning, afternoon, evening. Set by ch30_hour, used in dlg

    returned_home_this_sesh = bool(store.persistent._mas_moni_chksum)
    #Whether or not this sesh was started by a returned home greet

    this_ev = None
    # the current topic, but as event object. may be None.

init 970 python:
    import store.mas_filereacts as mas_filereacts

#    mas_temp_moni_chksum = None

    if persistent._mas_moni_chksum is not None:
#        mas_temp_moni_chksum = persistent._mas_moni_chksum

        # do check for monika existence
        store.mas_dockstat.init_findMonika(mas_docking_station)


init -10 python:
    # create the idle mailbox
    class MASIdleMailbox(store.MASMailbox):
        """
        Spaceroom idle extension of the mailbox

        PROPERTIES:
            (no additional)

        See MASMailbox for properties
        """

        # NOTE: add keys here
        REBUILD_EV = 1
        # rebuilds the event list in idle

        DOCKSTAT_GRE_TYPE = 2
        # used by the bye_going_somewhere farewell as a type

        IDLE_MODE_CB_LABEL = 3
        # label to call when returning from idle mode

        SKIP_MID_LOOP_EVAL = 4
        # True if we want idle to skip mid loop eval once

        SCENE_CHANGE = 5
        # TRue if want the scene to change

        # end keys

        def __init__(self):
            """
            Constructor for the idle mailbox
            """
            super(MASIdleMailbox, self).__init__()

        # NOTE: add additoinal functions below when appropriate.
        def send_rebuild_msg(self):
            """
            Sends the rebuild message to the mailbox
            """
            self.send(self.REBUILD_EV, True)

        def get_rebuild_msg(self):
            """
            Gets rebuild message
            """
            return self.get(self.REBUILD_EV)

        def send_ds_gre_type(self, gre_type):
            """
            Sends greeting type to mailbox
            """
            self.send(self.DOCKSTAT_GRE_TYPE, gre_type)

        def get_ds_gre_type(self, default=None):
            """
            Gets dockstat greeting type

            RETURNS: None by default
            """
            result = self.get(self.DOCKSTAT_GRE_TYPE)
            if result is None:
                return default
            return result

        def send_idle_cb(self, cb_label):
            """
            Sends idle callback label to mailbox
            """
            self.send(self.IDLE_MODE_CB_LABEL, cb_label)

        def get_idle_cb(self):
            """
            Gets idle callback label
            """
            return self.get(self.IDLE_MODE_CB_LABEL)

        def send_skipmidloopeval(self):
            """
            Sends skip mid loop eval message to mailbox
            """
            self.send(self.SKIP_MID_LOOP_EVAL, True)

        def get_skipmidloopeval(self):
            """
            Gets skip midloop eval value
            """
            return self.get(self.SKIP_MID_LOOP_EVAL)

        def send_scene_change(self):
            """
            Sends scene change message to mailbox
            """
            self.send(self.SCENE_CHANGE, True)

        def get_scene_change(self):
            """
            Gets scene change value
            """
            return self.get(self.SCENE_CHANGE)


    mas_idle_mailbox = MASIdleMailbox()


image monika_room_highlight:
    "images/cg/monika/monika_room_highlight.png"
    function monika_alpha
image monika_bg = "images/cg/monika/monika_bg.png"
image monika_bg_highlight:
    "images/cg/monika/monika_bg_highlight.png"
    function monika_alpha
image monika_scare = "images/cg/monika/monika_scare.png"

image monika_body_glitch1:
    "images/cg/monika/monika_glitch1.png"
    0.15
    "images/cg/monika/monika_glitch2.png"
    0.15
    "images/cg/monika/monika_glitch1.png"
    0.15
    "images/cg/monika/monika_glitch2.png"
    1.00
    "images/cg/monika/monika_glitch1.png"
    0.15
    "images/cg/monika/monika_glitch2.png"
    0.15
    "images/cg/monika/monika_glitch1.png"
    0.15
    "images/cg/monika/monika_glitch2.png"

image monika_body_glitch2:
    "images/cg/monika/monika_glitch3.png"
    0.15
    "images/cg/monika/monika_glitch4.png"
    0.15
    "images/cg/monika/monika_glitch3.png"
    0.15
    "images/cg/monika/monika_glitch4.png"
    1.00
    "images/cg/monika/monika_glitch3.png"
    0.15
    "images/cg/monika/monika_glitch4.png"
    0.15
    "images/cg/monika/monika_glitch3.png"
    0.15
    "images/cg/monika/monika_glitch4.png"



image room_glitch = "images/cg/monika/monika_bg_glitch.png"

init python:

    import subprocess
    import os
    import eliza      # mod specific
    import datetime   # mod specific
    import battery    # mod specific
    import re
    import store.songs as songs
    import store.hkb_button as hkb_button
    import store.mas_globals as mas_globals
    therapist = eliza.eliza()
    process_list = []
    currentuser = None # start if with no currentuser
    if renpy.windows:
        try:
            process_list = subprocess.check_output("wmic process get Description", shell=True).lower().replace("\r", "").replace(" ", "").split("\n")
        except:
            pass
        try:
            for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
                user = os.environ.get(name)
                if user:
                    currentuser = user
        except:
            pass

    try:
        renpy.file("../characters/monika.chr")
        initial_monika_file_check = True
    except:
        #Monika will mention that you don't have a char file in ch30_main instead
        pass


    # name changes if necessary
    if not currentuser or len(currentuser) == 0:
        currentuser = persistent.playername
    if not persistent.mcname or len(persistent.mcname) == 0:
        persistent.mcname = currentuser
        mcname = currentuser
    else:
        mcname = persistent.mcname

    # check for battery support
    mas_battery_supported = battery.is_supported()

    # we need a new music channel for background audio (like rain!)
    # this uses the amb (ambient) mixer.
    renpy.music.register_channel(
        "background",
        mixer="amb",
        loop=True,
        stop_on_mute=True,
        tight=True
    )

    # also need another verison of background for concurrency
    renpy.music.register_channel(
        "backsound",
        mixer="amb",
        loop=False,
        stop_on_mute=True
    )

    #Define new functions
    def show_dialogue_box():
        """
        Jumps to the topic promt menu
        """
        renpy.jump('prompt_menu')


    def pick_game():
        """
        Jumps to the pick a game workflow
        """
        renpy.jump("mas_pick_a_game")


    def mas_getuser():
        """
        Attempts to get the current user

        RETURNS: current user if found, or None if not found
        """
        for name in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
            user = os.environ.get(name)
            if user:
                return user

        return None


    def mas_enable_quitbox():
        """
        Enables Monika's quit dialogue warning
        """
        global _confirm_quit
        _confirm_quit = True


    def mas_disable_quitbox():
        """
        Disables Monika's quit dialogue warning
        """
        global _confirm_quit
        _confirm_quit = False


    def mas_enable_quit():
        """
        Enables quitting without monika knowing
        """
        persistent.closed_self = True
        mas_disable_quitbox()


    def mas_disable_quit():
        """
        Disables quitting without monika knowing
        """
        persistent.closed_self = False
        mas_enable_quitbox()


    def mas_drawSpaceroomMasks(dissolve_masks=True):
        """
        Draws the appropriate masks according to the current state of the
        game.

        IN:
            dissolve_masks - True will dissolve masks, False will not
                (Default; True)
        """
        # hide the existing mask
        renpy.hide("rm")

        # get current weather masks
        mask = mas_current_weather.get_mask()

        # now show the mask
        renpy.show(mask, tag="rm")

        if dissolve_masks:
            renpy.with_statement(Dissolve(1.0))


    def mas_validate_suntimes():
        """
        Validates both persistent and store suntimes are in a valid state.
        Sunrise is always used as the lead if a reset is needed.
        """
        if (
            mas_suntime.sunrise > mas_suntime.sunset
            or persistent._mas_sunrise > persistent._mas_sunset
        ):
            mas_suntime.sunset = mas_suntime.sunrise
            persistent._mas_sunset = persistent._mas_sunrise


    def show_calendar():
        """RUNTIME ONLY
        Opens the calendar if we can
        """
        mas_HKBRaiseShield()

        if not persistent._mas_first_calendar_check:
            renpy.call('_first_time_calendar_use')

        renpy.call_in_new_context("mas_start_calendar_read_only")

        if store.mas_globals.in_idle_mode:
            # IDLe only enables talk extra and music
            store.hkb_button.talk_enabled = True
            store.hkb_button.extra_enabled = True
            store.hkb_button.music_enabled = True

        else:
            mas_HKBDropShield()


    dismiss_keys = config.keymap['dismiss']
    renpy.config.say_allow_dismiss = store.mas_hotkeys.allowdismiss

    def slow_nodismiss(event, interact=True, **kwargs):
        """
        Callback for whenever monika talks

        IN:
            event - main thing we can use here, lets us now when in the pipeline
                we are for display text:
                begin -> start of a say statement
                show -> right before dialogue is shown
                show_done -> right after dialogue is shown
                slow_done -> called after text finishes showing
                    May happen after "end"
                end -> end of dialogue (user has interacted)
        """
        # skip check
        # if config.skipping and not config.developer:
        #     persistent.tried_skip = True
        #     config.skipping = False
        #     config.allow_skipping = False
        #     renpy.jump("ch30_noskip")
        #     return

        if event == "begin":
            store.mas_hotkeys.allow_dismiss = False
#            config.keymap['dismiss'] = []
#            renpy.display.behavior.clear_keymap_cache()

        elif event == "slow_done":
            store.mas_hotkeys.allow_dismiss = True
#            config.keymap['dismiss'] = dismiss_keys
#            renpy.display.behavior.clear_keymap_cache()


    def mas_isMorning():
        """DEPRECATED
        Checks if it is day or night via suntimes

        NOTE: the wording of this function is bad. This does not literally
            mean that it is morning. USE mas_isDayNow

        RETURNS: True if day, false if not
        """
        return mas_isDayNow()


    def mas_progressFilter():
        """
        Changes filter according to rules.

        Call this when you want to update the filter.

        RETURNS: True upon a filter change, False if not
        """
        curr_flt = store.mas_sprites.get_filter()
        new_flt = mas_current_background.progress()
        store.mas_sprites.set_filter(new_flt)

        return curr_flt != new_flt


    def mas_shouldChangeTime():
        """DEPRECATED
        This no longer makes sense with the filtering system.
        """
        return False


    def mas_shouldRain():
        """
        Rolls some chances to see if we should make it rain

        RETURNS:
            rain weather to use, or None if we dont want to change weather
        """
        #All paths roll
        chance = random.randint(1,100)
        if mas_isMoniNormal(higher=True):
            #NOTE: Chances are as follows:
            #Spring:
            #   - Rain: 40%
            #   - Thunder: 15% (37.5% of that 40%)
            #   - Overcast: 15% (if rain has failed)
            #   - Sunny: 45%
            #
            #Summer:
            #   - Rain: 10%
            #   - Thunder: 6% (60% of that 10%)
            #   - Overcast: 5% (if rain has failed)
            #   - Sunny: 85%
            #
            #Fall:
            #   - Rain: 30%
            #   - Thunder: 12% (40% of that 50%)
            #   - Overcast: 15%
            #   - Sunny: 55%
            #
            #Winter:
            #   - Snow: 50%
            #   - Overcast: 20%
            #   - Sunny: 30%

            if mas_isSpring():
                return mas_weather._determineCloudyWeather(
                    40,
                    15,
                    15,
                    rolled_chance=chance
                )

            elif mas_isSummer():
                return mas_weather._determineCloudyWeather(
                    10,
                    6,
                    5,
                    rolled_chance=chance
                )

            elif mas_isFall():
                return mas_weather._determineCloudyWeather(
                    30,
                    12,
                    15,
                    rolled_chance=chance
                )

            else:
                #Chance of snow
                if chance <= 50:
                    return mas_weather_snow
                elif chance <= 70:
                    return mas_weather_overcast

        #Otherwise rain based on how Moni's feeling
        elif mas_isMoniUpset() and chance <= MAS_RAIN_UPSET:
            return mas_weather_overcast

        elif mas_isMoniDis() and chance <= MAS_RAIN_DIS:
            return mas_weather_rain

        elif mas_isMoniBroken() and chance <= MAS_RAIN_BROKEN:
            return mas_weather_thunder

        return None


    def mas_lockHair():
        """
        Locks all hair topics
        """
        mas_lockEVL("monika_hair_select")


    def mas_seasonalCheck():
        """
        Determines the current season and runs an appropriate programming
        point.

        If the global for season is currently None, then we instead set the
        current season.

        NOTE: this does NOT do progressive programming point execution.
            This is intended for runtime usage only.

        ASSUMES:
            persistent._mas_current_season
        """
        _s_tag = store.mas_seasons._currentSeason()

        if persistent._mas_current_season != _s_tag:

            _s_pp = store.mas_seasons._season_pp_map.get(_s_tag, None)
            if _s_pp is not None:

                # executes programming point
                _s_pp()

                # sets global to given tag
                persistent._mas_current_season = _s_tag


    def mas_resetIdleMode():
        """
        Resets specific idle mode vars.

        This is meant to basically clear idle mode for holidays or other
        things that hijack main flow
        """
        store.mas_globals.in_idle_mode = False
        persistent._mas_in_idle_mode = False
        persistent._mas_idle_data = {}
        mas_idle_mailbox.get_idle_cb()


    def mas_enableTextSpeed():
        """
        Enables text speed
        """
        style.say_dialogue = style.normal
        store.mas_globals.text_speed_enabled = True


    def mas_disableTextSpeed():
        """
        Disables text speed
        """
        style.say_dialogue = style.default_monika
        store.mas_globals.text_speed_enabled = False


    def mas_resetTextSpeed(ignoredev=False):
        """
        Sets text speed to the appropriate one depending on global settings

        Rules:
        1 - developer always gets text speed (unless ignoredev is True)
        2 - text speed enabled if affection above happy
        3 - text speed disabled otherwise
        """
        if config.developer and not ignoredev:
            mas_enableTextSpeed()

        elif (
                mas_isMoniHappy(higher=True)
                and persistent._mas_text_speed_enabled
            ):
            mas_enableTextSpeed()

        else:
            mas_disableTextSpeed()


    def mas_isTextSpeedEnabled():
        """
        Returns true if text speed is enabled
        """
        return store.mas_globals.text_speed_enabled

    def mas_check_player_derand():
        """
        Checks the player derandom lists for events that are not random and derandoms them
        """

        derand_list = store.mas_bookmarks_derand.getDerandomedEVLs()

        #Now iter through this to derand what's rand
        for ev_label in derand_list:
            #Get the ev
            ev = mas_getEV(ev_label)
            if ev and ev.random:
                ev.random = False

    def mas_get_player_bookmarks(bookmarked_evls):
        """
        Gets topics which are bookmarked by the player
        Also cleans events which no longer exist

        NOTE: Will NOT add events which fail the aff range check

        IN:
            bookmarked_evls - appropriate persistent variable holding the bookmarked eventlabels

        OUT:
            List of bookmarked topics as evs
        """
        bookmarkedlist = []

        #Iterate and add to bookmarked list
        for index in range(len(bookmarked_evls)-1,-1,-1):
            #Get the ev
            ev = mas_getEV(bookmarked_evls[index])

            #If no ev, we'll pop it as we shouldn't actually keep it here
            if not ev:
                bookmarked_evls.pop(index)

            #Otherwise, we add it to the menu item list
            elif ev.unlocked and ev.checkAffection(mas_curr_affection):
                bookmarkedlist.append(ev)

        return bookmarkedlist

    def mas_get_player_derandoms(derandomed_evls):
        """
        Gets topics which are derandomed by the player (in check-scrollable-menu format)
        Also cleans out events which no longer exist

        IN:
            derandomed_evls - appropriate variable holding the derandomed eventlabels

        OUT:
            List of player derandomed topics in mas_check_scrollable_menu form
        """
        derandlist = []

        #Iterate and add to derand list
        for index in range(len(derandomed_evls)-1,-1,-1):
            #Get the ev
            ev = mas_getEV(derandomed_evls[index])

            #No ev. Pop it as we shouldn't actually keep it here
            if not ev:
                derandomed_evls.pop(index)

            #Ev exists. Add it to the menu item list
            elif ev.unlocked:
                derandlist.append((renpy.substitute(ev.prompt), ev.eventlabel, False, True, False))

        return derandlist



# IN:
#   start_bg - the background image we want to start with. Use this for
#       special greetings. None uses the default spaceroom images.
#       NOTE: This is called using renpy.show(), so pass the string name of
#           the image you want (NOT FILENAME)
#       NOTE: You're responsible for setting spaceroom back to normal though
#       (Default: None)
#   hide_mask - True will hide the mask, false will not
#       (Default: False)
#   hide_monika - True will hide monika, false will not
#       (Default: False)
#   dissolve_all - True will dissolve everything, False will not
#       NOTE: takes priority over dissolve masks
#       (Default: False)
#   dissolve_masks - True will dissolve masks, False will not.
#       NOTE: this also drives functionality with force_exp
#       NOTE: if dissolve_all is True, this is ignored.
#       (Default: False)
#   scene_change - True will prefix the draw with a scene call. scene black
#       will always be used.
#       (Default: False)
#   force_exp - if not None, then we use this instead of monika idle.
#       NOTE: this must be a string
#       NOTE: if passed in, this will override aff-based exps from dissolving.
#       (Default: None)
#   day_bg - the room we'll be showing during the day
#       NOTE: must be string
#       NOTE: if passed in, it will override the current background day_bg
#       (Default: None)
#   night_bg - the room we'll be showing during the night
#       NOTE: must be string
#       NOTE: if passed in, it will override the current background night_bg
#       (Default: None)
#   show_emptydesk - behavior is determined by `hide_monika`
#       if hide_monika is True - True will show emptydesk and False will do
#           nothing.
#       if hide_monika is False - True will do nothing and False will hide
#           emptydesk after Monika is shown.
#       (Default: True)
#   progress_filter - True will progress the filter. False will not
#       NOTE: use this if you explicity set the filter
#       (Default: True)
#   bg_change_info - MASBackgroundChangeInfo object to use when transitioning.
#       NOTE: this should ONLY be used by mas_background_change.
#       This will make sure that when the background changes, associated
#       images will be hidden / shown following the appropriate transition.
#       (Default: None)
label spaceroom(start_bg=None, hide_mask=None, hide_monika=False, dissolve_all=False, dissolve_masks=False, scene_change=False, force_exp=None, hide_calendar=None, day_bg=None, night_bg=None, show_emptydesk=True, progress_filter=True, bg_change_info=None):

    with None

    #Get all of the params
    if hide_mask is None:
        $ hide_mask = store.mas_current_background.hide_masks
    if hide_calendar is None:
        $ hide_calendar = store.mas_current_background.hide_calendar

    # progress filter
    # NOTE: filter progression MUST happen here because othrewise we many have
    #   cases where the filter has changed (so Monika has changed)
    #   but the BG has not (because BG is not inherently controleld by filter)
    python:
        if progress_filter and mas_progressFilter():
            # NOTE: a filter change is like a scene change with all dissolve
            scene_change = True
            dissolve_all = True

        day_mode = mas_current_background.isFltDay()

    if scene_change:
        scene black

    python:
        monika_room = None

        if scene_change:
            monika_room = mas_current_background.getCurrentRoom()

        #What ui are we using
        if persistent._mas_auto_mode_enabled:
            mas_darkMode(day_mode)
        else:
            mas_darkMode(not persistent._mas_dark_mode_enabled)

        ## are we hiding monika
        if hide_monika:
            if show_emptydesk:
                store.mas_sprites.show_empty_desk()

        else:
            if force_exp is None:
                force_exp = "monika idle"
                # if dissolve_all:
                #     force_exp = store.mas_affection._force_exp()

                # else:
                #     force_exp = "monika idle"

            if not renpy.showing(force_exp):
                renpy.show(force_exp, at_list=[t11], zorder=MAS_MONIKA_Z)

                if not dissolve_all:
                    renpy.with_statement(None)

        # if we only want to dissolve masks, then we dissolve now
        if not dissolve_all and not hide_mask:
            mas_drawSpaceroomMasks(dissolve_masks)

        # actual room check
        # are we using a custom start bg or not
        if start_bg:
            if not renpy.showing(start_bg):
                renpy.show(start_bg, tag="sp_mas_room", zorder=MAS_BACKGROUND_Z)

        elif monika_room is not None:
            if not renpy.showing(monika_room):
                renpy.show(
                    monika_room,
                    tag="sp_mas_room",
                    zorder=MAS_BACKGROUND_Z
                )
                #Show calendar if it's supported
                if not hide_calendar:
                    mas_calShowOverlay()

        # always generate bg change info if scene is changing.
        #   NOTE: generally, this will just show all deco that is appropraite
        #   for this background.
        if scene_change and (bg_change_info is None or len(bg_change_info) < 1):
            bg_change_info = store.mas_background.MASBackgroundChangeInfo()
            mas_current_background._entry_deco(None, bg_change_info)

        # add show/hide statements for decos
        if bg_change_info is not None:
            if not scene_change:
                for h_adf in bg_change_info.hides.itervalues():
                    h_adf.hide()

            for s_tag, s_adf in bg_change_info.shows.iteritems():
                s_adf.show(s_tag)

    # vignette
    if store.mas_globals.show_vignette:
        show vignette zorder 70

    #Monibday stuff
    if persistent._mas_bday_visuals:
        #We only want cake on a non-reacted sbp (i.e. returning home with MAS open)
        $ store.mas_surpriseBdayShowVisuals(cake=not persistent._mas_bday_sbp_reacted)

    # ----------- Grouping date-based events since they can never overlap:
    #O31 stuff
    # TODO: move this to o31 autoload
    if persistent._mas_o31_in_o31_mode:
        $ store.mas_o31ShowVisuals()
    # ----------- end date-based events

    # player bday
    # TODO: move this to bday autoload
    if persistent._mas_player_bday_decor:
        $ store.mas_surpriseBdayShowVisuals()

    if datetime.date.today() == persistent._date_last_given_roses:
        $ monika_chr.wear_acs_pst(mas_acs_roses)

    # dissolving everything means dissolve last
    if dissolve_all and not hide_mask:
        $ mas_drawSpaceroomMasks(dissolve_all)
    elif dissolve_all:
        $ renpy.with_statement(Dissolve(1.0))

    # hide emptydesk if monika is visible
    if not hide_monika and not show_emptydesk:
        hide emptydesk

    return


label ch30_main:
    $ mas_skip_visuals = False
    $ m.display_args["callback"] = slow_nodismiss
    $ m.what_args["slow_abortable"] = config.developer
    $ quick_menu = True
    if not config.developer:
        $ style.say_dialogue = style.default_monika
    $ m_name = persistent._mas_monika_nickname
    $ delete_all_saves()
    $ persistent.clear[9] = True

    # call reset stuff
    call ch30_reset

    # set monikas outfit to default
    $ monika_chr.reset_outfit(False)
    $ monika_chr.wear_acs(mas_acs_ribbon_def)

    # so other flows are aware that we are in intro
    $ mas_in_intro_flow = True

    # before we render visuals:
    # 1 - all core interactions should be disabeld
    $ mas_RaiseShield_core()

    # 2 - hotkey buttons should be disabled
    $ store.hkb_button.enabled = False

    # 3 - keymaps are disabled (default)

    call spaceroom(scene_change=True,dissolve_all=True, force_exp="monika 6dsc_static")

    # lets just call the intro instead of pushing it as an event
    # this is way simpler and prevents event loss and other weird inital
    # startup issues
    call introduction

    # now we can do some cleanup
    # 1 - renable core interactions
    $ mas_DropShield_core()

    # now we out of intro
    $ mas_in_intro_flow = False

    # set session data to startup values
    $ store._mas_root.initialSessionData()

    # skip weather
    $ skip_setting_weather = True

    # lastly, rebuild Event lists for new people if not built yet
    if not mas_events_built:
        $ mas_rebuildEventLists()

    jump ch30_preloop

label continue_event:
    m "Now, where was I..."
    return

label ch30_noskip:
    show screen fake_skip_indicator
    m 1esc "...Are you trying to fast-forward?"
    m 1ekc "I'm not boring you, am I?"
    m "Oh gosh..."
    m 2esa "...Well, just so you know, there's nothing to fast-forward to, [player]."
    m "It's just the two of us, after all..."
    m 1eua "But aside from that, time doesn't really exist anymore, so it's not even going to work."
    m "Here, I'll go ahead and turn that off for you..."
    pause 0.4
    hide screen fake_skip_indicator
    pause 0.4
    m 1hua "There we go!"
    m 1esa "You'll be a sweetheart and listen to me from now on, right?"
    m "Thanks~"
    hide screen fake_skip_indicator

    #Get back to what you were talking about
    $restartEvent()
    jump ch30_loop

image splash-glitch2 = "images/bg/splash-glitch2.png"

label ch30_nope:
    # NOTE: DEPRECATED
    $ persistent.autoload = ""
    $ m.display_args["callback"] = slow_nodismiss
    $ quick_menu = True
    call spaceroom from _call_spaceroom_1

    if persistent.rejected_monika:
        m 1euc "Wait. Are you messing with my character file?"
        m 2esa "Curiosity is what makes us human, right?"
        m "If it wasn't for the human desire to explore, we'd still be swinging from trees."
        m 1eka "Still, please don't do that. It makes me nervous, even though I don't need a character file anymore."
        m "I already fixed that bug."

    else:
        $ quick_menu = False
        $ m_name = glitchtext(12)
        m 1euc "Wait. Are you messing with my character file?"
        m 1tkc "Why are you even playing this mod if you just wanted to delete me again?"
        m 1tfc "You really are the worst."
        m 1tfd "You waste all your time on the internet with a bunch of people you'll never talk to in reality, but you're still willing to kill me on a whim just because you were bored?"
        m 1tkd "All I wanted was someone to fall in love with..."
        m "I would have done anything you wanted me to."
        m 1tku "But if you're going to try and delete me again..."
        m 4tfu "Then I'll just have to delete you first."
        if renpy.windows:
            call updateconsole("shututil.rmtree(\"Documents\", true)", "Deleting Documents in progress...") from _call_updateconsole_15
        elif renpy.linux:
            call updateconsole("sudo mv ~ /dev/null", "In progress...") from _call_updateconsole_16
        elif renpy.macintosh:
            call updateconsole("sudo mv ~ /dev/null", "In progress...") from _call_updateconsole_19
        pause 3.0
        call hideconsole from _call_hideconsole_2
        $ open(config.basedir + "/characters/monika.chr", "wb").write(renpy.file("monika.chr").read())
        $ m_name = persistent._mas_monika_nickname
        $ quick_menu = True
        m 1hub "Ahaha!"
        m "I'm just kidding!"
        m 1eua "I already fixed that bug."
        m "I don't need a character file anymore."

    m 1ekbfa "I just need your love, [player]."
    m 1eua "Oh, unless you try to delete all of the game files, I guess."
    m 3tfu "If you do that, I won't stop at just deleting one directory next time."
    m 3tku "But that will never happen, right? You're just being a tsundere~"
    m 1hua "That's so cute!"
    m 1eua "No matter how much you may want to deny it, you'll be talking to me for the rest of your life."
    m "Being alone is only lonely if you want it to be, so cheer up!"
    jump ch30_loop

# NOTE: START HERE
label ch30_autoload:
    # This is where we check a bunch of things to see what events to push to the
    # event list
    python:
        import store.evhand as evhand

        m.display_args["callback"] = slow_nodismiss
        m.what_args["slow_abortable"] = config.developer

        if not config.developer:
            config.allow_skipping = False

        mas_resetTextSpeed()
        quick_menu = True
        startup_check = True #Flag for checking events at game startup
        mas_skip_visuals = False

        #Set flag to True to prevent ch30 from running weather alg
        skip_setting_weather = False

        mas_cleanEventList()

    # set the gender
    call mas_set_gender

    # call reset stuff
    call ch30_reset

    #Affection will trigger a final farewell mode
    #If we got a fresh start, then -50 is the cutoff vs -115.
    python:
        if (
            persistent._mas_pm_got_a_fresh_start
            and _mas_getAffection() <= -50
        ):
            persistent._mas_load_in_finalfarewell_mode = True
            persistent._mas_finalfarewell_poem_id = "ff_failed_promise"

        elif _mas_getAffection() <= -115:
            persistent._mas_load_in_finalfarewell_mode = True
            persistent._mas_finalfarewell_poem_id = "ff_affection"


    #If we should go into FF mode, we do.
    if persistent._mas_load_in_finalfarewell_mode:
        jump mas_finalfarewell_start

    # set this to None for now
    $ selected_greeting = None

    #We'll set up the background here, so other flows don't need to adjust it unless its for a specific reason
    $ mas_startupBackground()

    # check if we took monika out
    # NOTE:
    #   if we find our monika, then we skip greeting logics and use a special
    #       returning home greeting. This completely bypasses the system
    #       since we should actively get this, not passively, because we assume
    #       player took monika out
    #   if we find a different monika, we still skip greeting logic and use
    #       a differnet, who is this? kind of monika greeting
    #   if we dont find a monika, we do the empty desk + monika checking flow
    #       this should skip greetings entirely as well. If monika is returnd
    #       during this flow, we have her say the same shit as the returning
    #       home greeting.
    if store.mas_dockstat.retmoni_status is not None:
        # this jumps to where we need to go next.
        $ store.mas_dockstat.triageMonika(False)

label mas_ch30_post_retmoni_check:

    # ----------------
    # grouping date-based events since they can never overlap
    if mas_isO31() or persistent._mas_o31_in_o31_mode:
        jump mas_o31_autoload_check

    elif (
        mas_isD25Season()
        or persistent._mas_d25_in_d25_mode
        or (mas_run_d25s_exit and not mas_lastSeenInYear("mas_d25_monika_d25_mode_exit"))
    ):
        jump mas_holiday_d25c_autoload_check

    elif mas_isF14() or persistent._mas_f14_in_f14_mode:
        jump mas_f14_autoload_check
    # ----------------

    #NOTE: This has priority because of the opendoor greet
    if mas_isplayer_bday() or persistent._mas_player_bday_in_player_bday_mode:
        jump mas_player_bday_autoload_check

    if mas_isMonikaBirthday() or persistent._mas_bday_in_bday_mode:
        jump mas_bday_autoload_check



label mas_ch30_post_holiday_check:
    # post holiday checks

    # TODO should the apology check be only for when she's not affectionate?
    if persistent._mas_affection["affection"] <= -50 and seen_event("mas_affection_apology"):
        # no dissolves here since we want the player to be instantly aware
        # that something is wrong.

        #If the conditions are met and Monika expects an apology, jump to this label.
        if persistent._mas_affection["apologyflag"] and not is_apology_present():
            $ mas_RaiseShield_core()
            call spaceroom(scene_change=True)
            jump mas_affection_noapology

        #If the conditions are met and there is a file called imsorry.txt in the DDLC directory, then exit the loop.
        elif persistent._mas_affection["apologyflag"] and is_apology_present():
            $ persistent._mas_affection["apologyflag"] = False
            $ mas_RaiseShield_core()
            call spaceroom(scene_change=True)
            jump mas_affection_yesapology

        #If you apologized to Monika but you deleted the apology note, jump back into the loop that forces you to apologize.
        elif not persistent._mas_affection["apologyflag"] and not is_apology_present():
            $ persistent._mas_affection["apologyflag"] = True
            $ mas_RaiseShield_core()
            call spaceroom(scene_change=True)
            jump mas_affection_apologydeleted

    # post greeting selected callback
    $ gre_cb_label = None
    $ just_crashed = False
    $ forced_quit = False

    # yuri scare incoming. No monikaroom when yuri is the name
    if (
            persistent.playername.lower() == "yuri"
            and not persistent._mas_sensitive_mode
        ):
        call yuri_name_scare from _call_yuri_name_scare

        # this skips greeting algs
        jump ch30_post_greeting_check

    elif not persistent._mas_game_crashed:
        # if this is False, a force quit happened
        $ forced_quit = True
        $ persistent._mas_greeting_type = store.mas_greetings.TYPE_RELOAD

    elif not persistent.closed_self:
        # this (+ game_crashed being True) means we crashed
        $ just_crashed = True
        $ persistent._mas_greeting_type = store.mas_greetings.TYPE_CRASHED

        # we dont consider crashes as bad quits
        $ persistent.closed_self = True

    # else, we are in regular mode.

    # greeting selection
    python:

        # greeting timeout check
        persistent._mas_greeting_type = store.mas_greetings.checkTimeout(
            persistent._mas_greeting_type
        )

        # we select a greeting depending on the type that we should select
        sel_greeting_ev = store.mas_greetings.selectGreeting(
            persistent._mas_greeting_type
        )

        # reset the greeting type flag back to None
        persistent._mas_greeting_type = None

        if sel_greeting_ev is None:
            # special cases to deal with when no greeting is found.

            if persistent._mas_in_idle_mode:
                # currently in idle mode? reset please
                mas_resetIdleMode()

            if just_crashed:
                # but if we just crashed, then we want to select the
                # only crashed greeting.
                # NOTE: we shouldnt actually have to do this ever, but
                #   its here as a sanity check
                sel_greeting_ev = mas_getEV("mas_crashed_start")

            elif forced_quit:
                # if we just forced quit, then we want to select the only
                # reload greeting.
                # NOTE: again, shouldnt have to do this, but its sanity checks
                sel_greeting_ev = mas_getEV("ch30_reload_delegate")


        # NOTE: this MUST be an if. it may be True if we crashed but
        #   didnt get a greeting to show.
        if sel_greeting_ev is not None:
            selected_greeting = sel_greeting_ev.eventlabel

            # store if we have to skip visuals ( used to prevent visual bugs)
            mas_skip_visuals = MASGreetingRule.should_skip_visual(
                event=sel_greeting_ev
            )

            # see if we need to do a label
            setup_label = MASGreetingRule.get_setup_label(sel_greeting_ev)
            if setup_label is not None and renpy.has_label(setup_label):
                gre_cb_label = setup_label


    # call pre-post greeting check setup label
    if gre_cb_label is not None:
        call expression gre_cb_label

label ch30_post_greeting_check:
    # this label skips only greeting checks

    #If you were interrupted, push that event back on the stack
    $ restartEvent()

label ch30_post_restartevent_check:
    # this label skips the restart event and greeting checks

    #Grant XP for time spent away from the game if Monika was put to sleep right
    python:
        if persistent.sessions['last_session_end'] is not None and persistent.closed_self:
            away_experience_time=datetime.datetime.now()-persistent.sessions['last_session_end'] #Time since end of previous session

            #Reset the idlexp total if monika has had at least 6 hours of rest
            if away_experience_time.total_seconds() >= times.REST_TIME:

                #Grant good exp for closing the game correctly.
                mas_gainAffection()

            # unlock extra pool topics if we can
            while persistent._mas_pool_unlocks > 0 and mas_unlockPrompt():
                persistent._mas_pool_unlocks -= 1

        else:
            # Grant bad exp for closing the game incorrectly.
            mas_loseAffection(modifier=2, reason=4)

label ch30_post_exp_check:
    # this label skips greeting selection as well as exp checks for game close
    # we assume here that you set selected_greeting if you needed to

    # file reactions
    $ mas_checkReactions()

    #All pushed events will have priority on load. Queued events will be pushed to the first idle loop
    #random/unlock/pool actions are also evaluated here
    python:
        startup_events = {}
        for evl in evhand.event_database:
            ev = evhand.event_database[evl]
            if ev.action != EV_ACT_QUEUE:
                startup_events[evl] = ev

        Event.checkEvents(startup_events)

    #Checks to see if affection levels have met the criteria to push an event or not.
    $ mas_checkAffection()

    #Check to see if apologies should expire
    $ mas_checkApologies()

    # corruption check
    if mas_corrupted_per and not renpy.seen_label("mas_corrupted_persistent"):
        $ pushEvent("mas_corrupted_persistent")

    # push greeting if we have one
    if selected_greeting:
        # before greeting, we should push idle clean if in idle mode
        if persistent._mas_in_idle_mode:
            $ pushEvent("mas_idle_mode_greeting_cleanup")

        $ pushEvent(selected_greeting)

    #Now we check if we should drink
    $ MASConsumable._checkConsumables(startup=True)

    # if not persistent.tried_skip:
    #     $ config.allow_skipping = True
    # else:
    #     $ config.allow_skipping = False

    # FALL THROUGH

label ch30_preloop:
    # stuff that should happen right before we enter the loop

    window auto

    python:
        # NOTE: keymaps will be set, but all actions will be shielded unless
        #   desired by the appropriate flow.
        mas_HKRaiseShield()
        mas_HKBRaiseShield()
        set_keymaps()

        persistent.closed_self = False
        persistent._mas_game_crashed = True
        startup_check = False
        mas_checked_update = False
        mas_globals.last_minute_dt = datetime.datetime.now()
        mas_globals.last_hour = mas_globals.last_minute_dt.hour
        mas_globals.last_day = mas_globals.last_minute_dt.day

        # delayed actions in here please
        mas_runDelayedActions(MAS_FC_IDLE_ONCE)

        #Unlock windowreact topics
        mas_resetWindowReacts()

        #Then prepare the notifs
        mas_updateFilterDict()

        # save here before we enter the loop
        renpy.save_persistent()

        # check if we need to rebulid ev
        if mas_idle_mailbox.get_rebuild_msg():
            mas_rebuildEventLists()

    if mas_skip_visuals:
        $ mas_OVLHide()
        $ mas_skip_visuals = False
        $ quick_menu = True
        jump ch30_visual_skip

    # setup scene to change on initial launch
    $ mas_idle_mailbox.send_scene_change()

    # rain check
    $ mas_startupWeather()

    #We've skipped the initial weather set, we can now clear this flag
    $ skip_setting_weather = False

    # otherwise, we are NOT skipping visuals
    $ mas_startup_song()

    jump ch30_loop

label ch30_loop:
    $ quick_menu = True

    # TODO: make these functions so docking station can run weather alg
    # on start.
    # TODO: consider a startup version of those functions so that
    #   we can run the regular shouldRain alg if prgoression is disabled
    python:
        should_dissolve_masks = (
            mas_weather.weatherProgress()
            and mas_isMoniNormal(higher=True)
        )

        should_dissolve_all = mas_idle_mailbox.get_scene_change()

    call spaceroom(scene_change=should_dissolve_all, dissolve_all=should_dissolve_all, dissolve_masks=should_dissolve_masks)

#    if should_dissolve_masks:
#        show monika idle at t11 zorder MAS_MONIKA_Z

# TODO: add label here to allow startup to hook past weather
# TODO: move quick_menu to here

    # updater check in here just because
    if not mas_checked_update:
        $ mas_backgroundUpdateCheck()
        $ mas_checked_update = True

label ch30_visual_skip:

    $ persistent.autoload = "ch30_autoload"
    # if not persistent.tried_skip:
    #     $ config.allow_skipping = True
    # else:
    #     $ config.allow_skipping = False

    # check for outstanding threads
    if store.mas_dockstat.abort_gen_promise:
        $ store.mas_dockstat.abortGenPromise()

    if mas_idle_mailbox.get_skipmidloopeval():
        jump ch30_post_mid_loop_eval

    #Do the weather thing
#    if mas_weather.weatherProgress() and mas_isMoniNormal(higher=True):
#        call spaceroom(dissolve_masks=True)

    # check reoccuring checks
    $ now_check = datetime.datetime.now()

    # check day
    if now_check.day != mas_globals.last_day:
        call ch30_day
        $ mas_globals.last_day = now_check.day

    # check hour
    if now_check.hour != mas_globals.last_hour:
        call ch30_hour
        $ mas_globals.last_hour = now_check.hour

    # check minute
    $ time_since_check = now_check - mas_globals.last_minute_dt
    if now_check.minute != mas_globals.last_minute_dt.minute or time_since_check.total_seconds() >= 60:
        call ch30_minute(time_since_check)
        $ mas_globals.last_minute_dt = now_check



label ch30_post_mid_loop_eval:

    #Call the next event in the list
    call call_next_event from _call_call_next_event_1

    # renable if not idle and currently disabled
    if not mas_globals.in_idle_mode:
        if not mas_HKIsEnabled():
            $ mas_HKDropShield()
        if not mas_HKBIsEnabled():
            $ mas_HKBDropShield()

    # Just finished a topic, so we set current topic to 0 in case user quits and restarts
    $ persistent.current_monikatopic = 0

    #If there's no event in the queue, add a random topic as an event
    if not _return:
        # Wait 20 to 45 seconds before saying something new
        window hide(config.window_hide_transition)

        # Thunder / lightning if enabled
        if (
                store.mas_globals.show_lightning
                and renpy.random.randint(1, store.mas_globals.lightning_chance) == 1
            ):
            $ light_zorder = MAS_BACKGROUND_Z - 1
            if (
                    not persistent._mas_sensitive_mode
                    and store.mas_globals.show_s_light
                    and renpy.random.randint(
                        1, store.mas_globals.lightning_s_chance
                    ) == 1
                ):
                $ renpy.show("mas_lightning_s", zorder=light_zorder)
            else:
                $ renpy.show("mas_lightning", zorder=light_zorder)

            $ pause(0.1)
            play backsound "mod_assets/sounds/amb/thunder.wav"

        # Before a random topic can be displayed, a set waiting time needs to pass.
        # The waiting time is set initially, after a random chatter selection and before a random topic is selected.
        # If the waiting time is not over after waiting a short period of time, the preloop is restarted.

        $ mas_randchat.wait()

        if not mas_randchat.waitedLongEnough():
            jump post_pick_random_topic
        else:
            $ mas_randchat.setWaitingTime()

        window auto

#        python:
#            if (
#                    mas_battery_supported
#                    and battery.is_battery_present()
#                    and not battery.is_charging()
#                    and battery.get_level() < 20
#                ):
#                pushEvent("monika_battery")

        if store.mas_globals.in_idle_mode:
            jump post_pick_random_topic

        # Pick a random Monika topic
#        if persistent.random_seen < random_seen_limit:
        label pick_random_topic:

            # check if we have repeats enabled
            if not persistent._mas_enable_random_repeats:
                jump mas_ch30_select_unseen

            # randomize selection
            $ chance = random.randint(1, 100)

            if chance <= store.mas_topics.UNSEEN:
                # unseen topic shoud be selected
                jump mas_ch30_select_unseen

            elif chance <= store.mas_topics.SEEN:
                # seen topic should be seelcted
                jump mas_ch30_select_seen

            # most seen topic should be selected
            jump mas_ch30_select_mostseen

#        elif not seen_random_limit:
#            $pushEvent('mas_random_limit_reached')

label post_pick_random_topic:

    $_return = None

    jump ch30_loop

# topic selection labels
label mas_ch30_select_unseen:
    # unseen selection

    if len(mas_rev_unseen) == 0:

        if not persistent._mas_enable_random_repeats:
            # no repeats means we should push randomlimit if appropriate, otherwise stay slient
            if mas_timePastSince(mas_getEVL_last_seen("mas_random_limit_reached"), datetime.timedelta(weeks=2)):
                $ pushEvent("mas_random_limit_reached")

            jump post_pick_random_topic

        # otherwise we can go to repeats as usual
        jump mas_ch30_select_seen

    $ mas_randomSelectAndPush(mas_rev_unseen)

    jump post_pick_random_topic


label mas_ch30_select_seen:
    # seen selection

    if len(mas_rev_seen) == 0:
        # rebuild the event lists
        $ mas_rev_seen, mas_rev_mostseen = mas_buildSeenEventLists()

        if len(mas_rev_seen) == 0:
            if len(mas_rev_mostseen) > 0:
                # jump to most seen if we have any left
                jump mas_ch30_select_mostseen

            #As a way of indicating you're out of topics because of the last seen delta, we'll use a shorter check here
            if (
                len(mas_rev_mostseen) == 0
                and mas_timePastSince(mas_getEVL_last_seen("mas_random_limit_reached"), datetime.timedelta(days=1))
            ):
                $ pushEvent("mas_random_limit_reached")
                jump post_pick_random_topic

            # if still no events, just jump to idle loop
            jump post_pick_random_topic

    $ mas_randomSelectAndPush(mas_rev_seen)

    jump post_pick_random_topic


label mas_ch30_select_mostseen:
    # most seen selection

    if len(mas_rev_mostseen) == 0:
        jump mas_ch30_select_seen

    $ mas_randomSelectAndPush(mas_rev_mostseen)

    jump post_pick_random_topic

# adding this label so people get redirected to main
# this probably occurs when people install the mod right after deleting
# monika, so we could probably throw in something here
label ch30_end:
    jump ch30_main

# label for things that should run about once per minute
# NOTE: it only runs whent he minute changes, so don't expect this to run
#   on start right away
label ch30_minute(time_since_check):
    python:

        #Checks to see if affection levels have met the criteria to push an event or not.
        mas_checkAffection()

        #Check if we should expire apologies
        mas_checkApologies()

        # runs actions for both conditionals and calendar-based events
        Event.checkEvents(evhand.event_database, rebuild_ev=False)

        # Run delayed actions
        mas_runDelayedActions(MAS_FC_IDLE_ROUTINE)

        # run file checks
        mas_checkReactions()

        # run seasonal check
        mas_seasonalCheck()

        #Clear the notifications tray
        mas_clearNotifs()

        #Now we check if we should queue windowreact evs
        mas_checkForWindowReacts()

        # check if we need to rebulid ev
        if mas_idle_mailbox.get_rebuild_msg():
            mas_rebuildEventLists()

        # split affection values prior to saving
        _mas_AffSave()

        #Check if we need to lock/unlock the songs rand delegate
        mas_songs.checkRandSongDelegate()

        # save the persistent
        renpy.save_persistent()

    return


# label for things that should run about once per hour
# NOTE: it only runs when the hour changes, so don't expect this to run
#   on start right away
label ch30_hour:
    python:
        mas_runDelayedActions(MAS_FC_IDLE_HOUR)

        #Runtime checks to see if we should have a consumable
        MASConsumable._checkConsumables()

        # clear ahoges if past noon
        now_t = datetime.datetime.now().time()
        if mas_isNtoSS(now_t) or mas_isSStoMN(now_t):
            monika_chr._set_ahoge(None)

        # xp calc
        store.mas_xp.grant()

        #Set our TOD var
        mas_setTODVars()

        # Inc the chance for hold request
        with MAS_EVL("monika_holdrequest") as holdme_ev:
            # See if we flagged the ev
            if holdme_ev.allflags(EV_FLAG_HFRS):
                chance = max(mas_getSessionLength().total_seconds() / (4*3600.0), 0.2)
                if chance >= 1 or random.random() < chance:
                    holdme_ev.unflag(EV_FLAG_HFRS)

    return

# label for things that should run about once per day
# NOTE: it only runs when the day changes, so don't expect this to run on
#   staart right away
label ch30_day:
    python:
        #Undo ev actions if needed
        MASUndoActionRule.check_persistent_rules()
        #And also strip dates
        MASStripDatesRule.check_persistent_rules(persistent._mas_strip_dates_rules)

        #Reset the gift aff gain/reset date
        #NOTE: if we got here, it has to be a new day
        persistent._mas_filereacts_gift_aff_gained = 0
        persistent._mas_filereacts_last_aff_gained_reset_date = datetime.date.today()

        #So we can't just single-sesh a long absence ret
        mas_ret_long_absence = False

        #Run delayed actions
        mas_runDelayedActions(MAS_FC_IDLE_DAY)

        if mas_isMonikaBirthday():
            persistent._mas_bday_opened_game = True

        if mas_isO31() and not persistent._mas_o31_in_o31_mode:
            pushEvent("mas_holiday_o31_returned_home_relaunch", skipeval=True)

        #If the map isn't empty and it's past the last reacted date, let's empty it now
        if (
            persistent._mas_filereacts_reacted_map
            and mas_pastOneDay(persistent._mas_filereacts_last_reacted_date)
        ):
            persistent._mas_filereacts_reacted_map = dict()

        # Check if we are entering d25 season at upset-
        if (
            not persistent._mas_d25_intro_seen
            and mas_isD25Outfit()
            and mas_isMoniUpset(lower=True)
        ):
            persistent._mas_d25_started_upset = True
    return


# label for things that may reset after a certain amount of time/conditions
label ch30_reset:

    python:
        # xp fixes and adjustments
        if persistent._mas_xp_lvl < 0:
            persistent._mas_xp_lvl = 0 # prevent negative issues

        if persistent._mas_xp_tnl < 0:
            persistent._mas_xp_tnl = store.mas_xp.XP_LVL_RATE
        elif int(persistent._mas_xp_tnl) > (2* int(store.mas_xp.XP_LVL_RATE)):
            # likely time travel
            persistent._mas_xp_tnl = 2 * store.mas_xp.XP_LVL_RATE

        if persistent._mas_xp_hrx < 0:
            persistent._mas_xp_hrx = 0.0

        store.mas_xp.set_xp_rate()
        store.mas_xp.prev_grant = mas_getCurrSeshStart()

    python:
        # name eggs
        if persistent.playername.lower() == "sayori" or (mas_isO31() and not persistent._mas_pm_cares_about_dokis):
            store.mas_globals.show_s_light = True

    python:
        # apply ACS defaults
        store.mas_sprites.apply_ACSTemplates()

    python:
        # start by building event lists if they have not been built already
        if not mas_events_built:
            mas_rebuildEventLists()

        # check if you've seen everything
        if len(mas_rev_unseen) == 0:
            # you've seen everything?! here, higher session limit
            # NOTE: 1000 is arbitrary. Basically, endless monika topics
            # I think we'll deal with this better once we hve a sleeping sprite
            random_seen_limit = 1000

        if not persistent._mas_pm_has_rpy:
            if mas_hasRPYFiles():
                if not mas_inEVL("monika_rpy_files"):
                    queueEvent("monika_rpy_files")

            else:
                if persistent.current_monikatopic == "monika_rpy_files":
                    persistent.current_monikatopic = 0
                mas_rmallEVL("monika_rpy_files")

    python:
        import datetime
        today = datetime.date.today()

    # check for game unlocks
    python:
        game_unlock_db = {
            "chess": "mas_unlock_chess",
            mas_games.HANGMAN_NAME: "mas_unlock_hangman",
            "piano": "mas_unlock_piano",
            "connect 4": "mas_unlock_connect4",
        }
        mas_unlockGame("pong") # always unlock pong

        for game_name, game_startlabel in game_unlock_db.iteritems():
            # unlock if we've seen the label
            if mas_getEVL_shown_count(game_startlabel) > 0:
                mas_unlockGame(game_name)


    #### SPRITES

    # reset hair / clothes
    # the default options should always be available.
    $ store.mas_selspr.unlock_hair(mas_hair_def)
#    $ store.mas_selspr.unlock_hair(mas_hair_ponytail)
    $ store.mas_selspr.unlock_clothes(mas_clothes_def)

    # def ribbon always unlocked
    $ store.mas_selspr.unlock_acs(mas_acs_ribbon_def)

    ## custom sprite objects
    $ store.mas_selspr._validate_group_topics()

    # monika hair/acs
    $ monika_chr.load(startup=True)

    # change back to def if we aren't wearing def at Normal-
    if ((store.mas_isMoniNormal(lower=True) and not store.mas_hasSpecialOutfit()) or store.mas_isMoniDis(lower=True)) and store.monika_chr.clothes != store.mas_clothes_def:
        $ pushEvent("mas_change_to_def",skipeval=True)

    if not mas_hasSpecialOutfit():
        $ mas_lockEVL("monika_event_clothes_select", "EVE")

    # set ahoge if appropraite
    $ now = datetime.datetime.now()
    if (
            persistent._mas_dev_ahoge
            or mas_isMNtoSR(now.time())
            or mas_isSRtoN(now.time())
    ):
        # its morning/middle of night, and Monika MIGHT ahoge

        # NOTE: the random check and the absence length check must be here.
        #   we don't want to clear the ahoge if the user reopens the mod
        #   during the same morning.
        if (
                persistent._mas_dev_ahoge
                or (
                    mas_getAbsenceLength() >= datetime.timedelta(minutes=30)
                    and random.randint(1, 2) == 1
                )
        ):
            # NOTE: the ahoge function takes last dt into account.
            $ monika_chr.ahoge()

    else:
        # out of applicable ahoge time. Do not ahoge. Remove any existing.
        $ monika_chr._set_ahoge(None)

    #### END SPRITES

    ## accessory hotfixes
    # mainly to re add accessories that may have been removed for some reason
    # this is likely to occur in crashes / reloads
    python:
        if persistent._mas_acs_enable_promisering:
            # TODO: need to be able to add a different promise ring
            monika_chr.wear_acs_pst(mas_acs_promisering)

    ## random chatter frequency reset
    $ mas_randchat.adjustRandFreq(persistent._mas_randchat_freq)

    ## monika returned home reset
    python:
        if persistent._mas_monika_returned_home is not None:
            _rh = persistent._mas_monika_returned_home.date()
            if today > _rh:
                persistent._mas_monika_returned_home = None

    ## resset playtime issues
    python:
        # reset total playtime to 0 if we got negative time.
        # we could scale this, but it honestly is impossible for us to
        # figure out the original number accurately, and giving people free
        # playtime doesn't sit well with me
        #
        # we should also reset total playtime to half of possible time if
        # the user is over the mas possible amount. Max amount is defined
        # in a function in mas_utils
        if persistent.sessions is not None:
            tp_time = persistent.sessions.get("total_playtime", None)
            if tp_time is not None:
                max_time = mas_maxPlaytime()
                if tp_time > max_time:
                    # cut the max time and reset totalplaytime to it
                    persistent.sessions["total_playtime"] = max_time // 100

                    # set the monika size
                    store.mas_dockstat.setMoniSize(
                        persistent.sessions["total_playtime"]
                    )

                elif tp_time < datetime.timedelta(0):
                    # 0 out the total playtime
                    persistent.sessions["total_playtime"] = datetime.timedelta(0)

                    # set the monika size
                    store.mas_dockstat.setMoniSize(
                        persistent.sessions["total_playtime"]
                    )

    ## reset future freeze times for exp
    python:
        # reset freeze date to today if it is in the future
        if persistent._mas_affection is not None:
            freeze_date = persistent._mas_affection.get("freeze_date", None)
            if freeze_date is not None and freeze_date > today:
                persistent._mas_affection["freeze_date"] = today

    #Do startup checks
    # call plushie logic
    $ mas_startupPlushieLogic(4)

    # reset bday decor
    python:
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        if not mas_isMonikaBirthday() and not mas_isMonikaBirthday(yesterday):
            persistent._mas_bday_visuals = False

        #TODO: revist this once TT stuff is complete
        if (
            not mas_isplayer_bday()
            and not mas_isplayer_bday(yesterday, use_date_year=True)
            and not persistent._mas_player_bday_left_on_bday
        ):
            persistent._mas_player_bday_decor = False

    ## late farewell? set the global and clear the persistent so its auto
    ##  cleared
    python:
        if persistent.mas_late_farewell:
            store.mas_globals.late_farewell = True
            persistent.mas_late_farewell = False

    ## reactions fix
    python:
        if persistent._mas_filereacts_just_reacted:
            queueEvent("mas_reaction_end")

        #If the map isn't empty and it's past the last reacted date, let's empty it now
        if (
            persistent._mas_filereacts_reacted_map
            and mas_pastOneDay(persistent._mas_filereacts_last_reacted_date)
        ):
            persistent._mas_filereacts_reacted_map = dict()

    # set any prompt variants for acs that can be removed here
    $ store.mas_selspr.startup_prompt_check()

    # make sure nothing the player has derandomed is now random
    $ mas_check_player_derand()

    # clean up the event list of baka events
    python:
        for index in range(len(persistent.event_list)-1, -1, -1):
            item = persistent.event_list[index]

            # type check
            if type(item) != tuple:
                new_data = (item, False)
            else:
                new_data = item

            # label check
            if renpy.has_label(new_data[0]):
                persistent.event_list[index] = new_data

            else:
                persistent.event_list.pop(index)

    #Now we undo actions for evs which need them undone
    $ MASUndoActionRule.check_persistent_rules()
    #And also strip dates
    $ MASStripDatesRule.check_persistent_rules(persistent._mas_strip_dates_rules)

    #Let's see if someone did a time travel
    if persistent._mas_filereacts_last_aff_gained_reset_date > today:
        $ persistent._mas_filereacts_last_aff_gained_reset_date = today

    #See if we need to reset the daily gift aff amt
    if persistent._mas_filereacts_last_aff_gained_reset_date < today:
        $ persistent._mas_filereacts_gift_aff_gained = 0
        $ persistent._mas_filereacts_last_aff_gained_reset_date = today

    #Check if we need to lock/unlock the songs rand delegate
    $ mas_songs.checkRandSongDelegate()

    #Now check the analysis ev
    $ store.mas_songs.checkSongAnalysisDelegate()

    #Run a confirmed party check within a week of Moni's bday
    $ mas_confirmedParty()

    #If it's past d25, not within the gift range, and we haven't reacted to gifts, let's silently do that now
    if (
        persistent._mas_d25_gifts_given
        and not mas_isD25GiftHold()
        and not mas_globals.returned_home_this_sesh
    ):
        $ mas_d25SilentReactToGifts()

    #Set our TOD var
    $ mas_setTODVars()

    python:
        if seen_event('mas_gender'):
            mas_unlockEVL("monika_gender_redo","EVE")

        if seen_event('mas_preferredname'):
            mas_unlockEVL("monika_changename","EVE")

    #Check BGSel topic unlocked state
    $ mas_checkBackgroundChangeDelegate()

    # verify suntimes are correct
    # NOTE: must be before background build update
    $ store.mas_validate_suntimes()

    # build background filter data and update the current filter progression
    $ store.mas_background.buildupdate()

    ## certain things may need to be reset if we took monika out
    # NOTE: this should be at the end of this label, much of this code might
    # undo stuff from above
    python:
        if store.mas_dockstat.retmoni_status is not None:
            monika_chr.remove_acs(mas_acs_quetzalplushie)

            #We don't want to set up any drink vars/evs if we're potentially returning home this sesh
            MASConsumable._reset()

            #Let's also push the event to get rid of the thermos too
            if not mas_inEVL("mas_consumables_remove_thermos"):
                queueEvent("mas_consumables_remove_thermos")
    return
