# pong difficulty changes on win / loss. Determines monika's paddle-movement-cap, the ball's start-speed, max-speed and acceleration.
default persistent._mas_pong_difficulty = 10
# increases the pong difficulty for the next game by the value this is set to. Resets after a finished match.
default persistent._mas_pong_difficulty_change_next_game = 0
# whether the player answered monika he lets her win on purpose
default persistent._mas_pm_ever_let_monika_win_on_purpose = False
# the day at which the difficulty change was initiated
default persistent._mas_pong_difficulty_change_next_game_date = datetime.date.today()

define PONG_DIFFICULTY_CHANGE_ON_WIN            = +1
define PONG_DIFFICULTY_CHANGE_ON_LOSS           = -1
define PONG_DIFFICULTY_POWERUP                  = +5
define PONG_DIFFICULTY_POWERDOWN                = -5
define PONG_PONG_DIFFICULTY_POWERDOWNBIG        = -10

#Triggering the same response twice in a row leads to a different response, not all responses reset this (on purpose)
define PONG_MONIKA_RESPONSE_NONE                                                = 0
define PONG_MONIKA_RESPONSE_WIN_AFTER_PLAYER_WON_MIN_THREE_TIMES                = 1
define PONG_MONIKA_RESPONSE_SECOND_WIN_AFTER_PLAYER_WON_MIN_THREE_TIMES         = 2
define PONG_MONIKA_RESPONSE_WIN_LONG_GAME                                       = 3
define PONG_MONIKA_RESPONSE_WIN_SHORT_GAME                                      = 4
define PONG_MONIKA_RESPONSE_WIN_TRICKSHOT                                       = 5
define PONG_MONIKA_RESPONSE_WIN_EASY_GAME                                       = 6
define PONG_MONIKA_RESPONSE_WIN_MEDIUM_GAME                                     = 7
define PONG_MONIKA_RESPONSE_WIN_HARD_GAME                                       = 8
define PONG_MONIKA_RESPONSE_WIN_EXPERT_GAME                                     = 9
define PONG_MONIKA_RESPONSE_WIN_EXTREME_GAME                                    = 10
define PONG_MONIKA_RESPONSE_LOSE_WITHOUT_HITTING_BALL                           = 11
define PONG_MONIKA_RESPONSE_LOSE_TRICKSHOT                                      = 12
define PONG_MONIKA_RESPONSE_LOSE_LONG_GAME                                      = 13
define PONG_MONIKA_RESPONSE_LOSE_SHORT_GAME                                     = 14
define PONG_MONIKA_RESPONSE_LOSE_EASY_GAME                                      = 15
define PONG_MONIKA_RESPONSE_LOSE_MEDIUM_GAME                                    = 16
define PONG_MONIKA_RESPONSE_LOSE_HARD_GAME                                      = 17
define PONG_MONIKA_RESPONSE_LOSE_EXPERT_GAME                                    = 18
define PONG_MONIKA_RESPONSE_LOSE_EXTREME_GAME                                   = 19

define pong_monika_last_response_id = PONG_MONIKA_RESPONSE_NONE

define played_pong_this_session = False
define mas_pong_taking_break = False
define player_lets_monika_win_on_purpose = False
define instant_loss_streak_counter = 0
define loss_streak_counter = 0
define win_streak_counter = 0
define lose_on_purpose = False
define monika_asks_to_go_easy = False

# Need to be set before every game and be accessible outside the class
define ball_paddle_bounces = 0
define powerup_value_this_game = 0
define instant_loss_streak_counter_before = 0
define loss_streak_counter_before = 0
define win_streak_counter_before = 0
define pong_difficulty_before = 0
define pong_angle_last_shot = 0.0

