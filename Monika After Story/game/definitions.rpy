define persistent.demo = False

define config.developer = False #This is the flag for Developer tools
# define persistent.steam = "steamapps" in config.basedir.lower()

python early:
    import singleton
    me = singleton.SingleInstance()
    # define the zorders
    MAS_MONIKA_Z = 10
    MAS_BACKGROUND_Z = 3

    # this is now global
    import datetime

    # uncomment when needed
    import traceback
    _dev_tb_list = []

    ### Overrides of core renpy things
    def dummy(*args, **kwargs):
        """
        Dummy function that does nothing
        """
        return

    class MASDummyClass(object):
        """
        Dummy class that does nothing.

        If compared to, it will always return False.
        """

        def __call__(self, *args, **kwargs):
            return MASDummyClass()

        def __len__(self):
            return 0

        def __getattr__(self, name):
            return MASDummyClass()

        def __setattr__(self, name, value):
            return

        def __lt__(self, other):
            return False

        def __le__(self, other):
            return False

        def __eq__(self, other):
            return False

        def __ne__(self, other):
            return False

        def __gt__(self, other):
            return False

        def __ge__(self, other):
            return False

        def __nonzero__(self):
            return False


    # clear this so no more traceback. We expect node loops anyway
    renpy.execution.check_infinite_loop = dummy

    class MASFormatter(renpy.substitutions.Formatter):
        """
        Our string formatter that uses more
        advanced formatting rules compared to the RenPy one
        """
        def get_field(self, field_name, args, kwargs):
            """
            Originally this method returns objects by references
            Our variant allows us to eval functions, e.g. "Text [my_func(arg1)]."
            and use negative indexes for iterables, e.g. "Text [my_iterable[-2]]."

            IN:
                field_name - the reference to the object
                args - not sure, but renpy doesn't use it (passes in an empty tuple)
                kwargs - the store modules where renpy will look for the object

            OUT:
                tuple of the object and its key
            """
            def _getStoreNameForObject(object_name, *scopes):
                """
                Returns the name of the store where the given object
                was defined or imported to

                IN:
                    object_name - the name of the object to look for (string)
                    scopes - the scopes where we look for the object (storemodule.__dict__)

                OUT:
                    name of the store module where the object was defined
                    or empty string if we couldn't find it
                """
                for scope in scopes:
                    if object_name in scope:
                        stores_names_list = [
                            store_module_name
                            for store_module_name, store_module in sys.modules.iteritems()
                            if store_module and store_module.__dict__ is scope
                        ]
                        if stores_names_list:
                            return stores_names_list[0]

                return ""

            # if it's a function call, we eval it
            if "(" in field_name:
                # split the string into its components
                func_name, paren, args = field_name.partition("(")

                # it still may include store modules, try to split it
                func_store_name, dot, func_name = func_name.partition(".")

                # with partition we'll always get the right bit in the first position
                # be it store module or function
                first = func_store_name

                # now we find the store's name to use in eval
                if isinstance(kwargs, renpy.substitutions.MultipleDict):
                    scope_store_name = _getStoreNameForObject(first, *kwargs.dicts)

                else:
                    scope_store_name = _getStoreNameForObject(first, kwargs)

                # apply formatting if appropriate
                if scope_store_name:
                    scope_store_name = "renpy.{0}.".format(scope_store_name)

                # finally get the value from the function
                obj = eval(
                    "{0}{1}{2}{3}{4}{5}".format(
                        scope_store_name,
                        func_store_name,
                        dot,
                        func_name,
                        paren,
                        args
                    )
                )

            # otherwise just get the reference
            else:
                first, rest = field_name._formatter_field_name_split()

                obj = self.get_value(first, args, kwargs)

                for is_attr, i in rest:
                    if is_attr:
                        obj = getattr(obj, i)

                    else:
                        # convert the accessor only if obj isn't a dict
                        # so the accessor is always a long for other iterables
                        if not isinstance(obj, dict):
                            i = long(i)

                        obj = obj[i]

            return obj, first

    # allows us to use a more advanced string formatting
    renpy.substitutions.formatter = MASFormatter()

    def mas_with_statement(trans, always=False, paired=None, clear=True):
        """
        Causes a transition to occur. This is the Python equivalent of the
        with statement

        IN:
            trans - the transition to use
            always - if True, the transition will always occur, even if the user has disabled transitions
            paired - Tom knows
            clear - if True cleans out transient stuff at the end of an interaction

        OUT:
            True if the user chose to interrupt the transition,
            and False otherwise
        """
        if renpy.game.context().init_phase:
            raise Exception("With statements may not run while in init phase.")

        if renpy.config.skipping:
            trans = None

        if not (renpy.game.preferences.transitions or always):
            trans = None

        renpy.exports.mode('with')

        if isinstance(paired, dict):
            paired = paired.get(None, None)

            if (trans is None) and (paired is None):
                return

        if isinstance(trans, dict):

            for k, v in trans.items():
                if k is None:
                    continue

                renpy.exports.transition(v, layer=k)

            if None not in trans:
                return

            trans = trans[None]

        return renpy.game.interface.do_with(trans, paired, clear=clear)

    renpy.exports.with_statement = mas_with_statement

    def mas_find_target(self):
        """
        This method tries to find an image by its reference. It can be a displayable or tuple.
        If this method can't find an image and it follows the pattern of Monika's sprites, it'll try to generate one.

        Main change to this function is the ability to auto generate displayables
        """
        name = self.name

        if isinstance(name, renpy.display.core.Displayable):
            self.target = name
            return True

        if not isinstance(name, tuple):
            name = tuple(name.split())

        def error(msg):
            self.target = renpy.text.text.Text(msg, color=(255, 0, 0, 255), xanchor=0, xpos=0, yanchor=0, ypos=0)

            if renpy.config.debug:
                raise Exception(msg)

        args = [ ]

        while name:
            target = renpy.display.image.images.get(name, None)

            if target is not None:
                break

            args.insert(0, name[-1])
            name = name[:-1]

        #Main difference:
        #Check if the sprite exists at all
        if not name:
            if (
                isinstance(self.name, tuple)
                and len(self.name) == 2
                and self.name[0] == "monika"
            ):
                #If this is a Monika sprite and it doesn't exist, we should try to generate it
                #We did some sanity checks, but just in case will use a try/except block
                try:
                    #Reset name
                    name = self.name
                    #Generate
                    store.mas_sprites.generate_images(name[1])
                    #Try to get the img again
                    target = renpy.display.image.images[name]

                #If we somehow failed, show the exception and return False
                except:
                    error("Image '%s' not found." % ' '.join(self.name))
                    return False

            else:
                error("Image '%s' not found." % ' '.join(self.name))
                return False

        try:
            a = self._args.copy(name=name, args=args)
            self.target = target._duplicate(a)

        except Exception as e:
            if renpy.config.debug:
                raise

            error(str(e))

        #Copy the old transform over.
        new_transform = self.target._target()

        if isinstance(new_transform, renpy.display.transform.Transform):
            if self.old_transform is not None:
                new_transform.take_state(self.old_transform)

            self.old_transform = new_transform

        else:
            self.old_transform = None

        return True

    renpy.display.image.ImageReference.find_target = mas_find_target

# uncomment this if you want syntax highlighting support on vim
# init -1 python:

    # special constants for event
    EV_ACT_PUSH = "push"
    EV_ACT_QUEUE = "queue"
    EV_ACT_UNLOCK = "unlock"
    EV_ACT_RANDOM = "random"
    EV_ACT_POOL = "pool"

    # list of those special constants
    EV_ACTIONS = [
        EV_ACT_PUSH,
        EV_ACT_QUEUE,
        EV_ACT_UNLOCK,
        EV_ACT_RANDOM,
        EV_ACT_POOL
    ]

    #### bitmask flags
    # all bitmask flags apply until next restart or the flag is unset.
    # NOTE: do NOT add a bitmask flag if you want to save its value.
    #   if you need saved data, add a new prop or use an existing one.

    EV_FLAG_HFM = 2
    # Hidden From Menus
    # this flag marks an event as temporarily hidden from all menus

    EV_FLAG_HFRS = 4
    # Hidden From Random Selection
    # this flag marks an event as temporarily hidden from all random-based
    # selection
    # Random-based selection consists of:
    #   - startup greetings
    #   - randomly selected farewells
    #   - random topics

    EV_FLAG_HFNAS = EV_FLAG_HFM | EV_FLAG_HFRS
    # Hidden from Non-Active Selection
    # combines hidden from menu and random select

    # TODO: when needed:
    # Hidden From Check Events - ignored in Event.checkEvents
    #   NOTE: this is potentially dangerous, so maybe we dont need
    # Hidden From Active Selection - like blacklisting queue/push actions

    #### End bitmask flags

    # custom event exceptions
    class EventException(Exception):
        def __init__(self, _msg):
            self.msg = _msg
        def __str__(self):
            return self.msg

    # event class for chatbot replacement
    # NOTE: effectively a wrapper for dict of tuples
    # NOTE: Events are TIED to the database they are found in. Moving databases
    #   is not supported ATM
    #
    # PROPERTIES:
    #   per_eventdb - persistent database (dict of tupes) this event is
    #       connectet to
    #       NOTE: REQUIRED
    #   eventlabel - the identifier for this event. basically the label that
    #       this event is tied to. MUST BE UNIQUE
    #       NOTE: REQUIRED
    #   prompt - String label shown on the button for this topic in the prompt
    #       menu
    #       (Default: eventlabel)
    #   label - Optional plain text name of the event, good for calendars
    #       (Default: prompt)
    #   category - Tuple of string that define the categories for the event
    #       (Default: None)
    #   unlocked - True if the event appears in the prompt menu, False if not
    #       (Default: False)
    #   random - True if the event can appear in random chatter, False if not
    #       (Default: False)
    #   pool - True if the event is in the pool of prompts that get drawn from
    #       when new prompts become randomly available, False if not
    #       (Default: False)
    #   conditional - string that is a conditional expression that can be
    #       executed via eval. This is checked at various points to determine
    #       if this event gets pushed to the stack or not
    #       (Default: None)
    #   action - an EV_ACTION constant that tells us what to do if the
    #       conditional is True (See EV_ACTIONS and EV_ACT_...)
    #       (Default: None)
    #   start_date - datetime for when this event is available
    #       NOTE: date can be provided, this will be converted to datetime
    #       (Default: None)
    #   end_date - datetime for when this event is no longer available
    #       NOTE: date can be provided, this will be converted to datetime
    #       (Default: None)
    #   unlock_date - datetime for when this event is unlocked
    #       (Default: None)
    #   shown_count - number of times this event has been shown to the user
    #       NOTE: this must be set by the caller, and it is asssumed that
    #           call_next_event is the only one who changes this
    #       NOTE: IF AN EVENT HAS BEEN SEEN, IT SHOULD ALWAYS HAVE A POSITIVE
    #           SHOWN COUNT. The only exception to this is if we crashed
    #           halfway through a topic, in which case we will know this
    #           since shown count will be 0 and the label would have been seen.
    #           In that circumstance, we should immediately update the shown
    #           count. (Event will not do this in case you need to do specific
    #           crash handling). Call syncShownCount on the event object to
    #           update shown count in the crash scenario
    #       (Default: 0)
    #   diary_entry - string that will be added as a diary entry if this event
    #       has been seen. This string will respect \n and other formatting
    #       characters. Can be None
    #       NOTE: diary entries cannot be longer than 500 characters
    #       NOTE: treat diary entries as single paragraphs
    #       (Default: None)
    #   rules - dict of special rules that this event uses for various cases.
    #       NOTE: this does not get svaed to persistent
    #       NOTE: refer to RULES documentation in event-rules
    #       NOTE: if you set this to None, you will break this forever
    #       (Default: empty dict)
    #   last_seen - datetime of the last time this topic has been seen
    #       (Default: None)
    #   years - list of years that this event repeats in.
    #       NOTE: requires start_date param to be not None
    #       NOTE: If this is given, the year part of start_date and end_date
    #           will be IGNORED
    #       (Default: None)
    #   sensitive - True means this is a sensitve topic, False means it is not
    #       (Default: False)
    #   aff_range - tuple of the following format:
    #       [0]: - low limit of affection where this event is available
    #           (inclusive)
    #           If None, assumed to be no lower limit
    #       [1]: - upper limit of affection where this event is available
    #           (inclusive)
    #           If None, assumed to be no uppwer limit
    #       If None, then event is considered to be always available regardless
    #       of affection level
    #       NOTE: the tuple items should be AFFECTION STATES.
    #           not using an affection state may break things
    #       (Default: None)
    #   show_in_idle - True if this Event can be shown during idle
    #       False if not
    #       (Default: False)
    #   flags - bitmask system that acts as unchanging or temporary flags.
    #       (Default: 0)
    class Event(object):

        # tuple constants
        T_EVENT_NAMES = {
            "eventlabel":0,
            "prompt":1,
            "label":2,
            "category":3,
            "unlocked":4,
            "random":5,
            "pool":6,
            "conditional":7,
            "action":8,
            "start_date":9,
            "end_date":10,
            "unlock_date":11,
            "shown_count":12,
            #"diary_entry":13, # NOTE: this will not be removed until later
            "last_seen":14,
            "years":15,
            "sensitive":16,
            "aff_range":17,
            "show_in_idle":18,
        }

        # name constants
        N_EVENT_NAMES = (
            "per_eventdb",
            "eventlabel",
            "locks",
            "rules",
            "diary_entry",
            "flags"
        )

        # filterables
        FLT = (
            "category", # 0
            "unlocked", # 1
            "random", # 2
            "pool", # 3
            "action", # 4
            "seen", # 5
            "excl_cat", # 6
            "moni_wants", # 7
            "sensitive", # 8
            "aff", # 9
            "flag_req", # 10
            "flag_ban", # 11
        )

        # other constants
        DIARY_LIMIT = 500

        # initaliztion locks
        # dict of tuples, where each item in the tuple represents each property
        # of an event. If the item is True, then the property cannot be
        # modified during object creation. If false, then the property can be
        # modified during object creation
        # NOTE: this is set in evhand at an init level of -500
        INIT_LOCKDB = None

        # action MAP
        # actions that should be done given an event
        # NOTE: this is actually populated later, at init level 1
        #   SEE the evhand store in event-handler
        # NOTE: action code should be callable on a given event object
        ACTION_MAP = dict()

        # Conditional cache
        # A map from conditional string to compiled code objects
        # (speeds up event checks)
        _conditional_cache = dict()

        # NOTE: _eventlabel is required, its the key to this event
        # its also how we handle equality. also it cannot be None
        def __init__(self,
                per_eventdb,
                eventlabel,
                prompt=None,
                label=None,
                category=None,
                unlocked=False,
                random=False,
                pool=False,
                conditional=None,
                action=None,
                start_date=None,
                end_date=None,
                unlock_date=None,
#                diary_entry=None,
                rules=dict(),
                last_seen=None,
                years=None,
                sensitive=False,
                aff_range=None,
                show_in_idle=False,
                flags=0
            ):

            # setting up defaults
            if not eventlabel:
                raise EventException("'_eventlabel' cannot be None")
            if per_eventdb is None:
                raise EventException("'per_eventdb' cannot be None")
            if action is not None and action not in EV_ACTIONS:
                raise EventException("'" + action + "' is not a valid action")
#            if diary_entry is not None and len(diary_entry) > self.DIARY_LIMIT:
#                raise Exception(
#                    (
#                        "diary entry for {0} is longer than {1} characters"
#                    ).format(eventlabel, self.DIARY_LIMIT)
#                )
            if rules is None:
                raise Exception(
                    "'{0}' - rules property cannot be None".format(eventlabel)
                )
            if (
                    start_date is not None
                    and type(start_date) is not datetime.datetime
                    and type(start_date) is not datetime.date
                ):
                raise Exception(
                    "'{0}' - invalid start date.".format(eventlabel)
                )
            if (
                    end_date is not None
                    and type(end_date) is not datetime.datetime
                    and type(end_date) is not datetime.date
                ):
                raise Exception(
                    "'{0}' - invalid end date.".format(eventlabel)
                )
            if years is not None and type(years) is not list:
                raise Exception(
                    "'{0}' - invalid years.".format(eventlabel)
                )

            # we'll simplify aff_range so we dont have to deal with extra
            #   storage
            if aff_range is not None:
                low, high = aff_range
                if low is None and high is None:
                    aff_range = None

            # and then check for valid affection states
            # NOTE: we assume that the affection store is visible by now
            if not store.mas_affection._isValidAffRange(aff_range):
                raise Exception("{0} | bad aff range: {1}".format(
                    eventlabel, str(aff_range)
                ))

            if not isinstance(flags, int):
                raise Exception("'{0}' - invalid flags".format(eventlabel))

            self.eventlabel = eventlabel
            self.per_eventdb = per_eventdb

            # default prompt is the eventlabel
            if not prompt:
                prompt = self.eventlabel

            # default label is a prompt
            if not label:
                label = prompt

            # convert dates to datetimes
            if type(start_date) is datetime.date:
                start_date = datetime.datetime.combine(
                    start_date,
                    datetime.time.min
                )
            if type(end_date) is datetime.date:
                end_date = datetime.datetime.combine(
                    end_date,
                    datetime.time.min
                )

            self.rules = rules
            self.flags = flags

            # this is the data tuple. we assemble it here because we need
            # it in two different flows
            data_row = (
                self.eventlabel,
                prompt,
                label,
                category,
                unlocked,
                random,
                pool,
                conditional,
                action,
                start_date,
                end_date,
                unlock_date,
                0, # shown_count
                "", # diary_entry
                last_seen,
                years,
                sensitive,
                aff_range,
                show_in_idle
            )

            stored_data_row = self.per_eventdb.get(eventlabel, None)

            # if the item exists, reform data if the length has increased
            # if the length shrinks, use updates scripts
            if stored_data_row:

                stored_data_list = list(stored_data_row)

                # first, check for lock existence
                lock_entry = Event.INIT_LOCKDB.get(eventlabel, None)

                if lock_entry:

                    if len(stored_data_row) < len(data_row):
                        # with differing lengths, we need to append the
                        # changes to the stored data row prior to update
                        # using the lock entry
                        stored_data_list.extend(
                            data_row[len(stored_data_row):]
                        )

                    # if the lock exists, then iterate through the names
                    # and only update items that are unlocked
                    for name,index in Event.T_EVENT_NAMES.iteritems():

                        if not lock_entry[index]:
                            stored_data_list[index] = data_row[index]

                    self.per_eventdb[eventlabel] = tuple(stored_data_list)

                else:
                    # otherwise, no lock entry, update normally

                    if len(stored_data_row) < len(data_row):
                        # splice and dice
                        data_row = list(data_row)
                        data_row[0:len(stored_data_list)] = stored_data_list
                        self.per_eventdb[self.eventlabel] = tuple(data_row)

                    # actaully this should be always
                    self.prompt = prompt
                    self.category = category
#                    self.diary_entry = diary_entry
#                    self.rules = rules
                    self.years = years
                    self.sensitive = sensitive
                    self.aff_range = aff_range
                    self.show_in_idle = show_in_idle

            # new items are added appropriately
            else:
                # add this data to the DB
                self.per_eventdb[self.eventlabel] = data_row

            # setup lock entry
            Event.INIT_LOCKDB.setdefault(eventlabel, mas_init_lockdb_template)

            # Cache conditional
            if self.conditional is not None and self.conditional not in Event._conditional_cache:
                Event._conditional_cache[self.conditional] = renpy.python.py_compile(self.conditional, "eval")

        def __eq__(self, other):
            """
            Equality override

            IN:
                other - the object to compare this event with

            OUT:
                boolean
            """
            if isinstance(self, other.__class__):
                return self.eventlabel == other.eventlabel
            return False

        def __ne__(self, other):
            """
            Non-equality override

            IN:
                other - the object to compare this event with

            OUT:
                boolean
            """
            return not self.__eq__(other)

        def __setattr__(self, name, value):
            """
            Override of setattr so we can do cool things

            IN:
                name - the name of the prop to change (str)
                value - the new value
            """
            if name in self.N_EVENT_NAMES:
                super(Event, self).__setattr__(name, value)
