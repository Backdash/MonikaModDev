# pong difficulty changes on win / loss. Determines monika's paddle-movement-cap, the ball's start-speed, max-speed and acceleration. 
default persistent.pong_difficulty = 10
# increases the pong difficulty for the next game by the value this is set to. Resets after a finished match.
default persistent.pong_difficulty_powerup = 0
# whether the player answered monika he lets her win on purpose
default persistent.player_once_let_monika_win_on_purpose = False

define DIFFICULTY_CHANGE_ON_WIN  = +1
define DIFFICULTY_CHANGE_ON_LOSS = -1
define DIFFICULTY_POWERUP        = 5
define DIFFICULTY_POWERDOWN      = -5
define DIFFICULTY_POWERDOWNBIG   = -10

define played_pong_this_session = False
define player_lets_monika_win_on_purpose = False
define instant_loss_streak_counter = 0
define loss_streak_counter = 0
define win_streak_counter = 0
define lose_on_purpose = False
define monika_asks_to_go_easy = False
define pong_last_responce_id = -1

# Need to be set before every game and be accessible outside the class
define ball_paddle_bounces = 0
define powerup_value_this_game = 0
define instant_loss_streak_counter_before = 0
define loss_streak_counter_before = 0
define win_streak_counter_before = 0
define pong_difficulty_before = 0
define pong_angle_last_shot = 0.0
    
init:

    image bg pong field = "mod_assets/pong_field.png"

    python:
        import random
        import math

        class PongDisplayable(renpy.Displayable):

            def __init__(self):

                renpy.Displayable.__init__(self)

                # Some displayables we use.
                self.paddle = Image("mod_assets/pong.png")
                self.ball = Image("mod_assets/pong_ball.png")
                self.player = Text(_("[player]"), size=36)
                self.monika = Text(_("[m_name]"), size=36)
                self.ctb = Text(_("Click to Begin"), size=36)

                # Sounds used.
                self.playsounds = True
                self.soundboop = "mod_assets/pong_boop.wav"
                self.soundbeep = "mod_assets/pong_beep.wav"

                # The sizes of some of the images.
                self.PADDLE_WIDTH = 8
                self.PADDLE_HEIGHT = 79
                self.PADDLE_RADIUS = self.PADDLE_HEIGHT / 2
                self.BALL_WIDTH = 15
                self.BALL_HEIGHT = 15
                self.COURT_TOP = 124
                self.COURT_BOTTOM = 654
                
                # Other variables
                self.CURRENT_DIFFICULTY = max(persistent.pong_difficulty + persistent.pong_difficulty_powerup, 0)
                
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
        m 5esu "You wanna play pong again?"
        m 4esb "I'm ready when you are~"
    else:
        m 1eua "You wanna play a game of Pong? Okay!"
        $ played_pong_this_session = True
        
    $ pong_last_responce_id = -1

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
    $ pong_difficulty_before = persistent.pong_difficulty
    $ powerup_value_this_game = persistent.pong_difficulty_powerup
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
    $scene_change=True #Force scene generation
    call spaceroom from _call_spaceroom_3

    show monika 1eua
    
    # resets the temporary difficulty bonus
    $ persistent.pong_difficulty_powerup = 0;  

    if winner == "monika":
        $ new_difficulty = persistent.pong_difficulty + DIFFICULTY_CHANGE_ON_LOSS
            
        $ inst_dialogue = store.mas_pong.DLG_WINNER

    else:
        $ new_difficulty = persistent.pong_difficulty + DIFFICULTY_CHANGE_ON_WIN
        
        $ inst_dialogue = store.mas_pong.DLG_LOSER
        
        #Give player XP if this is their first win
        if not persistent.ever_won['pong']:
            $persistent.ever_won['pong'] = True
            $grant_xp(xp.WIN_GAME)
        
    if new_difficulty < 0:
        $ persistent.pong_difficulty = 0
    else:
        $ persistent.pong_difficulty = new_difficulty; 
         
    call expression inst_dialogue from _mas_pong_inst_dialogue

    $ mas_gainAffection(modifier=0.5)

    show monika 1hua
    
    menu:
        m "Do you want to play again?"

        "Yes.":
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

## pong text dialogue adjustments

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

