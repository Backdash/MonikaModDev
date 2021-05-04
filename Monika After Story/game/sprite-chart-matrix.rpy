# sprite generation using matrix for night sprites
# TODO: look at adding a highlight option to ACS/Clothes/Hair

python early:
# Custom filter renderable

# uncomment this if you want syntax highlighting support on vim
#init -1 python:

    class MASFilterException(Exception):
        """
        General filter exceptions
        """

        def __init__(self, msg):
            """
            Constructor

            IN:
                msg - messgae to show
            """
            self.msg = msg

        def __str__(self):
            return self.msg


    class MASInvalidFilterException(MASFilterException):
        """
        Use when an invalid filter is being used
        """

        def __init__(self, bad_flt):
            """
            Constructor

            IN:
                bad_flt - the invalid filter being used
            """
            self.msg = "'{0}' is not a valid filter".format(bad_flt)


    class MASFilterable(renpy.Displayable):
        """
        Special displayable that adjusts its image based on filter.
        Also includes surface caching, if desired.

        PROPERTIES:
            flt - filter we last used
        """

        def __init__(self,
                focus=None,
                default=False,
                style='default',
                _args=None,
                **properties
        ):
            """
            Constructor

            IN:
                All params are passed to Displayable
            """
            super(renpy.Displayable, self).__init__(
                focus=focus,
                default=default,
                style=style,
                _args=_args,
                **properties
            )
            self.flt = None

        # NOTE: extended classes should impelement the render function.


    class MASFilterableSprite(MASFilterable):
        """
        Generic Filterable Sprite with Highlight support

        Potentially more optimal than MASFilterSwitch, but likely to have less
        configuration.

        NOTE:
            Many of the style properties will likely NOT work with this.
            If you can make it work, submit a PR.

        PROPERTIES:
            img_path - image path of this sprite
            img_obj = Image object of this sprite
            highlight - MASFilterMap of highlights to use
        """

        def __init__(self,
                image_path,
                highlight,
                focus=None,
                default=False,
                style='default',
                _args=None,
                **properties
        ):
            """
            Constructor

            IN:
                image_path - MUST be an image path string.
                highlight - MASFilterMap object of highlights to apply
            """
            super(MASFilterable, self).__init__(
                focus=focus,
                default=default,
                style=style,
                _args=_args,
                **properties
            )
            self.img_path = image_path
            self.img_obj = Image(image_path)
            self.highlight = highlight

        def __gen_hl(self):
            """
            Builds highlight Image based on current filters and cache

            REUTRNS: Image to use as highlight, None if we shouldnt make filter
            """
            # no highlight, no worry
            if self.highlight is None:
                return None

            # check cache
            img_key = (self.flt, self.img_path)
            hlg_c = store.mas_sprites._gc(store.mas_sprites.CID_HLG)
            if img_key in hlg_c:
                return hlg_c[img_key]

            # get hlcode
            hlcode = self.highlight.get(self.flt)

            # check if we even have highlight for this filter
            if hlcode is None:
                hlg_c[img_key] = None
                return None

            # we have a highlight, so lets build
            new_img = store.mas_sprites._bhlifp(self.img_path, hlcode)
            hlg_c[img_key] = new_img
            return new_img

        def render(self, width, height, st, at):
            """
            Render function
            """

            self.flt = store.mas_sprites.get_filter()

            # generate image
            new_img = store.mas_sprites._gen_im(self.flt, self.img_obj)

            # then highlight
            hl_img = self.__gen_hl()

            # NOTE: branching this for efficiency.
            #   we woudl still need to branch once to check of hl is valid,
            #   so we don't lose anything in branching the render into two
            #   separate paths. Non-highlights get a slightly faster render.
            if hl_img is None:
                # no looping, just do a quick render

                # render and blit
                render = renpy.render(new_img, width, height, st, at)
                rw, rh = render.get_size()
                rv = renpy.Render(rw, rh)
                rv.blit(render, (0, 0))

            else:
                # loop render
                render_list = [
                    renpy.render(img, width, height, st, at)
                    for img in (new_img, hl_img)
                ]

                # size is determined by the image render
                rw, rh = render_list[0].get_size()
                rv = renpy.Render(rw, rh)

                # loop blit
                for render in render_list:
                    rv.blit(render, (0, 0))

            # save
            return rv

        def visit(self):
            self.flt = store.mas_sprites.get_filter()

            # prepare filtered image
            new_img = store.mas_sprites._gen_im(self.flt, self.img_obj)

            # and highlight
            hl_img = self.__gen_hl()

            # decide what to return
            if hl_img is None:
                return [new_img]

            return [new_img, hl_img]


    def MASFilterSwitch(img):
        """
        Builds a condition switch that applies appropriate filters.

        NOTE: as this returns a ConditionSwitch, use this when you need
            more renpy-based control over an image.

        IN:
            img - image path/ImageBase to build filter switch for
                NOTE: CANNOT BE A DISPLAYABLE

        RETURNS: ConditionSwitch for filters
        """
        if isinstance(img, basestring):
            img = renpy.substitute(img)

        args = []
        for flt in store.mas_sprites.FILTERS.iterkeys():

            # condition
            args.append("store.mas_sprites.get_filter() == '{0}'".format(flt))

            # filtered image
            args.append(store.mas_sprites._gen_im(flt, img))

        return ConditionSwitch(*args)


    def MASLiteralFilterSwitch(def_img, filterize_def, **flt_pairs):
        """
        Builds a filter switch that lets you explicitly define the images
        for a filter.

        NOTE: this is a bad choice to use UNLESS you have a good default.

        IN:
            def_img - the default image to use for any filter not defined.
            filterize_def - True will apply filters to the default image
                as appropraite, False will NOT apply filters.
                Setting this as False may result in a sprite that looks shit
                in certain settings.
            **flt_pairs - name=value args for specific filters:
                name: filter enum (day/night/etc...)
                value: the image value to use for that filter

        RETURNS: ConditionSwitch with filter support
        """
        return MASDictFilterSwitch(def_img, filterize_def, flt_pairs)


    def MASDictFilterSwitch(def_img, filterize_def, flt_pairs):
        """
        Builds a filter switch that lets you explicitly define the images
        for a filter.

        NOTE: this is a bad choice to use UNLESS you have a good default.

        IN:
            def_img - the default image to use for any filter not defined.
            filterize_def - True will apply filters to the default image
                as appropraite, False will NOT apply filters.
                Setting this as False may result in a sprite that looks shit
                in certain settings.
            flt_pairs - dict mapping filtesr to images
                key: filter enum (day/night/etc...)
                value: the image value to use for that filter

        RETURNS: ConditionSwitch with filter support
        """
        args = []

        # process explicit filter pairs
        for flt in flt_pairs:
            if flt in store.mas_sprites.FILTERS:
                # condition
                args.append("mas_isCurrentFlt('{0}')".format(flt))

                # image
                args.append(flt_pairs[flt])

        # add default
        if filterize_def:

            # default should be filterized
            for flt in store.mas_sprites.FILTERS.iterkeys():

                # only use the filtesr we have not already added
                if flt not in flt_pairs:
                    # condition
                    args.append("mas_isCurrentFlt('{0}')".format(flt))

                    # image
                    args.append(store.mas_sprites._gen_im(flt, def_img))

        else:
            # otherwise set as just default
            args.append("True")
            args.append(def_img)

        return ConditionSwitch(*args)


    def MASDayNightFilterSwitch(day_img, night_img):
        """
        Builds a filter switch that changes image based on if the current flt
        is a day/night filter.

        This does NOT apply any filters.

        IN:
            day_img - image to return if day flt is in use
            night_img - image to return if night flt is in use

        RETURNS: ConditionSwitch that works with day/night filters.
        """
        return ConditionSwitch(
            "store.mas_current_background.isFltDay()", day_img,
            "store.mas_current_background.isFltNight()", night_img
        )


    def MASFilteredSprite(flt, img):
        """
        Generates an already filtered version of the given image

        IN:
            flt - filter to use
            img_base - image path/ImageBase to build filtered sprite for

        RETURNS: Displayable of the filtered image
        """
        return renpy.easy.displayable(store.mas_sprites._gen_im(flt, img))


    def MASFallbackFilterDisplayable(**filter_pairs):
        """
        Generates a dynamic displayable for filters that applies fallback
        mechanics. If you don't need fallback mechanics, use the filter
        switches.

        IN:
            **filter_pairs - filter=val args to use. invalid filters are
                ignored.

        RETURNS: Dynamic displayable that handles fallback filters
        """
        return DynamicDisplayable(
            mas_fbf_select,
            MASFilterMapFallback(**filter_pairs)
        )


    def MASFilterWeatherDisplayable(use_fb, **filter_pairs):
        """
        Generates a dynamic displayable that maps filters to weathers for
        arbitrary objects.

        This supports fallback-based value getting. For example:
            Assuming there are 3 precip types (pt - 1, 2, 3)
            and there are 4 filters (flt - A, B, C, D)
            Fallback is denoted by fb
            Precip type 1 is the DEFAULT precip type.

            Let's say the configuration for this MASFilterWeatherDisp is:

            flt A - pt 1, 2, 3
            flt B - pt 1, 3     - fb: A
            flt C - pt 2        - fb: B

            flt B is a fallback for flt D, but flt D is NOT defined in this
            MASFilterWeatherDisp.

            This is what would happen for combinations of filter, precip_type,
            and use_fb settings:

            Current flt: A - Current pt: 2 - use_fb: any
            In this case, flt A is defined and has a value for precip type 2.
            The image at flt A, pt 2 is selected.

            Current flt: B - Current pt: 3 - use_fb: any
            In this case, flt B is defined and has a value for pt 3. The image
            at flt B, pt 3 is selected.

            Current flt: B - Current pt: 2 - use_fb: True
            In this case, flt B does not have a precip_type of 2. Since we are
            using fallback mode and flt A is a fallback of B, the image at
            flt A, pt 2 is selected.

            Current flt: B - Current pt: 2 - use_fb: False
            This is the same case as above except we are NOT using fallback
            mode. In this case, the image at flt B, pt 1 is selected since it
            is the default precip type.

            Current flt: C - Current pt: 3 - use_fb: True
            In this case, flt C does not have a pt of 3. Since we are using
            fallback mode and flt B is a fallback of C, the image at flt B,
            pt 3 is selected.

            Current flt: C - Current pt: 3 - use_fb: False
            This case would NEVER happen because an exception would be raised
            on startup. If use_fb is False, a default precip type must be
            defined for all filters.

            Current flt: D - Current pt: 3 - use_fb: True
            In this case, flt D is not defined in this MASFilterWeatherDisp.
            Since we are using fallback mode and flt B is a fallback of flt D,
            the image at flt B, pt 3 is selected.

            Current flt: D - Current pt: 3 - use_fb: False
            In thise, flt D is not defined. Even though we are NOT using
            fallback mode, since flt B is a fallback of flt D, the image at
            flt B, pt 3 is selected.

            Current flt: D - Current pt: 2 - use_fb: True
            In this case, flt D is not defined, but flt B does NOT have an
            image for pt 2. Since we are using fallback mode, flt B is a
            fallback of flt D, and flt A is a fallback of flt B, the image at
            flt A, pt 2 is selected.

            Current flt: D - Current pt: 2 - use_fb: False
            In thise case, flt D is not defined. Since we are NOT using
            fallback mode and flt B does NOT have an image for pt 2, the image
            at flt B, pt 1 is selected as it is the default precip type.

        In terms of filter_pairs, if fallback-based getting is used, then
        only the base filters need a PRECIP_TYPE_DEF to be valid for all
        filter+weather type combinations. If normal getting is used, then
        every filter will need PRECIP_TYPE_DEF to be set or else images may
        not exist for a filter. This is checked on startup at init level 2.

        IN:
            use_fb - set to True to use filter fallback-based value getting.
                This will use the filter fallback mapping to retrieve values
                for a precip_type if a selected filter does not have a value
                for a precip_type. See above for an example.
                False will use standard value getting.
            **filter_pairs - fitler pairs to pass directly to
                MASFilterWeatherMap

        RETURNS: DynamicDisplayable that respects Filters and weather.
        """
        return MASFilterWeatherDisplayableCustom(
            mas_fwm_select,
            use_fb,
            **filter_pairs
        )


    def MASFilterWeatherDisplayableCustom(dyn_func, use_fb, **filter_pairs):
        """
        Version of MASFilterWeatherDisplayable that accepts a custom function
        to use instead of the default mas_fwm_select.

        See MASFilterWeatherDisplayable for explanations of this kind of disp.

        NOTE: in general, you should use MASFilterWeatherDisplayable.
        """
        # build new MASFilterWeatherMap
        new_map = MASFilterWeatherMap(**filter_pairs)
        new_map.use_fb = use_fb

        # add to DB and set ID
        new_id = store.mas_sprites.FW_ID + 1
        store.mas_sprites.FW_DB[new_id] = new_map
        store.mas_sprites.FW_ID += 1

        # return DynDisp
        return DynamicDisplayable(dyn_func, new_map)


