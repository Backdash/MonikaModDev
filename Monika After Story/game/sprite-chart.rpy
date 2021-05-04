# Monika's sprites!
# To add new images, use the sprite adder tool in MonikaModDev/tools/toolsmenu
#
###### SPRITE CODE (IMG010)
#
# The sprite code system is a way of picking an appropriate sprite without
# having to look up what the sprite looks like.
# All expressions use this code system. the original 19 expressions (with
# counterparts have been aliased to the correct code system. Please avoid
# using the og 19+ coutnerparts)
#
# For aliases, see [IMG032]
#
# The sprite code system consists of:
# <pose number><eyes type><eyebrow type><nose type><eyebag type><blush type>
# <tears type><sweat type><emote type><mouth type>
#
# Only <pose number><eyes type><eyebrow type><mouth type> are required
#
# Here are the available values for each type:
# <pose number> - arms/body pose to use
#   1 - resting on hands (steepling)
#   2 - arms crossed (crossed)
#   3 - resting on left arm, pointing to the right (restleftpointright)
#   4 - pointing right (pointright)
#   5 - leaning (def)
#   6 - arms down (down)
#   7 - down left arm, rest point right (downleftpointright)
#
# <eyes type> - type of eyes
#   e - normal eyes (normal)
#   w - wide eyes (wide)
#   s - sparkly eyes (sparkle)
#   t - straight/smug eyes (smug)
#   c - crazy eyes (crazy)
#   r - look right eyes (right)
#   l - look left eyes (left)
#   h - closed happy eyes (closedhappy)
#   d - closed sad eyes (closedsad)
#   k - left eye wink (winkleft)
#   n - right eye wink (winkright)
#   f - soft eyes (soft)
#   m - left smug (smugleft)
#   g - right smug (smugright)
#
# <eyebrow type> - type of eyebrow
#   f - furrowed / angery (furrowed)
#   u - up / happy (up)
#   k - knit / upset / concerned (knit)
#   s - straight / normal / regular (mid)
#   t - thinking (think)
#
# <nose type> - type of nose
#   nd - default nose (def) NOTE: UNUSED
#
# <eyebag type> - type of eyebags
#   ebd - default eyebags (def) NOTE: UNUSED
#
# <blush type> - type of blush
#   bl - blush lines (lines)
#   bs - blush shade (shade)
#   bf - full blush / lines and shade blush (full)
#
# <tears type> - type of tears
#   ts - tears streaming / running (streaming)
#   td - dried tears (dried)
#   tp - like dried tears but with no redness (pooled)
#   tu - tears, single stream, both eyes (up)
#
# <sweat type> - type of sweat drop
#   sdl - sweat drop left (def)
#   sdr - sweat drop right (right)
#
# <emote type> - type of emote
#   ec - confusion emote (confuse) NOTE: UNUSED
#
# <mouth type> - type of mouth
#   a - smile (smile)
#   b - open smile (big)
#   c - apathetic / straight mouth / neither smile nor frown (smirk)
#   d - open mouth (small)
#   o - gasp / open mouth (gasp)
#   u - smug (smug)
#   w - wide / open mouth (wide)
#   x - angery (angry)
#   p - tsundere/ puffy cheek (pout)
#   t - triangle (triangle)
#   g - disgust/uwah (disgust)
#
# For example, the expression code 1sub is:
#   1 - resting on hands pose
#   s - sparkly eyes
#   u - happy eyebrows
#   b - big open smile
#
# NOTE:
# not every possible combination has been created as an image. If you want
# a particular expression, make a github issue about it and why we need it.
#
# hmmmmmm (1etecc)

# This defines a dynamic displayable for Monika whose position and style changes
# depending on the variables is_sitting
define is_sitting = True

# accessories list
default persistent._mas_acs_pre_list = []
default persistent._mas_acs_bbh_list = []
default persistent._mas_acs_bse_list = []
default persistent._mas_acs_bba_list = []
default persistent._mas_acs_ase_list = []
default persistent._mas_acs_bmh_list = []
default persistent._mas_acs_mmh_list = []
default persistent._mas_acs_bat_list = []
default persistent._mas_acs_mat_list = []
default persistent._mas_acs_mab_list = []
default persistent._mas_acs_bfh_list = []
default persistent._mas_acs_afh_list = []
default persistent._mas_acs_mid_list = []
default persistent._mas_acs_pst_list = []

# zoom levels
default persistent._mas_zoom_zoom_level = None

default persistent._mas_force_clothes = False
# Set to True if the user manually set clothes

default persistent._mas_force_hair = False
# Set to True if the user manually set hair

default persistent._mas_last_ahoge_dt = None
# set to the dt of when we last set the ahoge

define m = DynamicCharacter('m_name', image='monika', what_prefix='', what_suffix='', ctc="ctc", ctc_position="fixed", show_function=store.mas_core.show_display_say)

#image night_filter = Solid("#20101897", xsize=1280, ysize=850)

image mas_finalnote_idle = "mod_assets/poem_finalfarewell_desk.png"

# Monika's piano sprite
image mas_piano = MASFilterSwitch("mod_assets/other/mas_piano.png")

init -10 python in mas_core:
    import renpy
    _last_text = None

    def show_display_say(who, what_string, **kwargs):
        """
        semi-override of show_display_say so we can force text to render
        immediately.
        """
        global _last_text
        rv = renpy.character.show_display_say(who, what_string, **kwargs)

        if isinstance(rv, tuple):
            # r7-specific handling.
            # purposely not doing *rv in case tom changes stuff again
            rv = renpy.display.screen.get_widget(rv[0], rv[1], rv[2])

        _last_text = rv
        return _last_text

### ACS TYPE + DEFAULTING FRAMEWORK ###########################################
# this contains special acs type mappings
# basically on startup, we evaluate each acs and add mux types and other
# properties.

init -101 python in mas_sprites:

    class ACSTemplate(renpy.store.object):
        """
        ACS template object
        Establishes guidelines for defauling properties for an ACS

        PROPERTIES:
            acs_type - the acs type associated with this template
            mux_type - the default mux type list for this template
            ex_props - default exprops dict for this template
            keep_on_desk - default keep on desk flag for this templat
        """

        def __init__(self,
                acs_type,
                mux_type=None,
                ex_props=None,
                keep_on_desk=None
        ):
            """
            Constructor

            IN:
                acs_type - acs type this template should be associated with
                mux_type - the mux_type we want to use as default. Ignored if
                    None.
                    (Default: None)
                ex_props - the ex_props we want to use as default. Ignored if
                    None.
                    (Default: None)
                keep_on_desk - the keep_on_desk flag we want to use as default.
                    Ignored if None.
                    (Default: None)
            """
            self.acs_type = acs_type
            self.mux_type = mux_type
            self.ex_props = ex_props
            self.keep_on_desk = keep_on_desk

        def _apply_ex_props(self, acs):
            """
            Applies ex prop defaults to the given ACS.

            acs_type is NOT checked.

            IN:
                acs - acs to modify
            """
            if self.ex_props is None:
                return

            if acs.ex_props is None:
                acs.ex_props = dict(self.ex_props)

            else:
                acs.ex_props.update(self.ex_props)

        def _apply_keep_on_desk(self, acs):
            """
            Applies keep_on_desk defaults to the given ACS.

            acs_type is NOT checked.

            IN:
                acs- acs to modify
            """
            if self.keep_on_desk is None:
                return

            acs.keep_on_desk = self.keep_on_desk

        def _apply_mux_type(self, acs):
            """
            Applies mux type defaults to the given ACS.

            acs_type is NOT checked.

            IN:
                acs - acs to modify.
            """
            if self.mux_type is None:
                return

            if acs.mux_type is None:
                acs.mux_type = list(self.mux_type)

            else:
                for mux_type in self.mux_type:
                    if mux_type not in acs.mux_type:
                        acs.mux_type.append(mux_type)

        def apply(self, acs):
            """
            Applies the defaults to the given ACS. (NOTE: acs type is checked)
            """
            if self.acs_type == acs.acs_type:
                self._apply_ex_props(acs)
                self._apply_keep_on_desk(acs)
                self._apply_mux_type(acs)


init -100 python in mas_sprites:

    # --- exprops ---

    # ---- ACS ----

    EXP_A_EXCLHP = "excluded-hair-props"
    # v: list of strings
    # marks that an ACS requires a hairstyle with none of the value'd props
    # to be worn

    EXP_A_LHSEL = "left-hair-strand-eye-level"
    # v: ignored
    # marks that an ACS is located at the left hair strand, eye level

    EXP_A_RQHP = "required-hair-prop"
    # v: string/list
    # marks that an ACS requires a hairstyle with the value'd prop(s) to be
    # worn

    EXP_A_LD = "left-desk-acs"
    # v: ignored
    # marks that this ACS is on the left side (Monika's left) of the desk

    EXP_A_RBL = "ribbon-like"
    # v: ignored
    # marks that an ACS is like a ribbon in function

    EXP_A_TWRB = "twin-ribbon"
    # v: ignored
    # marks that an ACS is a twin ribbon-based acs

    EXP_A_FOOD = "food"
    # v: ignored
    # marks that this ACS is a food

    EXP_A_DRINK = "drink"
    # v: ignored
    # marks that this ACS is a drink

    # ---- HAIR ----

    EXP_H_TT = "twintails"
    # v: ignored
    # marks that a hair style is a twintails style

    EXP_H_RQCP = "required-clothes-prop"
    # v: string/list
    # marks that a hair style requires clothes with the value'd prop(s) to be
    # worn

    EXP_H_EXCLCP = "excluded-clothes-props"
    # v: list of strings
    # marks that a hair style requires clothes with none of the value'd props
    # to be worn

    EXP_H_TS = "tiedstrand"
    # v: ignored
    # marks that a hair style is a tied strand style

    EXP_H_NT = "no-tails"
    # v: ignored
    # marks that a hair style has no tails. By default we assume ponytail.

    EXP_H_TB = "twinbraid"
    #v: ignored
    #marks the hair as a twinbraid hairstyle

    # ---- CLOTHES ----

    EXP_C_BLS = "bare-left-shoulder"
    # v: ignored
    # marks that a clothing item has a bare left shoulder
    # this is auto-added if bare-shoulders is added

    EXP_C_BRS = "bare-right-shoulder"
    # v: ignored
    # marks that a clothing item has a bare right shoulder
    # this is auto-added if bare-shoulders is added

    EXP_C_BS = "bare-shoulders"
    # v: ignored
    # marks that a clothing item has bare shoulders
    # this is auto-added if both left/right bare shoulders are added

    EXP_C_C_DTS = "compat-downtiedstrand"
    # v: ignored
    # compatibilty exprop saying that these clothes work with the 
    # downtiedstrand hair style
    # NOTE: THIS IS AN EXCEPTION. We should not be doing exprops like this.

    EXP_C_COST = "costume"
    # v: costume type as string (o31, d25, etc..)
    # marks that a clothing item is a costume

    EXP_C_COSP = "cosplay"
    # v: ignored
    # marks that a clothing item is a cosplay outfit

    EXP_C_LING = "lingerie"
    # v: ignored
    # marks that a clothing item is lingerie

    # --- default exprops ---

    DEF_EXP_TT_EXCL = [EXP_H_TT]
    # twin tail exclusions

    # --- default mux types ---

    DEF_MUX_AHOGE = [
        "ahoge",
        "hat",
    ]
    # default mux type for ahoges

    DEF_MUX_RB = [
        "ribbon",
        "bow",
        "bunny-scrunchie",
        "hat",
        "s-type-ribbon",
        "twin-ribbons",
    ]
    # default mux types for ribbon-based items.

    DEF_MUX_HS = [
        "headset",
        "earphones",
        "hat",
        "headband",
        "headphones",
        "left-hair-flower-ear",
    ]
    # default mux types for headset-based items

    DEF_MUX_HB = [
        "headband",
        "hat",
        "headphones",
        "headset",
    ]
    # default mux types for headband-based items

    DEF_MUX_LHC = ["left-hair-clip"]
    # default mux types for left hair clip-based items

    DEF_MUX_LHFE = [
        "left-hair-flower-ear",
        "earphones",
        "front-hair-flower-crown",
        "hat",
        "headset",
        "headphones",
        "left-hair-flower",
    ]
    # default mux types for left hair flower-baesd items

    DEF_MUX_LD = [
        "plush_q",
        "chocs",
        "plate"
    ]
    # default mux types for left-desk related items (namely foods)

    DEF_MUX_HAT = [
        "ahoge",
        "hat",
        "bow",
        "bunny-scrunchie",
        "earphones",
        "front-hair-flower-crown",
        "headband",
        "headphones",
        "headset",
        "left-hair-flower",
        "ribbon",
        "s-type-ribbon",
        "twin-ribbons",
    ]
    # default mux types for hats

    # maps ACS types to their ACS template
    ACS_DEFS = {
        "ahoge": ACSTemplate(
            "ahoge",
            mux_type=DEF_MUX_AHOGE,
        ),
        "bow": ACSTemplate(
            "bow",
            mux_type=DEF_MUX_RB,
            ex_props={
                EXP_A_RBL: True,
                EXP_A_EXCLHP: DEF_EXP_TT_EXCL,
            }
        ),
        "bunny-scrunchie": ACSTemplate(
            "bunny-scrunchie",
            mux_type=DEF_MUX_RB,
            ex_props={
                EXP_A_RBL: True,
                EXP_A_EXCLHP: DEF_EXP_TT_EXCL,
            }
        ),
        "choker": ACSTemplate(
            "choker",
            mux_type=["choker"],
            ex_props={
                "bare neck": True
            }
        ),
        "front-hair-flower-crown": ACSTemplate(
            "front-hair-flower-crown",
            mux_type=DEF_MUX_LHFE,
            ex_props={
                "front-hair-crown": True,
            },
        ),
        "hat": ACSTemplate(
            "hat",
            mux_type=DEF_MUX_HAT
        ),
        "headband": ACSTemplate(
            "headband",
            mux_type=DEF_MUX_HB
        ),
        "headset": ACSTemplate(
            "headset",
            mux_type=DEF_MUX_HS
        ),
        "left-hair-clip": ACSTemplate(
            "left-hair-clip",
            mux_type=DEF_MUX_LHC,
            ex_props={
                EXP_A_LHSEL: True
            }
        ),
        "left-hair-flower": ACSTemplate(
            "left-hair-flower",
            mux_type=[
                "left-hair-flower",
                "left-hair-flower-ear",
                "front-hair-flower-crown"
            ],
            ex_props={
                EXP_A_LHSEL: True
            }
        ),
        "left-hair-flower-ear": ACSTemplate(
            "left-hair-flower-ear",
            mux_type=DEF_MUX_LHFE,
            ex_props={
                EXP_A_LHSEL: True
            }
        ),
        "mug": ACSTemplate(
            "mug",
            mux_type=["mug", "thermos-mug"],
            keep_on_desk=True,
            ex_props={
                EXP_A_DRINK: True
            }
        ),
        "necklace": ACSTemplate(
            "necklace",
            mux_type=["necklace"],
            ex_props={
                "bare collar": True,
            }
        ),
        "plate": ACSTemplate(
            "plate",
            mux_type=DEF_MUX_LD,
            keep_on_desk=True,
            ex_props={
                EXP_A_LD: True,
                EXP_A_FOOD: True
            }
        ),
        # ring
        "ribbon": ACSTemplate(
            "ribbon",
            mux_type=DEF_MUX_RB
        ),
        "s-type-ribbon": ACSTemplate(
            "s-type-ribbon",
            mux_type=DEF_MUX_RB,
            ex_props={
                EXP_A_RBL: True,
            }
        ),
        "thermos-mug": ACSTemplate(
            "thermos-mug",
            mux_type=["mug", "thermos-mug"],
            keep_on_desk=False
        ),
        "twin-ribbons": ACSTemplate(
            "twin-ribbons",
            mux_type=DEF_MUX_RB,
            ex_props={
                EXP_A_TWRB: True,
                EXP_A_RBL: True,
                EXP_A_RQHP: [EXP_H_TT],
            }
        ),
        "wrist-bracelet": ACSTemplate(
            "wrist-bracelet",
            mux_type=["wrist-bracelet"],
            ex_props={
                "bare wrist": True,
            }
        ),
    }


    def apply_ACSTemplate(acs):
        """
        Applies ACS template to the given ACS

        IN:
            acs - acs to apply defaults to
        """
        template = get_ACSTemplate(acs)
        if template is not None:
            template.apply(acs)


    def apply_ACSTemplates():
        """RUNTIME ONLY
        Applies all templates to the available ACS.
        """
        for acs_name in ACS_MAP:
            apply_ACSTemplate(ACS_MAP[acs_name])


    def get_ACSTemplate(acs):
        """
        Gets the template for an ACS given the ACS.

        IN:
            acs - acs to get template for

        RETURNS: ACSTemplate associated with the acs, or None if not found
        """
        if acs is None:
            return None
        return get_ACSTemplate_by_type(acs.acs_type)


    def get_ACSTemplate_by_type(acs_type):
        """
        Gets the template for an ACS given the ACS type

        IN:
            acs_type - acs type to get template for

        RETURNS: ACSTemplate associated with the acs_type or Nonr if not ound
        """
        return ACS_DEFS.get(acs_type, None)


init -5 python in mas_sprites:
    # specific image generation functions
    import store

    # main art path
    MOD_ART_PATH = "mod_assets/monika/"
    STOCK_ART_PATH = "monika/"

    # delimiters
    ART_DLM = "-"

    # important keywords
    KW_STOCK_ART = "def"

    ### other paths:
    # H - hair
    # C - clothing
    # B - base
    # F - face parts
    # A - accessories
    # S - standing
    # T - table
    H_MAIN = MOD_ART_PATH + "h/"
    C_MAIN = MOD_ART_PATH + "c/"
    B_MAIN = MOD_ART_PATH + "b/"
    F_MAIN = MOD_ART_PATH + "f/"
    A_MAIN = MOD_ART_PATH + "a/"
    S_MAIN = MOD_ART_PATH + "s/"
    T_MAIN = MOD_ART_PATH + "t/"

    # sitting standing parts
#    S_MAIN = "standing/"

    # facial parts
    F_T_MAIN = F_MAIN
#    F_S_MAIN = F_MAIN + S_MAIN

    # accessories parts
    A_T_MAIN = A_MAIN

    ### End paths

    # location stuff for some of the compsoite
    LOC_REG = "(1280, 850)"
    LOC_LEAN = "(1280, 850)"
    LOC_Z = "(0, 0)"
    LOC_STAND = "(960, 960)"

    LOC_W = 1280
    LOC_H = 850
    LOC_WH = (1280, 850)

    # composite stuff
    I_COMP = "im.Composite"
    L_COMP = "LiveComposite"
    TRAN = "Transform"

    # zoom
    ZOOM = "zoom="

    default_zoom_level = 3

    if store.persistent._mas_zoom_zoom_level is None:
        store.persistent._mas_zoom_zoom_level = default_zoom_level
        zoom_level = default_zoom_level

    else:
        zoom_level = store.persistent._mas_zoom_zoom_level

    zoom_step = 0.05
    default_value_zoom = 1.25
    value_zoom = default_value_zoom
    max_zoom = 20

    # adjustable location stuff
    default_x = 0
    default_y = 0
    adjust_x = default_x
    adjust_y = default_y
#    y_step = 40
    y_step = 20

    # adding optimized initial parts of the sprite string
    PRE_SPRITE_STR = TRAN + "(" + L_COMP + "("

    # Prefixes for files
    PREFIX_TORSO = "torso" + ART_DLM
    PREFIX_TORSO_LEAN = "torso-leaning" + ART_DLM
    PREFIX_BODY = "body" + ART_DLM
    PREFIX_BODY_LEAN = "body-leaning" + ART_DLM
    PREFIX_HAIR = "hair" + ART_DLM
    PREFIX_HAIR_LEAN = "hair-leaning" + ART_DLM
    PREFIX_ARMS = "arms" + ART_DLM
    PREFIX_ARMS_LEAN = "arms-leaning" + ART_DLM
    PREFIX_ARMS_LEFT = "left" + ART_DLM
    PREFIX_ARMS_RIGHT = "right" + ART_DLM
    PREFIX_FACE = "face" + ART_DLM
    PREFIX_FACE_LEAN = "face-leaning" + ART_DLM
    PREFIX_ACS = "acs" + ART_DLM
    PREFIX_ACS_LEAN = "acs-leaning" + ART_DLM
    PREFIX_EYEB = "eyebrows" + ART_DLM
    PREFIX_EYES = "eyes" + ART_DLM
    PREFIX_NOSE = "nose" + ART_DLM
    PREFIX_MOUTH = "mouth" + ART_DLM
    PREFIX_SWEAT = "sweatdrop" + ART_DLM
    PREFIX_EMOTE = "emote" + ART_DLM
    PREFIX_TEARS = "tears" + ART_DLM
    PREFIX_EYEG = "eyebags" + ART_DLM
    PREFIX_BLUSH = "blush" + ART_DLM
    PREFIX_TABLE = "table" + ART_DLM
    PREFIX_CHAIR = "chair" + ART_DLM

    # keys
    FHAIR = "front"
    BHAIR = "back"
    MHAIR = "mid"

    # head
    HEAD = "head"

    # suffixes
    NIGHT_SUFFIX = ART_DLM + "n"
    SHADOW_SUFFIX = ART_DLM + "s"
    FHAIR_SUFFIX  = ART_DLM + FHAIR
    BHAIR_SUFFIX = ART_DLM + BHAIR
    MHAIR_SUFFIX = ART_DLM + MHAIR
    HLITE_SUFFIX = ART_DLM + "h"
    FILE_EXT = ".png"

    # other const
    DEF_BODY = "def"
    NEW_BODY_STR = PREFIX_BODY + DEF_BODY

    # base constants
    BASE_BODY_STR = PREFIX_BODY + DEF_BODY + ART_DLM
    BASE_BODY_STR_LEAN = PREFIX_BODY_LEAN + DEF_BODY + ART_DLM

    # table strings
    TC_GEN = "".join((
        T_MAIN,
        "{0}", # prefix table or chair
        "{1}", # table or chair tag
        "{2}", # shadow suffix
        "{3}", # night suffix
        FILE_EXT
    ))


    def alt_bcode(v_list, prefix, inc_night):
        """
        Adds bcode 0 and bcode 1 versions of the given prefix to the given
        list.

        IN:
            prefix - string to add bcode to
            inc_night - if True, then we also do night variants of each bcode
                version, otherwise, just day versions

        OUT:
            v_list - list to add strings to
        """
        if inc_night:
            alt_night(v_list, prefix + ART_DLM + "0")
            alt_night(v_list, prefix + ART_DLM + "1")

        else:
            v_list.append(prefix + ART_DLM + "0" + FILE_EXT)
            v_list.append(prefix + ART_DLM + "1" + FILE_EXT)


    def alt_hsplit(v_list, prefix, inc_night):
        """
        Adds backhair/front hair versionsof the given prefix to the given list

        IN:
            prefix - string to add bhair/front hair to
            inc_night - if Ture, then we also do night varaints of each bhair
                fhair version, otherwise just day versions

        OUT:
            v_list - list to add strings to
        """
        if inc_night:
            alt_night(v_list, prefix + FHAIR_SUFFIX)
            alt_night(v_list, prefix + BHAIR_SUFFIX)

        else:
            v_list.append(prefix + FHAIR_SUFFIX + FILE_EXT)
            v_list.append(prefix + BHAIR_SUFFIX + FILE_EXT)


    ## BLK010
    # ACCESSORY BLACKLIST
    lean_acs_blacklist = [
        "test"
    ]

    # list of available hairstyles
    HAIRS = [
        "def", # ponytail
        "down" # hair down
    ]

    # list of available clothes
    CLOTHES = [
        "def" # school uniform
    ]

    # zoom adjuster
    def adjust_zoom():
        """
        Sets the value zoom to an appropraite amoutn based on the current
        zoom level.
        NOTE: also sets the persistent save for zoom
        """
        global value_zoom, adjust_y
        if zoom_level > default_zoom_level:
            value_zoom = default_value_zoom + (
                (zoom_level-default_zoom_level) * zoom_step
            )
            adjust_y = default_y + ((zoom_level-default_zoom_level) * y_step)

        elif zoom_level < default_zoom_level:
            value_zoom = default_value_zoom - (
                (default_zoom_level-zoom_level) * zoom_step
            )
            adjust_y = default_y
        else:
            # zoom level is at 10
            value_zoom = default_value_zoom
            adjust_y = default_y

        store.persistent._mas_zoom_zoom_level = zoom_level


    def reset_zoom():
        """
        Resets the zoom to the default value
        NOTE: also set sthe persistent save for zoom
        """
        global zoom_level
        zoom_level = default_zoom_level
        adjust_zoom()


    def zoom_out():
        """
        zooms out to the farthest zoom level
        NOTE: also sets the persistent save for zoom
        """
        global zoom_level
        zoom_level = 0
        adjust_zoom()


    # tryparses for the hair and clothes
    # TODO: adjust this for docking station when ready
    def tryparsehair(_hair, default="def"):
        """
        Returns the given hair if it exists, or the default if not exist

        IN:
            _hair - hair to check for existence
            default - default if hair dont exist

        RETURNS:
            the hair if it exists, or default if not
        """
        if _hair in HAIRS:
            return _hair

        return default


    # TODO: adjust this for docking station when ready
    def tryparseclothes(_clothes, default="def"):
        """
        Returns the given clothes if it exists, or the default if not exist

        IN:
            _clothes - clothes to check for existence
            default - default if clothes dont exist

        RETURNS:
            the clothes if it exists, or default if not
        """
        if _clothes in CLOTHES:
            return _clothes

        return default


    ## Accessory dictionary
    ACS_MAP = dict()

    ## hair dictionary
    HAIR_MAP = dict()

    ## clothes dictionary
    CLOTH_MAP = dict()

    ### SP CONSTANTS
    SP_ACS = store.mas_sprites_json.SP_ACS
    SP_HAIR = store.mas_sprites_json.SP_HAIR
    SP_CLOTHES = store.mas_sprites_json.SP_CLOTHES

    SP_MAP = {
        SP_ACS: ACS_MAP,
        SP_HAIR: HAIR_MAP,
        SP_CLOTHES: CLOTH_MAP
    }

    # available lean types
    LEAN_TYPES = [
        "def"
    ]

    # Numerical pose map
    NUM_POSE = {
        1: "steepling",
        2: "crossed",
        3: "restleftpointright",
        4: "pointright",
        5: "def|def",
        6: "down",
        7: "downleftpointright",
    }

    ## Pose list
    # NOTE: do NOT include leans in here.
    POSES = [
        NUM_POSE[1],
        NUM_POSE[2],
        NUM_POSE[3],
        NUM_POSE[4],
        NUM_POSE[6],
        NUM_POSE[7],
    ]

    ## lean poses
    # NOTE: these should be like:
    #   lean|arms
    # NOTE: do NOT include regular poses in here
    L_POSES = [
        NUM_POSE[5],
    ]

    # all poses
    # this is purely for iterative purposes
    ALL_POSES = []
    ALL_POSES.extend(POSES)
    ALL_POSES.extend(L_POSES)

    # arms
    NUM_ARMS = {
        1: "crossed",
        2: "left-down",
        3: "left-rest",
        4: "right-down",
        5: "right-point",
        6: "right-restpoint",
        7: "steepling",
        8: "def|left-def",
        9: "def|right-def",
    }

    # NOTE: arm mapping happens at the base level
    ARMS = list(NUM_ARMS.values())

    # leaning arms
    # NOTE: no number should be linked to more than one lean type
    LEAN_ARMS = {
        LEAN_TYPES[0]: (8, 9),
    }

    # reverse map for eaiser lookup
    ARMS_LEAN = {}
    for lean, values in LEAN_ARMS.iteritems():
        for value in values:
            ARMS_LEAN[value] = lean

    # sprite exprop - list of topics
    EXPROP_TOPIC_MAP = {
        EXP_A_LHSEL: [
            "monika_hairclip_select"
        ],
    }

    # sprite acs type - topic
    ACSTYPE_TOPIC_MAP = {
        "ribbon": "monika_ribbon_select"
    }

    def _genLK(keys):
        """
        generates a tuple of keys + leanables using the given kens

        Leanable Keys are keys prefixed with a lean type like: <lean>|<key>

        IN:
            keys - iterable of keys to use

        RETURNS: tuple of keys + leanable keys
        """
        key_list = list(keys)
        for lean in LEAN_TYPES:
            key_list.extend([lean + "|" + key for key in keys])

        return tuple(key_list)


    def _verify_uprightpose(val):
        return val in POSES


    def _verify_lean(val):
        return val in LEAN_TYPES


    def _verify_leaningpose(val):
        return val in L_POSES


    def _verify_pose(val, allow_none=True):
        if val is None:
            return allow_none
        return _verify_uprightpose(val) or _verify_leaningpose(val)


    def acs_lean_mode(sprite_list, lean):
        """
        NOTE: DEPRECATED

        Adds the appropriate accessory prefix dpenedong on lean

        IN:
            sprite_list - list to add sprites to
            lean - type of lean
        """
        if lean:
            sprite_list.extend((
                PREFIX_ACS_LEAN,
                lean,
                ART_DLM
            ))

        else:
            sprite_list.append(PREFIX_ACS)


    def face_lean_mode(lean):
        """
        Returns the appropriate face prefix depending on lean

        IN:
            lean - type of lean

        RETURNS:
            appropriat eface prefix string
        """
        if lean:
            return "".join((
                PREFIX_FACE_LEAN,
                lean,
                ART_DLM
            ))

        return PREFIX_FACE


    def create_remover(acs_type, group, mux_types):
        """
        Creates a remover ACS

        IN:
            acs_type - acs type for the remover. This is also used in mux_type
            group - group of selectables this ACS remover should be linked to
                This is used in the naming of the ACS.
            mux_types - list of types to use for mux_type

        RETURNS: remover ACS object
        """
        remover_acs = store.MASAccessory(
            group + "-remover",
            "ribbon_blank",
            store.MASPoseMap(
                default="0",
                use_reg_for_l=True
            ),
            stay_on_start=False,
            acs_type=acs_type,
            mux_type=mux_types
        )
        init_acs(remover_acs)
        return remover_acs


    def get_acs(acs_name):
        """
        Gets the ACS object for a given name from the ACS map

        IN:
            acs_name - name of the ACS to get

        RETURNS: ACS object, or None if no acs object with the given name
        """
        return ACS_MAP.get(acs_name, None)


    def get_acs_of_type(acs_type):
        """
        Gets all ACS objects for a given ACS type.

        IN:
            acs_type - type of ACS to get

        RETURNS: list of ACS objects with the given type. list may be empty
            if no ACS of the given type
        """
        return [
            acs for acs in ACS_MAP.itervalues()
            if acs.acs_type == acs_type
        ]


    def init_acs(mas_acs):
        """
        Initlializes the given MAS accessory into a dictionary map setting

        IN:
            mas_acs - MASAccessory to initialize
        """
        if mas_acs.name in ACS_MAP:
            raise Exception(
                "MASAccessory name '{0}' already exists.".format(mas_acs.name)
            )

        # otherwise, unique name
        ACS_MAP[mas_acs.name] = mas_acs


    def init_hair(mas_hair):
        """
        Initlializes the given MAS hairstyle into a dictionary map setting

        IN:
            mas_hair - MASHair to initialize
        """
        if mas_hair.name in HAIR_MAP:
            raise Exception(
                "MASHair name '{0}' already exists.".format(mas_hair.name)
            )

        # otherwise, unique name
        HAIR_MAP[mas_hair.name] = mas_hair


    def init_clothes(mas_cloth):
        """
        Initlializes the given MAS clothes into a dictionary map setting

        IN:
            mas_clothes - MASClothes to initialize
        """
        if mas_cloth.name in CLOTH_MAP:
            raise Exception(
                "MASClothes name '{0}' already exists.".format(mas_cloth.name)
            )

        # otherwise, unique name
        CLOTH_MAP[mas_cloth.name] = mas_cloth


    def rm_acs(acs):
        """
        Deletes an ACS by removing it from the map

        IN:
            acs - ACS to remove
        """
        if acs.name in ACS_MAP:
            ACS_MAP.pop(acs.name)


    def lock_exprop_topics(exprop):
        """
        Locks topics with the given exprop

        IN:
            exprop - extended property to lock associated topics wtih
        """
        topic_list = EXPROP_TOPIC_MAP.get(exprop, None)
        if topic_list is not None:
            for topic in topic_list:
                store.mas_lockEVL(topic, "EVE")


    def lock_acstype_topics(acs_type):
        """
        Locks topics with the given acs type

        IN:
            acstype - acs type to lock assicated topics with
        """
        topic_label = ACSTYPE_TOPIC_MAP.get(acs_type, None)
        if topic_label is not None:
            store.mas_lockEVL(topic_label, "EVE")


    def unlock_exprop_topics(exprop):
        """
        Unlocks topics with the given exprop

        IN:
            exprop - extended property to unlock associated topics with
        """
        topic_list = EXPROP_TOPIC_MAP.get(exprop, None)
        if topic_list is not None:
            for topic in topic_list:
                store.mas_unlockEVL(topic, "EVE")


    def unlock_acstype_topics(acs_type):
        """
        Unlocks topics with the given acs type

        IN:
            acstype - acs type to unlock associated topics with
        """
        topic_label = ACSTYPE_TOPIC_MAP.get(acs_type, None)
        if topic_label is not None:
            store.mas_unlockEVL(topic, "EVE")


    def should_disable_lean(lean, arms, character):
        """
        Figures out if we need to disable the lean or not based on current
        character settings

        IN:
            lean - lean type we want to do
            arms - arms type involved with lean
            character - MASMonika object

        RETURNS:
            True if we should disable lean, False otherwise
        """
        if lean is None:
            return False

        # otherwise check blacklist elements
        if len(character.lean_acs_blacklist) > 0:
            # monika is wearing a blacklisted accessory
            return True

        larms = lean + "|" + arms

        if not character.hair.pose_map.l_map.get(larms, False):
            return True

        if not character.clothes.pose_map.l_map.get(larms, False):
            return True

        # otherwise, this is good
        return False


    def build_loc():
        """
        RETURNS location string for the sprite
        """
        return "".join(("(", str(adjust_x), ",", str(adjust_y), ")"))


    def build_loc_val():
        """
        RETURNS location tuple for a sprite
        """
        return (adjust_x, adjust_y)


    def get_sprite(sprite_type, sprite_name):
        """
        Returns the sprite object with the given sprite name and sprite type.
        Or None if we couldn't find one.
        """
        # NOTE: we have to use the module because we need updated maps.
        sprite_map = SP_MAP.get(sprite_type, None)
        if sprite_map is None:
            return None

        # otherwise we have a map
        return sprite_map.get(sprite_name, None)