#                self.__dict__[name] = value

            # otherwise, figure out the location of an attribute, then repack
            # a tup
            else:
                attr_loc = self.T_EVENT_NAMES.get(name, None)

                if attr_loc:
                    # found the location
                    data_row = self.per_eventdb.get(self.eventlabel, None)

                    if not data_row:
                        # couldnt find this event, raise excp
                        raise EventException(
                            self.eventlabel + " not found in eventdb"
                        )

                    # if we are dealing with start/end dates, we need to
                    #   ensure that they are datetimes
                    if name == "start_date" or name == "end_date":
                        if type(value) is datetime.date:
                            value = datetime.datetime.combine(
                                value,
                                datetime.time.min
                            )

                        # nullify bad date types
                        if type(value) is not datetime.datetime:
                            value = None

                    # If we are setting a conditional, we may need to compile it
                    elif (
                        name == "conditional"
                        and value is not None
                        and value not in Event._conditional_cache
                    ):
                        Event._conditional_cache[value] = renpy.python.py_compile(value, "eval")

                    # otherwise, repack the tuples
                    data_row = list(data_row)
                    data_row[attr_loc] = value
                    data_row = tuple(data_row)

                    # now put it back in the dict
                    self.per_eventdb[self.eventlabel] = data_row

                else:
                    raise EventException(
                        "'{0}' is not a valid attribute for Event".format(name)
                    )

        # get attribute ovverride
        def __getattr__(self, name):
            attr_loc = self.T_EVENT_NAMES.get(name, None)

            if attr_loc:
                # found the location
                data_row = self.per_eventdb.get(self.eventlabel, None)

                if not data_row:
                    # couldnt find this event, raise exp
                    raise EventException(
                        self.eventlabel + " not found in db"
                    )

                # otherwise return the attribute
                return data_row[attr_loc]

            else:
                return super(Event, self).__getattribute__(name)

        #repr override
        def __repr__(self):
            return "<Event: (evl: {0})>".format(self.eventlabel)

        def monikaWantsThisFirst(self):
            """
            Checks if a special instant key is in this Event's rule dict

            RETURNS: True if the this key is here, false otherwise
            """
            return (
                self.rules is not None
                and "monika wants this first" in self.rules
            )

        def allflags(self, flags):
            """
            Checks if this event has ALL flags from flags

            IN:
                flags - flags to check

            RETURNS: True if all flags from flags is in this event's flags
            """
            return (flags & ~self.flags) == 0

        def anyflags(self, flags):
            """
            Checks if this event has ANY flag from flags

            IN:
                flags - flags to check

            RETURNS: True if any flag from flags is in this event's flag
            """
            return (self.flags & flags) != 0

        def checkAffection(self, aff_level):
            """
            Checks if the given aff_level is within range of this event's
            aff_range.

            IN:
                aff_level - aff_level to check

            RETURNS: True if aff_level is within range of event's aff_range,
                False otherwise
            """
            if self.aff_range is None:
                return True

            # otheerwise check the range
            low, high = self.aff_range
            return store.mas_affection._betweenAff(low, aff_level, high)

        def checkConditional(self, globals=None, locals=None):
            """
            Checks conditional of this event

            IN:
                globals - global scope for eval. If None, the base store is used.
                    (Default: None)
                locals - local scope for eval. If None, set to globals.
                    (Default: None)

            OUT:
                boolean:
                    True if passed, False if not
            """
            if self.conditional is None:
                return True

            return renpy.python.py_eval_bytecode(Event._conditional_cache[self.conditional], globals=globals, locals=locals)

        def canRepeat(self):
            """
            Checks if this event has the vars to enable repeat

            RETURNS: True if this event can repeat, False if not
            """
            return (
                self.start_date is not None
                and self.end_date is not None
                and self.years is not None
            )

        def flag(self, flags):
            """
            Adds flags from the given flags to this event's flags

            IN:
                flags - flags to add to this event
            """
            self.flags |= flags

        def prepareRepeat(self, force=False):
            """
            Prepres this event's dates for a repeat.

            NOTE: does not check if the event hasnt been reached this year.

            IN:
                force - If True, we force the years to change
                    (Default: False)

            RETURNS: True if this event can repeat, False if not
            """
            # sanity check
            if not self.canRepeat():
                return False

            new_start, new_end, was_changed = Event._yearAdjustEV(self, force)

            if was_changed:
                if self.isWithinRange():
                    store.evhand.addYearsetBlacklist(
                        self.eventlabel,
                        self.end_date
                    )
                self.start_date = new_start
                self.end_date = new_end

            return True

        def isWithinRange(self, check_dt=None):
            """
            Checks if the given dt is within range of this events start/end

            IN:
                check_dt - datetime to check, if None passed, we use .now()

            RETURNS: True if within range, False if not within range, None
                if no dts to compare
            """
            if self.start_date is None or self.end_date is None:
                return None
            check_dt = datetime.datetime.now()
            return self.start_date <= check_dt < self.end_date

        def stripDates(self):
            """
            Removes date data from the event
            """
            self.start_date = None
            self.end_date = None

        def syncShownCount(self):
            """
            Updates shown count if it is < 1 but we have seen the label
            """
            if self.shown_count < 1 and renpy.seen_label(self.eventlabel):
                self.shown_count = 1

        def timePassedSinceLastSeen_d(self, time_passed, _now=None):
            """
            Checks if time_passed amount of time has passed since we've last seen this event, in terms of datetime.date
            (Excludes hours, minutes, seconds, and microseconds)

            IN:
                time_passed - amount of time to check should have passed
                _now - current time. If None, now is assumed (Default: None)

            OUT:
                boolean:
                    - True if the amount of time provided has passed since we've last seen this event
                    - False otherwise

            NOTE: This can only be used after init 2 as mas_timePastSince() doesn't exist otherwise
            """
            if self.last_seen is not None:
                last_seen_date = self.last_seen.date()
            else:
                last_seen_date = None

            return mas_timePastSince(last_seen_date, time_passed, _now)

        def timePassedSinceLastSeen_dt(self, time_passed, _now=None):
            """
            Checks if time_passed amount of time has passed since we've last seen this event, precise to datetime.datetime
            (Includes hours, minutes, seconds, and microseconds)

            IN:
                time_passed - amount of time to check should have passed
                _now - current time. If None, now is assumed (Default: None)

            OUT:
                boolean:
                    - True if the amount of time provided has passed since we've last seen this event
                    - False otherwise

            NOTE: This can only be used after init 2 as mas_timePastSince() doesn't exist otherwise
            """
            return mas_timePastSince(self.last_seen, time_passed, _now)

        def unflag(self, flags):
            """
            Removes given flags from this event's flags

            IN:
                flags - flags to remove from this event
            """
            self.flags &= ~flags

        @classmethod
        def validateConditionals(cls):
            """
            A method to validate conditionals

            ASSUMES:
                mas_all_ev_db
            """
            for ev in mas_all_ev_db.itervalues():
                if ev.conditional is not None:
                    try:
                        renpy.python.py_eval_bytecode(cls._conditional_cache[ev.conditional])

                    except Exception as e:
                        raise EventException(
                            "Failed to evaluate the '{0}' conditional for the event with the '{1}' label:\n{2}.".format(
                                ev.conditional,
                                ev.eventlabel,
                                traceback.format_exc()
                            )
                        )

        @staticmethod
        def getSortPrompt(ev):
            #
            # Special function we use to get a lowercased version of the prompt
            # for sorting purposes
            return renpy.substitute(ev.prompt).lower()

        @staticmethod
        def getSortShownCount(ev):
            """
            Function used for sorting by shown counts

            RETURNS: the shown_count property of an event
            """
            return ev.shown_count

        @staticmethod
        def lockInit(name, ev=None, ev_label=None):
            """
            Locks the property for a given event object or eventlabel.
            This will prevent the property from being overwritten on object
            creation.

            IN:
                name - name of property to lock
                ev - Event object to property lock
                    (Default: None)
                ev_label - event label of Event to property lock
                    (Default: None)
            """
            Event._modifyInitLock(name, True, ev=ev, ev_label=ev_label)


        @staticmethod
        def unlockInit(name, ev=None, ev_label=None):
            """
            Unlocks the property for a given event object or event label.
            This will allow the property to be overwritten on object creation.

            IN:
                name - name of property to lock
                ev - Event object to property lock
                    (Default: None)
                ev_label - event label of Event to property lock
                    (Default: None)
            """
            Event._modifyInitLock(name, False, ev=ev, ev_label=ev_label)


        @staticmethod
        def _modifyInitLock(name, value, ev=None, ev_label=None):
            """
            Modifies the init lock for a given event/eventlabel

            IN:
                name - name of property to modify
                value - value to set the property
                ev - Eveng object to property lock
                    (Default: None)
                ev_label - event label of Event to property lock
                    (Default: None)
            """
            # check if we have somthing to work with
            if ev is None and ev_label is None:
                return

            # check if we have a valid property
            property_dex = Event.T_EVENT_NAMES.get(name, None)
            if property_dex is None:
                return

            # prioritize Event over evlabel
            if ev:
                ev_label = ev.eventlabel

            # now lock the property
            lock_entry = list(Event.INIT_LOCKDB[ev_label])
            lock_entry[property_dex] = value
            Event.INIT_LOCKDB[ev_label] = tuple(lock_entry)


        @staticmethod
        def _verifyAndSetDatesEV(ev):
            """
            Runs _verifyDatesEV and sets the event properties if change
            happens

            IN:
                ev - event object to verify and set

            RETURNS: was_changed
            """
            new_start, new_end, was_changed = Event._verifyDatesEV(ev)
            if was_changed:
                ev.start_date = new_start
                ev.end_date = new_end

            return was_changed


        @staticmethod
        def _verifyDatesEV(ev):
            """
            _verifyDates, but for an Event object.

            IN:
                ev - event object to verify dates

            RETURNS: See _verifyDates
            """
            return Event._verifyDates(ev.start_date, ev.end_date, ev.years)


        @staticmethod
        def _yearAdjustEV(ev, force=False):
            """
            _yearAdjust, but for an Event object

            IN:
                ev - evnet object to adjust years
                force - if True, we force years to update
                    (Default: False)

            RETURNS: See _verifyDates
            """
            return Event._yearAdjust(
                ev.start_date,
                ev.end_date,
                ev.years,
                force
            )


        @staticmethod
        def _verifyDates(_start, _end, _years):
            """
            Given start/end/_yeras, figure out the appropriate start and end
            dates. We use current datetime to figure this out.

            NOTE: this is meant for Event use ONLY
            NOTE: this is NOT meant to be used with an Event object.
                See _verifyDatesEV

            IN:
                _start - start datetime
                _end - end datetime (exclusive)
                _years - years list

            RETURNS tuple of the following format:
                [0]: start datetime to use
                [1]: end datetime to use
                [2]: True if there was and adjustment, False if not
            """
            # initial sanity check
            if _start is None or _end is None or _years is None:
                # if at least one item is None, this is not a repeatable.
                return (_start, _end, False)

            # otherwise, we need to repeat
            return Event._yearAdjust(_start, _end, _years)


        @staticmethod
        def _yearAdjust(_start, _end, _years, force=False):
            """
            Performs the year adjustment algorithm.

            IN:
                force - If True, we force year to update
                    (Default: False)

            RETURNS: see _verifyDates
            """
            _now = datetime.datetime.now()

            # no changes necessary if we are currently in the zone
            if (_start <= _now < _end) and not force:
                return (_start, _end, False)

            # otherwise, we need to repeat.
            add_yr_fun = store.mas_utils.add_years

            if len(_years) == 0:
                # years is empty list, we are repeat yearly.

                if force:
                    # force mode means we always update year
                    return (add_yr_fun(_start, 1), add_yr_fun(_end, 1), True)

                # we only need to check if current works, and if not,
                # move to one year ahead of current.
                diff = _now.year - _start.year
                new_end = add_yr_fun(_end, diff)

                if new_end <= _now:
                    # in this case, we should actually be +1 current year
                    diff += 1
                    new_end = add_yr_fun(_end, diff)

                # now return the new start and the modified end
                return (add_yr_fun(_start, diff), new_end, diff != 0)

            # otherwise, we have a list of years, and shoudl determine next
            if force:
                # forcing means we should look forward from teh current
                # year
                new_years = [
                    year
                    for year in _years
                    if year > _now.year
                ]

            else:
                new_years = [
                    year
                    for year in _years
                    if year >= _now.year
                ]

            if len(new_years) == 0:
                # no repeat years, we have already reached the limit.
                return (_start, _end, False)

            new_years.sort()

            # calc diff for the first year in this list
            diff = _now.year - new_years[0]
            new_end = add_yr_fun(_end, diff)

            if force:
                # force means we should just use this diff right away
                return (add_yr_fun(_start, diff), new_end, diff != 0)

            if new_end <= _now:
                if len(new_years) <= 1:
                    # no more years, so we should just not change anything
                    return (_start, _end, False)

                # otherwise, we can get a valid setup by going 1 further.
                diff = _now.year - new_years[1]
                new_end = add_yr_fun(_end, diff)

            return (add_yr_fun(_start, diff), new_end, diff != 0)


        @staticmethod
        def _getNextYear(_years, year_comp):
            """
            Retreieves the next possible year into the future from the given
            years list.

            NOTE: if empty list, we return current year.

            IN:
                _years - list of years
                year_comp - year to start search from.

            RETURNS next possible year into the future from the given years
                list. If _years is empty, current year is returned.
                If unable to find a next year, we return None.
            """
            # empty lits means repeat yearly
            if len(_years) == 0:
                return datetime.date.today().year

            # non empty list means we should repeat on these years
            new_years = [
                year
                for year in _years
                if year > year_comp
            ]

            # no new years to repeat, no repeats needed
            if len(new_years) == 0:
                return None

            # otherwise, return the next year in the list
            return sorted(new_years)[0]


        @staticmethod
        def _filterEvent(
                event,
                category=None,
                unlocked=None,
                random=None,
                pool=None,
                action=None,
                seen=None,
                excl_cat=None,
                moni_wants=None,
                sensitive=None,
                aff=None,
                flag_req=None,
                flag_ban=None
        ):
            """
            Filters the given event object accoridng to the given filters
            NOTE: NO SANITY CHECKS

            For variable explanations, please see the static method
            filterEvents

            RETURNS:
                True if this event passes the filter, False if not
            """

            # collections allow us to match all
            from collections import Counter

            # NOTE: this is done in an order to minimize branching.

            # now lets filter
            if unlocked is not None and event.unlocked != unlocked:
                return False

            if aff is not None and not event.checkAffection(aff):
                return False

            if random is not None and event.random != random:
                return False

            if pool is not None and event.pool != pool:
                return False

            if flag_ban is not None and event.anyflags(flag_ban):
                return False

            if flag_req is not None and event.allflags(flag_req):
                return False

            if seen is not None and renpy.seen_label(event.eventlabel) != seen:
                return False

            if category is not None:
                # USE OR LOGIC
                if category[0]:
                    if not event.category or len(set(category[1]).intersection(set(event.category))) == 0:
                        return False

                # USE AND logic
                elif not event.category or len(set(category[1]).intersection(set(event.category))) != len(category[1]):
                    return False

            if action is not None and event.action not in action:
                return False

            if excl_cat is not None:
                # list is empty and event.category isn't
                if not excl_cat and event.category:
                    return False

                # check if they have categories in common
                if event.category and len(set(excl_cat).intersection(set(event.category))) > 0:
                    return False

            # sensitivyt
            if sensitive is not None and event.sensitive != sensitive:
                return False

            # check if event contains the monika wants this rule
            if moni_wants is not None and event.monikaWantsThisFirst() != moni_wants:
                return False

            # we've passed all the filtering rules somehow
            return True

        @staticmethod
        def filterEvents(events, **flt_args):
            """
            Filters the given events dict according to the given filters.
            HOW TO USE: Use ** to pass in a dict of filters. they must match
            the names we use here.

            IN:
                events - the dict of events we want to filter
                **flt_args - see FILTERING RULES below for name=value rules

            FILTERING RULES: (recommend to use **kwargs)
            NOTE: None means we ignore that filtering rule
                category - Tuple of the following format:
                    [0]: True means we use OR logic. False means AND logic.
                    [1]: Tuple/list of strings that to match category.
                    (Default: None)
                    NOTE: If either element is None, we ignore this
                        filtering rule.
                unlocked - boolean value to match unlocked attribute.
                    (Default: None)
                random - boolean value to match random attribute
                    (Default: None)
                pool - boolean value to match pool attribute
                    (Default: None)
                action - Tuple/list of strings/EV_ACTIONS to match action
                    NOTE: OR logic is applied
                    (Default: None)
                seen - boolean value to match renpy.seen_label
                    (True means include seen, False means dont include seen)
                    (Default: None)
                excl_cat - list of categories to exclude, if given an empty
                    list it filters out events that have a non-None category
                    (Default: None)
                moni_wants - boolean value to match if the event has the monika
                    wants this first.
                    (Default: None )
                sensitive - boolean value to match if the event is sensitive
                    or not
                    NOTE: if None, we use inverse of _mas_sensitive_mode, only
                        if sensitive mode is True.
                        AKA: we only filter sensitve topics if sensitve mode is
                        enabled.
                    (Default: None)
                aff - affection level to match aff_range
                    (Default: None)
                flag_req - flags that the event must match
                    (Default: None)
                flag_ban - flags that the event must NOT have
                    (Default: None)

            RETURNS: copy of references of the Events in a new dict with
                the given filters applied.
                if the given events is None, empty, or no filters are given,
                events is returned
            """
            # sanity check
            if (
                    not events
                    or len(events) == 0
                    or store.mas_utils.all_none(data=flt_args)
            ):
                return events

            # copy check
#            if full_copy:
#                from copy import deepcopy

            # setup keys
            cat_key = Event.FLT[0]
            act_key = Event.FLT[4]
            sns_key = Event.FLT[8]

            # validate filter rules
            category = flt_args.get(cat_key)
            if (
                    category
                    and (
                        len(category) < 2
                        or category[0] is None
                        or category[1] is None
                        or len(category[1]) == 0
                    )
            ):
                flt_args[cat_key] = None

            action = flt_args.get(act_key)
            if action and len(action) == 0:
                flt_args[act_key] = None

            sensitive = flt_args.get(sns_key)
            if sensitive is None:
                try:
                    # i have no idea if this is reachable from here
                    if persistent._mas_sensitive_mode:
                        flt_args[sns_key] = False
                except:
                    pass

            filt_ev_dict = dict()

            # python 2
            for k,v in events.iteritems():
                # time to apply filtering rules
                if Event._filterEvent(v, **flt_args):
                    filt_ev_dict[k] = v

            return filt_ev_dict

        @staticmethod
        def getSortedKeys(events, include_none=False):
            #
            # Returns a list of eventlables (keys) of the given dict of events
            # sorted by the field unlock_date. The list is sorted in
            # chronological order (newest first). Events with an unlock_date
            # of None are not included unless include_none is True, in which
            # case, Nones are put after everything else
            #
            # IN:
            #   events - dict of events of the following format:
            #       eventlabel: event object
            #   include_none - True means we include events that have None for
            #       unlock_date int he sorted key list, False means we dont
            #       (Default: False)
            #
            # RETURNS:
            #   list of eventlabels (keys), sorted in chronological order.
            #   OR: [] if the given events is empty or all unlock_date fields
            #   were None and include_none is False

            # sanity check
            if not events or len(events) == 0:
                return []

            # dict check
            ev_list = events.values() # python 2

            # none check
            if include_none:
                none_labels = list()

            # insertion sort
            eventlabels = list()
            for ev in ev_list:

                if ev.unlock_date is not None:
                    index = 0

                    while (index < len(eventlabels)
                            and ev.unlock_date < events[
                                eventlabels[index]
                            ].unlock_date):
                        index += 1
                    eventlabels.insert(index, ev.eventlabel)

                elif include_none: # eventlabel was none
                    none_labels.append(ev.eventlabel)

            if include_none:
                eventlabels.extend(none_labels)

            # final sanity check
            if len(eventlabels) == 0:
                return []

            return eventlabels

        @staticmethod
        def checkConditionals(events, rebuild_ev=False):
            # NOTE: DEPRECATED
            #
            # This checks the conditionals for all of the events in the event list
            # if any evaluate to true, run the desired action then clear the
            # conditional.
            #
            # IN:
            #   rebulid_ev - pass in True to notify idle to rebuild events
            #       if a random action occured.
            import datetime

            # sanity check
            if not events or len(events) == 0:
                return None

            _now = datetime.datetime.now()

            for ev_label,ev in events.iteritems():
                # TODO: honestly, we should index events with conditionals
                #   so we only check what needs to be checked. Its a bit of an
                #   annoyance to check all of these properties once per minute.

                # NOTE: we only check events with:
                #   - a conditional property
                #   - current affection is within aff_range
                #   - has None for date properties

                if (
                        # has conditional property
                        ev.conditional is not None

                        # within aff range
                        and ev.checkAffection(mas_curr_affection)

                        # no date props
                        and ev.start_date is None
                        and ev.end_date is None

                        # check if the action is valid
                        and ev.action in Event.ACTION_MAP

                        # finally check if the conditional is true
                        and eval(ev.conditional)
                    ):

                    # perform action
                    Event._performAction(
                        ev,
                        unlock_time=_now,
                        rebuild_ev=rebuild_ev
                    )

                    #Clear the conditional
                    ev.conditional = None


            return events

        @staticmethod
        def checkCalendar(events):
            # NOTE: DEPRECATED
            #
            # This checks the date for all events to see if they are active.
            # If they are active, then it checks for a conditional, and evaluates
            # if an action should be run.
            import datetime

            # sanity check
            if not events or len(events) == 0:
                return None

            # dict check
            ev_list = events.keys() # python 2

            current_time = datetime.datetime.now()
            # insertion sort
            for ev in ev_list:

                e = events[ev]

                #If the event has no time-dependence, don't check it
                if (e.start_date is None) and (e.end_date is None):
                    continue

                #Calendar must be based on a date
                if e.start_date is not None:
                    if e.start_date > current_time:
                        continue

                if e.end_date is not None:
                    if e.end_date <= current_time:
                        continue

                if e.conditional is not None:
                    if not eval(e.conditional):
                        continue


                if e.action in Event.ACTION_MAP:
                    # perform action
                    Event._performAction(e, unlock_time=current_time)

                    # Check if we have a years property
                    if e.years is not None:

                        # if it's an empty list
                        if len(e.years) == 0:

                            # get event ready for next year
                            e.start_date = store.mas_utils.add_years(e.start_date, 1)
                            e.end_date = store.mas_utils.add_years(e.end_date, 1)
                            continue

                        # if it's not empty, get all the years that are in the future
                        new_years = [year for year in e.years if year > e.start_date.year]

                        # if we have possible new years
                        if len(new_years) > 0:
                            # sort them to ensure we get the nearest one
                            new_years.sort()

                            # pick it
                            new_year = new_years[0]

                            # get the difference
                            diff = new_year - e.start_date.year

                            # update event for the year it should repeat
                            e.start_date = store.mas_utils.add_years(e.start_date, diff)
                            e.end_date = store.mas_utils.add_years(e.end_date, diff)
                            continue

                    # Clear the conditional since the event shouldn't repeat
                    events[ev].conditional = "False"

            return events


        @staticmethod
        def _checkEvent(ev, curr_time):
            """
            Singular filter function for checkEvents

            RETURNS: True if passes filter, False if not
            """
            # check if this event even has trigger points
            if ev.start_date is None and ev.conditional is None:
                return False

            # check aff
            if not ev.checkAffection(mas_curr_affection):
                return False

            # check dates, if needed
            if ev.start_date is not None and ev.start_date > curr_time:
                return False

            if ev.end_date is not None and ev.end_date <= curr_time:
                return False

            # now check conditional, if needed
            if not ev.checkConditional():
                return False

            # check if valid action
            if ev.action not in Event.ACTION_MAP:
                return False

            # success
            return True


        @staticmethod
        def checkEvents(ev_dict, rebuild_ev=True):
            """
            This acts as a combination of both checkConditoinal and
            checkCalendar

            does NOT return dict
            """
            if not ev_dict or len(ev_dict) == 0:
                return

            _now = datetime.datetime.now()

            for ev_label,ev in ev_dict.iteritems():
                # TODO: same TODO as in checkConditionals.
                #   indexing would be smarter.

                if Event._checkEvent(ev, _now):
                    # perform action
                    Event._performAction(
                        ev,
                        unlock_time=_now,
                        rebuild_ev=rebuild_ev
                    )

                    # check if we should repeat
                    if not ev.prepareRepeat(True):
                        # no repeats
                        ev.conditional = None
                        ev.action = None

            return


        @staticmethod
        def _checkRepeatRule(ev, check_time, defval=True):
            """DEPRECATED

            (remove when farewells is updated)

            Checks a single event against its repeat rules, which are evaled
            to a time.
            NOTE: no sanity checks

            IN:
                ev - single event to check
                check_time - datetime used to check time rules
                defval - defval to pass into the rules
                    (Default: True)

            RETURNS:
                True if this event passes its repeat rule, False otherwise
            """
            # check if the event contains a MASSelectiveRepeatRule and
            # evaluate it
            if MASSelectiveRepeatRule.evaluate_rule(
                    check_time, ev, defval=defval
                ):
                return True

            # check if the event contains a MASNumericalRepeatRule and
            # evaluate it
            if MASNumericalRepeatRule.evaluate_rule(
                    check_time, ev, defval=defval
                ):
                return True

            return False


        @staticmethod
        def checkRepeatRules(events, check_time=None):
            """DEPRECATED

            (remove when farewells is updated)

            checks the event dict against repeat rules, which are evaluated
            to a time.

            IN:
                events - dict of events of the following format:
                    eventlabel: event object
                check_time - the datetime object that will be used to check the
                    timed rules, if none is passed we check against the current time

            RETURNS:
                A filtered dict containing the events that passed their own rules
                for the given check_time
            """
            # sanity check
            if not events or len(events) == 0:
                return None

            # if check_time is none we check against current time
            if check_time is None:
                check_time = datetime.datetime.now()

            # prepare empty dict to store events that pass their own rules
            available_events = dict()

            # iterate over each event in the given events dict
            for label, event in events.iteritems():
                if Event._checkRepeatRule(event, check_time, defval=False):

                    if event.monikaWantsThisFirst():
                        return {event.eventlabel: event}

                    available_events[event.eventlabel] = event

            # return the available events dict
            return available_events


        @staticmethod
        def _checkFarewellRule(ev):
            """
            Checks the given event against its own farewell specific rule.

            IN:
                ev - event to check

            RETURNS:
                True if this event passes its repeat rule, False otherwise
            """
            return MASFarewellRule.evaluate_rule(ev)


        @staticmethod
        def checkFarewellRules(events):
            """
            Checks the event dict (farewells) against their own farewell specific
            rules, filters out those Events whose rule check return true. As for
            now the only rule specific is their specific special random chance

            IN:
                events - dict of events of the following format:
                    eventlabel: event object

            RETURNS:
                A filtered dict containing the events that passed their own rules

            """
            # sanity check
            if not events or len(events) == 0:
                return None

            # prepare empty dict to store events that pass their own rules
            available_events = dict()

            # iterate over each event in the given events dict
            for label, event in events.iteritems():

                # check if the event contains a MASFarewellRule and evaluate it
                if Event._checkFarewellRule(event):

                    if event.monikaWantsThisFirst():
                        return {event.eventlabel: event}

                    # add the event to our available events dict
                    available_events[label] = event

            # return the available events dict
            return available_events

        @staticmethod
        def _checkAffectionRule(ev,keepNoRule=False):
            """
            Checks the given event against its own affection specific rule.

            IN:
                ev - event to check

            RETURNS:
                True if this event passes its repeat rule, False otherwise
            """
            return MASAffectionRule.evaluate_rule(ev,noRuleReturn=keepNoRule)


        @staticmethod
        def checkAffectionRules(events,keepNoRule=False):
            """
            Checks the event dict against their own affection specific rules,
            filters out those Events whose rule check return true. This rule
            checks if current affection is inside the specified range contained
            on the rule

            IN:
                events - dict of events of the following format:
                    eventlabel: event object
                keepNoRule - Boolean indicating wheter if it should keep
                    events that don't have an affection rule defined

            RETURNS:
                A filtered dict containing the events that passed their own rules

            """
            # sanity check
            if not events or len(events) == 0:
                return None

            # prepare empty dict to store events that pass their own rules
            available_events = dict()

            # iterate over each event in the given events dict
            for label, event in events.iteritems():

                # check if the event contains a MASAffectionRule and evaluate it
                if Event._checkAffectionRule(event,keepNoRule=keepNoRule):

                    if event.monikaWantsThisFirst():
                        return {event.eventlabel: event}

                    # add the event to our available events dict
                    available_events[label] = event

            # return the available events dict
            return available_events


        @staticmethod
        def _performAction(ev, **kwargs):
            """
            Efficient / no checking action performing

            NOTE: does NOT check ev.action for nonNone

            IN:
                ev - event we are performing action on
                **kwargs - keyword args to pass to action
            """
            Event.ACTION_MAP[ev.action](ev, **kwargs)


        @staticmethod
        def performAction(ev, **kwargs):
            """
            Performs the action of the given event

            IN:
                ev - event we are perfrming action on
            """
            if ev.action in Event.ACTION_MAP:
                Event._performAction(ev, **kwargs)

        @staticmethod
        def _undoEVAction(ev):
            """
            Undoes the ev_action

            IN:
                ev - event to undo ev action for
            """
            if ev.action == EV_ACT_UNLOCK:
                ev.unlocked = False

            elif ev.action == EV_ACT_RANDOM:
                ev.random = False
                #And just pull this out of the event list if it's in there at all (provided we haven't bypassed it)
                if "no rmallEVL" not in ev.rules:
                    mas_rmallEVL(ev.eventlabel)

            #NOTE: we don't add the rest since there's no reason to undo those.

# init -1 python:
    # this should be in the EARLY block
    class MASButtonDisplayable(renpy.Displayable):
        """
        Special button type that represents a usable button for custom
        displayables.

        PROPERTIES:
            xpos - x position of this button (relative to container)
            ypos - y position of this button (relative to container)
            width - width of this button
            height - height of this button
            hover_sound - sound played when being hovered (this is played only
                once per hover. IF None, no sound is played)
            activate_sound - sound played when activated (this is played only
                once per activation. If None, no sound is played)
            enable_when_disabled - True means that the button is active even
                if shown disabled. False if otherwise
            sound_when_disabled - True means that sound is active even when the
                button is shown disabled, False if not.
                NOTE: only works if enable_when_disabled is True
            return_value - Value returned when button is activated
            disabled - True means to disable this button, False not
            hovered - True if we are being hovered, False if not
            _button_click - integer value to match a mouse click:
                1 - left (Default)
                2 - middle
                3 - right
                4 - scroll up
                5 - scroll down
            _button_down - pygame mouse button event type to activate button
                MOUSEBUTTONUP (Default)
                MOUSEBUTTONDOWN
        """
        import pygame

        # states of the button
        _STATE_IDLE = 0
        _STATE_HOVER = 1
        _STATE_DISABLED = 2

        # indexes for button parts
        _INDEX_TEXT = 0
        _INDEX_BUTTON = 1

        def __init__(self,
                idle_text,
                hover_text,
                disable_text,
                idle_back,
                hover_back,
                disable_back,
                xpos,
                ypos,
                width,
                height,
                hover_sound=None,
                activate_sound=None,
                enable_when_disabled=False,
                sound_when_disabled=False,
                return_value=True
            ):
            """
            Constructor for the custom displayable

            IN:
                idle_text - Text object to show when button is idle
                hover_text - Text object to show when button is being hovered
                disable_text - Text object to show when button is disabled
                idle_back - Image object for background when button is idle
                hover_back - Image object for background when button is being
                    hovered
                disable_back - Image object for background when button is
                    disabled
                xpos - x position of this button (relative to container)
                ypos - y position of this button (relative to container)
                with - with of this button
                height - height of this button
                hover_sound - sound to play when hovering. If None, no sound
                    is played
                    (Default: None)
                activate_sound - sound to play when activated. If None, no
                    sound is played
                    (Default: None)
                enable_when_disabled - True will enable the button even if
                    it is visibly disabled. FAlse will not
                    (Default: False)
                sound_when_disabled - True will enable sound even if the
                    button is visibly disabled. False will not. Only works if
                    enable_when_disabled is True.
                    (Default: False)
                return_value - Value to return when the button is activated
                    (Default: True)
            """

            # setup
