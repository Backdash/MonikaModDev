# enabling unstable mode
default persistent._mas_unstable_mode = False
default persistent._mas_can_update = True

# flag used so we know we just updated through the internal updater
default persistent._mas_just_updated = False

# legacy. These will be redirected to the s3 links after 090
#define mas_updater.regular = "http://updates.monikaafterstory.com/updates.json"
#define mas_updater.unstable = "http://unstable.monikaafterstory.com/updates.json"

# new s3 links
define mas_updater.regular = "http://d2vycydjjutzqv.cloudfront.net/updates.json"
define mas_updater.unstable = "http://dzfsgufpiee38.cloudfront.net/updates.json"

define mas_updater.force = False
define mas_updater.timeout = 10 # timeout default

# transform for the sliding updater
transform mas_updater_slide:
    xpos 641 xanchor 0 ypos -35 yanchor 0
    linear 1.0 ypos 0 yanchor 0
    time 10.0
    linear 1.0 ypos -35 yanchor 0

image mas_update_available = ConditionSwitch(
    "not mas_globals.dark_mode",
    "mod_assets/updateavailable.png",
    "mas_globals.dark_mode",
    "mod_assets/updateavailable_d.png"
)

init -1 python:

    # custom displayable for the updater screen
    class MASUpdaterDisplayable(renpy.Displayable):
        # this displayable will handle UpdateVersion on its own while enabling
        # interactions
        # since UpdateVersion occurs in a background thread, we want to
        # handle most logic in the render function, despite the
        # event-driven framework
        # we will return -1 upon cancel / ok
        # 1 upon update

        import pygame # mouse stuff
        import time # for timeouts
        import threading

        # CONSTANTS
        BUTTON_WIDTH = 120
        BUTTON_HEIGHT = 35
        BUTTON_BOT_SPACE = 50
        BUTTON_SPACING = 10

        FRAME_WIDTH = 500
        FRAME_HEIGHT = 250

        VIEW_WIDTH = 1280
        VIEW_HEIGHT = 720

        TEXT_YOFFSET = -15

        MOUSE_EVENTS = (
            pygame.MOUSEMOTION,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEBUTTONDOWN
        )

        TIMEOUT = 10 # 10 seconds

        # STATES

        # prior to checking for an update. This is visiually the same as
        # checking for an update.
        STATE_PRECHECK = -1

        # checknig for an update. This should also be the inital state
        # update button disabled, cancel button clickable
        STATE_CHECKING = 0

        # update found
        # we found an update.
        # update and cancel enabled
        STATE_BEHIND = 1

        # no update found
        # we are at the current verison
        # update and cancel hidden, ok button is shown and enabled
        STATE_UPDATED = 2

        # timeout
        # we timed out.
        # Update button becomes try again and is enabled. Cancel button enabled
        STATE_TIMEOUT = 3

        # in correct response from server
        # didnt get an OK
        # Update button becomes retry and is enabled. cancel button enabled
        STATE_NO_OK = 4

        # json decoding error
        # didnt get a valid json from server
        # Update button becomes retry and is enabled. cancel button enabled
        STATE_BAD_JSON = 5


        def __init__(self, update_link):
            """
            Constructor
            """
            super(renpy.Displayable, self).__init__()

            self.update_link = update_link

            # background tile
            # hangman frame color (50% trans)
            self.background = Solid(
                "#FFE6F47F",
                xsize=self.VIEW_WIDTH,
                ysize=self.VIEW_HEIGHT
            )

            # confirm screen (black, 70%)
            self.confirm = Solid(
                "#000000B2",
                xsize=self.FRAME_WIDTH,
                ysize=self.FRAME_HEIGHT
            )

            # calculate positions
            # top left x, y
            self._confirm_x = int((self.VIEW_WIDTH - self.FRAME_WIDTH) / 2)
            self._confirm_y = int((self.VIEW_HEIGHT - self.FRAME_HEIGHT) / 2)

            # top left, center button x y
            button_center_x = (
                int((self.FRAME_WIDTH - self.BUTTON_WIDTH) / 2) +
                self._confirm_x
            )
            button_center_y = (
                (self._confirm_y + self.FRAME_HEIGHT) -
                self.BUTTON_BOT_SPACE
            )

            # top left, left button x y
            button_left_x = (
                int(
                    (
                        self.FRAME_WIDTH -
                        (
                            (2 * self.BUTTON_WIDTH) +
                            self.BUTTON_SPACING
                        )
                    ) / 2
                ) +
                self._confirm_x
            )
            button_left_y = button_center_y

            # create the buttons
            self._button_ok = MASButtonDisplayable.create_stb(
                _("Ok"),
                False,
                button_center_x,
                button_center_y,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT,
                hover_sound=gui.hover_sound,
                activate_sound=gui.activate_sound
            )

            self._button_cancel = MASButtonDisplayable.create_stb(
                _("Cancel"),
                False,
                button_left_x + self.BUTTON_WIDTH + self.BUTTON_SPACING,
                button_left_y,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT,
                hover_sound=gui.hover_sound,
                activate_sound=gui.activate_sound
            )

            self._button_update = MASButtonDisplayable.create_stb(
                _("Update"),
                True,
                button_left_x,
                button_left_y,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT,
                hover_sound=gui.hover_sound,
                activate_sound=gui.activate_sound
            )

            self._button_retry = MASButtonDisplayable.create_stb(
                _("Retry"),
                True,
                button_left_x,
                button_left_y,
                self.BUTTON_WIDTH,
                self.BUTTON_HEIGHT,
                hover_sound=gui.hover_sound,
                activate_sound=gui.activate_sound
            )

            # confirm text
            self._text_checking = Text(
                _("Checking for updates..."),
                font=gui.default_font,
                size=gui.text_size,
                color="#ffe6f4",
                outlines=[]
            )
            self._text_update = Text(
                _("New update available!"),
                font=gui.default_font,
                size=gui.text_size,
                color="#ffe6f4",
                outlines=[]
            )
            self._text_noupdate = Text(
                _("No update found."),
                font=gui.default_font,
                size=gui.text_size,
                color="#ffe6f4",
                outlines=[]
            )
            self._text_timeout = Text(
                _("Connection timed out."),
                font=gui.default_font,
                size=gui.text_size,
                color="#ffe6f4",
                outlines=[]
            )
            self._text_badresponse = Text(
                _("Server returned bad response."),
                font=gui.default_font,
                size=gui.text_size,
                color="#ffe6f4",
                outlines=[]
            )
            self._text_badjson = Text(
                _("Server returned bad JSON."),
                font=gui.default_font,
                size=gui.text_size,
                color="#ffe6f4",
                outlines=[]
            )

            # grouped buttons
            self._checking_buttons = [
                self._button_update,
                self._button_cancel
            ]
            self._behind_buttons = self._checking_buttons
            self._updated_buttons = [self._button_ok]
            self._timeout_buttons = [
                self._button_retry,
                self._button_cancel
            ]

            # inital state
            self._state = self.STATE_PRECHECK

            # inital button states
            self._button_update.disable()

            # inital time
            self._prev_time = time.time()

            # thread stuff
            self._check_thread = None
            self._thread_result = list()


        def _checkUpdate(self):
            """
            Does the purely logical update checking
            This will set the appropriate states
            """

            if self._state == self.STATE_CHECKING:
                # checking for updates

                # lists are thread-safe!
                if len(self._thread_result) > 0:
                    self._state = self._thread_result.pop()

                    # special state processing
                    if self._state == self.STATE_BEHIND:
                        # this state needs to enable the update button
                        self._button_update.enable()

                elif time.time() - self._prev_time > self.TIMEOUT:
                    # timeout!
                    self._state = self.STATE_TIMEOUT

            elif self._state == self.STATE_PRECHECK:
                # pre check, launch the checking thread
                # threading stuff for the web connection
