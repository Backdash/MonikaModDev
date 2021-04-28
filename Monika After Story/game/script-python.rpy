# Monika's Python Tip of the Day (PTOD)
#
# I probably will be adding many of these, so For the sake of organization
# this is kept separate from script-topics.
#
# NOTE: these are considered pool type events, similar to writing tips
# NOTE: these are also NOT literally once a day. There is a day in between
#   unlocking the next one, though
#
# And to keep the theme, these are 0-indexed
#
# META: Python things to talk about:
# DONE:
#   0 - intro
#   1 - what is python?
#   --- sugestion python compared to other languages/ how does it work
#   --- suggestion mention syntax and probably how to get python maybe separate each part
#   2 - types
#       - numbers and strings, bools and Nones
#   3 - interpreted language
#   5 - comparisons and booleans
#   6 - Variables and assignment
#   8 - Literals
#   9 - Truth Values
#  11 - String Functions and Operations
#
# TODO:
#   4 - Python sytnax ?
#   7 - variable sizes
#   3 - If statement / elif and else
#   4 - while loop
#   5 - for loop
#   6 - functions
#   7 - functions continiued?
#   10 - Evaluation order and short circuting
#   ? - classes (might be too much) -- Definitely too much, we should probably stick to functional programming
#   ? - modules (might be too much) / importing? -- mention importing only, module making is too much
#   ? - lists
#   11 - dict
#   12 - tuples
#   13 - py2 vs py3
#   15 - start talking about renpy
#
#   Implement advanced python tips for users who have some experience (persistent._mas_advanced_py_tips)
#
# Also what about Renpy?
#
# Another NOTE: We should try to make the topics of an adequate lenght otherwise
# we're just going to throw a lot of info that is going to be ignored or forgotten quickly
# I think splitting something in more than one topic may be a good idea
#
## We can assume evhand is already imported

###### tip tree ##############################
# 0 -> 1
# 1 -> 3
# 2 -> 6
# 3 -> 2
# 5 -> 9
# 6 -> 5, 8, 11
##############################################

init 4 python in mas_ptod:
    # to simplify unlocking, lets use a special function to unlock tips
    import datetime
    import store.evhand as evhand

    M_PTOD = "monika_ptod_tip{:0>3d}"

    def has_day_past_tip(tip_num):
        """
        Checks if the tip with the given number has already been seen and
        a day has past since it was unlocked.
        NOTE: by day, we mean date has changd, not 24 hours

        IN:
            tip_num - number of the tip to check

        RETURNS:
            true if the tip has been seen and a day has past since it was
            unlocked, False otherwise
        """
        # as a special thing for devs
        if renpy.game.persistent._mas_dev_enable_ptods:
            return True

        tip_ev = evhand.event_database.get(
            M_PTOD.format(tip_num),
            None
        )

        return (
            tip_ev is not None
            and tip_ev.last_seen is not None
            and tip_ev.timePassedSinceLastSeen_d(datetime.timedelta(days=1))
        )

    def has_day_past_tips(*tip_nums):
        """
        Variant of has_day_past_tip that can check multiple numbers

        SEE has_day_past_tip for more info

        RETURNS:
            true if all the given tip nums have been see nand a day has past
                since the latest one was unlocked, False otherwise
        """
        for tip_num in tip_nums:
            if not has_day_past_tip(tip_num):
                return False

        return True


# The initial event is getting Monika to talk about python
# this must be hidden after it has been completed
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_ptod_tip000",
            category=["python tips"],
            prompt="Can you teach me about Python?",
            pool=True,
            rules={"bookmark_rule": store.mas_bookmarks_derand.BLACKLIST}
        )
    )

label monika_ptod_tip000:
    m 3eub "You want to learn about Python?"
    m 3hub "I'm so happy you asked me!"
    m 1lksdlb "I don't know {i}that{/i} much about programming, but I'll try my best to explain."
    m 1esa "Let's start with what Python even is."

    # hide the intro topic after viewing
    $ mas_hideEVL("monika_ptod_tip000", "EVE", lock=True, depool=True)

    # enable tip 1
    $ tip_label = "monika_ptod_tip001"
    $ mas_showEVL(tip_label, "EVE", unlock=True, _pool=True)
    $ pushEvent(tip_label,skipeval=True)
    return

###############################################################################
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_ptod_tip001",
            category=["python tips"],
            prompt="What is Python?"
        )
    )

label monika_ptod_tip001:

    m 1esa "Python was created by Guido Van Rossum in the early '90s."
    m "It is super versatile, so you can find it in web apps, embedded systems, Linux, and of course..."
    m 1hua "This mod!"
    m 1eua "DDLC uses a visual novel engine called Ren'Py,{w=0.2} which is built off of Python."
    m 3eub "That means if you learn a bit of Python, you can add content to my world!"
    m 1hua "Wouldn't that be great, [mas_get_player_nickname()]?"
    m 3eub "Anyway, I need to mention that there are currently two main versions of Python:{w=0.2} Python2 and Python3."
    m 3eua "These versions are {u}incompatible{/u} with each other because the changes added in Python3 fixed many fundamental design flaws in Python2."
    m "Even though this caused a rift in the Python community,{w=0.2} it's generally agreed that both versions of the language have their own strengths and weaknesses."
    m 1eub "I'll tell you about those differences in another lesson."

    m 1eua "Since this mod runs on a Ren'Py version that uses Python2, I won't be talking about Python3 too often."
    m 1hua "But I'll mention it when it's appropriate."

    m 3eua "That's my lesson for today."
    m 1hua "Thanks for listening!"
    return

###############################################################################
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_ptod_tip002",
            category=["python tips"],
            prompt="Types",
            pool=True,
            conditional="store.mas_ptod.has_day_past_tip(3)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

