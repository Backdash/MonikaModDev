# Monika's Grammar Tip of the Day (GTOD)
# TIPS
# 0 - Intro
# 1 - Clauses
# 2 - Comma Splices/Run-ons
# 3 - Conjunctions
# 4 - Semicolons
# 5 - Subjects and Objects
# 6 - Active and Passive Voices
# 7 - Who vs. Whom
# 8 - And I vs. And me
# 9 - Apostrophes
# 10 - The Oxford Comma

init 4 python in mas_gtod:
    # to simplify unlocking, lets use a special function to unlock tips
    import datetime
    import store.evhand as evhand

    M_GTOD = "monika_gtod_tip{:0>3d}"

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

        tip_ev = evhand.event_database.get(
            M_GTOD.format(tip_num),
            None
        )

        return (
            tip_ev is not None
            and tip_ev.last_seen is not None
            and tip_ev.timePassedSinceLastSeen_d(datetime.timedelta(days=1))
        )

# gtod intro topic
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gtod_tip000",
            category=["grammar tips"],
            prompt="Can you teach me about grammar?",
            pool=True,
            rules={"bookmark_rule": store.mas_bookmarks_derand.BLACKLIST}
        )
    )

label monika_gtod_tip000:
    m 3eub "Of course I'll teach you about grammar, [player]!"
    m 3hua "It makes me really happy you want to improve your writing skills."
    m 1eub "I've actually been reviewing some books on writing, and I think there are some interesting things we can talk about!"
    m 1rksdla "I'll admit...{w=0.5}it kind of sounds strange to discuss something as specific as grammar."
    m 1rksdlc "I know it's not the most exciting thing that comes up in people's minds."
    m 3eksdld "...Maybe you think of strict teachers, or stuck-up editors..."
    m 3eka "But I think that there's a certain beauty in mastering how you write and eloquently delivering your message."
    m 1eub "So...{w=0.5}starting today, I'll be sharing Monika's Grammar Tip of the Day!"
    m 1hua "Let's improve our writing together, [mas_get_player_nickname()]~"
    m 3eub "We'll start with clauses, the basic building blocks of sentences!"

    # hide the intro topic after viewing
    $ mas_hideEVL("monika_gtod_tip000", "EVE", lock=True, depool=True)

    # enable tip 1
    $ tip_label = "monika_gtod_tip001"
    $ mas_showEVL(tip_label, "EVE", unlock=True, _pool=True)
    $ pushEvent(tip_label,skipeval=True)
    return

##############################################################################
# Actual tips start here
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gtod_tip001",
            category=["grammar tips"],
            prompt="Clauses"
        )
    )

label monika_gtod_tip001:
    m 3eud "You probably know this already, but a clause is a group of words that has a subject and an action, or predicate."
    m 1euc "For the most part, clauses can be sorted into either independent or dependent clauses."
    m 1esd "Independent clauses can stand on their own as sentences, such as in the sentence '{b}I wrote that.{/b}'"
    m 3euc "Dependent clauses, on the other hand, can't stand on their own and usually appear as parts of longer sentences."
    m 3eua "An example of one could be '{b}who saved her.{/b}'"
    m 3eud "There's a subject, '{b}who{/b},' and an action, '{b}saved her{/b},' but of course, the clause can't be a sentence by itself."
    m 1ekbsa "...{w=0.5}I think you know how to finish that sentence, [player]~"
    m 3eub "Okay, that's all for today's lesson. Thanks for listening!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gtod_tip002",
            category=["grammar tips"],
            prompt="Comma Splices and Run-ons",
            pool=True,
            conditional="store.mas_gtod.has_day_past_tip(1)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

