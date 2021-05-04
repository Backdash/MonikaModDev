## This splash screen is the first thing that Renpy will show the player
##
## Before load, check to be sure that the archive files were found.
## If not, display an error message and quit.
init -100 python:
    #Check for each archive needed
    for archive in ['audio','images','scripts','fonts']:
        if not archive in config.archives:
            #If one is missing, throw an error and chlose
            renpy.error("DDLC archive files not found in /game folder. Check installation and try again.")

## First, a disclaimer declaring this is a mod is shown, then there is a
## check for the original DDLC assets in the install folder. If those are
## not found, the player is directed to the developer's site to download.
##
init python:
    menu_trans_time = 1
    #The default splash message, originally shown in Act 1 and Act 4
    splash_message_default = _("This game is an unofficial fan work, unaffiliated with Team Salvato.")
    splash_messages = [
    _("Please support Doki Doki Literature Club & Team Salvato."),
    _("You are my sunshine,\nMy only sunshine"),
    _("I missed you."),
    _("Play with me"),
    _("It's just a game, mostly."),
    _("This game is not suitable for children\nor those who are easily disturbed?"),
    _("sdfasdklfgsdfgsgoinrfoenlvbd"),
    _("null"),
    _("I have granted kids to hell"),
    _("PM died for this."),
    _("It was only partially your fault."),
    _("This game is not suitable for children\nor those who are easily dismembered.")
#    "Don't forget to backup Monika's character file."
    ]

image splash_warning = ParameterizedText(style="splash_text", xalign=0.5, yalign=0.5)

##Here's where you can change the logo file to whatever you want
image menu_logo:
    "mod_assets/menu_new.png"
    subpixel True
    xcenter 240
    ycenter 120
    zoom 0.60
    menu_logo_move

#Removed rendering below of other char imgs in main menu

image menu_bg:
    topleft
    "gui/menu_bg.png"
    menu_bg_move

image game_menu_bg:
    topleft
    "gui/menu_bg.png"
    menu_bg_loop

image menu_fade:
    "white"
    menu_fadeout

image menu_art_m:
    subpixel True
    "gui/menu_art_m.png"
    xcenter 1000
    ycenter 640
    zoom 1.00
    menu_art_move(1.00, 1000, 1.00)

image menu_art_m_ghost:
    subpixel True
    "gui/menu_art_m_ghost.png"
    xcenter 1000
    ycenter 640
    zoom 1.00
    menu_art_move(1.00, 1000, 1.00)

image menu_nav:
    "gui/overlay/main_menu.png"
    menu_nav_move

image menu_particles:
    2.481
    xpos 224
    ypos 104
    ParticleBurst("gui/menu_particle.png", explodeTime=0, numParticles=20, particleTime=2.0, particleXSpeed=6, particleYSpeed=4).sm
    particle_fadeout

transform particle_fadeout:
    easeout 1.5 alpha 0

transform menu_bg_move:
    subpixel True
    topleft
    parallel:
        xoffset 0 yoffset 0
        linear 3.0 xoffset -100 yoffset -100
        repeat
    parallel:
        ypos 0
        time 0.65
        ease_cubic 2.5 ypos -500

transform menu_bg_loop:
    subpixel True
    topleft
    parallel:
        xoffset 0 yoffset 0
        linear 3.0 xoffset -100 yoffset -100
        repeat

transform menu_logo_move:
    subpixel True
    yoffset -300
    time 1.925
    easein_bounce 1.5 yoffset 0

transform menu_nav_move:
    subpixel True
    xoffset -500
    time 1.5
    easein_quint 1 xoffset 0

transform menu_fadeout:
    easeout 0.75 alpha 0
    time 2.481
    alpha 0.4
    linear 0.5 alpha 0

transform menu_art_move(z, x, z2):
    subpixel True
    yoffset 0 + (1200 * z)
    xoffset (740 - x) * z * 0.5
    zoom z2 * 0.75
    time 1.0
    parallel:
        ease 1.75 yoffset 0
    parallel:
        pause 0.75
        ease 1.5 zoom z2 xoffset 0

image intro:
    truecenter
    "white"
    0.5
    "bg/splash.png" with Dissolve(0.5, alpha=True)
    2.5
    "white" with Dissolve(0.5, alpha=True)
    0.5

image warning:
    truecenter
    "white"
    "splash_warning" with Dissolve(0.5, alpha=True)
    2.5
    "white" with Dissolve(0.5, alpha=True)
    0.5

image tos = "bg/warning.png"
image tos2 = "bg/warning2.png"


label splashscreen:
    python:
        _mas_AffStartup()

        persistent.sessions['current_session_start']=datetime.datetime.now()
        persistent.sessions['total_sessions'] = persistent.sessions['total_sessions']+ 1
        store.mas_calendar.loadCalendarDatabase()

        # set zoom
        store.mas_sprites.adjust_zoom()

        # We're about to start, all things should be loaded, we can check event conditionals
        Event.validateConditionals()

    if mas_corrupted_per and (mas_no_backups_found or mas_backup_copy_failed):
        # we have a corrupted persistent but was unable to recover via the
        # backup system
        call mas_backups_you_have_corrupted_persistent

    scene white

    #If this is the first time the game has been run, show a disclaimer
    if not persistent.first_run:
        $ quick_menu = False
        pause 0.5
        scene tos
        with Dissolve(1.0)
        pause 1.0
        "[config.name] is a Doki Doki Literature Club fan mod that is not affiliated with Team Salvato."
        "It is designed to be played only after the official game has been completed, and contains spoilers for the official game."
        "Game files for Doki Doki Literature Club are required to play this mod and can be downloaded for free at: http://ddlc.moe"
        menu:
            "By playing [config.name] you agree that you have completed Doki Doki Literature Club and accept any spoilers contained within."
            "I agree.":
                pass
        scene tos2
        with Dissolve(1.5)
        pause 1.0

        scene white
        with Dissolve(1.5)

        #Optional, load a copy of DDLC save data
        if not persistent.has_merged:
            call import_ddlc_persistent from _call_import_ddlc_persistent

        $ persistent.first_run = True