init -2 python:

    def mas_fwm_select(st, at, mfwm):
        """
        Selects an image based on current filter and weather.

        IN:
            st - renpy related
            at - renpy related
            mfwm - MASFilterWeatherMap to select image wtih

        RETURNS: dynamic disp output
        """
        return (
            mfwm.fw_get(
                store.mas_sprites.get_filter(),
                store.mas_current_weather
            ),
            None
        )


    def mas_fbf_select(st, at, mfmfb):
        """
        Selects an image based on current filter, respecting fallback
        mechanics.

        IN:
            st - renpy related
            at - renpy related
            mfmfb - MASFilterMapFallback object to select image with

        RETURNS: dynamic disp output
        """
        return mfmfb.get(store.mas_sprites.get_filter()), None


init 1 python in mas_sprites:

    def _verify_fwm_db():
        """
        Verifies that data in the FW_DB is correct.
        MASFilterWeatherMaps are valid if:
            1. if the MFWM is fallback-based:
                a) All filters provided include a fallback filter with
                    PRECIP_TYPE_DEF set.
            2. If the MFWM is standard:
                a) All filters contain a PRECIP_TYPE_DEF set.

        Raises all errors.
        """
        for mfwm_id, mfwm in FW_DB.iteritems():
            _verify_mfwm(mfwm_id, mfwm)


    def _verify_mfwm(mfwm_id, mfwm):
        """
        Verifies a MASFilterWeatherMap object.

        Raises all errors.

        IN:
            mfwm_id - ID of the MASFilterWeatherMap object
            mfwm - MASFilterWeatherMap object to verify
        """
        if mwfm.use_fb:
            # fallback-based

            # contains all flts that have a valid default fallback somewhere.
            flt_defs = {}

            for flt in mfwm.flts():
                if not _mfwm_find_fb_def(mfwm, flt, flt_defs):
                    raise Exception(
                        (
                            "MASFilterWeatherMap does not have default "
                            "precip type set in the fallback chain for "
                            "filter '{0}'. ID: {1}"
                        ).format(
                            flt,
                            mfwm_id
                        )
                    )

        else:
            # standard
            for flt in mfwm.flts():
                wmap = mfwm._raw_get(flt)
                if wmap._raw_get(store.mas_weather.PRECIP_TYPE_DEF) is None:
                    raise Exception(
                        (
                            "MASFilterWeatherMap does not have a default "
                            "precip type set for filter '{0}'. ID: {1}"
                        ).format(
                            flt,
                            mfwm_id
                        )
                    )


    def _mfwm_find_fb_def(mfwm, flt, flt_defs):
        """
        Finds fallbacks from a starting flt that are covered with a default
        precip type.

        IN:
            mfwm - MASFilterWeatherMap object we are checking
            flt - filter we are checking for fallbacks
            flt_defs - dict containing keys of filters that already have known
                defaults in their fallback chains.

        OUT:
            flt_defs - additional filters with known defaults are added to this
                dict as we go through the fallback chain of the given flt.

        RETURNS: True if we found a non-None default precip type. False if not
        """
        # check if filter has already been checked.
        if flt in flt_defs:
            return True

        # otherwise begin fallback chains
        memo = {}
        ord_memo = []
        curr_flt = _find_next_fb(flt, memo, ord_memo)
        while not mfwm.has_def(curr_flt):
            nxt_flt = _find_nxt_fb(curr_flt, memo, ord_memo)

            # if filter has not changed, we are done searching.
            if nxt_flt == curr_flt:
                # we should have returned True somewhere if we found a default.
                return False

            if nxt_flt in flt_defs:
                # this chain of fallbacks has already been resolved to a
                # a default
                flt_defs.update(memo)
                return True

            curr_flt = nxt_flt

        # if we got here, then we found a default at the current flt.
        # save the results and return True
        flt_defs.update(memo)
        return True


    def _find_circ_fb(flt, memo):
        """
        Tries to find circular fallbacks.
        Assumes that the current flt has not been placed into memo yet.

        IN:
            flt - flt we are checking
            memo - dict of all flts we traversed here

        OUT:
            memo - if False is returned, all keys in this memo are deemed to
                be non-circular fallbacks.

        RETURNS: True if circular fallback is found, False otherwise
        """
        # if we find this in the memo, we have a circular dependcy
        if flt in memo:
            return True

        # otherwise mark that we found this flt
        memo[flt] = True

        # get next flt and check if we are done
        next_flt = _rslv_flt(flt)
        if next_flt == flt:
            FLT_BASE[flt] = True
            return False

        # recursively check flts
        return _find_circ_fb(next_flt, memo)


    def _find_next_fb(flt, memo, ordered_memo):
        """
        Finds next filter and stores in memo and ordered memo

        IN:
            flt - filter to find next filter for

        OUT:
            memo - dict to add the next filter as a key if not None
            ordered memo - list to append the next filter if not None

        RETURNS: the next filter, or None if no next filter.
        """
        nxt_flt = _rslv_flt(flt)
        if nxt_flt != flt:
            memo[nxt_flt] = True
            ordered_memo.append(nxt_flt)

        return nxt_flt


    def _verify_flt_fb():
        """
        Verifies that there are no circular fallbacks in the filter
        fallback dict.

        Raises an error if circular fallbacks are found
        """
        non_cd = {}

        for flt in FLT_FB:
            memo = {}
            if _find_circ_fb(flt, memo):
                raise Exception("filter '{0}' has a circular fallback".format(
                    flt
                ))

            # otherwise good filter fallbac train
            non_cd.update(memo)


    # do verifications
    _verify_flt_fb()
    _verify_fwm_db()


init -1 python in mas_sprites:

    __ignore_filters = True
    # set to prevent additional filters being added when inappropriate


