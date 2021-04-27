
# large rewrite incoming

init -700 python in mas_deco:
    deco_def_db = {}
    # mapping of deco definitions.

    vis_store = {}
    # mapping of deco tags (see deco_db) of all deco objects that were shown
    # key: deco name/tag
    # value: ignored


init -20 python in mas_deco:
    import store

    deco_name_db = {}
    # maps shorthand deco names to actual deco names
    # key: shorthand decoration name
    # value: real decoration name

    deco_db = {}
    # decoration filename DB
    # key: decoration name
    # value: MASDecoration object

    # zorder layers that all deco objects are allowed to be on
    LAYER_FRONT = 5
    LAYER_MID = 6
    LAYER_BACK = 7

    LAYERS = (
        LAYER_FRONT,
        LAYER_MID,
        LAYER_BACK,
    )

    # decoration prefix
    DECO_PREFIX = "mas_deco_"


    def add_deco(s_name, obj):
        """
        Adds deco object to the deco db. Raises an exception if there are
        duplicates. All deco objects get prefixed wtih text to prevent
        collisions with standard sprite objects.

        IN:
            s_name - shorthand name to apply to this deco object
            obj - MASDecoration object to add to the deco db
        """
        if s_name in deco_name_db:
            raise Exception("Deco object '{0}' already exists".format(s_name))

        # we can probably assume that DECO_PREFIX + s_name does not exist
        # in the deco_db at this point.
        new_deco_name = DECO_PREFIX + s_name
        obj.name = new_deco_name

        deco_name_db[s_name] = new_deco_name
        deco_db[new_deco_name] = obj


    def _add_it_deco(obj):
        """
        Adds a MASImageTagDecoration object to the deco db. Raises exceptions
        if a duplicate was found OR if the object is not a
        MASImageTagDecoration.

        IN:
            obj - MASImageTagDecoration object to add to the deco db
        """
        if not isinstance(obj, store.MASImageTagDecoration):
            raise Exception("{0} is not MASImageTagDecoration".format(obj))

        # MASImageTagDecoration objects's names are added directly to the deco
        # db
        if obj.name in deco_db:
            raise Exception("Deco object '{0}' already exists".format(
                obj.name)
            )

        deco_db[obj.name] = obj


    def get_deco(name):
        """
        Gets a deco object by name. This accepts shortname or regular deco name

        IN:
            name - can either be shortname or actual deco name

        RETURNS: MASDecoration object, or None if not valid name
        """
        if not name.startswith(DECO_PREFIX):
            name = deco_name_db.get(name, "")

        if name:
            return deco_db.get(name, None)

        return None


