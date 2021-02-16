# unit testing module
# NOTE: no framework for now

init -1 python in mas_dev_unit_tests:
    import store
    import store.mas_ev_data_ver as medv

    unit_tests = [
#        ("Event - yearAdjust", "dev_unit_test_event_yearadjust", False, False),
        ("MASHistorySaver", "dev_unit_test_mhs", False, False),
        ("MASHistorySaver - correct_pbday_mhs", "dev_unit_test_mhs_cpm", False, False),
        ("UTC APIs", "dev_unit_test_utc_api", False, False),
    ]

    class MASUnitTest(object):
        """
        Simple class to represent a test
        """

        def __init__(self, test_name, outcome, expected, actual, ovrstr=None):
            """
            Constructor for a MASUnitTest

            IN:
                test_name - name of the test
                outcome - outcome of the test (True or false)
                expected - expected value of the test
                actual - actual value of the test
                ovrstr - if passed, then we display this instead of
                    the standard expected/actual string
            """
            self.test_name = test_name
            self.outcome = outcome
            self.expected = expected
            self.actual = actual
            self.ovrstr = ovrstr

        def __str__(self):
            """
            toString. Format is:
            <testname>: (pass/FAIL) | <expected> -> <actual>
            """
            if self.outcome:
                pass_str = "pass"
            else:
                pass_str = "FAIL"

            if self.ovrstr is None:
                ea_str = "{0} -> {1}".format(
                    str(self.expected),
                    str(self.actual)
                )
            else:
                ea_str = self.ovrstr

            return "{0}: {1} | {2}".format(
                str(self.test_name),
                pass_str,
                ea_str
            )

        def failed(self):
            """
            Returns True if this test failed, false if passsed
            """
            return not self.outcome

        def passed(self):
            """
            Returns True if this test passed, false if failed
            """
            return self.outcome

    class MASUnitTester(object):
        """
        Simple class for running asserts
        """
        LEN_STR = "len mismatch: expected {0} -> actual {1}"
        KEY_STR = "expected key {0}, not found in actual"
        KEY_STR_A = "extra keys found in actual: {0}"

        def __init__(self):
            self.setupTests()

        def __str__(self):
            return "\n".join(self.tests)

        def _assertDictEqual(self, expected, actual):
            """
            Internal dict assertion. Assumes that given items are dicts.

            IN:
                expected - expected value
                actual - actual value

            RETURNS: True if equal, False if not
            """
            # lengths must be the same
            if len(expected) != len(actual):
                self.tests.append(MASUnitTest(
                    self.test_name,
                    False,
                    expected,
                    actual,
                    ovrstr=self.LEN_STR.format(len(expected), len(actual))
                ))
                return False

            # now check keys + values 
            a_keys = sorted(actual.keys())
            for e_key in expected:
                
                if e_key not in a_keys:
                    self.tests.append(MASUnitTest(
                        self.test_name,
                        False,
                        e_key,
                        None,
                        ovrstr=self.KEY_STR.format(e_key)
                    ))
                    return False

                # pop key off 
                a_keys.remove(e_key)
                if not self.assertEqual(expected[e_key], actual[e_key]):
                    return False

            # if any keys remain in a, then we had a mismatch 
            if len(a_keys) > 0:
                self.tests.append(MASUnitTest(
                    self.test_name,
                    False,
                    expected,
                    actual,
                    ovrstr=self.KEY_STR_A.format(a_keys)
                ))
                return False

            return True

        def _assertListEqual(self, expected, actual):
            """
            Internal list assertion. Assumes that the given items are lists.

            IN:
                expected - expected value
                actual - actual value

            RETURNS: True if equal, False if not
            """
            # lengths must be the same
            if len(expected) != len(actual):
                self.tests.append(MASUnitTest(
                    self.test_name,
                    False,
                    expected,
                    actual,
                    ovrstr=self.LEN_STR.format(len(expected), len(actual))
                ))
                return False

            # otherwise check each element
            for index in range(len(expected)):
                if not self.assertEqual(expected[index], actual[index]):
                    return False

            return True

        def assertDictEqual(self, expected, actual):
            """
            Asserts if two dicts are equal and contain equal items

            If expected/actual are not dict, assertListEqual is used
            this is recursive.
            """
            if (
                    medv._verify_dict(expected, False)
                    and medv._verify_dict(actual, False)
            ):
                return self._assertDictEqual(expected, actual)

            # otherwise use assEqual
            return self.assertEqual(expected, actual)

        def assertEqual(self, expected, actual):
            """
            Asserts if the two items are equal

            IN:
                expected - expected value
                actual - actual value

            RETURNS: True if equal, False if not
            """
            # First, delegate to the correct type
            if (
                    medv._verify_dict(expected, False)
                    and medv._verify_dict(actual, False)
            ):
                return self._assertDictEqual(expected, actual)

            elif (
                    medv._verify_list(expected, False)
                    and medv._verify_list(actual, False)
            ):
                return self._assertListEqual(expected, actual)

            # otherwise, we compare the two directly
            outcome = expected == actual
            self.tests.append(MASUnitTest(
                self.test_name,
                outcome,
                expected,
                actual
            ))
            return outcome

        def assertFalse(self, actual):
            """
            Asserts if the given value is False

            IN:
                actual - value to check

            RETURNS: True if False, False if not
            """
            outcome = not bool(actual)
            self.tests.append(MASUnitTest(
                self.test_name,
                outcome,
                False,
                bool(actual)
            ))
            return outcome

        def assertIdentity(self, expected, actual):
            """
            Asserts if the two items point to the same thing

            IN:
                expected - expected item
                actual - actual item

            RETURNS: True if the same reference, False if not
            """
            outcome = actual is expected
            self.tests.append(MASUnitTest(
                self.test_name,
                outcome,
                expected,
                actual
            ))
            return outcome

        def assertIsNone(self, actual):
            """
            Asserts if the given item is None

            IN:
                actual - value to check

            RETURNS: True if None, False if not
            """
            outcome = actual is None
            self.tests.append(MASUnitTest(
                self.test_name,
                outcome,
                None,
                actual
            ))
            return outcome

        def assertIsNotNone(self, actual):
            """
            Asserts if the given item is not None

            IN:
                actual - value to check

            RETURNS: True if not None, False if None
            """
            outcome = actual is not None
            self.tests.append(MASUnitTest(
                self.test_name,
                outcome,
                "not None",
                actual
            ))
            return outcome

        def assertListEqual(self, expected, actual):
            """
            Asserts if two lists are equal and contain equal items

            if expected/actual are not list, we use assertEqual.

            IN:
                expected - expected value
                actual - actual value

            RETURNS: True if equal, False if not
            """
            if (
                    medv._verify_list(expected, False)
                    and medv._verify_list(actual, False)
            ):
                return self._assertListEqual(expected, actual)

            # otherwise, use assertEqual, which should fail in most
            # circumstances
            return self.assertEqual(expected, actual)

        def assertTrue(self, actual):
            """
            Asserts if the given value is True

            IN:
                actual - value to check

            RETURNS: True if True, False if not
            """
            outcome = bool(actual)
            self.tests.append(MASUnitTest(
                self.test_name,
                outcome,
                True,
                bool(actual)
            ))
            return outcome

        def cleanTest(self):
            """
            Cleans up the last test
            """
            self.test_name = ""

        def concludeTests(self):
            """
            Concludes testing by sorting tests by results

            RETURNS:
                tuple of the following format:
                [0] - list of passed tests
                [1] - list of failed tests
            """
            passed_tests = []
            failed_tests = []
            for test in self.tests:
                if test.passed():
                    passed_tests.append(test)
                else:
                    failed_tests.append(test)

            return passed_tests, failed_tests

        def prepareTest(self, test_name):
            """
            Prepares a test by setting test name

            IN:
                test_name - name of next test
            """
            self.test_name = test_name

        def setupTests(self):
            """
            Sets up testing
            """
            self.test_name = ""
            self.tests = []

