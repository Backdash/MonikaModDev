#Runtime code equivalent of our spritemaker tool
init python in mas_sprite_decoder:
    import store

    EYEBROW_MAP = {
        "f": "furrowed",
        "u": "up",
        "k": "knit",
        "s": "mid",
        "t": "think",
    }

    EYE_MAP = {
        "e": "normal",
        "w": "wide",
        "s": "sparkle",
        "t": "smug",
        "c": "crazy",
        "r": "right",
        "l": "left",
        "h": "closedhappy",
        "d": "closedsad",
        "k": "winkleft",
        "n": "winkright",
        "f": "soft",
        "m": "smugleft",
        "g": "smugright",
    }

    MOUTH_MAP = {
        "a": "smile",
        "b": "big",
        "c": "smirk",
        "d": "small",
        "o": "gasp",
        "u": "smug",
        "w": "wide",
        "x": "angry",
        "p": "pout",
        "t": "triangle",
    }

    ARM_MAP = {
        "1": "steepling",
        "2": "crossed",
        "3": "restleftpointright",
        "4": "pointright",
        "5": ("def", "def"),
        "6": "down",
        "7": "downleftpointright",
    }

    #Standing sprite parts
    HEAD_MAP = {
        # exact eye - eyebrow - mouth match
        "eua": "a",
        "eub": "b",
        "euc": "c",
        "eud": "d",
        "eka": "e",
        "ekc": "f",
        "ekd": "g",
        "esc": "h",
        "esd": "i",
        "hua": "j",
        "hub": "k",
        "hkb": "l", #sdl
        "lka": "m", #sdl
        "lkb": "n", #sdl
        "lkc": "o", #sdl
        "lkd": "p", #sdl
        "dsc": "q",
        "dsd": "r",
    }

    SIDES_MAP = {
        "1": ("1l", "1r"),
        "2": ("1l", "2r"),
        "3": ("2l", "2r"),
        "4": ("2l", "2r"),
        "5": ("", ""),
        "6": ("1l", "1r"),
        "7": ("1l", "2r"),
    }

    #NOTE: Everything not present here is assumed 3b
    SINGLE_MAP = {
        "a": "3a",
        "u": "3a",
    }

    BLUSH_MAP = {
        "bl": "lines",
        "bs": "shade",
        "bf": "full"
    }

    TEAR_MAP = {
        "ts": "streaming",
        "td": "dried",
        "tp": "pooled",
        "tu": "up",
    }

    SWEAT_MAP = {
        "sdl": "def",
        "sdr": "right"
    }

    def __process_blush(spcode, index, export_dict, *prefixes):
        """
        Processes a blush off the given sprite code at the given index

        IN:
            spcode the spcode to check
            index the next index to check
            export_dict - dict to add the sprite data to
            prefixes letters to prefix the code with

        OUT:
            Tuple of the following format:
                [0] - True if the blush was valid, False if not
                [1] - the number of spots to increase the index by
        """
        #Next letter must be blush type
        fullcode = list(prefixes)
        fullcode.append(spcode[index])

        blush = BLUSH_MAP.get("".join(fullcode), None)

        if blush is None:
            return False, 0

        #All checks pass and we have blush. Let's add that
        export_dict["blush"] = blush
        return True, 1

    def __process_s(spcode, index, export_dict, *prefixes):
        """
        Processes the s-prefixed spcodes at the given index

        IN:
            spcode the spcode to check
            index the next index to check
            export_dict - dict to add the sprite data to
            prefixes letters to prefix the code with

        OUT:
            Tuple of the following format:
                [0] - True if the processes were valid, False if not
                [1] - the number of spots to increase the index by
        """
        midfix = spcode[index]
        index += 1
        sprite_added = False

        processor = SUB_PROCESS_MAP["s"].get(midfix, None)

        if processor is not None:
            fullcode = list(prefixes)
            fullcode.append(midfix)

            sprite_added, increaseby = processor(
                spcode,
                index,
                export_dict,
                *fullcode
            )

        # if any sprite failed, or we didnt find a midfix
        if not sprite_added:
            return False, 0

        # otherwise, we good to go
        return True, 1 + increaseby

    def __process_sweatdrop(spcode, index, export_dict, *prefixes):
        """
        Processes a sweatdrop off the given spcode at the given index

        IN:
            spcode the spcode to check
            index the next index to check
            export_dict - dict to add the sprite data to
            prefixes letters to prefix the code with

        OUT:
            Tuple of the following format:
                [0] - True if the sweatdrops were valid, False if not
                [1] - the number of spots to increase the index by
        """
        # next letter must be the sweatdrop type
        fullcode = list(prefixes)
        fullcode.append(spcode[index])

        sweatdrop = SWEAT_MAP.get("".join(fullcode), None)

        if sweatdrop is None:
            return False, 0

        #All checks pass, we have sweat
        export_dict["sweat"] = sweatdrop
        return True, 1

    def __process_tears(spcode, index, export_dict, *prefixes):
        """
        Processes a tear off the given spcode at the given index

        IN:
            spcode the spcode to check
            index the next index to check
            export_dict - dict to add the sprite data to
            prefixes letters to prefix the code with

        OUT:
            Tuple of the following format:
                [0] - True if the tears were valid, False if not
                [1] - the number of spots to increase the index by
        """
        # next letter must be the tear type
        fullcode = list(prefixes)
        fullcode.append(spcode[index])

        tears = TEAR_MAP.get("".join(fullcode), None)

        if tears is None:
            return False, 0

        #Checks passed. Let's add this
        export_dict["tears"] = tears
        return True, 1

    PROCESS_MAP = {
        "b": __process_blush,
        "s": __process_s,
        "t": __process_tears,
    }

    SUB_PROCESS_MAP = {
        "s": {
            "d": __process_sweatdrop,
        },
    }

    def parse_exp_to_kwargs(exp):
        """
        Converts exp codes to kwargs to pass into mas_drawmonika_rk

        IN:
            exp - spritecode to convert

        OUT:
            dict representing the exp as kwargs for mas_drawmonika_rk

        ASSUMES:
            exp is not in the staticsprite format (not exp_static)

        RAISES:
            - KeyError if pose, eyes, eyebrows, or mouth is invalid
            - Exception if optional sprite is invalid
        """
        full_code = exp
        kwargs = dict()

        #First parse arms, taking care of leaning as well here
        arms = ARM_MAP[exp[0]]

        #Leaning is always a tuple
        if isinstance(arms, tuple):
            #Since this is a tuple, we should unpack this here, so lean type and arms are set accordingly
            kwargs["lean"], arms = arms

            #We'll also manage leaning's standing sprite fully here
            kwargs["single"] = SINGLE_MAP.get(exp[-1], "3b")

        else:
            #Leaning doesn't get sides
            kwargs["left"], kwargs["right"] = SIDES_MAP[exp[0]]


        kwargs["arms"] = arms

        #Now let's see if we have a head match
        kwargs["head"] = HEAD_MAP.get("".join((exp[1], exp[2], exp[-1])), "")

        #Now the eyes
        kwargs["eyes"] = EYE_MAP[exp[1]]

        #Now the eyebrows
        kwargs["eyebrows"] = EYEBROW_MAP[exp[2]]

        #Next, we'll take care of the mouth
        kwargs["mouth"] = MOUTH_MAP[exp[-1]]

        #Let's condense the exp string here
        exp = exp[3:-1]

        #Since nose is static, just keep that here
        kwargs["nose"] = "def"

        index = 0
        while index < len(exp):
            prefix = exp[index]
            index += 1
            sprite_added = False

            #Let's see what we should process this with
            processor = PROCESS_MAP.get(prefix, None)
            if processor is not None:
                sprite_added, increaseby = processor(
                    exp,
                    index,
                    kwargs,
                    prefix
                )

            #If any sprite failed, or we didnt find a prefix, we will raise an exception since the code is invalid
            if not sprite_added:
                raise Exception("Invalid sprite used: {0}".format(full_code))

            # otherwise, we good to continue
            index += increaseby

        return kwargs

    def isValidSpritecode(exp):
        """
        Spritecode validity tester

        IN:
            exp - exp to check validity

        OUT:
            boolean:
                - True if code is valid
                - False otherwise
        """
        #First, make sure it's not static
        exp = exp.replace("_static", "")

        #Now we try/except
        try:
            parse_exp_to_kwargs(exp)

            #If no error here, then this is valid
            return True

        #Otherwise this is invalid
        except:
            return False
