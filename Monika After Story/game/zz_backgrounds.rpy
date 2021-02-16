#Here's where we store our background data
default persistent._mas_background_MBGdata = {}

#Store the persistent background
#Defaults to def (spaceroom)
default persistent._mas_current_background = "spaceroom"

init -5 python in mas_background:
    #Marks this background as an outdoor type (disables opendoor for it)
    #value: ignored
    EXP_TYPE_OUTDOOR = "outdoor"

    #Tells the background changer to skip the leadin dialogue
    #value: ignored
    EXP_SKIP_LEADIN = "skip_leadin"

    #Tells the background changer to skip the transition (black screen)
    #value: ignored
    EXP_SKIP_TRANSITION = "skip_transition"

    #Tells the background changer to skip the outro dialogue
    #value: ignored
    EXP_SKIP_OUTRO = "skip_outro"

#START: Class definition
init -10 python:

    class MASBackgroundFilterTypeException(Exception):
        """
        Type exception for MASBackgroundFilter objects
        """

        def __init__(self, obj, mbf_type):
            """
            Constructor

            IN:
                obj - object that was not what we expected
                mbf_type - type we expected
            """
            self.msg = "{0} is not of {1}".format(obj, mbf_type)

        def __str__(self):
            """
            String
            """
            return self.msg


    class MASBackgroundFilterSliceDuplicateException(Exception):
        """
        Exception for when a Background fitler slice is in both a day chunk
        and a night chunk.
        """

        def __init__(self, flt):
            """
            Constructor

            IN:
                flt - the filter name of the offending fitler slice.
            """
            self.msg = "filter '{0}' found in both day chunk and night chunk".format(flt)

        def __str__(self):
            return self.msg


    class MASBackgroundFilterSlice(object):
        """
        Represntation of a filter for a MASBackground.
        this is related to the sprite filters, but gives each filter extra
        oomph.

        BG filters are designed to be flexible to work with BGs.
        See the MASBackgroundFilterChunk for more info on how this works.

        PROPERTIES:
            name - the name of this filter. This should be a filter ENUM.
                NOTE: this not checked until init level 0
            minlength - the amount of time in seconds that this filter must
                be able to be used for it to be shown. If the filter cannot be
                shown for this amount of time, it will not be shown at all.
            maxlength - the amount of time in seconds that this filter can
                be shown. The filter will never be shown more than this amt
                of seconds. If None, then max is unbounded.
            priority - the priority of this filter object. Larger number means
                higher priority. Lower priority means filter will be removed
                first.
            flt - the filter (imagematrix) objects to use. OPTIONAL.
                if this is None, it is assumed the filter data is handled
                elsewhere.
        """
        cache = {}
        # internal cache of MASBackgroundFilterSlice objects to avoid
        #   building duplicates.

        def __init__(self,
                name,
                minlength,
                maxlength=None,
                priority=1,
                flt=None,
                cache=True
        ):
            """
            Constructor

            IN:
                name - name of the filter. This is NOT checked against filter
                    ENUMS until init level 0.
                minlength - amount of time in seconds that this filter must
                    be at least shown for.
                maxlength - amount of time in seconds that this at most can be
                    shown for.
                    if None, max time is unbounded
                    (Default: None)
                priority - priority of this filter object. Larger number means
                    higher priority.
                    Must be between 1 and 10, inclusive.
                    Defaults to 10 if invalid.
                    (Default: 10)
                flt - imagemanip/matrix compatible filter to use.
                    only pass in if you wish to use the `add_to_filters`
                    function
                    (Default: None)
                cache - pass False to not cache this object.
                    Only for debug purposes
                    (Default: True)
            """
            self.name = name
            self.minlength = minlength
            self.maxlength = maxlength
            self.flt = flt

            if 1 <= priority <= 10:
                self.priority = priority
            else:
                self.priority = 10

            if cache:
                # store in cache
                self.cache[hash(self)] = self

        def __eq__(self, other):
            """
            EQ implementation.
            Based on hash
            """
            if isinstance(self, other.__class__):
                return hash(self) == hash(other)
            return False

        def __hash__(self):
            """
            Hash implementation. FilterSlices are unique based on name,
            minlength and priority
            """
            return MASBackgroundFilterSlice.gen_hash(
                self.name,
                self.minlength,
                self.maxlength,
                self.priority
            )

        def __ne__(self, other):
            """
            Not equals implementation
            """
            return not self.__eq__(other)

        def __repr__(self):
            return (
                "<FilterSlice: (name: {0}, min: {1}, max: {2}, pri: {3})>"
            ).format(
                self.name,
                self.minlength,
                self.maxlength,
                self.priority
            )

        def __str__(self):
            """
            Slice as string
            """
            return "M: {1:>6}|X: {3:>6}|N: {0} |P: {2}".format(
                self.name,
                self.minlength,
                self.priority,
                self.maxlength
            )

        def add_to_filters(self):
            """
            Adds this filter to the filters dict. Wil fail and log if used
            after init level -1.
            Only works if self.flt is not None.
            """
            if self.flt is not None:
                store.mas_sprites.add_filter(self.name, self.flt)

        @classmethod
        def cachecreate(cls,
                name,
                minlength,
                maxlength=None,
                priority=10,
                flt=None
        ):
            """
            Builds a MASBackgroundFilterSlice unless we have one in cache

            IN:
                See Constructor

            RETURNS: MASBackgroundFilterSlice object
            """
            hash_key = cls.gen_hash(name, minlength, maxlength, priority)
            if hash_key in cls.cache:
                return cls.cache[hash_key]

            return MASBackgroundFilterSlice(
                name,
                minlength,
                maxlength=maxlength,
                priority=priority,
                flt=flt
            )

        def can_fit(self, seconds):
            """
            Checks if this filter can fit in the time allotted

            IN:
                seconds - number of seconds to check

            RETURNS: True if this filter can fit in the given number of seconds
                FAlse if not
            """
            return self.minlength <= seconds

        def can_fit_td(self, td):
            """
            Checks if the filter can fit in the time allotted

            IN:
                td - timedelta object to check

            RETURNS: True if this filter can fit in the given timedelta,
                False if not
            """
            return self.minlength <= int(td.total_seconds())

        @staticmethod
        def gen_hash(name, minlength, maxlength, priority):
            """
            Generates a hash of the components of a MASBackgroundFilterSlice

            IN:
                name - name to use
                minlength - minlength to use
                maxlength - maxlength to use
                priority - priority to use

            RETURNS: hash of the object that would be created with the given
                properties.
            """
            return hash("-".join((
                name,
                str(minlength),
                str(maxlength),
                str(priority),
            )))

        def is_max(self, value):
            """
            Checks if the given vlaue is larger than max length.
            If this slice is unbounded, this will always return False

            IN:
                value - value to check

            RETURNS: True if the value is larger than maxlength, False if not
            """
            if self.maxlength is None:
                return False

            return value > self.maxlength

        def verify(self):
            """
            Verifies if this filter's name is a valid filter. Call this
            after init level -1.

            RETURNS: True if filter is valid, False if not
            """
            return store.mas_sprites.is_filter(self.name)


    class MASBackgroundFilterSliceData(object):
        """
        Relates a MASBackgroundFilterSlice to its order and offset

        PROPERTIES:
            offset - the offset associated with this slice
            length - the length of this slice data
            order - the order associated to this slice
            flt_slice - the slice to associate
        """

        def __init__(self, order, flt_slice):
            """
            Constructor

            IN:
                order - the order for this slice
                flt_slice - the slice to associate with this order
            """
            self.order = order
            self.offset = order
            self.flt_slice = flt_slice
            self.length = flt_slice.minlength

        def __gt__(self, other):
            """
            Greater than uses order
            """
            if isinstance(other, MASBackgroundFilterSliceData):
                return self.order > other.order
            return NotImplemented

        def __lt__(self, other):
            """
            Less than uses order
            """
            if isinstance(other, MASBackgroundFilterSliceData):
                return self.order < other.order
            return NotImplemented

        def __repr__(self):
            return (
                "<FilterSliceData: (order: {0}, offset: {1}, length: {2}"
                ", flt_slice: {3})>"
            ).format(
                self.order,
                self.offset,
                self.length,
                repr(self.flt_slice)
            )

        def __str__(self):
            """
            strings are offset + order + name
            """
            return "{0:>5}|ORD: {1} |AL: {3}|{2}".format(
                self.offset,
                self.order,
                self.flt_slice,
                self.length
            )

        def __len__(self):
            """
            Returns length
            """
            return self.length

        def eff_minlength(self):
            """
            Calculates the ending offset assuming min length

            RETURNS: offset + minlength
            """
            return self.offset + self.flt_slice.minlength

        @staticmethod
        def highest_priority(sl_data_list):
            """
            Finds the MASBackgroundFilterSliceData with the highest priority
            and returns its index

            IN:
                sl_data_list - list containig MASBackgroundFilterSliceData
                    objects to check

            RETURNS: index of the MASBackgroundFilterSliceData with the
                highest priority
            """
            h_priority = 0
            h_index = 0
            for index, sl_data in enumerate(sl_data_list):
                if sl_data.flt_slice.priority > h_priority:
                    h_priority = sl_data.flt_slice.priority
                    h_index = index

            return h_index

        @staticmethod
        def lowest_priority(sl_data_list):
            """
            Finds the MASBackgroundFilterSliceData with the lowest priority
            and returns its index

            IN:
                sl_data_list - list containing MASBackgroundFilterSliceData
                    objects to check

            RETURNS: index of the MASBackgroundFilterSliceData with the
                lowest priority
            """
            l_priority = 10
            l_index = 0
            for index, sl_data in enumerate(sl_data_list):
                if sl_data.flt_slice.priority < l_priority:
                    l_priority = sl_data.flt_slice.priority
                    l_index = index

            return l_index

        @staticmethod
        def sk(obj):
            """
            order sort key
            """
            return obj.order

        @staticmethod
        def sko(obj):
            """
            offset sort key
            """
            return obj.offset


    class MASBackgroundFilterChunk(object):
        """
        Chunk of filters for backgrounds.

        A BG filter chunk is a set of slices that represent a progression
        of filters througout the time range. The slices are handled in a way
        where they are intelligently picked depending on suntimes. This allows
        for handling of cases where there isn't enough time for each slice to
        exist.

        Each slice is a MASBackgroundFilterSlice object. The minlength property
        is used to determine if the object canfit in its allocated time slice.
        Priorities are used to determine the slices to keep. By default we
        try to keep every slice we can. Minlength is also used to determine
        when to swap filters.

        Slices are organized by an order. The order value determines the
        desired order of slices.

        Code can be ran during a filter change by passing in function to
        appropriate param. Any exceptions are caught and loggged.

        PROPERTIES:
            is_day - True if this is a day chunk, False if not
        """

        _ERR_PP_STR = (
            "[ERROR] error in slice pp | {0}\n"
            "=====FROM: {1} -> {2}\n"
        )
        _ERR_PP_STR_G = (
            "[ERROR] error in global slice pp | {0}\n"
            "=====FROM: {1} -> {2}\n"
        )

        def __init__(self, is_day, pp, *slices):
            """
            Constructor

            IN:
                is_day - True if this is a "Day" chunk. False if not
                pp - progpoint to run on a filter change (or slice change)
                    This is ran multiple times if multiple filter changes
                    occur, but NOT at all if a chunk change occurs.
                    This is NOT guaranteed to run if more a than day goes by
                    between progressions.
                    the following args are passed to the progpoint:
                        flt_old - the outgoing filter (string)
                            NOTE: this is None if we are starting the game
                        flt_new - the incoming filter (string)
                        curr_time - the current time
                    pass None to not use a progpoint
                *slices - slice arguments. Each item should be a
                    MASBackgroundFilterSlice object.
                    This should be in the desired order.
                    NOTE: there must be at least one slice with unbounded time
            """
            self.is_day = is_day

            self._slices = []
            # MASBackgroundFilterSliceData objects in standard order

            self._eff_slices = []
            # MASBackgroundFilterSliceData objects that we are actually
            # using in standard order

            self._pp = pp
            # progpoint

            self._index = 0
            # the index in eff_slices of the last filter change

            self._length = 0
            # the last length value passed into build

            self._parse_slices(slices)

        def __repr__(self):
            return (
                "<FilterChunk: (index: {0}, length: {1}, slices: {2}, "
                "eff_slices: {3})>"
            ).format(
                self._index,
                self._length,
                self._slices,
                self._eff_slices
            )

        def __str__(self):
            """
            Shows effective slice information
            """
            output = [
                "Current Slice: {0}".format(self._index),
                "Total Length: {0}".format(self._length),
                "Slices:",
            ]

            # string other slices
            for index in range(len(self._eff_slices)):

                # determine appropriate end time for eff size
                if index < len(self._eff_slices)-1:
                    endl = self._eff_slices[index+1].offset
                else:
                    endl = self._length

                # string slice
                sl_data = self._eff_slices[index]
                output.append("ES: {0:>5}|{1}".format(
                    endl - sl_data.offset,
                    sl_data
                ))

            return "\n".join(output)

        def __len__(self):
            """
            Length of this chunk
            """
            return self._length

        def _adjust_offset(self, index, amt):
            """
            Adjust offset of all eff_slices, starting from the given index.

            IN:
                index - index to start adjusting offsets.
                amt - amount to add to offsets. can be negative to
                    subtract.
            """
            for sl_data in self._eff_slices[index:]:
                sl_data.offset += amt

        def adv_slice(self, sfco, st_index, run_pp, curr_time):
            """
            Runs advance slice alg, running progpoints, but does NOT actually
            set new index.

            IN:
                sfco - seconds from chunk offset
                st_index - index to start at
                run_pp - True will run the progpoints, False will not
                curr_time - passed to the progpoint, should be current time
                    as a datetime.time object

            RETURNS: new slice index
            """
            # slices length
            s_len = len(self._eff_slices)
            if s_len < 2:
                return 0

            st_index -= 1

            # loop until sfco in range of current slice
            # or we reach last slice
            while (
                    st_index < s_len-1
                    and self._adv_slice_change(
                        st_index + 1,
                        sfco,
                        run_pp,
                        curr_time
                    )
            ):
                st_index += 1

            return st_index

        def _adv_slice_change(self, slidx, sfco, run_pp, curr_time):
            """
            Checks if a slice offset at the given index is smaller than
            sfco, and runs pps if so. This is mainly to combine a condition
            check and work together so we don't need extra if statements.

            IN:
                slidx - index of the NEXT slice to check
                    Assumes will not go past eff_slices length
                sfco - seconds from chunk offset
                run_pp - True will run progpoints, False will not
                curr_time - passed to progpoints, should be current time as
                    datetime.time object

            RETURNS: True if we should continue looping index, False if we
                have found the slice sfco belongs in.
            """
            if self._eff_slices[slidx].offset > sfco:
                return False

            # determine current and next slice data for a movement
            if slidx > 0:
                csl_data = self._eff_slices[slidx-1]
            else:
                csl_data = None

            if csl_data is not None:
                nsl_data = self._eff_slices[slidx]

                # run progs
                if run_pp:
                    self._pp_exec(
                        csl_data.flt_slice.name,
                        nsl_data.flt_slice.name,
                        curr_time
                    )

                # always run global
                store.mas_background.run_gbl_flt_change(
                    csl_data.flt_slice.name,
                    nsl_data.flt_slice.name,
                    curr_time
                )

            return True

        def build(self, length):
            """
            Builds the effective slices array using the given length as
            guidance.

            slices are built in a greedy fashion starting from 0, respecting
            priorities and etc.

            IN:
                length - the amount of seconds this chunk encompasses
            """
            self._length = length

            if length < 1:
                # this chunk has no length. clear it out
                self._eff_slices = []
                return

            if len(self._slices) < 2:
                # with only once slice, just set that slice as the
                # main slice
                sl_data = self._slices[0]
                sl_data.length = length
                sl_data.offset = 0
                self._eff_slices = [sl_data]
                return

            # always start with the minimum length expansion alg
            leftovers = self._min_fill(length)

            if len(leftovers) > 0:
                # if we have leftovers, then use complex alg
                self._priority_fill(length, leftovers)

            # set everyones length to minimum
            for sl_data in self._eff_slices:
                sl_data.length = sl_data.flt_slice.minlength

            # lastly, expand to fill voids
            self._expand(length)

            self.reset_index()

        def current(self):
            """
            Gets current filter

            RETURNS: current filter, or None if could not
            """
            if 0 <= self._index < len(self._eff_slices):
                return self._eff_slices[self._index].flt_slice.name
            return None

        def current_pos(self):
            """
            Generates internal information related to current position

            RETURNS: tuple:
                [0] - current slice index
                [1] - beginning offset of the current slice
                [2] - beginning offset of the next slice
                    NOTE: this is -1 if no next slice
            """
            if 0 <= self._index < len(self._eff_slices)-1:
                next_offset = self._eff_slices[self._index+1].offset
            else:
                next_offset = -1

            return (self._index, self._current_sldata().offset, next_offset)

        def _current_sldata(self):
            """
            Gets current slice data

            RETURNS: current slice data
            """
            return self._eff_slices[self._index]

        def _eff_chunk_min_end(self):
            """
            Gets the minimal chunk end length.

            RETURNS: last eff_slice's eff_offset + its minlength
            """
            return self._eff_slices[-1].eff_minlength()

        def _expand(self, length):
            """
            Expands all slices in effective slices until it fills the given
            length

            IN:
                length - the amount of length we need to fill
            """
            es_count = len(self._eff_slices)
            diff = length - self._eff_chunk_min_end()

            # make a list of inc amounts for easy looping
            inc_amts = [diff / es_count] * es_count

            # reverse add lefovers
            store.mas_utils.lo_distribute(
                inc_amts,
                diff % es_count,
                reverse=True
            )

            # apply amounts to values until we are out
            while sum(inc_amts) > 0:
                self._expand_once(inc_amts)

                # reform inc_amts so we continue adding leftover amounts to
                # slices that can still be expanded
                leftovers = store.mas_utils.fz_distribute(inc_amts)
                if leftovers > 0:
                    store.mas_utils.lo_distribute(
                        inc_amts,
                        leftovers,
                        reverse=True,
                        nz=True
                    )

        def _expand_once(self, value_list):
            """
            Runs expansion alg. This will add index-based numbers from the
            given value list to effective slice offsets and subtract added amts
            from the given corresponding position in value list.

            IN:
                value_list - list of amounts to add to individual items in
                    eff_slices

            OUT:
                value_list - leftover amounts to distribute to eff_slices
            """
            # apply inc amounts
            # start by figuring the base new length
            c_off = 0
            for index in range(len(self._eff_slices)):
                c_off = self._expand_sld(index, value_list, c_off)

        def _expand_sld(self, index, value_list, c_off):
            """
            Expands a slicedata item. Also adjusts value list as appropriate

            IN:
                index - position to expand slice data and value list
                value_list - list of amounts to add to individual items in
                    eff_slices
                c_off - current offset value

            OUT:
                value_list - value at index changed to leftover amounts or 0

            RETURNS: new current offset value
            """
            # get sl data
            sl_data = self._eff_slices[index]

            # the current offset is always this sl data's new start
            sl_data.offset = c_off

            # how long is this slice?
            sl_len = sl_data.length + value_list[index]

            # if too big, adjust
            if sl_data.flt_slice.is_max(sl_len):
                diff = sl_len - sl_data.flt_slice.maxlength
                value_list[index] = diff
                sl_len = sl_data.flt_slice.maxlength
            else:
                value_list[index] = 0

            # and set new length
            sl_data.length = sl_len

            # calculate next offset
            return c_off + sl_len

        def filters(self, ordered=False):
            """
            Gets list of filters

            IN:
                ordered - True will return the filters in an ordered list.
                    This may contain duplicates.

            RETURNS: list of all the filters associatd with this filter chunk
                (list of strings)
            """
            if ordered:
                # ordered list
                return [sl_data.flt_slice.name for sl_data in self._slices]

            # otherwise use a dict so we only return each filter once
            filters = {}
            for sl_data in self._slices:
                filters[sl_data.flt_slice.name] = None

            return filters.keys()

        def first_flt(self):
            """
            Gets the first filter in this chunk

            RETURNS: first filter in this chunk, or None if no eff slices
            """
            if len(self._eff_slices) > 0:
                return self._eff_slices[0].flt_slice.name

            return None

        def last_flt(self):
            """
            Gets the last filter in this chunk

            RETURNS: last filter in this chunk, or None if no eff slices
            """
            last_idx = len(self._eff_slices)-1
            if last_idx < 0:
                return None

            return self._eff_slices[last_idx].flt_slice.name

        def _min_fill(self, length):
            """
            Fills the effective slices using minlength logic.

            IN:
                length - the length we are filling

            RETURNS: leftovers - contains slices that we could not fit. Could
                be empty if we managed to fit all slices.
            """
            built_length = 0
            index = 1
            # start at the 2nd slice as thats where we start adjusting offsets

            # always start with the first slice
            built_length = self._slices[0].flt_slice.minlength
            self._eff_slices = [self._slices[0]]

            # add slices
            while built_length < length and index < len(self._slices):
                # retrieve slice info for this index
                curr_sl_data = self._slices[index]

                # add the slice
                curr_sl_data.offset = built_length
                self._eff_slices.append(curr_sl_data)

                # increment built length
                built_length += curr_sl_data.flt_slice.minlength
                index += 1

            if built_length < length:
                # we managed to fit every slice!
                return []

            # otherwise, we have a leftover slice in some way
            last_sl_data = self._eff_slices.pop()

            # and add any remaining slices
            return [last_sl_data] + self._slices[index:]

        def _parse_slices(self, slices):
            """
            Parses the slices data
            """
            # verify slices
            if len(slices) < 1:
                raise Exception("No slices found")

            has_unbounded = False
            for index, bg_flt in enumerate(slices):

                # check slice
                if not isinstance(bg_flt, MASBackgroundFilterSlice):
                    raise MASBackgroundFilterTypeException(
                        bg_flt,
                        MASBackgroundFilterSlice
                    )

                if bg_flt.maxlength is None:
                    has_unbounded = True
                    bg_flt.priority = 11 # force this slice to be important

                # add to slices
                store.mas_utils.insert_sort(
                    self._slices,
                    MASBackgroundFilterSliceData(index, bg_flt),
                    MASBackgroundFilterSliceData.sk
                )

            if not has_unbounded:
                raise Exception("No unbounded slice found")

            # set offset of initial slice to 0
            self._slices[0].offset = 0

        def _pf_insert(self, index, sl_data):
            """
            Inserts a filter slice offset into the effective slices list
            based on a starting index.

            IN:
                index - starting index
                sl_data - the slice data to insert
            """
            # looop, finding the right place for the sl_off
            while (
                    index < len(self._eff_slices)
                    and self._eff_slices[index] < sl_data
            ):
                index += 1

            # we must have the correct location now
            # determine the offset to use
            if index == 0:
                sl_data.offset = 0
            else:
                sl_data.offset = self._eff_slices[index-1].eff_minlength()
            self._eff_slices.insert(index, sl_data)

            # now adjust offsets for all remaining sl datas
            self._adjust_offset(index + 1, sl_data.flt_slice.minlength)

        def _pp_exec(self, flt_old, flt_new, curr_time):
            """
            Executes a progpoint

            Exceptions are logged

            IN:
                flt_old - outgoing filter (string)
                flt_new - incoming filter (string)
                curr_time - current time as datetime.time
            """
            if self._pp is None:
                return

            try:
                self._pp(flt_old=flt_old, flt_new=flt_new, curr_time=curr_time)
            except Exception as e:
                store.mas_utils.writelog(self._ERR_PP_STR.format(
                    repr(e),
                    flt_old,
                    flt_new
                ))

        def _priority_fill(self, length, leftovers):
            """
            Fills the effective slices using priority logic.
            This assumes the eff slices has been filled with minimal logic

            IN:
                length - the amount of length we need to fill
                leftovers - slices that have not been added yet
            """
            # Gist:
            #   1. reverse through the eff_slices, removing elements with
            #       lower priorities than leftovers, and adding high priority
            #       elements from leftovers.

            # highest priority in leftovers
            hpsl_data = leftovers.pop(
                MASBackgroundFilterSliceData.highest_priority(leftovers)
            )

            for es_index in range(len(self._eff_slices)-1, -1, -1):

                # get current slice
                csl_data = self._eff_slices[es_index]

                if csl_data.flt_slice.priority < hpsl_data.flt_slice.priority:
                    # current has a lower priority

                    # remove the lower priority item, and store in leftovers
                    leftovers.insert(0, self._eff_slices.pop(es_index))

                    # then clean up the offsets
                    self._adjust_offset(
                        es_index,
                        csl_data.flt_slice.minlength * -1
                    )

                    # add the higher priority item
                    self._pf_insert(es_index, hpsl_data)

                    # and find newest high leftover priority
                    hpsl_data = leftovers.pop(
                        MASBackgroundFilterSliceData.highest_priority(
                            leftovers
                        )
                    )

            # clean up if our current min length is too large
            while (
                    len(self._eff_slices) > 1
                    and self._eff_chunk_min_end() > length
            ):
                # obtain lowest priority filter slice offset object and remove
                llop_index = MASBackgroundFilterSliceData.lowest_priority(
                    self._eff_slices
                )
                lpsl_data = self._eff_slices.pop(llop_index)

                # fix eff offsets
                self._adjust_offset(
                    llop_index,
                    lpsl_data.flt_slice.minlength * -1
                )

            # ensure first slice has 0 offset
            self._eff_slices[0].offset = 0

        def progress(self, sfco, curr_time):
            """
            Progresses the filter, running progpoints and updating indexes

            NOTE: we assume that our next target is in this chunk.

            Progpoints are ran for every slice we go through.

            IN:
                sfco - seconds from chunk offset to progress to
                curr_time - current time in datetime.time

            RETURNS: current filter after progression
            """
            # advance slices
            self._index = self.adv_slice(sfco, self._index, True, curr_time)

            return self.current()

        def update(self, ct_off):
            """
            Updates the internal indexes.
            NOTE: this will NOT call any progpoints

            IN:
                ct_off - offset of current time, with respect to the chunk this
                    slice is in.
            """
            s_len = len(self._eff_slices)
            if s_len < 2:
                self._index = 0
                return

            # determine current slice offsets
            sidx = -1

            while (
                    sidx < s_len-1
                    and self._eff_slices[sidx+1].offset <= ct_off
            ):
                # deteremine next current offset and next index
                sidx += 1

            # now we should have the correct index probably
            self._index = sidx

        def reset_index(self):
            """
            Resets slice index to 0
            """
            self._index = 0

        def verify(self):
            """
            Verifies the filters in this filter Chunk
            Assumed to be called at least at init level 0
            Filters should all exist.

            Exceptions are raised if a bad filter is found.
            """
            for sl_data in self._slices:
                flt_slice = sl_data.flt_slice
                if not flt_slice.verify():
                    raise MASInvalidFilterException(flt_slice.name)


    class MASBackgroundFilterManager(object):
        """
        Filter Management class for backgrounds.

        The BG filter system slices a day into 3 chunks.
        these chunks correspond to the suntimes system.
        MidNight to SunRise (MN - SR)
        SunRise to SunSet (SR - SS)
        SunSet to MidNignt (SS - MN)

        Each chunk is marked day/night, and is used when determining if a
        filter is day or night. This means two separate chunks with different
        day/night settings can NOT contain same filters. If you need the same
        filter content to be considerd day AND night, make two separate filter
        enums. This is to avoid ambiguities.

        PROPERTIES:
            None
        """

        _ERR_PP_STR = (
            "[ERROR] error in chunk pp | {0}\n\n"
            "=====FROM:\n{1}\n\n"
            "=====TO\n{2}\n"
        )
        _ERR_PP_STR_G = (
            "[ERROR] error in global chunk pp | {0}\n\n"
            "=====FROM:\n{1}\n\n"
            "=====TO\n{2}\n"
        )

        def __init__(self, mn_sr, sr_ss, ss_mn, pp=None):
            """
            Constructor

            IN:
                mn_sr - MASBackgroundFilterChunk for midnight to sunrise
                sr_ss - MASBackgroundFilterChunk for sunrise to sunset
                ss_mn - MASBackgroundFilterChunk for sunset to midnight
                pp - progpoint to run on a chunk change.
                    This may run multiple times if multiple chunk changes
                    have occurred.
                    This is NOT guaranteed to run if more than a day of time
                    passes between progressions.
                    the following args are passed to the progpoint:
                        chunk_old - the outgoing chunk (MBGFChunk)
                            NOTE: this is None if we are staring the game
                        chunk_new - the incoming chunk (MBGFChunk)
                        curr_time - the current time
                    (Default: None)
            """
            if not isinstance(mn_sr, MASBackgroundFilterChunk):
                raise MASBackgroundFilterTypeException(
                    mn_sr,
                    MASBackgroundFilterChunk
                )
            if not isinstance(sr_ss, MASBackgroundFilterChunk):
                raise MASBackgroundFilterTypeException(
                    sr_ss,
                    MASBackgroundFilterChunk
                )
            if not isinstance(ss_mn, MASBackgroundFilterChunk):
                raise MASBackgroundFilterTypeException(
                    ss_mn,
                    MASBackgroundFilterChunk
                )

            self._mn_sr = mn_sr
            # midnight to sunrise

            self._sr_ss = sr_ss
            # sunrise to sunset

            self._ss_mn = ss_mn
            # sunset to midnight

            self._chunks = [self._mn_sr, self._sr_ss, self._ss_mn]
            # ordered chunks for easier swapping

            self._pp = pp
            # progpoint

            self._day_filters = {}
            self._night_filters = {}
            # organized filter dicts
            # key: name of filter
            # value: Ignored
            # NOTE: organized in verify.

            self._index = 0
            # the index in _chunks of the current chunk

            self._prev_flt = None
            # set to the current filter if update was used

            self._updated = False
            # set to True upon an update, set to False upon progress

        def __repr__(self):
            day_f = self._day_filters
            if day_f is not None:
                day_f = day_f.keys()

            night_f = self._night_filters
            if night_f is not None:
                night_f = night_f.keys()

            return (
                "<FilterManager: (index: {0}, updated: {1}, prev_flt: {2}, "
                "day_flts: {3}, night_flts: {4}, mn_sr: {5}, sr_ss: {6}, "
                "ss_mn: {7})>"
            ).format(
                self._index,
                self._updated,
                self._prev_flt,
                day_f,
                night_f,
                repr(self._mn_sr),
                repr(self._sr_ss),
                repr(self._ss_mn)
            )

        def __str__(self):
            """
            Shows chunks and curr chunk information
            """
            output = []

            # mn to sr chunk
            chunk_name = "Midnight to Sunrise"
            if self._index == 0:
                chunk_name += "| CURRENT CHUNK"
            output.append(chunk_name)
            output.append(str(self._mn_sr))

            # sr to ss chunk
            chunk_name = "Sunrise to Sunset"
            if self._index == 1:
                chunk_name += "| CURRENT CHUNK"
            output.append("")
            output.append(chunk_name)
            output.append(str(self._sr_ss))

            # ss to mn chunk
            chunk_name = "Sunset to Midnight"
            if self._index == 2:
                chunk_name += "| CURRENT CHUNK"
            output.append("")
            output.append(chunk_name)
            output.append(str(self._ss_mn))

            return "\n".join(output)

        def adv_chunk(self, sfmn, st_index, run_pp, curr_time):
            """
            Runs advance chunks alg, running progpoints but does NOT actually
            set new index. This WILL SET SLICE INDEXES.

            IN:
                sfmn - number of seconds since midnight
                st_index - index to start at
                run_pp - True will run the progpoints, FAlse will not
                curr_time - passed to the progpoint. should be current time
                    as a datetime.time object

            RETURNS: new chunk index
            """
            # chunk length
            c_len = len(self._chunks)

            # determine current chunk offsets
            # Current Beginning OFFset, Next Beginning OFFset
            cb_off, nb_off = self._calc_off(st_index)
            curr_chunk = self._chunks[st_index]
            found = False

            # force stop iteration if something bad happened
            iter_stop = 10

            # loop until we found the chunk, or if we found it, until the first
            #   non-zero chunk
            while iter_stop > 0 and (not found or len(curr_chunk) < 1):

                # determine next chunk index
                nxt_index = (st_index + 1) % c_len # next index or 0 if max len

                # next chunk
                new_chunk = self._chunks[nxt_index]

                # determine next chunk offsets
                # next curent chunk offset offset or 0 if 86400
                cb_off = nb_off % (store.mas_utils.secInDay())

                # next chunk's offset
                nb_off = cb_off + len(new_chunk)

                # set found if we found the chunk
                if not found:
                    found = cb_off <= sfmn < nb_off
                    # once this is set, the next loops will only happen if
                    # current chunks are less than zero

                # lastly run pp if desired
                if run_pp:
                    self._pp_exec(
                        curr_chunk,
                        new_chunk,
                        curr_time
                    )

                    # and global
                    try:
                        store.mas_background._gbl_chunk_change(
                            curr_chunk,
                            new_chunk,
                            curr_time
                        )
                    except Exception as e:
                        store.mas_utils.writelog(self._ERR_PP_STR_G.format(
                            repr(e),
                            str(curr_chunk),
                            str(new_chunk),
                        ))

                # then finally reset slice index for the chunk we are leaving
                curr_chunk.reset_index()

                # and set the current chunk to next chunk
                curr_chunk = new_chunk
                st_index = nxt_index

                iter_stop -= 1

            if iter_stop < 1:
                # this is bad
                raise Exception("inf looped here")

            return st_index

        def backmap(self, anchors):
            """
            Generates a backwords lookback map with a set of anchors.
            Basically, this creates a mapping of the internal filters such that
            each filter is mapped to an "anchor" filter, based on the order
            of the filters. The lookback for determining an anchor also loops
            upon reaching the end of a day.

            Example:
                Anchors: flt_1, flt_3
                Order: flt_0, flt_1, flt_2, flt_3, flt_4, flt_5
                Resulting mapping:
                    flt_0: flt_3 - (because we loop to flt_5 when looking back
                                    from flt_0)
                    flt_1: flt_1
                    flt_2: flt_1 - (flt_1 is the closest previous anchor from
                                    flt_2)
                    flt_3: flt_3
                    flt_4: flt_3
                    flt_5: flt_3

            IN:
                anchors - dict of anchors. Set the keys to the anchor filters.

            OUT:
                anchors - the values will be set to lists of all filtesr mapped
                    to those anchors

            RETURNS: reverse map where each filter is a key, and the values are
                anchors.
            """
            if len(anchors) < 1:
                return {}

            # organize all filters in order
            ordered_flts = []
            for chunk in self._chunks:
                ordered_flts.extend(chunk.filters(True))

            if len(ordered_flts) < 1:
                return {}

            # init anchors lists
            for anc_key in anchors:
                anchors[anc_key] = []

            # init reverse map
            r_map = {}

            # loop over filters
            curr_anchor = None
            orphans = []
            for flt in ordered_flts:
                # check for new anchor
                if flt in anchors:
                    curr_anchor = flt

                # now organize
                if curr_anchor is None:
                    # orphans are added to the last anchor
                    orphans.append(flt)

                else:
                    # have anchor, add to lists and maps
                    r_map[flt] = curr_anchor
                    anchors[curr_anchor].append(flt)

            # add orphans to the last filter
            if curr_anchor is not None:
                anchors[curr_anchor].extend(orphans)
                for orphan in orphans:
                    r_map[orphan] = curr_anchor

            return r_map

        def build(self, sunrise, sunset):
            """
            Builds each chunk with the given sunrise and sunset values.

            IN:
                sunrise - sunrise time in number of seconds from midnight
                sunset - sunset time in number of seconds from midnight
            """
            self._mn_sr.build(sunrise)
            self._sr_ss.build(sunset - sunrise)
            self._ss_mn.build((store.mas_utils.secInDay()) - sunset)
            self._index = 0

        def buildupdate(self, sunrise, sunset, curr_time):
            """
            Builds each chunk with given sunrise/sunset values, then runs
            update to set the correct index.

            Mostly a combination of build and update.

            Properly sets prev_flt in this scenario.

            IN:
                sunrise - see build
                sunset - see build
                curr_time - see update
            """
            # save current, pre-build filter
            prev_flt = self.current()

            # build new slices
            self.build(sunrise, sunset)

            # run update
            self.update(curr_time)

            # set prev flt correctly
            self._prev_flt = prev_flt

        def _calc_off(self, index):
            """
            caluates beginning and next offset from chunk at the given index

            IN:
                index - index of chunk to check

            RETURNS: tuple:
                [0] - beginning offset of chunk at index
                [1] - beginning offset of chunk at index+1 (or next chunk)
            """
            # calclulate current
            cb_off = 0
            for idx in range(index):
                cb_off += len(self._chunks[idx])

            # now for next
            if index < len(self._chunks)-1:
                nb_off = cb_off + len(self._chunks[index])
            else:
                nb_off = store.mas_utils.secInDay()

            return cb_off, nb_off

        def current(self):
            """
            Gets current filter

            RETURNS: current filter
            """
            return self._chunks[self._index].current()

        def _current_chunk(self):
            """
            Gets current chunk

            RETURNS: current chunk
            """
            return self._chunks[self._index]

        def current_pos(self):
            """
            Generates internal informatiom related to the current position

            RETURNS: tuple:
                [0] - current chunk index
                [1] - beginning offset of the current chunk
                [2] - beginning offset of the next chunk
                    NOTE: this is number of seconds in day if no next chunk
                [3] - current slice index
                [4] - beginning offset of the current slice
                [5] - beginning offset of the next slice
                    NOTE: this is set to the next chunk offset if no next
                        slice
            """
            curr_offset, next_offset = self._calc_off(self._index)

            # now get slice info
            sl_index, sl_begin, sl_end = self._current_chunk().current_pos()

            # end sl might be different
            if sl_end < 0:
                sl_end = next_offset

            # and return info
            return (
                self._index,
                curr_offset,
                next_offset,
                sl_index,
                sl_begin,
                sl_end
            )

        def filters(self):
            """
            RETURNS: list of all filters associated with this filter manager
                (list of strings)
                NOTE: does not contain duplicates.
            """
            both = {}
            both.update(self._day_filters)
            both.update(self._night_filters)
            return both.keys()

        def filters_day(self):
            """
            RETURNS: list of all day filters associated with this filter
                manager.
                (list of stirngs)
                NOTE: does not contain duplicates
            """
            return self._day_filters.keys()

        def filters_night(self):
            """
            RETURNS: list of all night filters associated with this filter
                manager.
                (list of strings)
                NOTE: does not contain duplicates
            """
            return self._night_filters.keys()

        def is_flt_day(self, flt):
            """
            Checks if the given filter is day according to this filter manager
            NOTE: assumes we are organized already.

            IN:
                flt - filter to check

            RETURNS: True if day, false if not, None if filter not associatd
                with this filter manager
            """
            if flt in self._day_filters:
                return True
            if flt in self._night_filters:
                return False
            return None

        def _organize(self):
            """
            Organize filters into day and night dicts
            """
            self._organize_chunk(self._mn_sr)
            self._organize_chunk(self._sr_ss)
            self._organize_chunk(self._ss_mn)

        def _organize_chunk(self, chunk):
            """
            Organizes a single chunk into the day and night dicts

            IN:
                chunk - MASBackgroundFilterChunk to organize
            """
            if chunk.is_day:
                flt_d = self._day_filters
            else:
                flt_d = self._night_filters

            for flt in chunk.filters():
                flt_d[flt] = None

        def _pp_exec(self, chunk_old, chunk_new, curr_time):
            """
            Executes a progpoint

            Exceptions are logged

            IN:
                chunk_old - outgoing MASBackgroundFilterChunk
                chunk_new - incoming MASBackgroundFilterChunk
                curr_time - current time as datetime.time
            """
            if self._pp is None:
                return

            try:
                self._pp(
                    chunk_old=chunk_old,
                    chunk_new=chunk_new,
                    curr_time=curr_time
                )
            except Exception as e:
                store.mas_utils.writelog(self._ERR_PP_STR.format(
                    repr(e),
                    str(chunk_old),
                    str(chunk_new)
                ))

        def progress(self):
            """
            Progresses the filter, running progpoints and updating indexes.

            NOTE: if update was called before this, then we only run the
            global filter change progpoint if there was a filter change.

            NOTE: we do NOT do full loop arounds. This means that even if
            there was a literal day between progressions, this will only run
            as if it were same day progression.

            Progpoint execution rules:
            * progression remains in the same chunk:
                1. progpoint in that chunk is ran for every slice change.
                2. global progpoint is ran for every slice change.
            * progression moves to next chunk:
                1. progpoint from chunk to chunk is ran.
                2. global progpoint from chunk to chunk is ran.
                3. progpoints in the NEW chunk is ran for every slice change.
                4. global progpoint is ran for every slice change in the NEW
                    chunk.
            * progression moves through multiple chunks:
                1. progpoint from chunk to chunk is ran for every chunk change.
                2. global progpoint from chunk to chunk is ran for every
                    chunk change.
                3. progpoints in the chunk we END UP IN is ran for every
                    slice change.
                4. global progpoint is ran for every slice change in the chunk
                    we END UP IN.
            * progression changes via update:
                1. global progpoint is ran for one slice change if the filter
                    changes.

            RETURNS: the current filter after progression
            """
            # seconds from midnight + curr time
            curr_time = datetime.datetime.now().time()
            sfmn = store.mas_utils.time2sec(curr_time)

            if self._updated:
                # if we just updated, then we just need to run global prog
                # point upon flt change and return new
                new_flt = self.current()
                self._updated = False
                if new_flt != self._prev_flt:
                    store.mas_background.run_gbl_flt_change(
                        self._prev_flt,
                        new_flt,
                        curr_time
                    )

                return new_flt

            # determine our current position range
            pos_data = self.current_pos()

            # are we technically in same chunk but before in time?
            # reset the current chunk's slice index then advance
            if (
                    pos_data[1] <= sfmn < pos_data[2]  # in same chunk
                    and sfmn < (pos_data[1] + pos_data[4]) # earlier than slice
            ):
                self._current_chunk().reset_index()

            else:
                # start by advancing chunks correctly, if needed
                self._index = self.adv_chunk(
                    sfmn,
                    self._index,
                    True,
                    curr_time
                )

            # now we can start advancing slices
            return self._chunks[self._index].progress(
                sfmn - (self._calc_off(self._index)[0]),
                curr_time
            )

        def reset_indexes(self):
            """
            Resets all indexes to 0, so we are in fresh state mode
            """
            self._index = 0
            for chunk in self._chunks:
                chunk._index = 0

        def update(self, curr_time=None):
            """
            Updates the internal indexes.
            NOTE: this will NOT call any progpoints. Call progress after this
                to run (some) progpoints if needed

            IN:
                curr_time - datetime.time object to update internal indexes
                    to.
                    If NOne, then we use current.
                    (Default: None)
            """
            if curr_time is None:
                curr_time = datetime.datetime.now().time()

            # keep track of current filter
            self._prev_flt = self.current()

            # establish seconds
            # Seconds From MidNight
            sfmn = store.mas_utils.time2sec(curr_time)

            cindex = self.adv_chunk(sfmn, 0, False, curr_time)

            # we should now be in the correct index probably
            self._chunks[self._index].reset_index()
            self._index = cindex
            boff, eoff = self._calc_off(cindex)
            self._chunks[cindex].update(sfmn - boff)

            # mark that we used update
            self._updated = True

        def verify(self):
            """
            Verifies the filters in this filter manager.
            Assumed to be called at least at init level 0
            Filters cannot be in both day and night chunks. If this happens,
            an exception will be raised.

            We also verify filters in each chunk here.
            """
            # first organize filters into day and night
            self._organize()

            # now compare the lists
            for day_flt in self._day_filters:
                if day_flt in self._night_filters:
                    raise MASBackgroundFilterSliceDuplicateException(day_flt)

            # now verify each chunk
            self._mn_sr.verify()
            self._sr_ss.verify()
            self._ss_mn.verify()


    def MASBackground(
            background_id,
            prompt,
            image_day,
            image_night,
            image_rain_day=None,
            image_rain_night=None,
            image_overcast_day=None,
            image_overcast_night=None,
            image_snow_day=None,
            image_snow_night=None,
            hide_calendar=False,
            hide_masks=False,
            disable_progressive=None,
            unlocked=False,
            entry_pp=None,
            exit_pp=None
    ):
        """DEPRECATED
        Old-style MASBackground objects.
        This is mapped to a MASFilterableBackground with default
        (aka pre0.11.3 filters) slice management

        IN:
            background_id:
                id that defines the background object
                NOTE: Must be unique

            prompt:
                button label for this bg

            image_day:
                the renpy.image object we use for this bg during the day
                NOTE: Mandatory

            image_night:
                the renpy.image object we use for this bg during the night
                NOTE: Mandatory

            image_rain_day:
                the image tag we use for the background while it's raining (day)
                (Default: None, not required)

            image_rain_night:
                the image tag we use for the background while it's raining (night)
                (Default: None, not required)

            image_overcast_day:
                the image tag we use for the background while it's overcast (day)
                (Default: None, not required)

            image_overcast_night:
                the image tag we use for the background while it's overcast (night)
                (Default: None, not required)

            image_snow_day:
                the image tag we use for the background while it's snowing (day)
                (Default: None, not required)

            image_snow_night:
                the image tag we use for the background while it's snowing (night)
                (Default: None, not required)

            hide_calendar:
                whether or not we want to display the calendar
                (Default: False)

            hide_masks:
                weather or not we want to show the windows
                (Default: False)

            disable_progressive:
                weather or not we want to disable progressive weather
                (Default: None, if hide masks is true and this is not provided, we assume True, otherwise False)

            unlocked:
                whether or not this background starts unlocked
                (Default: False)

            entry_pp:
                Entry programming point for the background
                (Default: None)

            exit_pp:
                Exit programming point for this background
                (Default: None)

        RETURNS: MASFilterableBackground object
        """
        # build map data
        img_map_data = {
            store.mas_sprites.FLT_DAY: MASWeatherMap(precip_map={
                store.mas_weather.PRECIP_TYPE_DEF: image_day,
                store.mas_weather.PRECIP_TYPE_RAIN: image_rain_day,
                store.mas_weather.PRECIP_TYPE_OVERCAST: image_overcast_day,
                store.mas_weather.PRECIP_TYPE_SNOW: image_snow_day,
            }),
            store.mas_sprites.FLT_NIGHT: MASWeatherMap(precip_map={
                store.mas_weather.PRECIP_TYPE_DEF: image_night,
                store.mas_weather.PRECIP_TYPE_RAIN: image_rain_night,
                store.mas_weather.PRECIP_TYPE_OVERCAST: image_overcast_night,
                store.mas_weather.PRECIP_TYPE_SNOW: image_snow_night,
            }),
        }

        # build object
        return MASFilterableBackground(
            background_id,
            prompt,
            MASFilterWeatherMap(**img_map_data),
            store.mas_background.default_MBGFM(),
            hide_calendar=hide_calendar,
            hide_masks=hide_masks,
            disable_progressive=disable_progressive,
            unlocked=unlocked,
            entry_pp=entry_pp,
            exit_pp=exit_pp
        )


    class MASFilterableBackground(object):
        """
        Background class to get display props for bgs

        PROPERTIES:
            background_id - the id which defines this bg
            prompt - button label for the bg
            image_map - MASFilterWeatherMap object containing mappings of
                filter + weather to images
            hide_calendar - whether or not we display the calendar with this
            hide_masks - whether or not we display the window masks
            disable_progressive - weather or not we disable progesssive weather
            unlocked - whether or not this background is unlocked
            entry_pp - entry programming points for bgs
            exit_pp - exit programming points
        """
        import store.mas_background as mas_background
        import store.mas_weather as mas_weather

        def __init__(self,
            background_id,
            prompt,
            image_map,
            filter_man,
            hide_calendar=False,
            hide_masks=False,
            disable_progressive=None,
            unlocked=False,
            entry_pp=None,
            exit_pp=None,
            ex_props=None,
            deco_man=None,
        ):
            """
            Constructor for background objects

            IN:
                background_id:
                    id that defines the background object
                    NOTE: Must be unique

                prompt:
                    button label for this bg

                image_map:
                    MASFilterWeatherMap of bg images to use.
                    Use image tags for MASWeatherMap values.

                filter_man:
                    MASBackgroundFilterManager to use

                backup_img:
                    image tag/image path to use as a backup

                hide_calendar:
                    whether or not we want to display the calendar
                    (Default: False)

                hide_masks:
                    weather or not we want to show the windows
                    (Default: False)

                disable_progressive:
                    weather or not we want to disable progressive weather
                    (Default: None, if hide masks is true and this is not provided, we assume True, otherwise False)

                unlocked:
                    whether or not this background starts unlocked
                    (Default: False)

                entry_pp:
                    Entry programming point for the background
                    (Default: None)

                exit_pp:
                    Exit programming point for this background
                    (Default: None)

                ex_props:
                    Extra properties for backgrounds. If None, an empty dict is assigned
                    (Default: None)

                deco_man:
                    MASDecoManager to use
                    (Default: None)
            """
            # sanity checks
            if background_id in self.mas_background.BACKGROUND_MAP:
                raise Exception("duplicate background ID")
            if not isinstance(image_map, MASFilterWeatherMap):
                raise TypeError(
                    "Expected MASFilterWeatherMap, got {0}".format(
                        type(image_map)
                    )
                )
            if not isinstance(filter_man, MASBackgroundFilterManager):
                raise TypeError(
                    "Exepcted MASBackroundFilterManager, got {0}".format(
                        type(filter_man)
                    )
                )

            if deco_man is None:
                deco_man = MASDecoManager()

            self.background_id = background_id
            self.prompt = prompt
            self.image_map = image_map
            self._flt_man = filter_man
            self._deco_man = deco_man

            # internal mapping of filters to their latest image.
            # see MASBackgroundFilterManager.backmap for explanation.
            # we use this to ensure that every filter has an appropriate
            # set of BG images to use.
            # key: filter
            # value: filter to check for images
            self._flt_img_map = {}

            # reverse map of the above, mapping filters-with-images to lists
            # of dependent filters.
            # key: filter
            # value: list of filters that use the key's images.
            self._flt_img_anc = {}

            #Then the other props
            self.hide_calendar = hide_calendar
            self.hide_masks = hide_masks

            #Progressive handling
            if disable_progressive is None:
                self.disable_progressive = hide_masks
            else:
                self.disable_progressive = disable_progressive

            self.unlocked = unlocked
            self.entry_pp = entry_pp
            self.exit_pp = exit_pp

            #Add ex_props
            if ex_props is None:
                ex_props = dict()

            self.ex_props = ex_props

            # add to background map
            self.mas_background.BACKGROUND_MAP[background_id] = self

        def __eq__(self, other):
            if isinstance(other, MASFilterableBackground):
                return self.background_id == other.background_id
            return NotImplemented

        def __ne__(self, other):
            result = self.__eq__(other)
            if result is NotImplemented:
                return result
            return not result

        def build(self):
            """
            Builds filter slices using current suntimes.
            Also builds appropraite BG image maps.

            NOTE: should only be called during init.
            NOTE: IF YOU PLAN TO CALL UPDATE AFTER THIS, use buildupdate
                instead.
            """
            # build filter slices
            self._flt_man.build(
                persistent._mas_sunrise * 60,
                persistent._mas_sunset * 60
            )

            # now build flt image maps
            self._flt_img_map = self._flt_man.backmap(self._flt_img_anc)

        def buildupdate(self, curr_time=None):
            """
            Builds filter slices appropriately, then runs update.
            This will set prev_flt correctly when doing an update after a
            build.

            IN:
                curr_time - see MASFilterableBackground.update
            """
            if store.mas_background.dbg_log:
                store.mas_utils.writelog("\nCalled from - bupd\n")
                if store.mas_background.dbg_log_st:
                    store.mas_utils.writestack()

                store.mas_utils.writelog(
                    store.mas_background.DBG_MSG_C.format(
                        self._flt_man.current(),
                        str(self._flt_man.current_pos())
                    )
                )

            # build and update slices
            self._flt_man.buildupdate(
                persistent._mas_sunrise * 60,
                persistent._mas_sunset * 60,
                curr_time
            )

            # build flt image maps
            self._flt_img_map = self._flt_man.backmap(self._flt_img_anc)

            if store.mas_background.dbg_log:
                store.mas_utils.writelog(
                    store.mas_background.DBG_MSG_NU.format(
                        self._flt_man.current(),
                        str(self._flt_man.current_pos())
                    )
                )

        def _deco_add(self, deco=None, tag=None):
            """
            Adds deco object to the background.
            NOTE: do NOT use this. This should only be used by the public
            show/hide deco functions as well as other internal stuff.

            NOTE: currently only supports advanceed deco frames

            IN:
                deco - TODO
                tag - ImageTag of the deco to add - This must have an image
                    tag definition for this to work.
            """
            if tag is not None:
                adv_frame = self.get_deco_adf(tag)
                deco = store.mas_deco.get_deco(tag)
                if adv_frame is not None and deco is not None:
                    self._deco_man._adv_add_deco(deco, adv_frame)

        def _deco_rm(self, name):
            """
            Removes deco object from this background.
            NOTE: do NOT use this. This should only be used by the public
            show/hide deco functions as well as other internal stuff

            IN:
                name - tag, either deco name or image tag, of the deco object
                    to remove.
            """
            self._deco_man.rm_deco(name)

        def entry(self, old_background, **kwargs):
            """
            Run the entry programming point
            """
            # populate deco images to show
            change_info = kwargs.get("_change_info", None)
            if change_info is not None:
                self._entry_deco(old_background, change_info)

            if self.entry_pp is not None:
                self.entry_pp(old_background, **kwargs)

        def _entry_deco(self, old_bg, change_info):
            """
            Entry code for deco

            IN:
                old_bg - BG object being changed from
                change_info - MASBackgroundChangeInfo object

            OUT:
                change_info - MASBackgroundChangeInfo object with shows
                    populated.
            """
            for vis_tag in store.mas_deco.vis_store:
                # show all deco objects that are currently visible.
                # and do not have equivalent deco frames.

                new_adf = self.get_deco_adf(vis_tag)
                if new_adf is not None:
                    change_info.shows[vis_tag] = new_adf
                    self._deco_add(tag=vis_tag)

        def exit(self, new_background, **kwargs):
            """
            Run the exit programming point
            """
            change_info = kwargs.get("_change_info", None)
            if change_info is not None:
                self._exit_deco(new_background, change_info)

            if self.exit_pp is not None:
                self.exit_pp(new_background, **kwargs)

        def _exit_deco(self, new_bg, change_info):
            """
            Exit code for deco

            IN:
                new_bg - BG object being changed to
                change_info - MASBackgroundChangeInfo object

            OUT:
                change_info - MASBackgroundChangeInfo object with hides
                    populated.
            """
            for deco_obj, adv_df in self._deco_man.deco_iter_adv():

                new_adf = new_bg.get_deco_adf(deco_obj.name)
                if (
                        not mas_isDecoTagVisible(deco_obj.name)
                        or new_adf is None
                        or new_adf != adv_df
                ):
                    # hide all deco objects that do not have a definition
                    # in the new bg OR have a differing deco frame OR are not in
                    # the vis_store
                    change_info.hides[deco_obj.name] = adv_df
                    self._deco_rm(deco_obj.name)

        def fromTuple(self, data_tuple):
            """
            Loads data from tuple

            IN:
                data_tuple - tuple of the following format:
                    [0]: unlocked property
            """
            self.unlocked = data_tuple[0]

        def toTuple(self):
            """
            Converts this MASWeather object into a tuple

            RETURNS: tuple of the following format:
                [0]: unlocked property
            """
            return (self.unlocked,)

        def get_deco_adf(self, tag):
            """
            Gets MASAdvancedDecoFrame associatd with this tag, if one exists.

            IN:
                tag - tag to get deco frame for

            RETURNS: MASAdvancedDecoFrame object, or None if none exists
            """
            return MASImageTagDecoDefinition.get_adf(self.background_id, tag)

        def getRoom(self, flt, weather=None):
            """
            Gets room associated with the given flt and weather
            This performs lookback and other checks to try and find an image.

            Calling this before init level 0 may result in undefined behavior.

            IN:
                flt - filter to check
                weather - weather to check. If None, we use the current
                    weather
                    (Default: None)

            RETURNS: room image, or None if not found
            """
            precip_type = MASFilterableWeather.getPrecipTypeFrom(weather)

            # get image using normal ways
            img = self._get_image(flt, precip_type)
            if img is None:
                # no image, so we should try lookback
                m_w_m = self._lookback(flt)
                if m_w_m is not None:
                    img = m_w_m.get(precip_type)

            return img

        def getCurrentRoom(self):
            """
            Gets current Room

            RETURNS: Current room image, may be None if this BG is badly built
            """
            return self.getRoom(self._flt_man.current())

        def getDayRoom(self, weather=None):
            """DEPRECATED
            Can't use this anymore since there's no single image that defines
            "day" anymore. It's all filter based.
            See getDayRooms instead
            """
            pass

        def getDayRooms(self, weather=None):
            """
            Gets all day images for a weather.

            IN:
                weather - weather to check. If None, we use the current
                    weather.
                    (Default: None)

            RETURNS: dict of the following format:
                key: flt
                value: day according to the weather.
                NOTE: only filters that have a room with the given weather
                    are returned. No lookback.
            """
            precip_type = MASFilterableWeather.getPrecipTypeFrom(weather)

            results = {}
            for flt in self._flt_man.filters_day():
                img = self._get_image(flt, precip_type)
                if img is not None:
                    results[flt] = img

            return results

        def _get_image(self, flt, precip_type):
            """
            Gets image associated with the given flt and precip_type
            does NOT perform lookback checks.

            IN:
                flt - filter to check
                precip_type - precip type to check

            RETURNS: image, or None if not found
            """
            m_w_m = self.image_map.get(flt)
            if m_w_m is None:
                return None
            return m_w_m.get(precip_type)

        def getNightRoom(self, weather=None):
            """DEPRECATED
            Can't use this anymore since there's no single image that defines
            "night" anymore. It's all filter-based
            See getNightRooms instead
            """
            pass

        def getNightRooms(self, weather=None):
            """
            Gets all night images for a weather.

            IN:
                weather - weather to check. If None, we use the current
                    weather.
                    (Default: None)

            RETURNS: dict of the following format:
                key: flt
                value: night according to the weather.
                NOTE: only filters that have a room with the given weather
                    are returned. No lookback.
            """
            precip_type = MASFilterableWeather.getPrecipTypeFrom(weather)

            results = {}
            for flt in self._flt_man.filters_night():
                img = self._get_image(flt, precip_type)
                if img is not None:
                    results[flt] = img

            return results

        def getRoomForTime(self, weather=None):
            """
            Gets the room for the current time and desired weather

            NOTE: if you just want current room to use, use getCurrentRoom.

            IN:
                weather - get the room bg for the time and weather
                (Default: current weather)

            RETURNS: room image for the current weather and time
            """
            return self.getRoom(self._flt_man.current(), weather)

        def isChangingRoom(self, old_weather, new_weather):
            """
            Checks if the room would change because of a change in weather

            IN:
                old_weather - weather to start from
                new_weather - weather to change to

            RETURNS: true if the room would change, False otherwise
            """
            curr_flt = self._flt_man.current()
            return (
                self._get_image(curr_flt, old_weather.precip_type)
                != self._get_image(curr_flt, new_weather.precip_type)
            )

        def isFltDay(self, flt=None):
            """
            Checks if the given filter is considered a "day" filter according
            to this background.

            IN:
                flt - filter to check
                    if None, we use the current filter

            RETURNS: True if flt is a "day" filter according to this bg,
                False if night filter, None if not associated with this BG
            """
            if flt is None:
                flt = store.mas_sprites.get_filter()

            return self._flt_man.is_flt_day(flt)

        def isFltNight(self, flt=None):
            """
            Checks if the given filter is considered a "night" filter according
            to this background.

            IN:
                flt - filter to check
                    if None, we use the current filter

            RETURNS: True if flt is a "night" filter according to this BG,
                False if day filter, None if not associated with this BG.
            """
            flt_res = self.isFltDay(flt)
            if flt_res is not None:
                return not flt_res
            return None

        def _lookback(self, flt):
            """
            Gets MASWeatherMap for a filter, using lookback

            IN:
                flt - filter to check

            RETURNS: MASWeatherMap, or None if not found
            """
            return self.image_map.get(self._flt_img_map.get(flt))

        def progress(self):
            """
            Progresses the filter.
            If update was called before this, then we only run the global
            filter change progpoint if there was a filter change.

            RETURNS: the new filter
            """
            if store.mas_background.dbg_log:
                store.mas_utils.writelog("\nCalled from - prog\n")
                if store.mas_background.dbg_log_st:
                    store.mas_utils.writestack()

                store.mas_utils.writelog(
                    store.mas_background.DBG_MSG_C.format(
                        self._flt_man.current(),
                        str(self._flt_man.current_pos())
                    )
                )

            try:
                new_flt = self._flt_man.progress()
            except Exception as e:
                # in this case, we don't know what happened, but we got
                # screwed. log out state of the flt man as well as the
                # traceback
                store.mas_background.log_bg(
                    self,
                    store.mas_utils.sys.exc_info()
                )

                # reset the manager to defualt indexes. Next time progress
                # is called will hopefully update without error
                self._flt_man.reset_indexes()
                new_flt = self._flt_man.current()

            if store.mas_background.dbg_log:
                store.mas_utils.writelog(
                    store.mas_background.DBG_MSG_N.format(
                        new_flt,
                        self._flt_man.current(),
                        str(self._flt_man.current_pos())
                    )
                )

            if new_flt is not None:
                return new_flt

            # if we had an issue with filter progression OR if we didn't get
            # a filter back, we'll return a fallback of the first filter
            # available in the filter manager. If that doesn't work,
            # then its forever daytime (FLT_DAY)

            flts = self._flt_man.filters()
            if len(flts) > 0:
                new_flt = flts[0]
                if new_flt is not None:
                    return new_flt

            return store.mas_sprites.FLT_DAY # should exist for every sprite

        def register_deco_tag(self, tag, adv_deco_frame):
            """
            Registers an advanced deco frame for the given tag. Analogous to
            MASImageTagDecoDefinition.register_img, except bg_id is provided
            by this BG object.

            NOTE: this is NOT required if you already used
                MASImageTagDefinition to define the associated tags.

            IN:
                tag - tag to register
                adv_deco_frame - the MASAdvancedDecoFrame to register
            """
            MASImageTagDecoDefinition.register_img(
                tag,
                self.background_id,
                adv_deco_frame
            )

        def update(self, curr_time=None):
            """
            Updates the internal indexes.
            NOTE: this will NOT call any progpoints. Call progress after this
                to run (some) progpoints if needed.
            NOTE: IF YOU PLAN TO CALL BUILD BEFORE THIS, use buildupdate
                instead.

            IN:
                curr_time - datetime.time object to update internal indexes to
                    if None, then we use current.
                    (Default: None)
            """
            if store.mas_background.dbg_log:
                store.mas_utils.writelog("\nCalled from - upd:\n")
                if store.mas_background.dbg_log_st:
                    store.mas_utils.writestack()

                store.mas_utils.writelog(
                    store.mas_background.DBG_MSG_C.format(
                        self._flt_man.current(),
                        str(self._flt_man.current_pos())
                    )
                )

            self._flt_man.update(curr_time)

            if store.mas_background.dbg_log:
                store.mas_utils.writelog(
                    store.mas_background.DBG_MSG_NU.format(
                        self._flt_man.current(),
                        str(self._flt_man.current_pos())
                    )
                )

        def verify(self):
            """
            Verifies all internal filter and weather data is valid.
            Raises exception upon errors.
            Assumed to be called at least at init level 0
            """
            self._flt_man.verify()
            self._verify_img_flts(self._flt_man._day_filters.keys())
            self._verify_img_flts(self._flt_man._night_filters.keys())

        def _verify_img_flts(self, flts):
            """
            Verifies that at least one image exists for the given flts.
            Also organizes filters that have a default image

            Raises an exception if no images found

            IN:
                flts - list of filters to check
            """
            img_found = False
            for flt in flts:
                m_w_m = self.image_map.get(flt)
                if m_w_m is not None:
                    img = m_w_m.get(store.mas_weather.PRECIP_TYPE_DEF)
                    if img is not None:
                        img_found = True
                        self._flt_img_anc[flt] = []
                        return

            if not img_found:
                raise Exception("No images found for these filters")