# PREREQS:
#   interpreted language (tip 3)
label monika_ptod_tip002:
    $ last_seen_is_none = mas_getEVL_last_seen("monika_ptod_tip002") is None
    if last_seen_is_none:
        m 1eua "In most programming languages, data that can be changed or modified by the program has a {i}type{/i} associated with it."
        m 3eua "For example, if some data should be treated as a number, then it will have a numeric type. If some data should be treated as text, then it will have a string type."
        m "There are many types in Python, but today we'll talk about the more basic, or primitive ones."

    $ store.mas_ptod.rst_cn()
    $ local_ctx = dict()
    show monika at t22
    show screen mas_py_console_teaching

    ### numbers
    m 1eua "Python has two types to represent numbers:{w=0.3} {i}integers{/i}, or {b}ints{/b},{w=0.3} and {i}floats{/i}."

    ## integers
    m 1eua "Integers are used to represent whole numbers; basically anything that isn't a decimal."

    call mas_wx_cmd("type(-22)", local_ctx)
    call mas_wx_cmd("type(0)", local_ctx)
    call mas_wx_cmd("type(-1234)", local_ctx)
    call mas_wx_cmd("type(42)", local_ctx)

    ## floats
    m 1eub "Floats are used to represent decimals."
    show monika 1eua

    call mas_wx_cmd("type(0.14)", local_ctx)
    call mas_wx_cmd("type(9.3)", local_ctx)
    call mas_wx_cmd("type(-10.2)", local_ctx)

    ### strings
    m 1eua "Text is represented with {i}string{/i} types."
    m "Anything surrounded in single quotes (') or double quotes (\") are strings."
    m 3eub "For example:"
    show monika 3eua

    call mas_wx_cmd("type('This is a string in single quotes')", local_ctx)
    call mas_wx_cmd('type("And this is a string in double quotes")', local_ctx)

    m 1eksdlb "I know the interpreter says {i}unicode{/i}, but for what we're doing, it's basically the same thing."
    m 1eua "Strings can also be created with three double quotes (\"\"\"), but these are treated differently than regular strings.{w=0.2} I'll talk about them another day."

    ### booleans
    m "Booleans are special types that represent {b}True{/b} or {b}False{/b} values."
    call mas_wx_cmd("type(True)", local_ctx)
    call mas_wx_cmd("type(False)", local_ctx)

    m 1eua "I'll go into more detail about what booleans are and what they are used for in another lesson."

    ### Nones
    m 3eub "Python also has a special data type called a {b}NoneType{/b}.{w=0.2} This type represents the absence of any data."
    m "If you're familiar with other programing languages, this is like a {i}null{/i} or {i}undefined{/i} type."
    m "The keyword {i}None{/i} represents NoneTypes in Python."
    show monika 1eua

    call mas_wx_cmd("type(None)", local_ctx)

    m 1eua "All the types I mentioned here are known as {i}primitive{/i} data types."

    if last_seen_is_none:
        m "Python uses a variety of other types as well, but I think these ones are enough for today."

    $ store.mas_ptod.ex_cn()
    hide screen mas_py_console_teaching
    show monika at t11

    m 1hua "Thanks for listening!"
    return

###############################################################################
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_ptod_tip003", # may change order, you decide on this
            category=["python tips"],
            prompt="An Interpreted Language",
            pool=True,
            conditional="store.mas_ptod.has_day_past_tip(1)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

# PREREQS:
#   What is python (tip 1)
label monika_ptod_tip003:
    m 1eua "Programming languages are usually either compiled or interpreted."
    m "Compiled languages require their code to be converted to a machine-readable format before being executed."
    m 3eub "C and Java are two very popular compiled languages."
    m 1eua "Interpreted languages are converted into a machine-readable format as they are being executed."
    m 3eub "Python is an interpreted language."
    m 1rksdlb "However, different implementations of Python may be compiled, but that's a complicated topic that I may talk about in a later lesson."

    m 1eua "Since Python is an interpreted language, it has a neat interactive thing called an interpreter, which looks like..."

    $ store.mas_ptod.rst_cn()
    $ local_ctx = dict()
    show monika 3eua at t22
    show screen mas_py_console_teaching

    m 3eub "this!"

    m "You can enter Python code directly into here and run it, like so:"
    show monika 3eua

    # base commands shown as starter ones
    call mas_wx_cmd("12 + 3", local_ctx)
    call mas_wx_cmd("7 * 6", local_ctx)
    call mas_wx_cmd("121 / 11", local_ctx)
    # NOTE: add more commands as the user goes thru the tips

    if mas_getEVL_last_seen("monika_ptod_tip003") is None:
        m 1eua "You can do more than just math using this tool, but I'll show you all of that as we go along."

        m 1hksdlb "Unfortunately, since this is a fully functional Python interpreter and I don't want to risk you accidentally deleting me or breaking the game,"
        m "Not that you would{fast}{nw}"
        $ _history_list.pop()
        m 1eksdlb "I can't let you use this.{w=0.3} Sorry..."
        m "If you want to follow along in future lessons, then run a Python interpreter in a separate window."

        m 1eua "Anyway, I'll be using {i}this{/i} interpreter to help with teaching."

    else:
        m 1hua "Pretty cool, right?"

    $ store.mas_ptod.ex_cn()
    hide screen mas_py_console_teaching
    show monika at t11

    m 1hua "Thanks for listening!"
    return

###############################################################################
#init 5 python:
#    addEvent(
#        Event(
#            persistent.event_database,
#            eventlabel="monika_ptod_tip004",
#            category=["python tips"],
#            prompt="What does python code look like?",
#            pool=True,
#            conditional="store.mas_ptod.has_day_past_tip(3)",
#            action=EV_ACT_UNLOCK,
#            rules={"no_unlock":None}
#        )
#    )

# PREREQs:
#   interpreted language (tip 3)
label monika_ptod_tip004:
    # PYTHON SYNTAX
    # TODO, actually ths should be a pre-req for block-based code,
    # as this will talk about indentaiton. However, we could probably
    # have this after the first wave of lessons
    #
    # Python code is incredibly simple to write.

    $ store.mas_ptod.rst_cn()
    $ local_ctx = dict()
    show monika at t22
    show screen mas_py_console_teaching

    # [Show this once]
    # Hopefully
    # [end]
    #
    # Oh well this may be a bit hard to explain here but I'll do my best for you [player]
    # The first thing you need to know is that any line starting with a # is going to
    # be ignored and you can write anything on that line
    # those lines are named comments, and you use them to explain what your code does
    # it's a good practice to comment your code so you don't forget later what it was supposed to do!
    # TODO unfinished and probably will split it in more than just one, also I know I should call it
    # python syntax but I'm making it non programmers friendly
    #
    # TODO: change the prompt to Python Syntax after this has been seen once
    return

###############################################################################
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_ptod_tip005",
            category=["python tips"],
            prompt="Comparisons and Booleans",
            pool=True,
            conditional="store.mas_ptod.has_day_past_tip(6)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