# dialogue shown right when monika wins
label mas_pong_dlg_winner:
    # adapts the dialog, depending on the difficulty, game length (bounces), games losses, wins and dialog response.
    # the order of the dialog is crucial, the first matching condition is chosen, other possible dialog is cancelled in the process.
    # todo: adapt dialog to affection
    # todo: add randomized dialog
        
        
    #Player lets Monika win after being asked to go easy on her without hitting the ball
    if monika_asks_to_go_easy and ball_paddle_bounces == 1:
        m 2lssdrb "Ahaha.."
        m 1hsb "This isn't exactly what I had in mind."
        m 4esb "However, I do appreciate the gesture~"
        $ monika_asks_to_go_easy = False
        
        
    #Player lets Monika win after being asked to go easy on her without hitting the ball too much
    if monika_asks_to_go_easy and ball_paddle_bounces <= 9:
        m 1esb "Yay, I won!"
        m 5ekbfa "Thanks, [player]!"
        m 5hubfb "You are awesome~"
        $ monika_asks_to_go_easy = False
        
        
    #The player fails to hit the first ball
    elif ball_paddle_bounces == 1:
        
        #One time
        if instant_loss_streak_counter == 1:
            m 5hub "Ahaha, how did you miss that?"#
            
            
        #Two times
        elif instant_loss_streak_counter == 2:
            m 2tsb "[player], you missed again!"#
            
            
        #Three times
        elif instant_loss_streak_counter == 3:
            m 2tub "[player]!"#
            
            if persistent.player_once_let_monika_win_on_purpose:
                m 5rub "Are you letting me win on purpose again?"#
            else:
                m 5eub "Are you letting me win on purpose?"#
                
            menu:
                "Yes":
                    m 1hub "You are so cute, [player]!"#
                    m 5hua "Thank you for letting me win~"
                    if persistent.player_once_let_monika_win_on_purpose:
                        m 1ekbsa "But you know I wouldn't mind losing against you."#
                        m 5hua "I like to see you win just as much as you like to see me win~"
                    else:
                        m 1eka "I wouldn't mind losing against you, though."#
                    $ player_lets_monika_win_on_purpose = True
                    $ persistent.player_once_let_monika_win_on_purpose = True
                "No": 
                    if persistent.player_once_let_monika_win_on_purpose:
                        m 1ttu "Are you sure?"
                        menu:
                            "Yes": 
                                m 1hua "Alright."#
                                m 2ekc "I'm sorry for assuming then..."
                                m 3ekb "In case you can't concentrate, maybe you should take a break."
                                m 4eka "Drinking a glass of water can also help."
                                $ player_lets_monika_win_on_purpose = False
                            "No":
                                m 1rfu "[player]."#
                                m 2eub "Stop teasing me!"
                                $ player_lets_monika_win_on_purpose = True
                                $ lose_on_purpose = True
                        
                    else:
                        m 2ekd "I'm sorry for assuming..."#
                        m 3eka "If you can't concentrate, maybe you should take a break."
                        m 4eka "Drinking a glass of water can also help."
                        $ player_lets_monika_win_on_purpose = False
                    
                    
        #More than three times
        else:
            if player_lets_monika_win_on_purpose:
                m 5eub "Aren't you getting tired of letting me win, [player]?"#
            else: 
                m 1rsc "..."#
        
        
    #Monika wins a game after the player let her win on purpose at least three times
    elif instant_loss_streak_counter_before >= 3 and player_lets_monika_win_on_purpose:
        m 3hub "Nice try, [player]!"#
        m 6eua "As you see I can win all by myself!"
        m 5hub "Ehehe~"
        
    
    #Monika wins after telling the player she would win the next game
    elif powerup_value_this_game == DIFFICULTY_POWERUP:
        m 1hub "Ehehe."
        
        $ dt = datetime.date.today()
        $ dt = datetime.datetime(dt.year, dt.month, dt.day)

        if persistent.pong_difficulty_powerup_date == dt:
            m 2tsb "Didn't I tell you I would win this time?"#
        else:
            m 4tsb "Remember how I told you I would win the next game?"
    
    
    #Monika wins after going easy on the player
    elif powerup_value_this_game == DIFFICULTY_POWERDOWN:
        m 2wud "Oh."
        m 3esb "Try again, [player]!"
        $ persistent.pong_difficulty_powerup = DIFFICULTY_POWERDOWNBIG;  
    
    
    #Monika wins after going even easier on the player
    elif powerup_value_this_game == DIFFICULTY_POWERDOWNBIG:
        m 2lssdrb "Ahahaha."
        m 2lksdrb "I really hoped you would win this game."
        m 2hksdrb "Sorry about that, [player]!"
        
        
    #The player has lost 3, 8, 13, ... matches in a row.
    elif loss_streak_counter >= 3 and loss_streak_counter % 5 == 3:
        m 2eku "Come on, [player], I know you can beat me!" 
        m 2duu "Stay determined!"
        
        
    #The player has lost 5, 10, 15, ... matches in a row.
    elif loss_streak_counter >= 5 and loss_streak_counter % 5 == 0:
        m 2esd "I hope you are having fun, [player]."
        m 2rksdlc "I don't want you to feel bad for losing too often."
        
        
    #Monika wins after the player got a 3+ winstreak
    elif win_streak_counter_before >= 3:
        m 1hub "Ahahaha!"
        m 1duu "Sorry, [player]."
        m 1tub "It looks like your luck has run out."
        m 4hua "Now it's my turn to shine~"
            
        $ pong_last_responce_id = 60
        
        
    #Monika wins a second time after the player got a 3+ winstreak
    elif pong_last_responce_id == 60:
        m 6hua "Ehehe!"
        m 1eub "Keep up, [player]!"
        
        if persistent.gender == "M":
            m 2tku "You don't want to lose to a girl like that, do you?"
            
            
        $ pong_last_responce_id = 65


    #Monika wins a long game
    elif ball_paddle_bounces > 9 and ball_paddle_bounces > pong_difficulty_before * 1/2:
        if pong_last_responce_id == 70:
            m 2hub "Playing against you is really tough, [player]!"
            m 4eub "Keep it up and you will beat me, I'm sure of it."
        else:
            m 6hub "Well played, [player]!"
            m 4eub "You are really good at pong!"
            m 5hub "But so am I, Ahahaha!"
            
        $ pong_last_responce_id = 70
        
        
    #Monika wins a short game
    elif ball_paddle_bounces <= 3:
        if pong_last_responce_id == 80:            
            m 6hub "Another quick win for me~"
        else:
            m 4hub "Ehehe, I got you with that one!"
        
        $ pong_last_responce_id = 80
        
        
    #Monika wins by a trickshot
    elif pong_angle_last_shot >= 0.9 or pong_angle_last_shot <= -0.9:
        if pong_last_responce_id == 90:     
            m 2eksdld "Oh..." 
            m 6ekc "It happened again." 
            m 1hub "Sorry about that!"
        else:
            m 2hub "Ahahaha, sorry [player]!"
            m 3rud "It wasn't supposed to bounce that much..."
        
        $ pong_last_responce_id = 90
        
        
    #Monika wins a game
    else:
        
        #On easy difficulty
        if pong_difficulty_before <= 5:
            if pong_last_responce_id == 100:
                m 1eub "You can do it, [player]!" 
                m 5hua "I believe in you~"
            else:
                m 5eua "Concentrate, [player]." 
                m 4hua "I'm sure you will win soon, if you try hard enough."
        
            $ pong_last_responce_id = 100
            
            
        #On medium difficulty
        elif pong_difficulty_before <= 10:
            if pong_last_responce_id == 110:
                m 1hub "I win another round~"
            else:
                if loss_streak_counter > 1:
                    m 2esa "Looks like I won again."
                else:
                    m 2esa "Looks like I won."
        
            $ pong_last_responce_id = 110           
            
            
        #On hard difficulty
        elif pong_difficulty_before <= 15:
            if pong_last_responce_id == 120:
                m 1hub "Ahahaha!"
                m 3tsb "Am I playing too good for you?"
                m 5hub "I am just kidding, [player]!"
                m 6esa "I know you are pretty good yourself!"
            else:
                if loss_streak_counter > 1:
                    m 1huu "I win again~!"
                else:
                    m 1huu "I win~!"
        
            $ pong_last_responce_id = 120 
            
            
        #On expert difficulty
        elif pong_difficulty_before <= 20:
            if pong_last_responce_id == 130:
                m 5hub "It feels good to win!"
                m 5eua "Don't worry, I'm sure you will win again soon~"
            else:
                if loss_streak_counter > 1:
                    m 2eub "I win another round!"
                else:
                    m 2eub "I win this round!"
        
            $ pong_last_responce_id = 130
            
            
        #On extreme difficulty
        else:
            if pong_last_responce_id == 140:
                m 2duu "You have done well to come this far, [player]."
                m 4esb "I gave it everything I got, so don't feel too bad for losing from time to time."
            else:
                m 2hub "This time it's my win!"
                m 5hub "Keep up, [player]!"
        
            $ pong_last_responce_id = 140
        
    return
    
    