init:

    image bg pong field = "mod_assets/games/pong/pong_field.png"

    python:
        import random
        import math

        class PongDisplayable(renpy.Displayable):

            def __init__(self):

                renpy.Displayable.__init__(self)

                # Some displayables we use.
                self.paddle = Image("mod_assets/games/pong/pong.png")
                self.ball = Image("mod_assets/games/pong/pong_ball.png")
                self.player = Text(_("[player]"), size=36)
                self.monika = Text(_("Monika"), size=36)
                self.ctb = Text(_("Click to Begin!"), size=36)

                # Sounds used.
                self.playsounds = True
                self.soundboop = "mod_assets/sounds/pong_sounds/pong_boop.wav"
                self.soundbeep = "mod_assets/sounds/pong_sounds/pong_beep.wav"

                # The sizes of some of the images.
                self.PADDLE_WIDTH = 8
                self.PADDLE_HEIGHT = 79
                self.PADDLE_RADIUS = self.PADDLE_HEIGHT / 2
                self.BALL_WIDTH = 15
                self.BALL_HEIGHT = 15
                self.COURT_TOP = 124
                self.COURT_BOTTOM = 654

                # Other variables
                self.CURRENT_DIFFICULTY = max(persistent._mas_pong_difficulty + persistent._mas_pong_difficulty_change_next_game, 0)

                self.COURT_WIDTH = 1280
                self.COURT_HEIGHT = 720

                self.BALL_LEFT = 80 - self.BALL_WIDTH / 2
                self.BALL_RIGHT = 1199 + self.BALL_WIDTH / 2
                self.BALL_TOP = self.COURT_TOP + self.BALL_HEIGHT / 2
                self.BALL_BOTTOM = self.COURT_BOTTOM - self.BALL_HEIGHT / 2

                self.PADDLE_X_PLAYER = 128                                      #self.COURT_WIDTH * 0.1
                self.PADDLE_X_MONIKA = 1152 - self.PADDLE_WIDTH                 #self.COURT_WIDTH * 0.9 - self.PADDLE_WIDTH

                self.BALL_MAX_SPEED = 2000.0 + self.CURRENT_DIFFICULTY * 100.0

                # The maximum possible reflection angle, achieved when the ball
                # hits the corners of the paddle.
                self.MAX_REFLECT_ANGLE = math.pi / 3
                # A bit redundand, but math.pi / 3 is greater than 1, which is a problem.
                self.MAX_ANGLE = 0.9

                # If the ball is stuck to the paddle.
                self.stuck = True

                # The positions of the two paddles.
                self.playery = (self.COURT_BOTTOM - self.COURT_TOP) / 2
                self.computery = (self.COURT_BOTTOM - self.COURT_TOP) / 2

                # The computer should aim at somewhere along the paddle, but
                # not always at the centre. This is the offset, measured from
                # the centre.
                self.ctargetoffset = self.get_random_offset()

                # The speed of Monika's paddle.
                self.computerspeed = 150.0 + self.CURRENT_DIFFICULTY * 30.0

                # Get an initial angle for launching the ball.
                init_angle = random.uniform(-self.MAX_REFLECT_ANGLE, self.MAX_REFLECT_ANGLE)

                # The position, dental-position, and the speed of the ball.
                self.bx = self.PADDLE_X_PLAYER + self.PADDLE_WIDTH + 0.1
                self.by = self.playery
                self.bdx = .5 * math.cos(init_angle)
                self.bdy = .5 * math.sin(init_angle)
                self.bspeed = 500.0 + self.CURRENT_DIFFICULTY * 25

                # Where the computer wants to go.
                self.ctargety = self.by + self.ctargetoffset

                # The time of the past render-frame.
                self.oldst = None

                # The winner.
                self.winner = None

            def get_random_offset(self):
                return random.uniform(-self.PADDLE_RADIUS, self.PADDLE_RADIUS)

            def visit(self):
                return [ self.paddle, self.ball, self.player, self.monika, self.ctb ]

            def check_bounce_off_top(self):
                # The ball wants to leave the screen upwards.
                if self.by < self.BALL_TOP and self.oldby - self.by != 0:

                    # The x value at which the ball hits the upper wall.
                    collisionbx = self.oldbx + (self.bx - self.oldbx) * ((self.oldby - self.BALL_TOP) / (self.oldby - self.by))

                    # Ignores the walls outside the field.
                    if collisionbx < self.BALL_LEFT or collisionbx > self.BALL_RIGHT:
                        return

                    self.bouncebx = collisionbx
                    self.bounceby = self.BALL_TOP

                    # Bounce off by teleporting ball (mirror position on wall).
                    self.by = -self.by + 2 * self.BALL_TOP

                    if not self.stuck:
                        self.bdy = -self.bdy

                    # Ball is so fast it still wants to leave the screen after mirroring, now downwards.
                    # Bounces the ball again (to the other wall) and leaves it there.
                    if self.by > self.BALL_BOTTOM:
                        self.bx = self.bouncebx + (self.bx - self.bouncebx) * ((self.bounceby - self.BALL_BOTTOM) / (self.bounceby - self.by))
                        self.by = self.BALL_BOTTOM
                        self.bdy = -self.bdy

                    if not self.stuck:
                        if self.playsounds:
                            renpy.sound.play(self.soundbeep, channel=1)

                    return True
                return False

            def check_bounce_off_bottom(self):
                # The ball wants to leave the screen downwards.
                if self.by > self.BALL_BOTTOM and self.oldby - self.by != 0:

                    # The x value at which the ball hits the lower wall.
                    collisionbx = self.oldbx + (self.bx - self.oldbx) * ((self.oldby - self.BALL_BOTTOM) / (self.oldby - self.by))

                    # Ignores the walls outside the field.
                    if collisionbx < self.BALL_LEFT or collisionbx > self.BALL_RIGHT:
                        return

                    self.bouncebx = collisionbx
                    self.bounceby = self.BALL_BOTTOM

                    # Bounce off by teleporting ball (mirror position on wall).
                    self.by = -self.by + 2 * self.BALL_BOTTOM

                    if not self.stuck:
                        self.bdy = -self.bdy

                    # Ball is so fast it still wants to leave the screen after mirroring, now downwards.
                    # Bounces the ball again (to the other wall) and leaves it there.
                    if self.by < self.BALL_TOP:
                        self.bx = self.bouncebx + (self.bx - self.bouncebx) * ((self.bounceby - self.BALL_TOP) / (self.bounceby - self.by))
                        self.by = self.BALL_TOP
                        self.bdy = -self.bdy

                    if not self.stuck:
                        if self.playsounds:
                            renpy.sound.play(self.soundbeep, channel=1)

                    return True
                return False

            def getCollisionY(self, hotside, is_computer):
                # Checks whether the ball went through the player's paddle on the x-axis while moving left or monika's paddle while moving right.
                # Returns the y collision-position and sets self.collidedonx

                self.collidedonx = is_computer and self.oldbx <= hotside <= self.bx or not is_computer and self.oldbx >= hotside >= self.bx;

                if self.collidedonx:

                    # Checks whether a bounce happened before potentially colliding with the paddle.
                    if self.oldbx <= self.bouncebx <= hotside <= self.bx or self.oldbx >= self.bouncebx >= hotside >= self.bx:
                        startbx = self.bouncebx
                        startby = self.bounceby
                    else:
                        startbx = self.oldbx
                        startby = self.oldby

                    # The y value at which the ball hits the paddle.
                    if startbx - self.bx != 0:
                        return startby + (self.by - startby) * ((startbx - hotside) / (startbx - self.bx))
                    else:
                        return startby

                # The ball did not go through the paddle on the x-axis.
                else:
                    return self.oldby

            # Recomputes the position of the ball, handles bounces, and
            # draws the screen.
            def render(self, width, height, st, at):

                # The Render object we'll be drawing into.
                r = renpy.Render(width, height)

                # Figure out the time elapsed since the previous frame.
                if self.oldst is None:
                    self.oldst = st

                dtime = st - self.oldst
                self.oldst = st

                # Figure out where we want to move the ball to.
                speed = dtime * self.bspeed

                # Stores the starting position of the ball.
                self.oldbx = self.bx
                self.oldby = self.by
                self.bouncebx = self.bx
                self.bounceby = self.by

                # Handles the ball-speed.
                if self.stuck:
                    self.by = self.playery
                else:
                    self.bx += self.bdx * speed
                    self.by += self.bdy * speed

                # Bounces the ball up to one time, either up or down
                if not self.check_bounce_off_top():
                   self.check_bounce_off_bottom()

                # Handles Monika's targeting and speed.

                # If the ball goes through Monika's paddle, aim for the collision-y, not ball-y.
                # Avoids Monika overshooting her aim on lags.
                collisionby = self.getCollisionY(self.PADDLE_X_MONIKA, True)
                if self.collidedonx:
                    self.ctargety = collisionby + self.ctargetoffset
                else:
                    self.ctargety = self.by + self.ctargetoffset

                cspeed = self.computerspeed * dtime

                # Moves Monika's paddle. It wants to go to self.by, but
                # may be limited by it's speed limit.
                global lose_on_purpose
                if lose_on_purpose and self.bx >= self.COURT_WIDTH * 0.75:
                    if self.bx <= self.PADDLE_X_MONIKA:
                        if self.ctargety > self.computery:
                            self.computery -= cspeed
                        else:
                            self.computery += cspeed

                else:
                    cspeed = self.computerspeed * dtime

                    if abs(self.ctargety - self.computery) <= cspeed:
                        self.computery = self.ctargety
                    elif self.ctargety >= self.computery:
                        self.computery += cspeed
                    else:
                        self.computery -= cspeed

                # Limits the position of Monika's paddle.
                if self.computery > self.COURT_BOTTOM:
                    self.computery = self.COURT_BOTTOM
                elif self.computery < self.COURT_TOP:
                    self.computery = self.COURT_TOP;

                # This draws a paddle, and checks for bounces.
                def paddle(px, py, hotside, is_computer):

                    # Render the paddle image. We give it an 1280x720 area
                    # to render into, knowing that images will render smaller.
                    # (This isn't the case with all displayables. Solid, Frame,
                    # and Fixed will expand to fill the space allotted.)
                    # We also pass in st and at.
                    pi = renpy.render(self.paddle, self.COURT_WIDTH, self.COURT_HEIGHT, st, at)

                    # renpy.render returns a Render object, which we can
                    # blit to the Render we're making.
                    r.blit(pi, (int(px), int(py - self.PADDLE_RADIUS)))

                    # Checks whether the ball went through the paddle on the x-axis and gets the y-collision-posisiton.
                    collisionby = self.getCollisionY(hotside, is_computer)

                    # Checks whether the ball went through the paddle on the y-axis.
                    collidedony = py - self.PADDLE_RADIUS - self.BALL_HEIGHT / 2 <= collisionby <= py + self.PADDLE_RADIUS + self.BALL_HEIGHT / 2

                    # Checks whether the ball collided with the paddle
                    if not self.stuck and self.collidedonx and collidedony:
                        hit = True
                        if self.oldbx >= hotside >= self.bx:
                            self.bx = hotside + (hotside - self.bx)
                        elif self.oldbx <= hotside <= self.bx:
                            self.bx = hotside - (self.bx - hotside)
                        else:
                            hit = False

                        if hit:
                            # The reflection angle scales linearly with the
                            # distance from the centre to the point of impact.
                            angle = (self.by - py) / (self.PADDLE_RADIUS + self.BALL_HEIGHT / 2) * self.MAX_REFLECT_ANGLE

                            if angle >    self.MAX_ANGLE:
                                angle =   self.MAX_ANGLE
                            elif angle < -self.MAX_ANGLE:
                                angle =  -self.MAX_ANGLE;

                            global pong_angle_last_shot
                            pong_angle_last_shot = angle;

                            self.bdy = .5 * math.sin(angle)
                            self.bdx = math.copysign(.5 * math.cos(angle), -self.bdx)

                            global ball_paddle_bounces
                            ball_paddle_bounces += 1

                            # Changes where the computer aims after a hit.
                            if is_computer:
                                self.ctargetoffset = self.get_random_offset()

                            if self.playsounds:
                                renpy.sound.play(self.soundboop, channel=1)

                            self.bspeed += 125.0 + self.CURRENT_DIFFICULTY * 12.5
                            if self.bspeed > self.BALL_MAX_SPEED:
                                self.bspeed = self.BALL_MAX_SPEED

                # Draw the two paddles.
                paddle(self.PADDLE_X_PLAYER, self.playery, self.PADDLE_X_PLAYER + self.PADDLE_WIDTH, False)
                paddle(self.PADDLE_X_MONIKA, self.computery, self.PADDLE_X_MONIKA, True)

                # Draw the ball.
                ball = renpy.render(self.ball, self.COURT_WIDTH, self.COURT_HEIGHT, st, at)
                r.blit(ball, (int(self.bx - self.BALL_WIDTH / 2),
                              int(self.by - self.BALL_HEIGHT / 2)))

                # Show the player names.
                player = renpy.render(self.player, self.COURT_WIDTH, self.COURT_HEIGHT, st, at)
                r.blit(player, (self.PADDLE_X_PLAYER, 25))

                # Show Monika's name.
                monika = renpy.render(self.monika, self.COURT_WIDTH, self.COURT_HEIGHT, st, at)
                ew, eh = monika.get_size()
                r.blit(monika, (self.PADDLE_X_MONIKA - ew, 25))

                # Show the "Click to Begin" label.
                if self.stuck:
                    ctb = renpy.render(self.ctb, self.COURT_WIDTH, self.COURT_HEIGHT, st, at)
                    cw, ch = ctb.get_size()
                    r.blit(ctb, ((self.COURT_WIDTH - cw) / 2, 30))


                # Check for a winner.
                if self.bx < -200:

                    if self.winner == None:
                        global loss_streak_counter
                        loss_streak_counter += 1

                        if ball_paddle_bounces <= 1:
                            global instant_loss_streak_counter
                            instant_loss_streak_counter += 1
                        else:
                            global instant_loss_streak_counter
                            instant_loss_streak_counter = 0

                    global win_streak_counter
                    win_streak_counter = 0;

                    self.winner = "monika"

                    # Needed to ensure that event is called, noticing
                    # the winner.
                    renpy.timeout(0)

                elif self.bx > self.COURT_WIDTH + 200:

                    if self.winner == None:
                        global win_streak_counter
                        win_streak_counter += 1;

                    global loss_streak_counter
                    loss_streak_counter = 0

                    #won't reset if Monika misses the first hit
                    if ball_paddle_bounces > 1:
                        global instant_loss_streak_counter
                        instant_loss_streak_counter = 0

                    self.winner = "player"

                    renpy.timeout(0)

                # Ask that we be re-rendered ASAP, so we can show the next
                # frame.
                renpy.redraw(self, 0.0)

                # Return the Render object.
                return r

            # Handles events.
            def event(self, ev, x, y, st):

                import pygame

                # Mousebutton down == start the game by setting stuck to
                # false.
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    self.stuck = False

                # Set the position of the player's paddle.
                y = max(y, self.COURT_TOP)
                y = min(y, self.COURT_BOTTOM)
                self.playery = y

                # If we have a winner, return him or her. Otherwise, ignore
                # the current event.
                if self.winner:
                    return self.winner
                else:
                    raise renpy.IgnoreEvent()