#                MASUpdaterDisplayable._sendRequest(self.update_link, self._thread_result)
                self._thread_result = list()
                self._check_thread = threading.Thread(
                    target=MASUpdaterDisplayable._sendRequest,
                    args=(self.update_link, self._thread_result)
                )
                self._check_thread.start()
                self._state = self.STATE_CHECKING


        @staticmethod
        def _handleRedirect(new_url):
            """
            Attempts to connect to the redircted url
            IN:
                new_url - the redirect we want to connect to
            Returns read_json if we got a connection, Nnone otherwise
            """
            import httplib

            _http, double_slash, url = new_url.partition("//")
            url, single_slash, req_uri = url.partition("/")
            read_json = None
            h_conn = httplib.HTTPConnection(
                url
            )

            try:
                # make connection
                h_conn.connect()

                # get file we need
                h_conn.request("GET", single_slash + req_uri)
                server_response = h_conn.getresponse()

                if server_response.status != 200:
                    # we dont follow anymore redirects
                    return None

                read_json = server_response.read()

            except httplib.HTTPException:
                # we assume a timeout / connection error
                return None

            finally:
                h_conn.close()

            return read_json


        # some function here
        @staticmethod
        def _sendRequest(update_link, thread_result):
            """
            Sends out the http request and returns a response and stuff
            NOTE: designed to be called as a background thread
            ASSUMES:
                _thread_result
                    appends appropriate state for use
            """
            import httplib
            import json

            # separate the update link parts
            # (its okay to access this, main thread does not)
            _http, double_slash, url = update_link.partition("//")
            url, single_slash, json_file = url.partition("/")
            read_json = None
            h_conn = httplib.HTTPConnection(
                url
            )

            try:
                # make connection and attempt to connect
                h_conn.connect()

                # get the file we need
                h_conn.request("GET", "/" + json_file)
                server_response = h_conn.getresponse()

                # check status
                if server_response.status == 301:
                    # redirect, pull the location header and continue
                    new_url = server_response.getheader("location", None)

                    if new_url is None:
                        # we have to have the redirect location to continue
                        thread_result.append(MASUpdaterDisplayable.STATE_NO_OK)
                        return

                    # otherwise, switch connection to the new url
                    h_conn.close()
                    read_json = MASUpdaterDisplayable._handleRedirect(new_url)

                    if read_json is None:
                        # redirect failed too
                        thread_result.append(MASUpdaterDisplayable.STATE_NO_OK)
                        return

                elif server_response.status != 200:
                    # didnt get an OK response
                    thread_result.append(MASUpdaterDisplayable.STATE_NO_OK)
                    return

                else:
                    # good status, lets get the value
                    read_json = server_response.read()

            except httplib.HTTPException:
                # we assume a timeout / connection error
                thread_result.append(MASUpdaterDisplayable.STATE_TIMEOUT)
                return

            finally:
                h_conn.close()

            # now to parse the json
            try:
                read_json = json.loads(read_json)

            except ValueError:
                # error decoding the json
                thread_result.append(MASUpdaterDisplayable.STATE_BAD_JSON)
                return

            # now to get the pretty version
            try:
                _mod = read_json.get("Mod", None)

            except:
                # this wasnt a dict?!
                thread_result.append(MASUpdaterDisplayable.STATE_BAD_JSON)
                return

            if _mod is None:
                # json is missing Mod
                thread_result.append(MASUpdaterDisplayable.STATE_BAD_JSON)
                return

            latest_version = _mod.get("pretty_version", None)

            if latest_version is None:
                # json is missing pretty version
                thread_result.append(MASUpdaterDisplayable.STATE_BAD_JSON)
                return

            # old version check
            if persistent._mas_unstable_mode:
                # rpartion the ., the last item should be build number
                lv_build_number = store.mas_utils.tryparseint(
                    latest_version.rpartition(".")[2],
                    default=None
                )
                build_number = store.mas_utils.tryparseint(
                    config.version.rpartition(".")[2],
                    default=None
                )
                if lv_build_number is None or build_number is None:
                    thread_result.append(MASUpdaterDisplayable.STATE_BAD_JSON)
                    return

                lv_is_old = lv_build_number <= build_number

            else:
                # just replcae dots with underscores, prefix v
                parsed_version = "v" + latest_version.replace(".", "_")
                lv_is_old = parsed_version in store.updates.version_updates

            # okay we have a latest version, compare to the current version
            if latest_version == config.version or lv_is_old:
                # same version (or version on server is older)
                thread_result.append(MASUpdaterDisplayable.STATE_UPDATED)

            else:
                # new version found!
                thread_result.append(MASUpdaterDisplayable.STATE_BEHIND)

            return


        def render(self, width, height, st, at):
            """
            RENDER
            """

            # check states
            self._checkUpdate()

            # now render
            r = renpy.Render(width, height)

            # starting with backgrounds
            back = renpy.render(self.background, width, height, st, at)
            confirm = renpy.render(self.confirm, width, height, st, at)

            if (
                    self._state == self.STATE_CHECKING
                    or self._state == self.STATE_PRECHECK
                ):
                # checking for updates
                display_text = renpy.render(
                    self._text_checking,
                    width,
                    height,
                    st,
                    at
                )
                display_buttons = self._checking_buttons

            elif self._state == self.STATE_UPDATED:
                # no update avaiable
                display_text = renpy.render(
                    self._text_noupdate,
                    width,
                    height,
                    st,
                    at
                )
                display_buttons = self._updated_buttons

            elif self._state == self.STATE_BEHIND:
                # update available
                display_text = renpy.render(
                    self._text_update,
                    width,
                    height,
                    st,
                    at
                )
                display_buttons = self._behind_buttons

            else:
                # timed out
                # connection error
                # json error

                if self._state == self.STATE_TIMEOUT:
                    # timeout
                    display_text = renpy.render(
                        self._text_timeout,
                        width,
                        height,
                        st,
                        at
                    )

                elif self._state == self.STATE_NO_OK:
                    # connection error
                    display_text = renpy.render(
                        self._text_badresponse,
                        width,
                        height,
                        st,
                        at
                    )

                else:
                    # json error
                    display_text = renpy.render(
                        self._text_badjson,
                        width,
                        height,
                        st,
                        at
                    )

                display_buttons = self._timeout_buttons

            # render the buttons
            rendered_buttons = [
                (
                    x.render(width, height, st, at),
                    (x.xpos, x.ypos)
                )
                for x in display_buttons
            ]

            # get display text blit coords
            pw, ph = display_text.get_size()

            # now blit em all
            r.blit(back, (0, 0))
            r.blit(confirm, (self._confirm_x, self._confirm_y))
            r.blit(
                display_text,
                (
                    int((width - pw) / 2),
                    int((height - ph) / 2) + self.TEXT_YOFFSET
                )
            )
            for vis_b, xy in rendered_buttons:
                r.blit(vis_b, xy)

            # force a redraww so we keep checking udpater
            renpy.redraw(self, 1.0)

            return r


        def event(self, ev, x, y, st):
            """
            EVENT
            """
            if ev.type in self.MOUSE_EVENTS:

                if (
                        self._state == self.STATE_CHECKING
                        or self._state == self.STATE_PRECHECK
                    ):
                    # checking for an update state

                    if self._button_cancel.event(ev, x, y, st):
                        # cancel clicked! return -1
                        return -1

                elif self._state == self.STATE_UPDATED:
                    # no update found

                    if self._button_ok.event(ev, x, y, st):
                        # ok clicked! return -1
                        return -1

                elif self._state == self.STATE_BEHIND:
                    # found an update

                    if self._button_update.event(ev, x, y, st):
                        # update clicked! return 1
                        return 1

                    if self._button_cancel.event(ev, x, y, st):
                        # cancel clicked! return -1
                        return -1

                else:
                    # timeout state
                    # connection error state
                    # bad json state

                    if self._button_cancel.event(ev, x, y, st):
                        # cancel clicked! return -1
                        return -1

                    if self._button_retry.event(ev, x, y, st):
                        # retry clicked! go back to checking
                        self._button_update.disable()
                        self._prev_time = time.time()
                        self._state = self.STATE_PRECHECK

                renpy.redraw(self, 0)

            raise renpy.IgnoreEvent()