# dialogtue shown right when monika loses
label mas_pong_dlg_loser:
    # adapts the dialog, depending on the difficulty, game length (bounces), games losses, wins and dialog response.
    # the order of the dialog is crucial, the first matching condition is chosen, other possible dialog is cancelled in the process.
    # todo: adapt dialog to affection
    # todo: add randomized dialog
    
    $ monika_asks_to_go_easy = False
    
     
    #Monika loses on purpose
    if lose_on_purpose:
        m 5hub "Ahahaha!"
        m 1kua "Now we're even, [player]!"
        $ lose_on_purpose = False
        
        
    #Monika loses without hitting the ball
    elif ball_paddle_bounces == 0:
        if pong_last_responce_id == 1010: 
            m 1rksdlb "Maybe I should try a bit harder..."
        else:
            m 1rksdlb "Ahaha, I guess I was a bit too slow there..."
        
        $ pong_last_responce_id = 1010
              
              
    #Player starts playing seriously and wins after losing at least 3 times on purpose
    elif instant_loss_streak_counter_before >= 3 and persistent.player_once_let_monika_win_on_purpose:
        m 5tsu "So you are playing seriously now?"#
        m 1huu "Let's find out how good you really are, [player]!"  
        
    
    #Player wins after losing at least three times in a row
    elif loss_streak_counter_before >= 3:
        m 4eub "Congrats [player]!"#
        m 2eua "I knew you would win a game after enough practice!"
        m 4eua "Remember that skill comes mostly through repetitive training."
        m 4hub "If you train long enough I'm sure you can reach everything you aim for!"
        
        
    #Monika loses after saying she would win this time
    elif powerup_value_this_game == DIFFICULTY_POWERUP:
        m 6wuo "Wow..."
        m 2tub "I was really trying this time, but you still won."
        m 5hub "Way to go, [player]!"
        
        
    #Monika loses after going easy on the player
    elif powerup_value_this_game == DIFFICULTY_POWERDOWN:
        m 5hub "Ehehe!"
        m 6esa "Good job, [player]!"
        
        
    #Monika loses after going even easier on the player
    elif powerup_value_this_game == DIFFICULTY_POWERDOWNBIG:
        m 1hsb "I'm glad you won this time, [player]."
        
    
    #Monika loses by a trickshot
    elif pong_angle_last_shot >= 0.9 or pong_angle_last_shot <= -0.9:
        if pong_last_responce_id == 1070:     
            m 2dfd "[player]!" 
            m 2tkc "This is kind of unfair..." 
            m 2ekp "..."
            m 1hksdlb "Sorry, [player]."
            m 1lsc "Losing like this kind of gets to me."
        else:
            m 2ekb "Wow, I just couldn't hit this trickshot."
        
        $ pong_last_responce_id = 1070  
        
        
    #Monika loses three times in a row
    elif win_streak_counter == 3:
        m 2wuo "Wow, [player]..."
        m 2wud "You have beaten me three times in a row already..."
        
        #On easy difficulty
        if pong_difficulty_before <= 5:
            m 2tub "Maybe I am going a little bit too easy on you~"
            
            
        #On medium difficulty
        elif pong_difficulty_before <= 10:
            m 4hua "You definitely know how to play!"
            
            
        #On hard difficulty
        elif pong_difficulty_before <= 15:
            m 5tsu "Watching you play is quite impressive!"
            
            
        #On expert difficulty
        elif pong_difficulty_before <= 20:
            m 4tub "You should get a medal!"
            
            
        #On extreme difficulty
        else:
            m 5tsu "Are you sure you aren't cheating?"
            m 1kua "Ehehe!"
        
        
    #Monika loses five times in a row
    elif win_streak_counter == 5:
        m 2wud "[player]..." 
        m 5euc "Have you been playing pong behind my back?" 
        m 6ekd "I don't know what happened but I don't stand a chance against you!" 
        m 1eua "Could you go a little bit easier on me please?"
        m 3hub "I would really appreciate it~"
        $ monika_asks_to_go_easy = True
        
        
    #Monika loses a long game 
    elif ball_paddle_bounces > 10 and ball_paddle_bounces > pong_difficulty_before * 1/2:
        if pong_last_responce_id == 1100:
            m 2esb "Incredible, [player]!"
            m 4esb "I just can't keep up with you, way to go!"
        else:
            m 2hub "Amazing, [player]!"
            m 4esb "You have an excellent technique to come that far!"
        
        $ pong_last_responce_id = 1100
        
        
    #Monika loses a short game
    elif ball_paddle_bounces <= 2:
        if pong_last_responce_id == 1110:     
            m 2hksdlb "Ahahaha..." 
            m 3eksdla "I guess I should try a little harder..."
        else:
            m 1rusdlb "I did not expect to lose this quickly."
        
        $ pong_last_responce_id = 1110
        
        
    #Monika loses a game
    else:
        
        #On easy difficulty
        if pong_difficulty_before <= 5:
            if pong_last_responce_id == 1120:
                m 4eub "You win this round as well."
            else:
                if win_streak_counter > 1:
                    m 2esb "You won again!"
                else:
                    m 2esb "You won!"
        
            $ pong_last_responce_id = 1120
            
            
        #On medium difficulty
        elif pong_difficulty_before <= 10:
            if pong_last_responce_id == 1130:
                m 5eub "It is nice to see you win like that, [player]."
                m 5hub "Keep it up~"
            else:
                if win_streak_counter > 1:
                    m 1esb "You won again! Not bad."
                else:
                    m 1esb "You won! Not bad."
        
            $ pong_last_responce_id = 1130
            
            
        #On hard difficulty
        elif pong_difficulty_before <= 15:
            if pong_last_responce_id == 1140:
                m 4eud "You won yet another time!"
                m 4eub "Pretty impressive, [player]."
            else:
                if win_streak_counter > 1:
                    m 2hub "You won again! Congratulations!"
                else:
                    m 2hub "You won! Congratulations!"
        
            $ pong_last_responce_id = 1140
            
            
        #On expert difficulty
        elif pong_difficulty_before <= 20:
            if pong_last_responce_id == 1150:
                m 2eud "Wow, I am really trying but you just keep on winning!"
                m 3tsb "Well, I'm sure I will beat you sooner or later [player]..."
                m 6hub "Ahahaha!"
            else:
                if win_streak_counter > 1:
                    m 4hubfb "You won again! Impressive!"
                else:
                    m 4hubfb "You won! Impressive!"
        
            $ pong_last_responce_id = 1150
            
            
        #On extreme difficulty
        else:
            if pong_last_responce_id == 1160:
                m 2esc "I simply can't believe how good you are at this."
                m 4eud "You have great potential."
                m 5eub "If you use it for something different than pong, I'm sure you can accomplish great things!"
            else:
                m 1tsu "This is getting intense!"
                m 5hub "Good job, [player]!"
                m 5esu "You really know how to play pong, huh?"
        
            $ pong_last_responce_id = 1160
        
    return



