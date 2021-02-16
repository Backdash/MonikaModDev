#! /usr/bin/env python

import sys
import os
import tempfile
# import logging

class SingleInstanceException(BaseException):
    pass

class SingleInstance:

    """
    If you want to prevent your script from running in parallel just instantiate SingleInstance() class. If is there another instance already running it will throw a `SingleInstanceException`.

    >>> import tendo
    ... me = SingleInstance()

    This option is very useful if you have scripts executed by crontab at small amounts of time.

    Remember that this works by creating a lock file with a filename based on the full path to the script file.

    Providing a flavor_id will augment the filename with the provided flavor_id, allowing you to create multiple singleton instances from the same file. This is particularly useful if you want specific functions to have their own singleton instances.
    """
    def __init__(self, flavor_id=""):
        self.initialized = False
        basename = os.path.splitext(os.path.abspath(sys.argv[0]))[0].replace(
            "/", "-").replace(":", "").replace("\\", "-") + '-%s' % flavor_id + '.lock'
        # os.path.splitext(os.path.abspath(sys.modules['__main__'].__file__))[0].replace("/", "-").replace(":", "").replace("\\", "-") + '-%s' % flavor_id + '.lock'
        self.lockfile = os.path.normpath(
            tempfile.gettempdir() + '/' + basename)

        # logger.debug("SingleInstance lockfile: " + self.lockfile)
        if sys.platform == 'win32':
            try:
                # file already exists, we try to remove (in case previous
                # execution was interrupted)
                if os.path.exists(self.lockfile):
                    os.unlink(self.lockfile)
                self.fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)

            except OSError as e:
                # _type, e, tb = sys.exc_info()
                if e.errno in (13, 17):
                    # logger.error("Another instance is already running, quitting.")
                    raise SingleInstanceException(
                        "Another instance is already running, quitting. If the issue persists, restart your computer or manually delete '{0}'".format(
                            self.lockfile
                        )
                    )
                # print(e.errno)
                raise

        # non Windows
        else:
            import fcntl
            self.fp = open(self.lockfile, 'w')
            self.fp.flush()
            try:
                fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)

            except IOError:
                # logger.warning("Another instance is already running, quitting.")
                raise SingleInstanceException(
                    "Another instance is already running, quitting. If the issue persists, restart your computer or manually delete '{0}'".format(
                        self.lockfile
                    )
                )

        self.initialized = True

    def __del__(self):
        if not self.initialized:
            return

        try:
            if sys.platform == 'win32':
                if hasattr(self, 'fd'):
                    os.close(self.fd)
                    os.unlink(self.lockfile)

            else:
                import fcntl
                fcntl.lockf(self.fp, fcntl.LOCK_UN)
                # os.close(self.fp)
                if os.path.isfile(self.lockfile):
                    os.unlink(self.lockfile)

        except Exception as e:
            # if logger:
            #     logger.warning(e)
            # else:
            #     print("Unloggable error: %s" % e)
            sys.exit(-1)

# def f(name):
#     tmp = logger.level
#     logger.setLevel(logging.CRITICAL)  # we do not want to see the warning
#     try:
#         me2 = SingleInstance(flavor_id=name)  # noqa
#     except SingleInstanceException:
#         sys.exit(-1)
#     logger.setLevel(tmp)
#     pass

# logger = logging.getLogger("tendo.singleton")
# logger.addHandler(logging.StreamHandler())