#            self.idle_text = idle_text
#            self.hover_text = hover_text
#            self.disable_text = disable_text
#            self.idle_back = idle_back
#            self.hover_back = hover_back
#            self.disable_back = disable_back
            self.xpos = xpos
            self.ypos = ypos
            self.width = width
            self.height = height
            self.hover_sound = hover_sound
            self.activate_sound = activate_sound
            self.enable_when_disabled = enable_when_disabled
            self.sound_when_disabled = sound_when_disabled
            self.return_value = return_value
            self.disabled = False
            self.hovered = False
            self._button_click = 1
            self._button_down = pygame.MOUSEBUTTONUP

            # the states of a button
            self._button_states = {
                self._STATE_IDLE: (idle_text, idle_back),
                self._STATE_HOVER: (hover_text, hover_back),
                self._STATE_DISABLED: (disable_text, disable_back)
            }

            # current state
            self._state = self._STATE_IDLE

        def _isOverMe(self, x, y):
            """
            Checks if the given x and y coodrinates are over this button.

            RETURNS: True if the given x, y is over this button, False if not
            """
            return (
                0 <= (x - self.xpos) <= self.width
                and 0 <= (y - self.ypos) <= self.height
            )

        def _playActivateSound(self):
            """
            Plays the activate sound if we are allowed to.
            """
            if not self.disabled or self.sound_when_disabled:
                renpy.play(self.activate_sound, channel="sound")

        def _playHoverSound(self):
            """
            Plays the hover soudn if we are allowed to.
            """
            if not self.disabled or self.sound_when_disabled:
                renpy.play(self.hover_sound, channel="sound")

        @staticmethod
        def create_st(
                text_str,
                incl_disb_text,
                *args,
                **kwargs
        ):
            """
            Creates a MASButtonDisplyable using a single text string.

            Default font/textsize/colors/outlines are used here.

            IN:
                text_str - the text to use for the button
                incl_disb_text - True if we may have a disabled state for
                    this button, False if not
                *args - positional args to pass into constructor.
                    do NOT include:
                        - idle_text
                        - hover_text
                        - disable_text
                **kwargs - keyword args to pass into constructor

            RETURNS: created MASButtondisplayable
            """
            if incl_disb_text:
                disb_button = Text(
                    text_str,
                    font=gui.default_font,
                    size=gui.text_size,
                    color=mas_globals.button_text_insensitive_color,
                    outlines=[]
                )
            else:
                disb_button = Null()

            return MASButtonDisplayable(
                Text(
                    text_str,
                    font=gui.default_font,
                    size=gui.text_size,
                    color=mas_globals.button_text_idle_color,
                    outlines=[]
                ),
                Text(
                    text_str,
                    font=gui.default_font,
                    size=gui.text_size,
                    color=mas_globals.button_text_hover_color,
                    outlines=[],
                ),
                disb_button,
                *args,
                **kwargs
            )

        @staticmethod
        def create_stb(
                text_str,
                incl_disb_text,
                *args,
                **kwargs
        ):
            """
            Creates a MASButtonDisplayable using a snigle text string and
            standard button images.

            IN:
                text_str - the text to use for the button
                incl_disb_text - True if we may have a disabled state for this
                    button, False if not
                *args - positional args to pass into constructor.
                    do NOT include:
                        - idle_text
                        - hover_text
                        - disable_text
                        - idle_back
                        - hover_back
                        - disable_back
                **kwargs - keyword args to pass into constructor
            """
            # determine disabled stuff
            if incl_disb_text:
                disb_button = Text(
                    text_str,
                    font=gui.default_font,
                    size=gui.text_size,
                    color=mas_globals.button_text_insensitive_color,
                    outlines=[]
                )
                disb_back = MASButtonDisplayable._gen_bg("insensitive")
            else:
                disb_button = Null()
                disb_back = Null()

            return MASButtonDisplayable(
                Text(
                    text_str,
                    font=gui.default_font,
                    size=gui.text_size,
                    color=mas_globals.button_text_idle_color,
                    outlines=[]
                ),
                Text(
                    text_str,
                    font=gui.default_font,
                    size=gui.text_size,
                    color=mas_globals.button_text_hover_color,
                    outlines=[],
                ),
                disb_button,
                MASButtonDisplayable._gen_bg("idle"),
                MASButtonDisplayable._gen_bg("hover"),
                disb_back,
                *args,
                **kwargs
            )

        @staticmethod
        def _gen_bg(prefix):
            """
            Attempts to pull choice button's Frame and build an appropraite
                image with it using the given prefix.
                This is specifically for MASButtonDisplayables.

            IN:
                prefix - prefix to use in the frame
                    do NOT append "_"

            RETURNS: Frame object to use
            """
            gen_frame = mas_prefixFrame(
                mas_getPropFromStyle("choice_button", "background"),
                prefix
            )

            if gen_frame is None:
                # backup frame in case cannot find choice
                return Frame(
                    mas_getTimeFile(
                        "mod_assets/buttons/generic/{0}_bg.png".format(prefix)
                    ),
                    Borders(5, 5, 5, 5)
                )

            return gen_frame

        def disable(self):
            """
            Disables this button. This changes the internal state, so its
            preferable to use this over setting the disabled property
            directly
            """
            self.disabled = True
            self._state = self._STATE_DISABLED

        def enable(self):
            """
            Enables this button. This changes the internal state, so its
            preferable to use this over setting the disabled property
            directly
            """
            self.disabled = False
            self._state = self._STATE_IDLE

        def getSize(self):
            """
            Returns the size of this button

            RETURNS:
                tuple of the following format:
                    [0]: width
                    [1]: height
            """
            return (self.width, self.height)

        def ground(self):
            """
            Grounds (unhovers) this button. This changes the internal state,
            so its preferable to use this over setting the hovered property
            directly

            NOTE: If this button is disabled (and not enable_when_disabled),
            this will do NOTHING
            """
            if not self.disabled or self.enable_when_disabled:
                self.hovered = False

                if self.disabled:
                    self._state = self._STATE_DISABLED
                else:
                    self._state = self._STATE_IDLE

        def hover(self):
            """
            Hovers this button. This changes the internal state, so its
            preferable to use this over setting the hovered property directly

            NOTE: IF this button is disabled (and not enable_when_disabled),
            this will do NOTHING
            """
            if not self.disabled or self.enable_when_disabled:
                self.hovered = True
                self._state = self._STATE_HOVER

        def render(self, width, height, st, at):

            # pull out the current button back and text and render them
            render_text, render_back = self._button_states[self._state]
            render_text = renpy.render(render_text, width, height, st, at)
            render_back = renpy.render(render_back, self.width, self.height, st, at)

            # what is the text's with and height
            rt_w, rt_h = render_text.get_size()

            # build our renderer
            r = renpy.Render(self.width, self.height)

            # blit our textures
            r.blit(render_back, (0, 0))
            r.blit(
                render_text,
                (int((self.width - rt_w) / 2), int((self.height - rt_h) / 2))
            )

            # return rendere
            return r

        def event(self, ev, x, y, st):

            # only check if we arent disabled (or are allowed to work while
            #   disabled)
            if self._state != self._STATE_DISABLED or self.enable_when_disabled:

                # we onyl care about mouse events here
                if ev.type == pygame.MOUSEMOTION:
                    is_over_me = self._isOverMe(x, y)
                    if self.hovered:
                        if not is_over_me:
                            self.hovered = False
                            self._state = self._STATE_IDLE

                        # else remain in hover mode

                    elif is_over_me:
                        self.hovered = True
                        self._state = self._STATE_HOVER

                        if self.hover_sound:
                            self._playHoverSound()

                elif (
                        ev.type == self._button_down
                        and ev.button == self._button_click
                    ):
                    if self.hovered:
                        if self.activate_sound:
                            self._playActivateSound()
                        return self.return_value

            # otherwise continue on
            return None


# init -1 python:

    class MASLinearForm(object):
        """
        Representation of a linear functions
        """
        THRESH = 0.001

        def __init__(self, xdiff, ydiff, yint):
            """
            Constructor for a Linear Formula.

            IN:
                xdiff - difference in x coords (used in M)
                ydiff - difference in y coords (used in M)
                yint - y intercept
            """
            self.xdiff = xdiff
            self.ydiff = ydiff

            # NOTE: this xdiff is actullay used in calculations
            self._fxdiff = float(xdiff)

            # double check yintercept calcuations
            if xdiff == 0:
                self.yint = None
            elif ydiff == 0:
                self.yint = 0
            else:
                self.yint = yint

        def getx(self, y):
            """
            Calculates the X value given a y

            IN:
                y - y value to input

            RETURNS: x value, or None if not possible
            """
            if self.yint is None:
                return x
            if self.ydiff == 0:
                return None

            return self._getx(y)

        def gety(self, x):
            """
            Calculates the Y value given an x

            IN:
                x - x value to input

            RETURNS: y value, or None if not possible
            """
            if self.yint is None:
                return None

            return self._gety(x)

        @staticmethod
        def diffPoints(p1, p2):
            """
            Generats x/y diffs for 2 points

            IN:
                p1 - (x, y) point
                p2 - (x, y) point

            RETURNS: tuple of the following format:
                [0] - xdiff
                [1] - ydiff
            """
            lp, rp = MASLinearForm.sortPoints(p1, p2)
            return rp[0] - lp[0], rp[1] - lp[1]

        @staticmethod
        def fromPoints(p1, p2):
            """
            Generates a MASLinearform object using points

            IN:
                p1 - (x, y) point
                p2 - (x, y) point

            RETURNS: MASLinearForm object
            """
            xdiff, ydiff = MASLinearForm.diffPoints(p1, p2)
            yint = MASLinearForm.yintPoints(p1, p2)
            return MASLinearForm(xdiff, ydiff, yint)

        @staticmethod
        def fromSlope(slope, yint):
            """
            Generates a MASLinearForm object using slope

            IN:
                slope - the slope of the line
                yint - the yintercept of the line

            RETURNS: MASLinearForm object
            """
            return MASLinearForm(1, m, yint)

        @staticmethod
        def sortPoints(p1, p2):
            """
            Returns the two points as an ordered tuple

            IN:
                p1 - (x, y) point
                p2 - (x, y) point

            RETURNS: tuple of the following format:
                [0] - left most point
                [1] - right most point
            """
            if p1[0] < p2[0]:
                return p1, p2

            return p2, p1

        @staticmethod
        def yintPoints(p1, p2):
            """
            Returns yintercept from 2 points

            IN:
                p1 - (x, y) point
                p2 - (x, y) point

            RETURNS: yintercept, or None if no yintercept
            """
            # initial diff checks
            xdiff, ydiff = MASLinearForm.diffPoints(p1, p2)
            if xdiff == 0:
                return None
            elif ydiff == 0:
                return 0

            # otherwise, we need to check the points
            lp, rp = MASLinearForm.sortPoints(p1, p2)
            lx, ly = lp

            # if the left point is already on y axis, this is easy
            if lx == 0:
                return lp[1]

            # otherwise, we need to do math
            pot_yint = ly - ( (ydiff * lx) / float(xdiff) )

            # threshold check is so we dont have too many floats in simple
            # cases
            # NOTE: so here we are checking that the difference bewteen the
            #   float value and its integercomponent is less than the
            #   threshold (a small value), then we assume it is int instead
            #   float.
            if abs(int(pot_yint) - pot_yint) < MASLinearForm.THRESH:
                pot_yint = int(pot_yint)

            return pot_yint

        def _getx(self, y):
            """
            Gets x without any checks (this can crash)
            """
            return (y - self.yint) / self._slope()

        def _gety(self, x):
            """
            Gets y with out any checks (this can crash)
            """
            return self._slope(x) + self.yint

        def _slope(self, x=1):
            """
            Returns the slope of this line
            Pass in X to calculate mx instead of just m
            """
            return  (self.ydiff * x) / self._fxdiff


    class MASEdge(object):
        """
        Representation of an edge (line with 2 points)
        Has functions related to determining if a point will intersect with
        this edge (aka for point in polygon calculations)
        """

        def __init__(self, p1, p2):
            """
            Constructor for an edge
            NOTE: the edges do NOT have to be the correct order. This is
                determined internally.

            IN:
                p1 - start point of edge (x, y)
                p2 - end point of edge (x, y)
            """
            self._horizontal = False
            self._vertical = False
            self._left_point = None
            self._right_point = None
            self.__bb_x_min = None
            self.__bb_x_max = None
            self.__bb_y_min = None
            self.__bb_y_max = None
            self.__norm_lp = (0, 0)
            self.__norm_rp = None
            self.__line = None

            self.__setup(p1, p2)

        def inBoundingBox(self, x, y):
            """
            Checks if the given x,y is in teh bounding box

            IN:
                x - x coordinate to check
                y - y coordinate to check

            RETURNS: True if in bounding box, False if not
            """
            return self._inBoundingBoxX(x) and self._inBoundingBoxY(y)

        def horizontalIntersect(self, x, y):
            """
            Checks if a horizontal ray going right with the given point as
            the origin of the ray will intersect this Edge

            IN:
                x - x coordinate to check
                y - y coodinate to check

            RETURNS: True if it intersects, False if not
            """
            # horizontal lines will always be considered not hitting
            if self._horizontal:
                return False

            # then check if within the horizontal range of the edge
            if not self._inBoundingBoxY(y):
                return False

            # right of the bounding box is for sure a miss
            if self.__bb_x_max < x:
                return False

            # left of the bounding box is for sure a hit
            # NOTE: this also handles vertical lines
            if x < self.__bb_x_min:
                return True

            # otherwise, we are for sure within the bounding box.

            # vertical lines means we only have to check x
            if self._vertical:
                # in this case, we treat on the line as passing
                return x <= self.__bb_x_min

            # now just run the inverse of the linear formula, and if
            # our x is less than that, then the point is for sure before the
            # edge
            x, y = self._normalize((x, y))
            return x <= self.__line._getx(y)

        def _inBoundingBoxX(self, x):
            """
            Checks if the given point is within the vertical parts of the
            bounding box (within x range)

            IN:
                x - x coordinate to check

            RETURNS: True if the given x is within bounding box range, False
                if not
            """
            return self.__bb_x_min <= x <= self.__bb_x_max

        def _inBoundingBoxY(self, y):
            """
            Checks if the given y coord is within the horizontal parts of the
            bounding box (within y range)

            IN:
                y - y coordinate to check

            RETURNS: True if the given y is within bounding box range, False if
                not
            """
            return self.__bb_y_min <= y <= self.__bb_y_max

        def __setup(self, p1, p2):
            """
            Sets up this MASEdge using given points
            """
            self.__setupPoints(p1, p2)
            self.__setupBoundingBox()
            self.__setupNormalizedPoints()
            self.__setupLinearFunction()

        def __setupBoundingBox(self):
            """
            Sets up bounding box
            """
            self.__bb_x_min = self._left_point[0]
            self.__bb_x_max = self._right_point[0]
            self.__bb_y_min = min(self._left_point[1], self._right_point[1])
            self.__bb_y_max = max(self._left_point[1], self._right_point[1])

        def __setupLinearFunction(self):
            """
            Sets up the MASLinearForm functions for this Edge
            """
            self.__line = MASLinearForm.fromPoints(
                self.__norm_lp,
                self.__norm_rp
            )

        def __setupNormalizedPoints(self):
            """
            Sets up the appropraite normlization points
            """
            self.__norm_rp = MASLinearForm.diffPoints(
                self._left_point,
                self._right_point
            )

        def __setupPoints(self, p1, p2):
            """
            Sets up the appropriate vars for point handling
            """
            # split points
            p1x, p1y = p1
            p2x, p2y = p2

            # determine of vertical line
            if p1x == p2x:
                self._vertical = True

            # determine if horizontal line
            elif p1y == p2y:
                self._horizontal = True

            # determine left and righ tpoint
            self._left_point, self._right_point = MASLinearForm.sortPoints(
                p1,
                p2
            )

        def _normalize(self, point):
            """
            Normalizes a point so its normalized to this edge

            IN:
                point - (x, y) point to normalize

            RETURNS: normalized point (x, y)
            """
            return (
                point[0] - self._left_point[0],
                point[1] - self._left_point[1]
            )


    class MASClickZone(renpy.Displayable):
        """
        Special mousezone that can react depending if being clicked
        with mouse. Meant for custom displayable use.

        PROPERTIES:
            corners - list of verticies. each element should be a tuple like
                (x, y)
            disabled - True means to disable this mouse zone, False not
        """
        LEFT_CLICK = 1
        MIDDLE_CLICK = 2
        RIGHT_CLICK = 3

        def __init__(self, corners):
            """
            Constructor for the Clickzone displayable

            IN:
                corners - list of verticies (x, y)
                    ASSUMES THAT THIS IS SORTED IN ORDER
            """
            if len(corners) <= 0:
                raise Exception("Clickzone cannot be built with empty corners")

            super(renpy.Displayable, self).__init__()

            self.corners = corners
            self.disabled = False
            self._debug_back = False
            self.__edges = []
            self._button_down = pygame.MOUSEBUTTONUP

            self.__setup()

        @staticmethod
        def copyfrom(other, new_vx):
            """
            Copies a MASClickZone state, but applies a new_vx to it.

            RETURNS: new MASClickZone to use
            """
            new_cz = MASClickZone(new_vx)
            new_cz.disabled = other.disabled
            new_cz._debug_back = other._debug_back
            new_cz._button_down = other._button_down

            return new_cz

        def render(self, width, height, st, at):
            """
            Render functions
            """
            # NOTE: we are using the given width and height because of teh
            #   debug canvas mode
            r = renpy.Render(width, height)

            # only show a box if debug mode is on
            if self._debug_back:
                canvas = r.canvas()
                canvas.polygon("#FFE6F4", self.corners, width=0)

            return r

        def event(self, ev, x, y, st):
            """
            Event function
            """
            if ev.type == self._button_down and not self.disabled:
                # determine if this event happend here
                if self._isOverMe(x, y):
                    return ev.button

            # othewise, nothing happened
            return None

        def _inBoundingBox(self, x, y):
            """
            Checks if the given coordinates are within the bounding box

            IN:
                x - x coordinate to check
                y - y coordinat eto check

            RETURNS: True if these coords are within the bounding box, False
                if not
            """
            return (
                self.__bb_x_min <= x <= self.__bb_x_max
                and self.__bb_y_min <= y <= self.__bb_y_max
            )

        def _isOverMe(self, x, y):
            """
            Determines if the given coordinates are inside this click zone

            IN:
                x - x coordinage to check
                y - y coordinate to check

            RETURNS: True if these coordinates are in this clickzone, False
                if not
            """
            # bounding box covers most cases
            if not self._inBoundingBox(x, y):
                return False

            # otherwise, determine if in polygon
            intersections = 0
            for edge in self.__edges:
                intersections += int(edge.horizontalIntersect(x, y))

            # odd number of intersctions mean inside
            return (intersections % 2) == 1

        def _start_click(self, button):
            """
            Marks the appropraite spot where a click should occur
            ASSUMES MOUSEBUTTONDOWN was found, and we are just determining
            the click.
            """
            self.__click_start[button - 1] = True

        def _was_clicked(self, button):
            """
            Checks if this button spot was clicked
            """
            return self.__click_start[button - 1]

        def _reset_click(self, button):
            """
            Resets click status for a button
            """
            self.__click_start[button - 1] = False

        def __setup(self):
            """
            setup functions
            """
            self.__setupBoundingBox()
            self.__setupEdges()

        def __setupBoundingBox(self):
            """
            Generates the bounding box for this click zone
            """
            # set intiial vlaues
            self.__bb_x_min = self.corners[0][0]
            self.__bb_x_max = self.corners[0][0]
            self.__bb_y_min = self.corners[0][1]
            self.__bb_y_max = self.corners[0][1]

            # create box
            for index in range(1, len(self.corners)):
                x, y = self.corners[index]
                self.__bb_x_min = min(self.__bb_x_min, x)
                self.__bb_x_max = max(self.__bb_x_max, x)
                self.__bb_y_min = min(self.__bb_y_min, y)
                self.__bb_y_max = max(self.__bb_y_max, y)

            # finally, set the internal width and height for rendering
            self.__width = self.__bb_x_max - self.__bb_x_min
            self.__height = self.__bb_y_max - self.__bb_y_min

        def __setupEdges(self):
            """
            Sets up the edges for this click zone
            """
            # only generate the edges up to the final edge
            for index in range(len(self.corners)-1):
                self.__edges.append(
                    MASEdge(self.corners[index], self.corners[index+1])
                )

            # and the final edge
            self.__edges.append(MASEdge(
                self.corners[0],
                self.corners[-1]
            ))

# init -1 python:

    class MASInteractable(renpy.Displayable):
        """DEPRECATED

        Do not use this.
        """

        def __init__(self, *args, **kwargs):
            pass


# init -1 python:
    # new class to manage a list of quips
    class MASQuipList(object):
        import random
        """
        Class that manages a list of quips. Quips have types which helps us
        when deciding how to execute quips. Also we have some properties that
        make it easy to customize a quiplist.

        I suggest that you only use this if you need to have multipe types
        of quips in a list. If you're only doing one-liners, a regular list
        will suffice.

        Currently 3 types of quips:
            glitchtext - special type for a glitchtext generated quip.
            label - this quip is actually the label for the actual quip
                (assumed the label has a return and is designed to be called)
            line - this quip is the actual line we want to display.
            other - other types of quips

        CONSTANTS:
            TYPE_GLITCH - glitch text type quip
            TYPE_LABEL - label type quip
            TYPE_LINE - line type quip
            TYPE_OTHER - other, custom types of quips

        PROPERTIES:
            allow_glitch - True means glitch quips can be added to this list
            allow_label - True means label quips can be added to this list
            allow_line - True means line quips can be added to this list
            raise_issues - True will raise exceptions if bad things occur:
                - if a quip that was not allowed was added
                - if a label that does not exist was added
                - etc...
        """

        TYPE_GLITCH = 0
        TYPE_LABEL = 1
        TYPE_LINE = 2
        TYPE_OTHER = 50

        TYPES = (
            TYPE_GLITCH,
            TYPE_LABEL,
            TYPE_LINE,
            TYPE_OTHER
        )

        def __init__(self,
                allow_glitch=True,
                allow_label=True,
                allow_line=True,
                raise_issues=True
            ):
            """
            Constructor for MASQuipList

            IN:
                allow_glitch - True means glitch quips can be added to this
                    list, False means no
                    (Default: True)
                allow_label - True means label quips can be added to this list,
                    False means no
                    (Default: True)
                allow_line - True means line quips can be added to ths list,
                    False means no
                    (Default: True)
                raise_issues - True means we will raise exceptions if bad
                    things occour. False means we stay quiet
                    (Default: True)
            """

            # set properties
            self.allow_glitch = allow_glitch
            self.allow_label = allow_label
            self.allow_line = allow_line
            self.raise_issues = raise_issues

            # this is the actual internal ist
            self.__quiplist = list()


        def addGlitchQuip(self,
                length,
                cps_speed=0,
                wait_time=None,
                no_wait=False
            ):
            """
            Adds a glitch quip based upon the given params.

            IN:
                length - length of the glitch text
                cps_speed - integer value to use as glitchtext speed multiplier
                    If 0 or 1, no cps speed change is done.
                    (Default: 0)
                wait_time - integer value to use as wait time. If None, no
                    wait tag is used
                    (Default: None)
                no_wait - If True, a no wait tag is added to the glitchtext.
                    otherwise, no no-wait tag is added.
                    (Default: False)

            RETURNS:
                index location of the added quip, or -1 if we werent allowed to
            """
            if self.allow_glitch:

                # create the glitchtext quip
                quip = glitchtext(length)

                # check for cps speed adding
                if cps_speed > 0 and cps_speed != 1:
                    cps_speedtxt = "cps=*{0}".format(cps_speed)
                    quip = "{" + cps_speedtxt + "}" + quip + "{/cps}"

                # check for wait adding
                if wait_time is not None:
                    wait_text = "w={0}".format(wait_time)
                    quip += "{" + wait_text + "}"

                # check no wait
                if no_wait:
                    quip += "{nw}"

                # now add the quip to the internal ist
                self.__quiplist.append((self.TYPE_GLITCH, quip))

                return len(self.__quiplist) - 1

            else:
                self.__throwError(
                    "Glitchtext cannot be added to this MASQuipList"
                )
                return -1


        def addLabelQuip(self, label_name):
            """
            Adds a label quip.

            IN:
                label_name - label name of this quip

            RETURNS:
                index location of the added quip, or -1 if we werent allowed to
                or the label didnt exist
            """
            if self.allow_label:

                # check for label existence first
                if not renpy.has_label(label_name):
                    # okay throw an error and reutrn -1
                    self.__throwError(
                        "Label '{0}' does not exist".format(label_name)
                    )
                    return -1

                # otherwise, we are good to add this thing
                self.__quiplist.append((self.TYPE_LABEL, label_name))

                return len(self.__quiplist) - 1

            else:
                self.__throwError(
                    "Labels cannot be added to this MASQuipList"
                )
                return -1


        def addLabelQuips(self, label_list):
            """
            Adds multiple label quips.

            IN:
                label_list - list of label names to add
            """
            for _label in label_list:
                self.addLabelQuip(_label)


        def addLineQuip(self, line, custom_type=None):
            """
            Adds a line quip. A custom type can be given if the caller wants
            this line quip to be differentable from other line quips.

            IN:
                line - line quip
                custom_type - the type to use for this line quip instead of
                    TYPE_LINE. If None, TYPE_LINE is used.
                    (Default: None)

            RETURNS:
                index location of the added quip, or -1 if we werent allowed to
                or the given custom_type is conflicting exisiting types.
            """
            if self.allow_line:

                # check given type
                if custom_type is None:
                    custom_type = self.TYPE_LINE

                elif custom_type in self.TYPES:
                    # cant have conflicing types
                    self.__throwError(
                        (
                            "Custom type for '{0}' conflicts with default " +
                            "types."
                        ).format(line)
                    )
                    return -1

                # otherwise, we are good for adding this line
                self.__quiplist.append((custom_type, line))

                return len(self.__quiplist) -1

            else:
                self.__throwError(
                    "Lines cannot be added to this MASQuipList"
                )
                return -1


        def quip(self, remove=False):
            """
            Randomly picks a quip and returns the result.

            Line quips are automatically cleaned and prepared ([player],
            gender pronouns are all replaced appropraitely). If the caller
            wants additional variable replacements, they must do that
            themselves.

            IN:
                remove - True means we remove the quip we select. False means
                    keep it in the internal list.

            RETURNS:
                tuple of the following format:
                    [0]: type of this quip
                    [1]: value of this quip
            """
            if remove:
                # if we need to remove, we should use randint instead
                sel_index = random.randint(0, len(self.__quiplist) - 1)
                quip_type, quip_value = self.__quiplist.pop(sel_index)

            else:
                # if we dont need to remove, we can just use renpy random
                # choice
                quip_type, quip_value = random.choice(self.__quiplist)

            # now do preocessing then send
            if quip_type == self.TYPE_GLITCH:
                quip_value = self._quipGlitch(quip_value)

            elif quip_type == self.TYPE_LABEL:
                quip_value = self._quipLabel(quip_value)

            elif quip_type == self.TYPE_LINE:
                quip_value = self._quipLine(quip_value)

            return (quip_type, quip_value)


        def _getQuip(self, index):
            """
            Retrieves the quip at the given index.

            IN:
                index - the index the wanted quip is at

            RETURNS:
                tuple of the following format:
                    [0]: type of this quip
                    [1]: value of this quip
            """
            return self.__quiplist[index]


        def _getQuipList(self):
            """
            Retrieves the internal quip list. This is a direct reference to
            the internal list, so be careful.

            RETURNS:
                the internal quiplist
            """
            return self.__quiplist


        def _quipGlitch(self, gt_quip):
            """
            Processes the given glitch text quip for usage.

            IN:
                gt_quip - the glitchtext quip (value) to process

            RETURNS:
                glitchtext quip ready for display.
            """
            # NOTE: for now, we dont need to do processing here
            return gt_quip


        def _quipLabel(self, la_quip):
            """
            Processes the given label quip for usage.

            IN:
                la_quip - the label quip (value) to process

            RETURNS:
                label quip ready for call
            """
            # NOTE: for now, we dont need to do processing here
            return la_quip


        def _quipLine(self, li_quip):
            """
            Processes the given line quip for usage.

            IN:
                li_quip - the line quip (value) to process

            RETURNS:
                line quip ready for display
            """
            # lines need processing
            #quip_replacements = self.__generateLineQuipReplacements()

            #for keyword, value in quip_replacements:
            #    li_quip = li_quip.replace(keyword, value)

            # turns out we can do this in one line
            # TODO: test if this actually works, we might need to pass in
            # scope as well
            return renpy.substitute(li_quip)


        def _removeQuip(self, index):
            """
            Removes the quip at the given index. (and returns it back)

            IN:
                index - the index of the quip to remove.

            RETURNS:
                tuple of the following format:
                    [0]: type of the removed quip
                    [1]: value of the removed quip
            """
            quip_tup = self.__quiplist.pop(index)
            return quip_tup


        def __generateLineQuipReplacements(self):
            """
            Generates line quip replacement list for easy string replacement.

            RETURNS: a list for line quip variable replacements

            ASSUMES:
                player
                currentuser
                mcname
                <all gender prounouns>
            """
            return [
                ("[player]", player),
                ("[currentuser]", currentuser),
                ("[mcname]", mcname),
                ("[his]", his),
                ("[he]", he),
                ("[hes]", hes),
                ("[heis]", heis),
                ("[bf]", bf),
                ("[man]", man),
                ("[boy]", boy),
                ("[guy]", guy)
            ]


        def __throwError(self, msg):
            """
            Internal function that throws an error if we are allowed to raise
            issues.

            IN:
                msg - message to display
            """
            if self.raise_issues:
                raise Exception(msg)


