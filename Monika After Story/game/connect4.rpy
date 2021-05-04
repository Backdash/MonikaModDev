
            
            
            
init python:
    import pygame
    import re
    import copy
    
    class MASConnect4Displayable(renpy.Displayable):
        # pygame events
        MOUSE_EVENTS = (
            pygame.MOUSEMOTION,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEBUTTONDOWN
        )
        
        # variables to indicate Monika and player's pins/turn
        EMPTY = 0
        AI = 1
        PLAYER = 2
        
        # indicate the board's rows columns
        CEL_COL = 7
        CEL_ROW = 6
        
        BOARD_INDEX = [[(i, j) for j in range(7)] for i in range(6)]
        BOARD_EMPTY = [[0 for j in range(7)] for i in range(6)]
        
        # the  board's dimensions
        BOARD_BORDER_WIDTH = 15
        BOARD_BORDER_HEIGHT = 15
        CEL_WIDTH = 60
        CEL_HEIGHT = 60
        BOARD_WIDTH = BOARD_BORDER_WIDTH * 2 + CEL_WIDTH * CEL_COL
        BOARD_HEIGHT = BOARD_BORDER_HEIGHT * 2 + CEL_HEIGHT * CEL_ROW
        
        # offset for board's position
        DISP_X_OFFSET = 200
        DISP_Y_OFFSET = 200
        
        BOARD_X_POS = int(1280 - BOARD_WIDTH - DISP_X_OFFSET)
        BOARD_Y_POS = int(720 - BOARD_HEIGHT - DISP_Y_OFFSET)
        
        # position of the upper left most cel
        CEL_BASE_X_POS = BOARD_X_POS + BOARD_BORDER_WIDTH
        CEL_BASE_Y_POS = BOARD_Y_POS + BOARD_BORDER_HEIGHT
        
        # dimensions of buttons the player use to drop pins on their turn (AKA col button)
        COL_BUTTON_WIDTH = 60
        COL_BUTTON_HEIGHT = 53
        COL_BUTTON_X_SPACING = 5
        COL_BUTTON_Y_SPACING = 7
        COL_BUTTON_X_DISTANCE = int(COL_BUTTON_WIDTH + COL_BUTTON_X_SPACING)
        
        # menu button dimensions
        BUTTON_WIDTH = 120
        BUTTON_HEIGHT = 35
        BUTTON_X_SPACING = 10
        BUTTON_Y_SPACING = 10
        BUTTON_Y_DISTANCE = int(BUTTON_HEIGHT + BUTTON_Y_SPACING)
        
        # col button position
        COL_BUTTON_X = int(BOARD_X_POS + BOARD_WIDTH / 2 - COL_BUTTON_WIDTH / 2)
        COL_BUTTON_Y = int(BOARD_Y_POS - COL_BUTTON_HEIGHT - COL_BUTTON_Y_SPACING)
        
        # menu button position
        BUTTON_X = BOARD_X_POS + BOARD_WIDTH + BUTTON_X_SPACING
        BUTTON_Y = BOARD_Y_POS + BOARD_HEIGHT - BUTTON_HEIGHT
        
        # images definition
        AI_IMAGE = Image("mod_assets/games/connect4/monika_pin.png")
        PLAYER_IMAGE = Image("mod_assets/games/connect4/player_pin.png")
        BOARD_IMAGE = Image("mod_assets/games/connect4/connect4_board.png")
        WIN_TILE_IMAGE = Image("mod_assets/games/connect4/win_tile.png")
        COL_BUTTON_IDLE_IMAGE = Image("mod_assets/games/connect4/arrow_down_idle.png")
        COL_BUTTON_HOVER_IMAGE = Image("mod_assets/games/connect4/arrow_down_hover.png")
        COL_BUTTON_INSENSITIVE_IMAGE = Image("mod_assets/games/connect4/arrow_down_insensitive.png")
        
        def __init__(self, first_turn):
            # prepare the Displayable
            super(MASConnect4Displayable, self).__init__()
            
            # init the variables
            self.is_game_over = False
            self.quit_game = False
            self.turn = first_turn
            self.board = copy.deepcopy(self.BOARD_EMPTY)
            self.full_col = set()
            self.turn_move_success = False
            self.winner = False
            self.win_tiles = set()
            
            # init col buttons
            self._col_buttons = list()
            for i in range(self.CEL_COL):
                button = MASButtonDisplayable(
                    Null(),
                    Null(),
                    Null(),
                    Frame(self.COL_BUTTON_IDLE_IMAGE, Borders(0, 0, 0, 0)),
                    Frame(self.COL_BUTTON_HOVER_IMAGE, Borders(0, 0, 0, 0)),
                    Frame(self.COL_BUTTON_INSENSITIVE_IMAGE, Borders(0, 0, 0, 0)),
                    MASConnect4Displayable.COL_BUTTON_X + MASConnect4Displayable.COL_BUTTON_X_DISTANCE * (i - 3),
                    MASConnect4Displayable.COL_BUTTON_Y,
                    MASConnect4Displayable.COL_BUTTON_WIDTH,
                    MASConnect4Displayable.COL_BUTTON_HEIGHT,
                    hover_sound=gui.hover_sound,
                    activate_sound=gui.activate_sound,
                    return_value=i
                )
                self._col_buttons.append(button)
                
            # init menu buttons
            self._button_quit = MASButtonDisplayable.create_stb(
                _("Quit"),
                True,
                MASConnect4Displayable.BUTTON_X,
                MASConnect4Displayable.BUTTON_Y,
                MASConnect4Displayable.BUTTON_WIDTH,
                MASConnect4Displayable.BUTTON_HEIGHT,
                hover_sound=gui.hover_sound,
                activate_sound=gui.activate_sound
            )
                
            self._button_done = MASButtonDisplayable.create_stb(
                _("Done"),
                False,
                MASConnect4Displayable.BUTTON_X,
                MASConnect4Displayable.BUTTON_Y,
                MASConnect4Displayable.BUTTON_WIDTH,
                MASConnect4Displayable.BUTTON_HEIGHT,
                hover_sound=gui.hover_sound,
                activate_sound=gui.activate_sound
            )
            
            self._visible_buttons = [
                self._button_quit
            ]
            
            self._visible_buttons_winner = [
                self._button_done
            ]
        
        def render(self, width, height, st, at):
            """
            This function shows the board into the screen
            """
            render = renpy.Render(width, height)
            
            # prepare the board as rendererr
            board = renpy.render(MASConnect4Displayable.BOARD_IMAGE, 1280, 720, st , at)
            
            # prepare col buttons as renderers
            # (they look the same, but their return values are different on init, thus, they are put in a list)
            col_buttons = [
                (b.render(width, height, st, at), b.xpos, b.ypos)
                for b in self._col_buttons
            ]
            
            # prepare menu buttons as renderers
            visible_buttons = list()
            if self.is_game_over:
                visible_buttons = [
                    (b.render(width, height, st, at), b.xpos, b.ypos)
                    for b in self._visible_buttons_winner
                ]
            else:
                visible_buttons = [
                    (b.render(width, height, st, at), b.xpos, b.ypos)
                    for b in self._visible_buttons
                ]
            
            # debugging stuff
            # show = re.sub('[{}"]', '', str(self.board)) if self.board else "empty"
            # render.blit(
                # renpy.render(Text(show), 1280, 720, st , at), 
                # (0, 0)
            # )
            
            # show = "game over = " + str(self.is_game_over)
            # render.blit(
                # renpy.render(Text(show), 1280, 720, st , at), 
                # (0, 50)
            # )
            
            # show = "turn = " + str(self.turn)
            # render.blit(
                # renpy.render(Text(show), 1280, 720, st , at), 
                # (0, 75)
            # )
            
            # show = "move success = " + str(self.turn_move_success)
            # render.blit(
                # renpy.render(Text(show), 1280, 720, st , at), 
                # (0, 100)
            # )
            
            # show = "win tiles =" + " ".join(self.win_tiles)
            # render.blit(
                # renpy.render(Text(show), 1280, 720, st , at), 
                # (0, 125)
            # )
            
            # draw the board
            render.blit(board, (MASConnect4Displayable.BOARD_X_POS, MASConnect4Displayable.BOARD_Y_POS))
            
            if self.win_tiles:
                # prepare winning tile highlight as renderer
                win_tile = renpy.render(MASConnect4Displayable.WIN_TILE_IMAGE, 1280, 720, st , at)
                
                # draw winning tile highlights
                for t in self.win_tiles:
                    y, x = (int(t[0]) * MASConnect4Displayable.CEL_WIDTH, int(t[1]) * MASConnect4Displayable.CEL_HEIGHT)
                    render.blit(win_tile, (MASConnect4Displayable.CEL_BASE_X_POS + x, MASConnect4Displayable.CEL_BASE_Y_POS + y))
            
            for i in self.board:
                if self.PLAYER in i:
                    # prepare the pins as renderer
                    player_pin = renpy.render(MASConnect4Displayable.PLAYER_IMAGE, 1280, 720, st , at)
                    break
            
            for i in range(len(self.board)):
                if self.PLAYER in self.board[i]:
                    # draw the player pins
                    for j in range(len(self.board[i])):
                        y, x = (i * MASConnect4Displayable.CEL_WIDTH, j * MASConnect4Displayable.CEL_HEIGHT)
                        if self.board[i][j] == self.PLAYER:
                            render.blit(player_pin, (MASConnect4Displayable.CEL_BASE_X_POS + x, MASConnect4Displayable.CEL_BASE_Y_POS + y))
            
            for i in self.board:
                if self.AI in i:
                    # prepare the AI pins as renderer
                    ai_pin = renpy.render(MASConnect4Displayable.AI_IMAGE, 1280, 720, st , at)
            
            for i in range(len(self.board)):
                if self.AI in self.board[i]:
                    # draw the AI pins
                    for j in range(len(self.board[i])):
                        y, x = (i * MASConnect4Displayable.CEL_WIDTH, j * MASConnect4Displayable.CEL_HEIGHT)
                        if self.board[i][j] == self.AI:
                            render.blit(ai_pin, (MASConnect4Displayable.CEL_BASE_X_POS + x, MASConnect4Displayable.CEL_BASE_Y_POS + y))
                    
            # draw col buttons
            for b in col_buttons:
                render.blit(b[0], (b[1], b[2]))
                
            # draw menu buttons
            for b in visible_buttons:
                render.blit(b[0], (b[1], b[2]))
            
            renpy.redraw(self, 0)
            return render
            
        def set_button_states(self):
            """
            Disable/enable buttons according to other variables
            """
            if not self.is_game_over and self.turn == self.PLAYER:
            
                for b in range(len(self._col_buttons)):
                    if self.board[0][b] == self.EMPTY:
                        self._col_buttons[b].enable()
                    else:
                        self._col_buttons[b].disable()
                
                self._button_quit.enable()
                
                self._button_done.disable()
                
            else:
            
                for b in self._col_buttons:
                    b.disable()
                
                self._button_quit.disable()
                
                self._button_done.enable()
            
        def event(self, ev, x, y, st):
            """
            Function for events. Is called internally by renpy on its own (i guess)
            """
            if ev.type in self.MOUSE_EVENTS:
                ret_value = None
                for b in self._col_buttons:
                    if type(b.event(ev, x, y, st)) is int:
                        ret_value = b.event(ev, x, y, st)
                        self.col_fill(ret_value, self.turn)
                        return "mouse_button_up"
                
                if self._visible_buttons or self._visible_buttons_winner:
                    ret_value = self.check_buttons(ev, x, y, st)

                if ret_value is not None:
                    return ret_value
                    
            return None
            
        def check_buttons(self, ev, x, y, st):
            """
            Checks if menu buttons are pressed
            """
            if self.is_game_over:
                if self._button_done.event(ev, x, y, st):
                    self.quit_game = True
                    return (self.winner, 0)
                    
            elif self.turn == self.PLAYER:
                if self._button_quit.event(ev, x, y, st):
                    self.quit_game = True
                    return (self.winner, 1)

        def show(self):
            """
            Shows this displayable
            """
            ui.layer("minigames")
            ui.implicit_add(self)
            ui.close()

        def hide(self):
            """
            Hides this displayable
            """
            ui.layer("minigames")
            ui.remove(self)
            ui.close()
            
        def turn_switch(self):
            """
            Switches turn (obviously)
            """
            self.turn = self.PLAYER if self.turn == self.AI else self.AI
            self.turn_move_success = False
                
        # GET LINE UP FUNCTIONS START
        # These functions return a LIST of LINE UPS
        # a LINE UP is a LIST of the BOARD'S (KEY, VALUE) in tuple pair
        # didn't use dict() because it's unordered and the order needs to be preserved
        
        def get_vertical(self):
            """
            Returns vertical line ups
            """
            board_form = [[row[i] for row in self.BOARD_INDEX] for i in range(len(self.BOARD_INDEX[0]))]
            return board_form
            
        def get_horizontal(self):
            """
            Returns horizontal line ups
            """
            board_form = self.BOARD_INDEX
            return board_form
            
        def in_bounds(self, start_x, start_y):
            for i in self.BOARD_INDEX:
                if (start_x, start_y) in i:
                    return True
            return False
            
        def generate_diag(self, start_x, start_y, positive_slope):
            # also assuming top left is (0,0)
            if not self.in_bounds(start_x, start_y):
                return []
            
            if positive_slope:
                slope_mod = 1
            else:
                slope_mod = -1

            x = start_x
            y = start_y
            xy_tups = [(start_x, start_y)]
            while True:
                x += 1
                y += slope_mod

                if self.in_bounds(x, y):
                    xy_tups.append((x, y))
                else:
                    return xy_tups

            return xy_tups
                
        def get_diagonal_ltr(self):
            """
            Returns diagonal top Left To bottom Right (ltr) line ups
            """
            start_cels = [(2,0), (1,0), (0,0), (0,1), (0,2), (0,3)]
            board_form = list()
            for i in start_cels:
                board_form.append(self.generate_diag(i[0], i[1], True))
            return board_form
            
        def get_diagonal_rtl(self):
            """
            Returns diagonal top Right To bottom Left (rtl) line ups
            """
            start_cels = [(0,3), (0,4), (0,5), (0,6), (1,6), (2,6)]
            board_form = list()
            for i in start_cels:
                board_form.append(self.generate_diag(i[0], i[1], False))
            return board_form
                
        # GET LINE UP FUNCTIONS END
    
        def col_fill(self, col, turn):
            """
            Fills a column and signals the end of a turn
            
            INPUT:
                col = Which column to fill
                turn = Who is making the move
            """
            for i in range(5, -1, -1):
                if self.board[i][col] == self.EMPTY:
                    self.board[i][col] = turn
                    self.turn_move_success = True
                    break
        
        def check_connect(self, line_up):
            """
            Checks the board for 4 same pins in a row
            
            INPUT: a line up to check
            """
            for i in range(len(line_up)):
                if i+4 > len(line_up):
                    break
                four = [self.board[i2[0]][i2[1]] for i2 in line_up[i:i+4]]
                if four == [self.AI for i3 in range(4)] or four == [self.PLAYER for i3 in range(4)]:
                    self.win_set(four[0], line_up[i:i+4])
                    
        def examine_board(self):
            """
            Examines the board, called after every turn
            """
            for i in self.get_vertical():
                self.check_connect(i)
            for i in self.get_horizontal():
                self.check_connect(i)
            for i in self.get_diagonal_ltr():
                self.check_connect(i)
            for i in self.get_diagonal_rtl():
                self.check_connect(i)
                
            if len(self.board) >= 42:
                self.win_set()
                
            for i in range(self.CEL_COL):
                if self.board[0][i] != 0:
                    self.full_col.add(i)
                
        def player_move(self):
            """
            Player makes a move
            """
            interact = ui.interact(type="minigame")
            return interact
                
        def game_loop(self):
            """
            The game loop where things happen
            """
            while not self.quit_game:
                self.set_button_states()
            
                while not self.turn_move_success:
                    if self.turn == self.AI and not self.is_game_over:
                        self.ai_move()
                    else:
                        interact = self.player_move()
                        break
                self.turn_switch()
                
                self.examine_board()
                
                # Debug Stuff, Don't Mind These
                # if len(self.win_tiles) > 0:
                    # say = " ".join(self.win_tiles)
                    # renpy.say(m, say, interact=False)
                
                if self.quit_game:
                    return interact
        
        def win_set(self, winner=False, win_tiles=None):
            """
            Sets win variables
            
            INPUT:
                winner = the winner of the game
                win_tiles = tiles where the win happen
            """
            if win_tiles != None:
                for i in win_tiles:
                    self.win_tiles.add(i)
            self.is_game_over = True
            if winner:
                self.winner = winner
            
        # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX AI CODES XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
            
        def get_winning_line_up(self, pin, line_up):
            """
            Returns tiles where one of the player is about to win the next move
            
            INPUT:
                pin = which player's pins to check for
                line_up = the line up to check
                
            OUTPUT: a list of cels where winning move can be made the next turn
            """
            winning_line_up = list()
            for i in range(len(line_up)):
                if i+4 > len(line_up):
                    break
                four = [self.board[i2[0]][i2[1]] for i2 in line_up[i:i+4]]
                if four.count(pin) == 3 and self.EMPTY in four:
                    for i3 in range(len(four)):
                        if four[i3] is self.EMPTY:
                            winning_line_up.append(line_up[i+i3])
                            
            return winning_line_up
            
        def get_ai_winning_cels(self):
            """
            Returns cels where the AI can win using get_winning_line_up function
            
            OUTPUT: a list of cels where AI can win the next move
            """
            winning_cels = list()
            for line_up in self.get_vertical():
                winning_cels.extend(self.get_winning_line_up(self.AI, line_up))
            for line_up in self.get_horizontal():
                winning_cels.extend(self.get_winning_line_up(self.AI, line_up))
            for line_up in self.get_diagonal_ltr():
                winning_cels.extend(self.get_winning_line_up(self.AI, line_up))
            for line_up in self.get_diagonal_rtl():
                winning_cels.extend(self.get_winning_line_up(self.AI, line_up))
            return winning_cels
            
        def get_player_winning_cels(self):
            """
            Returns cels where the player can win using get_winning_line_up function
            
            OUTPUT: a list of cels where player can win the next move
            """
            winning_cels = list()
            for line_up in self.get_vertical():
                winning_cels.extend(self.get_winning_line_up(self.PLAYER, line_up))
            for line_up in self.get_horizontal():
                winning_cels.extend(self.get_winning_line_up(self.PLAYER, line_up))
            for line_up in self.get_diagonal_ltr():
                winning_cels.extend(self.get_winning_line_up(self.PLAYER, line_up))
            for line_up in self.get_diagonal_rtl():
                winning_cels.extend(self.get_winning_line_up(self.PLAYER, line_up))
            return winning_cels
        
        def get_two_pin_line_up(self, pin, line_up):
            two_pin_line_up = list()
            for i in range(len(line_up)):
                if i+4 > len(line_up):
                    break
                four = (line_up[i:i+4], [self.board[i2[0]][i2[1]] for i2 in line_up[i:i+4]])
                if four[1] == [self.EMPTY, pin, pin, self.EMPTY]:
                    for i3 in range(len(four[1])):
                        if four[1][i3] is self.EMPTY:
                            is_bottom_good = four[0][i3][0] == 5 or self.board[four[0][i3][0] + 1][four[0][i3][1]] is not self.EMPTY
                            if is_bottom_good:
                                two_pin_line_up.append(four[0][i3])
                            
            return two_pin_line_up
            
        def get_player_two_pin_cels(self):
            two_pin_cels = list()
            for line_up in self.get_horizontal():
                two_pin_cels.extend(self.get_two_pin_line_up(self.PLAYER, line_up))
            for line_up in self.get_diagonal_ltr():
                two_pin_cels.extend(self.get_two_pin_line_up(self.PLAYER, line_up))
            for line_up in self.get_diagonal_rtl():
                two_pin_cels.extend(self.get_two_pin_line_up(self.PLAYER, line_up))
            return two_pin_cels
    
        def ai_move(self):
            """
            Tells the AI to move
            """
            # first we get the cels where someone can win
            ai_winning_try_moves = list(self.get_ai_winning_cels())
            player_winning_try_moves = list(self.get_player_winning_cels())
            player_two_pin_try_moves = list(self.get_player_two_pin_cels())
            
            while not self.turn_move_success:
                renpy.pause(1.5)
                
                # the AI checks where it can win first. if found, makes a move there to win
                while ai_winning_try_moves and not self.turn_move_success:
                    try_fill = random.choice(ai_winning_try_moves)
                    is_bottom_good = try_fill[0] == 5 or self.board[try_fill[0] + 1][try_fill[1]] is not self.EMPTY
                    if is_bottom_good:
                        self.col_fill(try_fill[1], self.AI)
                    else:
                        ai_winning_try_moves.remove(try_fill)
                
                # if there are no winning move, check for tiles where player can win to cancel them from winning
                while player_winning_try_moves and not self.turn_move_success:
                    try_fill = random.choice(player_winning_try_moves)
                    is_bottom_good = try_fill[0] == 5 or self.board[try_fill[0] + 1][try_fill[1]] is not self.EMPTY
                    if is_bottom_good:
                        self.col_fill(try_fill[1], self.AI)
                    else:
                        player_winning_try_moves.remove(try_fill)
                
                # if there are no player winning move, block player's chance of winning next turn when there are two of their pins in adjacent tiles
                while player_two_pin_try_moves and not self.turn_move_success:
                    try_fill = random.choice(player_two_pin_try_moves)
                    is_bottom_good = try_fill[0] == 5 or self.board[try_fill[0] + 1][try_fill[1]] is not self.EMPTY
                    if is_bottom_good:
                        self.col_fill(try_fill[1], self.AI)
                    else:
                        player_two_pin_try_moves.remove(try_fill)
                        
                # makes a random move if there are no winning tiles lol
                if not self.turn_move_success:
                    self.col_fill(renpy.random.choice(list({i for i in range(self.CEL_COL)} - self.full_col)), self.AI)
        
    
    