init 10 python in mas_dev_unit_tests:
    from store.mas_ui import SCROLLABLE_MENU_TALL_AREA, SCROLLABLE_MENU_XALIGN


label dev_unit_tests_show_pass:
    m 1hua "passed"
    return

label dev_unit_tests_show_fail:
    m 1ektsc "!!!FAILED!!!"
    return 

label dev_unit_tests_show_msgs(msg_list, format_text=False):
    $ index = 0
    while index < len(msg_list):
        $ this_msg = msg_list[index]
        if format_text:
            $ this_msg = renpy.substitute(this_msg)
        m 1eua "[this_msg]"
        $ _history_list.pop()
        $ index += 1
    return


label dev_unit_tests_show_items(item_list):
    $ index = 0
    while index < len(item_list):
        $ this_msg = str(item_list[index])
        m 1eua "[this_msg]"
        $ index += 1
    return


label dev_unit_tests_finish_test(mhs_tester):
    python:
        passed, failed = mhs_tester.concludeTests()
        failed_test_count = len(failed)
        passed_test_count = len(passed)

    if failed_test_count > 0:
        m 1ektsc "[failed_test_count] test failed."
        call dev_unit_tests_show_items(failed)

    else:
        m 1hua "All [passed_test_count] tests passed!"

    return


init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="dev_unit_tests",
            category=["dev"],
            prompt="UNIT TESTS",
            pool=True,
            unlocked=True
        )
    )


label dev_unit_tests:
    $ final_item = ("RETURN", False, False, False, 20)
    call screen mas_gen_scrollable_menu(store.mas_dev_unit_tests.unit_tests, store.mas_dev_unit_tests.SCROLLABLE_MENU_TALL_AREA, store.mas_dev_unit_tests.SCROLLABLE_MENU_XALIGN, final_item)

    if _return == "RETURN":
        return

    if renpy.has_label(_return):
        call expression _return
        m 1tuu "Unit test over"
        jump dev_unit_tests

    return


## unit tests

label dev_unit_test_event_yearadjust:
    m "Running Tests..."
    python:
        def add_years(in_dt, diff):
            return store.mas_utils.add_years(in_dt, diff)

        eya_tester = store.mas_dev_unit_tests.MASUnitTester()

        eya_tester.prepareTest("is current")
        now_dt = datetime.datetime.now()
        start_dt = now_dt - datetime.timedelta(days=1)
        end_dt = now_dt + datetime.timedelta(days=1)
        expected = (start_dt, end_dt, False)
        actual = Event._yearAdjust(start_dt, end_dt, [])
        eya_tester.assertEqual(expected, actual)

        eya_tester.prepareTest("is current, same as start")
        now_dt = datetime.datetime.now()
        start_dt = now_dt
        end_dt = now_dt + datetime.timedelta(days=1)
        expected = (start_dt, end_dt, False)
        actual = Event._yearAdjust(start_dt, end_dt, [])
        eya_tester.assertEqual(expected, actual)

        eya_tester.prepareTest("is current, no years, forced")
        now_dt = datetime.datetime.now()
        start_dt = now_dt - datetime.timedelta(days=1)
        end_dt = now_dt + datetime.timedelta(days=1)
        expected = (add_years(start_dt, 1), add_years(end_dt, 1), True)
        actual = Event._yearAdjust(start_dt, end_dt, [], force=True)
        eya_tester.assertEqual(expected, actual)

        eya_tester.prepareTest("before now, same year")
        now_dt = datetime.datetime.now()
        start_dt = now_dt - datetime.timedelta(days=10)
        end_dt = now_dt - datetime.timedelta(days=5)
        expected = (add_years(start_dt, 1), add_years(end_dt, 1), True)
        actual = Event._yearAdjust(start_dt, end_dt, [])
        eya_tester.assertEqual(expected, actual)

        eya_tester.prepareTest("before now, diff year")
        now_dt = datetime.datetime.now()
        start_dt = now_dt - datetime.timedelta(days=400)
        end_dt = now_dt - datetime.timedelta(days=380)
        expected = (add_years(start_dt, 2), add_years(end_dt, 2), True)
        actual = Event._yearAdjust(start_dt, end_dt, [])
        eya_tester.assertEqual(expected, actual)       

        eya_tester.prepareTest("ahead now, same year")
        now_dt = datetime.datetime.now()
        start_dt = now_dt + datetime.timedelta(days=5)
        end_dt = now_dt + datetime.timedelta(days=10)
        expected = (start_dt, end_dt, False)
        actual = Event._yearAdjust(start_dt, end_dt, [])
        eya_tester.assertEqual(expected, actual)              

        eya_tester.prepareTest("ahead now, diff year")
        now_dt = datetime.datetime.now()
        start_dt = now_dt + datetime.timedelta(days=380)
        end_dt = now_dt + datetime.timedelta(days=400)
        expected = (add_years(start_dt, -1), add_years(end_dt, -1), True)
        actual = Event._yearAdjust(start_dt, end_dt, [])
        eya_tester.assertEqual(expected, actual)

        # TODO: finish these tests. for now im tired and this function hasnt
        #   been changed enough that we actual need this.



    return

