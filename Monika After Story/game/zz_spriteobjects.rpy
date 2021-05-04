# All Sprite objects belong here
#
# For documentation on classes, see sprite-chart
#
# quicklinks:
#   [SPR005] - Shaired programming points/prog point utilities
#   [SPR010] - Hair programming points
#   [SPR020] - Clothes programming points
#   [SPR030] - ACS programming points
#   [SPR110] - Hair sprite objects
#   [SPR120] - Clothes sprite objects
#   [SPR130] - ACS sprite objects
#   [SPR140] - Table sprite objects
#   [SPR230] - ACS variables

init -2 python in mas_sprites:
    # all progrmaming points should go here
    # organize by type then id
    # ASSUME all programming points only run at runtime
    import store

    temp_storage = dict()
    # all programming points have access to this storage var.
    # use names + an identifier as keys so you wont collide
    # NOTE: this will NOT be maintained on a restart

    ######### TESTING PROG POINTS ##########
    # none of these actually do anything. They are for testing the
    # JSON sprite system

    _hair__testing_entry = False
    _hair__testing_exit = False
    _clothes__testing_entry = False
    _clothes__testing_exit = False
    _acs__testing_entry = False
    _acs__testing_exit = False


    ######### SHARED PROGPOINTS [SPR005] ######################
    # These should be used by other prog points to streamline commonly done
    # actions.
    def _acs_wear_if_found(_moni_chr, acs_name):
        """
        Wears the acs if the acs exists

        IN:
            _moni_chr - MASMonika object
            acs_name - name of the accessory
        """
        acs_to_wear = store.mas_sprites.get_sprite(
            store.mas_sprites.SP_ACS,
            acs_name
        )
        if acs_to_wear is not None:
            _moni_chr.wear_acs(acs_to_wear)


    def _acs_wear_if_gifted(_moni_chr, acs_name):
        """
        Wears the acs if it exists and has been gifted/reacted.
        It has been gifted/reacted if the selectable is unlocked.

        IN:
            _moni_chr - MASMonika object
            acs_name - name of the accessory
        """
        acs_to_wear = store.mas_sprites.get_sprite(
            store.mas_sprites.SP_ACS,
            acs_name
        )
        if acs_to_wear is not None and store.mas_SELisUnlocked(acs_to_wear):
            _moni_chr.wear_acs(acs_to_wear)


    def _acs_wear_if_in_tempstorage(_moni_chr, key):
        """
        Wears the acs in tempstorage at the given key, if any.

        IN:
            _moni_chr - MASMonika object
            key - key in tempstorage
        """
        acs_items = temp_storage.get(key, None)
        if acs_items is not None:
            for acs_item in acs_items:
                _moni_chr.wear_acs(acs_item)


    def _acs_wear_if_in_tempstorage_s(_moni_chr, key):
        """
        Wears a single acs in tempstorage at the given key, if any.

        IN:
            _moni_chr - MASMonika object
            key - key in tempstorage
        """
        acs_item = temp_storage.get(key, None)
        if acs_item is not None:
            _moni_chr.wear_acs(acs_item)


    def _acs_wear_if_wearing_acs(_moni_chr, acs, acs_to_wear):
        """
        Wears the given acs if wearing another acs.

        IN:
            _moni_chr - MASMonika object
            acs - acs to check if wearing
            acs_to_wear - acs to wear if wearing acs
        """
        if _moni_chr.is_wearing_acs(acs):
            _moni_chr.wear_acs(acs_to_wear)


    def _acs_wear_if_wearing_type(_moni_chr, acs_type, acs_to_wear):
        """
        Wears the given acs if wearing an acs of the given type.

        IN:
            _moni_chr - MASMonika object
            acs_type - acs type to check if wearing
            acs_to_wear - acs to wear if wearing acs type
        """
        if _moni_chr.is_wearing_acs_type(acs_type):
            _moni_chr.wear_acs(acs_to_wear)


    def _acs_wear_if_not_wearing_type(_moni_chr, acs_type, acs_to_wear):
        """
        Wears the given acs if NOT wearing an acs of the given type.

        IN:
            _moni_chr - MASMonika object
            acs_type - asc type to check if not wearing
            acs_to_wear - acs to wear if not wearing acs type
        """
        if not _moni_chr.is_wearing_acs_type(acs_type):
            _moni_chr.wear_acs(acs_to_wear)


    def _acs_remove_if_found(_moni_chr, acs_name):
        """
        REmoves an acs if the name exists

        IN:
            _moni_chr - MASMonika object
            acs_name - name of the accessory to remove
        """
        acs_to_remove = store.mas_sprites.get_sprite(
            store.mas_sprites.SP_ACS,
            acs_name
        )
        if acs_to_remove is not None:
            _moni_chr.remove_acs(acs_to_remove)


    def _acs_ribbon_save_and_remove(_moni_chr):
        """
        Removes ribbon acs and aves them to temp storage.

        IN:
            _moni_chr - MASMonika object
        """
        prev_ribbon = _moni_chr.get_acs_of_type("ribbon")

        # always save ribbon even if not wearing one (so ok to save None)
        if prev_ribbon != store.mas_acs_ribbon_blank:
            temp_storage["hair.ribbon"] = prev_ribbon

        if prev_ribbon is not None:
            _moni_chr.remove_acs(prev_ribbon)

        # lock ribbon select
        store.mas_lockEVL("monika_ribbon_select", "EVE")


    def _acs_ribbon_like_save_and_remove(_moni_chr):
        """
        Removes ribbon-like acs and saves them to temp storage, if found

        IN:
            _moni_chr - MASMonika object
        """
        prev_ribbon_like = _moni_chr.get_acs_of_exprop("ribbon-like")

        if prev_ribbon_like is not None:
            _moni_chr.remove_acs(prev_ribbon_like)
            temp_storage["hair.ribbon"] = prev_ribbon_like


    def _acs_save_and_remove_exprop(_moni_chr, exprop, key, lock_topics):
        """
        Removes acs with given exprop, saving them to temp storage with
        given key.
        Also locks topics with the exprop if desired

        IN:
            _moni_chr - MASMonika object
            exprop - exprop to remove and save acs
            key - key to use for temp storage
            lock_topics - True will lock topics associated with this exprop
                False will not
        """
        acs_items = _moni_chr.get_acs_of_exprop(exprop, get_all=True)
        if len(acs_items) > 0:
            temp_storage[key] = acs_items
            _moni_chr.remove_acs_exprop(exprop)

        if lock_topics:
            lock_exprop_topics(exprop)


    def _hair_unlock_select_if_needed():
        """
        Unlocks the hairdown selector if enough hair is unlocked.
        """
        if len(store.mas_selspr.filter_hair(True)) > 1:
            store.mas_unlockEVL("monika_hair_select", "EVE")


    def _clothes_baked_entry(_moni_chr):
        """
        Clothes baked entry
        """
        for prompt_key in store.mas_selspr.PROMPT_MAP:
            if prompt_key != "clothes":
                prompt_ev = store.mas_selspr.PROMPT_MAP[prompt_key].get(
                    "_ev",
                    None
                )
                if prompt_ev is not None:
                    store.mas_lockEVL(prompt_ev, "EVE")

        # removes all acs
        _moni_chr.remove_all_acs()
        # and update prompts
        store.mas_selspr._switch_to_wear_prompts()


    ######### HAIR [SPR010] ###########
    # available kwargs:
    #   entry:
    #       prev_hair - previously worn hair
    #   exit:
    #       new_hair - hair that is to be worn

    def _hair_def_entry(_moni_chr, **kwargs):
        """
        Entry programming point for ponytail
        """
        pass

    def _hair_def_exit(_moni_chr, **kwargs):
        """
        Exit programming point for ponytail
        """
        pass

    def _hair_down_entry(_moni_chr, **kwargs):
        """
        Entry programming point for hair down
        """
        pass

    def _hair_down_exit(_moni_chr, **kwargs):
        """
        Exit programming point for hair down
        """
        pass

    def _hair_bun_entry(_moni_chr, **kwargs):
        """
        Entry programming point for hair bun
        """
        pass

    def _hair_orcaramelo_bunbraid_exit(_moni_chr, **kwargs):
        """
        Exit prog point for bunbraid
        """
        # always take off the headband
        _acs_remove_if_found(_moni_chr, "orcaramelo_sakuya_izayoi_headband")

    def _hair_braided_entry(_moni_chr, **kwargs):
        """
        Entry prog point for braided hair
        """
        _moni_chr.wear_acs(store.mas_acs_rin_bows_back)
        _moni_chr.wear_acs(store.mas_acs_rin_bows_front)

    def _hair_braided_exit(_moni_chr, **kwargs):
        """
        Exit prog point for braided hair
        """
        _moni_chr.remove_acs(store.mas_acs_rin_bows_front)
        _moni_chr.remove_acs(store.mas_acs_rin_bows_back)
        #Always remove rin ears
        _moni_chr.remove_acs(store.mas_acs_rin_ears)

    ######### CLOTHES [SPR020] ###########
    # available kwargs:
    #   entry:
    #       prev_clothes - prevoiusly worn clothes
    #   exit:
    #       new_clothes - clothes that are to be worn

    def _clothes_def_entry(_moni_chr, **kwargs):
        """
        Entry programming point for def clothes
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        if outfit_mode:
            # ponytail and white ribbon
            _moni_chr.change_hair(store.mas_hair_def)
            _moni_chr.wear_acs(store.mas_acs_ribbon_def)

        store.mas_lockEVL("mas_compliment_outfit", "CMP")

        # TODO: need to add ex prop checking and more
        # so we can rmeove bare acs


    def _clothes_def_exit(_moni_chr, **kwargs):
        """
        Exit programming point for def clothes
        """

        store.mas_unlockEVL("mas_compliment_outfit", "CMP")


    def _clothes_rin_entry(_moni_chr, **kwargs):
        """
        Entry programming point for rin clothes
        """
        outfit_mode = kwargs.get("outfit_mode")

        if outfit_mode:
            _moni_chr.change_hair(store.mas_hair_braided)
            _moni_chr.wear_acs(store.mas_acs_rin_ears)


    def _clothes_rin_exit(_moni_chr, **kwargs):
        """
        Exit programming point for rin clothes
        """
        _moni_chr.remove_acs(store.mas_acs_rin_ears)


    def _clothes_marisa_entry(_moni_chr, **kwargs):
        """
        Entry programming point for marisa clothes
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        if outfit_mode:
            _moni_chr.change_hair(store.mas_hair_downtiedstrand)
            _moni_chr.wear_acs(store.mas_acs_marisa_strandbow)
            _moni_chr.wear_acs(store.mas_acs_marisa_witchhat)


    def _clothes_marisa_exit(_moni_chr, **kwargs):
        """
        Exit programming point for marisa clothes
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        _moni_chr.remove_acs(store.mas_acs_marisa_strandbow)

        if outfit_mode:
            _moni_chr.remove_acs(store.mas_acs_marisa_witchhat)


    def _clothes_orcaramelo_hatsune_miku_entry(_moni_chr, **kwargs):
        """
        Entry pp for orcaramelo miku
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        if outfit_mode:
            # swap to bun braid if found. if not, dont wear acs.
            twintails = store.mas_sprites.get_sprite(
                store.mas_sprites.SP_HAIR,
                "orcaramelo_twintails"
            )
            if twintails is not None:
                _moni_chr.change_hair(twintails)

                # find acs and wear for this outfit
                _acs_wear_if_found(
                    _moni_chr,
                    "orcaramelo_hatsune_miku_headset"
                )
                _acs_wear_if_found(
                    _moni_chr,
                    "orcaramelo_hatsune_miku_twinsquares"
                )


    def _clothes_orcaramelo_hatsune_miku_exit(_moni_chr, **kwargs):
        """
        Exit pp for orcaramelo miku
        """
        # find and remove acs if found
        _acs_remove_if_found(
            _moni_chr,
            "orcaramelo_hatsune_miku_headset"
        )
        _acs_remove_if_found(
            _moni_chr,
            "orcaramelo_hatsune_miku_twinsquares"
        )


    def _clothes_orcaramelo_sakuya_izayoi_entry(_moni_chr, **kwargs):
        """
        Entry pp for orcaramelo sakuya
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        if outfit_mode:
            # swap to bun braid if found. if not, dont wear acs.
            bunbraid = store.mas_sprites.get_sprite(
                store.mas_sprites.SP_HAIR,
                "orcaramelo_bunbraid"
            )
            if bunbraid is not None:
                _moni_chr.change_hair(bunbraid)

                # find acs and wear for this outfit
                _acs_wear_if_found(
                    _moni_chr,
                    "orcaramelo_sakuya_izayoi_headband"
                )
                _acs_wear_if_found(
                    _moni_chr,
                    "orcaramelo_sakuya_izayoi_strandbow"
                )

                #Remove ribbon so we just get the intended costume since the correct hairstyle is present
                ribbon_acs = _moni_chr.get_acs_of_type("ribbon")
                if ribbon_acs is not None:
                    _moni_chr.remove_acs(ribbon_acs)


    def _clothes_orcaramelo_sakuya_izayoi_exit(_moni_chr, **kwargs):
        """
        Exit pp for orcaramelo sakuya
        """
        # find and remove acs if found
        _acs_remove_if_found(
            _moni_chr,
            "orcaramelo_sakuya_izayoi_headband"
        )
        _acs_remove_if_found(
            _moni_chr,
            "orcaramelo_sakuya_izayoi_strandbow"
        )


    def _clothes_santa_entry(_moni_chr, **kwargs):
        """
        Entry programming point for santa clothes
        """
        store.mas_selspr.unlock_acs(store.mas_acs_holly_hairclip)

        outfit_mode = kwargs.get("outfit_mode", False)

        if outfit_mode:
            _moni_chr.change_hair(store.mas_hair_def)
            _moni_chr.wear_acs(store.mas_acs_ribbon_wine)
            _moni_chr.wear_acs(store.mas_acs_holly_hairclip)


    def _clothes_santa_exit(_moni_chr, **kwargs):
        """
        Exit programming point for santa clothes
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        if outfit_mode:
            _moni_chr.remove_acs(store.mas_acs_holly_hairclip)


    def _clothes_santa_lingerie_entry(_moni_chr, **kwargs):
        """
        Entry programming point for santa lingerie
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        if outfit_mode:
            _moni_chr.wear_acs(store.mas_acs_holly_hairclip)


    def _clothes_santa_lingerie_exit(_moni_chr, **kwargs):
        """
        Exit programming point for santa lingerie
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        if outfit_mode:
            _moni_chr.remove_acs(store.mas_acs_holly_hairclip)


    def _clothes_dress_newyears_entry(_moni_chr, **kwargs):
        """
        entry progpoint for dress_newyears
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        if outfit_mode:
            #Swap to braided ponytail if found
            ponytailbraid = store.mas_sprites.get_sprite(
                store.mas_sprites.SP_HAIR,
                "orcaramelo_ponytailbraid"
            )
            if ponytailbraid is not None:
                _moni_chr.change_hair(ponytailbraid)

            _moni_chr.wear_acs(store.mas_acs_flower_crown)
            _moni_chr.wear_acs(store.mas_acs_hairties_bracelet_brown)

            #Remove hairclips
            hairclip = _moni_chr.get_acs_of_type("left-hair-clip")
            if hairclip:
                _moni_chr.remove_acs(hairclip)

            #Remove ribbon
            ribbon = _moni_chr.get_acs_of_type("ribbon")
            if ribbon:
                _moni_chr.remove_acs(ribbon)


    def _clothes_dress_newyears_exit(_moni_chr, **kwargs):
        """
        exit progpoint for dress_newyears
        """
        _moni_chr.remove_acs(store.mas_acs_flower_crown)
        _moni_chr.remove_acs(store.mas_acs_hairties_bracelet_brown)

    def _clothes_sundress_white_entry(_moni_chr, **kwargs):
        """
        Entry programming point for sundress white
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        if outfit_mode:
            _moni_chr.wear_acs(store.mas_acs_hairties_bracelet_brown)
            _moni_chr.wear_acs(store.mas_acs_musicnote_necklace_gold)


    def _clothes_sundress_white_exit(_moni_chr, **kwargs):
        """
        Exit programming point for sundress white
        """
        # TODO: add selectors for these items so they dont have to be
        #   removed
        _moni_chr.remove_acs(store.mas_acs_hairties_bracelet_brown)
        _moni_chr.remove_acs(store.mas_acs_musicnote_necklace_gold)


    def _clothes_velius94_dress_whitenavyblue_entry(_moni_chr, **kwargs):
        """
        Entry prog point for navyblue dress
        """
        outfit_mode = kwargs.get("outfit_mode", False)

        if outfit_mode:
            # default to ponytail if not wearing a ribbon-acceptable hair
            if (
                    not _moni_chr.is_wearing_hair_with_exprop("ribbon")
                    or _moni_chr.is_wearing_hair_with_exprop("twintails")
            ):
                _moni_chr.change_hair(store.mas_hair_def)

            _acs_wear_if_gifted(_moni_chr, "velius94_bunnyscrunchie_blue")


    ######### ACS [SPR030] ###########
    # available kwargs:
    #   NONE

    def _acs_quetzalplushie_entry(_moni_chr, **kwargs):
        """
        Entry programming point for quetzal plushie acs
        """
        #We need to unlock/random monika_plushie since the plush is active
        store.mas_showEVL('monika_plushie', 'EVE', _random=True)

        if store.persistent._mas_d25_deco_active:
            _moni_chr.wear_acs(store.mas_acs_quetzalplushie_santahat)

    def _acs_quetzalplushie_exit(_moni_chr, **kwargs):
        """
        Exit programming point for quetzal plushie acs
        """
        #Since no more plush, we need to lock/derandom monika_plushie
        store.mas_hideEVL('monika_plushie', 'EVE', derandom=True)

        # remove the santa hat if we are removing the plushie
        _moni_chr.remove_acs(store.mas_acs_quetzalplushie_santahat)
        # also remove antlers
        _moni_chr.remove_acs(store.mas_acs_quetzalplushie_antlers)

    def _acs_center_quetzalplushie_entry(_moni_chr, **kwargs):
        """
        Entry programming point for quetzal plushie (mid version) acs
        """
        store.mas_showEVL("monika_plushie", "EVE", _random=True)

        if store.persistent._mas_d25_deco_active:
            _moni_chr.wear_acs(store.mas_acs_quetzalplushie_center_santahat)

    def _acs_center_quetzalplushie_exit(_moni_chr, **kwargs):
        """
        Exit programming point for quetzal plushie (mid version) acs
        """
        store.mas_hideEVL("monika_plushie", "EVE", derandom=True)

        _moni_chr.remove_acs(store.mas_acs_quetzalplushie_center_santahat)
        # FIXME: We don't have center antiers yet
        # _moni_chr.remove_acs(store.mas_acs_quetzalplushie_center_antlers)

    def _acs_quetzalplushie_santahat_entry(_moni_chr, **kwargs):
        """
        Entry programming point for quetzal plushie santa hat acs
        """
        # need to wear the quetzal plushie if we putting the santa hat on
        _moni_chr.wear_acs(store.mas_acs_quetzalplushie)

    def _acs_center_quetzalplushie_santahat_entry(_moni_chr, **kwargs):
        """
        Entry programming point for quetzal plushie santa hat (mid version) acs
        """
        _moni_chr.wear_acs(store.mas_acs_center_quetzalplushie)

    def _acs_quetzalplushie_antlers_entry(_moni_chr, **kwargs):
        """
        Entry programming point for quetzal plushie antlers acs
        """
        # need to wear the quetzal plushie if we putting the antlers on
        _moni_chr.wear_acs(store.mas_acs_quetzalplushie)

    def _acs_heartchoc_entry(_moni_chr, **kwargs):
        """
        Entry programming point for heartchoc acs
        """
        #We only want to be temporarily moving the plush if not on f14
        #Since we keep the chocs post reaction if it is f14

        # TODO: might need to make a center version of santa hat
        #   or just make heartchoc not giftable during d25

        if not (store.mas_isF14() or store.mas_isD25Season()):
            if _moni_chr.is_wearing_acs(store.mas_acs_quetzalplushie):
                _moni_chr.wear_acs(store.mas_acs_center_quetzalplushie)

        else:
            _moni_chr.remove_acs(store.mas_acs_quetzalplushie)

    def _acs_heartchoc_exit(_moni_chr, **kwargs):
        """
        Exit programming point for heartchoc acs
        """
        if _moni_chr.is_wearing_acs(store.mas_acs_center_quetzalplushie):
            _moni_chr.wear_acs(store.mas_acs_quetzalplushie)