# PREREQS:
#   Variables and Assignment
label monika_ptod_tip005:
    $ store.mas_ptod.rst_cn()
    $ local_ctx = dict()
    $ store.mas_ptod.set_local_context(local_ctx)
    $ last_seen_is_none = mas_getEVL_last_seen("monika_ptod_tip005") is None

    if last_seen_is_none:
        m 1eua "Remember when I was describing different Python types and mentioned booleans?"
        m 1eub "Well, today I'm going into more detail about booleans and how they relate to making comparisons between values."

    m 1eua "Booleans are commonly used in deciding what code to run or setting a flag to note if something happened or not."
    m "When we do comparisons, each expression is evaluated to a boolean."

    if last_seen_is_none:
        m 1eksdlb "This probably makes no sense right now, so I'll pull up the console and show you some examples."

    show monika at t22
    show screen mas_py_console_teaching

    m 3eub "Let's start with some of the basic symbols used in variable-to-variable comparisons."

    call mas_wx_cmd("a = 10")
    call mas_wx_cmd("b = 10")
    call mas_wx_cmd("c = 3")

    m 3eua "To check if two values are equivalent, use two equal signs (==):"
    call mas_wx_cmd("a == b")
    call mas_wx_cmd("a == c")

    m 3eua "To check if two values are not equivalent, use an exclamation mark and an equal sign (!=):"
    call mas_wx_cmd("a != b")
    call mas_wx_cmd("a != c")
    m 3eub "The exclamation mark is often referred to as a logical 'not' operator in other programming languages, so (!=) is read as 'not-equals'."

    m 3eua "To check if a value is greater than or less than another value, use the greater-than (>) or less-than (<) signs, respectively."
    call mas_wx_cmd("a > c")
    call mas_wx_cmd("a < c")

    m 3eub "Greater-than-or-equal-to (>=) and less-than-or-equal-to (<=) also have their own symbols, which,{w=1} unsurprisingly,{w=1} are just the greater-than and less-than signs with equal signs."
    call mas_wx_cmd("a >= b")
    call mas_wx_cmd("a <= b")
    call mas_wx_cmd("a >= c")
    call mas_wx_cmd("a <= c")

    if last_seen_is_none:
        m 1eua "You may have noticed that every comparison returned {b}True{/b} or {b}False{/b}."
        m 1eksdlb "{i}That{/i} is what I meant when I said that comparison expressions evaluate to booleans."

    m 1eua "It's also possible to chain multiple comparison expressions together by using the keywords {b}and{/b} and {b}or{/b}. These are also known as {i}logical operators{/i}."
    m "The {b}and{/b} operator links two comparisons by evaluating the complete expression as {b}True{/b} if both comparisons evaluate to {b}True{/b},{w=0.3} and {b}False{/b} if at least one comparison evaluates to {b}False{/b}."
    m 1hua "Let's go through some examples."

    $ val_a = local_ctx["a"]
    $ val_b = local_ctx["b"]
    $ val_c = local_ctx["c"]

    call mas_w_cmd("a == b and a == c")
    m 3eua "Since 'a' and 'b' are both [val_a], the first comparison evaluates to {b}True{/b}."
    m "'c', however, is [val_c], so the second comparison evaluates to {b}False{/b}."
    m 3eub "Since at least one comparison evaluated to {b}False{/b}, the complete expression evaluates to {b}False{/b}."
    call mas_x_cmd()
    pause 1.0

    call mas_w_cmd("a == b and a >= c")
    m 3eua "In this example, the first comparison again evaluates to {b}True{/b}."
    m "[val_a] is certainly greater-than-or-equal-to [val_c], so the second comparison evaluates to {b}True{/b} as well."
    m 3eub "Since both comparisons evaluated to {b}True{/b}, the complete expression evaluates to {b}True{/b}."
    call mas_x_cmd()
    pause 1.0

    call mas_w_cmd("a != b and a >= c")
    m 3eua "In this example, the first comparison evaluates to {b}False{/b} this time."
    m "Since we immediately have at least one comparison evaluating to {b}False{/b}, it doesn't matter what the second comparison evaluates to."
    m 3eub "We know for sure that the complete expression evaluates to {b}False{/b}."
    call mas_x_cmd()

    m "Same goes for the next example:"
    call mas_wx_cmd("a != b and a == c")

    m 1eub "Again, when using the {b}and{/b} operator, the result is {b}True{/b} if and only if both comparisons evaluate to {b}True{/b}."

    m 1eua "In contrast, the {b}or{/b} operator links two comparisons by evaluating the complete expression as {b}True{/b} if either comparison evaluates to {b}True{/b},{w=0.3} and {b}False{/b} if both comparisons evaluate to {b}False{/b}."
    m 3eua "Let's go through some examples."

    call mas_w_cmd("a == b or a == c")
    m 3eua "This time, since the first comparison evaluates to {b}True{/b}, we don't have to check the second comparison."
    m 3eub "The result of this expression is {b}True{/b}."
    call mas_x_cmd()
    pause 1.0

    call mas_w_cmd("a == b or a >= c")
    m 3eua "Again, the first comparison evaluates to {b}True{/b}, so the complete expression evaluates to {b}True{/b}."
    call mas_x_cmd()
    pause 1.0

    call mas_w_cmd("a != b or a >= c")
    m 3eua "In this case, the first comparison evaluates to {b}False{/b}."
    m "Since [val_a] is greater-than-or-equal-to [val_c], the second comparison evaluates to {b}True{/b}."
    m 3eub "And since at least one comparison evaluated to {b}True{/b}, the complete expression evaluates to {b}True{/b}."
    call mas_x_cmd()
    pause 1.0

    call mas_w_cmd("a != b or a == c")
    m 3eua "We know that the first comparison evaluates to {b}False{/b}."
    m "Since [val_a] is certainly not equal to [val_c], the second comparison also evaluates to {b}False{/b}."
    m 3eub "Since neither comparison evaluated to {b}True{/b}, the complete expression evaluates to {b}False{/b}."
    call mas_x_cmd()
    pause 1.0

    m 3eub "Again, when using the {b}or{/b} operator, the result is {b}True{/b} if either comparison evaluates to {b}True{/b}."

    m 1eua "There is also a third logical operator called the {b}not{/b} operator. Instead of linking multiple comparisons together, this operator inverts the boolean value of a comparison."
    m 3eua "Here's an example of this:"
    call mas_wx_cmd("not (a == b and a == c)")
    call mas_wx_cmd("not (a == b or a == c)")

    m "Note that I'm using parentheses to group the comparisons together. The code in the parentheses is evaluated first, then the result of that comparison is inverted with {b}not{/b}."
    m 1eua "If I drop the parentheses:"
    call mas_wx_cmd("not a == b and a == c")
    m 3eua "We get a different result!{w=0.2} This is because the {b}not{/b} gets applied to the 'a == b' comparison before being linked to the second comparison by the {b}and{/b}."

    m 3eka "Earlier I mentioned that the exclamation point is used as the logical 'not' operator in other programming languages.{w=0.2} Python, however, uses the word 'not' instead for easier readability."

    m 1eua "Lastly, since the comparisons get evaluated to booleans, we can store the result of a comparison in a variable."
    call mas_wx_cmd("d = a == b and a >= c")
    call mas_wx_cmd("d")
    call mas_wx_cmd("e = a == b and a == c")
    call mas_wx_cmd("e")

    m 3eub "And use those variables in comparisons as well!"
    call mas_wx_cmd("d and e")
    m "Since 'd' is {b}True{/b} but 'e' is {b}False{/b}, this expression evaluates to {b}False{/b}."

    call mas_wx_cmd("d or e")
    m "Since 'd' is {b}True{/b}, we know that at least one of the comparisons in this expression is {b}True{/b}. Therefore the complete expression is {b}True{/b}."

    call mas_wx_cmd("not (d or e)")
    m 3eua "We know that the inner expression 'd or e' evaluates to {b}True{/b}. The inverse of that is {b}False{/b}, so this expression evaluates to {b}False{/b}."

    call mas_wx_cmd("d and not e")
    m 3eub "In this case, we know that 'd' is {b}True{/b}."
    m "The 'not' operator is applied to 'e', which inverts its {b}False{/b} value to {b}True{/b}."
    m 3eua "Since both comparison expressions evaluate to {b}True{/b}, the complete expression evaluates to {b}True{/b}."

    m 1eua "Comparisons are used everywhere in every programming language."
    m 1hua "If you ever decide to do programming for a living, you'll find that a lot of your code is just checking if some comparisons are true so you can make your programs do the {i}right{/i} thing."
    m 1eksdla "And even if coding isn't part of your career path, we'll be doing lots of comparisons in future lessons, so be prepared!"

    if last_seen_is_none:
        m 1eua "I think that's enough for today."

    $ store.mas_ptod.ex_cn()
    hide screen mas_py_console_teaching
    show monika at t11
    m 1hua "Thanks for listening!"
    return