#Helper methods and such
init -20 python in mas_background:
    import store
    BACKGROUND_MAP = {}
    BACKGROUND_RETURN = "Nevermind"
    dbg_log = False
    dbg_log_st = False
    DBG_MSG_C = "\nCurrent: {0} | {1}\n"
    DBG_MSG_N = "\nNew: ret: {0} | {1} | {2}\n"
    DBG_MSG_NU = "\nNew: {0} | {1}\n"


    class MASBackgroundChangeInfo(object):
        """
        Encapsulation class that knows the information needed for a bg change
        to go smoothly.

        PROPERTIES:
            hides - dict of image tags and MASAdvancedDecoFrames to hide
            shows - dict of image tags and MASAdvancedDecoFrames to show
        """

        def __init__(self, hides=None, shows=None):
            """
            Constructor

            IN:
                hides - dict of image tags and MASAdvancedDecoFrames to
                    hide in the dissolve
                    (Default: None)
                shows - dict of image tags and MASAdvancedDecoFrames to
                    show in the dissolve
                    (Default: None)
            """
            if hides is None:
                hides = {}
            if shows is None:
                shows = {}

            self.hides = hides
            self.shows = shows

        def __repr__(self):
            """
            Returns description of this object
            """
            return "<BackgroundChangeInfo: (hides: {0}, shows: {1})>".format(self.hides, self.shows)

        def __len__(self):
            return len(self.hides) + len(self.shows)

    def build():
        """
        Builds all background objects using current time settings.
        """
        for flt_bg in BACKGROUND_MAP.itervalues():
            flt_bg.build()


    def buildupdate():
        """
        Builds all background objects and updates current time settings.
        This properly saves prev_flt.
        """
        prev_flt = store.mas_current_background._flt_man.current()
        build()
        store.mas_current_background.update()
        store.mas_current_background._flt_man._prev_flt = prev_flt


    def default_MBGFM():
        """
        Generates a MASBackgroundFilterManager using the default
        (aka pre0.11.3) settings.

        RETURNS: MASBackgroundFilterManager object
        """
        return store.MASBackgroundFilterManager(
            store.MASBackgroundFilterChunk(
                False,
                None,
                store.MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_NIGHT,
                    60
                )
            ),
            store.MASBackgroundFilterChunk(
                True,
                None,
                store.MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_DAY,
                    60
                )
            ),
            store.MASBackgroundFilterChunk(
                False,
                None,
                store.MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_NIGHT,
                    60
                )
            ),
        )


    def loadMBGData():
        """
        Loads persistent MASBackground data into the weather map

        ASSUMES: background map is already filled
        """
        if store.persistent._mas_background_MBGdata is None:
            return

        for mbg_id, mbg_data in store.persistent._mas_background_MBGdata.iteritems():
            mbg_obj = BACKGROUND_MAP.get(mbg_id, None)
            if mbg_obj is not None:
                mbg_obj.fromTuple(mbg_data)

    def saveMBGData():
        """
        Saves MASBackground data from weather map into persistent
        """
        for mbg_id, mbg_obj in BACKGROUND_MAP.iteritems():
            store.persistent._mas_background_MBGdata[mbg_id] = mbg_obj.toTuple()

    def getUnlockedBGCount():
        """
        Gets the number of unlocked backgrounds
        """
        unlocked_count = 0
        for mbg_obj in BACKGROUND_MAP.itervalues():
            unlocked_count += int(mbg_obj.unlocked)

        return unlocked_count

    def hasXUnlockedBGs(min_amt_unlocked):
        """
        Checks if we have at least min_amt_unlocked bgs unlocked

        IN:
            min_amt_unlocked - minimum number of BGs which should be unlocked to return true
        OUT:
            True if we have at least min_amt_unlocked BGs unlocked, False otherwise
        """
        unlocked_count = 0
        for mbg_obj in BACKGROUND_MAP.itervalues():
            unlocked_count += int(mbg_obj.unlocked)

            #Now check if we've surpassed the minimum
            if unlocked_count >= min_amt_unlocked:
                return True

        return False


    def log_bg(bg_obj, exc_info=None):
        """
        Logs the given BG object to standard bg log

        IN:
            bg_obj - bg object to log
            exc_info - exception info. Should be tuple:
                [0] - exception type
                [1] - exception value
                [2] - traceback
                (Default: None)
        """
        if bg_obj is None:
            return

        bg_log = store.mas_utils.getMASLog("bg_flt", append=True, flush=True)
        if not bg_log.open():
            # could not log, just abort here
            return

        # otherwise log output
        bg_log.raw_write = True

        # NOTE: version should already be written out if this is runtime
        bg_log.write("\n\nBackground Object: {0}\n".format(
            bg_obj.background_id
        ))
        bg_log.write("Filter System:\n\n")
        bg_log.write(str(bg_obj._flt_man))
        bg_log.write("\n\nRaw Filter Manager Data:\n")
        bg_log.write(repr(bg_obj._flt_man))

        if exc_info:
            import traceback

            bg_log.write("\n\n")
            for tb_line in traceback.format_exception(*exc_info):
                bg_log.write(tb_line)