init -99 python in mas_sprites:
    import store
    import store.mas_utils as mas_utils

    FW_ID = 1

    FW_DB = {}
    # internal collection of all MASFitlerWeatherDisplayable flt objects.
    # (basically a dict of MASFilterWeatherMap objects)
    # this is primarily used for verification later.
    # IDs are generic integers.

    # Filtering Framework
    # TODO: consider making the filter dict use Curryables so custom filters
    #   can use non-Matrixcolor-based logic
    #   import renpy.curry.Curry # but do we really need this?

    # filter enums
    FLT_DAY = "day"
    FLT_NIGHT = "night"
    FLT_SUNSET = "sunset"

    # filter dict
    FILTERS = {
        FLT_DAY: store.im.matrix.identity(),
        FLT_NIGHT: store.im.matrix.tint(0.59, 0.49, 0.55),
        FLT_SUNSET: store.im.matrix.tint(0.93, 0.82, 0.78),
    }

    # filter fallback dict
    # key: filter
    # value: filter that should be considered "base" filter
    FLT_FB = {
        FLT_SUNSET: FLT_DAY
    }

    # contains all base filters. These are filtesr without a fallback.
    # this is populated during filter fallback verification and is availabe
    # for use AFTER init level 1.
    # key: filter
    # value: Ignored.
    FLT_BASE = {}

    # should be false until init -1
    __ignore_filters = False

    # global filter variable.
    # NOTE: we keep this out of mas_globals to prevent crashes.
    __flt_global = FLT_DAY


    def add_filter(flt_enum, imx, base=None):
        """
        Adds a filter to the global filters
        You can also use this to override built-in filters.

        NOTE: if you plan to use this, please use it before init level -1
        Filters beyond this level will be ignored.

        NOn-pythonable filter names are ignored

        IN:
            flt_enum - enum key to use as a filter.
            imx - image matrix to use as filter
            base - filter to use as a backup for this filter. Any images
                that are unable to be shown for flt_enum will be revert to
                the base filter.
                This should also be a FLT_ENUM.
                This is checked to make sure it is a valid, preexisting enum,
                so if chaining multiple bases, add them in order.
                If None, no base is given for the flt.
                (Default: None)
        """
        # check init
        if __ignore_filters:
            mas_utils.writelog(
                "[Warning!]: Cannot add filter '{0}' after init -1\n".format(
                    flt_enum
                )
            )
            return

        # check name arg able
        if not _test_filter(flt_enum):
            return

        # check base if given
        if base is not None:
            if base not in FILTERS:
                mas_utils.writelog(
                    (
                        "[Warning!]: Cannot add filter '{0}' with base '{1}', "
                        "base flt not exist\n"
                    ).format(flt_enum, base)
                )
                return

            if not _test_filter(base):
                return

            FLT_FB[flt_enum] = base

        FILTERS[flt_enum] = imx


    def _decide_filter():
        """DEPRECATED
        Please use get_filter
        """
        return get_filter()


    def get_filter():
        """
        Returns the current filter

        RETURNS: filter to use
        """
        return __flt_global


    def is_filter(flt):
        """
        Checks if the given filter is a valid filter

        IN:
            flt - filter enum to check

        RETURNS: True if valid filter, False if not
        """
        return flt in FILTERS


    def _rslv_flt(flt):
        """
        Gets base filter for a flt.

        IN:
            flt - flt to get base filter for

        RETURNS: base flt for flt, or the flt itself if no base
        """
        return FLT_FB.get(flt, flt)


    def set_filter(flt_enum):
        """
        Sets the current filter if it is valid.
        Invalid filters are ignored.

        IN:
            flt_enum - filter to set
        """
        global __flt_global
        if flt_enum in FILTERS:
            __flt_global = flt_enum


    def _test_filter(flt_enum):
        """
        Checks if this filter enum can be a filter enum.

        Logs to mas log if there are errors

        IN:
            flt_enum - filter enum to test

        RETURNS: True if passed test, False if not
        """
        fake_context = {flt_enum: True}
        try:
            eval(flt_enum, fake_context)
            return True
        except:
            mas_utils.writelog(
                (
                    "[Warning!]: Cannot add filter '{0}'. Name is not "
                    "python syntax friendly\n"
                ).format(flt_enum)
            )

        return False


init -98 python:

    # global filter-based functions
    # NOTE: only put the most used filter checks.

    def mas_isCurrentFlt(flt):
        """
        Checks if the given filter is the current filter.

        IN:
            flt - filter to check

        RETURNS: True if flt is the current filter, false if not
        """
        return store.mas_sprites.get_filter() == flt