# uncomment for syntax highlight on vim
#init -1 python:

    class MASMailbox(object):
        """
        Async communication between different objects.

        NOTE: even though this is usable on its own, its highly recommended
        that you extend this class to encapsulate message constants.

        NOTE: this is NOT like notify, objects can only respond to messages
            when they are active.

        PROPERTIES:
            box - the actual mailbox that contains messages
        """
        RETURN_KEY = "__mas_return"


        def __init__(self):
            """
            Constructor
            """
            self.box = {}


        def get(self, headline):
            """
            Removes a message from the box, and returns it.

            IN:
                headline - identifier for the message

            RETURNS:
                the message data stored, None if no message data or if the
                message was actually None.
            """
            if headline in self.box:
                return self.box.pop(headline)

            return None


        def mas_get_return(self):
            """
            Removes and returns a MAS_RETURN message.

            RETURNS:
                the returned message, or None if no message data or if the
                emssage was wasctually none
            """
            return self.get(self.RETURN_KEY)


        def mas_send_return(self, msg):
            """
            Adds a MAS_RETURN message to the box.

            IN:
                msg - message to return
            """
            self.send(self.RETURN_KEY, msg)


        def read(self, headline):
            """
            Reads a message from the box.

            NOTE: does NOT remove the message.

            IN:
                headline - identifier for the message

            RETURNS:
                the message data stored, None if no message data or if the
                message was actually None
            """
            return self.box.get(headline, None)


        def send(self, headline, msg):
            """
            Adds a message to the box.

            IN:
                headline - identifier for this message.
                msg - message to send
            """
            self.box[headline] = msg

    class MASExtraPropable(object):
        """
        base class that supports ex_prop-based extensions.

        Properties can be accessed by using `ex__` prefix.
        Supports the following:

        ACCESSING props:
            via `<obj>.ex__<name>`
            if no prop is found, None is returned.

        SETTING PROPS:
            via `<obj>.ex__<name> = <value>`

        CHECKING FOR PROP EXISTENCE:
            via `<name>` in <obj>

        ADDING props:
            *same as setting props

        REMOVING PROPS:
            via pop function

        EQUIVALENCE:
            No eq support, but I am open to it. Let me know.

        NOTE: using this means that all of the ex_props you want to use
            _should_ be pythonic in name. Props that are NOT pythonic in name
            are will not be accessible via property.

        PROPERTIES:
            ex_props - direct dictionary of ex_props
        """
        EX_PFX = "ex__"
        _EX_LEN = len(EX_PFX)

        def __init__(self, ex_props=None):
            """
            Constructor.

            IN:
                ex_props - initial dict of ex props to set internal data to
                    pass None to start with an empty dict.
                    (Default: None)
            """
            if ex_props is None:
                ex_props = {}

            self.ex_props = ex_props

        def __contains__(self, item):
            return item in self.ex_props

        def __len__(self):
            return len(self.ex_props)

        def __getattr__(self, key):
            if key.startswith(self.EX_PFX):
                return self.ex_props.get(key[self._EX_LEN:], None)

            return super(MASExtraPropable, self).__getattr__(key)

        def __setattr__(self, key, value):
            if key.startswith(self.EX_PFX):
                # the real property name is without the prefix
                stripped_key = key[self._EX_LEN:]
                if len(stripped_key) > 0:
                    self.ex_props[stripped_key] = value

            super(MASExtraPropable, self).__setattr__(key, value)

        def ex_has(self, key):
            """
            Checks for existence of the given exprop in this object.

            IN:
                key - name of exprop

            RETURNS: True if the key exists as an ex prop, False if not
            """
            return key in self

        def ex_iter(self):
            """
            Generates generator of exprops in this object.

            RETURNS: iter of ex prop names and values
            """
            return (item for item in self.ex_props.iteritems())

        def ex_pop(self, key, default=None):
            """
            Pops and returns an exprop from the internal dict

            IN:
                key - key to pop/get ex_prop
                default - default value to use if no prop found
                    (Default: None)

            RETURNS: value of the popped ex_prop, or the default if not found
            """
            return self.ex_props.pop(key, default)

        @staticmethod
        def repr_out(obj):
            """
            returns a repr string of the ex props in an object.

            IN:
                obj - object to repr ex props for

            RETURNS: repr string of ex_props in object. empty string if
                no ex_props property.
            """
            try:
                ex_props = obj.ex_props
                if ex_props is None:
                    return "<exprops: ()>"

                props = [
                    "{0}: {1}".format(key, value)
                    for key, value in ex_props.iteritems()
                ]
                return "<exprops: ({0})>".format(", ".join(props))

            except:
                return ""

init 25 python:
    class PauseDisplayable(renpy.Displayable):
        """
        Pause until click variant of Pause
        This is because normal pause until click is broken for some reason
        """
        def __init__(self):
            super(renpy.Displayable, self).__init__()

        def render(self, width, height, st, at):
            # dont actually render anything
            return renpy.Render(0, 0)

        def event(self, ev, x, y, st):
            if ev.type == pygame.MOUSEBUTTONDOWN and ev.button not in (4, 5):
                return True

            raise renpy.IgnoreEvent()

    class PauseDisplayableEvent(object):
        """
        Class to represent events for PauseDisplayableWithEvents
        """
        def __init__(self, timedelta, functions, repeatable=False, invoke_in_new_context=False):
            """
            Constructor for events

            IN:
                timedelta - datetime.timedelta after which we'll run the event
                functions - the func or a list of the funcs that get called on the event
                    NOTE: if you need args/kwargs use renpy.partial
                repeatable - whether or not we'll repeat the event
                    (Default: False)
                invoke_in_new_context - whether or not we'll invoke the functions
                    to avoid interaction issues
                    (Default: False)
            """
            self.timedelta = timedelta

            if not isinstance(functions, tuple):
                if isinstance(functions, list):
                    functions = tuple(functions)

                else:
                    functions = (functions,)

            self.functions = functions
            self.repeatable = repeatable
            self.invoke_in_new_context = invoke_in_new_context

            self.end_datetime = None

        def set_end_datetime(self, value):
            """
            Sets end datetime for this event

            IN:
                value - value to set
            """
            self.end_datetime = value

        def __repr__(self):
            """
            Representation of this obj
            """
            return "<PauseDisplayableEvent (timedelta {0}, functions {1})>".format(self.timedelta, self.functions)

        def __call__(self):
            """
            Executes this event
            """
            for func in self.functions:
                if self.invoke_in_new_context:
                    renpy.invoke_in_new_context(func)

                else:
                    func()

    class PauseDisplayableWithEvents(renpy.Displayable):
        """
        Advanced pause displayable that supports hotkeys and can run events during pause
        """
        # The keysims that are allowed during pause
        _RESPECTED_KEYSIMS = {
            "screenshot": renpy.store._screenshot,
            "toggle_fullscreen": renpy.toggle_fullscreen,
            "mas_hide_windows": renpy.store._mas_hide_windows,
            "mas_game_menu": renpy.store._mas_game_menu,
            "change_music": renpy.store._mas_hk_select_music,
            "mute_music": renpy.store._mas_hk_mute_music,
            "dec_musicvol": renpy.store._mas_hk_dec_musicvol,
            "inc_musicvol": renpy.store._mas_hk_inc_musicvol
        }

        # An attempt to fix renpy's memory leak
        CRUTCH_EVENT =  PauseDisplayableEvent(
            datetime.timedelta(minutes=5),
            renpy.restart_interaction,
            repeatable=True
        )

        def __init__(self, events=None, respected_keysims=None):
            """
            Constructor for this displayable

            IN:
                events - a single PauseDisplayableEvent object or a list of PauseDisplayableEvent objects
                    If None, no event will be ran
                    (Default: None)
                respected_keysims - keysims that are respected during this pause, if None we'll use some default ones.
                    If not None, assuming it's a dict with the name of a defined keybinding and its function
                    (Default: None)
            """
            super(renpy.Displayable, self).__init__()

            if events is None:
                events = [PauseDisplayableWithEvents.CRUTCH_EVENT]

            elif isinstance(events, tuple):
                events = list(events)
                events.append(PauseDisplayableWithEvents.CRUTCH_EVENT)

            elif isinstance(events, list):
                events.append(PauseDisplayableWithEvents.CRUTCH_EVENT)

            # Assuming it's a single PauseDisplayableEvent
            else:
                events = [events, PauseDisplayableWithEvents.CRUTCH_EVENT]

            events.sort(key=PauseDisplayableWithEvents.__sort_key_td)

            self.events = events
            self.__events = list(events)
            self.respected_keysims = respected_keysims or PauseDisplayableWithEvents._RESPECTED_KEYSIMS
            self.__abort_events = False
            self.should_enable_afm = None

        def __repr__(self):
            """
            Representation of this obj
            """
            return "<PauseDisplayableWithEvents ({0})>".format(self.events)

        def __set_end_datetimes(self):
            """
            Sets end datetimes for events using current time
            """
            _now = datetime.datetime.now()
            for event in self.events:
                event.set_end_datetime(_now + event.timedelta)

        def __reset_events(self):
            """
            Resets events state
            """
            self.events = self.__events[:]
            for ev in self.events:
                ev.set_end_datetime(None)

        def start(self):
            """
            Starts this displayable
            """
            self.should_enable_afm = store._preferences.afm_enable
            self.__set_end_datetimes()
            ui.implicit_add(self)
            ui.interact()

        def stop(self):
            """
            Stops this disp's interaction, aborts its event
            """
            ui.remove(self)
            self.__abort_events = True
            self.should_enable_afm = None

            if renpy.game.context().interacting:
                renpy.end_interaction(False)

        def reset(self):
            """
            Completely resets this disp's state
            """
            ui.remove(self)
            self.__reset_events()
            self.__abort_events = False
            self.should_enable_afm = None

            if renpy.game.context().interacting:
                renpy.end_interaction(False)

        def __get_events_for_time(self):
            """
            Returns the events that we need to run NOW
            and pops them from the event list

            OUT:
                generator over the events

            ASSUMES:
                the events are sorted
            """
            _now = datetime.datetime.now()

            for event in self.events[:]:
                if _now >= event.end_datetime:
                    self.events.remove(event)
                    yield event

                # no need to keep iter, we can return at this point
                else:
                    return

        def __set_timeout(self):
            """
            Sets a timeout for event generator
            """
            # No need to do anything if we have no pending events
            if not self.events:
                return

            _now = datetime.datetime.now()
            _end_dt = self.events[0].end_datetime

            if _end_dt >= _now:
                timeout = (_end_dt - _now).total_seconds() + 0.1

            else:
                timeout = 0.1

            renpy.timeout(timeout)

        def render(self, width, height, st, at):
            """
            Our render
            """
            # We don't render anything
            return renpy.Render(0, 0)

        def __check_keysims(self, ev):
            """
            Checks if an event matches the respected keysims of this displayable
            If it does, run the appropriate func

            OUT:
                True if we ran a func, False otherwise
            """
            for keysim in self.respected_keysims:
                if renpy.map_event(ev, keysim):
                    self.respected_keysims[keysim]()
                    return True

            return False

        def event(self, ev, x, y, st):
            """
            Handles interactions
            """
            # Should run our time event?
            if ev.type == renpy.display.core.TIMEEVENT:
                for event in self.__get_events_for_time():
                    if not self.__abort_events:
                        event()
                        if event.repeatable:
                            event.set_end_datetime(datetime.datetime.now() + event.timedelta)
                            store.mas_utils.insert_sort(self.events, event, PauseDisplayableWithEvents.__sort_key_dt)

                    # If we aborted, we need to quit asap
                    else:
                        return None

                self.__set_timeout()
                raise renpy.IgnoreEvent()

            # Detected a m1 click? Interrupt pause
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                self.__abort_events = True
                ui.remove(self)
                if self.should_enable_afm:
                    self.should_enable_afm = None
                    store._preferences.afm_enable = True
                return True

            # Other kind of event? Check our keysims
            elif self.__check_keysims(ev):
                raise renpy.IgnoreEvent()

            # Otherwise continue listening
            return None

        def per_interact(self):
            """
            We don't need to do anything here
            """
            return

        @staticmethod
        def __sort_key_td(ev):
            """
            Sort key for sorting by ev's timedelta
            """
            return ev.timedelta

        @staticmethod
        def __sort_key_dt(ev):
            """
            Sort key for sorting by ev's end_datetime
            """
            return ev.end_datetime

# special store that contains powerful (see damaging) functions
init -1 python in _mas_root:
    import store
    import datetime

    # redefine this because I can't get access to global functions, also
    # i dont care to find out how
    nonunicode = (
        "¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿ÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝ" +
        "Þßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿĀāĂăĄąĆćĈĉĊċČčĎďĐđĒēĔĕĖėĘę" +
        "ĚěĜĝĞğĠġĢģĤĥĦħĨĩĪīĬĭĮįİıĲĳĴĵĶķĸĹĺĻļĽľĿŀŁłŃńŅņŇňŉŊŋŌōŎŏŐőŒœŔŕŖ" +
        "ŗŘřŚśŜŝŞşŠšŢţŤťŦŧŨũŪūŬŭŮůŰűŲųŴŵŶŷŸŹźŻżŽž"
    )

    def glitchtext(length):
        import random
        output = ""
        for x in range(length):
            output += random.choice(nonunicode)
        return output

    def mangleFile(filepath, mangle_length=1000):
        """
        Mangles the file at the given filepath. Will create the file if it
        doesnt exists

        IN:
            filepath - path of the file to mangle
            mangle_length - how many characters to use to mangle
                (Default: 1000)
        """
        import struct
        bad_text = glitchtext(mangle_length)
        bad_text = [ord(x) for x in bad_text]
        bad_text = struct.pack("{0}i".format(mangle_length), *bad_text)
        with open(filepath, "wb") as m_file:
            m_file.write(bad_text)


    def resetPlayerData():
        """
        Completely resets player data in persistents.

        NOTE: Not all player-related persistent values may be reset by this
        function. If there are more player-related data in persistent that is
        not reset by this function, PLEASE LET US KNOW

        ASSUMES: a ton of persistent stuff
        """
        import datetime

        # starting with hidden values
        renpy.game.persistent._seen_ever = dict()

        # now general player (stock) stuff
        renpy.game.persistent.playername = ""
        renpy.game.persistent.playthrough = 0
        renpy.game.persistent.yuri_kill = 0
        renpy.game.persistent.clear = [False] * 10
        renpy.game.persistent.special_poems = None
        renpy.game.persistent.clearall = None
        renpy.game.persistent.first_load = None

        # mod related general
        renpy.game.persistent.event_database = dict()
        renpy.game.persistent.farewell_database = dict()
        renpy.game.persistent.closed_self = False
        renpy.game.persistent.seen_monika_in_room = False
        renpy.game.persistent.ever_won = {
            'pong':False,
            'chess':False,
            'hangman':False,
            'piano':False
        }
        renpy.game.persistent.sessions={
            'last_session_end':datetime.datetime.now(),
            'current_session_start':datetime.datetime.now(),
            'total_playtime':datetime.timedelta(seconds=0),
            'total_sessions':0,
            'first_session':datetime.datetime.now()
        }
        renpy.game.persistent._mas_xp_lvl = 0
        renpy.game.persistent.rejected_monika = True
        renpy.game.persistent.current_track = None

        # chess
        renpy.game.persistent._mas_chess_stats = {
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "practice_wins": 0,
            "practice_losses": 0,
            "practice_draws": 0
        }
        renpy.game.persistent._mas_chess_quicksave = ""
        renpy.game.persistent._mas_chess_difficulty = (0, 1)
        renpy.game.persistent._mas_chess_dlg_actions = dict()
        renpy.game.persistent._mas_chess_timed_disable = None
        renpy.game.persistent._mas_chess_3_edit_sorry = False

        # greetings
        renpy.game.persistent._mas_you_chr = False
        renpy.game.persistent.opendoor_opencount = 0
        renpy.game.persistent.opendoor_knockyes = False
        renpy.game.persistent._mas_greeting_type = None

        # hangman
        renpy.game.persistent._mas_hangman_playername = False

        # piano
        renpy.game.persistent._mas_pnml_data = list()
        renpy.game.persistent._mas_piano_keymaps = dict()

        # affection
        renpy.game.persistent._mas_affection["affection"] = 0


    def initialSessionData():
        """
        Completely resets session data to usable initial values.
        NOTE: these are not the defaults, but rather what they would be set to
        on a first load.
        """
        store.persistent.sessions = {
            "last_session_end": None,
            "current_session_start": datetime.datetime.now(),
            "total_playtime": datetime.timedelta(seconds=0),
            "total_sessions": 1,
            "first_session": datetime.datetime.now()
        }


init -999 python:
    import os
    import pytz

    _OVERRIDE_LABEL_TO_BASE_LABEL_MAP = dict()

    # create the log folder if not exist
    if not os.access(os.path.normcase(renpy.config.basedir + "/log"), os.F_OK):
        try:
            os.mkdir(os.path.normcase(renpy.config.basedir + "/log"))
        except:
            pass

    # load timezone info
    # NOTE: this is needed since initialzation of pytz will not include find
    #   timezones if they are included locally
    # NOTE: this means that tz info is not guaranteed until this call.
    pytz.load_resources(os.path.join(
        renpy.config.gamedir,
        "python-packages",
        "pytz",
    ))

    def mas_override_label(label_to_override, override_label):
        """
        Label override function

        IN:
            label_to_override - the label which will be overridden
            override_label - the label to override with
        """
        global _OVERRIDE_LABEL_TO_BASE_LABEL_MAP

        #Check if we're overriding an already overridden label
        if label_to_override in config.label_overrides:
            old_override = config.label_overrides.pop(label_to_override)

            #Remove the data for the label which is no longer acting as an override
            if old_override in _OVERRIDE_LABEL_TO_BASE_LABEL_MAP:
                _OVERRIDE_LABEL_TO_BASE_LABEL_MAP.pop(old_override)

        config.label_overrides[label_to_override] = override_label
        _OVERRIDE_LABEL_TO_BASE_LABEL_MAP[override_label] = label_to_override

init -995 python in mas_utils:
    import store
    import os
    import stat
    import shutil
    import datetime
    import codecs
    import platform
    import time
    import traceback
    import sys
    import pytz
    import tzlocal
    #import tempfile
    from os.path import expanduser
    from renpy.log import LogFile
    from bisect import bisect
    from contextlib import contextmanager

    # LOG messges
    _mas__failrm = "[ERROR] Failed remove: '{0}' | {1}\n"
    _mas__failcp = "[ERROR] Failed copy: '{0}' -> '{1}' | {2}\n"
    _mas__faildir = "[ERROR] Failed to check if dir: {0} | {1}\n"

    # bad text dict
    BAD_TEXT = {
        "{": "{{",
        "[": "[["
    }

    # timezone cache
    _tz_cache = None

    def compareVersionLists(curr_vers, comparative_vers):
        """
        Generic version number checker

        IN:
            curr_vers - current version number as a list (eg. 1.2.5 -> [1, 2, 5])
            comparative_vers - the version we're comparing to as a list, same format as above

            NOTE: The version numbers can be different lengths

        OUT:
            integer:
                - (-1) if the current version number is less than the comparitive version
                - 0 if the current version is the same as the comparitive version
                - 1 if the current version is greater than the comparitive version
        """
        #Define a local function to use to fix up the version lists if need be
        def fixVersionListLen(smaller_vers_list, larger_vers_list):
            """
            Adjusts the smaller version list to be the same length as the larger version list for easy comparison

            IN:
                smaller_vers_list - the smol list to adjust
                larger_vers_list - the list we will adjust the smol list to

            OUT:
                adjusted version list

            NOTE: fills missing indeces with 0's
            """
            for missing_ind in range(len(larger_vers_list) - len(smaller_vers_list)):
                smaller_vers_list.append(0)
            return smaller_vers_list

        #Let's verify that the lists are the same length
        if len(curr_vers) < len(comparative_vers):
            curr_vers = fixVersionListLen(curr_vers, comparative_vers)

        elif len(curr_vers) > len(comparative_vers):
            comparative_vers = fixVersionListLen(comparative_vers, curr_vers)

        #Check if the lists are the same. If so, we're the same version and can return 0
        if comparative_vers == curr_vers:
            return 0

        #Now we iterate and check the version numbers sequentially from left to right
        for index in range(len(curr_vers)):
            if curr_vers[index] > comparative_vers[index]:
                #The current version is greater here, let's return 1 as the rest of the version is irrelevant
                return 1

            elif curr_vers[index] < comparative_vers[index]:
                #Comparative version is greater, the rest of this is irrelevant
                return -1

    def all_none(data=None, lata=None):
        """
        Checks if a dict and/or list is all None

        IN:
            data - Dict of data. values are checked for None-ness
                (Default: None)
            lata - List of data. values are checked for None-ness
                (Default: None)

        RETURNS: True if all data is None, False otherwise
        """
        # check dicts
        if data is not None:
            for value in data.itervalues():
                if value is not None:
                    return False

        # now lists
        if lata is not None:
            for value in lata:
                if value is not None:
                    return False

        return True

    def clean_gui_text(text):
        """
        Cleans the given text so its suitable for GUI usage

        IN:
            text - text to clean

        RETURNS:
            cleaned text
        """
        for bad in BAD_TEXT:
            text = text.replace(bad, BAD_TEXT[bad])

        return text

    def eqfloat(left, right, places=6):
        """
        Float comparisons thatcan handle accuracy errors.
        This uses checks equivalence within a given amount of decimal places

        IN:
            left - value to compare
            right - other value to compare

        RETURNS: True if values are equal, False if not
        """
        acc = 0.1
        if places > 1:
            for x in range(places):
                acc /= 10.0

        return abs(left-right) < acc


    def truncround(value, places=6):
        """
        Does "truncated rounding" for floats. This is done via a floatsplit_i
        that reassembles into a float.

        IN:
            value - float to round
            places - number of decimal places to truncate round to
                (Default: 6)

        RETURNS: truncate-rounded float
        """
        return floatcombine_i(floatsplit_i(value, places), places)


    def floatcombine_i(value, places=6):
        """
        Combines output of floatsplit_i back into a float

        IN:
            value - tuple of the following format:
                [0]: integer part of the float
                [1]: float part of the float as integer
            places - number of places to apply to the float part
                (Default: 6)

        RETURNS: float
        """
        return value[0] + (value[1] / (10.0**places))


    def floatsplit(value):
        """
        Splits a float into int and float parts (unlike _splitfloat which
        returns three ints, or floatsplit_i which returns two ints with
        rounding)

        IN:
            value - float to split

        RETURNS: tuple of the following format:
            [0] - integer portion of float (int)
            [1] - float portion of float (float)
        """
        int_part = int(value)
        return int_part, value - int_part


    def floatsplit_i(value, places=6):
        """
        Similar to floatsplit, but converts the float portion into an int

        IN:
            value - float to split
            places - number of decimal places to keep when converting the
                float to an int
                (Default: 6)

        RETURNS: tuple of the following format:
            [0] - integer portion of float
            [1] - float portion of float, multiplied by 10^places
        """
        int_part, float_part = floatsplit(value)
        scale = 10**places
        return int_part, int(float_part * scale)


    def pdget(key, table, validator=None, defval=None):
        """
        Protected Dict GET
        Gets an item from a dict, using protections to ensure this item is
        valid

        IN:
            key - key of item to get
            table - dict to get from
            validator - function to call with the item to validate it
                If None, no validating done
                (Default: None)
            defval - default value to return if could not get from dict
        """
        if table is not None and key in table:

            item = table[key]

            if validator is None:
                return item

            if validator(table[key]):
                return item

        return defval

    def td2hr(duration):
        """
        Converts a timedetla to hours (fractional)

        IN:
            duration - timedelta to convert

        RETURNS: hours as float
        """
        return (duration.days * 24) + (duration.seconds / 3600.0)


    def get_localzone():
        """
        Wrapper around tzlocal.get_localzone() that won't raise exceptions

        NOTE: this caches the timezone. Call reload_localzone() to gurantee
        timezone is updated.

        RETURNS: pytz tzinfo object of the local time zone.
            if system timezone info is configured wrong, then a special-MAS
            version of a timezone is returned instead. This version works
            like a static, unchanging timezone, using the time.timezone/altzone
            values.
        """
        global _tz_cache
        if _tz_cache is not None:
            return _tz_cache

        try:
            _tz_cache = tzlocal.get_localzone()
        except:
            _tz_cache = store.MASLocalTz.create()

        return _tz_cache


    def reload_localzone():
        """
        Reloads the cached localzone.

        RETURNS: see get_localzone()
        """
        try:
            _tz_cache = tzlocal.reload_localzone()
        except:
            _tz_cache = store.MASLocalTz.reload()

        return _tz_cache


    def local_to_utc(local_dt, latest=True):
        """
        Converts the given local datetime into a UTC datetime.

        NOTE: you shouldn't be using this. UTC time should be where you do
        dt manipulations and use utc_to_local to get a localized dt for human
        reading. datetime has a utcnow() function so use that to get started
        instead of now()

        IN:
            local_dt - datetime to convert, should be naive (no tzinfo)
            latest - True will attempt to reload the local timezone before
                doing the conversion. If dealing with an old datetime, you
                might want to pass False
                (Default: True)

        RETURNS:
            UTC-based naive datetime (no tzinfo).
            This is safe for pickling/saving to persistent.
        """
        if latest:
            local_tz = reload_localzone()
        else:
            local_tz = get_localzone()

        return local_tz.localize(local_dt).astimezone(pytz.utc).replace(tzinfo=None)


    def utc_to_any(utc_dt, target_tz):
        """
        Converts the given UTC datetime into any tz datetime

        IN:
            utc_dt - datetime to convert, should be naive (no tzinfo)
            target_tz - pytz.tzinfo object of the timezone to convert to

        RETURNS:
            datetime converted to the target timezone.
            NOTE: DO NOT PICKLE THIS OR SAVE TO PERSISTENT.
        """
        return pytz.utc.localize(utc_dt).astimezone(target_tz)


    def utc_to_local(utc_dt, latest=True):
        """
        Converts the given UTC datetime into a local datetime

        IN:
            utc_dt - datetime to convert, should be naive (no tzinfo)
            latest - True will attempt to reload the local timezone before
                doing the conversion. If dealing with an old datetime, you
                might want to pass False
                (Default: True)

        RETURNS:
            localized datetime with tzinfo of this zone (see pytz docs)
            NOTE: DO NOT PICKLE THIS or SAVE TO PERSISTENT. While pytz can
                safely pickle, we do not want to force a dependency on the
                persistent.
        """
        if latest:
            return utc_to_any(utc_dt, reload_localzone())

        return utc_to_any(utc_dt, get_localzone())


    def copyfile(oldpath, newpath):
        """
        Copies the file at oldpath into a file at newpath
        Paths assumed to include the filename (like an mv command)

        NOTE:
            if a copy fails, the error is logged

        IN:
            oldpath - path to old file, including filename
            newpath - path to new file, including filename

        RETURNS:
            True if copy succeeded, False otherwise
        """
        try:
            shutil.copyfile(oldpath, newpath)
            return True
        except Exception as e:
            writelog(_mas__failcp.format(oldpath, newpath, str(e)))
        return False


    @contextmanager
    def stdout_as(outstream):
        """
        Context manager that can replace stdout temporarily. Use with the
        with statement (python).

        IN:
            outstream - the stream to temporarily replace sys.stdout with
        """
        oldout = sys.stdout
        sys.stdout = outstream
        try:
            yield
        finally:
            sys.stdout = oldout

    def trydel(f_path, log=False):
        """
        Attempts to delete something at the given path

        NOTE: completely hides exceptions, unless log is True
        """
        try:
            os.remove(f_path)
        except Exception as e:
            if log:
                writelog("[exp] {0}\n".format(repr(e)))

    def trywrite(f_path, msg, log=False, mode="w"):
        """
        Attempts to write out a file at the given path

        Exceptions are hidden

        IN:
            f_path - path to write file
            msg - text to write
            log - True means we log exceptions
                (Default: False)
            mode - write mode to use
                (Defaut: w)
        """
        outfile = None
        try:
            outfile = open(f_path, mode)
            outfile.write(msg)
        except Exception as e:
            if log:
                writelog("[exp] {0}\n".format(repr(e)))
        finally:
            if outfile is not None:
                outfile.close()

    def tryparsedt(_datetime, default=None, sep=" "):
        """
        Trys to parse a datetime isoformat string into a datetime object

        IN:
            _datetime - datetime iso format string to parse
            default - default value to return if parsing fails
            sep - separator used when converting to isoformat

        RETURNS:
            datetime object, or default if parsing failed
        """
        if len(_datetime) == 0:
            return default

        try:
            # separate into date / time portions
            _date, _sep, _time = _datetime.partition(sep)

            # separate _date into y/m/d
            year, month, day = _date.split("-")

            # separate _time into h/m/s
            hour, minute, second = _time.split(":", 2)

            # separate second into s/ms (if applicable)
            second, _sep, ms = second.partition(".")

            # clean ms
            ms = ms[:6]

            # now try and parse everything into ints
            year = tryparseint(year, -1)
            month = tryparseint(month, -1)
            day = tryparseint(day, -1)
            hour = tryparseint(hour, -1)
            minute = tryparseint(minute, -1)
            second = tryparseint(second, -1)
            ms = tryparseint(ms, 0) # ms isn't really important

            # now try to bulid our datetime
            return datetime.datetime(year, month, day, hour, minute, second, ms)

        except:
            return default

    def is_file_present(filename):
        """
        Checks if a file is present
        """
        if not filename.startswith("/"):
            filename = "/" + filename

        filepath = renpy.config.basedir + filename

        try:
            return os.access(os.path.normcase(filepath), os.F_OK)
        except:
            return False

    # unstable should never delete logs
    if store.persistent._mas_unstable_mode:
        mas_log = getMASLog("log/mas_log", append=True, flush=True)
    else:
        mas_log = getMASLog("log/mas_log")

    mas_log_open = mas_log.open()
    mas_log.raw_write = True
    mas_log.write("VERSION: {0}\n".format(store.persistent.version_number))

    def weightedChoice(choice_weight_tuple_list):
        """
        Returns a random item based on weighting.
        NOTE: That weight essentially corresponds to the equivalent of how many times to duplicate the choice

        IN:
            choice_weight_tuple_list - List of tuples with the form (choice, weighting)

        OUT:
            random choice value picked using choice weights
        """
        #No items? Just return None
        if not choice_weight_tuple_list:
            return None

        #Firstly, sort the choice_weight_tuple_list
        choice_weight_tuple_list.sort(key=lambda x: x[1])

        #Now split our tuples into individual lists for choices and weights
        choices, weights = zip(*choice_weight_tuple_list)

        #Some var setup
        total_weight = 0
        cumulative_weights = list()

        #Now we collect all the weights and geneate a cumulative and total weight amount
        for weight in weights:
            total_weight += weight
            cumulative_weights.append(total_weight)

        #NOTE: At first glance this useage of bisect seems incorrect, however it is used to find the closest weight
        #To the randomly selected weight. This is used to return the appropriate choice.
        r_index = bisect(
            cumulative_weights,
            renpy.random.random() * total_weight
        )

        #And return the weighted choice
        return choices[r_index]

