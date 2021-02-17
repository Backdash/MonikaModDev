
            
            
            
init python:
    import pygame
    import re
    
    class MASConnect4Displayable(renpy.Displayable):
        # pygame events
        MOUSE_EVENTS = (
            pygame.MOUSEMOTION,
            pygame.MOUSEBUTTONUP,
            pygame.MOUSEBUTTONDOWN
        )
        
        # variables to indicate Monika and player's pins/turn
        AI = 1
        PLAYER = 2
        
        # indicate the board's rows columns
        CEL_COL = 7
        CEL_ROW = 6
        
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
        
        def __init__(self):
            # prepare the Displayable
            super(MASConnect4Displayable, self).__init__()
            
            # init the variables
            self.is_game_over = False
            self.quit_game = False
            self.turn = renpy.random.choice([self.AI, self.PLAYER])
            self.board = dict()
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
                
            if self.PLAYER in self.board.values():
                # prepare the pins as renderer
                player_pin = renpy.render(MASConnect4Displayable.PLAYER_IMAGE, 1280, 720, st , at)
                
                # draw the player pins
                for key, pin in self.board.items():
                    y, x = (int(key[0]) * MASConnect4Displayable.CEL_WIDTH, int(key[1]) * MASConnect4Displayable.CEL_HEIGHT)
                    if pin == self.PLAYER:
                        render.blit(player_pin, (MASConnect4Displayable.CEL_BASE_X_POS + x, MASConnect4Displayable.CEL_BASE_Y_POS + y))
                        
            if self.AI in self.board.values():
                # prepare the AI pins as renderer
                ai_pin = renpy.render(MASConnect4Displayable.AI_IMAGE, 1280, 720, st , at)
                
                # draw the AI pins
                for key, pin in self.board.items():
                    y, x = (int(key[0]) * MASConnect4Displayable.CEL_WIDTH, int(key[1]) * MASConnect4Displayable.CEL_HEIGHT)
                    if pin == self.AI:
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
                    if self.board.get(self.g_k(0, b)) == None:
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

        def g_k(self, i, j):
            """
            g_k stands for "get key" (is meant to be short), used to get the board's cel
            
            INPUT: two integers that refers to a cel's coordinates on the board
            
            OUTPUT: a string, the cel's coordinate on the board
            """
            return str(i) + str(j)
            
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
            board_form = [[(self.g_k(j, i), self.board.get(self.g_k(j, i))) for j in range(self.CEL_ROW)] for i in range(self.CEL_COL)]
            return board_form
                    
        def get_horizontal(self):
            """
            Returns horizontal line ups
            """
            board_form = [[(self.g_k(i, j), self.board.get(self.g_k(i, j))) for j in range(self.CEL_COL)] for i in range(self.CEL_ROW)]
            return board_form
                
        def get_diagonal_ltr(self):
            """
            Returns diagonal top Left To bottom Right (ltr) line ups
            """
            board_form = list()
            for i in range(4):
                line_up = list()
                line_up2 = list()
                i2 = 0
                for j in range(6):
                    line_up.append((self.g_k(i+i2, j), self.board.get(self.g_k(i+i2, j))))
                    line_up2.append((self.g_k(j, i+i2), self.board.get(self.g_k(j, i+i2))))
                    i2 += 1
                if i != 0:
                    board_form.append(line_up)
                board_form.append(line_up2)
            return board_form
            
        def get_diagonal_rtl(self):
            """
            Returns diagonal top Right To bottom Left (rtl) line ups
            """
            board_form = list()
            for i in range(6):
                line_up = list()
                i2 = list(range(3, 9))
                for j in range(9):
                    line_up.append((self.g_k(i2[i]-j, j), self.board.get(self.g_k(i2[i]-j, j))))
                board_form.append(line_up)
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
                if self.board.get(self.g_k(i, col), 0) == 0:
                    self.board[self.g_k(i, col)] = turn
                    self.turn_move_success = True
                    break
        
        def check_connect(self, line_up):
            """
            Checks the board for 4 same pins in a row
            
            INPUT: a line up to check
            """
            l_line_up = list()
            for i, _i in line_up:
                l_line_up.append(i)
            for i in range(len(l_line_up)):
                if i+4 > len(l_line_up):
                    break
                four = [self.board.get(i2, None) for i2 in l_line_up[i:i+4]]
                if four == [self.AI for i2 in range(4)] or four == [self.PLAYER for i2 in range(4)]:
                    self.win_set(four[0], l_line_up[i:i+4])
                    
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
                if self.board.get(self.g_k(0, i), None) != None:
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
                if len(self.win_tiles) > 0:
                    say = " ".join(self.win_tiles)
                    renpy.say(m, say, interact=False)
                
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
                four = [i2 for i2 in line_up[i:i+4]]
                if [i2[1] for i2 in four].count(pin) == 3 and None in [i2[1] for i2 in four]:
                    for key, val in four:
                        if val is None:
                            winning_line_up.append(key)
                            
            for i in winning_line_up:
                if '-' in i or len(i) > 2:
                    winning_line_up.remove(i)
                elif int(i[0]) > 5 or int(i[1]) > 6:
                    winning_line_up.remove(i)
                            
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
    
        def ai_move(self):
            """
            Tells the AI to move
            """
            # first we get the cels where someone can win
            ai_winning_try_moves = list(self.get_ai_winning_cels())
            player_winning_try_moves = list(self.get_player_winning_cels())
            
            while not self.turn_move_success:
                renpy.pause(1.5)
                
                # the AI checks where it can win first. if found, makes a move there to win
                while ai_winning_try_moves and not self.turn_move_success:
                    try_fill = random.choice(ai_winning_try_moves)
                    is_bottom_good = try_fill[0] == '5' or self.board.get(self.g_k(int(try_fill[0]) + 1, int(try_fill[1])), None) is not None
                    if is_bottom_good:
                        self.col_fill(try_fill[1], self.AI)
                    else:
                        ai_winning_try_moves.remove(try_fill)
                
                # if there are no winning move, check for tiles where player can win to cancel them from winning
                while player_winning_try_moves and not self.turn_move_success:
                    try_fill = random.choice(player_winning_try_moves)
                    is_bottom_good = try_fill[0] == '5' or self.board.get(self.g_k(int(try_fill[0]) + 1, int(try_fill[1])), None) is not None
                    if is_bottom_good:
                        self.col_fill(try_fill[1], self.AI)
                    else:
                        player_winning_try_moves.remove(try_fill)
                        
                # makes a random move if there are no winning tiles lol
                if not self.turn_move_success:
                    self.col_fill(renpy.random.choice(list({i for i in range(self.CEL_COL)} - self.full_col)), self.AI)
        
    
    
label game_connect4:
    m "Let's start!"
    
    label start_connect4:
        pass
        
    window hide None
    show monika 1eua at t21
    python:
        quick_menu = False
        
        connect4_displayable_obj = MASConnect4Displayable()
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
            m "Oh, it's a draw."
            m "I mean, I saw it coming, but it's quite a rare circumstance."
        elif ending == 1:
            m "Oh? You want to quit?"
            m "I was having so much fun, [player]."
            m "Oh well..."
            m "Let's play again some time."
            
    else:
        if winner == 1:
            m "I won!"
            
        elif winner == 2:
            m "Oh, you won."
            
        m "No matter the outcome, I love playing with you."
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



















