init 100 python:
    layout.QUIT = store.mas_layout.QUIT
    layout.UNSTABLE = store.mas_layout.UNSTABLE

init -1 python:
    layout.QUIT_YES = _("Please don't close the game on me!")
    layout.QUIT_NO = _("Thank you, [player]!\nLet's spend more time together~")

    # tooltips
    layout.MAS_TT_SENS_MODE = (
        "Sensitive mode removes content that may be disturbing, offensive, "
        " or considered tasteless."
    )
    layout.MAS_TT_UNSTABLE = (
        "Unstable mode downloads updates from the experimental unstable "
        "branch of development. It is HIGHLY recommended to make a backup "
        "of your persistents before enabling this mode."
    )
    layout.MAS_TT_REPEAT = _(
        "Enable this to let Monika repeat topics that you have already seen."
    )
    layout.MAS_TT_NOTIF = _(
        "Enabling this will let Monika use your system's notifications and check if MAS is your active window "
    )
    layout.MAS_TT_NOTIF_SOUND = _(
        "If enabled, a custom notification sound will play for Monika's notifications "
    )
    layout.MAS_TT_G_NOTIF = _(
        "Enables notifications for the selected group."
    )
    layout.MAS_TT_ACTV_WND = (
        "Enabling this will allow Monika to see your active window "
        "and offer some comments based on what you're doing."
    )

    _TXT_FINISHED_UPDATING = (
        "The updates have been installed. Please reopen Monika After Story.\n\n"
        "Get spritepacks {a=http://monikaafterstory.com/releases.html}{i}{u}from our website{/u}{/i}{/a}.\n"
        "See the patch notes {a=https://github.com/Monika-After-Story/MonikaModDev/releases/latest}{i}{u}here{/u}{/i}{/a}.\n"
        "Confused about some features? Take a look at our {a=https://github.com/Monika-After-Story/MonikaModDev/wiki}{i}{u}wiki page{/u}{/i}{/a}."
    )


init python in mas_layout:
    import store
    import store.mas_affection as aff

    QUIT_YES = store.layout.QUIT_YES
    QUIT_NO = store.layout.QUIT_NO
    QUIT = _("Leaving without saying goodbye, [player]?")
    UNSTABLE = (
        "WARNING: Enabling unstable mode will download updates from the " +
        "experimental unstable branch. It is HIGHLY recommended to make a " +
        "backup of your persistents before enabling this mode. Please report " +
        "issues found here with an [[UNSTABLE] tag."
    )

    # quit yes messages affection scaled
    QUIT_YES_BROKEN = _("You could at least pretend that you care.")
    QUIT_YES_DIS = _(":(")
    QUIT_YES_AFF = _("T_T [player]...")

    # quit no messages affection scaled
    QUIT_NO_BROKEN = _("{i}Now{/i} you listen?")
    QUIT_NO_UPSET = _("Thanks for being considerate, [player].")
    QUIT_NO_HAPPY = _(":)")
    QUIT_NO_AFF_G = _("Good [boy].")
    QUIT_NO_AFF_GL = _("Good. :)")
    QUIT_NO_LOVE = _("<3 u")

    # quit messages affection scaled
    QUIT_BROKEN = _("Just go.")
    QUIT_AFF = _("Why are you here?\n Click 'No' and use the 'Goodbye' button, silly!")

    if store.persistent.gender == "M" or store.persistent.gender == "F":
        _usage_quit_aff = QUIT_NO_AFF_G
    else:
        _usage_quit_aff = QUIT_NO_AFF_GL

    # quit message dicts
    # tuple:
    #   [0]: quit message
    #   [1]: quit yes message
    #   [2]: quit no message
    # if something is None we go to the state closest to normal
    QUIT_MAP = {
        aff.BROKEN: (QUIT_BROKEN, QUIT_YES_BROKEN, QUIT_NO_BROKEN),
        aff.DISTRESSED: (None, QUIT_YES_DIS, None),
        aff.UPSET: (None, None, QUIT_NO_UPSET),
        aff.NORMAL: (QUIT, QUIT_YES, QUIT_NO),
        aff.HAPPY: (None, None, QUIT_NO_HAPPY),
        aff.AFFECTIONATE: (QUIT_AFF, QUIT_YES_AFF, _usage_quit_aff),
        aff.ENAMORED: (None, None, None),
        aff.LOVE: (None, None, QUIT_NO_LOVE)
    }


    def findMsg(start_aff, index):
        """
        Finds first non-None quit message we need

        This uses the cascade map from affection

        IN:
            start_aff - starting affection
            index - index of the tuple we need to look at

        RETURNS:
            first non-None quit message found.
        """
        msg = QUIT_MAP[start_aff][index]
        while msg is None:
            start_aff = aff._aff_cascade_map[start_aff]
            msg = QUIT_MAP[start_aff][index]

        return msg


    def setupQuits():
        """
        Sets up quit message based on the current affection state
        """
        curr_aff_state = store.mas_curr_affection

        quit_msg, quit_yes, quit_no = QUIT_MAP[curr_aff_state]

        if quit_msg is None:
            quit_msg = findMsg(curr_aff_state, 0)

        if quit_yes is None:
            quit_yes = findMsg(curr_aff_state, 1)

        if quit_no is None:
            quit_no = findMsg(curr_aff_state, 2)

        store.layout.QUIT = quit_msg
        store.layout.QUIT_YES = quit_yes
        store.layout.QUIT_NO = quit_no


init 900 python:
    import store.mas_layout
    store.mas_layout.setupQuits()


## Initialization
################################################################################

init offset = -1


################################################################################
## Styles
################################################################################

style default:
    font gui.default_font
    size gui.text_size
    color gui.text_color
    outlines [(2, "#000000aa", 0, 0)]
    line_overlap_split 1
    line_spacing 1

style default_monika is normal:
    slow_cps 30

style edited is default:
    font "gui/font/VerilySerifMono.otf"
    kerning 8
    outlines [(10, "#000", 0, 0)]
    pos (gui.text_xpos, gui.text_ypos)
    xanchor gui.text_xalign
    xsize gui.text_width
    text_align gui.text_xalign
    layout ("subtitle" if gui.text_xalign else "tex")

style edited_dark is default:
    font "gui/font/VerilySerifMono.otf"
    kerning 8
    outlines [] # FIXME: why there's no outlines?
    pos (gui.text_xpos, gui.text_ypos)
    xanchor gui.text_xalign
    xsize gui.text_width
    text_align gui.text_xalign
    layout ("subtitle" if gui.text_xalign else "tex")

style normal is default:
    pos (gui.text_xpos, gui.text_ypos)
    xanchor gui.text_xalign
    xsize gui.text_width
    text_align gui.text_xalign
    layout ("subtitle" if gui.text_xalign else "tex")

style input:
    color gui.accent_color

style hyperlink_text:
    color gui.accent_color
    hover_color gui.hover_color
    hover_underline True

style splash_text:
    font gui.default_font
    size 24
    color "#000"
    text_align 0.5
    outlines []

style poemgame_text:
    yalign 0.5
    font "gui/font/Halogen.ttf"
    size 30
    color "#000"
    outlines []
    hover_xoffset -3
    hover_outlines [(3, "#fef", 0, 0), (2, "#fcf", 0, 0), (1, "#faf", 0, 0)]

style poemgame_text_dark:
    yalign 0.5
    font "gui/font/Halogen.ttf"
    size 30
    color "#000"
    outlines []
    hover_xoffset -3
    hover_outlines [(3, "#fef", 0, 0), (2, "#fcf", 0, 0), (1, "#faf", 0, 0)]

style gui_text:
    font gui.interface_font
    size gui.interface_text_size
    color gui.interface_text_color


style button:
    properties gui.button_properties("button")
    xysize (None, 36)
    padding (4, 4, 4, 4)

style button_dark:
    properties gui.button_properties("button_dark")
    xysize (None, 36)
    padding (4, 4, 4, 4)

style button_text is gui_text:
    properties gui.button_text_properties("button")
    font gui.interface_font
    size gui.interface_text_size
    idle_color gui.idle_color
    hover_color gui.hover_color
    selected_color gui.selected_color
    insensitive_color gui.insensitive_color
    align (0.0, 0.5)

style button_text_dark is gui_text:
    properties gui.button_text_properties("button_dark")
    font gui.interface_font
    size gui.interface_text_size
    idle_color gui.idle_color
    hover_color gui.hover_color
    selected_color gui.selected_color
    insensitive_color gui.insensitive_color
    align (0.0, 0.5)

style label_text is gui_text:
    size gui.label_text_size
    color gui.accent_color

style label_text_dark is gui_text:
    size gui.label_text_size
    color gui.accent_color

style prompt_text is gui_text:
    size gui.interface_text_size
    color gui.text_color


#style bar:
#    ysize gui.bar_size
#    left_bar Frame("gui/bar/left.png", gui.bar_borders, tile=gui.bar_tile)
#    right_bar Frame("gui/bar/right.png", gui.bar_borders, tile=gui.bar_tile)

style vbar:
    xsize gui.bar_size
    top_bar Frame("gui/bar/top.png", gui.vbar_borders, tile=gui.bar_tile)
    bottom_bar Frame("gui/bar/bottom.png", gui.vbar_borders, tile=gui.bar_tile)

style bar:
    ysize 18
    base_bar Frame("gui/scrollbar/horizontal_poem_bar.png", tile=False)
    thumb Frame("gui/scrollbar/horizontal_poem_thumb.png", top=6, right=6, tile=True)

style scrollbar:
    ysize 18
    base_bar Frame("gui/scrollbar/horizontal_poem_bar.png", tile=False)
    thumb Frame("gui/scrollbar/horizontal_poem_thumb.png", top=6, right=6, tile=True)
    unscrollable "hide"
    bar_invert True

style scrollbar_dark:
    ysize 18
    base_bar Frame("gui/scrollbar/horizontal_poem_bar_d.png", tile=False)
    thumb Frame("gui/scrollbar/horizontal_poem_thumb.png", top=6, right=6, tile=True)
    unscrollable "hide"
    bar_invert True

#style vscrollbar:
#    xsize gui.scrollbar_size
#    base_bar Frame("gui/scrollbar/vertical_[prefix_]bar.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)
#    thumb Frame("gui/scrollbar/vertical_[prefix_]thumb.png", gui.vscrollbar_borders, tile=gui.scrollbar_tile)