#START: BG change functions
init 800 python:
    def mas_setBackground(_background, **kwargs):
        """
        Sets the initial bg

        Does not do anything if the current bg is same.

        NOTE: We don't handle exit pp's here

        IN:
            _background:
                The background we're changing to.
                Assumes this is already built.

            **kwargs:
                Additional kwargs to send to the prog points
        """
        if _background != mas_current_background:
            global mas_current_background
            old_background = mas_current_background
            mas_current_background = _background
            mas_current_background.entry(old_background, **kwargs)


    def mas_changeBackground(new_background, by_user=None, set_persistent=False, **kwargs):
        """
        changes the background w/o any scene changes. Will not run progpoints
        or do any actual bg changes if the current background is already set to
        the background we are changing to.

        IN:
            new_background:
                The background we're changing to

            by_user:
                True if the user switched the background themselves

            set_persistent:
                True if we want this to be persistent

            **kwargs:
                Additional kwargs to send to the prog points

        RETURNS: MASBackgroundChangeInfo object of the changes that occured.
        """
        if by_user is not None:
            mas_background.force_background = bool(by_user)

        if set_persistent:
            persistent._mas_current_background = new_background.background_id

        change_info = store.mas_background.MASBackgroundChangeInfo()
        kwargs["_change_info"] = change_info

        if new_background != mas_current_background:
            mas_current_background.exit(new_background, **kwargs)
            new_background.update() # NOTE: do not put this in setBackground.
            mas_setBackground(new_background, **kwargs)

        store.mas_is_indoors = store.mas_background.EXP_TYPE_OUTDOOR not in new_background.ex_props

        return change_info


    def mas_startupBackground():
        """
        Sets up the spaceroom to start up in the background you left in if it is unlocked and still exists
        """
        if (
            mas_isMoniEnamored(higher=True)
            and persistent._mas_current_background in store.mas_background.BACKGROUND_MAP
            and mas_getBackground(persistent._mas_current_background).unlocked
        ):
            background_to_set = store.mas_background.BACKGROUND_MAP[persistent._mas_current_background]
            mas_changeBackground(background_to_set, startup=True)

            if background_to_set.disable_progressive:
                store.skip_setting_weather = True

        #If for whatever reason, we are no longer able to use the persistent background now, we reset to spaceroom
        else:
            persistent._mas_current_background = "spaceroom"

    def mas_checkBackgroundChangeDelegate():
        """
        Checks to see if the background change delegate should be locked or unlocked and changes its state accordingly

        Key rule: at least 2 available backgrounds
        """
        if mas_background.getUnlockedBGCount() < 2:
            mas_lockEVL("monika_change_background","EVE")
        else:
            mas_unlockEVL("monika_change_background", "EVE")


    #Just set us to the normal room here
    mas_setBackground(mas_background_def)