label monika_gtod_tip002:
    m 1eua "Do you remember when we talked about clauses, [player]?"
    m 1eud "There's actually a very common mistake that many writers fall into when joining them."
    m 3esc "When you join two independent clauses together, this is called a comma splice."
    m 3esa "Here's an example:{w=0.5} '{b}I visited the park, I looked at the sky, I saw many stars.{/b}"
    m 1eua "This doesn't seem like a problem at first, but you could imagine adding more and more clauses to that sentence..."
    m 3wud "The result would be a mess!"
    m 1esd "'{b}I visited the park, I looked at the sky, I saw many stars, I saw some constellations, one of them looked like a crab{/b}...'{w=0.5} It could go on and on."
    m 1eua "The best way to avoid this mistake is to separate independent clauses with periods, conjunctions, or semicolons."
    m 1eud "A conjunction is basically a word that you use to connect two clauses or phrases together."
    m 3eub "They're a pretty interesting topic on their own, so we can go over them in a future tip!"
    m 3eud "Anyway, taking that example we had earlier, let's add a conjunction and a period to make our sentence flow better..."
    m 1eud "'{b}I visited the park, and I looked at the sky. I saw many stars.{/b}'"
    m 3hua "Much better, don't you think?"
    m 1eub "That's all I have for today, [player]."
    m 3hub "Thanks for listening!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gtod_tip003",
            category=["grammar tips"],
            prompt="Conjunctions",
            pool=True,
            conditional="store.mas_gtod.has_day_past_tip(2)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

label monika_gtod_tip003:
    m 1eub "Okay, [player]! I think it's time we talk about...{w=0.5}conjunctions!"
    m 3esa "Like I said before, conjunctions are words or phrases that bring two ideas together."
    m 3wud "When you think about it, that's a big category! There are so many words we use to accomplish that."
    m 1euc "Just imagine speaking without conjunctions..."
    m 1esc "It would be dull.{w=0.3} You would sound choppy.{w=0.3} These ideas all relate.{w=0.3} We should connect them."
    m 3eua "As you will see, conjunctions are great for combining ideas, and at the same time, they make your writing sound fluid and more similar to how we actually talk."
    m 1eua "Now, let's revisit our earlier example, this time with conjunctions..."
    m 1eub "'{b}It would be dull, and you would sound choppy. Since these ideas all relate, we should connect them.{/b}'"
    m 3hua "Much better, don't you think?"
    m 1esa "Anyway, there are three types of conjunctions:{w=0.5} coordinating, correlative, and subordinating."
    m 1hksdla "Their names may sound a little daunting, but I promise they'll make more sense as we go through them. I'll give you examples as we go along."
    m 1esd "Coordinating clauses bridge two words, phrases, or clauses of the same 'rank' together. This just means that they have to be of the same type...words with words, or clauses with clauses."
    m 3euc "Some common examples include:{w=0.5} '{b}and{/b},' '{b}or{/b},' '{b}but{/b},' '{b}so{/b},' and '{b}yet{/b}.'"
    m 3eub "You can connect independent clauses, {i}and{/i} you can avoid comma splices!"
    m 1esd "Correlative conjunctions are pairs of conjunctions used to connect ideas."
    m 3euc "A few common pairs are:{w=0.5} '{b}either{/b}/{b}or{/b},' '{b}both{/b}/{b}and{/b},' and '{b}whether{/b}/{b}or{/b}.'"
    m 3eub "{i}Whether{/i} you realize it {i}or{/i} not, we use them all the time...like in this sentence!"
    m 1esd "Lastly, subordinating conjunctions bring together independent and dependent clauses."
    m 3eub "As you can imagine, there are many ways we can do that!"
    m 3euc "Examples include:{w=0.5} '{b}although{/b},' '{b}until{/b},' '{b}since{/b},' '{b}while{/b},' and '{b}as long as{/b}.'"
    m 3eub "{i}Since{/i} there are so many, this category of conjunctions is the widest!"
    m 3tsd "Oh, and another thing...{w=0.5} A pretty common misconception is that you shouldn't begin sentences with conjunctions."
    m 3hub "As I just showed you with the last two examples, you definitely can, ahaha!"
    m 1rksdla "But just avoid going overboard with them. Or else you sound a little forced."
    m 1eub "I think that's enough for today, [player]."
    m 3hub "Thanks for listening!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gtod_tip004",
            category=["grammar tips"],
            prompt="Semicolons",
            pool=True,
            conditional="store.mas_gtod.has_day_past_tip(3)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