style vscrollbar:
    xsize 18
    base_bar Frame("gui/scrollbar/vertical_poem_bar.png", tile=False)
    thumb Frame("gui/scrollbar/vertical_poem_thumb.png", left=6, top=6, tile=True)
    unscrollable "hide"
    bar_vertical True
    bar_invert True

style vscrollbar_dark:
    xsize 18
    base_bar Frame("gui/scrollbar/vertical_poem_bar_d.png", tile=False)
    thumb Frame("gui/scrollbar/vertical_poem_thumb.png", left=6, top=6, tile=True)
    unscrollable "hide"
    bar_vertical True
    bar_invert True

style slider:
    ysize 18
    base_bar Frame("gui/scrollbar/horizontal_poem_bar.png", tile=False)
    thumb "gui/slider/horizontal_hover_thumb.png"

style slider_dark:
    ysize 18
    base_bar Frame("gui/scrollbar/horizontal_poem_bar_d.png", tile=False)
    thumb "gui/slider/horizontal_hover_thumb.png"

style vslider:
    xsize gui.slider_size
    base_bar Frame("gui/slider/vertical_[prefix_]bar.png", gui.vslider_borders, tile=gui.slider_tile)
    thumb "gui/slider/vertical_[prefix_]thumb.png"

style frame:
    padding gui.frame_borders.padding
    background Frame("gui/frame.png", gui.frame_borders, tile=gui.frame_tile)

style frame_dark:
    padding gui.frame_borders.padding
    background Frame("gui/frame_d.png", gui.frame_borders, tile=gui.frame_tile)


################################################################################
## In-game screens
################################################################################


## Say screen ##################################################################
##
## The say screen is used to display dialogue to the player. It takes two
## parameters, who and what, which are the name of the speaking character and
## the text to be displayed, respectively. (The who parameter can be None if no
## name is given.)
##
## This screen must create a text displayable with id "what", as Ren'Py uses
## this to manage text display. It can also create displayables with id "who"
## and id "window" to apply style properties.
##
## https://www.renpy.org/doc/html/screen_special.html#say

screen say(who, what):
    style_prefix "say"

    window:
        id "window"

        text what id "what"

        if who is not None:

            window:
                style "namebox"
                text who id "who"

    # If there's a side image, display it above the text. Do not display
    # on the phone variant - there's no room.
    if not renpy.variant("small"):
        add SideImage() xalign (0.0 if not mas_globals.dark_mode else 2.5) yalign (1.0 if not mas_globals.dark_mode else 2.5)

    use quick_menu


style window is default:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize gui.textbox_height
    background Image("gui/textbox.png", xalign=0.5, yalign=1.0)

style window_dark is default:
    xalign 0.5
    xfill True
    yalign gui.textbox_yalign
    ysize gui.textbox_height
    background Image("gui/textbox_d.png", xalign=0.5, yalign=1.0)

style window_monika is window:
    background Image("gui/textbox_monika.png", xalign=0.5, yalign=1.0)

style window_monika_dark is window:
    background Image("gui/textbox_monika_d.png", xalign=0.5, yalign=1.0)

