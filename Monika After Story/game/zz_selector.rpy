## module that contains a workable selection screen?
#
# NOTE: i have no idea how generic this can get.
#   Chances are, it will not be very generic.
#
# Selection MAPS:
#   new class: Selec


# databaess for selectable sprite data
# key: name of item
# value: tuple containing data
default persistent._mas_selspr_acs_db = {}
default persistent._mas_selspr_hair_db = {}
default persistent._mas_selspr_clothes_db = {}

init -150 python in mas_selspr:
    import store
    import store.mas_utils as mas_utils

    ## selector rules
    # selector rules are functions that should be checked prior to unlocking
    # a selector.
    # NOTE: all selector rules are assumed to be ran at runtime

    def _rule_ribbon():
        """
        Ribbon selector should only be unocked if:
            1 - outfit is not baked
            2 - hair supports ribbon
        """
        return (
            not store.monika_chr.is_wearing_clothes_with_exprop("baked outfit")
            and store.monika_chr.is_wearing_hair_with_exprop("ribbon")
        )


init -100 python in mas_selspr:

    # prompt constants go here
    PROMPT_MAP = {
        "choker": {
            "_ev": "monika_choker_select",
            "change": "Can you change your choker?",
            "wear": "Can you wear a choker?",
        },
        "clothes": {
            "_ev": "monika_clothes_select",
            "change": "Can you change your clothes?",
            # TODO: min-items
        },
        "earrings": {
            "_ev": "monika_earrings_select",
            "_min-items": 1,
            "change": "Can you change your earrings?",
            "wear": "Can you wear earrings?",
        },
        "hair": {
            "_ev": "monika_hair_select",
            "change": "Can you change your hairstyle?",
            # TODO: min-items
        },
        "hat": {
            "_ev": "monika_hat_select",
            "_min-items": 1,
            "change": "Can you change your hat?",
            "wear": "Can you wear a hat?",
        },
        "left-hair-clip": {
            "_ev": "monika_hairclip_select",
            "_min-items": 1,
            "change": "Can you change your hairclip?",
            "wear": "Can you wear a hairclip?",
        },
        "left-hair-flower": {
            "_ev": "monika_hairflower_select",
            "_min-items": 1,
            "change": "Can you change the flower in your hair?",
            "wear": "Can you wear a flower in your hair?",
        },
        "ribbon": {
            "_ev": "monika_ribbon_select",
            "_min-items": 1,
            "_rule": _rule_ribbon,
            "change": "Can you tie your hair with something else?",
            "wear": "Can you tie your hair with something else?",
        },
    }


    def check_prompt(key):
        """
        Checks if the prompt's rule passes.

        IN:
            key - select key

        RETURNS: True if prompt's rule passes (or doesnt exist), False if not.
        """
        prompt_rule = PROMPT_MAP.get(key, {}).get("_rule", None)

        if prompt_rule is None:
            return True

        return prompt_rule()


    def get_prompt(key, prompt_key="change"):
        """
        Gets prompt with the given key and prompt key

        IN:
            key - select key
            prompt_key - key to get prompt

        RETURNS: prompt. "" if invalid
        """
        if prompt_key.startswith("_"):
            return ""

        return PROMPT_MAP.get(key, {}).get(prompt_key, "")


    def get_minitems(key, defval=1):
        """
        Gets minimum number of items required to unlock this selector.

        IN:
            key - select key
            defval - default value to return

        RETURNS: minimum number of items to unlock the selector.
        """
        return PROMPT_MAP.get(key, {}).get("_min-items", defval)


    def in_prompt_map(key):
        """
        Checks if a key is in the prompt select map

        IN:
            key - select key to check

        RETURNS: True if in the map, FAlse if not
        """
        return key in PROMPT_MAP


    def lock_prompt(key):
        """
        Locks ev with the given key

        IN:
            key - select key
        """
        evl = PROMPT_MAP.get(key, {}).get("_ev", None)
        if evl is not None:
            store.mas_lockEVL(evl, "EVE")


    def set_prompt(key, prompt_key="change"):
        """
        Sets prompt of ev with the given key with one associatd with given
        prompt key.

        IN:
            key - select key
            prompt_key - key to get propmt. if _ev, then no change
        """
        if prompt_key == "_ev":
            return

        prompt_data = PROMPT_MAP.get(key, {})

        ev = store.mas_getEV(prompt_data.get("_ev", None))
        prompt = prompt_data.get(prompt_key, None)

        if ev is not None and prompt is not None:
            ev.prompt = prompt


    def unlock_prompt(key):
        """
        Unlocks ev with the given key

        IN:
            key - select key
        """
        evl = PROMPT_MAP.get(key, {}).get("_ev", None)
        if evl is not None:
            store.mas_unlockEVL(evl, "EVE")


    def startup_prompt_check():
        """
        Checks all prompts and adjusts them if needed
        """
        # ribbon is its own thing
        if store.monika_chr.is_wearing_ribbon():
            set_prompt("ribbon", "change")
        else:
            set_prompt("ribbon", "wear")

        # now for the rest
        for group in GRP_TOPIC_LIST:
            if group != "ribbon":
                if store.monika_chr.is_wearing_acs_type(group):
                    set_prompt(group, "change")
                else:
                    set_prompt(group, "wear")


init -20 python:

    class MASSelectableSprite(object):
        """
        Wrapper around selectable sprite objects. We do this instead of
        extending because not everything would be selectble

        PROPERTIES:
            name - this is always the same thing as the MASSprite object we
                create thsi with.
            display_name - the name to use in the selectbale button screen
            thumb - thumbnail image to use for selection screen. Aim for a
                180x180
                (png is added in the constructor)
            group - string id to group related selectable sprites. this really
                applies only to acs, but in case other things need this.
            unlocked - True if this selectable sprite can be selected,
                False otherwise.
            visible_when_locked - True if this should be visible when locked
                False, otherwise.
                Locked items will generally be displayed with a placeholder
                thumb.
            hover_dlg - list of text to display when hovering over the object
            first_select_dlg - text to display the first time you
                select this sprite
            select_dlg - list text to display everytime you select this sprite
                (after the first time)
            selected - True if this item is selected, False if not
            disabled_type - disable type to use in the displayable in selector.
                NOTE: this property may be set by the selector labels.
                Do NOT expect this property to be respected if set manually.
        """


        def __init__(self,
                _sprite_object,
                display_name,
                thumb,
                group,
                visible_when_locked=True,
                hover_dlg=None,
                first_select_dlg=None,
                select_dlg=None
            ):
            """
            Selectable sprite objects constructor

            IN:
                _sprite_object - MASSpriteBase object to build this selectable
                    sprite object with.
                    NOTE: because of inheritance issues, this is NOT CHECKED.
                        The extending classes MUST check types.
                display_name - name to show on the selectable screen
                thumb - thumbnail to use on the select screen
                group - group id to group related selectable sprites.
                visible_when_locked - True if this item should be visible in
                    the screen when locked, False otherwise
                    (Default: True)
                hover_dlg - list of text to display when hovering over the
                    object
                    (Default: None)
                first_select_dlg - text to display the first time you select
                    this sprite
                    (Default: None)
                select_dlg - list of text to display everytime you select this
                    sprite
                    (after the first time)
                    (Default: None)
            """
#            self._check_dlg(hover_dlg)
#            self._check_dlg(first_select_dlg)
#            self._check_dlg(select_dlg)

            self.name = _sprite_object.name
            self.display_name = display_name
            self.thumb = thumb + ".png"
            self.group = group
            self.unlocked = False
            self.visible_when_locked = visible_when_locked
            self.hover_dlg = hover_dlg
            self.first_select_dlg = first_select_dlg
            self.select_dlg = select_dlg
            self.selected = False
            self.disable_type = store.mas_selspr.DISB_NONE

            # by default
            # NOTE: only ACS can override this
            self.remover = False


        def _check_dlg(self, dlg):
            if dlg is not None and not renpy.has_label(dlg):
                raise Exception("label '{0}' no exist".format(dlg))


        def _build_thumbstr(self):
            """
            Returns thumb string for this selectable
            """
            return MASSelectableImageButtonDisplayable.THUMB_DIR + self.thumb


        def fromTuple(self, read_tuple):
            """
            Loads data from the given tuple.

            IN:
                read_tuple - tuple of the following format:
                    [0]: unlocked property
                    [1]: visible_when_locked
            """
            self.unlocked, self.visible_when_locked = read_tuple


        def toTuple(self):
            """
            RETURNS: tuple version of this data:
                [0]: unlocked property
                [1]: visible_when_locked
            """
            return (self.unlocked, self.visible_when_locked)


    class MASSelectableAccessory(MASSelectableSprite):
        """
        Wrapper around MASAccessory sprite objects.

        PROPERTIES:
            remover - True if this item is a remover, aka a blank ACS,
                False if not


        SEE MASSelectableSprite for inherieted properties
        """

        def __init__(self,
                _sprite_object,
                display_name,
                thumb,
                group,
                visible_when_locked=True,
                hover_dlg=None,
                first_select_dlg=None,
                select_dlg=None,
                remover=False
            ):
            """
            MASSelectableAccessory

            IN:
                _sprite_object - MASAccessory object to build this selectable
                    sprite object with.
                display_name - name to show on the selectable screen
                thumb - thumbnail to use on the select screen
                group - group id to group related selectable sprites.
                visible_when_locked - True if this item should be visible in
                    the screen when locked, False otherwise
                    (Default: True)
                hover_dlg - list of text to display when hovering over the
                    object
                    (Default: None)
                first_select_dlg - text to display the first time you select
                    this sprite
                    (Default: None)
                select_dlg - list of text to display everytime you select this
                    sprite
                    (after the first time)
                    (Default: None)
                remove - True if this ACS is a blank ACS (remover), False if
                    not
                    (Default: False)
            """
            if not isinstance(_sprite_object, MASAccessoryBase):
                raise Exception("not an acs: {0}".format(group))
            if remover and store.mas_selspr._has_remover(group):
                raise Exception(
                    "cannot have more than 1 remover per group: '{0}'".format(
                        group
                    )
                )

            super(MASSelectableAccessory, self).__init__(
                _sprite_object,
                display_name,
                "acs-" + thumb,
                group,
                visible_when_locked,
                hover_dlg,
                first_select_dlg,
                select_dlg
            )

            self.remover = remover


        def get_sprobj(self):
            """
            Gets the sprite object associated with this selectable.

            RETURNS: the sprite object for this selectbale, or None if not
                found
            """
            return store.mas_sprites.ACS_MAP.get(self.name, None)


    class MASSelectableHair(MASSelectableSprite):
        """
        Wrappare around MASHair sprite objects

        PROPERTIES:
            (no additional)

        SEE MASSelectableSprite for inherited properties
        """


        def __init__(self,
                _sprite_object,
                display_name,
                thumb,
                group,
                visible_when_locked=True,
                hover_dlg=None,
                first_select_dlg=None,
                select_dlg=None
            ):
            """
            MASSelectableHair constructor

            IN:
                _sprite_object - MASHair object to build this selectable
                    sprite object with.
                display_name - name to show on the selectable screen
                thumb - thumbnail to use on the select screen
                group - group id to group related selectable sprites.
                visible_when_locked - True if this item should be visible in
                    the screen when locked, False otherwise
                    (Default: True)
                hover_dlg - list of text to display when hovering over the
                    object
                    (Default: None)
                first_select_dlg - text to display the first time you select
                    this sprite
                    (Default: None)
                select_dlg - list of text to display everytime you select this
                    sprite
                    (after the first time)
                    (Default: None)
            """
            if type(_sprite_object) != MASHair:
                raise Exception("not a hair: {0}".format(group))

            super(MASSelectableHair, self).__init__(
                _sprite_object,
                display_name,
                "hair-" + thumb,
                group,
                visible_when_locked,
                hover_dlg,
                first_select_dlg,
                select_dlg
            )


        def get_sprobj(self):
            """
            Gets the sprite object associated with this selectable.

            RETURNS: the sprite object for this selectbale, or None if not
                found
            """
            return store.mas_sprites.HAIR_MAP.get(self.name, None)


    class MASSelectableClothes(MASSelectableSprite):
        """
        Wrappare around MASClothes sprite objects

        PROPERTIES:
            (no additional)

        SEE MASSelectableSprite for inherited properties
        """


        def __init__(self,
                _sprite_object,
                display_name,
                thumb,
                group,
                visible_when_locked=True,
                hover_dlg=None,
                first_select_dlg=None,
                select_dlg=None
            ):
            """
            MASSelectableClothes constructor

            IN:
                _sprite_object - MASClothes object to build this selectable
                    sprite object with.
                display_name - name to show on the selectable screen
                thumb - thumbnail to use on the select screen
                group - group id to group related selectable sprites.
                visible_when_locked - True if this item should be visible in
                    the screen when locked, False otherwise
                    (Default: True)
                hover_dlg - list of text to display when hovering over the
                    object
                    (Default: None)
                first_select_dlg - text to display the first time you select
                    this sprite
                    (Default: None)
                select_dlg - list of text to display everytime you select this
                    sprite
                    (after the first time)
                    (Default: None)
            """
            if type(_sprite_object) != MASClothes:
                raise Exception("not a clothes: {0}".format(group))

            super(MASSelectableClothes, self).__init__(
                _sprite_object,
                display_name,
                "clothes-" + thumb,
                group,
                visible_when_locked,
                hover_dlg,
                first_select_dlg,
                select_dlg
            )


        def get_sprobj(self):
            """
            Gets the sprite object associated with this selectable.

            RETURNS: the sprite object for this selectbale, or None if not
                found
            """
            return store.mas_sprites.CLOTH_MAP.get(self.name, None)