###############################################################################
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_ptod_tip006",
            category=["python tips"],
            prompt="Variables and Assignment",
            pool=True,
            conditional="store.mas_ptod.has_day_past_tip(2)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

# PREREQS:
#   Types (tip 2)
label monika_ptod_tip006:
    $ store.mas_ptod.rst_cn()
    $ local_ctx = dict()
    $ num_store = "922"
    $ b_num_store = "323"
    $ last_seen_is_none = mas_getEVL_last_seen("monika_ptod_tip006") is None

    if last_seen_is_none:
        m 1eub "Now that you know about types, I can teach you about variables."

    # variable intro
    m 1eua "Variables represent memory locations that store data."
    m "To create a variable,"

    show monika at t22
    show screen mas_py_console_teaching

    # a number
    m 3eua "you do '{b}symbol_name{/b} = {b}value{/b}', like this:"

    call mas_wx_cmd("a_number = " + num_store, local_ctx)

    m "The symbol 'a_number' now points to a memory location storing the integer [num_store]."
    m "If we enter in the symbol name here,"
    call mas_w_cmd("a_number")
    m 3eub "We can retrieve the value that we stored."
    show monika 3eua
    call mas_x_cmd(local_ctx)

    m "Notice how we associated the symbol 'a_number' to the value [num_store] using an equals (=) sign?"
    m 1eub "That is called assignment, where we take whatever is on the left of the equals sign and point it to, or {i}assign{/i} it, the value of whatever is on the right."

    # b_number
    m 1eua "Assignment is executed in right-to-left order.{w=0.3} To illustrate this, let's create a new variable, 'b_number'."
    call mas_w_cmd("b_number = a_number  -  " + b_num_store)

    m "In assignment, the right side of the equal sign is evaluated first,{w=0.2} then its data type is inferred and an appropriate amount of memory is reserved."
    m "That memory is linked to the symbol on the left via a lookup table."
    m 1eub "When Python encounters a symbol,{w=0.2} it looks that symbol up in the lookup table and replaces it with the value that the symbol was linked to."

    m 3eub "Here, 'a_number' would be replaced with [num_store],{w=0.2} so the expression that would be evaluated and assigned to 'b_number' is '[num_store] - [b_num_store]'."
    show monika 3eua
    call mas_x_cmd(local_ctx)

    m 1eua "We can verify this by entering only the symbol 'b_number'."
    m "This will retrieve the value linked to this symbol in the lookup table and show it to us."
    call mas_wx_cmd("b_number", local_ctx)

    # c number
    m 3eua "Note that if we enter in a symbol that hasn't been assigned anything, Python will complain."
    call mas_wx_cmd("c_number", local_ctx)

    m 3eub "But if we assign this symbol a value..."
    show monika 3eua
    call mas_wx_cmd("c_number = b_number * a_number", local_ctx)
    call mas_wx_cmd("c_number", local_ctx)

    m 1hua "Python is able to find the symbol in the lookup table and won't give us an error."

    m 1eua "The variables we created are all {i}integer{/i} types."
    m "We didn't have to explicitly say that those variables were integers because Python does dynamic typing."
    m 1eub "This means that the Python interpreter infers the type of a variable based on the data you are storing in it."
    m "Other languages, like C or Java, require types to be defined with the variable."
    m "Dynamic typing enables variables in Python to change types during execution,"
    m 1rksdlb "but that is generally frowned upon as it can make your code confusing for others to read."

    if last_seen_is_none:
        m 1eud "Whew!{w=0.2} That was a mouthful!"

    m "Did you understand all that?{nw}"
    $ _history_list.pop()
    menu:
        m "Did you understand all that?{fast}"
        "Yes!":
            m 1hua "Yay!"

        "I'm a bit confused.":
            m 1eksdla "That's okay.{w=0.3} Even though I mentioned symbols and values here, programmers usually just refer to this as creating, assigning, or setting variables."
            m "The symbol / value names are really only useful for hinting at how variables work under the hood, so don't feel bad if you didn't understand it all."
            m 1eua "Just knowing how to work with variables is enough for future lessons."
            m "Anyway..."

    $ store.mas_ptod.ex_cn()
    hide screen mas_py_console_teaching
    show monika at t11

    if last_seen_is_none:
        m 1eua "I think that's enough Python for today."

    m 1hua "Thanks for listening!"
    return


###############################################################################
#init 5 python:
#    addEvent(
#        Event(
#            persistent.event_database,
#            eventlabel="monika_ptod_tip007",
#            category=["python tips"],
#            prompt="Variable Sizes",
#            pool=True,
#            conditional="store.mas_ptod.has_day_past_tip(6)",
#            action=EV_ACT_UNLOCK,
#            rules={"no_unlock":None}
#        )
#    )

# PREREQS:
#   Variables and Assignment (tip 6)
#
label monika_ptod_tip007:
    # TODO

    # integer size
    m 1eua "In C and many other languages, integers are usually stored in 4 bytes."
    m "Python, however, reserves a different amount of memory depending on the size of the integer being stored."
    m 3eua "We can check how much memory our variable 'a_number' stores by borrowing a function from the {i}sys{/i} library."

    call mas_wx_cmd("import sys", local_ctx)
    call mas_wx_cmd("sys.getsizeof(a_number)", local_ctx)
    $ int_size = store.mas_ptod.get_last_line()

    m 1eksdla "I'll talk about libraries and importing later."
    m 1eua "For now, take a look at the number returned by the {i}getsizeof{/i} function."
    m "To store the number [num_store], Python uses [int_size] bytes."

    return

###############################################################################
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_ptod_tip008",
            category=["python tips"],
            prompt="Literals",
            pool=True,
            conditional="store.mas_ptod.has_day_past_tip(6)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

# PREREQS:
#   Variables and Assignment (tip 6)
label monika_ptod_tip008:
    $ store.mas_ptod.rst_cn()
    $ local_ctx = dict()
    $ store.mas_ptod.set_local_context(local_ctx)
    $ last_seen_is_none = mas_getEVL_last_seen("monika_ptod_tip008") is None

    m 1eua "Remember when I showed you how to make variables and assign them values?"
    m 1dsa "Imagine if we dropped the notion of variables and focused on using the values directly in code."
    m 1hua "That is where literals come in. I'll show you what I mean by this with the following demonstration."

    show monika at t22
    show screen mas_py_console_teaching

    call mas_wx_cmd("a = 10")
    m 3eua "Here I made a variable called 'a' and assigned it an integer value of 10."
    m "When I type 'a' into the interpreter..."

    call mas_wx_cmd("a")
    m 3eub "Python looks up the symbol 'a' and finds that it's associated with the value 10, so 10 is shown to us."
    m "If I type in just '10', however..."

    call mas_wx_cmd("10")
    m 3hua "Python still shows us a 10!"
    m 3eua "This happens because Python interprets the '10' as an integer value straight away, without having to look up a symbol and retrieve its value."
    m "Code that Python can interpret into values directly are called {i}literals{/i}."
    m 3eub "All the data types I mentioned in the Types lesson can be written as literals."

    call mas_wx_cmd("23")
    call mas_wx_cmd("21.05")
    m 3eua "These are {b}integer{/b} and {b}float{/b} literals."

    call mas_wx_cmd('"this is a string"')
    call mas_wx_cmd("'this is another string'")
    m "These are {b}string{/b} literals."

    call mas_wx_cmd("True")
    call mas_wx_cmd("False")
    m "These are {b}boolean{/b} literals."

    call mas_wx_cmd("None")
    m "The keyword {i}None{/i} is itself a literal."

    # TODO: lists, dicts

    if last_seen_is_none:
        m 1eua "There are more literals for other types, but I'll mention them when I talk about those types."

    m 1eua "Literals can be used in place of variables when writing code. For example:"

    call mas_wx_cmd("10 + 21")
    call mas_wx_cmd("10 * 5")
    m "We can do math with literals instead of variables."

    call mas_wx_cmd("a + 21")
    call mas_wx_cmd("a * 5")
    m "We can also use literals alongside variables."
    m 1eub "Additionally, literals are great for creating and using data on-the-fly without the overhead of creating unnecessary variables."

    if last_seen_is_none:
        m 1kua "Alright, that's about all I can {i}literally{/i} say about literals."

    $ store.mas_ptod.ex_cn()
    hide screen mas_py_console_teaching
    show monika at t11

    m 1hua "Thanks for listening!"
    return

