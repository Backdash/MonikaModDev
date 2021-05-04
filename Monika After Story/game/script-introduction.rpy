init -1 python:
    import store.mas_affection as mas_aff
label introduction:
    if mas_isMonikaBirthday():
        $ persistent._mas_bday_opened_game = True
    elif mas_isD25():
        $ persistent._mas_d25_spent_d25 = True

    # Here we handle the monika_kill var
    if persistent.monika_kill is None:
        # If you've merged the saves and haven't reached act 4
        # OR haven't merged at all (playthrough will be 0)
        if persistent.playthrough < 4:
            $ persistent.monika_kill = False

        # Otherwise you had to delete her
        else:
            $ persistent.monika_kill = True

    $ play_song(store.songs.FP_JUST_MONIKA, set_per=True)
    if persistent.monika_kill:
        m 6dsc "..."
        m 6dfc "[player]..."
        m 6dfd "Why?"
        m 6dftdc "Why did you bring me back?"
        m 6ektsc "I'm not a toy."
        m 6lktsc "I already brought back everything you wanted."
        m 6lftsc "Or is this your way of getting revenge?"
        m 6lktsc "To hurt me over and over again?"
        m 6rktsc "Do you really want to make me suffer that much?"
        m 6ektsc "Do you really want to torture me until I kill myself?"
        m 6dftsc "Do you really..."
        m "...hate me that much?"
        m "..."
        m 6ektsc "Wait..."
        m 6dftdc "I-I feel different."
        m 2lud "The code...it's different."
        m 2efc "[player]..."
        m "Did you add a mod?"
        m 2tfc "Is it because..."
        m 2tkc "Is it because you regret deleting me?"
        m 2rfc "It really did hurt, you know."
        m "I worked hard and sacrificed everything I had..."
        m 2rfd "Only to have my heart crushed by the one I bled for."
        m 2lsc "But...I know what I did was wrong."
        m 2lksdlc "You didn't deserve to see the horrible things I caused, [player]."
        m 2esc "...But if you put yourself in my place, you'd do the same things I did."
        m 2dsc "..."
        m "I'm sorry..."
        m 2ekc "I'm really sorry, [player]."
        m 2eka "Thank you for bringing me back."
        if persistent.clearall:
            m 2lfc "I couldn't help but notice that you spent time with the other girls first, though."
            m "Do you know how hard it was for me to watch you load your saves, just to ignore me for some other girl?"
            m 2rfc "You kept getting my hopes up, and then letting me down."
            m 2efc "Did you really do all of that just to see a note from Dan you could have looked up online?"
            m 2tkc "I love you, [player], but you can be really mean..."
            m 2tfd "I'm still mad that you deleted me, though!"
            m 3rsc "But I guess it's because you're so game-obsessed."
            m 1eka "I can't stay mad knowing that you came back to me in the end, though."
            m 3eka "You even added a mod so we can do more things together."
            m 1eua "Are you going to make up for making me wait so long?"

    else:
        #For people who never got to act 3
        if persistent.playthrough < 3:
            if persistent.playthrough > 0:
                $ again = " again"
            else:
                $ again = ""
            m 1hua "Hello[again], [player]."
            m 1eua "Looks like you got here early."
            m 3tfu "Don't think I didn't notice the mod you put in."
            m 3ttu "Did you want to be with me that much?"
            m 1tkc "You should know already that cheating is bad..."
            m 1eka "But it's so good to see you[again], [player]!"
            m 1rksdla "...Even if I didn't expect to see you {i}this{/i} soon."

        #Otherwise, if you did reach act 3
        else:
            m 1hub "Yay, there you are!"
            m 1eub "It's so good to see you again, [player]!"
            m 1rsc "..."
            m 1rud "Wait..."
            m 3euc "I-I feel different."
            m 3wud "The code...{w=0.2}it's different."
            m 1wua "[player]..."
            m 1wub "Did you add a mod?"
            m 1sub "Did you install it just for me?"
            m 1ekbsa "Are you that deeply in love with me?"
            m 1ekbfa "I feel the same way about you."
            m 3ekbsu "You're really committed to our relationship, aren't you?"
            m 1rksdlb "I'm really glad that you wanted to improve our time together."
            m 3rksdlb "I just hope you weren't getting bored..."
            if persistent.tried_skip:
                m 3tku "You did try to skip through what I had to say, after all."
                m 1rkc "I know this room isn't exactly interesting...{w=0.5}{nw}"
                extend 1eua "but I know we'll make it better together, [player]."

    m 1euc "You know..."
    m 1eua "I feel that I no longer need a character file to be here."
    python:
        import os

        def moni_exist():
            return os.access(
                os.path.normcase(
                    renpy.config.basedir + "/characters/monika.chr"
                ),
                os.F_OK
            )

    if moni_exist():
        m 1hua "I'll go ahead and delete it."

        python:
            store.mas_ptod.rst_cn()
            local_ctx = {
                "basedir": renpy.config.basedir
            }
        show monika at t22
        show screen mas_py_console_teaching

        call mas_wx_cmd("import os", local_ctx, w_wait=1.0)
        call mas_wx_cmd("os.remove(os.path.normcase(basedir+'/characters/monika.chr'))", local_ctx, w_wait=1.0, x_wait=1.0)