init -10 python in mas_selspr:
    import datetime
    import store

    # mailbox constants
    MB_DISP = "disp_text"
    MB_DISP_DEF = "def_disp_text"
    MB_CONF = "conf_enable"
    MB_DISP_FAST = "disp_fast"
    MB_OCB_VISIBLE = "ocb_visible"
    MB_OCB_CHECKED = "ocb_checked"
    MB_RSTR_ENABLE = "restore_enable"
    MB_PREV_STATE = "prev_state"
    MB_FRAME_VSIZE = "frame_vsize"

    ## screen constants
    SB_VIEWPORT_BOUNDS_X = 1075
    SB_VIEWPORT_BOUNDS_Y = 5
    SB_VIEWPORT_BOUNDS_W = 200
    #SB_VIEWPORT_BOUNDS_H = 625
    SB_VIEWPORT_BOUNDS_H = 585
    SB_VIEWPORT_BOUNDS_HS = 40
    SB_VIEWPORT_BOUNDS_H1 = 545
    SB_VIEWPORT_BOUNDS_BS = 5
    # keep this in sync with teh screen area

    ## string constants
    DEF_DISP = "..."

    ## selection types
    SELECT_ACS = store.mas_sprites_json.SP_ACS
    SELECT_HAIR = store.mas_sprites_json.SP_HAIR
    SELECT_CLOTH = store.mas_sprites_json.SP_CLOTHES

    SELECT_CONSTS = (
        SELECT_ACS,
        SELECT_HAIR,
        SELECT_CLOTH
    )

    # create the selectable lists
    # we also create a dict mapping similar to sprites.
    # maps
    # key: sprite object name
    # value: selectable object
    ACS_SEL_MAP = {}
    HAIR_SEL_MAP = {}
    CLOTH_SEL_MAP = {}

    # lists, these should be sorted so do insertSort
    ACS_SEL_SL = []
    HAIR_SEL_SL = []
    CLOTH_SEL_SL = []

    GRP_TOPIC_LIST = [
        "choker",
        "earrings",
        "hat",
        "left-hair-clip",
        "left-hair-flower",
        "ribbon",
    ]

    # generic select dlg quips go here
    # should be as neutral as possible to go with any kind of acs
    # be it singular or plural
    generic_sel_dlg_quips = [
        "Good choice, [player]!",
        "I was thinking the same thing, [player]!",
        "Great choice, [player]!",
        "What do you think, [player]?",
        "How do I look, [player]?",
        "I really like this look, [player]!",
        "Just what I was thinking!",
        "Just what I had in mind!"
    ]

    # disable constants
    DISB_NONE = 0
    DISB_HAIR_BC_CLOTH = 1
    DISB_ACS_BC_HAIR = 2

    # disable select dlg quips
    disable_sel_dlg_quips = {
        DISB_NONE: None,
        DISB_HAIR_BC_CLOTH: [
            "That hairstyle doesn't really work with my clothes.",
            "I don't think this hairstyle really works with this outfit.",
            "That hairstyle doesn't really work with this outfit.",
            "I think this hairstyle works better with a different outfit."
        ],
        DISB_ACS_BC_HAIR: [
            "That doesn't really work with my hair.",
            "I don't think this really works with my hairstyle.",
            "This might work with a different hairstyle.",
            "I don't really think this goes with my hair."
        ],
    }


    def selectable_key(selectable):
        """
        Returns the display name of a selectable. meant for sorting.

        IN:
            selectable - the selectbale to get key for

        RETURNS the display name of the selectable
        """
        return selectable.display_name


    def _validate_group_topics():
        """
        Locks selector topics if there are no unlocked selectables with the
        appropriate group.
        Unlocks selector topics if they are unlocked selectables.
        NOTE: also checks the prompt rule
        """
        #ACS
        for group in GRP_TOPIC_LIST:
            min_items = get_minitems(group, 1)
            if (
                    check_prompt(group)
                    and len(filter_acs(True, group=group)) >= min_items
            ):
                unlock_prompt(group)
            else:
                lock_prompt(group)


    def _switch_to_wear_prompts():
        """
        Switches all prompts for grp_topic_list topics to use their wear prompt.
        """
        for group in GRP_TOPIC_LIST:
            set_prompt(group, "wear")


    def _has_remover(group):
        """
        Checks if acs of the given group have a remover

        IN:
            group - group to check

        RETURNS: True if this group already has a remover, False otherwise
        """
        acs_list = filter_acs(False, group=group)
        for acs in acs_list:
            if acs.remover:
                return True

        return False


    def _unlock_removers():
        """
        Unlocks remover ACS selectables
        """
        for acs in ACS_SEL_SL:
            if acs.remover:
                acs.unlocked = True


    def _rm_remover(item_list):
        """
        Gets the remover from a given list of items, takes it out of the list
        and reutrns it.

        IN:
            item_list - list of ACS

        RETURNS:
            remover selectable, or None if not found
        """
        for index in range(len(item_list)-1, -1, -1):
            if item_list[index].remover:
                return item_list.pop(index)

        return None


    def create_selectable_remover(acs_type, group, remover_name=None):
        """
        Creates a selectable remover for acs

        IN:
            acs_type - acs type of the acs/remover to make
            group - group of selectables this ACS remover should be linked to
            remover_name - the name to use for the remover. If None, we use
                "Remove"

        RETURNS: remover ACS selectable
        """
        if remover_name is None:
            remover_name = "Remove"

        # get default mux for this acs type
        template = store.mas_sprites.get_ACSTemplate_by_type(acs_type)
        if template is None:
            mux_type = None
        else:
            mux_type = template.mux_type

        remover_acs = store.mas_sprites.create_remover(
            acs_type,
            group,
            mux_type
        )
        init_selectable_acs(
            remover_acs,
            remover_name,
            "remove",
            group,
            remover=True
        )
        return ACS_SEL_MAP[remover_acs.name]


    def rm_selectable_remover(remover_sel):
        """
        Removes a selectable remover for acs.
        NOTE: also removes the ACS associated with this selectable.
        NOTE: only does this for remover type seelctables

        IN:
            remover_sel - remover selectable to remove
        """
        if not remover_sel.remover:
            return

        # otherwise is remover

        # remove the acs
        store.mas_sprites.rm_acs(remover_sel.get_sprobj())

        # and now the selectable
        for index in range(len(ACS_SEL_SL)-1, -1, -1):
            if ACS_SEL_SL[index].name == remover_sel.name:
                ACS_SEL_SL.pop(index)

        if remover_sel.name in ACS_SEL_MAP:
            ACS_SEL_MAP.pop(remover_sel.name)


    ## init functions for the sprites to use
    def init_selectable_acs(
            acs,
            display_name,
            thumb,
            group,
            visible_when_locked=True,
            hover_dlg=None,
            first_select_dlg=None,
            select_dlg=None,
            remover=False
        ):
        """
        Inits the selectable acs

        IN:
            acs - the acs to create a selectable from
            display_name - display name to use
            thumb - thumbnail image
            group - grouping id
            visible_when_locked - True if this should be visible even if locked
                (Default: True)
            hover_dlg - list of dialogue to say when the item is hovered over
                (Default: None)
            first_select_dlg - list of dialogue to say when the item is
                selected for the first time
                (Default: None)
            select_dlg - list of dialogue to say when the item is selected
                after the first time
                (Default: None)
            remover - True if this ACS is a blank one, False otherwise
                (Default: False)
        """
        # no duplicates
        if acs.name in ACS_SEL_MAP:
            raise Exception("ACS already is selectable: {0}".format(acs.name))

        new_sel_acs = store.MASSelectableAccessory(
            acs,
            display_name,
            thumb,
            group,
            visible_when_locked,
            hover_dlg,
            first_select_dlg,
            select_dlg,
            remover
        )
        ACS_SEL_MAP[acs.name] = new_sel_acs
        store.mas_utils.insert_sort(ACS_SEL_SL, new_sel_acs, selectable_key)


    def init_selectable_clothes(
            clothes,
            display_name,
            thumb,
            group,
            visible_when_locked=True,
            hover_dlg=None,
            first_select_dlg=None,
            select_dlg=None
        ):
        """
        Inits the selectable clothes

        IN:
            clothes - the clothes to create selectable from
            display_name - display name to use
            thumb - thumbnail image
            group - grouping id
            visible_when_locked - True if this should be visible even if locked
                (Default: True)
            hover_dlg - list of dialogue to say when the item is hovered over
                (Default: None)
            first_select_dlg - list of dialogue to say when the item is
                selected for the first time
                (Default: None)
            select_dlg - list of dialogue to say when the item is selected
                after the first time
                (Default: None)
        """
        # no duplicates
        if clothes.name in CLOTH_SEL_MAP:
            raise Exception(
                "Clothes already is selectable: {0}".format(clothes.name)
            )

        new_sel_clothes = store.MASSelectableClothes(
            clothes,
            display_name,
            thumb,
            group,
            visible_when_locked,
            hover_dlg,
            first_select_dlg,
            select_dlg
        )
        CLOTH_SEL_MAP[clothes.name] = new_sel_clothes
        store.mas_utils.insert_sort(CLOTH_SEL_SL, new_sel_clothes, selectable_key)


    def init_selectable_hair(
            hair,
            display_name,
            thumb,
            group,
            visible_when_locked=True,
            hover_dlg=None,
            first_select_dlg=None,
            select_dlg=None
        ):
        """
        Inits the selectable hair

        IN:
            hair - the hair to create a selectable from
            display_name - display name to use
            thumb - thumbnail image
            group - grouping id
            visible_when_locked - True if this should be visible even if locked
                (Default: True)
            hover_dlg - list of dialogue to say when the item is hovered over
                (Default: None)
            first_select_dlg - list of dialogue to say when the item is
                selected for the first time
                (Default: None)
            select_dlg - list of dialogue to say when the item is selected
                after the first time
                (Default: None)
        """
        # no duplicates
        if hair.name in HAIR_SEL_MAP:
            raise Exception("Hair already is selectable: {0}".format(hair.name))

        new_sel_hair = store.MASSelectableHair(
            hair,
            display_name,
            thumb,
            group,
            visible_when_locked,
            hover_dlg,
            first_select_dlg,
            select_dlg
        )
        HAIR_SEL_MAP[hair.name] = new_sel_hair
        store.mas_utils.insert_sort(HAIR_SEL_SL, new_sel_hair, selectable_key)


    ## adjust an aspect of monika.
    # NOTE: meant soley in use of preview and deselections.
    def _adjust_monika(
            moni_chr,
            old_map,
            new_map,
            select_type,
            use_old=False,
            outfit_mode=False
        ):
        """
        Adjusts an aspect of monika based on the select type

        NOTE: this also logs exceptions if they occur. Also will undo
            a chnage that causes crash.

        IN:
            moni_chr - MASMonika object to adjust
            old_map - the old select map (what was previously selected)
            new_map - the new select map (what is currently selected)
            select_type - the select type, which determins what parts of
                monika to adjust
            use_old - True means we are reverting back to the old map,
                False meanse use the old map
                (Default: False)
            outfit_mode - True means we are in outfit mode, False if not
                This is used in the clothing changes
                (Default: False)
        """
        if select_type == SELECT_ACS:
            old_map_view = old_map.viewkeys()
            new_map_view = new_map.viewkeys()

            # determine which map is the "old" and which is "new"
            # we want to remove what is excess from the desired map
            if use_old:
                remove_keys = new_map_view - old_map_view
                remove_map = new_map
                add_map = old_map

            else:
                remove_keys = old_map_view - new_map_view
                remove_map = old_map
                add_map = new_map

            # remove what is excess
            for item_name in remove_keys:
                moni_chr.remove_acs(
                    remove_map[item_name].selectable.get_sprobj()
                )

            # then readd everything that was previous
            # EXCEPT removers
            for item in add_map.itervalues():
                if not item.selectable.remover:
                    moni_chr.wear_acs(item.selectable.get_sprobj())

        elif select_type == SELECT_HAIR:

            # determine which map to change to
            if use_old:
                select_map = old_map

            else:
                select_map = new_map

            # change to that map
            for item in select_map.itervalues():
                if use_old or item.selected:
                    prev_hair = moni_chr.hair
                    new_hair = item.selectable.get_sprobj()

                    if prev_hair == new_hair:
                        # hair is the same? no point in changing
                        return

                    try:
                        moni_chr.change_hair(new_hair)

                    except Exception as e:
                        mas_utils.writelog("BAD HAIR: " + repr(e))
                        moni_chr.change_hair(prev_hair)

                    return # always quit early since you can only have 1 hair

        elif select_type == SELECT_CLOTH:

            # determine which map to change to
            if use_old:
                select_map = old_map

            else:
                select_map = new_map

            # change to that map
            for item in select_map.itervalues():
                if use_old or item.selected:
                    prev_cloth = moni_chr.clothes
                    new_cloth = item.selectable.get_sprobj()

                    if prev_cloth == new_cloth:
                        # we are changing to the what we are wearing? no point
                        return

                    try:
                        moni_chr.change_clothes(
                            new_cloth,
                            outfit_mode=outfit_mode
                        )

                    except Exception as e:
                        mas_utils.writelog("BAD CLOTHES: " + repr(e))
                        moni_chr.change_clothes(prev_cloth)

                    return # quit early since you can only have 1 clothes

        # else, we do not do anything.


    def _fill_select_map(moni_chr, select_type, items, select_map):
        """
        Fills the select map with what monika is currently wearing, based on
        the given select type

        IN:
            moni_chr - MASMonika object to read from
            select_type - the select type, which determins what part of monika
                to read
            items - list of displayables we should check if monika is wearing

        OUT:
            select_map - select map filled with appropriate selectbales.

        RETURNS: true if Monika was found wearing something in the list,
            False if not.
        """
        found_item = False
        if select_type == SELECT_ACS:
            for item in items:
                acs_obj = item.selectable.get_sprobj()
                if moni_chr.is_wearing_acs(acs_obj):
                    select_map[item.selectable.name] = item
                    item.selected = True
                    found_item = True

                # NOTE: cannot quit early because multiple accessories

        elif select_type == SELECT_HAIR:
            for item in items:
                if item.selectable.name == moni_chr.hair.name:
                    select_map[moni_chr.hair.name] = item
                    item.selected = True
                    # we can quit early since you can only have 1 hair
                    return True

        elif select_type == SELECT_CLOTH:
            for item in items:
                if item.selectable.name == moni_chr.clothes.name:
                    select_map[moni_chr.clothes.name] = item
                    item.selected = True
                    # we can quit early since you only have 1 clothes
                    return True

        # else we do not do anything
        return found_item


    def _fill_select_map_and_set_remover(
            moni_chr,
            select_type,
            items,
            select_map,
            remover_disp_item=None
    ):
        """
        Fills select map and sets remover item if passed in.
        If remover item is not passsed in, this functions exactly the same as
        fill_select_map

        IN:
            moni_chr - See _fill_select_map
            select_type - see _fill_select_map
            items - see _fill_select_map
            remover_disp_item - if not None, set this selector if no item is
                found.

        OUT:
            select_map - see _fill_select_map

        RETURNS: see _fill_select_map
        """
        item_found = _fill_select_map(moni_chr, select_type, items, select_map)
        if remover_disp_item is not None and not item_found:
            select_map[remover_disp_item.selectable.name] = remover_disp_item
            remover_disp_item.selected = True

        return item_found


    def _clean_select_map(
            select_map,
            select_type,
            remove_items,
            moni_chr,
            force=False
    ):
        """
        Cleans the select map of non-selected items.

        IN:
            select_map - select map to clean
            select_type - select type, only used if remove_items is True
            remove_items - True means we also remove items from monika chr
            moni_chr - MASMonika object to modify.
            force - if True, we deselect and remove regardless.

        OUT:
            select_map - select map cleaned of non-selectd items
        """
        for item_name in select_map.keys():
            if force or not select_map[item_name].selected:
                item = select_map.pop(item_name)
                item.selected = False # force deselection

                if remove_items and (select_type == SELECT_ACS):
                    moni_chr.remove_acs(item.selectable.get_sprobj())


    ## selection group check
    def valid_select_type(sel_con):
        """
        Returns True if valid selection constant, False otherwise

        IN:
            sel_con - selection constnat to check

        RETURNS: True if vali dselection constant
        """
        sel_types = (SELECT_ACS, SELECT_HAIR, SELECT_CLOTH)
        return sel_con in sel_types


    ## acs/hair/clothes selection helper functions
    def is_same(old_map_view, new_map_view):
        """
        Compares the given select map views for differences.

        NOTE: we only check key existence. Use this after you clean the
        map.

        IN:
            old_map_view - viewkeys view of the old map
            new_map_view - viewkeys view of the new map

        RETURNS:
            True if the maps are the same, false if different.
        """
        old_len = len(old_map_view)

        # lengths dont match? clearly these views do not match then.
        if old_len != len(new_map_view):
            return False

        # otherwise, now we get intersection and verify length
        return old_len == len(old_map_view & new_map_view)


    def _save_selectable(source, dest):
        """
        Saves selectable data from the given source into the destination.

        IN:
            source - source data to read
            dest - data place to save
        """
        for item_name, item in source.iteritems():
            dest[item_name] = item.toTuple()


    def save_selectables():
        """
        Goes through the selectables and saves their unlocked property.

        NOTE: we do this by adding the name into the appropriate persistent.
        also the data we want to save
        """
        _save_selectable(ACS_SEL_MAP, store.persistent._mas_selspr_acs_db)
        _save_selectable(HAIR_SEL_MAP, store.persistent._mas_selspr_hair_db)
        _save_selectable(
            CLOTH_SEL_MAP,
            store.persistent._mas_selspr_clothes_db
        )


    def _load_selectable(source, dest):
        """
        Loads selectable data from the given source into the destination.

        IN:
            source - source data to load from
            dest - data to save the loaded data into
        """
        for item_name, item_tuple in source.iteritems():
            if item_name in dest:
                dest[item_name].fromTuple(item_tuple)


    def load_selectables():
        """
        Loads the persistent data into selectables.
        """
        _load_selectable(store.persistent._mas_selspr_acs_db, ACS_SEL_MAP)
        _load_selectable(store.persistent._mas_selspr_hair_db, HAIR_SEL_MAP)
        _load_selectable(
            store.persistent._mas_selspr_clothes_db,
            CLOTH_SEL_MAP
        )


    def _filter_sel_single(item, unlocked, group):
        """
        Checks if the given item matches the given criteria

        IN:
            item - selectable to check
            unlocked - True means item matches if its unlocked
            group - if not None, then item matches if the group matches

        RETURNS:
            True if the item matches the criteria, False otherwise
        """
        if unlocked and not item.unlocked:
            return False

        if group is not None and item.group != group:
            return False

        return True


    def _filter_sel(select_list, unlocked, group=None):
        """
        Filters the selectable list based on criteria

        IN:
            select_list - list of Selectables to filter
            unlocked - True means we only match unlocked selectables
            group - non-None means we match selectables that match this
                group. If None, we dont check group at all.
                (Default: None)

        RETURNS: list of selectables that match criteria
        """
        return [
            item
            for item in select_list
            if _filter_sel_single(item, unlocked, group)
        ]


    def filter_acs(unlocked, group=None):
        """
        Filters the selectable acs based on criteria

        IN:
            unlocked - True means we only match unlocked selectables
            group - non-None means we match selectables that match this group
                if None, we don't check group at all.
                (Default: None)

        RETURNS: list of selectable acs that match criteria
        """
        return _filter_sel(ACS_SEL_SL, unlocked, group)


    def filter_clothes(unlocked, group=None):
        """
        Filters the selectable clothes based on critera

        IN:
            unlocked - True means we only match unlocked selectables
            group - non-None means we match selectables that match this group
                if None, we don't check group at all
                (Default: None)

        RETURNS: list of selectable clothes that match criteria
        """
        return _filter_sel(CLOTH_SEL_SL, unlocked, group)


    def filter_hair(unlocked, group=None):
        """
        Filters the selectable hair based on critera

        IN:
            unlocked - True means we only match unlocked selectables
            group - non-None means we match selectables that match this group
                if None, we don't check group at all
                (Default: None)

        RETURNS: list of selectable hair that match criteria
        """
        return _filter_sel(HAIR_SEL_SL, unlocked, group)


    def _get_sel(item, select_type):
        """
        Retreives the selectable for the given item.

        IN:
            item - item to find Selectable for
            select_type - the type of selectable we are trying to find

        RETURNS the selectable for the item, or None if not found
        """
        if select_type == SELECT_ACS:
            return get_sel_acs(item)

        elif select_type == SELECT_HAIR:
            return get_sel_hair(item)

        elif select_type == SELECT_CLOTH:
            return get_sel_clothes(item)

        return None


    def get_sel(item):
        """
        Retrieves the selectable for the given item
        This uses sprite object type from jsons.

        IN:
            item - sprite objct to find the Selectable for

        RETURNS: selectable for the given item
        """
        if item.gettype() == store.mas_sprites_json.SP_ACS:
            return get_sel_acs(item)

        elif item.gettype() == store.mas_sprites_json.SP_HAIR:
            return get_sel_hair(item)

        elif item.gettype() == store.mas_sprites_json.SP_CLOTHES:
            return get_sel_clothes(item)

        return None


    def get_sel_acs(acs):
        """
        Retrieves the selectable for the given accessory.

        IN:
            acs - MASAccessory object to find selectable for

        RETURNS the selectable for this acs, or None if not found.
        """
        return ACS_SEL_MAP.get(acs.name, None)


    def get_sel_clothes(clothes):
        """
        Retrieves the selectable for the given clothes

        IN:
            clothes - MASClothes object to find selectable for

        RETURNS the selectable for these clothes, or None if not found
        """
        return CLOTH_SEL_MAP.get(clothes.name, None)


    def get_sel_hair(hair):
        """
        Retrieves the selectable for the given hair

        IN:
            hair - MASHair object to find selectbale for

        RETURNS the selectable for this hair, or none if not found
        """
        return HAIR_SEL_MAP.get(hair.name, None)


    def is_hairacs_compatible(hair, acs_sel):
        """
        Wrapper around mas_sprites.is_hairacs_compatible that uses an ACS
        selector.

        IN:
            hair - hair to check
            acs_sel - ACS selector to check

        RETURNS: True if hair+acs is compatible, False if not
        """
        return store.mas_sprites.is_hairacs_compatible(
            hair,
            acs_sel.get_sprobj()
        )


    def is_clotheshair_compatible(clothes, hair_sel):
        """
        Wrapper around mas_sprites.is_clotheshair_compatible that uses a
        hair selector.

        IN:
            clothes - clothes to check
            hair_sel - hair selector to check

        RETURNS: True if clothes+hair is compatible, false if not
        """
        return store.mas_sprites.is_clotheshair_compatible(
            clothes,
            hair_sel.get_sprobj()
        )


    def _lock_item(item, select_type):
        """
        Locks the given item's selectable.

        IN:
            item - item to find selectable for
            select_type - the type of selectable we are trying to find
        """
        sel_item = _get_sel(item, select_type)
        if sel_item:
            sel_item.unlocked = False


    def lock_acs(acs):
        """
        Locks the given accessory's selectable

        IN:
            acs - MASAccessory object to lock
        """
        _lock_item(acs, SELECT_ACS)


    def lock_clothes(clothes):
        """
        Locks the given clothes' selectable

        IN:
            clothes - MASClothes object to lock
        """
        _lock_item(clothes, SELECT_CLOTH)


    def lock_hair(hair):
        """
        locks the given hair's selectable

        IN:
            hair - MASHair object to lock
        """
        _lock_item(hair, SELECT_HAIR)


    def set_compat_acs(acs_sels, hair):
        """
        Checks compatibility of the given list of acs selectors to the given
        hair sprite object and sets appropriate flags

        IN:
            acs_sels - list of acs selectors to check
            hair - hair sprite object to check

        OUT:
            acs_sels - acs selectors with modified flags for compatibility
        """
        for acs_sel in acs_sels:
            if is_hairacs_compatible(hair, acs_sel):
                acs_sel.disable_type = store.mas_selspr.DISB_NONE
            else:
                acs_sel.disable_type = store.mas_selspr.DISB_ACS_BC_HAIR


    def set_compat_hair(hair_sels, clothes):
        """
        Checks compatiblity of the given list of hair selectors to the given
        clothing sprite object and sets appropriate flags.

        IN:
            hair_sels - list of hair selectors to check
            clothes - clothing sprite object to check

        OUT:
            hair_sels - hair selectors with modified flags for compatibility
        """
        for hair_sel in hair_sels:
            if is_clotheshair_compatible(clothes, hair_sel):
                hair_sel.disable_type = store.mas_selspr.DISB_NONE
            else:
                hair_sel.disable_type = store.mas_selspr.DISB_HAIR_BC_CLOTH


    def _unlock_item(item, select_type):
        """
        Unlocks the given item's selectable

        IN:
            item - item to find selectable for
            select_type - the type of selectable we are trying to find
        """
        sel_item = _get_sel(item, select_type)
        if sel_item:
            sel_item.unlocked = True


    def unlock_acs(acs):
        """
        Unlocks the given accessory's selectable

        IN:
            acs - MASAccessory object to unlock
        """
        _unlock_item(acs, SELECT_ACS)


    def unlock_clothes(clothes):
        """
        Unlocks the given clothes' selectable

        IN:
            clothes - MASClothes object to unlock
        """
        _unlock_item(clothes, SELECT_CLOTH)


    def unlock_hair(hair):
        """
        Unlocks the given hair's selectable

        IN:
            hair - MASHair object to unlock
        """
        _unlock_item(hair, SELECT_HAIR)


    def unlock_selector(group):
        """DEPRECATED - Use unlock_prompt instead
        Unlocks the selector of the given group.

        IN:
            group - group to unlock selector topic.
        """
        unlock_prompt(group)


    def json_sprite_unlock(sp_obj, unlock_label=True):
        """RUNTIME ONLY
        Unlocks selectable for the given sprite, as ewll as the selector
        topic for that sprite.

        NOTE: checks if the prompt's rules passes before unlocking.

        IN:
            sp_obj - sprite object to unlock selectbale+
            unlock_label - True will unlock the selector lable, False will not
                (Default: True)
        """
        sp_type = sp_obj.gettype()

        # unlocks the selectable
        _unlock_item(sp_obj, sp_type)

        # retrieve selectable and unlock the group's selector
        if unlock_label:
            sel_obj = _get_sel(sp_obj, sp_type)
            if check_prompt(sel_obj.group):
                unlock_prompt(sel_obj.group)

                # make sure the selector uses the right propmt



    # extension of mailbox
    class MASSelectableSpriteMailbox(store.MASMailbox):
        """
        SelectableSprite extension of the mailbox

        PROPERTIES:
            (no additional)

        See MASMailbox for properties.
        """
        def __init__(self, def_disp_text=DEF_DISP):
            """
            Constructor for the selectable sprite mailbox
            """
            super(MASSelectableSpriteMailbox, self).__init__()
            self.send_def_disp_text(def_disp_text)
            self.send_conf_enable(False)
            self.send_restore_enable(False)
            self.send_frame_vsize(SB_VIEWPORT_BOUNDS_H)

        def _get(self, headline):
            """
            Class the super class's get

            This is just for ease of use
            """
            return super(MASSelectableSpriteMailbox, self).get(headline)

        def _read(self, headline):
            """
            Calls the super class read

            THis is just for ease of us
            """
            return super(MASSelectableSpriteMailbox, self).read(headline)

        def _send(self, headline, msg):
            """
            Calls the super classs's send

            This is just for ease of use.
            """
            super(MASSelectableSpriteMailbox, self).send(headline, msg)

        def read_conf_enable(self):
            """
            Returns the value of the conf enable message

            RETURNS:
                True if the confirmation button should be enabled, False
                otherwise
            """
            return self._read(MB_CONF)

        def read_def_disp_text(self):
            """
            Returns the default display text message

            NOTE: does NOT remove.

            RETURNS: display text, default
            """
            return self._read(MB_DISP_DEF)

        def read_frame_vsize(self):
            """
            Returns frame fsize
            """
            return self._read(MB_FRAME_VSIZE)

        def read_outfit_checkbox_checked(self):
            """
            Returns the value of the outfit checkbox checked message

            RETURNS:
                True if the outfit checkbox is checked, False otherwise
            """
            return self._read(MB_OCB_CHECKED)

        def read_outfit_checkbox_visible(self):
            """
            Returns the value of the outfit checkbox visible message

            RETURNS:
                True if the outfit checkbox should be visible, False otherwise
            """
            return self._read(MB_OCB_VISIBLE)

        def read_prev_state(self):
            """
            Returns value of the prev_state message

            RETURNS: previous MASMOnika state.
            """
            return self._read(MB_PREV_STATE)

        def read_restore_enable(self):
            """
            Returns the value of the restore enable message

            RETURNS: True if the restore button should be enabled, False
                otherwise
            """
            return self._read(MB_RSTR_ENABLE)

        def read_restore_visible(self):
            """
            Returns the value of the restore visible message

            RETURNS: True if the restore button should be visible, false
                otherwise
            """
            return self._read(MB_RSTR_VISIBLE)

        def get_disp_fast(self):
            """
            Removes and returns the fast flag

            RETURNS: True if we want to append fast, False/None if not
            """
            return self._get(MB_DISP_FAST)

        def get_disp_text(self):
            """
            Removes and returns the display text message

            RETURNS: display text
            """
            return self._get(MB_DISP)

        def send_conf_enable(self, enable):
            """
            Sends enable message

            IN:
                enable - True means to enable, False means to disable
            """
            self._send(MB_CONF, enable)

        def send_def_disp_text(self, txt):
            """
            Sends default display message

            IN:
                txt - txt to display
            """
            self._send(MB_DISP_DEF, txt)

        def send_disp_fast(self):
            """
            Sends default fast flag
            """
            self._send(MB_DISP_FAST, True)

        def send_disp_text(self, txt):
            """
            Sends display text message

            IN:
                txt - txt to display
            """
            self._send(MB_DISP, txt)

        def send_frame_vsize(self, vsize):
            """
            Sends frame vsize message

            IN:
                vsize - vsize
            """
            self._send(MB_FRAME_VSIZE, vsize)

        def send_outfit_checkbox_checked(self, checked):
            """
            Sends ocb checked message

            IN:
                checked - True means checkbox checked, False means not checked
            """
            self._send(MB_OCB_CHECKED, checked)

        def send_outfit_checkbox_visible(self, visible):
            """
            Sends ocb visible message

            IN:
                visible - True means to show the outfit checkbox, False means
                    hide
            """
            self._send(MB_OCB_VISIBLE, visible)

        def send_prev_state(self, prev_state):
            """
            Sends previous MASMonika state

            IN:
                prev_state - previous MASMonika state
            """
            self._send(MB_PREV_STATE, prev_state)

        def send_restore_enable(self, enable):
            """
            sends restore enable messgae

            IN:
                enable - True means to enable the restore button, False means
                    disable
            """
            self._send(MB_RSTR_ENABLE, enable)


