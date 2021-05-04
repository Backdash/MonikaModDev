# Module for turning json formats into sprite objects
# NOTE: This DEPENDS on sprite-chart.rpy and sprite-chart-matrix.rpy
#
# NOTE: all JSON formats do NOT have prog points. This is a security thing.
#   prog points will be assumed using the type of sprite object and name.
#
# Shared JSON props:
# {
#   "type": integer type of sprite object this is,
#       - REQUIRED
#       - integer
#       - see the json store below for constants
#   "name": "id"
#       - REQUIRED
#       - id for this sprite object. Must be unqiue for the type of object.
#       - This is also referred to in prog points.
#   "img_sit": "base filename for sitting image",
#       - REQUIRED
#       - do not include extension
#   "pose_map": {Pose Map object},
#       - REQUIRED
#       - this is used differently based on object. For more info, see the
#           PoseMap JSON below.
#   "stay_on_start": True if this sprite object should be saved for startup
#       - optional
#       - boolean
#       - default False
#   "ex_props": {arbitrary properties}
#       - optional
#       - additional properties to apply to this sprite object. used for
#            a variety of things. This will be more publicly documented
#           in the future.
#       - NOTE: arbitrary properties can only exist 1 level. (aka no
#           collections as values of these props)
#       - keys should be strings.
#       - acceptable values are int/string/bool.
#       - default empty dict
#   "select_info": {Selectable object}
#       - optional
#       - providing this will enable the object to be selected in some
#            activities
#       - see Selectable JSON below for more info
#   "highlight": varies
#       - optional
#       - highlights are layers added to sprites that ignore the filtering
#           system.
#       - ACS: this may be a {Highlight object} or {Highlight Split object}
#           Split is used if an ACS has `arm_split` set
#       - HAIR: {Highlight object}
#       - CLOTHES: {Highlight object}
#   "dryrun": <anything>
#       - optional
#       - add this to dry run adding this sprite object
# }
#
#
# Additional props for ACS:
# {
#   "rec_layer": recommended layer constant,
#       - optional
#       - integer
#       - See MASMonika class for the constants
#       - if not given, we assume PST (post)
#   "priority": render priority
#       - optional
#       - integer.
#       - lower is rendered first
#       - default 10
#   "acs_type": "type of this acs"
#       - optional
#       - this is not necessary, but used in conjunction with mux_type to
#           remove potential conflicting acs types
#       - an ACS cannot have multiple types, but it can have multiple
#           conflicting types
#       - default None
#   "mux_type": [list of acs types this conflicts with]
#       - optional
#       - used in confjunction with acs_type
#       - must be list of strings
#       - default None
#   "arm_split": {Pose Map object}
#       - required if rec layer is 8/9 (BSE/ASE)
#       - each value should be a string
#       - See MASSplitAccessory for more info
#       - if omitted, then this will make a regular ACS
#   "dlg_desc": string describing this ACS for dialogue usage
#       - optional
#       - used in conjunction with dlg_plural
#       - must be a string
#       - default None
#   "dlg_plural": true if dlg_desc is a plural object, false if not
#       - optional
#       - used in conjuction with dlg_desc
#       - must be a bool
#       - default None
#   "keep_on_desk": true if this ACS should remain on desk if Monika is not
#       at the desk, False otherwise
#       - optional
#       - must be a bool
#       - default False
# }
#
# Shared props for ACS and CLOTHES:
#
# {
#   "giftname": "filename of the gift that unlocks this item",
#       - optional
#       - NOTE: if not provided, and this item is not unlocked or used
#           under other means, this item will NOT be selectable or usable.
#       - do not include extension
#       - default None
# }
#
# HAIR only props:
# {
#   "unlock": True will unlock the hair sprite for selecting. False will not.
#       - optional
#       - if False, then custom code will be required to unlock the sprite.
#       - if True, the sprite will unlock automatically
#       - Default True
#   "mid_hair_map": {Pose Map object}
#       - optional
#       - denotes which poses support the mid hair layer
# }
#
# CLOTHES only props:
#
# {
#   "hair_map": {hair string id mappings}
#       - optional
#       - This maps hair string IDs to other hair string IDs. When rendering
#           this clothing item, if the current hair is in this map, the
#           value is used instead.
#       - Use "all" as a key to signify a default for everything to map to.
#       - Both keys and values should be strings and should match to an
#           existing hair ID.
#       - default empty dict
#   "pose_arms": {Pose Arms object}
#       - optional
#       - if null, then we use the base pose as guide when determing pose
#           arms
# }
#
# PoseMap JSONSs
# NOTE: this is used differently based on the sprite object type.
# NOTE: the type is of most props also varies based onusage.
#
# In general:
#
# {
#   "mpm_type": type of this pose map
#       - required IF pose_map for hair or clothes
#       - integer
#       - 0 if enable/disable pose map
#       - 1 if fallback posemap
#   "default": value to use as default for all non-leaning poses
#       - optional
#       - default None
#   "l_default": value to use as default for all leaning poses
#       - optional
#       - default None
#   "use_reg_for_l": True will set the l_default value to default.
#       - optional
#       - boolean
#       - basically, this will set the default value for all leaning
#           poses to use the same as non-leaning poses.
#       - default False
#   "p1": value to use for pose 1
#       - optional
#       - This is the "steepling" pose
#       - default None
#   "p2": value to use for pose 2
#       - optional
#       - This is the "crossed" pose
#       - default None
#   "p3": value to use for pose 3
#       - optional
#       - This is the "restleftpointright" pose
#       - default None
#   "p4": value to use for pose 4
#       - optional
#       - This is the "pointright" pose
#       - default None
#   "p5": value to use for pose 5
#       - optional
#       - This is the "leaning-def-def" pose
#       - default None
#   "p6": value to use for pose 6
#       - optional
#       - This is the "down" pose
#       - default None
#   "p7": value to use for pose 7
#       - optional
#       - this is the "downleftpointright" pose
#       - default None
# }
#
# ACS (pose_map):
#   Values should be acs ID code (string). This code is part of the filename
#   for an ACS. This allows you to use a specific ACS image for certain poses.
#
# ACS (arm_split):
#   Values should be a ^ delimited string denoting layer codes:
#       0 - body-0 or arms-0 layer
#       1 - body-1 layer
#       5 - arms-5 layer
#       10 - arms-10 layer
#       * - all layers
#       "" - no layers
#   Delimited string example: 1^5^10
#   This allows you to split ACS that exist on split layers
#
# HAIR (pose_map):
#   If mpm_type is 1, then value should pose names (string). This is used
#       to determine what pose use instead of the desired pose.
#   If mpm_type is 0 (default), then value should be (boolean). This is
#       used to determine if a pose should be enabled or disabled for this
#       hair. True values will mean enabled, False means disabled.
#       By default, poses with False values will use steepling instead.
#
# CLOTHES (pose_map):
#   This functions the same as pose_map for HAIR.
#
# Selectables JSON:
#
# {
#   "display_name": "Name that should be shown in a selector menu for this
#       item",
#       - REQUIRED
#   "thumb": "Thumnail code of image",
#       - REQUIRED
#       - do not include extension
#   "group": "id of group this should be selectable with",
#       - REQUIRED
#       - this is like the type of acs/clothing/hair this item should be
#           selectable with
#   "visible_when_locked": True if this item should be visible in selectors
#       even when locked, False if not,
#       - optional
#       - boolean
#       - locked items will show the locked item thumbnail
#       - default True
#   "hover_dlg": [List of text to show when mouse is hovered over this in
#       selector],
#       - optional
#       - list of strings
#       - lines are picked randomly when hovered
#       - default None
#   "select_dlg": [List of text to show when this item is selected in the
#       selector],
#       - optional
#       - list of strings
#       - lines are picked randomly when selected
#       - default None
# }
#
# Pose Arm JSON
# This is a mappnig of all available arms
# Any omitted arm means that no layers should be shown for that arm.
# An empty dict means these clothes have no arm layers.
# {
#   "crossed": {Pose Arm Data object}
#       - optional
#       - pose arm data to use for crossed arms
#   "left-down": {Pose Arm Data object}
#       - optional
#       - pose arm data to use for the left down arm
#   "left-rest": {Pose Arm Data object}
#       - optional
#       - pose arm data to use for the left-rest arm
#   "right-down": {Pose Arm Data object}
#       - optional
#       - pose arm data to use for the right-down arm
#   "right-point": {Pose Arm Data object}
#       - optional
#       - pose arm data to use for the right point arm
#   "right-restpoint": {Pose Arm Data object}
#       - optional
#       - pose arm data to use for the right-restpoint arm
#   "steepling": {Pose Arm Data object}
#       - optional
#       - pose arm data to use for steepling arms
#   "def|left-def" {Pose Arm Data object}
#       - optional
#       - pose arm data to use for the leaning-def-left-def arm
#   "def|right-def" {Pose Arm Data object}
#       - optional
#       - pose arm data to use for the leaning-def-right-def arm
# }
#
# Pose Arm Data JSON
# {
#   "tag": name of the arm string to use in a pose
#       - REQUIRED
#       - string
#       - used in format like arms-<tag> or arms-left/right-<tag>
#   "layers": ^ delimited string denoting layers for this arm
#       - REQUIRED
#       - string
#       - available values:
#           "*" - this arm exists on all layers
#           "0" - this arm exists on the 0 layer
#           "5" - this arm exists on the 5 layer
#           "10" - this arm exists on the 10 layer
#           "" - this arm does not exist on any layer
#       - delimited stirng should look like: "5^10"
#   "highlight": {Highlight object}
#       - optional
#       - highlights for this arm
# }
#
# Highlight Split JSON
#   Highlight split objects are only for MASSPlitAccessory (Split ACS).
#   Keys should be the same as values used in the corresponding pose_map.
#   Values should be {Highlight objects}
#
# Highlight JSON
#   Intended values vary wildly based on object. See below the JSON for
#   specifics
# {
#   "default": {Filter object}
#       - optional
#       - default filter to use
#   "mapping": {object}
#       - optional
#       - maps keys to {Filter object}
#       - keys will vary. See below for specifics
# }
#
# ACS(highlight) - for REGULAR ACS
#   Keys should be same as values used in the corresponding pose_map.
#
# HAIR(highlight)
#   Keys:
#       "front" - highlight for front hair layer
#       "back" - highlight for back hair layre
#       "def|front" - highlight for front leaning hair layer
#       "def|back" - highlight for back leaning hair layer
#
# CLOTHES(highlight
#   Keys:
#       "0" - highlight for the body-0 layer
#       "1" - highlight for the body-1 layer
#       "def|0" - highlight for the body-0 leaning layer
#       "def|1" - highlight for the body-1 leaning layer
#
# Pose Arm Data(highlight)
#   Keys:
#       "0" - highlight for the arm-0 layer
#       "5" - highlight for the arm-5 layer
#       "10" - highlight for the arm-10 layer

