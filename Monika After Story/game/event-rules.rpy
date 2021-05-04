# Module that defines static classes used to create the rule tuples used in the
# Event class.
# The static classes are the ones used to manipulate the rule tuples
# Each class has a method named evaluate_rule

init -1 python:
    import datetime
    import store.mas_utils as mas_utils

    # special constants for rule type identifiers for the rule dict on Event class
    EV_RULE_RP_SELECTIVE = "rp_selective"
    EV_RULE_RP_NUMERICAL = "rp_numerical"
    EV_RULE_GREET_RANDOM = "greet_random"
    EV_RULE_FAREWELL_RANDOM = "farewell_random"
    EV_RULE_AFF_RANGE = "affection_range"
    EV_RULE_PRIORITY = "rule_priority"
    EV_RULE_PROBABILITY = "rule_probability"
    EV_RULE_REPEAT_TD = "rule_repeat_td"


    # special constants for numerical repeat rules
    EV_NUM_RULE_DAY = "day"
    EV_NUM_RULE_WEEK = "week"
    EV_NUM_RULE_MONTH = "month"
    EV_NUM_RULE_YEAR = "year"

    # list of those constants
    EV_NUM_RULES = [
        EV_NUM_RULE_DAY,
        EV_NUM_RULE_WEEK,
        EV_NUM_RULE_MONTH,
        EV_NUM_RULE_YEAR
    ]

    class MASNumericalRepeatRule(object):
        """
        Static Class used to create numerical repetition rules in tuple form.
        That tuple is then stored in a dict containing this rule name constant.
        Each rule is defined by a repeat which specifies the time interval for
        the repetition and an advance_by which specifies how many of the time
        intervals the next repetition is going to get scheduled.
        The repetition rule increases the event start_date and end_date and
        works seamlessly with the current calendar function.
        """

        @staticmethod
        def create_rule(repeat, advance_by=1, ev=None):
            """
            IN:
                repeat - An EV_NUM_RULE, that determines the time unit we'll be
                    using to increment the start_date and end_date
                advance_by - A positive integer used to determine how many times
                    the desired time unit will be added to start_date and
                    end_date
                    (Default: 1)
                ev - Event to add this rule to. This will replace exisiting
                    rules of the same key.
                    (Default: None)

            RETURNS:
                a dict containing the specified rule with the appropriate key
            """

            # raise exception if repeat is not a valid rule
            if repeat not in EV_NUM_RULES:
                raise Exception("'{0}' is not a valid repeat rule".format(repeat))

            # since repeat is correct we just check if advance by is higher than 0
            if advance_by > 0:

                rule = {EV_RULE_RP_NUMERICAL : (repeat, advance_by)}

                if ev:
                    ev.rules.update(rule)

                # return the dict containing the specified rule
                return rule

            # raise exception since advance by was 0 or lower
            raise Exception("'{0}' is not a valid 'advance_by' rule, it should be higher than 0".format(repeat))

        @staticmethod
        def update_dates(rule, check_time, ev=None, start_end_dates=None):
            """
            Updates the start_date and end_date to be the next possible dates
            checked against check_time

            IN:
                rule - a MASNumericalRepeatRule tuple containing the rules for the
                    appropiate update
                check_time - The time to check and update against
                ev - Event to update as well. This will update the existing
                    rules of the same key.
                    NOTE: this has priority over start_end_dates
                    (Default: None)
                start_end_date - tuple of the following format:
                    [0]: start_date
                    [1]: end_date
                    (Default: None)

            RETURNS:
                A tuple containing the new start_date and end_date. If bad
                values were given, (-1, -1) is returned
            """
            # sanity check
            if ev:
                # priortize event
                start_date = ev.start_date
                end_date = ev.end_date

            elif start_end_dates and len(start_end_dates) >= 2:
                # use range tuple
                start_date, end_date = start_end_dates

            else:
                # user gave us weird values
                return (-1, -1)

            # final check to ensure start and end date are appropriate
            if start_date is None or end_date is None:
                return (-1, -1)

            # Check if the event is already in the future so we don't do anything
            if check_time < end_date:
                return (start_date, end_date)

            # we get the difference between end and start date
            delta = end_date - start_date

            # unpack the tuple for easy manipulation
            repeat, advance_by = rule

            # define and initialize the new_end_date with old end_date
            new_end_date = end_date

            # store current time
            current = datetime.datetime.now()

            # repeat the time additions until we get a date in the future
            while new_end_date < current:

                # check if the rule is for days
                if repeat == EV_NUM_RULE_DAY:

                    # use timedelta to add days and get the new_end_date
                    new_end_date = new_end_date + datetime.timedelta(days=advance_by)

                # check if the rule is for weeks
                elif repeat == EV_NUM_RULE_WEEK:

                    # use timedelta to add weeks and get the new_end_date
                    new_end_date = new_end_date + datetime.timedelta(weeks=advance_by)

                # check if the rule is for months
                elif repeat == EV_NUM_RULE_MONTH:

                    # use the add_months function to add the required amount of months
                    new_end_date = mas_utils.add_months(new_end_date,advance_by)

                # check if the rule is for years
                elif repeat == EV_NUM_RULE_YEAR:

                    # use the add_year function to add the required amount of years
                    new_end_date = mas_utils.add_years(new_end_date, advance_by)

            # finally we determine the new_start_date by subtracting the delta
            new_start_date = new_end_date - delta

            # update event if we have one
            if ev:
                ev.start_date = new_start_date
                ev.end_date = new_end_date

            # return the new dates
            return (new_start_date, new_end_date)

        @staticmethod
        def evaluate_rule(
                check_time,
                ev,
                rule=None,
                skip_update=False,
                defval=True
            ):
            """
            Evaluates the rule given and updates the event's start_date and
            end_date

            IN:
                check_time - The datetime to check the rule against
                ev - The Event to check and update
                rule - a MASNumericalRepeatRule tuple containing the rules for the
                    appropiate update
                    If passed in, we use this instead of the given event's rule
                    (Default: None)
                skip_update - True means we shoudl skip updating the given
                    Event's rule.
                    (Default: False)
                defval - value to return if sanity checks fail or if the
                    event doesnt have a rule
                    (Default: True)

            RETURNS:
                True if the event date comply to the rule, False if it doesn't
            """
            # sanity check
            if ev is None:
                return defval

            # sanity check if we don' have start_date, end_date
            if ev.start_date is None or ev.end_date is None:
                return defval

            # sanity check for a rule to use
            if rule is None:

                if EV_RULE_RP_NUMERICAL not in ev.rules:
                    return defval

                # use event's rule if user didn't give us a rule
                rule = ev.rules[EV_RULE_RP_NUMERICAL]

            # if we skipping update, just check
            if skip_update:
                return ev.start_date <= check_time <= ev.end_date

            # call update dates to get the new start and end dates
            start_date, end_date = MASNumericalRepeatRule.update_dates(rule, check_time, ev=ev)

            # finally check if the event is available for the given datetime
            return start_date <= check_time <= end_date


    class MASSelectiveRepeatRule(object):
        """
        Static Class used to create selective repetition rules in tuple form.
        That tuple is then stored in a dict containing this rule name constant.
        Each rule is defined by a list of acceptable values for that rule.
        The rules then are evaluated against the current datetime.
        """

        @staticmethod
        def create_rule(
                seconds=None,
                minutes=None,
                hours=None,
                days=None,
                weekdays=None,
                months=None,
                years=None,
                ev=None
            ):
            """
            NOTE: these values are assumed to be the same as stored in datetime

            IN:
                seconds - list of seconds this rule will match to
                minutes - list of minutess this rule will match to
                hours - list of hours this rule will match to
                days - list of days this rule will match to
                weekdays - list of weekdays this rule will match to
                months - list of months this rule will match to
                years - list of years this rule will match to
                ev - Event to store this rule in, if not None
                    (Default: None)

            RETURNS:
                a dict containing the specified rules
            """

            # check if seconds are defined that they are valid
            if seconds and any([(s < 0 or s > 59) for s in seconds]):
                raise Exception("seconds are out of a valid range")

            # check if valid minutes
            if minutes and any([(m < 0 or m > 59) for m in minutes]):
                raise Exception("minutes are out of a valid range")

            # check for invalid hours
            if hours and any([(h < 0 or h > 23) for h in hours]):
                raise Exception("hours are out of a valid range")

            # check for invalid days
            if days and any([(d < 1 or d > 31) for d in days]):
                raise Exception("days are out of a valid range")

            # check for invalid weekdays
            if weekdays and any([(d < 0 or d > 6) for d in weekdays]):
                raise Exception("weekdays are out of a valid range")

            # check for invalid months
            if months and any([(m < 1 or m > 12) for m in months]):
                raise Exception("months are out of a valid range")

            # check for invalid years meaning from this year 2018 to 2100
            # Monika should be in our reality by then
            if years and any([(y < 2018 or y > 2100) for y in years]):
                raise Exception("seconds are out of a valid range")

            # return as a dict
            rule = {EV_RULE_RP_SELECTIVE : (seconds, minutes, hours, days, weekdays, months, years)}

            if ev:
                ev.rules.update(rule)

            return rule

        @staticmethod
        def evaluate_rule(check_time, ev=None, rule=None, defval=True):
            """
            Checks if the current_time is valid for the rule

            IN:
                check_time - The time to check against the rule
                ev - Event to check
                    NOTE: this takes prioriy over the rule param
                    (Default: None)
                rule - MASSelectiveRepeatRule to check
                    (Default: None)
                defval - value to return if this event doesn't have a rule
                    to check
                    (Default: True)

            RETURNS:
                A boolean value indicating if the time is in the defined interval
            """
            # check if we have an event that contains the rule we need
            # event rule takes priority so it's checked here
            if ev and EV_RULE_RP_SELECTIVE in ev.rules:
                rule = ev.rules[EV_RULE_RP_SELECTIVE]

            # sanity check if we don't have a rule return default
            if rule is None:
                return defval

            # unpack tuple for easy access
            seconds, minutes, hours, days, weekdays, months, years = rule

            # check if current seconds are in the valid interval
            if seconds and check_time.second not in seconds:
                return False

            # check if current minutes are in the valid interval
            if minutes and check_time.minute not in minutes:
                return False

            # check if hours are in the valid interval
            if hours and check_time.hour not in hours:
                return False

            # check if days are in the valid interval
            if days and check_time.day not in days:
                return False

            # check if weekdays are in the valid interval
            if weekdays and check_time.weekday() not in weekdays:
                return False

            # check if current months are in the valid interval
            if months and check_time.month not in months:
                return False

            # check if current years are in the valid interval
            if years and check_time.year not in years:
                return False

            # since we passed all checks we return true to indicate that we comply
            # to that rule
            return True

    class MASGreetingRule(object):
        """
        Static Class used to create greeting specific rules in tuple form.
        That tuple is then stored in a dict containing this rule name constant.
        Each rule is defined by a skip_visual boolean and a special random chance.
        skip_visual is used to store if the greeting should be executed without
        executing the normal visual setup, this is useful for special greetings
        random_chance is used to define the 1 in random_chance chance that this
        greeting can be called
        """

        @staticmethod
        def create_rule(
                ev=None,
                skip_visual=False,
                random_chance=0,
                setup_label=None,
                override_type=False,
                forced_exp=None
            ):
            """
            IN:
                ev - Event to create rule for, if passed in
                    (Default: None)
                skip_visual - A boolean stating wheter we should skip visual
                    initialization
                    (Default: False)
                random_chance - An int used to determine 1 in random_chance
                    special chance for this greeting to appear
                    If 0, we ignore this property
                    (Default: 0)
                setup_label - label to call right after this greeting is
                    selected. This happens before post_greeting_check.
                    (Default: None)
                override_type - True will let this greeting override type
                    checks during selection, False will not
                    (Default: False)
                forced_exp - FULL exp code we want to force
                    for the first spaceroom render
                    (Default: None)

            RETURNS:
                a dict containing the specified rules
            """

            # random_chance can't be negative
            if random_chance < 0:
                raise Exception("random_chance can't be negative")

            # setup_label must exist
            if setup_label is not None and not renpy.has_label(setup_label):
                raise Exception("'{0}' does not exist.".format(setup_label))

            # return the tuple inside a dict
            rule = {
                EV_RULE_GREET_RANDOM: (
                    skip_visual,
                    random_chance,
                    setup_label,
                    override_type,
                    forced_exp
                )
            }

            if ev:
                ev.rules.update(rule)

            return rule

        @staticmethod
        def evaluate_rule(event=None, rule=None, defval=True):
            """
            IN:
                event - the event to evaluate
                rule - the MASGreetingRule to check it's random_chance
                defval - value to return if event/rule doesn't exist
                    (Default: True)

            RETURNS:
                True if the random returned 1
            """
            # check if we have an event that contains the rule we need
            # event rule takes priority so it's checked here
            if event and EV_RULE_GREET_RANDOM in event.rules:
                rule = event.rules[EV_RULE_GREET_RANDOM]

            # sanity check if we don't have a rule return default
            if rule is None:
                return defval

            # unpack the tuple for easy access
            random_chance = rule[1]

            if random_chance == 0:
                # 0 chance, return default
                return defval

            # check if random_chance is less than 0 return False
            if random_chance <= 0:
                return False

            # Evaluate randint with a chance of 1 in random_chance
            return renpy.random.randint(1,random_chance) == 1

        @staticmethod
        def should_override_type(ev=None, rule=None):
            """
            IN:
                ev - the event to evaluate, gets priority
                rule - the MASGreetingRule to evaluate

            RETURNS: True if the rule should override types, false if not
            """
            if ev:
                rule = ev.rules.get(EV_RULE_GREET_RANDOM, None)

            if rule is not None and len(rule) > 3:
                return rule[3]

            return False

        @staticmethod
        def should_skip_visual(event=None, rule=None):
            """
            IN:
                event - the event to evaluate, gets priority
                rule - the MASGreetingRule to evaluate

            RETURNS:
                True if the rule is True to skip_visual
            """

            # returns the skip_visual boolean
            if event and EV_RULE_GREET_RANDOM in event.rules:
                return event.rules[EV_RULE_GREET_RANDOM][0]

            # returns the skip_visual boolean of the rule
            if rule:
                return rule[0]

            # False since there was no rule to check
            return False

        @staticmethod
        def get_setup_label(ev):
            """
            Gets th setup label from the given ev

            IN:
                ev - the event to evalute

            RETURNS: setup label, or NOne if not found
            """
            if ev:
                ev_tup = ev.rules.get(EV_RULE_GREET_RANDOM, None)
                if ev_tup is not None:
                    return ev_tup[2]

            return None

        @staticmethod
        def get_forced_exp(ev):
            """
            Gets the forced exp for an event

            IN:
                ev - the event to evalute

            OUT:
                string with full exp code, or None
            """
            if ev:
                ev_rule = ev.rules.get(EV_RULE_GREET_RANDOM, None)
                if ev_rule is not None:
                    return ev_rule[4]

            return None

    class MASFarewellRule(object):
        """
        Static Class used to create farewell specific rules in tuple form.
        That tuple is then stored in a dict containing this rule name constant.
        Each rule is defined by a special random chance.
        random_chance is used to define the 1 in random_chance chance that this
        farewell can be called
        """

        @staticmethod
        def create_rule(random_chance, ev=None):
            """
            IN:
                random_chance - An int used to determine 1 in random_chance
                    special chance for this farewell to appear
                ev - Event to create rule for, if passed in
                    (Default: None)

            RETURNS:
                a dict containing the specified rules
            """

            # random_chance can't be negative
            if random_chance < 0:
                raise Exception("random_chance can't be negative")

            # return the rule inside a dict
            rule = {EV_RULE_FAREWELL_RANDOM : random_chance}

            if ev:
                ev.rules.update(rule)

            return rule


        @staticmethod
        def evaluate_rule(event=None, rule=None):
            """
            IN:
                event - the event to evaluate
                rule - the MASFarewellRule to check it's random_chance

            RETURNS:
                True if the random returned 1
            """
            # check if we have an event that contains the rule we need
            # event rule takes priority so it's checked here
            if event and EV_RULE_FAREWELL_RANDOM in event.rules:
                rule = event.rules[EV_RULE_FAREWELL_RANDOM]

            # sanity check if we don't have a rule return False
            if rule is None:
                return False

            # store the rule for easy access
            # keeping this so when we add another rule we'll keep
            # the same code structure, also it's more readable changing the name
            random_chance = rule

            # check if random_chance is less or equal to 0 return False
            if random_chance <= 0:
                return False

            # Evaluate randint with a chance of 1 in random_chance
            return renpy.random.randint(1,random_chance) == 1

    class MASAffectionRule(object):
        """
        NOTE: DEPRECATED
        Use the aff_range property for Events instead

        Static Class used to create affection specific rules in tuple form.
        That tuple is then stored in a dict containing this rule name constant.
        Each rule is defined by a min and a max determining a range of affection
        to check against.
        """

        @staticmethod
        def create_rule(min, max, ev=None):
            """
            IN:
                min - An int representing the minimal(inclusive) affection required
                    for the event to be available, if None is passed is assumed
                    that there's no minimal affection
                max - An int representing the maximum(inclusive) affection required
                    for the event to be available, if None is passed is assumed
                    that there's no maximum affection
                ev - Event to create rule for, if passed in
                    (Default: None)

            RETURNS:
                a dict containing the specified rules
            """

            # both min and max can't be None at the same time, since that means
            # that this is not affection dependent
            if not min and not max:
                raise Exception("at least min or max must not be None")

            # return the rule inside a dict
            rule = {EV_RULE_AFF_RANGE : (min, max)}

            if ev:
                ev.rules.update(rule)

            return rule


        @staticmethod
        def evaluate_rule(event=None, rule=None, affection=None, noRuleReturn=False):
            """
            IN:
                event - the event to evaluate
                rule - the MASAffectionRule to check against
                affection - the affection to check the rule against

            RETURNS:
                True if the current affection is inside the rule range
            """

            # check if we have an event that contains the rule we need
            # event rule takes priority so it's checked here

            if event and EV_RULE_AFF_RANGE in event.rules:
                rule = event.rules[EV_RULE_AFF_RANGE]

            # sanity check if we don't have a rule return False
            if rule is None:
                return noRuleReturn

            # store affection for easy checking
            if not affection:
                affection = persistent._mas_affection["affection"]

            # unpack the rule for easy access
            min, max = rule

            # Evaluate if affection is inside the rule range, in case both are None
            # will return true (however that case should be catched on create_rule)
            return  (affection >= min and not max) or (min <= affection <= max)


    class MASPriorityRule(object):
        """
        Static class used to create priority rules. Priority rules are just
        integers that determine priority of somehting.
        Lower numbers mean higher priority.
        """
        DEF_PRIORITY = 500

        @staticmethod
        def create_rule(priority, ev=None):
            """
            IN:
                priority - the priority to set.
                    If None is passed in, we use the default priority value.
                ev - Event to add this rule to. This will replace existing
                    rules of the same key.
                    (Default: None)
            """
            if priority is None:
                priority = MASPriorityRule.DEF_PRIORITY

            if type(priority) is not int:
                raise Exception(
                    "'{0}' is not a valid in priority".format(priority)
                )

            rule = {EV_RULE_PRIORITY: priority}

            if ev:
                ev.rules.update(rule)

            return rule


        @staticmethod
        def get_priority(ev):
            """
            Gets the priority of the given event.

            IN:
                ev - event to get priority of

            RETURNS the priority of the given event, or def if no priorityrule
                is found
            """
            return ev.rules.get(EV_RULE_PRIORITY, MASPriorityRule.DEF_PRIORITY)


    class MASProbabilityRule(object):
        """
        Static class used to create probability rules.

        Probability rules are just integers that determine the probability of something being selected.


        Probabilities must be greater than 1

        This value is designed to be used with mas_utils.weightedChoice, and acts essentially akin to duplicating
        the choice `probability` times in the list
        """
        DEF_PROBABILITY = 1

        @staticmethod
        def create_rule(probability, ev=None):
            """
            IN:
                probability - the probability to set.
                    If None is passed in, we use the default probability value.
                    NOTE: If it is below 1 probability, is is set to 1

                ev - Event to add this rule to. This will replace existing
                    rules of the same key.
                    (Default: None)
            """
            if probability is None:
                probability = MASProbabilityRule.DEF_PROBABILITY

            elif probability < 1:
                probability = 1

            if not store.mas_ev_data_ver._verify_int(probability, allow_none=False):
                raise Exception(
                    "'{0}' is not a valid in probability".format(probability)
                )

            rule = {EV_RULE_PROBABILITY: probability}

            if ev:
                ev.rules.update(rule)

            return rule


        @staticmethod
        def get_probability(ev):
            """
            Gets the probability of the given event.

            IN:
                ev - event to get probability of

            OUT:
                The probability of the given event, or def if no ProbilityRule is found
            """
            return ev.rules.get(EV_RULE_PROBABILITY, MASProbabilityRule.DEF_PROBABILITY)

    class MASTimedeltaRepeatRule(object):
        """
        Static class used to create repeat rules.
        Timedelta repeat rules allow events to be repeated only every 'timedelta' since their last seen.
        """
        @staticmethod
        def create_rule(timedelta, ev=None):
            """
            IN:
                timedelta - the timedelta to set

                ev - the event to add this rule to
                    (Default: None)

            OUT:
                dict containing the rule
            """
            if not isinstance(timedelta, datetime.timedelta):
                raise Exception(
                    "MASTimedeltaRepeatRule expects a datetime.timedelta object, got: '{0}'.".format(timedelta)
                )

            elif not timedelta:
                raise Exception(
                    "MASTimedeltaRepeatRule expects a datetime.timedelta object with a non-null value."
                )

            rule = {EV_RULE_REPEAT_TD: timedelta}

            if ev:
                ev.rules.update(rule)

            return rule

        @staticmethod
        def evaluate_rule(event=None, rule=None, now=None):
            """
            Evaluates a MASTimedeltaRepeatRule rule

            IN:
                event - the event to evaluate
                rule - the timedelta of the MASTimedeltaRepeatRule to check against,
                    if None, we get it from the event
                    (Default: None)
                now - time to check against, if None, datetime.datetime.now() is used
                    (Default: None)

            OUT:
                boolean whether or not the event's passed
            """
            # No event, no deal
            if event is None:
                return False

            if rule is None:
                rule = event.rules.get(EV_RULE_REPEAT_TD, None)

            # Empty timedelta? You passed
            if not rule:
                return True

            if now is None:
                now = datetime.datetime.now()

            return event.timePassedSinceLastSeen_dt(rule, now)