##### special mas monika functions (hooks)
    # NOTE: set flag "abort" to True in prechange points to prevent
    #   change/add/removal. This is dependent on the specific hook.
    #   ACS: only wear_mux_pre_change and rm_exit_pre_change
    #   HAIR: hair_exit_pre_change
    #   CLOTHES: clothes_exit_pre_change
    # NOTE: available temp_space flags by type:
    #   ACS:
    #       abort - see above
    #       acs_list - list of acs Monika is currently wearing
    #
    #   HAIR:
    #       abort - see above
    #       by_user - True if set by the user, False if not
    #       startup - True if we are in startup flow, false if not
    #
    #   CLOTHES:
    #       abort - see above
    #       by_user - same as hair
    #       startup - same as hair
    #       outfit_mode - True if in outfit mode, False if not

    def acs_rm_exit_pre_change(temp_space, moni_chr, rm_acs, acs_loc):
        """
        Runs before exit point runs for acs

        IN:
            temp_space - temp space
            moni_chr - MASMonika object
            rm_acs - acs we are removing
            acs_loc - acs location to rm this acs from
        """
        pass


    def acs_rm_exit_pst_change(temp_space, moni_chr, rm_acs, acs_loc):
        """
        Runs after exit point runs runs for acs

        IN:
            temp_space - temp space
            moni_chr - MASMonika object
            rm_acs - acs we are removing
            acs_loc -  acs location to rm this acs from
        """
        if store.mas_selspr.in_prompt_map(rm_acs.acs_type):
            store.mas_selspr.set_prompt(rm_acs.acs_type, "wear")


    def acs_rm_exit_pst_removal(temp_space, moni_chr, rm_acs, acs_loc):
        """
        Runs after the ACS is removed

        IN:
            temp_space - temp space
            moni_chr - MASMonika object
            rm_acs - acs we are removing
            acs_loc - acs location the ACS was removed from
        """
        # if removing hat, wear ahoge if we have any
        if rm_acs.acs_type == "hat" and moni_chr.last_ahoge is not None:
            moni_chr.wear_acs(moni_chr.last_ahoge)


    def acs_wear_mux_pre_change(temp_space, moni_chr, new_acs, acs_loc):
        """
        Runs before mux type acs are removed

        IN:
            temp_space - temp space
            moni_chr - MASMonika object
            new_acs - acs we are adding
            acs_loc - acs location to wear this acs
        """
        # abort if current hair not compatible wtih CAS
        if not is_hairacs_compatible(moni_chr.hair, new_acs):
            temp_space["abort"] = True
            return


    def acs_wear_mux_pst_change(temp_space, moni_chr, new_acs, acs_loc):
        """
        Runs after mux type acs removed, before insertion

        IN:
            temp space - temp space
            moni_chr - MASMonika object
            new_acs - acs we are adding
            acs_loc - acs location to wear this acs
        """
        pass


    def acs_wear_entry_pre_change(temp_space, moni_chr, new_acs, acs_loc):
        """
        Runs after insertion, before entry pooint

        IN:
            temp_space - temp space
            moni_chr - MASmonika object
            new_acs - acs we are adding
            acs_loc - acs location to wear this acs
        """
        pass


    def acs_wear_entry_pst_change(temp_space, moni_chr, new_acs, acs_loc):
        """
        Runs after entry point

        IN:
            temp_space - temp space
            moni_chr - MASMonika object
            new_acs - acs we are adding
            acs_loc - acs location to wear this acs
        """
        if store.mas_selspr.in_prompt_map(new_acs.acs_type):
            store.mas_selspr.set_prompt(new_acs.acs_type, "change")


    def clothes_exit_pre_change(temp_space, moni_chr, prev_cloth, new_cloth):
        """
        Runs pre clothes change code. This code is ran prior to clothes being
        changed and prior to exit prog point

        IN:
            temp_space - temporary dictionary space
            moni_chr - MASMonika object
            prev_cloth - current clothes
            new_cloth - clothes we are changing to
        """
        pass


    def clothes_exit_pst_change(temp_space, moni_chr, prev_cloth, new_cloth):
        """
        Runs after exit prog point is ran, before the actual change.

        IN:
            temp_space - temp dict space
            moni_chr - MASMonika object
            prev_cloth - current clothes
            new_cloth - clothes we are changing to
        """

        # if clothes had a desired ribbon, restore to previous
        desired_ribbon = prev_cloth.getprop("desired-ribbon")
        if (
                desired_ribbon is not None
                and desired_ribbon in ACS_MAP
                and moni_chr.is_wearing_hair_with_exprop("ribbon")
        ):
            temp_ribbon = temp_storage.get("hair.ribbon", None)
            if temp_ribbon is None:
                moni_chr.remove_acs(ACS_MAP[desired_ribbon])

            else:
                moni_chr.wear_acs(temp_ribbon)


    def clothes_entry_pre_change(temp_space, moni_chr, prev_cloth, new_cloth):
        """
        Runs after change, before entry prog point.

        IN:
            temp_space - temp dict space
            moni_chr - MASMonika object
            prev_cloth - current clothes
            new_cloth - clothes we are changing to
        """
        if prev_cloth.hasprop("baked outfit"):
            # a baked outfit causes selector issues. we need to re-evaluate
            # certain cases.
            _hair_unlock_select_if_needed()
            store.mas_selspr._validate_group_topics()


    def clothes_entry_pst_change(temp_space, moni_chr, prev_cloth, new_cloth):
        """
        Runs after entry prog point

        IN:
            temp_space - temp dict space
            moni_chr - MASMonika object
            prev_cloth - current clothes
            new_cloth - clothes we are changing to
        """
        outfit_mode = temp_space.get("outfit_mode", False)

        # if clothes has a desired ribbon, change to it if outfit mode
        desired_ribbon = new_cloth.getprop("desired-ribbon")
        if (
                outfit_mode
                and desired_ribbon is not None
                and desired_ribbon in ACS_MAP
                and moni_chr.is_wearing_hair_with_exprop("ribbon")
        ):
            prev_ribbon = moni_chr.get_acs_of_type("ribbon")
            if prev_ribbon is None:
                prev_ribbon = moni_chr.get_acs_of_exprop("ribbon-like")

            if prev_ribbon != store.mas_acs_ribbon_blank:
                temp_storage["hair.ribbon"] = prev_ribbon

            moni_chr.wear_acs(ACS_MAP[desired_ribbon])

        # if current hair is incompatible, swap to def.
        # NOTE: we will enforce def has a hairstyle that all clothing
        #   items MUST work with.
        if not is_clotheshair_compatible(new_cloth, moni_chr.hair):
            moni_chr.reset_hair(False)


    def hair_exit_pre_change(temp_space, moni_chr, prev_hair, new_hair):
        """
        Runs pre hair change code. This code is ran prior to hair being
        changed and prior to exit prog point.

        IN:
            temp_space - temporary dictionary space
            moni_chr - MASMonika object
            prev_hair - current hair
            new_hair - hair we are changing to
        """
        # abort if current clothes is not comaptible with new hair
        if not is_clotheshair_compatible(moni_chr.clothes, new_hair):
            temp_space["abort"] = True
            return

        all_acs = moni_chr.get_acs()
        for acs in all_acs:
            if not is_hairacs_compatible(new_hair, acs):
                moni_chr.remove_acs(acs)


    def hair_exit_pst_change(temp_space, moni_chr, prev_hair, new_hair):
        """
        Runs after exit prog point is ran, before the actual change.

        IN:
            temp_space - temp dict space
            moni_chr - MASMonika object
            prev_hair - current hair
            new_hair - hair we are changing to
        """
        pass


    def hair_entry_pre_change(temp_space, moni_chr, prev_hair, new_hair):
        """
        Runs after change, before entry prog point.

        IN:
            temp_space - temp dict space
            moni_chr - MASMonika object
            preV_hair - current hair
            new_hair - hair we are changing to
        """
        pass


    def hair_entry_pst_change(temp_space, moni_chr, prev_hair, new_hair):
        """
        Runs after entry prog point

        IN:
            temp_space - temp dict space
            moni_chr - MASMonika object
            prev_hair - current hair
            new_hair - hair we are changing to
        """
        startup = temp_space.get("startup", False)

        if new_hair.hasprop("ribbon"):
            # new hair is enabled for ribbon

            if new_hair.hasprop("ribbon-restore"):
                temp_ribbon = temp_storage.get("hair.ribbon", None)

                # dont force ribbon on startup
                if not startup and temp_ribbon is not None:
                    # force ribbon means that we need to force a ribbon
                    _acs_wear_if_not_wearing_type(
                        moni_chr,
                        "ribbon",
                        temp_ribbon
#                        temp_storage.get(
#                            "hair.ribbon",
#                            store.mas_acs_ribbon_def
#                        )
                    )

            elif new_hair.hasprop("ribbon-off"):
                # take ribbon off for this hairstyle
                _acs_ribbon_save_and_remove(moni_chr)
                _acs_ribbon_like_save_and_remove(_moni_chr)

            if not moni_chr.is_wearing_clothes_with_exprop("baked outfit"):
                # unlock selector for ribbons if you have more than one
                store.mas_filterUnlockGroup(SP_ACS, "ribbon")

            # also change name of the ribbon select prompt
            if moni_chr.is_wearing_ribbon():
                store.mas_selspr.set_prompt("ribbon", "change")

            else:
                store.mas_selspr.set_prompt("ribbon", "wear")

        else:
            # new hair not enabled for ribbon
            _acs_ribbon_save_and_remove(moni_chr)
            _acs_ribbon_like_save_and_remove(moni_chr)

    # hook function helpers

    def is_hairacs_compatible(hair, acs):
        """
        Checks if the given hair is compatible with the given acs

        IN:
            hair - hair to check
            acs - acs to check

        RETURNS: True if hair+acs is compatible, False if not
        """
        # first check for required hair prop
        req_hair_props = acs.getprop(EXP_A_RQHP, None)
        if req_hair_props is not None:
            for req_hair_prop in req_hair_props:
                if not hair.hasprop(req_hair_prop):
                    return False

        # then check exclusions
        excl_hair_props = acs.getprop(EXP_A_EXCLHP, None)
        if excl_hair_props is not None:
            for excl_hair_prop in excl_hair_props:
                if hair.hasprop(excl_hair_prop):
                    return False

        return True


    def is_clotheshair_compatible(clothes, hair):
        """
        Checks if the given clothes is compatible with the given hair

        IN:
            clothes - clothes to check
            hair - hair to check

        RETURNS: True if clothes+hair is comaptible, False if not
        """
        # first check for required clothes prop
        req_cloth_props = hair.getprop(EXP_H_RQCP, None)
        if req_cloth_props is not None:
            for req_cloth_prop in req_cloth_props:
                if not clothes.hasprop(req_cloth_prop):
                    return False

        # then check exclusions
        excl_cloth_props = hair.getprop(EXP_H_EXCLCP, None)
        if excl_cloth_props is not None:
            for excl_cloth_prop in excl_cloth_props:
                if clothes.hasprop(excl_cloth_prop):
                    return False

        return True


    # sprite maker functions

    def _ms_head(clothing, hair, head):
        """
        Creates head string

        IN:
            clothing - type of clothing
            hair - type of hair
            head - type of head

        RETURNS:
            head string
        """
        # NOTE: untested
        return "".join([
            build_loc(),
            ',"',
            S_MAIN,
            clothing,
            "/",
            hair,
            ART_DLM,
            head,
            FILE_EXT,
            '"'
        ])


    def _ms_left(clothing, hair, left):
        """
        Creates left side string

        IN:
            clothing - type of clothing
            hair - type of hair
            left - type of left side

        RETURNS:
            left side stirng
        """
        # NOTE UNTESTED
        return "".join([
            build_loc(),
            ',"',
            S_MAIN,
            clothing,
            "/",
            hair,
            ART_DLM,
            left,
            FILE_EXT,
            '"'
        ])


    def _ms_right(clothing, hair, right):
        """
        Creates right body string

        IN:
            clothing - type of clothing
            hair - type of hair
            right - type of right side

        RETURNS:
            right body string
        """
        # NOTE: UNTESTED
        return "".join([
            build_loc(),
            ',"',
            S_MAIN,
            clothing,
            "/",
            hair,
            ART_DLM,
            head,
            FILE_EXT,
            '"'
        ])


    def _ms_standing(clothing, hair, head, left, right, acs_list):
        """
        Creates the custom standing string
        This is different than the stock ones because of image location

        IN:
            clothing - type of clothing
            hair - type of hair
            head - type of head
            left - type of left side
            right - type of right side
            acs_list - list of MASAccessory objects
                NOTE: this should the combined list because we don't have
                    layering in standing mode

        RETURNS:
            custom standing sprite
        """
        # NOTE: UNTESTED
        return "".join([
            I_COMP,
            "(",
            LOC_STAND,
            ",",
            _ms_left(clothing, hair, left),
            ",",
            _ms_right(clothing, hair, right),
            ",",
            _ms_head(clothing, hair, head),
            _ms_accessorylist(acs_list, False, False),
            ")"
        ])


    def _ms_standingstock(head, left, right, acs_list, single=None):
        """
        Creates the stock standing string
        This is different then the custom ones because of image location

        Also no night version atm.

        IN:
            head - type of head
            left - type of left side
            right - type of right side
            acs_list - list of MASAccessory objects
                NOTE: this should be the combined list because we don't have
                    layering in standing mode
            single - type of single standing picture.
                (Defualt: None)

        RETURNS:
            stock standing string
        """
        # TODO: update this to work with the more optimized system for
        # building sprites
        if single:
            return "".join([
                I_COMP,
                "(",
                LOC_STAND,
                ",",
                build_loc(),
                ',"',
                STOCK_ART_PATH,
                single,
                FILE_EXT,
                '"',
#                _ms_accessorylist(acs_list, False, False),
                ")"
            ])

        return "".join([
            I_COMP,
            "(",
            LOC_STAND,
            ",",
            build_loc(),
            ',"',
            STOCK_ART_PATH,
            left,
            FILE_EXT,
            '",',
            build_loc(),
            ',"',
            STOCK_ART_PATH,
            right,
            FILE_EXT,
            '",',
            build_loc(),
            ',"',
            STOCK_ART_PATH,
            head,
            FILE_EXT,
            '"',
#            _ms_accessorylist(acs_list, False, False),
            ")"
        ])


# Dynamic sprite builder
# retrieved from a Dress Up Renpy Cookbook
# https://lemmasoft.renai.us/forums/viewtopic.php?f=51&t=30643


init -10 python:

    class MASHighlightMap(object):
        """SEALED
        Maps arbitrary keys to <MASFilterMap> objects

        DO NOT EXTEND THIS CLASS. If you need similar functionality, make a
        wrapper around this. This class contains functions that may crash
        when used in an unexpected context.

        NOTE: values dont have to be MASFilterMAP objects, but certain
            functions will fail if not.

        NOTE: this can iterated over to retrieve all objects in here
            EXCEPT for the default.

        PROPERTIES:
            None. Use provided functions to manipulate the map.
        """
        __KEY_ALL = "*"

        def __init__(self, keys, default=None):
            """
            Constructor

            IN:
                keys - iterable of keys that we are allowed to use.
                    NOTE: the default catch all key of "*" (KEY_ALL) does NOt
                    need to be in here.
                default - value to use as the default/catch all object. This
                    is assigned to the KEY_ALL key.
            """
            self.__map = { self.__KEY_ALL: default }

            # remove keyall
            key_list = list(keys)
            if self.__KEY_ALL in key_list:
                key_list.remove(self.__KEY_ALL)

            # remove duplicate
            self.__valid_keys = tuple(set(key_list))

        def __iter__(self):
            """
            Iterator object (generator)
            """
            for key in self.__valid_keys:
                item = self.get(key)
                if item is not None:
                    yield item

        def _add_key(self, new_key, new_value=None):
            """
            Adds a key to the valid keys list. Also adds a value if desired
            NOTE: this is not intended to be done wildly. Please do not
            make a habit of adding keys after construction.
            NOTE: do not use this to add values. if the given key already
            exists, the value is ignored.

            IN:
                new_key - new key to add
                new_value - new value to associate with this key
                    (Default: None)
            """
            if new_key not in self.__valid_keys and new_key != self.__KEY_ALL:
                key_list = list(self.__valid_keys)
                key_list.append(new_key)
                self.__valid_keys = tuple(key_list)
                self.add(new_key, new_value)

        def add(self, key, value):
            """
            Adds value to map.
            NOTE: type is enforced here. If the given item is None
            it is ignored.
            NOTE: this will NOT set the default even if KEY_ALL is passed in

            IN:
                key - key to store item to
                value - value to add
                    if None is passed, this is equivalent to clear
            """
            if value is None:
                self.clear(key)
                return

            if key == self.__KEY_ALL or key not in self.__valid_keys:
                return

            # otherwise valid to add
            self.__map[key] = value

        def apply(self, mapping):
            """
            Applies the given dict mapping to this MASHighlightMap.
            NOTE: will not add invalid keys.

            IN:
                mapping - dict of the following format:
                    key: valid key for this map
                    value: value to add
            """
            for key in mapping:
                self.add(key, mapping[key])

        def clear(self, key):
            """
            Clears value with the given key.
            NOTE: will NOT clear the default even if KEY_ALL is passed in

            IN:
                key - key to clear with
            """
            if key != self.__KEY_ALL and key in self.__map:
                self.__map.pop(key)

        @staticmethod
        def clear_hl_mapping(hl_mpm_data):
            """
            Clears hl mapping in the given hl data object. AKA: Sets the
            hl mapping portion of a pre-MHM MPM to {}.

            NOTE: this should only be used with  the MASPoseMap._transform
            function with MASAccessory

            IN:
                hl_mpm_data - hl data set in a MASPoseMap.

            RETURNS: hl data to set in a MASPoseMap.
            """
            if hl_mpm_data is None:
                return None
            return (hl_mpm_data[0], {})

        @staticmethod
        def convert_mpm(hl_keys, mpm):
            """
            Converts hl mappings in a MASPoseMap to MASHighlightMAp objects

            IN:
                hl_keys - highlight keys to use
                mpm - MASPoseMap object to convert
            """
            if mpm is None:
                return

            # first, build modify pargs map
            pargs = {}
            for param in MASPoseMap.P_PARAM_NAMES:
                hl_data = mpm.get(MASPoseMap.pn2lp(param), None)
                if hl_data is None:
                    pargs[param] = None
                else:
                    pargs[param] = MASHighlightMap.create_from_mapping(
                        hl_keys,
                        hl_data[0],
                        hl_data[1]
                    )

            # then modify the mpm
            mpm._modify(**pargs)

        @staticmethod
        def create_from_mapping(hl_keys, hl_def, hl_mapping):
            """
            Creates a MASHighlightMap using keys/default/mapping

            IN:
                hl_keys - list of keys to use
                hl_def - default highlight to use. Can be None
                hl_mapping - mapping to use.

            RETURNS: created MASHighlightMap
            """
            mhm = MASHighlightMap(hl_keys, default=hl_def)
            mhm.apply(hl_mapping)
            return mhm

        def fltget(self, key, flt, defval=None):
            """
            Combines getting from here and getting the resulting MASFilterMap
            object.

            IN:
                key - key to get from this map
                flt - filter to get from associated MASFilterMap, if found
                defval - default value to return if no flt value could be
                    found.
                    (Default: None)

            RETURNS: value in the MASFilterMap associated with the given
                flt, using the MASFilterMap associated with the given key.
                or defval if no valid MASfilterMap or value found.
            """
            mfm = self.get(key)
            if mfm is None:
                return defval

            return mfm.get(flt, defval=defval)

        @staticmethod
        def fromJSON(json_obj, msg_log, ind_lvl, hl_keys):
            """
            Builds hl data from JSON data

            IN:
                json_obj - JSON object to parse
                ind_lvl - indentation level
                    NOTE: this function handles loading/success log so
                    do NOT increment indent when passing in
                hl_keys - expected keys of this highlight map

            OUT:
                msg_log - list to add messagse to

            RETURNS: hl_data, ready to passed split and passed into
                create_from_mapping. Tuple:
                [0] - default MASFilterMap object
                [1] - dict:
                    key: hl_key
                    value: MASFilterMap object
                or None if no data, False if failure in parsing occured
            """
            # first log loading
            msg_log.append((
                store.mas_sprites_json.MSG_INFO_T,
                ind_lvl,
                store.mas_sprites_json.MHM_LOADING
            ))

            # parse the data
            hl_data = MASHighlightMap._fromJSON_hl_data(
                json_obj,
                msg_log,
                ind_lvl + 1,
                hl_keys
            )

            # check fai/succ
            if hl_data is False:
                # loggin should take care of this already
                return False

            # log success
            msg_log.append((
                store.mas_sprites_json.MSG_INFO_T,
                ind_lvl,
                store.mas_sprites_json.MHM_SUCCESS
            ))

            return hl_data

        def get(self, key):
            """
            Gets value wth the given key.

            IN:
                key - key of item to get

            RETURNS: MASFilterMap object, or None if not found
            """
            if key in self.__map:
                return self.__map[key]

            # otherwise return default
            return self.getdef()

        def getdef(self):
            """
            Gets the default value

            RETURNS: MASFilterMap object, or NOne if not found
            """
            return self.__map.get(self.__KEY_ALL, None)

        def keys(self):
            """
            gets keys in this map

            RETURNS: tuple of keys
            """
            return self.__valid_keys

        @staticmethod
        def o_fltget(mhm, key, flt, defval=None):
            """
            Similar to fltget, but on a MASHighlightMap object.
            NOTE: does None checks of mhm and flt.

            IN:
                mhm - MASHighlightMap object to run fltget on
                key - key to get MASFilterMap from mhm
                flt - filter to get from associated MASFilterMap
                defval - default value to return if no flt value could be found
                    (Default: None)

            RETURNS: See fltget
            """
            if mhm is None or flt is None:
                return defval

            return mhm.fltget(key, flt, defval=defval)

        def setdefault(self, value):
            """
            Sets the default value

            IN:
                value - value to use as default
            """
            if value is None or isinstance(value, MASFilterMap):
                self.__map[self.__KEY_ALL] = value