init -1 python:
    # HAIR (SPR110)
    # Hairs are representations of image objects with propertes
    #
    # NAMING:
    # mas_hair_<hair name>
    #
    # <hair name> MUST BE UNIQUE
    #
    # NOTE: see the existing standards for hair file naming
    # NOTE: PoseMaps are used to determin which lean types exist for
    #   a given hair type, NOT filenames
    #
    # NOTE: the fallback system:
    #   by setting fallback to True, you can use the fallback system to
    #   make poses fallback to a different pose. NOTE: non-lean types CANNOT
    #   fallback to a lean type. Lean types can fallback to anything.
    #
    #   When using the fallback system, map poses to the pose/lean types
    #   that you want to fallback on.
    #   AKA: to make pose 2 fallback to steepling, do `p2="steepling"`
    #   To make everything fallback to steepling, do `default="steepling"`
    #   This means that steepling MUST exist for the fallback system to work
    #   perfectly.
    #
    # NOTE: valid exprops
    #   ribbon - True if this works with ribobn. False or not set if not
    #   ribbon-restore - Set if this hair should restore previously saved
    #       ribbon if found
    #   ribbon-off - True if wearing this hair should take off the ribbon.
    #       This should only be used with ribbon. force-ribbon takes predence
    #
    # NOTE: template:
    ### HUMAN UNDERSTANDABLE NAME OF HAIR STYLE
    ## hairidentifiername
    # General description of the hair style

    ### PONYTAIL WITH RIBBON (default)
    ## def
    # Monika's default hairstyle, aka the ponytail
    # thanks Ryuse/Iron707/Taross/Metisz/Tri/JMO/Orca
    mas_hair_def = MASHair(
        "def",
        "def",
        MASPoseMap(
            default=True,
            use_reg_for_l=True
        ),
#        entry_pp=store.mas_sprites._hair_def_entry,
#        exit_pp=store.mas_sprites._hair_def_exit,
        ex_props={
            "ribbon": True,
            "ribbon-restore": True
        }
    )
    store.mas_sprites.init_hair(mas_hair_def)
    store.mas_selspr.init_selectable_hair(
        mas_hair_def,
        "Ponytail",
        "def",
        "hair",
        select_dlg=[
            "Do you like my ponytail, [player]?"
        ]
    )
    store.mas_selspr.unlock_hair(mas_hair_def)

    ### DOWN
    ## down
    # Hair is down, not tied up
    # thanks Ryuse/Finale/Iron707/Taross/Metisz/Tri/JMO/Orca
    mas_hair_down = MASHair(
        "down",
        "down",
        MASPoseMap(
            default=True,
            use_reg_for_l=True
        ),
        ex_props={
            store.mas_sprites.EXP_H_NT: True,
        }
#        entry_pp=store.mas_sprites._hair_down_entry,
#        exit_pp=store.mas_sprites._hair_down_exit,
#        split=False
    )
    store.mas_sprites.init_hair(mas_hair_down)
    store.mas_selspr.init_selectable_hair(
        mas_hair_down,
        "Down",
        "down",
        "hair",
        select_dlg=[
            "Feels nice to let my hair down..."
        ]
    )

    ### DOWNTIED
    ## downtiedstrand
    # Hair is down but with a tied strand
    # Thanks Orca
    mas_hair_downtiedstrand = MASHair(
        "downtiedstrand",
        "downtiedstrand",
        MASPoseMap(
            default=True,
            use_reg_for_l=True
        ),
        ex_props={
            store.mas_sprites.EXP_H_RQCP: store.mas_sprites.EXP_C_C_DTS,
            store.mas_sprites.EXP_H_TS: True,
            store.mas_sprites.EXP_H_NT: True,
        }
    )
    store.mas_sprites.init_hair(mas_hair_downtiedstrand)
    store.mas_selspr.init_selectable_hair(
        mas_hair_downtiedstrand,
        "Down (Tied strand)",
        "downtiedstrand",
        "hair",
        select_dlg=[
            "Feels nice to let my hair down...",
            "Looks cute, don't you think?"
        ]
    )

    ### BRAIDED
    ## braided
    # Hair is braided on the left/right. Auto adds bows
    # Thanks Briar/SS
    mas_hair_braided = MASHair(
        "braided",
        "braided",
        MASPoseMap(
            default=True,
            use_reg_for_l=True
        ),
        ex_props={
            store.mas_sprites.EXP_H_TB: True,
            store.mas_sprites.EXP_H_RQCP: "rin"
        },
        entry_pp=store.mas_sprites._hair_braided_entry,
        exit_pp=store.mas_sprites._hair_braided_exit
    )
    store.mas_sprites.init_hair(mas_hair_braided)
    store.mas_selspr.init_selectable_hair(
        mas_hair_braided,
        "Braided",
        "braided",
        "hair",
        select_dlg=[
            "Looks cute, don't you think?"
        ]
    )

    ### CUSTOM
    ## custom
    # Not a real hair object. If an outfit uses this, it's assumed that the
    # actual clothes have the hair baked into them.
    mas_hair_custom = MASHair(
        "custom",
        "custom",
        MASPoseMap(),

        # NOTE: custom disables hair splitting.
        split=MASPoseMap(
            default=False,
            use_reg_for_l=True
        ),
    )
    store.mas_sprites.init_hair(mas_hair_custom)