label game_pong:
    hide screen keylistener

    if played_pong_this_session:
        if mas_pong_taking_break:
            m 1eua "Ready to try again?"
            m 2tfb "Give me your best, [mas_get_player_nickname(regex_replace_with_nullstr='my ')]!"

            #Reset this flag
            $ mas_pong_taking_break = False
        else:
            m 1hua "You want to play pong again?"
            m 3eub "I'm ready when you are~"
    else:
        $ played_pong_this_session = True

    $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_NONE

    call demo_minigame_pong from _call_demo_minigame_pong
    return

label demo_minigame_pong:

    window hide None

    # Put up the pong background, in the usual fashion.
    scene bg pong field

    # natsuki scare setup if appropriate
    if persistent.playername.lower() == "natsuki" and not persistent._mas_sensitive_mode:
        $ playing_okayev = store.songs.getPlayingMusicName() == "Okay, Everyone! (Monika)"

        # we'll take advantage of Okay everyone's sync with natsuki's version
        if playing_okayev:
            $ currentpos = get_pos(channel="music")
            $ adjusted_t5 = "<from " + str(currentpos) + " loop 4.444>bgm/5_natsuki.ogg"
            stop music fadeout 2.0
            $ renpy.music.play(adjusted_t5, fadein=2.0, tight=True)

    $ ball_paddle_bounces = 0
    $ pong_difficulty_before = persistent._mas_pong_difficulty
    $ powerup_value_this_game = persistent._mas_pong_difficulty_change_next_game
    $ loss_streak_counter_before = loss_streak_counter
    $ win_streak_counter_before = win_streak_counter
    $ instant_loss_streak_counter_before = instant_loss_streak_counter

    # Run the pong minigame, and determine the winner.
    python:
        ui.add(PongDisplayable())
        winner = ui.interact(suppress_overlay=True, suppress_underlay=True)

    # natsuki scare if appropriate
    if persistent.playername.lower() == "natsuki" and not persistent._mas_sensitive_mode:
        call natsuki_name_scare(playing_okayev=playing_okayev) from _call_natsuki_name_scare

    #Regenerate the spaceroom scene
    call spaceroom(scene_change=True, force_exp='monika 3eua')

    # resets the temporary difficulty bonus
    $ persistent._mas_pong_difficulty_change_next_game = 0;

    if winner == "monika":
        $ new_difficulty = persistent._mas_pong_difficulty + PONG_DIFFICULTY_CHANGE_ON_LOSS

        $ inst_dialogue = store.mas_pong.DLG_WINNER

    else:
        $ new_difficulty = persistent._mas_pong_difficulty + PONG_DIFFICULTY_CHANGE_ON_WIN

        $ inst_dialogue = store.mas_pong.DLG_LOSER

        #Give player XP if this is their first win
        if not persistent._mas_ever_won['pong']:
            $persistent._mas_ever_won['pong'] = True

    if new_difficulty < 0:
        $ persistent._mas_pong_difficulty = 0
    else:
        $ persistent._mas_pong_difficulty = new_difficulty;

    call expression inst_dialogue from _mas_pong_inst_dialogue

    $ mas_gainAffection(modifier=0.5)

    m 3eua "Would you like to play again?{nw}"
    $ _history_list.pop()
    menu:
        m "Would you like to play again?{fast}"

        "Yes.":
            $ pong_ev = mas_getEV("mas_pong")
            if pong_ev:
                # each game counts as a game played
                $ pong_ev.shown_count += 1

            jump demo_minigame_pong

        "No.":
            if winner == "monika":
                if renpy.seen_label(store.mas_pong.DLG_WINNER_END):
                    $ end_dialogue = store.mas_pong.DLG_WINNER_FAST
                else:
                    $ end_dialogue = store.mas_pong.DLG_WINNER_END

            else:
                if renpy.seen_label(store.mas_pong.DLG_LOSER_END):
                    $ end_dialogue = store.mas_pong.DLG_LOSER_FAST
                else:
                    $ end_dialogue = store.mas_pong.DLG_LOSER_END

            call expression end_dialogue from _mas_pong_end_dialogue
    return