label monika_gtod_tip004:
    m 1eua "Today we will talk about a rarely used and commonly misunderstood punctuation mark..."
    m 3eub "The semicolon!"
    m 3eua "Some interesting things have been written about semicolons, including this from the author Lewis Thomas..."
    m 1esd "'{i}Sometimes you get a glimpse of a semicolon coming, a few lines farther on, and it is like climbing a steep path through woods and seeing a wooden bench just at a bend in the road ahead{/i}...'"
    m 1esa "'{i}...a place where you can expect to sit for a moment, catching your breath.{/i}'"
    m 1hua "I really appreciate how eloquently he describes something as simple as a punctuation mark!"
    m 1euc "Some people think you can use a semicolon as a substitute for a colon, while others treat it as a period..."
    m 1esd "If you recall our talk on clauses, the semicolon is actually meant to connect two independent clauses."
    m 3euc "For example, if I wanted to keep two ideas together, such as '{b}You're here{/b}' and '{b}I'm happy{/b},' I could write them as..."
    m 3eud "'{b}You're here; I'm happy{/b}' instead of '{b}You're here, and I'm happy{/b}' or '{b}You're here. I'm happy{/b}.'"
    m 1eub "All three sentences convey the same message, but in comparison, '{b}You're here; I'm happy{/b}' connects the two clauses at a happy medium."
    m 1esa "In the end, this always depends on the ideas you want to connect, but I think that Thomas puts it well when you compare them to periods or commas."
    m 1eud "Unlike a period, which opens up to a completely different sentence, or a comma, which shows you there is more to come in the same one..."
    m 3eub "A semicolon really is that in-between, or, as Thomas says, '{i}a place where you can expect to sit for a moment and catch your breath.{/i}'"
    m 1esa "At least this gives you a whole other option; hopefully, you can now make better use of the semicolon when you're writing..."
    m 1hua "Ehehe."
    m 1eub "Okay, that's enough for today, [player]."
    m 3hub "Thanks for listening!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gtod_tip005",
            category=["grammar tips"],
            prompt="Subjects and Objects",
            pool=True,
            conditional="store.mas_gtod.has_day_past_tip(4)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

label monika_gtod_tip005:
    m 1eua "Today we'll talk about subjects and objects, [player]."
    m 1eud "Remember when I told you about clauses having an action and a verb?"
    m 3eub "The object is the person or thing that the subject acts on!"
    m 1eua "So, in the sentence '{b}We watched the fireworks together{/b},' the object would be...{w=0.5}the '{b}fireworks{/b}.'"
    m 3esd "Oh, it's important to note that objects aren't necessary to form complete sentences..."
    m 1eua "The sentence could very well have been, '{b}We watched.{/b}'"
    m 3hksdlb "That's a complete sentence...although it's an ambiguous one, ahaha!"
    m 1eud "There's also nothing that says that the object has to come last, but I'll discuss that in more detail another time."
    m 3esa "Just remember that the subject is doing the action and the object is acted upon."
    m 1eub "Okay, that's all for today..."
    m 3hub "Thanks for listening, [player]! I love."
    m 1eua "..."
    m 1tuu "..."
    m 3hub "You!"
    return "love"

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gtod_tip006",
            category=["grammar tips"],
            prompt="Active and Passive Voices",
            pool=True,
            conditional="store.mas_gtod.has_day_past_tip(5)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