# quick dialogue shown when monika is the pong loser
label mas_pong_dlg_loser_fast:
    m 1tfu "I'll beat you next time, [player]."
    
    $ persistent.pong_difficulty_powerup = DIFFICULTY_POWERUP;    
    $ persistent.pong_difficulty_powerup_date = datetime.datetime.today()
    $ persistent.pong_difficulty_powerup_date = datetime.datetime(persistent.pong_difficulty_powerup_date.year, persistent.pong_difficulty_powerup_date.month, persistent.pong_difficulty_powerup_date.day)
    return



# quick dialogue shown when monika is the pong winner
label mas_pong_dlg_winner_fast:
    m 5hua "Thanks for playing Pong and letting me win, [player]."
    m 6eua "I look forward to play with you again sometime."
    
    $ persistent.pong_difficulty_powerup = DIFFICULTY_POWERDOWN;    
    return
    
    

# end dialogue shown when monka is the pong loser
label mas_pong_dlg_loser_end:
    m 1wuo "Wow, I was actually trying that time."
    m 1eua "You must have really practiced at Pong to get so good."
    m 1tku "Is that something for you to be proud of?"
    m 1hua "I guess you wanted to impress me, [player]~"
    return



# end dialogue shown when monika is the pong winner
label mas_pong_dlg_winner_end:
    m 4tku "I can't really get excited for a game this simple..."
    m 1eua "At least we can still hang out with each other."
    m 1hub "Ahaha!"
    m 1eua "Thanks for letting me win, [player]."
    m 1tku "Only elementary schoolers seriously lose at Pong, right?"
    m 1hua "Ehehe~"
    return