#    $ basedir = config.basedir.replace('\\', '/')
#   NOTE: this keeps screwing with my syntax coloring
    python:
        basedir = config.basedir.replace("\\", "/")

        # dump verseion to a firstrun-style file
        with open(basedir + "/game/masrun", "w") as versfile:
            versfile.write(config.name + "|" + config.version + "\n")


    #Check for game updates before loading the game or the splash screen

    #autoload handling
    #Use persistent.autoload if you want to bypass the splashscreen on startup for some reason
    if persistent.autoload and not _restart:
        jump autoload

    $ mas_enable_quit()

    # Start splash logic
    $ config.allow_skipping = False

    # Splash screen
    show white
    $ persistent.ghost_menu = False #Handling for easter egg from DDLC
    $ splash_message = splash_message_default #Default splash message
    $ config.main_menu_music = audio.t1
    $ renpy.music.play(config.main_menu_music)
    show intro with Dissolve(0.5, alpha=True)
    pause 2.5
    hide intro with Dissolve(0.5, alpha=True)
    #You can use random splash messages, as well. By default, they are only shown during certain acts.
    if renpy.random.randint(0, 3) == 0:
        $ splash_message = renpy.random.choice(splash_messages)
    show splash_warning "[splash_message]" with Dissolve(0.5, alpha=True)
    pause 2.0
    hide splash_warning with Dissolve(0.5, alpha=True)
    $ config.allow_skipping = False

    python:
        if persistent._mas_auto_mode_enabled:
            mas_darkMode(mas_current_background.isFltDay())
        else:
            mas_darkMode(not persistent._mas_dark_mode_enabled)
    return

label warningscreen:
    hide intro
    show warning
    pause 3.0

label after_load:
    $ config.allow_skipping = False
    $ _dismiss_pause = config.developer
    $ persistent.ghost_menu = False #Handling for easter egg from DDLC
    $ style.say_dialogue = style.normal
    #Check if the save has been tampered with
    if anticheat != persistent.anticheat:
        stop music
        scene black
        "The save file could not be loaded."
        "Are you trying to cheat?"
        #Handle however you want, default is to force reset all save data
        $ renpy.utter_restart()
    return


label autoload:
    python:
        # Stuff that's normally done after splash
        if "_old_game_menu_screen" in globals():
            _game_menu_screen = _old_game_menu_screen
            del _old_game_menu_screen
        if "_old_history" in globals():
            _history = _old_history
            del _old_history
        renpy.block_rollback()

        # Fix the game context (normally done when loading save file)
        renpy.context()._menu = False
        renpy.context()._main_menu = False
        main_menu = False
        _in_replay = None

    # explicity remove keymaps we dont want
    $ config.keymap["debug_voicing"] = list()
    $ config.keymap["choose_renderer"] = list()

    # Pop the _splashscreen label which has _confirm_quit as False and other stuff
    $ renpy.pop_call()

    # oh shit we are going to break everything right here
    if persistent._mas_chess_mangle_all:
        jump mas_chess_go_ham_and_delete_everything

    python:
        # okay lets setup monika's clothes
        # monika_chr.change_outfit(
        #     persistent._mas_monika_clothes,
        #     persistent._mas_monika_hair
        # )

        # need to set the monisize correctly
        store.mas_dockstat.setMoniSize(persistent.sessions["total_playtime"])
        # finally lets run actions that needed to be run
        mas_runDelayedActions(MAS_FC_START)
        # Start predict idle sprites
        renpy.start_predict("monika idle")

    #jump expression persistent.autoload
    # NOTE: we should always jump to ch30 instead
    jump ch30_autoload

label before_main_menu:
    $ config.main_menu_music = audio.t1
    return

label quit:
    python:
        store.mas_calendar.saveCalendarDatabase(CustomEncoder)
        persistent.sessions['last_session_end']=datetime.datetime.now()
        today_time = (
            persistent.sessions["last_session_end"]
            - persistent.sessions["current_session_start"]
        )
        new_time = today_time + persistent.sessions["total_playtime"]

        # prevent out of boudns time
        if datetime.timedelta(0) < new_time <= mas_maxPlaytime():
            persistent.sessions['total_playtime'] = new_time

        # set the monika size
        store.mas_dockstat.setMoniSize(persistent.sessions["total_playtime"])

        # save selectables
        store.mas_selspr.save_selectables()

        # save current hair / clothes / acs
        monika_chr.save()

        # save weather options
        store.mas_weather.saveMWData()

        # save bgs
        store.mas_background.saveMBGData()

        # remove special images
        store.mas_island_event.removeImages()

        #remove o31 cgs
        store.mas_o31_event.removeImages()

        # delayed action stuff
        mas_runDelayedActions(MAS_FC_END)
        store.mas_delact.saveDelayedActionMap()

        _mas_AffSave()

        # delete the monika file if we aren't leaving
        if not persistent._mas_dockstat_going_to_leave:
            store.mas_utils.trydel(mas_docking_station._trackPackage("monika"))

        # clear image caches
        store.mas_sprites._clear_caches()

        # xp calc
        store.mas_xp.grant()

    return