init -19 python:


    class MASDecorationBase(MASExtraPropable):
        """
        Base class for decortaions objects.

        INHERITED PROPS:
            ex_props- arbitrary properties associated with this deco object

        PROPERTIES:
            name - unique identifier of this deco object
        """

        def __init__(self, name, ex_props=None):
            """
            Constructor for base decoration objets

            IN:
                name - unique identifier to use for this deco object
                ex_props - dict of aribtrary properties associated with this
                    deco object.
                    (Default: None)
            """
            self.name = name
            super(MASDecorationBase, self).__init__(ex_props)

        def __eq__(self, other):
            if isinstance(other, MASDecorationBase):
                return self.name == other.name
            return NotImplemented

        def __ne__(self, other):
            result = self.__eq__(other)
            if result is NotImplemented:
                return result
            return not result


    class MASDecoration(MASDecorationBase):
        """
        Decoration object. Does NOT know positioning.

        PROPERTIES:
            name - unique identifier of this deco object
            ex_props - arbitrary properties associated with tihs deco object
        """

        def __init__(self, s_name, img=None, fwm=None, ex_props=None):
            """
            constructor for MASDecoration. this will auto add the
            deco object to the deco_db.

            IN:
                s_name - shortname for this deco object. This should be
                    unique.
                    NOTE: this object's real name will be set to something
                        different. To lookup deco objects,
                        see mas_deco.get_deco.
                img - image filepath associated with this deco object. If None,
                    then we assume fwm is set.
                    (Default: None)
                fwm - MASFilterWeatherMap to use for this deco object. pass
                    None to mark the deco object as a "simple" object that
                    gets the standard filters applied.
                    (Default: None)
                ex_props - dict of arbitrary properties associated with this
                    deco object.
                    (Default: None)
            """
            super(MASDecoration, self).__init__("", ex_props)

            # check for duplicate name
            store.mas_deco.add_deco(s_name, self)

            # img or fwm is required
            if img is None and fwm is None:
                raise Exception(
                    (
                        "Deco object '{0}' does not contain image or "
                        "MASFilterWeatherMap"
                    ).format(s_name)
                )

            self._img = img
            self._fwm = fwm # TODO: verify fwm

            # mark if this is a complex or simple deco object
            # simple deco objects do not have custom filter settings
            self._simple = fwm is None

        def __repr__(self):
            return "<MASDecoration: (name: {0}, img: {1})>".format(
                self.name,
                self.img
            )

        def is_simple(self):
            """
            Returns True if this is a simple deco object.
            Simple Deco objects do not have custom filter settings.

            RETURNS: True if simple deco object, False otherwise
            """
            return self._simple


    class MASImageTagDecoration(MASDecorationBase):
        """
        Variation of MASDecoration meant for images already defined as image
        tags in game.

        PROPERTIES:
            See MASDecorationBase
        """

        def __init__(self, tag, ex_props=None):
            """
            Constructor for MASImageTagDecoration

            IN:
                tag - image tag to build this decoration for. This is also
                    used as the decoration name.
                ex_props - arbitraary props to assocaitd with this deco object
                    (Default: None)
            """
            super(MASImageTagDecoration, self).__init__(tag, ex_props)

            # check for duplicate deco
            store.mas_deco._add_it_deco(self)

        def __repr__(self):
            return "<MASImageTagDecoration: (tag: {0})>".format(self.name)

        @staticmethod
        def create(tag, ex_props=None):
            """
            Creates a MASImageTagDecoration and returns it. Will return an
            existing one if we find one with the same tag.

            IN:
                tag - tag to create MASImageTagDecoration for
                ex_props - passed to the MASImageTagDecoration constructor.
                    NOTE: will be ignored if an existing MASImageTagDecoration
                    exists.
                    (Default: None)

            RETURNS: MASImageTagDecoration to use
            """
            it_deco = store.mas_deco.get_deco(tag)
            if it_deco is not None:
                return it_deco

            return MASImageTagDecoration(tag, ex_props)


    class MASDecoFrame(object):
        """
        Contains position, scale, and rotation info about a decoration

        PROPERTIES:
            priority - integer priority that this deco frame should be shown.
                Smaller numbers are rendered first, and therefore can be hidden
                behind deco frames with higher priorities.
            pos - (x, y) coordinates of the top left of the decoration
            scale - (ws, hs) scale values to apply to the image's width and
                height. This is fed directly to FactorScale.
                    ws - multiplied to the decoration's image's width
                    hs - multiplied to the decoration's images' height
                Both scale values have a precision limit of 2 decimal places
            rotation - radians/degrees to rotate the decoration.
                NOTE: CURRENTLY UNUSED
        """

        def __init__(self, priority, pos, scale, rotation):
            """
            Constructor for a MASDecoFrame

            IN:
                priority - integer priority that this deco frame should be shown.
                pos - initial (x, y) coordinates to show the decoration on
                scale - (ws, hs) scale values to apply to the image's width and
                    height. This is fed directly to FactorScale.
                        ws - multiplied to the decoration's image's width
                        hs - multiplied to the decoration's images' height
                    Both scale values have a precision limit of 2 decimal places
            """
            self.priority = priority
            self.pos = pos
            self.scale = scale
            self.rotation = 0

        def __setattr__(self, name, value):
            """
            Set attr override for MASDecoFrame. This does very specific checks
            for all numerical values to ensure compliance. This is important
            since these are directly responsible for image appearance.
            """
            if name == "pos":
                # ensure position coordinates are integers
                value = (int(value[0]), int(value[1]))

            elif name == "scale":
                # round scale to 2 decimal points, with adjustments for
                # close to integer values.
                ws, hs = value

                if store.mas_utils.eqfloat(abs(ws), ws, 2):
                    ws = abs(ws)
                else:
                    ws = store.mas_utils.truncround(ws, 2)

                if store.mas_utils.eqfloat(abs(hs), hs, 2):
                    hs = abs(hs)
                else:
                    hs = store.mas_utils.truncround(hs, 2)

                value = (ws, hs)

            #elif name == "rotation":
            #    pass

            super(MASDecoFrame, self).__setattr__(name, value)

        def __repr__(self):
            return (
                "<MASDecoFrame: (pty: {0}, pos: {1}, scale: {2}, rot: {3})>"
            ).format(
                self.priority,
                self.pos,
                self.scale,
                self.rotation
            )

        def fromTuple(self, data):
            """
            Loads data from a tuple into this deco frame's propeties.

            IN:
                data - tuplized data of a MASDecoFrame. See toTuple for format

            RETURNS: True if successful, false otherwise
            """
            if len(data) < 5:
                # tuple data has 5 elements
                return False

            # NOTE: setattr will auto handle most of these
            self.pos = data[0]
            self.scale = (
                store.mas_utils.floatcombine_i(data[1], 2),
                store.mas_utils.floatcombine_i(data[2], 2),
            )
            self.rotation = data[3]
            self.priority = data[4]

            return True

        def toTuple(self):
            """
            Creates a tuple of this deco's properties for saving.

            RETURNS: tuple of the following format:
                [0]: position (x, y)
                [1]: width scale (integer, float part as integer)
                [2]: height scale (integer, float part as integer)
                [3]: rotation
                [4]: priority
            """
            return (
                self.pos,
                store.mas_utils.floatsplit_i(self.scale[0], 2),
                store.mas_utils.floatsplit_i(self.scale[1], 2),
                self.rotation,
                self.priority,
            )


    class MASAdvancedDecoFrame(object):
        """
        Advanced deco frame. Basically an interface around
        renpy.show params.

        Equivalence is supported, but only in positionig AND tag.

        PROPERTIES: NOTE: refer to renpy.show for info
            name - set when this is shown
            at_list
            layer
            what
            zorder
            tag - used as the decoration tag in deco db, if given
            behind
            real_tag - tag this image ends up being shown with.
        """

        def __init__(self,
                at_list=None,
                layer="master",
                what=None,
                zorder=0,
                tag=None,
                behind=None
        ):
            """
            Constructor.
            NOTE: all parameter doc is copied from renpy.show

            at_list - list of tranforms applyed to the image
                Equivalent of the `at` property
                (Default: None)
            layer - string, giving name of layer on which image will be shown
                Equivalent of the `onlayer` property
                (Default: None)
            what - if not None, displaybale that will be shown
                Equivalent of `show expression`.
                If provided, name will be the tag for the image
                (Default: None)
            zorder - integer for zorder
                if None, zorder is preserved, otherwise set to 0.
                Equivalent of `zorder` property
                (Default: 0)
            tag - string, used to specify the tag of image
                Equivalent of the `as` property
                (Default: None)
            behind - list of strings, giving image tags that this image is
                shown behind.
                Equivalent of the `behind` property
            """
            if at_list is None:
                at_list = []
            if behind is None:
                behind = []

            self.at_list = at_list
            self.layer = layer
            self.what = what
            self.zorder = zorder
            self.tag = tag
            self.behind = behind
            self.real_tag = None
            self.name = None

        def __eq__(self, other):
            if isinstance(other, MASAdvancedDecoFrame):
                return (
                    self.at_list == other.at_list
                    and self.layer == other.layer
                    and self.what == other.what
                    and self.zorder == other.zorder
                    and self.tag == other.tag
                    and self.behind == other.behind
                )

            return NotImplemented

        def __ne__(self, other):
            result = self.__eq__(other)
            if result is NotImplemented:
                return result
            return not result

        def hide(self):
            """
            Hides this image
            """
            if self.real_tag is not None:
                renpy.hide(self.real_tag, layer=self.layer)
                self.real_tag = None
                self.name = None

        def show(self, name):
            """
            Shows image at this deco frame

            IN:
                name - tag of the image to show
            """
            self.name = name
            if self.name is None:
                return

            # first, determine the tag that will end up being used.
            if self.tag is None:
                self.real_tag = name
            else:
                self.real_tag = self.tag

            renpy.show(
                self.name,
                at_list=self.at_list,
                layer=self.layer,
                what=self.what,
                zorder=self.zorder,
                tag=self.tag,
                behind=self.behind
            )

        def showing(self, layer=None):
            """
            Analogus to renpy.showing

            IN:
                layer - layer to check, if None, uses the default layer for
                    the tag.
                    (Default: None)

            RETURNS: True if this deco frame is showing on the layer, False
                if not
            """
            return self.name is not None and renpy.showing(self.name, layer)


    class MASImageTagDecoDefinition(MASExtraPropable):
        """
        Class that defines bg-based properties for image tags.

        The Primary purpose of these is for auto image management when
        dealing with backgrounds. You can define position position information
        for every image for specific backgrounds (NOTE: this is via
        MASAdvancedDecoFrame)

        Defaults cannot be defined because of the general issues.
        Custom BGs should run the staticmethod register_img to setup
        their custom mapping (or override)

        PROPERTIES:
            deco - MASImageTagDecoration object associated with this definition
            bg_map - mapping of background ids to tuple:
                [0] - tag to use, or None to use the known tag
                [1] - adv deco frame
        """

        def __init__(self, deco):
            """
            Constructor

            IN:
                deco - MASImageTagDefintion object to use
            """
            self.deco = deco
            self.bg_map = {}

            if deco.name in store.mas_deco.deco_def_db:
                raise Exception("duplicate deco definition found")

            store.mas_deco.deco_def_db[deco.name] = self

        @staticmethod
        def get_adf(bg_id, tag):
            """
            Gets MASAdvancedDecoFrame for a bg for a given tag.

            IN:
                bg_id - background ID to get deco frame for
                tag - tag to get deco frame for

            RETURNS: MASAdvancedDecoFrame, or None if not found
            """
            deco_def = store.mas_deco.deco_def_db.get(tag, None)
            if deco_def is None:
                return None

            return deco_def.bg_map.get(bg_id, None)

        def get_img(bg_id):
            """
            Gets the tag and MASAdvancedDecoFrame to use for a bg for this
            definition.

            IN:
                bg_id - background ID to get img info for
                tag - tag to get img info for

            RETURNS: tuple (or None if not found)
                [0] - tag to use
                [1] - MASAdvancedDecoFrame to use
            """
            img_info = self.bg_map.get(bg_id, None)
            if img_info is None:
                return None

            tag, adf = img_info
            if tag is None:
                tag = self.deco.name

            return tag, adf

        @staticmethod
        def get_img_for_bg(bg_id, tag):
            """
            Gets the tag and MASAdvancedDecoFrame to use for a bg for a
            given main tag.

            IN:
                bg_id - backgroud ID to get img info for
                tag - tag to get img info for

            RETURNS: tuple (or None if not found)
                [0] - tag to use 
                [1] - MASAdvancedDecoFrame to use
            """
            deco_def = store.mas_deco.deco_def_db.get(tag, None)
            if deco_def is None:
                return None

            return deco_def.get_img(bg_id)

        @staticmethod
        def get_img_setting(bg_id, tag):
            """
            Gets the tag and MASAdvancedDecoFrame setting to use for a bg for
            a given main tag.
            NOTE: do not use this for render. Use this for getting raw 
            settings.

            IN:
                bg_id - background ID to get img info for
                tag - tag to get img info for

            RETURNS: tuple (or None if not found)
                [0] - tag used in the setting
                [1] - MASAdvancedDecoFrame used in the setting
            """
            deco_def = store.mas_deco.deco_def_db.get(tag, None)
            if deco_def is None:
                return None

            return deco_def.bg_map.get(bg_id, None)

        def register_bg(self, bg_id, adv_deco_frame, replace_tag=None):
            """
            Registers the given MASAdvanecdDecoFrame to this definition for
            a bg id.

            IN:
                bg_id - MASBackgroundID
                adv_deco_frame - MASAdvancedDecoFrame to register
                replace_tag - tag to use instead of the known tag
                    if None, then we use the known tag instead.
                    (Default: None)
            """
            self.bg_map[bg_id] = (replace_tag, adv_deco_frame)

        def register_bg_same(self, bg_id_src, bg_id_dest):
            """
            Register that a bg for this tag should use the same
            MASAdvancedDecoFrame + tag info as another bg.

            IN:
                bg_id_src - bg ID of the background to copy deco frame from
                bg_id_dest - bg ID of the background to use deco frame for
            """
            adf = self.bg_map.get(bg_id_src, None)
            if adf is not None:
                self.bg_map[bg_id_dest] = adf

        @staticmethod
        def register_img(tag, bg_id, adv_deco_frame, replace_tag=None):
            """
            Registers MASAdvancedDecoFrame for a BG and tag.
            Will create a new entry if the tag does not have a definition yet.
            NOTE: this will basically create a dummy MASImageTagDecoration
            object. Use store.mas_deco.get_deco to get the decoration object.

            IN:
                tag - tag to register decoframe for bg
                bg_id - id of teh bg to register decoframe for
                adv_dec_frame - the decoframe to register
                replace_tag - tag to use instead of the known tag for this bg
                    if None, then we use the known tag instead.
                    (Default: None)
            """
            deco_def = store.mas_deco.deco_def_db.get(tag, None)
            if deco_def is None:
                deco_def = MASImageTagDecoDefinition(
                    MASImageTagDecoration(tag)
                )

            deco_def.register_bg(bg_id, adv_deco_frame, replace_tag=replace_tag)

        @staticmethod
        def register_img_same(tag, bg_id_src, bg_id_dest):
            """
            Registers that a bg for a tag should use the same
            MASAdvancedDecoFRame + tag info as another bg for that tag.
            Will create a new entry if the tag does not have a definition yet.

            IN:
                tag - tag to register decoframe for
                bg_id_src - bg ID of the background to copy deco frame from
                bg_id_dest - bg ID of the background to use deco frame for
            """
            img_info = MASImageTagDecoDefinition.get_img_setting(
                bg_id_src,
                tag
            )
            if img_info is not None:
                replace_tag, adf = img_info
                MASImageTagDecoDefinition.register_img(
                    tag,
                    bg_id_dest,
                    adf,
                    replace_tag=replace_tag
                )


    class MASDecoManager(object):
        """
        Decoration manager for a background.
        Manages decoration objects and their assocation with layers.

        GETTING:
            This supports getting via bracket notation []
            If a tag does not exist, None is returned.

        PROPERTIES:
            changed - set when the decorations have changed and spaceroom
                will need to show new things. (should be set by callers)
        """

        def __init__(self):
            """
            Constructor
            """
            self._decos = {}
            # db for non advanced decos
            # key: deco tag
            # value: MASDecoration object

            self._adv_decos = {}
            # db for decos that were added using the AdvancedDecoFrames.
            # key: deco tag
            # value: MASDecoration object

            self._deco_layer_map = {}
            # key: deco tag
            # value: layer code

            self._deco_frame_map = {}
            # key: deco tag
            # value: MASDecoFrame (adv deco frame) for that tag

            self._deco_render_map = {
                store.mas_deco.LAYER_BACK: [],
                store.mas_deco.LAYER_MID: [],
                store.mas_deco.LAYER_FRONT: [],
            }
            # key: layer code
            # value: list of MASDecoration objects, in priority order

            self.changed = False

        def __getitem__(self, item):
            if item in self._adv_decos:
                return self._adv_decos[item]

            if item in self._decos:
                return self._decos[item]

            return None

        def _add_deco(self, layer, deco_obj, deco_frame):
            """
            Adds a decoration object to the deco manager.
            NOTE: if decoration has already been added, the existing decoration
            object is instead updated to the given layer and decoframe.

            NOTE: this should only be used for non-advanced decos

            IN:
                layer - layer to add deco object to
                deco_obj - MASDecoration object to add
                deco_frame - MASDecoFrame to associated with deco object
            """
            if deco_obj.name in self._decos:
                # if the deco object already exists, remove from the
                # decorender map
                old_layer = self._deco_layer_map,get(deco_obj.name, None)
                if old_layer is not None:
                    decos = self._deco_render_map.get(old_layer, [])
                    if deco_obj in decos:
                        decos.remove(deco_obj)

            # TODO:
            #   1 - need to decide if multiple instances should be allowed
            #   2 - it would really be same deco but associated with different
            #       deco frame.
            #   3 - update all other dec db information
            #   4 - set changed

        def _adv_add_deco(self, deco_obj, adv_deco_frame):
            """
            Adds a decoration object to teh deco manager.
            This is meant for Advanced DecoFrames

            IN:
                deco_obj - MASDecoration object to add
                adv_deco_frame - MASAdvancedDecoFRame to associate with deco
                    object.
            """
            # TODO - update for deco tag replace
            self._adv_decos[deco_obj.name] = deco_obj
            self._deco_frame_map[deco_obj.name] = adv_deco_frame

        def add_back(self, deco_obj, deco_frame):
            """
            Adds a decoration object to the back deco layer
            """
            # TODO: complete for room deco
            #   should just call _add_deco

        def add_front(self, deco_obj, deco_frame):
            """
            Adds a decoration object to the front deco layer
            """
            # TODO: complete for room deco
            #   shoudl just call _add_deco

        def add_mid(self, deco_obj, deco_frame):
            """
            Adds a decoration object to the middle deco layer
            """
            # TODO: complete for room deco
            #   should just call _add_deco

        def deco_iter(self):
            """
            Generator that yields deco objects and their frames

            TODO: probably should return more than this

            YIELDS: tuple contianing deco object and frame
            """
            # TODO: complete for room deco

        def deco_iter_adv(self):
            """
            Generates iter of advanced deco objects and their frames

            RETURNS: iter of tuple containing deco object and adv deco frame
            """
            for deco_name, deco_obj in self._adv_decos:
                yield deco_obj, self._deco_frame_map[deco_name]

        def diff_deco_adv(self, deco, adv_df):
            """
            Checks diffs between the given deco + frame and the the same deco
            in this manager.

            IN:
                deco - deco to check
                adv_df - MASAdvancedDecoFrame to check

            RETURNS: integer code:
                0 - the given deco and equivalent frame exist in this
                    deco manager.
                1 - the given deco exists but has a different frame in this
                    deco manager.
                -1 - the given deco does NOT exist in this deco manager.
            """
            df = self._deco_frame_map.get(deco.name, None)
            if df is None:
                return -1

            if df == adv_df:
                return 0

            return 1

        def rm_deco(self, name):
            """
            REmoves all instances of the deco with the given name from this
            deco manager.

            IN:
                name - tag, either deco name or image tag, of the deco object
                    to remove
            """
            deco_obj = None
            if name in self._decos:
                deco_obj = self._decos.pop(name)

            if name in self._adv_decos:
                deco_obj = self._adv_decos.pop(name)

            if name in self._deco_frame_map:
                self._deco_frame_map.pop(name)

            deco_lst = self._deco_render_map.get(
                self._deco_layer_map.get(name, None),
                []
            )
            if deco_obj in deco_lst:
                deco_lst.remove(deco_obj)


    ## key functions
    def mas_showDecoTag(tag, show_now=False):
        """
        Shows a decoration object that is an image tag.

        NOTE: this should be called when you want to show a decoration-based
        image, regardless of background. This will refer to the image tag
        definition to determine how the object will be shown.

        To hide an image shown this way, see mas_hideDecoTag.

        IN:
            tag - the image tag to show
            show_now - set to True to show immediately
                (Deafult: False)
        """
        store.mas_deco.vis_store[tag] = None
        mas_current_background._deco_add(tag=tag)

        if show_now:
            adf = mas_current_background.get_deco_adf(tag)
            if adf is not None:
                adf.show(tag)
        else:
            mas_current_background._deco_man.changed = True


    def mas_hideDecoTag(tag, hide_now=False):
        """
        Hides a decoration object that is an image tag

        NOTE: this should be called when you want to hide a decoration-based
        image, regardless of background.

        This is primarily for hiding images shown with the mas_showDecoTag
        function.

        IN:
            tag - the image tag to hide
            hide_now - set to True to hide immediately
                (Default: False)
        """
        if tag in store.mas_deco.vis_store:
            store.mas_deco.vis_store.pop(tag)

        if hide_now:
            adf = mas_current_background.get_deco_adf(tag)
            if adf is not None:
                adf.hide()
        else:
            mas_current_background._deco_man.changed = True


    def mas_isDecoTagVisible(tag):
        """
        Checks if the given deco tag is still visible. (as in the vis_store)

        IN:
            tag - the image tag to check

        RETURNS: True if the deco is still visible, false if not
        """
        return tag in store.mas_deco.vis_store