###############################################################################
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_ptod_tip009",
            category=["python tips"],
            prompt="Truth Values",
            pool=True,
            conditional="store.mas_ptod.has_day_past_tip(5)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

# PREREQS:
#   Comparisons and Booleans (5)
label monika_ptod_tip009:
    $ store.mas_ptod.rst_cn()
    $ local_ctx = dict()
    $ store.mas_ptod.set_local_context(local_ctx)

    if mas_getEVL_last_seen("monika_ptod_tip009") is None:
        m 1eua "When we talked about comparisons and booleans, we used integers as the basis for our comparisons."
        m 1dsa "But..."
        m 3eua "Did you know that every type has its own truth value associated with it?"

    m 1eua "All types have a 'truth value' that can change depending on the value of the type."

    # TODO: when we go over built-in functions, this should be
    # changed to function bool, not keyword
    m "We can check the truth value of a type by using the keyword {b}bool{/b}."

    show monika at t22
    show screen mas_py_console_teaching

    m 3eua "Let's start by taking a look at the truth values for integers."
    call mas_wx_cmd("bool(10)")
    call mas_wx_cmd("bool(-1)")
    m 3eua "All non-zero integers have a truth value of {b}True{/b}."
    call mas_wx_cmd("bool(0)")
    m 3eub "Zero, on the other hand, has a truth value of {b}False{/b}."

    m 1eua "Floats follow the same rules as integers:"
    call mas_wx_cmd("bool(10.02)")
    call mas_wx_cmd("bool(0.14)")
    call mas_wx_cmd("bool(0.0)")

    m 1eua "Now let's look at strings."
    call mas_wx_cmd('bool("string with text")')
    call mas_wx_cmd('bool("  ")')
    m 3eub "A string with text, even if the text is only whitespace characters, has a truth value of {b}True{/b}."
    call mas_wx_cmd('bool("")')
    m "An empty string, or a string with length 0, has a truth value of {b}False{/b}."

    m 1eua "Now let's look at {b}None{/b}."
    call mas_wx_cmd("bool(None)")
    m 1eub "{b}None{/b} always has a truth value of {b}False{/b}."

    # TODO: lists and dicts

    m 1eua "If we do comparisons with these values, the values are evaluated to their truth values before being applied in comparisons."
    m 1hua "Let me show some examples."
    m 3eua "First, I'll set up some variables:"
    call mas_wx_cmd("num10 = 10")
    call mas_wx_cmd("num0 = 0")
    call mas_wx_cmd('text = "text"')
    call mas_wx_cmd('empty_text = ""')
    call mas_wx_cmd("none_var = None")

    m 3eub "And then do several comparisons."
    call mas_wx_cmd("bool(num10 and num0)")
    call mas_wx_cmd("bool(num10 and text)")
    call mas_wx_cmd("bool(empty_text or num0)")
    call mas_wx_cmd("bool(none_var and text)")
    call mas_wx_cmd("bool(empty_text or none_var)")

    m 1eua "Knowing the truth values of different types can be useful in performing certain comparisons more efficiently."
    m 1hua "I'll mention when it's possible to do so when we come across those situations in future lessons."

    $ store.mas_ptod.ex_cn()
    hide screen mas_py_console_teaching
    show monika at t11
    m 1hua "Thanks for listening!"
    return

###############################################################################
#init 5 python:
#    addEvent(
#        Event(
#            persistent.event_database,
#            eventlabel="monika_ptod_tip006",
#            category=["python tips"],
#            prompt="Evaluation Order and Short Circuiting",
# TODO: this should be after if statements.
#            conditional="store.mas_ptod.has_day_past_tip(2)",
#            action=EV_ACT_UNLOCK,
#            rules={"no_unlock":None}
#        )
#    )

label monika_ptod_tip010:
    # evaluation order and short circuting
    return

###############################################################################
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_ptod_tip011",
            category=["python tips"],
            prompt="String Functions and Operations",
            pool=True,
            conditional="store.mas_ptod.has_day_past_tip(6)",
            action=EV_ACT_UNLOCK,
            rules={"no unlock":None}
        )
    )