# this should be after sprite-chart's initialization
init -4 python in mas_sprites:
    # NOTE: render_key

    # Y_OFFSET = -130

    # cache ids
    CID_FACE = 1 # NOTE: we should not use highlights for this
    CID_ARMS = 2
    CID_BODY = 3
    CID_HAIR = 4
    CID_ACS = 5
    CID_TC = 6
    CID_HL = 7
    CID_HLG = 8
    CID_BG = 9 # TODO: maybe

    # several caches for images

    CACHE_TABLE = {
        CID_FACE: {},
        # the facial expression cache. Facial expressions are the most likely
        # things to overlap across clothing, hair, and ACS, so we should cache
        # them together to maximize performance
        # key:
        #   tuple containing all sprite strings that may be used. None is fine
        #   here.
        #   [0] - should be the filter code.
        #   [1] - should be pre/post (0 or 1)
        #   [2] - type of lean
        #   [3+] remaining values dependent on type:
        #       * pre - only blush
        #       * post - all values except blush
        # value:
        #   image manip containing render, or None if should not be rendered

        CID_ARMS: {},
        # the arms cache. This includes clothes and base sprites.
        # key:
        #   tuple containing strings.
        #   [0] - filter code
        #   [1] - base code
        #   [2] - clothing type, "base" for base arms
        #   [3] - leanpose
        # value:
        #   image manip containing render, or None if should not be rendered

        CID_BODY: {},
        # the body cache. This includes clothes and base sprites.
        # key:
        #   tuple containing strings.
        #   [0] - should be the filter code.
        #   [1] - shoud be image path
        # value:
        #   image manip containing render, or None if should not be rendered

        CID_HAIR: {},
        # the hair cache
        # key:
        #   tuple containing strings.
        #   [0] - should be the filter code.
        #   [1] - should be image path
        # value:
        #   image manip containing render, or None if should not be rendered

        CID_ACS: {},
        # the ACS cache
        # key:
        #   tuple containing strings.
        #   [0] - should be the filter code.
        #   [1] - acs name (id)
        #   [3] - poseid
        #   [4] - arm code
        # value:
        #   image manip containing render, or None if should not be rendered

        CID_TC: {},
        # the tablechair cache
        # key:
        #   tuple containing strings
        #   [0] - should be the filter code
        #   [1] - should be either table/chair (0, 1)
        #   [2] - table/chair type
        #   [3] - 0 for no shadow, 1 for shadow (ignored for chairs)
        # value:
        #   image manip containing render, or None if should not be rendered

        CID_HL: {},
        # the highlight cache
        # key:
        #   tuple containing:
        #   [0] - cache ID - determines what sprite this highlight is for
        #   [1+] - the sprite's key
        # value:
        #   Image object, or None if should not be rendered

        CID_HLG: {}
        # the global highlight cache
        # this should be used for anything that is not part of Monika sprite
        # rendering system.
        # key:
        #   tuple containig:
        #   [0] - filter
        #   [1] - image path
        # value:
        #   Image object, or None if should not be rendered
    }

    MFM_CACHE = {}
    # MASFilterMap cache
    # key: hash value of a MASFilterMAp
    # value: MASFilterMap for a hash value


    def _clear_caches():
        """
        Clears all caches
        """
        for cid, cache in CACHE_TABLE.iteritems():
            for key in cache.keys():
                cache.pop(key)

        for key in MFM_CACHE.keys():
            MFM_CACHE.pop(key)


    class MASMonikaRender(store.MASFilterable):
        """
        custom rendering class for MASMonika. This does caching and rendering
        at the same time.

        INHERED PROPS:
            flt - filter we are using (string)

        PROPERTIES:
            render_keys - list of tuples of the following format:
                [0] - key of an image to generate. used to check cache
                [1] - cache ID of the cache to use
                [2] - ImageBase to build the image, IF NOT IN CACHE.
                    This should be set to None if we are sure a surf
                    object is in the cache.
                [3] - ImageBase to build the highlight. Set to None if no
                    no highlight or in cache.
            xpos - xposition to blit objects with
            ypos - yposition to blit objects with
            width - width to render objects with
            height - height to render objects with
        """

        def __init__(self, render_keys, flt, xpos, ypos, width, height):
            """
            Constructor for a MASMOnikaRender object

            IN:
                render_keys - image keys and ImageBase if needed.
                    See props.
                flt - filter we are using (string)
                xpos - xposition to blit objects with
                ypos - yposition to blit objects with
                width - width to render objects with
                height - height to render objects with
            """
            super(store.MASFilterable, self).__init__()
            self.render_keys = render_keys
            self.xpos = xpos
            self.ypos = ypos
            self.width = width
            self.height = height
            self.flt = flt

        def _l_render_hl(self, render_list, render_key, st, at):
            """
            Retrieves highlight image from cache, or renders if needed

            IN:
                render_key - tuple of the following format
                    [0] - key of image to generate
                    [1] - cache ID of the cache to use
                    [2] - ImageBase to build the image
                    [3] - ImageBase to build the highlight
                st - renpy related
                at - renpy related

            OUT:
                render_list - list to add render to, if needed
            """
            # NOTE: face will never have highlight (for now)
            if render_key[1] == store.mas_sprites.CID_FACE:
                return None

            # add cache id to front for highlight key
            hl_key = (render_key[1],) + render_key[0]

            # check highlight cache
            img_base = store.mas_sprites._cs_im(
                hl_key,
                store.mas_sprites.CID_HL,
                render_key[3]
            )

            if img_base is not None:
                render_list.append(renpy.render(
                    img_base,
                    self.width,
                    self.height,
                    st, at
                ))


        def _render_surf(self, render_key, st, at):
            """
            Retrieves surf image from cache, or renders if needed

            IN:
                render_key - tuple of the following format:
                    [0] - key of image to generate
                    [1] - cache ID of the cache to use
                    [2] - ImageBase to build the image
                    [3] - ImageBase to build the highlight
                st - renpy related
                at - renpy related

            RETURNS: rendered surf image to use
            """
            # render this bitch
            new_surf = renpy.render(
                store.mas_sprites._cgen_im(
                    self.flt,
                    render_key[0],
                    render_key[1],
                    render_key[2]
                ),
                self.width,
                self.height,
                st, at
            )

            #new_surf = renpy.display.im.load_surface(
            #    store.mas_sprites._gen_im(self.flt, img_base)
            #)
            return new_surf

        def render(self, width, height, st, at):
            """
            Render function
            """
            self.flt = store.mas_sprites.get_filter()

            renders = []
            for render_key in self.render_keys:
                renders.append(self._render_surf(render_key, st, at))
                self._l_render_hl(renders, render_key, st, at)

            # blit all
            rv = renpy.Render(self.width, self.height)
            for render in renders:
                rv.blit(render, (self.xpos, self.ypos))

            return rv


        def visit(self):
            """
            Returns a list of displayables we obtain
            NOTE: will also save to our cache
            """
            self.flt = store.mas_sprites.get_filter()
            disp_list = []
            for render_key in self.render_keys:
                store.mas_sprites._cgha_im(disp_list, self.flt, render_key)

            return disp_list


    def _add_arms_rk(
            rk_list,
            arms,
            pfx,
            flt,
            bcode,
            clothing_t,
            leanpose
    ):
        """
        Adds render key for multiple MASArm objects, if needed

        IN:
            arms - MASArm objects to add render key for
            pfx - prefix tuple to generate image string with
            flt - filter code to use
            bcode - base code to use
            clothing_t - type of clothing to use
            leanpose - leanpose to use

        OUT:
            rk_list - render key list to add render keys to
        """
        # check cache
        img_key = (flt, bcode, clothing_t, leanpose)
        cache_arms = _gc(CID_ARMS)
        day_key = None
        if img_key in cache_arms:
            if cache_arms[img_key] is not None:
                rk_list.append((img_key, CID_ARMS, None, None))

            return

        elif flt != FLT_DAY:
            # try checking if day version is None
            day_key = _dayify(img_key)
            if cache_arms.get(day_key, True) is None:
                # no image for this key, let the main key know
                cache_arms[img_key] = None
                return

        # check if arm actually exist
        if arms is None:
            # no arms to render
            cache_arms[img_key] = None
            cache_arms[day_key] = None
            return

        # filter for arms that exist at thies layer code
        arm_data = []
        for arm in arms:
            tag_list = arm.get(bcode)
            if len(tag_list) > 0:
                arm_data.append((arm, tag_list))

        # check if arm at layer exist
        if len(arm_data) == 0:
            # no arms to render
            cache_arms[img_key] = None
            cache_arms[day_key] = None
            return

        # if only 1 item , then dont need to composite
        if len(arm_data) < 2:
            arm, tag_list = arm_data[0]
            img_list = pfx + tag_list + [FILE_EXT]

            # create render key
            rk_list.append((
                img_key,
                CID_ARMS,
                store.Image("".join(img_list)),
                _bhli(img_list, arm.gethlc(bcode, flt))
            ))
            return

        # more than 1 item, need to composite
        arm_comp_args = [LOC_WH]
        hl_comp_args = [LOC_WH]

        for arm, tag_list in arm_data:
            img_list = pfx + tag_list
            arm_comp_args.append((0, 0))
            arm_comp_args.append("".join(img_list + [FILE_EXT]))

            # check for hl
            hlc = arm.gethlc(bcode, flt)
            if hlc is not None:
                hl_comp_args.append((0, 0))
                hl_comp_args.append("".join(
                    img_list + [
                        HLITE_SUFFIX,
                        hlc,
                        FILE_EXT
                    ]
                ))

        # now generate composites
        img_comp = store.im.Composite(*arm_comp_args)
        if len(hl_comp_args) > 1:
            hl_comp = store.im.Composite(*hl_comp_args)
        else:
            hl_comp = None

        # and add results
        rk_list.append((img_key, CID_ARMS, img_comp, hl_comp))


    def _bhli(img_list, hlcode):
        """
        Builds a
        High-
        Light
        Image using the base image path

        IN:
            img_list - list of strings that form the base image string
                NOTE: we assume that the last item in this string is the
                FILE_EXT. This also assumes highlight codes are always inserted
                right before the file extension.
            hlcode - highlight code to use. Can be None.

        RETURNS: Image to use for highlight, or None if no highlight.
        """
        if hlcode is None:
            return None

        # otherwise list copy and splice
        hl_list = list(img_list)
        hl_list[-1:-1] = [HLITE_SUFFIX, hlcode]
        return store.Image("".join(hl_list))


    def _bhlifp(img_path, hlcode):
        """
        Builds a
        High-
        Light
        Image using an image's
        File
        Path

        IN:
            img_path - full filepath to an image, including extension.
            hlcode - highlight code to use. Can be None

        RETURNS: Image to use for highlight, or None if no highlight
        """
        if hlcode is None:
            return None

        # otherwise partition and build
        pre_img, ext, ignore = img_path.partition(FILE_EXT)
        return store.Image("".join((pre_img, HLITE_SUFFIX, hlcode, ext)))


    def _cgen_im(flt, key, cid, img_base):
        """
        Checks cache for an im,
        GENerates the im if not found

        IN:
            flt - filter to use
            key - key of the image
            cid - cache ID of the cache to use
            img_base - ImageBase to build the image

        RETURNS: Image Manipulator for this render
        """
        img_cache = _gc(cid)
        if key in img_cache:
            return img_cache[key]

        # generate the im and cache it
        new_im = _gen_im(flt, img_base)
        img_cache[key] = new_im
        return new_im


    def _cgha_im(render_list, flt, render_key):
        """
        Checks cache of an image
        Generates the im if not found, and sets
        Highlight if needed.
        Adds IMs to the given render list

        NOTE: should only be used by the visit function

        IN:
            flt - filter to use
            render_key - tuple of the following format:
                [0] - key of the image to generate
                [1] - cache ID of the cahce to use
                [2] - ImageBase to build the image
                [3] - ImageBase to build the highlight
            st - renpy related
            at - renpy related

        OUT:
            render_list - list to add IMs to
        """
        img_key, cid, img_base, hl_base = render_key
        img_cache = _gc(cid)
        hl_key = _hlify(img_key, cid)
        if img_key in img_cache:
            render_list.append(img_base)

            # check for highlight
            # NOTE: if the img key exists in the cache, then we know for sure
            #   that the highlight must be in the cache already
            hl_base = _gc(CID_HL).get(hl_key, None)
            if hl_base is not None:
                render_list.append(hl_base)
            return

        # otherwise, we need to generate the im (and maybe hl) and cache it
        new_im = _gen_im(flt, img_base)
        img_cache[img_key] = new_im
        render_list.append(new_im)

        # check for highlight
        _gc(CID_HL)[hl_key] = hl_base
        if hl_base is not None:
            render_list.append(hl_base)


    def _cs_im(key, cid, img_base):
        """
        Checks cache for an im
        Stores the img_base if not found

        IN:
            key - key of the image
            cid - cache ID of the cache to use
            img_base - ImageBase to build the image

        RETURNS: ImageBase
        """
        img_cache = _gc(cid)
        if key in img_cache:
            return img_cache[key]

        # store then return
        img_cache[key] = img_base
        return img_base


    def _dayify(img_key):
        """
        Dayifies the given image key.
        DAying simply replaces the filter portion of the key with "day"

        IN:
            img_key - image key to dayify

        RETURNS: dayified key
        """
        img_key_list = list(img_key)
        img_key_list[0] = FLT_DAY
        return tuple(img_key_list)


    def _gc(cid):
        """
        Gets the
        Cache

        IN:
            cid - cache ID of the cache to get

        RETURNS: cache, or empty dict if cache not found
        """
        return CACHE_TABLE.get(cid, {})


    def _gen_im(flt, img_base):
        """
        GENerates an image maniuplator
        NOTE: always assumes we have an available filter.

        IN:
            flt - filter to use
            img_base - image path or manipulator to use

        RETURNS: generated render key
        """
        # NOTE: no render
        return store.im.MatrixColor(img_base, FILTERS[flt])


    def _hlify(key, cid):
        """
        Highlightifies the given key.
        Highlightifying is just prefixing the key with the cid

        IN:
            key - key to highlightify
            cid - cid to use when highlighting

        RETURNS: highlightified key
        """
        return (cid,) + key


    # rk-based sprite maker functions
    def _rk_accessory(
            rk_list,
            acs,
            flt,
            arm_split,
            leanpose=None
    ):
        """
        Adds accessory render key if needed

        IN:
            acs - MASAccessory object
            flt - filter to apply
            arm_split - see MASAccessory.arm_split for codes. None for no
                codes at all.
            leanpose - current pose
                (Default: None)

        OUT:
            rk_list - list to add render keys to
        """
        # pose map check
        # Since None means we dont show, we are going to assume that the
        # accessory should not be shown if the pose key is missing.
        poseid = acs.pose_map.get(leanpose, None)

        # get arm code if needed
        # NOTE: we can be sure that a nonsplit acs will not be used in
        #   a split context.
        if arm_split is None:
            arm_code = ""

        elif arm_split in acs.get_arm_split_code(leanpose):
            arm_code = ART_DLM + arm_split

        else:
            # we should not render
            arm_code = None

        # now we can generate the key and check cache
        img_key = (flt, acs.name, poseid, arm_code)
        cache_acs = _gc(CID_ACS)
        day_key = None
        if img_key in cache_acs:
            if cache_acs[img_key] is not None:
                rk_list.append((img_key, CID_ACS, None, None))

            return

        elif flt != FLT_DAY:
            # check of day version is none
            day_key = _dayify(img_key)
            if cache_acs.get(day_key, True) is None:
                # no image for this key, let main key know
                cache_acs[img_key] = None
                return

        # now check other acs-related elements that may stop render
        if poseid is None or arm_code is None:
            # a None here means we should shouldnt' even show this acs
            # for this pose. Weird, but maybe it happens?
            cache_acs[img_key] = None
            cache_acs[day_key] = None
            return

        # build img list minus file extensions
        img_list = [
            A_T_MAIN,
            PREFIX_ACS,
            acs.img_sit,
            ART_DLM,
            poseid,
            arm_code,
            FILE_EXT,
        ]

        # finally add the render key
        rk_list.append((
            img_key,
            CID_ACS,
            store.Image("".join(img_list)),
            _bhli(img_list, acs.opt_gethlc(poseid, flt, arm_split))
        ))


    def _rk_accessory_list(
            rk_list,
            acs_list,
            flt,
            leanpose=None,
            arm_split=None
    ):
        """
        Adds accessory render keys for a list of accessories

        IN:
            acs_list - list of MASAccessory objects, in order of rendering
            flt - filter to use
            arm_split - set to MASAccessory.arm_split code if we are rendering
                arm_split-affected ACS. If None, we use standard algs.
                (Default: None)
            leanpose - arms pose for we are currently rendering
                (Default: None)

        OUT:
            rk_list - list to add render keys to
        """
        if len(acs_list) == 0:
            return

        for acs in acs_list:
            _rk_accessory(
                rk_list,
                acs,
                flt,
                arm_split,
                leanpose
            )


    def _rk_arms_base_nh(rk_list, barms, leanpose, flt, bcode):
        """
        Adds arms base render keys
        (equiv to _ms_arms_nh_up_base)

        IN:
            barms - tuple of MASArm objects to use
            leanpose - leanpose to use
            flt - filter to use
            bcode - base code to use

        OUT:
            rk_list - list to add render keys to
        """
        _add_arms_rk(
            rk_list,
            barms,
            [
                B_MAIN,
                PREFIX_ARMS,
            ],
            flt,
            bcode,
            "base",
            leanpose
        )


    def _rk_arms_base_lean_nh(rk_list, barms, lean, leanpose, flt, bcode):
        """
        Adds arms base lean render key
        (eqiv to _ms_arms_nh_leaning_base)

        IN:
            barms - tuple of MASArm objects to use
            lean - type of lean
            leanpose - leanpose to use
            flt - filter to use
            bcode - base code to use

        OUT:
            rk_list - list to add render keys to
        """
        _add_arms_rk(
            rk_list,
            barms,
            [
                B_MAIN,
                PREFIX_ARMS_LEAN,
                lean,
                ART_DLM,
            ],
            flt,
            bcode,
            "base",
            leanpose
        )


    def _rk_arms_nh(rk_list, parms, clothing, leanpose, flt, bcode):
        """
        Adds arms render key
        (equiv to _ms_arms_nh_up_arms)

        IN:
            parms - tuple of MASArm objects to use
            clothing - MASClothes object
            leanpose - leanpose to use
            flt - filter to use
            bcode - base code to use

        OUT:
            rk_list - list to add render keys to
        """
        _add_arms_rk(
            rk_list,
            parms,
            [
                C_MAIN,
                clothing.img_sit,
                "/",
                PREFIX_ARMS,
            ],
            flt,
            bcode,
            clothing.img_sit,
            leanpose
        )


    def _rk_arms_lean_nh(rk_list, parms, clothing, lean, leanpose, flt, bcode):
        """
        Adds arms lean render key
        (equiv to _ms_arms_nh_leaning_arms)

        IN:
            parms - tuple of MASArm objects to use
            clothing - MASClothes object
            lean - type of lean
            leanpose - leanpose to use
            flt - filter to use
            bcode - base code to use

        OUT:
            rk_list - list to add render keys to
        """
        _add_arms_rk(
            rk_list,
            parms,
            [
                C_MAIN,
                clothing.img_sit,
                "/",
                PREFIX_ARMS_LEAN,
                lean,
                ART_DLM,
            ],
            flt,
            bcode,
            clothing.img_sit,
            leanpose
        )


    def _rk_arms_nh_wbase(
            rk_list,
            barms,
            parms,
            clothing,
            acs_ase_list,
            leanpose,
            lean,
            flt,
            bcode
    ):
        """
        Adds arms render keys, no hair, with baes

        IN:
            barms - tuple of MASArm objects for base
            parms - tuple of MASArm objects for pose
            clothing - MASClothes object
            acs_ase_list - acs between arms-base-0 and arms-0
            leanpose - leanpose to pass to accessorylist
            lean - lean to use
            flt - filter to use
            bcode - base code to use

        OUT:
            rk_list - list to add render keys to
        """
        if lean:
            # arms-base-0
            _rk_arms_base_lean_nh(rk_list, barms, lean, leanpose, flt, bcode)

            # acs-ase
            _rk_accessory_list(rk_list, acs_ase_list, flt, leanpose, bcode)

            if parms is not None:
                # arms-0
                _rk_arms_lean_nh(
                    rk_list,
                    parms,
                    clothing,
                    lean,
                    leanpose,
                    flt,
                    bcode
                )

        else:
            # arms-base-0
            _rk_arms_base_nh(rk_list, barms, leanpose, flt, bcode)

            # acs-ase
            _rk_accessory_list(rk_list, acs_ase_list, flt, leanpose, bcode)

            if parms is not None:
                # arms-0
                _rk_arms_nh(rk_list, parms, clothing, leanpose, flt, bcode)


    def _rk_base_body_nh(rk_list, flt, bcode):
        """
        Adds base body render keys, no hair
        (equiv of _ms_torso_nh_base)

        IN:
            flt - filter ot use
            bcode- base code to use

        OUT:
            rk_list - list to add render keys to
        """
        img_str = "".join((
            B_MAIN,
            BASE_BODY_STR,
            bcode,
            FILE_EXT,
        ))

        # cache check
        img_key = (flt, img_str)
        if img_key in _gc(CID_BODY):
            rk_list.append((img_key, CID_BODY, None, None))
            return

        rk_list.append((img_key, CID_BODY, store.Image(img_str), None))


    def _rk_base_body_lean_nh(rk_list, lean, flt, bcode):
        """
        Adds base body lean render keys, no hair
        (equivalent of _ms_torsoleaning_nh_base)

        IN:
            lean - type of lean
            flt - filter to use
            bcode - base code to use

        OUT:
            rk_list - list to add render keys to
        """
        img_str = "".join((
            B_MAIN,
            PREFIX_BODY_LEAN,
            lean,
            ART_DLM,
            bcode,
            FILE_EXT,
        ))

        # cache check
        img_key = (flt, img_str)
        if img_key in _gc(CID_BODY):
            rk_list.append((img_key, CID_BODY, None, None))
            return

        rk_list.append((img_key, CID_BODY, store.Image(img_str), None))


    def _rk_body_nh(rk_list, clothing, flt, bcode):
        """
        Adds body render keys, no hair
        (equiv of _ms_torso_nh)

        IN:
            clothing - MASClothes object
            flt - filter to use
            bcode - base code to use

        OUT:
            rk_list - list to add render keys to
        """
        img_list = (
            C_MAIN,
            clothing.img_sit,
            "/",
            NEW_BODY_STR,
            ART_DLM,
            bcode,
            FILE_EXT,
        )
        img_str = "".join(img_list)

        # cache check
        img_key = (flt, img_str)
        if img_key in _gc(CID_BODY):
            rk_list.append((img_key, CID_BODY, None, None))
            return

        # otherwise build ImageBase
        rk_list.append((
            img_key,
            CID_BODY,
            store.Image(img_str),
            _bhli(img_list, clothing.gethlc(bcode, None, flt)),
        ))


    def _rk_body_lean_nh(rk_list, clothing, lean, flt, bcode):
        """
        Adds body leaning render keys, no hair
        (equiv of _ms_torsoleaning_nh)

        IN:
            clothing - MASClothes object
            lean - type of lean
            flt - filter to use
            bcode - base code to use

        OUT:
            rk_list - list to add render keys to
        """
        # build img str
        img_list = (
            C_MAIN,
            clothing.img_sit,
            "/",
            PREFIX_BODY_LEAN,
            lean,
            ART_DLM,
            bcode,
            FILE_EXT,
        )
        img_str = "".join(img_list)

        # key check
        img_key = (flt, img_str)
        cache_body = _gc(CID_BODY)
        if img_key in cache_body:
            rk_list.append((img_key, CID_BODY, None, None))
            return

        # otherwise need to build ImageBase
        rk_list.append((
            img_key,
            CID_BODY,
            store.Image(img_str),
            _bhli(img_list, clothing.gethlc(bcode, lean, flt))
        ))


    def _rk_body_nh_wbase(
            rk_list,
            clothing,
            acs_bse_list,
            bcode,
            flt,
            leanpose,
            lean=None
    ):
        """
        Adds body render keys, including base and bse acs, no hair

        IN:
            clothing - MASClothes object
            acs_bse_list - acs between base-0 and body-0
            bcode - base code to use
            flt - filter to use
            leanpose - leanpose to pass to accessorylist
            lean - type of lean

        OUT:
            rk_list - list to add render keys to
        """
        if lean:
            # base-0
            _rk_base_body_lean_nh(rk_list, lean, flt, bcode)

            # acs_bse
            _rk_accessory_list(rk_list, acs_bse_list, flt, leanpose, bcode)

            # body-0
            _rk_body_lean_nh(rk_list, clothing, lean, flt, bcode)

        else:
            # base-0
            _rk_base_body_nh(rk_list, flt, bcode)

            # acs_bse
            _rk_accessory_list(rk_list, acs_bse_list, flt, leanpose, bcode)

            # body-0
            _rk_body_nh(rk_list, clothing, flt, bcode)


    def _rk_chair(rk_list, mtc, flt):
        """
        Adds chair render key

        IN:
            mtc - MASTableChair object
            flt - filter to use

        OUT:
            rk_list - list to add render keys to
        """
        # check cache
        img_key = (flt, 1, mtc.chair)
        cache_tc = _gc(CID_TC)
        if img_key in cache_tc:
            rk_list.append((img_key, CID_TC, None, None))
            return

        # otherwise build it
        img_list = (
            T_MAIN,
            PREFIX_CHAIR,
            mtc.chair,
            FILE_EXT,
        )
        img_str = "".join(img_list)

        rk_list.append((
            img_key,
            CID_TC,
            store.Image(img_str),
            _bhli(
                img_list,
                store.MASHighlightMap.o_fltget(mtc.hl_map, "c", flt)
            )
        ))


    def _rk_face(
            rk_list,
            eyes,
            eyebrows,
            nose,
            mouth,
            flt,
            fpfx,
            lean,
            sweat,
            tears,
            emote
        ):
        """
        Adds face render keys

        IN:
            eyes - type of eyes
            eyebrows - type of eyebrows
            nose - type of nose
            mouth - type of mouth
            flt - filter to use
            fpfx - face prefix to use
            lean - type of lean to use
            sweat - type of sweat drop
            tears - type of tears
            emote - type of emote

        OUT:
            rk_list - list to add render keys to
        """
        img_key = (
            flt,
            1,
            lean,
            eyes,
            eyebrows,
            nose,
            mouth,
            sweat,
            tears,
            emote
        )
        day_key = None
        cache_face = _gc(CID_FACE)
        if img_key in cache_face:
            if cache_face[img_key] is not None:
                rk_list.append((img_key, CID_FACE, None, None))
            return

        elif flt != FLT_DAY:
            # try using day key
            day_key = _dayify(img_key)
            if cache_face.get(day_key, True) is None:
                # no image for this key, let main key know
                cache_face[img_key] = None
                return

        # othewise need to generate

        # we will always have at least four images to composite
        img_str_list = [
            (0, 0),
            "".join((
                F_T_MAIN,
                fpfx,
                PREFIX_EYES,
                eyes,
                FILE_EXT,
            )),
            (0, 0),
            "".join((
                F_T_MAIN,
                fpfx,
                PREFIX_EYEB,
                eyebrows,
                FILE_EXT,
            )),
            (0, 0),
            "".join((
                F_T_MAIN,
                fpfx,
                PREFIX_NOSE,
                nose,
                FILE_EXT,
            )),
            (0, 0),
            "".join((
                F_T_MAIN,
                fpfx,
                PREFIX_MOUTH,
                mouth,
                FILE_EXT,
            )),
        ]

        # check for others
        if sweat:
            img_str_list.extend((
                (0,0),
                "".join((
                    F_T_MAIN,
                    fpfx,
                    PREFIX_SWEAT,
                    sweat,
                    FILE_EXT,
                ))
            ))

        if tears:
            img_str_list.extend((
                (0, 0),
                "".join((
                    F_T_MAIN,
                    fpfx,
                    PREFIX_TEARS,
                    tears,
                    FILE_EXT,
                ))
            ))

        if emote:
            img_str_list.extend((
                (0, 0),
                "".join((
                    F_T_MAIN,
                    fpfx,
                    PREFIX_EMOTE,
                    emote,
                    FILE_EXT,
                ))
            ))

        # generate imComposite
        rk_list.append((
            img_key,
            CID_FACE,
            store.im.Composite((1280, 850), *img_str_list),
            None
        ))


    def _rk_face_pre(rk_list, flt, fpfx, lean, blush):
        """
        Adds face render keys that go before hair

        IN:
            flt - filter to use
            fpfx - face prefix to use
            lean - type of lean to use
            blush - type of blush

        OUT:
            rk_list - list to add render keys to
        """
        img_key = (flt, 0, lean, blush)
        day_key = None
        cache_face = _gc(CID_FACE)
        if img_key in cache_face:
            if cache_face[img_key] is not None:
                rk_list.append((img_key, CID_FACE, None, None))

            return

        elif flt != FLT_DAY:
            # try checking for day version
            day_key = _dayify(img_key)
            if cache_face.get(day_key, True) is None:
                # no image for this key, let the main key know
                cache_face[img_key] = None
                return

        # NOTE: since theres only 1 thing here, we wont do anything fancy

        # otherwise, time to generate the im
        if blush:
            rk_list.append((
                img_key,
                CID_FACE,
                store.Image("".join((
                    F_T_MAIN,
                    fpfx,
                    PREFIX_BLUSH,
                    blush,
                    FILE_EXT
                ))),
                None,
            ))
            return

        # otherwise nothing here
        cache_face[img_key] = None
        cache_face[day_key] = None


    def _rk_hair(rk_list, hair, flt, hair_key, lean, leanpose):
        """
        Adds hair render key

        IN:
            hair - MASHair object
            flt - filter to use
            hair_key - hair key to use (front/back/mid)
            lean - tyoe of lean
            leanpose - leanpose

        OUT:
            rk_list - list to add render keys to
        """
        # build img str
        if lean:
            img_list = (
                H_MAIN,
                PREFIX_HAIR_LEAN,
                lean,
                ART_DLM,
                hair.img_sit,
                ART_DLM,
                hair_key,
                FILE_EXT,
            )

        else:
            img_list = (
                H_MAIN,
                PREFIX_HAIR,
                hair.img_sit,
                ART_DLM,
                hair_key,
                FILE_EXT,
            )

        # genreate string for key check
        img_str = "".join(img_list)

        # key check
        img_key = (flt, img_str)
        cache_hair = _gc(CID_HAIR)
        if img_key in cache_hair:
            if cache_hair[img_key] is not None:
                rk_list.append((img_key, CID_HAIR, None, None))
            return

        # check if mid and no need to render
        if hair_key == MHAIR:
            if hair.mpm_mid is None or not hair.mpm_mid.get(leanpose, False):
                # mid not in this hair for this pose
                cache_hair[img_key] = None
                return

        # otherwise need to build ImageBase
        rk_list.append((
            img_key,
            CID_HAIR,
            store.Image(img_str),
            _bhli(img_list, hair.gethlc(hair_key, lean, flt)),
        ))


    def _rk_head(rk_list, flt, lean):
        """
        Adds head render keys.

        IN:
            bcode - base code to use
            flt - filter to use
            lean - type of lean

        OUT:
            rk_list - list to add render keys to
        """
        if lean:
            img_str = "".join((
                B_MAIN,
                PREFIX_BODY_LEAN,
                lean,
                ART_DLM,
                HEAD,
                FILE_EXT,
            ))

        else:
            img_str = "".join((
                B_MAIN,
                BASE_BODY_STR,
                HEAD,
                FILE_EXT
            ))

        # cache check
        img_key = (flt, img_str)
        if img_key in _gc(CID_BODY):
            rk_list.append((img_key, CID_BODY, None, None))
            return

        rk_list.append((img_key, CID_BODY, store.Image(img_str), None))


    def _rk_table(rk_list, tablechair, show_shadow, flt):
        """
        Adds table render key

        IN:
            table - MASTableChair object
            show_shadow - True if shadow should be included, false if not
            flt filter to use

        OUT:
            rk_list - list to add render keys to
        """
        img_key = (flt, 0, tablechair.table, int(show_shadow))
        if img_key in _gc(CID_TC):
            rk_list.append((img_key, CID_TC, None, None))
            return

        # otherwise, we need to create the table sprite
        table_list = (
            T_MAIN,
            PREFIX_TABLE,
            tablechair.table,
            FILE_EXT,
        )

        # highlight is determined by shadow
        if show_shadow:

            # need to make shadow
            shdw_list = (
                T_MAIN,
                PREFIX_TABLE,
                tablechair.table,
                SHADOW_SUFFIX,
                FILE_EXT,
            )
            shdw_str = "".join(shdw_list)

            # determine highlight
            hl_img = _bhli(
                shdw_list,
                store.MASHighlightMap.o_fltget(tablechair.hl_map, "ts", flt)
            )

            if hl_img is None:
                # no need to composite
                hl_img = store.Image(shdw_str)

            else:
                # need to composite
                hl_img = store.im.Composite(
                    (1280, 850),
                    (0, 0), shdw_str,
                    (0, 0), hl_img
                )

        else:
            # determine highlight
            hl_img = _bhli(
                table_list,
                store.MASHighlightMap.o_fltget(tablechair.hl_map, "t", flt)
            )

        # add to list
        rk_list.append((
            img_key,
            CID_TC,
            store.Image("".join(table_list)),
            hl_img
        ))