init -1 python:
    import random

    # better more user-friendly sel functions
    def mas_SELisUnlocked(_sprite_item):
        """
        Checks if the given sprite item is unlocked

        IN:
            _sprite_item - sprite object to check

        RETURNS: True if the given sprite item is unlocked, false otherwise
        """
        _sel_item = store.mas_selspr._get_sel(
            _sprite_item,
            _sprite_item.gettype()
        )
        if _sel_item is not None:
            return _sel_item.unlocked

        return False


    def mas_filterUnlockGroup(
            sp_type,
            group,
            unlock_min=None,
            allow_lock=False
    ):
        """
        Unlock selector topic for the given group if appropriate number of
        selector objects are unlocked.

        IN:
            sp_type - sprite type to filter on
            group - group to use for filtering selectors
            unlock_min - minimum number that has to be unlocked for us to
                unock the selector topic.
                IF None, then we use the amount provided by the PROMPT_MAP
                (Default: None)
            allow_lock - True will lock the selector topic if it fails to be
                unlocked.
                (Default: False)
        """
        # type sanity check
        if sp_type not in store.mas_selspr.SELECT_CONSTS:
            return

        # check if we even have a label to unlock
        if not store.mas_selspr.in_prompt_map(group):
            return

        # check if the selector's rule passes as that takes priority.
        if not store.mas_selspr.check_prompt(group):
            return

        # set default unlock min
        if unlock_min is None:
            unlock_min = store.mas_selspr.get_minitems(group, defval=1)

        # get the number of unlocked itms
        if sp_type == store.mas_selspr.SELECT_ACS:
            sel_list = store.mas_selspr.filter_acs(True, group=group)

        elif sp_type == store.mas_selspr.SELECT_HAIR:
            sel_list = store.mas_selspr.filter_hair(True, group=group)

        else:
            sel_list = store.mas_selspr.filter_clothes(True, group=group)

        if len(sel_list) >= unlock_min:
            store.mas_selspr.unlock_prompt(group)

        elif allow_lock:
            store.mas_selspr.lock_prompt(group)


    def mas_hasUnlockedClothesWithExprop(exprop, value=None):
        """
        Checks if we have unlocked clothes with a specific exprop

        IN:
            exprop - exprop to look for
            value - value the exprop should be. Set to None to ignore.
            (Default: None)

        OUT:
            boolean:
                True if we have unlocked clothes with the exprop + value provided
                False otherwise
        """
        for clothes in MASClothes.by_exprop(exprop, value):
            if mas_SELisUnlocked(clothes):
                return True
        return False


    def mas_hasLockedClothesWithExprop(exprop, value=None):
        """
        Checks if we have locked clothes with a specific exprop

        IN:
            exprop - exprop to look for
            value - value the exprop should be. Set to None to ignore.
            (Default: None)

        OUT:
            boolean:
                True if we have locked clothes with the exprop + value provided
                False otherwise
        """
        for clothes in MASClothes.by_exprop(exprop, value):
            if not mas_SELisUnlocked(clothes):
                return True
        return False


    ## custom displayable
    class MASSelectableImageButtonDisplayable(renpy.Displayable):
        """
        Custom button for the selectable items.
        """
        import pygame
        from store.mas_selspr import MB_DISP, DISB_NONE, DISB_HAIR_BC_CLOTH

        # constnats
        THUMB_DIR = "mod_assets/thumbs/"

        WIDTH = 180 # default width
        TX_WIDTH = 170 # width of the text object

        # technically this should change.
        TOTAL_HEIGHT = 218
        SELECTOR_HEIGHT = 180

        # this is the default, but the real may change using the expanding
        # frame properties.
        TOP_FRAME_HEIGHT = 38 # default
        TOP_FRAME_TEXT_HEIGHT = 35 # part of the top frame where text should be
        TOP_FRAME_CHUNK = 35 # each text chunk should consist of 35px
        TOP_FRAME_SPACER = 5 # pixels between each text chunk line

        # mouse stuff
        MOUSE_EVENTS = (
            pygame.MOUSEMOTION,
            pygame.MOUSEBUTTONDOWN,
            pygame.MOUSEBUTTONUP
        )
        MOUSE_WHEEL = (4, 5)

        def __init__(self,
                _selectable,
                select_map,
                viewport_bounds,
                mailbox=None,
                multi_select=False,
                disable_type=store.mas_selspr.DISB_NONE
            ):
            """
            Constructor for this displayable

            IN:
                selectable - the selectable object we want to encapsulate
                select_map - dict containing group keys of previously selected
                    objects.
                viewport_bounds - tuple of the following format:
                    [0]: xpos of the viewport upper left
                    [1]: ypos of the viewport upper left
                    [2]: width of the viewport
                    [3]: height of the viewport
                    [4]: border size
                mailbox - dict to send messages to outside from this
                    displayable.
                    (Default: None)
                multi_select - True means we can select more than one item.
                    False otherwise
                    (Default: False)
                disable_type - pass in a disable constant to disable this item
                    for the specified reason.
                    (Default: 0 - DISB_NONE)
            """
            super(MASSelectableImageButtonDisplayable, self).__init__()

            if mailbox is None:
                self.mailbox = {}
            else:
                self.mailbox = mailbox

            self.selectable = _selectable
            self.select_map = select_map
            self.multi_select = multi_select
            self.been_selected = False
            self.disable_type = disable_type
            self.disabled = disable_type != self.DISB_NONE

            # if this is a remover, we don't use the thumb
            if self.selectable.remover:
                thumb_path = self.THUMB_DIR + "remove.png"

            else:
                # as a precaution, if a thumb doesn't exist, we use a
                # placeholder.
                thumb_path = self.THUMB_DIR + _selectable.thumb
                if not renpy.loadable(thumb_path):
                    thumb_path = self.THUMB_DIR + "unknown.png"

            self.thumb = Image(thumb_path)

            # image setups
            self.thumb_overlay = Image(
                mas_getTimeFile("mod_assets/frames/selector_overlay.png")
            )
            self.thumb_overlay_locked = Image(
                mas_getTimeFile("mod_assets/frames/selector_overlay_disabled.png")
            )
            self.top_frame = Frame(
                mas_getTimeFile("mod_assets/frames/selector_top_frame.png"),
                left=4,
                top=4,
                tile=True
            )
            self.top_frame_selected = Frame(
                mas_getTimeFile("mod_assets/frames/selector_top_frame_selected.png"),
                left=4,
                top=4,
                tile=True
            )
            self.top_frame_locked = Frame(
                mas_getTimeFile("mod_assets/frames/selector_top_frame_disabled.png"),
                left=4,
                top=4,
                tile=True
            )

            # renpy solids and stuff
            self.hover_overlay = Solid("#ffaa99aa")

            # text objects
            # NOTE: we build these on first render
            self.item_name = []
            self.item_name_hover = []