# Highlight Split object values
#   Keys:
#       "0" - highlight for acs-0 layer
#       "1" - highlight for acs-1 layer
#       "5" - highlight for acs-5 layer
#       "10" - highlight for acs-10 layer
#
# Filter JSON
#   Filter objects map filters to highlight codes. Highlight codes are suffixed
#   to the end of files (before extension) as "h<code>"
# {
#   "default": "default higlight code to use"
#       - optional
#       - string
#       - highlight code to use as default
#   "day": "highlight code to use"
#       - optional
#       - string
#       - highlight code to map to day filters
#   "night": "highlight code to use"
#       - optional
#       - string
#       - highlight code to map to night filters
# }


default persistent._mas_sprites_json_gifted_sprites = {}
# contains sprite gifts that have been reacted to (aka unlocked)
# key: typle of the following fomrat:
#   [0] - spritre type (0 - ACS, 1 - HAIr, 2 - CLOTHES)
#   [1] - name of the sprite object this gift unlocks
# value: giftname to react to
#
# NOTE: contains sprite gifts after being unlocked. When its locked, it
#   should be in _mas_filereacts_sprite_gifts


init -21 python in mas_sprites_json:
    import __builtin__
    import json
    import store
    import store.mas_utils as mas_utils
    import traceback

    SP_JSON_VER = 3
    VERSION_TXT = "version"
    # CURRENT SPRITE VERSION. Change if fundamental sprite format chagnes.

    # these imports are for the classes
    from store.mas_ev_data_ver import _verify_bool, _verify_str, \
        _verify_int, _verify_list, _verify_dict

    log = mas_utils.getMASLog("log/spj")
    log_open = log.open()
    log.raw_write = True

    py_list = __builtin__.list
    py_dict = __builtin__.dict

    sprite_station = store.MASDockingStation(
        renpy.config.basedir + "/game/mod_assets/monika/j/"
    )
    # docking station for custom sprites.

    # verification dicts
    # We use key for O(1) and repeats
    # value is a list of sprite names we found the item in
    hm_key_delayed_veri = {}
    # keys that are missing will give warnings

    hm_val_delayed_veri = {}
    # vals tha tar emissing will give warnings. If a value is missing, it is
    #   replaced with teh default hairstyle (def)


    def _add_hair_to_verify(hairname, verimap, name):
        # only for use with the above dicts
        if hairname not in verimap:
            verimap[hairname] = []

        verimap[hairname].append(name)


    # mapping giftnames to sprite type / name
    # NOTE: __testing is a prohibiited name
    #   anything starting wtih 2 underscores is ignored.
    giftname_map = {
        "__testing": (0, "__testing"),
    }
    # key: giftname to react to
    # value: typle of the following format:
    #   [0] - sprite type (0 - ACS, 1 - HAIr, 2 - CLOTHES)
    #   [1] - name of the sprite object this gift unlocks
    #
    # NOTE: we load all sprites into this map.
    #   DUPLICATES ARE NOT ALLOWED
    #   then we compare:
    #       _mas_filereacts_sprite_gifts
    #   and remove the ones in those dicts that are not in this one.

    namegift_map = {
        (0, "__testing"): "__testing",
    }
    # reverse maps names to giftname
    # key: (sprite type, name)
    # value: giftname


    def writelog(msg):
        # new lines always added ourselves
        if log_open:
            log.write(msg)


    def writelogs(msgs):
        # writes multiple msges given list
        if log_open:
            for msg in msgs:
                log.write(msg)

        # clear msgs list
        msgs[:] = []

    ### LOG CONSTANTS
    ## Global
    READING_FILE = "reading JSON at '{0}'..."
    SP_LOADING = "loading {0} sprite object '{1}'..."
    SP_SUCCESS = "{0} sprite object '{1}' loaded successfully!"
    SP_SUCCESS_DRY = "{0} sprite object '{1}' loaded successfully! DRY RUN"
    VER_NOT_FOUND = "version not found"
    VER_BAD = "version mismatch. expected '{0}', found '{1}'"

    BAD_TYPE = "property '{0}' - expected type {1}, got {2}"
    EXTRA_PROP = "extra property '{0}' found"
    REQ_MISS = "required property '{0}' not found"
    BAD_SPR_TYPE = "invalid sprite type '{0}'"
    BAD_ACS_LAYER = "invalid ACS layer '{0}'"
    BAD_LIST_TYPE = "property '{0}' index '{1}' - expected type {2}, got {3}"
    EMPTY_LIST = "property '{0}' cannot be an empty list"

    DUPE_GIFTNAME = "giftname '{0}' already exists"
    MATCH_GIFT = (
        "cannot associate giftname '{0}' with sprite object type {1} name "
        "'{2}' - sprite object already associated with giftname '{3}'"
    )
    NO_GIFT = "without 'giftname', this cannot be natively unlocked"

    NO_DLG_DESC = "'dlg_desc' not found, ignoring 'dlg_plural'"
    NO_DLG_PLUR = "'dlg_plural' not found, ignoring 'dlg_desc'"

    ## MASPoseMap
    MPM_LOADING = "loading Pose Map in '{0}'..."
    MPM_SUCCESS = "Pose Map '{0}' loaded successfully!"
    MPM_BAD_TYPE = "invalid mpm_type '{0}'"
    MPM_TYPE_MISS = "expected mpm_type in {0}, got '{1}'"
    MPM_BAD_POSE = "property '{0}' - invalid pose '{1}'"
    MPM_FB_DEF = "in fallback mode but default not set"
    MPM_FB_DEF_L = "in fallback mode but leaning default not set"
    MPM_ACS_DEF = "acs default pose not set"
    MPM_ACS_DEF_L = "acs leaning default pose not set"
    MPM_DEF = "default not set"
    MPM_DEF_L = "leaning default not set"
    MPM_BAD_POSE_TYPE = "property '{0}' - expected type {1}, got {2}"
    MPM_AS_BAD_TYPE = "property '{0}' - expected {1}, got {2}"
    MPM_AS_EXTRA = "arm_split cannot be used with rec_layer '{0}'"
    MPM_PA_BAD_TYPE = "property '{0}' - expected object, got {1}"

    ## MASHighlightMap
    MHM_LOADING = "loading Highlight object..."
    MHM_SUCCESS = "Highlight object loaded successfully!"
    MHM_S_LOADING = "loading Highlight Split object..."
    MHM_S_SUCCESS = "Highlight Split object loaded successfully!"
    MHM_SK_LOADING = "loading Highlight object for key '{0}'..."
    MHM_SK_SUCCESS = "Highlight object for key '{0}' loaded successfully!"
    MHM_LOADING_MAPPING = "loading mapping..."
    MHM_SUCCESS_MAPPING = "mapping loaded successfully!"
    MHM_NO_DATA = "No data in Highlight object, ignoring"
    MHM_S_NO_DATA = "No data in Highlight Split object, ignoring"
    MHM_KEY_BAD_TYPE = "key '{0}' - expected type {1} got {2}"
    MHM_NOT_DICT = "Highlight object must be of type {0}. got {1}"
    MHM_S_NOT_DICT = "Highlight split object must be of type {0}. got {1}"

    ## MASFilterMap
    MFM_LOADING = "loading Filter object in '{0}'..."
    MFM_SUCCESS = "Filter object '{0}' loaded successfully!"
    MFM_NONE_FLT = "filter '{0}' set to null, ignoring"
    MFM_BAD_TYPE = "filter '{0}' - expected type str, got {1}"
    MFM_NO_DATA = "No data in Filter object, ignoring"

    ## MASPoseArms
    MPA_LOADING = "loading Pose Arms in '{0}'..."
    MPA_SUCCESS = "Pose Arms '{0}' loaded successfully!"
    MPA_BAD_TYPE = "Arm ID: {0} - expected type {1} got {2}"
    MPA_NO_DATA = "No Pose Arms data found"

    ## MASArm
    MA_LOADING = "loading Arm in '{0}'..."
    MA_SUCCESS = "Arm '{0}' loaded successfully!"
    MA_INVALID_LAYER = "invalid layer '{0}' found, ignoring"
    MA_NO_LAYERS = "Arm must have valid layers set"

    ## Hair Map
    HM_LOADING = "loading hair_map..."
    HM_SUCCESS = "hair_map loaded successfully!"
    HM_BAD_K_TYPE = "key '{0}' - expected type {1}, got {2}"
    HM_BAD_V_TYPE = "value for key '{0}' - expected type {1}, got {2}"
    HM_MISS_ALL = "hair_map does not have key 'all' set. Using default for 'all'."
    HM_FOUND_CUST = (
        "'custom' hair cannot be used in JSON hair maps. "
        "Outfits using 'custom' hair must be created manually."
    )
    HM_VER_ALL = "verifying hair maps..."
    HM_VER_SUCCESS = "hair map verification complete!"
    HM_NO_KEY = (
        "hair '{0}' does not exist - found in hair_map keys of these "
        "sprites: {1}"
    )
    HM_NO_VAL = (
        "hair '{0}' does not exist - found in hair_map values of these "
        "sprites: {1}. replacing with defaults."
    )

    ## ex_props
    EP_LOADING = "loading ex_props..."
    EP_SUCCESS = "ex_props loaded successfully!"
    EP_BAD_K_TYPE = "key '{0}' - expected type {1}, got {2}"
    EP_BAD_V_TYPE = "value for key '{0}' - expected type int/str/bool, got {1}"

    ## sel info props
    SI_LOADING = "loading select_info..."
    SI_SUCCESS = "sel_info loaded successfully!"

    ## prog points
    PP_MISS = "'{0}' progpoint not found"
    PP_NOTFUN = "'{0}' progpoint not callable"

    ## images loadable
    IL_NOTLOAD = "image at '{0}' is not loadable"

    ## gift labels
    GR_LOADING = "creating reactions for gifts..."
    GR_SUCCESS = "gift reactions created successfully!"
    GR_FOUND = "reaction label found for {0} sprite '{1}', giftname '{2}'"
    GR_GEN = "using generic reaction for {0} sprite '{1}', giftname '{2}'"


    ### CONSTANTS
    SP_ACS = 0
    SP_HAIR = 1
    SP_CLOTHES = 2

    SP_CONSTS = (
        SP_ACS,
        SP_HAIR,
        SP_CLOTHES,
    )

    SP_STR = {
        SP_ACS: "ACS",
        SP_HAIR: "HAIR",
        SP_CLOTHES: "CLOTHES",
    }

    SP_UF_STR = {
        SP_ACS: "accessory",
        SP_HAIR: "hairstyle",
        SP_CLOTHES: "outfit",
    }

    SP_PP = {
        SP_ACS: "store.mas_sprites._acs_{0}_{1}",
        SP_HAIR: "store.mas_sprites._hair_{0}_{1}",
        SP_CLOTHES: "store.mas_sprites._clothes_{0}_{1}",
    }

    SP_RL = {
        SP_ACS: "mas_reaction_gift_acs_{0}",
        SP_HAIR: "mas_reaction_gift_hair_{0}",
        SP_CLOTHES: "mas_reaction_gift_clothes_{0}",
    }

    SP_RL_GEN = "{0}|{1}|{2}"

    def _verify_sptype(val, allow_none=True):
        if val is None:
            return allow_none
        return val in SP_CONSTS


    ## param names
    ## with expected types and verifications, as well as msg to
    ##  show when verification fails.
    ##      (if None, we use the default bad type)

    # special params
    HLITE = "highlight"

    # main params

    REQ_SHARED_PARAM_NAMES = {
        # type must be checked first, so its not included in this loop.
#        "type": _verify_sptype,
        "name": (str, _verify_str),
        "img_sit": (str, _verify_str),
        # pose map verificaiton is different
#        "pose_map": None,
    }

    OPT_SHARED_PARAM_NAMES = {
        "stay_on_start": (bool, _verify_bool),

        # object-based verificatrion is different
#        "ex_props": None,
#        "select_info": None,

    }

    OPT_AC_SHARED_PARAM_NAMES = {
        "giftname": (str, _verify_str),
    }

    OPT_ACS_PARAM_NAMES = {
        # this is handled differently
#        "rec_layer": None,
#        "mux_type": (None, _verify_muxtype,

        "priority": (int, _verify_int),
        "acs_type": (str, _verify_str),
        "dlg_desc": (str, _verify_str),
        "dlg_plural": (str, _verify_bool),
        "keep_on_desk": (bool, _verify_bool),
    }
    OPT_ACS_PARAM_NAMES.update(OPT_AC_SHARED_PARAM_NAMES)

    OPT_HC_SHARED_PARAM_NAMES = {
#        "fallback": (bool, _verify_bool),
    }

    OPT_HAIR_PARAM_NAMES = {
        # object-based verification is different
#        "split": None,
        "unlock": (bool, _verify_bool),
    }

    OPT_CLOTH_PARAM_NAMES = {
        # object-based verificaiton is different
#        "hair_map": None,
    }
    OPT_CLOTH_PARAM_NAMES.update(OPT_AC_SHARED_PARAM_NAMES)

    ## special param name groups
    OBJ_BASED_PARAM_NAMES = (
        "pose_map",
        "ex_props",
        "select_info",
        "split",
        "hair_map",
        "arm_split",
        "pose_arms",
        HLITE,
        "mid_hair_map",
    )

    # select info params
    SEL_INFO_REQ_PARAM_NAMES = {
        "display_name": (str, _verify_str),
        "thumb": (str, _verify_str),
        "group": (str, _verify_str),
    }

    SEL_INFO_OPT_PARAM_NAMES = {
        "visible_when_locked": (bool, _verify_bool),
    }

    # pose arm data params
    PAD_REQ_PARAM_NAMES = {
        "tag": (str, _verify_str),
        "layers": (str, _verify_str),
    }

    # debug param name. If the json includes this, we dont actualy add
    # the sprite object
    DRY_RUN = "dryrun"