init python in mas_updater:


    def checkUpdate():
        """
        RETURNS:
            update_link if theres update available
            None if no update avaiable, or no need to update rn
        """
        import time
        import os
        import shutil

        curr_time = time.time()

        if renpy.game.persistent._mas_unstable_mode:
            update_link = unstable

        else:
            update_link = regular

        last_updated = renpy.game.persistent._update_last_checked.get(update_link, 0)

        if last_updated > curr_time:
            last_updated = 0

        # always move update folder if possible
        game_update = os.path.normcase(renpy.config.basedir + "/game/update")
        ddlc_update = os.path.normcase(renpy.config.basedir + "/update")
        base_update = os.path.normcase(renpy.config.basedir)
        if os.access(game_update, os.F_OK):
            try:
                if os.access(ddlc_update, os.F_OK):
                    shutil.rmtree(ddlc_update)

                shutil.move(game_update, base_update)
                can_update = renpy.store.updater.can_update()

            except:
                can_update = False

        else:
            can_update = renpy.store.updater.can_update()

        # notify user
        renpy.game.persistent._mas_can_update = can_update

        if force:
            check_wait = 0
        else:
            # wait 24 hours before updating
            check_wait = 3600 * 24

        if curr_time-last_updated > check_wait and can_update:
            return update_link

        return None