#            self.item_name = self._display_name(False, self.selectable.display_name)
#            self.item_name_hover = self._display_name(True, self.selectable.display_name)

            # setup viewport bound values
            vpx, vpy, vpw, vph, vpb = viewport_bounds
            self.xlim_lo = vpx + vpb
            self.xlim_up = (vpx + vpw) - vpb
            self.ylim_lo = vpy + vpb
            self.ylim_up = (vpy + vph) - vpb

            # flags
            self.hovered = False
            self.hover_jumped = False # True means we just jumped to label

            # these get changed
            self.hover_width = self.WIDTH
            self.hover_height = self.TOTAL_HEIGHT

            self.selected = False
            self.select_jump = False

            self.first_render = True

            # when True, we make a call to end the interaction after reaching
            # the end of event.
            self.end_interaction = False

            # top frame sizes
            self.top_frame_height = self.TOP_FRAME_HEIGHT

            # locked mode
            self.locked = not self.selectable.unlocked
            self.locked_thumb = Image("mod_assets/thumbs/locked.png")


        def _blit_bottom_frame(self, r, _renders):
            """
            bliting the bottom frames

            IN:
                r - render to blit to
                _renders - list of bottom renders to blit
            """
            for _render in _renders:
                r.blit(_render, (0, self.top_frame_height))


        def _blit_top_frame(self, r, _renders, _disp_name):
            """
            bliting the top frames

            IN:
                r - render to blit to
                _renders - list of top renders to blit
                _disp_name - list of display name renders to blit
            """
            for _render in _renders:
                r.blit(_render, (0, 0))

            # text
            line_index = 1
            for line in _disp_name:
                r.blit(
                    line,
                    (
                        5,
                        (line_index * self.TOP_FRAME_CHUNK)
                        - line.get_size()[1]
                    )
                )
                line_index += 1

        def _check_display_name(self, _display_name_text, st, at):
            """
            Checks the given display name to see if it fits within the frame
            bounds. We will have to adjust if not

            IN:
                _display_name_text - display name as text

            RETURNS:
                the rendered display name rendre if it fits, None if not.
            """
            # render the text object we want to test
            _disp_text = self._display_name(False, _display_name_text)
            _render = self._render_display_name_test(_disp_text, st, at)
            dtw, dth = _render.get_size()

            # check width
            if dtw > self.TX_WIDTH:
                return None

            return _render

        def _check_render_split(self, line, lines_list, st, at):
            """
            Checks the given line to see if it fits within a line render.

            NOTE: adds hypen and multiple lines if the line is too long

            IN:
                line - the line we want to check for render
                lines_list - list to add lines to
                st - st for renpy render
                at - at for renpy render

            OUT:
                lines_list - list with lines added
            """
            _render = self._check_display_name(line, st, at)
            if not _render:
                self._hypen_render_split(line, lines_list, st, at)

            else:
                self.item_name.append(_render)
                lines_list.append(line)


        def _display_name(self, selected, _text):
            """
            Returns the text object for the display name.

            IN:
                selected - True if selected, False if not
                _text - actual text to convert into display name obj

            RETURNS:
                the text object for the display name
            """
            if selected:
                color = mas_ui.light_button_text_hover_color

            else:
                color = mas_globals.button_text_idle_color

            return Text(
                _text,
                font=gui.default_font,
                size=gui.text_size,
                color=color,
                outlines=[]
            )


        def _hover(self):
            """
            Does hover actions, which include playing hover sound and sending
            hover msg if appropriate
            """
            if not self.hovered:
                self.hover_jumped = False

            elif not self.hover_jumped:
                # first time hovering
                self.hover_jumped = True

                # play hover sound
                renpy.play(gui.hover_sound, channel="sound")

                # send out hover dlg
                # NOTE: keep in case we want hover text again