# TODO: complete with real room deco
#
#    class MASSelectableDecoration(store.MASSelectableSprite):
#        def __init__(self,
#                    decoration,
#                    display_name,
#                    thumb,
#                    group,
#                    visible_when_locked=True,
#                    hover_dlg=None,
#                    first_select_dlg=None,
#                    select_dlg=None,
#                    unlocked = True):
#            """
#            IN:
#                decoration - MASDecoration object
#
#                display_name - name to show on the selectable screen
#                thumb - thumbnail to use on the select screen
#                group - group id to group related selectable sprites.
#                visible_when_locked - True if this item should be visible in
#                    the screen when locked, False otherwise
#                    (Default: True)
#                hover_dlg - list of text to display when hovering over the
#                    object
#                    (Default: None)
#                first_select_dlg - text to display the first time you select
#                    this sprite
#                    (Default: None)
#                select_dlg - list of text to display everytime you select this
#                    sprite
#                    (after the first time)
#                    (Default: None)
#            """
#
#            #Imports
#            import store
#
#
#            #Init
#            self._sprite_object = decoration
#            store.MASSelectableSprite.__init__(self, self._sprite_object, display_name, thumb, group, visible_when_locked, hover_dlg, first_select_dlg, select_dlg)
#
#
#            #Set basic normal properties
#            self.ex_props = self._sprite_object.ex_props
#            self.name = self._sprite_object.name
#            self.img_sit = self._sprite_object.img_sit
#            self.unlocked = unlocked
#
#            #Comp setup
#
#            #Checks it there are any sub_objects in the posemap, this var will determine if sub_objects are ever added
#            if len(self._sprite_object.sub_objects) > 0:
#                self.sub_objects_present = True
#            else:
#                self.sub_objects_present = False
#
#            self.size = store.mas_sprites.LOC_WH
#            self.loc = (0,0)
#            self.l_comp_str = store.mas_sprites.L_COMP
#            self.init_str = "{0}({1}".format(self.l_comp_str, self.size)
#            self.sprite_str_list = [self.init_str]
#            self.sub_object_str = store.mas_decorations.sub_object_str
#            self.full_composite_str = store.mas_decorations.full_composite_str
#            self.composite_map = {}
#
#            #IO Setup
#            self.path = self._sprite_object.dir
#            self.file_ext_str = self._sprite_object.FILE_EXT
#
#            #Weather_map setup
#            self.weather_map = self._sprite_object.weather_map
#            self.weather_map["def"] =  {}
#
#            self.same_map_str = store.mas_decorations.same_map_str
#
#
#
#
#            #Final setup, creates keys and values for composite_map
#            self.def_str = "def"
#            self.times = store.mas_decorations.times_dict
#
#            if self.sub_objects_present:
#                self.sub_objects = self._sprite_object.sub_objects
#                self.composite_init("sub", self.times)
#
#            self.composite_init("full", self.times)
#
#
#        def get_comp_value(self, mode, weather, times, time_of_day):
#            """
#            Generates value which will be assigned to a composition key in the composite_map
#
#            IN:
#                mode - Specifies are we going for a sub_objects or full composite
#                weather - weahter key from weather_map
#                times - dictionary of suffix's for differnet times
#                time_of_day - key from times
#
#            RETURNS: LiveComposite
#            """
#
#            if mode == "sub":
#                value  = self.sub_object_composite(sub_objects = self.sub_objects, weather = weather, night_suffix = times[time_of_day])
#            elif mode == "full":
#                sub_objects = self.composite_map.get('{0}_{1}_{2}'.format(self.sub_object_str, weather, time_of_day))
#                value  = self.full_composite(sub_objects = sub_objects, weather = weather, night_suffix = times[time_of_day])
#            return value
#
#        def get_same_comp_value(self, comp_key_str, weather, time_of_day):
#            """
#            Get values from composite_map to assign to other weathers in the composite_map
#
#            IN:
#                comp_key_str - Major stirng used as a base to build the composite_map key
#                weather - weather key from weather_map
#                time_of_day - key from times
#
#            RETURNS: LiveComposite
#            """
#
#            value = self.composite_map.get("{0}_{1}_{2}".format(comp_key_str, weather, time_of_day))
#            return value
#
#        def composite_init(self, mode, times):
#            """
#            IN:
#                mode - Specifies are we going for sub_objects or full composite
#                times - dictionary of suffix's for differnet times
#
#            """
#
#            #Sets comp_key_str based on mode
#            if mode == "sub":
#                comp_key_str = self.sub_object_str
#            elif mode == "full":
#                comp_key_str = self.full_composite_str
#
#            #Iterates weather_map
#            for key in self.weather_map.keys():
#
#                #ignore same_map until the end once everything else is defined
#                if key == self.same_map_str:
#                    pass
#
#                #Interates through times and sets composite_map entries
#                else:
#                    for time_of_day in times.keys():
#
#                        #Check if ignore_night or ignore_night are true and use def values instead
#                        if self.weather_map[key].get("ignore_night") == True and time_of_day == "night":
#                            value = self.get_same_comp_value(comp_key_str, self.def_str, time_of_day)
#
#                        elif self.weather_map[key].get("ignore_day") == True and time_of_day == "day":
#                            value = self.get_same_comp_value(comp_key_str, self.def_str, time_of_day)
#
#                        #Else just get value normal for the differnt weather
#                        else:
#                            value = self.get_comp_value(mode, key, times, time_of_day)
#
#                        #Finnaly Sets the composite_map key/value
#                        self.composite_map["{0}_{1}_{2}".format(comp_key_str, key, time_of_day)] = value
#
#            #Handles same_map values
#
#            #Checks if the same_map key exists
#            if self.same_map_str in self.weather_map.keys():
#
#                #Init vars
#                same_dict = self.weather_map[self.same_map_str]
#                same_keys = same_dict.keys()
#
#                #Iterates through weathers whose value will be used for other weathers
#                for same_key in same_keys:
#
#                    #Iterates through same_map what weathers will equal the same_map key
#                    for same_weather in same_dict[same_key]:
#                        for time_of_day in times.keys():
#
#                            #Gets value and sets composite_map
#                            value = self.get_same_comp_value(comp_key_str, same_key, time_of_day)
#                            self.composite_map["{0}_{1}_{2}".format(comp_key_str, same_weather, time_of_day)] = value
#            return
#
#
#        def sub_object_composite(self, sub_objects, weather = "def", night_suffix = ""):
#            """
#            IN:
#                sub_objects - dictionary of addional objs that should be added to the composite
#                weather - string for weather of the current composite img
#                night_suffix - string for time of dat of the current composite img
#
#            RETURNS: LiveComposite
#            """
#            #Init vars
#            keys = sub_objects.keys()
#            sprite_str_list = [self.init_str]
#
#            #Iterates through the len() of sub_objects
#            for i in range(len(sub_objects)):
#                sprite_str_list.append(',{0},"{1}{2}{3}{4}{5}{6}"'.format(self.loc, self.path, sub_objects[keys[i]], mas_sprites.ART_DLM, weather, night_suffix, self.file_ext_str))
#            sprite_str_list.append(")")
#            result_sub_objects = "".join(sprite_str_list)
#            return eval(result_sub_objects)
#
#        def full_composite(self, sub_objects, weather = "def", night_suffix = ""):
#            """
#            IN:
#                sub_objects - LiveCompsite of desired sub_objects to be added to full comp_key_str
#                weather - string for weather of main full composite img
#                night_suffix - string for time of dat of the current composite img
#            RETURNS: LiveComposite
#            """
#            #Init Vars
#            sprite_str_list = [self.init_str]
#
#
#            if sub_objects:
#               full_composite = renpy.display.layout.LiveComposite(self.size, self.loc, '{}{}{}{}{}{}'.format(self.path, self.img_sit, mas_sprites.ART_DLM, weather, night_suffix, self.file_ext_str), self.loc, sub_objects)
#            else:
#               full_composite = renpy.display.layout.LiveComposite(self.size, self.loc, '{}{}{}{}{}{}'.format(self.path, self.img_sit, mas_sprites.ART_DLM, weather, night_suffix, self.file_ext_str))
#
#            return full_composite
#
#
#
#
#
#
#    class MASSelectableImageButtonDisplayable_Decoration(store.MASSelectableImageButtonDisplayable):
#        """
#        Modified version of the MASSelectableImageButtonDisplayable class that allows for multi select and direct asigment of variables when object is selected
#        """
#
#        def __init__(self,
#            _selectable,
#            select_map,
#            viewport_bounds,
#            mailbox=None,
#            multi_select=False,
#            disable_type=store.mas_selspr.DISB_NONE
#            ):
#            """
#            Constructor for this displayable
#
#            IN:
#                selectable - the selectable object we want to encapsulate
#                select_map - dict containing group keys of previously selected
#                    objects.
#                viewport_bounds - tuple of the following format:
#                    [0]: xpos of the viewport upper left
#                    [1]: ypos of the viewport upper left
#                    [2]: width of the viewport
#                    [3]: height of the viewport
#                    [4]: border size
#                mailbox - dict to send messages to outside from this
#                    displayable.
#                    (Default: None)
#                multi_select - True means we can select more than one item.
#                    False otherwise
#                    (Default: False)
#                disable_type - pass in a disable constant to disable this item
#                    for the specified reason.
#                    (Default: 0 - DISB_NONE)
#            """
#
#            store.MASSelectableImageButtonDisplayable.__init__(self, _selectable, select_map, viewport_bounds, mailbox, multi_select, disable_type)
#            if store.persistent.mas_decorations_items.get(self.selectable.name) is not None:
#                self.selected = store.persistent.mas_decorations_items.get(self.selectable.name)["selected"]
#
#        def _select(self):
#            """
#            Makes this item a selected item. Also handles other logic realted
#            to selecting this.
#            """
#
#            # if already selected, then we need to deselect.
#            if self.selected:
#                self.selected = False
#                self.selectable.selected = False
#                #Sets persistent so decoration will remain when we come back to it
#                store.persistent.mas_decorations_items[self.selectable.name]["selected"] = self.selectable.selected
#                for key in store.persistent.mas_decorations_items.keys():
#                 if drag_dict.get(key) is not None:
#                #Sets persistent position about this decoration so it stays in the same spot
#                    store.mas_decorations_items_tmp_pos[x]["pos"] = store.drag_dict[x].x, store.drag_dict[x].y
#
#            else:
#                self.selected = True
#                self.selectable.selected = True
#                self.select_map[self.selectable.name] = self
#                #Sets persistent so decoration will go away
#                store.persistent.mas_decorations_items[self.selectable.name]["selected"] = self.selectable.selected
#
#
#            # the appropriate dialogue
#            if self.been_selected:
#                if self.selectable.select_dlg is not None:
#                    # this should be first as it allows us to override
#                    # remover dialogue
#                    self._send_select_text()
#
#                elif self.selectable.remover:
#                    self.mailbox.send_disp_fast()
#
#                else:
#                    self._send_generic_select_text()
#
#            else:
#                # not been selected before
#                self.been_selected = True
#                if self.selectable.first_select_dlg is not None:
#                    self._send_first_select_text()
#
#                elif self.selectable.select_dlg is not None:
#                    self._send_select_text()
#
#                elif self.selectable.remover:
#                    self._send_msg_disp_text(None)
#                    self.mailbox.send_disp_fast()
#
#                else:
#                    self._send_generic_select_text()
#            renpy.play(gui.activate_sound, channel="sound")
#            renpy.redraw(self, 0)
#            self.end_interaction = True
#            return
#
#
#init 100 python:
#    #adds extra layer so stuff can behind monika but for some reason you actually gotta use master
#    config.layers = ['background', 'master', 'transient', 'screens', 'overlay' ]
#
#    #generates defualt list decoration objects
#    import store
#    from collections import OrderedDict
#    store.drag_dict = OrderedDict()
#
#
#init -1 python in mas_decorations:
#    #Imports
#    import store
#    from collections import OrderedDict
#
#    #Init Vars
#    DECORATION_SEL_MAP = OrderedDict()
#    DECORATION_SEL_SL = []
#    DECORATION_DIR = "mod_assets/location/spaceroom/decoration/"
#    json_iteration = 0
#    default_visibility = False
#    sub_object_str = "sub_object_img"
#    full_composite_str = "full_composite_img"
#
#    same_map_str = "same_map"
#    times_dict = {"day" : "", "night" : store.mas_sprites.NIGHT_SUFFIX}
#
#
#    def create_MASSelectable_object_from_json(sel_params):
#        """
#        Creates MASSelectableDecoration objects
#
#        IN:
#            sel_params -
#        RETURNS:
#        """
#        new_sel_type = store.MASSelectableDecoration(**sel_params)
#
#        store.mas_decorations.DECORATION_SEL_MAP[sel_params.get("decoration").name] = new_sel_type
#        store.mas_decorations.DECORATION_SEL_SL.insert(store.mas_decorations.json_iteration, new_sel_type)
#        store.mas_decorations.json_iteration +=1
#        return new_sel_type
#
#
#    def get_weather_suffix():
#        """ Gets the suffix to add to make the composition key
#
#            RETURNS: full weather suffix & the time suffix strings
#        """
#
#        mas_weather_suffix = [store.mas_current_weather.weather_id]
#        if store.morning_flag:
#            time_suffix = "_day"
#            mas_weather_suffix.append(time_suffix)
#        else:
#            time_suffix = "_night"
#            mas_weather_suffix.append(time_suffix)
#        mas_weather_suffix = "".join(mas_weather_suffix)
#        return mas_weather_suffix, time_suffix
#
#    def full_comp_exists(items, current_key, mas_weather_suffix):
#        """
#        Verifies the composite key exists
#
#        IN :
#            items - current dictionary of items to get() from
#            current_key - key of current MASSelectableDecoration object
#            mas_weather_suffix - suffix to add to regular key to get proper time and weather key
#
#        RETURNS: True/False
#        """
#        return items[current_key].composite_map.get('full_composite_img_{}'.format(mas_weather_suffix))
#
#    def get_full_comp_str(drag_loc_str, current_key, mas_weather_suffix):
#        """
#        IN:
#            drag_loc_str - location str for LiveComposite
#            current_key - key of current MASSelectableDecoration object
#            mas_weather_suffix - suffix to add to regular key to get proper time and weather key
#
#        RETURNS: string to be used in genrateding composite
#        """
#        return ', {}, items["{}"].composite_map["full_composite_img_{}"]'.format(drag_loc_str, current_key, mas_weather_suffix)
#
#
#    def decoration_composite(st,at):
#        """
#        IN:
#            st, at - Stuff required for DynamicDisplayable
#        RETURN LiveComposite
#        """
#
#        size = (1280,720)
#        l_comp_str = "renpy.display.layout.LiveComposite("
#        init = "{}{}".format(l_comp_str, size)
#        path = '"mod_assets/location/spaceroom/decoration/'
#        sprite_str_list = [init]
#        items = DECORATION_SEL_MAP
#        keys = items.keys()
#        persistent_data = store.persistent.mas_decorations_items
#
#        #Checks if decoration was selected when in drag mode
#        for x in range(len(items)):
#            current_key = keys[x]
#            current_item = items[current_key]
#            drag_loc_str = persistent_data[current_key]["pos"]
#
#            #Checks if the comp we are about to access actually exists
#            if persistent_data[current_key]["selected"] == True:
#                mas_weather_suffix, time = get_weather_suffix()
#                if full_comp_exists(items, current_key, mas_weather_suffix) is not None:
#                    sprite_str_list.append(get_full_comp_str(drag_loc_str, current_key, mas_weather_suffix))
#                else:
#                    sprite_str_list.append(get_full_comp_str(drag_loc_str, current_key, "def{}".format(time)))
#
#        sprite_str_list.append(")")
#
#        result_decoration = "".join(sprite_str_list)
#        return eval(result_decoration), None
#
#
#
#
#    def reload_decorations():
#        """Deletes and reloads decorations"""
#        DECORATION_SEL_SL = []
#        DECORATION_SEL_MAP = {}
#        mas_sprites_json.addSpriteObjects()
#
#
#
#    def save_persistent_drag_pos():
#        """
#        Takes postion of decoration as a drag and sets it in persistent
#        """
#        #Init Vars
#        items = store.persistent.mas_decorations_items
#        keys = items.keys()
#        drag_dict = store.drag_dict
#
#        for x in range(len(items)):
#            current_key = keys[x]
#            current_item = drag_dict[current_key]
#            if drag_dict.get(current_key) is not None:
#                x_pos = drag_dict.get(current_key).x
#                y_pos = drag_dict.get(current_key).y
#                drag_loc_str = (x_pos, y_pos)
#            else:
#                drag_loc_str = (0,0)
#            items[current_key]["pos"] = drag_loc_str
#
#
#    def add_drags(drag_dict, draggroup):
#        """
#        IN:
#            drag_dict - dictonary of drags to add to dragroup form
#            draggroup - draggroup to add drags to
#        """
#
#        #Init Vars
#        keys = drag_dict.keys()
#        create_drag_dict(store.mas_decorations_items_tmp_pos)
#
#        for i in range(len(drag_dict)):
#            current_key = keys[i]
#            current_item = drag_dict[current_key]
#
#            #if decoration in persistent and is "selected" or active added it
#            if store.persistent.mas_decorations_items.get(current_item.drag_name)["selected"] == True:
#                draggroup.add(current_item)
#            else:
#                pass
#        return
#
#
#    def decoration_drags(**kwargs):
#        """
#
#        """
#        DG = ui.draggroup()
#        add_drags(store.drag_dict, DG)
#        ui.close()
#        return
#
#    renpy.define_screen("decoration_drags", decoration_drags, zorder = "5")
#
#
#
#    def create_drag_dict(dec_data = store.persistent.mas_decorations_items):
#        """
#        Creates a drag dictionary based off of saved data
#
#        IN:
#            dec_data - decoration data used to build the drag dictionary
#        """
#
#        #Init Vars
#        Drag = renpy.display.dragdrop.Drag
#        items = DECORATION_SEL_MAP
#        keys = items.keys()
#
#        for x in range(len(DECORATION_SEL_MAP)):
#            current_key = keys[x]
#            current_item = items[current_key]
#            mas_weather_suffix, time = get_weather_suffix()
#
#            if full_comp_exists(items, current_key, mas_weather_suffix) is not None:
#                value = current_item.composite_map["full_composite_img_{}".format(mas_weather_suffix)]
#            else:
#                value = current_item.composite_map["full_composite_img_{}".format("def{}".format(time))]
#
#            store.drag_dict[current_item.name] = Drag(drag_name = current_item.name, d = value, drag_offscreen = True, draggable = True, xpos = dec_data[current_key]["pos"][0], ypos = dec_data[current_key]["pos"][1])
#        return
#
#
#
#
#image decoration = DynamicDisplayable(store.mas_decorations.decoration_composite)
#
#
#
#
#### Start lables and actual menu items
#init 5 python:
#    """Init to add decoration selector list to apperance game menu"""
#    store.mas_selspr.PROMPT_MAP["decoration"] = {"_ev": "monika_decoration_select", "change": "Can you change your decoration?",}
#
#    addEvent(
#        Event(
#            persistent.event_database,
#            eventlabel="monika_decoration_select",
#            category=["appearance"],
#            prompt=store.mas_selspr.get_prompt("decoration", "change"),
#            pool=True,
#            unlocked=True,
#            aff_range=(mas_aff.HAPPY, None)
#        ),
#        restartBlacklist=True
#    )
#
#
#label monika_decoration_select:
#    #Creates the decoration objects and calls the selector with decoration list made at run_init
#    call mas_selector_sidebar_select_decoration(store.mas_decorations.DECORATION_SEL_SL)
#    return
#
#label mas_selector_sidebar_select_decoration(items, preview_selections=True, only_unlocked=True, save_on_confirm=True, mailbox=None, select_map={}):
#    python:
#
#        renpy.hide("decoration")
#        store.mas_decorations.create_drag_dict()
#        renpy.show_screen("decoration_drags", _layer = "master")
#
#
#        store.mas_decorations_items_backup = store.persistent.mas_decorations_items.copy()
#        store.mas_decorations_items_tmp_pos = {}
#
#        for x in store.persistent.mas_decorations_items.keys():
#            store.mas_decorations_items_tmp_pos[x] = {}
#            store.mas_decorations_items_tmp_pos[x]["pos"] = store.persistent.mas_decorations_items[x]["pos"]
#
#
#    call mas_selector_sidebar_select_decoration_main(items, 3, preview_selections, only_unlocked, save_on_confirm, mailbox, select_map)
#
#    python:
#        if _return == True:
#            store.mas_decorations.save_persistent_drag_pos()
#        renpy.hide_screen("decoration_drags", layer = "master")
#        renpy.show("decoration", zorder = 5)
#
#    return _return
#
#
#
#label mas_selector_sidebar_select_decoration_main(items, select_type, preview_selections=True, only_unlocked=True, save_on_confirm=True, mailbox=None, select_map={}):
#
#    python:
#        # setup the mailbox
#        if mailbox is None:
#            mailbox = store.mas_selspr.MASSelectableSpriteMailbox()
#
#        viewport_bounds = (
#            store.mas_selspr.SB_VIEWPORT_BOUNDS_X,
#            store.mas_selspr.SB_VIEWPORT_BOUNDS_Y,
#            store.mas_selspr.SB_VIEWPORT_BOUNDS_W,
#            mailbox.read_frame_vsize(),
#            store.mas_selspr.SB_VIEWPORT_BOUNDS_BS
#        )
#
#    # sanity check to avoid crashes
#    if len(items) < 1:
#        return False
#
#    python:
#
#        # only show unlock
#        if only_unlocked:
#            disp_items = [
#                MASSelectableImageButtonDisplayable_Decoration(
#                    item,
#                    select_map,
#                    viewport_bounds,
#                    mailbox,
#                    False, # TODO: multi-select
#                    item.disable_type
#                )
#                for item in items
#                if item.unlocked
#            ]
#
#        else:
#            disp_items = [
#                MASSelectableImageButtonDisplayable_Decoration(
#                    item,
#                    select_map,
#                    viewport_bounds,
#                    mailbox,
#                    False, # TODO: multi-select
#                    item.disable_type
#                )
#                for item in items
#            ]
#
#        # disable menu interactions to prevent bugs
#        disable_esc()
#
#        # store current auto forward mode state
#        afm_state = _preferences.afm_enable
#
#        # and disable it
#        _preferences.afm_enable = False
#
#        # setup prev line
#        prev_line = ""
#
#    show screen mas_selector_sidebar_decoration(disp_items, mailbox, "mas_selector_sidebar_select_confirm_decoration", "mas_selector_sidebar_select_cancel_decoration", "mas_selector_sidebar_select_restore_decoration")
#
#
#label mas_selector_sidebar_select_midloop_decoration:
#
#    python:
#
#        mailbox.send_conf_enable(True)
#        mailbox.send_restore_enable(True)
#
#        # display text parsing
#        disp_text = mailbox.get_disp_text()
#        disp_fast = mailbox.get_disp_fast()
#
#        if disp_text is None:
#            disp_text = mailbox.read_def_disp_text()
#
#        if disp_fast:
#            disp_text += "{fast}"
#
#        # force this to execute in this python block (no prediction)
#        renpy.say(m, disp_text)
#
#        #Clear repeated lines
#        if prev_line != disp_text:
#            _history_list.pop()
#            #Using this to clear relevant entries from history
#            prev_line = disp_text
#
#label mas_selector_sidebar_select_restore_decoration:
#
#    python:
#        #Clear repeated lines
#        if prev_line != disp_text:
#            _history_list.pop()
#            #Using this to clear relevant entries from history
#            prev_line = disp_text
#
#        # make next display fast
#        mailbox.send_disp_fast()
#        store.mas_decorations.create_drag_dict(store.mas_decorations_items_backup)
#    # jump back to mid loop
#
#    jump mas_selector_sidebar_select_midloop_decoration
#
#label mas_selector_sidebar_select_confirm_decoration:
#    hide screen mas_selector_sidebar_decoration
#    python:
#        # re-enable the menu and restore afm
#        _preferences.afm_enable = afm_state
#        enable_esc()
#        renpy.save_persistent()
#
#    return True
#
#label mas_selector_sidebar_select_cancel_decoration:
#    hide screen mas_selector_sidebar_decoration
#    python:
#        # re-enable the menu and restore afm
#        _preferences.afm_enable = afm_state
#        enable_esc()
#        store.mas_decorations.create_drag_dict(store.mas_decorations_items_backup)
#    return False
#
#screen mas_selector_sidebar_decoration(items, mailbox, confirm, cancel, restore):
#    zorder 50
##    modal True
#
#    $ sel_frame_vsize = mailbox.read_frame_vsize()
#
#    frame:
#        area (1075, 5, 200, sel_frame_vsize)
#        background Frame(store.mas_ui.sel_sb_frame, left=6, top=6, tile=True)
#
#        vbox:
#            xsize 200
#            xalign 0.5
#            viewport id "sidebar_scroll":
#                mousewheel True
#                arrowkeys True
#
#                vbox:
#                    xsize 200
#                    spacing 10
#                    null height 1
#
#                    for selectable in items:
#                        add selectable:
##                            xoffset 5
#                            xalign 0.5
#
#                    null height 1
#
#            null height 10
#
#            if mailbox.read_outfit_checkbox_visible():
#                $ ocb_checked = mailbox.read_outfit_checkbox_checked()
#                textbutton _("Outfit Mode"):
#                    style mas_ui.st_cbx_style
#                    activate_sound gui.activate_sound
#                    action [
#                        ToggleField(persistent, "_mas_setting_ocb"),
#                        Function(
#                            mailbox.send_outfit_checkbox_checked,
#                            not ocb_checked
#                        )
#                    ]
#                    selected ocb_checked
#
#            if mailbox.read_conf_enable():
#                textbutton _("Confirm"):
#                    style store.mas_ui.hkb_button_style
#                    xalign 0.5
#                    action Jump(confirm)
#            else:
#                frame:
#                    ypadding 5
#                    xsize 120
#                    xalign 0.5
#
#                    background Image(store.mas_ui.hkb_disabled_bg)
#                    text "Confirm" style store.mas_ui.hkb_text_style
#
#            if mailbox.read_restore_enable():
#                textbutton _("Restore"):
#                    style store.mas_ui.hkb_button_style
#                    xalign 0.5
#                    action Jump(restore)
#
#            else:
#                frame:
#                    ypadding 5
#                    xsize 120
#                    xalign 0.5
#
#                    background Image(store.mas_ui.hkb_disabled_bg)
#                    text "Restore" style store.mas_ui.hkb_text_style
#
#            textbutton _("Cancel"):
#                style store.mas_ui.hkb_button_style
#                xalign 0.5
#                action Jump(cancel)
##                action Function(mailbox.mas_send_return, -1)
#
#        vbar value YScrollValue("sidebar_scroll"):
#            style "mas_selector_sidebar_vbar"
#            xoffset -25
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
