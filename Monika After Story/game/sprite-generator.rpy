init python in mas_sprites:
    #START: main funcs

    def register_image(name, d):
        """
        Thanks for nothing, RenPy

        Registers the existence of an image with `name`, and that the image
        used displayable d.

        IN:
            name - tuple of strings (tag, attributes)
            d - displayables
        """
        if store.mas_globals.is_r7:
            renpy.display.image.register_image(name, d)

        else:
            img_tag = name[0]
            img_attr = name[1:]
            existing_attrs = renpy.display.image.image_attributes[img_tag]

            #Override the displayable if it exists
            renpy.display.image.images[name] = d
            #Override the attributes if those exist
            if img_attr not in existing_attrs:
                existing_attrs.append(img_attr)

    def needs_closed_eye_variant(exp):
        """
        Checks if an exp needs a closed eye variation

        IN:
            exp - spritecode to check

        OUT:
            boolean - True if the given spritecode needs a closed eye variant, False otherwise
        """
        return exp[1] not in "hd"

    def is_wink_sprite(exp):
        """
        Checks if an exp is a wink sprite

        IN:
            exp - spritecode to check

        OUT:
            boolean - True if this is a wink sprite, False otherwise
        """
        return exp[1] in "kn"

    def is_follow_sprite(exp):
        """
        Checks if an exp is a follow sprite

        IN:
            exp - spritecode to check

        OUT:
            boolean - True if this is a follow sprite, False otherwise
        """
        return exp.endswith("_follow")

    def needs_tear_atl(exp):
        """
        Checks if this spritecode needs a streaming tears atl

        IN:
            exp - spritecode to check

        OUT:
            boolean - True if so, False otherwise
        """
        return "ts" in exp[3:-1]

    def replace_eyes(exp, replacement_eyes):
        """
        Returns the sprite string for the closed eye variant

        IN:
            exp - exp to replace eyes
            replacement_eyes - spritecode part representing the replacement eyes

        OUT:
            closed eye representation of the given spritecode
        """
        pose = exp[:1]
        rest = exp[2:]
        return pose + replacement_eyes + rest

    def generate_static_sprite(exp):
        """
        Creates the DynamicDisplayable object for the given exp

        IN:
            exp - exp to make a closed eye version of
        """
        register_image(
            ("monika", exp + "_static"),
            store.DynamicDisplayable(
                store.mas_drawmonika_rk,
                character=store.monika_chr,
                **store.mas_sprite_decoder.parse_exp_to_kwargs(exp)
            )
        )

    def generate_follow_sprite(exp):
        """
        Creates the follow version of the given sprite
        """
        exp = exp.replace("_follow", '')
        look_left_img = replace_eyes(exp, "r")
        look_right_img = replace_eyes(exp, "l")

        if not renpy.has_image("monika " + exp):
            generate_normal_sprite(exp)

        if not renpy.has_image("monika " + look_left_img):
            generate_normal_sprite(look_left_img)

        if not renpy.has_image("monika " + look_right_img):
            generate_normal_sprite(look_right_img)

        m_prefix = "monika "
        register_image(
            ("monika", "{0}_follow".format(exp)),
            #TODO: When we get Briar's sprites in, add a small displayable that'll handle follow sprites
            store.ConditionSwitch(
                "store.mas_windowutils.isCursorLeftOfMASWindow()", m_prefix + look_left_img,
                "store.mas_windowutils.isCursorRightOfMASWindow()", m_prefix + look_right_img,
                "True", m_prefix + exp,
                #NOTE: This works only on r7, but does no harm on r6
                predict_all=True
            )
        )

    def add_static_sprite_alias(exp):
        """
        Registers an alias for static sprites

        IN:
            exp to make an alias for

        ASSUMES:
            non-static version exists
        """
        register_image(
            ("monika", exp),
            renpy.display.image.images[("monika", exp + "_static")]
        )

    def generate_normal_sprite(exp):
        """
        Generates sprites for standard open/closed eye variants

        DOES NOT HANDLE WINKS

        IN:
            exp - spritecode to generate sprites for
        """
        #Do we want to generate just a static sprite?
        just_static = False
        if exp.endswith("_static"):
            #We don't need the suffix
            exp = exp.replace("_static", "")
            just_static = True

        #Now, verify if we have the closed eye variant if needed. If not we should make that
        closed_eyes_variant = replace_eyes(exp, 'd')

        #Do we need to make the atl variant?
        needs_atl = not just_static and needs_closed_eye_variant(exp)

        if needs_atl and not renpy.has_image("monika " + closed_eyes_variant):
            generate_static_sprite(closed_eyes_variant)
            add_static_sprite_alias(closed_eyes_variant)

        #Now generate the requested sprite
        generate_static_sprite(exp)

        #If this requires an ATL, we'll gen it here
        if needs_atl:
            if needs_tear_atl(exp):
                register_image(
                    ("monika", exp),
                    store.streaming_tears_transform(
                        "monika " + exp + "_static",
                        "monika " + closed_eyes_variant + "_static"
                    )
                )

            else:
                register_image(
                    ("monika", exp),
                    store.blink_transform(
                        "monika " + exp + "_static",
                        "monika " + closed_eyes_variant + "_static"
                    )
                )

        #Don't make alias if we were asked for just static
        elif not just_static:
            add_static_sprite_alias(exp)

    def generate_wink_sprite(exp):
        """
        Generates wink sprites and their prerequisites
        """
        open_eye_variant = replace_eyes(exp, 'e')
        #Firstly, let's check if its normal eye variant exists
        if not renpy.has_image(open_eye_variant):
            #Since it doesn't, we'll need to generate it
            generate_normal_sprite(open_eye_variant)

        #Now let's make wink spr
        generate_static_sprite(exp)

        #And now we make its ATL
        register_image(
            ("monika", exp),
            store.wink_transform(
                "monika " + exp + "_static",
                "monika " + open_eye_variant
            )
        )

    def generate_images(exp):
        """
        Generates sprites, aliases, and their prerequisites and adds them to the renpy.display.image.images map

        IN:
            exp - spritecode to generate
        """
        exp = unicode(exp)

        if is_wink_sprite(exp):
            generate_wink_sprite(exp)
        elif is_follow_sprite(exp):
            generate_follow_sprite(exp)
        else:
            generate_normal_sprite(exp)