init 10 python:

    def _mas_backgroundUpdateCheck():
        """
        THIS IS A PRIVATE FUNCTION
        Background update check
        """
        import time
        import store.mas_updater as mas_updater

        update_link = mas_updater.checkUpdate()

        if not update_link:
            return

        # now we creathe thre thread list for renderering
        thread_result = list()
        MASUpdaterDisplayable._sendRequest(update_link, thread_result)

        if len(thread_result) > 0:
            # the update returned a result
            state = thread_result.pop()

            if state == MASUpdaterDisplayable.STATE_BEHIND:
                # we have an update available
                renpy.show(
                    "mas_update_available",
                    at_list=[mas_updater_slide],
                    layer="front",
                    zorder=18,
                    tag="masupdateroverlay"
                )

        return


    def mas_backgroundUpdateCheck():
        """
        This launches the background update thread
        """
        import threading

#        _mas_backgroundUpdateCheck()
        the_thread = threading.Thread(
            target=_mas_backgroundUpdateCheck
        )
        the_thread.start()

# Update cleanup flow:
init -894 python:

    def _mas_getBadFiles():
        """
        Searches through the entire mod_assets folder for any file
        with the '.new' extension and returns their paths
        RETURNS:
            a list containing the file names, list will be empty if
            there was no 'bad' files
        """
        import os

        return [
            os.path.join(root, file)
            for root, dirs, files in os.walk(os.path.join(config.gamedir,'mod_assets'))
                for file in files
                    if file.endswith(".new")
            ]

    def mas_cleanBadUpdateFiles():
        """
        Moves any file with the '.new' extension to the correct file
        """
        import shutil
        files = _mas_getBadFiles()
        for file in files:
            shutil.move(file, file[:-4])

    # if we just updated
    if renpy.game.persistent._mas_just_updated:
        # check if we have files to move
        mas_cleanBadUpdateFiles()
        # reset the flag
        renpy.game.persistent._mas_just_updated = False