init 189 python in mas_sprites_json:
    from store.mas_sprites import _verify_pose, HAIR_MAP, CLOTH_MAP, ACS_MAP
    from store.mas_piano_keys import MSG_INFO, MSG_WARN, MSG_ERR, \
        JSON_LOAD_FAILED, FILE_LOAD_FAILED, \
        LOAD_TRY, LOAD_SUCC, LOAD_FAILED, \
        NAME_BAD

    # ACS_MAP / HAIR_MAP / CLOTH_MAP
    import store.mas_sprites as sms
    import store.mas_selspr as sml

    # msg log constants
    MSG_INFO_T = 0
    MSG_WARN_T = 1
    MSG_ERR_T = 2

    MSG_MAP = {
        MSG_INFO_T: MSG_INFO,
        MSG_WARN_T: MSG_WARN,
        MSG_ERR_T: MSG_ERR
    }

    # main functions


    def parsewritelog(msg_data):
        """
        write log using specially formatted data.

        IN:
            msg_data - tuple of the following format:
                [0] - log constant
                [1] - indentation level
                [2] - msg to write

        RETURNS: True if an ERR constant was found, False if not
        """
        log_con, indent, msg = msg_data
        prefix = MSG_MAP.get(log_con, None)
        if prefix is None:
            return True

        indents = " " * (indent * 2)
        msg = indents + prefix.format(msg)
        writelog(msg)

        return log_con == MSG_ERR_T


    def parsewritelogs(msgs_data):
        """
        Write logs using specially formatted data

        IN:
            msgs_data - list of tuples of the following format:
                [0] - log constant
                [1] - indentation level
                [2] - msg to write

        RETURNS: True if an ERR constnat was found, False if not
        """
        is_bad = False
        for msg_data in msgs_data:
            if parsewritelog(msg_data):
                is_bad = True

        return is_bad


    def _replace_hair_map(sp_name, hair_to_replace):
        """
        Replaces the hair vals of the given sprite object with the given name
        of the given hair with defaults.

        IN:
            sp_name - name of the clothing sprite object to replace hair
                map values in
            hair_to_replace - hair name to replace with defaults
        """
        # sanity checks
        sp_obj = CLOTH_MAP.get(sp_name, None)
        if sp_obj is None or sp_obj.hair_map is None:
            return

        # otherwise this is a real clothing with a hair map
        for hair_key in sp_obj.hair_map:
            if sp_obj.hair_map[hair_key] == hair_to_replace:
                sp_obj.hair_map[hair_key] = store.mas_hair_def.name


    def _remove_sel_list(name, sel_list):
        """
        Removes selectable from selectbale list

        Only intended for json usage. DO not use elsewhere. In general, you
        should NEVER need to remove a selectable from the selectable list.
        """
        for index in range(len(sel_list)-1, -1, -1):
            if sel_list[index].name == name:
                sel_list.pop(index)


    def _reset_sp_obj(sp_obj):
        """
        Uninits the given sprite object. This is meant only for json
        sprite usage if we need to back out.

        IN:
            sp_obj - sprite object to remove
        """
        sp_type = sp_obj.gettype()
        sp_name = sp_obj.name

        # sanity check
        if sp_type not in SP_CONSTS:
            return

        if sp_type == SP_ACS:
            _item_map = sms.ACS_MAP
            _sel_map = sml.ACS_SEL_MAP
            _sel_list = sml.ACS_SEL_SL

        elif sp_type == SP_HAIR:
            _item_map = sms.HAIR_MAP
            _sel_map = sml.HAIR_SEL_MAP
            _sel_list = sml.HAIR_SEL_SL

        else:
            # clothes
            _item_map = sms.CLOTH_MAP
            _sel_map = sml.CLOTH_SEL_MAP
            _sel_list = sml.CLOTH_SEL_SL

        # remvoe from sprite object map
        if sp_name in _item_map:
            _item_map.pop(sp_name)

        if sml.get_sel(sp_obj) is not None:
            # remove from selectable map
            if sp_name in _sel_map:
                _sel_map.pop(sp_name)

            # remove from selectable list
            _remove_sel_list(sp_name, _sel_list)


    def _build_loadstrs(sp_obj, sel_obj=None):
        """
        Builds list of strings that need to be verified via loadable.

        IN:
            sp_obj - sprite object to build strings from
            sel_obj - selectable to build thumb string from.
                Ignored if None
                (Default: None)

        RETURNS: list of strings that would need to be loadable verified
        """
        # determine full prefix

        # ACS: images consist of the all pose code items that are
        # in the /a/ folder
        # + night versions
        #
        # HAIR: images consist of upright and leaning items in /h/
        # folder
        # + night versions
        #
        # CLOTHES: images consist of upright and leaning body items
        # in /c/ folder
        # + night versions
        if sp_obj.gettype() == SP_ACS:
            prefix = [sms.A_MAIN]

        elif sp_obj.gettype() == SP_HAIR:
            prefix = [sms.H_MAIN]

        elif sp_obj.gettype() == SP_CLOTHES:
            prefix = [sms.C_MAIN]

        else:
            return []

        # list of strings to verify
        to_verify = [
            "".join(str_tup)
            for str_tup in sp_obj.build_loadstrs(prefix)
        ]

        # thumbs
        if sel_obj is not None:
            to_verify.append(sel_obj._build_thumbstr())

        return to_verify


    def _check_giftname(giftname, sp_type, sp_name, msg_log, ind_lvl):
        """
        Initializes the giftname with the sprite info

        IN:
            giftname - giftname we want to use
            sp_type - sprite type we want to init
            sp_name - name of the sprite object to associated with this gift
                (use the sprite's name property == ID)
            ind_lvl - indentation level to use

        OUT:
            msg_log - list to log messages to
        """
        # giftname must be unique
        if giftname in giftname_map:
            msg_log.append((
                MSG_ERR_T,
                ind_lvl,
                DUPE_GIFTNAME.format(giftname)
            ))
            return

        # cannot have a sprite object assocaited with 2 giftnames
        sp_value = (sp_type, sp_name)
        if sp_value in namegift_map:
            msg_log.append((
                MSG_ERR_T,
                ind_lvl,
                MATCH_GIFT.format(
                    giftname,
                    SP_STR[sp_type],
                    sp_name,
                    namegift_map[sp_value]
                )
            ))
            return


    def _init_giftname(giftname, sp_type, sp_name):
        """
        Initializes the giftname with the sprite info
        does not check for valid giftname.

        IN:
            giftname - giftname we want to use
            sp_type - sprite type we want to init
            sp_name - name of the sprite object to associate with this gift
        """
        # add item to gift maps
        giftname_map[giftname] = (sp_type, sp_name)
        namegift_map[(sp_type, sp_name)] = giftname


    def _process_giftname():
        """
        Process the gift maps by cleaning the persistent vars
        """
        # clean filereacts sprite gifts
        for fr_sp_gn in store.persistent._mas_filereacts_sprite_gifts:
            if fr_sp_gn not in giftname_map:
                store.persistent._mas_filereacts_sprite_gifts.pop(fr_sp_gn)

        # clean json gift sprites list
        for j_sp_data in store.persistent._mas_sprites_json_gifted_sprites:
            if j_sp_data not in namegift_map:
                store.persistent._mas_sprites_json_gifted_sprites.pop(j_sp_data)


    def _process_progpoint(
            sp_type,
            name,
            save_obj,
            msg_log,
            ind_lvl,
            progname
        ):
        """
        Attempts to find a prop point for a sprite object with the given
        sp_type and name

        IN:
            sp_type - sprite object type
            name - name of sprite object
            ind_lvl - indent level
            progname - name of progpoint (do not include suffix)

        OUT:
            save_obj - dict to save progpoint to
            msg_log - list to save messages to
        """
        # get string version
        e_pp_str = SP_PP[sp_type].format(name, progname)

        # eval string version
        try:
            e_pp = eval(e_pp_str)

        except:
            # only error is not exist
            e_pp = None

        # validate progpoint
        if e_pp is None:
            msg_log.append((
                MSG_INFO_T,
                ind_lvl,
                PP_MISS.format(progname)
            ))

        elif not callable(e_pp):
            msg_log.append((
                MSG_WARN_T,
                ind_lvl,
                PP_NOTFUN.format(progname)
            ))

        else:
            # success
            save_obj[progname + "_pp"] = e_pp


    def _test_loadables(sp_obj, msg_log, ind_lvl):
        """
        Tests loadable images and errs if an image is not loadable.

        IN:
            sp_obj - sprite object to test
            ind_lvl - indentation level

        OUT:
            msg_log - list to add messages to
        """
        sel_obj = sml.get_sel(sp_obj)

        # and strs to verify
        to_verify = _build_loadstrs(sp_obj, sel_obj)

        # verfiy each string
        for imgpath in to_verify:
            if not renpy.loadable(imgpath):
                msg_log.append((
                    MSG_ERR_T,
                    ind_lvl,
                    IL_NOTLOAD.format(imgpath)
                ))


    def _validate_type(json_obj):
        """
        Validates the type of this json object.

        Logs errors. Also pops type off

        IN:
            json_obj - json object to validate

        RETURNS: SP constant if valid type, None otherwise
        """
        # check for type existence
        if "type" not in json_obj:
            writelog(MSG_ERR_ID.format(REQ_MISS.format("type")))
            return None

        # type exists, validate
        type_val = json_obj.pop("type")
        if not _verify_sptype(type_val, False):
            writelog(MSG_ERR_ID.format(BAD_SPR_TYPE.format(type(type_val))))
            return None

        # type validated, return it
        return type_val


    def _validate_mux_type(json_obj, msg_log, indent_lvl):
        """
        Validates mux_type of this json object

        IN:
            json_obj - json object to validate
            indent_lvl - indtenation lvl to use

        OUT:
            msg_log - list to save error messages to
                if nothing was addeed to this list, the mux_type is valid

        RETURNS: mux_type found. May be None
        """
        if "mux_type" not in json_obj:
            return None

        # otherwise it exists
        mux_type = json_obj.pop("mux_type")

        if not _verify_list(mux_type):
            # not list is bad
            msg_log.append((
                MSG_ERR_T,
                indent_lvl,
                BAD_TYPE.format(
                    "mux_type",
                    py_list,
                    type(mux_type)
                )
            ))
            return None

        # otherwise, verify each element of this list
        for index in range(len(mux_type)):
            acs_type = mux_type[index]
            if not _verify_str(acs_type):
                msg_log.append((
                    MSG_ERR_T,
                    indent_lvl,
                    BAD_LIST_TYPE.format(
                        "mux_type",
                        index,
                        str,
                        type(acs_type)
                    )
                ))
                # NOTE: we log these but still return the muxtype.
                #   it is up to the caller to check for messages
                #   to determine if the item is valid

        return mux_type


    def _validate_iterstr(
            jobj,
            save_obj,
            propname,
            required,
            allow_none,
            msg_log,
            indent_lvl
        ):
        """
        Validates an iterable if it consists solely of strings

        an empty list is considered bad.

        IN:
            jobj - json object to parse
            propname - property name for error messages
            required - True if this property is required, False if not
            allow_none - True if None is valid value, False if not
            indent_lvl - indentation level

        OUT:
            save_obj - dict to save to
            msg_log - list to save messages to

        RETURNS: True if good, False if bad
        """
        # sanity checks
        if propname not in jobj:
            if required:
                msg_log.append((
                    MSG_ERR_T,
                    indent_lvl,
                    REQ_MISS.format(propname)
                ))
                return False
            return True

        # prop found
        iterval = jobj.pop(propname)

        # should None be allowed
        if iterval is None:
            if not allow_none:
                msg_log.append((
                    MSG_ERR_T,
                    indent_lvl,
                    BAD_TYPE.format(propname, py_list, type(iterval))
                ))
                return False
            return True

        # okay not None
        if len(iterval) <= 0:
            msg_log.append((
                MSG_ERR_T,
                indent_lvl,
                EMPTY_LIST.format(propname)
            ))
            return False

        # check individual strings
        is_bad = False
        for index in range(len(iterval)):
            item = iterval[index]

            if not _verify_str(item):
                msg_log.append((
                    MSG_ERR_T,
                    indent_lvl,
                    BAD_LIST_TYPE.format(propname, index, str, type(item))
                ))
                is_bad = True

        if is_bad:
            return False

        # no errors? save data
        save_obj[propname] = iterval
        return True


    def _validate_params(
            jobj,
            save_obj,
            param_dict,
            required,
            msg_log,
            indent_lvl,
        ):
        """
        Validates a list of parameters, while also saving said params into
        given save object.

        Errors/Warnings are logged to given lists

        IN:
            jobj - json object to parse
            param_dict - dict of params + verification functiosn
            required - True if the given params are required, False otherwise.
            indent_lvl - indentation level to use

        OUT:
            save_obj - dict to save data to
            msg_log - log to save messages to

        RETURNS: True if success, False if not
        """
        # if required, we do not accept Nones
        allow_none = not required
        is_bad = False

        for param_name, verifier_info in param_dict.iteritems():
            if param_name in jobj:
                param_val = jobj.pop(param_name)
                desired_type, verifier = verifier_info

                if not verifier(param_val, allow_none):
                    # failed verification
                    msg_log.append((
                        MSG_ERR_T,
                        indent_lvl,
                        BAD_TYPE.format(
                            param_name,
                            desired_type,
                            type(param_val)
                        )
                    ))
                    is_bad = True

                # otherwise, good, transfer the property over
                # and continue
                save_obj[param_name] = param_val

            elif required:
                # this was a required param, add error
                msg_log.append((
                    MSG_ERR_T,
                    indent_lvl,
                    REQ_MISS.format(param_name)
                ))
                is_bad = True

        return not is_bad


    def _validate_acs(jobj, save_obj, obj_based, msg_log, indent_lvl):
        """
        Validates ACS-specific properties, as well as acs pose map

        Props validated:
            - rec_layer
            - priority
            - acs_type
            - dlg_desc
            - dlg_plural
            - mux_type
            - pose_map
            - giftname
            - arm_split
            - highlight

        IN:
            jobj - json object to pasrse
            obj_based - dict of object-based items
                (contains pose_map)
            indent_lvl - indentation lvl to use

        OUT:
            save_obj - dict to save data to
            msg_log - list to add messages to

        RETURNS: True if validation success, False if not
        """
        # validate ez to validate props
        # priority
        # acs_type
        # dlg_desc
        # dlg_plural
        # keep_on_desk
        if not _validate_params(
            jobj,
            save_obj,
            OPT_ACS_PARAM_NAMES,
            False,
            msg_log,
            indent_lvl
        ):
            return False

        # combine dlg_desc and dlg_plur
        if "dlg_desc" in save_obj:
            dlg_desc = save_obj.pop("dlg_desc")

            # both fields are required
            if "dlg_plural" in save_obj:

                # combine data
                save_obj["dlg_data"] = (dlg_desc, save_obj.pop("dlg_plural"))

            else:
                # dlg_plural not found, show a warn
                msg_log.append((MSG_WARN_T, indent_lvl, NO_DLG_PLUR))

        elif "dlg_plural" in save_obj:
            # dlg_desc was not found, just pop out dlg_plur
            msg_log.append((MSG_WARN_T, indent_lvl, NO_DLG_DESC))
            save_obj.pop("dlg_plural")

        # now for rec_layer
        if "rec_layer" in jobj:
            rec_layer = jobj.pop("rec_layer")

            if not store.MASMonika._verify_rec_layer(rec_layer):
                msg_log.append((
                    MSG_ERR_T,
                    indent_lvl,
                    BAD_ACS_LAYER.format(rec_layer)
                ))
                return False

            # otherwise valid
            save_obj["rec_layer"] = rec_layer

        # now for mux_type
        err_log = []
        mux_type = _validate_mux_type(jobj, err_log, indent_lvl)
        if len(err_log) > 0:
            msg_log.extend(err_log)
            return False

        # otherwise valid
        save_obj["mux_type"] = mux_type

        # now for pose map
        msg_log.append((
            MSG_INFO_T,
            indent_lvl,
            MPM_LOADING.format("pose_map")
        ))

        # pose map must exist for us to reach this point.
        # NOTE: all ACS use the IC type
        mpm_obj = obj_based.pop("pose_map")
        mpm_obj["mpm_type"] = store.MASPoseMap.MPM_TYPE_IC
        mpm_msg_log = []
        pose_map = store.MASPoseMap.fromJSON(
            mpm_obj,
            mpm_msg_log,
            indent_lvl + 1
        )
        msg_log.extend(mpm_msg_log)
        if pose_map is None:
            return False

        # and succ
        msg_log.append((
            MSG_INFO_T,
            indent_lvl,
            MPM_SUCCESS.format("pose_map")
        ))
        save_obj["pose_map"] = pose_map

        # now for arm split
        arm_split = None
        if store.MASMonika._verify_spl_layer(rec_layer):
            # this is an arm split layer, so we should parse it
            if "arm_split" not in obj_based:
                # NOTE: this is required for SPL layers
                msg_log.append((
                    MSG_ERR_T,
                    indent_lvl,
                    REQ_MISS.format("arm_split")
                ))
                return False

            # type checking should have occurred already
            # now for arm split
            msg_log.append((
                MSG_INFO_T,
                indent_lvl,
                MPM_LOADING.format("arm_split")
            ))

            # this posemap should be treated as arm splits
            mpm_obj = obj_based.pop("arm_split")
            mpm_obj["mpm_type"] = store.MASPoseMap.MPM_TYPE_AS
            mpm_msg_log = []
            arm_split = store.MASPoseMap.fromJSON(
                mpm_obj,
                mpm_msg_log,
                indent_lvl + 1
            )
            msg_log.extend(mpm_msg_log)
            if arm_split is None:
                return False

            # succ
            msg_log.append((
                MSG_INFO_T,
                indent_lvl,
                MPM_SUCCESS.format("arm_split")
            ))
            save_obj["arm_split"] = arm_split

        elif "arm_split" in obj_based:
            # otherwise, just warn if the property exists
            obj_based.pop("arm_split")
            msg_log.append((
                MSG_WARN_T,
                indent_lvl,
                MPM_AS_EXTRA.format(rec_layer)
            ))

        # now for highlight
        # NOTE: this depends on pose_map and arm_split
        if HLITE in obj_based:

            # first determine the hl keys
            hl_keys = pose_map.unique_values()

            if arm_split:
                # this should be a split accessory

                hl_data = store.MASSplitAccessory.fromJSON_hl_data(
                    obj_based.pop(HLITE),
                    msg_log,
                    indent_lvl,
                    hl_keys,
                    rec_layer
                )

                # validate hl data
                if hl_data is False:
                    return False

                # otherwise good
                if hl_data is not None:
                    save_obj["hl_data"] = hl_data

            else:
                # not a split accessory

                if not _validate_highlight(
                        obj_based,
                        save_obj,
                        msg_log,
                        indent_lvl,
                        hl_keys
                ):
                    return False

        return True


    def _validate_fallbacks(jobj, save_obj, obj_based, msg_log, indent_lvl):
        """
        Validates fallback related properties and pose map

        Props validated:
            - fallback
            - pose_map

        IN:
            jobj - json object to parse
            obj_based - dict of object-based items
                (contains pose_map)
            indent_lvl - indentation lvl to use

        OUT:
            save_obj - dict to save data to
            msg_log - list to save messages to

        RETURNS: True if success, False if not
        """
        # validate fallback
        if not _validate_params(
            jobj,
            save_obj,
            OPT_HC_SHARED_PARAM_NAMES,
            False,
            msg_log,
            indent_lvl
        ):
            return False

        # valid fallback? determine it
        fallback = save_obj.get("fallback", False)

        # now parse pose map
        msg_log.append((
            MSG_INFO_T,
            indent_lvl,
            MPM_LOADING.format("pose_map")
        ))
        mpm_msg_log = []
        pose_map = store.MASPoseMap.fromJSON(
            obj_based.pop("pose_map"),
            mpm_msg_log,
            indent_lvl + 1,
            valid_types=(
                store.MASPoseMap.MPM_TYPE_ED,
                store.MASPoseMap.MPM_TYPE_FB
            )
        )
        msg_log.extend(mpm_msg_log)
        if pose_map is None:
            return False

        # and successful
        msg_log.append((
            MSG_INFO_T,
            indent_lvl,
            MPM_SUCCESS.format("pose_map")
        ))
        save_obj["pose_map"] = pose_map
        return True


    def _validate_hair(jobj, save_obj, obj_based, msg_log, indent_lvl):
        """
        Validates HAIR related properties

        Props validated:
            - unlock
            - highlight

        IN:
            jobj - json object to parse
            obj_based - dict of object-based items
            indent_lvl - indentation lvl

        OUT:
            save_obj - dict to save data to
            msg_log - list to save messagse to

        RETURNS: True on success, False if not
        """
        # validate optional params
        if not _validate_params(
            jobj,
            save_obj,
            OPT_HAIR_PARAM_NAMES,
            False,
            msg_log,
            indent_lvl
        ):
            return False

        # mid hair map
        if "mid_hair_map" in obj_based:
            msg_log.append((
                MSG_INFO_T,
                indent_lvl,
                MPM_LOADING.format("mid_hair_map")
            ))
            mpm_msg_log = []
            mid_hair_map = store.MASPoseMap.fromJSON(
                obj_based.pop("mid_hair_map"),
                mpm_msg_log,
                indent_lvl + 1,
                valid_types=(
                    store.MASPoseMap.MPM_TYPE_ED,
                )
            )
            msg_log.extend(mpm_msg_log)
            if mid_hair_map is None:
                return False

            # and success
            msg_log.append((
                MSG_INFO_T,
                indent_lvl,
                MPM_SUCCESS.format("mid_hair_map")
            ))
            save_obj["mpm_mid"] = mid_hair_map

        # now validate highlight
        if HLITE in obj_based:

            # parse
            if not _validate_highlight(
                    obj_based,
                    save_obj,
                    msg_log,
                    indent_lvl,
                    store.MASHair.hl_keys_c()
            ):
                return False