#NOTE: This is at init 0 so it can be used for conditionals in events/etc
init python:
    def mas_getBackground(background_id, default=None):
        """
        Gets a MASFilterableBackground by id

        IN:
            background_id - id of the background to get
            default - default to return if not found

        OUT:
            MASFilterableBackground if found, None otherwise
        """
        return store.mas_background.BACKGROUND_MAP.get(background_id, default)

#START: Programming points
init -2 python in mas_background:
    import store
    import store.mas_sprites as mspr


    def run_gbl_flt_change(old_flt, new_flt, curr_time):
        """
        Runs global filter change progpoint, logging for errors

        IN:
            See _gbl_flt_change
        """
        try:
            _gbl_flt_change(old_flt, new_flt, curr_time)
        except Exception as e:
            store.mas_utils.writelog(
                store.MASBackgroundFilterChunk._ERR_PP_STR_G.format(
                    repr(e),
                    old_flt,
                    new_flt
                )
            )


    def _gbl_flt_change(old_flt, new_flt, curr_time):
        """
        Runs when a filter change occurs

        IN:
            old_flt - outgoing filter. Will be None on startup.
            new_flt - incoming filter.
            curr_time - current time as datetime.time
        """
        if new_flt == mspr.FLT_DAY or new_flt == mspr.FLT_NIGHT:
            # allow islands to be shown
            store.mas_unflagEVL(
                "mas_monika_islands",
                "EVE",
                store.EV_FLAG_HFM
            )
            store.mas_unflagEVL(
                "greeting_ourreality",
                "GRE",
                store.EV_FLAG_HFRS
            )
        else:
            # hide islands
            store.mas_flagEVL("mas_monika_islands", "EVE", store.EV_FLAG_HFM)
            store.mas_flagEVL("greeting_ourreality", "GRE", store.EV_FLAG_HFRS)


    def _gbl_chunk_change(old_chunk, new_chunk, curr_time):
        """
        Runs when a chunk change occurs

        IN:
            old_chunk - outgoing chunk, will be None on startup
            new_flt - incoming chunk
            curr_time - current time as datetime.time
        """
        first_flt = new_chunk.first_flt()
        if first_flt == mspr.FLT_DAY or first_flt == mspr.FLT_NIGHT:
            # allow islands to be shown
            store.mas_unflagEVL(
                "mas_monika_islands",
                "EVE",
                store.EV_FLAG_HFM
            )
            store.mas_unflagEVL(
                "greeting_ourreality",
                "GRE",
                store.EV_FLAG_HFRS
            )
        else:
            # hide islands
            store.mas_flagEVL("mas_monika_islands", "EVE", store.EV_FLAG_HFM)
            store.mas_flagEVL("greeting_ourreality", "GRE", store.EV_FLAG_HFRS)


    def _def_background_entry(_old, **kwargs):
        """
        Entry programming point for default background
        """
        if store.seen_event("mas_monika_islands"):
            store.mas_unlockEVL("mas_monika_islands", "EVE")

        #NOTE: We check if _old here because it acts as a check for whether or not we're in the init phase
        if _old:
            #Since these holidays demand a specific weather, we'll set them here
            if store.mas_isO31():
                store.mas_changeWeather(store.mas_weather_thunder, by_user=True)

            elif store.mas_isD25():
                store.mas_changeWeather(store.mas_weather_snow, by_user=True)

        #Weather should always be unlocked for spaceroom
        #This catches the potential of a deleted background which does not support weather
        store.mas_unlockEVL("monika_change_weather", "EVE")

        if store.mas_getEVLPropValue("monika_why_spaceroom", "unlock_date", None):
            store.mas_unlockEVL("monika_why_spaceroom", "EVE")

    def _def_background_exit(_new, **kwargs):
        """
        Exit programming point for default background
        """
        store.mas_lockEVL("mas_monika_islands", "EVE")
        store.mas_lockEVL("monika_why_spaceroom", "EVE")

        #Lock the weather is the background we are changing to does not support it
        #This handles the case where you switch bgs but on startup the entry pp unlocks the weather and it remains unlocked
        if _new.disable_progressive:
            store.mas_lockEVL("monika_change_weather", "EVE")