init -3 python:
#    import renpy.store as store
#    import renpy.exports as renpy # we need this so Ren'Py properly handles rollback with classes
#    from operator import attrgetter # we need this for sorting items
    import math
    from collections import namedtuple

    # Monika character base
    class MASMonika(renpy.store.object):
        import store.mas_sprites as mas_sprites

        # CONSTANTS
        PRE_ACS = 0 # PRE ACCESSORY (before body)
        MID_ACS = 1 # MID ACCESSORY (between face and front arms)
        PST_ACS = 2 # post accessory (after front arms)
        BBH_ACS = 3 # betweeen Body and Back Hair accessory
        BFH_ACS = 4 # between Body and Front Hair accessory
        AFH_ACS = 5 # between face and front hair accessory
        BBA_ACS = 6 # between body and back arms
        MAB_ACS = 7 # between middle arms and boobs
        BSE_ACS = 8 # between base and clothes
        ASE_ACS = 9 # between base arms and clothes
        BAT_ACS = 10 # between mid hair and table
        MAT_ACS = 11 # between middle arms and table
        BMH_ACS = 12 # between back arms and mid hair
        MMH_ACS = 13 # between mid hair and head

        # valid rec layers
        # NOTE: this MUST be in the same order as save_state/load_State
        # NOTE: do not remove layers. Because of load state, we can only
        #   ignore layers if needed, but not remove. BEtter to just replace
        #   a layer than remove it.
        REC_LAYERS = (
            PRE_ACS,
            BBH_ACS,
            BFH_ACS,
            AFH_ACS,
            MID_ACS,
            PST_ACS,
            BBA_ACS,
            MAB_ACS,
            BSE_ACS,
            ASE_ACS,
            BAT_ACS,
            MAT_ACS,
            BMH_ACS,
            MMH_ACS,
        )

        # split layers
        SPL_LAYERS = (
            BSE_ACS,
            ASE_ACS,
        )

        # rec layers in standard render order
        RENDER_ORDER = (
            PRE_ACS,
            BBH_ACS,
            BSE_ACS,
            BBA_ACS,
            ASE_ACS,
            BMH_ACS,
            MMH_ACS,
            BAT_ACS,
            MAT_ACS,
            MAB_ACS,
            BFH_ACS,
            AFH_ACS,
            MID_ACS,
            PST_ACS,
        )

        def __init__(self):
            """
            Constructor
            """
            self.name="Monika"
            self.haircut="default"
            self.haircolor="default"
            self.skin_hue=0 # monika probably doesn't have different skin color
            self.lipstick="default" # i guess no lipstick

            self.clothes = mas_clothes_def # default clothes is school outfit
            self.hair = mas_hair_def # default hair is the usual whtie ribbon
            #self.table = mas_table_def # default table

            # list of lean blacklisted accessory names currently equipped
            self.lean_acs_blacklist = []

            # setup acs dict
            self.acs = {
                # accesories to be rendereed before anything
                self.PRE_ACS: [],

                # accessories to be rendered after back hair, before body
                self.BBH_ACS: [],

                # accessories to be rendered after base body, before body clothes
                self.BSE_ACS: [],

                # accessories to be rendered after body, before back arms
                self.BBA_ACS: [],

                # accessories to be rendered after base arms, before arm clothes
                self.ASE_ACS: [],

                # accessories to be rendered after back arms, before mid hair
                self.BMH_ACS: [],

                # accessories to be rendered after mid hair, before head
                self.MMH_ACS: [],

                # accessories to be rendered after head, before table
                self.BAT_ACS: [],

                # accessories to be rendered after table, before middle arms
                self.MAT_ACS: [],

                # accessories to be rendered after middle arms before boobs
                self.MAB_ACS: [],

                # accessories to be rendered after boobs, before front hair
                self.BFH_ACS: [],

                # accessories to be rendered after fornt hair, before face
                self.AFH_ACS: [],

                # accessories to be rendered after face, before front arms
                self.MID_ACS: [],

                # accessories to be rendered last
                self.PST_ACS: [],
            }

            # use this dict to map acs IDs with which acs list they are in.
            # this will increase speed of removal and checking.
            self.acs_list_map = {}

            # LOCK VARS
            # True if we should block any changes to hair
            self.lock_hair = False

            # True if we should block any chnages to clothes
            self.lock_clothes = False

            # True if we should block any changes to cas
            self.lock_acs = False

            # set to True to allow ACS overriding
            self._override_rec_layer = False

            # the current table/chair combo we
            # NOTE: this is associated with monika because we could definitely
            # have multiple table/chairs in a MASBackground.
            # NOTE: replacing this is untested, but will be required because
            #   of highlights
            self.tablechair = MASTableChair("def", "def")

            # set to the ahoge we had set during this session
            self.last_ahoge = None

            # special mapping of ACS with acs types
            # this is a dual key map. Use this for quick removal of acs types
            # key: acs type
            # value: dict of the following format:
            #   key: acs name
            #   value: acs object
            self._acs_type_map = {}

        def __repr__(self):
            """
            this is lengthy and will contain all objects
            """
            # build ACS strings
            # this determines order to show ACS in
            acs_str_map = (
                "PRE",
                "BBH",
                "BSE",
                "BBA",
                "ASE",
                "BMH",
                "MMH",
                "BAT",
                "MAT",
                "MAB",
                "BFH",
                "AFH",
                "MID",
                "PST",
            )
            acs_str = []
            for idx, pfx in enumerate(acs_str_map):
                rec_layer = self.RENDER_ORDER[idx]
                acs_list = self.__get_acs(rec_layer)
                if len(acs_list) > 0:
                    acs_str.append("{0}: {1}".format(pfx, acs_list))

            return "<Monika: ({0}, {1}, {2}, {3})>".format(
                self.clothes,
                self.hair,
                ", ".join(acs_str),
                self.tablechair
            )

        def __get_acs(self, acs_type):
            """
            Returns the accessory list associated with the given type

            IN:
                acs_type - the accessory type to get

            RETURNS:
                accessory list, or None if the given acs_type is not valid
            """
            return self.acs.get(acs_type, None)

        def ahoge(self, force_change=False):
            """
            Applies a random ahoge to Monika.

            IN:
                force_change - True will force an ahoge to be set, even if
                    one is currently available.
                    (Deafult: False)

            RETURNS: True if we set the ahoge, False if not
            """
            # dont wear one if this ahoge was already set today, unless
            # we are doing a force change.
            if (
                    persistent._mas_last_ahoge_dt is not None
                    and not force_change
                    and datetime.datetime.now().date()
                        == persistent._mas_last_ahoge_dt.date()
            ):
                    # we already set the ahoge today so dont set it again.
                    return False

            # random select an ahoge
            self._set_ahoge(
                random.choice(store.mas_sprites.get_acs_of_type("ahoge"))
            )
            return True

        def _set_ahoge(self, ahoge_acs, force_wear=False):
            """
            Sets the ahoge for Monika, also setting the appropriate last
            ahoge and everything.

            IN:
                ahoge_acs - the ACS object for the ahoge to wear
                    NOTE: pass in None to clear the ahoge.
                force_wear - pass True to wear the ahoge even if we are wearing
                    a hat.
                    (Default: False)
            """
            if ahoge_acs is None:
                # clear the ahoge, if we are wearing it.
                if self.last_ahoge is not None:
                    self.remove_acs(self.last_ahoge)
                    self.last_ahoge = None
                return

            # set the last ahoge to the given acs
            self.last_ahoge = ahoge_acs
            persistent._mas_last_ahoge_dt = datetime.datetime.now()

            if self.get_acs_of_type("hat") is not None and not force_wear:
                return

            self.wear_acs(ahoge_acs)

        def _determine_poses(self, lean, arms):
            """
            determines the lean/pose/hair/baked data for monika based on
            the requested lean and arms

            IN:
                lean - requested lean
                arms - requested arms

            RETURNS: tuple of the following format:
                [0] - lean to use
                [1] - leanpose to use
                [2] - arms to use
                [3] - hair to use
                [4] - base arms to use
                [5] - pose arms to use
            """
            # first check black list
            if store.mas_sprites.should_disable_lean(lean, arms, self):
                # set lean to None if its on the blacklist
                # NOTE: this function checks pose_maps
                lean = None
                arms = "steepling"

            # fallback adjustments:
            if self.hair.pose_map.is_fallback():
                arms, lean = self.hair.get_fallback(arms, lean)

            if self.clothes.pose_map.is_fallback():
                arms, lean = self.clothes.get_fallback(arms, lean)

            # get the mapped hair for the current clothes
            if self.clothes.has_hair_map():
                hair = store.mas_sprites.HAIR_MAP.get(
                    self.clothes.get_hair(self.hair.name),
                    mas_hair_def
                )

            else:
                hair = self.hair

            # combined pose with lean for efficient
            if lean is not None:
                leanpose = lean + "|" + arms
            else:
                leanpose = arms

            # MASPoseArms rules:
            #   1. If the pose_arms property in clothes is None, then we assume
            #   that the clothes follows the base pose rules.
            #   2. If the pose_arms property exists, and the
            #   corresponding pose in that map is None, then we assume that
            #   the clothes does NOT have layers for this pose.
            # select MASPoseArms for baes and outfit

            # NOTE: we can always assume that base arms exist
            # NOTE: but we will default steepling justin case
            base_arms = [
                store.mas_sprites.base_arms.get(arm_id)
                for arm_id in store.mas_sprites.base_mpm.get(leanpose, [7])
            ]
            if self.clothes.pose_arms is None:
                pose_arms = base_arms

            else:
                pose_arms = self.clothes.pose_arms.getflp(leanpose)

            return (lean, leanpose, arms, hair, base_arms, pose_arms)

        def _same_state_acs(self, a1, a2):
            """
            Compares given acs lists as acs objects

            NOTE: order does not matter

            IN:
                a1 - list of acs objects to compare
                a2 - list of acs objects to compare

            RETURNS: True if the same, False if not
            """
            # quick chec
            if len(a1) != len(a2):
                return False

            # make a list of names for comparison
            a2_names = [acs.name for acs in a2]

            # now do comparison
            same_count = 0
            for a1_acs in a1:
                if a1_acs.name in a2_names:
                    same_count += 1
                else:
                    return False

            return len(a2_names) == same_count

        def _same_state_acs_prims(self, a1, a2):
            """
            Compares given acs lists as primitive data.

            NOTE: order does not matter

            IN:
                a1 - list of acs names to compare
                a2 - list of acs names to compare

            RETURNS: True if the same, False if not
            """
            # quick check
            if len(a1) != len(a2):
                return False

            same_count = 0
            for a1_name in a1:
                if a1_name in a2:
                    same_count += 1
                else:
                    return False

            return len(a2) == same_count

        def _same_state(self, data):
            """
            Compares the given state as objects

            IN:
                data - previous object state

            RETURNS: True if the same, False if not
            """
            # object data is sprite objects, but we compare names

            # get current monikas state
            curr_state = self.save_state(True, True, True, False)

            # first compare size
            if len(data) != len(curr_state):
                return False

            # clothes
            if data[0].name != curr_state[0].name:
                return False

            # hair
            if data[1].name != curr_state[1].name:
                return False

            # acs lists
            for index in range(2, len(data)):
                if not self._same_state_acs(data[index], curr_state[index]):
                    return False

            return True

        def _same_state_prims(self, data):
            """
            Compares the given state as primitives

            IN:
                data - previous primitive state

            RETURNS: True if the same, False if not
            """
            # primtiive data is stored as names

            # get current monika's state
            curr_state = self.save_state(True, True, True, True)

            # first compare state size
            if len(data) != len(curr_state):
                return False

            # clothes
            if data[0] != curr_state[0]:
                return False

            # hair
            if data[1] != curr_state[1]:
                return False

            # acs lists
            for index in range(2, len(data)):
                if not self._same_state_acs_prims(data[index], curr_state[index]):
                    return False

            return True

        def _load(self,
                # NOTE: this is in REC_LAYER order
                _clothes_name,
                _hair_name,
                _acs_pre_names,
                _acs_bbh_names,
                _acs_bfh_names,
                _acs_afh_names,
                _acs_mid_names,
                _acs_pst_names,
                _acs_bba_names,
                _acs_mab_names,
                _acs_bse_names,
                _acs_ase_names,
                _acs_bat_names,
                _acs_mat_names,
                _acs_bmh_names,
                _acs_mmh_names,
                startup=False
            ):
            """
            INTERNAL

            load function using names/IDs

            IN:
                _clothes_name - name of clothing to load
                _hair_name - name of hair to load
                _acs_pre_names - list of pre acs names to load
                _acs_bbh_names - list of bbh acs names to load
                _acs_bfh_names - list of bfh acs names to load
                _acs_afh_names - list of afh acs names to load
                _acs_mid_names - list of mid acs names to load
                _acs_pst_names - list of pst acs names to load
                _acs_bba_names - list of bba acs names to load
                _acs_mab_names - list of mab acs names to load
                _acs_bse_names - list of bse acs names to load
                _acs_ase_names - list of ase acs names to load
                _acs_bat_names - list of bat acs names to load
                _acs_mat_names - list of mat acs names to load
                _acs_bmh_names - list of bmh acs names to load
                _acs_mmh_names - list of mmh acs names to load
                startup - True if we are loading on start, False if not
                    (Default: False)
            """
            # clothes and hair
            self.change_outfit(
                store.mas_sprites.CLOTH_MAP.get(_clothes_name, store.mas_clothes_def),
                store.mas_sprites.HAIR_MAP.get(_hair_name, store.mas_hair_def),
                startup=startup
            )

            # acs
            # NOTE: this is in render layer order
            self._load_acs(_acs_pre_names, self.PRE_ACS)
            self._load_acs(_acs_bbh_names, self.BBH_ACS)
            self._load_acs(_acs_bse_names, self.BSE_ACS)
            self._load_acs(_acs_bba_names, self.BBA_ACS)
            self._load_acs(_acs_ase_names, self.ASE_ACS)
            self._load_acs(_acs_bmh_names, self.BMH_ACS)
            self._load_acs(_acs_mmh_names, self.MMH_ACS)
            self._load_acs(_acs_bat_names, self.BAT_ACS)
            self._load_acs(_acs_mat_names, self.MAT_ACS)
            self._load_acs(_acs_mab_names, self.MAB_ACS)
            self._load_acs(_acs_bfh_names, self.BFH_ACS)
            self._load_acs(_acs_afh_names, self.AFH_ACS)
            self._load_acs(_acs_mid_names, self.MID_ACS)
            self._load_acs(_acs_pst_names, self.PST_ACS)

            # set ahoge if we have one
            self.last_ahoge = self.get_acs_of_type("ahoge")

        def _load_acs(self, per_acs, acs_type):
            """
            Loads accessories from the given persistent into the given
            acs type.

            IN:
                per_acs - persistent list to grab acs from
                acs_type - acs type to load acs into
            """
            for acs_name in per_acs:
                _acs = store.mas_sprites.ACS_MAP.get(acs_name, None)
                if _acs:
                    self.wear_acs_in(_acs, acs_type)

        def _load_acs_obj(self, acs_objs, acs_type):
            """
            Loads accessories from a given list of accessory objects into
            the given acs type

            IN:
                acs_objs - list of acs to load
                acs_type - acs type to load acs into
            """
            for _acs in acs_objs:
                # must verify sprite before loading
                if _acs.name in store.mas_sprites.ACS_MAP:
                    self.wear_acs_in(_acs, acs_type)

        def _save_acs(self, acs_type, force_acs=False):
            """
            Generates list of accessory names to save to persistent.

            IN:
                acs_type - acs type to build acs names list
                force_acs - True means to save acs even if stay_on_start is
                    False
                    (Default: False)

            RETURNS:
                list of acs names to save to persistent
            """
            return [
                acs.name
                for acs in self.acs[acs_type]
                if force_acs or acs.stay_on_start
            ]

        def _save_acs_obj(self, acs_type, force_acs=False):
            """
            Generaltes list of acs objects to save

            IN:
                acs_type - acs type to buld acs list
                force_acs - True means to save acs even if stay_on_start is
                    False
                    (Default: False)

            RETURNS:
                list of acs objects to save
            """
            return [
                acs
                for acs in self.acs[acs_type]
                if force_acs or acs.stay_on_start
            ]

        @staticmethod
        def _verify_rec_layer(val, allow_none=True):
            if val is None:
                return allow_none
            return val in MASMonika.REC_LAYERS

        @staticmethod
        def _verify_spl_layer(val, allow_none=True):
            if val is None:
                return allow_none
            return val in MASMonika.SPL_LAYERS

        def change_clothes(
                self,
                new_cloth,
                by_user=None,
                startup=False,
                outfit_mode=False
        ):
            """
            Changes clothes to the given cloth. also sets the persistent
            force clothes var to by_user, if its not None

            IN:
                new_cloth - new clothes to wear
                by_user - True if this action was mandated by the user, False
                    if not. If None, we do NOT set the forced clothes var
                    (Default: None)
                startup - True if we are loading on startup, False if not
                    When True, we dont respect locking
                    (Default: False)
                outfit_mode - True means we should change hair/acs if it
                    completes the outfit. False means we should not.
                    NOTE: this does NOT affect hair/acs that must change for
                        consistency purposes.
                    (Default: False)
            """
            if self.lock_clothes and not startup:
                return

            # setup temp space
            temp_space = {
                "by_user": by_user,
                "startup": startup,
                "outfit_mode": outfit_mode
            }

            prev_cloth = self.clothes

            # run pre clothes change logic
            store.mas_sprites.clothes_exit_pre_change(
                temp_space,
                self,
                prev_cloth,
                new_cloth
            )

            # abort if asked
            if temp_space.get("abort", False):
                return

            # exit point
            self.clothes.exit(
                self,
                new_clothes=new_cloth,
                outfit_mode=outfit_mode
            )

            # post exit, pre change
            store.mas_sprites.clothes_exit_pst_change(
                temp_space,
                self,
                prev_cloth,
                new_cloth
            )

            # change
            self.clothes = new_cloth

            # post change, pre entry
            store.mas_sprites.clothes_entry_pre_change(
                temp_space,
                self,
                prev_cloth,
                new_cloth
            )

            # entry point
            self.clothes.entry(
                self,
                prev_clothes=prev_cloth,
                outfit_mode=outfit_mode
            )

            # post entry point
            store.mas_sprites.clothes_entry_pst_change(
                temp_space,
                self,
                prev_cloth,
                new_cloth
            )

            if by_user is not None:
                persistent._mas_force_clothes = bool(by_user)

        def change_hair(self, new_hair, by_user=None, startup=False):
            """
            Changes hair to the given hair. also sets the persistent force
            hair var to by_user, if its not None

            IN:
                new_hair - new hair to wear
                by_user - True if this action was mandated by the user, False
                    if not. If None, we do NOT set the forced hair var
                    (Default: None)
                startup - True if we are loading on startup, False if not
                    When True, we dont respect locking
                    (Default: False)
            """
            if self.lock_hair and not startup:
                return

            # setup temp space
            temp_space = {
                "by_user": by_user,
                "startup": startup,
            }

            prev_hair = self.hair

            # run pre hair change logic
            store.mas_sprites.hair_exit_pre_change(
                temp_space,
                self,
                prev_hair,
                new_hair
            )

            # abort if asked
            if temp_space.get("abort", False):
                return

            # exit point
            self.hair.exit(self, new_hair=new_hair)

            # post exit , pre hair change
            store.mas_sprites.hair_exit_pst_change(
                temp_space,
                self,
                prev_hair,
                new_hair
            )

            # change
            self.hair = new_hair

            # post change, pre entry
            store.mas_sprites.hair_entry_pre_change(
                temp_space,
                self,
                prev_hair,
                new_hair
            )

            # entry point
            self.hair.entry(self, prev_hair=prev_hair)

            # post entry point
            store.mas_sprites.hair_entry_pst_change(
                temp_space,
                self,
                prev_hair,
                new_hair
            )

            if by_user is not None:
                persistent._mas_force_hair = bool(by_user)


        def change_outfit(
                self,
                new_cloth,
                new_hair,
                by_user=None,
                startup=False
            ):
            """
            Changes both clothes and hair. also sets the persisten forced vars
            to by_user, if its not None

            IN:
                new_cloth - new clothes to wear
                new_hair - new hair to wear
                by_user - True if this action ws mandated by user, False if not
                    If None, we do NOT set the forced vars
                    (Default: None)
                startup - True if we are loading on startup, False if not
                    (Default: False)
            """
            self.change_clothes(new_cloth, by_user=by_user, startup=startup)
            self.change_hair(new_hair, by_user=by_user, startup=startup)


        def get_acs(self):
            """
            Gets all acs objects currently worn by Monika

            RETURNS: list of all acs objects being worn
            """
            acs_items = []
            for acs_name in self.acs_list_map:
                acs = store.mas_sprites.ACS_MAP.get(acs_name, None)
                if acs is not None:
                    acs_items.append(acs)

            return acs_items


        def get_acs_by_desk(self, flag_value=True):
            """
            Returns all acs that have a keep_on_desk flag set to flag_value

            IN:
                flag_value - flag value to check for
                    (Default: True)

            RETURNS: list of ACS objects with a keep_on_desk flag set to
                flag_value
            """
            acs_items = []
            for acs_name in self.acs_list.map:
                _acs = store.mas_sprites.ACS_MAP.get(acs_name, None)
                if _acs and _acs.keep_on_desk == flag_value:
                    acs_items.append(_acs)

            return acs_items


        def get_acs_of_exprop(self, exprop, get_all=False):
            """
            Gets the acs objects currently being work of a given ex prop

            IN:
                exprop - extended property to check for
                get_all - True means we get all acs being worn of this exprop
                    False will return the first one
                    (Default: False)

            RETURNS: single matching acs or None if get_all is False, list of
                matching acs or empty list if get_all is True.
            """
            if get_all:
                acs_items = []
            else:
                acs_items = None

            for acs_name in self.acs_list_map:
                _acs = store.mas_sprites.ACS_MAP.get(acs_name, None)
                if _acs and _acs.hasprop(exprop):
                    if get_all:
                        acs_items.append(_acs)

                    else:
                        return _acs

            return acs_items


        def get_acs_of_type(self, acs_type, get_all=False):
            """
            Gets the acs objects currently being worn of a given type.

            IN:
                acs_type - acs type to check for
                get_all - True means we get all acs being worn of this type,
                    False will just return the first one
                    (Default: False)

            RETURNS: single matchin acs or None if get_all is False. list of
                matching acs or empty list if get_all is True.
            """
            if get_all:
                acs_items = []
            else:
                acs_items = None

            for acs_name in self.acs_list_map:
                _acs = store.mas_sprites.ACS_MAP.get(acs_name, None)
                if _acs and _acs.acs_type == acs_type:
                    if get_all:
                        acs_items.append(_acs)
                    else:
                        return _acs

            return acs_items


        def get_outfit(self):
            """
            Returns the current outfit

            RETURNS:
                tuple:
                    [0] - current clothes
                    [1] - current hair
            """
            return (self.clothes, self.hair)


        def is_wearing_acs(self, accessory):
            """
            Checks if currently wearing the given accessory

            IN:
                accessory - accessory to check

            RETURNS:
                True if wearing accessory, false if not
            """
            return accessory.name in self.acs_list_map


        def is_wearing_acs_with_exprop(self, exprop):
            """
            Checks if currently wearing any accessory with given exprop

            IN:
                exprop - extended property to check

            RETURNS: True if wearing accessory, False if not
            """
            for acs_name in self.acs_list_map:
                _acs = store.mas_sprites.ACS_MAP.get(acs_name, None)
                if _acs and _acs.hasprop(exprop):
                    return True

            return False


        def is_wearing_acs_type(self, acs_type):
            """
            Checks if currently wearing any accessory with given type

            IN:
                acs_type - accessory type to check

            RETURNS: True if wearing acccesroy, False if not
            """
            for acs_name in self.acs_list_map:
                _acs = store.mas_sprites.ACS_MAP.get(acs_name, None)
                if _acs and _acs.acs_type == acs_type:
                    return True

            return False


        def is_wearing_acs_types(self, *acs_types):
            """
            multiple arg version of is_wearing_acs_type

            IN:
                *acs_types - any number of acs types to check

            RETURNS: True if any the ACS types checks are True, False if not
            """
            for acs_type in acs_types:
                if self.is_wearing_acs_type(acs_type):
                    return True

            return False

        def is_wearing_acs_with_mux(self, acs_type):
            """
            Checks if currently wearing any ACS with the given acs_type in its
            mux type

            IN:
                acs_type - acceessory type to check
            """
            for acs_name in self.acs_list_map:
                acs = store.mas_sprites.ACS_MAP.get(acs_name, None)
                if (
                        acs
                        and acs.mux_type is not None
                        and acs_type in acs.mux_type
                ):
                    return True

            return False

        def is_wearing_acs_in(self, accessory, acs_type):
            """
            Checks if the currently wearing the given accessory as the given
            accessory type

            IN:
                accessory - accessory to check
                acs_type - accessory type to check

            RETURNS:
                True if wearing accessory, False if not
            """
            acs_list = self.__get_acs(acs_type)

            if acs_list is not None:
                return accessory in acs_list

            return False


        def is_wearing_clothes_with_exprop(self, exprop):
            """
            Checks if we are currently wearing clothes with the given exprop

            IN:
                exprop - extended property to check

            RETURNS: True if wearing clothes with the exprop, False if not
            """
            return self.clothes.hasprop(exprop)


        def is_wearing_hair_with_exprop(self, exprop):
            """
            Checks if we are currently wearing hair with the given exprop

            IN:
                exprop - extend property to check

            RETURNS: True if wearing hair with the exprop, False if not
            """
            return self.hair.hasprop(exprop)


        def is_wearing_ribbon(self):
            """
            Checks if we are currently wearing a ribbon or ribbon-like ACS

            RETURNS: True if wearing ACS with ribbon type or ACS with
                ribbon-like ex prop
            """
            return (
                self.is_wearing_acs_type("ribbon")
                or self.is_wearing_acs_with_exprop("ribbon-like")
            )

        def load(self, startup=False):
            """
            Loads hair/clothes/accessories from persistent.

            IN:
                startup - True if loading on start, False if not
                    When True, we dont respesct locking
                    (Default: False)
            """
            self._load(
                store.persistent._mas_monika_clothes,
                store.persistent._mas_monika_hair,
                store.persistent._mas_acs_pre_list,
                store.persistent._mas_acs_bbh_list,
                store.persistent._mas_acs_bfh_list,
                store.persistent._mas_acs_afh_list,
                store.persistent._mas_acs_mid_list,
                store.persistent._mas_acs_pst_list,
                store.persistent._mas_acs_bba_list,
                store.persistent._mas_acs_mab_list,
                store.persistent._mas_acs_bse_list,
                store.persistent._mas_acs_ase_list,
                store.persistent._mas_acs_bat_list,
                store.persistent._mas_acs_mat_list,
                store.persistent._mas_acs_bmh_list,
                store.persistent._mas_acs_mmh_list,
                startup=startup
            )

        # TODO: consider adding startup to this
        def load_state(self, _data, as_prims=False):
            """
            Loads clothes/hair/acs from a tuple data format that was saved
            using the save_state function.

            IN:
                _data - data to load from. tuple of the following format:
                    [0]: clothes data
                    [1]: hair data
                    [2]: pre acs data
                    [3]: bbh acs data
                    [4]: bfh acs data
                    [5]: afh acs data
                    [6]: mid acs data
                    [7]: pst acs data
                    [8]: bba acs data
                    [9]: mab acs data
                    [10]: bse acs data
                    [11]: ase acs data
                    [12]: bat acs data
                    [13]: mat acs data
                    [14]: bmh acs data
                    [15]: mmh acs data
                as_prims - True if this data was saved as primitive data types,
                    false if as objects
                    (Default: False)
            """
            if as_prims:
                # for prims, we can just call an existing function
                self._load(*_data)
                return

            # otherwise, we need to set things ourselves
            # clothes and hair
            self.change_outfit(_data[0], _data[1])

            # acs
            for index, rec_layer in enumerate(self.REC_LAYERS):
                self._load_acs_obj(_data[index+2], rec_layer)

            # set ahoge if we have one
            self.last_ahoge = self.get_acs_of_type("ahoge")

        def reset_all(self, by_user=None):
            """
            Resets all of monika

            IN:
                by_user - True if this action was mandated by user, False if
                    not. If None, we do NOT set force vars.
                    (Default: None)
            """
            self.reset_clothes(by_user)
            self.reset_hair(by_user)
            self.remove_all_acs()

        def remove_acs(self, accessory):
            """
            Removes the given accessory. this uses the map to determine where
            the accessory is located.

            IN:
                accessory - accessory to remove
            """
            self.remove_acs_in(
                accessory,
                self.acs_list_map.get(accessory.name, None)
            )

        def remove_acs_exprop(self, exprop):
            """
            Removes all ACS of given exprop.

            IN:
                exprop - exprop to check for
            """
            for acs_name in self.acs_list_map.keys():
                _acs = store.mas_sprites.ACS_MAP.get(acs_name, None)
                if _acs and _acs.hasprop(exprop):
                    self.remove_acs_in(_acs, self.acs_list_map[acs_name])

        def remove_acs_mux(self, mux_types):
            """
            Removes all ACS with a mux type in the given list.

            IN:
                mux_types - list of acs_types to remove from acs
            """
            for mux_type in mux_types:
                acs_with_mux = self._acs_type_map.get(mux_type, {})
                for acs_name in acs_with_mux.keys():
                    self.remove_acs(store.mas_sprites.get_acs(acs_name))

        def remove_acs_in(self, accessory, acs_layer):
            """
            Removes the given accessory from the given accessory list layer

            IN:
                accessory - accessory to remove
                acs_layer - ACS layer to remove from
            """
            if self.lock_acs:
                return

            acs_list = self.__get_acs(acs_layer)
            temp_space = {
                "acs_list": acs_list,
            }

            if acs_list is not None and accessory in acs_list:

                # run pre exit point code
                store.mas_sprites.acs_rm_exit_pre_change(
                    temp_space,
                    self,
                    accessory,
                    acs_layer
                )

                # abort removal if we were told to abort
                if temp_space.get("abort", False):
                    return

                # run programming point
                accessory.exit(self)

                # run post exit code
                store.mas_sprites.acs_rm_exit_pst_change(
                    temp_space,
                    self,
                    accessory,
                    acs_layer
                )

                # cleanup blacklist
                if accessory.name in self.lean_acs_blacklist:
                    self.lean_acs_blacklist.remove(accessory.name)

                # cleanup mapping
                if accessory.name in self.acs_list_map:
                    self.acs_list_map.pop(accessory.name)

                # cleanup type mapping
                type_map = self._acs_type_map.get(accessory.acs_type, {})
                if accessory.name in type_map:
                    type_map.pop(accessory.name)

                # now remove
                acs_list.remove(accessory)

                # finally post removal code
                store.mas_sprites.acs_rm_exit_pst_removal(
                    temp_space,
                    self,
                    accessory,
                    acs_layer
                )

        def remove_all_acs(self):
            """
            Removes all accessories from all accessory lists
            """
            for rec_layer in self.REC_LAYERS:
                self.remove_all_acs_in(rec_layer)

        def remove_all_acs_in(self, acs_layer):
            """
            Removes all accessories from the given accessory layer

            IN:
                acs_layer - ACS layer to remove acs from
            """
            if self.lock_acs:
                return

            if acs_layer in self.acs:
                # need to clear blacklisted
                for acs in self.acs[acs_layer]:
                    # run programming point
                    acs.exit(self)

                    # cleanup blacklist
                    if acs.name in self.lean_acs_blacklist:
                        self.lean_acs_blacklist.remove(acs.name)

                    # remove from mapping
                    if acs.name in self.acs_list_map:
                        self.acs_list_map.pop(acs.name)

                self.acs[acs_layer] = list()

        def reset_clothes(self, by_user=None):
            """
            Resets clothing to default

            IN:
                by_user - True if this action was mandated by user, False if
                    not. If None, then we do NOT set force clothed vars
                    (Default: None)
            """
            self.change_clothes(mas_clothes_def, by_user)


        def reset_hair(self, by_user=None):
            """
            Resets hair to default

            IN:
                by_user - True if this action was mandated by user, False if
                    not. If None, then we do NOT set forced hair vars
                    (Default: None)
            """
            self.change_hair(mas_hair_def, by_user)


        def reset_outfit(self, by_user=None):
            """
            Resetse clothing and hair to default

            IN:
                by_user - True if this action was mandated by user, False if
                    not. If None, then we do NOT set forced vars
                    (Default: None)
            """
            self.reset_clothes(by_user)
            self.reset_hair(by_user)

        def restore(self, _data, as_prims=False):
            """
            Restores monika to a previous state. This will reset outfit and
            clear ACS before loading.

            IN:
                _data - see load_state
                as_prims - see load_state
            """
            self.reset_outfit()
            self.remove_all_acs()
            self.load_state(_data, as_prims=as_prims)

        def save(self, force_hair=False, force_clothes=False, force_acs=False):
            """
            Saves hair/clothes/acs to persistent

            IN:
                force_hair - True means we force hair saving even if
                    stay_on_start is False
                    (Default: False)
                force_clothes - True means we force clothes saving even if
                    stay_on_start is False
                    (Default: False)
                force_acs - True means we force acs saving even if
                    stay_on_start is False
                    (Default: False)
            """
            # hair and clothes
            if force_hair or self.hair.stay_on_start:
                store.persistent._mas_monika_hair = self.hair.name

            if force_clothes or self.clothes.stay_on_start:
                store.persistent._mas_monika_clothes = self.clothes.name

            # acs
            store.persistent._mas_acs_pre_list = self._save_acs(
                self.PRE_ACS,
                force_acs
            )
            store.persistent._mas_acs_bbh_list = self._save_acs(
                self.BBH_ACS,
                force_acs
            )
            store.persistent._mas_acs_bse_list = self._save_acs(
                self.BSE_ACS,
                force_acs
            )
            store.persistent._mas_acs_bba_list = self._save_acs(
                self.BBA_ACS,
                force_acs
            )
            store.persistent._mas_acs_ase_list = self._save_acs(
                self.ASE_ACS,
                force_acs
            )
            store.persistent._mas_acs_bmh_list = self._save_acs(
                self.BMH_ACS,
                force_acs
            )
            store.persistent._mas_acs_mmh_list = self._save_acs(
                self.MMH_ACS,
                force_acs
            )
            store.persistent._mas_acs_bat_list = self._save_acs(
                self.BAT_ACS,
                force_acs
            )
            store.persistent._mas_acs_mat_list = self._save_acs(
                self.MAT_ACS,
                force_acs
            )
            store.persistent._mas_acs_mab_list = self._save_acs(
                self.MAB_ACS,
                force_acs
            )
            store.persistent._mas_acs_bfh_list = self._save_acs(
                self.BFH_ACS,
                force_acs
            )
            store.persistent._mas_acs_afh_list = self._save_acs(
                self.AFH_ACS,
                force_acs
            )
            store.persistent._mas_acs_mid_list = self._save_acs(
                self.MID_ACS,
                force_acs
            )
            store.persistent._mas_acs_pst_list = self._save_acs(
                self.PST_ACS,
                force_acs
            )


        def same_state(self, data, as_prims=False):
            """
            compares if the given state is the same as current monika

            IN:
                data - data to compare
                as_prims - True if prims, False if not

            RETURNS: True if same state, False if not
            """
            if as_prims:
                return self._same_state_prims(data)

            return self._same_state(data)

        def save_state(self,
                force_hair=False,
                force_clothes=False,
                force_acs=False,
                as_prims=False
            ):
            """
            Saves hair/clothes/acs to a tuple data format that can be loaded
            later using the load_state function.

            IN:
                force_hair - True means force hair saving even if stay_on_start
                    is False. If False and stay_on_start is False, the default
                    hair will be returned.
                    (Default: False)
                force_clothes - True meanas force clothes saving even if
                    stay_on_start is False. If False and stay_on_start is
                    False, the default clothes will be returned.
                    (Default: False)
                force_acs - True means force acs saving even if stay_on_start
                    is False. At minimum, this will be an empty list.
                    (Default: False)
                as_prims - True means to save the data as primitive types
                    for persistent saving. False will save the data as
                    objects.
                    (Default: False)

            RETURNS tuple of the following format:
                [0]: clothes data (Default: mas_clothes_def)
                [1]: hair data (Default: mas_hair_def)
                [2]: pre acs data (Default: [])
                [3]: bbh acs data (Default: [])
                [4]: bfh acs data (Default: [])
                [5]: afh acs data (Default: [])
                [6]: mid acs data (Default: [])
                [7]: pst acs data (Default: [])
                [8]: bba acs data (Default: [])
                [9]: mab acs data (Default: [])
                [10]: bse acs data (Default: [])
                [11]: ase acs data (Default: [])
                [12]: bat acs data (Default: [])
                [13]: mat acs data (Default: [])
                [14]: bmh acs data (Default: [])
                [15]: mmh acs data (Default: [])
            """
            # determine which clothes to save
            if force_clothes or self.clothes.stay_on_start:
                cloth_data = self.clothes
            else:
                cloth_data = mas_clothes_def

            # determine which hair to save
            if force_hair or self.hair.stay_on_start:
                hair_data = self.hair
            else:
                hair_data = mas_hair_def

            state_data = []

            # save clothes and hair
            if as_prims:
                state_data.extend((cloth_data.name, hair_data.name))
            else:
                state_data.extend((cloth_data, hair_data))

            # now acs
            for rec_layer in self.REC_LAYERS:
                if as_prims:
                    state_data.append(self._save_acs(rec_layer, force_acs))
                else:
                    state_data.append(self._save_acs_obj(rec_layer, force_acs))

            # finally return results
            return tuple(state_data)

        def wear_acs(self, acs):
            """
            Wears the given accessory in that accessory's recommended
            spot, as defined by the accessory.

            IN:
                acs - accessory to wear
            """
            self.wear_acs_in(acs, acs.get_rec_layer())

        def wear_acs_in(self, accessory, acs_layer):
            """
            Wears the given accessory

            NOTE: will not allow mismatching layers, unless overrides are
                enabled.

            IN:
                accessory - accessory to wear
                acs_layer - layer to wear the acs in.
            """
            if self.lock_acs or accessory.name in self.acs_list_map:
                # we never wear dupes
                return

            # if the given layer does not match rec layer, force the correct
            # layer unless override
            if (
                    acs_layer != accessory.get_rec_layer()
                    and not self._override_rec_layer
            ):
                acs_layer = accessory.get_rec_layer()

            # verify aso_type is valid for the desired acs layer
            # unless override
            if not self._override_rec_layer:
                if acs_layer in (self.BSE_ACS, self.ASE_ACS):
                    valid_aso_type = MASAccessoryBase.ASO_SPLIT
                else:
                    valid_aso_type = MASAccessoryBase.ASO_REG

                if accessory.aso_type != valid_aso_type:
                    return

            acs_list = self.__get_acs(acs_layer)
            temp_space = {
                "acs_list": acs_list,
            }

            if acs_list is not None and accessory not in acs_list:

                # run pre exclusion code
                store.mas_sprites.acs_wear_mux_pre_change(
                    temp_space,
                    self,
                    accessory,
                    acs_layer
                )

                # abort wearing if we were told to abort
                if temp_space.get("abort", False):
                    return

                # run mutual exclusion for acs
                if accessory.mux_type is not None:
                    self.remove_acs_mux(accessory.mux_type)

                # run post exclusion code
                store.mas_sprites.acs_wear_mux_pst_change(
                    temp_space,
                    self,
                    accessory,
                    acs_layer
                )

                # now insert the acs
                mas_insertSort(acs_list, accessory, MASAccessory.get_priority)

                # add to mappings
                self.acs_list_map[accessory.name] = acs_layer

                acs_type = accessory.acs_type
                if acs_type not in self._acs_type_map:
                    self._acs_type_map[acs_type] = {}
                self._acs_type_map[acs_type][accessory.name] = accessory

                if accessory.name in mas_sprites.lean_acs_blacklist:
                    self.lean_acs_blacklist.append(accessory.name)

                # run pre entry
                store.mas_sprites.acs_wear_entry_pre_change(
                    temp_space,
                    self,
                    accessory,
                    acs_layer
                )

                # run programming point for acs
                accessory.entry(self)

                # run post entry
                store.mas_sprites.acs_wear_entry_pst_change(
                    temp_space,
                    self,
                    accessory,
                    acs_layer
                )

        def wear_acs_pre(self, acs):
            """DEPRECATED
            Wears the given accessory in the pre body accessory mode

            IN:
                acs - accessory to wear
            """
            self.wear_acs_in(acs, self.PRE_ACS)


        def wear_acs_bbh(self, acs):
            """DEPRECATED
            Wears the given accessory in the post back hair accessory loc

            IN:
                acs - accessory to wear
            """
            self.wear_acs_in(acs, self.BBH_ACS)


        def wear_acs_bfh(self, acs):
            """DEPRECATED
            Wears the given accessory in the pre front hair accesory log

            IN:
                acs - accessory to wear
            """
            self.wear_acs_in(acs, self.BFH_ACS)


        def wear_acs_afh(self, acs):
            """DEPRECATED
            Wears the given accessory in the between front hair and arms
            acs log

            IN:
                acs - accessory to wear
            """
            self.wear_acs_in(acs, self.AFH_ACS)


        def wear_acs_mid(self, acs):
            """DEPRECATED
            Wears the given accessory in the mid body acessory mode

            IN:
                acs - acessory to wear
            """
            self.wear_acs_in(acs, self.MID_ACS)


        def wear_acs_pst(self, acs):
            """DEPRECATED
            Wears the given accessory in the post body accessory mode

            IN:
                acs - accessory to wear
            """
            self.wear_acs_in(acs, self.PST_ACS)


    # hues, probably not going to use these