#                if self.selectable.hover_dlg is not None:
#                    self._send_hover_text()
#                    self.end_interaction = True
#
#                else:
#                    self.mailbox.send_disp_fast()
#
#                # always reset on a hover
#                self.end_interaction = True


        def _hypen_render_split(self, line, lines_list, st, at, tokens=None):
            """
            Splits a line via hypen.

            We do a reverse through the string to find appropriate render
            sizes.

            NOTE: we add renders to self.item_name

            IN:
                line - line to split
                lines_list - list to add lines to
                st - st for renpy render
                at - at for renpy render
                tokens - current list of tokens, if we are in the token mode.
                    Insert the leftover token word at position 1.
                    (Default: None)

            OUT:
                lines_list - list with lines added
            """
            # NOTE: we do reverse because it is more likely that text is
            #   just barely too large, than dealing with one huge string.
            index = len(line)-2
            while index >= 0:
                # split and add hypen
                line1 = line[:index] + "-"

                # check the render
                _l1_render = self._check_display_name(line1, st, at)
                if _l1_render:
                    # add line 1
                    self.item_name.append(_l1_render)
                    lines_list.append(line1)

                    # recurse 2nd line
                    line2 = line[index:]
                    if tokens is not None:
                        tokens.insert(1, line2)
                    else:
                        self._check_render_split(line2, lines_list, st, at)
                    return

                # doesnt fit, decreaes index and continue
                index -= 1


        def _is_over_me(self, x, y):
            """
            Returns True if the given x, y is over us.
            This also handles if the mouse is past the viewport bounds.

            IN:
                x - x coord relative to upper left of this displayable
                y - y coord relative to upper left of this displayable
            """
            mouse_x, mouse_y = renpy.get_mouse_pos()
            return (
                self.xlim_lo <= mouse_x <= self.xlim_up
                and self.ylim_lo <= mouse_y <= self.ylim_up
                and 0 <= x <= self.hover_width
                and 0 <= y <= self.hover_height
            )


        def _rand_select_dlg(self, dlg_list):
            """
            Randomly selects dialogue from the given list

            IN:
                dlg_list - list to select from

            ASSUMES the list is not empty
            """
            return dlg_list[random.randint(0, len(dlg_list)-1)]


        def _render_bottom_frame(self, hover, st, at):
            """
            Renders the bottom frames, returns a list of the renders in order
            of bliting.

            IN:
                hover - True means we are hovering (or are selected), false
                    otherwise

            RETURNS:
                list of renders, in correct blit order
            """
            _renders = [
                self._render_bottom_frame_piece(self.thumb, st, at),
                self._render_bottom_frame_piece(self.thumb_overlay, st, at)
            ]

            if hover:
                _renders.append(
                    self._render_bottom_frame_piece(self.hover_overlay, st, at)
                )

            return _renders

        def _render_bottom_frame_piece(self, piece, st, at):
            """
            Renders a single bottom frame piece and returns it
            """
            return renpy.render(
                piece,
                self.WIDTH,
                self.SELECTOR_HEIGHT,
                st,
                at
            )

        def _render_display_name(self, hover, _text, st, at):
            """
            Renders display name

            IN:
                hover - True if selected, False if not
                _text - actual text to render
                st - st for renpy render
                at - at for renpy render

            RETURNS: rendered display name
            """
            return self._render_display_name_raw(
                self._display_name(hover, _text),
                st,
                at
            )

        def _render_display_name_raw(self, disp_text, st, at):
            """
            Renders display name, given a text object

            IN:
                disp_text - text object to display
                st - st for renpy render
                at - at for renpy render

            RETURNS: rendered display name
            """
            return renpy.render(
                disp_text,
                self.WIDTH,
                self.TOP_FRAME_CHUNK,
                st,
                at
            )

        def _render_display_name_test(self, disp_text, st, at):
            """
            Renders display name using testing width. (1000)

            IN:
                disp_text - the text to show
                st - st for renpy render
                at - at for renpy render

            RETURNS: rendered display name
            """
            return renpy.render(disp_text, 1000, self.TOP_FRAME_CHUNK, st, at)

        def _render_top_frame(self, hover, st, at):
            """
            Renders the top renders, returns a list of the renders in order of
            bliting.

            IN:
                hover - True means we are hovering (or are selected

            RETURNS:
                list of renders, in correct blit order
            """
            if hover:
                _main_piece = self._render_top_frame_piece(
                    self.top_frame_selected,
                    st,
                    at
                )

            else:
                _main_piece = self._render_top_frame_piece(
                    self.top_frame,
                    st,
                    at
                )

            return [_main_piece]

        def _render_top_frame_piece(self, piece, st, at):
            """
            Renders a top frame piece. No Text, please
            """
            return renpy.render(
                piece,
                self.WIDTH,
                self.top_frame_height,
                st,
                at
            )

        def _select(self):
            """
            Makes this item a selected item. Also handles other logic realted
            to selecting this.
            """
            # if already selected, then we need to deselect.
            if self.selected:
                # TODO: this actually can break things if we dselect
                #   probably should handle this a smarter way like if
                #   something was selected originally, dont make it possible
                #   to deselect.
                #   or make it select what was originally selected.
                # deselect self
#                self.selected = False
#                renpy.redraw(self, 0)

                # end interaction so display text is rest