init -20 python in mas_background:

    # background ID definitions
    # NOTE: you do NOT need to define ids here. Assigning IDs here just
    #   makes it easier for MASImageTagDefintions
    MBG_DEF = "spaceroom"


#START: bg defs
init -1 python:
    mas_current_background = None

    #Default spaceroom
    mas_background_def = MASFilterableBackground(
        # ID
        store.mas_background.MBG_DEF,
        "Spaceroom",

        # mapping of filters to MASWeatherMaps
        MASFilterWeatherMap(
            day=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "monika_day_room",
                store.mas_weather.PRECIP_TYPE_RAIN: "monika_rain_room",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "monika_rain_room",
                store.mas_weather.PRECIP_TYPE_SNOW: "monika_snow_room_day",
            }),
            night=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "monika_room",
                store.mas_weather.PRECIP_TYPE_SNOW: "monika_snow_room_night",
            }),
            sunset=MASWeatherMap({
                store.mas_weather.PRECIP_TYPE_DEF: "monika_ss_room",
                store.mas_weather.PRECIP_TYPE_RAIN: "monika_rain_room_ss",
                store.mas_weather.PRECIP_TYPE_OVERCAST: "monika_rain_room_ss",
                store.mas_weather.PRECIP_TYPE_SNOW: "monika_snow_room_ss",
            }),
        ),

        # filter manager
        MASBackgroundFilterManager(
            MASBackgroundFilterChunk(
                False,
                None,
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_NIGHT,
                    60
                )
            ),
            MASBackgroundFilterChunk(
                True,
                None,
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_SUNSET,
                    60,
                    30*60,
                    10,
                ),
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_DAY,
                    60
                ),
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_SUNSET,
                    60,
                    30*60,
                    10,
                ),
            ),
            MASBackgroundFilterChunk(
                False,
                None,
                MASBackgroundFilterSlice.cachecreate(
                    store.mas_sprites.FLT_NIGHT,
                    60
                )
            )
        ),

        unlocked=True,
        entry_pp=store.mas_background._def_background_entry,
        exit_pp=store.mas_background._def_background_exit,
    )

    #Now load data
    store.mas_background.loadMBGData()