#    hair_hue1 = im.matrix([ 1, 0, 0, 0, 0,
#                        0, 1, 0, 0, 0,
#                        0, 0, 1, 0, 0,
#                        0, 0, 0, 1, 0 ])
#    hair_hue2 = im.matrix([ 3.734, 0, 0, 0, 0,
#                        0, 3.531, 0, 0, 0,
#                        0, 0, 1.375, 0, 0,
#                        0, 0, 0, 1, 0 ])
#    hair_hue3 = im.matrix([ 3.718, 0, 0, 0, 0,
#                        0, 3.703, 0, 0, 0,
#                        0, 0, 3.781, 0, 0,
#                        0, 0, 0, 1, 0 ])
#    hair_hue4 = im.matrix([ 3.906, 0, 0, 0, 0,
#                        0, 3.671, 0, 0, 0,
#                        0, 0, 3.375, 0, 0,
#                        0, 0, 0, 1, 0 ])
#    skin_hue1 = hair_hue1
#    skin_hue2 = im.matrix([ 0.925, 0, 0, 0, 0,
#                        0, 0.840, 0, 0, 0,
#                        0, 0, 0.806, 0, 0,
#                        0, 0, 0, 1, 0 ])
#    skin_hue3 = im.matrix([ 0.851, 0, 0, 0, 0,
#                        0, 0.633, 0, 0, 0,
#                        0, 0, 0.542, 0, 0,
#                        0, 0, 0, 1, 0 ])
#
#    hair_huearray = [hair_hue1,hair_hue2,hair_hue3,hair_hue4]
#
#    skin_huearray = [skin_hue1,skin_hue2,skin_hue3]


    class MASTableChair(object):
        """
        Representation of an available table + chair combo.

        PROPERTIES:
            has_shadow - True if this table has a shadow
            table - table tag associated with this table chair combo
                This will be used in bulding the table sprite string
            chair - chair tag associated with tihs table chair combo
                This will be used in building the chair sprite string
            hl_map - MASHighlightMap associated with this table chair
                keys:
                    t - table
                    ts - table shadow - Used instead of table whenever shadow
                        is applied.
                    c - chair
        """
        from store.mas_sprites import TC_GEN, PREFIX_TABLE, SHADOW_SUFFIX, NIGHT_SUFFIX
        __MHM_KEYS = ("t", "ts", "c")

        def __init__(self, table, chair, hl_data=None):
            """
            constructor

            IN:
                table - table tag to use
                chair - chair tag to use
                hl_data - highlight mapping data. format:
                    [0] - default highilght to use. Pass in None to not set
                        a default.
                    [1] - highlight mapping to use. Format:
                        key: "t" for table, "c" for chair
                        value: MASFilterMap object, or None if no highlight
                    pass in None if no highlights shoudl be used at all
            """
            self.table = table
            self.chair = chair
            self.has_shadow = False
            self.prepare()

            if hl_data is None:
                self.hl_map = None
            else:
                self.hl_map = MASHighlightMap.create_from_mapping(
                    self.__MHM_KEYS,
                    hl_data[0],
                    hl_data[1]
                )

        def __repr__(self):
            return "<TableChair: (table: {0}, chair: {1})>".format(
                self.table,
                self.chair
            )

        def prepare(self):
            """
            Prepares this table chair combo by checking for shadow.
            """
            self.has_shadow = (
                renpy.loadable(self.TC_GEN.format(
                    self.PREFIX_TABLE,
                    self.table,
                    self.SHADOW_SUFFIX,
                    ""
                ))
            )

        def setTable(self, new_table):
            """
            sets the table tag and checks shadow

            IN:
                new_table - the new table tag to set
                    if an invalid string or NOne is passed in, we reset to
                    default
            """
            if new_table:
                self.table = new_table
            else:
                self.table = "def"

            self.prepare()


    class MASArm(object):
        """
        Representation of an "Arm"

        Each Arm consists of of a layered combination:
        NOTE: we re using spaced layers so we can insert more if needed.
        0 - bottom layer. after body-0 but before table. Primary bottom layer.
        5 - middle layer. after table but before body-1.
        10 - top layer. after body-1.

        PROPERTIES:
            tag - the tag string of this arm
            layer_map - mapping of layer exiestence to image code
                key: layer code
                value: True if exists, False if not
            hl_map - MASHighlightMap with layer code keys
        """

        LAYER_BOT = "0"
        LAYER_MID = "5"
        LAYER_TOP = "10"

        __MPA_KEYS = (LAYER_BOT, LAYER_MID, LAYER_TOP)

        def __init__(self, tag, layer_map, hl_data=None):
            """
            Constructor

            IN:
                tag - tag string for this arm
                layer_map - layer map to use
                    key: image layer code
                    value: True if exists, False if not
                hl_data - highlght map data. tuple of the following formaT:
                    [0] - default MASFilterMap to use. Pass in None to
                        not set a default highlight
                    [1] - highlight mapping to use. Format:
                        key: image layer code
                        value: MASFilterMap object, or None if no highlight
                    pass in None if no highlights should be used at all
            """
            self.tag = tag
            self.clean_map(layer_map)
            self.layer_map = layer_map

            if hl_data is not None:
                self.hl_map = MASHighlightMap.create_from_mapping(
                    self.__MPA_KEYS,
                    hl_data[0],
                    hl_data[1]
                )
            else:
                self.hl_map = None

        def __build_loadstrs_hl(self, prefix, layer_code):
            """
            Builds load strings for a hlight from a given map

            IN:
                prefix - prefix to apply
                layer_code - layer code to generate loadstrings for

            RETURNS: list of lists of strings representing image path for all
                highlights for a layer code
            """
            if self.hl_map is None:
                return []

            mfm = self.hl_map.get(layer_code)
            if mfm is None:
                return []

            # generate for all unique
            return [
                prefix + [
                    store.mas_sprites.HLITE_SUFFIX,
                    hlc,
                    store.mas_sprites.FILE_EXT
                ]
                for hlc in mfm.unique_values()
            ]

        @classmethod
        def _fromJSON(cls, json_obj, msg_log, ind_lvl, build_class):
            """
            Builds a MASArm object based on the given JSON format of it

            IN:
                json_obj - JSON object to parse
                ind_lvl - indent level
                build_class - actual MASArm derivative to build

            OUT:
                msg_log - list to save messages to

            RETURNS: MASArm instance built with the JSON, or None if failed
            """
            params = {}
            # start with required params
            # tag
            # layers
            if not store.mas_sprites_json._validate_params(
                    json_obj,
                    params,
                    {
                        "tag": (str, store.mas_sprites_json._verify_str),
                        "layers": (str, store.mas_sprites_json._verify_str),
                    },
                    True,
                    msg_log,
                    ind_lvl
            ):
                return None

            # additional processing for the layers to ensure valid data
            layer_map = {}
            for layer in params.pop("layers").split("^"):
                if layer in cls.__MPA_KEYS:
                    layer_map[layer] = True

                else:
                    # invalid layer
                    # warn and ignore
                    msg_log.append((
                        store.mas_sprites_json.MSG_WARN_T,
                        ind_lvl,
                        store.mas_sprites_json.MA_INVALID_LAYER.format(layer)
                    ))

            # NOTE: ERR if we have no layers for an arm. This is useless to
            # include if no layers.
            if len(layer_map) == 0:
                msg_log.append((
                    store.mas_sprites_json.MSG_ERR_T,
                    ind_lvl,
                    store.mas_sprites_json.MA_NO_LAYERS
                ))
                return None

            # add layers to params
            params["layer_map"] = layer_map

            # now check highlight
            if store.mas_sprites_json.HLITE in json_obj:

                # parse
                vhl_data = {}

                if store.mas_sprites_json._validate_highlight(
                        json_obj,
                        vhl_data,
                        msg_log,
                        ind_lvl,
                        layer_map.keys()
                ):
                    # success
                    hl_data = vhl_data.get("hl_data", None)
                    if hl_data is not None:
                        params["hl_data"] = hl_data

                else:
                    # failure
                    return None

            # warn for extra properties
            for extra_prop in json_obj:
                msg_log.append((
                    store.mas_sprites_json.MSG_WARN_T,
                    ind_lvl,
                    store.mas_sprites_json.EXTRA_PROP.format(extra_prop)
                ))

            # we now should have all the data we need to build
            return build_class(**params)

        def build_loadstrs(self, prefix):
            """
            Builds loadstrs for this arm

            IN:
                prefix - prefix to apply to the loadstrs
                    should be list of strings

            RETURNS: list of lists of strings representing the load strings
                for this arm, + highlights
            """
            if not self.tag:
                return []

            loadstrs = []

            # add arms based on layer code
            for layer_code in self.__MPA_KEYS:
                # NOTE: we only add an arm + hlite if it exists for a layer
                # code

                if self.layer_map.get(layer_code, False):

                    # generate image
                    new_img = prefix + [
                        self.tag,
                        store.mas_sprites.ART_DLM,
                        str(layer_code)
                    ]

                    # add with extension
                    loadstrs.append(new_img + [store.mas_sprites.FILE_EXT])

                    # generate highlights
                    loadstrs.extend(self.__build_loadstrs_hl(
                        new_img,
                        layer_code
                    ))

            return loadstrs

        def clean_map(self, mapping):
            """
            cleans the given map, ensuring it contains only valid layer
            keys. No errors are logged.

            IN:
                mapping - mapping to clean
            """
            for map_key in mapping.keys():
                if map_key not in self.__MPA_KEYS:
                    mapping.pop(map_key)

        def get(self, layer_code, prefix=[]):
            """
            Generates tag name + suffixes to use for
            a given layer code. A tag name is a tuple of strings
            that can be joined to build the full tag name,
            Tag Names do NOT include file extensions

            IN:
                layer_code - layer code to fetch tag names for
                prefix - prefix to apply to the tag string if desired
                    (Default: [])

            RETURNS: list consisting of the tag strings and
                appropriate suffixes
            """
            if not self.tag:
                return []

            # should this item exist on tihs layer code?
            if not self.layer_map.get(layer_code, False):
                return []

            # should exist, generate the primary tag string
            return prefix + [
                self.tag,
                store.mas_sprites.ART_DLM,
                str(layer_code)
            ]

        def gethlc(self, layer_code, flt, defval=None):
            """
            Gets highlight code.

            IN:
                layer_code - layer to get highlight for
                flt - filter to get highilght for
                defval - default value to return
                    (Default: None)

            RETURNS: highlight code, or None if no highligiht
            """
            return MASHighlightMap.o_fltget(
                self.hl_map,
                layer_code,
                flt,
                defval
            )

        def hl_keys(self):
            """
            Returns hl keys for a MASArm

            RETURNS: tuple of hl keys
            """
            return self.__MPA_KEYS

        @classmethod
        def hl_keys_c(cls):
            """
            Class method version of hl_keys

            RETURNS: tuple of hl keys
            """
            return cls.__MPA_KEYS


    class MASArmBoth(MASArm):
        """
        Representation of an "arm" that actually covers both arms

        This currently has no additional behavior.
        It's primary use is to act as a type of MASArm

        PROPERTIES:
            see MASArm
        """
        pass


    class MASArmLeft(MASArm):
        """
        Representation of a left arm.

        Overrides prefix-based functions

        PROPERTIES:
            see MASArm
        """

        def build_loadstrs(self, prefix):
            """
            Generates loadstrs for this arm

            IN:
                prefix - prefix to apply to the loadstrs
                    list of strings

            RETURNS: list of lists of strings representing the loadstrs
            """
            return super(MASArmLeft, self).build_loadstrs(
                prefix + [store.mas_sprites.PREFIX_ARMS_LEFT]
            )

        def get(self, layer_code):
            """
            See MASArm.get

            This adds left- prefix to result
            """
            return super(MASArmLeft, self).get(
                layer_code,
                prefix=["left", store.mas_sprites.ART_DLM]
            )


    class MASArmRight(MASArm):
        """
        Representation of a right arm.

        Overrides prefix-based functions

        PROPERTIES:
            see MASArm
        """

        def build_loadstrs(self, prefix):
            """
            Generates loadstrs for this arm

            IN:
                prefix - prefix to apply to the loadstrs
                    list of strings

            RETURNS: list of lists of strings representing the loadstrs
            """
            return super(MASArmRight, self).build_loadstrs(
                prefix + [store.mas_sprites.PREFIX_ARMS_RIGHT]
            )

        def get(self, layer_code):
            """
            See MASArm.get

            This adds right- prefix to result
            """
            return super(MASArmRight, self).get(
                layer_code,
                prefix=["right", store.mas_sprites.ART_DLM]
            )


    class MASPoseArms(object):
        """
        Collection of MASArm objects. An Arm object is the representation of
        an arm sprite.

        PROPERTIES:
            arms - dict mapping arms to MASArm objects
                keys: number from NUM_ARMS
                value: MASArm object. None means no arm for this arm

        """
        import store.mas_sprites_json as msj

        def __init__(self, arm_data, def_base=True):
            """
            Constructor

            IN:
                arm_data - see arms property
                def_base - True will use base arms for all missing data
                    False will not
                    (Default: True)
            """
            # must have a mas pose arm
            if not store.mas_ev_data_ver._verify_dict(
                    arm_data,
                    allow_none=False
            ):
                raise Exception("arm data required for MASPoseArms")

            # clean arms before setting
            self._clean_arms(arm_data, def_base)
            self.arms = arm_data

        def _clean_arms(self, arm_data, def_base):
            """
            Cleans arm data given
            Will Noneify invalid-typed data

            IN:
                arm_data - arm data to clean
                def_base - True will use base arms for all missing data
                    False will not

            OUT:
                arm_data - cleaned arm data
            """
            # first validate the arm data
            for arm_key in arm_data.keys():

                # then check
                if arm_key in store.mas_sprites.NUM_ARMS:
                    # NOneify invalid data
                    if not isinstance(arm_data[arm_key], MASArm):
                        store.mas_utils.writelog(
                            "Invalid arm data at '{0}'\n".format(arm_key)
                        )
                        arm_data[arm_key] = None

                else:
                    # remove invalid keys
                    arm_data.pop(arm_key)

            # now go through the arm data and set base for all non-included
            # arm data
            if def_base:
                for arm_key in store.mas_sprites.NUM_ARMS:
                    if arm_key not in arm_data:
                        arm_data[arm_key] = store.mas_sprites.use_bma(arm_key)

                # NOTE: if def_base is False, then get will auto return
                #   None so no need to set any data

        def build_loadstrs(self, prefix):
            """
            Generates loadstrs for this PoseArms object

            IN:
                prefix - list of strings to apply as prefix

            RETURNS: list of lists of strings representing the load strs
            """
            loadstrs = []

            # loop over all the arms we have
            for arm_key in self.arms:
                # only od actual arms
                arm = self.arms[arm_key]

                if arm is not None:

                    # check for leans
                    lean = store.mas_sprites.ARMS_LEAN.get(arm_key, None)
                    if lean is None:
                        # no lean, do normal prefix
                        arm_prefix = prefix + [store.mas_sprites.PREFIX_ARMS]
                    else:
                        # have lean, do lean prefix
                        arm_prefix = prefix + [
                            store.mas_sprites.PREFIX_ARMS_LEAN,
                            lean,
                            store.mas_sprites.ART_DLM
                        ]

                    # pass in prefix to the arm
                    loadstrs.extend(arm.build_loadstrs(arm_prefix))

            return loadstrs

        @staticmethod
        def fromJSON(json_obj, msg_log, ind_lvl):
            """
            Builds a MASPoseArms object given a JSON format of it

            IN:
                json_obj - json object to parse
                ind_lvl - indent level

            OUT:
                msg_log - list to save messages to

            RETURNS: MASPoseArms object built using the JSON, None if no
                data to be made, False if error occured
            """
            # NOTE: we can assume type is checked already

            arm_data = {}

            # loop over valid arm data
            isbad = False
            for arm_id, arm_sid in store.mas_sprites.NUM_ARMS.iteritems():
                if arm_sid in json_obj:
                    arm_obj = json_obj.pop(arm_sid)

                    # check object first
                    if arm_obj is None:
                        # None is okay
                        arm_data[arm_id] = None

                    elif not store.mas_sprites_json._verify_dict(arm_obj):
                        # must be dict, however
                        msg_log.append((
                            store.mas_sprites_json.MSG_ERR_T,
                            ind_lvl,
                            store.mas_sprites_json.MPA_BAD_TYPE.format(
                                arm_sid,
                                dict,
                                type(arm_obj)
                            )
                        ))
                        isbad = True

                    else:
                        # otherwise try and parse this data

                        # log loading
                        msg_log.append((
                            store.mas_sprites_json.MSG_INFO_T,
                            ind_lvl,
                            store.mas_sprites_json.MA_LOADING.format(arm_sid)
                        ))

                        # parse
                        arm = MASArm._fromJSON(
                            arm_obj,
                            msg_log,
                            ind_lvl + 1,
                            store.mas_sprites.NUM_MARMS[arm_id]
                        )

                        # check valid
                        if arm is None:
                            # failure case
                            isbad = True

                        else:
                            # log success
                            msg_log.append((
                                store.mas_sprites_json.MSG_INFO_T,
                                ind_lvl,
                                store.mas_sprites_json.MA_SUCCESS.format(
                                    arm_sid
                                )
                            ))

                            # and save the data
                            arm_data[arm_id] = arm

            # now check for extras
            for extra_prop in json_obj:
                msg_log.append((
                    store.mas_sprites_json.MSG_WARN_T,
                    ind_lvl,
                    store.mas_sprites_json.EXTRA_PROP.format(extra_prop)
                ))

            # quit if failures
            if isbad:
                return False

            # NOTE: no 0 data checks because a pose arms with nothing in it
            #   would be considered sleeve/armless (think bikinis)

            # otherwise we are good so we can build
            # NOTE: we never use base options with JSONS.
            #   spritepack creators should always describe each used arm
            #   incase the base poses change
            return MASPoseArms(arm_data, def_base=False)

        def get(self, arm_key):
            """
            Gets the arm data associated with the given arm key

            IN:
                arm_key - key of the arm data to get

            RETURNS: MASArm object requested, or NOne if not available for the
                arm key
            """
            return self.arms.get(arm_key, None)

        def getflp(self, leanpose):
            """
            Retrieves arms assocaited with the given leanpose

            IN:
                leanpose - the leanpose to get arms for

            RETURNS: Tuple of arms associated with the leanpose. None may be
                returned if no arms for the leanpose. The number of arms is
                not a guarantee.
            """
            arm_data = []
            for arm_key in store.mas_sprites.base_mpm.get(leanpose, []):
                arm = self.get(arm_key)
                if arm is not None:
                    arm_data.append(arm)

            if len(arm_data) > 0:
                return tuple(arm_data)

            # otherwse return None because no arms
            return None


    # pose map helps map poses to an image
    class MASPoseMap(renpy.store.object):
        """
        The Posemap helps connect pose names to images

        NOTE: the internal maps are public, but should be converted to
            private.

        This is done via a dict containing pose names and where they
        map to.

        There is also a seperate dict to handle lean variants
        """
        from store.mas_sprites import POSES, L_POSES
        import store.mas_sprites_json as msj

        # pargs
        # NOTE: order MUST be same as POSES
        PARAM_NAMES = (
            "p1", # steeplnig
            "p2", # crossed
            "p3", # restleftpointright
            "p4", # pointright

            "p6", # down
            "p7", # downleftpointright
        )

        # NOTE: order MUST be same as L_POSES
        L_PARAM_NAMES = (
            "p5", # LEAN - def|def
        )

        P_PARAM_NAMES = tuple(list(PARAM_NAMES) + list(L_PARAM_NAMES))

        # all params
        CONS_PARAM_NAMES = (
            "default",
            "l_default",
#            "use_reg_for_l",
        ) + P_PARAM_NAMES

        MPM_TYPE_ED = 0
        # enable/disbale mode
        # each pose should be True/False
        # True enables the pose, False disables.

        MPM_TYPE_FB = 1
        # fallback mode
        # each pose should be a string of the pose to actually use
        # the strings should be pose names (steepling/crossed/etc...)

        MPM_TYPE_AS = 2
        # arm split mode
        # each pose should contain one of the following strings:
        # See MASAccessory for more info

        MPM_TYPE_PA = 3
        # pose arms mode
        # each pose should contain None or a MASPoseArms object

        MPM_TYPE_IC = 4
        # image code mode
        # each pose is a string that determines the code to use
        # NOTE: somewhat identical to FB mode in data held

        MPM_TYPES = (
            MPM_TYPE_ED,
            MPM_TYPE_FB,
            MPM_TYPE_AS,
            MPM_TYPE_PA,
            MPM_TYPE_IC
        )

        def __init__(self,
                # NOTE: when updating params, make sure to modify param name
                #   lists above accordingly.
                mpm_type=0,
                default=None,
                l_default=None,
                use_reg_for_l=False,
                **pargs
            ):
            """
            Constructor

            If None is passed in for any var, we assume that no image should
            be shown for that pose

            IN:
                mpm_type - MASPoseMap type of this posemap
                    Default is 0 (enable/disble mode)
                default - default pose id to use for poses that are not
                    specified (aka are None).
                l_default - default pose id to use for lean poses that are not
                    specified (aka are None).
                use_reg_for_l - if True and default is not None and l_default
                    is None, then we use the default instead of l_default
                    when rendering for lean poses
                **pargs - the remaining name value pairs are checked in param
                    names. Each apply to specific pose.
                    (See MASPoseArms.PARAM_NAMES and L_PARAM_NAMES)
            """
            # setup maps
            poses, lposes = self.__listify(pargs)

            self.map = {}
            for index in range(len(self.POSES)):
                self.map[self.POSES[index]] = poses[index]

            self.l_map = {}
            for index in range(len(self.L_POSES)):
                self.l_map[self.L_POSES[index]] = lposes[index]

            # setup defaults
            self.__default = default
            self.__l_default = l_default
            self.use_reg_for_l = use_reg_for_l
            self.__set_defaults()

            # use all map for quick pose lookup
            self.__all_map = {}
            self.__sync_all()

            self._mpm_type = mpm_type

        def __associate(self, pargs):
            """
            Associates the given pargs (retrieved from **pargs) and with
            index values related to POSES and L_POSES

            IN:
                pargs - dict retrieved from a **pargs var

            RETURNS: tuple of the following format:
                [0] - POSES associations. List of tuples:
                    [0] - index to map
                    [1] - parg value to map to
                [1] - L_POSES associations. List of tuples:
                    [0] - index to map
                    [1] - parg value to map to
            """
            return (
                [
                    (index, pargs[self.PARAM_NAMES[index]])
                    for index in range(len(self.POSES))
                    if self.PARAM_NAMES[index] in pargs
                ],
                [
                    (index, pargs[self.L_PARAM_NAMES[index]])
                    for index in range(len(self.L_POSES))
                    if self.L_PARAM_NAMES[index] in pargs
                ]
            )

        def __listify(self, pargs):
            """
            Takes the pargs and generates lists of them in the same order as
            POSES and L_POSES.

            If an item doesnt exist in pargs, None is used

            IN:
                pargs - dict retrieved from a **pargs var

            RETURNS: tuple of hte following format:
                [0] - list of pose values from pargs, in order of POSES
                [1] - list of lean values from pargs, in order of L_POSES
            """
            return (
                [ pargs.get(param, None) for param in self.PARAM_NAMES ],
                [ pargs.get(lparam, None) for lparam in self.L_PARAM_NAMES ],
            )

        def __set_defaults(self):
            """
            Sets all pose defaults
            """
            self.__set_posedefs(self.map, self.__default)
            if (
                    self.use_reg_for_l
                    and self.__l_default is None
                    and self.__default is not None
            ):
                self.__set_posedefs(self.l_map, self.__default)
            else:
                self.__set_posedefs(self.l_map, self.__l_default)

        def __set_posedefs(self, pose_dict, _def):
            """
            Sets pose defaults

            IN:
                pose_dict - dict of poses
                _def - default to use here
            """
            for k in pose_dict:
                if pose_dict[k] is None:
                    pose_dict[k] = _def

        def __sync_all(self):
            """
            Syncs internal all map with the internal maps
            """
            self.__all_map.update(self.map)
            self.__all_map.update(self.l_map)

        def _modify(self, **pargs):
            """
            Modifes poses based on given pargs.
            NOTE: this can damage the sprite system if done incorrectly.

            IN:
                **pargs - param name-value pairs. See MASPoseArms.PARAM_NAMES
                    and MASPoseArms.L_PARAM_NAMES
            """
            pose_changes, lpose_changes = self.__associate(pargs)
            for index, new_value in pose_changes:
                self.map[self.POSES[index]] = new_value

            for index, new_value in lpose_changes:
                self.l_map[self.L_POSES[index]] = new_value

            # re-set defaults if needed
            self.__set_defaults()

            # now update the all map
            self.__sync_all()

        def _transform(self, func):
            """
            Applies the given function to transform value in each pose
            NOTE: this can damage the sprite system if done incorrectly

            IN:
                func - function to call for each pose. The current vlaue for
                    each pose is passed in. The return value of this function
                    is set to the pose.
            """
            for pose in self.map:
                self.map[pose] = func(self.map[pose])
            for lpose in self.l_map:
                self.l_map[lpose] = func(self.l_map[lpose])

            # set defaults if needed
            self.__set_defaults()

            # update the all map
            self.__sync_all()

        @classmethod
        def _verify_mpm_item(cls,
                mpm_data,
                msg_log,
                ind_lvl,
                mpm_type,
                prop_name,
                prop_val
        ):
            """
            Verifies data for an mpm item based on type

            IN:
                ind_lvl - indent lvl
                mpm_type - mpm type to check values for
                prop_name - name of the item to check
                prop_val - value of the item to check

            OUT:
                mpm_data - dict to save data to
                msg_log - list to add messages to

            RETURNS: True if successful verification, False if not
            """
            if mpm_type == cls.MPM_TYPE_IC:
                # image code usage means each item should be a string

                if cls.msj._verify_str(prop_val):
                    mpm_data[prop_name] = prop_val

                else:
                    msg_log.append((
                        cls.msj.MSG_ERR_T,
                        ind_lvl,
                        cls.msj.MPM_BAD_POSE_TYPE.format(
                            prop_name,
                            str,
                            type(prop_val)
                        )
                    ))
                    return False

            if mpm_type == cls.MPM_TYPE_AS:
                # arm split mean each item should be a string

                if MASSplitAccessory.verify_arm_split_val(prop_val):
                    mpm_data[prop_name] = prop_val

                else:
                    msg_log.append((
                        cls.msj.MSG_ERR_T,
                        ind_lvl,
                        cls.msj.MPM_AS_BAD_TYPE.format(
                            prop_name,
                            str(MASSplitAccessory.hl_keys()),
                            prop_val
                        )
                    ))
                    return False

            if mpm_type == cls.MPM_TYPE_ED:
                # enable/disable uses bools

                if cls.msj._verify_bool(prop_val):
                    mpm_data[prop_name] = prop_val

                else:
                    msg_log.append((
                        cls.msj.MSG_ERR_T,
                        ind_lvl,
                        cls.msj.MPM_BAD_POSE_TYPE.format(
                            prop_name,
                            bool,
                            type(prop_val)
                        )
                    ))
                    return False

            if mpm_type == cls.MPM_TYPE_FB:
                # fallbacks use poses (as strings)

                if cls.msj._verify_pose(prop_val, allow_none=False):
                    mpm_data[prop_name] = prop_val

                else:
                    msg_log.append((
                        cls.msj.MSG_ERR_T,
                        ind_lvl,
                        cls.msj.MPM_BAD_POSE.format(
                            prop_name,
                            prop_val
                        )
                    ))
                    return False

            # invalid types should not be an issue here, so no warning
            return True

        @classmethod
        def fromJSON(cls, json_obj, msg_log, ind_lvl, valid_types=None):
            """
            Builds a MASPoseMap given a JSON format of it

            IN:
                json_obj - json object to parse
                ind_lvl - indent lvl
                valid_types - tuple/list of MPM types we should consider valid.
                    NOTE: this should be used by the caller to ensure that
                    the MPM being loaded is the correct one.
                    If not passed, then we don't check for valid types

            OUT:
                msg_log - list to add messages to

            RETURNS: MASPoseMap object built using the JSON, or None if failed
            """
            mpm_prop = "mpm_type"
            urfl_prop = "use_reg_for_l"
            mpm_data = {}

            # verify mpm type
            if mpm_prop not in json_obj:
                msg_log.append((
                    cls.msj.MSG_ERR_T,
                    ind_lvl,
                    cls.msj.REQ_MISS.format(mpm_prop)
                ))
                return None

            mpm_type = json_obj.pop(mpm_prop)

            if not cls.msj._verify_int(mpm_type, allow_none=False):
                msg_log.append((
                    cls.msj.MSG_ERR_T,
                    ind_lvl,
                    cls.msj.BAD_TYPE.format(mpm_prop, int, type(mpm_type))
                ))
                return None

            if mpm_type not in cls.MPM_TYPES:
                msg_log.append((
                    cls.msj.MSG_ERR_T,
                    ind_lvl,
                    cls.msj.MPM_BAD_TYPE.format(mpm_type)
                ))
                return None

            if valid_types is not None and mpm_type not in valid_types:
                msg_log.append((
                    cls.msj.MSG_ERR_T,
                    ind_lvl,
                    cls.msj.MPM_TYPE_MISS.format(valid_types, mpm_type)
                ))
                return None

            mpm_data[mpm_prop] = mpm_type

            # verify use_reg_for_l
            if urfl_prop in json_obj:
                use_reg_for_l = json_obj.pop(urfl_prop)
                if not cls.msj._verify_bool(use_reg_for_l, allow_none=False):
                    msg_log.append((
                        cls.msj.MSG_ERR_T,
                        ind_lvl,
                        cls.msj.BAD_TYPE.format(
                            urfl_prop,
                            str,
                            type(use_reg_for_l)
                        )
                    ))
                    return None

                mpm_data[urfl_prop] = use_reg_for_l

            else:
                use_reg_for_l = None

            # verify other params
            isbad = False
            for prop_name in json_obj.keys():
                prop_val = json_obj.pop(prop_name)
                if prop_name in cls.CONS_PARAM_NAMES:
                    if not cls._verify_mpm_item(
                            mpm_data,
                            msg_log,
                            ind_lvl,
                            mpm_type,
                            prop_name,
                            prop_val
                    ):
                        isbad = True

                else:
                    # prop name NOT part of MASPoseMap. log as warning.
                    msg_log.append((
                        cls.msj.MSG_WARN_T,
                        ind_lvl,
                        cls.msj.EXTRA_PROP.format(prop_name)
                    ))

            # finally check for valid params
            if isbad:
                return None

            # we should alwyas suggest a default
            _param_urfl = mpm_data.get("use_reg_for_l", False)
            if "default" not in mpm_data:
                msg_log.append((
                    cls.msj.MSG_WARN_T,
                    ind_lvl,
                    cls.msj.MPM_DEF
                ))

            if "l_default" not in mpm_data and not _param_urfl:
                # we suggest using lean default when in fallback mode or
                #   acs
                # and not using reg for l
                msg_log.append((
                    cls.msj.MSG_WARN_T,
                    ind_lvl,
                    cls.msj.MPM_DEF_L
                ))

            return MASPoseMap(**mpm_data)

        def get(self, pose, defval):
            """
            Get passed to the internal pose map
            only because its common to call get on this object.

            IN:
                pose - pose to get from pose map
                defval - default value to return if pose not found

            RETURNS:
                value of pose in internal dict, or defval if not found
            """
            return self.__all_map.get(pose, defval)

        def is_fallback(self):
            """
            Checks if this posemap is a fallback one via type.

            RETURNS: True if this posemap is a fallback one, False if not
            """
            return self._mpm_type == self.MPM_TYPE_FB

        def unique_values(self):
            """
            Gets all unique non-None values in this MASPoseMap.
            NOTE: because MPM's may not include hashable values, this is
            try/excepted to handle those cases. If something is non-hashable,
            we always return all values.

            RETURNS: list of unique non-None values in this MASPoseMap
            """
            try:
                values = []
                for value in self.__all_map.itervalues():
                    if value is not None and value not in values:
                        values.append(value)

                return values
            except:
                return self.values()

        def values(self):
            """
            Gets all non-None values in this MASPoseMap.

            RETURNS: list of all non-None values in this MASPoseMap
            """
            return [
                value
                for value in self.__all_map.itervalues()
                if value is not None
            ]

        @staticmethod
        def lp2pn(leanpose):
            """
            Converts a leanpose to a PARAM NAME

            IN:
                leanpose - leanpose to convert

            RETURNS: param name associated with leanpose, or "" if not valid
            """
            if leanpose in MASPoseMap.POSES:
                return MASPoseMap.PARAM_NAMES[MASPoseMap.POSES.index(leanpose)]

            if leanpose in MASPoseMap.L_POSES:
                return MASPoseMap.L_PARAM_NAMES[MASPoseMap.L_POSES.index(
                    leanpose
                )]

            return ""

        @staticmethod
        def pn2lp(name):
            """
            Converts a PARAM NAME to a leanpose

            IN:
                name - name of the param to convert

            RETURNS: leanpose associated with param name, or "" if not valid
            """
            if name in MASPoseMap.PARAM_NAMES:
                return MASPoseMap.POSES[MASPoseMap.PARAM_NAMES.index(name)]

            if name in MASPoseMap.L_PARAM_NAMES:
                return MASPoseMap.L_POSES[MASPoseMap.L_PARAM_NAMES.index(name)]

            return ""

    # base class for MAS sprite things
    class MASSpriteBase(renpy.store.object):
        """
        Base class for MAS sprite objects

        PROPERTIES:
            name - name of the item
            img_sit - filename of the sitting version of the item
            img_stand - filename of the standing version of the item
            pose_map - MASPoseMap object that contains pose mappings
            stay_on_start - determines if the item stays on startup
            entry_pp - programmign point to call when wearing this sprite
                the MASMonika object that is being changed is fed into this
                function
                NOTE: this is called after the item is added to MASMonika
            exit_pp - programming point to call when taking off this sprite
                the MASMonika object that is being changed is fed into this
                function
                NOTE: this is called before the item is removed from MASMonika
            is_custom - True if this is a custom object. False if not.
                NOTE: this must be set AFTER object creation
            hl_map - MASHighlightMap. Actual implementation may vary by extended
                classes
        """
        import store.mas_sprites_json as msj

        def __init__(self,
                name,
                img_sit,
                pose_map,
                img_stand="",
                stay_on_start=False,
                entry_pp=None,
                exit_pp=None,
                ex_props=None,
                full_hl_data=None
            ):
            """
            MASSpriteBase constructor

            IN:
                name - name of this item
                img_sit - filename of the sitting image
                pose_map - MASPoseMAp object that contains pose mappings
                img_stand - filename of the standing image
                    If this is not passed in, this is considered blacklisted
                    from standing sprites.
                    (Default: "")
                stay_on_start - True means the item should reappear on startup
                    False means the item should always drop when restarting.
                    (Default: False)
                entry_pp - programming point to call when wearing this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                exit_pp - programming point to call when taking off this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                ex_props - dict of additional properties to apply to this
                    sprite object.
                    (Default: None)
                full_hl_data - tuple of the following format:
                    [0] - keys to use for MASHighlightMap
                    [1] - default value for MASHighlightMap
                        if None, no default highlights
                    [2] - mapping dict of the following format:
                        key: key in [0]
                        value: value to use for key
                            if None, no highlight for this key
                        if None, no mapped highlights
                    if None, no highlights at all
                    (Default: None)
            """
            self.__sp_type = -1
            self.name = name
            self.img_sit = img_sit
            self.img_stand = img_stand
            self.stay_on_start = stay_on_start
            self.pose_map = pose_map
            self.entry_pp = entry_pp
            self.exit_pp = exit_pp
            self.is_custom = False

            if type(pose_map) != MASPoseMap:
                raise Exception("PoseMap is REQUIRED")

            #sets the ex_props to an empty dict if ex_props is None
            if ex_props is None:
                self.ex_props = {}
            else:
                self.ex_props = ex_props

            # setup exprop related material
            self.default_exprops()
            self.format_exprops()

            # setup highlight map
            self.__setup_hl_map(full_hl_data)

        def __eq__(self, other):
            """
            Equality override
            """
            if isinstance(other, MASSpriteBase):
                return self.name == other.name

            return NotImplemented

        def __ne__(self, other):
            """
            Not equal override
            """
            result = self.__eq__(other)
            if result is NotImplemented:
                return result
            return not result

        def __setup_hl_map(self, hl_data):
            """
            Sets up the highlight map

            IN:
                hl_data - See constructor for description
            """
            if hl_data is None:
                self.hl_map = None
                return

            # no highlght if filled with Nones
            hl_keys, hl_def, hl_mapping = hl_data
            if hl_def is None and hl_mapping is None:
                self.hl_map = None
                return

            # otherwise we can generate this map
            self.hl_map = MASHighlightMap.create_from_mapping(
                hl_keys,
                hl_def,
                hl_mapping
            )

        def addprop(self, prop):
            """
            Adds the given prop to the ex_props list

            IN:
                prop - prop to add
            """
            self.ex_props[prop] = True

        def build_loadstrs(self, prefix):
            """
            Build list of strings representing each image that may be used
            in this sprite.

            NOTE: this should be implemented by the extending classes

            IN:
                prefix - prefix to apply to each image. should be list of
                    strings
                    (DEfault: "")

            RETURNS: list of lists of strings represented in this image.
                use .join on each inner list to make the image
            """
            raise NotImplementedError

        def default_exprops(self):
            """
            Called after sprite creation in the base class. This should be
            implemented by sprite object classes as appropraite.

            the only things that should happen in here are defaulting of
            exprops as a result of other exprops.

            All code in here should be safe to call more than once.
            """
            pass

        def entry(self, _monika_chr, **kwargs):
            """
            Calls the entry programming point if it exists

            IN:
                _monika_chr - the MASMonika object being changed
                **kwargs - other keyword args to pass
            """
            if self.entry_pp is not None:
                self.entry_pp(_monika_chr, **kwargs)

        def exit(self, _monika_chr, **kwargs):
            """
            Calls the exit programming point if it exists

            IN:
                _monika_chr - the MASMonika object being changed
                **kwargs - other keyword args to pass
            """
            if self.exit_pp is not None:
                self.exit_pp(_monika_chr, **kwargs)

        def format_exprops(self):
            """
            Called after sprite creation in the base class, after exprops
            have been defaulted in. This should be implemented by sprite object
            classes as appropriate.

            The only things that should happen here are adjusting formats
            of exprops so they are valid/uniform/as expected by consuming code

            All code in here should be safe to call more than once.
            """
            pass

        def gethlc(self, *args, **kwargs):
            """
            Gets highlight code

            NOTE: actual args and implementation should be handled by the
                extended classes

            RETURNS: highlight code, or defval if no highlight
            """
            raise NotImplementedError

        def getprop(self, prop, defval=None):
            """
            Gets the exprop

            IN:
                prop - prop to get
                defval - default value to return if prop not found
            """
            return self.ex_props.get(prop, defval)

        def gettype(self):
            """
            Gets the type of this sprite object

            RETURNS: type of this sprite object
            """
            return self.__sp_type

        def hasprogpoints(self):
            """
            RETURNS: true if this sprite object has at least 1 non-null prog
                point, False otherwise
            """
            return self.entry_pp is not None or self.exit_pp is not None

        def hasprop(self, prop):
            """
            Checks if this sprite object has the given prop

            IN:
                prop - prop in ex_props to look for

            RETURNS: True if this sprite object has the ex_prop, False if not
            """
            return prop in self.ex_props

        def hl_keys(self):
            """
            Gets keys used for the MASHighlightMap

            RETURNS: keys used in the primary level of this MASHighlightMap.
            An empty list is returned if no hl map or no keys
            """
            if self.hl_map is None:
                return []

            return self.hl_map.keys()

        def rmprop(self, prop):
            """
            Removes the prop from this sprite's ex_props, if it exists

            IN:
                prop - prop to remove

            RETURNS: True if the prop was found and removed, False otherwise
            """
            if prop in self.ex_props:
                self.ex_props.pop(prop)
                return True

            return False

        @staticmethod
        def sortkey(sprite_base):
            """
            Returns the sorting key of the given MASSpriteBase object
            """
            if isinstance(sprite_base, MASSpriteBase):
                return sprite_base.name

            return ""

    class MASSpriteFallbackBase(MASSpriteBase):
        """
        MAS sprites that can use pose maps as fallback maps.

        PROPERTIES:
            None

        SEE MASSpriteBase for inherited properties
        """

        def __init__(self,
                name,
                img_sit,
                pose_map,
                img_stand="",
                stay_on_start=False,
                fallback=False,
                entry_pp=None,
                exit_pp=None,
                ex_props=None,
                full_hl_data=None
            ):
            """
            MASSpriteFallbackBase constructor

            IN:
                name - name of this item
                img_sit - filename of the sitting image for this item
                pose_map - MASPoseMap object that contains pose mappings or
                    fallback mappings
                img_stand - filename of the stnading image
                    If this is not passed in, this is considered blacklisted
                    from standing sprites.
                    (Default: "")
                stay_on_start - True means the item should reappear on startup
                    False means the item should always drop when restarting
                    (Default: False)
                fallback - Unused
                entry_pp - programming point to call when wearing this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                exit_pp - programming point to call when taking off this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                ex_props - dict of additional properties to apply to this
                    sprite object.
                    (Default: None)
                hl_data - tuple of the following format:
                    [0] - keys to use for MASHighlightMap
                    [1] - default value for MASHighlightMap
                        if None, no default highlights
                    [2] - mapping dict of the following format:
                        key: key in [0]
                        value: value to use for key
                            if None, no highlight for this key
                        if None, no mapped highlights
                    if None, no highlights at all
                    (Default: None)
            """
            super(MASSpriteFallbackBase, self).__init__(
                name,
                img_sit,
                pose_map,
                img_stand,
                stay_on_start,
                entry_pp,
                exit_pp,
                ex_props,
                full_hl_data
            )
            self.__sp_type = -2

        def get_fallback(self, pose, lean):
            """
            Gets the fallback pose for a given pose or lean

            NOTE: the fallback variable is NOT checked

            Lean is checked first if its not None.

            IN:
                pose - pose to retrieve fallback for
                lean - lean to retrieve fallback for

            RETURNS:
                tuple fo thef ollowing format:
                [0]: arms type
                    - default for this is steepling
                [1]: lean type
                    - defualt for this is None
            """
            # now check for fallbacks
            if lean is not None:
                # we have a lean, check for fallbacks
                fb_lean = self.pose_map.l_map.get(lean + "|" + pose, None)

                # no fallback? assume steepling
                if fb_lean is None:
                    return ("steepling", None)

                # a pipe means we are dealing with a lean fallback
                if "|" in fb_lean:
                    return fb_lean.split("|")

                # otherwise we can assume its an arms fall back
                return (fb_lean, None)

            # otherwise check the pose
            return (self.pose_map.map.get(pose, "steepling"), None)

        def get_leanpose(self, leanpose, defval=None):
            """
            Gets actual leanpose based on posemaps + fallback settings

            IN:
                leanpose - leanpose we are trying to get actual leanpose for
                defval - default value to return if no leanpose
                    (Default: None)


            RETURNS: actual leanpose, or defval if not found
            """
            # cehck fallback
            if self.pose_map.is_fallback():
                return self.pose_map.get(leanpose, defval)

            # check enabled
            if self.pose_map.get(leanpose, False):
                return leanpose

            # otherwise disabled so return defval
            return defval


    # instead of clothes, these are accessories
    class MASAccessoryBase(MASSpriteBase):
        """
        MASAccesory base objects

        PROPERTIES:
            priority - render priority. Lower is rendered first
            acs_type - an optional type to help organize acs
            mux_type - list of acs types that we shoudl treat
                as mutally exclusive with this type. Basically if this acs is
                worn, all acs with a type in this property are removed.
            dlg_desc - user friendly way to describe this accessory in dialogue
                Think "black bow" or "silver earrings"
            dlg_plur - True if the dlg_desc should be used in the plural
                sense, like "these silver earrings", False if not, like:
                "this black bow"
            keep_on_desk - Set to True to keep the ACS on the desk when monika
                leaves, False if not
            hl_map - MASHighlightMap object where keys are defined by the given
                posemap. Value determined by extending classes.

        SEE MASSpriteBase for inherited properties
        """

        # Accessory Sprite Object types

        ASO_REG = 1
        # regular accessory

        ASO_SPLIT = 2
        # split accessory type

        ASO_TYPES = (
            ASO_REG,
            ASO_SPLIT
        )

        def __init__(self,
                aso_type,
                name,
                img_sit,
                pose_map,
                img_stand="",
                rec_layer=MASMonika.PST_ACS,
                priority=10,
                stay_on_start=False,
                entry_pp=None,
                exit_pp=None,
                acs_type=None,
                mux_type=None,
                ex_props=None,
                dlg_data=None,
                keep_on_desk=False,
                hl_data=None
            ):
            """
            MASAccessory constructor

            IN:
                aso_type - Accessory Sprite Object type
                name - name of this accessory
                img_sit - file name of the sitting image
                pose_map - MASPoseMap object that contains pose mappings
                img_stand - file name of the standing image
                    IF this is not passed in, we assume the standing version
                        has no accessory.
                    (Default: "")
                rec_layer - recommended layer to place this accessory
                    (Must be one the ACS types in MASMonika)
                    (Default: MASMonika.PST_ACS)
                priority - render priority. Lower is rendered first
                    (Default: 10)
                stay_on_start - True means the accessory is saved for next
                    startup. False means the accessory is dropped on next
                    startup.
                    (Default: False)
                entry_pp - programming point to call when wearing this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                exit_pp - programming point to call when taking off this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                acs_type - type, for ease of organization of acs
                    This works with mux type to determine if an ACS can work
                    with another ACS.
                    (Default: None)
                mux_type - list of acs types that should be
                    mutually exclusive with this acs.
                    this works with acs_type to determine if this works with
                    other ACS.
                    (Default: None)
                ex_props - dict of additional properties to apply to this
                    sprite object.
                    (Default: None)
                dlg_data - tuple of the following format:
                    [0] - string to use for dlg_desc
                    [1] - boolean value for dlg_plur
                    (Default: None)
                keep_on_desk - determines if ACS should be shown if monika
                    leaves
                    (Default: False)
                hl_data - tuple of the following format:
                    [0] - default value for MASHighlightMap
                        if None, no default highlight
                    [1] - dict-based highlight map data:
                        key: string. should match values used in pose_map
                        value: highlight data. Determined by extended classes.
                            if None, then no highlight for the key
                        if None, then no mapped highlights
                    if None, no highlights at all
                    (Default: None)
            """
            super(MASAccessoryBase, self).__init__(
                name,
                img_sit,
                pose_map,
                img_stand,
                stay_on_start,
                entry_pp,
                exit_pp,
                ex_props,
                MASAccessoryBase._prepare_hl_data(hl_data, pose_map)
            )
            self.aso_type = aso_type
            self.__rec_layer = rec_layer
            self.__sp_type = store.mas_sprites_json.SP_ACS
            self.priority=priority
            self.acs_type = acs_type
            self.mux_type = mux_type
            self.keep_on_desk = keep_on_desk

            if dlg_data is not None and len(dlg_data) == 2:
                self.dlg_desc, self.dlg_plur = dlg_data
            else:
                self.dlg_desc = None
                self.dlg_plur = None

        @staticmethod
        def _prepare_hl_data(hl_data, pose_map):
            """
            Generates hl-ready data from ahldata

            IN:
                hl_data - ahl data. See constructor for info
                pose_map - pose map. see constructor for info

            RETURNS: hl data to pass into MASSpriteBase
            """
            # NOTE: if pose map is None, this will crash in MASSpriteBase
            if hl_data is None or pose_map is None:
                return None

            # splitup ahl data
            hl_def, hl_mapping = hl_data

            # pose map values are the keys
            hl_keys = pose_map.unique_values()

            # now generate the hl data
            return (hl_keys, hl_def, hl_mapping)

        def format_exprops(self):
            """
            Override of base class function
            """
            super(MASAccessoryBase, self).format_exprops()

            # format required-hair-prop into list if itsnt
            # NOTE: no handilng for non-string types
            req_hair_prop = self.getprop(store.mas_sprites.EXP_A_RQHP)
            if store.mas_sprites_json._verify_str(req_hair_prop, False):
                self.ex_props[store.mas_sprites.EXP_A_RQHP] = [req_hair_prop]

        @staticmethod
        def get_priority(acs):
            """
            Gets the priority of the given accessory

            This is for sorting
            """
            return acs.priority

        def get_arm_split_code(self, poseid):
            """DEPRECATED
            NOTE: we are keeping this around for compatiblity purposes

            IN:
                poseid - ignored

            RETURNS: empty list
            """
            return []

        def get_rec_layer(self):
            """
            Returns the recommended layer ofr this accessory

            RETURNS:
                recommend MASMOnika accessory type for this accessory
            """
            return self.__rec_layer

        def opt_gethlc(self, poseid, flt, arm_split, defval=None):
            """
            Optimized highlight code getter. Implementation varies in
            extended classes.
            The point of this is to avoid additional lookups during render.
            """
            raise NotImplementedError


    class MASAccessory(MASAccessoryBase):
        """
        Standard MASAccessory object.

        PROPERTIES:
            hl_map - MASHighlightMap containing MASFilterMap objects.

        See MASAccessoryBase for inherited properties.
        """

        def __init__(self,
                name,
                img_sit,
                pose_map,
                img_stand="",
                rec_layer=MASMonika.PST_ACS,
                priority=10,
                stay_on_start=False,
                entry_pp=None,
                exit_pp=None,
                acs_type=None,
                mux_type=None,
                ex_props=None,
                dlg_data=None,
                keep_on_desk=False,
                hl_data=None
        ):
            """
            Constructor.

            IN:
                name - name of this accessory
                img_sit - file name of the sitting image
                pose_map - MASPoseMap object that contains pose mappings
                img_stand - file name of the standing image
                    IF this is not passed in, we assume the standing version
                        has no accessory.
                    (Default: "")
                rec_layer - recommended layer to place this accessory
                    (Must be one the ACS types in MASMonika)
                    (Default: MASMonika.PST_ACS)
                priority - render priority. Lower is rendered first
                    (Default: 10)
                stay_on_start - True means the accessory is saved for next
                    startup. False means the accessory is dropped on next
                    startup.
                    (Default: False)
                entry_pp - programming point to call when wearing this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                exit_pp - programming point to call when taking off this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                acs_type - type, for ease of organization of acs
                    This works with mux type to determine if an ACS can work
                    with another ACS.
                    (Default: None)
                mux_type - list of acs types that should be
                    mutually exclusive with this acs.
                    this works with acs_type to determine if this works with
                    other ACS.
                    (Default: None)
                ex_props - dict of additional properties to apply to this
                    sprite object.
                    (Default: None)
                dlg_data - tuple of the following format:
                    [0] - string to use for dlg_desc
                    [1] - boolean value for dlg_plur
                    (Default: None)
                keep_on_desk - determines if ACS should be shown if monika
                    leaves
                    (Default: False)
                hl_data - ACS highlight data. Format: tuple:
                    [0] - default MASFilterMap highlight to use
                        if None, then no default highlight
                    [1] - dict of the following format:
                        key: values used for pose_map
                        value: MASFilterMap to associate with that pose id
                            None means no highlight for the pose code
                        if None, then no mapped highlights
                    if None, then no highlights at all
                    (Default: None)
            """
            super(MASAccessory, self).__init__(
                self.ASO_REG,
                name,
                img_sit,
                pose_map,
                img_stand,
                rec_layer,
                priority,
                stay_on_start,
                entry_pp,
                exit_pp,
                acs_type,
                mux_type,
                ex_props,
                dlg_data,
                keep_on_desk,
                hl_data
            )

        def __repr__(self):
            return "<ACS: {0}>".format(self.name)

        def __build_loadstrs_hl(self, prefix, poseid):
            """
            Builds highlight load strs for a pose

            IN:
                prefix - prefix to apply to the load strings
                    should be a list of strings
                poseid - pose id to find highlights for

            RETURNS: list of lists of strings
            """
            if self.hl_map is None:
                return []

            # get filter map
            mfm = self.hl_map.get(poseid)
            if mfm is None:
                return []

            # get all unique filter values
            return [
                prefix + [
                    store.mas_sprites.HLITE_SUFFIX,
                    hlc,
                    store.mas_sprites.FILE_EXT
                ]
                for hlc in mfm.unique_values()
            ]

        def build_loadstrs(self, prefix):
            """
            See MASSpriteBase.build_loadstrs
            """
            loadstrs = []

            # loop over MASPoseMap for pose ids
            for poseid in self.pose_map.unique_values():
                # generate new img str
                new_img = prefix + [
                    store.mas_sprites.PREFIX_ACS,
                    self.img_sit,
                    store.mas_sprites.ART_DLM,
                    poseid,
                ]

                # add the image
                loadstrs.append(new_img + [store.mas_sprites.FILE_EXT])

                # highlights
                loadstrs.extend(self.__build_loadstrs_hl(new_img, poseid))

            return loadstrs

        def gethlc(self, leanpose, flt, hl_key, defval=None):
            """
            Gets highlight code.
            NOTE: if you already know the poseid, use opt_gethlc

            IN:
                leanpose - leanpose to get highlight for
                flt - filter to get highlight for
                hl_key - unused
                defval - default value to return
                    (Default: None)

            RETURNS: highlight code, or None if no highlight
            """
            return self.opt_gethlc(
                self.pose_map.get(leanpose, None),
                flt,
                None,
                defval
            )

        def opt_gethlc(self, poseid, flt, arm_split, defval=None):
            """
            MASAccessory-specific gethlc.
            Optimized to only accept the args that actually matter for
            MASAccessory objects.

            IN:
                poseid - string from pose_map
                flt - fitler to get highlight for
                arm_split - unused
                defval - default value to return
                    (Default: None)

            RETURNS: highlight code, or None if no highlight
            """
            return MASHighlightMap.o_fltget(self.hl_map, poseid, flt, defval)


    class MASSplitAccessory(MASAccessoryBase):
        """
        MASSplitAccessory object. For accessories that should be placeable
        at split layers (ASE/BSE)

        PROPERTIES:
            arm_split - MASPoseMap determining which arm position the ACS
                should be visible in. This only applies to ACS that are
                intended to be used in a BSE or ASE ACS layer.
                This accepts the following values for poses;
                    "0" - sprite has "-0" version, and should be used for
                        arms-0 for this pose or body-0
                    "1" - sprite has "-1" version, and should be used for
                        body-1
                    "5" - sprite has "-5" version, and should be used for
                        arms-5 for this pose
                    "10" - sprite has "-10" version, and should be used for
                        arms-10
                    "" - sprite does not have any arm split for this pose
                    "*" - sprite has an arm split for all poses.
                    A ^ (caret) delimted string is also acceptable:
                        1^5^10
            hl_map - MASHighlightMap (with same keys as pose_map values) of
                MASHighlightMap objects (with same keys as arm_split values)
                of MASFilterMap objects.

        See MASAccessoryBase for inherited propeties
        """

        __MHM_KEYS = ("0", "1", "5", "10")
        # valid MAShlightMap keys for this object
        # also known as the arm codes

        __ASE_KEYS = ("0", "5", "10")
        __BSE_KEYS = ("0", "1")
        # layer-specific keys

        def __init__(self,
                name,
                img_sit,
                pose_map,
                img_stand="",
                rec_layer=MASMonika.PST_ACS,
                priority=10,
                stay_on_start=False,
                entry_pp=None,
                exit_pp=None,
                acs_type=None,
                mux_type=None,
                ex_props=None,
                arm_split=None,
                dlg_data=None,
                keep_on_desk=False,
                hl_data=None
            ):
            """
            MASSplitAccessory constructor

            IN:
                name - name of this accessory
                img_sit - file name of the sitting image
                pose_map - MASPoseMap object that contains pose mappings
                img_stand - file name of the standing image
                    IF this is not passed in, we assume the standing version
                        has no accessory.
                    (Default: "")
                rec_layer - recommended layer to place this accessory
                    (Must be one the ACS types in MASMonika)
                    (Default: MASMonika.PST_ACS)
                priority - render priority. Lower is rendered first
                    (Default: 10)
                stay_on_start - True means the accessory is saved for next
                    startup. False means the accessory is dropped on next
                    startup.
                    (Default: False)
                entry_pp - programming point to call when wearing this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                exit_pp - programming point to call when taking off this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                acs_type - type, for ease of organization of acs
                    This works with mux type to determine if an ACS can work
                    with another ACS.
                    (Default: None)
                mux_type - list of acs types that should be
                    mutually exclusive with this acs.
                    this works with acs_type to determine if this works with
                    other ACS.
                    (Default: None)
                ex_props - dict of additional properties to apply to this
                    sprite object.
                    (Default: None)
                arm_split - MASPoseMap object for determining arm splits. See
                    property list above for more info.
                    (Default: None)
                dlg_data - tuple of the following format:
                    [0] - string to use for dlg_desc
                    [1] - boolean value for dlg_plur
                    (Default: None)
                keep_on_desk - determines if ACS should be shown if monika
                    leaves
                    (Default: False)
                hl_data - highlight data. Format:
                    key: values used for pose_map
                    value: tuple:
                        [0] - default highlight ot use. pass in None to not
                            set a default (MASFilterMap object)
                        [1] - highlight mapping to use. format:
                            key: see arm_split property
                            value: MASFilterMap objects
                                None means no highlight for this layer
                        None means no highlight for this pose
                    if None, then no highlights at all
                    (Default: None)
            """
            super(MASSplitAccessory, self).__init__(
                self.ASO_SPLIT,
                name,
                img_sit,
                pose_map,
                img_stand,
                rec_layer,
                priority,
                stay_on_start,
                entry_pp,
                exit_pp,
                acs_type,
                mux_type,
                ex_props,
                dlg_data,
                keep_on_desk,
                MASSplitAccessory._prepare_hl_data(hl_data)
            )

            self.arm_split = arm_split

        def __repr__(self):
            return "<SACS: {0}>".format(self.name)

        def __build_loadstrs_hl(self, prefix, poseid, armcode):
            """
            Builds highlight load strs for a pose and arm layer

            IN:
                prefix - prefix to apply to the load strings
                    should be a list of strings
                poseid - pose id to find highlight for
                armcode - arm_split code to find highlight for

            RETURNS: list of lists of strings
            """
            if self.hl_map is None:
                return []

            # get hl map for a pose
            mhm = self.hl_map.get(poseid)
            if mhm is None:
                return []

            # get filter map for an arm code
            mfm = mhm.get(armcode)
            if mfm is None:
                return []

            # get all unique filter values
            return [
                prefix + [
                    store.mas_sprites.HLITE_SUFFIX,
                    hlc,
                    store.mas_sprites.FILE_EXT
                ]
                for hlc in mfm.unique_values()
            ]

        @classmethod
        def _prepare_hl_data(cls, hl_data):
            """
            Generates hl-ready data from ahl data for MASAccessoryBase
                processing

            IN:
                hl_data - ahl data. See constructor for info

            RETURNS: hl_data to pass into MASAccessoryBase
            """
            if hl_data is None:
                return None

            # for each data element, we need to generate an MHM
            for key in hl_data:
                data = hl_data[key]
                if data is not None:
                    hl_data[key] = MASHighlightMap.create_from_mapping(
                        cls.__MHM_KEYS,
                        data[0],
                        data[1]
                    )

            return (None, hl_data)

        def build_loadstrs(self, prefix):
            """
            See MASSpriteBase.build_loadstrs
            """
            loadstrs = []

            # loop over MASPoseMap for pose ids
            for poseid in self.pose_map.unique_values():

                # generate new img str
                new_img = prefix + [
                    store.mas_sprites.PREFIX_ACS,
                    self.img_sit,
                    store.mas_sprites.ART_DLM,
                    poseid,
                ]

                # check layers
                for armcode in self.get_arm_split_code(poseid):

                    # generate arm code img str
                    ac_img = new_img + [store.mas_sprites.ART_DLM, arm_code]

                    # add that to list
                    loadstrs.append(ac_img + [store.mas_sprites.FILE_EXT])

                    # highlights
                    loadstrs.extend(self.__build_loadstrs_hl(
                        ac_img,
                        poseid,
                        armcode
                    ))

            return loadstrs

        @classmethod
        def fromJSON_hl_data(cls,
                json_obj,
                msg_log,
                ind_lvl,
                pm_keys,
                rec_layer
        ):
            """
            Parses JSOn data for a highlight split object

            IN:
                json_obj - JSON object to parse
                ind_lvl - indentation level
                    NOTE: this function handles loading/success so do NOT
                        incrememnt indent
                pm_keys - pose map keys
                rec_layer - the layer that this ACS wants to be on

            OUT:
                msg_log - list to add messages to

            RETURNS: split hl_data, completely validated:
                dict:
                key: pose map keys
                value: tuple:
                    [0] - default MASFilterMap object
                    [1] - dict:
                        key: arm split keys
                        value: MASFilterMap object
                or None if no data, False if failure in parsing occured
            """
            # check rec layer for valid split
            if rec_layer == MASMonika.BSE_ACS:
                as_keys = cls.__BSE_KEYS
            elif rec_layer == MASMonika.ASE_ACS:
                as_keys = cls.__ASE_KEYS
            else:
                # silently fail in this case. This should never actually
                # happen
                return None

            # log loading
            msg_log.append((
                store.mas_sprites_json.MSG_INFO_T,
                ind_lvl,
                store.mas_sprites_json.MHM_S_LOADING
            ))

            # check type
            if not store.mas_sprites_json._verify_dict(json_obj, False):
                msg_log.append((
                    store.mas_sprites_json.MSG_ERR_T,
                    ind_lvl + 1,
                    store.mas_sprites_json.MHM_S_NOT_DICT.format(
                        dict,
                        type(json_obj)
                    )
                ))
                return False

            shl_data = {}

            # parse data as dict
            # the initial level keys should be pose map ones
            has_map_data = False
            isbad = False
            for pm_key in pm_keys:
                if pm_key in json_obj:
                    hl_obj = json_obj.pop(pm_key)

                    # log loading
                    msg_log.append((
                        store.mas_sprites_json.MSG_INFO_T,
                        ind_lvl + 1,
                        store.mas_sprites_json.MHM_SK_LOADING.format(pm_key)
                    ))

                    # parse data
                    vhl_data = {}
                    if store.mas_sprites_json._validate_highlight_core(
                            hl_obj,
                            vhl_data,
                            msg_log,
                            ind_lvl + 2,
                            as_keys
                    ):
                        # success

                        # log success
                        msg_log.append((
                            store.mas_sprites_json.MSG_INFO_T,
                            ind_lvl + 1,
                            store.mas_sprites_json.MHM_SK_SUCCESS.format(
                                pm_key
                            )
                        ))

                        hl_data = vhl_data.get("hl_data", None)

                        if hl_data is not None:
                            # none check the hl object for later
                            has_map_data = True

                        shl_data[pm_key] = hl_data

                    else:
                        # failure case
                        isbad = True

            # warn if any extras
            for extra_prop in json_obj:
                msg_log.append((
                    store.mas_sprites_json.MSG_WARN_T,
                    ind_lvl,
                    store.mas_sprites_json.EXTRA_PROP.format(extra_prop)
                ))

            # quit if failure
            if isbad:
                return False

            # check if we actually have any data
            if len(shl_data) == 0 or not has_map_data:
                # no data, warn but no failure
                msg_log.append((
                    store.mas_sprites_json.MSG_WARN_T,
                    ind_lvl,
                    store.mas_sprites_json.MHM_S_NO_DATA
                ))
                shl_data = None

            # log success
            msg_log.append((
                store.mas_sprites_json.MSG_INFO_T,
                ind_lvl,
                store.mas_sprites_json.MHM_S_SUCCESS
            ))

            return shl_data

        def get_arm_split_code(self, poseid):
            """
            Gets arm split code if needed

            IN:
                poseid - poseid to get arm split code for

            RETURNS: arms split code as iterable, or empty list
            """
            if self.arm_split is None:
                return []

            # find arm code
            arm_code = self.arm_split.get(poseid, None)
            if not arm_code:
                return []

            # valid arm code (or not empty string)
            if arm_code == "*":
                return self.__MHM_KEYS

            # otherwise split on delimter
            return arm_code.split("^")

        def gethlc(self, leanpose, flt, hl_key, defval=None):
            """
            Gets highlight code.
            NOTE: if you already know the pose id, use opt_gethlc

            IN:
                leanpose - leanpose to get highlight for
                flt - filter to get highlight for
                hl_key - arm_spilt code
                defval - default value to use
                    (Default: None)

            RETURNS: highlight code, or none if no highlight
            """
            return self.opt_gethlc(
                self.pose_map.get(leanpose, None),
                flt,
                hl_key,
                defval
            )

        def hl_keys(self):
            """
            Returns keys used for MASHighlightMap.

            RETURNS: keys used for all MASHighlightMaps for MASAccessories.
            """
            return self.__MHM_KEYS

        @classmethod
        def hl_keys_c(cls):
            """
            Class method version of hl_keys

            RETURNS: tuple of hl keys
            """
            return cls.__MHM_KEYS

        def opt_gethlc(self, poseid, flt, arm_split, defval=None):
            """
            MASSplitAccessory-specific gethlc.
            Optimized to only accept the args that actually matter for
            MASSplitAccessory objects

            IN:
                poseid - string from pose_map
                flt - filter to get highlight for
                arm_split - arm split code to get highlight for
                defval - default value to return
                    (Default: None)

            RETURNS: highlight code, or None if no highlight
            """
            if self.hl_map is None or arm_split is None:
                return defval

            return MASHighlightMap.o_fltget(
                self.hl_map.get(poseid),
                arm_split,
                flt,
                defval
            )

        @classmethod
        def verify_arm_split_val(cls, value):
            """
            Verifies if an arm split value is valid

            IN:
                value - arm split value to check

            RETURNS: True if valid, false if not
            """
            return value in cls.__MHM_KEYS


    class MASHair(MASSpriteFallbackBase):
        """
        MASHair objects

        Representations of hair items

        PROPERTIES:
            split - MASPoseMap object that determins if a pose has split hair
                or not.
                if a pose has True, it is split. False or None means no split.
            hl_map - MASHighlightMap with the following format:
                keys:
                    "front" - front hair
                    "back" - back hair
                    "mid" - mid hair
                    "<lean>|front" - front hair for a leaning type
                        NOTE: can be multiple of this format
                    "<lean>|back" - back hair for a leaning type
                        NOTE: can be multiple of this format
                    "<lean>|mid" - mid hair for a leaning type
                        NOTE: can be multiple of this format
                values:
                    MASFilterMap objects
            mpm_mid - MASPoseMap for mid hair layer.
                Determines if the mid layer should be used for a pose.
                This is the enable/disable type

        SEE MASSpriteFallbackBase for inherited properties

        POSEMAP explanations:
            Use an empty string to
        """

        __MHM_KEYS = store.mas_sprites._genLK(("front", "back", "mid"))

        def __init__(self,
                name,
                img_sit,
                pose_map,
                img_stand="",
                stay_on_start=True,
                fallback=False,
                entry_pp=None,
                exit_pp=None,
                split=None,
                ex_props=None,
                hl_data=None,
                mpm_mid=None 
            ):
            """
            MASHair constructor

            IN;
                name - name of this hairstyle
                img_sit - filename of the sitting image for this hairstyle
                pose_map - MASPoseMap object that contains pose mappings
                img_stand - filename of the standing image for this hairstyle
                    If this is not passed in, this is considered blacklisted
                        from standing sprites.
                    (Default: "")
                stay_on_strat - True means the hairstyle should reappear on
                    startup. False means a restart clears the hairstyle
                    (Default: True)
                fallback - Unused
                entry_pp - programming point to call when wearing this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                exit_pp - programming point to call when taking off this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                split - MASPoseMap object saying which hair has splits or Not.
                    If None, we assume hair has splits for everything.
                    (Default: None)
                ex_props - dict of additional properties to apply to this
                    sprite object.
                    (Default: None)
                hl_data - tuple of the following format:
                    [0] - default MASFilterMap to use.
                        NOTE: it almost certain that you do NOT want to set
                            this
                        If None, no default highlight
                    [1] - mapping dict. Format:
                        key: see hl_map property
                        value: MASFilterMap object, or None if no highlight
                    if None, then no highlights at all.
                    (Default: None)
                mpm_mid - MASPoseMap for mid hair usage.
                    Determines if a mid layer should be used for a pose.
                    Should be enable/disable type or else we crash
                    (Default: None)
            """
            super(MASHair, self).__init__(
                name,
                img_sit,
                pose_map,
                img_stand,
                stay_on_start,
                fallback,
                entry_pp,
                exit_pp,
                ex_props,
                MASHair._prepare_hl_data(hl_data)
            )
            self.__sp_type = store.mas_sprites_json.SP_HAIR

            if split is not None and type(split) != MASPoseMap:
                raise Exception("split MUST be PoseMap")

            if (
                    mpm_mid is not None
                    and not isinstance(mpm_mid, MASPoseMap)
                    and mpm_mid._mpm_type != MASPoseMap.MPM_TYPE_ED
            ):
                raise Exception("mpm_mid must be MASPoseMap of type ED / 0")

            self.split = split
            self.mpm_mid = mpm_mid

        def __repr__(self):
            return "<Hair: {0}>".format(self.name)

        def __build_loadstrs_hl(self, prefix, hl_key):
            """
            Builds highlight load strs for a split layer

            IN:
                prefix - prefix to apply to the load strings
                    should be a list of strings
                hl_key - key of the hl to use

            RETURNS: list of lists of strings
            """
            if self.hl_map is None:
                return []

            # get filter map
            mfm = self.hl_map.get(hl_key)
            if mfm is None:
                return []

            return [
                prefix + [
                    store.mas_sprites.HLITE_SUFFIX,
                    hlc,
                    store.mas_sprites.FILE_EXT
                ]
                for hlc in mfm.unique_values()
            ]

        @classmethod
        def _prepare_hl_data(cls, hl_data):
            """
            Generates hl-ready data for MASSpriteBase

            IN:
                hl_data - hl data. See Constructor for info

            RETURNS: hl_data to pass into MASSpriteBase
            """
            if hl_data is None:
                return None

            hl_def, hl_mapping = hl_data
            if hl_def is None and hl_mapping is None:
                return None

            return (cls.__MHM_KEYS, hl_def, hl_mapping)

        def build_loadstrs(self, prefix):
            """
            See MASSpriteBase.build_loadstrs
            """
            loadstrs = []

            # NOTE: we only allow split layers, but this check is to ensure
            #   we don't have any weirdness going on
            all_split = self.split is None

            # loop over all poses
            for leanpose in store.mas_sprites.ALL_POSES:

                # determine actual pose
                actual_pose = self.get_leanpose(leanpose)

                # check for valid pose
                # and only allow splits
                if (
                        actual_pose
                        and (all_split or self.split.get(actual_pose, False))
                ):
                    # determine lean
                    islean = "|" in leanpose

                    # generate img string
                    new_img = list(prefix)

                    # determine starting prefix
                    if islean:
                        lean = leanpose.partition("|")[0]
                        hl_key = lean + "|{0}"
                        new_img.extend((
                            store.mas_sprites.PREFIX_HAIR_LEAN,
                            lean,
                            store.mas_sprites.ART_DLM
                        ))
                    else:
                        hl_key = "{0}"
                        new_img.append(store.mas_sprites.PREFIX_HAIR)

                    # add the tag
                    new_img.append(self.img_sit)

                    # genreate back and front images
                    back_img = new_img + [store.mas_sprites.BHAIR_SUFFIX]
                    front_img = new_img + [store.mas_sprites.FHAIR_SUFFIX]

                    # mid images as well
                    if (
                            self.mpm_mid is not None
                            and self.mpm_mid.get(leanpose, False)
                    ):
                        mid_img = new_img + [store.mas_sprites.MHAIR_SUFFIX]

                    else:
                        mid_img = None

                    # add them to list
                    loadstrs.append(back_img + [store.mas_sprites.FILE_EXT])
                    loadstrs.append(front_img + [store.mas_sprites.FILE_EXT])
                    if mid_img is not None:
                        loadstrs.append(mid_img + [store.mas_sprites.FILE_EXT])

                    # highlights
                    loadstrs.extend(self.__build_loadstrs_hl(
                        back_img,
                        hl_key.format(store.mas_sprites.BHAIR)
                    ))
                    loadstrs.extend(self.__build_loadstrs_hl(
                        front_img,
                        hl_key.format(store.mas_sprites.FHAIR)
                    ))
                    if mid_img is not None:
                        loadstrs.extend(self.__build_loadstrs_hl(
                            mid_img,
                            hl_key.format(store.mas_sprites.MHAIR)
                        ))

            return loadstrs

        def format_exprops(self):
            """
            Override of base class function
            """
            super(MASHair, self).format_exprops()

            # format required-clothes-prop into list if it isn't.
            # NOTE: no handling for non-string types
            req_cloth_prop = self.getprop(store.mas_sprites.EXP_H_RQCP)
            if store.mas_sprites_json._verify_str(req_cloth_prop, False):
                self.ex_props[store.mas_sprites.EXP_H_RQCP] = [req_cloth_prop]

        def gethlc(self, hair_key, lean, flt, defval=None):
            """
            Gets highlight code

            IN:
                hair_key - the hair key to get hlc for (front/back)
                lean - type of lean to get hlc for
                flt - filter to get highlight for
                defval - the default value to return
                    (Default: None)

            RETURNS: highlight code, or defval if no highlight
            """
            if self.hl_map is None:
                return defval

            if lean:
                hl_key = "|".join((lean, hair_key))
            else:
                hl_key = hair_key

            return MASHighlightMap.o_fltget(
                self.hl_map,
                hl_key,
                flt,
                defval
            )

        def hl_keys(self):
            """
            Returns keys used for MASHighlightMap.

            RETURNS: keys used for all MASHighlightMaps for MASHair objects
            """
            return self.__MHM_KEYS

        @classmethod
        def hl_keys_c(cls):
            """
            Class method of hl_keys

            RETURNS: tuple of hl keys
            """
            return cls.__MHM_KEYS


    class MASClothes(MASSpriteFallbackBase):
        """
        MASClothes objects

        Representations of clothes

        PROPERTIES:
            hair_map - dict of available hair styles for these clothes
                keys should be hair name properites. Values should also be
                hair name properties.
                use "all" to signify a default hair style for all mappings that
                are not found.
            pose_arms - MASPoseArms object containing the arms for these
                clothes.
            hl_map - MASHighlightMap with the following format:
                keys:
                    "0" - body-0 layer
                    "1" - body-1 layer
                    "<lean>|0" - body-0 layer for a leaning type
                        NOTE: can be multiple of this format
                    "<lean>|1" - body-1 layer for a leaning type
                        NOTE: can be multiple of this format
                values:
                    MASFilterMap objects

        SEE MASSpriteFallbackBase for inherited properties
        """
        import store.mas_sprites as mas_sprites

        __MHM_KEYS = store.mas_sprites._genLK(("0", "1"))

        def __init__(self,
                name,
                img_sit,
                pose_map,
                img_stand="",
                stay_on_start=False,
                fallback=False,
                hair_map={},
                entry_pp=None,
                exit_pp=None,
                ex_props=None,
                pose_arms=None,
                hl_data=None
            ):
            """
            MASClothes constructor

            IN;
                name - name of these clothes
                img_sit - filename of the sitting image for these clothes
                pose_map - MASPoseMap object that contains pose mappings
                img_stand - filename of the standing image for these clothes
                    If this is not passed in, this is considered blacklisted
                        from standing sprites.
                    (Default: "")
                stay_on_start - True means the clothes should reappear on
                    startup. False means a restart clears the clothes
                    (Default: False)
                fallback - Unused
                hair_map - dict of available hair styles and what they map to
                    These should all be strings. To signify a default, add
                    a single item called "all" with the value being the hair
                    to map to.
                    NOTE: use the name property for hairstyles.
                    (Default: {})
                entry_pp - programming point to call when wearing this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                exit_pp - programming point to call when taking off this sprite
                    the MASMonika object that is being changed is fed into this
                    function
                    (Default: None)
                ex_props - dict of additional properties to apply to this
                    sprite object.
                    (Default: None)
                pose_arms - MASPoseMap object represneting the arm layers
                    for poses. If None is passed, we assume use the base
                    layers as a guide
                    (Default: None)
                hl_data - tuple of the following format:
                    [0] - default MASFilterMap to use.
                        NOTE: it almost certain that you do NOT want to set
                            this
                        If None, no default highlight
                    [1] - mapping dict. Format:
                        key: see hl_map proprety
                        value: MASFilterMap object, or None if no highlight
                    if None, then no highlights at all.
                    (Default: None)
            """
            super(MASClothes, self).__init__(
                name,
                img_sit,
                pose_map,
                img_stand,
                stay_on_start,
                fallback,
                entry_pp,
                exit_pp,
                ex_props,
                MASClothes._prepare_hl_data(hl_data)
            )
            self.__sp_type = store.mas_sprites_json.SP_CLOTHES

            self.hair_map = hair_map
            self.pose_arms = pose_arms

            # add defaults if we need them
            if "all" in hair_map:
                for hair_name in mas_sprites.HAIR_MAP:
                    if hair_name not in self.hair_map:
                        self.hair_map[hair_name] = self.hair_map["all"]

        def __repr__(self):
            return "<Clothes: {0}>".format(self.name)

        def __build_loadstrs_hl(self, prefix, hl_key):
            """
            Builds loadstrs for body highlights

            IN:
                prefix - prefix to apply
                    should be a list of strings
                hl_key - key of the hl to use

            RETURNS: list of lists of strings representing image paths
            """
            if self.hl_map is None:
                return []

            # get filter map
            mfm = self.hl_map.get(hl_key)
            if mfm is None:
                return []

            return [
                prefix + [
                    store.mas_sprites.HLITE_SUFFIX,
                    hlc,
                    store.mas_sprites.FILE_EXT
                ]
                for hlc in mfm.unique_values()
            ]

        @classmethod
        def _prepare_hl_data(cls, hl_data):
            """
            Generates hl-ready data for MASSpriteBase

            IN:
                hl_data - hl data. See constructor for info

            RETURNS: hl_data to pass into MASSpriteBase
            """
            if hl_data is None:
                return None

            hl_def, hl_mapping = hl_data
            if hl_def is None and hl_mapping is None:
                return None

            return (cls.__MHM_KEYS, hl_def, hl_mapping)

        def build_loadstrs(self, prefix):
            """
            See MASSpriteBase.build_loadstrs
            """
            loadstrs = []

            # prefix + folder name
            c_prefix = prefix + [
                self.img_sit,
                "/"
            ]

            # start with body
            # upright first
            # NOTE: if we have different body types, we will need to change
            #   this
            loadstrs.append(c_prefix + [
                store.mas_sprites.NEW_BODY_STR,
                store.mas_sprites.ART_DLM,
                "0",
                store.mas_sprites.FILE_EXT
            ])
            loadstrs.append(c_prefix + [
                store.mas_sprites.NEW_BODY_STR,
                store.mas_sprites.ART_DLM,
                "1",
                store.mas_sprites.FILE_EXT
            ])

            # leaning types
            for lpose in store.mas_sprites.L_POSES:

                # determine actual pose
                actual_pose = self.get_leanpose(lpose)

                # only accept valid poses and leanables
                if actual_pose and "|" in actual_pose:
                    # get lean type from pose
                    lean, pose = actual_pose.split("|")

                    # build prefix and add file
                    l_prefix = c_prefix + [
                        store.mas_sprites.PREFIX_BODY_LEAN,
                        lean,
                        store.mas_sprites.ART_DLM
                    ]
                    l0_prefix = l_prefix + ["0"]
                    l1_prefix = l_prefix + ["1"]
                    loadstrs.append(l0_prefix + [store.mas_sprites.FILE_EXT])
                    loadstrs.append(l1_prefix + [store.mas_sprites.FILE_EXT])

                    # check hl map for leans
                    loadstrs.extend(self.__build_loadstrs_hl(
                        l0_prefix,
                        lean + "|0"
                    ))
                    loadstrs.extend(self.__build_loadstrs_hl(
                        l1_prefix,
                        lean + "|1"
                    ))

            # now do arms
            if self.pose_arms is None:
                # use base arms
                pose_arms = store.mas_sprites.base_arms
            else:
                pose_arms = self.pose_arms

            loadstrs.extend(pose_arms.build_loadstrs(c_prefix))

            return loadstrs

        def default_exprops(self):
            """
            Override of base class function
            """
            super(MASClothes, self).default_exprops()

            # default bare shoulder exprops
            if self.hasprop(store.mas_sprites.EXP_C_BS):
                self.addprop(store.mas_sprites.EXP_C_BLS)
                self.addprop(store.mas_sprites.EXP_C_BRS)
            elif (
                    self.hasprop(store.mas_sprites.EXP_C_BLS)
                    and self.hasprop(store.mas_sprites.EXP_C_BRS)
            ):
                self.addprop(store.mas_sprites.EXP_C_BS)

            # default DTS compat if BRS is set
            if self.hasprop(store.mas_sprites.EXP_C_BRS):
                self.addprop(store.mas_sprites.EXP_C_C_DTS)

        def determine_arms(self, leanpose):
            """
            Determines arms pose to use for a given leanpose

            IN:
                leanpose - leanpose to determine arms pose for

            RETURNS: MASPoseArms object to use for this leanpose, or None if
                no MASPoseArms to use
            """
            # check our arms
            # NOTE: if no arms, we always use base
            if self.pose_arms is None:
                return store.mas_sprites.base_pose_arms_map.get(
                    leanpose,
                    None
                )

            # otherwise use our arms but return None if not need to render
            return self.pose_arms.get(leanpose, None)

        def get_hair(self, hair):
            """
            Given a hair type, grabs the available mapping for this hair type

            IN:
                hair - hair type to get mapping for

            RETURNS:
                the hair mapping to use inplace for the given hair type
            """
            return self.hair_map.get(hair, self.hair_map.get("all", hair))

        def gethlc(self, bcode, lean, flt, defval=None):
            """
            Gets highlight code

            IN:
                bcode - base code to get hlc for (0,1)
                lean - type of lean
                flt - filter to get highlight for
                defval - the default value to return
                    (Default: None)

            RETURNS: highlight code, or defval is no highlight
            """
            if self.hl_map is None:
                return defval

            if lean:
                hl_key = "|".join((lean, bcode))
            else:
                hl_key = bcode

            return MASHighlightMap.o_fltget(
                self.hl_map,
                hl_key,
                flt,
                defval
            )

        def has_hair_map(self):
            """
            RETURNS: True if we have a mapping to check, False otherwise
            """
            return len(self.hair_map) > 0

        def hl_keys(self):
            """
            Returns keys used for MASHighlightMap.

            RETURNS: keys used for all MASHighlightMaps for MASHair objects
            """
            return self.__MHM_KEYS

        @classmethod
        def hl_keys_c(cls):
            """
            Class method version of hl_keys

            RETURNS: tuple of hl keys
            """
            return cls.__MHM_KEYS

        @staticmethod
        def by_exprop(exprop, value=True):
            """
            Gets all clothes that have the given exprop.

            IN:
                exprop - exprop to look for
                value - value the exprop should be. Set to None to ignore.

            RETURNS: list of MASClothes objects with the given exprop and value
            """
            clothes = []

            for c_name in store.mas_sprites.CLOTH_MAP:
                clothing = store.mas_sprites.CLOTH_MAP[c_name]
                if (
                        clothing.hasprop(exprop)
                        and (
                            value is None
                            or value == clothing.getprop(exprop)
                        )
                ):
                    clothes.append(clothing)

            return clothes


    # The main drawing function...
    def mas_drawmonika(
            st,
            at,
            character,

            # requried sitting parts
            eyebrows,
            eyes,
            nose,
            mouth,

            # optional sitting parts
            lean=None,
            arms="steepling",
            eyebags=None,
            sweat=None,
            blush=None,
            tears=None,
            emote=None,

            # optional standing parts
            head="",
            left="",
            right="",
            stock=True,
            single=None
        ):
        """DEPRECATED
        This function has been gutted and only draws standing

        IN:
            st - renpy related
            at - renpy related
            character - MASMonika character object
            eyebrows - type of eyebrows (sitting)
            eyes - type of eyes (sitting)
            nose - type of nose (sitting)
            mouth - type of mouth (sitting)
            head - type of head (standing)
            left - type of left side (standing)
            right - type of right side (standing)
            lean - type of lean (sitting)
                (Default: None)
            arms - type of arms (sitting)
                (Default: "steepling")
            eyebags - type of eyebags (sitting)
                (Default: None)
            sweat - type of sweatdrop (sitting)
                (Default: None)
            blush - type of blush (sitting)
                (Default: None)
            tears - type of tears (sitting)
                (Default: None)
            emote - type of emote (sitting)
                (Default: None)
            stock - True means we are using stock standing, False means not
                (standing)
                (Default: True)
            single - type of single standing image (standing)
                (Default: None)
        """
        # NOTE: we only support stand sprites strings

        # TODO: this is missing img_stand checks
        # TODO change this to an elif and else the custom stnading mode