#                self.end_interaction = True
                return

            # TODO: should be moved to the top when deselect can happen
            # play the select sound
            renpy.play(gui.activate_sound, channel="sound")

            # otherwise select self
            self.selected = True

            if not self.multi_select:
                # must clean select map
                for item in self.select_map.itervalues():
                    # setting to False will queue for removal of item
                    # NOTE: the caller must handle teh removal
                    item.selected = False
                    renpy.redraw(item, 0)

            # add this item to the select map
            self.select_map[self.selectable.name] = self

            # the appropriate dialogue
            if self.been_selected:
                if self.selectable.select_dlg is not None:
                    # this should be first as it allows us to override
                    # remover dialogue
                    self._send_select_text()

                elif self.selectable.remover:
                    self.mailbox.send_disp_fast()

                else:
                    self._send_generic_select_text()

            else:
                # not been selected before
                self.been_selected = True
                if self.selectable.first_select_dlg is not None:
                    self._send_first_select_text()

                elif self.selectable.select_dlg is not None:
                    self._send_select_text()

                elif self.selectable.remover:
                    self._send_msg_disp_text(None)
                    self.mailbox.send_disp_fast()

                else:
                    self._send_generic_select_text()

            # always reset interaction if something has been selected
            self.end_interaction = True

        def _select_disabled(self):
            """
            Called when selecting a disabled item.
            """
            renpy.play(gui.activate_sound_glitch, channel="sound")
            self._send_disabled_select_text()
            self.mailbox.send_disp_fast()
            self.end_interaction = True

        def _send_first_select_text(self):
            """
            Sends first select text to mailbox

            ASSUMES first select text exists
            """
            self._send_msg_disp_text(
                self._rand_select_dlg(
                    self.selectable.first_select_dlg
                )
            )

        def _send_disabled_select_text(self):
            """
            Sends disabled select text to mailbox

            ASSUMES we are disabled
            """
            sendable_txts = store.mas_selspr.disable_sel_dlg_quips.get(
                self.disable_type,
                None
            )
            if sendable_txts:
                self._send_msg_disp_text(self._rand_select_dlg(sendable_txts))

        def _send_generic_select_text(self):
            """
            Sends generic select text to mailbox
            """
            self._send_msg_disp_text(
                self._rand_select_dlg(
                    store.mas_selspr.generic_sel_dlg_quips
                )
            )

        def _send_hover_text(self):
            """
            Sends hover text to mailbox

            ASSUMES hover text exists
            """
            self._send_msg_disp_text(
                self._rand_select_dlg(
                    self.selectable.hover_dlg
                )
            )

        def _send_msg_disp_text(self, msg):
            """
            Sends text message to mailbox.

            IN:
                msg - text message to send
            """
            self.mailbox.send_disp_text(msg)

        def _send_select_text(self):
            """
            Sends the select text to mailbox

            ASSUMES select text exists
            """
            self._send_msg_disp_text(
                self._rand_select_dlg(
                    self.selectable.select_dlg
                )
            )

        def _setup_display_name(self, st, at):
            """
            Sets up item_name and item_name_hover with list of text display
            objects, ready for render.

            IN:
                st - st for renpy render
                at - at for renpy render
            """
            # lets initially check if the pure text renders nicely
            _render = self._check_display_name(
                self.selectable.display_name,
                st,
                at
            )

            if _render:
                self.item_name = [
                    self._display_name(False, self.selectable.display_name)
                ]
                self.item_name_hover = [
                    self._display_name(True, self.selectable.display_name)
                ]
                return

            # if we got a None, the text is too long.
            _lines = self._split_render(self.selectable.display_name, st, at)
            # NOTE: rather than rewriting split_render, decided to just
            # use the returned lines and overwrite the render list
            self.item_name = [
                self._display_name(False, line) for line in _lines
            ]

            # get displaynames for the hover variants
            # and calculate total height
#            top_height = 0
            self.item_name_hover = [
                self._display_name(True, line)
                for line in _lines
            ]
#            top_height += (_render.get_size()[1] + self.TOP_FRAME_SPACER)

            # now setup the new frame size
            self.top_frame_height = (
                (self.TOP_FRAME_CHUNK * len(self.item_name_hover))
            )


        def _split_render(self, disp_name, st, at):
            """
            Attempts to split the displayname, then checks renders for it
            to see if it fits within the bounds.

            NOTE: this will add renders to self.item_name

            IN:
                disp_name - display name to split
                st - st for renpy render
                at - at for renpy render

            RETURNS:
                list of string lines that fit when rendered.
            """
            _tokens = disp_name.split()
            _lines = []

            self._split_render_tokens(_tokens, _lines, st, at)

            return _lines


        def _split_render_tokens(self, tokens, lines_list, st, at, loop=False):
            """
            Token version of _split_render

            IN:
                tokens - tokens to handle with
                lines_list - list of string lines that we rendered
                st - st for renpy render
                at - at for renpy render
                loop - True if we are recursively calling this.
                    (Default: False)
            """
            # sanity check
            if len(tokens) == 0:
                return

            if len(tokens) > 2 or loop:
                self._token_render_split(tokens, lines_list, st, at)

            elif len(tokens) <= 1:
                self._hypen_render_split(tokens[0], lines_list, st, at)

            else:
                # otherwise, we can just use the 2 splits
                self._check_render_split(tokens[0], lines_list, st, at)
                self._check_render_split(tokens[1], lines_list, st, at)


        def _token_render_split(self, tokens, lines_list, st, at):
            """
            Uses the given tokens to determine best fit render options for
            those tokens.

            NOTE: we also do self.item_name

            IN:
                tokens - list of string tokens to apply best fit
                lines_list - list to add lines to
                st - st for renpy render
                at - at for renpy render

            OUT:
                lines_list - list with lines added
            """
            # reverse order siunce we want to maximize render line size
            index = len(tokens)
            while index > 0:

                # build a string with a number of tokens
                line1 = " ".join(tokens[:index])

                # check the render
                _l1_render = self._check_display_name(line1, st, at)
                if _l1_render:
                    # add line 1
                    self.item_name.append(_l1_render)
                    lines_list.append(line1)

                    # recurse the remaining tokens
                    self._split_render_tokens(
                        tokens[index:],
                        lines_list,
                        st,
                        at,
                        True
                    )
                    return

                # otherwise, lower index
                index -= 1

            # if we got here, then we are dealing with a single token that is
            # too long.
            self._hypen_render_split(tokens[0], lines_list, st, at, tokens)
            self._split_render_tokens(tokens[1:], lines_list, st, at, True)


        def event(self, ev, x, y, st):
            """
            EVENT. We only want to handle 2 cases:
                MOUSEMOTION + hover is over us
                MOUSEDOWN + mouse is over us
            """
            # window event means we need to re-render everything
            if ev.type == pygame.WINDOWEVENT:
                self.first_render = True
                renpy.redraw(self, 0)
                return

            if ev.type in self.MOUSE_EVENTS:

                if ev.type == pygame.MOUSEMOTION:
                    if not self.locked:
                        self.hovered = self._is_over_me(x, y)
                        renpy.redraw(self, 0)

                elif ev.type == pygame.MOUSEBUTTONDOWN:

                    if ev.button in self.MOUSE_WHEEL:
                        # TODO: scrolling in mouse wheel is not perfect,
                        #   the previously hovered item gest hovered instead
                        #   of what we actually want.
                        if not self.locked:
                            self.hovered = self._is_over_me(x, y)
                            renpy.redraw(self, 0)

                    elif ev.button == 1:
                        # left click
                        if self._is_over_me(x, y):
                            if self.disabled:
                                self._select_disabled()

                            elif not self.locked:
                                self._select()
                                renpy.redraw(self, 0)

#                        elif self.selected and not self.multi_select:
#                            self.selected = False
#                            renpy.redraw(self, 0)

            # apply hover dialogue logic if not selected
            if not self.selected and not self.locked and not self.disabled:
                self._hover()

            if self.end_interaction:
                self.end_interaction = False
                renpy.end_interaction(True)


        def render(self, width, height, st, at):
            """
            Render. we want the button here.
            """
            if self.first_render:
                # render and determine if name is split or not
                self._setup_display_name(st, at)

                # setup the hiehg tof this displyaable
                self.real_height = self.top_frame_height + self.SELECTOR_HEIGHT
                self.hover_height = self.real_height

                self.first_render = False

            # each selector consists of its bottom, top, and disp name
            _bottom_renders = []
            _top_renders = []
            _disp_name = None

            if self.locked or self.disabled:

                # determine the thumbnail
                if self.locked:
                    thumb_render = self._render_bottom_frame_piece(
                        self.locked_thumb,
                        st,
                        at
                    ),
                else:
                    # disabled
                    thumb_render = self._render_bottom_frame_piece(
                        self.thumb,
                        st,
                        at
                    )

                # otherwise, locked and disabled is basically the same
                _bottom_renders = [
                    thumb_render,
                    self._render_bottom_frame_piece(
                        self.thumb_overlay_locked,
                        st,
                        at
                    )
                ]
                _top_renders = [
                    self._render_top_frame_piece(
                        self.top_frame_locked,
                        st,
                        at
                    )
                ]
                _disp_name = [
                    self._render_display_name_raw(txt_obj, st, at)
                    for txt_obj in self.item_name
                ]

            else:
                hov_sel = self.hovered or self.selected

                _bottom_renders = self._render_bottom_frame(hov_sel, st, at)
                _top_renders = self._render_top_frame(hov_sel, st, at)

                if hov_sel:
                    _disp_name = self.item_name_hover
                else:
                    _disp_name = self.item_name

                _disp_name = [
                    self._render_display_name_raw(txt_obj, st, at)
                    for txt_obj in _disp_name
                ]

            # now blit
            r = renpy.Render(self.WIDTH, self.real_height)
            self._blit_top_frame(r, _top_renders, _disp_name)
            self._blit_bottom_frame(r, _bottom_renders)
            return r


init 200 python in mas_selspr:
    load_selectables()


# now these tranforms are for the selector sidebar screen
transform mas_selector_sidebar_tr_show:
    xpos 1280 xanchor 0 ypos 10 yanchor 0
    easein 0.7 xpos 1070

transform mas_selector_sidebar_tr_hide:
    xpos 1080 xanchor 0 ypos 10 yanchor 0
    easeout 0.7 xpos 1280

style mas_selector_sidebar_vbar:
    xsize 18
    base_bar Frame("gui/scrollbar/vertical_poem_bar.png", tile=False)
#    thumb "gui/slider/horizontal_hover_thumb.png"
    thumb Frame("gui/scrollbar/vertical_poem_thumb.png", left=6, top=6, tile=True)
    bar_vertical True
    bar_invert True

# the selector screen sidebar version should be shown, not called.
# note that we do tons of calls here, so just be ready to do tons of loop overs
# every couple of seconds.
#
# IN:
#   items - list of MASSelectableImagebuttonDisplayables to display
#   mailbox - MASSelectableSpriteMailbox for messages
#   confirm - label to jump to when confirming
#   cancel - label to jump to when canceling
#   restore - label to jump to when restoring
#   remover - remover display item, if appropriate. Can be None
screen mas_selector_sidebar(items, mailbox, confirm, cancel, restore, remover=None):
    zorder 50
#    modal True

    $ sel_frame_vsize = mailbox.read_frame_vsize()

    frame:
        area (1075, 5, 200, sel_frame_vsize)
        background Frame(store.mas_ui.sel_sb_frame, left=6, top=6, tile=True)

        vbox:
            xsize 200
            xalign 0.5
            spacing 5

            viewport id "sidebar_scroll":
                mousewheel True
                arrowkeys True

                vbox:
                    xsize 200
                    spacing 10
                    null height 1

                    # add the remover
                    if remover is not None:
                        add remover:
                            xalign 0.5

                    for selectable in items:
                        add selectable:
#                            xoffset 5
                            xalign 0.5

                    null height 1

            null height 5

            if mailbox.read_outfit_checkbox_visible():
                $ ocb_checked = mailbox.read_outfit_checkbox_checked()
                textbutton _("Outfit Mode"):
                    style "generic_fancy_check_button"
                    activate_sound gui.activate_sound
                    action [
                        ToggleField(persistent, "_mas_setting_ocb"),
                        Function(
                            mailbox.send_outfit_checkbox_checked,
                            not ocb_checked
                        )
                    ]
                    selected ocb_checked

            if mailbox.read_conf_enable():
                textbutton _("Confirm"):
                    style "hkb_button"
                    xalign 0.5
                    action Jump(confirm)
            else:
                textbutton _("Confirm"):
                    style "hkb_button"
                    xalign 0.5

            if mailbox.read_restore_enable():
                textbutton _("Restore"):
                    style "hkb_button"
                    xalign 0.5
                    action Jump(restore)
            else:
                textbutton _("Restore"):
                    style "hkb_button"
                    xalign 0.5

            textbutton _("Cancel"):
                style "hkb_button"
                xalign 0.5
                action Jump(cancel)