init -100 python in mas_utils:
    # utility functions for other stores.
    import datetime
    import ctypes
    import random
    import os
    import math
    from cStringIO import StringIO as fastIO

    __secInDay = 24 * 60 * 60

    __FLIMIT = 1000000

    def tryparsefloat(value, default=0):
        """
        Attempts to parse the given value into a float. Returns the default if
        that parse failed.

        IN:
            value - value to parse
            default - value to return if parse fails
            (Default: 0)

        RETURNS: a float representation of the given value, or default if
            the given value could not be parsed into an float
        """
        try:
            return float(value)
        except:
            return default

    def bullet_list(_list, bullet="  -"):
        """
        Converts a list of items into a bulleted list of strings.

        IN:
            _list - list to convert into bulleted list
            bullet - the bullet to use. A space is added between the bullet and
                the item.
                (Default: 2 spaces and a dash)

        RETURNS: a list of strings where each string is an item with a bullet.
        """
        return [bullet + " " + str(item) for item in _list]


    ### date adjusting functions
    def add_years(initial_date, years):
        """
        ASSUMES:
            initial_date as datetime
            years as an int

        IN:
            initial_date: the date to add years to
            years : the number of years to add

        RETURNS:
            the date with the years added, if it's feb 29th it goes to mar 1st,
            if feb 29 doesn't exists in the new year
        """
        try:

            # Simply add the years using replace
            return initial_date.replace(year=initial_date.year + years)
        except ValueError:

            # We handle the only exception feb 29
            return  initial_date + (datetime.date(initial_date.year + years, 1, 1)
                                - datetime.date(initial_date.year, 1, 1))

    def add_months(starting_date, months):
        """
        Takes a datetime object and add a number of months
        Handles the case where the new month doesn't have that day

        IN:
            starting_date - date representing the date to add months to
            months - amount of months to add

        OUT:
            datetime.date representing the inputted date with the corresponding months added
        """
        old_month=starting_date.month
        old_year=starting_date.year
        old_day=starting_date.day

        #To handle F29 consistently with add_years, we explicitly manage it
        if months and (months/12 + old_year) % 4 != 0 and old_month == 2 and old_day == 29:
            old_month = 3
            old_day = 1

        # get the total of months
        total_months = old_month + months

        # get the new month based on date
        new_month = total_months % 12

        # handle december specially
        new_month = 12 if new_month == 0 else new_month

        # get the new year
        new_year = old_year + int(total_months / 12)
        if new_month == 12:
            new_year -= 1

        #Try adding a month, if that doesn't work (there aren't enough days in the month)
        #keep subtracting days till it works.
        date_worked=False
        reduce_days=0
        while reduce_days<=3 and not date_worked:
            try:
                new_date = starting_date.replace(year=new_year,month=new_month,day=old_day-reduce_days)
                date_worked = True
            except ValueError:
                reduce_days+=1

        if not date_worked:
            raise ValueError('Adding months failed')

        return new_date

    #Takes a datetime object and returns a new datetime with the same date
    #at 3 AM
    # START-OF-DAY
    def sod(starting_date):
        return am3(starting_date)


    def mdnt(starting_date):
        """
        Takes a datetime object and returns a new datetime with the same date
        at midnight

        IN:
            starting_date - date to change

        RETURNS:
            starting_date but at midnight
        """
        return starting_date.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )


    def am3(_datetime):
        """
        Takes a datetime object and returns a new datetime with the same date
        at 3 am.

        IN:
            _datetime - datetime to change

        RETURNS:
            _datetime but at 3am
        """
        return _datetime.replace(
            hour=3,
            minute=0,
            second=0,
            microsecond=0
        )


    def secInDay():
        """
        RETURNS: number of seconds in a day
        """
        return __secInDay


    def time2sec(_time):
        """
        Converts a time value to seconds

        IN:
            time - datetime.time object to convert

        RETURNS: number of seconds
        """
        return (_time.hour * 3600) + (_time.minute * 60) + _time.second


    def fli_indk(lst, d):
        """
        Find
        List
        Item
        IN
        Dictionary
        Keys

        Finds index of an item in the list if it is a key in the given dict.

        IN:
            lst - list to cehck
            d - dictionary to check

        RETURNS: The index of the first item in the list that is a key in the
            dict. There are no checks of if the item can be a valid key.
            -1 is returned if no item in the list is a key in the dict.
        """
        for idx, item in enumerate(lst):
            if item in d:
                return idx

        return -1


    def insert_sort(sort_list, item, key):
        """
        Performs a round of insertion sort.
        This does least to greatest sorting

        IN:
            sort_list - list to insert + sort
            item - item to sort and insert
            key - function to call using the given item to retrieve sort key

        OUT:
            sort_list - list with 1 additonal element, sorted
        """
        index = len(sort_list) - 1
        while index >= 0 and key(sort_list[index]) > key(item):
            index -= 1

        sort_list.insert(index + 1, item)


    def insert_sort_compare(sort_list, item, cmp_func):
        """
        Performs a round of insertion sort using comparison function

        IN:
            sort_list - list to insert + sort
            item - item to sort and insert
            cmp_func - function to compare items with.
                first arg will be item in the list
                second arg will always be the item being inserted
                This should return True if the item is not in the correct place
                False when the item is in the correct place

        OUT:
            sort_list - list with 1 additional element, sorted
        """
        index = len(sort_list) - 1
        while index >= 0 and cmp_func(sort_list[index], item):
            index -= 1

        sort_list.insert(index + 1, item)


    def insert_sort_keyless(sort_list, item):
        """
        Performs a round of insertion sort for natural comparison objects.
        This does least to greatest sorting.

        IN:
            sort_list - list to insert + sort
            item - item to sort and insert

        OUT:
            sort_list - list with 1 additional element, sorted
        """
        index = len(sort_list) - 1
        while index >= 0 and sort_list[index] > item:
            index -= 1

        sort_list.insert(index + 1, item)


    def normalize_points(points, offsets, add=True):
        """
        normalizes a list of points using the given offsets

        IN:
            points - list of points to normalize
            offsets - Tuple of the following format:
                [0] - amount to offset x coords
                [1] - amount to offset y coords
            add - True will add offsets, False will subtract offsets

        RETURNS: list of normalized points
        """
        normal_pts = []

        # setup offsets
        xoffset, yoffset = offsets
        if not add:
            xoffset *= -1
            yoffset *= -1

        for xcoord, ycoord in points:
            normal_pts.append((
                xcoord + xoffset,
                ycoord + yoffset
            ))

        return normal_pts


    def nz_count(value_list):
        """
        NonZero Count

        Counts all non-zero values in the given list

        IN:
            value_list - list to count nonzero values for

        RETURNS: number of nonzero values in list
        """
        count = 0
        for value in value_list:
            count += int(value != 0)

        return count


    def ev_distribute(value_list, amt, nz=False):
        """
        EVen Distribute

        Evenly distributes the given value to a given value list.
        NOTE: only for ints

        IN:
            value_list - list of numbers to distribute to
            amt - amount to evenly distribute
            nz - True will make distribution only apply to non-zero values,
                False will distribute to all
                (Default: False)

        OUT:
            value_list - even distribution amount added to each appropriate
                item in this list

        RETURNS: leftover amount
        """
        # determine effective size
        size = len(value_list)
        if nz:
            size -= nz_count(value_list)

        # deteremine distribution amount
        d_amt = amt / size

        # now distribute
        for index in range(len(value_list)):
            if not nz or value_list[index] > 0:
                value_list[index] += d_amt

        # leftovers
        return amt % size


    def fz_distribute(value_list):
        """
        Flipped Zero Distribute

        Redistributes values in the given list such that:
        1. any index with a value larger than 0 is set to 0
        2. any index with a value of 0 now has a nonzero value
        3. the nonzero is evenly divided among the appropriate indexes

        IN:
            value_list - list of numbers to flip zero distribute

        OUT:
            value_list - flip-zero distributed list of numbers

        RETURNS: any leftover amount
        """
        # determine amt to distribute
        amt = sum(value_list)

        # dont do anything if nothing to distribute
        if amt < 1:
            return 0

        # determine distribution amount
        size = len(value_list) - nz_count(value_list)
        d_amt = amt / size

        # now apply the amount to zero and clear non-zero values
        for index in range(len(value_list)):
            if value_list[index] > 0:
                value_list[index] = 0
            else:
                value_list[index] = d_amt

        # and return leftovers
        return amt % size


    def ip_distribute(value_list, amt_list):
        """
        In Place Distribute

        Distributes values from one list to the other list, based on index.
        Mismatched list sizes are allowed. There is no concept of leftovers
        here.

        IN:
            value_list - list of numbers to distribute to
            amt_list - list of amounts to distribute

        OUT:
            value_list - each corresponding index in amt_list added to
                corresponding index in value_list
        """
        vindex = 0
        amtindex = 0
        while vindex < len(value_list) and amtindex < len(amt_list):
            value_list[vindex] += amt_list[amtindex]


    def lo_distribute(value_list, leftovers, reverse=False, nz=False):
        """
        LeftOver Distribute
        Applies leftovers to the given value list.

        If leftovers are larger than the value list, we do ev_distribute first

        IN:
            value_list - list of numbers to distribute to
            leftovers - amount of leftover to distribute
            reverse - True will add in reverse order, false will not
                (Default: False)
            nz - True will only apply leftovers to non-zero values
                False will not
                (Default: False)

        OUT:
            value_list - some items will have leftovers added to them
        """
        # determine effective size
        if nz:
            size = nz_count(value_list)
        else:
            size = len(value_list)

        # apply ev distribute if leftovesr is too large
        if leftovers >= size:
            leftovers = ev_distribute(value_list, leftovers, nz=nz)

        # dont add leftovers if none leftover
        if leftovers < 1:
            return

        # determine direction
        if reverse:
            indexes = range(len(value_list)-1, -1, -1)
        else:
            indexes = range(len(value_list))

        # apply leftovers
        index = 0
        while leftovers > 0 and index < len(indexes):
            real_index = indexes[index]
            if not nz or value_list[real_index] > 0:
                value_list[real_index] += 1
                leftovers -= 1

            index += 1


    def _EVgenY(_start, _end, current, for_start):
        """
        Generates/decides if a given start/end datetime/date should have its
        year incremented or not.

        NOTE: specialized for Event creation datetime selection
        NOTE: this only modifies year.

        IN:
            _start - datetime/date that begins this period
            _end - datetime/date that ends this period
            current - datetime/date to compare with (should be either today
                or now)
            for_start - True if we want the next valid start, False for end

        RETURNS either next valid _start or next valid _end.
        """
        # keep track of which elem is important to us
        if for_start:
            _focus = _start
        else:
            _focus = _end

        if current < _end:
            # the range hasnt been reached yet, we are fine with this value.
            # or if we are in the range
            return _focus

        # now is actually ahead of target, we should adjust year
        return _focus.replace(year=current.year + 1)


    def randomblob(size, seed=None):
        """
        Generates a blob of StringIO data with the given size

        NOTE: if seed is given, the current random state will be restored
            after this function ends

        NOTE: generated bytes are in range of 0-255

        IN:
            size - size in bytes of the blob to make
            seed - seed to use
                if None, curent time is used (as per random documentation)
                (Default: None)

        RETURNS:
            a cStringIO buffer of the random blob
        """
        data = fastIO()
        _byte_count = 0
        curr_state = None

        # seed set
        curr_state = random.getstate()
        random.seed(seed)

        # generate random bytes
        while _byte_count < size:
            data.write(chr(random.randint(0, 255)))
            _byte_count += 1

        # reset state
        random.setstate(curr_state)

        return data


    def randomblob_fast(size):
        """
        Generates a randomb blob of stringIO data more efficientally and with
        true random using urandom

        NOTE: to prevent errors, we only generate bytes at 4M per iteration

        IN:
            size - size in bytes of the blob to make

        RETURNS:
            a cStringIO buffer of the random blob
        """
        data = fastIO()
        _byte_limit = 4 * (1024**2) # 4MB

        while size > 0:
            make_bytes = _byte_limit
            if (size - _byte_limit) <= 0:
                make_bytes = size
                size = 0

            else:
                size -= make_bytes

            data.write(os.urandom(make_bytes))

        return data


    def intersperse(_list, _sep):
        """
        Intersperses a list with the given separator
        """
        result_list = [_sep] * (len(_list) * 2 - 1)
        result_list[0::2] = _list
        return result_list


    def log_entry(entry_log, value):
        """
        Generic entry add to the given log.
        Stores both time and given value as a tuple:
            [0]: datetime.now()
            [1]: value

        IN:
            entry_log - list to log entry to
            value - value to log in this entry
        """
        entry_log.append((datetime.datetime.now(), value))


    class ISCRAM(ctypes.BigEndianStructure):
        _iscramfieldbuilder = [
            3, 3, 2, 1, 3, 2, 2, 1, 3, 3, 1, 3, 1
        ] # free candy
        _iscramfieldorder = [
            12, 11, 0, 4, 2, 9, 5, 3, 8, 7, 6, 1, 10
        ] # r.org
        _iscramfieldlist = [
            ("sign", ctypes.c_ubyte, 1)
        ]
        for x in range(0, len(_iscramfieldorder)):
            _iscramfieldlist.append((
                "b" + str(x),
                ctypes.c_ubyte,
                _iscramfieldbuilder[_iscramfieldorder.index(x)]
            ))
        _pack_ = 1
        _fields_ = list(_iscramfieldlist)


    class FSCRAM(ctypes.BigEndianStructure):
        _pack_ = 1
        _fields_ = [
            ("sign", ctypes.c_ubyte, 1),
            ("inum", ISCRAM),
            ("fnum", ISCRAM),
            ("dnum", ISCRAM)
        ]


    def _ntoub(num, bsize):
        """
        Partial packing.
        """
        st = 1
        val = 0
        for i in range(0,bsize):
            if (num & st) > 0:
                val += st
            st *= 2

        return val


    def _itoIS(num):
        """
        integer packing
        """
        packednum = ISCRAM()
        if num < 0:
            packednum.sign = 1
            num *= -1

        for i in range(0, len(ISCRAM._iscramfieldbuilder)):
            bsize = ISCRAM._iscramfieldbuilder[i]
            savepoint = _ntoub(num, bsize)
            exec("".join([
                "packednum.b",
                str(ISCRAM._iscramfieldorder[i]),
                " = ",
                str(savepoint)
            ]))
            num = num >> bsize
#            if num <= 0:
#                return packednum

        return packednum


    def _IStoi(packednum):
        """
        integer unpacking
        """
        num = 0
        for i in range(len(ISCRAM._iscramfieldbuilder)-1, -1, -1):
            num = num << ISCRAM._iscramfieldbuilder[i]
            num = num | eval("".join([
                "packednum.b",
                str(ISCRAM._iscramfieldorder[i])
            ]))

        if packednum.sign > 0:
            return num * -1

        return num


    def _ftoFS(num):
        """
        Float packing
        """
        packednum = FSCRAM()
        if num < 0:
            packednum.sign = 1
            num *= -1

        ival = int(num)
        packednum.inum = _itoIS(ival)
        packednum.fnum = _itoIS(int((num - ival) * __FLIMIT))
        packednum.dnum = _itoIS(__FLIMIT)

        return packednum


    def _FStof(packednum):
        """
        Float unpacking
        """
        ival = _IStoi(packednum.inum)
        fnum = _IStoi(packednum.fnum)
        dnum = float(_IStoi(packednum.dnum))

        fval = ival + (fnum / dnum)

        if packednum.sign > 0:
            return fval * -1

        return fval


    def _splitfloat(num):
        """
        Splits a float into integer parts:

        [0]: integer
        [1]: numerator
        [2]: denominator
        """
        ival = int(num)
        cleanival = ival
        if num < 0:
            num *= -1
            cleanival *= -1
        return (ival, int((num - cleanival) * __FLIMIT), __FLIMIT)


init -985 python:
    # global stuff that should be defined somewhat early

    def mas_getSessionLength():
        """
        Gets length of current session, IF this cannot be determined, a
        time delta of 0 is returned
        """
        _now = datetime.datetime.now()
        return _now - store.mas_utils.pdget(
            "current_session_start",
            persistent.sessions,
            validator=store.mas_ev_data_ver._verify_dt_nn,
            defval=_now
        )


    def mas_getAbsenceLength():
        """
        Gets time diff between current session start and last session end
        aka the diff between last session and this
        if not found, time delta of 0 is returned
        """
        return mas_getCurrSeshStart() - mas_getLastSeshEnd()


    def mas_getCurrSeshStart():
        """
        Returns the current session start datetime
        If there is None, we use first session
        """
        return store.mas_utils.pdget(
            "current_session_start",
            persistent.sessions,
            validator=store.mas_ev_data_ver._verify_dt_nn,
            defval=mas_getFirstSesh()
        )


    def mas_getFirstSesh():
        """
        Returns the first session datetime.

        If we could not get it, datetime.datetime.now() is returnd
        """
        return store.mas_utils.pdget(
            "first_session",
            persistent.sessions,
            validator=store.mas_ev_data_ver._verify_dt_nn,
            defval=datetime.datetime.now()
        )

    def mas_isFirstSeshPast(_date):
        """
        Checks if the first session is past the given date

        IN:
            _date - datetime.date to check against

        OUT:
            boolean:
                - True if first sesh is past given date
                - False otherwise
        """
        return mas_getFirstSesh().date() > _date

    def mas_getLastSeshEnd():
        """
        Returns datetime of the last session
        NOTE: if there was no last session, we use first session instead
        """
        return store.mas_utils.pdget(
            "last_session_end",
            persistent.sessions,
            validator=store.mas_ev_data_ver._verify_dt_nn,
            defval=mas_getFirstSesh()
        )


    def mas_getTotalPlaytime():
        """
        Gets total playtime.

        RETURNS: total playtime as a timedelta. If not found, we return a
            time delta of 0
        """
        return store.mas_utils.pdget(
            "total_playtime",
            persistent.sessions,
            validator=store.mas_ev_data_ver._verify_td_nn,
            defval=datetime.timedelta(0)
        )


    def mas_getTotalSessions():
        """
        Gets total sessions

        REUTRNS: total number of sessions. If not found, we return 1
        """
        return store.mas_utils.pdget(
            "total_sessions",
            persistent.sessions,
            validator=store.mas_ev_data_ver._verify_int_nn,
            defval=1
        )


    def mas_TTDetected():
        """
        Checks if time travel was detected
        NOTE: TT detection occurs at init -890
        """
        return store.mas_globals.tt_detected

init -101 python:
    def is_file_present(filename):
        """DEPRECIATED

        Use mas_utils.is_file_present instead
        """
        return store.mas_utils.is_file_present(filename)

init -1 python:
    import datetime # for mac issues i guess.

    if "mouseup_3" in config.keymap['game_menu']:
        config.keymap['game_menu'].remove('mouseup_3')
    if "mouseup_3" not in config.keymap["hide_windows"]:
        config.keymap['hide_windows'].append('mouseup_3')
    config.keymap['self_voicing'] = []
    config.keymap['clipboard_voicing'] = []
    config.keymap['toggle_skip'] = []
    renpy.music.register_channel("music_poem", mixer="music", tight=True)

    #Lookup tables for Monika input topics
    #Add entries with your script in script-topics.rpy
    monika_topics = {}

    def get_procs():
        """
        Retrieves list of processes running right now!

        Only works for windows atm

        RETURNS: list of running processes, or an empty list if
        we couldn't do that
        """
        if renpy.windows:
            import subprocess
            try:
                return subprocess.check_output(
                    "wmic process get Description",
                    shell=True
                ).lower().replace("\r", "").replace(" ", "").split("\n")
            except:
                pass
        return []


    def is_running(proc_list):
        """
        Checks if a process in the given list is currently running.

        RETURNS: True if a proccess in proc_list is running, False otherwise
        """
        running_procs = get_procs()
        if len(running_procs) == 0:
            return False

        for proc in proc_list:
            if proc in running_procs:
                return True

        # otherwise, not found
        return False

    def is_apology_present():
        """
        Checks if the 'imsorry' file is in the characters folder.

        OUT:
            True is apology is present, False otherwise
        """
        return (
            store.mas_utils.is_file_present('/characters/imsorry')
            or store.mas_utils.is_file_present('/characters/imsorry.txt')
        )

    def mas_cvToHM(mins):
        """
        Converts the given minutes into hour / minutes

        IN:
            mins - number of minutes

        RETURNS:
            tuple of the following format:
                [0] - hours
                [1] - minutes
        """
        return (int(mins / 60), int(mins % 60))


    def mas_isSTtoAny(_time, _suntime, _hour, _min):
        """
        Checks if the given time is within this range:
        _suntime <= _time < (_hour, _min)

        NOTE: upper bound is limited to midnight

        IN:
            _time - current time to check
                NOTE: datetime.time object
            _suntime - suntime to use for lower bound
                NOTE: suntimes are given in minutes
            _hour - hour to use for upper bound
            _min - minute to use for upper bound

        RETURNS:
            True if the given time is within bounds of the given suntime and
                given hour / mins, False otherwise
        """
        _curr_minutes = (_time.hour * 60) + _time.minute
        _upper_minutes = (_hour * 60) + _min
        return _suntime <= _curr_minutes < _upper_minutes


    def mas_isSRtoAny(_time, _hour, _min=0):
        """
        Checks if the given time is within Sunrise time to the given _hour
        and _minute

        NOTE: upper bound is limited to midnight

        IN:
            _time - current time to check
                NOTE: datetime.time object
            _hour - hour to use for upper bound
            _min - minute to use for upper bound
                (Default: 0)

        RETURNS:
            True if the given time is whithin bounds of sunrise and the given
            hour / mins, False otherwise
        """
        return mas_isSTtoAny(_time, persistent._mas_sunrise, _hour, _min)


    def mas_isSStoAny(_time, _hour, _min=0):
        """
        Checks if the given time is within sunset to the given _hour and minute

        NOTE: upper bound is limited to midnight

        IN:
            _time - current time to check
                NOTE: datetime.time object
            _hour - hour to use for upper bound
            _min - minute to use for upper bound
                (Default: 0)

        RETURNS:
            True if the given time is within bounds of sunset and the given
            hour/min, False otherwise
        """
        return mas_isSTtoAny(_time, persistent._mas_sunset, _hour, _min)


    def mas_isMNtoAny(_time, _hour, _min=0):
        """
        Checks if the given time is within midnight to the given hour/min.

        NOTE: upper bound is 24 midnight
        NOTE: lower bound is 0 midnight

        IN:
            _time - current time to check
                NOTE: datetime.time object
            _hour - hour to use for upper bound
            _min - minute to use for upper bound
                (Default: 0)

        RETURNS:
            True if the given time is within bounds of midnight and the given
            hour/min, False otherwise
        """
        return mas_isSTtoAny(_time, 0, _hour, _min)


    def mas_isNtoAny(_time, _hour, _min=0):
        """
        Checks if the given time is within noon to the given hour/min.

        NOTE: upper bound is 24 midnight

        IN:
            _time - current time to check
                NOTE: datetime.time object
            _hour - hour to use for upper bound
            _min - minute to use for upper bound
                (Default: 0)

        RETURNS:
            True if the given time is within bounds of noon and the given hour
            /min, False otherwise
        """
        return mas_isSTtoAny(_time, 12*60, _hour, _min)


    def mas_isAnytoST(_time, _hour, _min, _suntime):
        """
        Checks if the given time is within this range:
        (_hour, _min) <= _time < _suntime

        NOTE: lower bound is limited to midnight

        IN:
            _time - current time to check
                NOTE: datetime.time object
            _hour - hour to use for lower bound
            _min - minute to use for lower bound
            _suntime - suntime to use for upper bound
                NOTE: suntimes are given in minutes

        RETURNS:
            True if the given time is within bounds of the given hour / mins
            and the given suntime, false Otherwise
        """
        _curr_minutes = (_time.hour * 60) + _time.minute
        _lower_minutes = (_hour * 60) + _min
        return _lower_minutes <= _curr_minutes < _suntime


    def mas_isAnytoSR(_time, _hour, _min=0):
        """
        Checks if the given time is within a given hour and minute to sunrise
        time

        NOTE: lower bound is limited to midnight

        IN:
            _time - current time to check
                NOTE: datetime.time object
            _hour - hour to use for lower bound
            _min - minute to use for lower bound
                (Default: 0)

        RETURNS:
            True if the given time is within the bounds of the given hour/min
            and sunrise, False otherwise
        """
        return mas_isAnytoST(_time, _hour, _min, persistent._mas_sunrise)


    def mas_isAnytoSS(_time, _hour, _min=0):
        """
        Checks if the given time is within a given hour/min to sunset time

        NOTE: lower bound is limited to midnight

        IN:
            _time - current time to check
                NOTE: datetime.time object
            _hour - hour to use for lower bound
            _min - minute to use for lower bound
                (Default: 0)

        RETURNS:
            True if the given time is within the bounds of the given hour/min
            and sunset, False otherwise
        """
        return mas_isAnytoST(_time, _hour, _min, persistent._mas_sunset)


    def mas_isAnytoMN(_time, _hour, _min=0):
        """
        Checks if the given time is within a given hour/min to midnight (next
        day)

        NOTE: lower bound is limited to midnight
        NOTE: upper bound is 24 - midnight

        IN:
            _time - current time to check
                NOTE: datetime.time object
            _hour - hour to use for lower bound
            _min - mintue to use for lower bound
                (DEfault: 0)

        RETURNS:
            True if the given time is within the bounds of the given hour/min
            and midnight, False otherwise
        """
        return mas_isAnytoST(_time, _hour, _min, 24*60)


    def mas_isAnytoN(_time, _hour, _min=0):
        """
        Checks if the given time is within a given hour/min to noon.

        NOTE: lower bound is limited to midnight

        IN:
            _time - current time to check
                NOTE: datetime.time object
            _hour - hour to use for lower bound
            _min - minute to use for lower bound
                (Default: 0)

        RETURNS:
            True if the given tim eis within the bounds of the given hour/min
            and Noon, False otherwise
        """
        return mas_isAnytoST(_time, _hour, _min, 12*60)


    def mas_isMNtoSR(_time):
        """
        Checks if the given time is within midnight to sunrise

        IN:
            _time - current time to check
                NOTE: datetime.time object

        RETURNS: True if the given time is within midnight to sunrise
        """
        return mas_isAnytoSR(_time, 0)


    def mas_isSRtoN(_time):
        """
        Checks if the given time is within sunrise to noon

        IN:
            _time - current time to check
                NOTE: datetime.time object

        RETURNS: True if the given time is witin sunrise to noon
        """
        return mas_isSRtoAny(_time, 12)


    def mas_isNtoSS(_time):
        """
        Checks if the given time is within noon to sunset

        IN:
            _time - current time to check
                NOTE: datetime.time object

        RETURNS: True if the given time is within noon to sunset
        """
        return mas_isAnytoSS(_time, 12)


    def mas_isSStoMN(_time):
        """
        Checks if the given time is within sunset to midnight

        IN:
            _time - current time to check
                NOTE: datetime.time object

        RETURNS: True if the given time is within sunset to midnight
        """
        return mas_isSStoAny(_time, 24)


    def mas_isSunny(_time):
        """DEPRECATED
        Use mas_isDay instead
        """
        return mas_isDay(_time)


    def mas_isDay(_time):
        """
        Checks if the sun would be up during the given time

        IN:
            _time - current time to check
                NOTE: datetime.time object

        RETURNS: True if it is day time during the given time
        """
        _curr_mins = (_time.hour * 60) + _time.minute
        return persistent._mas_sunrise <= _curr_mins < persistent._mas_sunset


    def mas_isDayNow():
        """
        Checks if the sun would be up right now

        RETURNS: True if the sun would be up now, False if not
        """
        return mas_isDay(datetime.datetime.now().time())


    def mas_isNight(_time):
        """
        Checks if the sun is down during the given time

        IN:
            _time - current time to check
                NOTE: datetime.time object

        RETURNS: True if it the sun is down during the given time
        """
        return not mas_isDay(_time)


    def mas_isNightNow():
        """
        Checks if the sun is down right now

        RETURNS: True if it is night now, False if not
        """
        return not mas_isDayNow()


    def mas_cvToDHM(mins):
        """
        Converts the given minutes into a displayable hour / minutes
        HH:MM
        NOTE: 24 hour format only

        IN:
            mins - number of minutes

        RETURNS:
            string time perfect for displaying
        """
        s_hour, s_min = mas_cvToHM(mins)
        return "{0:0>2d}:{1:0>2d}".format(s_hour, s_min)


    def mas_genDateRange(_start, _end):
        """
        Generates a list of datetime.date objects with the given range.

        NOTE: exclusive:

        IN:
            _start - starting date of range
            _end - ending date of range

        RETURNS: list of datetime.date objects between the _start and _end,
            exclusive. May be empty if invalid start and end dates are given
        """
        # sanity check
        if _start >= _end:
            return []

        _date_range = []
        one_day = datetime.timedelta(days=1)
        curr_date = _start

        while curr_date < _end:
            _date_range.append(curr_date)
            curr_date += one_day

        return _date_range


    def mas_EVgenYDT(_start, _end, for_start):
        """
        Creates a valid start or end datetime for Event creation, given the
        start and end datetimes.

        NOTE: this only modifies year. Build a custom function for something
        more precise.

        IN:
            _start - datetime that begins this period
            _end - datetime that ends this period
            for_start - True if we want the next valid starting datetime
                False if we want the next valid ending datetime

        RETURNS: valid datetime for Event creation
        """
        return store.mas_utils._EVgenY(
            _start,
            _end,
            datetime.datetime.now(),
            for_start
        )


    def mas_EVgenYD(
            _start,
            _end,
            for_start,
            _time=datetime.time.min
        ):
        """
        Variation of mas_EVgenYDT that accepts datetime.dates. This still
        returns datetimes though.

        IN:
            _start - date that begins this period
            _end - date that ends this period
            for_start - True if we want the next valid starting datetime
                False if we want the next valid ending datetime
            _time - time to use with the dates.
                (Default: datetime.time.min)

        RETURNS: valid datetime for Event creation
        """
        return datetime.datetime.combine(
            store.mas_utils._EVgenY(
                _start,
                _end,
                datetime.date.today(),
                for_start
            ),
            _time
        )


    def mas_isSpecialDay():
        """
        Checks if today is a special day(birthday, anniversary or holiday)

        RETURNS:
            boolean indicating if today is a special day.
        """
        # TODO keep adding special days as we add them
        return (
            mas_isMonikaBirthday()
            or mas_isO31()
            or mas_isD25()
            or (mas_anni.isAnniAny() and not mas_anni.isAnniWeek())
            or mas_isNYE()
            or mas_isF14()
        )


    def mas_maxPlaytime():
        return datetime.datetime.now() - datetime.datetime(2017, 9, 22)


    def mas_isInDateRange(
            subject,
            _start,
            _end,
            start_inclusive=True,
            end_inclusive=False
        ):
        """
        Checks if the given subject date is within  range of the given start
        end dates.

        NOTE: this does year normalization, so we only compare months and days
        NOTE: we do NOT compare years

        IN:
            subject - subject date to compare
            _start - starting date of the range
            _end - ending date of the range
            start_inclusive - True if start date should be inclusive
                (Derfault: True)
            end_inclusive - True if end date should be inclusive
                (Default: False)

        RETURNS: True if the given subject is within date range, False if not
        """
        real_start = _start.replace(year=subject.year)
        real_end = _end.replace(year=subject.year)

        if start_inclusive:
            if real_start > subject:
                return False

        else:
            if real_start >= subject:
                return False

        if end_inclusive:
            if subject > real_end:
                return False

        else:
            if subject >= real_end:
                return False

        # otherwise we passed the cases
        return True


    def get_pos(channel='music'):
        """
        Gets the current position in what's playing on the provided channel

        IN:
            channel - The channel to get the sound position for
                (Default: 'music')
        """
        pos = renpy.music.get_pos(channel=channel)
        if pos:
            return pos
        return 0


    def delete_all_saves():
        """
        Deletes all saved states
        """
        for savegame in renpy.list_saved_games(fast=True):
            renpy.unlink_save(savegame)


    def delete_character(name):
        """
        Deletes a .chr file for a character

        IN:
            name of the character who's chr file we want to delete
        """
        if persistent.do_not_delete:
            return

        try:
            os.remove(config.basedir + "/characters/" + name + ".chr")

        except:
            pass


    def pause(time=None):
        """
        Pauses for the given amount of time

        IN:
            time - The time to pause for. If None, a pause until the user progresses is assumed
                (Default: None)
        """
        if not time:
            renpy.ui.saybehavior(afm=" ")
            renpy.ui.interact(mouse='pause', type='pause', roll_forward=None)
            return

        #Verify valid time
        if time <= 0:
            return

        renpy.pause(time)


        # Return installed Steam IDS from steam installation directory
    def enumerate_steam():
        """
        Gets installed steam application IDs from the main steam install directory

        OUT:
            List of application IDs

        NOTE: Does NOT work if the user has edited their game install directory for windows at all
        """
        installPath=""
        if renpy.windows:
            import _winreg    # mod specific
            # Grab first steam installation directory
            # If you're like me, it will miss libraries installed on another drive
            aReg = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)

            try:
                # Check 32 bit
                keyVal = _winreg.OpenKey(aReg, r"SOFTWARE\Valve\Steam")

            except:
                # Check 64 bit
                try:
                   keyVal = _winreg.OpenKey(aReg, r"SOFTWARE\Wow6432Node\Valve\Steam")

                except:
                   # No Steam
                   return None

            for i in range(4):
                # Value Name, Value Data, Value Type
                n, installPath, t = _winreg.EnumValue(keyVal, i)
                if n == "InstallPath":
                    break

            installPath += "/steamapps"

        elif renpy.macintosh:
            installPath = os.environ.get("HOME") + "/Library/Application Support/Steam/SteamApps"

        elif renpy.linux:
            installPath = os.environ.get("HOME") + "/.steam/Steam/steamapps"
            # Possibly also ~/.local/share/Steam/SteamApps/common/Kerbal Space Program?

        #Ideally we should never end up here, but in the case we do, we should prevent any work from being done
        #That's not necessary
        else:
            return None

        try:
            appIds = [file[12:-4] for file in os.listdir(installPath) if file.startswith("appmanifest")]

        except:
            appIds = None
        return appIds