#        # validate split
#        if "split" not in obj_based:
#            # no split found, not a problem
#            return
#
#        # split exists, lets get and validate
#        writelog(MSG_INFO_ID.format(MPM_LOADING.format("split")))
#        split = store.MASPoseMap.fromJSON(
#            obj_based.pop("split"),
#            False,
#            False,
#            errs,
#            warns
#        )
#        if split is None or len(errs) > 0:
#            writelogs(warns)
#            return
#
#        # valid pose map!
#        # write out wrans
#        writelogs(warns)
#
#        # and success
#        writelog(MSG_INFO_ID.format(MPM_SUCCESS.format("split")))
#        save_obj["split"] = split

        return True


    def _validate_clothes(
            jobj,
            save_obj,
            obj_based,
            sp_name,
            dry_run,
            msg_log,
            indent_lvl
        ):
        """
        Validates CLOTHES related properties

        Props validated:
            - hair_map
            - giftname
            - pose_arms
            - highlight

        IN:
            jobj - json object to parse
            obj_based - dict of objected-baesd items
                (contains split)
            sp_name - name of the clothes we are validating
            dry_run - true if we are dry running, False if not
            indent_lvl - indentation lvl

        OUT:
            save_obj - dict to save data to
            msg_log - list to save messages to

        RETURNS: True if good, False if not
        """
        # giftname
        if not _validate_params(
            jobj,
            save_obj,
            OPT_CLOTH_PARAM_NAMES,
            False,
            msg_log,
            indent_lvl
        ):
            return

        # validate hair_map
        if "hair_map" in obj_based:

            # hair map exists, get and validate
            msg_log.append((MSG_INFO_T, indent_lvl, HM_LOADING))
            hair_map = obj_based.pop("hair_map")
            is_bad = False

            for hair_key,hair_value in hair_map.iteritems():
                # start with type validations

                # key
                if _verify_str(hair_key):
                    if (
                            not dry_run
                            and hair_key != "all"
                            and hair_key not in HAIR_MAP
                        ):
                        _add_hair_to_verify(
                            hair_key,
                            hm_key_delayed_veri,
                            sp_name
                        )
                else:
                    msg_log.append((
                        MSG_ERR_T,
                        indent_lvl + 1,
                        HM_BAD_K_TYPE.format(hair_key, str, type(hair_key))
                    ))
                    is_bad = True

                # value
                if _verify_str(hair_value):
                    if hair_value == "custom":
                        msg_log.append((
                            MSG_ERR_T,
                            indent_lvl + 1,
                            HM_FOUND_CUST
                        ))
                        is_bad = True

                    elif not dry_run and hair_value not in HAIR_MAP:
                        _add_hair_to_verify(
                            hair_value,
                            hm_val_delayed_veri,
                            sp_name
                        )

                else:
                    msg_log.append((
                        MSG_ERR_T,
                        indent_lvl + 1,
                        HM_BAD_V_TYPE.format(hair_key, str, type(hair_value))
                    ))
                    is_bad = True

            # recommend "all" and set it to default
            if "all" not in hair_map:
                msg_log.append((MSG_WARN_T, indent_lvl + 1, HM_MISS_ALL))
                hair_map["all"] = "def"

            # check for no errors
            if is_bad:
                return False

            # hair map loaded! verification will happen later.
            msg_log.append((MSG_INFO_T, indent_lvl, HM_SUCCESS))
            save_obj["hair_map"] = hair_map

        # validate pose arms
        if "pose_arms" in obj_based:
            # pose arms exists, get and validate
            msg_log.append((
                MSG_INFO_T,
                indent_lvl,
                MPA_LOADING.format("pose_arms")
            ))

            # check type
            pa_obj = obj_based.pop("pose_arms")
            if not _verify_dict(pa_obj, False):
                msg_log.append((
                    MSG_ERR_T,
                    indent_lvl + 1,
                    BAD_TYPE.format("pose_arms", dict, type(pa_obj))
                ))
                return False

            # load pose arms
            pose_arms = store.MASPoseArms.fromJSON(
                pa_obj,
                msg_log,
                indent_lvl + 1
            )

            # check fail/succ
            if pose_arms is False:
                return False

            # succ
            msg_log.append((
                MSG_INFO_T,
                indent_lvl,
                MPA_SUCCESS.format("pose_arms")
            ))

            if pose_arms is not None:
                save_obj["pose_arms"] = pose_arms

        # now for highlight
        if HLITE in obj_based:
            # parse
            if not _validate_highlight(
                    obj_based,
                    save_obj,
                    msg_log,
                    indent_lvl,
                    store.MASClothes.hl_keys_c()
            ):
                return False

        return True


    def _validate_ex_props(jobj, save_obj, obj_based, msg_log, ind_lvl):
        """
        Validates ex_props proprety

        Props validated:
            - ex_props

        IN:
            jobj - json object to parse
            obj_based - dict of object-based items
                (contains ex_props)
            ind_lvl - indentation level

        OUT:
            save_obj - dict to save data to
            msg_log - list to save messages to
        """
        # validate ex_props
        if "ex_props" not in obj_based:
            return

        # ex_props exists, get and validate
        msg_log.append((MSG_INFO_T, ind_lvl, EP_LOADING))
        ex_props = obj_based.pop("ex_props")

        isbad = False
        for ep_key,ep_val in ex_props.iteritems():
            if not _verify_str(ep_key):
                msg_log.append((
                    MSG_ERR_T,
                    ind_lvl + 1,
                    EP_BAD_K_TYPE.format(ep_key, str, type(ep_key))
                ))
                isbad = True

            if not (
                    _verify_str(ep_val)
                    or _verify_bool(ep_val)
                    or _verify_int(ep_val)
                ):
                msg_log.append((
                    MSG_ERR_T,
                    ind_lvl + 1,
                    EP_BAD_V_TYPE.format(ep_key, type(ep_val))
                ))
                isbad = True

        # check for no errors
        if isbad:
            return

        # otherwise, we can say successful loading!
        msg_log.append((MSG_INFO_T, ind_lvl, EP_SUCCESS))
        save_obj["ex_props"] = ex_props


    def _validate_highlight(obj_based, save_obj, msg_log, ind_lvl, hl_keys):
        """
        Validates highlight objects

        Props validated:
            - highlight

        IN:
            obj_based - dict of object-based props
            hl_keys - the keys that this highlight object should be using
            ind_lvl - indentation level

        OUT:
            save_obj - dict to save data to
            msg_log - list to add messages to

        RETURNS: True if valid, False if not
        """
        # first log loading
        msg_log.append((MSG_INFO_T, ind_lvl, MHM_LOADING))

        # parse the data
        if not _validate_highlight_core(
                obj_based.pop(HLITE),
                save_obj,
                msg_log,
                ind_lvl + 1,
                hl_keys
        ):
            # failure case
            return False

        # otherwise successful
        msg_log.append((MSG_INFO_T, ind_lvl, MHM_SUCCESS))
        return True


    def _validate_highlight_core(jobj, save_obj, msg_log, ind_lvl, hl_keys):
        """
        Primary portion of highlight validation. This is so it can be
        used seamlessly with highlight split object validation logs.

        Props validated:
            - highlight

        IN:
            jobj - json object to parse
            hl_keys - the keys this highlight object should be using

        OUT:
            save_obj - dict to save data to
            msg_log - list to add messages to

        RETURNS: True if valid, False if not
        """
        # first check type of this data
        if not _verify_dict(jobj, allow_none=False):
            msg_log.append((
                MSG_ERR_T,
                ind_lvl,
                MHM_NOT_DICT.format(dict, type(jobj))
            ))
            return False

        # setup hl data
        hl_def = None
        hl_mapping = {}

        # first try parsing for default
        if "default" in jobj:
            hl_def = store.MASFilterMap.fromJSON(
                jobj.pop("default"),
                msg_log,
                ind_lvl,
                "default"
            )

        # now for mapping
        # mapping data should be in Dict format
        has_map_data = False
        if "mapping" in jobj:
            mapobj = jobj.pop("mapping")

            # loading mapping
            msg_log.append((MSG_INFO_T, ind_lvl, MHM_LOADING_MAPPING))

            # check type
            if not _verify_dict(mapobj, allow_none=False):
                msg_log.append((
                    MSG_ERR_T,
                    ind_lvl + 1,
                    BAD_TYPE.format("mapping", dict, type(mapobj))
                ))
                return False

            # loop over hl keys
            isbad = False
            for hl_key in hl_keys:
                if hl_key in mapobj:
                    flt_obj = store.MASFilterMap.fromJSON(
                        mapobj.pop(hl_key),
                        msg_log,
                        ind_lvl + 1,
                        hl_key
                    )

                    # check for fail/succ
                    if flt_obj is False:
                        isbad = True
                    else:
                        if flt_obj is not None:
                            # None check the flt object for later
                            has_map_data = True

                        hl_mapping[hl_key] = flt_obj

            # warn if any extras
            for extra_prop in mapobj:
                msg_log.append((
                    MSG_WARN_T,
                    ind_lvl + 1,
                    EXTRA_PROP.format(extra_prop)
                ))

            # quit if failure
            # log should be handled by the MFM logging
            if isbad:
                return False

            # done lodaing mapping
            msg_log.append((MSG_INFO_T, ind_lvl, MHM_SUCCESS_MAPPING))

        # check if we actually have any data
        if hl_def is None and (len(hl_mapping) == 0 or not has_map_data):
            # no data, warn but no failure
            msg_log.append((MSG_WARN_T, ind_lvl, MHM_NO_DATA))

        else:
            # otherwise valid data probably
            save_obj["hl_data"] = (hl_def, hl_mapping)

        return True


    def _validate_selectable(jobj, save_obj, obj_based, msg_log, indent_lvl):
        """
        Validates selectable

        Props validated:
            - select_info

        IN:
            jobj - json object to parse
            obj_based - dict of object-based items
                (contains select_info)
            indent_lvl - indentation level

        OUT:
            save_obj - dict to save data to
            msg_log - list to write messages to

        RETURNS: True if success, false if failure
        """
        # select_info exists, get and validate
        msg_log.append((MSG_INFO_T, indent_lvl, SI_LOADING))
        select_info = obj_based.pop("select_info")

        # validate required
        if not _validate_params(
            select_info,
            save_obj,
            SEL_INFO_REQ_PARAM_NAMES,
            True,
            msg_log,
            indent_lvl + 1
        ):
            return False

        # now for optional
        if not _validate_params(
            select_info,
            save_obj,
            SEL_INFO_OPT_PARAM_NAMES,
            False,
            msg_log,
            indent_lvl + 1
        ):
            return False

        # now for list based
        if "hover_dlg" in select_info:
            select_info.pop("hover_dlg")