# store to hold pong related constants
init -1 python in mas_pong:

    DLG_WINNER = "mas_pong_dlg_winner"
    DLG_WINNER_FAST = "mas_pong_dlg_winner_fast"
    DLG_LOSER = "mas_pong_dlg_loser"
    DLG_LOSER_FAST = "mas_pong_dlg_loser_fast"

    DLG_WINNER_END = "mas_pong_dlg_winner_end"
    DLG_LOSER_END = "mas_pong_dlg_loser_end"

    # tuple of all dialogue block labels
    DLG_BLOCKS = (
        DLG_WINNER,
        DLG_WINNER_FAST,
        DLG_WINNER_END,
        DLG_LOSER,
        DLG_LOSER_FAST,
        DLG_LOSER_END
    )

#START: Dialogue shown when Monika wins
label mas_pong_dlg_winner:
    #Dlg based on difficulty
    #NOTE: Order is very important here.
    #TODO: Dlg based on affection


    #Player lets Monika win after being asked to go easy on her without hitting the ball
    if monika_asks_to_go_easy and ball_paddle_bounces == 1:
        m 1rksdlb "Ahaha..."
        m 1hksdla "I know I asked you to go easy on me, but this isn't what I had in mind..."
        m 3eka "I do appreciate the gesture though~"
        $ monika_asks_to_go_easy = False

    #Player lets Monika win after being asked to go easy on her without hitting the ball too much
    elif monika_asks_to_go_easy and ball_paddle_bounces <= 9:
        m 1hub "Yay, I won!"
        show monika 5ekbfa at t11 zorder MAS_MONIKA_Z with dissolve_monika
        m 5ekbfa "Thanks, [mas_get_player_nickname(regex_replace_with_nullstr='my ')]. I appreciate it~"
        $ monika_asks_to_go_easy = False


    #The player fails to hit the first ball
    elif ball_paddle_bounces == 1:

        #Once
        if instant_loss_streak_counter == 1:
            m 2rksdlb "Ahaha, that's unfortunate..."

        #Twice
        elif instant_loss_streak_counter == 2:
            m 2rksdlc "[player],{w=0.1} you missed again..."

        #Thrice
        elif instant_loss_streak_counter == 3:
            m 2tfd "[player]!"

            if persistent._mas_pm_ever_let_monika_win_on_purpose:
                $ menu_response = _("Are you letting me win on purpose again?")
            else:
                $ menu_response = _("Are you letting me win on purpose?")

            m 2rkc "[menu_response]"
            $ _history_list.pop()
            menu:
                m "[menu_response]{fast}"

                "...Maybe.":
                    m 1hua "Ehehe!~"
                    m 1eka "Thank you, [player]~"
                    show monika 5eka at t11 zorder MAS_MONIKA_Z with dissolve_monika
                    m 5eka "But you know,{w=0.1} I don't mind losing to you every now and then."

                    if persistent._mas_pm_ever_let_monika_win_on_purpose:
                        m 5eua "I like to see you win just as much as you like to see me win~"

                    $ player_lets_monika_win_on_purpose = True
                    $ persistent._mas_pm_ever_let_monika_win_on_purpose = True

                "No.":
                    if persistent._mas_pm_ever_let_monika_win_on_purpose:
                        show monika 1ttu
                        m "Are you {i}sure?{/i}{nw}"
                        $ _history_list.pop()
                        menu:
                            m "Are you {i}sure?{/i}{fast}"

                            "Yes":
                                call mas_pong_dlg_sorry_assuming

                            "No":
                                m 1rfu "[player]!"
                                m 2hksdlb "Stop teasing me!"
                                $ player_lets_monika_win_on_purpose = True
                                $ lose_on_purpose = True

                    else:
                        call mas_pong_dlg_sorry_assuming

        #Any more times
        else:
            if player_lets_monika_win_on_purpose:
                m 2tku "Aren't you getting tired of letting me win, [player]?"
            else:
                m 1rsc "..."

                #Just so we don't get this every time, feels a little more genuine
                if random.randint(1,3) == 1:
                    m 1eka "Come on, [mas_get_player_nickname(regex_replace_with_nullstr='my ')]!"
                    m 1hub "You can do it, I believe in you!"

    #Monika wins a game after the player let her win on purpose at least three times
    elif instant_loss_streak_counter_before >= 3 and player_lets_monika_win_on_purpose:
        m 3hub "Nice try [player],{w=0.1} {nw}"
        extend 3tsu "but I can win by myself!"
        m 3hub "Ahaha!"

    #Monika wins after telling the player she would win the next game
    elif powerup_value_this_game == PONG_DIFFICULTY_POWERUP:
        m 1hua "Ehehe~"

        if persistent._mas_pong_difficulty_change_next_game_date == datetime.date.today():
            m 2tsb "Didn't I tell you I would win this time?"
        else:
            $ p_nickname = mas_get_player_nickname(regex_replace_with_nullstr='my ')
            m 2ttu "Remember, [p_nickname]?{w=0.1} {nw}"
            extend 2tfb "I told you I'd win our next match."

    #Monika wins after going easy on the player
    elif powerup_value_this_game == PONG_DIFFICULTY_POWERDOWN:
        m 1rksdla "Ah..."
        m 3hksdlb "Try again, [player]!"

        $ persistent._mas_pong_difficulty_change_next_game = PONG_PONG_DIFFICULTY_POWERDOWNBIG

    #Monika wins after going even easier on the player
    elif powerup_value_this_game == PONG_PONG_DIFFICULTY_POWERDOWNBIG:
        m 2rksdlb "Ahaha..."
        m 2eksdla "I really hoped you'd win this game."
        m 2hksdlb "Sorry about that, [mas_get_player_nickname(regex_replace_with_nullstr='my ')]!"

    #The player has lost 3, 8, 13, ... matches in a row.
    elif loss_streak_counter >= 3 and loss_streak_counter % 5 == 3:
        m 2eka "Come on, [player], I know you can beat me..."
        m 3hub "Keep trying!"

    #The player has lost 5, 10, 15, ... matches in a row.
    elif loss_streak_counter >= 5 and loss_streak_counter % 5 == 0:
        m 1eua "I hope you're having fun, [mas_get_player_nickname(regex_replace_with_nullstr='my ')]."
        m 1eka "I wouldn't want you get upset over a game, after all."
        m 1hua "We can always take a break and play again later if you want."

    #Monika wins after the player got a 3+ winstreak
    elif win_streak_counter_before >= 3:
        $ p_nickname = mas_get_player_nickname(regex_replace_with_nullstr='my ')
        m 1hub "Ahaha!"
        m 2tfu "Sorry [p_nickname],{w=0.1} {nw}"
        extend 2tub "but it looks like your luck's run out."
        m 2hub "Now it's my time to shine~"

        $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_WIN_AFTER_PLAYER_WON_MIN_THREE_TIMES

    #Monika wins a second time after the player got a 3+ winstreak
    elif pong_monika_last_response_id == PONG_MONIKA_RESPONSE_WIN_AFTER_PLAYER_WON_MIN_THREE_TIMES:
        m 1hua "Ehehe!"
        m 1tub "Keep up, [player]!{w=0.3} {nw}"
        extend 2tfu "It looks like your streak is over!"

        $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_SECOND_WIN_AFTER_PLAYER_WON_MIN_THREE_TIMES

    #Monika wins a long game
    elif ball_paddle_bounces > 9 and ball_paddle_bounces > pong_difficulty_before * 0.5:
        if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_WIN_LONG_GAME:
            m 3eub "Playing against you is really tough, [player]."
            m 1hub "Keep it up and you'll beat me, I'm sure of it!"
        else:
            m 3hub "Well played, [player], you're really good!"
            m 1tfu "But so am I,{w=0.1} {nw}"
            extend 1hub "ahaha!"

        $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_WIN_LONG_GAME

    #Monika wins a short game
    elif ball_paddle_bounces <= 3:
        if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_WIN_SHORT_GAME:
            m 3hub "Another quick win for me~"
        else:
            m 4huu "Ehehe,{w=0.1} {nw}"
            extend 4hub "I got you with that one!"

        $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_WIN_SHORT_GAME

    #Monika wins by a trickshot
    elif pong_angle_last_shot >= 0.9 or pong_angle_last_shot <= -0.9:
        if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_WIN_TRICKSHOT:
            m 2eksdld "Ah...{w=0.3}{nw}"
            extend 2rksdlc "it happened again."
            m 1hksdlb "Sorry about that, [player]!"
        else:
            m 2rksdlb "Sorry, [player]!"
            m 3hksdlb "I didn't mean for it to bounce around that much..."

        $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_WIN_TRICKSHOT

    #Monika wins a game
    else:
        #Easy
        if pong_difficulty_before <= 5:
            if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_WIN_EASY_GAME:
                m 1eub "You can do it, [mas_get_player_nickname(regex_replace_with_nullstr='my ')]!"
                m 3hub "I believe in you~"
            else:
                m 2duu "Concentrate, [player]."
                m 3hub "Keep trying, I know you'll beat me soon!"

            $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_WIN_EASY_GAME

        #Medium
        elif pong_difficulty_before <= 10:
            if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_WIN_MEDIUM_GAME:
                m 1hub "I win another round~"
            else:
                if loss_streak_counter > 1:
                    m 3hub "Looks like I won again~"
                else:
                    m 3hua "Looks like I won~"

            $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_WIN_MEDIUM_GAME

        #Hard
        elif pong_difficulty_before <= 15:
            if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_WIN_HARD_GAME:
                m 1hub "Ahaha!"
                m 2tsb "Am I playing too well for you?"
                m 1tsu "I'm just kidding, [player]."
                m 3hub "You're pretty good!"
            else:
                if loss_streak_counter > 1:
                    m 1hub "I win again~"
                else:
                    m 1huu "I win~"

            $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_WIN_HARD_GAME

        #Expert
        elif pong_difficulty_before <= 20:
            if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_WIN_EXPERT_GAME:
                m 2tub "It feels good to win!"
                m 2hub "Don't worry, I'm sure you'll win again soon~"
            else:
                if loss_streak_counter > 1:
                    m 2eub "I win another round!"
                else:
                    m 2eub "I win this round!"

            $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_WIN_EXPERT_GAME

        #Extreme
        else:
            if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_WIN_EXTREME_GAME:
                m 2duu "Not bad, [mas_get_player_nickname(regex_replace_with_nullstr='my ')]."
                m 4eua "I gave it everything I had, so don't feel too bad for losing from time to time."
            else:
                m 2hub "This time, the win is mine!"
                m 2efu "Keep up, [player]!"

            $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_WIN_EXTREME_GAME

    return

