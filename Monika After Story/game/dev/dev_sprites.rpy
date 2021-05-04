# sprite testing code

init 100 python:
    def mas_test_sitting():
        dd = {
            "clothing": "def",
            "hair": "def",
            "eyebrows": "mid",
            "eyes": "normal",
            "nose": "def",
            "mouth": "smile"
        }

        return [
            store.mas_sprites._ms_sitting(
                isnight=False,
                arms="crossed",
                **dd
            ),
            store.mas_sprites._ms_sitting(
                isnight=True,
                arms="crossed",
                **dd
            ),
            store.mas_sprites._ms_sitting(
                isnight=False,
                lean="def",
                **dd
            ),
            store.mas_sprites._ms_sitting(
                isnight=True,
                lean="def",
                **dd
            ),
            store.mas_sprites._ms_sitting(
                isnight=False,
                arms="crossed",
                eyebags="def",
                sweat="def",
                blush="def",
                tears="def",
                emote="def",
                **dd
            ),
            store.mas_sprites._ms_sitting(
                isnight=True,
                arms="crossed",
                eyebags="def",
                sweat="def",
                blush="def",
                tears="def",
                emote="def",
                **dd
            ),
            store.mas_sprites._ms_sitting(
                isnight=True,
                lean="def",
                eyebags="def",
                sweat="def",
                blush="def",
                tears="def",
                emote="def",
                **dd
            )
        ]

    def mas_supertest():
        abc = open("test.log", "w")
        tests = mas_test_sitting()

        for line in tests:
            abc.write(line + "\n")

        abc.close()


    def mas_matrix_cache_report():
        mb_size = 1000.0
        sum_line = "{0}: {1} - {2:.3f} KB\n"

        def _cro(cache, name, cache_log):
            cache_size = 0

            # header
            cache_log.write("\n\n==================================\n")
            cache_log.write("# Logging cache for {0}\n".format(name))
            cache_log.write("==================================\n")

            # output elements
            for img_key in cache:
                item = cache[img_key]
                cache_log.write("{0}: {1}\n".format(img_key, item))
                cache_size += sys.getsizeof(item)

            return cache_size

        # build temp dict for this
        names = (
            "Face",
            "Arms",
            "Body",
            "Hair",
            "ACS",
            "TableChair",
            "Highlight",
        )
        name_map = {}
        for index in range(len(names)):
            name_map[names[index]] = store.mas_sprites._gc(index+1)

        with open("cache_report.log", "w") as cache_log:
            # write each caceh out
            size_map = {}
            for name in names:
                size_map[name] = _cro(name_map[name], name, cache_log)

            # summary report
            cache_log.write("\n\n---- Size Summary ----\n")
            for name in names:
                cache_log.write(sum_line.format(
                    name,
                    len(name_map[name]),
                    size_map[name] / mb_size
                ))


init -1 python:
    dev_mas_hair_test = MASHair(
        "dev_test",
        "dev_test",
        MASPoseMap(
            default=True,
            use_reg_for_l=True,
        ),
        ex_props={
            "ribbon": True,
        },
        mpm_mid=MASPoseMap(
            default=True,
            l_default=False,
        )
    )
    store.mas_sprites.init_hair(dev_mas_hair_test)
    store.mas_selspr.init_selectable_hair(
        dev_mas_hair_test,
        "DEV TEST",
        "dev_test",
        "hair",
        select_dlg=[
            "I AM A TEST"
        ]
    )


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_acs_pose_test",
            category=["dev"],
            prompt="ACCESSORY POSE TEST",
            pool=True,
            unlocked=True
        )
    )

label dev_acs_pose_test:
    m 1hua "Hello there!"
    m 1eua "I'm going to test the wonderful accessory system."
    m "First, I'll clear all current accessories."
    $ monika_chr.remove_all_acs()
    m 6sub "I'm going to put on the ring now~"
    $ monika_chr.wear_acs_pst(mas_acs_promisering)
    m 1eua "You should see it now!"
    m 2eua "And it's gone."
    m 3eua "Here it is!"
    m 4eua "Still here~"
    m 5eua "And it's gone."
    m 6sub "Still gone..."
    m "And let's take it all off now~"
    $ monika_chr.remove_all_acs()
    m "Please remember to try it at different times!"
    m 1hua "We wouldn't want anything missing now, would we?"
    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_sp_obj_pp_test",
            category=["dev"],
            prompt="SPRITE PROG POINT TEST",
            pool=True,
            unlocked=True
        )
    )

label dev_sp_obj_pp_test:
    python:
        # pull custom sprites with progpoints
        custom_acs = [
            acs.name
            for acs in store.mas_sprites.ACS_MAP.values()
            if acs.is_custom and acs.hasprogpoints()
        ]
        custom_hair = [
            hair.name
            for hair in store.mas_sprites.HAIR_MAP.values()
            if hair.is_custom and hair.hasprogpoints()
        ]
        custom_clothes = [
            clothes.name
            for clothes in store.mas_sprites.CLOTH_MAP.values()
            if clothes.is_custom and clothes.hasprogpoints()
        ]

        # sort these
        custom_acs.sort()
        custom_hair.sort()
        custom_clothes.sort()

        # now reform list for menu usage, with sprite objects
        custom_acs = [
            (name, store.mas_sprites.ACS_MAP[name], False, False)
            for name in custom_acs
        ]
        custom_hair = [
            (name, store.mas_sprites.HAIR_MAP[name], False, False)
            for name in custom_hair
        ]
        custom_clothes = [
            (name, store.mas_sprites.CLOTH_MAP[name], False, False)
            for name in custom_clothes
        ]

        # create the starting menu
        top_level_menu = [
            ("ACS", custom_acs, False, False),
            ("HAIR", custom_hair, False, False),
            ("CLOTHES", custom_clothes, False, False)
        ]

        # reutrn entry
        returner = ("Back", False, False, False, 20)

        # message constants
        ENTRY_ERR = "entry point failed!: {0}"
        EXIT_ERR = "exit point failed!: {0}"

        # save monika chr state
        monika_state = monika_chr.save_state(True, True, True)

    # FALL THROUGH
    m 1hua "going to test prog points."
    m 1eua "NOTE: this will {b}NOT{/b} change any of my oufits, hair, or acs."
    m "but side effects may occur."