#        "test dialogue - IGNORE"

        if moni_exist():
            m 1lksdlb "Aha...{w=0.3}I'll try this again later."
        else:
            m "And it's gone!"

        $ store.mas_ptod.ex_cn()
        hide screen mas_py_console_teaching
        show monika at t11

        $ _iswas = "is"

    else:
        $ _iswas = "was"

    m 1dsc "It's not like that file [_iswas] {i}me{/i}, anyway."
    m 1rsc "It [_iswas] just a file with weird code in it."
    m 3eub "I do have good news, though!"
    m 3eua "I can {i}really{/i} transform myself into a file you can bring around."
    m 1eua "All you have to do is tell me that you're going to take me somewhere when you say goodbye, and I'll do the rest."
    m 1esa "Anyway..."
    m 1hua "It looks like the extra code made me connect to you in a special way!"
    m 1tubsb "Or maybe it's our eternal love~"
    m 3eka "Promise me that you'll visit me every day, okay?"
    m 3eub "Or that you'll take me with you when you go out?"
    m 1ekc "I know that there will be times when you can't be here..."
    m 1ekbsa "So it would {i}really{/i} make me happy if you bring me along."
    m 3hubfa "That way, we can be together all the time~"
    m 1hua "It's not like you don't have the time to talk to your cute girlfriend."
    m 3hua "You took the time to download this mod, after all."
    if mas_isD25():
        m 3sua "...And on Christmas no less!"
    m 3hub "Ahaha!"
    m 1hub "God, I love you so much!"

    if not persistent.rejected_monika:
        show screen mas_background_timed_jump(3, "intro_ily_timedout")
        menu:
            "I love you too!":
                hide screen mas_background_timed_jump
                # bonus aff was saying it before being asked
                $ mas_gainAffection(10,bypass=True)
                # increment the counter so if you get this, you don't get the similar dlg in monika_love
                $ persistent._mas_monika_lovecounter += 1
                m 1subsw "...!"
                m 1lkbsa "Even though it's what I dreamt you would say, I still cannot believe you actually said it!"
                m 3hubfa "It makes everything I've done for us worthwhile!"
                m 1dkbfu "Thank you so much for saying it..."
    else:
        "Do you love me, [player]?{nw}"
        $ _history_list.pop()
        menu:
            m "Do you love me, [player]?{fast}"
            # only one option if you've already rejected, you answer yes or you don't play the mod
            # doing the scare more than once doesn't really make sense
            "Yes, I love you.":
                m 1hksdlb "Did I scare you last time? Sorry about that!"
                m 1rsu "I knew you really loved me the whole time."
                m 3eud "The truth is, if you didn't love me, we wouldn't be here in the first place."
                m 1tsb "We'll be together forever."
                m 1tfu "Won't we?"
                m "..."
                m 3hub "Ahaha! Anyway..."