# main sprite compilation

    def _rk_sitting(
            clothing,
            hair,
            base_arms,
            pose_arms,
            eyebrows,
            eyes,
            nose,
            mouth,
            flt,
            acs_pre_list,
            acs_bbh_list,
            acs_bse_list,
            acs_bba_list,
            acs_ase_list,
            acs_bmh_list,
            acs_mhh_list,
            acs_bat_list,
            acs_mat_list,
            acs_mab_list,
            acs_bfh_list,
            acs_afh_list,
            acs_mid_list,
            acs_pst_list,
            leanpose,
            lean,
            arms,
            eyebags,
            sweat,
            blush,
            tears,
            emote,
            tablechair,
            show_shadow
    ):
        """
        Creates a list of render keys in order of desired render.

        IN:
            clothing - MASClothes object
            hair - MASHair object
            base_arms - tuple of MASArm objects to use for the base
            pose_arms - tuple of MASArm objects to use for the clothes arms
            eyebrows - type of eyebrows
            eyes - type of eyes
            nose - type of nose
            mouth - type of mouth
            flt - filter to use
            acs_pre_list - sorted list of MASAccessories to draw prior to body
            acs_bbh_list - sroted list of MASAccessories to draw between back
                hair and body
            acs_bse_list - sorted list of MASAccessories to draw between base
                body and outfit
            acs_bba_list - sorted list of MASAccessories to draw between
                body and back arms
            acs_ase_list - sorted list of MASAccessories to draw between base
                arms and outfit
            acs_bmh_list - sorted list of MASAccessories to draw betrween back
                arms and mid hair
            acs_mmh_list - sorted list of MASAccessories to draw between mid
                hair and head
            acs_bat_list - sorted list of MASAccessories to draw before table
            acs_mat_list - sorted list of MASAccessories to draw between
                middle arms and table
            acs_mab_list - sorted list of MASAccessories to draw between
                middle arms and boobs
            acs_bfh_list - sorted list of MASAccessories to draw between boobs
                and front hair
            acs_afh_list - sorted list of MASAccessories to draw between front
                hair and face
            acs_mid_list - sorted list of MASAccessories to draw between body
                and arms
            acs_pst_list - sorted list of MASAccessories to draw after arms
            leanpose - lean and arms together
            lean - type of lean
            arms - type of arms
            eyebags - type of eyebags
            sweat - type of sweatdrop
            blush - type of blush
            tears - type of tears
            emote - type of emote
            tablechair - MASTableChair object
            show_shadow - True will show shadow, false will not

        RETURNS: list of render keys
        """
        # NOTE: render order
        #   1. pre-acs - every acs that should render before anything
        #   2. back-hair - back portion of hair (split mode)
        #   3. bbh-acs - acs between Body and Back Hair
        #   4. chair - chair sprite
        #   5. base-0 - the base back part of body
        #   6. bse-acs - between base and body-0
        #   7. body-0 - the back part of body (no arms in split mode)
        #   8. bba-acs - acs between Body and Back Arms
        #   9. arms-base-0 - the base back part of arm
        #   10. ase-acs-0 - between base arms and clothes, back part
        #   11. arms-0 - the back part of arms
        #   12. bmh-acs - acs between the Back Arms and Mid hair
        #   13. mid-hair - mid portion of hair, behind head and above body
        #   14. mhh-acs - acs between Mid Hair and Head
        #   15. body-head - the head + ears
        #   16. bat-acs - acs Before Table
        #   17. table - the table/desk
        #   18. mat-acs acs between Middle Arms and Table
        #   19. arms-base-5 - the base middle part of arm
        #   20. ase-acs-5 - between base arms and clothes, middle part
        #   21. arms-5 - the middle part of arms
        #   22. mab-acs - acs between Middle Arms and Body-1
        #   23. base-1 - the base front part of body
        #   24. bse-acs - between base and body-1
        #   25. body-1 - the front part of body (boobs)
        #   26. bfh-acs - acs between Body and Front Hair
        #   27. face-pre - pre front hair facial expressions
        #   28. front-hair - front portion of hair (split mode)
        #   29. afh-acs - acs betweem Arms and Front Hair
        #   30. face - facial expressions
        #   31. mid-acs - acs between face and front arms
        #   32. arms-base-10 - the base front part of arms
        #   33. ase-acs-10 - between base arms and clothes, front part
        #   34. arms-10 - front arms
        #   35. pst-acs - acs after everything

        # initial values
        fpfx = face_lean_mode(lean)
        rk_list = []

        # 1. pre-acs
        _rk_accessory_list(rk_list, acs_pre_list, flt, leanpose)

        # 2. back hair
        _rk_hair(rk_list, hair, flt, BHAIR, lean, leanpose)

        # 3. bbh-acs
        _rk_accessory_list(rk_list, acs_bbh_list, flt, leanpose)

        # 4. chair
        _rk_chair(rk_list, tablechair, flt)

        # 5. base-0
        # 6. bse-acs-0
        # 7. body-0
        _rk_body_nh_wbase(
            rk_list,
            clothing,
            acs_bse_list,
            "0",
            flt,
            leanpose,
            lean=lean
        )

        # 8. bba-acs
        _rk_accessory_list(rk_list, acs_bba_list, flt, leanpose)

        # 9. arms-base-0
        # 10. ase-acs-0
        # 11. arms-0
        _rk_arms_nh_wbase(
            rk_list,
            base_arms,
            pose_arms,
            clothing,
            acs_ase_list,
            leanpose,
            lean,
            flt,
            "0"
        )

        # 12. bmh-acs
        _rk_accessory_list(rk_list, acs_bmh_list, flt, leanpose)

        # 13. mid-hair
        _rk_hair(rk_list, hair, flt, MHAIR, lean, leanpose)

        # 14. mmh-acs
        _rk_accessory_list(rk_list, acs_mhh_list, flt, leanpose)

        # 15. body-head
        _rk_head(rk_list, flt, lean)

        # 16. bat-acs
        _rk_accessory_list(rk_list, acs_bat_list, flt, leanpose)

        # 17. table
        _rk_table(rk_list, tablechair, show_shadow, flt)

        # 18. mat-acs
        _rk_accessory_list(rk_list, acs_mat_list, flt, leanpose)

        # 19. arms-base-5
        # 20. ase-acs-5
        # 21. arms-5
        _rk_arms_nh_wbase(
            rk_list,
            base_arms,
            pose_arms,
            clothing,
            acs_ase_list,
            leanpose,
            lean,
            flt,
            "5"
        )

        # 22. mab-acs
        _rk_accessory_list(rk_list, acs_mab_list, flt, leanpose)

        # 23. base-1
        # 24. bse-acs-1
        # 25. body-1
        _rk_body_nh_wbase(
            rk_list,
            clothing,
            acs_bse_list,
            "1",
            flt,
            leanpose,
            lean=lean
        )

        # 26. bfh-acs
        _rk_accessory_list(rk_list, acs_bfh_list, flt, leanpose)

        # 27. face-pre
        _rk_face_pre(rk_list, flt, fpfx, lean, blush)

        # 28. front-hair
        _rk_hair(rk_list, hair, flt, FHAIR, lean, leanpose)

        # 29. afh-acs
        _rk_accessory_list(rk_list, acs_afh_list, flt, leanpose)

        # 30. face
        _rk_face(
            rk_list,
            eyes,
            eyebrows,
            nose,
            mouth,
            flt,
            fpfx,
            lean,
            sweat,
            tears,
            emote
        )

        # 31. mid-acs
        _rk_accessory_list(rk_list, acs_mid_list, flt, leanpose)

        # 32. arms-base-1
        # 33. ase-acs-1
        # 34. arms-1
        _rk_arms_nh_wbase(
            rk_list,
            base_arms,
            pose_arms,
            clothing,
            acs_ase_list,
            leanpose,
            lean,
            flt,
            "10"
        )

        # 35. pst-acs
        _rk_accessory_list(rk_list, acs_pst_list, flt, leanpose)

        return rk_list