style namebox is default:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height
    background Frame("gui/namebox.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding

style namebox_dark is default:
    xpos gui.name_xpos
    xanchor gui.name_xalign
    xsize gui.namebox_width
    ypos gui.name_ypos
    ysize gui.namebox_height
    background Frame("gui/namebox_d.png", gui.namebox_borders, tile=gui.namebox_tile, xalign=gui.name_xalign)
    padding gui.namebox_borders.padding

style say_label is default:
    font gui.name_font
    size gui.name_text_size
    xalign gui.name_xalign
    yalign 0.5
    color gui.accent_color
    outlines [(3, "#b59", 0, 0), (1, "#b59", 1, 1)]

style say_label_dark is default:
    font gui.name_font
    size gui.name_text_size
    xalign gui.name_xalign
    yalign 0.5
    color "#FFD9E8"
    outlines [(3, "#DE367E", 0, 0), (1, "#DE367E", 1, 1)]

style say_dialogue is default:
    xpos gui.text_xpos
    xanchor gui.text_xalign
    xsize gui.text_width
    ypos gui.text_ypos
    text_align gui.text_xalign
    layout ("subtitle" if gui.text_xalign else "tex")

style say_thought is say_dialogue

image ctc:
    xalign 0.81 yalign 0.98 xoffset -5 alpha 0.0 subpixel True
    "gui/ctc.png"
    block:
        easeout 0.75 alpha 1.0 xoffset 0
        easein 0.75 alpha 0.5 xoffset -5
        repeat

## Input screen ################################################################
##
## This screen is used to display renpy.input. The prompt parameter is used to
## pass a text prompt in.
##
## This screen must create an input displayable with id "input" to accept the
## various input parameters.
##
## http://www.renpy.org/doc/html/screen_special.html#input

image input_caret:
    Solid("#b59")
    size (2,25) subpixel True
    block:
        linear 0.35 alpha 0
        linear 0.35 alpha 1
        repeat

screen input(prompt, use_return_button=False, return_button_prompt="Nevermind", return_button_value="cancel_input"):
    style_prefix "input"

    window:
        if use_return_button:
            hbox:
                style_prefix "quick"

                xalign 0.5
                yalign 0.995

                textbutton return_button_prompt:
                    action Return(return_button_value)

        vbox:
            align (0.5, 0.5)
            spacing 30

            text prompt style "input_prompt"
            input id "input"

style input_prompt:
    xmaximum gui.text_width
    xcenter 0.5
    text_align 0.5

style input:
    caret "input_caret"
    xmaximum gui.text_width
    xcenter 0.5
    text_align 0.5


## Choice screen ###############################################################
##
## This screen is used to display the in-game choices presented by the menu
## statement. The one parameter, items, is a list of objects, each with caption
## and action fields.
##
## http://www.renpy.org/doc/html/screen_special.html#choice

screen choice(items):
    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption action i.action


## When this is true, menu captions will be spoken by the narrator. When false,
## menu captions will be displayed as empty buttons.
define config.narrator_menu = True


style choice_vbox is vbox:
    xalign 0.5
    ypos 270
    yanchor 0.5
    spacing gui.choice_spacing

style choice_button is generic_button_light:
    xysize (420, None)
    padding (100, 5, 100, 5)

style choice_button_dark is generic_button_dark:
    xysize (420, None)
    padding (100, 5, 100, 5)

style choice_button_text is generic_button_text_light:
    text_align 0.5
    layout "subtitle"

style choice_button_text_dark is generic_button_text_dark:
    text_align 0.5
    layout "subtitle"

init python:
    def RigMouse():
        currentpos = renpy.get_mouse_pos()
        targetpos = [640, 345]
        if currentpos[1] < targetpos[1]:
            renpy.display.draw.set_mouse_pos((currentpos[0] * 9 + targetpos[0]) / 10.0, (currentpos[1] * 9 + targetpos[1]) / 10.0)

screen rigged_choice(items):
    style_prefix "choice"

    vbox:
        for i in items:
            textbutton i.caption action i.action

    timer 1.0/30.0 repeat True action Function(RigMouse)

style talk_choice_vbox is choice_vbox:
    xcenter 960

style talk_choice_button is choice_button

style talk_choice_button_dark is choice_button_dark

style talk_choice_button_text is choice_button_text

style talk_choice_button_text_dark is choice_button_text_dark


## This screen is used for the talk menu
screen talk_choice(items):
    style_prefix "talk_choice"

    vbox:
        for i in items:
            textbutton i.caption action i.action


## When this is true, menu captions will be spoken by the narrator. When false,
## menu captions will be displayed as empty buttons.
define config.narrator_menu = True


## Quick Menu screen ###########################################################
##
## The quick menu is displayed in-game to provide easy access to the out-of-game
## menus.

screen quick_menu():

    # Ensure this appears on top of other screens.
    zorder 100

    if quick_menu:

        # Add an in-game quick menu.
        hbox:
            style_prefix "quick"

            xalign 0.5
            yalign 0.995

            #textbutton _("Back") action Rollback()

#            textbutton _("History") action ShowMenu('history')
            textbutton _("History") action Function(_mas_quick_menu_cb, "history")

            textbutton _("Skip") action Skip() alternate Skip(fast=True, confirm=True)
            textbutton _("Auto") action Preference("auto-forward", "toggle")

#            textbutton _("Save") action ShowMenu('save')
            textbutton _("Save") action Function(_mas_quick_menu_cb, "save")

#            textbutton _("Load") action ShowMenu('load')
            textbutton _("Load") action Function(_mas_quick_menu_cb, "load")
            #textbutton _("Q.Save") action QuickSave()
            #textbutton _("Q.Load") action QuickLoad()

#            textbutton _("Settings") action ShowMenu("preferences")
            textbutton _("Settings") action Function(_mas_quick_menu_cb, "preferences")


## This code ensures that the quick_menu screen is displayed in-game, whenever
## the player has not explicitly hidden the interface.
#init python:
#    config.overlay_screens.append("quick_menu")

default quick_menu = True

# START: quick menu styles
style quick_button:
    properties gui.button_properties("quick_button")
    activate_sound gui.activate_sound

style quick_button_dark:
    properties gui.button_properties("quick_button_dark")
    activate_sound gui.activate_sound

style quick_button_text:
    properties gui.button_text_properties("quick_button")
    outlines []

style quick_button_text_dark:
    properties gui.button_text_properties("quick_button_dark")
    xysize (205, None)
    font gui.default_font
    size 14
    idle_color "#FFAA99"
    selected_color "#FFEEEB"
    hover_color "#FFD4CC"
    kerning 0.2
    outlines []

################################################################################
# Main and Game Menu Screens
################################################################################

## Navigation screen ###########################################################
##
## This screen is included in the main and game menus, and provides navigation
## to other menus, and to start the game.

init 4 python:
    def FinishEnterName():
        global player

        if not player:
            return

        if (
            mas_bad_name_comp.search(player)
            or mas_awk_name_comp.search(player)
        ):
            renpy.call_in_new_context("mas_bad_name_input")
            player = ""
            renpy.show(
                "chibika smile",
                at_list=[mas_chflip(-1), mas_chmove(x=130, y=552, travel_time=0)],
                layer="screens",
                zorder=10
            )
            return

        # if the name is correct, set it
        persistent.playername = player
        renpy.hide_screen("name_input")
        renpy.jump_out_of_context("start")

label mas_bad_name_input:
    show screen fake_main_menu
    $ disable_esc()

    if not renpy.seen_label("mas_bad_name_input.first_time_bad_name"):
        label .first_time_bad_name:
            play sound "sfx/glitch3.ogg"
            window show

            show chibika smile at mas_chflip(-1), mas_chriseup(x=700, y=552, travel_time=0.5) onlayer screens zorder 10
            pause 1

            show chibika at  mas_chflip_s(1) onlayer screens zorder 10
            "Hey there!"

            show chibika at mas_chlongjump(x=650, y=405, ymax=375, travel_time=0.8) onlayer screens zorder 10
            "I'm glad you decided to come back!"
            "I'm sure that you and Monika will be a great couple."

            show chibika sad at mas_chflip_s(-1) onlayer screens zorder 10
            "But if you call yourself names like that...{w=0.5}{nw}"

            show chibika at sticker_hop onlayer screens zorder 10
            extend "you won't win her heart!"

            show chibika smile at mas_chmove(x=300, y=405, travel_time=1) onlayer screens zorder 10
            "...But just embarrass her instead."

            show chibika at mas_chlongjump(x=190, y=552, ymax=375, travel_time=0.8) onlayer screens zorder 10
            "Why don't you choose something more appropriate."
            window auto

    else:
        show chibika smile at mas_chflip(-1), mas_chmove(x=130, y=552, travel_time=0), sticker_hop onlayer screens zorder 10
        "I don't think she would be comfortable calling you that..."
        "Why don't you choose something more appropriate instead."

    $ enable_esc()
    hide screen fake_main_menu
    return

# like main_menu, but w/o animations and w/ inactive buttons
screen fake_main_menu():
    style_prefix "main_menu"

    add "game_menu_bg"

    frame:
        pass

    vbox:
        style_prefix "navigation"

        xpos gui.navigation_xpos
        yalign 0.8

        spacing gui.navigation_spacing

        textbutton _("Just Monika")

        textbutton _("Load Game")

        textbutton _("Settings")

        if store.mas_submod_utils.submod_map:
            textbutton _("Submods")

        textbutton _("Hotkeys")

        if renpy.variant("pc"):

            textbutton _("Help")

            textbutton _("Quit")

    if gui.show_name:

        vbox:
            text "[config.name!t]":
                style "main_menu_title"

            text "[config.version]":
                style "main_menu_version"

    # add "fake_menu_logo"
    add Image(
        "mod_assets/menu_new.png"
    ) subpixel True xcenter 240 ycenter 120 zoom 0.60
    # add "fake_menu_art_m"
    add Image(
        "gui/menu_art_m.png"
    ) subpixel True xcenter 1000 ycenter 640 zoom 1.00

    key "K_ESCAPE" action Quit(confirm=False)

screen navigation():
    vbox:
        style_prefix "navigation"

        xpos gui.navigation_xpos
        yalign 0.8

        spacing gui.navigation_spacing


        if main_menu:

            textbutton _("Just Monika") action If(persistent.playername, true=Start(), false=Show(screen="name_input", message="Please enter your name", ok_action=Function(FinishEnterName)))

        else:

            textbutton _("History") action [ShowMenu("history"), SensitiveIf(renpy.get_screen("history") == None)]

            textbutton _("Save Game") action [ShowMenu("save"), SensitiveIf(renpy.get_screen("save") == None)]

        textbutton _("Load Game") action [ShowMenu("load"), SensitiveIf(renpy.get_screen("load") == None)]

        if _in_replay:

            textbutton _("End Replay") action EndReplay(confirm=True)

        elif not main_menu:
            textbutton _("Main Menu") action NullAction(), Show(screen="dialog", message="No need to go back there.\nYou'll just end up back here so don't worry.", ok_action=Hide("dialog"))

        textbutton _("Settings") action [ShowMenu("preferences"), SensitiveIf(renpy.get_screen("preferences") == None)]

        if store.mas_submod_utils.submod_map:
            textbutton _("Submods") action [ShowMenu("submods"), SensitiveIf(renpy.get_screen("submods") == None)]

        if store.mas_windowreacts.can_show_notifs and not main_menu:
            textbutton _("Alerts") action [ShowMenu("notif_settings"), SensitiveIf(renpy.get_screen("notif_settings") == None)]

        textbutton _("Hotkeys") action [ShowMenu("hot_keys"), SensitiveIf(renpy.get_screen("hot_keys") == None)]

        #textbutton _("About") action ShowMenu("about")

        if renpy.variant("pc"):

            ## Help isn't necessary or relevant to mobile devices.
            textbutton _("Help") action Help("README.html")

            ## The quit button is banned on iOS and unnecessary on Android.
            #If we're on the main menu, we don't want to confirm quit as Monika isn't back yet
            textbutton _("Quit") action Quit(confirm=(None if main_menu else _confirm_quit))

        if not main_menu:
            textbutton _("Return") action Return()

style navigation_button is gui_button:
    size_group "navigation"
    properties gui.button_properties("navigation_button")
    hover_sound gui.hover_sound
    activate_sound gui.activate_sound

style navigation_button_dark is gui_button:
    size_group "navigation"
    properties gui.button_properties("navigation_button_dark")
    hover_sound gui.hover_sound
    activate_sound gui.activate_sound

style navigation_button_text is gui_button_text:
    properties gui.button_text_properties("navigation_button")
    font "gui/font/RifficFree-Bold.ttf"
    color "#fff"
    outlines [(4, "#b59", 0, 0), (2, "#b59", 2, 2)]
    hover_outlines [(4, "#fac", 0, 0), (2, "#fac", 2, 2)]
    insensitive_outlines [(4, "#fce", 0, 0), (2, "#fce", 2, 2)]

style navigation_button_text_dark is gui_button_text_dark:
    properties gui.button_text_properties("navigation_button_dark")
    font "gui/font/RifficFree-Bold.ttf"
    color "#FFD9E8"
    outlines [(4, "#DE367E", 0, 0), (2, "#DE367E", 2, 2)]
    hover_outlines [(4, "#FF80B7", 0, 0), (2, "#FF80B7", 2, 2)]
    insensitive_outlines [(4, "#FFB2D4", 0, 0), (2, "#FFB2D4", 2, 2)]

## Main Menu screen ############################################################
##
## Used to display the main menu when Ren'Py starts.
##
## http://www.renpy.org/doc/html/screen_special.html#main-menu

screen main_menu():

    # This ensures that any other menu screen is replaced.
    tag menu

    style_prefix "main_menu"

#Just add Monika art now!

    #   if persistent.ghost_menu:
    #      add "white"
    #     add "menu_art_y_ghost"
    #    add "menu_art_n_ghost"
    #    else:
    add "menu_bg"
        #add "menu_art_y"
        #add "menu_art_n"
    frame:
        pass

## The use statement includes another screen inside this one. The actual
## contents of the main menu are in the navigation screen.
    use navigation

    if gui.show_name:

        vbox:
            text "[config.name!t]":
                style "main_menu_title"

            text "[config.version]":
                style "main_menu_version"

#    if not persistent.ghost_menu:
    add "menu_particles"
    add "menu_particles"
    add "menu_particles"
    add "menu_logo"
#    if persistent.ghost_menu:
#        add "menu_art_s_ghost"
#        add "menu_art_m_ghost"
#    else:
#        if persistent.playthrough == 1 or persistent.playthrough == 2:
#            add "menu_art_s_glitch"
#        else:
#            add "menu_art_s"
    add "menu_particles"
#        if persistent.playthrough != 4:
    add "menu_art_m"
    add "menu_fade"

    key "K_ESCAPE" action Quit(confirm=False)

style main_menu_version is main_menu_text:
    color "#000000"
    size 16
    outlines []

style main_menu_version_dark is main_menu_text:
    color mas_ui.dark_button_text_idle_color
    size 16
    outlines []

style main_menu_frame is empty:
    xsize 310
    yfill True
    background "menu_nav"

style main_menu_frame_dark is empty:
    xsize 310
    yfill True
    background "menu_nav"

style main_menu_vbox is vbox:
    xalign 1.0
    xoffset -20
    xmaximum 800
    yalign 1.0
    yoffset -20

style main_menu_text is gui_text:
    xalign 1.0
    layout "subtitle"
    text_align 1.0
    color gui.accent_color

style main_menu_title is main_menu_text:
    size gui.title_text_size


## Game Menu screen ############################################################
##
## This lays out the basic common structure of a game menu screen. It's called
## with the screen title, and displays the background, title, and navigation.
##
## The scroll parameter can be None, or one of "viewport" or "vpgrid". When this
## screen is intended to be used with one or more children, which are
## transcluded (placed) inside it.

screen game_menu_m():
    $ persistent.menu_bg_m = True
    add "gui/menu_bg_m.png"
    timer 0.3 action Hide("game_menu_m")

screen game_menu(title, scroll=None):

    # when teh game menu is open, we should disable the hotkeys
    key "noshift_T" action NullAction()
    key "noshift_t" action NullAction()
    key "noshift_M" action NullAction()
    key "noshift_m" action NullAction()
    key "noshift_P" action NullAction()
    key "noshift_p" action NullAction()
    key "noshift_E" action NullAction()
    key "noshift_e" action NullAction()

    # Add the backgrounds.
    if main_menu:
        add gui.main_menu_background
    else:
        key "mouseup_3" action Return()
        add gui.game_menu_background

    style_prefix "game_menu"

    frame:
        style "game_menu_outer_frame"

        hbox:

            # Reserve space for the navigation section.
            frame:
                style "game_menu_navigation_frame"

            frame:
                style "game_menu_content_frame"

                if scroll == "viewport":

                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        draggable True
                        yinitial 1.0

                        side_yfill True

                        vbox:
                            transclude

                elif scroll == "vpgrid":

                    vpgrid:
                        cols 1
                        yinitial 1.0

                        scrollbars "vertical"
                        mousewheel True
                        draggable True

                        side_yfill True

                        transclude

                else:

                    transclude

    use navigation

    # if not main_menu and not persistent.menu_bg_m and renpy.random.randint(0, 49) == 0:
    #     on "show" action Show("game_menu_m")

    label title style "game_menu_label"

    if main_menu:
        key "game_menu" action ShowMenu("main_menu")


style game_menu_outer_frame is empty:
    bottom_padding 30
    top_padding 120
    background "gui/overlay/game_menu.png"

style game_menu_outer_frame_dark is empty:
    bottom_padding 30
    top_padding 120
    background "gui/overlay/game_menu_d.png"

style game_menu_navigation_frame is empty:
    xsize 280
    yfill True

style game_menu_content_frame is empty:
    left_margin 40
    right_margin 20
    top_margin -40

style game_menu_viewport is gui_viewport:
    xsize 920

style game_menu_scrollbar is gui_vscrollbar

style game_menu_vscrollbar:
    unscrollable gui.unscrollable

style game_menu_side is gui_side:
    spacing 10

style game_menu_label is gui_label:
    xpos 50
    ysize 120

style game_menu_label_dark is gui_label:
    xpos 50
    ysize 120

style game_menu_label_text is gui_label_text:
    font "gui/font/RifficFree-Bold.ttf"
    size gui.title_text_size
    color "#fff"
    outlines [(6, "#b59", 0, 0), (3, "#b59", 2, 2)]
    yalign 0.5

style game_menu_label_text_dark is gui_label_text:
    font "gui/font/RifficFree-Bold.ttf"
    size gui.title_text_size
    color "#FFD9E8"
    outlines [(6, "#DE367E", 0, 0), (3, "#DE367E", 2, 2)]
    yalign 0.5

style return_button is navigation_button:
    xpos gui.navigation_xpos
    yalign 1.0
    yoffset -30

style return_button_dark is navigation_button:
    xpos gui.navigation_xpos
    yalign 1.0
    yoffset -30

style return_button_text is navigation_button_text

style return_button_text_dark is navigation_button_text_dark

## About screen ################################################################
##
## This screen gives credit and copyright information about the game and Ren'Py.
##
## There's nothing special about this screen, and hence it also serves as an
## example of how to make a custom screen.

screen about():

    tag menu

    ## This use statement includes the game_menu screen inside this one. The
    ## vbox child is then included inside the viewport inside the game_menu
    ## screen.
    use game_menu(_("About"), scroll="viewport"):

        style_prefix "about"

        vbox:

            label "[config.name!t]"
            text _("Version [config.version!t]\n")

            ## gui.about is usually set in options.rpy.
            if gui.about:
                text "[gui.about!t]\n"

            text _("Made with {a=https://www.renpy.org/}Ren'Py{/a} [renpy.version_only].\n\n[renpy.license!t]")


## This is redefined in options.rpy to add text to the about screen.
define gui.about = ""


style about_label is gui_label

style about_label_text is gui_label_text:
    size gui.label_text_size

style about_text is gui_text


## Load and Save screens #######################################################
##
## These screens are responsible for letting the player save the game and load
## it again. Since they share nearly everything in common, both are implemented
## in terms of a third screen, file_slots.
##
## https://www.renpy.org/doc/html/screen_special.html#save
## https://www.renpy.org/doc/html/screen_special.html#load

screen save():

    tag menu

    use file_slots(_("Save"))


screen load():

    tag menu

    use file_slots(_("Load"))

init python:
    def FileActionMod(name, page=None, **kwargs):
        if renpy.current_screen().screen_name[0] == "save":
            return Show(screen="dialog", message="There's no point in saving anymore.\nDon't worry, I'm not going anywhere.", ok_action=Hide("dialog"))


screen file_slots(title):

    default page_name_value = FilePageNameInputValue()

    use game_menu(title):

        fixed:

            ## This ensures the input will get the enter event before any of the
            ## buttons do.
            order_reverse True

            # The page name, which can be edited by clicking on a button.

            button:
                style "page_label"

                #key_events True
                xalign 0.5
                #action page_name_value.Toggle()

                input:
                    style "page_label_text"
                    value page_name_value

            ## The grid of file slots.
            grid gui.file_slot_cols gui.file_slot_rows:
                style_prefix "slot"

                xalign 0.5
                yalign 0.5

                spacing gui.slot_spacing

                for i in range(gui.file_slot_cols * gui.file_slot_rows):

                    $ slot = i + 1

                    button:
                        action FileActionMod(slot)

                        has vbox

                        add FileScreenshot(slot) xalign 0.5

                        text FileTime(slot, format=_("{#file_time}%A, %B %d %Y, %H:%M"), empty=_("empty slot")):
                            style "slot_time_text"

                        text FileSaveName(slot):
                            style "slot_name_text"

                        key "save_delete" action FileDelete(slot)

            ## Buttons to access other pages.
            hbox:
                style_prefix "page"

                xalign 0.5
                yalign 1.0

                spacing gui.page_spacing

                #textbutton _("<") action FilePagePrevious(max=9, wrap=True)

                #textbutton _("{#auto_page}A") action FilePage("auto")

                #textbutton _("{#quick_page}Q") action FilePage("quick")

                # range(1, 10) gives the numbers from 1 to 9.
                for page in range(1, 10):
                    textbutton "[page]" action FilePage(page)

                #textbutton _(">") action FilePageNext(max=9, wrap=True)


style page_label is gui_label:
    xpadding 50
    ypadding 3

style page_label_dark is gui_label:
    xpadding 50
    ypadding 3

style page_label_text is gui_label_text:
    color "#000"
    outlines []
    text_align 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_label_text_dark is gui_label_text:
    color "#FFD9E8"
    outlines []
    text_align 0.5
    layout "subtitle"
    hover_color gui.hover_color

style page_button is gui_button:
    properties gui.button_properties("page_button")

style page_button_text is gui_button_text:
    properties gui.button_text_properties("page_button")
    outlines []

style slot_button is gui_button:
    properties gui.button_properties("slot_button")

style slot_button_dark is gui_button:
    properties gui.button_properties("slot_button")

style slot_button_text is gui_button_text:
    properties gui.button_text_properties("slot_button")
    color "#666"
    outlines []

style slot_button_text_dark is gui_button_text:
    properties gui.button_text_properties("slot_button")
    color "#8C8C8C"
    outlines []

style slot_time_text is slot_button_text

style slot_name_text is slot_button_text

## Preferences screen ##########################################################
##
## The preferences screen allows the player to configure the game to better suit
## themselves.
##
## https://www.renpy.org/doc/html/screen_special.html#preferences

screen preferences():

    tag menu

    if renpy.mobile:
        $ cols = 2
    else:
        $ cols = 4

    default tooltip = Tooltip("")

    use game_menu(_("Settings"), scroll="viewport"):

        vbox:
            xoffset 50

            hbox:
                box_wrap True

                if renpy.variant("pc"):

                    vbox:
                        style_prefix "radio"
                        label _("Display")
                        textbutton _("Window") action Preference("display", "window")
                        textbutton _("Fullscreen") action Preference("display", "fullscreen")

#                vbox:
#                    style_prefix "check"
#                    label _("Skip")
#                    textbutton _("Unseen Text") action Preference("skip", "toggle")
#                    textbutton _("After Choices") action Preference("after choices", "toggle")
                    #textbutton _("Transitions") action InvertSelected(Preference("transitions", "toggle"))

                #Disable/Enable space animation AND lens flair in room
                vbox:
                    style_prefix "check"
                    label _("Graphics")
                    textbutton _("Disable Animation") action ToggleField(persistent, "_mas_disable_animations")
                    textbutton _("Change Renderer") action Function(renpy.call_in_new_context, "mas_gmenu_start")

                    #Handle buttons
                    textbutton _("UI: Night Mode"):
                        action [Function(mas_settings._ui_change_wrapper, persistent._mas_dark_mode_enabled), Function(mas_settings._dark_mode_toggle)]
                        selected persistent._mas_dark_mode_enabled
                    textbutton _("UI: D/N Cycle"):
                        action [Function(mas_settings._ui_change_wrapper, mas_current_background.isFltDay()), Function(mas_settings._auto_mode_toggle)]
                        selected persistent._mas_auto_mode_enabled


                vbox:
                    style_prefix "check"
                    label _("Gameplay")
                    if not main_menu:
                        if persistent._mas_unstable_mode:
                            textbutton _("Unstable"):
                                action SetField(persistent, "_mas_unstable_mode", False)
                                selected persistent._mas_unstable_mode

                        else:
                            textbutton _("Unstable"):
                                action [Show(screen="dialog", message=layout.UNSTABLE, ok_action=Hide(screen="dialog")), SetField(persistent, "_mas_unstable_mode", True)]
                                selected persistent._mas_unstable_mode
                                hovered tooltip.Action(layout.MAS_TT_UNSTABLE)

                    textbutton _("Repeat Topics"):
                        action ToggleField(persistent,"_mas_enable_random_repeats", True, False)
                        hovered tooltip.Action(layout.MAS_TT_REPEAT)

                ## Additional vboxes of type "radio_pref" or "check_pref" can be
                ## added here, to add additional creator-defined preferences.
                vbox:
                    style_prefix "check"
                    label _(" ")
#                    textbutton _("Sensitive Mode"):
#                        action ToggleField(persistent, "_mas_sensitive_mode", True, False)
#                        hovered tooltip.Action(layout.MAS_TT_SENS_MODE)

                    if store.mas_windowreacts.can_do_windowreacts:
                        textbutton _("Window Reacts"):
                            action ToggleField(persistent, "_mas_windowreacts_windowreacts_enabled", True, False)
                            hovered tooltip.Action(layout.MAS_TT_ACTV_WND)

            null height (4 * gui.pref_spacing)

            hbox:
                style_prefix "slider"
                box_wrap True

                python:
                    ### random chatter preprocessing
                    if mas_randchat_prev != persistent._mas_randchat_freq:
                        # adjust the randoms if it changed
                        mas_randchat.adjustRandFreq(
                            persistent._mas_randchat_freq
                        )

                    # setup the display string
                    rc_display = mas_randchat.getRandChatDisp(
                        persistent._mas_randchat_freq
                    )

                    # setup previous values
                    store.mas_randchat_prev = persistent._mas_randchat_freq


                    ### sunrise / sunset preprocessing
                    # figure out which value is changing (if any)
                    if mas_suntime.change_state == mas_suntime.RISE_CHANGE:
                        # we are modifying sunrise

                        if mas_suntime.sunrise > mas_suntime.sunset:
                            # ensure sunset remains >= than sunrise
                            mas_suntime.sunset = mas_suntime.sunrise

                        if mas_sunrise_prev == mas_suntime.sunrise:
                            # if no change since previous, then switch state
                            mas_suntime.change_state = mas_suntime.NO_CHANGE

                        mas_sunrise_prev = mas_suntime.sunrise

                    elif mas_suntime.change_state == mas_suntime.SET_CHANGE:
                        # we are modifying sunset

                        if mas_suntime.sunset < mas_suntime.sunrise:
                            # ensure sunrise remains <= than sunset
                            mas_suntime.sunrise = mas_suntime.sunset

                        if mas_sunset_prev == mas_suntime.sunset:
                            # if no change since previous, then switch state
                            mas_suntime.change_state = mas_suntime.NO_CHANGE

                        mas_sunset_prev = mas_suntime.sunset
                    else:
                        # decide if we are modifying sunrise or sunset

                        if mas_sunrise_prev != mas_suntime.sunrise:
                            mas_suntime.change_state = mas_suntime.RISE_CHANGE

                        elif mas_sunset_prev != mas_suntime.sunset:
                            mas_suntime.change_state = mas_suntime.SET_CHANGE

                        # set previous values
                        mas_sunrise_prev = mas_suntime.sunrise
                        mas_sunset_prev = mas_suntime.sunset


                    ## prepreocess display time
                    persistent._mas_sunrise = mas_suntime.sunrise * 5
                    persistent._mas_sunset = mas_suntime.sunset * 5
                    sr_display = mas_cvToDHM(persistent._mas_sunrise)
                    ss_display = mas_cvToDHM(persistent._mas_sunset)

                vbox:

                    hbox:
                        label _("Sunrise  ")

                        # display time
                        label _("[[ " + sr_display + " ]")

                    bar value FieldValue(mas_suntime, "sunrise", range=mas_max_suntime, style="slider")


                    hbox:
                        label _("Sunset  ")

                        # display time
                        label _("[[ " + ss_display + " ]")

                    bar value FieldValue(mas_suntime, "sunset", range=mas_max_suntime, style="slider")


                vbox:

                    hbox:
                        label _("Random Chatter  ")

                        # display str
                        label _("[[ " + rc_display + " ]")

                    bar value FieldValue(
                        persistent,
                        "_mas_randchat_freq",
                        range=store.mas_affection.RANDCHAT_RANGE_MAP[mas_curr_affection],
                        style="slider"
                    )

                    hbox:
                        label _("Ambient Volume")

                    bar value Preference("mixer amb volume")


                vbox:

                    label _("Text Speed")

                    #bar value Preference("text speed")
                    bar value FieldValue(_preferences, "text_cps", range=170, max_is_zero=False, style="slider", offset=30)

                    label _("Auto-Forward Time")

                    bar value Preference("auto-forward time")

                vbox:

                    if config.has_music:
                        label _("Music Volume")

                        hbox:
                            bar value Preference("music volume")

                    if config.has_sound:

                        label _("Sound Volume")

                        hbox:
                            bar value Preference("sound volume")

                            if config.sample_sound:
                                textbutton _("Test") action Play("sound", config.sample_sound)


                    if config.has_voice:
                        label _("Voice Volume")

                        hbox:
                            bar value Preference("voice volume")

                            if config.sample_voice:
                                textbutton _("Test") action Play("voice", config.sample_voice)

                    if config.has_music or config.has_sound or config.has_voice:
                        null height gui.pref_spacing

                        textbutton _("Mute All"):
                            action Preference("all mute", "toggle")
                            style "mute_all_button"


            hbox:
                #We disable updating on the main menu because it causes graphical issues
                #due to the spaceroom not being loaded in
                if not main_menu:
                    textbutton _("Update Version"):
                        action Function(renpy.call_in_new_context, 'forced_update_now')
                        style "navigation_button"

                textbutton _("Import DDLC Save Data"):
                    action Function(renpy.call_in_new_context, 'import_ddlc_persistent_in_settings')
                    style "navigation_button"


    text tooltip.value:
        xalign 0.0 yalign 1.0
        xoffset 300 yoffset -10
        style "main_menu_version"
#        layout "greedy"
#        text_align 0.5
#        xmaximum 650

    text "v[config.version]":
        xalign 1.0 yalign 0.0
        xoffset -10
        style "main_menu_version"

# Preference
style pref_label is gui_label:
    top_margin gui.pref_spacing
    bottom_margin 2

style pref_label_dark is gui_label:
    top_margin gui.pref_spacing
    bottom_margin 2

style pref_label_text is gui_label_text:
    font "gui/font/RifficFree-Bold.ttf"
    size 24
    color "#fff"
    outlines [(3, "#b59", 0, 0), (1, "#b59", 1, 1)]
    yalign 1.0

style pref_label_text_dark is gui_label_text:
    font "gui/font/RifficFree-Bold.ttf"
    size 24
    color "#FFD9E8"
    outlines [(3, "#DE367E", 0, 0), (1, "#DE367E", 1, 1)]
    yalign 1.0

style pref_vbox is vbox:
    xsize 225

# Radio
style radio_label is pref_label

style radio_label_dark is pref_label

style radio_label_text is pref_label_text

style radio_label_text_dark is pref_label_text

style radio_vbox is pref_vbox:
    spacing gui.pref_button_spacing

style radio_button is gui_button:
    properties gui.button_properties("radio_button")
    foreground "gui/button/check_[prefix_]foreground.png"
    padding (28, 4, 4, 4)

style radio_button_dark is gui_button_dark:
    properties gui.button_properties("radio_button_dark")
    foreground "gui/button/check_[prefix_]foreground_d.png"
    padding (28, 4, 4, 4)

style radio_button_text is gui_button_text:
    properties gui.button_text_properties("radio_button")
    font "gui/font/Halogen.ttf"
    outlines []

style radio_button_text_dark is gui_button_text_dark:
    properties gui.button_text_properties("radio_button_dark")
    font "gui/font/Halogen.ttf"
    color "#8C8C8C"
    hover_color "#FF80B7"
    selected_color "#DE367E"
    outlines []

# Check
style check_label is pref_label

style check_label_dark is pref_label

style check_label_text is pref_label_text

style check_label_text_dark is pref_label_text

style check_vbox is pref_vbox:
    spacing gui.pref_button_spacing

style check_button is gui_button:
    properties gui.button_properties("check_button")
    foreground "gui/button/check_[prefix_]foreground.png"
    padding (28, 4, 4, 4)

style check_button_dark is gui_button_dark:
    properties gui.button_properties("check_button_dark")
    foreground "gui/button/check_[prefix_]foreground_d.png"
    padding (28, 4, 4, 4)

style check_button_text is gui_button_text:
    properties gui.button_text_properties("check_button")
    font "gui/font/Halogen.ttf"
    outlines []

style check_button_text_dark is gui_button_text_dark:
    properties gui.button_text_properties("check_button_dark")
    font "gui/font/Halogen.ttf"
    color "#8C8C8C"
    hover_color "#FF80B7"
    selected_color "#DE367E"
    outlines []

# Mute all
style mute_all_button is check_button

style mute_all_button_dark is check_button_dark

style mute_all_button_text is check_button_text

style mute_all_button_text_dark is check_button_text_dark

# Slider
style slider_label is pref_label

style slider_label_dark is pref_label

style slider_label_text is pref_label_text

style slider_label_text_dark is pref_label_text

style slider_slider is gui_slider:
    xsize 350

style slider_slider_dark is gui_slider_dark:
    xsize 350

style slider_button is gui_button:
    properties gui.button_properties("slider_button")
    yalign 0.5
    left_margin 10

style slider_button_dark is gui_button:
    properties gui.button_properties("slider_button_dark")
    yalign 0.5
    left_margin 10

style slider_button_text is gui_button_text:
    properties gui.button_text_properties("slider_button")

style slider_button_text_dark is gui_button_text:
    properties gui.button_text_properties("slider_button_dark")

style slider_vbox:
    xsize 450

style slider_pref_vbox is pref_vbox

##Notifications Settings Screen
screen notif_settings():
    tag menu

    use game_menu(("Alerts"), scroll="viewport"):

        default tooltip = Tooltip("")

        vbox:
            style_prefix "check"
            hbox:
                spacing 25
                textbutton _("Use Notifications"):
                    action ToggleField(persistent, "_mas_enable_notifications")
                    selected persistent._mas_enable_notifications
                    hovered tooltip.Action(layout.MAS_TT_NOTIF)

                textbutton _("Sounds"):
                    action ToggleField(persistent, "_mas_notification_sounds")
                    selected persistent._mas_notification_sounds
                    hovered tooltip.Action(layout.MAS_TT_NOTIF_SOUND)

            label _("Alert Filters")

        hbox:
            style_prefix "check"
            box_wrap True
            spacing 25

            #Dynamically populate this
            for item in persistent._mas_windowreacts_notif_filters:
                if item != "Window Reactions" or persistent._mas_windowreacts_windowreacts_enabled:
                    textbutton _(item):
                        action ToggleDict(persistent._mas_windowreacts_notif_filters, item)
                        selected persistent._mas_windowreacts_notif_filters.get(item)
                        hovered tooltip.Action(layout.MAS_TT_G_NOTIF)


    text tooltip.value:
        xalign 0 yalign 1.0
        xoffset 300 yoffset -10
        style "main_menu_version"

## hotkeys helper screen
screen hot_keys():
    tag menu

    use game_menu(("Hotkeys"), scroll="viewport"):

        default tooltip = Tooltip("")

        # making each indivual list a vbox essentially lets us auto-align
        vbox:
            spacing 25

            hbox:
                style_prefix "check"
                vbox:
                    label _("General")
                    spacing 10
                    text _("Music")
                    text _("Play")
                    text _("Talk")
                    text _("Bookmark")
                    text _("Derandom")
                    text _("Fullscreen")
                    text _("Screenshot")
                    text _("Settings")

                vbox:
                    label _("")
                    spacing 10
                    text _("M")
                    text _("P")
                    text _("T")
                    text _("B")
                    text _("X")
                    text _("F")
                    text _("S")
                    text _("Esc")

            hbox:
                style_prefix "check"
                vbox:
                    label _("Music")
                    spacing 10
                    text _("Volume Up")
                    text _("Volume Down")
                    text _("Mute")

                vbox:
                    label _("")
                    spacing 10
                    text _("+")
                    text _("-")
                    text _("Shift-M")

    # there are lesser used hotkeys in Help that aren't needed here
    text "Click 'Help' for the complete list.":
        xalign 1.0 yalign 0.0
        xoffset -10
        style "main_menu_version"


## History screen ##############################################################
##
## This is a screen that displays the dialogue history to the player. While
## there isn't anything special about this screen, it does have to access the
## dialogue history stored in _history_list.
##
## https://www.renpy.org/doc/html/history.html

screen history():

    tag menu

    ## Avoid predicting this screen, as it can be very large.
    predict False

    use game_menu(_("History"), scroll=("vpgrid" if gui.history_height else "viewport")):

        style_prefix "history"

        for h in _history_list:

            window:

                ## This lays things out properly if history_height is None.
                has fixed:
                    yfit True

                if h.who:

                    label h.who:
                        style "history_name"

                        ## Take the color of the who text from the Character, if
                        ## set.
                        if "color" in h.who_args:
                            text_color h.who_args["color"]

                text h.what.replace("[","[[")  # ]" fix syntax highlight issue

        if not _history_list:
            label _("The dialogue history is empty.")


style history_window is empty:
    xfill True
    ysize gui.history_height

style history_name is gui_label:
    xpos gui.history_name_xpos
    xanchor gui.history_name_xalign
    ypos gui.history_name_ypos
    xsize gui.history_name_width

style history_name_text is gui_label_text:
    min_width gui.history_name_width
    text_align gui.history_name_xalign

style history_text is gui_text:
    xpos gui.history_text_xpos
    ypos gui.history_text_ypos
    xanchor gui.history_text_xalign
    xsize gui.history_text_width
    min_width gui.history_text_width
    text_align gui.history_text_xalign
    layout ("subtitle" if gui.history_text_xalign else "tex")

style history_label is gui_label:
    xfill True

style history_label_text is gui_label_text:
    xalign 0.5


## Help screen #################################################################
##
## A screen that gives information about key and mouse bindings. It uses other
## screens (keyboard_help, mouse_help, and gamepad_help) to display the actual
## help.

#screen help():
#
#    tag menu
#
#    default device = "keyboard"
#
#    use game_menu(_("Help"), scroll="viewport"):
#
#        style_prefix "help"
#
#        vbox:
#            spacing 15
#
#            hbox:
#
#                textbutton _("Keyboard") action SetScreenVariable("device", "keyboard")
#                textbutton _("Mouse") action SetScreenVariable("device", "mouse")
#
#                if GamepadExists():
#                    textbutton _("Gamepad") action SetScreenVariable("device", "gamepad")
#
#            if device == "keyboard":
#                use keyboard_help
#            elif device == "mouse":
#                use mouse_help
#            elif device == "gamepad":
#                use gamepad_help
#
#
#screen keyboard_help():
#
#    hbox:
#        label _("Enter")
#        text _("Advances dialogue and activates the interface.")
#
#    hbox:
#        label _("Space")
#        text _("Advances dialogue without selecting choices.")
#
#    hbox:
#        label _("Arrow Keys")
#        text _("Navigate the interface.")
#
#    hbox:
#        label _("Escape")
#        text _("Accesses the game menu.")
#
#    hbox:
#        label _("Ctrl")
#        text _("Skips dialogue while held down.")
#
#    hbox:
#        label _("Tab")
#        text _("Toggles dialogue skipping.")
#
#    hbox:
#        label _("Page Up")
#        text _("Rolls back to earlier dialogue.")
#
#    hbox:
#        label _("Page Down")
#        text _("Rolls forward to later dialogue.")
#
#    hbox:
#        label "H"
#        text _("Hides the user interface.")
#
#    hbox:
#        label "S"
#        text _("Takes a screenshot.")
#
#    hbox:
#        label "V"
#        text _("Toggles assistive {a=https://www.renpy.org/l/voicing}self-voicing{/a}.")
#
#
#screen mouse_help():
#
#    hbox:
#        label _("Left Click")
#        text _("Advances dialogue and activates the interface.")
#
#    hbox:
#        label _("Middle Click")
#        text _("Hides the user interface.")
#
#    hbox:
#        label _("Right Click")
#        text _("Accesses the game menu.")
#
#    hbox:
#        label _("Mouse Wheel Up\nClick Rollback Side")
#        text _("Rolls back to earlier dialogue.")
#
#    hbox:
#        label _("Mouse Wheel Down")
#        text _("Rolls forward to later dialogue.")
#
#
#screen gamepad_help():
#
#    hbox:
#        label _("Right Trigger\nA/Bottom Button")
#        text _("Advance dialogue and activates the interface.")
#
#    hbox:
#        label ("Left Trigger\nLeft Shoulder")
#        text _("Roll back to earlier dialogue.")
#
#    hbox:
#        label _("Right Shoulder")
#        text _("Roll forward to later dialogue.")
#
#    hbox:
#        label _("D-Pad, Sticks")
#        text _("Navigate the interface.")
#
#    hbox:
#        label _("Start, Guide")
#        text _("Access the game menu.")
#
#    hbox:
#        label _("Y/Top Button")
#        text _("Hides the user interface.")
#
#    textbutton _("Calibrate") action GamepadCalibrate()
#
#
#style help_button is gui_button:
#    properties gui.button_properties("help_button")
#    xmargin 8
#
#style help_button_text is gui_button_text:
#    properties gui.button_text_properties("help_button")
#
#style help_label is gui_label:
#    xsize 250
#    right_padding 20
#
#style help_label_text is gui_label_text:
#    size gui.text_size
#    xalign 1.0
#    text_align 1.0
#
#style help_text is gui_text



################################################################################
## Additional screens
################################################################################


## Confirm screen ##############################################################
##
## The confirm screen is called when Ren'Py wants to ask the player a yes or no
## question.
##
## http://www.renpy.org/doc/html/screen_special.html#confirm

screen name_input(message, ok_action):
    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"
    add mas_getTimeFile("gui/overlay/confirm.png")

    key "K_RETURN" action [Play("sound", gui.activate_sound), ok_action]

    frame:
        vbox:
            xalign .5
            yalign .5
            spacing 30

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            input default "" value VariableInputValue("player") length 12 allow "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action ok_action

screen dialog(message, ok_action):
    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"
    add mas_getTimeFile("gui/overlay/confirm.png")

    frame:
        vbox:
            xalign .5
            yalign .5
            spacing 30

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action ok_action

screen quit_dialog(message, ok_action):
    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"
    add mas_getTimeFile("gui/overlay/confirm.png")

    frame:
        vbox:
            xalign .5
            yalign .5
            spacing 30

            label _(message):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("QUIT") action ok_action

image confirm_glitch:
    "gui/overlay/confirm_glitch.png"
    pause 0.02
    "gui/overlay/confirm_glitch2.png"
    pause 0.02
    repeat

screen confirm(message, yes_action, no_action):
    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"
    add mas_getTimeFile("gui/overlay/confirm.png")

    frame:
        vbox:
            xalign .5
            yalign .5
            spacing 30

            if in_sayori_kill and message == layout.QUIT:
                add "confirm_glitch" xalign 0.5

            else:
                label _(message):
                    style "confirm_prompt"
                    xalign 0.5

            hbox:
                xalign 0.5
                spacing 100

                if mas_in_finalfarewell_mode:
                    textbutton _("-") action yes_action
                    textbutton _("-") action yes_action
                else:
                    textbutton _("Yes") action [SetField(persistent, "_mas_game_crashed", False), Show(screen="quit_dialog", message=layout.QUIT_YES, ok_action=yes_action)]
                    textbutton _("No") action no_action, Show(screen="dialog", message=layout.QUIT_NO, ok_action=Hide("dialog"))

    ## Right-click and escape answer "no".
    #key "game_menu" action no_action


style confirm_frame is gui_frame:
    background Frame(["gui/confirm_frame.png", "gui/frame.png"], gui.confirm_frame_borders, tile=gui.frame_tile)
    padding gui.confirm_frame_borders.padding
    align (0.5, 0.5)

style confirm_frame_dark is gui_frame:
    background Frame(["gui/confirm_frame.png", "gui/frame_d.png"], gui.confirm_frame_borders, tile=gui.frame_tile)
    padding gui.confirm_frame_borders.padding
    align (0.5, 0.5)

style confirm_prompt is gui_prompt

style confirm_prompt_text is gui_prompt_text:
    color "#000"
    outlines []
    text_align 0.5
    layout "subtitle"

style confirm_prompt_text_dark is gui_prompt_text:
    color "#FD5BA2"
    outlines []
    text_align 0.5
    layout "subtitle"

style confirm_button is gui_medium_button:
    properties gui.button_properties("confirm_button")
    hover_sound gui.hover_sound
    activate_sound gui.activate_sound

style confirm_button_text is navigation_button_text:
    properties gui.button_text_properties("confirm_button")


##Updating screen
screen update_check(ok_action,cancel_action,mode):

    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "update_check"
    add mas_getTimeFile("gui/overlay/confirm.png")

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 30

            if mode == 0:
                label _('An update is now avalable!'):
                    style "confirm_prompt"
                    xalign 0.5

            elif mode == 1:
                label _("No update available."):
                    style "confirm_prompt"
                    xalign 0.5

            elif mode == 2:
                label _('Checking for updates...'):
                    style "confirm_prompt"
                    xalign 0.5
            else:
                # otherwise, we assume a timeout
                label _('Timeout occured while checking for updates. Try again later.'):
                    style "confirm_prompt"
                    xalign 0.5

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("Install") action [ok_action, SensitiveIf(mode == 0)]

                textbutton _("Cancel") action cancel_action

    timer 1.0 action Return("None")

    ## Right-click and escape answer "no".
    #key "game_menu" action no_action


style update_check_frame is confirm_frame
style update_check_prompt is confirm_prompt
style update_check_prompt_text is confirm_prompt_text
style update_check_button is confirm_button
style update_check_button_text is confirm_button_text

## Updater screen #######################################################
##
## This is the screen called when the game needs to update versions
##
screen updater:
    modal True

    style_prefix "updater"

    frame:
        has side "t c b":
            spacing gui._scale(10)

        label _("Updater")

        fixed:
            vbox:
                if u.state == u.ERROR:
                    text _("An error has occured:")
                elif u.state == u.CHECKING:
                    text _("Checking for updates.")
                elif u.state == u.UPDATE_AVAILABLE:
                    text _("Version [u.version] is available. Do you want to install it?")

                elif u.state == u.UPDATE_NOT_AVAILABLE:
                    text _("Monika After Story is up to date.")
                elif u.state == u.PREPARING:
                    text _("Preparing to download the updates.")
                elif u.state == u.DOWNLOADING:
                    text _("Downloading the updates. (Progress bar may not advance during download)")
                elif u.state == u.UNPACKING:
                    text _("Unpacking the updates.")
                elif u.state == u.FINISHING:
                    text _("Finishing up.")
                elif u.state == u.DONE:
                    text _(_TXT_FINISHED_UPDATING)
                elif u.state == u.DONE_NO_RESTART:
                    text _("The updates have been installed.")
                elif u.state == u.CANCELLED:
                    text _("The updates were cancelled.")

                if u.message is not None:
                    null height gui._scale(10)
                    text "[u.message!q]"

                if u.progress is not None:
                    null height gui._scale(10)
                    bar value u.progress range 1.0 left_bar Solid("#cc6699") right_bar Solid("#ffffff" if not mas_globals.dark_mode else "#13060d") thumb None

        hbox:
            spacing gui._scale(25)

            if u.can_proceed:
                textbutton _("Proceed") action u.proceed

            if u.can_cancel:
                textbutton _("Cancel") action Return()


style updater_button is confirm_button
style updater_button_text is navigation_button_text
style updater_label is gui_label
style updater_label_text is game_menu_label_text
style updater_text is gui_text

## Skip indicator screen #######################################################
##
## The skip_indicator screen is displayed to indicate that skipping is in
## progress.
##
## https://www.renpy.org/doc/html/screen_special.html#skip-indicator
screen fake_skip_indicator():
    use skip_indicator

screen skip_indicator():

    zorder 100
    style_prefix "skip"

    frame:

        hbox:
            spacing 6

            text _("Skipping")

            text "▸" at delayed_blink(0.0, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.2, 1.0) style "skip_triangle"
            text "▸" at delayed_blink(0.4, 1.0) style "skip_triangle"


## This transform is used to blink the arrows one after another.
transform delayed_blink(delay, cycle):
    alpha .5

    pause delay

    block:
        linear .2 alpha 1.0
        pause .2
        linear .2 alpha 0.5
        pause (cycle - .4)
        repeat


style skip_frame is empty:
    ypos gui.skip_ypos
    background Frame("gui/skip.png", gui.skip_frame_borders, tile=gui.frame_tile)
    padding gui.skip_frame_borders.padding

style skip_text is gui_text:
    size gui.notify_text_size

style skip_triangle is skip_text:
    # We have to use a font that has the BLACK RIGHT-POINTING SMALL TRIANGLE
    # glyph in it.
    font "DejaVuSans.ttf"


## Notify screen ###############################################################
##
## The notify screen is used to show the player a message. (For example, when
## the game is quicksaved or a screenshot has been taken.)
##
## https://www.renpy.org/doc/html/screen_special.html#notify-screen

screen notify(message):

    zorder 100
    style_prefix "notify"

    frame at notify_appear:
        text message

    timer 3.25 action Hide('notify')


transform notify_appear:
    on show:
        alpha 0
        linear .25 alpha 1.0
    on hide:
        linear .5 alpha 0.0


style notify_frame is empty:
    ypos gui.notify_ypos

    background Frame("gui/notify.png", gui.notify_frame_borders, tile=gui.frame_tile)
    padding gui.notify_frame_borders.padding

style notify_text is gui_text:
    size gui.notify_text_size

## Scrollable Menu ###############################################################
##
## This screen creates a vertically scrollable menu of prompts attached to labels

#Define the properties of the object textbutton. textbutton is made by two parts:
#button and button_text. To customize textbutton, both botton and button_text need to be modified
#This part is usually found in gui.rpy

# Overrides for the UI elements which are placed on top of the classroom BG
# FIXME: there might be a better way, but for now it does its job
style classroom_vscrollbar is vscrollbar:
    base_bar Frame("gui/scrollbar/vertical_poem_bar.png", tile=False)

style classroom_vscrollbar_dark is vscrollbar_dark:
    base_bar Frame("gui/scrollbar/vertical_poem_bar.png", tile=False)

#Define the styles used for scrollable_menu_vbox, scrollable_menu_button and scrollable_menu_button_text

# Scrollable
style scrollable_menu_vbox is vbox:
    xalign 0.5
    ypos 270
    yanchor 0.5
    spacing 5

style scrollable_menu_button is choice_button:
    xysize (560, None)
    padding (25, 5, 25, 5)

style scrollable_menu_button_dark is choice_button_dark:
    xysize (560, None)
    padding (25, 5, 25, 5)

style scrollable_menu_button_text is choice_button_text:
    text_align 0.0
    align (0.0, 0.0)

style scrollable_menu_button_text_dark is choice_button_text_dark:
    text_align 0.0
    align (0.0, 0.0)

style scrollable_menu_new_button is scrollable_menu_button

style scrollable_menu_new_button_dark is scrollable_menu_button_dark

style scrollable_menu_new_button_text is scrollable_menu_button_text:
    italic True

style scrollable_menu_new_button_text_dark is scrollable_menu_button_text_dark:
    italic True

style scrollable_menu_special_button is scrollable_menu_button

style scrollable_menu_special_button_dark is scrollable_menu_button_dark

style scrollable_menu_special_button_text is scrollable_menu_button_text:
    bold True

style scrollable_menu_special_button_text_dark is scrollable_menu_button_text_dark:
    bold True

style scrollable_menu_crazy_button is scrollable_menu_button

style scrollable_menu_crazy_button_dark is scrollable_menu_button_dark

style scrollable_menu_crazy_button_text is scrollable_menu_button_text:
    italic True
    bold True

style scrollable_menu_crazy_button_text_dark is scrollable_menu_button_text_dark:
    italic True
    bold True

# Two-pane scrollable
style twopane_scrollable_menu_vbox is vbox:
    xalign 0.5
    ypos 270
    yanchor 0.5
    spacing 5

style twopane_scrollable_menu_button is choice_button:
    xysize (250, None)
    padding (25, 5, 25, 5)

style twopane_scrollable_menu_button_dark is choice_button_dark:
    xysize (250, None)
    padding (25, 5, 25, 5)

style twopane_scrollable_menu_button_text is choice_button_text:
    align (0.0, 0.0)
    text_align 0.0

style twopane_scrollable_menu_button_text_dark is choice_button_text_dark:
    align (0.0, 0.0)
    text_align 0.0

style twopane_scrollable_menu_new_button is twopane_scrollable_menu_button

style twopane_scrollable_menu_new_button_dark is twopane_scrollable_menu_button_dark

style twopane_scrollable_menu_new_button_text is twopane_scrollable_menu_button_text:
    italic True

style twopane_scrollable_menu_new_button_text_dark is twopane_scrollable_menu_button_text_dark:
    italic True

style twopane_scrollable_menu_special_button is twopane_scrollable_menu_button

style twopane_scrollable_menu_special_button_dark is twopane_scrollable_menu_button_dark

style twopane_scrollable_menu_special_button_text is twopane_scrollable_menu_button_text:
    bold True

style twopane_scrollable_menu_special_button_text_dark is twopane_scrollable_menu_button_text_dark:
    bold True

# check scrollable menu
style check_scrollable_menu_button is scrollable_menu_button:
    foreground "mod_assets/buttons/checkbox/[prefix_]check_fg.png"
    padding (33, 5, 25, 5)

style check_scrollable_menu_button_dark is scrollable_menu_button_dark:
    foreground "mod_assets/buttons/checkbox/[prefix_]check_fg_d.png"
    padding (33, 5, 25, 5)

style check_scrollable_menu_button_text is scrollable_menu_button_text
style check_scrollable_menu_button_text_dark is scrollable_menu_button_text_dark
style check_scrollable_menu_new_button is scrollable_menu_new_button
style check_scrollable_menu_new_button_dark is scrollable_menu_new_button_dark
style check_scrollable_menu_new_button_text is scrollable_menu_new_button_text
style check_scrollable_menu_new_button_text_dark is scrollable_menu_new_button_text_dark
style check_scrollable_menu_special_button is scrollable_menu_special_button
style check_scrollable_menu_special_button_dark is scrollable_menu_special_button_dark
style check_scrollable_menu_special_button_text is scrollable_menu_special_button_text
style check_scrollable_menu_special_button_text_dark is scrollable_menu_special_button_text_dark
style check_scrollable_menu_crazy_button is scrollable_menu_crazy_button
style check_scrollable_menu_crazy_button_dark is scrollable_menu_crazy_button_dark
style check_scrollable_menu_crazy_button_text is scrollable_menu_crazy_button_text
style check_scrollable_menu_crazy_button_text_dark is scrollable_menu_crazy_button_text_dark

# adjustments for the twopane menu
define prev_adj = ui.adjustment()
define main_adj = ui.adjustment()

#scrollable_menu selection screen
#This screen is based on work from the tutorial menu selection by haloff1
screen twopane_scrollable_menu(prev_items, main_items, left_area, left_align, right_area, right_align, cat_length):
    on "hide" action Function(store.main_adj.change, 0)

    default flt_evs = None

    style_prefix "twopane_scrollable_menu"

    # If the user used search, we show only teh results
    if flt_evs is not None:
        fixed:
            pos (left_area[0], left_area[1])
            xsize right_area[0] - left_area[0] + right_area[2]
            ysize left_area[3]

            vbox:
                pos (0, 0)
                anchor (0, 0)

                viewport:
                    id "viewport"
                    yfill False
                    mousewheel True
                    arrowkeys True

                    vbox:
                        for ev in flt_evs:
                            textbutton ev.prompt:
                                if renpy.has_label(ev.eventlabel) and not seen_event(ev.eventlabel):
                                    style "scrollable_menu_new_button"
                                else:
                                    style "scrollable_menu_button"
                                xsize right_area[0] - left_area[0] + right_area[2]
                                action [Function(mas_ui.twopane_menu_delegate_callback, ev.eventlabel), Return(ev.eventlabel)]

                null height 20

                textbutton _("Nevermind."):
                    style "scrollable_menu_button"
                    xsize right_area[0] - left_area[0] + right_area[2]
                    action [Return(False), Function(store.prev_adj.change, 0)]

            bar:
                style "classroom_vscrollbar"
                value YScrollValue("viewport")
                # RenPy is tresh, so we have to do this here
                xalign left_align / 2 + 0.005

    # Otherwise basic twopane
    else:
        # Left panel
        fixed:
            anchor (0, 0)
            pos (left_area[0], left_area[1])
            xsize left_area[2]

            if cat_length != 1:
                ysize left_area[3]
            else:
                ysize left_area[3] + evhand.LEFT_EXTRA_SPACE

            bar:
                adjustment prev_adj
                style "classroom_vscrollbar"
                xalign left_align

            vbox:
                ypos 0
                yanchor 0

                viewport:
                    yadjustment prev_adj
                    yfill False
                    mousewheel True
                    arrowkeys True

                    vbox:
                        for i_caption, i_label in prev_items:
                            textbutton i_caption:
                                if renpy.has_label(i_label) and not seen_event(i_label):
                                    style "twopane_scrollable_menu_new_button"

                                elif not renpy.has_label(i_label):
                                    style "twopane_scrollable_menu_special_button"

                                action Return(i_label)

                if cat_length != 1:
                    null height 20

                    if cat_length == 0:
                        textbutton _("Nevermind.") action [Return(False), Function(store.prev_adj.change, 0)]

                    elif cat_length > 1:
                        textbutton _("Go Back") action [Return(-1), Function(store.prev_adj.change, 0)]

        # Right panel
        if main_items:
            fixed:
                area right_area

                bar:
                    adjustment main_adj
                    style "classroom_vscrollbar"
                    xalign right_align

                vbox:
                    ypos 0
                    yanchor 0

                    viewport:
                        yadjustment main_adj
                        yfill False
                        mousewheel True
                        arrowkeys True

                        vbox:
                            for i_caption, i_label in main_items:
                                textbutton i_caption:
                                    if renpy.has_label(i_label) and not seen_event(i_label):
                                        style "twopane_scrollable_menu_new_button"

                                    elif not renpy.has_label(i_label):
                                        style "twopane_scrollable_menu_special_button"

                                    action [Return(i_label), Function(store.prev_adj.change, 0)]

                    null height 20

                    textbutton _("Nevermind.") action [Return(False), Function(store.prev_adj.change, 0)]

    # Search bar
    # The constants are hardcoded, but the menu looks good so just don't change them
    frame:
        xpos left_area[0]
        ypos left_area[1] - 55
        xsize right_area[0] - left_area[0] + right_area[2]# 530
        ysize 40
        background Solid("#ffaa99aa")

        viewport:
            draggable False
            arrowkeys False
            mousewheel "horizontal"
            xsize right_area[0] - left_area[0] + right_area[2] - 10
            ysize 38
            xadjustment ui.adjustment(ranged=store.mas_ui.twopane_menu_adj_ranged_callback)

            input:
                id "search_input"
                style_prefix "input"
                length 50
                xalign 0.0
                layout "nobreak"
                first_indent (0 if flt_evs is None else 10)
                # allow "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 _#"
                changed store.mas_ui.twopane_menu_search_callback

        if flt_evs is None:
            text "Search for a conversation...":
                text_align 0.0
                layout "nobreak"
                color "#EEEEEEB2"
                first_indent 10
                line_leading 1
                outlines []

# the regular scrollabe menu
screen scrollable_menu(items, display_area, scroll_align, nvm_text, remove=None):
    style_prefix "scrollable_menu"

    fixed:
        area display_area

        vbox:
            ypos 0
            yanchor 0

            viewport:
                id "viewport"
                yfill False
                mousewheel True

                vbox:
                    for i_caption, i_label in items:
                        textbutton i_caption:
                            if renpy.has_label(i_label) and not seen_event(i_label):
                                style "scrollable_menu_new_button"

                            elif not renpy.has_label(i_label):
                                style "scrollable_menu_special_button"

                            action Return(i_label)

            null height 20

            if remove:
                # in case we want the option to hide this menu
                textbutton _(remove[0]) action Return(remove[1])

            textbutton _(nvm_text) action Return(False)

        bar:
            style "classroom_vscrollbar"
            value YScrollValue("viewport")
            xalign scroll_align

# more general scrollable menu. This one takes the following params:
# IN:
#   items - list of items to display in the menu. Each item must be a tuple of
#       the following format:
#           [0]: prompt button
#           [1]: prompt return object
#           [2]: True if we want the button italics, False if not
#           [3]: True if we want the button bold, False if not
#   display_area - defines the display area of the menu. Tuple of the following
#       format:
#           [0]: x coordinate of menu
#           [1]: y coordinate of menu
#           [2]: width of menu
#           [3]: height of menu
#   scroll_align - alignment of vertical scrollbar
#   *args - represents the final (usually quit) item(s) of the menu
#       tuple of the following format:
#           [0]: text of the button
#           [1]: return value of the button
#           [2]: True if we want the button italics, False if not
#           [3]: True if we want the button bold, False if not
#           [4]: integer spacing between this button and the regular buttons
#               NOTE: must be >= 0
#       (Default: None)
screen mas_gen_scrollable_menu(items, display_area, scroll_align, *args):
    style_prefix "scrollable_menu"

    fixed:
        area display_area

        vbox:
            ypos 0
            yanchor 0

            viewport:
                id "viewport"
                yfill False
                mousewheel True

                vbox:
                    for item_prompt, item_value, is_italic, is_bold in items:
                        textbutton item_prompt:
                            if is_italic and is_bold:
                                style "scrollable_menu_crazy_button"

                            elif is_italic:
                                style "scrollable_menu_new_button"

                            elif is_bold:
                                style "scrollable_menu_special_button"

                            xsize display_area[2]
                            action Return(item_value)

            for final_items in args:
                if final_items[4] > 0:
                    null height final_items[4]

                textbutton _(final_items[0]):
                    if final_items[2] and final_items[3]:
                        style "scrollable_menu_crazy_button"

                    elif final_items[2]:
                        style "scrollable_menu_new_button"

                    elif final_items[3]:
                        style "scrollable_menu_special_button"

                    xsize display_area[2]
                    action Return(final_items[1])

        bar:
            style "classroom_vscrollbar"
            value YScrollValue("viewport")
            xalign scroll_align

# Scrollable menu with checkboxes. Toggles values between True/False
# Won't close itself until the user clicks on the return button
#
# IN:
#     items - list of tuples of the following format:
#         (prompt, key, start_selected, true_value, false_value)
#         NOTE: keys must be unique
#     display_area - area to display the menu in of the following format:
#         (x, y, width, height)
#     scroll_align - alignment of the scroll bar for the menu
#     selected_button_prompt - prompt for the return button if a button was selected
#         (Default: 'Done.')
#     default_button_prompt - prmpt for the return button provided no buttons are selected
#         (Default: 'Nevermind.')
#     return_all - whether or not we return all items or only the items with True in their values
#         (Default: False)
#
# OUT:
#     dict of buttons keys and new values
screen mas_check_scrollable_menu(
    items,
    display_area,
    scroll_align,
    selected_button_prompt="Done",
    default_button_prompt="Nevermind",
    return_all=False
):
    default buttons_data = {
        _tuple[1]: {
            "return_value": _tuple[3] if _tuple[2] else _tuple[4],
            "true_value": _tuple[3],
            "false_value": _tuple[4]
        }
        for _tuple in items
    }

    style_prefix "check_scrollable_menu"

    fixed:
        area display_area

        vbox:
            ypos 0
            yanchor 0

            viewport:
                id "viewport"
                yfill False
                mousewheel True

                vbox:
                    for button_prompt, button_key, start_selected, true_value, false_value in items:
                        textbutton button_prompt:
                            selected buttons_data[button_key]["return_value"] == buttons_data[button_key]["true_value"]
                            xsize display_area[2]
                            action ToggleDict(
                                buttons_data[button_key],
                                "return_value",
                                true_value,
                                false_value
                            )

            null height 20

            textbutton store.mas_ui.check_scr_menu_choose_prompt(buttons_data, selected_button_prompt, default_button_prompt):
                style "scrollable_menu_button"
                xsize display_area[2]
                action Function(
                    store.mas_ui.check_scr_menu_return_values,
                    buttons_data,
                    return_all
                )

        bar:
            style "classroom_vscrollbar"
            value YScrollValue("viewport")
            xalign scroll_align

# background timed jump screen
# NOTE: caller is responsible for hiding this screen
#
# IN:
#   timeout - number of seconds to time
#   timeout_label - label to jump to when timeout
screen mas_background_timed_jump(timeout, timeout_label):
    timer timeout action Jump(timeout_label)

# MAS restart monika screen
screen mas_generic_restart:
    # this will always return True
    # this has like a be right back button

    ## Ensure other screens do not get input while this screen is displayed.
    modal True

    zorder 200

    style_prefix "confirm"
    add mas_ui.cm_bg

    frame:

        vbox:
            xalign .5
            yalign .5
            spacing 30

# TODO have a brb feature somehow
# TODO: that would tie into the knowing how long player is out
#            label _("Tell Monika that you'll be right back?"):
            label _("Please restart Monika After Story."):
                style "confirm_prompt"
                xalign 0.5

            hbox:
                xalign 0.5
                spacing 100

                textbutton _("OK") action Return(True)

# Partial generic showpoem screen
# IN:
#   _poem - Poem object to show
#   paper - type of paper to use as background
#   _styletext - text style to use as a string
screen mas_generic_poem(_poem, paper="paper", _styletext="monika_text"):
    style_prefix "poem"
    vbox:
        add paper
    viewport id "vp":
        child_size (710, None)
        mousewheel True
        draggable True
        has vbox
        null height 40
        text "{0}\n\n{1}".format(renpy.substitute(_poem.title), renpy.substitute(_poem.text)) style _styletext
        null height 100
    vbar value YScrollValue(viewport="vp") style "poem_vbar"

#Chibika's text style
style chibika_note_text:
    font "gui/font/Halogen.ttf"
    size 28
    color "#000"
    outlines []

#Submods screen, integrated with the Submod class where a custom screen can be passed in as an arg, and will be added here
screen submods():
    tag menu

    use game_menu(("Submods")):

        default tooltip = Tooltip("")

        viewport id "scrollme":
            scrollbars "vertical"
            mousewheel True
            draggable True

            vbox:
                style_prefix "check"
                xfill True
                xmaximum 1000

                for submod in sorted(store.mas_submod_utils.submod_map.values(), key=lambda x: x.name):
                    vbox:
                        xfill True
                        xmaximum 1000

                        label submod.name:
                            yanchor 0
                            xalign 0
                            text_text_align 0.0

                        if submod.coauthors:
                            $ authors = "v{0}{{space=20}}by {1}, {2}".format(submod.version, submod.author, ", ".join(submod.coauthors))

                        else:
                            $ authors = "v{0}{{space=20}}by {1}".format(submod.version, submod.author)

                        text "[authors]":
                            yanchor 0
                            xalign 0
                            text_align 0.0
                            layout "greedy"
                            style "main_menu_version"

                        if submod.description:
                            text submod.description text_align 0.0

                    if submod.settings_pane:
                        $ renpy.display.screen.use_screen(submod.settings_pane, _name="{0}_{1}".format(submod.author, submod.name))

    text tooltip.value:
        xalign 0 yalign 1.0
        xoffset 300 yoffset -10
        style "main_menu_version"