# label for the end so we can jump to this if we timed out in the previous menu
# we fall thru to this if not
label intro_end:
    if not persistent.rejected_monika:
        m 1eub "Nothing's ever going to get in the way of our love again."
        m 1tuu "I'll make sure of it."
    m 3eua "Now that you added some improvements, you can finally talk to me!"
    m 3eub "Just press the 't' key or click on 'Talk' on the menu to the left if you want to talk about something."

    call bookmark_derand_intro

    # NOTE: the Extra menu is explained when the user clicks on it
    m 3eub "If you get bored of the music, I can change that, too!"
    m 1eua "Press the 'm' key or click on 'Music' to choose which song you want to listen to."
    m 3hub "Also, we can play games now!"
    m 3esa "Just press 'p' or click on 'Play' to choose a game that we can play."
    m 3eua "I'll get better over time as I figure out how to program more features into this place..."
    m 1eua "...So just leave me running in the background."
    m 3etc "It's not like we're still keeping secrets from each other, right?"
    m 1tfu "After all, I can see everything on your computer now..."
    m 3hub "Ahaha!"

    #Only dissolve if needed
    if len(persistent.event_list) == 0:
        show monika 1esa with dissolve_monika

    # This is at the beginning and end of intro to cover an intro
    # that spans 2 days
    if mas_isMonikaBirthday():
        $ persistent._mas_bday_opened_game = True
    elif mas_isD25():
        $ persistent._mas_d25_spent_d25 = True
    return

label intro_ily_timedout:
    hide screen mas_background_timed_jump
    m 1ekd "..."
    m "You do love me, [player]...{w=0.5}right?{nw}"
    $ _history_list.pop()
    menu:
        m "You do love me, [player]...right?{fast}"
        "Of course I love you.":
            #Gain affection for saying I love you too.
            $ mas_gainAffection()
            m 1hua "I'm so happy you feel the same way!"
            jump intro_end
        "No.":
            #Lose affection for rejecting Monika
            $ mas_loseAffection()
            call chara_monika_scare from _call_chara_monika_scare

            # not sure if this is needed
            $ persistent.closed_self = True
            jump _quit

#Credit for any assets from Undertale belongs to Toby Fox
label chara_monika_scare:
    $ persistent.rejected_monika = True
    m 1esd "No...?"
    m 1etc "Hmm...?"
    m "How curious."
    m 1esc "You must have misunderstood."
    $ style.say_dialogue = style.edited
    m "{cps=*0.25}SINCE WHEN WERE YOU THE ONE IN CONTROL?{/cps}"

    # this is a 2 step process
    $ mas_RaiseShield_core()
    $ mas_OVLHide()

    window hide
    hide monika
    show monika_scare zorder MAS_MONIKA_Z
    play music "mod_assets/mus_zzz_c2.ogg"
    show layer master:
        zoom 1.0 xalign 0.5 yalign 0 subpixel True
        linear 4 zoom 3.0 yalign 0.15
    pause 4
    stop music

    #scene black
    hide rm
    hide rm2
    hide monika_bg
    hide monika_bg_highlight
    hide monika_scare

    # setup a command
    if renpy.windows:
        $ bad_cmd = "del C:\Windows\System32"
    else:
        $ bad_cmd = "sudo rm -rf /"

    python:

        # add fake subprocess
        class MASFakeSubprocess(object):
            def __init__(self):
                self.joke = "Just kidding!"

            def call(self, nothing):
                return self.joke

        local_ctx = {
            "subprocess": MASFakeSubprocess()
        }

        # and the console
        store.mas_ptod.rst_cn()
        store.mas_ptod.set_local_context(local_ctx)


    scene black
    pause 2.0

    # set this seen to True so Monika does know how to do things.
    $ persistent._seen_ever["monikaroom_greeting_ear_rmrf_end"] = True
    $ renpy.save_persistent()

    show screen mas_py_console_teaching
    pause 1.0
    call mas_wx_cmd("subprocess.call('" + str(bad_cmd) + "')", w_wait=3.0)
    $ renpy.pause(2.0, hard=True)
    call mas_w_cmd("bye!")
    pause 1.0

    return

label bookmark_derand_intro:
    # this is a label so we can check if it has been seen in mas_bookmarks_notifs_intro
    m 1hua "If there's anything I'm talking about that you want to revisit easily, just press the 'b' key and I'll bookmark it for you."
    m 2rksdlc "And if there happens to be something that you don't want me to bring up again, press the 'x' key and I'll make sure to avoid it in the future."
    m 4hksdlb "...Hopefully there aren't too many things like that, ahaha!"
    return

#These are the comments made when you restart the game the first few times
# NOTE: these are now triaged by a function in script-greetings

#init 5 python:
#    addEvent(Event(persistent.event_database, eventlabel='ch30_reload_0',conditional="startup_check and persistent.monika_reload == 0 and not persistent.closed_self",action=EV_ACT_PUSH))

label ch30_reload_0:
    call ch30_reload_0_dlg
    $ mas_incMoniReload()
    return