#        elif stock:
            # stock standing mode
        cmd = store.mas_sprites._ms_standingstock(
            head,
            left,
            right,
            [], # TODO maybe need a ring in standing mode?
            single=single
        )


        return eval(cmd),None # Unless you're using animations, you can set refresh rate to None

python early:
# # # START: Idle disp stuff
    import random

    class IdleExpException(Exception):
        """
        Custor exception for MASMoniIdleExp
        """
        def __init__(self, msg):
            self.msg = msg

        def __str__(self):
            return "IdleExpException: " + self.msg

    class MASMoniIdleExp(object):
        """
        A class to represent a single idle exp

        PROPERTIES:
            code - (str) exp code for this exp
            ref - (ImageReference) image reference to the sprite
            duration - (int/tuple) duration of this exp in seconds
            aff_range - (None/tuple) affection range for this exp
            conditional - (None/str) python condition for this exp
            weight - (None/int) weight of this exp that's used in random selection
            tag - (None/str) tag for this exp
            repeatable - (boolean) boolean indicating whether or not this exp can be reused
            add_to_tag_map - (boolean) private flag whether or not this exp will be added to the tag map
                NOTE: usually you want to add exp to the map, unless they are temp. Exps in the map WILL NOT be removed by gc
        """
        MIN_WEIGHT = 1
        MAX_WEIGHT = 100

        exp_tags_map = dict()
        _conditional_cache = dict()

        def __init__(self, code, duration=(20, 30), aff_range=None, conditional=None, weight=50, tag=None, repeatable=True, add_to_tag_map=True):
            """
            Constructor for idle expressions

            IN:
                code - exp code
                duration - duration for this exp in seconds. This can be int or a tuple of 2 ints. If it's a tuple, the duration is being choosen at random between 2 values
                    (Default: tuple (20, 30))
                aff_range - affection range for this exp. If not None, assuming it's a tuple of 2 aff constants.
                    Values can be None to not limit lower or upper bounds
                    (Default: None)
                conditional - string with condition, assuming it's python code. If when evaled it returns False, this exp won't be used
                    (Default: None)
                weight - weight to use when choosing from a pool of exps. Must be between 1 and 100.
                    NOTE: if this is None, this exp will be FORCED among with other exps that has None as weight. This is to guarantee that we'll get an exp
                    (Default: 50)
                tag - tag for this exp. Used to group exps. There's no group for exps with no tag
                    (Default: None)
                repeatable - whether or not this exp can be used multiple times
                    (Default: True)
                add_to_tag_map - whether or not this exp will be added to the tag map using its tag
                    (Default: True)
            """
            self.code = code
            self.ref = renpy.display.image.ImageReference(("monika", code,))

            if isinstance(duration, list):
                duration = tuple(duration)
            if isinstance(duration, tuple):
                _len = len(duration)
                if _len != 2:
                    raise IdleExpException(
                        "Expected a tuple/list of 2 items for the duration property. Got the tuple/list of {0} item{1} instead.".format(
                            _len,
                            "s" if _len != 1 else ""
                        )
                    )

                elif duration[0] < 1 or duration[1] < 1:
                    raise IdleExpException(
                        "Duration for idle expression must be at least one second long. Got: {0} and {1}.".format(
                            duration[0],
                            duration[1]
                        )
                    )

            elif duration < 1:
                raise IdleExpException(
                    "Duration for idle expression must be at least one second long. Got: {0}.".format(
                        duration[0]
                    )
                )
            self.duration = duration

            # The rest is handles in another method
            self._finish_init(aff_range, conditional, weight, tag, repeatable, add_to_tag_map)

        def _finish_init(self, aff_range, conditional, weight, tag, repeatable, add_to_tag_map):
            """
            This method only exists so we don't need to copy/paste code.
            Finishes init process. For args explanation look up __init__
            """
            if not mas_affection._isValidAffRange(aff_range):
                raise IdleExpException(
                    "Got invalid aff range: {0}.".format(
                        aff_range
                    )
                )
            self.aff_range = aff_range

            if (
                conditional is not None
                and conditional not in MASMoniIdleExp._conditional_cache
            ):
                MASMoniIdleExp._conditional_cache[conditional] = renpy.python.py_compile(conditional, "eval")
            self.conditional = conditional

            if weight is not None and not MASMoniIdleExp.MIN_WEIGHT <= weight <= MASMoniIdleExp.MAX_WEIGHT:
                raise IdleExpException(
                    "Weight must be between 0 and 100. Got {0}.".format(
                        weight
                    )
                )
            self.weight = weight

            if tag is not None and add_to_tag_map:
                if tag in MASMoniIdleExp.exp_tags_map:
                    MASMoniIdleExp.exp_tags_map[tag].append(self)

                else:
                    MASMoniIdleExp.exp_tags_map[tag] = [self]
            self.tag = tag
            self._add_to_tag_map = add_to_tag_map

            self.repeatable = repeatable

        def __repr__(self):
            """
            Representation of this object
            """
            if self.tag is None:
                tag = "None"
            else:
                tag = "'{0}'".format(self.tag)

            if isinstance(self.duration, tuple):
                duration = "{0}-{1} sec".format(self.duration[0], self.duration[1])
            else:
                duration = "{0} sec".format(self.duration)

            return "<MASMoniIdleExp: (code: '{0}', duration: {1}, tag: {2})>".format(
                self.code,
                duration,
                tag
            )

        def select_duration(self):
            """
            A method to select duration for this exp

            OUT:
                int in range of the duration property of this exp, or the prop itself if it's not a range
            """
            if isinstance(self.duration, tuple):
                return random.randint(self.duration[0], self.duration[1])
            return self.duration

        def check_aff(self, aff=None):
            """
            Checks if we're within aff range of this exp

            IN:
                aff - affection to check, if None, uses current affection lvl
                    (Default: None)

            OUT:
                boolean: True if we're within the range, False otherwise

            ASSUMES:
                mas_curr_affection
                mas_affection._betweenAff
            """
            if self.aff_range is None:
                return True

            if aff is None:
                aff = mas_curr_affection
            return mas_affection._betweenAff(self.aff_range[0], aff, self.aff_range[1])

        def check_conditional(self):
            """
            Checks conditional for this exp

            OUT:
                True if we passed, False otherwise
            """
            if self.conditional is None:
                return True

            code_obj = MASMoniIdleExp._conditional_cache[self.conditional]
            return bool(renpy.python.py_eval_bytecode(code_obj))

        @staticmethod
        def weighted_choice(exps):
            """
            Does weighted choice

            IN:
                exps - list/tuple of MASMoniIdleExp

            OUT:
                MASMoniIdleExp or None if was given incorrect input

            ASSUMES:
                mas_utils.weightedChoice
            """
            rng_choice = list()
            weighted_choice = list()

            for exp in exps:
                if exp.weight is None:
                    rng_choice.append(exp)

                else:
                    weighted_choice.append((exp, exp.weight))

            if rng_choice:
                exp = random.choice(rng_choice)

            else:
                exp = mas_utils.weightedChoice(weighted_choice)

            return exp

    class MASMoniIdleExpGroup(MASMoniIdleExp):
        """
        A class to represent a group of MASMoniIdleExp's

        PROPERTIES:
            exps - (list) exps (MASMoniIdleExp) in this group
            current_index - (int) id of the currently selected exp
            These are the same as for MASMoniIdleExp:
                aff_range
                conditional
                weight
                tag
                repeatable
                add_to_tag_map
        """
        def __init__(self, exps, aff_range=None, conditional=None, weight=50, tag=None, repeatable=True, add_to_tag_map=True):
            """
            Constructor for groups of idle exps
            NOTE: Check MASMoniIdleExp for explanation of params/methods

            IN:
                exps - list of or a single MASMoniIdleExp
                    NOTE: technically you CAN do inner groups by passing in MASMoniIdleExpGroup
                aff_range - affection range for this group. If this doesn't pass, no exps of this group will be shown
                    (Default: None)
                conditional - string with condition. If this doesn't pass, no exps of this group will be shown
                    (Default: None)
                weight - weight to use when choosing from a pool of exps/groups. Must be between 1 and 100.
                    NOTE: if this is None, this group will be FORCED among with other exps/groups that has None as weight.
                        This is to guarantee that we'll get this if we want so
                    (Default: 50)
                tag - tag for this group. Used to group groups
                    (Default: None)
                repeatable - whether or not this group can be used multiple times
                    (Default: True)
                add_to_tag_map - whether or not this exp will be added to the tag map using its tag
                    (Default: True)
            """
            if isinstance(exps, tuple):
                exps = list(exps)
            elif not isinstance(exps, list):
                exps = [exps]
            self.exps = exps
            self.current_index = -1

            self._finish_init(aff_range, conditional, weight, tag, repeatable, add_to_tag_map)
            self._validate_children_aff_range()

        def _validate_children_aff_range(self):
            """
            Validates aff range of the exps

            ASSUMES:
                we finished init this group
            """
            if self.aff_range is not None:
                for exp in self.exps:
                    if exp.aff_range is None:
                        exp.aff_range = self.aff_range
                        if isinstance(exp, MASMoniIdleExpGroup):
                            exp._validate_children_aff_range()

        def __repr__(self):
            """
            Representation of this object
            """
            if self.tag is None:
                tag = "None"
            else:
                tag = "'{0}'".format(self.tag)

            return "<MASMoniIdleExpGroup (group: {0}, tag: {1})>".format(
                self.exps,
                tag
            )

        def select_duration(self):
            """
            Meaningless as hawaiian pizza
            """
            return NotImplemented

        def check_aff(self, aff=None, check_children=True):
            """
            Checks if we're within aff range of this group

            IN:
                aff - affection to check, if None, uses current affection lvl
                    (Default: None)
                check_children - boolean wheather or not we should check this group's exps aff ranges as well
                    (Default: True)

            OUT:
                boolean: True if we're within the range, False otherwise

            ASSUMES:
                mas_curr_affection
                mas_affection._betweenAff
            """
            if aff is None:
                aff = mas_curr_affection

            return (
                (
                    self.aff_range is None
                    or mas_affection._betweenAff(self.aff_range[0], aff, self.aff_range[1])
                )
                and (
                    not check_children
                    or any([exp.check_aff(aff) for exp in self.exps])
                )
            )

        def check_conditional(self, check_children=True):
            """
            Checks conditional for this group

            IN:
                check_children - boolean wheather or not we should check this group's exps conditionals as well
                    (Default: True)

            OUT:
                True if we passed, False otherwise
            """
            return (
                (
                    self.conditional is None
                    or bool(
                        renpy.python.py_eval_bytecode(
                            MASMoniIdleExpGroup._conditional_cache[self.conditional]
                        )
                    )
                )
                and (
                    not check_children
                    or any([exp.check_conditional() for exp in self.exps])
                )
            )

        def progress_group(self):
            """
            Progresses the group to the next exp

            OUT:
                tuple:
                    selected exp or None
                        NOTE: Ideally we should never get a None from this
                    boolean whether or not we've finished this group (so we can move to the next one)
                    boolean whether or not this group is empty (so the group can be removed)
            """
            exp = None
            max_index = len(self.exps) - 1
            self.current_index += 1

            # Try to select an exp while we can/'til we find one
            while self.current_index <= max_index and exp is None:
                exp = self.exps[self.current_index]

                # Validate it
                if exp.check_aff() and exp.check_conditional():
                    # Pop if it's a one'n'done one
                    if not exp.repeatable:
                        self.exps.pop(self.current_index)
                        self.current_index -= 1# We need to decrement the id

                # Or try again with the next id
                else:
                    exp = None
                    self.current_index += 1

            # If we reached the max index, then we're done with this group
            is_done = (self.current_index >= max_index) or exp is None
            # If we popped all the exps from this group, then we should ask to remove it
            is_empty = not bool(self.exps)

            # Reset the index since we may reuse this group later
            if is_done and not is_empty:
                self.current_index = -1

            return exp, is_done, is_empty

    class MASMoniIdleExpRngGroup(MASMoniIdleExpGroup):
        """
        Like MASMoniIdleExpGroup, but chooses exps at random

        PROPERTIES:
            exps - (list) exps (MASMoniIdleExp) in this group
            max_uses - (int) max number of random selections for this group before switching to next exp/group
            uses - (int) how many times we used this group to select an exp
            These are the same as for MASMoniIdleExp:
                aff_range
                conditional
                weight
                tag
                repeatable
                add_to_tag_map
        """
        def __init__(self, exps, max_uses=None, aff_range=None, conditional=None, weight=50, tag=None, repeatable=True, add_to_tag_map=True):
            """
            Constructor for groups of random idle exps
            NOTE: Check MASMoniIdleExp and MASMoniIdleExpGroup for explanation of params/methods

            IN:
                exps - list of or a single MASMoniIdleExp
                    NOTE: technically you CAN do inner groups by passing in MASMoniIdleExpGroup / MASMoniIdleExpRngGroup
                max_uses - number of times this group will select an exp before ending its cycle. If None,
                    this'll be set to the number of children
                    (Default: None)
                aff_range - affection range for this group. If this doesn't pass, no exps of this group will be shown
                    (Default: None)
                conditional - string with condition. If this doesn't pass, no exps of this group will be shown
                    (Default: None)
                weight - weight to use when choosing from a pool of exps/groups. Must be between 1 and 100.
                    NOTE: if this is None, this group will be FORCED among with other exps/groups that has None as weight.
                        This is to guarantee that we'll get this if we want so
                    (Default: 50)
                tag - tag for this group. Used to group groups
                    (Default: None)
                repeatable - whether or not this group can be used multiple times
                    (Default: True)
                add_to_tag_map - whether or not this exp will be added to the tag map using its tag
                    (Default: True)
            """
            if isinstance(exps, tuple):
                exps = list(exps)
            elif not isinstance(exps, list):
                exps = [exps]
            self.exps = exps

            if max_uses is None:
                max_uses = len(self.exps)
            self.max_uses = max_uses
            self.uses = 0

            self._finish_init(aff_range, conditional, weight, tag, repeatable, add_to_tag_map)
            self._validate_children_aff_range()

        def __repr__(self):
            """
            Representation of this object
            """
            if self.tag is None:
                tag = "None"
            else:
                tag = "'{0}'".format(self.tag)

            return "<MASMoniIdleExpRngGroup (group: {0}, tag: {1})>".format(
                self.exps,
                tag
            )

        def progress_group(self):
            """
            Progresses the group to the next exp

            OUT:
                tuple:
                    selected exp or None
                        NOTE: Ideally we should never get a None from this
                    boolean whether or not we've finished this group (so we can move to the next one)
                    boolean whether or not this group is empty (so the group can be removed)
            """
            exp = None

            if self.uses < self.max_uses:
                self.uses += 1
                exp_pool = filter(lambda exp: exp.check_aff() and exp.check_conditional(), self.exps)
                exp = MASMoniIdleExpRngGroup.weighted_choice(exp_pool)

                if exp is not None and not exp.repeatable:
                    self.exps.remove(exp)

            is_done = (self.uses >= self.max_uses) or exp is None
            is_empty = not bool(self.exps)

            if is_done and not is_empty:
                self.uses = 0

            return exp, is_done, is_empty

    class MASMoniIdleDisp(renpy.display.core.Displayable):
        """
        Advanced displayable for managing Moni's idle sprites

        PROPERTIES:
            exp_map - (dict) map between exps and aff lvls
            forced_exps - (list) forced exps
            current_exp - (MASMoniIdleExp) currently selected exp
            dissolve - (Dissolve) the Dissolve transform we're currently rendering
            exp_groups - (list) MASMoniIdleExpGroup objects that are being 'itered' through
            fallback - (MASMoniIdleExp) fallback exp. Must ALWAYS be available
            redraw_st - (int/float) required shown timebase to switch to the next exp
            current_st - (float) current shown timebase
            duration - (float) duration (in seconds) for the current exp
                (basically the difference between redraw_st and current_st)
            dissolve_duration - (float) the duration of the current dissolve
            forced_mode - (boolean) indicates that we've forced an expression
            group_mode - (boolean) - indicates that we're handling a group of expressions
        """
        # eyes codes whose transforms we manually reset
        # EYES_EXP_CODES = ("k", "n")
        # Dissolve for exp changes
        QUICK_DISSOLVE = 0.1
        # Dissolve for pose changes
        SLOW_DISSOLVE = 0.25

        BLIT_COORDS = (0, 0)

        # Cache the dissolves so we can reuse them
        _transform_cache = dict()

        def __init__(self, exps=None, fallback=None):
            """
            Constructor for idle displayable

            IN:
                exps - list/tuple of MASMoniIdleExp / MASMoniIdleExpGroup objects
                    (Default: None)
                fallback - MASMoniIdleExp that is used as a fallback
                    when all other exps aren't passing checks. If None, a standart MASMoniIdleExp
                    will be used with the '1esa' exp code.
                    NOTE: This one MUST ALWAYS be valid.
                    (Default: None)

            ASSUMES:
                mas_affection._aff_order
            """
            super(MASMoniIdleDisp, self).__init__()

            if exps is None:
                exps = tuple()

            self.exp_map = dict()
            for aff_lvl in mas_affection._aff_order:
                self.exp_map[aff_lvl] = [exp for exp in exps if exp.check_aff(aff_lvl)]

            self.forced_exps = list()
            self.exp_groups = list()

            self.forced_mode = False
            self.group_mode = False
            self._predicted_modes = {"forced_mode": None, "group_mode": None}

            if fallback is None:
                fallback = MASMoniIdleExp("1esa", duration=10, tag="fallback", add_to_tag_map=False)
            self.fallback = fallback
            self.current_exp = fallback
            self._predicted_exp = None
            self.current_img = None
            self._skip_dissolve = False

            self._last_st = 0.0
            self.redraw_st = 0.0
            self.current_st = 0.0
            self.dissolve_duration = 0.0

        def __repr__(self):
            """
            Representation of this object
            """
            return "<MASMoniIdleDisp: (curr exp: {0}, next exp in: {1} sec)>".format(
                self.current_exp,
                self.duration
            )

        @property
        def duration(self):
            """
            Prop for the current exp duration
            NOTE: we round the value

            OUT:
                float - duration of the current exp in seconds
            """
            return round(self.redraw_st - self.current_st, 1)

        def update(self):
            """
            This causes this disp to update
            """
            self.redraw_st = 0.0
            self.dissolve_duration = 0.0
            renpy.redraw(self, 0.0)

        def add(self, exps, redraw=False):
            """
            Adds expressions to this idle disp

            IN:
                exps - list of MASMoniIdleExp / MASMoniIdleExpGroup objects or a single object
                redraw - whether or not we're forcing a redraw
                    (Default: False)
            """
            # Workaround for single obj
            if not isinstance(exps, (tuple, list)):
                exps = (exps,)

            for exp in exps:
                for aff_lvl, exp_list in self.exp_map.iteritems():
                    if exp.check_aff(aff_lvl):
                        exp_list.append(exp)

            if redraw:
                self.update()

        def add_by_code(self, code, redraw=False, **kwargs):
            """
            Adds an expression to this idle disp generating it from exp code
            NOTE: the exp won't be added to the tag map unless you specify it to

            IN:
                code - exp code
                redraw - whether or not we're forcing a redraw
                    (Default: False)
                kwargs - additional kwargs that will be passed into MASMoniIdleExp
            """
            if "add_to_tag_map" not in kwargs:
                kwargs["add_to_tag_map"] = False

            self.add(
                MASMoniIdleExp(code, **kwargs),
                redraw=redraw
            )

        def add_by_tag(self, tag, redraw=False):
            """
            Adds an expression to this disp using tags
            Uses weighted choice to select an exp If there's more
            than one exp with this tag

            IN:
                tag - tag tou se
                redraw - whether or not we're forcing a redraw
                    (Default: False)
            """
            exps = MASMoniIdleExp.exp_tags_map.get(tag, tuple())
            exp = MASMoniIdleExp.weighted_choice(exps)
            if exp is not None:
                self.add(exp, redraw=redraw)

        def remove(self, exp, redraw=False):
            """
            Removes an expression by instance

            IN:
                exp - MASMoniIdleExp / MASMoniIdleExpGroup object
                redraw - whether or not we're forcing a redraw
                    (Default: False)
            """
            need_redraw = self.current_exp is exp

            for exp_list in self.exp_map.itervalues():
                if exp in exp_list:
                    exp_list.remove(exp)
                    need_redraw = True

            if (
                isinstance(exp, MASMoniIdleExpGroup)
                and exp in self.exp_groups
            ):
                self.exp_groups[:] = list()
                need_redraw = True

            if self._predicted_exp is exp:
                self._predicted_exp = None

            if redraw and need_redraw:
                self.update()

        def remove_by_tag(self, tag, redraw=False):
            """
            Removes expressions by tag

            IN:
                tag - tag to filter by
                redraw - whether or not we're forcing a redraw
                    (Default: False)
            """
            need_redraw = self.current_exp.tag == tag

            for group in self.exp_groups:
                if group.tag == tag:
                    self.exp_groups[:] = list()
                    need_redraw = True
                    break

            for exp_list in self.exp_map.itervalues():
                for exp_id in range(len(exp_list)-1, -1, -1):
                    if exp_list[exp_id].tag == tag:
                        exp_list.pop(exp_id)
                        need_redraw = True

            if self._predicted_exp is not None and self._predicted_exp.tag == tag:
                self._predicted_exp = None

            if redraw and need_redraw:
                self.update()

        def force(self, exps, clear=True, redraw=True, skip_dissolve=False):
            """
            Forces current idle expression to be exps
            NOTE: the weight and repeatable params are ignored

            IN:
                exps - list of MASMoniIdleExp / MASMoniIdleExpGroup objects or a single object
                clear - whether or not we'll clear currently forced/queued exps
                    (Default: True)
                redraw - whether or not we're forcing a redraw
                    (Default: True)
                skip_dissolve - whether or not we skip dissolve transition for the next exp change
                    (Default: False)
            """
            if clear:
                self.forced_exps[:] = list()
                self.exp_groups[:] = list()

            if isinstance(exps, (MASMoniIdleExp, MASMoniIdleExpGroup)):
                self.forced_exps.append(exps)

            else:
                if isinstance(exps, tuple):
                    exps = list(exps)
                self.forced_exps += exps

            if clear:
                self._predicted_exp = None

            if skip_dissolve:
                self._skip_dissolve = True

            if redraw:
                self.update()

        def force_by_code(self, code, clear=True, redraw=True, skip_dissolve=False, **kwargs):
            """
            Forces current idle expression to a new exp using exp code
            NOTE: the exp won't be added to the tag map unless you specify it to

            IN:
                code - exp code
                clear - whether or not we'll clear currently forced/queued exps
                    (Default: True)
                redraw - whether or not we're forcing a redraw
                    (Default: True)
                skip_dissolve - whether or not we skip dissolve transition for the next exp change
                    (Default: False)
                kwargs - additional kwargs that will be passed into MASMoniIdleExp
            """
            if "add_to_tag_map" not in kwargs:
                kwargs["add_to_tag_map"] = False

            self.force(
                MASMoniIdleExp(code, **kwargs),
                clear=clear,
                skip_dissolve=skip_dissolve,
                redraw=redraw
            )

        def force_by_tag(self, tag, clear=True, redraw=True, skip_dissolve=False):
            """
            Forces current idle expression to a new exp using exp tag.
            If there's several exp with the same tag, we use weighted choice.

            IN:
                tag - exp tag
                clear - whether or not we'll clear currently forced/queued exps
                    (Default: True)
                redraw - whether or not we're forcing a redraw
                    (Default: True)
                skip_dissolve - whether or not we skip dissolve transition for the next exp change
                    (Default: False)
            """
            exps = MASMoniIdleExp.exp_tags_map.get(tag, tuple())
            exp = MASMoniIdleExp.weighted_choice(exps)
            if exp is not None:
                self.force(exp, clear=clear, redraw=redraw, skip_dissolve=skip_dissolve)

        def unforce(self, exp, redraw=True, skip_dissolve=False):
            """
            Removes forced exp by instance

            IN:
                exp - MASMoniIdleExp / MASMoniIdleExpGroup object
                redraw - whether or not we're forcing a redraw
                    (Default: True)
                skip_dissolve - whether or not we skip dissolve transition for the next exp change
                    (Default: False)
            """
            if not (self.forced_mode or self.forced_exps or self._predicted_modes["forced_mode"]):
                return

            need_redraw = self.current_exp is exp

            if exp in self.forced_exps:
                self.forced_exps.remove(exp)
                need_redraw = True

            if (
                isinstance(exp, MASMoniIdleExpGroup)
                and exp in self.exp_groups
            ):
                self.exp_groups[:] = list()
                need_redraw = True

            if self._predicted_exp is exp:
                self._predicted_exp = None

            if skip_dissolve:
                self._skip_dissolve = True

            if redraw and need_redraw:
                self.update()

        def unforce_by_tag(self, tag, redraw=True, skip_dissolve=False):
            """
            Removes forced exp by tag

            IN:
                tag - tag to filter by
                redraw - whether or not we're forcing a redraw
                    (Default: True)
                skip_dissolve - whether or not we skip dissolve transition for the next exp change
                    (Default: False)
            """
            if not (self.forced_mode or self.forced_exps or self._predicted_modes["forced_mode"]):
                return

            need_redraw = self.current_exp.tag == tag

            for group in self.exp_groups:
                if group.tag == tag:
                    self.exp_groups[:] = list()
                    need_redraw = True
                    break

            for f_exp_id in range(len(self.forced_exps)-1, -1, -1):
                if self.forced_exps[f_exp_id].tag == tag:
                    self.forced_exps.pop(f_exp_id)
                    need_redraw = True

            if self._predicted_exp is not None and self._predicted_exp.tag == tag:
                self._predicted_exp = None

            if skip_dissolve:
                self._skip_dissolve = True

            if redraw and need_redraw:
                self.update()

        def unforce_all(self, redraw=True, skip_dissolve=False):
            """
            Removes all forced exp

            IN:
                redraw - whether or not we're forcing a redraw
                    (Default: True)
                skip_dissolve - whether or not we skip dissolve transition for the next exp change
                    (Default: False)
            """
            if not (self.forced_mode or self.forced_exps or self._predicted_modes["forced_mode"]):
                return

            if (
                (self.forced_mode and self.group_mode)
                or (self._predicted_modes["forced_mode"] and self._predicted_modes["group_mode"])
            ):
                self.exp_groups[:] = list()

            self._predicted_exp = None

            self.forced_exps[:] = list()

            if skip_dissolve:
                self._skip_dissolve = True

            if redraw:
                self.update()

        def __handle_group(self, group, add_to_list=True):
            """
            Handles a group OwO

            OUT:
                MASMoniIdleExp
            """
            # Get actuall exp
            exp, is_done, is_empty = group.progress_group()

            # This should never happen
            if exp is None:
                self.remove(group)
                exp = self.fallback

            # If the group is empty, we remove it
            elif is_empty:
                self.remove(group)

            # If this gruop cycle has ended, we remove it from the currently selected groups
            elif is_done:
                if group in self.exp_groups:
                    self.exp_groups.remove(group)

                # Also remove it from the pool if it's 'unrepeatable'
                if not group.repeatable:
                    self.remove(group)

            # Otherwise everything is good, add to the list of groups if needed
            elif add_to_list:
                self.exp_groups.append(group)

            return exp

        def __select_exp(self):
            """
            Selects an appropriate expression that we can show now

            OUT:
                MASMoniIdleExp

            ASSUMES:
                mas_curr_affection
                mas_utils.weightedChoice
            """
            exp = None
            exp_id = None
            chose_group = False

            # If we're currently using a group, then we continue
            while exp is None and self.exp_groups:
                chose_group = True

                group = self.exp_groups[-1]
                # We need to check the group in case of aff/cond changes
                if (
                    group.check_aff(check_children=False)
                    and group.check_conditional(check_children=False)
                ):
                    exp = self.__handle_group(group, add_to_list=False)

                # This group should be removed as inappropriate
                else:
                    self.exp_groups.pop(-1)

            # Otherwise try to select one of forced exps
            while exp is None and self.forced_exps:
                self._predicted_modes["forced_mode"] = True
                exp = self.forced_exps.pop(0)
                if not exp.check_aff() or not exp.check_conditional():
                    exp = None

            # If we still haven't chosen anything, select one of base exps
            if exp is None:
                self._predicted_modes["group_mode"] = False
                self._predicted_modes["forced_mode"] = False
                exp_list = self.exp_map[mas_curr_affection]
                if exp_list:
                    choices = list()
                    forced_choices = list()
                    has_valid_exp = False

                    for id, exp in enumerate(exp_list):
                        if exp.check_conditional():
                            has_valid_exp = True
                            # For convinience we force exps whose weight is None
                            if exp.weight is None:
                                forced_choices.append(id)

                            # Otherwise add to weighted choice
                            else:
                                choices.append((id, exp.weight))

                    if has_valid_exp:
                        if forced_choices:
                            exp_id = random.choice(forced_choices)

                        else:
                            exp_id = mas_utils.weightedChoice(choices)

                        exp = exp_list[exp_id]

                    else:
                        exp = None

            # Handle inner groups
            while isinstance(exp, MASMoniIdleExpGroup):
                self._predicted_modes["group_mode"] = True
                chose_group = True
                exp = self.__handle_group(exp, add_to_list=True)

            # If we STILL haven't chosen anything, we use the fallback
            if exp is None:
                self._predicted_modes["group_mode"] = False
                exp = self.fallback

            # Otherwise check if we should remove this exp
            elif not chose_group and not exp.repeatable:
                self.remove(exp)

            return exp

        def select_exp(self):
            """
            Actually selects an expression. If we had a predicted exp, return it,
            otherwise select one now.

            OUT:
                MASMoniIdleExp
            """
            if (
                self._predicted_exp is not None
                and self._predicted_exp.check_aff()
                and self._predicted_exp.check_conditional()
            ):
                exp = self._predicted_exp

            else:
                exp = self.__select_exp()

            self._predicted_exp = None
            self.forced_mode = self._predicted_modes["forced_mode"]
            self.group_mode = self._predicted_modes["group_mode"]

            # We meed to reset some params for wink transforms since RenPy is dum
            # if exp.code[1] in MASMoniIdleDisp.EYES_EXP_CODES:
            #     MASMoniIdleDisp.__reset_transform(exp.ref._target(), exp.code)

            return exp

        def render(self, width, height, st, at):
            """
            Render for this disp
            I have no idea how this works
            """
            if st > self._last_st:
                self.current_st += (st - self._last_st)

            # else:
            #     self.current_st += st

            self._last_st = st

            # Is it the time to select a new exp/stop dissolving?
            if (
                self.current_st >= self.redraw_st
                or (
                    self.dissolve_duration == 0.0
                    and (
                        not self.current_exp.check_aff()
                        or not self.current_exp.check_conditional()
                    )
                )
            ):
                self.current_st = 0.0

                # If we were dissolving, we just finished
                # Set next redraw using the exp duration
                if self.dissolve_duration != 0.0:
                    self.current_img = self.current_exp.ref
                    self.dissolve_duration = 0.0
                    self.redraw_st = self.current_exp.select_duration()
                    redraw_time = self.redraw_st

                # The current exp has expired, we need to select a new one
                else:
                    next_exp = self.select_exp()

                    # New pose? Dissolve
                    if not self._skip_dissolve and next_exp.code[0] != self.current_exp.code[0]:
                        key = (MASMoniIdleDisp.SLOW_DISSOLVE, self.current_exp.code, next_exp.code)

                        if key not in MASMoniIdleDisp._transform_cache:
                            self.current_img = renpy.display.transition.Dissolve(
                                time=MASMoniIdleDisp.SLOW_DISSOLVE,
                                old_widget=self.current_exp.ref,
                                new_widget=next_exp.ref,
                                alpha=True
                            )
                            MASMoniIdleDisp._transform_cache[key] = self.current_img

                        else:
                            self.current_img = MASMoniIdleDisp._transform_cache[key]

                        self.dissolve_duration = MASMoniIdleDisp.SLOW_DISSOLVE
                        self.redraw_st = MASMoniIdleDisp.SLOW_DISSOLVE
                        redraw_time = self.redraw_st

                    # Different exp? Dissolve
                    elif not self._skip_dissolve and next_exp.code != self.current_exp.code:
                        key = (MASMoniIdleDisp.QUICK_DISSOLVE, self.current_exp.code, next_exp.code)

                        if key not in MASMoniIdleDisp._transform_cache:
                            self.current_img = renpy.display.transition.Dissolve(
                                time=MASMoniIdleDisp.QUICK_DISSOLVE,
                                old_widget=self.current_exp.ref,
                                new_widget=next_exp.ref,
                                alpha=True
                            )
                            MASMoniIdleDisp._transform_cache[key] = self.current_img

                        else:
                            self.current_img = MASMoniIdleDisp._transform_cache[key]

                        self.dissolve_duration = MASMoniIdleDisp.QUICK_DISSOLVE
                        self.redraw_st = MASMoniIdleDisp.QUICK_DISSOLVE
                        redraw_time = self.redraw_st

                    # Otherwise we don't need to dissolve since the exp is the same (or we decided to skip dissolve in/out)
                    else:
                        self.current_img = next_exp.ref
                        self.dissolve_duration = 0.0
                        self._skip_dissolve = False
                        self.redraw_st = next_exp.select_duration()
                        redraw_time = self.redraw_st

                    # Now we can set the current exp
                    self.current_exp = next_exp

            # Otherwise we come here too early
            else:
                redraw_time = self.redraw_st - self.current_st

            img_render = renpy.render(self.current_img, width, height, self.current_st, at)

            main_render = renpy.Render(img_render.width, img_render.height)
            # main_render.place(img, x=0, y=0, st=render_st)
            main_render.blit(img_render, MASMoniIdleDisp.BLIT_COORDS)

            renpy.redraw(self, redraw_time)

            return main_render

        def get_placement(self):
            """
            Override that returns a more correct placement for this disp
            """
            xpos, ypos, xanchor, yanchor, xoffset, yoffset, subpixel = self.current_exp.ref.get_placement()

            if xoffset is None:
                xoffset = 0
            if yoffset is None:
                yoffset = 0

            return xpos, ypos, xanchor, yanchor, xoffset, yoffset, subpixel

        def visit(self):
            """
            Returns exps for prediction

            OUT:
                list of displayables
            """
            if self._predicted_exp is None:
                self._predicted_exp = self.__select_exp()
            return [self.current_exp.ref, self._predicted_exp.ref]

        def do_after_topic_logic(self):
            """
            Checks if we should reset the current exp
            since we just finished a topic, and if we should, does it
            NOTE: this is intended to be called in call_next_event
            """
            if not self.forced_mode:
                # Makes no sense to continue the group because of the topic interruption
                if self.group_mode:
                    self.exp_groups[:] = list()
                    self._predicted_exp = None
                    self._skip_dissolve = True
                    self.update()

                # If the current exp expires soon, we just skip it to avoid unnatural exp/pose changes
                elif self.duration < 2:
                    self._skip_dissolve = True
                    self.update()

        # @staticmethod
        # def __reset_transform(transform, code):
        #     """
        #     A method to partially reset a transform

        #     IN:
        #         transform - transform to reset params for
        #         code - exp code that's used to reset the transforms' child
        #     """
        #     transform.st = 0
        #     transform.at = 0
        #     transform.block = None
        #     # transform.predict_block = None
        #     transform.atl_state = None
        #     transform.done = False
        #     transform.transform_event = None
        #     transform.last_transform_event = None
        #     transform.last_child_transform_event = None
        #     transform.atl_st_offset = 0

        #     og_child = renpy.display.image.ImageReference(("monika", code,))
        #     transform.set_child(og_child)
        #     transform.raw_child = og_child

    class MASMoniBlinkTransform(renpy.display.core.Displayable):
        """
        A displayable which makes blinking possible
        (replaces the old ATL which was quite buggy)
        """
        # Consts for blink steps
        STEP_START = "start"
        STEP_DB_START = "db_start"
        STEP_DB_END = "db_end"
        STEP_END = "end"

        # The chance for double blink
        DB_CHANCE = 0.01

        # Blink timings (min, max)
        STEP_START_DUR_MIN = 3
        STEP_START_DUR_MAX = 7

        STEP_END_DUR_MIN = 0.06
        STEP_END_DUR_MAX = 0.07

        STEP_END_INTO_DB_DUR_MIN = 0.02
        STEP_END_INTO_DB_DUR_MAX = 0.04

        STEP_DB_START_DUR_MIN = 0.1
        STEP_DB_START_DUR_MAX = 0.15

        STEP_DB_END_DUR_MIN = STEP_END_DUR_MIN
        STEP_DB_END_DUR_MAX = STEP_END_DUR_MAX

        # Dissolves durations
        STEP_START_DIS_DUR = 0.01
        STEP_END_DIS_DUR = 0.01
        STEP_DB_START_DIS_DUR = STEP_START_DIS_DUR
        STEP_DB_END_DIS_DUR = STEP_END_DIS_DUR

        WINK_EYES = ("k", "n")

        BLIT_COORDS = (0, 0)

        # We keep these params in the class' namespace so we can keep the blink state between different exp
        current_img = None
        current_step = STEP_START
        next_step = STEP_START
        _last_at = 0.0
        current_at = 0.0
        redraw_at = 0.0

        def __init__(self, open_eyes_img, closed_eyes_img):
            """
            Constructor
            NOTE: this takes in full image names, with prefixes and suffixes

            IN:
                open_eyes_img - FULL name of the image for open eyes
                closed_eyes_img - FULL name of the image for closed eyes
            """
            super(MASMoniBlinkTransform, self).__init__(self)

            self.open_eyes_img = renpy.display.image.ImageReference(open_eyes_img)
            self.closed_eyes_img = renpy.display.image.ImageReference(closed_eyes_img)
            self.transform_map = {
                MASMoniBlinkTransform.STEP_START: renpy.display.transition.Dissolve(
                    time=MASMoniBlinkTransform.STEP_START_DIS_DUR,
                    old_widget=self.closed_eyes_img,
                    new_widget=self.open_eyes_img,
                    alpha=True
                ),
                MASMoniBlinkTransform.STEP_END: renpy.display.transition.Dissolve(
                    time=MASMoniBlinkTransform.STEP_END_DIS_DUR,
                    old_widget=self.open_eyes_img,
                    new_widget=self.closed_eyes_img,
                    alpha=True
                ),
                MASMoniBlinkTransform.STEP_DB_START: renpy.display.transition.Dissolve(
                    time=MASMoniBlinkTransform.STEP_DB_START_DIS_DUR,
                    old_widget=self.closed_eyes_img,
                    new_widget=self.open_eyes_img,
                    alpha=True
                ),
                MASMoniBlinkTransform.STEP_DB_END: renpy.display.transition.Dissolve(
                    time=MASMoniBlinkTransform.STEP_DB_END_DIS_DUR,
                    old_widget=self.open_eyes_img,
                    new_widget=self.closed_eyes_img,
                    alpha=True
                )
            }
            # Do this here to save some time during rendering
            self.is_wink = bool(open_eyes_img.split("monika ")[-1].split("_")[0][1] in MASMoniBlinkTransform.WINK_EYES)

        def render(self, width, height, st, at):
            """
            Render of this disp
            """
            # If st == 0, we do not increment the current at,
            # that's so Monika doesn't blink immediately after closed eyes
            if at > MASMoniBlinkTransform._last_at and st != 0:
                MASMoniBlinkTransform.current_at += (at - MASMoniBlinkTransform._last_at)

            MASMoniBlinkTransform._last_at = at

            # st == 0 means we just switched to this exp, might want to extend the blink dur for little bit
            if st == 0 and MASMoniBlinkTransform.current_step in (MASMoniBlinkTransform.STEP_START, MASMoniBlinkTransform.STEP_DB_START):
                # NOTE: If this is a wink and we just started showing it, we extend the blink duration
                # so Monika can finish her wink. This is a bit gross, but gives us better visuals.
                # If we ever need such handling for the other eyes, we might need a better system
                if self.is_wink:
                    MASMoniBlinkTransform.current_at = MASMoniBlinkTransform.redraw_at - MASMoniWinkTransform.STEP_START_DUR

                # Otherwise just some arbitrary number if it's the time to blink soon
                elif MASMoniBlinkTransform.redraw_at - MASMoniBlinkTransform.current_at < 0.5:
                    MASMoniBlinkTransform.current_at = MASMoniBlinkTransform.redraw_at - 0.25

                # Sanitize it
                # MASMoniBlinkTransform.redraw_at = min(MASMoniBlinkTransform.redraw_at, MASMoniBlinkTransform.STEP_START_DUR_MAX)
                MASMoniBlinkTransform.current_at = max(0, MASMoniBlinkTransform.current_at)

            # at == 0 means we just showed Monika, no transition at all
            if at == 0:
                MASMoniBlinkTransform.current_step = MASMoniBlinkTransform.STEP_START
                MASMoniBlinkTransform.current_at = 0.0
                MASMoniBlinkTransform.current_img = self.open_eyes_img
                MASMoniBlinkTransform.redraw_at = random.randint(MASMoniBlinkTransform.STEP_START_DUR_MIN, MASMoniBlinkTransform.STEP_START_DUR_MAX)
                MASMoniBlinkTransform.next_step = MASMoniBlinkTransform.STEP_END

            # Otherwise check if we should move to the next step
            elif MASMoniBlinkTransform.current_at >= MASMoniBlinkTransform.redraw_at:
                MASMoniBlinkTransform.current_at = 0.0
                MASMoniBlinkTransform.current_img = self.transform_map[MASMoniBlinkTransform.next_step]

                # First step (open eyes)
                if MASMoniBlinkTransform.next_step == MASMoniBlinkTransform.STEP_START:
                    MASMoniBlinkTransform.current_step = MASMoniBlinkTransform.STEP_START
                    MASMoniBlinkTransform.redraw_at = random.randint(MASMoniBlinkTransform.STEP_START_DUR_MIN, MASMoniBlinkTransform.STEP_START_DUR_MAX)
                    MASMoniBlinkTransform.next_step = MASMoniBlinkTransform.STEP_END

                # Last step (close eyes)
                elif MASMoniBlinkTransform.next_step == MASMoniBlinkTransform.STEP_END:
                    MASMoniBlinkTransform.current_step = MASMoniBlinkTransform.STEP_END
                    # Do we want a double blink?
                    if random.random() > MASMoniBlinkTransform.DB_CHANCE:
                        # No
                        MASMoniBlinkTransform.redraw_at = random.uniform(MASMoniBlinkTransform.STEP_END_DUR_MIN, MASMoniBlinkTransform.STEP_END_DUR_MAX)
                        MASMoniBlinkTransform.next_step = MASMoniBlinkTransform.STEP_START

                    else:
                        # Yes
                        MASMoniBlinkTransform.redraw_at = random.uniform(MASMoniBlinkTransform.STEP_END_INTO_DB_DUR_MIN, MASMoniBlinkTransform.STEP_END_INTO_DB_DUR_MAX)
                        MASMoniBlinkTransform.next_step = MASMoniBlinkTransform.STEP_DB_START

                # Substep start (double blink open eyes)
                elif MASMoniBlinkTransform.next_step == MASMoniBlinkTransform.STEP_DB_START:
                    MASMoniBlinkTransform.current_step = MASMoniBlinkTransform.STEP_DB_START
                    MASMoniBlinkTransform.redraw_at = random.uniform(MASMoniBlinkTransform.STEP_DB_START_DUR_MIN, MASMoniBlinkTransform.STEP_DB_START_DUR_MAX)
                    MASMoniBlinkTransform.next_step = MASMoniBlinkTransform.STEP_DB_END

                # Substep end (double blink close eyes)
                elif MASMoniBlinkTransform.next_step == MASMoniBlinkTransform.STEP_DB_END:
                    MASMoniBlinkTransform.current_step = MASMoniBlinkTransform.STEP_DB_END
                    MASMoniBlinkTransform.redraw_at = random.uniform(MASMoniBlinkTransform.STEP_DB_END_DUR_MIN, MASMoniBlinkTransform.STEP_DB_END_DUR_MAX)
                    MASMoniBlinkTransform.next_step = MASMoniBlinkTransform.STEP_START

            # Otherwise we're here too early, request a redraw
            else:
                # NOTE: It's important to update the curr img here
                MASMoniBlinkTransform.current_img = self.transform_map[MASMoniBlinkTransform.current_step]

            img_render = renpy.render(MASMoniBlinkTransform.current_img, width, height, MASMoniBlinkTransform.current_at, at)
            rv = renpy.Render(img_render.width, img_render.height)
            rv.blit(img_render, MASMoniBlinkTransform.BLIT_COORDS)

            # I'd like to save us redraws, but we can't. At minimum we need a redraw every 0.1-0.2 sec
            renpy.redraw(self, 0.1)

            return rv

        def visit(self):
            """
            Returns imgs for prediction

            OUT:
                list of displayables
            """
            return self.transform_map.values()

    class MASMoniWinkTransform(renpy.display.core.Displayable):
        """
        A displayable which makes winks possible
        (replaces the old ATL which was quite buggy)
        """
        STEP_START = "start"
        STEP_END = "end"
        STEP_DONE = "done"

        STEP_START_DUR = 1.0
        STEP_END_DIS_DUR = 0.01

        RESETTING_EVS = ("replace", "replaced")
        BLIT_COORDS = (0, 0)

        def __init__(self, wink_img, open_eyes_img):
            """
            Constructor
            NOTE: this takes in full image names, with prefixes and suffixes

            IN:
                wink_img - FULL name of the image for wink eyes
                open_eyes_img - FULL name of the image for opened eyes
            """
            super(MASMoniWinkTransform, self).__init__(self)

            self.wink_img = renpy.display.image.ImageReference(wink_img)
            self.open_eyes_img = renpy.display.image.ImageReference(open_eyes_img)
            self.current_img = self.wink_img
            self.wink_into_open_eyes_dis = renpy.display.transition.Dissolve(
                time=MASMoniBlinkTransform.STEP_END_DIS_DUR,
                old_widget=self.wink_img,
                new_widget=self.open_eyes_img,
                alpha=True
            )

            self.next_step = MASMoniWinkTransform.STEP_START

            self._last_st = 0.0
            self.current_st = 0.0
            self.redraw_st = 0.0

        def render(self, width, height, st, at):
            """
            Render of this disp
            """
            if st > self._last_st:
                self.current_st += (st - self._last_st)

            else:
                self.__reset()
                # self.current_st += st

            self._last_st = st

            if (
                self.redraw_st is not None
                and self.current_st >= self.redraw_st
            ):
                self.current_st = 0.0

                # First step (wink)
                if self.next_step == MASMoniWinkTransform.STEP_START:
                    self.current_img = self.wink_img
                    self.redraw_st = MASMoniWinkTransform.STEP_START_DUR
                    self.next_step = MASMoniWinkTransform.STEP_END

                # "Last" step (open eyes)
                elif self.next_step == MASMoniWinkTransform.STEP_END:
                    self.current_img = self.wink_into_open_eyes_dis
                    self.redraw_st = None

            img_render = renpy.render(self.current_img, width, height, self.current_st, at)
            rv = renpy.Render(img_render.width, img_render.height)
            rv.blit(img_render, MASMoniWinkTransform.BLIT_COORDS)

            if self.redraw_st is not None:
                renpy.redraw(self, self.redraw_st - self.current_st)

            return rv

        def visit(self):
            """
            Returns imgs for prediction

            OUT:
                list of displayables
            """
            return [self.wink_img, self.wink_into_open_eyes_dis]

        def __reset(self):
            """
            A method to reset params of this disp
            """
            self.next_step = MASMoniWinkTransform.STEP_START
            self._last_st = 0.0
            self.current_st = 0.0
            self.redraw_st = 0.0
            # self.current_img = self.open_eyes_img
            self.transform_event = None

        def _hide(self, st, at, kind):
            """
            This method is being called (sometimes) when the disp is being hidden.
            We use it to reset some params
            NOTE: must always return None
            """
            self.__reset()
            return None

        def _show(self):
            """
            This method is being called (sometimes) when the disp is being shown.
            We use it to reset some params
            """
            self.__reset()

    class MASMoniTearsTransform(renpy.display.core.Displayable):
        """
        A displayable which makes tears possible
        (replaces the old ATL which was quite buggy)
        """
        # Transforms "steps" consts
        STEP_START = "start"
        STEP_END = "end"

        # Timings consts
        STEP_START_DUR_MIN = 9
        STEP_START_DUR_MAX = 12

        STEP_END_DUR_MIN = 0.14
        STEP_END_DUR_MAX = 0.16

        # Dissolve duration consts
        STEP_START_DIS_DUR = 0.01
        STEP_END_DIS_DUR = 0.01

        BLIT_COORDS = (0, 0)

        current_img = None
        current_step = STEP_START
        next_step = STEP_START
        _last_at = 0.0
        current_at = 0.0
        redraw_at = 0.0

        def __init__(self, open_eyes_img, closed_eyes_img):
            """
            Constructor
            NOTE: this takes in full image names, with prefixes and suffixes

            IN:
                open_eyes_img - FULL name of the image for open eyes
                closed_eyes_img - FULL name of the image for closed eyes
            """
            super(MASMoniTearsTransform, self).__init__(self)

            self.open_eyes_img = renpy.display.image.ImageReference(open_eyes_img)
            self.closed_eyes_img = renpy.display.image.ImageReference(closed_eyes_img)
            self.transform_map = {
                MASMoniTearsTransform.STEP_START: renpy.display.transition.Dissolve(
                    time=MASMoniTearsTransform.STEP_START_DIS_DUR,
                    old_widget=self.closed_eyes_img,
                    new_widget=self.open_eyes_img,
                    alpha=True
                ),
                MASMoniTearsTransform.STEP_END: renpy.display.transition.Dissolve(
                    time=MASMoniTearsTransform.STEP_END_DIS_DUR,
                    old_widget=self.open_eyes_img,
                    new_widget=self.closed_eyes_img,
                    alpha=True
                )
            }

        def render(self, width, height, st, at):
            """
            Render of this disp
            """
            if at > MASMoniTearsTransform._last_at and st != 0:
                MASMoniTearsTransform.current_at += (at - MASMoniTearsTransform._last_at)

            MASMoniTearsTransform._last_at = at

            # st == 0 means we just switched to this exp, might want to extend the blink dur for little bit
            if (
                st == 0
                and MASMoniTearsTransform.current_step == MASMoniTearsTransform.STEP_START
                and MASMoniTearsTransform.redraw_at - MASMoniTearsTransform.current_at < 0.5
            ):
                MASMoniTearsTransform.current_at = max(0, MASMoniTearsTransform.redraw_at - 0.25)

            if at == 0:
                MASMoniTearsTransform.current_step = MASMoniTearsTransform.STEP_START
                MASMoniTearsTransform.current_at = 0.0
                MASMoniTearsTransform.current_img = self.open_eyes_img
                MASMoniTearsTransform.redraw_at = random.randint(MASMoniTearsTransform.STEP_START_DUR_MIN, MASMoniTearsTransform.STEP_START_DUR_MAX)
                MASMoniTearsTransform.next_step = MASMoniTearsTransform.STEP_END

            elif MASMoniTearsTransform.current_at >= MASMoniTearsTransform.redraw_at:
                MASMoniTearsTransform.current_at = 0.0
                MASMoniTearsTransform.current_img = self.transform_map[MASMoniTearsTransform.next_step]

                # First step (close eyes)
                if MASMoniTearsTransform.next_step == MASMoniTearsTransform.STEP_START:
                    MASMoniTearsTransform.current_step = MASMoniTearsTransform.STEP_START
                    MASMoniTearsTransform.redraw_at = random.randint(MASMoniTearsTransform.STEP_START_DUR_MIN, MASMoniTearsTransform.STEP_START_DUR_MAX)
                    MASMoniTearsTransform.next_step = MASMoniTearsTransform.STEP_END

                # Last step (open eyes)
                elif MASMoniTearsTransform.next_step == MASMoniTearsTransform.STEP_END:
                    MASMoniTearsTransform.current_step = MASMoniTearsTransform.STEP_END
                    MASMoniTearsTransform.redraw_at = random.uniform(MASMoniTearsTransform.STEP_END_DUR_MIN, MASMoniTearsTransform.STEP_END_DUR_MAX)
                    MASMoniTearsTransform.next_step = MASMoniTearsTransform.STEP_START

            else:
                MASMoniTearsTransform.current_img = self.transform_map[MASMoniTearsTransform.current_step]

            img_render = renpy.render(MASMoniTearsTransform.current_img, width, height, MASMoniTearsTransform.current_at, at)
            rv = renpy.Render(img_render.width, img_render.height)
            rv.blit(img_render, MASMoniTearsTransform.BLIT_COORDS)

            renpy.redraw(self, 0.1)

            return rv

        def visit(self):
            """
            Returns imgs for prediction

            OUT:
                list of displayables
            """
            return self.transform_map.values()

    class _MASMoniFollowTransformDissolve(renpy.display.transition.Dissolve):
        """
        Dissolve subclass that allows to pass different st and at values to its widgets
        """
        def __init__(self, *args, **kwargs):
            """
            Adds 4 new params
            """
            super(_MASMoniFollowTransformDissolve, self).__init__(*args, **kwargs)

            # KEY CHANGES
            self.new_widget_st = None
            self.new_widget_at = None
            self.old_widget_st = None
            self.old_widget_at = None

        def render(self, width, height, st, at):
            """
            Makes use of the new params
            """
            if renpy.game.less_updates:
                return renpy.display.transition.null_render(self, width, height, st, at)

            if st >= self.time:
                self.events = True
                return renpy.display.transition.render(self.new_widget, width, height, st, at)

            complete = min(1.0, st / self.time)

            if self.time_warp is not None:
                complete = self.time_warp(complete)

            # KEY CHANGES
            old_widget_st = self.old_widget_st if self.old_widget_st is not None else st
            old_widget_at = self.old_widget_at if self.old_widget_at is not None else at
            new_widget_st = self.new_widget_st if self.new_widget_st is not None else st
            new_widget_at = self.new_widget_at if self.new_widget_at is not None else at

            bottom = renpy.display.transition.render(self.old_widget, width, height, old_widget_st, old_widget_at)
            top = renpy.display.transition.render(self.new_widget, width, height, new_widget_st, new_widget_at)

            width = min(top.width, bottom.width)
            height = min(top.height, bottom.height)

            rv = renpy.display.render.Render(width, height, opaque=not self.alpha)

            rv.operation = renpy.display.render.DISSOLVE
            rv.operation_alpha = self.alpha
            rv.operation_complete = complete

            rv.blit(bottom, (0, 0), focus=False, main=False)
            rv.blit(top, (0, 0), focus=True, main=True)

            renpy.display.render.redraw(self, 0)

            return rv

    class MASMoniFollowTransform(renpy.display.core.Displayable):
        """
        A displayable which makes follow sprites possible
        (replaces conditionswitch for dissolves and optimization)
        """
        REDRAW_PAUSE = 0.1

        DIS_DUR = 0.1

        BLIT_COORDS = (0, 0)

        def __init__(self, norm_eyes_img, left_eyes_img, right_eyes_img, up_eyes_img=None, down_eyes_img=None):
            """
            Constructor
            NOTE: this takes in full image names, with prefixes and suffixes

            IN:
                norm_eyes_img - FULL name of the image for look straight eyes
                left_eyes_img - FULL name of the image for look left eyes
                right_eyes_img - FULL name of the image for look right eyes
                up_eyes_img - FULL name of the image for look up eyes
                    NOTE: unused since we don't have the sprites yet
                down_eyes_img - FULL name of the image for look down eyes
                    NOTE: unused since we don't have the sprites yet
            """
            super(MASMoniFollowTransform, self).__init__(self)

            self.norm_eyes_code = norm_eyes_img
            self.norm_eyes_img = renpy.display.image.ImageReference(norm_eyes_img)
            self.left_eyes_code = left_eyes_img
            self.left_eyes_img = renpy.display.image.ImageReference(left_eyes_img)
            self.right_eyes_code = right_eyes_img
            self.right_eyes_img = renpy.display.image.ImageReference(right_eyes_img)
            # self.up_eyes_code = up_eyes_img
            # self.up_eyes_img = renpy.display.image.ImageReference(up_eyes_img)
            # self.down_eyes_code = down_eyes_img
            # self.down_eyes_img = renpy.display.image.ImageReference(down_eyes_img)

            self.current_img = self.norm_eyes_img
            self.current_exp_code = self.norm_eyes_code

            # NOTE: keys here are tuples of strings of the current and next exp
            self.transform_map = dict()
            img_map = {
                self.norm_eyes_code: self.norm_eyes_img,
                self.left_eyes_code: self.left_eyes_img,
                self.right_eyes_code: self.right_eyes_img,
                # self.up_eyes_code: self.up_eyes_img,
                # self.down_eyes_code: self.down_eyes_img
            }
            for first_img_code in img_map.iterkeys():
                for second_img_code in img_map.iterkeys():
                    if first_img_code != second_img_code:
                        self.transform_map[(first_img_code, second_img_code)] = _MASMoniFollowTransformDissolve(
                            time=MASMoniFollowTransform.DIS_DUR,
                            old_widget=img_map[first_img_code],
                            new_widget=img_map[second_img_code],
                            alpha=True
                        )

            self._last_st = 0.0
            self.current_st = 0.0
            self.redraw_st = 0.0

        def render(self, width, height, st, at):
            """
            Render of this disp
            """
            if st > self._last_st:
                self.current_st += (st - self._last_st)

            # else:
            #     self.current_st += st

            self._last_st = st

            if st == 0 or self.current_st >= self.redraw_st:
                self.current_st = 0.0
                self.redraw_st = MASMoniFollowTransform.REDRAW_PAUSE

                mouse_pos = store.mas_windowutils.getMousePosRelative()
                if mouse_pos[0] < 0:
                    next_img = self.left_eyes_img
                    next_exp_code = self.left_eyes_code

                elif mouse_pos[0] > 0:
                    next_img = self.right_eyes_img
                    next_exp_code = self.right_eyes_code

                # elif mouse_pos[1] > 0:
                #     next_img = self.up_eyes_img
                #     next_exp_code = self.up_eyes_code

                # elif mouse_pos[1] < 0:
                #     next_img = self.down_eyes_img
                #     next_exp_code = self.down_eyes_code

                else:
                    next_img = self.norm_eyes_img
                    next_exp_code = self.norm_eyes_code

                if st != 0 and self.current_exp_code != next_exp_code:
                    self.current_img = self.transform_map[(self.current_exp_code, next_exp_code)]
                    self.current_exp_code = next_exp_code
                    # Pass the st and at params to the transforms widgets
                    # so we can keep their states regardless of the transition
                    self.current_img.old_widget_st = st
                    self.current_img.old_widget_at = at
                    self.current_img.new_widget_st = st
                    self.current_img.new_widget_at = at
                    render_st = self.current_st

                else:
                    self.current_img = next_img
                    self.current_exp_code = next_exp_code
                    render_st = st

                redraw_time = self.redraw_st

            else:
                redraw_time = self.redraw_st - self.current_st
                render_st = st

            img_render = renpy.render(self.current_img, width, height, render_st, at)
            rv = renpy.Render(img_render.width, img_render.height)
            rv.blit(img_render, MASMoniFollowTransform.BLIT_COORDS)

            renpy.redraw(self, redraw_time)

            return rv

        def visit(self):
            """
            Returns imgs for prediction

            OUT:
                list of displayables
            """
            return self.transform_map.values()