label dev_unit_test_json_masposemap:
    m "Running Tests..."
    python:
        import copy

        def gen_data(jgroup, jdata):
            data = {}
            for index in range(len(jgroup)):
                data[jgroup[index]] = jdata[index]
            return data

        def gen_both(bdata):
            return gen_data(MASPoseArms.J_NAME_BOTH, bdata)

        def gen_left(ldata):
            return gen_data(MASPoseArms.J_NAME_LEFT, ldata)

        def gen_right(rdata):
            return gen_data(MASPoseArms.J_NAME_RIGHT, rdata)       

        def arms_both(extra=False):
            data = gen_both(("both_pa", True, True))
            if extra:
                data.update({
                    "extra": 123,
                    "extra2": 69,
                })
            return data

        def arms_lr(extra=False):
            data = gen_left(("left_pa", True, True))
            data.update(gen_right(("right_pa", True, True)))
            if extra:
                data.update({
                    "extra": 123,
                    "extra2": 10,
                })
            return data

        prop_mpm_type = "mpm_type"
        prop_default = "default"
        prop_l_default = "l_default"
        prop_urfl = "use_reg_for_l"
        prop_p1 = "p1"
        prop_p2 = "p2"
        prop_p3 = "p3"
        prop_p4 = "p4"
        prop_p5 = "p5"
        prop_p6 = "p6"
        pose1 = "steepling"
        pose2 = "crossed"
        pose3 = "restleftpointright"
        pose4 = "pointright"
        pose5 = "def|def"
        pose6 = "down"
        as_zero = "0"
        as_one = "1"
        as_star = "*"
        as_null = ""
        pa_both = "both_pa"
        pa_left = "left_pa"
        pa_right = "right_pa"
        ic_one = "1"
        ic_zero = "0"
        ic_custom = "special"

        mpm_tester = store.mas_dev_unit_tests.MASUnitTester()

        mpm_tester.prepareTest("no data passed")
        test_data = {}
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("bad mpm type")
        test_data = {
            prop_mpm_type: "bad"
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("invalid mpm")
        test_data = {
            prop_mpm_type: -1
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("bad use reg for l type")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_urfl: 10
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("valid types")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
        }
        valid_types = (MASPoseMap.MPM_TYPE_FB, MASPoseMap.MPM_TYPE_IC)
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0, valid_types)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(1, len(log))

        # testing all mpm type 0 interactions
        mpm_tester.prepareTest("mpm type 0, no props")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_ED, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 0, no props, default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_default: True
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_ED, actual._mpm_type)
        mpm_tester.assertTrue(actual.get(pose1, False))
        mpm_tester.assertTrue(actual.get(pose2, False))
        mpm_tester.assertTrue(actual.get(pose3, False))
        mpm_tester.assertTrue(actual.get(pose4, False))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertTrue(actual.get(pose6, False))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 0, no props, invalid default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_default: 10
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 0, no props, l_default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_l_default: False
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_ED, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertFalse(actual.get(pose5, True))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 0, no props, invalid l_default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_l_default: 10
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 0, no props, default + urfl")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_default: True,
            prop_urfl: True
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_ED, actual._mpm_type)
        mpm_tester.assertTrue(actual.get(pose1, False))
        mpm_tester.assertTrue(actual.get(pose2, False))
        mpm_tester.assertTrue(actual.get(pose3, False))
        mpm_tester.assertTrue(actual.get(pose4, False))
        mpm_tester.assertTrue(actual.get(pose5, False))
        mpm_tester.assertTrue(actual.get(pose6, False))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(0, len(log))

        mpm_tester.prepareTest("mpm type 0, no props, default + l_default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_default: True,
            prop_l_default: False
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_ED, actual._mpm_type)
        mpm_tester.assertTrue(actual.get(pose1, False))
        mpm_tester.assertTrue(actual.get(pose2, False))
        mpm_tester.assertTrue(actual.get(pose3, False))
        mpm_tester.assertTrue(actual.get(pose4, False))
        mpm_tester.assertFalse(actual.get(pose5, True))
        mpm_tester.assertTrue(actual.get(pose6, False))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(0, len(log))

        mpm_tester.prepareTest("mpm type 0, extra props")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            "extra": 123,
            "extra2": 69
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_ED, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(4, len(log))

        mpm_tester.prepareTest("mpm type 0, valid 1 2 5")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_p1: True,
            prop_p2: False,
            prop_p5: True,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_ED, actual._mpm_type)
        mpm_tester.assertTrue(actual.get(pose1, False))
        mpm_tester.assertFalse(actual.get(pose2, True))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertTrue(actual.get(pose5, False))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 0, valid 3 4 6")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_p3: False,
            prop_p4: True,
            prop_p6: False,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_ED, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertFalse(actual.get(pose3, True))
        mpm_tester.assertTrue(actual.get(pose4, False))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertFalse(actual.get(pose6, True))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 0, valid all, no defaults")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_p1: True,
            prop_p2: False,
            prop_p3: False,
            prop_p4: True,
            prop_p5: True,
            prop_p6: False,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_ED, actual._mpm_type)
        mpm_tester.assertTrue(actual.get(pose1, False))
        mpm_tester.assertFalse(actual.get(pose2, True))
        mpm_tester.assertTrue(actual.get(pose5, False))
        mpm_tester.assertFalse(actual.get(pose3, True))
        mpm_tester.assertTrue(actual.get(pose4, False))
        mpm_tester.assertFalse(actual.get(pose6, True))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 0, valid all, defaults")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_default: True,
            prop_l_default: False,
            prop_p1: True,
            prop_p2: False,
            prop_p3: False,
            prop_p4: True,
            prop_p5: True,
            prop_p6: False,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_ED, actual._mpm_type)
        mpm_tester.assertTrue(actual.get(pose1, False))
        mpm_tester.assertFalse(actual.get(pose2, True))
        mpm_tester.assertTrue(actual.get(pose5, False))
        mpm_tester.assertFalse(actual.get(pose3, True))
        mpm_tester.assertTrue(actual.get(pose4, False))
        mpm_tester.assertFalse(actual.get(pose6, True))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(0, len(log))

        mpm_tester.prepareTest("mpm type 0, one invalid, defaults")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_default: True,
            prop_l_default: False,
            prop_p1: True,
            prop_p2: False,
            prop_p3: False,
            prop_p4: 10,
            prop_p5: True,
            prop_p6: False,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 0, valid all, defaults, extra props")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_ED,
            prop_default: True,
            prop_l_default: False,
            prop_p1: True,
            prop_p2: False,
            prop_p3: False,
            prop_p4: True,
            prop_p5: True,
            prop_p6: False,
            "extra": 123,
            "extra2": 10,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_ED, actual._mpm_type)
        mpm_tester.assertTrue(actual.get(pose1, False))
        mpm_tester.assertFalse(actual.get(pose2, True))
        mpm_tester.assertTrue(actual.get(pose5, False))
        mpm_tester.assertFalse(actual.get(pose3, True))
        mpm_tester.assertTrue(actual.get(pose4, False))
        mpm_tester.assertFalse(actual.get(pose6, True))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        # type  1

        mpm_tester.prepareTest("mpm type 1, no props")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_FB, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 1, no props, default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            prop_default: pose3,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_FB, actual._mpm_type)
        mpm_tester.assertEqual(pose3, actual.get(pose1, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose2, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose3, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 1, no props, invalid default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            prop_default: "test"
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 1, no props, l_default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            prop_l_default: pose3,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_FB, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 1, no props, invalid l_default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            prop_l_default: "test",
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 1, no props, default + urfl")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            prop_default: pose3,
            prop_urfl: True
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_FB, actual._mpm_type)
        mpm_tester.assertEqual(pose3, actual.get(pose1, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose2, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose3, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose4, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose5, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(0, len(log))

        mpm_tester.prepareTest("mpm type 1, no props, default + l_default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            prop_default: pose3,
            prop_l_default: pose4,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_FB, actual._mpm_type)
        mpm_tester.assertEqual(pose3, actual.get(pose1, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose2, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose3, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose4, "test"))
        mpm_tester.assertEqual(pose4, actual.get(pose5, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(0, len(log))

        mpm_tester.prepareTest("mpm type 1, extra props")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            "extra": 123,
            "extra2": 69
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_FB, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(4, len(log))

        mpm_tester.prepareTest("mpm type 1, valid 1 2 5")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            prop_p1: pose2,
            prop_p2: pose3,
            prop_p5: pose4,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_FB, actual._mpm_type)
        mpm_tester.assertEqual(pose2, actual.get(pose1, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertEqual(pose4, actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 1, valid 3 4 6")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            prop_p3: pose2,
            prop_p4: pose3,
            prop_p6: pose4,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_FB, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertEqual(pose2, actual.get(pose3, "test"))
        mpm_tester.assertEqual(pose3, actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertEqual(pose4, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 1, valid all, no defaults")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            prop_p1: pose3,
            prop_p2: pose4,
            prop_p3: pose5,
            prop_p4: pose1,
            prop_p5: pose6,
            prop_p6: pose2,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_FB, actual._mpm_type)
        mpm_tester.assertEqual(pose3, actual.get(pose1, "test"))
        mpm_tester.assertEqual(pose4, actual.get(pose2, "test"))
        mpm_tester.assertEqual(pose5, actual.get(pose3, "test"))
        mpm_tester.assertEqual(pose1, actual.get(pose4, "test"))
        mpm_tester.assertEqual(pose6, actual.get(pose5, "test"))
        mpm_tester.assertEqual(pose2, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 1, valid all, defaults")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            prop_default: pose3,
            prop_l_default: pose4,
            prop_p1: pose6,
            prop_p2: pose4,
            prop_p3: pose4,
            prop_p4: pose5,
            prop_p5: pose2,
            prop_p6: pose5,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_FB, actual._mpm_type)
        mpm_tester.assertEqual(pose6, actual.get(pose1, "test"))
        mpm_tester.assertEqual(pose4, actual.get(pose2, "test"))
        mpm_tester.assertEqual(pose4, actual.get(pose3, "test"))
        mpm_tester.assertEqual(pose5, actual.get(pose4, "test"))
        mpm_tester.assertEqual(pose2, actual.get(pose5, "test"))
        mpm_tester.assertEqual(pose5, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(0, len(log))

        mpm_tester.prepareTest("mpm type 1, one invalid, defaults")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            prop_default: pose3,
            prop_l_default: pose4,
            prop_p1: pose6,
            prop_p2: pose4,
            prop_p3: 10,
            prop_p4: pose5,
            prop_p5: pose2,
            prop_p6: pose5,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 1, valid all, defaults, extra props")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_FB,
            prop_default: pose3,
            prop_l_default: pose4,
            prop_p1: pose6,
            prop_p2: pose4,
            prop_p3: pose4,
            prop_p4: pose5,
            prop_p5: pose2,
            prop_p6: pose5,
            "extra": 123,
            "extra2": 10,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_FB, actual._mpm_type)
        mpm_tester.assertEqual(pose6, actual.get(pose1, "test"))
        mpm_tester.assertEqual(pose4, actual.get(pose2, "test"))
        mpm_tester.assertEqual(pose4, actual.get(pose3, "test"))
        mpm_tester.assertEqual(pose5, actual.get(pose4, "test"))
        mpm_tester.assertEqual(pose2, actual.get(pose5, "test"))
        mpm_tester.assertEqual(pose5, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        # 2

        mpm_tester.prepareTest("mpm type 2, no props")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_AS, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 2, no props, default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            prop_default: as_one,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_AS, actual._mpm_type)
        mpm_tester.assertEqual(as_one, actual.get(pose1, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose2, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose3, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 2, no props, invalid default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            prop_default: "test"
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 2, no props, l_default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            prop_l_default: as_star,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_AS, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 2, no props, invalid l_default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            prop_l_default: "test",
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 2, no props, default + urfl")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            prop_default: as_one,
            prop_urfl: True
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_AS, actual._mpm_type)
        mpm_tester.assertEqual(as_one, actual.get(pose1, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose2, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose3, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose4, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose5, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(0, len(log))

        mpm_tester.prepareTest("mpm type 2, no props, default + l_default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            prop_default: as_one,
            prop_l_default: as_star,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_AS, actual._mpm_type)
        mpm_tester.assertEqual(as_one, actual.get(pose1, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose2, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose3, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose4, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose5, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(0, len(log))

        mpm_tester.prepareTest("mpm type 2, extra props")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            "extra": 123,
            "extra2": 69
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_AS, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(4, len(log))

        mpm_tester.prepareTest("mpm type 2, valid 1 2 5")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            prop_p1: as_one,
            prop_p2: as_zero,
            prop_p5: as_star,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_AS, actual._mpm_type)
        mpm_tester.assertEqual(as_one, actual.get(pose1, "test"))
        mpm_tester.assertEqual(as_zero, actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 2, valid 3 4 6")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            prop_p3: as_zero,
            prop_p4: as_star,
            prop_p6: as_one,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_AS, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertEqual(as_zero, actual.get(pose3, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 2, valid all, no defaults")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            prop_p1: as_zero,
            prop_p2: as_one,
            prop_p3: as_star,
            prop_p4: as_one,
            prop_p5: as_zero,
            prop_p6: as_star,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_AS, actual._mpm_type)
        mpm_tester.assertEqual(as_zero, actual.get(pose1, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose2, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose3, "test"))
        mpm_tester.assertEqual(as_one, actual.get(pose4, "test"))
        mpm_tester.assertEqual(as_zero, actual.get(pose5, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 2, valid all, defaults")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            prop_default: as_zero,
            prop_l_default: as_one,
            prop_p1: as_star,
            prop_p2: as_star,
            prop_p3: as_star,
            prop_p4: as_star,
            prop_p5: as_star,
            prop_p6: as_star,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_AS, actual._mpm_type)
        mpm_tester.assertEqual(as_star, actual.get(pose1, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose2, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose3, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose4, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose5, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(0, len(log))

        mpm_tester.prepareTest("mpm type 2, one invalid, defaults")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            prop_default: as_zero,
            prop_l_default: as_one,
            prop_p1: as_star,
            prop_p2: as_star,
            prop_p3: "test",
            prop_p4: as_star,
            prop_p5: as_star,
            prop_p6: as_star,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 2, valid all, defaults, extra props")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_AS,
            prop_default: as_zero,
            prop_l_default: as_one,
            prop_p1: as_star,
            prop_p2: as_star,
            prop_p3: as_star,
            prop_p4: as_star,
            prop_p5: as_star,
            prop_p6: as_star,
            "extra": 123,
            "extra2": 69,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_AS, actual._mpm_type)
        mpm_tester.assertEqual(as_star, actual.get(pose1, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose2, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose3, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose4, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose5, "test"))
        mpm_tester.assertEqual(as_star, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))


        # 4

        mpm_tester.prepareTest("mpm type 4, no props")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_IC, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 4, no props, default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            prop_default: ic_one,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_IC, actual._mpm_type)
        mpm_tester.assertEqual(ic_one, actual.get(pose1, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose2, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose3, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 4, no props, invalid default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            prop_default: 10,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 4, no props, l_default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            prop_l_default: ic_zero,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_IC, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertEqual(ic_zero, actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 4, no props, invalid l_default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            prop_l_default: 10,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 4, no props, default + urfl")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            prop_default: ic_one,
            prop_urfl: True
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_IC, actual._mpm_type)
        mpm_tester.assertEqual(ic_one, actual.get(pose1, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose2, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose3, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose4, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose5, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(0, len(log))

        mpm_tester.prepareTest("mpm type 4, no props, default + l_default")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            prop_default: ic_one,
            prop_l_default: ic_zero,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_IC, actual._mpm_type)
        mpm_tester.assertEqual(ic_one, actual.get(pose1, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose2, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose3, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose4, "test"))
        mpm_tester.assertEqual(ic_zero, actual.get(pose5, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(0, len(log))

        mpm_tester.prepareTest("mpm type 4, extra props")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            "extra": 123,
            "extra2": 69
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_IC, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(4, len(log))

        mpm_tester.prepareTest("mpm type 4, valid 1 2 5")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            prop_p1: ic_one,
            prop_p2: ic_zero,
            prop_p5: ic_custom,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_IC, actual._mpm_type)
        mpm_tester.assertEqual(ic_one, actual.get(pose1, "test"))
        mpm_tester.assertEqual(ic_zero, actual.get(pose2, "test"))
        mpm_tester.assertIsNone(actual.get(pose3, "test"))
        mpm_tester.assertIsNone(actual.get(pose4, "test"))
        mpm_tester.assertEqual(ic_custom, actual.get(pose5, "test"))
        mpm_tester.assertIsNone(actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 4, valid 3 4 6")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            prop_p3: ic_custom,
            prop_p4: ic_one,
            prop_p6: ic_zero,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_IC, actual._mpm_type)
        mpm_tester.assertIsNone(actual.get(pose1, "test"))
        mpm_tester.assertIsNone(actual.get(pose2, "test"))
        mpm_tester.assertEqual(ic_custom, actual.get(pose3, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose4, "test"))
        mpm_tester.assertIsNone(actual.get(pose5, "test"))
        mpm_tester.assertEqual(ic_zero, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 4, valid all, no defaults")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            prop_p1: ic_one,
            prop_p2: ic_custom,
            prop_p3: ic_zero,
            prop_p4: ic_zero,
            prop_p5: ic_one,
            prop_p6: ic_custom,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_IC, actual._mpm_type)
        mpm_tester.assertEqual(ic_one, actual.get(pose1, "test"))
        mpm_tester.assertEqual(ic_custom, actual.get(pose2, "test"))
        mpm_tester.assertEqual(ic_zero, actual.get(pose3, "test"))
        mpm_tester.assertEqual(ic_zero, actual.get(pose4, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose5, "test"))
        mpm_tester.assertEqual(ic_custom, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

        mpm_tester.prepareTest("mpm type 4, valid all, defaults")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            prop_default: ic_one,
            prop_l_default: ic_zero,
            prop_p1: ic_custom,
            prop_p2: ic_custom,
            prop_p3: ic_custom,
            prop_p4: ic_one,
            prop_p5: ic_one,
            prop_p6: ic_zero,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_IC, actual._mpm_type)
        mpm_tester.assertEqual(ic_custom, actual.get(pose1, "test"))
        mpm_tester.assertEqual(ic_custom, actual.get(pose2, "test"))
        mpm_tester.assertEqual(ic_custom, actual.get(pose3, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose4, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose5, "test"))
        mpm_tester.assertEqual(ic_zero, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(0, len(log))

        mpm_tester.prepareTest("mpm type 4, one invalid, defaults")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            prop_default: ic_one,
            prop_l_default: ic_zero,
            prop_p1: ic_custom,
            prop_p2: ic_custom,
            prop_p3: 10,
            prop_p4: ic_custom,
            prop_p5: ic_one,
            prop_p6: ic_zero,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNone(actual)
        mpm_tester.assertEqual(1, len(log))

        mpm_tester.prepareTest("mpm type 4, valid all, defaults, extra props")
        test_data = {
            prop_mpm_type: MASPoseMap.MPM_TYPE_IC,
            prop_default: ic_one,
            prop_l_default: ic_zero,
            prop_p1: ic_custom,
            prop_p2: ic_custom,
            prop_p3: ic_custom,
            prop_p4: ic_one,
            prop_p5: ic_one,
            prop_p6: ic_zero,
            "extra": 123,
            "extra2": 69,
        }
        log = []
        actual = MASPoseMap.fromJSON(test_data, log, 0)
        mpm_tester.assertIsNotNone(actual)
        mpm_tester.assertEqual(MASPoseMap.MPM_TYPE_IC, actual._mpm_type)
        mpm_tester.assertEqual(ic_custom, actual.get(pose1, "test"))
        mpm_tester.assertEqual(ic_custom, actual.get(pose2, "test"))
        mpm_tester.assertEqual(ic_custom, actual.get(pose3, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose4, "test"))
        mpm_tester.assertEqual(ic_one, actual.get(pose5, "test"))
        mpm_tester.assertEqual(ic_zero, actual.get(pose6, "test"))
        mpm_tester.assertEqual({}, test_data)
        mpm_tester.assertEqual(2, len(log))

    call dev_unit_tests_finish_test(mpm_tester)

    return


label dev_unit_test_mhs:
    m "Running Tests..."
    python:
        import copy
        def gen_fresh_mhs():
            return MASHistorySaver("testing", datetime.datetime.now(), {})

        mhs_tester = store.mas_dev_unit_tests.MASUnitTester()

        mhs_tester.prepareTest("CONSTRUCTOR")
        test_mhs = gen_fresh_mhs()
        mhs_tester.assertEqual("testing", test_mhs.id)

        mhs_tester.prepareTest("getSortKey")
        test_mhs = gen_fresh_mhs()
        dt_test = test_mhs.trigger
        sortkey = MASHistorySaver.getSortKey(test_mhs)
        mhs_tester.assertEqual(dt_test, sortkey)

        mhs_tester.prepareTest("correctTriggerYear|future same year")
        dt_test = datetime.datetime.now() + datetime.timedelta(days=1)
        correct_trig = MASHistorySaver.correctTriggerYear(dt_test)
        mhs_tester.assertEqual(dt_test, correct_trig)

        mhs_tester.prepareTest("correctTriggerYear|future diff year (1)")
        dt_test = datetime.datetime.now() + datetime.timedelta(days=1)
        expected = copy.deepcopy(dt_test)
        dt_test = dt_test.replace(year=dt_test.year+1)
        correct_trig = MASHistorySaver.correctTriggerYear(dt_test)
        mhs_tester.assertEqual(expected, correct_trig)

        mhs_tester.prepareTest("correctTriggerYear|future diff year (5)")
        dt_test = datetime.datetime.now() + datetime.timedelta(days=1)
        expected = copy.deepcopy(dt_test)
        dt_test = dt_test.replace(year=dt_test.year+5)
        correct_trig = MASHistorySaver.correctTriggerYear(dt_test)
        mhs_tester.assertEqual(expected, correct_trig)

        mhs_tester.prepareTest("correctTriggerYear|past same year")
        dt_test = datetime.datetime.now() - datetime.timedelta(days=1)
        expected = dt_test.replace(year=dt_test.year + 1)
        correct_trig = MASHistorySaver.correctTriggerYear(dt_test)
        mhs_tester.assertEqual(expected, correct_trig)

        mhs_tester.prepareTest("correctTriggerYear|past diff year")
        dt_test = datetime.datetime.now() - datetime.timedelta(days=1)
        expected = dt_test.replace(year=dt_test.year + 1)
        dt_test = dt_test.replace(year=dt_test.year - 3)
        correct_trig = MASHistorySaver.correctTriggerYear(dt_test)
        mhs_tester.assertEqual(expected, correct_trig)

        mhs_tester.prepareTest("fromTuple|(<standard dt>, True)")
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = False
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=100)
        test_data = (test_now + datetime.timedelta(days=1), True)
        test_mhs = gen_fresh_mhs()
        test_mhs.fromTuple(test_data)
        mhs_tester.assertEqual(test_data[0], test_mhs.trigger)
        mhs_tester.assertTrue(test_mhs.use_year_before)
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]

        mhs_tester.prepareTest("fromTuple|(<standard dt>,)")
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = False
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=100)
        test_data = (test_now + datetime.timedelta(days=1),)
        test_mhs = gen_fresh_mhs()
        test_mhs.fromTuple(test_data)
        mhs_tester.assertEqual(test_data[0], test_mhs.trigger)
        mhs_tester.assertFalse(test_mhs.use_year_before)
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]       

        mhs_tester.prepareTest("isActive|continuous")
        test_mhs = gen_fresh_mhs()
        test_dt = datetime.datetime.now()
        mhs_tester.assertTrue(test_mhs.isActive(test_dt))

        mhs_tester.prepareTest("isActive|check_dt in range")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2018, 4, 21)
        mhs_tester.assertTrue(test_mhs.isActive(check_dt))

        mhs_tester.prepareTest("isActive|check_dt in range, incl start")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2018, 4, 20)
        mhs_tester.assertTrue(test_mhs.isActive(check_dt))

        mhs_tester.prepareTest("isActive|check_dt not in range")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2018, 3, 10)
        mhs_tester.assertFalse(test_mhs.isActive(check_dt))

        mhs_tester.prepareTest("isActive|check_dt not in range, excl end")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2018, 4, 22)
        mhs_tester.assertFalse(test_mhs.isActive(check_dt))

        mhs_tester.prepareTest("isActive|check_dt in range, diff year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2017, 4, 21)
        mhs_tester.assertTrue(test_mhs.isActive(check_dt))

        mhs_tester.prepareTest("isActive|check_dt not in range, diff year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2017, 3, 10)
        mhs_tester.assertFalse(test_mhs.isActive(check_dt))

        mhs_tester.prepareTest("isActive|check_dt in range, yearprev, ny wrap")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 12, 30)
        test_mhs.end_dt = datetime.datetime(2019, 1, 2)
        check_dt = datetime.datetime(2018, 12, 31)
        mhs_tester.assertTrue(test_mhs.isActive(check_dt))

        mhs_tester.prepareTest(
            "isActive|check_dt not in range, year prev, ny wrap"
        )
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 12, 30)
        test_mhs.end_dt = datetime.datetime(2019, 1, 2)
        check_dt = datetime.datetime(2018, 12, 10)
        mhs_tester.assertFalse(test_mhs.isActive(check_dt))

        mhs_tester.prepareTest("isActive|check_dt in range, yearfut, ny wrap")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 12, 30)
        test_mhs.end_dt = datetime.datetime(2019, 1, 2)
        check_dt = datetime.datetime(2019, 1, 1)
        mhs_tester.assertTrue(test_mhs.isActive(check_dt))

        mhs_tester.prepareTest(
            "isActive|check_dt not in range, year fut, ny wrap"
        )
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 12, 30)
        test_mhs.end_dt = datetime.datetime(2019, 1, 2)
        check_dt = datetime.datetime(2019, 1, 3)
        mhs_tester.assertFalse(test_mhs.isActive(check_dt))

        mhs_tester.prepareTest("isActiveWithin|continuous")
        test_mhs = gen_fresh_mhs()
        st_dt = datetime.datetime(2018, 4, 20)
        en_dt = datetime.datetime(2018, 8, 31)
        mhs_tester.assertTrue(test_mhs.isActiveWithin(st_dt, en_dt))

        mhs_tester.prepareTest("isActiveWithin|start_dt active")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 10)
        test_mhs.end_dt = datetime.datetime(2018, 5, 10)
        st_dt = datetime.datetime(2018, 4, 20)
        en_dt = datetime.datetime(2018, 8, 31)
        mhs_tester.assertTrue(test_mhs.isActiveWithin(st_dt, en_dt))

        mhs_tester.prepareTest("isActiveWithin|end_dt active")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 7, 20)
        test_mhs.end_dt = datetime.datetime(2018, 9, 1)
        st_dt = datetime.datetime(2018, 4, 20)
        en_dt = datetime.datetime(2018, 8, 31)
        mhs_tester.assertTrue(test_mhs.isActiveWithin(st_dt, en_dt))

        mhs_tester.prepareTest("isActiveWithin|within range")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 6, 4)
        test_mhs.end_dt = datetime.datetime(2018, 7, 20)
        st_dt = datetime.datetime(2018, 4, 20)
        en_dt = datetime.datetime(2018, 8, 31)
        mhs_tester.assertTrue(test_mhs.isActiveWithin(st_dt, en_dt))

        mhs_tester.prepareTest("isActiveWithin|before range")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 1, 4)
        test_mhs.end_dt = datetime.datetime(2018, 3, 20)
        st_dt = datetime.datetime(2018, 4, 20)
        en_dt = datetime.datetime(2018, 8, 31)
        mhs_tester.assertFalse(test_mhs.isActiveWithin(st_dt, en_dt))

        mhs_tester.prepareTest("isActiveWithin|after range")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 9, 4)
        test_mhs.end_dt = datetime.datetime(2018, 11, 20)
        st_dt = datetime.datetime(2018, 4, 20)
        en_dt = datetime.datetime(2018, 8, 31)
        mhs_tester.assertFalse(test_mhs.isActiveWithin(st_dt, en_dt))

        mhs_tester.prepareTest("isContinuous|both dt None")
        test_mhs = gen_fresh_mhs()
        mhs_tester.assertTrue(test_mhs.isContinuous())

        mhs_tester.prepareTest("isContinuous|start dt None")
        test_mhs = gen_fresh_mhs()
        test_mhs.end_dt = datetime.datetime(2018, 4, 20)
        mhs_tester.assertTrue(test_mhs.isContinuous())

        mhs_tester.prepareTest("isContinuous|end dt None")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        mhs_tester.assertTrue(test_mhs.isContinuous())

        mhs_tester.prepareTest("isContinuous|both dt not None")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 21)
        mhs_tester.assertFalse(test_mhs.isContinuous())

        mhs_tester.prepareTest("isFuture|continuous")
        test_mhs = gen_fresh_mhs()
        check_dt = datetime.datetime(2018, 4, 20)
        mhs_tester.assertFalse(test_mhs.isFuture(check_dt))

        mhs_tester.prepareTest("isFuture|check_dt before start_dt, same year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2018, 4, 18)
        mhs_tester.assertTrue(test_mhs.isFuture(check_dt))

        mhs_tester.prepareTest("isFuture|check_dt before start_dt, diff year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2020, 4, 18)
        mhs_tester.assertTrue(test_mhs.isFuture(check_dt))

        mhs_tester.prepareTest("isFuture|check_dt after start_dt, same year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2018, 5, 20)
        mhs_tester.assertFalse(test_mhs.isFuture(check_dt))

        mhs_tester.prepareTest("isFuture|check_dt after start_dt, diff year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2014, 5, 20)
        mhs_tester.assertFalse(test_mhs.isFuture(check_dt))

        mhs_tester.prepareTest("isFuture|check_dt on start_dt, same year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2018, 4, 20)
        mhs_tester.assertFalse(test_mhs.isFuture(check_dt))

        mhs_tester.prepareTest("isFuture|check_dt on start_dt, diff year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2014, 4, 20)
        mhs_tester.assertFalse(test_mhs.isFuture(check_dt))

        mhs_tester.prepareTest("isPassed|continuous")
        test_mhs = gen_fresh_mhs()
        check_dt = datetime.datetime(2018, 4, 20)
        mhs_tester.assertFalse(test_mhs.isPassed(check_dt))

        mhs_tester.prepareTest("isPassed|check_dt before end_dt, same year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2018, 4, 20)
        mhs_tester.assertFalse(test_mhs.isPassed(check_dt))

        mhs_tester.prepareTest("isPassed|check_dt before end_dt, diff year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2020, 4, 20)
        mhs_tester.assertFalse(test_mhs.isPassed(check_dt))

        mhs_tester.prepareTest("isPassed|check_dt after end_dt, same year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2018, 5, 20)
        mhs_tester.assertTrue(test_mhs.isPassed(check_dt))

        mhs_tester.prepareTest("isPassed|check_dt after end_dt, diff year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2015, 5, 20)
        mhs_tester.assertTrue(test_mhs.isPassed(check_dt))

        mhs_tester.prepareTest("isPassed|check_dt on end_dt, same year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2018, 4, 22)
        mhs_tester.assertTrue(test_mhs.isPassed(check_dt))

        mhs_tester.prepareTest("isPassed|check_dt on end_dt, diff year")
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = datetime.datetime(2018, 4, 20)
        test_mhs.end_dt = datetime.datetime(2018, 4, 22)
        check_dt = datetime.datetime(2014, 4, 22)
        mhs_tester.assertTrue(test_mhs.isPassed(check_dt))

        # Set Trigger
        #   Cases:
        #   1 - trigger <= first_sesh -> trigger year is corrected
        #   2 - trigger year diff greater than 1 -> trigger year is corrected
        #   3 - TT detected + non continuuous + (future or active)
        #       -> trigger year is corrected
        #   4 - none of the above is true -> trigger unchanged
        mhs_tester.prepareTest("setTrigger|trigger <= first_sesh")
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = False
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=100)
        test_mhs = gen_fresh_mhs()
        test_mhs.use_year_before = True
        test_dt = MASHistorySaver.first_sesh - datetime.timedelta(days=1)
        test_mhs.setTrigger(test_dt)
        expected = MASHistorySaver.correctTriggerYear(test_dt)
        mhs_tester.assertEqual(expected, test_mhs.trigger)
        mhs_tester.assertFalse(mas_TTDetected())
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]

        mhs_tester.prepareTest("setTrigger|trigger <= first_sesh, same dt")
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = False
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=100)
        test_mhs = gen_fresh_mhs()
        test_dt = MASHistorySaver.first_sesh
        test_mhs.setTrigger(test_dt)
        expected = MASHistorySaver.correctTriggerYear(test_dt)
        mhs_tester.assertEqual(expected, test_mhs.trigger)
        mhs_tester.assertFalse(mas_TTDetected())
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]

        mhs_tester.prepareTest(
            "setTrigger|trigger <= first_sesh, same dt,"
        )
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = False
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=100)
        test_mhs = gen_fresh_mhs()
        test_dt = MASHistorySaver.first_sesh
        test_mhs.setTrigger(test_dt)
        expected = MASHistorySaver.correctTriggerYear(test_dt)
        mhs_tester.assertEqual(expected, test_mhs.trigger)
        mhs_tester.assertFalse(mas_TTDetected())
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]

        mhs_tester.prepareTest("setTrigger|trigger year diff > 1")
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = False
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=100)
        test_mhs = gen_fresh_mhs()
        test_dt = test_now.replace(year=test_now.year + 5)
        test_mhs.setTrigger(test_dt)
        expected = MASHistorySaver.correctTriggerYear(test_dt)
        mhs_tester.assertEqual(expected, test_mhs.trigger)
        mhs_tester.assertFalse(mas_TTDetected())
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]

        mhs_tester.prepareTest(
            "setTrigger|TT detected + not continuous + future"
        )
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = True
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=100)
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = test_now + datetime.timedelta(days=50)
        test_mhs.end_dt = test_now + datetime.timedelta(days=55)
        test_dt = test_now + datetime.timedelta(days=1)
        test_mhs.setTrigger(test_dt)
        expected = MASHistorySaver.correctTriggerYear(test_dt)
        mhs_tester.assertEqual(expected, test_mhs.trigger)
        mhs_tester.assertTrue(mas_TTDetected())
        mhs_tester.assertFalse(test_mhs.isContinuous())
        mhs_tester.assertTrue(test_mhs.isFuture(test_now))
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]

        mhs_tester.prepareTest(
            "setTrigger|TT detected + not continuous + active"
        )
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = True
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=100)
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = test_now - datetime.timedelta(days=5)
        test_mhs.end_dt = test_now + datetime.timedelta(days=5)
        test_dt = test_now + datetime.timedelta(days=1)
        test_mhs.setTrigger(test_dt)
        expected = MASHistorySaver.correctTriggerYear(test_dt)
        mhs_tester.assertEqual(expected, test_mhs.trigger)
        mhs_tester.assertTrue(mas_TTDetected())
        mhs_tester.assertFalse(test_mhs.isContinuous())
        mhs_tester.assertFalse(test_mhs.isFuture(test_now))
        mhs_tester.assertTrue(test_mhs.isActive(test_now))
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]

        mhs_tester.prepareTest("setTrigger|unchanged trigger")
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = False
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=100)
        test_mhs = gen_fresh_mhs()
        test_dt = test_now + datetime.timedelta(days=10)
        test_mhs.setTrigger(test_dt)
        mhs_tester.assertEqual(test_dt, test_mhs.trigger)
        mhs_tester.assertFalse(mas_TTDetected())
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]

        mhs_tester.prepareTest("isTuple")
        test_mhs = gen_fresh_mhs()
        test_data = (
            test_mhs.trigger,
            test_mhs.use_year_before
        )
        mhs_tester.assertEqual(test_data, test_mhs.toTuple())

        mhs_tester.prepareTest(
            "setTrigger|event in past, 2 year, not uyb"
        )
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = True
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=600)
        test_mhs = gen_fresh_mhs()
        test_mhs.start_dt = test_now - datetime.timedelta(days=50)
        test_mhs.end_dt = test_now - datetime.timedelta(days=20)
        test_dt = test_now + datetime.timedelta(days=1)
        test_dt = test_dt.replace(year=test_dt.year + 2)
        test_mhs.setTrigger(test_dt)
        expected = MASHistorySaver.correctTriggerYear(test_dt)
        mhs_tester.assertEqual(expected, test_mhs.trigger)
        mhs_tester.assertTrue(mas_TTDetected())
        mhs_tester.assertFalse(test_mhs.isContinuous())
        mhs_tester.assertFalse(test_mhs.isFuture(test_now))
        mhs_tester.assertFalse(test_mhs.isActive(test_now))
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]

        mhs_tester.prepareTest(
            "setTrigger|event in past, 2 year, uyb"
        )
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = True
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=600)
        test_mhs = gen_fresh_mhs()
        test_mhs.use_year_before = True
        test_mhs.start_dt = test_now - datetime.timedelta(days=50)
        test_mhs.end_dt = test_now - datetime.timedelta(days=20)
        test_dt = test_now + datetime.timedelta(days=1)
        test_dt = test_dt.replace(year=test_dt.year + 2)
        test_mhs.setTrigger(test_dt)
        expected = MASHistorySaver.correctTriggerYear(test_dt)
        expected = expected.replace(year=expected.year + 1)
        mhs_tester.assertEqual(expected, test_mhs.trigger)
        mhs_tester.assertTrue(mas_TTDetected())
        mhs_tester.assertFalse(test_mhs.isContinuous())
        mhs_tester.assertFalse(test_mhs.isFuture(test_now))
        mhs_tester.assertFalse(test_mhs.isActive(test_now))
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]

        mhs_tester.prepareTest(
            "setTrigger|event in past, 1 year, uyb"
        )
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = True
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=600)
        test_mhs = gen_fresh_mhs()
        test_mhs.use_year_before = True
        test_mhs.start_dt = test_now - datetime.timedelta(days=50)
        test_mhs.end_dt = test_now - datetime.timedelta(days=20)
        test_dt = test_now + datetime.timedelta(days=1)
        test_dt = test_dt.replace(year=test_dt.year + 1)
        test_mhs.setTrigger(test_dt)
        expected = test_dt
        mhs_tester.assertEqual(expected, test_mhs.trigger)
        mhs_tester.assertTrue(mas_TTDetected())
        mhs_tester.assertFalse(test_mhs.isContinuous())
        mhs_tester.assertFalse(test_mhs.isFuture(test_now))
        mhs_tester.assertFalse(test_mhs.isActive(test_now))
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]

        mhs_tester.prepareTest(
            "setTrigger|event in future, 1 year, uyb"
        )
        test_now = datetime.datetime.now()
        prev_data = (
            store.mas_globals.tt_detected,
            MASHistorySaver.first_sesh
        )
        store.mas_globals.tt_detected = True
        MASHistorySaver.first_sesh = test_now - datetime.timedelta(days=600)
        test_mhs = gen_fresh_mhs()
        test_mhs.use_year_before = True
        test_mhs.start_dt = test_now + datetime.timedelta(days=10)
        test_mhs.end_dt = test_now + datetime.timedelta(days=20)
        test_dt = (
            test_now.replace(year=test_now.year + 1)
            - datetime.timedelta(days=1)
        )
        test_mhs.setTrigger(test_dt)
        expected = MASHistorySaver.correctTriggerYear(test_dt)
        mhs_tester.assertEqual(expected, test_mhs.trigger)
        mhs_tester.assertTrue(mas_TTDetected())
        mhs_tester.assertFalse(test_mhs.isContinuous())
        mhs_tester.assertTrue(test_mhs.isFuture(test_now))
        mhs_tester.assertFalse(test_mhs.isActive(test_now))
        store.mas_globals.tt_detected = prev_data[0]
        MASHistorySaver.first_sesh = prev_data[1]


    call dev_unit_tests_finish_test(mhs_tester)

    return