init 2 python:
    import re
    #Global functions that should be defined after level 0
    def mas_startupPlushieLogic(chance=4):
        """
        Runs a simple random check for the quetzal plushie.

        IN:
            chance - value that determines the chance of that
                determines if the plushie will appear
                Defualts to 4
        """
        #3 conditions:

        #1. Do we even have plushie enabled?
        #2. Is it f14? (heartchoc gift interferes)
        #3. Are we currently eating something?

        #If any are true, we cannot have plushie out.
        if (
            not persistent._mas_acs_enable_quetzalplushie
            or mas_isF14()
            or MASConsumable._getCurrentFood()
        ):
            # run the plushie exit PP in case plushie is no longer enabled
            mas_acs_quetzalplushie.exit(monika_chr)
            return


        if renpy.random.randint(1,chance) == 1:
            if persistent._mas_d25_deco_active:
                #if in d25 mode, it's seasonal, and also norm+
                monika_chr.wear_acs_pst(mas_acs_quetzalplushie_santahat)

            else:
                monika_chr.wear_acs_pst(mas_acs_quetzalplushie)

        else:
            # run the plushie exit PP if plushie is not selected
            mas_acs_quetzalplushie.exit(monika_chr)

        return

    def mas_incMoniReload():
        """
        Increments the monika reload counter unless its at max
        """
        if persistent.monika_reload < 4:
            persistent.monika_reload += 1

    def mas_isFirstSeshDay(_date=None):
        """
        Checks if _date is the day of first session

        IN:
            _date - date to compare against
            (NOTE: if not provided, today is assumed)
        """
        if not _date:
            _date = datetime.date.today()

        return _date == mas_getFirstSesh().date()

    def mas_hasRPYFiles():
        """
        Checks if there are rpy files in the gamedir
        """
        return len(mas_getRPYFiles()) > 0

    def mas_getRPYFiles():
        """
        Gets a list of rpy files in the gamedir
        """
        rpyCheckStation = store.MASDockingStation(renpy.config.gamedir)

        return rpyCheckStation.getPackageList(".rpy")

    def mas_is18Over(_date=None):
        """
        Checks if player is over 18

        IN:
            _date - date to check
            If None, today is assumed.
            (Default: None)

        OUT:
            boolean:
                - True if player is over 18
                - False otherwise
        """
        #If we don't have player bday, we assume not.
        if not persistent._mas_player_bday:
            return False

        return mas_getPlayerAge(_date) >= 18

    def mas_getPlayerAge(_date=None):
        """
        Gets the player age

        IN:
            _date - the datetime.date to get the player age at
            (Default: None)

        OUT:
            integer representing the player's current age or None if we don't have player's bday
        """
        if not persistent._mas_player_bday:
            return 0

        elif _date is None:
            _date = datetime.date.today()

        year_bday = mas_player_bday_curr(_date)
        _years = year_bday.year - persistent._mas_player_bday.year

        if _date < year_bday:
            _years -= 1

        return _years

    def mas_canShowRisque(aff_thresh=2000, grace=None):
        """
        Checks if we can show something risque

        Conditions for this:
            1. We're not in sensitive mode
            2. Player has had first kiss (No point going for risque things if this hasn't been met yet)
            3. Player is over 18
            4. Aff condition (raw)

        IN:
            aff_thresh:
                - Raw affection value to be greater than or equal to
            grace:
                - a grace period passed in as a timedelta
                  defaults to 1 week

        OUT:
            boolean:
                - True if the above conditions are satisfied
                - False if not
        """

        if grace is None:
            grace = datetime.timedelta(weeks=1)

        _date = datetime.date.today() + grace

        return (
            not persistent._mas_sensitive_mode
            and persistent._mas_first_kiss is not None
            and mas_is18Over(_date)
            and persistent._mas_affection.get("affection", 0) >= aff_thresh
        )

    def mas_timePastSince(timekeeper, passed_time, _now=None):
        """
        Checks if a certain amount of time has passed since the time in the timekeeper
        IN:
            timekeeper:
                variable holding the time we last checked whatever it restricts
                (can be datetime.datetime or datetime.date)

            passed_time:
                datetime.timedelta of the amount of time which should
                have passed since the last check in order to return True

            _now:
                time to check against (If none, now is assumed, (Default: None))
        OUT:
            boolean:
                - True if it has been passed_time units past timekeeper
                - False otherwise
        """
        if timekeeper is None:
            return True

        elif _now is None:
            _now = datetime.datetime.now()

        #If our timekeeper is holding a datetime.date, we need to convert it to a datetime.datetime
        if not isinstance(timekeeper, datetime.datetime):
            timekeeper = datetime.datetime.combine(timekeeper, datetime.time())

        return timekeeper + passed_time <= _now

    def mas_pastOneDay(timekeeper, _now=None):
        """
        One day time past version of mas_timePastSince()

        IN:
            timekeeper - variable holding the time since last event
            _now - time to check against (Default: None)
        """
        return mas_timePastSince(timekeeper, datetime.timedelta(days=1), _now)

    def mas_setTODVars():
        """
        Sets the mas_globals.time_of_day variable

        NOTE: Ignores Suntime values

        RULES:
            4:00 AM - 11:59:59 AM == 'morning'
            12:00 PM - 4:59:59 PM == 'afternoon'
            5:00 PM - 8:59:59 PM == 'evening'
            9:00 PM - 3:59:59 AM == 'night'
        """
        curr_hour = datetime.datetime.now().time().hour

        #Set morning
        if 4 <= curr_hour <= 11:
            store.mas_globals.time_of_day_4state = "morning"
            store.mas_globals.time_of_day_3state = "morning"

        elif 12 <= curr_hour <= 16:
            store.mas_globals.time_of_day_4state = "afternoon"
            store.mas_globals.time_of_day_3state = "afternoon"

        elif 17 <= curr_hour <= 20:
            store.mas_globals.time_of_day_4state = "evening"
            store.mas_globals.time_of_day_3state = "evening"

        else:
            store.mas_globals.time_of_day_4state = "night"
            store.mas_globals.time_of_day_3state = "evening"

    def mas_seenLabels(label_list, seen_all=False):
        """
        List format for renpy.seen_label. Allows checking if we've seen multiple labels at once

        IN:
            label_list - list of labels we want to check if we've seen
            seen_all - True if all labels in label_list must have been seen in order for this function to return True.
            False otherwise
                (Default: False)
                (NOTE: If seen_all is False, seeing ANY of the labels will let this function return True)

        OUT:
            boolean:
                - True if we have seen the inputted labels and met the seen_all criteria
                - False otherwise
        """
        for _label in label_list:
            seen = renpy.seen_label(_label)

            #First, filter out if we have an unseen label and we must have seen all
            if not seen and seen_all:
                return False

            #As well, if it's a seen label and we don't need to see all
            elif seen and not seen_all:
                return True

        #If we're here, that means we need to do some returns based on the values we put in
        return seen_all

    def mas_a_an_str(ref_str, ignore_case=True):
        """
        Takes in a reference string and returns it back with an 'a' prefix or 'an' prefix depending on starting letter

        IN:
            ref_str - string in question to prefix
            ignore_case - whether or not we should ignore capitalization of a/an and not adjust the capitalization of ref_str
                (Default: True)

        OUT:
            string prefixed with a/an
        """
        return ("{0} {1}".format(
            mas_a_an(ref_str, ignore_case),
            ref_str.lower() if not ignore_case and (ref_str[0].isupper() and not ref_str.isupper()) else ref_str
        ))

    def mas_a_an(ref_str, ignore_case=True):
        """
        Takes in a reference string and returns either a/an based on the first letter of the word

        IN:
            ref_str - string in question to prefix
            ignore_case - whether or not we should ignore capitalization of a/an and just use lowercase
                (Default: True)

        OUT:
            a/an based on the ref string
        """
        should_capitalize = not ignore_case and ref_str[0].isupper()

        if ref_str[0] in "aeiouAEIOU":
            return "An" if should_capitalize else "an"
        return "A" if should_capitalize else "a"

    def mas_setEventPause(seconds=60):
        """
        Sets a pause 'til next event

        IN:
            seconds - the number of seconds to pause for. Can be None to remove pause
                (Default: 60)
        """
        if not seconds:
            mas_globals.event_unpause_dt = None

        else:
            mas_globals.event_unpause_dt = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)

init 21 python:
    def mas_get_player_nickname(capitalize=False, exclude_names=[], _default=None, regex_replace_with_nullstr=None):
        """
        Picks a nickname for the player at random based on accepted nicknames

        IN:
            capitalize - Whether or not we should capitalize the first character
                (Default: False)

            exclude_names - List of names to be excluded in the selection pool for nicknames
                (Default: Empty list)

            _default - Default name to return if affection < affectionate or no nicknames have been set/allowed
                If None, the player's name is assumed
                (Default: None)

            regex_replace_with_nullstr - Regex str to use to identify parts of a nickname which should be replaced with an empty
                string. If None, this is ignored
                (Default: None)

        NOTE: If affection is below affectionate or player has no nicknames set, we just use the player name
        """
        if _default is None:
            _default = player

        #If we're at or below happy, we just use playername
        if mas_isMoniHappy(lower=True) or not persistent._mas_player_nicknames:
            return _default

        nickname_pool = persistent._mas_player_nicknames + [player]

        #If we have some exclusions, we should factor them in
        if exclude_names:
            nickname_pool = [
                nickname
                for nickname in nickname_pool
                if nickname not in exclude_names
            ]

            #If we've excluded everything, we'll use the default value
            if not nickname_pool:
                return _default

        #Now select a name
        selected_nickname = random.choice(nickname_pool)

        if regex_replace_with_nullstr is not None:
            selected_nickname = re.sub(regex_replace_with_nullstr, "", selected_nickname)

        #And handle capitalization
        if capitalize:
            selected_nickname = selected_nickname.capitalize()
        return selected_nickname

    def mas_input(prompt, default="", allow=None, exclude="{}", length=None, with_none=None, pixel_width=None, screen="input", screen_kwargs={}):
        """
        Calling this function pops up a window asking the player to enter some
        text.

        IN:
            prompt - a string giving a prompt to display to the player

            default - a string giving the initial text that will be edited by the player
                (Default: "")

            allow - a string giving a list of characters that will
                be allowed in the text
                (Default: None)

            exclude - if a character is present in this string, it is not
                allowed in the text
                (Default: "{}")

            length - an integer giving the maximum length of the input string
                (Default: None)

            with_none - the transition to use
                (Default: None)

            pixel_width - if not None, the input is limited to being this many pixels wide,
                in the font used by the input to display text
                (Default: None)

            screen - the name of the screen that takes input. If not given, the 'input'
                screen is used
                (Default: "input")

            screen_kwargs - the keyword arguments to pass in to the screen
                NOTE: passing in the prompt argument is not mandatory here
                (Default: {})

        OUT:
            entered string
        """
        renpy.exports.mode("input")

        roll_forward = renpy.exports.roll_forward_info()
        if not isinstance(roll_forward, basestring):
            roll_forward = None

        # use previous data in rollback
        if roll_forward is not None:
            default = roll_forward

        fixed = renpy.in_fixed_rollback()

        if renpy.has_screen(screen):
            widget_properties = { }
            widget_properties["input"] = dict(default=default, length=length, allow=allow, exclude=exclude, editable=not fixed, pixel_width=pixel_width)

            screen_kwargs["prompt"] = prompt

            renpy.show_screen(screen, _transient=True, _widget_properties=widget_properties, **screen_kwargs)

        else:

            if screen != "input":
                raise Exception("The '{}' screen does not exist.".format(screen))

            renpy.ui.window(style="input_window")
            renpy.ui.vbox()
            renpy.ui.text(prompt, style="input_prompt")
            inputwidget = renpy.ui.input(default, length=length, style="input_text", allow=allow, exclude=exclude)

            # disable input in fixed rollback
            if fixed:
                inputwidget.disable()

            renpy.ui.close()

        renpy.exports.shown_window()

        if not renpy.game.after_rollback:
            renpy.loadsave.force_autosave(True)

        # use normal "say" click behavior if input can't be changed
        if fixed:
            renpy.ui.saybehavior()

        rv = renpy.ui.interact(mouse="prompt", type="input", roll_forward=roll_forward)
        renpy.exports.checkpoint(rv)

        if with_none is None:
            with_none = renpy.config.implicit_with_none

        if with_none:
            renpy.game.interface.do_with(None, None)

        return rv

    def mas_getMousePos():
        """
        Gets the mouse position in terms of physical screen size

        OUT:
            tuple, (x, y) coordinates representing the mouse position
        """
        virtual_width = config.screen_width * 10000
        virtual_height = config.screen_height * 10000
        physical_width, physical_height = renpy.get_physical_size()
        dw, dh = pygame.display.get_surface().get_size()
        mouse_x, mouse_y = pygame.mouse.get_pos()

        #Converts the mouse coordinates from pygame's relative screen size coords (based on config vars) to physical size
        #NOTE: THIS IS NEEDED FOR UI SCALING OTHER THAN 100%
        mouse_x = (mouse_x * physical_width) / dw
        mouse_y = (mouse_y * physical_height) / dh

        r = None
        #This part calculates the "true" position, it can handle weirdly sized screens
        if virtual_width / (virtual_height / 10000) > physical_width * 10000 / physical_height:
            r = virtual_width / physical_width
            mouse_y -= (physical_height - virtual_height / r) / 2
        else:
            r = virtual_height / physical_height
            mouse_x -= (physical_width - virtual_width / r) / 2

        newx = (mouse_x * r) / 10000
        newy = (mouse_y * r) / 10000

        return (newx, newy)

    def mas_quipExp(exp_code):
        """
        Allows expressions to be inserted into quips directly via function substitution

        (This is effectively a renpy.show that returns '' instead of None)

        IN:
            exp_code - code of the expression as str (ex: '1hua')
        """
        renpy.show("monika " + exp_code)
        return ""

# Music
define audio.t1 = "<loop 22.073>bgm/1.ogg"  #Main theme (title)
define audio.t2 = "<loop 4.499>bgm/2.ogg"   #Sayori theme
define audio.t2g = "bgm/2g.ogg"
define audio.t2g2 = "<from 4.499 loop 4.499>bgm/2.ogg"
define audio.t2g3 = "<loop 4.492>bgm/2g2.ogg"
define audio.t3 = "<loop 4.618>bgm/3.ogg"   #Main theme (in-game)
define audio.t3g = "<to 15.255>bgm/3g.ogg"
define audio.t3g2 = "<from 15.255 loop 4.618>bgm/3.ogg"
define audio.t3g3 = "<loop 4.618>bgm/3g2.ogg"
define audio.t3m = "<loop 4.618>bgm/3.ogg"
define audio.t4 = "<loop 19.451>bgm/4.ogg"  #Poem minigame
define audio.t4g = "<loop 1.000>bgm/4g.ogg"
define audio.t5 = "<loop 4.444>bgm/5.ogg"   #Sharing poems
define audio.t5b = "<loop 4.444>bgm/5.ogg"
define audio.t5c = "<loop 4.444>bgm/5.ogg"
define audio.t6 = "<loop 10.893>bgm/6.ogg"  #Yuri/Natsuki theme
define audio.t6g = "<loop 10.893>bgm/6g.ogg"
define audio.t6r = "<to 39.817 loop 0>bgm/6r.ogg"
define audio.t6s = "<loop 43.572>bgm/6s.ogg"
define audio.t7 = "<loop 2.291>bgm/7.ogg"   #Causing trouble
define audio.t7a = "<loop 4.316 to 12.453>bgm/7.ogg"
define audio.t7g = "<loop 31.880>bgm/7g.ogg"
define audio.t8 = "<loop 9.938>bgm/8.ogg"   #Trouble resolved
define audio.t9 = "<loop 3.172>bgm/9.ogg"   #Emotional
define audio.t9g = "<loop 1.532>bgm/9g.ogg" #207% speed
define audio.t10 = "<loop 5.861>bgm/10.ogg"   #Confession
define audio.t10y = "<loop 0>bgm/10-yuri.ogg"
define audio.td = "<loop 36.782>bgm/d.ogg"

define audio.m1 = "bgm/m1.ogg"
define audio.mend = "<loop 6.424>bgm/monika-end.ogg"

define audio.ghostmenu = "<loop 0>bgm/ghostmenu.ogg"
define audio.g1 = "<loop 0>bgm/g1.ogg"
define audio.g2 = "<loop 0>bgm/g2.ogg"
define audio.hb = "<loop 0>bgm/heartbeat.ogg"

define audio.closet_open = "sfx/closet-open.ogg"
define audio.closet_close = "sfx/closet-close.ogg"
define audio.page_turn = "sfx/pageflip.ogg"
define audio.fall = "sfx/fall.ogg"

# custom audio
# big thanks to sebastianN01 for the rain sounds
define audio.rain = "mod_assets/sounds/amb/rain_2.ogg"

# Backgrounds
image black = "#000000"
image dark = "#000000e4"
image darkred = "#110000c8"
image white = "#ffffff"
image splash = "bg/splash.png"
image end:
    truecenter
    "gui/end.png"
image bg residential_day = "bg/residential.png"
image bg class_day = "bg/class.png"
image bg corridor = "bg/corridor.png"
image bg club_day = "bg/club.png"
image bg club_day2:
    choice:
        "bg club_day"
    choice:
        "bg club_day"
    choice:
        "bg club_day"
    choice:
        "bg club_day"
    choice:
        "bg club_day"
    choice:
        "bg/club-skill.png"
image bg closet = "bg/closet.png"
image bg bedroom = "bg/bedroom.png"
image bg sayori_bedroom = "bg/sayori_bedroom.png"
image bg house = "bg/house.png"
image bg kitchen = "bg/kitchen.png"

image bg notebook = "bg/notebook.png"
image bg notebook-glitch = "bg/notebook-glitch.png"

image bg glitch = LiveTile("bg/glitch.jpg")

image glitch_color:
    ytile 3
    zoom 2.5
    parallel:
        "bg/glitch-red.png"
        0.1
        "bg/glitch-green.png"
        0.1
        "bg/glitch-blue.png"
        0.1
        repeat
    parallel:
        yoffset 720
        linear 0.5 yoffset 0
        repeat
    parallel:
        choice:
            xoffset 0
        choice:
            xoffset 10
        choice:
            xoffset 20
        choice:
            xoffset 35
        choice:
            xoffset -10
        choice:
            xoffset -20
        choice:
            xoffset -30
        0.01
        repeat
    parallel:
        alpha 0.6
        linear 0.15 alpha 0.1
        0.2
        alpha 0.6
        linear 0.15 alpha 0.1
        0.2
        alpha 0.7
        linear 0.45 alpha 0
        #1.0
        #linear 1.0 alpha 0.0

image glitch_color2:
    ytile 3
    zoom 2.5
    parallel:
        "bg/glitch-red.png"
        0.1
        "bg/glitch-green.png"
        0.1
        "bg/glitch-blue.png"
        0.1
        repeat
    parallel:
        yoffset 720
        linear 0.5 yoffset 0
        repeat
    parallel:
        choice:
            xoffset 0
        choice:
            xoffset 10
        choice:
            xoffset 20
        choice:
            xoffset 35
        choice:
            xoffset -10
        choice:
            xoffset -20
        choice:
            xoffset -30
        0.01
        repeat
    parallel:
        alpha 0.7
        linear 0.45 alpha 0
        #1.0
        #linear 1.0 alpha 0.0

# Sayori
image sayori 1 = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/a.png")
image sayori 1a = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/a.png")
image sayori 1b = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/b.png")
image sayori 1c = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/c.png")
image sayori 1d = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/d.png")
image sayori 1e = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/e.png")
image sayori 1f = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/f.png")
image sayori 1g = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/g.png")
image sayori 1h = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/h.png")
image sayori 1i = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/i.png")
image sayori 1j = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/j.png")
image sayori 1k = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/k.png")
image sayori 1l = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/l.png")
image sayori 1m = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/m.png")
image sayori 1n = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/n.png")
image sayori 1o = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/o.png")
image sayori 1p = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/p.png")
image sayori 1q = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/q.png")
image sayori 1r = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/r.png")
image sayori 1s = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/s.png")
image sayori 1t = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/t.png")
image sayori 1u = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/u.png")
image sayori 1v = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/v.png")
image sayori 1w = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/w.png")
image sayori 1x = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/x.png")
image sayori 1y = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/y.png")

image sayori 2 = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/a.png")
image sayori 2a = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/a.png")
image sayori 2b = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/b.png")
image sayori 2c = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/c.png")
image sayori 2d = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/d.png")
image sayori 2e = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/e.png")
image sayori 2f = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/f.png")
image sayori 2g = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/g.png")
image sayori 2h = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/h.png")
image sayori 2i = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/i.png")
image sayori 2j = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/j.png")
image sayori 2k = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/k.png")
image sayori 2l = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/l.png")
image sayori 2m = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/m.png")
image sayori 2n = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/n.png")
image sayori 2o = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/o.png")
image sayori 2p = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/p.png")
image sayori 2q = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/q.png")
image sayori 2r = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/r.png")
image sayori 2s = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/s.png")
image sayori 2t = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/t.png")
image sayori 2u = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/u.png")
image sayori 2v = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/v.png")
image sayori 2w = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/w.png")
image sayori 2x = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/x.png")
image sayori 2y = im.Composite((960, 960), (0, 0), "sayori/1l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/y.png")