init -1 python:
    # THIS MUST BE AFTER THE HAIR SECTION
    # CLOTHES (SPR120)
    # Clothes are representations of image objects with properties
    #
    # NAMING:
    # mas_clothes_<clothes name>
    #
    # <clothes name> MUST BE UNIQUE
    #
    # NOTE: see the existing standards for clothes file naming
    # NOTE: PoseMaps are used to determine which lean types exist for
    #  a given clothes type, NOT filenames
    #
    # NOTE: see IMG015 for info about the fallback system
    #
    # NOTE: exprops
    #   desired-ribbon: name of the ribbon that this outfit will try to wear
    #       may be overriden by user
    #
    # NOTE: template
    ### HUMAN UNDERSTANDABLE NAME OF THIS CLOTHES
    ## clothesidentifiername
    # General description of the clothes

    ### SCHOOL UNIFORM (default)
    ## def
    # Monika's school uniform
    # thanks Ryuse/Velius94 (Jacket)
    mas_clothes_def = MASClothes(
        "def",
        "def",
        MASPoseMap(
            default=True,
            use_reg_for_l=True
        ),
        stay_on_start=True,
        entry_pp=store.mas_sprites._clothes_def_entry,
        exit_pp=store.mas_sprites._clothes_def_exit
    )
    store.mas_sprites.init_clothes(mas_clothes_def)
    store.mas_selspr.init_selectable_clothes(
        mas_clothes_def,
        "School Uniform",
        "schooluniform",
        "clothes",
        visible_when_locked=True,
        hover_dlg=None,
        select_dlg=[
            "Ready for school!"
        ]
    )
    store.mas_selspr.unlock_clothes(mas_clothes_def)


    ### BLACK DRESS (OUR TIME)
    ## blackdress
    # Blackdress from Our Time Mod
    # thanks SovietSpartan/JMO/Orca/Velius94/Orca
    mas_clothes_blackdress = MASClothes(
        "blackdress",
        "blackdress",
        MASPoseMap(
            default=True,
            use_reg_for_l=True
        ),
        stay_on_start=True,
        ex_props={
            store.mas_sprites.EXP_C_BS: True,
        }
    )
    store.mas_sprites.init_clothes(mas_clothes_blackdress)
    store.mas_selspr.init_selectable_clothes(
        mas_clothes_blackdress,
        "Black Dress",
        "blackdress",
        "clothes",
        visible_when_locked=False,
        select_dlg=[
            "Are we going somewhere special, [player]?"
        ]
    )


    ### BLAZERLESS SCHOOL UNIFORM
    ## blazerless
    # Monika's school uniform, without the blazer
    # thanks Iron/Velius94/Orca
    mas_clothes_blazerless = MASClothes(
        "blazerless",
        "blazerless",
        MASPoseMap(
            default=True,
            use_reg_for_l=True
        ),
        stay_on_start=True,
        ex_props={
            store.mas_sprites.EXP_C_C_DTS: True
        },
        pose_arms=MASPoseArms(
            {
                1: MASArmBoth(
                    "crossed",
                    {
                        MASArm.LAYER_MID: True,
                    }
                ),
            }
        )
    )
    store.mas_sprites.init_clothes(mas_clothes_blazerless)
    store.mas_selspr.init_selectable_clothes(
        mas_clothes_blazerless,
        "School Uniform (Blazerless)",
        "schooluniform_blazerless",
        "clothes",
        visible_when_locked=True,
        hover_dlg=None,
        select_dlg=[
            "Ah, feels nice without the blazer!",
        ]
    )
    store.mas_selspr.unlock_clothes(mas_clothes_def)


    ### MARISA COSTUME
    ## marisa
    # Witch costume based on Marisa
    # thanks SovietSpartan
    mas_clothes_marisa = MASClothes(
        "marisa",
        "marisa",
        MASPoseMap(
            default=True,
            use_reg_for_l=True
        ),
        pose_arms=MASPoseArms(
            {
                1: MASArmBoth(
                    "crossed",
                    {
                        MASArm.LAYER_MID: True,
                    }
                ),
                9: MASArmRight(
                    "def",
                    {
                        MASArm.LAYER_MID: True,
                    }
                ),
            }
        ),
        stay_on_start=True,
        entry_pp=store.mas_sprites._clothes_marisa_entry,
        exit_pp=store.mas_sprites._clothes_marisa_exit,
        ex_props={
            store.mas_sprites.EXP_C_C_DTS: True,
            store.mas_sprites.EXP_C_COST: "o31",
            store.mas_sprites.EXP_C_COSP: True,
        }
    )
    store.mas_sprites.init_clothes(mas_clothes_marisa)
    store.mas_selspr.init_selectable_clothes(
        mas_clothes_marisa,
        "Witch Costume",
        "marisa",
        "clothes",
        visible_when_locked=False,
        hover_dlg=None,
        select_dlg=[
            "Just an ordinary costume, ~ze."
        ]
    )

    ### RIN COSTUME
    ## rin
    # Neko costume based on Rin
    # thanks SovietSpartan
    mas_clothes_rin = MASClothes(
        "rin",
        "rin",
        MASPoseMap(
            default=True,
            use_reg_for_l=True
        ),
        stay_on_start=True,
        entry_pp=store.mas_sprites._clothes_rin_entry,
        exit_pp=store.mas_sprites._clothes_rin_exit,
        ex_props={
            store.mas_sprites.EXP_C_COST: "o31",
            store.mas_sprites.EXP_C_COSP: True,
            "rin": True #NOTE: This is very very temp until we sort out the hair to work better w/ other outfits
        }
    )
    store.mas_sprites.init_clothes(mas_clothes_rin)
    store.mas_selspr.init_selectable_clothes(
        mas_clothes_rin,
        "Neko Costume",
        "rin",
        "clothes",
        visible_when_locked=False,
        hover_dlg=[
            "~nya?",
            "n-nya..."
        ],
        select_dlg=[
            "Nya!"
        ]
    )

    ### SANTA MONIKA
    ## santa
    # Monika with Santa costume
    # thanks Ryuse
    mas_clothes_santa = MASClothes(
        "santa",
        "santa",
        MASPoseMap(
            default=True,
            use_reg_for_l=True
        ),
        stay_on_start=True,
        entry_pp=store.mas_sprites._clothes_santa_entry,
        exit_pp=store.mas_sprites._clothes_santa_exit,
        ex_props={
            "costume": "d25"
        },
    )
    store.mas_sprites.init_clothes(mas_clothes_santa)
    store.mas_selspr.init_selectable_clothes(
        mas_clothes_santa,
        "Santa Costume",
        "santa",
        "clothes",
        visible_when_locked=False,
        hover_dlg=None,
        select_dlg=[
            "Merry Christmas!",
            "What kind of {i}presents{/i} do you want?",
            "Happy holidays!"
        ]
    )

    ### SEXY SANTA (santa lingerie)
    ## santa_lingerie
    # santa outfit which shows a lot of skin
    #Thanks Velius
    mas_clothes_santa_lingerie = MASClothes(
        "santa_lingerie",
        "santa_lingerie",
        MASPoseMap(
            default=True,
            use_reg_for_l=True
        ),
        stay_on_start=True,
        ex_props={
            store.mas_sprites.EXP_C_BS: True,
            "lingerie": "d25"
        },
        entry_pp=store.mas_sprites._clothes_santa_lingerie_entry,
        exit_pp=store.mas_sprites._clothes_santa_lingerie_exit,
        pose_arms=MASPoseArms({}, def_base=False)
    )
    store.mas_sprites.init_clothes(mas_clothes_santa_lingerie)
    store.mas_selspr.init_selectable_clothes(
        mas_clothes_santa_lingerie,
        "Lingerie (Santa)",
        "santa_lingerie",
        "clothes",
        visible_when_locked=False,
        hover_dlg=None,
        select_dlg=[
            "Would you like to open your present?~",
            "What kind of {i}presents{/i} do you want?",
            "Open your present, ehehe~",
            "All I want for Christmas is you~",
            "Santa baby~",
            "What {i}else{/i} do you want to unwrap?~"
        ]
    )


    ### New Year's Dress
    ## new_years_dress
    # dress Monika wears on New Year's Eve
    #Thanks Orca
    mas_clothes_dress_newyears = MASClothes(
        "new_years_dress",
        "new_years_dress",
        MASPoseMap(
            default=True,
            use_reg_for_l=True,
        ),
        entry_pp=store.mas_sprites._clothes_dress_newyears_entry,
        exit_pp=store.mas_sprites._clothes_dress_newyears_exit,
        stay_on_start=True,
        pose_arms=MASPoseArms({}, def_base=False),
        ex_props={
            store.mas_sprites.EXP_C_BS: True,
        }
    )
    store.mas_sprites.init_clothes(mas_clothes_dress_newyears)
    store.mas_selspr.init_selectable_clothes(
        mas_clothes_dress_newyears,
        "Dress (New Years)",
        "new_years_dress",
        "clothes",
        visible_when_locked=False,
        hover_dlg=None,
        select_dlg=[
            "Are we going somewhere special, [player]?",
            "Very formal!",
            "Any special occasion, [player]?"
        ],
    )

    ### SUNDRESS (WHITE)
    ## sundress_white
    # The casual outfit from vday
    # thanks Orca
    mas_clothes_sundress_white = MASClothes(
        "sundress_white",
        "sundress_white",
        MASPoseMap(
            default=True,
            use_reg_for_l=True,
        ),
        stay_on_start=True,
        entry_pp=store.mas_sprites._clothes_sundress_white_entry,
        exit_pp=store.mas_sprites._clothes_sundress_white_exit,
        pose_arms=MASPoseArms({}, def_base=False),
        ex_props={
            store.mas_sprites.EXP_C_BLS: True,
            store.mas_sprites.EXP_C_BRS: True,
        }
    )
    store.mas_sprites.init_clothes(mas_clothes_sundress_white)
    store.mas_selspr.init_selectable_clothes(
        mas_clothes_sundress_white,
        "Sundress (White)",
        "sundress_white",
        "clothes",
        visible_when_locked=False,
        hover_dlg=None,
        select_dlg=[
            "Are we going anywhere special today, [player]?",
            "I've always loved this outfit...",
        ],
    )

    ### Valentine's Lingerie
    ## vday_lingerie
    # valentines outfit which shows a lot of skin
    #Thanks Orca
    mas_clothes_vday_lingerie = MASClothes(
        "vday_lingerie",
        "vday_lingerie",
        MASPoseMap(
            default=True,
            use_reg_for_l=True,
        ),
        stay_on_start=True,
        ex_props={
            store.mas_sprites.EXP_C_LING: True,
            store.mas_sprites.EXP_C_BS: True,
        },
        pose_arms=MASPoseArms({}, def_base=False)
    )
    store.mas_sprites.init_clothes(mas_clothes_vday_lingerie)
    store.mas_selspr.init_selectable_clothes(
        mas_clothes_vday_lingerie,
        "Lingerie (Pink Lace)",
        "vday_lingerie",
        "clothes",
        visible_when_locked=False,
        hover_dlg=None,
        select_dlg=[
            "Ehehe~",
            "Do you like what you see, [player]?"
        ]
    )