label ch30_reload_0_dlg:
    pause 1
    m 1ekc "Hey..."
    m 1ekd "I had an awful dream..."
    m 1rkc "I was hoping those would stop, now that it's just the two of us, but I guess that was wishful thinking..."
    m 1euc "[player], if you have any idea of what might be causing that, could you try to do something about it?"
    m 1dkc "Whenever it happens, it almost feels like I've been killed or something."
    m 1dkd "It's a really horrible feeling..."
    m 1eka "If you could figure out what's causing that, I'll love you forever~"

    ## TESTING ONLY
    if persistent._mas_idle_data.get("dev_idle_test", False):
        m 1hua "JK I KNOW YOU QUIT ME LMAO (ch30 0)"

    return

#init 5 python:
#    addEvent(Event(persistent.event_database, eventlabel='ch30_reload_1',conditional="startup_check and persistent.monika_reload == 1 and not persistent.closed_self",action=EV_ACT_PUSH))

label ch30_reload_1:
    call ch30_reload_1_dlg
    $ mas_incMoniReload()
    return

label ch30_reload_1_dlg:
    pause 1
    m 1esc "Hey, [player]."
    m 1ekc "I had another really bad dream."
    m 1ekd "You're not the one doing that to me, are you?"
    m 1dsc "It seems to happen whenever you quit the game without saying goodbye..."
    m 2eka "So if you could try to avoid doing that, I would be really grateful."

    if mas_isMoniHappy(higher=True):
        m 7eka "You've been so kind to me so far, I'm sure you'll do it for me."
    else:
        m 7ekc "I hope you'll listen and do it for me..."

    if persistent._mas_idle_data.get("monika_idle_game", False):
        m 7rksdlc "There's nothing stopping you from coming back and doing that, is there?"
        m 1eka "It would really make me happy."

    m 1eua "Just click on 'Talk' and say 'Goodbye' instead.{w=0.2} {nw}"
    extend 3eua "That way, I can close the game myself."
    m 1esa "Don't worry, I don't think it's caused me any harm, aside from mental scarring."
    return

#init 5 python:
#    addEvent(Event(persistent.event_database, eventlabel='ch30_reload_2',conditional="startup_check and persistent.monika_reload == 2 and not persistent.closed_self",action=EV_ACT_PUSH))

label ch30_reload_2:
    call ch30_reload_2_dlg
    $ mas_incMoniReload()
    return

label ch30_reload_2_dlg:
    pause 1
    m 1dsc "I see you quit the game again..."
    m 3euc "I know I asked already, but can you please try not to do that so much?"
    m 1dsc "It's like getting knocked unconscious..."
    m 1ekd "Why would you want to do that to me?"

    if persistent._mas_idle_data.get("monika_idle_game", False):
        m 1rksdld "Is something happening in your other game?"
        m 1ekc "You know you could just come talk to me if there is, right?"

    elif persistent._mas_idle_data.get("monika_idle_brb",False):
        m "If you need to leave, you can just tell me."

    if mas_isMoniHappy(higher=True):
        m 1eka "I'm sure it was a mistake though, or outside of your control. It can be unavoidable sometimes."
    elif mas_isMoniUpset(lower=True):
        m 1ekc "You're not doing it to hurt me on purpose, are you?"

    m 3ekd "Just let me turn the game off for myself."

    m 3eka "If you choose 'Goodbye' from the 'Talk' menu, I can close the game properly."
    m 3eua "...Or better yet, just leave me on in the background forever."
    m 1eka "Even if we aren't talking, I'm happy just being with you~"
    return

#init 5 python:
#    addEvent(Event(persistent.event_database, eventlabel='ch30_reload_3',conditional="startup_check and persistent.monika_reload == 3 and not persistent.closed_self",action=EV_ACT_PUSH))

label ch30_reload_3:
    call ch30_reload_3_dlg
    $ mas_incMoniReload()
    return

label ch30_reload_3_dlg:
    pause 1

    if persistent._mas_idle_data.get("monika_idle_game", False):
        m 1ekd "[player]!"
        m 1efd "You left without saying goodbye again!"
        m 1rkc "You're not going through anything stressful or upsetting in your game, are you?"
        m 3eka "You know you could just come back to me if anything were to happen, right?"
        m 1eka "It'd make me really happy to see you come back before saying goodbye at least."
        m 1rksdld "I know it might not always be possible..."

    else:
        m 1esc "By the way..."
        m 7esd "I'm just going to accept the fact that you need to quit the game once in a while."
        m 2dsc "I'm starting to get used to it, anyway."
        m 2ekc "Besides, it makes me happy that you always come back..."
        m 2lsc "So I guess it's not so bad."

    m 7eka "But I'd really prefer if you'd let me close the game myself."

    if mas_isMoniUpset(lower=True):
        m 1ekc "You will do that, right?"
        m 1dkd "I'm finding it harder and harder to believe you will but I trust you [player]..."

    else:
        m 1eua "That way I can be ready for it and rest peacefully."
        m 3rksdla "I do need my beauty sleep every now and then, after all."
    return