#dlg for Monika saying she's sorry for assuming
#Duplicated, hence label
label mas_pong_dlg_sorry_assuming:
    m 3eka "Alright."
    m 2ekc "I'm sorry for assuming..."

    #This is only used in bits where the player lets Monika win on purpose
    $ player_lets_monika_win_on_purpose = False

    m 3eka "Would you like to take a break, [player]?{nw}"
    $ _history_list.pop()
    menu:
        m "Would you like to take a break, [player]?{fast}"

        "Okay.":
            m 1eka "Alright, [player].{w=0.3} {nw}"
            extend 1hua "I had fun, thanks for playing Pong with me!"
            m 1eua "Let me know when you're ready to play again."

            #Set this var so Monika knows you're ready to play again
            $ mas_pong_taking_break = True

            #Dissolve into idle poses
            show monika idle with dissolve_monika
            jump ch30_loop

        "No.":
            m 1eka "Alright, [player]. If you're sure."
            m 1hub "Keep going, you'll beat me soon!"
    return

#START: Dialogue shown right when monika loses
label mas_pong_dlg_loser:
    # adapts the dialog, depending on the difficulty, game length (bounces), games losses, wins and dialog response.
    # the order of the dialog is crucial, the first matching condition is chosen, other possible dialog is cancelled in the process.
    # todo: adapt dialog to affection
    # todo: add randomized dialog

    $ monika_asks_to_go_easy = False

    #Monika loses on purpose
    if lose_on_purpose:
        m 1hub "Ahaha!"
        m 1kua "Now we're even, [player]!"
        $ lose_on_purpose = False

    #Monika loses without hitting the ball
    elif ball_paddle_bounces == 0:
        m 1rksdlb "Ahaha..."

        if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_LOSE_WITHOUT_HITTING_BALL:
            m "Maybe I should try a bit harder..."
        else:
            m "I guess I was a bit too slow there..."

        $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_LOSE_WITHOUT_HITTING_BALL

    #Player starts playing seriously and wins after losing at least 3 times on purpose
    elif instant_loss_streak_counter_before >= 3 and persistent._mas_pm_ever_let_monika_win_on_purpose:
        m 2tsu "Playing serious now, are we?~"
        m 2tfu "Let's find out how good you really are, [player]!"

    #Player wins after losing at least three times in a row
    elif loss_streak_counter_before >= 3:
        m 4eub "Congrats, [player]!{w=0.3} {nw}"
        extend 2hub "I knew you would win a game after enough practice!"
        m 4eua "Remember, if you train long enough I'm sure you can reach everything you aim for!"

    #Monika loses after saying she would win this time
    elif powerup_value_this_game == PONG_DIFFICULTY_POWERUP:
        m 2wuo "Wow...{w=0.3}{nw}"
        extend 7wuo "I was really trying that time!"
        m 3hub "Way to go, [player]!"

    #Monika loses after going easy on the player
    elif powerup_value_this_game == PONG_DIFFICULTY_POWERDOWN:
        m 1hua "Ehehe!"
        m 2hub "Good job, [player]!"

    #Monika loses after going even easier on the player
    elif powerup_value_this_game == PONG_PONG_DIFFICULTY_POWERDOWNBIG:
        m 1hua "I'm glad you won this time, [player]."

    #Monika loses by a trickshot
    elif pong_angle_last_shot >= 0.9 or pong_angle_last_shot <= -0.9:
        if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_LOSE_TRICKSHOT:
            m 2wuo "[player]!"
            m 2hksdlb "There's no way I could've hit that!"
        else:
            m 2wuo "Wow, that was a great shot!"

        $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_LOSE_TRICKSHOT

    #Monika loses three times in a row
    elif win_streak_counter == 3:
        m 2wuo "Wow, [player]..."
        m 2wud "You've won three times in a row already..."

        #Easy
        if pong_difficulty_before <= 5:
            m 2tsu "Maybe it's time I pick up the pace~"

        #Medium
        elif pong_difficulty_before <= 10:
            m 4hua "You're pretty good!"

        #Hard
        elif pong_difficulty_before <= 15:
            m 3hub "Well played!"

        #Expert
        elif pong_difficulty_before <= 20:
            m 4wuo "That was amazing!"

        #Extreme
        else:
            m 2hub "That was legendary!"

    #Monika loses five times in a row
    elif win_streak_counter == 5:
        m 2wud "[mas_get_player_nickname(regex_replace_with_nullstr='my ')]..."
        m 2tsu "Have you been practicing?"
        m 3hksdlb "I don't know what happened, but I don't stand a chance against you!"
        m 1eka "Could you go a little bit easier on me please?{w=0.3} {nw}"
        extend 3hub "I would really appreciate it~"
        $ monika_asks_to_go_easy = True

    #Monika loses a long game
    elif ball_paddle_bounces > 10 and ball_paddle_bounces > pong_difficulty_before * 0.5:
        if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_LOSE_LONG_GAME:
            m 2wuo "Wow,{w=0.1} I can't keep up!"
        else:
            m 2hub "Amazing, [player]!"
            m 4eub "You're really good!"

        $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_LOSE_LONG_GAME

    #Monika loses a short game
    elif ball_paddle_bounces <= 2:
        if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_LOSE_SHORT_GAME:
            m 2hksdlb "Ahaha..."
            m 3eksdla "I guess I should try a little harder..."
        else:
            m 1rusdlb "I didn't expect to lose this quickly."

        $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_LOSE_SHORT_GAME

    #Monika loses a game
    else:
        #Easy difficulty
        if pong_difficulty_before <= 5:
            if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_LOSE_EASY_GAME:
                m 4eub "You win this round as well."
            else:
                if win_streak_counter > 1:
                    m 1hub "You won again!"
                else:
                    m 1hua "You won!"

            $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_LOSE_EASY_GAME

        #Medium
        elif pong_difficulty_before <= 10:
            if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_LOSE_MEDIUM_GAME:
                m 1eua "It's nice seeing you win, [player]."
                m 1hub "Keep it up~"
            else:
                if win_streak_counter > 1:
                    m 1hub "You won again! {w=0.2}Well done~"
                else:
                    m 1eua "You won! {w=0.2}Not bad."

            $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_LOSE_MEDIUM_GAME

        #Hard
        elif pong_difficulty_before <= 15:
            if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_LOSE_HARD_GAME:
                m 4hub "Another win for you!"
                m 4eua "Great job, [player]."
            else:
                if win_streak_counter > 1:
                    m 2hub "You won again! {w=0.2}Congrats!"
                else:
                    m 2hua "You won! {w=0.2}Congratulations!"

            $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_LOSE_HARD_GAME

        #Expert
        elif pong_difficulty_before <= 20:
            if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_LOSE_EXPERT_GAME:
                m 2wuo "Wow,{w=0.1} I'm really trying...{w=0.3}you're unstoppable!"
                m 2tfu "But I'm sure I'll beat you sooner or later, [player]."
                m 3hub "Ahaha!"
            else:
                if win_streak_counter > 1:
                    m 4hub "You won again! {w=0.2}Nice work!"
                else:
                    m 4hub "You won! {w=0.2}Impressive!"

            $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_LOSE_EXPERT_GAME

        #Extreme
        else:
            if pong_monika_last_response_id == PONG_MONIKA_RESPONSE_LOSE_EXTREME_GAME:
                m 3eua "You're really good, [player]."
                m 1hub "I love playing Pong with you!"
            else:
                m 1tsu "This is intense!"
                m 1hub "Keep at it, [mas_get_player_nickname(regex_replace_with_nullstr='my ')]!"

            $ pong_monika_last_response_id = PONG_MONIKA_RESPONSE_LOSE_EXTREME_GAME
    return