#                action Function(mailbox.mas_send_return, -1)

        vbar value YScrollValue("sidebar_scroll"):
            style "mas_selector_sidebar_vbar"
            xoffset -25

# GENERAL sidebar selector label
# NOTE: you should NOT call this label. You should call the helper labels
# instead.
# NOTE: this shows the `mas_selector_sidebar` screen. It is the caller's
#   responsibility to hide the screen when done.
#
# IN:
#   items - list of MASSelectable objects to select from.
#   select_type - SELECT_* constant for the current mode. We throw
#       exceptions if this is not passed in and is a valid type.
#   preview_selections - True means the selections are previewed, False means
#       they are not.
#       (Default: True)
#   only_unlocked - True means we only show unlocked items, False means
#       show everything.
#       (Default: True)
#   save_on_confirm - True means we should save selections on a confirm
#       (which means we dont undo selections), while False means we will
#       undo selections on a confirm, and let the caller handle the actual
#       selection saving.
#       (Default: True)
#   mailbox - MASSelectableSpriteMailbox object to use
#       Call send_def_disp_text to set the default display text.
#       Call send_disp_text to set the inital display text.
#       IF None, we create a MASSelectableSpriteMaibox for use.
#   add_remover - True if we want to include a remover in the selector menu,
#       False if not
#       (Default: False)
#   remover_name - name to use for the remover.
#       (Default: None)
#
# OUT:
#   select_map - map of selections. Organized like:
#       name: MASSelectableImageButtonDisplayable object
#
# RETURNS True if we are confirming the changes, False if not.
label mas_selector_sidebar_select(items, select_type, preview_selections=True, only_unlocked=True, save_on_confirm=True, mailbox=None, select_map={}, add_remover=False, remover_name=None):

    python:
        if not store.mas_selspr.valid_select_type(select_type):
            raise Exception(
                "invalid selection constant: {0}".format(select_type)
            )

        # otherwise, quickly setup the flags for what mode we are in.
#        selecting_acs = select_type == store.mas_selspr.SELECT_ACS
#        selecting_hair = select_type == store.mas_selspr.SELECT_HAIR
#        selecting_clothes = select_type == store.mas_selspr.SELECT_CLOTH

        # setup the mailbox
        if mailbox is None:
            mailbox = store.mas_selspr.MASSelectableSpriteMailbox()

        # save state
        prev_moni_state = monika_chr.save_state(True, True, True)
        mailbox.send_prev_state(prev_moni_state)

        # initalize vsize
        if mailbox.read_outfit_checkbox_visible():
            mailbox.send_frame_vsize(
                store.mas_selspr.SB_VIEWPORT_BOUNDS_H1
            )

        # pull out the remover selectable for special use, if found
        remover_item = store.mas_selspr._rm_remover(items)
        remover_disp_item = None

        viewport_bounds = (
            store.mas_selspr.SB_VIEWPORT_BOUNDS_X,
            store.mas_selspr.SB_VIEWPORT_BOUNDS_Y,
            store.mas_selspr.SB_VIEWPORT_BOUNDS_W,
            mailbox.read_frame_vsize(),
            store.mas_selspr.SB_VIEWPORT_BOUNDS_BS
        )

        # if in outfit mode, apply the outfit before launching
        if mailbox.read_outfit_checkbox_checked():
            monika_chr.change_clothes(
                monika_chr.clothes,
                by_user=True,
                outfit_mode=True
            )

    # sanity check to avoid crashes
    if len(items) < 1:
        return False

    python:

        # however, we only want to actually create a remover if we were
        # asked to do so
        if add_remover:
            if remover_item is None:
                sample_sel = items[0]
                sample_obj = sample_sel.get_sprobj()

                # create generic remover item
                remover_item = store.mas_selspr.create_selectable_remover(
                    sample_obj.acs_type,
                    sample_sel.group,
                    remover_name
                )

            # unlock the remover
            remover_item.unlocked = True

            # create the displayable
            remover_disp_item = MASSelectableImageButtonDisplayable(
                remover_item,
                select_map,
                viewport_bounds,
                mailbox
            )

        # only show unlock
        if only_unlocked:
            disp_items = [
                MASSelectableImageButtonDisplayable(
                    item,
                    select_map,
                    viewport_bounds,
                    mailbox,
                    False, # TODO: multi-select
                    item.disable_type
                )
                for item in items
                if item.unlocked
            ]

        else:
            disp_items = [
                MASSelectableImageButtonDisplayable(
                    item,
                    select_map,
                    viewport_bounds,
                    mailbox,
                    False, # TODO: multi-select
                    item.disable_type
                )
                for item in items
            ]

        # fill select map
        item_found = store.mas_selspr._fill_select_map_and_set_remover(
            monika_chr,
            select_type,
            disp_items,
            select_map,
            remover_disp_item=remover_disp_item
        )

        # make copy of old select map
        old_select_map = dict(select_map)

        # also create views that we use for comparisons
        old_view = old_select_map.viewkeys()
        new_view = select_map.viewkeys()

        # disable menu interactions to prevent bugs
        disable_esc()

        # store current auto forward mode state
        afm_state = _preferences.afm_enable

        # and disable it
        _preferences.afm_enable = False

        # setup prev line
        prev_line = ""

    show screen mas_selector_sidebar(disp_items, mailbox, "mas_selector_sidebar_select_confirm", "mas_selector_sidebar_select_cancel", "mas_selector_sidebar_select_restore", remover=remover_disp_item)

label mas_selector_sidebar_select_loop:
    python:

        # select map parsing
        store.mas_selspr._clean_select_map(
            select_map,
            select_type,
            preview_selections,
            monika_chr
        )

        if preview_selections:
            store.mas_selspr._adjust_monika(
                monika_chr,
                old_select_map,
                select_map,
                select_type,
                outfit_mode=mailbox.read_outfit_checkbox_checked()
            )


label mas_selector_sidebar_select_midloop:

    python:
        # once select map is cleaned, check if diff
        #has_diff = not store.mas_selspr.is_same(old_view, new_view)
        has_diff = not monika_chr.same_state(prev_moni_state)
        mailbox.send_conf_enable(has_diff)
        mailbox.send_restore_enable(has_diff)

        # display text parsing
        disp_text = mailbox.get_disp_text()
        disp_fast = mailbox.get_disp_fast()

        if disp_text is None:
            disp_text = mailbox.read_def_disp_text()

        if disp_fast:
            disp_text += "{fast}"

        # force this to execute in this python block (no prediction)
        renpy.say(m, disp_text)

        #Clear repeated lines
        if prev_line != disp_text:
            if len(_history_list) > 0:
                _history_list.pop()
            #Using this to clear relevant entries from history
            prev_line = disp_text

    jump mas_selector_sidebar_select_loop

label mas_selector_sidebar_select_restore:

    python:
        # clean the selections
        store.mas_selspr._clean_select_map(
            select_map,
            select_type,
            False,
            monika_chr,
            force=True
        )

        # restore monika back to previous
        monika_chr.restore(prev_moni_state)

        # refill selections
        store.mas_selspr._fill_select_map_and_set_remover(
            monika_chr,
            select_type,
            disp_items,
            select_map,
            remover_disp_item=remover_disp_item
        )

        #Clear repeated lines
        if prev_line != disp_text:
            if len(_history_list) > 0:
                _history_list.pop()
            #Using this to clear relevant entries from history
            prev_line = disp_text

        # make next display fast
        mailbox.send_disp_fast()

    # jump back to mid loop
    jump mas_selector_sidebar_select_midloop

label mas_selector_sidebar_select_confirm:
    hide screen mas_selector_sidebar

    # re-enable the menu and restore afm
    $ _preferences.afm_enable = afm_state
    $ enable_esc()

    python:
        if not save_on_confirm:
            store.mas_selspr._clean_select_map(
                select_map,
                select_type,
                preview_selections,
                monika_chr
            )

#            store.mas_selspr._adjust_monika(
#                monika_chr,
#                old_select_map,
#                select_map,
#                select_type,
#                True
#            )

            # reload state
            monika_chr.restore(prev_moni_state)

        # If monika is wearing a remover ACS, remove it.
        for item_name in select_map.keys():
            sel_obj = select_map[item_name].selectable
            if sel_obj.remover:
                spr_obj = sel_obj.get_sprobj()
                monika_chr.remove_acs(spr_obj)
                select_map.pop(item_name)

        # delete the remover if we used one
        if add_remover:
            store.mas_selspr.rm_selectable_remover(remover_item)

        # always save confirming
        monika_chr.save()
        renpy.save_persistent()

    return True

label mas_selector_sidebar_select_cancel:
    hide screen mas_selector_sidebar

    # re-enable the menu and restore afm
    $ _preferences.afm_enable = afm_state
    $ enable_esc()

    python:
        store.mas_selspr._clean_select_map(
            select_map,
            select_type,
            preview_selections,
            monika_chr
        )

#        store.mas_selspr._adjust_monika(
#            monika_chr,
#            old_select_map,
#            select_map,
#            select_type,
#            True
#        )

        # delete the remover if we used one
        if add_remover:
            store.mas_selspr.rm_selectable_remover(remover_item)

        # reload state
        monika_chr.reset_outfit()
        monika_chr.remove_all_acs()
        monika_chr.load_state(prev_moni_state)

    return False

# ACS sidebar selector label
#
# SEE mas_selector_sidebar_select for info on input params.
# NOTE: select_type is not a param here.
#
# RETURNS: True if we are confirming the changes, False if not
label mas_selector_sidebar_select_acs(items, preview_selections=True, only_unlocked=True, save_on_confirm=True, mailbox=None, select_map={}, add_remover=False, remover_name=None):

    call mas_selector_sidebar_select(items, store.mas_selspr.SELECT_ACS, preview_selections, only_unlocked, save_on_confirm, mailbox, select_map, add_remover, remover_name)

    return _return


# HAIR sidebar selector label
#
# SEE mas_selector_sidebar_select for info on input params.
# NOTE: select_type is not a param here.
#
# RETURNS: True if we are confirming the changes, False if not
label mas_selector_sidebar_select_hair(items, preview_selections=True, only_unlocked=True, save_on_confirm=True, mailbox=None, select_map={}, add_remover=False, remover_name=None):

    call mas_selector_sidebar_select(items, store.mas_selspr.SELECT_HAIR, preview_selections, only_unlocked, save_on_confirm, mailbox, select_map, add_remover, remover_name)

    if _return:
        # user hit confirm
        $ persistent._mas_force_hair = True

    return _return

# CLOTH sidebar selector label
#
# SEE mas_selector_sidebar_select for info on input params.
# NOTE: select_type is not a param here.
#
# RETURNS: True if we are confirming the changes, False if not
label mas_selector_sidebar_select_clothes(items, preview_selections=True, only_unlocked=True, save_on_confirm=True, mailbox=None, select_map={}, add_remover=False, remover_name=None):

    call mas_selector_sidebar_select(items, store.mas_selspr.SELECT_CLOTH, preview_selections, only_unlocked, save_on_confirm, mailbox, select_map, add_remover, remover_name)

    if _return:
        # user hit confirm
        $ persistent._mas_force_clothes = True

    return _return