label dev_unit_test_mhs_cpm:
    m "Running Tests..."

    python:
        def sv_mhs():
            mhs_pbday = mas_history.getMHS("player_bday")
            return (
                (
                    mhs_pbday.start_dt,
                    mhs_pbday.end_dt,
                    mhs_pbday.use_year_before,
                    mhs_pbday.trigger
                ),
                mhs_pbday
            )

        def rs_mhs(data):
            mhs_pbday = mas_history.getMHS("player_bday")
            mhs_pbday.start_dt = data[0]
            mhs_pbday.end_dt = data[1]
            mhs_pbday.use_year_before = data[2]
            mhs_pbday.setTrigger(data[3])

        mhs_tester = store.mas_dev_unit_tests.MASUnitTester()

        test_name = "standard date|"
        prev_data, test_mhs = sv_mhs()
        test_now = datetime.datetime.now()
        bday = datetime.date(1984, 4, 20)
        inc_year = int(bday.replace(year=test_now.year) < test_now.date())
        store.mas_player_bday_event.correct_pbday_mhs(bday)
        mhs_tester.prepareTest(test_name + "start dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 4, 20),
            test_mhs.start_dt
        )
        mhs_tester.prepareTest(test_name + "end dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 4, 22),
            test_mhs.end_dt
        )
        mhs_tester.prepareTest(test_name + "use year before")
        mhs_tester.assertFalse(test_mhs.use_year_before)
        mhs_tester.prepareTest(test_name + "trigger")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 4, 23),
            test_mhs.trigger
        )
        rs_mhs(prev_data)

        test_name = "edge month date|"
        prev_data, test_mhs = sv_mhs()
        test_now = datetime.datetime.now()
        bday = datetime.date(1984, 5, 30)
        inc_year = int(bday.replace(year=test_now.year) < test_now.date())
        store.mas_player_bday_event.correct_pbday_mhs(bday)
        mhs_tester.prepareTest(test_name + "start dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 5, 30),
            test_mhs.start_dt
        )
        mhs_tester.prepareTest(test_name + "end dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 6, 1),
            test_mhs.end_dt
        )
        mhs_tester.prepareTest(test_name + "use year before")
        mhs_tester.assertFalse(test_mhs.use_year_before)
        mhs_tester.prepareTest(test_name + "trigger")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 6, 2),
            test_mhs.trigger
        )
        rs_mhs(prev_data)

        test_name = "12-28|"
        prev_data, test_mhs = sv_mhs()
        test_now = datetime.datetime.now()
        bday = datetime.date(1984, 12, 28)
        inc_year = int(bday.replace(year=test_now.year) < test_now.date())
        store.mas_player_bday_event.correct_pbday_mhs(bday)
        mhs_tester.prepareTest(test_name + "start dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 12, 28),
            test_mhs.start_dt
        )
        mhs_tester.prepareTest(test_name + "end dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 12, 30),
            test_mhs.end_dt
        )
        mhs_tester.prepareTest(test_name + "use year before")
        mhs_tester.assertFalse(test_mhs.use_year_before)
        mhs_tester.prepareTest(test_name + "trigger")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 12, 31),
            test_mhs.trigger
        )
        rs_mhs(prev_data)

        test_name = "12-29|"
        prev_data, test_mhs = sv_mhs()
        test_now = datetime.datetime.now()
        bday = datetime.date(1984, 12, 29)
        inc_year = int(bday.replace(year=test_now.year) < test_now.date())
        store.mas_player_bday_event.correct_pbday_mhs(bday)
        mhs_tester.prepareTest(test_name + "start dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 12, 29),
            test_mhs.start_dt
        )
        mhs_tester.prepareTest(test_name + "end dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 12, 31),
            test_mhs.end_dt
        )
        mhs_tester.prepareTest(test_name + "use year before")
        mhs_tester.assertTrue(test_mhs.use_year_before)
        mhs_tester.prepareTest(test_name + "trigger")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year + 1, 1, 1),
            test_mhs.trigger
        )
        rs_mhs(prev_data)

        test_name = "12-30|"
        prev_data, test_mhs = sv_mhs()
        test_now = datetime.datetime.now()
        bday = datetime.date(1984, 12, 30)
        inc_year = int(bday.replace(year=test_now.year) < test_now.date())
        store.mas_player_bday_event.correct_pbday_mhs(bday)
        mhs_tester.prepareTest(test_name + "start dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 12, 30),
            test_mhs.start_dt
        )
        mhs_tester.prepareTest(test_name + "end dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year + 1, 1, 1),
            test_mhs.end_dt
        )
        mhs_tester.prepareTest(test_name + "use year before")
        mhs_tester.assertTrue(test_mhs.use_year_before)
        mhs_tester.prepareTest(test_name + "trigger")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year + 1, 1, 2),
            test_mhs.trigger
        )
        rs_mhs(prev_data)

        test_name = "12-31|"
        prev_data, test_mhs = sv_mhs()
        test_now = datetime.datetime.now()
        bday = datetime.date(1984, 12, 31)
        inc_year = int(bday.replace(year=test_now.year) < test_now.date())
        store.mas_player_bday_event.correct_pbday_mhs(bday)
        mhs_tester.prepareTest(test_name + "start dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 12, 31),
            test_mhs.start_dt
        )
        mhs_tester.prepareTest(test_name + "end dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year + 1, 1, 2),
            test_mhs.end_dt
        )
        mhs_tester.prepareTest(test_name + "use year before")
        mhs_tester.assertTrue(test_mhs.use_year_before)
        mhs_tester.prepareTest(test_name + "trigger")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year + 1, 1, 3),
            test_mhs.trigger
        )
        rs_mhs(prev_data)

        test_name = "1-1|"
        prev_data, test_mhs = sv_mhs()
        test_now = datetime.datetime.now()
        bday = datetime.date(1984, 1, 1)
        inc_year = int(bday.replace(year=test_now.year) < test_now.date())
        store.mas_player_bday_event.correct_pbday_mhs(bday)
        mhs_tester.prepareTest(test_name + "start dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 1, 1),
            test_mhs.start_dt
        )
        mhs_tester.prepareTest(test_name + "end dt")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 1, 3),
            test_mhs.end_dt
        )
        mhs_tester.prepareTest(test_name + "use year before")
        mhs_tester.assertFalse(test_mhs.use_year_before)
        mhs_tester.prepareTest(test_name + "trigger")
        mhs_tester.assertEqual(
            datetime.datetime(test_now.year + inc_year, 1, 4),
            test_mhs.trigger
        )
        rs_mhs(prev_data)

    call dev_unit_tests_finish_test(mhs_tester)

    return