image sayori 3 = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/a.png")
image sayori 3a = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/a.png")
image sayori 3b = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/b.png")
image sayori 3c = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/c.png")
image sayori 3d = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/d.png")
image sayori 3e = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/e.png")
image sayori 3f = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/f.png")
image sayori 3g = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/g.png")
image sayori 3h = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/h.png")
image sayori 3i = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/i.png")
image sayori 3j = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/j.png")
image sayori 3k = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/k.png")
image sayori 3l = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/l.png")
image sayori 3m = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/m.png")
image sayori 3n = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/n.png")
image sayori 3o = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/o.png")
image sayori 3p = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/p.png")
image sayori 3q = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/q.png")
image sayori 3r = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/r.png")
image sayori 3s = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/s.png")
image sayori 3t = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/t.png")
image sayori 3u = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/u.png")
image sayori 3v = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/v.png")
image sayori 3w = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/w.png")
image sayori 3x = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/x.png")
image sayori 3y = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/1r.png", (0, 0), "sayori/y.png")

image sayori 4 = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/a.png")
image sayori 4a = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/a.png")
image sayori 4b = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/b.png")
image sayori 4c = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/c.png")
image sayori 4d = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/d.png")
image sayori 4e = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/e.png")
image sayori 4f = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/f.png")
image sayori 4g = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/g.png")
image sayori 4h = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/h.png")
image sayori 4i = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/i.png")
image sayori 4j = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/j.png")
image sayori 4k = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/k.png")
image sayori 4l = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/l.png")
image sayori 4m = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/m.png")
image sayori 4n = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/n.png")
image sayori 4o = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/o.png")
image sayori 4p = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/p.png")
image sayori 4q = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/q.png")
image sayori 4r = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/r.png")
image sayori 4s = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/s.png")
image sayori 4t = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/t.png")
image sayori 4u = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/u.png")
image sayori 4v = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/v.png")
image sayori 4w = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/w.png")
image sayori 4x = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/x.png")
image sayori 4y = im.Composite((960, 960), (0, 0), "sayori/2l.png", (0, 0), "sayori/2r.png", (0, 0), "sayori/y.png")

image sayori 5 = im.Composite((960, 960), (0, 0), "sayori/3a.png")
image sayori 5a = im.Composite((960, 960), (0, 0), "sayori/3a.png")
image sayori 5b = im.Composite((960, 960), (0, 0), "sayori/3b.png")
image sayori 5c = im.Composite((960, 960), (0, 0), "sayori/3c.png")
image sayori 5d = im.Composite((960, 960), (0, 0), "sayori/3d.png")

image sayori 1ba = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/a.png")
image sayori 1bb = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/b.png")
image sayori 1bc = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/c.png")
image sayori 1bd = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/d.png")
image sayori 1be = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/e.png")
image sayori 1bf = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/f.png")
image sayori 1bg = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/g.png")
image sayori 1bh = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/h.png")
image sayori 1bi = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/i.png")
image sayori 1bj = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/j.png")
image sayori 1bk = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/k.png")
image sayori 1bl = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/l.png")
image sayori 1bm = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/m.png")
image sayori 1bn = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/n.png")
image sayori 1bo = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/o.png")
image sayori 1bp = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/p.png")
image sayori 1bq = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/q.png")
image sayori 1br = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/r.png")
image sayori 1bs = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/s.png")
image sayori 1bt = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/t.png")
image sayori 1bu = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/u.png")
image sayori 1bv = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/v.png")
image sayori 1bw = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/w.png")
image sayori 1bx = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/x.png")
image sayori 1by = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/y.png")

image sayori 2ba = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/a.png")
image sayori 2bb = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/b.png")
image sayori 2bc = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/c.png")
image sayori 2bd = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/d.png")
image sayori 2be = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/e.png")
image sayori 2bf = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/f.png")
image sayori 2bg = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/g.png")
image sayori 2bh = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/h.png")
image sayori 2bi = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/i.png")
image sayori 2bj = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/j.png")
image sayori 2bk = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/k.png")
image sayori 2bl = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/l.png")
image sayori 2bm = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/m.png")
image sayori 2bn = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/n.png")
image sayori 2bo = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/o.png")
image sayori 2bp = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/p.png")
image sayori 2bq = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/q.png")
image sayori 2br = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/r.png")
image sayori 2bs = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/s.png")
image sayori 2bt = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/t.png")
image sayori 2bu = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/u.png")
image sayori 2bv = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/v.png")
image sayori 2bw = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/w.png")
image sayori 2bx = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/x.png")
image sayori 2by = im.Composite((960, 960), (0, 0), "sayori/1bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/y.png")

image sayori 3ba = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/a.png")
image sayori 3bb = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/b.png")
image sayori 3bc = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/c.png")
image sayori 3bd = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/d.png")
image sayori 3be = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/e.png")
image sayori 3bf = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/f.png")
image sayori 3bg = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/g.png")
image sayori 3bh = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/h.png")
image sayori 3bi = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/i.png")
image sayori 3bj = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/j.png")
image sayori 3bk = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/k.png")
image sayori 3bl = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/l.png")
image sayori 3bm = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/m.png")
image sayori 3bn = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/n.png")
image sayori 3bo = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/o.png")
image sayori 3bp = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/p.png")
image sayori 3bq = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/q.png")
image sayori 3br = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/r.png")
image sayori 3bs = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/s.png")
image sayori 3bt = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/t.png")
image sayori 3bu = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/u.png")
image sayori 3bv = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/v.png")
image sayori 3bw = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/w.png")
image sayori 3bx = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/x.png")
image sayori 3by = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/1br.png", (0, 0), "sayori/y.png")

image sayori 4ba = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/a.png")
image sayori 4bb = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/b.png")
image sayori 4bc = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/c.png")
image sayori 4bd = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/d.png")
image sayori 4be = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/e.png")
image sayori 4bf = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/f.png")
image sayori 4bg = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/g.png")
image sayori 4bh = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/h.png")
image sayori 4bi = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/i.png")
image sayori 4bj = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/j.png")
image sayori 4bk = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/k.png")
image sayori 4bl = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/l.png")
image sayori 4bm = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/m.png")
image sayori 4bn = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/n.png")
image sayori 4bo = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/o.png")
image sayori 4bp = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/p.png")
image sayori 4bq = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/q.png")
image sayori 4br = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/r.png")
image sayori 4bs = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/s.png")
image sayori 4bt = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/t.png")
image sayori 4bu = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/u.png")
image sayori 4bv = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/v.png")
image sayori 4bw = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/w.png")
image sayori 4bx = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/x.png")
image sayori 4by = im.Composite((960, 960), (0, 0), "sayori/2bl.png", (0, 0), "sayori/2br.png", (0, 0), "sayori/y.png")

image sayori glitch:
    "sayori/glitch1.png"
    pause 0.01666
    "sayori/glitch2.png"
    pause 0.01666
    repeat

# Natsuki
image natsuki 11 = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/1t.png")
image natsuki 1a = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/a.png")
image natsuki 1b = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/b.png")
image natsuki 1c = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/c.png")
image natsuki 1d = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/d.png")
image natsuki 1e = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/e.png")
image natsuki 1f = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/f.png")
image natsuki 1g = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/g.png")
image natsuki 1h = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/h.png")
image natsuki 1i = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/i.png")
image natsuki 1j = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/j.png")
image natsuki 1k = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/k.png")
image natsuki 1l = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/l.png")
image natsuki 1m = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/m.png")
image natsuki 1n = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/n.png")
image natsuki 1o = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/o.png")
image natsuki 1p = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/p.png")
image natsuki 1q = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/q.png")
image natsuki 1r = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/r.png")
image natsuki 1s = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/s.png")
image natsuki 1t = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/t.png")
image natsuki 1u = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/u.png")
image natsuki 1v = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/v.png")
image natsuki 1w = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/w.png")
image natsuki 1x = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/x.png")
image natsuki 1y = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/y.png")
image natsuki 1z = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/z.png")

image natsuki 21 = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/1t.png")
image natsuki 2a = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/a.png")
image natsuki 2b = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/b.png")
image natsuki 2c = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/c.png")
image natsuki 2d = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/d.png")
image natsuki 2e = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/e.png")
image natsuki 2f = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/f.png")
image natsuki 2g = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/g.png")
image natsuki 2h = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/h.png")
image natsuki 2i = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/i.png")
image natsuki 2j = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/j.png")
image natsuki 2k = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/k.png")
image natsuki 2l = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/l.png")
image natsuki 2m = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/m.png")
image natsuki 2n = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/n.png")
image natsuki 2o = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/o.png")
image natsuki 2p = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/p.png")
image natsuki 2q = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/q.png")
image natsuki 2r = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/r.png")
image natsuki 2s = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/s.png")
image natsuki 2t = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/t.png")
image natsuki 2u = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/u.png")
image natsuki 2v = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/v.png")
image natsuki 2w = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/w.png")
image natsuki 2x = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/x.png")
image natsuki 2y = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/y.png")
image natsuki 2z = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/z.png")

image natsuki 31 = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/1t.png")
image natsuki 3a = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/a.png")
image natsuki 3b = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/b.png")
image natsuki 3c = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/c.png")
image natsuki 3d = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/d.png")
image natsuki 3e = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/e.png")
image natsuki 3f = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/f.png")
image natsuki 3g = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/g.png")
image natsuki 3h = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/h.png")
image natsuki 3i = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/i.png")
image natsuki 3j = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/j.png")
image natsuki 3k = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/k.png")
image natsuki 3l = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/l.png")
image natsuki 3m = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/m.png")
image natsuki 3n = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/n.png")
image natsuki 3o = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/o.png")
image natsuki 3p = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/p.png")
image natsuki 3q = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/q.png")
image natsuki 3r = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/r.png")
image natsuki 3s = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/s.png")
image natsuki 3t = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/t.png")
image natsuki 3u = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/u.png")
image natsuki 3v = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/v.png")
image natsuki 3w = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/w.png")
image natsuki 3x = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/x.png")
image natsuki 3y = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/y.png")
image natsuki 3z = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/z.png")

image natsuki 41 = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/1t.png")
image natsuki 4a = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/a.png")
image natsuki 4b = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/b.png")
image natsuki 4c = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/c.png")
image natsuki 4d = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/d.png")
image natsuki 4e = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/e.png")
image natsuki 4f = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/f.png")
image natsuki 4g = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/g.png")
image natsuki 4h = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/h.png")
image natsuki 4i = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/i.png")
image natsuki 4j = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/j.png")
image natsuki 4k = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/k.png")
image natsuki 4l = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/l.png")
image natsuki 4m = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/m.png")
image natsuki 4n = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/n.png")
image natsuki 4o = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/o.png")
image natsuki 4p = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/p.png")
image natsuki 4q = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/q.png")
image natsuki 4r = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/r.png")
image natsuki 4s = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/s.png")
image natsuki 4t = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/t.png")
image natsuki 4u = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/u.png")
image natsuki 4v = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/v.png")
image natsuki 4w = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/w.png")
image natsuki 4x = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/x.png")
image natsuki 4y = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/y.png")
image natsuki 4z = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/z.png")

image natsuki 12 = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/2t.png")
image natsuki 12a = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/2ta.png")
image natsuki 12b = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/2tb.png")
image natsuki 12c = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/2tc.png")
image natsuki 12d = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/2td.png")
image natsuki 12e = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/2te.png")
image natsuki 12f = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/2tf.png")
image natsuki 12g = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/2tg.png")
image natsuki 12h = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/2th.png")
image natsuki 12i = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/2ti.png")

image natsuki 42 = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/2t.png")
image natsuki 42a = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/2ta.png")
image natsuki 42b = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/2tb.png")
image natsuki 42c = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/2tc.png")
image natsuki 42d = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/2td.png")
image natsuki 42e = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/2te.png")
image natsuki 42f = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/2tf.png")
image natsuki 42g = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/2tg.png")
image natsuki 42h = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/2th.png")
image natsuki 42i = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/2ti.png")

image natsuki 51 = im.Composite((960, 960), (18, 22), "natsuki/1t.png", (0, 0), "natsuki/3.png")
image natsuki 5a = im.Composite((960, 960), (18, 22), "natsuki/a.png", (0, 0), "natsuki/3.png")
image natsuki 5b = im.Composite((960, 960), (18, 22), "natsuki/b.png", (0, 0), "natsuki/3.png")
image natsuki 5c = im.Composite((960, 960), (18, 22), "natsuki/c.png", (0, 0), "natsuki/3.png")
image natsuki 5d = im.Composite((960, 960), (18, 22), "natsuki/d.png", (0, 0), "natsuki/3.png")
image natsuki 5e = im.Composite((960, 960), (18, 22), "natsuki/e.png", (0, 0), "natsuki/3.png")
image natsuki 5f = im.Composite((960, 960), (18, 22), "natsuki/f.png", (0, 0), "natsuki/3.png")
image natsuki 5g = im.Composite((960, 960), (18, 22), "natsuki/g.png", (0, 0), "natsuki/3.png")
image natsuki 5h = im.Composite((960, 960), (18, 22), "natsuki/h.png", (0, 0), "natsuki/3.png")
image natsuki 5i = im.Composite((960, 960), (18, 22), "natsuki/i.png", (0, 0), "natsuki/3.png")
image natsuki 5j = im.Composite((960, 960), (18, 22), "natsuki/j.png", (0, 0), "natsuki/3.png")
image natsuki 5k = im.Composite((960, 960), (18, 22), "natsuki/k.png", (0, 0), "natsuki/3.png")
image natsuki 5l = im.Composite((960, 960), (18, 22), "natsuki/l.png", (0, 0), "natsuki/3.png")
image natsuki 5m = im.Composite((960, 960), (18, 22), "natsuki/m.png", (0, 0), "natsuki/3.png")
image natsuki 5n = im.Composite((960, 960), (18, 22), "natsuki/n.png", (0, 0), "natsuki/3.png")
image natsuki 5o = im.Composite((960, 960), (18, 22), "natsuki/o.png", (0, 0), "natsuki/3.png")
image natsuki 5p = im.Composite((960, 960), (18, 22), "natsuki/p.png", (0, 0), "natsuki/3.png")
image natsuki 5q = im.Composite((960, 960), (18, 22), "natsuki/q.png", (0, 0), "natsuki/3.png")
image natsuki 5r = im.Composite((960, 960), (18, 22), "natsuki/r.png", (0, 0), "natsuki/3.png")
image natsuki 5s = im.Composite((960, 960), (18, 22), "natsuki/s.png", (0, 0), "natsuki/3.png")
image natsuki 5t = im.Composite((960, 960), (18, 22), "natsuki/t.png", (0, 0), "natsuki/3.png")
image natsuki 5u = im.Composite((960, 960), (18, 22), "natsuki/u.png", (0, 0), "natsuki/3.png")
image natsuki 5v = im.Composite((960, 960), (18, 22), "natsuki/v.png", (0, 0), "natsuki/3.png")
image natsuki 5w = im.Composite((960, 960), (18, 22), "natsuki/w.png", (0, 0), "natsuki/3.png")
image natsuki 5x = im.Composite((960, 960), (18, 22), "natsuki/x.png", (0, 0), "natsuki/3.png")
image natsuki 5y = im.Composite((960, 960), (18, 22), "natsuki/y.png", (0, 0), "natsuki/3.png")
image natsuki 5z = im.Composite((960, 960), (18, 22), "natsuki/z.png", (0, 0), "natsuki/3.png")
#image natsuki 52 = im.Composite((960, 960), (0, 0), "natsuki/3.png", (0, 0), "natsuki/4t.png")


image natsuki 1ba = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/a.png")
image natsuki 1bb = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/b.png")
image natsuki 1bc = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/c.png")
image natsuki 1bd = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/d.png")
image natsuki 1be = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/e.png")
image natsuki 1bf = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/f.png")
image natsuki 1bg = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/g.png")
image natsuki 1bh = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/h.png")
image natsuki 1bi = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/i.png")
image natsuki 1bj = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/j.png")
image natsuki 1bk = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/k.png")
image natsuki 1bl = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/l.png")
image natsuki 1bm = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/m.png")
image natsuki 1bn = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/n.png")
image natsuki 1bo = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/o.png")
image natsuki 1bp = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/p.png")
image natsuki 1bq = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/q.png")
image natsuki 1br = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/r.png")
image natsuki 1bs = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/s.png")
image natsuki 1bt = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/t.png")
image natsuki 1bu = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/u.png")
image natsuki 1bv = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/v.png")
image natsuki 1bw = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/w.png")
image natsuki 1bx = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/x.png")
image natsuki 1by = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/y.png")
image natsuki 1bz = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/z.png")

image natsuki 2ba = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/a.png")
image natsuki 2bb = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/b.png")
image natsuki 2bc = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/c.png")
image natsuki 2bd = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/d.png")
image natsuki 2be = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/e.png")
image natsuki 2bf = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/f.png")
image natsuki 2bg = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/g.png")
image natsuki 2bh = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/h.png")
image natsuki 2bi = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/i.png")
image natsuki 2bj = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/j.png")
image natsuki 2bk = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/k.png")
image natsuki 2bl = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/l.png")
image natsuki 2bm = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/m.png")
image natsuki 2bn = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/n.png")
image natsuki 2bo = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/o.png")
image natsuki 2bp = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/p.png")
image natsuki 2bq = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/q.png")
image natsuki 2br = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/r.png")
image natsuki 2bs = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/s.png")
image natsuki 2bt = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/t.png")
image natsuki 2bu = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/u.png")
image natsuki 2bv = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/v.png")
image natsuki 2bw = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/w.png")
image natsuki 2bx = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/x.png")
image natsuki 2by = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/y.png")
image natsuki 2bz = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/z.png")

image natsuki 3ba = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/a.png")
image natsuki 3bb = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/b.png")
image natsuki 3bc = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/c.png")
image natsuki 3bd = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/d.png")
image natsuki 3be = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/e.png")
image natsuki 3bf = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/f.png")
image natsuki 3bg = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/g.png")
image natsuki 3bh = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/h.png")
image natsuki 3bi = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/i.png")
image natsuki 3bj = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/j.png")
image natsuki 3bk = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/k.png")
image natsuki 3bl = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/l.png")
image natsuki 3bm = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/m.png")
image natsuki 3bn = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/n.png")
image natsuki 3bo = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/o.png")
image natsuki 3bp = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/p.png")
image natsuki 3bq = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/q.png")
image natsuki 3br = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/r.png")
image natsuki 3bs = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/s.png")
image natsuki 3bt = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/t.png")
image natsuki 3bu = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/u.png")
image natsuki 3bv = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/v.png")
image natsuki 3bw = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/w.png")
image natsuki 3bx = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/x.png")
image natsuki 3by = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/y.png")
image natsuki 3bz = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/z.png")

image natsuki 4ba = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/a.png")
image natsuki 4bb = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/b.png")
image natsuki 4bc = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/c.png")
image natsuki 4bd = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/d.png")
image natsuki 4be = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/e.png")
image natsuki 4bf = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/f.png")
image natsuki 4bg = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/g.png")
image natsuki 4bh = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/h.png")
image natsuki 4bi = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/i.png")
image natsuki 4bj = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/j.png")
image natsuki 4bk = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/k.png")
image natsuki 4bl = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/l.png")
image natsuki 4bm = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/m.png")
image natsuki 4bn = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/n.png")
image natsuki 4bo = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/o.png")
image natsuki 4bp = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/p.png")
image natsuki 4bq = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/q.png")
image natsuki 4br = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/r.png")
image natsuki 4bs = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/s.png")
image natsuki 4bt = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/t.png")
image natsuki 4bu = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/u.png")
image natsuki 4bv = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/v.png")
image natsuki 4bw = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/w.png")
image natsuki 4bx = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/x.png")
image natsuki 4by = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/y.png")
image natsuki 4bz = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/z.png")

image natsuki 12ba = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/2bta.png")
image natsuki 12bb = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/2btb.png")
image natsuki 12bc = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/2btc.png")
image natsuki 12bd = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/2btd.png")
image natsuki 12be = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/2bte.png")
image natsuki 12bf = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/2btf.png")
image natsuki 12bg = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/2btg.png")
image natsuki 12bh = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/2bth.png")
image natsuki 12bi = im.Composite((960, 960), (0, 0), "natsuki/1bl.png", (0, 0), "natsuki/1br.png", (0, 0), "natsuki/2bti.png")

image natsuki 42ba = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/2bta.png")
image natsuki 42bb = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/2btb.png")
image natsuki 42bc = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/2btc.png")
image natsuki 42bd = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/2btd.png")
image natsuki 42be = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/2bte.png")
image natsuki 42bf = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/2btf.png")
image natsuki 42bg = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/2btg.png")
image natsuki 42bh = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/2bth.png")
image natsuki 42bi = im.Composite((960, 960), (0, 0), "natsuki/2bl.png", (0, 0), "natsuki/2br.png", (0, 0), "natsuki/2bti.png")

image natsuki 5ba = im.Composite((960, 960), (18, 22), "natsuki/a.png", (0, 0), "natsuki/3b.png")
image natsuki 5bb = im.Composite((960, 960), (18, 22), "natsuki/b.png", (0, 0), "natsuki/3b.png")
image natsuki 5bc = im.Composite((960, 960), (18, 22), "natsuki/c.png", (0, 0), "natsuki/3b.png")
image natsuki 5bd = im.Composite((960, 960), (18, 22), "natsuki/d.png", (0, 0), "natsuki/3b.png")
image natsuki 5be = im.Composite((960, 960), (18, 22), "natsuki/e.png", (0, 0), "natsuki/3b.png")
image natsuki 5bf = im.Composite((960, 960), (18, 22), "natsuki/f.png", (0, 0), "natsuki/3b.png")
image natsuki 5bg = im.Composite((960, 960), (18, 22), "natsuki/g.png", (0, 0), "natsuki/3b.png")
image natsuki 5bh = im.Composite((960, 960), (18, 22), "natsuki/h.png", (0, 0), "natsuki/3b.png")
image natsuki 5bi = im.Composite((960, 960), (18, 22), "natsuki/i.png", (0, 0), "natsuki/3b.png")
image natsuki 5bj = im.Composite((960, 960), (18, 22), "natsuki/j.png", (0, 0), "natsuki/3b.png")
image natsuki 5bk = im.Composite((960, 960), (18, 22), "natsuki/k.png", (0, 0), "natsuki/3b.png")
image natsuki 5bl = im.Composite((960, 960), (18, 22), "natsuki/l.png", (0, 0), "natsuki/3b.png")
image natsuki 5bm = im.Composite((960, 960), (18, 22), "natsuki/m.png", (0, 0), "natsuki/3b.png")
image natsuki 5bn = im.Composite((960, 960), (18, 22), "natsuki/n.png", (0, 0), "natsuki/3b.png")
image natsuki 5bo = im.Composite((960, 960), (18, 22), "natsuki/o.png", (0, 0), "natsuki/3b.png")
image natsuki 5bp = im.Composite((960, 960), (18, 22), "natsuki/p.png", (0, 0), "natsuki/3b.png")
image natsuki 5bq = im.Composite((960, 960), (18, 22), "natsuki/q.png", (0, 0), "natsuki/3b.png")
image natsuki 5br = im.Composite((960, 960), (18, 22), "natsuki/r.png", (0, 0), "natsuki/3b.png")
image natsuki 5bs = im.Composite((960, 960), (18, 22), "natsuki/s.png", (0, 0), "natsuki/3b.png")
image natsuki 5bt = im.Composite((960, 960), (18, 22), "natsuki/t.png", (0, 0), "natsuki/3b.png")
image natsuki 5bu = im.Composite((960, 960), (18, 22), "natsuki/u.png", (0, 0), "natsuki/3b.png")
image natsuki 5bv = im.Composite((960, 960), (18, 22), "natsuki/v.png", (0, 0), "natsuki/3b.png")
image natsuki 5bw = im.Composite((960, 960), (18, 22), "natsuki/w.png", (0, 0), "natsuki/3b.png")
image natsuki 5bx = im.Composite((960, 960), (18, 22), "natsuki/x.png", (0, 0), "natsuki/3b.png")
image natsuki 5by = im.Composite((960, 960), (18, 22), "natsuki/y.png", (0, 0), "natsuki/3b.png")
image natsuki 5bz = im.Composite((960, 960), (18, 22), "natsuki/z.png", (0, 0), "natsuki/3b.png")

# Natsuki legacy
image natsuki 1 = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/1t.png")
image natsuki 2 = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/1t.png")
image natsuki 3 = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/1t.png")
image natsuki 4 = im.Composite((960, 960), (0, 0), "natsuki/2l.png", (0, 0), "natsuki/2r.png", (0, 0), "natsuki/1t.png")
image natsuki 5 = im.Composite((960, 960), (18, 22), "natsuki/1t.png", (0, 0), "natsuki/3.png")

image natsuki mouth = LiveComposite((960, 960), (0, 0), "natsuki/0.png", (390, 340), "n_rects_mouth", (480, 334), "n_rects_mouth")

image n_rects_mouth:
    RectCluster(Solid("#000"), 4, 15, 5).sm
    size (20, 25)

image n_moving_mouth:
    "images/natsuki/mouth.png"
    pos (615, 305)
    xanchor 0.5 yanchor 0.5
    parallel:
        choice:
            ease 0.10 yzoom 0.2
        choice:
            ease 0.05 yzoom 0.2
        choice:
            ease 0.075 yzoom 0.2
        pass
        choice:
            0.02
        choice:
            0.04
        choice:
            0.06
        choice:
            0.08
        pass
        choice:
            ease 0.10 yzoom 1
        choice:
            ease 0.05 yzoom 1
        choice:
            ease 0.075 yzoom 1
        pass
        choice:
            0.02
        choice:
            0.04
        choice:
            0.06
        choice:
            0.08
        repeat
    parallel:
        choice:
            0.2
        choice:
            0.4
        choice:
            0.6
        ease 0.2 xzoom 0.4
        ease 0.2 xzoom 0.8
        repeat

image natsuki_ghost_blood:
    "#00000000"
    "natsuki/ghost_blood.png" with ImageDissolve("images/menu/wipedown.png", 80.0, ramplen=4, alpha=True)
    pos (620,320) zoom 0.80

image natsuki ghost_base:
    "natsuki/ghost1.png"
image natsuki ghost1:
    "natsuki 11"
    "natsuki ghost_base" with Dissolve(20.0, alpha=True)
image natsuki ghost2 = Image("natsuki/ghost2.png")
image natsuki ghost3 = Image("natsuki/ghost3.png")
image natsuki ghost4:
    "natsuki ghost3"
    parallel:
        easeout 0.25 zoom 4.5 yoffset 1200
    parallel:
        ease 0.025 xoffset -20
        ease 0.025 xoffset 20
        repeat
    0.25
    "black"
image natsuki glitch1:
    "natsuki/glitch1.png"
    zoom 1.25
    block:
        yoffset 300 xoffset 100 ytile 2
        linear 0.15 yoffset 200
        repeat
    time 0.75
    yoffset 0 zoom 1 xoffset 0 ytile 1
    "natsuki 4e"

image natsuki scream = im.Composite((960, 960), (0, 0), "natsuki/1l.png", (0, 0), "natsuki/1r.png", (0, 0), "natsuki/scream.png")
image natsuki vomit = "natsuki/vomit.png"

image n_blackeyes = "images/natsuki/blackeyes.png"
image n_eye = "images/natsuki/eye.png"

# Yuri
image yuri 1 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/a.png")
image yuri 2 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/a.png")
image yuri 3 = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/a.png")
image yuri 4 = im.Composite((960, 960), (0, 0), "yuri/3.png", (0, 0), "yuri/a2.png")