# # # END: Idle disp stuff

init -2 python in mas_sprites:
    # base-related sprtie stuff
    # NOTE: this should be made AFTER the sprite object classes are defined

    # ARMS to MASArm object mapping
    NUM_MARMS = {
        1: store.MASArmBoth,
        2: store.MASArmLeft,
        3: store.MASArmLeft,
        4: store.MASArmRight,
        5: store.MASArmRight,
        6: store.MASArmRight,
        7: store.MASArmBoth,
        8: store.MASArmLeft,
        9: store.MASArmRight,
    }

    # the base arms
    base_arms = store.MASPoseArms({

        # crossed
        1: NUM_MARMS[1](
            "crossed",
            {
                store.MASArm.LAYER_MID: True,
                store.MASArm.LAYER_TOP: True,
            }
        ),

        # left-down
        2: NUM_MARMS[2](
            "down",
            {
                store.MASArm.LAYER_BOT: True,
            }
        ),

        # left-rest
        3: NUM_MARMS[3](
            "rest",
            {
                store.MASArm.LAYER_TOP: True,
            }
        ),

        # right-down
        4: NUM_MARMS[4](
            "down",
            {
                store.MASArm.LAYER_BOT: True,
            }
        ),

        # right-point
        5: NUM_MARMS[5](
            "point",
            {
                store.MASArm.LAYER_BOT: True,
            }
        ),

        # right-restpoint
        6: NUM_MARMS[6](
            "restpoint",
            {
                store.MASArm.LAYER_TOP: True,
            }
        ),

        # steepling
        7: NUM_MARMS[7](
            "steepling",
            {
                store.MASArm.LAYER_TOP: True,
            }
        ),

        # def|left-def
        8: NUM_MARMS[8](
            "def",
            {
                store.MASArm.LAYER_TOP: True,
            }
        ),

        # def|right-def
        9: NUM_MARMS[9](
            "def",
            {
                store.MASArm.LAYER_MID: True,
                store.MASArm.LAYER_TOP: True,
            }
        ),
    })

    # the base pose arm map
    base_mpm = store.MASPoseMap(

        # steepling
        p1=(7,),

        # crossed
        p2=(1,),

        # restleftpointright - left-rest / right-restpoint
        p3=(3, 6),

        # pointright - left-down / right-point
        p4=(2, 5),

        # leaning-def - def|left-def / def|right-def
        p5=(8, 9),

        # down - left-down / right-down
        p6=(2, 4),

        # downleftpointright - left-down / right-restpoint
        p7=(2, 6)

    )

    # NOTE: consider allowing spritejsons to do this
    def use_bma(arm_id):
        """
        Returns base MASArm for an armid

        IN:
            arm_id - numerical digit for an arm. Corresponds to NUM_ARMS

        RETURNS: base MASArm for this arm, or None if no Arm
        """
        return base_arms.get(arm_id)

    def use_bmpm(posenum):
        """
        Returns tuple of MASArms for a pose num

        IN:
            posenum - numerical digit for a pose. This corresponds to
                NUM_POSE.

        RETURNS: base MASArms for this poes, or None if no arms
        """
        return use_bpam_s(NUM_POSE.get(posenum, None))


    def use_bmpm_s(leanpose):
        """
        Version of use_bpam that uses leanpose

        IN:
            leanpose - leanpose string

        RETURNS: base MASArms for this pose, or None if no arms
        """
        return base_mpm.get(leanpose, None)