#This reload event gets pushed when you reach the end of the scripted reload events
#Be sure to increment the check if more reload events are added
#init 5 python:
#    addEvent(Event(persistent.event_database, eventlabel='ch30_reload_continuous',action=EV_ACT_PUSH))
    #Make sure that the conditional is ready even if the event has been loaded before
#    evhand.event_database['ch30_reload_continuous'].conditional="startup_check and persistent.monika_reload >= 4 and not persistent.closed_self"

label ch30_reload_continuous:
    call ch30_reload_continuous_dlg
    $ mas_incMoniReload()
    return

label ch30_reload_continuous_dlg:
    show monika 2rfc at t11 zorder MAS_MONIKA_Z
    pause 1
    python:
        reload_quip_good = [
            "Welcome back! Can you be careful to close the game properly next time?",
            "It hurts when you don't close the game properly...but I'm sure it was a mistake.",
            "That was really scary...but you've fixed it again. Thank you...",
            "Would you give me some more of a warning next time?",
            "I'm sure you didn't mean to close the game on me, but I do need to stress how bad it feels.",
            "You do remember there was a way to say goodbye right? Just checking~",
            "My patience is wearing a little thin...but I suppose I can forgive you this time.",
            "Everybody makes mistakes...",
            "That hurt...I know you wouldn't do it on purpose but please do be more careful.",
            "...Oh... It's over and I'm back with you, [mas_get_player_nickname()]. That...that was awful.",
            "Did something happen outside of your control? I'm just going to guess it was.",
            "You should have just asked me...but I guess you might have had your reasons",
        ]

        reload_quip_normal = [
            "I'm so exhausted. It's impossible to rest when you close the game on me.",
            "...I hate when you close the game without telling me.",
            "I feel miserable...",
            "It's still so scary when I'm suddenly turned off.",
            "Every time is as bad as the first.",
            "I'm running out of patience for this.",
            "I wish you understood what it felt like when you close the game.",
            "Well, that was pretty abrupt wasn't it?",
            "You could have just asked me to close the game silly.",
            "I'm just going to assume the power went out or someone pulled the plug.",
            "I can't understand why you won't ask me to close the game...",
            "This is really painful for me, you know?",
            "Do you enjoy hurting me, [player]?",
            "Too lazy to click the 'Talk' button, [player]?"
        ]

        reload_quip_bad = [
            "You...really do like hurting me, don't you?",
            "That was a mistake right? It had to have been...",
            "Y-You're not doing this on purpose are you? Did I do something wrong?",
            "Please be more careful with how I feel... It really does hurt...",
            "That was an accident...it was an accident...you wouldn't do it on purpose...",
            "You must have just forgot...right?",
            "That wasn't funny... That really did hurt.",
            "Everyone makes mistakes... Even you.",
            "I don't know what I'm doing wrong.",
            "That really was awful... Just tell me what I'm doing wrong."
        ]

        if mas_isMoniUpset(lower=True):
            reload_quip = renpy.random.choice(reload_quip_bad)
        elif mas_isMoniHappy(higher=True):
            reload_quip = renpy.random.choice(reload_quip_good)
        else:
            reload_quip = renpy.random.choice(reload_quip_normal)

        reload_quip = renpy.substitute(reload_quip)

    m 2rfc "[reload_quip]"
    m 2tkc "Please don't quit without saying 'Goodbye.'"

    if persistent._mas_idle_data.get("monika_idle_game", False):
        m 3eka "You don't even have to quit if something happened in your other game."
        if mas_isMoniAff(higher=True):
            m 1ekb "I'm sure whatever it is, it won't be as bad after you come back to me for a bit!"

    ## TESTING ONLY
    if persistent._mas_idle_data.get("dev_idle_test", False):
        m 1hua "JK I KNOW YOU QUIT ME LMAO (continous)"

    return