label monika_gtod_tip006:
    m 1eud "[player], do you know about voices in writing?"
    m 3eua "There's the active voice and the passive voice."
    m 3euc "If you remember our talk on subjects and objects, the big difference between the two voices is whether the subject or the object comes first."
    m 1esd "Let's say the subject is '{b}Sayori{/b}' and the object is a '{b}cupcake{/b}.'"
    m 3eud "Here's the sentence in an active voice:{w=0.5} '{b}Sayori ate the last cupcake.{/b}'"
    m 3euc "Here it is again in a passive voice:{w=0.5} '{b}The last cupcake was eaten.{/b}'"
    m 1eub "As you can see, you can use the passive voice to be secretive about the subject yet still have a complete sentence."
    m 1tuu "It's true; you {i}can{/i} use the passive voice to be sneaky!{w=0.5} It does have other uses, though."
    m 3esd "For example, in some careers, people have to use the passive voice to be impersonal."
    m 3euc "Scientists describe experiments with '{b}the results were documented{/b}...' since the important part is their work and not who did it."
    m 1esa "Anyway, for the most part, stick with the active voice for readability and, you know, to directly tell who's doing what."
    m 1eub "I think that's enough for today, [player]."
    m 3hub "Thanks for listening!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gtod_tip007",
            category=["grammar tips"],
            prompt="Who vs. Whom",
            pool=True,
            conditional="store.mas_gtod.has_day_past_tip(6)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

label monika_gtod_tip007:
    m 1eua "Today we will talk about the uses of '{b}who{/b}' and '{b}whom{/b}.'"
    m 3hub "Most of the time, it seems like people just use '{b}who{/b}' without bothering to learn the difference, ahaha."
    m 1esd "The difference is that '{b}who{/b}' refers to a subject, and '{b}whom{/b}' refers to an object."
    m 3eub "It turns out that it's pretty easy to figure out when to use one or the other!"
    m 1euc "'{b}Who{/b}' corresponds to '{b}he{/b}/{b}she{/b}/{b}they{/b}' while '{b}whom{/b}' corresponds to '{b}him{/b}/{b}her{/b}/{b}them{/b}.'"
    m 3eud "Simply replace the possible '{b}who{/b}' or '{b}whom{/b}' with '{b}he{/b}/{b}she{/b}/{b}they{/b}' or '{b}him{/b}/{b}her{/b}/{b}them{/b}.'"
    m 1eua "Only one replacement should make sense, and that should tell you which one to use!"
    m 3eua "Let's take, for example, the title of my poem, {i}The Lady who Knows Everything{/i}."
    m 3esd "If we just look at the clause '{b}who knows everything{/b}' and replace the '{b}who{/b},' we get..."
    m 1esd "'{b}She knows everything{/b}' or '{b}her knows everything{/b}.'"
    m 3euc "Only '{b}she knows everything{/b}' makes sense, so the correct phrase is '{b}who knows everything{/b}.'"
    m 1hksdla "Who said writing was hard?"
    m 1eub "That's all I have for today, [player]."
    m 3hub "Thanks for listening!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gtod_tip008",
            category=["grammar tips"],
            prompt="And I vs. And me",
            pool=True,
            conditional="store.mas_gtod.has_day_past_tip(7)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

label monika_gtod_tip008:
    m 1eua "Last time, we talked about the difference between '{b}who{/b}' and '{b}whom{/b}.'"
    m 1esd "Another couple of words that can be just as confusing to use are '{b}and I{/b}' and '{b}and me{/b}.'"
    m 3etc "Is it '{b}[player] and I went on a date{/b}' or '{b}[player] and me went on a date{/b}?'"
    m 3eud "Just like with '{b}who{/b}' and '{b}whom{/b},' the issue boils down to one of subjects and objects."
    m 1esd "If the speaker is the subject of the sentence, '{b}and I{/b}' is correct."
    m 1euc "Conversely, if the speaker is the object of the sentence, '{b}and me{/b}' is correct."
    m 3eub "Luckily, just like when we talked about '{b}who{/b}' versus '{b}whom{/b},' it turns out there's a simple way to figure out which one is correct!"
    m 1euc "In our example, if you just take out '{b}[player] and{/b}' from the sentence, only one should make sense."
    m 1hua "Let's try it out!"
    m 3eud "The end result is:{w=0.5} '{b}I went on a date{/b}' or '{b}me went on a date{/b}.'"
    m 3eub "Clearly, only the first one makes sense, so it's '{b}[player] and I went on a date{/b}.'"
    m 1tuu "Oh, sorry, [player]...{w=1}did it make you feel left out when I said only '{b}I went on a date{/b}?'"
    m 1hksdlb "Ahaha! Don't worry, I'd never leave you behind."
    m 3eub "Now, on the other hand, if I was the object of the sentence, I would need to use '{b}and me{/b}' instead."
    m 3eua "For example:{w=0.5} '{b}Natsuki asked [player] and me if we liked her cupcakes.{/b}'"
    m 1eub "I hope that helps the next time you come across this situation while writing, [player]!"
    m 3hub "Anyway, that's all for today, thanks for listening!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gtod_tip009",
            category=["grammar tips"],
            prompt="Apostrophes",
            pool=True,
            conditional="store.mas_gtod.has_day_past_tip(8)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