init -1 python in mas_sprites:
    # other post-sprite object functions (do NOT put base stuff in here)

    def show_empty_desk():
        """
        shows empty desk
        """
        renpy.show(
            "emptydesk",
            tag="emptydesk",
            at_list=[store.i11],
            zorder=store.MAS_MONIKA_Z - 1
        )

# Monika
define monika_chr = MASMonika()

# empty desk should be defined after MASMonika
image emptydesk = DynamicDisplayable(
    mas_drawemptydesk_rk,
    character=monika_chr
)


#### IMAGE START (IMG030)
# Image are created using a DynamicDisplayable to allow for runtime changes
# to sprites without having to remake everything. This saves us on image
# costs.
#
# To create a new image, these parts are required:
#   eyebrows, eyes, nose, mouth (for sitting)
#   head, left, right OR a single image (for standing)
#
# Optional parts for sitting is:
#   sweat, tears, blush, emote, eyebags
#
# Non-leaning poses require an ARMS part.
# leaning poses require a LEAN part.
#
# For more information see mas_drawmonika function
#
#### FOLDER IMAGE RULES: (IMG031)
# To ensure that the images are created correctly, all images must be placed in
# a specific folder heirarchy.
#
# mod_assets/monika/f/<facial expressions>
# mod_assets/monika/c/<clothing types>/<body/arms/poses>
# mod_assets/monika/h/<hair types>
# mod_assets/monika/a/<accessories>
#
# All layers must have a night version, which is denoted using the -n suffix.
# All leaning layers must have a non-leaning fallback
#
## FACIAL EXPRESSIONS:
# Non leaning filenames:
#   face-{face part type}-{face part name}{-n}.png
#   (ie: face-mouth-big.png / face-mouth-big-n.png)
# leaning filenames:
#   face-leaning-{lean type}-{face part type}-{face part name}{-n}.png
#   (ie: face-leaning-eyes-sparkle.png / face-leaning-eyes-sparkle-n.png)
#
## BODY / POSE:
# NEW
# Non leaning:
#   body-def{-n}.png
#   arms-{arms name}{-n}.png
# Leaning:
#   body-leaning-{lean type}{-n}.png
#   arms-leaning-{lean type}-{arms pose}{-n}.png
#
# OLD:
# Non leaning filenames / parts:
#   torso-{hair type}{-n}.png
#   arms-{arms name}{-n}.png
#   (ie: torso-def.png / torso-def-n.png)
#   (ie: arms-def-steepling.png / arms-def-steepling-n.png)
# Leaning filenames:
#   torso-leaning-{hair type}-{lean name}{-n}.png
#   (ie: torso-leaning-def-def.png / torso-leaning-def-def-n.png)
#
## HAIR:
# hair-{hair type}-{front/back}{-n}.png
#