init 1 python in mas_background:

    # verify all backgrounds
    for flt_bg in BACKGROUND_MAP.itervalues():
        flt_bg.verify()

#START: Image definitions
#Spaceroom
image monika_day_room = "mod_assets/location/spaceroom/spaceroom.png"
image monika_room = "mod_assets/location/spaceroom/spaceroom-n.png"
image monika_ss_room = MASFilteredSprite(
    store.mas_sprites.FLT_SUNSET,
    "mod_assets/location/spaceroom/spaceroom.png"
)
#Thanks Orca
image monika_rain_room = "mod_assets/location/spaceroom/spaceroom_rain.png"
image monika_rain_room_ss = MASFilteredSprite(
    store.mas_sprites.FLT_SUNSET,
    "mod_assets/location/spaceroom/spaceroom_rain.png"
)
#Thanks Velius/Orca
image monika_snow_room_day = "mod_assets/location/spaceroom/spaceroom_snow.png"
image monika_snow_room_night = "mod_assets/location/spaceroom/spaceroom_snow-n.png"
image monika_snow_room_ss = "mod_assets/location/spaceroom/spaceroom_ss_snow.png"

#TODO: locking/unlocking of this based on other backgrounds
#START: Location Selector
init 5 python:
    # available only if moni affection is affectionate+
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_change_background",
            category=["location"],
            prompt="Can we go somewhere else?",
            pool=True,
            unlocked=False,
            rules={"no_unlock": None},
            aff_range=(mas_aff.ENAMORED, None)
        ),
        restartBlacklist=True
    )