init -1 python:
    # ACCESSORIES (SPR130)
    # Accessories are reprsentation of image objects with properties
    # Pleaes refer to MASAccesory to understand all the properties
    #
    # NAMING SCHEME:
    # mas_acs_<accessory name>
    # NOTE: creating an object reference is optional, EXCEPt if you need to
    #   build a selector object.
    #
    # <accessory name> MUST BE UNIQUE
    #
    # File naming:
    # Accessories should be named like:
    #   acs-<acs identifier/name>-<pose id>-<night suffix>
    #
    # acs name - name of the accessory (shoud be unique)
    # pose id - identifier to map this image to a pose (should be unique
    #       per accessory)
    #
    # NOTE: pleaes preface each accessory with the following commen template
    # this is to ensure we hvae an accurate description of what each accessory
    # is:
    ### HUMAN UNDERSTANDABLE NAME OF ACCESSORY
    ## accessoryidentifiername
    # General description of what the object is, where it is located

    # TODO: this should be sorted by alpha, using the ID

    ### AHOGE BENT
    ## ahoge_bent
    # A bent ahoge
    # thanks Briar Young
    store.mas_sprites.init_acs(MASAccessory(
        "ahoge_bent",
        "ahoge_bent",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="ahoge",
        rec_layer=MASMonika.AFH_ACS,
        priority=7,
    ))

    ### AHOGE CURL
    ## ahoge_curl
    # A curled ahoge
    # thanks Briar Young
    store.mas_sprites.init_acs(MASAccessory(
        "ahoge_curl",
        "ahoge_curl",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="ahoge",
        rec_layer=MASMonika.AFH_ACS,
        priority=7,
    ))

    ### AHOGE DOUBLE
    ## ahoge_double
    # A double ahoge
    # thanks Briar Young
    store.mas_sprites.init_acs(MASAccessory(
        "ahoge_double",
        "ahoge_double",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="ahoge",
        rec_layer=MASMonika.AFH_ACS,
        priority=7,
    ))

    ### AHOGE HEART
    ## ahoge_heart
    # A heart-shaped ahoge
    # thanks Briar Young
    store.mas_sprites.init_acs(MASAccessory(
        "ahoge_heart",
        "ahoge_heart",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="ahoge",
        rec_layer=MASMonika.AFH_ACS,
        priority=7,
    ))

    ### AHOGE LIGHTNING
    ## ahoge_lightning
    # A lightning-shaped ahoge
    # thanks Briar Young
    store.mas_sprites.init_acs(MASAccessory(
        "ahoge_lightning",
        "ahoge_lightning",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="ahoge",
        rec_layer=MASMonika.AFH_ACS,
        priority=7,
    ))

    ### AHOGE SHARP
    ## ahoge_sharp
    # A sharp ahoge
    # thanks Briar Young
    store.mas_sprites.init_acs(MASAccessory(
        "ahoge_sharp",
        "ahoge_sharp",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="ahoge",
        rec_layer=MASMonika.AFH_ACS,
        priority=7,
    ))

    ### AHOGE SIMPLE
    ## ahoge_simple
    # A simple ahoge
    # thanks Briar Young
    store.mas_sprites.init_acs(MASAccessory(
        "ahoge_simple",
        "ahoge_simple",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="ahoge",
        rec_layer=MASMonika.AFH_ACS,
        priority=7,
    ))

    ### AHOGE SMALL
    ## ahoge_small
    # A small ahoge
    # thanks Briar Young
    store.mas_sprites.init_acs(MASAccessory(
        "ahoge_small",
        "ahoge_small",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="ahoge",
        rec_layer=MASMonika.AFH_ACS,
        priority=7,
    ))

    ### AHOGE SWOOP
    ## ahoge_swoop
    # A swooping ahoge
    # NOTE: this one juts out in front so it should be rendered later than
    #   the others.
    # thanks Briar Young
    store.mas_sprites.init_acs(MASAccessory(
        "ahoge_swoop",
        "ahoge_swoop",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="ahoge",
        rec_layer=MASMonika.AFH_ACS,
        priority=13,
    ))

    ### AHOGE TWISTY
    ## ahoge_twisty
    # A twisted ahoge
    # thanks Briar Young
    store.mas_sprites.init_acs(MASAccessory(
        "ahoge_twisty",
        "ahoge_twisty",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="ahoge",
        rec_layer=MASMonika.AFH_ACS,
        priority=7,
    ))

    ### Candy canes
    ## candycane
    # candycane consumable, available to gift before d25
    # Thanks Briar
    mas_acs_candycane = MASAccessory(
        "candycane",
        "candycane",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        stay_on_start=True,
        acs_type="plate",
        mux_type=store.mas_sprites.DEF_MUX_LD,
        keep_on_desk=False
    )
    store.mas_sprites.init_acs(mas_acs_candycane)

    ### Christmascookies
    ## christmas_cookies
    # christmascookies consumable, available to gift before d25
    # Thanks JMO
    mas_acs_christmascookies = MASAccessory(
        "christmas_cookies",
        "christmas_cookies",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        stay_on_start=True,
        acs_type="plate",
        mux_type=store.mas_sprites.DEF_MUX_LD,
        keep_on_desk=False
    )
    store.mas_sprites.init_acs(mas_acs_christmascookies)

    ### HANAMI DANGO
    ## hanami_dango
    # Hanami dango that sits on Monika's desk for her to eat
    # thanks JMO
    mas_acs_hanami_dango = MASAccessory(
        "hanami_dango",
        "hanami_dango",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        stay_on_start=True,
        acs_type="plate",
        mux_type=store.mas_sprites.DEF_MUX_LD,
        keep_on_desk=True
    )
    store.mas_sprites.init_acs(mas_acs_hanami_dango)

    ### COFFEE MUG
    ## mug
    # Coffee mug that sits on Monika's desk
    # thanks Ryuse/EntonyEscX
    mas_acs_mug = MASAccessory(
        "mug",
        "mug",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        stay_on_start=True,
        acs_type="mug",
        mux_type=["mug"],
        keep_on_desk=True
    )
    store.mas_sprites.init_acs(mas_acs_mug)

    ### THERMOS MUG
    ## thermos_mug
    # Thermos Monika uses to bring warm drinks with her when going out with the player
    # Thanks JMO
    mas_acs_thermos_mug = MASAccessory(
        "thermos_mug",
        "thermos_mug",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        stay_on_start=True,
        acs_type="thermos-mug"
    )
    store.mas_sprites.init_acs(mas_acs_thermos_mug)
    store.mas_selspr.init_selectable_acs(
        mas_acs_thermos_mug,
        "Thermos (Just Monika)",
        "thermos_justmonika",
        "thermos-mug"
    )

    ### ROSE EAR ACCESSORY
    ## ear_rose
    # rose that is placed on Monika's ear
    # thanks JMO
    mas_acs_ear_rose = MASAccessory(
        "ear_rose",
        "ear_rose",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        acs_type="left-hair-flower-ear",
        mux_type=[
            "left-hair-flower-ear",
            "left-hair-flower"
        ],
        ex_props={
            "left-hair-strand-eye-level": True,
        },
        priority=20,
        stay_on_start=False,
        rec_layer=MASMonika.PST_ACS,
    )
    store.mas_sprites.init_acs(mas_acs_ear_rose)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ear_rose,
        "Rose",
        "hairflower_rose",
        "left-hair-flower",
        hover_dlg=[
            "TALE AS OLD AS TIME",
        ],
        select_dlg=[
            "TRUE AS IT CAN BE",
        ]
    )

    ### HAIRTIES BRACELET (BROWN)
    ## hairties_bracelet_brown
    # The bracelet Monika wore in the vday outfit
    # thanks Velius
    mas_acs_hairties_bracelet_brown = MASSplitAccessory(
        "hairties_bracelet_brown",
        "hairties_bracelet_brown",
        MASPoseMap(
            p1="1",
            p2="2",
            p3="1",
            p4="4",
            p5="5",
            p6=None,
            p7="1"
        ),
        stay_on_start=True,
        acs_type="wrist-bracelet",
        mux_type=["wrist-bracelet"],
        ex_props={
            "bare wrist": True,
        },
        rec_layer=MASMonika.ASE_ACS,
        arm_split=MASPoseMap(
            default="",
            p1="10",
            p2="5",
            p3="10",
            p4="0",
            p5="10",
            p7="10",
        )
    )
    store.mas_sprites.init_acs(mas_acs_hairties_bracelet_brown)

    ### HEART-SHAPED DESK CHOCOLATES
    ## heartchoc
    # heart-shaped chocolate box to be placed on Monika's desk
    # Thanks JMO
    mas_acs_heartchoc = MASAccessory(
        "heartchoc",
        "heartchoc",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        stay_on_start=False,
        acs_type="chocs",
        mux_type=store.mas_sprites.DEF_MUX_LD,
        keep_on_desk=False
    )
    store.mas_sprites.init_acs(mas_acs_heartchoc)

    ### HOT CHOCOLATE MUG
    ## hotchoc_mug
    # Coffee mug that sits on Monika's desk
    # thanks Ryuse/EntonyEscX
    mas_acs_hotchoc_mug = MASAccessory(
        "hotchoc_mug",
        "hotchoc_mug",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        stay_on_start=True,
        acs_type="mug",
        mux_type=["mug"],
        keep_on_desk=True
    )
    store.mas_sprites.init_acs(mas_acs_hotchoc_mug)

    ### MUSIC NOTE NECKLACE (GOLD)
    ## musicnote_necklace_gold
    # The necklace Monika wore in the vday outfit
    # thanks EntonyEscX
    mas_acs_musicnote_necklace_gold = MASSplitAccessory(
        "musicnote_necklace_gold",
        "musicnote_necklace_gold",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="necklace",
        mux_type=["necklace"],
        ex_props={
            "bare collar": True,
        },
        rec_layer=MASMonika.BSE_ACS,
        arm_split=MASPoseMap(
            default="0",
            use_reg_for_l=True
        )
    )
    store.mas_sprites.init_acs(mas_acs_musicnote_necklace_gold)

    ### Marisa Strandbow
    ## marisa_strandbow
    # Bow to go on Moni's hair strand in the Marisa outfit
    # Thanks SovietSpartan/Orca
    mas_acs_marisa_strandbow = MASAccessory(
        "marisa_strandbow",
        "marisa_strandbow",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="strandbow",
        # muxtype handled by defaults
        ex_props={
            store.mas_sprites.EXP_A_RQHP: store.mas_sprites.EXP_H_TS,
        },
        rec_layer=MASMonika.AFH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_marisa_strandbow)

    ### Marisa witchhat
    ## marisa_witchhat
    # Hat for Moni's Marisa costume
    # Thanks SovietSpartan/Orca
    mas_acs_marisa_witchhat = MASAccessory(
        "marisa_witchhat",
        "marisa_witchhat",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="hat",
        # muxtype handled by defaults
        ex_props={
            store.mas_sprites.EXP_A_RQHP: store.mas_sprites.EXP_H_NT,
            store.mas_sprites.EXP_A_EXCLHP: store.mas_sprites.EXP_H_TB
        },
        rec_layer=MASMonika.AFH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_marisa_witchhat)
    store.mas_selspr.init_selectable_acs(
        mas_acs_marisa_witchhat,
        "Witch Hat", # TODO: add (Marisa) if we ever add another witch hat
        "marisa_witchhat",
        "hat",
        select_dlg=[
            "Ze~",
            "Tea time, tea time. Even if we have coffee, it's tea time. Ehehe~",
            "Eye of newt, toe of frog...",
            "Now where did I leave that broom..."
        ]
    )

    ###Rin bows front
    ##rin_bows_front
    #Hair acs for rin's braided hairstyle (frontine layer)
    #Thanks Briar/SS
    mas_acs_rin_bows_front = MASAccessory(
        "rin_bows_front",
        "rin_bows_front",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="ribbon-front",
        mux_type=["ribbon-front"],
        rec_layer=MASMonika.AFH_ACS,
        priority=20
    )
    store.mas_sprites.init_acs(mas_acs_rin_bows_front)

    ###Rin bows back
    ##rin_bows_back
    #Hair acs for rin's braided hairstyle (back layer)
    #Thanks Briar/SS
    mas_acs_rin_bows_back = MASAccessory(
        "rin_bows_back",
        "rin_bows_back",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="ribbon-back",
        mux_type=["ribbon"],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_rin_bows_back)

    ###Rin ears
    ##rin_ears
    #Ears to wear in rin cosplay
    #Thanks Spikeran1
    mas_acs_rin_ears = MASAccessory(
        "rin_ears",
        "rin_ears",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="headband",
        rec_layer=MASMonika.AFH_ACS,
        priority=5
    )
    store.mas_sprites.init_acs(mas_acs_rin_ears)

    ### Holly Hairclip
    ## holly_hairclip
    # holly hairclip to go with the santa/santa_lingerie outfits
    #Thanks Orca
    mas_acs_holly_hairclip = MASAccessory(
        "holly_hairclip",
        "holly_hairclip",
        MASPoseMap(
            default="0",
            l_default="5"
        ),
        stay_on_start=True,
        acs_type="left-hair-clip",
        # mux type handled by defaults
        rec_layer=MASMonika.AFH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_holly_hairclip)
    store.mas_selspr.init_selectable_acs(
        mas_acs_holly_hairclip,
        "Hairclip (Holly)",
        "holly_hairclip",
        "left-hair-clip",
        select_dlg=[
            "Ready to deck the halls, [player]?"
        ]
    )

    ### FLOWER CROWN
    ## flower_crown
    # flower crown to go with the new year's dress (exclusive to the outfit)
    # Thanks Orca
    mas_acs_flower_crown = MASAccessory(
        "flower_crown",
        "flower_crown",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        acs_type="front-hair-flower-crown",
        priority=12,
        stay_on_start=True,
        rec_layer=MASMonika.AFH_ACS,
    )
    store.mas_sprites.init_acs(mas_acs_flower_crown)

    ### PROMISE RING
    ## promisering
    # Promise ring that can be given to Monika
    mas_acs_promisering = MASSplitAccessory(
        "promisering",
        "promisering",
        MASPoseMap(
            p1=None,
            p2="2",
            p3="3",
            p4=None,
            p5="5",
            p6=None,
            p7=None,
        ),
        stay_on_start=True,
        acs_type="ring",
        rec_layer=MASMonika.ASE_ACS,
        arm_split=MASPoseMap(
            default="",
            p2="10",
            p3="10",
            p5="10"
        ),
        ex_props={
            "bare hands": True
        }
    )
    store.mas_sprites.init_acs(mas_acs_promisering)

    ### QUETZAL PLUSHIE
    ## quetzalplushie
    # Quetzal plushie that sits on Monika's desk
    # thanks aldo
    mas_acs_quetzalplushie = MASAccessory(
        "quetzalplushie",
        "quetzalplushie",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        stay_on_start=False,
        acs_type="plush_q",
        mux_type=["plush_mid"] + store.mas_sprites.DEF_MUX_LD,
        entry_pp=store.mas_sprites._acs_quetzalplushie_entry,
        exit_pp=store.mas_sprites._acs_quetzalplushie_exit,
        keep_on_desk=True
    )
    store.mas_sprites.init_acs(mas_acs_quetzalplushie)

    ### QUETZAL PLUSHIE ANTLERS
    ## quetzalplushie_antlers
    # Antlers for the Quetzal Plushie
    # Thanks Finale
    mas_acs_quetzalplushie_antlers = MASAccessory(
        "quetzalplushie_antlers",
        "quetzalplushie_antlers",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        priority=12,
        stay_on_start=False,
        entry_pp=store.mas_sprites._acs_quetzalplushie_antlers_entry,
        keep_on_desk=True
    )

    ### QUETZAL PLUSHIE (CENTER)
    ## quetzalplushie_mid
    # version of the plushie that is on the center of the desk
    mas_acs_center_quetzalplushie = MASAccessory(
        "quetzalplushie_mid",
        "quetzalplushie_mid",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        stay_on_start=False,
        acs_type="plush_mid",
        mux_type=["plush_q"],
        entry_pp=store.mas_sprites._acs_center_quetzalplushie_entry,
        exit_pp=store.mas_sprites._acs_center_quetzalplushie_exit,
        keep_on_desk=True
    )
    store.mas_sprites.init_acs(mas_acs_center_quetzalplushie)

    ### QUETZAL PLUSHIE SANTA HAT
    ## quetzalplushie_santahat
    # Santa hat for the Quetzal Plushie
    # Thanks Finale
    mas_acs_quetzalplushie_santahat = MASAccessory(
        "quetzalplushie_santahat",
        "quetzalplushie_santahat",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        priority=11,
        stay_on_start=False,
        entry_pp=store.mas_sprites._acs_quetzalplushie_santahat_entry,
        keep_on_desk=True
    )
    store.mas_sprites.init_acs(mas_acs_quetzalplushie_santahat)

    ### QUETZAL PLUSHIE SANTA HAT (CENTER)
    ## quetzalplushie_santahat_mid
    # Santa hat for the Quetzal Plushie
    # Thanks Finale/Legend
    mas_acs_quetzalplushie_center_santahat = MASAccessory(
        "quetzalplushie_santahat_mid",
        "quetzalplushie_santahat_mid",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        priority=11,
        stay_on_start=False,
        entry_pp=store.mas_sprites._acs_center_quetzalplushie_santahat_entry,
        keep_on_desk=True
    )
    store.mas_sprites.init_acs(mas_acs_quetzalplushie_center_santahat)

    ### BLACK RIBBON
    ## ribbon_black
    # Black ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_black = MASAccessory(
        "ribbon_black",
        "ribbon_black",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=["ribbon"],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_black)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_black,
        "Ribbon (Black)",
        "ribbon_black",
        "ribbon",
        hover_dlg=[
            "That's pretty formal, [player]."
        ],
        select_dlg=[
            "Are we going somewhere special, [player]?"
        ]
    )

    ### BLANK RIBBON
    ## ribbon_blank
    # Blank ribbon for use in ponytail/bun with custom outfits
    mas_acs_ribbon_blank = MASAccessory(
        "ribbon_blank",
        "ribbon_blank",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=[
            "ribbon",
            "bow",
        ],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_blank)

    ### BLUE RIBBON
    ## ribbon_blue
    # Blue ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_blue = MASAccessory(
        "ribbon_blue",
        "ribbon_blue",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=[
            "ribbon",
            "bow",
        ],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_blue)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_blue,
        "Ribbon (Blue)",
        "ribbon_blue",
        "ribbon",
        hover_dlg=[
            "Like the ocean..."
        ],
        select_dlg=[
            "Great choice, [player]!"
        ]
    )

    ### DARK PURPLE RIBBON
    ## ribbon_dark_purple
    # Dark purple ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_darkpurple = MASAccessory(
        "ribbon_dark_purple",
        "ribbon_dark_purple",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=[
            "ribbon",
            "bow",
        ],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_darkpurple)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_darkpurple,
        "Ribbon (Dark Purple)",
        "ribbon_dark_purple",
        "ribbon",
        hover_dlg=[
            "I love that color!"
        ],
        select_dlg=[
            "Lavender is a nice change of pace."
        ]
    )

    ### EMERALED RIBBON
    ## ribbon_emeraled
    # Emerald ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_emerald = MASAccessory(
        "ribbon_emerald",
        "ribbon_emerald",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=[
            "ribbon",
            "bow",
        ],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_emerald)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_emerald,
        "Ribbon (Emerald)",
        "ribbon_emerald",
        "ribbon",
        hover_dlg=[
            "I've always loved this color...",
        ],
        select_dlg=[
            "It's just like my eyes!"
        ]
    )

    ### WHITE RIBBON
    ## ribbon_def
    # White ribbon (the default) for ponytail/bun hairstyles
    mas_acs_ribbon_def = MASAccessory(
        "ribbon_def",
        "ribbon_def",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=[
            "ribbon",
            "bow",
        ],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_def)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_def,
        "Ribbon (White)",
        "ribbon_def",
        "ribbon",
        hover_dlg=[
            "Do you miss my old ribbon, [player]?"
        ],
        select_dlg=[
            "Back to the classics!"
        ]
    )

    ### GRAY RIBBON
    ## ribbon_gray
    # Gray ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_gray = MASAccessory(
        "ribbon_gray",
        "ribbon_gray",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=[
            "ribbon",
            "bow",
        ],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_gray)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_gray,
        "Ribbon (Gray)",
        "ribbon_gray",
        "ribbon",
        hover_dlg=[
            "Like a warm, rainy day..."
        ],
        select_dlg=[
            "That's a really unique color, [player]."
        ]
    )

    ### GREEN RIBBON
    ## ribbon_green
    # Green ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_green = MASAccessory(
        "ribbon_green",
        "ribbon_green",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=[
            "ribbon",
            "bow",
        ],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_green)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_green,
        "Ribbon (Green)",
        "ribbon_green",
        "ribbon",
        hover_dlg=[
            "That's a lovely color!"
        ],
        select_dlg=[
            "Green, just like my eyes!"
        ]
    )

    ### LIGHT PURPLE RIBBON
    ## ribbon_light_purple
    # Light purple ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_lightpurple = MASAccessory(
        "ribbon_light_purple",
        "ribbon_light_purple",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=[
            "ribbon",
            "bow",
        ],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_lightpurple)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_lightpurple,
        "Ribbon (Light Purple)",
        "ribbon_light_purple",
        "ribbon",
        hover_dlg=[
            "This purple looks pretty nice, right [player]?"
        ],
        select_dlg=[
            "Really has a spring feel to it."
        ]
    )

    ### PEACH RIBBON
    ## ribbon_peach
    # Peach ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_peach = MASAccessory(
        "ribbon_peach",
        "ribbon_peach",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=[
            "ribbon",
            "bow",
        ],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_peach)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_peach,
        "Ribbon (Peach)",
        "ribbon_peach",
        "ribbon",
        hover_dlg=[
            "That's beautiful!"
        ],
        select_dlg=[
            "Just like autumn leaves..."
        ]
    )

    ### PINK RIBBON
    ## ribbon_pink
    # Pink ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_pink = MASAccessory(
        "ribbon_pink",
        "ribbon_pink",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=[
            "ribbon",
            "bow",
        ],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_pink)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_pink,
        "Ribbon (Pink)",
        "ribbon_pink",
        "ribbon",
        hover_dlg=[
            "Looks cute, right?"
        ],
        select_dlg=[
            "Good choice!"
        ]
    )

    ### PLATINUM RIBBON
    ## ribbon_platinum
    # Platinum ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_platinum = MASAccessory(
        "ribbon_platinum",
        "ribbon_platinum",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=["ribbon"],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_platinum)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_platinum,
        "Ribbon (Platinum)",
        "ribbon_platinum",
        "ribbon",
        hover_dlg=[
            "That's an interesting color, [player].",
        ],
        select_dlg=[
            "I'm quite fond of it, actually."
        ]
    )

    ### RED RIBBON
    ## ribbon_red
    # Red ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_red = MASAccessory(
        "ribbon_red",
        "ribbon_red",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=["ribbon"],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_red)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_red,
        "Ribbon (Red)",
        "ribbon_red",
        "ribbon",
        hover_dlg=[
            "Red is a beautiful color!"
        ],
        select_dlg=[
            "Just like roses~"
        ]
    )

    ### RUBY RIBBON
    ## ribbon_ruby
    # Ruby ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_ruby = MASAccessory(
        "ribbon_ruby",
        "ribbon_ruby",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=["ribbon"],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_ruby)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_ruby,
        "Ribbon (Ruby)",
        "ribbon_ruby",
        "ribbon",
        hover_dlg=[
            "That's a beautiful shade of red."
        ],
        select_dlg=[
            "Doesn't it look pretty?"
        ]
    )

    ### SAPPHIRE RIBBON
    ## ribbon_sapphire
    # Sapphire ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_sapphire = MASAccessory(
        "ribbon_sapphire",
        "ribbon_sapphire",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=["ribbon"],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_sapphire)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_sapphire,
        "Ribbon (Sapphire)",
        "ribbon_sapphire",
        "ribbon",
        hover_dlg=[
            "Like a clear summer sky..."
        ],
        select_dlg=[
            "Nice choice, [player]!"
        ]
    )

    ### SILVER RIBBON
    ## ribbon_silver
    # Silver ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_silver = MASAccessory(
        "ribbon_silver",
        "ribbon_silver",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=["ribbon"],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_silver)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_silver,
        "Ribbon (Silver)",
        "ribbon_silver",
        "ribbon",
        hover_dlg=[
            "I like the look of this one.",
            "I've always loved silver."
        ],
        select_dlg=[
            "Nice choice, [player]."
        ]
    )

    ### TEAL RIBBON
    ## ribbon_teal
    # Teal ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_teal = MASAccessory(
        "ribbon_teal",
        "ribbon_teal",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=["ribbon"],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_teal)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_teal,
        "Ribbon (Teal)",
        "ribbon_teal",
        "ribbon",
        hover_dlg=[
            "Looks really summer-y, right?"
        ],
        select_dlg=[
            "Just like a summer sky."
        ]
    )

    ### WINE RIBBON
    ## ribbon_wine
    # Wine ribbon for ponytail/bun hairstyles. This matches the santa outfit
    # thanks Ryuse/Ronin
    mas_acs_ribbon_wine = MASAccessory(
        "ribbon_wine",
        "ribbon_wine",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=["ribbon"],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_wine)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_wine,
        "Ribbon (Wine)",
        "ribbon_wine",
        "ribbon",
        hover_dlg=[
            "That's a great color!"
        ],
        select_dlg=[
            "Formal! Are you taking me somewhere special, [player]?"
        ]
    )

    ### YELLOW RIBBON
    ## ribbon_yellow
    # Yellow ribbon for ponytail/bun hairstyles
    # thanks Ronin
    mas_acs_ribbon_yellow = MASAccessory(
        "ribbon_yellow",
        "ribbon_yellow",
        MASPoseMap(
            default="0",
            p5="5"
        ),
        stay_on_start=True,
        acs_type="ribbon",
        mux_type=["ribbon"],
        rec_layer=MASMonika.BBH_ACS
    )
    store.mas_sprites.init_acs(mas_acs_ribbon_yellow)
    store.mas_selspr.init_selectable_acs(
        mas_acs_ribbon_yellow,
        "Ribbon (Yellow)",
        "ribbon_yellow",
        "ribbon",
        hover_dlg=[
            "This color reminds me of a nice summer day!"
        ],
        select_dlg=[
            "Great choice, [player]!"
        ]
    )

    ### DESK ROSES
    ## roses
    # roses to be placed on Monika's desk
    # Thanks JMO
    mas_acs_roses = MASAccessory(
        "roses",
        "roses",
        MASPoseMap(
            default="0",
            use_reg_for_l=True
        ),
        priority=11,
        stay_on_start=False,
        acs_type="flowers",
        keep_on_desk=True
    )
    store.mas_sprites.init_acs(mas_acs_roses)

#### ACCCESSORY VARIABLES (SPR230)
# variables that accessories may need for enabling / disabling / whatever
# please comment the groups and usage like so:
### accessory name
# <var>
# <var comment>

### QUETZAL PLUSHIE ###
default persistent._mas_acs_enable_quetzalplushie = False
# True enables plushie, False disables plushie

### PROMISE RING ###
default persistent._mas_acs_enable_promisering = False
# True enables promise ring, False disables promise ring