label mas_updater_steam_issue:
    show monika at t11
    m 1eub "[player]!{w=0.2} I see you're using Steam."
    m 1eksdlb "Unfortunately..."
    m 1efp "I can't run the updater because Steam is a meanie!"
    m 1eksdla "You'll have to manually install the update from the releases page on the mod's website.{w=0.2} {a=http://www.monikaafterstory.com/releases.html}Click here to go to releases page{/a}."
    m 1hua "Make sure to say goodbye to me first before installing the update."
    return

label mas_updater_rpy_issue:
    show monika at t11
    m 2eksdla "[player]...I see you have some rpy files in your game directory."
    if renpy.seen_label("monika_rpy_files"):
        m 2rksdlc "I'm sure you remember when I mentioned that those files can cause problems when you update..."
    else:
        m 2rksdlc "Those files can cause some problems when you update..."

    m 3rksdlb "So I can't run the updater while those are in there."
    m 1eua "I can delete those for you and run the updater if you want though!"

    m 1eua "Would you like me to delete them?{nw}"
    #NOTE: no history_list.pop() here because for some reason this doesn't end up in history
    menu:
        m "Would you like me to delete them?{fast}"

        "Yes, please.":
            m 1hua "Sure!"

            #Delete files
            call mas_rpy_file_delete

            m 3hub "There we go!"
            #Hide screen
            hide screen mas_py_console_teaching
            show monika at t11

            #Also going to rmallEVL here
            $ mas_rmallEVL("monika_rpy_files")

            m 2dsc "Now let me just run the updater.{w=0.5}.{w=0.5}.{nw}"
            window hide

            #Run the updater
            jump update_now

        "No, thanks.":
            m 3eka "Alright [player]. If you delete them and then try to update again, I'll run the updater for you."

    return