label monika_change_background:
    m 1hua "Sure!"

    #FALL THROUGH

label monika_change_background_loop:

    show monika 1eua at t21

    $ renpy.say(m, "Where would you like to go?", interact=False)

    python:
        # build menu list
        import store.mas_background as mas_background
        import store.mas_moods as mas_moods

        # we assume that we will always have more than 1
        # default should always be at the top
        backgrounds = [(mas_background_def.prompt, mas_background_def, False, False)]

        if not persistent._mas_o31_in_o31_mode:
            # build other backgrounds list
            other_backgrounds = [
                (mbg_obj.prompt, mbg_obj, False, False)
                for mbg_id, mbg_obj in mas_background.BACKGROUND_MAP.iteritems()
                if mbg_id != "spaceroom" and mbg_obj.unlocked
            ]

            # sort other backgrounds list
            other_backgrounds.sort()

            # build full list
            backgrounds.extend(other_backgrounds)

        # now add final quit item
        final_item = (mas_background.BACKGROUND_RETURN, False, False, False, 20)

    # call scrollable pane
    call screen mas_gen_scrollable_menu(backgrounds, mas_ui.SCROLLABLE_MENU_TXT_MEDIUM_AREA, mas_ui.SCROLLABLE_MENU_XALIGN, final_item)

    $ sel_background = _return

    show monika at t11

    # return value False? then return
    if sel_background is False:
        return "prompt"

    if sel_background == mas_current_background:
        m 1hua "We're here right now, silly."
        m "Try again~"
        jump monika_change_background_loop

    python:
        skip_leadin = mas_background.EXP_SKIP_LEADIN in sel_background.ex_props
        skip_transition = mas_background.EXP_SKIP_TRANSITION in sel_background.ex_props
        skip_outro = mas_background.EXP_SKIP_OUTRO in sel_background.ex_props

    call mas_background_change(sel_background, skip_leadin=skip_leadin, skip_outro=skip_outro, set_persistent=True)
    return