label game_connect4:
    m 2esa "Wanna play connect 4?"
    $ connect4_play_again = True
    while connect4_play_again:
        m 3eub "First, let's flip a coin."
        $ choice = random.randint(0, 1) == 0
        if choice:
            $ connect4_first_turn = 2
            m 2eua "Oh, looks like you go first, [player]."
        else:
            $ connect4_first_turn = 1
            m 2eua "Looks like I go first, [player]."
        m 2hua "Let's start~!"
        
        label start_connect4:
            pass
            
        window hide None
        show monika 1eua at t21
        python:
            quick_menu = False
            
            connect4_displayable_obj = MASConnect4Displayable(connect4_first_turn)
            connect4_displayable_obj.show()
            results = connect4_displayable_obj.game_loop()
            connect4_displayable_obj.hide()
            
            quick_menu = True
            
            winner, ending = results
            
        label .connect4_end:
            pass

        show monika at t11
        
        if winner == False:
            if ending == 0:
                m 2wud "Oh, it's a draw."
                m 2rksdlb "I mean, I saw it coming, but it's quite a rare circumstance."
            elif ending == 1:
                m 6ekc "Oh? You want to quit?"
                m 6eksdld "But I was having so much fun, [player]."
                m 1gksdlc "Oh well..."
                m 1eka "Let's play again some time."
                $ connect4_play_again = False
                
        else:
            if winner == 1:
                m 2wub "I won!"
                m 2tsa "Better luck next time, [player]."
                
            elif winner == 2:
                m 2wub "Oh, you won."
                m 2tfa "You're lucky this time."
            
        if ending == 0:
            m 2eua "Do you want to play again?{nw}"
            $ _history_list.pop()
            menu:
                m "Do you want to play again?{fast}"
                
                "Yes.":
                    pass
                "No.":
                    m "Alright, then."
                    m 1eka "Let's play again some time."
                    $ connect4_play_again = False
    return
            
            
            
init 5 python:
    addEvent(
        Event(
            persistent.event_database,
            eventlabel="mas_unlock_connect4",
            conditional="store.mas_xp.level() >= 0",
            # action=EV_ACT_QUEUE,
            action=EV_ACT_PUSH,
            # aff_range=(mas_aff.AFFECTIONATE, None)
            aff_range=(None, None)
        )
    )

label mas_unlock_connect4:
    m 2hua "Hey! I've got something exciting to tell you!"
    m 2eua "I've finally added connect 4 for us to play, [player]."
    $ mas_unlockGame("connect 4")
    return



