# PREREQS:
#   Variables and Assignment (6)
label monika_ptod_tip011:
    $ store.mas_ptod.rst_cn()
    $ local_ctx = dict()
    $ store.mas_ptod.set_local_context(local_ctx)
    $ tip_ev = mas_getEV("monika_ptod_tip011")

    # NOTE: strings have already been introduced as a type
    if tip_ev.last_seen is None:
        m 1eua "Today we'll be learning about some common functions and operations that can be applied to strings."

    # NOTE: consider agenda-style introduction?

    # intro to concat
    m 3eua "First, we'll learn about {i}concatenation{/i}."
    m 1eua "As you may remember, strings are used to represent text."
    m 3eua "In the same way that text can be built out of letters and words, strings can be built out of smaller strings.{w} In a programming context, this is known as {i}concatenation{/i}."

    # concat via + 
    m 6eub "Let me show you an example."
    show monika at t22
    show screen mas_py_console_teaching
    call mas_wx_cmd('a = "My name is "')
    call mas_wx_cmd('b = "Monika!"')
    m 3eua "Here I created two variables containing strings.{w} If I add them together with a plus sign..."
    call mas_wx_cmd("c = a + b")
    call mas_wx_cmd("c")
    m 3eub "The two strings have been put together, or {i}concatenated{/i}!"
    m 3eua "The concept of {i}concatenation{/i} is not Python-specific. Many other programming languages also allow strings to be concatenated."

    # concat via *
    m 1eua "A concatenation operation that {i}is{/i} Python-specific is the ability to multiply strings. This may seem weird at first, but it's actually pretty straightforward. For example, if I take the string we made earlier and multiply it by 4..."
    call mas_wx_cmd("m = b * 4")
    call mas_wx_cmd("m")
    m 3eub "We get the string concatenated 4 times. In other words, multiplying a string by a {b}number{/b} will concatenate the string to itself a {b}number{/b} amount of times." 
    m 1efa "However, you can't actually multiply strings by other strings.{w} That will cause an error."
    call mas_wx_cmd("m * m")

    # TODO: after lists have been learned, add something here about .join([])

    # transition to finding things in strings
    m 1eua "Now that we've covered how to create larger strings, let's move on to checking the contents of a string."

    # 'in' operator
    m "The simplest way to check if something is in a string is to use {b}in{/b}."
    m "For example..."
    call mas_wx_cmd('"Mon" in "Monika"')
    m 3eub "This checks if the string 'Mon' is in the string 'Monika'. Since 'Monika' clearly contains the string 'Mon', this expression evaluated to True."
    m 6eua "If we tried this with a string that isn't in 'Monika'..."
    call mas_wx_cmd('"Yuri" in "Monika"')
    m 3eub "then the expression evaluates to False as expected!"

    # in with variables
    m 1eua "Variables can also be used with {b}in{/b}, like so:"
    call mas_wx_cmd('big_string = "Monika is my name"')
    call mas_wx_cmd('my_name = "Monika"')
    call mas_wx_cmd('s_name = "Sayori"')
    call mas_wx_cmd("my_name in big_string")
    call mas_wx_cmd("s_name in big_string")

    # case-sensitive in
    # TODO

    # A brief explanation of case sensitivity
    m 3eud "However, this operator does a {i}case-sensitive{/i} check, and you need to be aware of that."
    m 3eua "For computer 'H' and 'h' are separate characters, and so are words 'Hello' and 'hello'."
    call mas_wx_cmd("'hello' in s")

    # Subscription & slicing introduction
    m 1eua "Now let's get to a bit more advanced operations: {i}subscription{/i} and {i}slicing{/i}."
    m 1eub "It's possible to get symbols from string by their index or even slice strings up because they are internally arrays of characters."

    # Subscription & zero index base warning
    m 3eua "For example, let's get first letter of our string using {i}subscript{/i} operator and a zero as its operand."
    extend "Don't forget that indexes star from zero, not one!"
    call mas_wx_cmd("s[0]")

    # Slicing explanation
    m 1eud "Another operation, {i}slicing{/i}, might need some extra explanation."
    m 3eub "Its similar to subscription, but it takes three operands: start, stop and step, separated by colons."
    m 3eua "Let's get the word 'Hello' from our variable."
    call mas_wx_cmd("s[0:5:1]")
    m 1eua "Actually, since the step operand is 1 we can just omit it, and it will work just as fine."
    call mas_wx_cmd("s[0:5]")
    m 1eua "Sometimes, you might need to slice string till its end - in that case, you can omit stop operand."
    m 3eua "That's how you could get a word 'World' from a string variable we assigned:"
    call mas_wx_cmd("s[6:]")

    # String functions introduction
    m 1hub "I hope you're not getting tired yet. There's something else that's way more powerful than this: string functions!"
    m 3eub "Functions in general are a huge topic to talk about, so we'll get to them a bit later. {w=0.5}{nw}"
    extend 3eua "For now, let's try just the most interesting of those."

    # find function
    m 1eud "We've been subscripting and slicing strings a few moments ago, but what if you don't know where exactly your program needs to begin slicing at?"
    m 3eub "To find location of one string in another, you could use the {i}find{/i} function."
    m 3eua "It takes a string you want to search for as an argument and returns its index:"
    call mas_wx_cmd("s.find('Hello')")
    m 1etc "But what if you are looking for something that's not even there?"
    m 3eud "If string does not contain a substring you are trying to find, this function will return -1."
    m 3eub "So be sure to check its return value before using it as index!"

    # split & partition examples and explanation
    m 1luc "Now let's see some more functions{cps=*0.3}...{/cps} Oh! I think you'll find these two quite useful:"
    call mas_wx_cmd("s.split(' ')")
    call mas_wx_cmd("s.partition(' ')")
    m 3eub "{i}split{/i} function takes a string as an argument, and splits string using it as a delimiter."
    m 1eub "As you can see, it resulted into a list of words in 'Hello World' sentence - because they are separated by spaces."
    m 1eua "{i}partition{/i} function does a similar thing, but it returns a tuple of three strings: string before delimiter, delimiter itself and string after delimiter."

    # is... functions examples & explanation
    m 1eud "But there are way more! For the next few examples, let's add some more variables."
    call mas_wx_cmd("gn = 'DDLC'")
    call mas_wx_cmd("m = 'Monika'")
    call mas_wx_cmd("tw = 'lilmonix3'")
    call mas_wx_cmd("y = '2017'")
    m 1eua "Now, let's experiment with some {i}is...{/i} functions."
    call mas_wx_cmd("m.isalpha()")
    call mas_wx_cmd("tw.isalnum()")
    call mas_wx_cmd("y.isdigit()")
    call mas_wx_cmd("gn.isupper()")
    call mas_wx_cmd("m.istitle()")
    call mas_wx_cmd("tw.islower()")
    m 3eud "You have probably figured out what they do by their names: an 'is' prefix usually means that function
    performs some checks, and the remaining part tells what they are checking for."
    m 1hua "However, some names might be a little confusing, so I'll try to explain them to you."
    m 3eua "{i}isalpha{/i} checks if string contains only letters - {u}alpha{/u}betical characters - and not spaces, digits or punctuation."
    m 3eua "{i}isalnum{/i} checks if string contains letters or digits, but nothing else."
    m 3eua "{i}isdigit{/i}, obviously, checks if string only has {u}digit{/u}s in it."
    m 3eua "{i}isupper{/i} checks if string has all letters {u}upper{/u}case, ignoring non-letters."
    m 3eua "{i}istitle{/i} will return True if string is en{u}title{/u}d, meaning its first letter is uppercase."
    m 3eua "{i}islower{/i} will tell if string has only {u}lower{/u}case letters, and will ignore non-letter characters."

    m 2eub "Phew, I think we're done here. Strings are really something, ahaha."

    $ store.mas_ptod.ex_cn()
    hide screen mas_py_console_teaching
    show monika at t11
    m 1hua "Thanks for listening!"
    return


############################# [CONSOLE] #######################################
# Unfortunately, it's not enough to have monika just talk. Having a working
# python interpreter will make things easier for teaching
#
# NOTE: base the solids off of hangman. That should help us out

image cn_frame = "mod_assets/console/cn_frame.png"
define mas_ptod.font = "mod_assets/font/mplus-1mn-medium.ttf"

# NOTE: Console text:
# style console_text (for regular console text)
# style console_text_console (for the actual typing text)
#   this style has a slow_cps of 30
#
# console_Text font is gui/font/F25_BankPrinter.ttf
style mas_py_console_text is console_text:
    font mas_ptod.font
style mas_py_console_text_cn is console_text_console:
    font mas_ptod.font

# images for console stuff
#image mas_py_cn_sym = Text(">>>", style="mas_py_console_text", anchor=(0, 0), xpos=10, ypos=538)
#image mas_py_cn_txt = ParameterizedText(style="mas_py_console_text_cn", anchor=(0, 0), xpos=75, ypos=538)
#image mas_py_cn_hist = ParameterizedText(style="mas_py_console_text", anchor(0, 1.0), xpos=10, ypos=538)