init -10 python:

    class MASFilterMap(object):
        """SEALED
        The FilterMap connects filters to values

        DO NOT EXTEND THIS CLASS. if you need similar functionality, just
        make a wrapper class. There are functions in this class that will
        cause crashes if used in unexpected contexts.

        NOTE: you can make filtermaps with non-string values, just dont
            use the hash/eq/ne operators.

        PROPERTIES:
            map - dict containg filter to string map
                key: filter constant
                value: string or, None if no highlight
        """
        import store.mas_sprites_json as msj

        def __init__(self,
                default=None,
                cache=True,
                verify=True,
                **filter_pairs
        ):
            """
            Constructor

            IN:
                default - default code to apply to all filters
                    (Default: None)
                cache - True will cache the MFM, False will not
                    (Default: True)
                verify - True will verify the filters, False will not.
                    NOTE: if passing False, use the verify function to
                    verify flts.
                    (Default: True)
                **filter_pairs - filter=val args to use. invalid filters are
                    ignored.
                    See FILTERS dict. Example:
                        day=None
                        night="0"
            """
            self.map = MASFilterMap.clean_flt_pairs(default, filter_pairs)

            if verify:
                self.verify()

            if cache:
                store.mas_sprites.MFM_CACHE[hash(self)] = self

        def __eq__(self, other):
            """
            Equals implementation.
            MASFilterMaps are equal based on their internal tuple/hash var
            """
            if isinstance(self, other.__class__):
                return hash(self) == hash(other)
            return False

        def __hash__(self):
            """
            Hashable implementation.
            MASFilterMaps are uniqued based on their internal map
            """
            return MASFilterMap.flt_hash(self.map)

        def __ne__(self, other):
            """
            Not equals implmentation.
            MASFilterMaps are not equal based on their internal tuple/hash var
            """
            return not self.__eq__(other)

        @staticmethod
        def _fromJSON_value(json_obj, msg_log, ind_lvl, prop_name, output):
            """
            Parses a single value from the json obj

            IN:
                json_obj - JSON object to parse
                ind_lvl - indentation level
                prop_name - name of the prop to parse for

            OUT:
                msg_log - list to add messagse to
                output - dict to add data to:
                    key: prop_name
                    value: prop value

            RETURNS: True if we should stop because of failure, false if not
            """
            if prop_name not in json_obj:
                return False

            # otherwise prop exist
            prop_val = json_obj.pop(prop_name)
            if prop_val is None:
                # warn and leave if None
                msg_log.append((
                    store.mas_sprites_json.MSG_WARN_T,
                    ind_lvl,
                    store.mas_sprites_json.MFM_NONE_FLT.format(prop_name)
                ))
                return False

            # check type
            if store.mas_sprites_json._verify_str(prop_val):
                # valid
                output[prop_name] = prop_val
                return False

            # invalid type
            msg_log.append((
                store.mas_sprites_json.MSG_ERR_T,
                ind_lvl,
                store.mas_sprites_json.MFM_BAD_TYPE.format(
                    prop_name,
                    type(prop_val)
                )
            ))
            return True

        @staticmethod
        def cachecreate(default=None, **filter_pairs):
            """
            Creates a MASFilterMap object ONLY if it is not in the filtermap
            cache.

            IN:
                default - See constructor for MASFilterMap
                **filter_pairs - See constructor for MASFilterMap

            RETURNS: MASFilterMap object to use
            """
            hash_value = MASFilterMap.flt_hash(MASFilterMap.clean_flt_pairs(
                default,
                filter_pairs
            ))

            if hash_value in store.mas_sprites.MFM_CACHE:
                return store.mas_sprites.MFM_CACHE[hash_value]

            # otherwise generate the MFM. It will be added to teh cache in
            #  the constructor
            return MASFilterMap(default=default, **filter_pairs)

        @staticmethod
        def clean_flt_pairs(default, filter_pairs):
            """
            cleans given filter pairs, setting defaults and only using valid
            filter keys.

            IN:
                default - default code to apply to all filters
                filter_pairs - filter pair dict:
                    key: filter as string
                    value: code to use as string

            RETURNS: dict with cleaned filter pairs
            """
            output = {}

            # cehck existing filter keys and apply defaults
            for flt in store.mas_sprites.FILTERS:
                output[flt] = filter_pairs.get(flt, default)

            return output

        @staticmethod
        def flt_hash(flt_pairs):
            """
            Generates a hash based on the given filter pairs

            IN:
                flt_pairs - dict of the following format:
                    key: filter as string
                    value: code to use as string
                    NOTE: default is assumed to already been set

            RETURNS: hash that would be generated by a MASFilterMAp created
                with the given filter pairs
            """
            # hash a tuple of this filtermap's map's values, using None for
            # empty spaces
            return hash(tuple([
                flt_pairs.get(flt, None)
                for flt in store.mas_sprites.FILTERS
            ]))

        @classmethod
        def fromJSON(cls, json_obj, msg_log, ind_lvl, prop_name):
            """
            Builds a MASFilterMap given a JSON format of it

            IN:
                json_obj - JSOn object to parse
                ind_lvl - indent lvl
                    NOTE: this handles loading/success log, so do not
                        increase indent level
                prop_name - name of the prop this MASFilterMap object is
                    being created from

            OUT:
                msg_log - list to add messages to

            RETURNS: MASFilterMap object build using the JSON, or None if not
                creatable, or False if failur
            """
            # log loading
            msg_log.append((
                store.mas_sprites_json.MSG_INFO_T,
                ind_lvl,
                store.mas_sprites_json.MFM_LOADING.format(prop_name)
            ))

            # check none first
            if json_obj is None:
                # no data to make
                msg_log.append((
                    store.mas_sprites_json.MSG_INFO_T,
                    ind_lvl + 1,
                    store.mas_sprites_json.MFM_NO_DATA
                ))
                return None

            # check type
            if not store.mas_sprites_json._verify_dict(json_obj):
                msg_log.append((
                    store.mas_sprites_json.MSG_ERR_T,
                    ind_lvl + 1,
                    store.mas_sprites_json.BAD_TYPE.format(
                        prop_name,
                        dict,
                        type(json_obj)
                    )
                ))
                return False

            fltpairs = {}

            # parse for default first
            isbad = cls._fromJSON_value(
                json_obj,
                msg_log,
                ind_lvl + 1,
                "default",
                fltpairs
            )

            # loop over available filters
            for flt in store.mas_sprites.FILTERS:
                if cls._fromJSON_value(
                        json_obj,
                        msg_log,
                        ind_lvl + 1,
                        flt,
                        fltpairs
                ):
                    isbad = True

            # now loop over extras and warn
            for extra_prop in json_obj:
                msg_log.append((
                    store.mas_sprites_json.MSG_WARN_T,
                    ind_lvl + 1,
                    store.mas_sprites_json.EXTRA_PROP.format(extra_prop)
                ))

            # leave if bad
            if isbad:
                return False

            if len(fltpairs) < 1:
                # this has no data. ignore and return None
                msg_log.append((
                    store.mas_sprites_json.MSG_WARN_T,
                    ind_lvl + 1,
                    store.mas_sprites_json.MFM_NO_DATA,
                ))
                return None

            # otherwise probably valid

            # take out default if exists
            def_flt = None
            if "default" in fltpairs:
                def_flt = fltpairs.pop("default")

            # log success
            msg_log.append((
                store.mas_sprites_json.MSG_INFO_T,
                ind_lvl,
                store.mas_sprites_json.MFM_SUCCESS.format(prop_name)
            ))

            # then create this
            return cls.cachecreate(def_flt, **fltpairs)

        def get(self, flt, defval=None):
            """
            Gets value from map based on filter

            IN:
                flt - filter to lookup
                defval - default value to reutrn if filter not found
                    (Default: None)

            RETURNS: value for given filter
            """
            return self.map.get(flt, defval)

        def unique_values(self):
            """
            Gets all unique non-None values in this filter map

            RETURNS: list of all non-NOne and unique values in this filter
                map
            """
            vals = []
            for key in self.map:
                value = self.map[key]
                if value is not None and value not in vals:
                    vals.append(value)

            return vals

        def verify(self):
            """
            Verifies all filters in this filter map. Raises exceptions if
            bad filtesr are found.
            """
            for flt in self.map:
                if not store.mas_sprites.is_filter(flt):
                    raise MASInvalidFilterException(flt)


    class MASFilterMapSimple(object):
        """
        MASFilterMap for simple implementations, aka filter - value pairs
        without type checks.

        Classes that need MASFilterMap should just extend this one as a base.

        This will NOT cache filter maps.

        PROPERTIES:
            None
        """

        def __init__(self, **filter_pairs):
            """
            Constructor

            Passes values directly to the internal MFM

            IN:
                **filter_pairs - filter=val args to use. invalid filters
                    are ignored.
            """
            self.__mfm = MASFilterMap(
                default=None,
                cache=False,
                **filter_pairs
            )

        def flts(self):
            """
            Gets all filter names in this filter map

            RETURNS: list of all filter names in this map
            """
            return self.__mfm.map.keys()

        def get(self, flt, defval=None):
            """
            See MASFilterMap.get
            """
            return self.__mfm.get(flt, defval)

        def _mfm(self):
            """
            Returns the intenral MASFilterMap. Only use if you know what you
            are doing.

            RETURNS: MASFilterMap
            """
            return self.__mfm


    class MASFilterMapFallback(MASFilterMapSimple):
        """
        MASFilterMap that respects fallback mechanics.

        Classes that need fallback behavior should just extend this one as a
        base.

        This will NOT cache filter maps.

        PROPERTIES:
            None
        """

        def __init__(self, **filter_pairs):
            """
            Constructor

            IN:
                **filter_pairs - filter=val args to use. invalid filters are
                    ignored.
            """
            super(MASFilterMapFallback, self).__init__(**filter_pairs)

        def get(self, flt, defval=None):
            """
            Gets value from map based on filter. This follows fallback
            mechanics until a non-None value is found.

            IN:
                flt - filter to lookup
                defval - default value to return if no non-None value is
                    found after exhausting all fallbacks.
                    (Default: None)

            REUTRNS: value for a given filter
            """
            value = self._raw_get(flt)
            cur_flt = flt
            while value is None:
                nxt_flt = store.mas_sprites._rslv_flt(cur_flt)

                if nxt_flt == cur_flt:
                    # if flt doesnt change, we have reached teh bottom
                    return defval

                value = self._raw_get(nxt_flt)
                cur_flt = nxt_flt

            return value

        def _raw_get(self, flt):
            """
            Gets value from map based on filter

            IN:
                flt - filter to lookup

            RETURNS: value for the given filter
            """
            return super(MASFilterMapFallback, self).get(flt)