label forced_update_now:
    $ mas_updater.force = True

    # steam check
    if store.mas_globals.is_steam and not persistent._mas_unstable_mode:

        $ mas_RaiseShield_core()

        call mas_updater_steam_issue

        if store.mas_globals.dlg_workflow:
            # current in dialogue workflow, we should only enable the escape
            # and music stuff
            $ enable_esc()
            $ mas_MUINDropShield()

        else:
            # otherwise, reenable core interactions
            $ mas_DropShield_core()
        return

    #Rpy file check
    elif mas_hasRPYFiles():
        $ mas_RaiseShield_core()

        call mas_updater_rpy_issue

        if store.mas_globals.dlg_workflow:
            # current in dialogue workflow, we should only enable the escape
            # and music stuff
            $ enable_esc()
            $ mas_MUINDropShield()

        else:
            # otherwise, reenable core interactions
            $ mas_DropShield_core()
        return

#This file goes through the actions for updating Monika After story
label update_now:
    $ import time #this instance of time can stay

    # steam check
    if store.mas_globals.is_steam and not persistent._mas_unstable_mode:
        return

    # screen check
    if renpy.showing("masupdateroverlay", layer="overlay"):
        hide masupdateroverlay

    $ update_link = store.mas_updater.checkUpdate()

    if not persistent._mas_can_update:
        # updates are currently disabled
        python:
            no_update_dialog = (
                "Error: Failed to move 'update/' folder. Please manually " +
                "move the update folder from 'game/' to the base 'ddlc/' " +
                "directory and try again."
            )
        call screen dialog(message=no_update_dialog, ok_action=Return())

    elif update_link:

        # call the updater displayable
        python:
            ui.add(MASUpdaterDisplayable(update_link))
            updater_selection = ui.interact()

#        "hold up"

        if updater_selection > 0:
            # user wishes to update
            $ persistent.closed_self = True # we take updates as self closed
            $ persistent._mas_just_updated = True #set the just updated flag

            #Stop background sound and music
            stop background
            stop music

            # call quit so we can save important stuff
            call quit
            $ renpy.save_persistent()
            $ updater.update(update_link, restart=True)

            #Clear any potential lingering things in tray
            $ mas_clearNotifs()

            # we have to quit because calling QUIT breaks things
            jump _quit

        else:
            # just update the last checked, regardless of issue
            $ persistent._update_last_checked[update_link] = time.time()
    return
