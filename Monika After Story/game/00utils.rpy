python early in mas_utils:
    import store
    import os

    # mac logging
    class MASMacLog(renpy.renpy.log.LogFile):
        def __init__(self, name, append=False, developer=False, flush=True):
            """
            `name`
                The name of the logfile, without the .txt extension.
            `append`
                If true, we will append to the logfile. If false, we will truncate
                it to an empty file the first time we write to it.
            `developer`
                If true, nothing happens if config.developer is not set to True.
            `flush`
                Determines if the file is flushed after each write.
            """
            renpy.renpy.log.LogFile.__init__(self, name, append=append, developer=developer, flush=flush)


        def open(self):  # @ReservedAssignment
            if self.file:
                return True

            if self.file is False:
                return False

            if self.developer and not renpy.config.developer:
                return False

            if not renpy.config.log_enable:
                return False

            try:

                home = expanduser("~")
                base = os.path.join(home,".MonikaAfterStory/" )

                if base is None:
                    return False

                fn = os.path.join(base, self.name + ".txt")

                path, filename = os.path.split(fn)
                if not os.path.exists(path):
                    os.makedirs(path)

                if self.append:
                    mode = "a"
                else:
                    mode = "w"

                if renpy.config.log_to_stdout:
                    self.file = real_stdout

                else:

                    try:
                        self.file = codecs.open(fn, mode, "utf-8")
                    except:
                        pass

                if self.append:
                    self.write('')
                    self.write('=' * 78)
                    self.write('')

                self.write("%s", time.ctime())
                try:
                    self.write("%s", platform.platform())
                except:
                    self.write("Unknown platform.")
                self.write("%s", renpy.version())
                self.write("%s %s", renpy.config.name, renpy.config.version)
                self.write("")

                return True

            except:
                self.file = False
                return False

    # A map from the log name to a log object.
    mas_mac_log_cache = { }

    def macLogOpen(name, append=False, developer=False, flush=False):  # @ReservedAssignment
        rv = mas_mac_log_cache.get(name, None)

        if rv is None:
            rv = MASMacLog(name, append=append, developer=developer, flush=flush)
            mas_mac_log_cache[name] = rv

        return rv

    def getMASLog(name, append=False, developer=False, flush=False):
        if renpy.macapp or renpy.macintosh:
            return macLogOpen(name, append=append, developer=developer, flush=flush)
        return renpy.renpy.log.open(name, append=append, developer=developer, flush=flush)

    def logcreate(filepath, append=False, flush=False, addversion=False):
        """
        Creates a log at the given filepath.
        This also opens the log and sets raw_write to True.
        This also adds per version number if desired

        IN:
            filepath - filepath of the log to create (extension is added)
            append - True will append to the log. False will overwrite
                (Default: False)
            flush - True will flush every operation, False will not
                (Default: False)
            addversion - True will add the version, False will not
                You dont need this if you create the log in runtime,
                (Default: False)

        RETURNS: created log object.
        """
        new_log = getMASLog(filepath, append=append, flush=flush)
        new_log.open()
        new_log.raw_write = True
        if addversion:
            new_log.write("VERSION: {0}\n".format(
                store.persistent.version_number
            ))
        return new_log

    def writelog(msg):
        """
        Writes to the mas log if it is open

        IN:
            msg - message to write to log
        """
        if mas_log_open:
            mas_log.write(msg)

    def wtf(msg):
        """
        Wow That Failed
        For logging stuff that should never happen

        IN:
            msg - message to log
        """
        writelog(msg)

    def writestack():
        """
        Prints current stack to log
        """
        writelog("".join(traceback.format_stack()))


    def logrotate(logpath, filename):
        """
        Does a log rotation. Log rotations contstantly increase. We defualt
        to about 2 decimal places, but let the limit go past that

        NOTE: exceptions are logged

        IN:
            logpath - path to the folder containing logs
                NOTE: this is assumed to have the trailing slash
            filename - filename of the log to rotate
        """
        try:
            filelist = os.listdir(logpath)
        except Exception as e:
            writelog("[ERROR] " + str(e) + "\n")
            return

        # log rotation constants
        __numformat = "{:02d}"
        __numdelim = "."

        # parse filelist for valid filenames,
        # also sort them so the largest number is last
        filelist = sorted([
            x
            for x in filelist
            if x.startswith(filename)
        ])

        # now extract only the largest number in this list.
        # NOTE: this is only possible if we have more than one file in the list
        if len(filelist) > 1:
            fname, dot, largest_num = filelist.pop().rpartition(__numdelim)
            largest_num = tryparseint(largest_num, -1)

        else:
            # otherwise
            largest_num = -1

        # now increaese largest num to get the next number we should write out
        largest_num += 1

        # delete whatever file that is if it exists
        new_path = os.path.normcase("".join([
            logpath,
            filename,
            __numdelim,
            __numformat.format(largest_num)
        ]))
        trydel(new_path)

        # and copy our main file over
        old_path = os.path.normcase(logpath + filename)
        copyfile(old_path, new_path)

        # and delete the current file
        trydel(old_path)

    def tryparseint(value, default=0):
        """
        Attempts to parse the given value into an int. Returns the default if
        that parse failed.

        IN:
            value - value to parse
            default - value to return if parse fails
            (Default: 0)

        RETURNS: an integer representation of the given value, or default if
            the given value could not be parsed into an int
        """
        try:
            return int(value)
        except:
            return default

    if renpy.game.persistent._mas_unstable_mode:
        mas_log = getMASLog("log/mas_log", append=True, flush=True)
    else:
        mas_log = getMASLog("log/mas_log")

    mas_log_open = mas_log.open()
    mas_log.raw_write = True
    mas_log.write("VERSION: {0}\n".format(renpy.game.persistent.version_number))