image yuri 1a = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/a.png")
image yuri 1b = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/b.png")
image yuri 1c = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/c.png")
image yuri 1d = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/d.png")
image yuri 1e = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/e.png")
image yuri 1f = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/f.png")
image yuri 1g = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/g.png")
image yuri 1h = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/h.png")
image yuri 1i = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/i.png")
image yuri 1j = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/j.png")
image yuri 1k = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/k.png")
image yuri 1l = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/l.png")
image yuri 1m = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/m.png")
image yuri 1n = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/n.png")
image yuri 1o = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/o.png")
image yuri 1p = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/p.png")
image yuri 1q = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/q.png")
image yuri 1r = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/r.png")
image yuri 1s = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/s.png")
image yuri 1t = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/t.png")
image yuri 1u = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/u.png")
image yuri 1v = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/v.png")
image yuri 1w = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/w.png")

image yuri 1y1 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/y1.png")
image yuri 1y2 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/y2.png")
image yuri 1y3 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/y3.png")
image yuri 1y4 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/y4.png")
image yuri 1y5 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/y5.png")
image yuri 1y6 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/y6.png")
image yuri 1y7 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/y7.png")

image yuri 2a = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/a.png")
image yuri 2b = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/b.png")
image yuri 2c = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/c.png")
image yuri 2d = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/d.png")
image yuri 2e = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/e.png")
image yuri 2f = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/f.png")
image yuri 2g = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/g.png")
image yuri 2h = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/h.png")
image yuri 2i = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/i.png")
image yuri 2j = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/j.png")
image yuri 2k = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/k.png")
image yuri 2l = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/l.png")
image yuri 2m = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/m.png")
image yuri 2n = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/n.png")
image yuri 2o = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/o.png")
image yuri 2p = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/p.png")
image yuri 2q = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/q.png")
image yuri 2r = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/r.png")
image yuri 2s = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/s.png")
image yuri 2t = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/t.png")
image yuri 2u = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/u.png")
image yuri 2v = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/v.png")
image yuri 2w = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/w.png")

image yuri 2y1 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y1.png")
image yuri 2y2 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y2.png")
image yuri 2y3 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y3.png")
image yuri 2y4 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y4.png")
image yuri 2y5 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y5.png")
image yuri 2y6 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y6.png")
image yuri 2y7 = im.Composite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y7.png")

image yuri 3a = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/a.png")
image yuri 3b = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/b.png")
image yuri 3c = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/c.png")
image yuri 3d = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/d.png")
image yuri 3e = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/e.png")
image yuri 3f = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/f.png")
image yuri 3g = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/g.png")
image yuri 3h = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/h.png")
image yuri 3i = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/i.png")
image yuri 3j = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/j.png")
image yuri 3k = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/k.png")
image yuri 3l = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/l.png")
image yuri 3m = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/m.png")
image yuri 3n = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/n.png")
image yuri 3o = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/o.png")
image yuri 3p = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/p.png")
image yuri 3q = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/q.png")
image yuri 3r = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/r.png")
image yuri 3s = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/s.png")
image yuri 3t = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/t.png")
image yuri 3u = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/u.png")
image yuri 3v = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/v.png")
image yuri 3w = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/w.png")

image yuri 3y1 = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y1.png")
image yuri 3y2 = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y2.png")
image yuri 3y3 = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y3.png")
image yuri 3y4 = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y4.png")
image yuri 3y5 = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y5.png")
image yuri 3y6 = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y6.png")
image yuri 3y7 = im.Composite((960, 960), (0, 0), "yuri/2l.png", (0, 0), "yuri/2r.png", (0, 0), "yuri/y7.png")

image yuri 4a = im.Composite((960, 960), (0, 0), "yuri/3.png", (0, 0), "yuri/a2.png")
image yuri 4b = im.Composite((960, 960), (0, 0), "yuri/3.png", (0, 0), "yuri/b2.png")
image yuri 4c = im.Composite((960, 960), (0, 0), "yuri/3.png", (0, 0), "yuri/c2.png")
image yuri 4d = im.Composite((960, 960), (0, 0), "yuri/3.png", (0, 0), "yuri/d2.png")
image yuri 4e = im.Composite((960, 960), (0, 0), "yuri/3.png", (0, 0), "yuri/e2.png")

image yuri 1ba = im.Composite((960, 960), (0, 0), "yuri/a.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bb = im.Composite((960, 960), (0, 0), "yuri/b.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bc = im.Composite((960, 960), (0, 0), "yuri/c.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bd = im.Composite((960, 960), (0, 0), "yuri/d.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1be = im.Composite((960, 960), (0, 0), "yuri/e.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bf = im.Composite((960, 960), (0, 0), "yuri/f.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bg = im.Composite((960, 960), (0, 0), "yuri/g.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bh = im.Composite((960, 960), (0, 0), "yuri/h.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bi = im.Composite((960, 960), (0, 0), "yuri/i.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bj = im.Composite((960, 960), (0, 0), "yuri/j.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bk = im.Composite((960, 960), (0, 0), "yuri/k.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bl = im.Composite((960, 960), (0, 0), "yuri/l.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bm = im.Composite((960, 960), (0, 0), "yuri/m.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bn = im.Composite((960, 960), (0, 0), "yuri/n.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bo = im.Composite((960, 960), (0, 0), "yuri/o.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bp = im.Composite((960, 960), (0, 0), "yuri/p.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bq = im.Composite((960, 960), (0, 0), "yuri/q.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1br = im.Composite((960, 960), (0, 0), "yuri/r.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bs = im.Composite((960, 960), (0, 0), "yuri/s.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bt = im.Composite((960, 960), (0, 0), "yuri/t.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bu = im.Composite((960, 960), (0, 0), "yuri/u.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bv = im.Composite((960, 960), (0, 0), "yuri/v.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")
image yuri 1bw = im.Composite((960, 960), (0, 0), "yuri/w.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/1br.png")

image yuri 2ba = im.Composite((960, 960), (0, 0), "yuri/a.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bb = im.Composite((960, 960), (0, 0), "yuri/b.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bc = im.Composite((960, 960), (0, 0), "yuri/c.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bd = im.Composite((960, 960), (0, 0), "yuri/d.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2be = im.Composite((960, 960), (0, 0), "yuri/e.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bf = im.Composite((960, 960), (0, 0), "yuri/f.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bg = im.Composite((960, 960), (0, 0), "yuri/g.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bh = im.Composite((960, 960), (0, 0), "yuri/h.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bi = im.Composite((960, 960), (0, 0), "yuri/i.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bj = im.Composite((960, 960), (0, 0), "yuri/j.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bk = im.Composite((960, 960), (0, 0), "yuri/k.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bl = im.Composite((960, 960), (0, 0), "yuri/l.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bm = im.Composite((960, 960), (0, 0), "yuri/m.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bn = im.Composite((960, 960), (0, 0), "yuri/n.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bo = im.Composite((960, 960), (0, 0), "yuri/o.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bp = im.Composite((960, 960), (0, 0), "yuri/p.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bq = im.Composite((960, 960), (0, 0), "yuri/q.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2br = im.Composite((960, 960), (0, 0), "yuri/r.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bs = im.Composite((960, 960), (0, 0), "yuri/s.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bt = im.Composite((960, 960), (0, 0), "yuri/t.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bu = im.Composite((960, 960), (0, 0), "yuri/u.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bv = im.Composite((960, 960), (0, 0), "yuri/v.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")
image yuri 2bw = im.Composite((960, 960), (0, 0), "yuri/w.png", (0, 0), "yuri/1bl.png", (0, 0), "yuri/2br.png")

image yuri 3ba = im.Composite((960, 960), (0, 0), "yuri/a.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bb = im.Composite((960, 960), (0, 0), "yuri/b.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bc = im.Composite((960, 960), (0, 0), "yuri/c.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bd = im.Composite((960, 960), (0, 0), "yuri/d.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3be = im.Composite((960, 960), (0, 0), "yuri/e.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bf = im.Composite((960, 960), (0, 0), "yuri/f.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bg = im.Composite((960, 960), (0, 0), "yuri/g.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bh = im.Composite((960, 960), (0, 0), "yuri/h.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bi = im.Composite((960, 960), (0, 0), "yuri/i.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bj = im.Composite((960, 960), (0, 0), "yuri/j.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bk = im.Composite((960, 960), (0, 0), "yuri/k.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bl = im.Composite((960, 960), (0, 0), "yuri/l.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bm = im.Composite((960, 960), (0, 0), "yuri/m.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bn = im.Composite((960, 960), (0, 0), "yuri/n.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bo = im.Composite((960, 960), (0, 0), "yuri/o.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bp = im.Composite((960, 960), (0, 0), "yuri/p.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bq = im.Composite((960, 960), (0, 0), "yuri/q.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3br = im.Composite((960, 960), (0, 0), "yuri/r.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bs = im.Composite((960, 960), (0, 0), "yuri/s.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bt = im.Composite((960, 960), (0, 0), "yuri/t.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bu = im.Composite((960, 960), (0, 0), "yuri/u.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bv = im.Composite((960, 960), (0, 0), "yuri/v.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")
image yuri 3bw = im.Composite((960, 960), (0, 0), "yuri/w.png", (0, 0), "yuri/2bl.png", (0, 0), "yuri/2br.png")

image yuri 4ba = im.Composite((960, 960), (0, 0), "yuri/a2.png", (0, 0), "yuri/3b.png")
image yuri 4bb = im.Composite((960, 960), (0, 0), "yuri/b2.png", (0, 0), "yuri/3b.png")
image yuri 4bc = im.Composite((960, 960), (0, 0), "yuri/c2.png", (0, 0), "yuri/3b.png")
image yuri 4bd = im.Composite((960, 960), (0, 0), "yuri/d2.png", (0, 0), "yuri/3b.png")
image yuri 4be = im.Composite((960, 960), (0, 0), "yuri/e2.png", (0, 0), "yuri/3b.png")

image y_glitch_head:
    "images/yuri/za.png"
    0.15
    "images/yuri/zb.png"
    0.15
    "images/yuri/zc.png"
    0.15
    "images/yuri/zd.png"
    0.15
    repeat

image yuri stab_1 = "yuri/stab/1.png"
image yuri stab_2 = "yuri/stab/2.png"
image yuri stab_3 = "yuri/stab/3.png"
image yuri stab_4 = "yuri/stab/4.png"
image yuri stab_5 = "yuri/stab/5.png"
image yuri stab_6 = LiveComposite((960,960), (0, 0), "yuri/stab/6-mask.png", (0, 0), "yuri stab_6_eyes", (0, 0), "yuri/stab/6.png")

image yuri stab_6_eyes:
    "yuri/stab/6-eyes.png"
    subpixel True
    parallel:
        choice:
            xoffset 0.5
        choice:
            xoffset 0
        choice:
            xoffset -0.5
        0.2
        repeat
    parallel:
        choice:
            yoffset 0.5
        choice:
            yoffset 0
        choice:
            yoffset -0.5
        0.2
        repeat
    parallel:
        2.05
        easeout 1.0 yoffset -15
        linear 10 yoffset -15


image yuri oneeye = LiveComposite((960, 960), (0, 0), "yuri/1l.png", (0, 0), "yuri/1r.png", (0, 0), "yuri/oneeye.png", (0, 0), "yuri oneeye2")
image yuri oneeye2:
    "yuri/oneeye2.png"
    subpixel True
    pause 5.0
    linear 60 xoffset -50 yoffset 20

image yuri glitch:
    "yuri/glitch1.png"
    pause 0.1
    "yuri/glitch2.png"
    pause 0.1
    "yuri/glitch3.png"
    pause 0.1
    "yuri/glitch4.png"
    pause 0.1
    "yuri/glitch5.png"
    pause 0.1
    repeat
image yuri glitch2:
    "yuri/0a.png"
    pause 0.1
    "yuri/0b.png"
    pause 0.5
    "yuri/0a.png"
    pause 0.3
    "yuri/0b.png"
    pause 0.3
    "yuri 1"

image yuri eyes = LiveComposite((1280, 720), (0, 0), "yuri/eyes1.png", (0, 0), "yuripupils")

image yuri eyes_base = "yuri/eyes1.png"

image yuripupils:
    "yuri/eyes2.png"
    yuripupils_move

image yuri cuts = "yuri/cuts.png"

image yuri dragon:
    "yuri 3"
    0.25
    parallel:
        "yuri/dragon1.png"
        0.01
        "yuri/dragon2.png"
        0.01
        repeat
    parallel:
        0.01
        choice:
            xoffset -1
            xoffset -2
            xoffset -5
            xoffset -6
            xoffset -9
            xoffset -10
        0.01
        xoffset 0
        repeat
    time 0.55
    xoffset 0
    "yuri 3"

# Character variables
define narrator = Character(ctc="ctc", ctc_position="fixed")
define mc = DynamicCharacter('player', what_prefix='"', what_suffix='"', ctc="ctc", ctc_position="fixed")
define s = DynamicCharacter('s_name', image='sayori', what_prefix='"', what_suffix='"', ctc="ctc", ctc_position="fixed")
define n = DynamicCharacter('n_name', image='natsuki', what_prefix='"', what_suffix='"', ctc="ctc", ctc_position="fixed")
define y = DynamicCharacter('y_name', image='yuri', what_prefix='"', what_suffix='"', ctc="ctc", ctc_position="fixed")
define ny = Character('Nat & Yuri', what_prefix='"', what_suffix='"', ctc="ctc", ctc_position="fixed")

define _dismiss_pause = config.developer

default persistent.playername = ""
default player = persistent.playername

## NOTE: name changing moved to script-ch30 because of currentuser

default persistent.playthrough = 0
default persistent.yuri_kill = 0
default persistent.seen_eyes = None
default persistent.seen_sticker = None
default persistent.ghost_menu = None
default persistent.seen_ghost_menu = None
default seen_eyes_this_chapter = False
default persistent.anticheat = 0
default persistent.clear = [False, False, False, False, False, False, False, False, False, False]
default persistent.special_poems = None
default persistent.clearall = None
default persistent.menu_bg_m = None
default persistent.first_load = None
default persistent.has_merged = False
default persistent._mas_monika_nickname = "Monika"
default in_sayori_kill = None
default in_yuri_kill = None
default anticheat = 0
define config.mouse = None
default allow_skipping = True
default basedir = config.basedir
default chapter = 0
default currentpos = 0
default faint_effect = None


default s_name = "Sayori"
default m_name = persistent._mas_monika_nickname
default n_name = "Natsuki"
default y_name = "Yuri"

# Instantiating variables for poem appeal. This is how much each character likes the poem for each day.
# -1 = Dislike, 0 = Neutral, 1 = Like
default n_poemappeal = [0, 0, 0]
default s_poemappeal = [0, 0, 0]
default y_poemappeal = [0, 0, 0]
default m_poemappeal = [0, 0, 0]

# The last winner of the poem minigame.
default poemwinner = ['sayori', 'sayori', 'sayori']

# Keeping track of who read your poem when you're showing it to each of the girls.
default s_readpoem = False
default n_readpoem = False
default y_readpoem = False
default m_readpoem = False

# Used in poemresponse_start because it's easier than checking true/false on everyone's read state.
default poemsread = 0

# The main appeal points. Whoever likes your poem the most gets an appeal point for that chapter.
# Appeal points are used to keep track of which exclusive scene to show each chapter.
default n_appeal = 0
default s_appeal = 0
default y_appeal = 0
default m_appeal = 0

# We keep track of whether we watched Natsuki's and sayori's second exclusive scenes
# to decide whether to play them in chapter 3.
default n_exclusivewatched = False
default y_exclusivewatched = False

# Yuri runs away after the first exclusive scene of playthrough 2.
default y_gave = False
default y_ranaway = False

# We choose who to side with in chapter 1.
default ch1_choice = "sayori"

# If we choose to help Sayori in ch3, some of the dialogue changes.
default help_sayori = None
default help_monika = None

# We choose who to spend time with in chapter 4.
default ch4_scene = "yuri"
default ch4_name = "Yuri"
default sayori_confess = True

# We read Natsuki's confession poem in chapter 23.
default natsuki_23 = None

#Mod-specific
default persistent.monika_topic = ""
default player_dialogue = persistent.monika_topic
default persistent.monika_said_topics = []
default persistent.event_list = []
default persistent.event_database = dict()
default persistent.farewell_database = dict()
default persistent.greeting_database = dict()
default persistent._mas_apology_database = dict()
default persistent._mas_undo_action_rules = dict()
default persistent._mas_strip_dates_rules = dict()
default persistent.gender = "M" #Assume gender matches the PC
default persistent.closed_self = False
default persistent._mas_game_crashed = False
default persistent.seen_monika_in_room = False
default persistent.ever_won = {'pong':False,'chess':False,'hangman':False,'piano':False}
default persistent.sessions={'last_session_end':None,'current_session_start':None,'total_playtime':datetime.timedelta(seconds=0),'total_sessions':0,'first_session':datetime.datetime.now()}
default persistent.random_seen = 0
default persistent._mas_affection = {"affection":0,"goodexp":1,"badexp":1,"apologyflag":False, "freeze_date": None, "today_exp":0}
default persistent._mas_enable_random_repeats = True
#default persistent._mas_monika_repeated_herself = False
default persistent._mas_first_calendar_check = False

#Var to see if we were on a long absence (post flag reset)
default mas_ret_long_absence = False

# rain
define mas_is_raining = False

# rain chances
define MAS_RAIN_UPSET = 25
define MAS_RAIN_DIS = 40
define MAS_RAIN_BROKEN = 70

# snow
define mas_is_snowing = False

# True if the current background is an indoors one
define mas_is_indoors = True

# idle
default persistent._mas_in_idle_mode = False
default persistent._mas_idle_data = {}

# music
#default persistent.current_track = renpy.store.songs.FP_JUST_MONIKA

# clothes
default persistent._mas_monika_clothes = "def"
default persistent._mas_monika_hair = "def"
default persistent._mas_likes_hairdown = False
default persistent._mas_hair_changed = False

# times
# they are stored in minutes so we can use bar nicely
default persistent._mas_sunrise = 6 * 60
default persistent._mas_sunset = 18 * 60

# 24 * 60 minutes, divided into chunks of 5
define mas_max_suntime = int((24 * 60) / 5) - 1
define mas_sunrise_prev = persistent._mas_sunrise
define mas_sunset_prev = persistent._mas_sunset
define mas_suntime.NO_CHANGE = 0
define mas_suntime.RISE_CHANGE = 1
define mas_suntime.SET_CHANGE = 2
define mas_suntime.change_state = mas_suntime.NO_CHANGE
define mas_suntime.modifier = 5 # modifier for chunking the time

# these 2 are our internal represenations of the suntimes in 5 minute
# chunks
define mas_suntime.sunrise = int(persistent._mas_sunrise / 5)
define mas_suntime.sunset = int(persistent._mas_sunset / 5)

define mas_checked_update = False
#define mas_monika_repeated = False
define random_seen_limit = 30
define times.REST_TIME = 6*3600
define times.FULL_XP_AWAY_TIME = 24*3600
define times.HALF_XP_AWAY_TIME = 72*3600

define mas_skip_visuals = False # renaming the variable since it's no longer limited to room greeting
define skip_setting_weather = False# in case of crashes/reloads, predefine it here

define mas_monika_twitter_handle = "lilmonix3"

# sensitive mode enabler
default persistent._mas_sensitive_mode = False

#Amount of times player has reloaded in ddlc
default persistent._mas_ddlc_reload_count = 0

define startup_check = False

# define temp zoom to default level in case of crash
define mas_temp_zoom_level = store.mas_sprites.default_zoom_level

define his = "his"
define he = "he"
define hes = "he's"
define heis = "he is"
define bf = "boyfriend"
define man = "man"
define boy = "boy"
define guy = "guy"
define him = "him"
define himself = "himself"

# Input characters filters
define numbers_only = "0123456789"
define lower_letters_only = " abcdefghijklmnopqrstuvwxyz"
define letters_only = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
define name_characters_only = " abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_'"

#Default is NORMAL
default persistent._mas_randchat_freq = mas_randchat.NORMAL
define mas_randchat_prev = persistent._mas_randchat_freq
init -1 python in mas_randchat:
    import store
    ### random chatter frequencies

    #Name - value constants
    VERY_OFTEN = 6
    OFTEN = 5
    NORMAL = 4
    LESS_OFTEN = 3
    OCCASIONALLY = 2
    RARELY = 1
    NEVER = 0

    # these numbers are the lower end of how many seconds to wait between random topics
    VERY_OFTEN_WAIT = 5 # end 15
    OFTEN_WAIT = 15 # end 45
    NORMAL_WAIT = 40 # end 120 (2 min)
    LESS_OFTEN_WAIT = 2*60 # end 360 (6 min)
    OCCASIONALLY_WAIT = 390 # end 1170 (19.5 min)
    RARELY_WAIT = 20*60 # end 3600 (60 mins)
    NEVER_WAIT = 0

    # this is multiplied to the low end to get the upper end of seconds
    SPAN_MULTIPLIER = 3

    ## to better work with the sliders, we will create a range from 0 to 6
    # (inclusive)
    # these values will be utilized in script-ch30 as well as screens
    SLIDER_MAP = {
        NEVER: NEVER_WAIT,
        RARELY: RARELY_WAIT,
        OCCASIONALLY: OCCASIONALLY_WAIT,
        LESS_OFTEN: LESS_OFTEN_WAIT,
        NORMAL: NORMAL_WAIT,
        OFTEN: OFTEN_WAIT,
        VERY_OFTEN: VERY_OFTEN_WAIT
    }

    ## slider map for displaying
    SLIDER_MAP_DISP = {
        NEVER: "Never",
        RARELY: "Rarely",
        OCCASIONALLY: "Occasionally",
        LESS_OFTEN: "Less Often",
        NORMAL: "Normal",
        OFTEN: "Often",
        VERY_OFTEN: "Very Often"
    }

    # current frequency times
    # also default to NORMAL, will get recaluated in reset
    rand_low = NORMAL
    rand_high = NORMAL * SPAN_MULTIPLIER
    rand_chat_waittime_left = 0

    def reduceRandchatForAff(aff_level):
        """
        Reduces the randchat setting if we're too high for the current affection level
        """
        max_setting_for_level = store.mas_affection.RANDCHAT_RANGE_MAP[aff_level]

        if store.persistent._mas_randchat_freq > max_setting_for_level:
            adjustRandFreq(max_setting_for_level)

    def adjustRandFreq(slider_value):
        """
        Properly adjusts the random limits given the slider value

        IN:
            slider_value - slider value given from the slider
                Should be between 0 - 6
        """
        slider_setting = SLIDER_MAP.get(slider_value, 4)

        # otherwise set up the times
        # globalize
        global rand_low
        global rand_high

        rand_low = slider_setting
        rand_high = slider_setting * SPAN_MULTIPLIER
        store.persistent._mas_randchat_freq = slider_value

        setWaitingTime()


    def getRandChatDisp(slider_value):
        """
        Retrieves the random chatter display string using the given slider
        value

        IN:
            slider_value - slider value given from the slider

        RETURNS:
            displayable string that reprsents the current random chatter
            setting
        """
        randchat_disp = SLIDER_MAP_DISP.get(slider_value, None)

        if slider_value is None:
            return "Never"

        return randchat_disp


    def setWaitingTime():
        """
        Sets up the waiting time for the next random chat, depending on the current random chatter selection.
        """
        global rand_chat_waittime_left

        rand_chat_waittime_left = renpy.random.randint(rand_low, rand_high)


    def wait():
        """
        Pauses renpy for a small amount of seconds.
        This helps adapting fast to a new random chatter selection.
        All events before a random chat can also be handled rather than to keep waiting the whole time at once.
        """
        global rand_chat_waittime_left

        WAITING_TIME = 5

        if rand_chat_waittime_left > WAITING_TIME:
            rand_chat_waittime_left -= WAITING_TIME
            renpy.pause(WAITING_TIME, hard=True)

        elif rand_chat_waittime_left > 0:
            waitFor = rand_chat_waittime_left
            rand_chat_waittime_left = 0
            renpy.pause(waitFor, hard=True)

        else:
            rand_chat_waittime_left = 0
            renpy.pause(WAITING_TIME, hard=True)


    def waitedLongEnough():
        """
        Checks whether the waiting time is up yet.

        RETURNS:
            boolean to determine whether the wait is over
        """
        global rand_chat_waittime_left

        return rand_chat_waittime_left == 0 and rand_low != 0



# stores that need to be globally available
init 4 python:
    import store.mas_randchat as mas_randchat

return

#Gender specific word replacement
#Those are to be used like this "It is [his] pen." Output:
#"It is his pen." (if the player's gender is declared as male)
#"It is her pen." (if the player's gender is decalred as female)
#"It is their pen." (if player's gender is not declared)
#Variables (i.e. what you put in square brackets) so far: his, he, hes, heis, bf, man, boy,
#Please remember to update the list if you add more gender exclusive words. ^
label mas_set_gender:
    python:
        pronoun_gender_map = {
            "M": {
                "his": "his",
                "he": "he",
                "hes": "he's",
                "heis": "he is",
                "bf": "boyfriend",
                "man": "man",
                "boy": "boy",
                "guy": "guy",
                "him": "him",
                "himself": "himself"
            },
            "F": {
                "his": "her",
                "he": "she",
                "hes": "she's",
                "heis": "she is",
                "bf": "girlfriend",
                "man": "woman",
                "boy": "girl",
                "guy": "girl",
                "him": "her",
                "himself": "herself"
            },
            "X": {
                "his": "their",
                "he": "they",
                "hes": "they're",
                "heis": "they are",
                "bf": "partner",
                "man": "person",
                "boy": "person",
                "guy": "person",
                "him": "them",
                "himself": "themselves"
            }
        }

        pronouns = pronoun_gender_map[persistent.gender]

        his = pronouns["his"]
        he = pronouns["he"]
        hes = pronouns["hes"]
        heis = pronouns["heis"]
        bf = pronouns["bf"]
        man = pronouns["man"]
        boy = pronouns["boy"]
        guy = pronouns["guy"]
        him = pronouns["him"]
        himself = pronouns["himself"]
    return

style jpn_text:
    font "mod_assets/font/mplus-2p-regular.ttf"

# functions related to ily2
init python:
    def mas_passedILY(pass_time):
        """
        Checks whether we are within the appropriate time since the last time
        Monika told the player 'ily' which is stored in persistent._mas_last_monika_ily
        IN:
            pass_time - a timedelta corresponding to the time limit we want to check against

        RETURNS:
            boolean indicating if we are within the time limit
        """
        check_time = datetime.datetime.now()

        # if a backward TT is detected here, return False and reset persistent._mas_last_monika_ily
        if persistent._mas_last_monika_ily is None or persistent._mas_last_monika_ily > check_time:
            persistent._mas_last_monika_ily = None
            return False

        return (check_time - persistent._mas_last_monika_ily) <= pass_time

    def mas_ILY(set_time=None):
        """
        Sets persistent._mas_last_monika_ily (the last time Monika said ily) to a given time
        IN:
            set_time - the time we want to set persistent._mas_last_monika_ily to
                defaults to datetime.datetime.now()
        """
        if set_time is None:
            set_time = datetime.datetime.now()
        persistent._mas_last_monika_ily = set_time

    def mas_shouldKiss(chance, cooldown=datetime.timedelta(hours=1), special_day_bypass=False):
        """
        Checks if Monika should give the player a random kiss

        CONDITIONS:
            1. Enamored+ affection
            2. Player already had their first kiss with Monika
            3. Random chance that changes depending on the chance and special_day_bypass vars
            4. Enough time has passed since the last kiss

        IN:
            chance:
                the chance to receive a kiss from Monika
            cooldown:
                a datetime.timedelta representing the amount of time after the
                last kiss the next random kiss will be allowed
                (Default: 1 hour)
            special_day_bypass:
                whether a special day should bypass the chance (Default=False)

        OUT:
            boolean:
                - True if the above conditions are met
                - False otherwise
        """
        should_kiss = (
            renpy.random.randint(1, chance) == 1
            or (special_day_bypass and mas_isSpecialDay())
            )

        return (
            mas_isMoniEnamored(higher=True)
            and persistent._mas_first_kiss
            and should_kiss
            and mas_timePastSince(persistent._mas_last_kiss, cooldown)
        )