# Note: formatted apostrophes have been used in examples in this tip for clarity. Please DO NOT remove them.
label monika_gtod_tip009:
    if player[-1].lower() == 's':
        $ tempname = player
    else:
        $ tempname = 'Alexis'

    m 1eua "Today we're going to talk about apostrophes. Pretty straightforward, right?"
    m 3eua "Add them to show possession: '{b}Sayori’s fork, Natsuki’s spoon, Yuri’s knife{/b}...'"
    m 1esd "I guess the issue that can come up is when you have to add an apostrophe to a word that ends with an '{b}s{/b}.'"
    m 3eub "For plural words, this is simple; just add the apostrophe at the end:{w=0.5} '{b}monkeys’{/b}.'"
    m 1hksdla "It's pretty clear that '{b}monkey’s{/b},' which would indicate possession belonging to a single monkey, or '{b}monkeys’s{/b}' would be wrong."
    m 1eud "The gray area that comes up is when we bring in people's names, like '{b}Sanders{/b}' or '{b}[tempname]{/b}.'"
    m 1euc "In some style guides I've read, it seems that we usually add an apostrophe and '{b}s{/b}' as usual, with the exception of historical names like '{b}Sophocles{/b}' or '{b}Zeus{/b}.'"
    m 3eub "Personally, I think all that matters here is consistency!"
    m 3esd "If you're going to go with '{b}[tempname]’{/b},' then it's fine as long as you use '{b}[tempname]’{/b}' for the entire text."
    m 1tuu "That matters more than honoring some old Greeks to me."
    m 3eud "One interesting exception is the case of '{b}its{/b}' versus '{b}it’s{/b}.'"
    m 3etc "You would think that for the possessive form of '{b}it{/b}' you would add an apostrophe, making it '{b}it’s{/b},' right?"
    m 3euc "Normally this would be correct, but in this case the possessive form of '{b}it{/b}' is simply '{b}its{/b}.'"
    m 1esd "This is because '{b}it’s{/b}' is reserved for the contracted form of '{b}it is{/b}.'"
    m 1eua "If you're wondering, a contraction is simply a shortened version of a word or words, with an apostrophe indicating where letters have been left out to make the contraction."
    m 1eub "Okay, [player], {i}it's{/i} about time to wrap it up...{w=0.5}I think this lesson has run {i}its{/i} course."
    m 3hub "Ehehe. Thanks for listening!"
    return

init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="monika_gtod_tip010",
            category=["grammar tips"],
            prompt="The Oxford Comma",
            pool=True,
            conditional="store.mas_gtod.has_day_past_tip(9)",
            action=EV_ACT_UNLOCK,
            rules={"no_unlock":None}
        )
    )

label monika_gtod_tip010:
    m 3eud "Did you know there's actually a debate about the placement of a specific comma in a list of three items?"
    m 3eub "This is called the Oxford, or serial, comma, and it's been known to completely change the meaning of a sentence!"
    m 1esa "Let me show you what I mean..."
    m 1hub "With the Oxford comma, I would say '{b}I love [player], reading, and writing.{/b}'"
    m 1eua "Without the Oxford comma, I would say '{b}I love [player], reading and writing.{/b}'"
    m 3eud "The confusion lies in whether I'm referring to loving three separate things, or if I'm referring to just loving you when you read and write."
    m 3hub "Of course, both of those meanings are true, so there's no confusion there for me, ahaha!"
    m 1eua "That's all I have for today, [player]."
    m 3hub "Thanks for listening!"
    return