#Generic background changing label, can be used if we wanted a sort of story related change
label mas_background_change(new_bg, skip_leadin=False, skip_transition=False, skip_outro=False, set_persistent=False):
    # otherwise, we can change the background now
    if not skip_leadin:
        m 1eua "Alright!"
        m 1hua "Let's go, [player]!"

    #Little transition
    if not skip_transition:
        hide monika
        scene black
        with dissolve
        pause 2.0

    python:
        #Set persistent
        if set_persistent:
            persistent._mas_current_background = new_bg.background_id

        #Store the old bg for use later
        old_bg = mas_current_background

        #Otherwise, If we're disabling progressive AND hiding masks, weather isn't supported here
        #so we lock to clear
        if new_bg.disable_progressive and new_bg.hide_masks:
            mas_weather.temp_weather_storage = mas_current_weather
            mas_changeWeather(mas_weather_def, new_bg=new_bg)

        else:
            if mas_weather.temp_weather_storage is not None:
                mas_changeWeather(mas_weather.temp_weather_storage, new_bg=new_bg)
                #Now reset the temp storage for weather
                mas_weather.temp_weather_storage = None

            else:
                #If we don't have tempstor, run the startup weather
                mas_startupWeather()

            #Then we unlock the weather sel here
            mas_unlockEVL("monika_change_weather", "EVE")

        #If we've disabled progressive and hidden masks, then we shouldn't allow weather change
        #NOTE: If you intend to force a weather for your background, set it via prog points
        if new_bg.disable_progressive:
            mas_lockEVL("monika_change_weather", "EVE")

        #Finally, change the background
        change_info = mas_changeBackground(new_bg)

    #Now redraw the room
    call spaceroom(scene_change=True, dissolve_all=True, bg_change_info=change_info)

    if not skip_outro:
        m 1eua "Here we are!"
        m "Let me know if you want to go somewhere else, okay?"
    return