#Quick Moni lose dlg
label mas_pong_dlg_loser_fast:
    m 1eka "Alright, [player]."
    m 3tfu "But I'll beat you next time."

    $ persistent._mas_pong_difficulty_change_next_game = PONG_DIFFICULTY_POWERUP;
    $ persistent._mas_pong_difficulty_change_next_game_date = datetime.date.today()
    return

#Quick Moni win dlg
label mas_pong_dlg_winner_fast:
    m 1eka "Alright, [player]. Thanks for playing Pong with me."
    m 1hua "I had a lot of fun! Let's play again sometime soon, okay?"

    $ persistent._mas_pong_difficulty_change_next_game = PONG_DIFFICULTY_POWERDOWN;
    return

#Post dlg Moni lose
label mas_pong_dlg_loser_end:
    m 1wuo "Wow, I was really trying that time."
    m 1eua "You must have really been practicing to get so good."
    m 2tuu "I guess you wanted to impress me, [player]."
    m 1hua "You're so sweet~"
    return

#Post dlg Moni win
label mas_pong_dlg_winner_end:
    m 4tku "I can't really get excited for a game this simple..."
    m 1eua "But at least it's still fun to play."
    m 1ekbsa "Especially with you, [player]."
    m 1hubfa "Ehehe~"
    return