init -1 python in mas_ptod:
    import store.mas_utils as mas_utils

    # symbol that we use
    SYM = ">>> "
    M_SYM = "... "

    # console history is alist
    cn_history = list()

    # history lenghtr limit
    H_SIZE = 20

    # current line
    cn_line = ""

    # current command, may not be what is shown
    cn_cmd = ""

    # block commands
    blk_cmd = list()

    # block commands stack level
    # increment for each stack level, decrement when dropping out of a
    # stack level
    stack_level = 0

    # stack to handle indent levels
    # this means indent levels that the opening : has
    # first stack level should ALWAYS BE 0
    indent_stack = list()

    # version text
    VER_TEXT_1 = "Python {0}"
    VER_TEXT_2 = "{0} in MAS"

    # line length limit
    LINE_MAX = 66

    # STATEs
    # used when the current line is only 1 line
    STATE_SINGLE = 0

    # used when current line is multi line
    STATE_MULTI = 1

    # used when we are doing block statements
    STATE_BLOCK = 2

    # used when doing multi line in block statements
    STATE_BLOCK_MULTI = 3

    # state when inerpreter is off
    STATE_OFF = 4

    # current state
    state = STATE_SINGLE

    # local context
    local_ctx = dict()

    # short variants of the comonly used commands:
    def clr_cn():
        """
        SEE clear_console
        """
        clear_console()


    def ex_cn():
        """
        SEE exit_console
        """
        exit_console()


    def rst_cn():
        """
        SEE restart_console
        """
        restart_console()


    def w_cmd(cmd):
        """
        SEE write_command
        """
        write_command(cmd)


    def x_cmd(context):
        """
        SEE exec_command
        """
        exec_command(context)


    def wx_cmd(cmd, context):
        """
        Does both write_command and exec_command
        """
        w_cmd(cmd)
        x_cmd(context)


    def write_command(cmd):
        """
        Writes a command to the console

        NOTE: Does not EXECUTE
        NOTE: remove previous command
        NOTE: does NOT append to previously written command (unless that cmd
            is in a block and was executed)

        IN:
            cmd - the command to write to the console
        """
        if state == STATE_OFF:
            return

        global cn_line, cn_cmd, state, stack_level

        if state == STATE_MULTI:
            # this is bad! You should execute the previous command first!
            # in this case, we will clear your current command and reset
            # state back to SINGLE
            cn_cmd = ""
            cn_line = ""
            state = STATE_SINGLE

        elif state == STATE_BLOCK_MULTI:
            # this is bad! you should execute the previous command first!
            # we will do the same that as MULTI did, except a different state
            cn_cmd = ""
            cn_line = ""
            state = STATE_BLOCK

        # we dont indent the command
        # we also dont check for indents
        cn_cmd = str(cmd)

        # pick appropriate shell symbol
        if state == STATE_SINGLE:
            # snigle mode
            sym = SYM

        else:
            # block mode
            sym = M_SYM

        # the prefixed command includes the shell symbol
        prefixed_cmd = sym + cn_cmd

        # break the lines accordingly
        cn_lines = _line_break(prefixed_cmd)

        if len(cn_lines) == 1:
            # dont need to split lines
            cn_line = cn_cmd

        else:
            # we need to split lines

            # everything except the last line goes to the history
            _update_console_history_list(cn_lines[:-1])

            # last line becomes the current line
            cn_line = cn_lines[len(cn_lines)-1]

            if state == STATE_SINGLE:
                # single mode
                state = STATE_MULTI

            else:
                # block mode
                state = STATE_BLOCK_MULTI


    def clear_console():
        """
        Cleares console hisotry and current line

        Also resets state to Single
        """
        global cn_history, cn_line, cn_history, state, local_ctx
        cn_line = ""
        cn_cmd = ""
        cn_history = []
        state = STATE_SINGLE
        local_ctx = {}


    def restart_console():
        """
        Cleares console history and current line, also sets up version text
        """
        global state
        import sys
        version = sys.version

        # first closing paren is where we need to split the version text
        split_dex = version.find(")")
        start_lines = [
#            mas_utils.clean_gui_text(VER_TEXT_1.format(version[:split_dex+1])),
#            mas_utils.clean_gui_text(VER_TEXT_2.format(version[split_dex+2:]))
            VER_TEXT_1.format(version[:split_dex+1]),
            VER_TEXT_2.format(version[split_dex+2:])
        ]

        # clear the console and add the 2 new lines
        clear_console()
        _update_console_history_list(start_lines)

        # turn the console on
        state = STATE_SINGLE


    def exit_console():
        """
        Disables the console
        """
        global state
        state = STATE_OFF


    def __exec_cmd(line, context, block=False):
        """
        Tries to eval the line first, then executes.
        Returns the result of the command

        IN:
            line - line to eval / exec
            context - dict that represnts the current context. should be locals
            block - True means we are executing a block command and should
                skip eval

        RETURNS:
            the result of the command, as a string
        """
        if block:
            return __exec_exec(line, context)

        # otherwise try eval first
        return __exec_evalexec(line, context)


    def __exec_exec(line, context):
        """
        Runs exec on the given line
        Returns an empty string or a string with an error if it occured.

        IN:
            line - line to exec
            context - dict that represents the current context

        RETURNS:
            empty string or string with error message
        """
        try:
            exec(line, context)
            return ""

        except Exception as e:
            return _exp_toString(e)


    def __exec_evalexec(line, context):
        """
        Tries to eval the line first, then executes.
        Returns the result of the command

        IN:
            line - line to eval / exec
            context - dict that represents the current context.

        RETURNS:
            the result of the command as a string
        """
        try:
            return str(eval(line, context))

        except:
            # eval fails, try to exec
            return __exec_exec(line, context)


    def exec_command(context):
        """
        Executes the command that is currently in the console.
        This is basically pressing Enter

        IN:
            context - dict that represnts the current context. You should pass
                locals here.
                If None, then we use the local_ctx.
        """
        if state == STATE_OFF:
            return

        if context is None:
            context = local_ctx

        global cn_cmd, cn_line, state, stack_level, blk_cmd

        ################### setup some initial conditions ################

        # block mode just means we are in a block
        block_mode = state == STATE_BLOCK or state == STATE_BLOCK_MULTI

        # empty line signals end of block (usually)
        empty_line = len(cn_cmd.strip()) == 0

        # ends with colon is special case
        time_to_block = cn_cmd.endswith(":")

        # but a bad block can happen (no text except a single colon)
        bad_block = time_to_block and len(cn_cmd.strip()) == 1

        # if this contains a value, then we executee
        full_cmd = None

        ################## pre-execution setup ###########################

        if empty_line:
            # like enter was pressed with no text

            if block_mode:
                # block mode means we clear a stack level
                __popi()

            else:
                # otherwise, add an empty new line to history, and thats it
                # dont need to execute since nothing will happen
                _update_console_history(SYM)
                cn_line = ""
                cn_cmd = ""
                return

        if bad_block:
            # user entered a bad block
            # we will execute it as a command
            full_cmd = cn_cmd
            stack_level = 0
            blk_cmd = list()

        elif time_to_block:
            # we are going to enter a new block mode
            blk_cmd.append(cn_cmd)

            if not block_mode:
                # we didnt start in block mode
                __pushi(0)

            else:
                # block mode
                pre_spaces = _count_sp(cn_cmd)

                if __peeki() != pre_spaces:
                    # if this colon line does NOT match current indentaion
                    # level then we need to push a new stack
                    __pushi(pre_spaces)

        elif block_mode:
            # in block mode already
            blk_cmd.append(cn_cmd)

            if stack_level == 0:
                # we've cleared all stacks, time to execute block commands
                full_cmd = "\n".join(blk_cmd)
                blk_cmd = list()

        else:
            # otherwise, we must be single mode or single multi

            # setup the command to be entered
            full_cmd = cn_cmd

        ########################## execution ##############################

        # execute command, if available
        if full_cmd is not None:
            result = __exec_cmd(full_cmd, context, block_mode)

        else:
            result = ""

        ################### console history update #########################

        if block_mode and empty_line:
            # we MUST be in block mode to reach here
            output = [M_SYM]

        else:
            # otherwise, use the sym we need
            if state == STATE_SINGLE:
                sym = SYM

            elif state == STATE_BLOCK:
                sym = M_SYM

            else:
                # multi dont need symbols
                sym = ""

            output = [sym + cn_line]

        # if we have any results, we need to show them too
        if len(result) > 0:
            output.append(result)

        # update console history and clear current lines / cmd
        cn_line = ""
        cn_cmd = ""
        _update_console_history_list(output)

        ###################### Post-execution updates ####################

        if bad_block:
            # bad block, means we abort lots of things
            state = STATE_SINGLE
            block_mode = False

        elif time_to_block:
            # new block, incrmenet stack levels, change to block states
            state = STATE_BLOCK
            block_mode = True

        ###################### final state updates ######################

        if (state == STATE_MULTI) or (block_mode and stack_level == 0):
            # no more stacks or in multi mode
            state = STATE_SINGLE

        elif state == STATE_BLOCK_MULTI:
            # multi modes end here
            state = STATE_BLOCK


    def get_last_line():
        """
        Retrieves the last line from the console history

        RETURNS:
            last line from console history as a string
        """
        if len(cn_history) > 0:
            return cn_history[len(cn_history)-1]

        return ""


    def set_local_context(context):
        """
        Sets the local context to the given context.

        Stuff in the old context are forgotten.
        """
        global local_ctx
        local_ctx = context


    def __pushi(indent_level):
        """
        Pushes a indent level into the stack

        IN:
            indent_level - indent to push into stack
        """
        global stack_level
        stack_level += 1
        indent_stack.append(indent_level)


    def __popi():
        """
        Pops indent level from stack

        REUTRNS:
            popped indent level
        """
        global stack_level
        stack_level -= 1

        if stack_level < 0:
            stack_level = 0

        if len(indent_stack) > 0:
            indent_stack.pop()


    def __peeki():
        """
        Returns value that would be popped from stack

        RETURNS:
            indent level that would be popped
        """
        return indent_stack[len(indent_stack)-1]


    def _exp_toString(exp):
        """
        Converts the given exception into a string that looks like
        how python interpreter prints out exceptions
        """
        err = repr(exp)
        err_split = err.partition("(")
        return err_split[0] + ": " + str(exp)


    def _indent_line(line):
        """
        Prepends the given line with an appropraite number of spaces, depending
        on the current stack level

        IN:
            line - line to prepend

        RETURNS:
            line prepended with spaces
        """
        return (" " * (stack_level * 4)) + line


    def _count_sp(line):
        """
        Counts number of spaces that prefix this line

        IN:
            line - line to cound spaces

        RETURNS:
            number of spaces at start of line
        """
        return len(line) - len(line.lstrip(" "))


    def _update_console_history(*new_items):
        """
        Updates the console history with the list of new lines to add

        IN:
            new_items - the items to add to the console history
        """
        _update_console_history_list(new_items)


    def _update_console_history_list(new_items):
        """
        Updates console history with list of new lines to add

        IN:
            new_items - list of new itme sto add to console history
        """
        global cn_history

        # make sure to break lines
        for line in new_items:
            broken_lines = _line_break(line)

            # and clean them too
            for b_line in broken_lines:
#                cn_history.append(mas_utils.clean_gui_text(b_line))
                cn_history.append(b_line)

        if len(cn_history) > H_SIZE:
            cn_history = cn_history[-H_SIZE:]


    def _line_break(line):
        """
        Lines cant be too large. This will line break entries.

        IN:
            line - the line to break

        RETURNS:
            list of strings, each item is a line.
        """
        if len(line) <= LINE_MAX:
            return [line]

        # otherwise, its TOO LONG
        broken_lines = list()
        while len(line) > LINE_MAX:
            broken_lines.append(line[:LINE_MAX])
            line = line[LINE_MAX:]

        # add final line
        broken_lines.append(line)
        return broken_lines


screen mas_py_console_teaching():

    frame:
        xanchor 0
        yanchor 0
        xpos 5
        ypos 5
        background "mod_assets/console/cn_frame.png"

        fixed:
            python:
                starting_index = len(store.mas_ptod.cn_history) - 1
                cn_h_y = 413
                cn_l_x = 41

            # console history
            for index in range(starting_index, -1, -1):
                $ cn_line = store.mas_ptod.cn_history[index]
                text "[cn_line]":
                    style "mas_py_console_text"
                    anchor (0, 1.0)
                    xpos 5
                    ypos cn_h_y
                $ cn_h_y -= 20

            # cursor symbol
            if store.mas_ptod.state == store.mas_ptod.STATE_SINGLE:
                text ">>> ":
                    style "mas_py_console_text"
                    anchor (0, 1.0)
                    xpos 5
                    ypos 433

            elif store.mas_ptod.state == store.mas_ptod.STATE_BLOCK:
                text "... ":
                    style "mas_py_console_text"
                    anchor (0, 1.0)
                    xpos 5
                    ypos 433

            else:
                # multi line statement, dont have the sym at all
                $ cn_l_x = 5

            # current line
            if len(store.mas_ptod.cn_line) > 0:
                text "[store.mas_ptod.cn_line]":
                    style "mas_py_console_text_cn"
                    anchor (0, 1.0)
                    xpos cn_l_x
                    ypos 433

# does a write command and waits
label mas_w_cmd(cmd, wait=0.7):
    $ store.mas_ptod.w_cmd(cmd)
    $ renpy.pause(wait, hard=True)
    return

# does an execute and waits
label mas_x_cmd(ctx=None, wait=0.7):
    $ store.mas_ptod.x_cmd(ctx)
    $ renpy.pause(wait, hard=True)
    return

# does both writing and executing, with waits
label mas_wx_cmd(cmd, ctx=None, w_wait=0.7, x_wait=0.7):
    $ store.mas_ptod.w_cmd(cmd)
    $ renpy.pause(w_wait, hard=True)
    $ store.mas_ptod.x_cmd(ctx)
    $ renpy.pause(x_wait, hard=True)
    return

# does both writing and executing, no x wait
label mas_wx_cmd_noxwait(cmd, ctx=None):
    call mas_wx_cmd(cmd, ctx, x_wait=0.0)
    return
