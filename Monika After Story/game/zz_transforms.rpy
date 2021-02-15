# Module containing custom transform functions.
# Last just because
# NOTE: Depends on script-poemgame

# special early access image accessors
init -10 python:

    def getCharacterImage(char, expression="1a"):
        #
        # Retrieves the image of the given character + expression combo
        # This is the raw object that represents an image
        #
        # IN:
        #   char - string name of the character to find:
        #       "monika", "sayori", "natsuki", "yuri"
        #   expression - string expression to find
        #       (Default: 1a)
        #
        # RETURNS:
        #   the image object that is held internally, or None if not found
        return renpy.display.image.images.get((char, expression), None)


    def mas_getPropFromStyle(style_name, prop_name):
        """
        Retrieves a property from a style
        Recursively checks parent styles until the property is found.

        IN:
            style_name - name of style as string
            prop_name - property to find as string

        RETURNS: value of the propery if we can find it, None if not found
        """
        style_name = (style_name,)
        prop_not_found = True
        while prop_not_found:
            # pull from styles dict
            # NOTE: directly accessing to avoid exceptions
            style_obj = renpy.style.styles.get(style_name, None)
            if style_obj is None:
                return None

            # sanity check to ensure properties exists
            if len(style_obj.properties) > 0:

                # check for the prop we want
                if prop_name in style_obj.properties[0]:
                    return style_obj.properties[0][prop_name]

            # otherwise check parent
            if style_obj.parent is None:
                return None

            # recurse
            style_name = style_obj.parent

        # should never be reached
        return None


    def mas_prefixFrame(frm, prefix):
        """
        Generates a frame object with the given prefix substitued into the
        image. This effectively makes a copy of the given Frame object.

        NOTE: cannot use _duplicate as it does shallow copy for some reason.

        IN:
            frm - Frame object
            prefix - prefix to replace `prefix_`. "_" will be added if not
                found

        RETURNS: Frame object, or None if failed to make it
        """
        if not prefix.endswith("_"):
            prefix += "_"

        try:
            # sve borders
            frm_borders = {
                "left": frm.left,
                "top": frm.top,
                "right": frm.right,
                "bottom": frm.bottom,
            }

            # set image path
            img_path = renpy.substitute(
                frm.image.name,
                scope={"prefix_": prefix}
            )

            # build frame
            return Frame(img_path, **frm_borders)
        except:
            return None

# A transition of the new type
# which only works with mas_with_statement or Ren'Py 7.0+
init -5 python:
    dissolve_monika = {"master": Dissolve(0.25, alpha=True)}
    dissolve_textbox = {"screens": Dissolve(0.2, alpha=True)}

# user defined trasnforms
transform leftin_slow(x=640, z=0.80, t=1.00):
    xcenter -300 yoffset 0 yanchor 1.0 ypos 1.03 zoom z*1.00 alpha 1.00 subpixel True
    easein t xcenter x

# transform positional shortcuts
# NOTE: only the ones that we need are defined. Add them as you need em
transform ls32:
    leftin_slow(x=640)

# piano slides in
transform lps32:
    leftin_slow(x=640,t=4.00)

# used so things that slide in will also slide back out
transform lslide(t=1.00, x=-600):
    subpixel True
    on hide:
        easeout t xcenter x

# used so Monika can slide back out
transform rs32:
    lslide()

# used so piano can slide back out
transform rps32:
    lslide(t=4.00,x=-700)

### transforms for chibi monika
transform mas_chdropin(x=640, y=405, travel_time=3.00):
    ypos -300 xcenter x
    easein travel_time ypos y

transform mas_chflip(dir):
    # -1 to face right.
    # 1 to face left
    xzoom dir

transform mas_chflip_s(dir, travel_time=0.36):
    ease travel_time xzoom dir

transform mas_chhopflip(dir, ydist=-15, travel_time=0.36):
    # -1 to face right
    # 1 to face left
    easein_quad travel_time/2.0 yoffset ydist xzoom 0
    easeout_quad travel_time/2.0 yoffset 0 xzoom dir

transform mas_chmove(x, y, travel_time=1.0):
    # x and y should be coordinates
    # use this to directly move to a location
    ease travel_time xpos x ypos y

# NOTE: use sticker_hop for straight hopping

transform mas_chriseup(x=300, y=405, travel_time=1.00):
    ypos 800 xcenter x
    easein travel_time ypos y

# parabola jump
transform mas_chlongjump(x, y, ymax, travel_time=1.0):
    parallel:
        linear travel_time xpos x
    parallel:
        easeout travel_time*0.6 ypos ymax
        easein travel_time*0.4 ypos y

#START: Transforms for Monika's sprite animations (blinking/winking/tear-specific-blinking)
transform blink_transform(open_eyes_img, closed_eyes_img):
    animation
    block:
        open_eyes_img
        block:
            choice:
                3
            choice:
                5
            choice:
                7
        closed_eyes_img
        choice 0.02:
            0.03
            open_eyes_img
            0.1
            closed_eyes_img
        choice 0.98:
            pass
        0.06
        repeat

transform wink_transform(wink_img, open_eyes_img):
    # HACK: we use events here so renpy allows us to reuse this transform
    on default, show, replace:
        wink_img
        1
        open_eyes_img

transform streaming_tears_transform(open_eyes_img, closed_eyes_img):
    animation
    block:
        open_eyes_img
        block:
            choice:
                9
            choice:
                11
            choice:
                12
        closed_eyes_img
        0.15
        repeat