init -2 python:


    def mas_drawmonika_rk(
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
            head="a",
            left="1l",
            right="1r",
            stock=True,
            single=None
        ):
        """
        Draws monika dynamically, using render keys
        See mas_drawmonika for more info.

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
        if not is_sitting:
            # image manips are only defined for sitting
            return mas_drawmonika(
                st, at, character,
                eyebrows, eyes, nose, mouth,
                lean, arms, eyebags, sweat, blush, tears, emote,
                head, left, right, stock, single
            )

        # gather accessories
        acs_pre_list = character.acs.get(MASMonika.PRE_ACS, [])
        acs_bbh_list = character.acs.get(MASMonika.BBH_ACS, [])
        acs_bse_list = character.acs.get(MASMonika.BSE_ACS, [])
        acs_bba_list = character.acs.get(MASMonika.BBA_ACS, [])
        acs_ase_list = character.acs.get(MASMonika.ASE_ACS, [])
        acs_bmh_list = character.acs.get(MASMonika.BMH_ACS, [])
        acs_mmh_list = character.acs.get(MASMonika.MMH_ACS, [])
        acs_bat_list = character.acs.get(MASMonika.BAT_ACS, [])
        acs_mat_list = character.acs.get(MASMonika.MAT_ACS, [])
        acs_mab_list = character.acs.get(MASMonika.MAB_ACS, [])
        acs_bfh_list = character.acs.get(MASMonika.BFH_ACS, [])
        acs_afh_list = character.acs.get(MASMonika.AFH_ACS, [])
        acs_mid_list = character.acs.get(MASMonika.MID_ACS, [])
        acs_pst_list = character.acs.get(MASMonika.PST_ACS, [])

        # NOTE: we also do not support baked

        # detremine all poses-specifc data to use:
        # [0] - lean to use
        # [1] - leanpose to use
        # [2] - arms to use
        # [3] - hair to use
        # [4] - base arms to use
        # [5] - pose arms to use
        pose_data = character._determine_poses(lean, arms)

        # determine filter to use
        flt = store.mas_sprites.get_filter()

        # generate sprite displayable
        sprite = store.mas_sprites.MASMonikaRender(
            store.mas_sprites._rk_sitting(
                character.clothes,
                pose_data[3],
                pose_data[4],
                pose_data[5],
                eyebrows,
                eyes,
                nose,
                mouth,
                flt,
                acs_pre_list,
                acs_bbh_list,
                acs_bse_list,
                acs_bba_list,
                acs_ase_list,
                acs_bmh_list,
                acs_mmh_list,
                acs_bat_list,
                acs_mat_list,
                acs_mab_list,
                acs_bfh_list,
                acs_afh_list,
                acs_mid_list,
                acs_pst_list,
                pose_data[1],
                pose_data[0],
                pose_data[2],
                eyebags,
                sweat,
                blush,
                tears,
                emote,
                character.tablechair,
                character.tablechair.has_shadow
            ),
            flt,
            store.mas_sprites.adjust_x,
            store.mas_sprites.adjust_y,
            store.mas_sprites.LOC_W,
            store.mas_sprites.LOC_H
        )

        # finally apply zoom
        return Transform(sprite, zoom=store.mas_sprites.value_zoom), None


    def mas_drawemptydesk_rk(st, at, character):
        """
        draws the table dynamically. includes ACS that should stay on desk.
        NOTE: uses image manips.
        NOTE: this is assumed to be used with empty desk ONLY
        NOTE: sitting only

        IN:
            st - renpy related
            at - renpy realted
            character - MASMonika character object
        """
        # in drawtable mode, only pst acs that stay on desk matter
        acs_pst_list = [
            acs
            for acs in character.acs.get(MASMonika.PST_ACS, [])
            if acs.keep_on_desk
        ]

        # prepare image manips
        rk_list = []

        # decide the filter
        flt = store.mas_sprites.get_filter()

        # now build the chair
        store.mas_sprites._rk_chair(rk_list, character.tablechair, flt)

        # then the able
        store.mas_sprites._rk_table(
            rk_list,
            character.tablechair,
            False,
            flt
        )

        # then the pst acs we got
        store.mas_sprites._rk_accessory_list(
            rk_list,
            acs_pst_list,
            flt,
            "steepling"
        )

        # generate sprite displayable
        sprite = store.mas_sprites.MASMonikaRender(
            rk_list,
            flt,
            store.mas_sprites.adjust_x,
            store.mas_sprites.adjust_y,
            store.mas_sprites.LOC_W,
            store.mas_sprites.LOC_H
        )

        # finally appyl zoom and return
        return Transform(sprite, zoom=store.mas_sprites.value_zoom), None