init python:
    # these rules are NOT actually event rules since they don't create rule
    # data in Event.


    class MASUndoActionRule(object):
        """
        Static class used to undo ev actions when outside their date ranges
        """

        @staticmethod
        def create_rule(ev, start_date=None, end_date=None):
            """
            Creates the undoactionrule

            IN:
                - ev: event to add the rule to
                - start_date: start date of the event
                    if None passed, we use the event
                - end_date: end date of the event
                    if None passed, we use the event
            """
            if start_date is None:
                start_date = ev.start_date
            if end_date is None:
                end_date = ev.end_date

            MASUndoActionRule.create_rule_EVL(ev.eventlabel, start_date, end_date)

        @staticmethod
        def create_rule_EVL(evl, start_date, end_date):
            """
            Creates undo action rule from EVL:

            IN:
                evl - event label to add rule for
                start_date - start date to use
                end_date - end date to use
            """
            #Step 1, verify that our start/end dates are datetime.datetimes or datetime.dates
            if type(start_date) is not datetime.datetime and type(start_date) is not datetime.date:
                raise Exception(
                    "{0} is not a valid start_date (eventlabel: {1})".format(start_date, evl)
                )

            if type(end_date) is not datetime.datetime and type(start_date) is not datetime.date:
                raise Exception(
                    "{0} is not a valid end_date (eventlabel: {1})".format(end_date, evl)
                )

            #Step 2, we need to turn datetime.date into datetime.datetime
            if type(start_date) is datetime.date:
                start_date = datetime.datetime.combine(start_date, datetime.time())

            if type(end_date) is datetime.date:
                end_date = datetime.datetime.combine(end_date, datetime.time())

            #Step 3, we need to add this to a persistent dict because these dates will change upon
            #EV action being executed
            #However, we do not want to overwrite this on every load
            if not MASUndoActionRule.has_rule_EVL(evl):
                persistent._mas_undo_action_rules[evl] = (start_date, end_date)

        @staticmethod
        def has_rule(ev):
            """
            Checks if the event has an undo action rule associated with it

            IN:
                ev - event to check
            """
            return MASUndoActionRule.has_rule_EVL(ev.eventlabel)

        @staticmethod
        def has_rule_EVL(evl):
            """
            Checks if event label as undo action rule associated with it

            IN:
                evl - event label to check
            """
            return evl in persistent._mas_undo_action_rules

        @staticmethod
        def adjust_rule(ev, start_date, end_date):
            """
            Adjusts the start/end dates stored

            IN:
                ev - event to adjust
                start_date - new start date
                end_date - new end date
            """
            if MASUndoActionRule.has_rule(ev):
                persistent._mas_undo_action_rules[ev.eventlabel] = (
                    start_date,
                    end_date
                )

        @staticmethod
        def remove_rule(ev):
            """
            Removes the rule from the persistent dict

            IN:
                ev - event to remove
            """
            if MASUndoActionRule.has_rule(ev):
                persistent._mas_undo_action_rules.pop(ev.eventlabel)

        @staticmethod
        def evaluate_rule(ev):
            """
            Evaluates to see if we need to undo the actions based on the ev dates stored in our persistent dict

            IN:
                - ev - event to evaluate

            OUT:
                True if we are past the stored end date and we need to
            """
            #If the ev doesn't exist, we cannot do any work. This should be removed
            if not ev:
                return None

            #NOTE: This should be used AFTER init 7
            _start_date, _end_date = persistent._mas_undo_action_rules.get(ev.eventlabel, (None, None))

            #Check for invalid data
            if not _start_date or not _end_date:
                #No start or end date? That can't be right. We should remove this
                return None

            #Need to turn
            _now = datetime.datetime.now()

            #If we're before the start date, we should ensure that if someone time-travelled, this isn't still here
            #Dates shouldn't need to change in our stored values, though
            if _start_date > _now:
                return True

            #If we've passed the stored end date, then this isn't correct and we should reset to the actual ev dates
            if _end_date < _now:
                _start_date = ev.start_date
                _end_date = ev.end_date

                #We return none here
                if not _start_date or not _end_date:
                    return None

                MASUndoActionRule.adjust_rule(ev, _start_date, _end_date)

                #We're now past the dates and need to undo the action
                return True
            #We're still not at the date or we're within the dates, so we cannot go
            return False

        @staticmethod
        def check_persistent_rules():
            """
            Applies rules from persistent dict

            NOTE: uses mas_getEV
            """
            for ev_label in persistent._mas_undo_action_rules.keys():
                ev = mas_getEV(ev_label)
                #Since we can have differing returns, we store this to use later
                should_undo = MASUndoActionRule.evaluate_rule(ev)

                #If we do have the dates and we're out of the time period, we undo the action
                if ev is not None and should_undo:
                    Event._undoEVAction(ev)

                #If this is None, we need to pop due to bad data
                elif should_undo is None:
                    persistent._mas_undo_action_rules.pop(ev_label)

    class MASStripDatesRule(object):
        """
        Static class for the strip ev dates rule.
        This rule will strip the event dates when out of the date range
        """

        @staticmethod
        def create_rule(ev, end_date=None):
            """
            Creates the strip event dates rule

            IN:
                ev - event to create rules for
                - end_date: end date of the event
                    if None is passed, we use the event's end date
            """
            if end_date is None:
                end_date = ev.end_date

            #Step 1, verify that our end date is a datetime.datetime or datetime.date
            if type(end_date) is not datetime.datetime:
                raise Exception(
                    "{0} is not a valid end_date".format(end_date)
                )

            #Step 2, we need to turn datetime.date into datetime.datetime
            if type(end_date) is datetime.date:
                end_date = datetime.datetime.combine(end_date, datetime.time())

            #Step 3, add to persist dict
            #However, we do not want to overwrite this on every load
            if ev.eventlabel not in persistent._mas_strip_dates_rules:
                persistent._mas_strip_dates_rules[ev.eventlabel] = end_date


        @staticmethod
        def remove_rule(ev):
            """
            Removes the rule from the persistent dict
            """
            if ev.eventlabel in persistent._mas_strip_dates_rules:
                persistent._mas_strip_dates_rules.pop(ev.eventlabel)

        @staticmethod
        def evaluate_rule(ev):
            """
            Evaluates to see if we need to strip the ev dates based on the stored end date in the persistent
            dict

            IN:
                ev - event to check

            OUT:
                True if we are past the stored end date and we need to strip dates
            """
            #NOTE: This should be used AFTER init 7
            end_date = persistent._mas_strip_dates_rules.get(ev.eventlabel)

            if not ev or not end_date:
                #This ev doesn't exist and/or it doesn't exist in the rules dict, so no point checking this
                return False

            #If we've passed the stored end date, we need to axe the dates
            if end_date < datetime.datetime.now():
                #If this has an undo action rule associated with it, we need to remove it
                MASUndoActionRule.remove_rule(ev)
                #And now we need to self-remove too
                MASStripDatesRule.remove_rule(ev)
                return True

            #We're still not at the date or we're within the dates, no strip
            return False

        @staticmethod
        def check_persistent_rules(per_rules):
            """
            Applies rules from persistent dict

            NOTE: pulls from mas_getEV

            IN:
                per_rule - persistent dict of rules
            """
            for ev_label in per_rules.keys():
                ev = mas_getEV(ev_label)
                if ev is not None and MASStripDatesRule.evaluate_rule(ev):
                    ev.stripDates()