label dev_sp_obj_pp_test_top:

    call screen mas_gen_scrollable_menu(top_level_menu, mas_ui.SCROLLABLE_MENU_MEDIUM_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, returner)

    if _return is False:
        # restore state
        $ monika_state = monika_chr.load_state(monika_state)
        return

    $ selected_sp_list = _return

label dev_sp_obj_pp_test_sp_select:

    # otherwise, create menu using the given list
    call screen mas_gen_scrollable_menu(selected_sp_list, mas_ui.SCROLLABLE_MENU_MEDIUM_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, returner)

    if _return is False:
        jump dev_sp_obj_pp_test_top

    # otherwise, we have a selected sprite object, lets attempt this
    python:
        sp_obj_to_test = _return

        kwargs = {
            "prev_clothes": monika_chr.clothes,
            "new_clothes": monika_chr.clothes,
            "prev_hair": monika_chr.hair,
            "new_hair": monika_chr.hair,
        }

        if sp_obj_to_test.entry_pp is not None:
            try:
                sp_obj_to_test.entry(monika_chr, **kwargs)
                renpy.show("monika 1hua")
                renpy.say(m, "entry passed!")
            except Exception as e:
                renpy.show("monika 1ektsc")
                renpy.say(m, ENTRY_ERR.format(e))

        if sp_obj_to_test.exit_pp is not None:
            try:
                sp_obj_to_test.exit(monika_chr, **kwargs)
                renpy.show("monika 1hua")
                renpy.say(m, "exit passed!")
            except Exception as e:
                renpy.show("monika 1ektsc")
                renpy.say(m, EXIT_ERR.format(e))

    show monika 1eua

    jump dev_sp_obj_pp_test_sp_select


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_empty_desk_test",
            category=["dev"],
            prompt="TEST EMPTY DESK",
            pool=True,
            unlocked=True
        )
    )

label dev_empty_desk_test:
    m 1eua "I will test empty desk"
    m 2eua "First i will wear the plush"
    $ monika_chr.wear_acs(mas_acs_quetzalplushie)
    m 1eua "then i will show the empty desk but behind me"
    show emptydesk at i11 zorder 9
    m 1eua "now i will fade away"
    hide monika with dissolve
    m 1eua "i should be gone, but asc should be there"
    m 2eua "now i will appear"
    $ renpy.show("monika 1eua", tag="monika", at_list=[i11], zorder=MAS_MONIKA_Z)
    $ renpy.with_statement(dissolve)
    m 1eua "I am back"
    hide emptydesk
    m 1eua "i hid the empty desk"
    $ monika_chr.remove_acs(mas_acs_quetzalplushie)
    m 2eua "plush gone"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_empty_desk_test_labels",
            category=["dev"],
            prompt="TEST EMPTY DESK (using transition labels)",
            pool=True,
            unlocked=True
        )
    )

label dev_empty_desk_test_labels:
    m 1eua "I will test empty desk with transition labels"
    m 2eua "First i will wear the plush"
    $ monika_chr.wear_acs(mas_acs_quetzalplushie)

    m 1eua "now i will hide"
    call mas_transition_to_emptydesk

    m "i am gone. but i will return with crossed arms and a diff exp"
    call mas_transition_from_emptydesk("monika 2tfu")

    m "i am here, but now to remove plush"
    $ monika_chr.remove_acs(mas_acs_quetzalplushie)
    m 2eua "plush gone"
    m "try with zoom"
    return

## dev functions for mas sprites that WILL cause exceptions

init -2 python in mas_sprites:

    def _hair__testingxcp_entry(_moni_chr, **kwargs):
        raise Exception("HAIR ENTRY")

    def _hair__testingxcp_exit(_moni_chr, **kwargs):
        raise Exception("HAIR EXIT")

    def _clothes__testingxcp_entry(_moni_chr, **kwargs):
        raise Exception("CLOTHES ENTRY")

    def _clothes__testingxcp_exit(_moni_chr, **kwargs):
        raise Exception("CLOTHES EXIT")

    def _acs__testingxcp_entry(_moni_chr, **kwargs):
        raise Exception("ACS ENTRY")

    def _acs__testingxcp_exit(_moni_chr, **kwargs):
        raise Exception("ACS EXIT")

init python:
    if persistent._mas_dev_ahoge is None:
        persistent._mas_dev_ahoge = config.developer

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_ahoge_test",
            category=["dev"],
            prompt="TEST AHOGES",
            pool=True,
            unlocked=True
        )
    )

label dev_ahoge_test:

    m 2tfblp "I test ahoges now. if wearing hat, it will be removed. zoom out if u want."
    m "dlg will dismiss auto, no need to click"

    $ ahoges = store.mas_sprites.get_acs_of_type("ahoge")
    $ index = 0
    while index < len(ahoges):
        $ monika_chr._set_ahoge(ahoges[index], force_wear=True)
        $ ahoge_name = ahoges[index].name
        m 6nkd "this is [ahoge_name]{w=1}{nw}"
        $ index += 1

    m 1eua "now we are done"

    $ monika_chr.remove_all_acs_in("ahoge")

    return