#            if not _validate_iterstr(
#                select_info,
#                save_obj,
#                "hover_dlg",
#                False,
#                True,
#                msg_log,
#                indent_lvl + 1
#            ):
#                return False

        if "select_dlg" in select_info:
            if not _validate_iterstr(
                select_info,
                save_obj,
                "select_dlg",
                False,
                True,
                msg_log,
                indent_lvl + 1
            ):
                return False

        # warning extra props
        for extra_prop in select_info:
            msg_log.append((
                MSG_WARN_T,
                indent_lvl + 1,
                EXTRA_PROP.format(extra_prop)
            ))

        # success, lets save
        msg_log.append((MSG_INFO_T, indent_lvl, SI_SUCCESS))

        # NOTE: item is already saved into the dict
        return True


    def addSpriteObject(filepath):
        """
        Adds a sprite object, given its json filepath

        NOTE: most exceptions logged
        NOTE: may raise exceptions

        IN:
            filepath - filepath to the JSON we want to load
        """
        dry_run = False
        jobj = None
        msgs_err = []
        msgs_warn = []
        msgs_info = []
        msgs_exprop = []
        obj_based_params = {}
        sp_obj_params = {}
        sel_params = {}
        unlock_hair = True
        giftname = None
        indent_lvl = 0

        writelog("\n" + MSG_INFO.format(READING_FILE.format(filepath)))

        # can we read file
        with open(filepath, "r") as jsonfile:
            jobj = json.load(jsonfile)

        # is file json
        if jobj is None:
            writelog(MSG_ERR.format(JSON_LOAD_FAILED.format(filepath)))
            return

        if DRY_RUN in jobj:
            jobj.pop(DRY_RUN)
            dry_run = True

        # get rid of __keys
        for jkey in jobj.keys():
            if jkey.startswith("__"):
                jobj.pop(jkey)

        # determine version. Versions must match SP_JSON_VER.
        if VERSION_TXT not in jobj:
            writelog(MSG_ERR.format(VER_NOT_FOUND))
            return

        # version text exists, check it
        version = jobj.pop(VERSION_TXT)

        # check type
        if not _verify_int(version, allow_none=False):
            # not valid version type, err this
            writelog(MSG_ERR.format(VER_BAD.format(SP_JSON_VER, version)))
            return

        # check version match
        if version != SP_JSON_VER:
            writelog(MSG_ERR.format(VER_BAD.format(SP_JSON_VER, version)))
            return

        # otherwise we good version

        ## this happens in 3 steps:
        # 1. build sprite object according to the json
        #   - this includes PoseMaps
        #   - and highlights
        # 2. build selectable (if provided)
        # 3. Init everything
        #
        # Everything should be wrapped in try/excepts. All exceptions should
        #   be logged, but we include the warning in the function comment
        #   in case.

        # determine type
        sp_type = _validate_type(jobj)
        if sp_type is None:
            return

        # check name and img_sit
        msg_log = []
        _validate_params(
            jobj,
            sp_obj_params,
            REQ_SHARED_PARAM_NAMES,
            True,
            msg_log,
            indent_lvl
        )
        if parsewritelogs(msg_log):
            return

        # save name for later
        sp_name = sp_obj_params["name"]

        # log out that we are loading the sprite object and name
        writelog(MSG_INFO.format(SP_LOADING.format(
            SP_STR.get(sp_type),
            sp_name
        )))
        indent_lvl = 1

        # check for existence of pose_map property. We will not validate until
        # later.
        if "pose_map" not in jobj:
            parsewritelog((MSG_ERR_T, indent_lvl, REQ_MISS.format("pose_map")))
            return

        # move object-based params out of the jobj
        for param_name in OBJ_BASED_PARAM_NAMES:
            if param_name in jobj:
                obj_val = jobj.pop(param_name)

                # objects must be dicts
                if not _verify_dict(obj_val, allow_none=False):
                    parsewritelog((
                        MSG_ERR_T,
                        indent_lvl,
                        BAD_TYPE.format(param_name, dict, type(obj_val))
                    ))
                    return

                obj_based_params[param_name] = obj_val

        # validate optional shared params
        msg_log = []
        _validate_params(
            jobj,
            sp_obj_params,
            OPT_SHARED_PARAM_NAMES,
            False,
            msg_log,
            indent_lvl
        )
        if parsewritelogs(msg_log):
            return

        # now for specific params
        if sp_type == SP_ACS:
            # ACS
            msg_log = []
            _validate_acs(
                jobj,
                sp_obj_params,
                obj_based_params,
                msg_log,
                indent_lvl
            )
            if parsewritelogs(msg_log):
                return

        else:
            # hair / clothes
            msg_log = []
            _validate_fallbacks(
                jobj,
                sp_obj_params,
                obj_based_params,
                msg_log,
                indent_lvl
            )
            if parsewritelogs(msg_log):
                return

            if sp_type == SP_HAIR:
                msg_log = []
                _validate_hair(
                    jobj,
                    sp_obj_params,
                    obj_based_params,
                    msg_log,
                    indent_lvl
                )
                if parsewritelogs(msg_log):
                    return

            else:
                # must be clothes
                msg_log = []
                _validate_clothes(
                    jobj,
                    sp_obj_params,
                    obj_based_params,
                    sp_name,
                    dry_run,
                    msg_log,
                    indent_lvl
                )
                if parsewritelogs(msg_log):
                    return

        # back to shared acs/hair/clothes stuff
        msg_log = []
        _validate_ex_props(
            jobj,
            sp_obj_params,
            obj_based_params,
            msg_log,
            indent_lvl
        )
        if parsewritelogs(msg_log):
            return

        # select info if found
        if "select_info" in obj_based_params:
            msg_log = []
            _validate_selectable(
                jobj,
                sel_params,
                obj_based_params,
                msg_log,
                indent_lvl
            )
            if parsewritelogs(msg_log):
                return

        # time to check for warnings/recommendes

        # extra property warnings
        for extra_prop in jobj:
            parsewritelog((
                MSG_WARN_T,
                indent_lvl,
                EXTRA_PROP.format(extra_prop)
            ))

        # no gift/unlock warnings
        if "unlock" in sp_obj_params:
            unlock_hair = sp_obj_params.pop("unlock")
            giftname = None

        elif "giftname" in sp_obj_params:
            giftname = sp_obj_params.pop("giftname")

            # validate gift stuff
            msg_log = []
            _check_giftname(giftname, sp_type, sp_name, msg_log, indent_lvl)
            if parsewritelogs(msg_log):
                return

        elif sp_type != SP_HAIR:
            parsewritelog((MSG_WARN_T, indent_lvl, NO_GIFT))
            giftname = None

        # progpoint processing
        msg_log = []
        _process_progpoint(
            sp_type,
            sp_name,
            sp_obj_params,
            msg_log,
            indent_lvl,
            "entry"
        )
        _process_progpoint(
            sp_type,
            sp_name,
            sp_obj_params,
            msg_log,
            indent_lvl,
            "exit"
        )
        parsewritelogs(msg_log)

        # now we can build the sprites
        try:
            #writelog(str(sp_obj_params))
            if sp_type == SP_ACS:

                if "arm_split" in sp_obj_params:
                    # must be split accessory
                    sp_obj = store.MASSplitAccessory(**sp_obj_params)

                else:
                    # normal accessory
                    sp_obj = store.MASAccessory(**sp_obj_params)

                sms.init_acs(sp_obj)
                sel_obj_name = "acs"

            elif sp_type == SP_HAIR:
                sp_obj = store.MASHair(**sp_obj_params)
                sms.init_hair(sp_obj)
                sel_obj_name = "hair"

            else:
                # clothing
                sp_obj = store.MASClothes(**sp_obj_params)
                sms.init_clothes(sp_obj)
                sel_obj_name = "clothes"

        except Exception as e:
            # in thise case, we ended up with a duplicate
            writelog(MSG_ERR.format(traceback.format_exc()))
            return

        # check image loadables
        msg_log = []
        _test_loadables(sp_obj, msg_log, 0)
        if parsewritelogs(msg_log):
            _reset_sp_obj(sp_obj)
            return

        # otherwise, we were successful in initializing this sprite
        # try initializing the selectable if we parsed it
        if len(sel_params) > 0:
            sel_params[sel_obj_name] = sp_obj

            try:
                if sp_type == SP_ACS:
                    sml.init_selectable_acs(**sel_params)

                elif sp_type == SP_HAIR:
                    sml.init_selectable_hair(**sel_params)
                    if unlock_hair:
                        sml.unlock_hair(sp_obj)

                else:
                    # clothing
                    sml.init_selectable_clothes(**sel_params)

            except Exception as e:
                # we probably ended up with a duplicate again
                writelog(MSG_ERR.format(e.message))

                # undo the sprite init
                _reset_sp_obj(sp_obj)
                return

        # giftname must be valid by here
        if giftname is not None and not dry_run:
            _init_giftname(giftname, sp_type, sp_name)

        # alright! we have built the sprite object!
        if dry_run:
            _reset_sp_obj(sp_obj)
            writelog(MSG_INFO.format(SP_SUCCESS_DRY.format(
                SP_STR.get(sp_type),
                sp_name
            )))

        else:
            sp_obj.is_custom = True
            writelog(MSG_INFO.format(SP_SUCCESS.format(
                SP_STR.get(sp_type),
                sp_name
            )))


    def addSpriteObjects():
        """
        Adds sprite objects if we find any

        Also does delayed validation rules:
            - hair
        """
        json_files = sprite_station.getPackageList(".json")

        if len(json_files) < 1:
            return

        # otherwise we have stuff
        for j_obj in json_files:
            j_path = sprite_station.station + j_obj
            try:
                addSpriteObject(j_path)
            except Exception as e:
                writelog(MSG_ERR.format(traceback.format_exc()))


    def initSpriteObjectProc():
        """
        Prepares internal data for sprite object processing
        """
        pass


    def verifyHairs():
        """
        Verifies all hair items that we encountered
        """
        writelog("\n" + MSG_INFO.format(HM_VER_ALL))

        # start with keys
        for hkey in hm_key_delayed_veri:
            if hkey not in HAIR_MAP:
                parsewritelog((
                    MSG_WARN_T,
                    1,
                    HM_NO_KEY.format(hkey, hm_key_delayed_veri[hkey])
                ))

        # now for values
        for hval in hm_val_delayed_veri:
            if hval not in HAIR_MAP:
                sp_name_list = hm_val_delayed_veri[hval]
                parsewritelog((
                    MSG_WARN_T,
                    1,
                    HM_NO_VAL.format(hval, sp_name_list)
                ))

                # also clean the values
                for sp_name in sp_name_list:
                    _replace_hair_map(sp_name, hval)

        writelog(MSG_INFO.format(HM_VER_SUCCESS))


    def _addGift(giftname, indent_lvl):
        """
        Adds the reaction for this gift, using the correct label depending on
        gift label existence.

        IN:
            giftname - giftname to add reaction for
            indent_lvl - indentation level to use
        """
        namegift = giftname_map.get(giftname, None)
        if namegift is None:
            return

        gifttype, spname = namegift
        rlstr = SP_RL.get(gifttype,  None)
        if rlstr is None:
            return

        # only add this reaction if we have a label for it
        reaction_label = rlstr.format(spname)
        if renpy.has_label(reaction_label):
            store.addReaction(reaction_label, giftname, is_good=True)
            parsewritelog((
                MSG_INFO_T,
                indent_lvl,
                GR_FOUND.format(SP_STR.get(gifttype), spname, giftname)
            ))

        else:
            parsewritelog((
                MSG_INFO_T,
                indent_lvl,
                GR_GEN.format(SP_STR.get(gifttype), spname, giftname)
            ))


    def processGifts():
        """
        Processes giftnames that were loaded, adding/removing them from
        certain dicts.
        """
        writelog("\n" + MSG_INFO.format(GR_LOADING))

        frs_gifts = store.persistent._mas_filereacts_sprite_gifts
        msj_gifts = store.persistent._mas_sprites_json_gifted_sprites

        for giftname in frs_gifts.keys():
            if giftname in giftname_map:
                # overwrite the gift data if in here
                frs_gifts[giftname] = giftname_map[giftname]

            else:
                # remove if not in here
                frs_gifts.pop(giftname)

        # now go through the giftnames and update persistent data as well
        # and add them to reactions
        for giftname in giftname_map:
            if not giftname.startswith("__"):
                sp_data = giftname_map[giftname]

                # no testing labels
                if sp_data in msj_gifts:
                    # alrady unlocked, but overwrite data
                    msj_gifts[sp_data] = giftname

                # always add the gift
                frs_gifts[giftname] = sp_data

                # now we always add the gift
                _addGift(giftname, 1)

        writelog(MSG_INFO.format(GR_SUCCESS))


init 190 python in mas_sprites_json:
    # NOTE: must be before 200, which is when saved selector data is loaded

    # prepare the alg
    initSpriteObjectProc()

    # run the alg
    addSpriteObjects()
    verifyHairs()

    # reaction setup
    processGifts()