# NOTE: all sprites moved to sprite-chart-00

### [IMG032]
# Image aliases
# NOTE: if you want to use a standing sprite, it must be one of these
#   HOWEVER: you may need to use the static variants because not every
#   sprite has closed eye versions.
#   The only sprite combos with closed eyes standing are _sc and _sd.
#   everything else does not have a closed eye variant. sux to succ

#NOTE: KEEPING THIS FOR REFERENCE AS TO WHAT SPRITES HAVE A STANDING EQUIVALENT
## pose 1
#monika 1 = "monika 1esa"
#monika 1a = "monika 1eua"
#monika 1b = "monika 1eub"
#monika 1c = "monika 1euc"
#monika 1d = "monika 1eud"
#monika 1e = "monika 1eka"
#monika 1f = "monika 1ekc"
#monika 1g = "monika 1ekd"
#monika 1h = "monika 1esc"
#monika 1i = "monika 1esd"
#monika 1j = "monika 1hua"
#monika 1k = "monika 1hub"
#monika 1l = "monika 1hksdlb"
#monika 1ll = "monika 1hksdrb"
#monika 1m = "monika 1lksdla"
#monika 1mm = "monika 1rksdla"
#monika 1n = "monika 1lksdlb"
#monika 1nn = "monika 1rksdlb"
#monika 1o = "monika 1lksdlc"
#monika 1oo = "monika 1rksdlc"
#monika 1p = "monika 1lksdld"
#monika 1pp = "monika 1rksdld"
#monika 1q = "monika 1dsc"
#monika 1r = "monika 1dsd"
#
## pose 2
#monika 2 = "monika 2esa"
#monika 2a = "monika 2eua"
#monika 2b = "monika 2eub"
#monika 2c = "monika 2euc"
#monika 2d = "monika 2eud"
#monika 2e = "monika 2eka"
#monika 2f = "monika 2ekc"
#monika 2g = "monika 2ekd"
#monika 2h = "monika 2esc"
#monika 2i = "monika 2esd"
#monika 2j = "monika 2hua"
#monika 2k = "monika 2hub"
#monika 2l = "monika 2hksdlb"
#monika 2ll = "monika 2hksdrb"
#monika 2m = "monika 2lksdla"
#monika 2mm = "monika 2rksdla"
#monika 2n = "monika 2lksdlb"
#monika 2nn = "monika 2rksdlb"
#monika 2o = "monika 2lksdlc"
#monika 2oo = "monika 2rksdlc"
#monika 2p = "monika 2lksdld"
#monika 2pp = "monika 2rksdld"
#monika 2q = "monika 2dsc"
#monika 2r = "monika 2dsd"
#
## pose 3
#monika 3 = "monika 3esa"
#monika 3a = "monika 3eua"
#monika 3b = "monika 3eub"
#monika 3c = "monika 3euc"
#monika 3d = "monika 3eud"
#monika 3e = "monika 3eka"
#monika 3f = "monika 3ekc"
#monika 3g = "monika 3ekd"
#monika 3h = "monika 3esc"
#monika 3i = "monika 3esd"
#monika 3j = "monika 3hua"
#monika 3k = "monika 3hub"
#monika 3l = "monika 3hksdlb"
#monika 3ll = "monika 3hksdrb"
#monika 3m = "monika 3lksdla"
#monika 3mm = "monika 3rksdla"
#monika 3n = "monika 3lksdlb"
#monika 3nn = "monika 3rksdlb"
#monika 3o = "monika 3lksdlc"
#monika 3oo = "monika 3rksdlc"
#monika 3p = "monika 3lksdld"
#monika 3pp = "monika 3rksdld"
#monika 3q = "monika 3dsc"
#monika 3r = "monika 3dsd"
#
## pose 4
#monika 4 = "monika 4esa"
#monika 4a = "monika 4eua"
#monika 4b = "monika 4eub"
#monika 4c = "monika 4euc"
#monika 4d = "monika 4eud"
#monika 4e = "monika 4eka"
#monika 4f = "monika 4ekc"
#monika 4g = "monika 4ekd"
#monika 4h = "monika 4esc"
#monika 4i = "monika 4esd"
#monika 4j = "monika 4hua"
#monika 4k = "monika 4hub"
#monika 4l = "monika 4hksdlb"
#monika 4ll = "monika 4hksdrb"
#monika 4m = "monika 4lksdla"
#monika 4mm = "monika 4rksdla"
#monika 4n = "monika 4lksdlb"
#monika 4nn = "monika 4rksdlb"
#monika 4o = "monika 4lksdlc"
#monika 4oo = "monika 4rksdlc"
#monika 4p = "monika 4lksdld"
#monika 4pp = "monika 4rksdld"
#monika 4q = "monika 4dsc"
#monika 4r = "monika 4dsd"
#
## pose 5
#monika 5 = "monika 5eua"
#monika 5a = "monika 5eua"
#monika 5b = "monika 5euc"

### [IMG040]
# Custom animated sprites
# Currently no naming convention, but please keep them somehwat consistent
# with the current setup:
# <pose number>ATL_<short descriptor>
#
# NOTE: if we do blinking, please make that a separate section from this

image monika 6ATL_cryleftright:
    block:

        # select an image
        block:
            choice:
                "monika 6lktsc"
            choice:
                "monika 6rktsc"

        # select a wait time
        block:
            choice:
                0.9
            choice:
                1.0
            choice:
                0.5
            choice:
                0.7
            choice:
                0.8

        repeat

# # # START: DEPRECATED IMAGES, THESE WILL BE REMOVED SOON
image monika 6ATL_lookleftright:

    # select image
    block:
        choice:
            "monika 6rkc"
        choice:
            "monika 6lkc"

    # select a wait time
    block:
        choice:
            5.0
        choice:
            6.0
        choice:
            7.0
        choice:
            8.0
        choice:
            9.0
        choice:
            10.0
    repeat

image monika ATL_0_to_upset:

    # 1 time this part
    "monika 2esc"
    5.0

    # repeat this part
    block:
        # select image
        block:
            choice 0.95:
                "monika 2esc"
            choice 0.05:
                "monika 5tsc"

        # select wait time
        block:
            choice:
                10.0
            choice:
                12.0
            choice:
                14.0
            choice:
                16.0
            choice:
                18.0
            choice:
                20.0

        repeat

image monika ATL_affectionate:
    # select image
    block:
        choice 0.02:
            "monika 1eua"
            1.0
            choice:
                "monika 1sua"
                4.0
            choice:
                "monika 1kua"
                1.5
            "monika 1eua"

        choice 0.98:
            choice 0.94898:
                "monika 1eua"
            choice 0.051020:
                "monika 1hua"

    # select wait time
    block:
        choice:
            20.0
        choice:
            22.0
        choice:
            24.0
        choice:
            26.0
        choice:
            28.0
        choice:
            30.0

    repeat

image monika ATL_enamored:

    # 1 time this part
    "monika 1eua"
    5.0

    # repeat
    block:
        # select image
        block:
            choice 0.02:
                "monika 1eua"
                1.0
                choice:
                    "monika 1sua"
                    4.0
                choice:
                    "monika 1kua"
                    1.5
                "monika 1eua"

            choice 0.98:
                choice 0.765306:
                    "monika 1eua"
                choice 0.112245:
                    "monika 5esu"
                choice 0.061224:
                    "monika 5tsu"
                choice 0.061224:
                    "monika 1huu"

        # select wait time
        block:
            choice:
                20.0
            choice:
                22.0
            choice:
                24.0
            choice:
                26.0
            choice:
                28.0
            choice:
                30.0

        repeat

image monika ATL_love:

    # 1 time this parrt
    "monika 1eua"
    5.0

    # repeat
    block:
        # select image
        block:
            choice 0.02:
                "monika 1eua"
                1.0
                choice:
                    "monika 1sua"
                    4.0
                choice:
                    "monika 1kua"
                    1.5
                "monika 1eua"

            choice 0.98:
                choice 0.510104:
                    "monika 1eua"
                choice 0.255102:
                    "monika 5esu"
                choice 0.091837:
                    "monika 5tsu"
                choice 0.091837:
                    "monika 1huu"
                choice 0.051020:
                    "monika 5eubla"

        # select wait time
        block:
            choice:
                20.0
            choice:
                22.0
            choice:
                24.0
            choice:
                26.0
            choice:
                28.0
            choice:
                30.0

        repeat
# # # END: DEPRECATED IMGS

### [IMG045]
# special purpose ATLs that cant really be used for other things atm

# random exps for love_too at normal thru aff
image monika ATL_love_too_norm_plus:
    block:
        choice:
            "monika 1hua"
        choice:
            "monika 1huu"
        choice:
            "monika 1ekbsu"
        choice:
            "monika 1ekbsa"
        choice:
            "monika 1dkbsu"
        choice:
            "monika 1dubsu"
        choice:
            "monika 1dkbsa"
        choice:
            "monika 5ekbsa"
        choice:
            "monika 5esu"
        choice:
            "monika 5eka"

# random exps for love_too at enam+
image monika ATL_love_too_enam_plus:
    block:
        choice 0.05:
            "monika 1sua"
        choice 0.05:
            "monika 1subsa"
        choice 0.10:
            "monika 1hua"
        choice 0.10:
            "monika 1huu"
        choice 0.10:
            "monika 1ekbsu"
        choice 0.10:
            "monika 1ekbsa"
        choice 0.10:
            "monika 1dkbsu"
        choice 0.10:
            "monika 1dubsu"
        choice 0.10:
            "monika 1dkbsa"
        choice 0.10:
            "monika 5ekbsa"
        choice 0.10:
            "monika 5esu"

### [IMG050]
# NOTE we need this ready before init 500
init 499 python:
    # Brand new displayable for idle
    mas_moni_idle_disp = MASMoniIdleDisp(
        (
            # Broken (how dared you, monster?)
            MASMoniIdleExp("6ckc", duration=60, aff_range=(None, mas_aff.BROKEN), tag="broken_exps"),
            # Distressed
            MASMoniIdleExp("6rkc", duration=(5, 10), aff_range=(mas_aff.DISTRESSED, mas_aff.DISTRESSED), tag="dist_exps"),
            MASMoniIdleExp("6lkc", duration=(5, 10), aff_range=(mas_aff.DISTRESSED, mas_aff.DISTRESSED), tag="dist_exps"),
            MASMoniIdleExpGroup(
                [
                    MASMoniIdleExpRngGroup(
                        [
                            MASMoniIdleExp("6rktpc", duration=(5, 10)),
                            MASMoniIdleExp("6lktpc", duration=(5, 10))
                        ],
                        max_uses=4
                    ),
                    MASMoniIdleExpRngGroup(
                        [
                            MASMoniIdleExp("6rktdc", duration=(5, 10)),
                            MASMoniIdleExp("6lktdc", duration=(5, 10))
                        ]
                    ),
                    MASMoniIdleExp("6dktdc", duration=(3, 5))
                ],
                aff_range=(mas_aff.DISTRESSED, mas_aff.DISTRESSED),
                weight=2,
                tag="dist_exps"
            ),
            # Below 0 and Upset
            MASMoniIdleExp("2esc", duration=5, aff_range=(mas_aff.UPSET, mas_aff.NORMAL), conditional="mas_isBelowZero()", weight=None, repeatable=False, tag="below_zero_startup_exps"),
            MASMoniIdleExp("2esc", aff_range=(mas_aff.UPSET, mas_aff.NORMAL), conditional="mas_isBelowZero()", weight=95, tag="below_zero_exps"),
            MASMoniIdleExp("5tsc", aff_range=(mas_aff.UPSET, mas_aff.NORMAL), conditional="mas_isBelowZero()", weight=5, tag="below_zero_exps"),
            # Normal
            MASMoniIdleExp("1esa", duration=60, aff_range=(mas_aff.NORMAL, mas_aff.NORMAL), conditional="not mas_isBelowZero()", tag="norm_exps"),
            # Happy
            MASMoniIdleExp("1eua", duration=60, aff_range=(mas_aff.HAPPY, mas_aff.HAPPY), tag="happy_exps"),
            # Affectionate
            MASMoniIdleExpGroup(
                [
                    MASMoniIdleExp("1eua", duration=1),
                    MASMoniIdleExp("1sua", duration=4),
                    MASMoniIdleExp("1eua"),
                ],
                aff_range=(mas_aff.AFFECTIONATE, None),
                weight=2,
                tag="idle_star_eyes"
            ),
            MASMoniIdleExpGroup(
                [
                    MASMoniIdleExp("1eua", duration=1),
                    MASMoniIdleExp("1kua", duration=1),
                    MASMoniIdleExp("1eua"),
                ],
                aff_range=(mas_aff.AFFECTIONATE, None),
                weight=2,
                tag="idle_wink"
            ),
            MASMoniIdleExpRngGroup(
                [
                    MASMoniIdleExp("1eua", weight=70),
                    MASMoniIdleExp("1eua_follow", weight=30)# 30% to follow
                ],
                max_uses=1,
                aff_range=(mas_aff.AFFECTIONATE, mas_aff.AFFECTIONATE),
                weight=94,
                tag="aff_exps"
            ),
            MASMoniIdleExp("1hua", aff_range=(mas_aff.AFFECTIONATE, mas_aff.AFFECTIONATE), weight=5, tag="aff_exps"),
            # Enamored
            MASMoniIdleExp("1eua", duration=5, aff_range=(mas_aff.ENAMORED, None), weight=None, repeatable=False, tag="enam_plus_startup_exps"),
            MASMoniIdleExpRngGroup(
                [
                    MASMoniIdleExp("1eua", weight=None),
                    MASMoniIdleExp("1eua_follow", weight=None)# 50% to follow
                ],
                max_uses=1,
                aff_range=(mas_aff.ENAMORED, mas_aff.ENAMORED),
                weight=75,
                tag="enam_exps"
            ),
            MASMoniIdleExpRngGroup(
                [
                    MASMoniIdleExp("5esu", weight=None),
                    MASMoniIdleExp("5esu_follow", weight=None)# 50% to follow
                ],
                max_uses=1,
                aff_range=(mas_aff.ENAMORED, mas_aff.ENAMORED),
                weight=11,
                tag="enam_exps"
            ),
            MASMoniIdleExp("5tsu", aff_range=(mas_aff.ENAMORED, mas_aff.ENAMORED), weight=6, tag="enam_exps"),
            MASMoniIdleExp("1huu", aff_range=(mas_aff.ENAMORED, mas_aff.ENAMORED), weight=6, tag="enam_exps"),
            # Love
            MASMoniIdleExpRngGroup(
                [
                    MASMoniIdleExp("1eua", weight=30),
                    MASMoniIdleExp("1eua_follow", weight=70)# 70% to follow
                ],
                max_uses=1,
                aff_range=(mas_aff.LOVE, None),
                weight=50,
                tag="love_exps"
            ),
            MASMoniIdleExpRngGroup(
                [
                    MASMoniIdleExp("5esu", weight=30),
                    MASMoniIdleExp("5esu_follow", weight=70)# 70% to follow
                ],
                max_uses=1,
                aff_range=(mas_aff.LOVE, None),
                weight=26,
                tag="love_exps"
            ),
            MASMoniIdleExp("5tsu", aff_range=(mas_aff.LOVE, None), weight=9, tag="love_exps"),
            MASMoniIdleExp("1huu", aff_range=(mas_aff.LOVE, None), weight=9, tag="love_exps"),
            MASMoniIdleExpRngGroup(
                [
                    MASMoniIdleExp("5eubla", weight=30),
                    MASMoniIdleExp("5eubla_follow", weight=70)# 70% to follow
                ],
                max_uses=1,
                aff_range=(mas_aff.LOVE, None),
                weight=5,
                tag="love_exps"
            ),
            MASMoniIdleExpRngGroup(
                [
                    MASMoniIdleExp("5eubsa", weight=30),
                    MASMoniIdleExp("5eubsa_follow", weight=70)# 70% to follow
                ],
                max_uses=1,
                aff_range=(mas_aff.LOVE, None),
                weight=2,
                tag="love_exps"
            )
        )
    )

image monika idle = mas_moni_idle_disp

### [IMG100]
# chibi monika sprites
image chibika smile = "gui/poemgame/m_sticker_1.png"
image chibika sad = "mod_assets/other/m_sticker_sad.png"
image chibika 3 = "gui/poemgame/m_sticker_2.png"

#Ghost monika
image ghost_monika:
    "mod_assets/other/ghost_monika.png"
    zoom 1.25

### [IMG200]
# transition labels

# transiton to empty desk
# NOTE: to hide a desk ACS, set that ACS to not keep on desk b4 calling this
label mas_transition_to_emptydesk(hide_dlg_box=True):
    if hide_dlg_box:
        window hide
    $ store.mas_sprites.show_empty_desk()
    hide monika with dissolve_monika
    return

# transition from empty desk
# NOTE: to unhide a desk ACS, set that ACS to keep on desk AFTER calling this
# IN:
#   exp - expression to show when monika is shown
label mas_transition_from_emptydesk(exp="monika 1eua", show_dlg_box=True):
    if show_dlg_box:
        window auto
    $ renpy.show(exp, tag="monika", at_list=[i11], zorder=MAS_MONIKA_Z)
    $ renpy.with_statement(dissolve_monika)
    hide emptydesk
    return