label dev_unit_test_utc_api:
    m "Running tests..."

    python:
        local_time = datetime.datetime.now().replace(microsecond=0)
        utc_time = datetime.datetime.utcnow().replace(microsecond=0)

        utc_tester = store.mas_dev_unit_tests.MASUnitTester()

        utc_tester.prepareTest("get_localzone")
        local_tz = store.mas_utils.get_localzone()
        utc_tester.assertIdentity(store.mas_utils._tz_cache, local_tz)

        utc_tester.prepareTest("reload_localzone")
        utc_tester.assertFalse(store.mas_utils.reload_localzone() is local_tz)

        utc_tester.prepareTest("local to utc")
        new_time = store.mas_utils.local_to_utc(local_time)
        utc_tester.assertIsNone(new_time.tzinfo)
        utc_tester.assertEqual(utc_time, new_time)

        utc_tester.prepareTest("utc to any")
        new_time = store.mas_utils.utc_to_any(utc_time, local_tz)
        utc_tester.assertIsNotNone(new_time.tzinfo)
        utc_tester.assertEqual(local_time, new_time.replace(tzinfo=None))

        utc_tester.prepareTest("utc to local")
        new_time = store.mas_utils.utc_to_local(utc_time)
        utc_tester.assertIsNotNone(new_time.tzinfo)
        utc_tester.assertEqual(local_time, new_time.replace(tzinfo=None))

    call dev_unit_tests_finish_test(utc_tester)

    return