# generic sidebar-based ACS select
# standardized code for ACS selections. If you need custom filtering,
# DONT use this.
# NOTE: this will always show remover (for now)
# NOTE: this wil only show unlocked ACS.
#
# IN:
#   acs_type - acs type of the ACS we want to show
#   use_acs - list of acs to use. if None, we use standard filter
#       (Default: None)
#   set_compat_flags - True will adjust the use_acs using compatibly filter
#       False will not
#       (Default: True)
#   launch_exp - the expression to use when saying "Sure [player]!" before
#       showing the selector.
#       (Default: monika 1eua)
#   idle_exp - the expression to use while the selector is runing.
#       if None is passed in, we use the launch exp.
#       (Default: None)
#   sel_group - the selector group to use.
#       if None, we use the acs_type
#       (Default: None)
#   idle_dlg - dialogue shown while selector is running and nothing has been
#       hovered/selected.
#       if None, we use acs_type, which might be yuck:
#       "Which <acs_type> would you like me to wear?"
#       (Default: None)
label mas_selector_generic_sidebar_select_acs(acs_type, use_acs=None, set_compat_flags=True, launch_exp="monika 1eua", idle_exp=None, sel_group=None, idle_dlg=None):
    python:
        # initial setup
        if sel_group is None:
            sel_group = acs_type
        if idle_dlg is None:
            idle_dlg = "Which {0} would you like me to wear?".format(acs_type)

        # filter for acs
        if use_acs is None:
            use_acs = store.mas_selspr.filter_acs(True, group=sel_group)

        # set compatibilities
        if set_compat_flags:
            store.mas_selspr.set_compat_acs(use_acs, monika_chr.hair)

        # setup mailbox and select map
        mailbox = store.mas_selspr.MASSelectableSpriteMailbox(idle_dlg)
        sel_map = {}

    $ renpy.show(launch_exp)
    m "Sure [player]!"

    if idle_exp is not None and idle_exp != launch_exp:
        $ renpy.show(idle_exp)

    call mas_selector_sidebar_select_acs(use_acs, mailbox=mailbox, select_map=sel_map, add_remover=True)

    if not _return:
        m 1eka "Oh, alright."

    # set the appropriate prompt and dialogue
    if monika_chr.get_acs_of_type(acs_type):
        $ store.mas_selspr.set_prompt(acs_type, "change")
    else:
        $ store.mas_selspr.set_prompt(acs_type, "wear")

    return


########################## SELECTOR TOPICS ####################################
# [MONSEL]

#### Begin monika clothes topics
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_clothes_select",
            category=["appearance"],
            prompt=store.mas_selspr.get_prompt("clothes", "change"),
            pool=True,
            unlocked=True,
            aff_range=(mas_aff.HAPPY, None)
        ),
        restartBlacklist=True,
        markSeen=True
    )

default persistent._mas_setting_ocb = False
# Outfit CheckBox setting

label monika_clothes_select:
    #Setup
    python:
        mailbox = store.mas_selspr.MASSelectableSpriteMailbox(
            "Which clothes would you like me to wear?"
        )
        mailbox.send_outfit_checkbox_visible(True)
        mailbox.send_outfit_checkbox_checked(persistent._mas_setting_ocb)
        sel_map = {}

    # initial dialogue
    m 1hua "Sure!"

    # setup the monika expression during the selection screen
    show monika 2eua

    # start the selection screen
    if mas_isMoniLove():
        # for Love, all unlocked clothes are available
        call mas_selector_sidebar_select_clothes(store.mas_selspr.CLOTH_SEL_SL, mailbox=mailbox, select_map=sel_map)

    else:
        python:
            # need to get a list of clothes that have been gifted
            # so we will get a list of all clothes and then remove the event_clothes
            gifted_clothes = mas_selspr.filter_clothes(True)

            for index in range(len(gifted_clothes)-1, -1, -1):
                spr_obj = gifted_clothes[index].get_sprobj()
                if (
                        not spr_obj.is_custom
                        and spr_obj != mas_clothes_def
                        and spr_obj != mas_clothes_blazerless
                ):
                    gifted_clothes.pop(index)

            #Now we handle holiday clothes
            clothes_to_add = persistent._mas_event_clothes_map.get(datetime.date.today())

            #If there's something for today, then we'll add it to be unlocked
            if clothes_to_add:
                #Get the outfit selector and add it
                gifted_clothes.append(mas_selspr.get_sel_clothes(
                    mas_sprites.get_sprite(
                        mas_sprites.SP_CLOTHES,
                        clothes_to_add
                    )
                ))
                gifted_clothes.sort(key=mas_selspr.selectable_key)


        # below Love, only gifted clothes (and def) are available
        call mas_selector_sidebar_select_clothes(gifted_clothes, mailbox=mailbox, select_map=sel_map)

    # results
    if not _return:
        # user hit cancel
        m 1eka "Oh, alright."

    return

# selector for event days with special outfits for normal and upset people
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_event_clothes_select",
            category=["appearance"],
            prompt=store.mas_selspr.get_prompt("clothes", "change"),
            pool=True,
            unlocked=False,
            rules={"no_unlock": None},
            aff_range=(mas_aff.UPSET, mas_aff.NORMAL)
        ),
        restartBlacklist=True,
        markSeen=True
    )

label monika_event_clothes_select:
    # setup
    python:
        mailbox = store.mas_selspr.MASSelectableSpriteMailbox(
            "Do you want me to change?"
        )
        # only def and the outfit in question will be available here, so outfit mode only
        mailbox.send_outfit_checkbox_visible(False)
        mailbox.send_outfit_checkbox_checked(True)
        sel_map = {}

        available_clothes = mas_selspr.filter_clothes(True)

        for index in range(len(available_clothes)-1, -1, -1):
            spr_obj = available_clothes[index].get_sprobj()
            if (
                    spr_obj != mas_clothes_def
            ):
                available_clothes.pop(index)

        clothes_to_add = persistent._mas_event_clothes_map.get(datetime.date.today())

        #If there's something for today, then we'll add it to be unlocked
        if clothes_to_add:
            #Get the outfit selector and add it
            available_clothes.append(mas_selspr.get_sel_clothes(
                mas_sprites.get_sprite(
                    mas_sprites.SP_CLOTHES,
                    clothes_to_add
                )
            ))
            available_clothes.sort(key=mas_selspr.selectable_key)

    # initial dialogue
    m 1hua "Sure!"

    call mas_selector_sidebar_select_clothes(available_clothes, mailbox=mailbox, select_map=sel_map)

    # results
    if not _return:
        # user hit cancel
        m 1eka "Oh, alright."

    if store.monika_chr.clothes == store.mas_clothes_def and not store.mas_hasSpecialOutfit():
        $ mas_lockEVL("monika_event_clothes_select", "EVE")

    return

#### ends Monika clothes topic

##### monika hair topics [MONHAIR]

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_hair_select",
            category=["appearance"],
            prompt=store.mas_selspr.get_prompt("hair", "change"),
            pool=True,
            unlocked=False,
            rules={"no_unlock": None}
        ),
        restartBlacklist=True,
        markSeen=True
    )

label monika_hair_select:
    # setup
    python:
        sorted_hair = store.mas_selspr.HAIR_SEL_SL
        mailbox = store.mas_selspr.MASSelectableSpriteMailbox(
            "Which hairstyle would you like me to wear?"
        )
        sel_map = {}

        # process hair
        store.mas_selspr.set_compat_hair(sorted_hair, monika_chr.clothes)

    # initial dialogue
    m 1hua "Sure!"

    # setup the monika expression during the selection screen
    show monika 2eua

    # start the selection screen
    call mas_selector_sidebar_select_hair(sorted_hair, mailbox=mailbox, select_map=sel_map)

    # results
    if not _return:
        # user hit cancel
        m 1eka "Oh, alright."

    return

##### End monika hair topics

#### Monika ribbons topic
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_ribbon_select",
            category=["appearance"],
            prompt=store.mas_selspr.get_prompt("ribbon", "change"),
            pool=True,
            unlocked=False,
            rules={"no_unlock": None},
            aff_range=(mas_aff.NORMAL, None)
        ),
        restartBlacklist=True
    )

    #NOTE: This does not default persistent._seen_ever as True to give the users an idea
    #That these are things which show up under the appearance tab

label monika_ribbon_select:
    python:
        # if we are not using a force ribbon hair, add a remover.
#        use_remover = not monika_chr.is_wearing_hair_with_exprop("force-ribbon")

        use_acs = store.mas_selspr.filter_acs(True, group="ribbon")

        # remove non-compatible acs
        for index in range(len(use_acs)-1, -1, -1):
            if (
                not store.mas_sprites.is_hairacs_compatible(
                    monika_chr.hair,
                    use_acs[index].get_sprobj()
                )
            ):
                use_acs.pop(index)

        # make sure ot use ribbon for remover type
        use_acs.append(store.mas_selspr.create_selectable_remover(
            "ribbon",
            "ribbon",
            "Basic Hair Band"
        ))

        mailbox = store.mas_selspr.MASSelectableSpriteMailbox(
            "Which hair tie would you like me to use?"
        )
        sel_map = {}

    m 1eua "Sure [player]!"

#    if monika_chr.hair.name != mas_hair_def.name:
#        m "But im going to change my clothes and hair back to normal."
#        $ monika_chr.reset_outfit(False)


    call mas_selector_sidebar_select_acs(use_acs, mailbox=mailbox, select_map=sel_map, add_remover=True)

    if not _return:
        m 1eka "Oh, alright."

    $ store.mas_selspr.set_prompt("ribbon", "change")

    return
#### End Ribbon change topic

#### Monika hairclips
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_hairclip_select",
            category=["appearance"],
            prompt=store.mas_selspr.get_prompt("left-hair-clip", "change"),
            pool=True,
            unlocked=False,
            rules={"no_unlock": None},
            aff_range=(mas_aff.HAPPY, None)
        ),
        restartBlacklist=True,
        markSeen=True
    )

label monika_hairclip_select:
    call mas_selector_generic_sidebar_select_acs("left-hair-clip", idle_dlg="Which hairclip would you like me to wear?")
    return


#### End Monika hairclips/strand topics

#### Monika left hair flower
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_hairflower_select",
            category=["appearance"],
            prompt=store.mas_selspr.get_prompt("left-hair-flower", "change"),
            pool=True,
            unlocked=False,
            rules={"no_unlock": None},
            aff_range=(mas_aff.HAPPY, None)
        ),
        restartBlacklist=True,
        markSeen=True
    )

label monika_hairflower_select:
    python:
        use_acs = store.mas_selspr.filter_acs(True, group="left-hair-flower")

        # since left-hair-flower group can have mutpile types, force using
        #   left-hair-flower type for muxing
        use_acs.append(store.mas_selspr.create_selectable_remover(
            "left-hair-flower",
            "left-hair-flower"
        ))

        mailbox = store.mas_selspr.MASSelectableSpriteMailbox(
            "Which flower would you like me to put in my hair?"
        )
        sel_map = {}

    m 1eua "Sure [player]!"

    call mas_selector_sidebar_select_acs(use_acs, mailbox=mailbox, select_map=sel_map, add_remover=True)

    if not _return:
        m 1eka "Oh, alright."

    # set the appropriate prompt and dialogue
    if monika_chr.get_acs_of_type("left-hair-flower"):
        $ store.mas_selspr.set_prompt("left-hair-flower", "change")
    else:
        $ store.mas_selspr.set_prompt("left-hair-flower", "wear")

    return

#### End Monika hairflower

#### Monika choker
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_choker_select",
            category=["appearance"],
            prompt=store.mas_selspr.get_prompt("choker", "change"),
            pool=True,
            unlocked=False,
            rules={"no_unlock": None},
            aff_range=(mas_aff.HAPPY, None)
        ),
        restartBlacklist=True,
        markSeen=True
    )

label monika_choker_select:
    call mas_selector_generic_sidebar_select_acs("choker", idle_exp="monika 6eua")
    return

#### End choker

#### hat

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_hat_select",
            category=["appearance"],
            prompt=store.mas_selspr.get_prompt("hat", "change"),
            pool=True,
            unlocked=False,
            rules={"no_unlock": None},
            aff_range=(mas_aff.HAPPY, None)
        ),
        restartBlacklist=True,
        markSeen=True
    )

label monika_hat_select:
    call mas_selector_generic_sidebar_select_acs("hat")
    return

#### end hat

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_earrings_select",
            category=["appearance"],
            prompt=store.mas_selspr.get_prompt("earrings", "change"),
            pool=True,
            unlocked=False,
            rules={"no_unlock": None},
            aff_range=(mas_aff.HAPPY, None)
        ),
        restartBlacklist=True,
        markSeen=True
    )

label monika_earrings_select:
    call mas_selector_generic_sidebar_select_acs("earrings")
    return

#### end earrings

############### END SELECTOR TOPICS ###########################################
