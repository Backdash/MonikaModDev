init python in mas_connect4:

    import copy
    
    CONNECT4_AI = "Monika"
    
    CONNECT4_PLAYER = renpy.game.persistent.playername
    
    CONNECT4_COLUMN_EMPTY = [0,0,0,0,0,0]
    
    CONNECT4_BOARD_EMPTY = [copy.copy(CONNECT4_COLUMN_EMPTY),copy.copy(CONNECT4_COLUMN_EMPTY),copy.copy(CONNECT4_COLUMN_EMPTY),copy.copy(CONNECT4_COLUMN_EMPTY),copy.copy(CONNECT4_COLUMN_EMPTY),copy.copy(CONNECT4_COLUMN_EMPTY),copy.copy(CONNECT4_COLUMN_EMPTY)]

    connect4_board = copy.deepcopy(CONNECT4_BOARD_EMPTY)
    
    connect4_game_over = False
    
    connect4_win = False
    
    connect4_winner = "draw"
    
    connect4_turn = CONNECT4_AI
    
    connect4_turn_moved = False
    
    connect4_turn_invalid = False
    
    connect4_is_board_full = []
    
    
    
    def start_game():
        """
        Sets variables to it's default values at the beginning of game.
        """
        global connect4_board
        global connect4_win
        global connect4_winner
        global connect4_game_over
        connect4_board = copy.deepcopy(CONNECT4_BOARD_EMPTY)
        connect4_win = False
        connect4_winner = "draw"
        connect4_game_over = False
    
    
    
    def new_turn():
        """
        Sets variables to it's default values at the start of turn.
        """
        global connect4_is_board_full
        global connect4_turn_moved
        global connect4_turn_invalid
        connect4_is_board_full = []
        connect4_turn_moved = False
        connect4_turn_invalid = False
    
    
    
    def check_board_full():
        """
        Checks whether or not the board is full.
        Ends the game if there are no more moves available.
        """
        for line_up in connect4_board:
            for i in line_up:
                connect4_is_board_full.append(i)
        if 0 not in connect4_is_board_full:
            game_over()
    
    
    
    def check_overflow_move():
        """
        Checks if a move is made in a full column.
        If move is valid, changes turn to the other player,
        else, does not change the player turn until a valid move is made
        (Ideally this should be managed by the screen, having its button insensitive instead).
        """
        global connect4_turn_invalid
        global connect4_turn
        if connect4_turn_moved:
            connect4_turn = [CONNECT4_PLAYER,CONNECT4_AI][connect4_turn == CONNECT4_PLAYER]
        else:
            connect4_turn_invalid = True
    
        
    
    def check_connect(line_up):
        """
        Checks if there are four same color checker pins in a list.
        Calls win_set(winner) if found.
        
        line_up inserts a list (the state of cells in the board; 1 = AI's pin, 2 = player's pin, 0 = empty).
        """
        four = []
        for i in range(len(line_up)):
            if i+4 > len(line_up):
                break
            four = line_up[i:i+4]
            if four == [1,1,1,1] or four == [2,2,2,2]:
                win_set(four[0])
    
    
    
    def win_set(winner):
        """
        Sets connect4_winner variable based on the parameter.
        
        winner inserts integer that corresponds to either player or AI (1 or 2).
        """
        global connect4_win
        global connect4_winner
        connect4_win = True
        if winner == 2:
            connect4_winner = CONNECT4_PLAYER
        else:
            connect4_winner = CONNECT4_AI
    
    
    
    def examine_vertical():
        """
        Examines the board vertically using check_connect(line_up).
        """
        board_form = connect4_board
        for line_up in board_form:
            check_connect(line_up)
            if connect4_win == True:
                game_over()
                break
    
    
    
    def examine_horizontal():
        """
        Examines the board horizontally using check_connect(line_up).
        """
        board_form = [[row[i] for row in connect4_board] for i in range(len(connect4_board[0]))]
        for line_up in board_form:
            check_connect(line_up)
            if connect4_win == True:
                game_over()
                break
    
    
    
    def examine_diagonal_ltr():
        """
        Examines the board diagonally using check_connect(line_up).
        There are two functions to manage the two diagonals (ltr ans rtl).
        """
        board_form = []
        
        item_length = 1
        item_sum = len(connect4_board[0])
        for i in range(item_sum):
            item = []
            for i2 in range(item_length):
                item.append(connect4_board[(len(connect4_board)-1)-i2][(item_length-1)-i2])
            board_form.append(item)
            item_length += 1
        
        item_length = 6
        item_sum = len(connect4_board) - 1
        for i in range(item_sum):
            item = []
            for i2 in range(item_length):
                item.append(connect4_board[(item_length-1)-i2][(len(connect4_board[0])-1)-i2])
            board_form.append(item)
            item_length -= 1
        
        for line_up in board_form:
            check_connect(line_up)
            if connect4_win == True:
                game_over()
                break
    
    
    
    def examine_diagonal_rtl():
        """
        Examines the board diagonally using check_connect(line_up).
        There are two functions to manage the two diagonals (ltr ans rtl).
        """
        board_form = []
        
        item_length = 1
        item_sum = len(connect4_board[0])
        for i in range(item_sum):
            item = []
            for i2 in range(item_length):
                item.append(connect4_board[(len(connect4_board)-1)-i2][(len(connect4_board[0])-1)-(item_length-1)+i2])
            board_form.append(item)
            item_length += 1
            
        item_length = 6
        item_sum = len(connect4_board) - 1
        for i in range(item_sum):
            item = []
            for i2 in range(item_length):
                item.append(connect4_board[(len(connect4_board)-2)-i-i2][0+i2])
            board_form.append(item)
            item_length -= 1
        
        for line_up in board_form:
            check_connect(line_up)
            if connect4_win == True:
                game_over()
                break
    
    
    
    def game_over():
        """
        The game over function. calls the corresponding game over labels (win or draw).
        """
        global connect4_game_over
        connect4_game_over = True
        renpy.show_screen("connect4_static")
    
    
    
    def col_fill(col,turn):
        """
        Makes a move and fills the board.
        
        col inserts which column to fill (one int of 0 to 6).
        turn inserts who makes the move (int of 1 or 0).
        """
        global connect4_turn_moved
        if turn is CONNECT4_PLAYER:
            checker = 2
        else:
            checker = 1
        for i in range(len(connect4_board[col])):
            if connect4_board[col][i] == 0:
                connect4_board[col][i] = checker
                connect4_turn_moved = True
                break
                
                
                
    def examine_board():
        """
        Calls all the examine functions together (ideally, the order should be random).
        """
        examine_diagonal_ltr()
        examine_diagonal_rtl()
        examine_horizontal()
        examine_vertical()
        
        
        
    
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX AI CODES XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    
    
    def check_ai_win(line_up):
        """
        This code works kind of like check_connect(line_up),
        but instead of 4 of the same pins, it checks for 3 AI pins.
        
        line_up inserts a list.
        
        returns a list that corresponds at which index in line_up is found an empty cell among 3 AI pins
        """
        four = []
        winning_line_up = []
        for i in range(len(line_up)):
            if i+4 > len(line_up):
                break
            four = line_up[i:i+4]
            if four.count(1) == 3 and 2 not in four:
                winning_line_up.append(i+four.index(0))
        winning_line_up = list(dict.fromkeys(winning_line_up))
        return winning_line_up
    
    
    def check_player_win(line_up):
        """
        This code works kind of like check_connect(line_up),
        but instead of 4 of the same pins, it checks for 3 player pins.
        
        line_up inserts a list.
        
        returns a list that corresponds at which index in line_up is found an empty cell among 3 player pins
        """
        four = []
        winning_line_up = []
        for i in range(len(line_up)):
            if i+4 > len(line_up):
                break
            four = line_up[i:i+4]
            if four.count(2) == 3 and 1 not in four:
                winning_line_up.append(i+four.index(0))
        winning_line_up = list(dict.fromkeys(winning_line_up))
        return winning_line_up
        
        
        
    def get_scan_diagonal_ltr(check_function):
        """
        This function is part of get_ai_win_cels() and get_player_win_cels() and is called there.
        
        Manages ltr diagonal.
        """
        board_form = []
        item_length = 1
        item_sum = len(connect4_board[0])
        for i in range(item_sum):
            item = []
            for i2 in range(item_length):
                item.append(connect4_board[(len(connect4_board)-1)-i2][(item_length-1)-i2])
            board_form.append(item)
            item_length += 1
        item_length = 6
        item_sum = len(connect4_board) - 1
        for i in range(item_sum):
            item = []
            for i2 in range(item_length):
                item.append(connect4_board[(item_length-1)-i2][(len(connect4_board[0])-1)-i2])
            board_form.append(item)
            item_length -= 1
        
        scan_diagonal_ltr = [[],[],[],[],[],[],[],[],[],[],[],[]]
        line_up_number = 0
        for line_up in board_form:
            for i in range(len(check_function(line_up))):
                scan_diagonal_ltr[line_up_number].append(check_function(line_up)[i])
            line_up_number += 1
        
        return scan_diagonal_ltr
        
        
        
    def get_scan_diagonal_ltr_board_form(scan_diagonal_ltr):
        """
        This function is part of get_ai_win_cels() and get_player_win_cels() and is called there.
        
        Manages ltr diagonal.
        """
        board_form = [[],[],[],[],[],[],[]]
        for i in range(6):
            for i2 in range(len(scan_diagonal_ltr[i])):
                board_form[6-scan_diagonal_ltr[i][i2]].append(i-scan_diagonal_ltr[i][i2])
        line_up_number = 0
        for i in range(6,12):
            for i2 in range(len(scan_diagonal_ltr[i])):
                board_form[5-line_up_number-scan_diagonal_ltr[i][i2]].append(5-scan_diagonal_ltr[i][i2])
            line_up_number += 1
            
        return board_form
        
        
        
    def get_scan_diagonal_rtl(check_function):
        """
        This function is part of get_ai_win_cels() and get_player_win_cels() and is called there.
        
        Manages rtl diagonal.
        """
        board_form = []
        item_length = 1
        item_sum = len(connect4_board[0])
        for i in range(item_sum):
            item = []
            for i2 in range(item_length):
                item.append(connect4_board[(len(connect4_board)-1)-i2][(len(connect4_board[0])-1)-(item_length-1)+i2])
            board_form.append(item)
            item_length += 1
        item_length = 6
        item_sum = len(connect4_board) - 1
        for i in range(item_sum):
            item = []
            for i2 in range(item_length):
                item.append(connect4_board[(len(connect4_board)-2)-i-i2][0+i2])
            board_form.append(item)
            item_length -= 1
            
        scan_diagonal_rtl = [[],[],[],[],[],[],[],[],[],[],[],[]]
        line_up_number = 0
        for line_up in board_form:
            for i in range(len(check_function(line_up))):
                scan_diagonal_rtl[line_up_number].append(check_function(line_up)[i])
            line_up_number += 1
            
        return scan_diagonal_rtl
        
        
        
    def get_scan_diagonal_rtl_board_form(scan_diagonal_rtl):
        """
        This function is part of get_ai_win_cels() and get_player_win_cels() and is called there.
        
        Manages rtl diagonal.
        """
        board_form = [[],[],[],[],[],[],[]]
        line_up_number = 5
        for i in range(6):
            for i2 in range(len(scan_diagonal_rtl[i])):
                board_form[6-scan_diagonal_rtl[i][i2]].append(line_up_number+scan_diagonal_rtl[i][i2])
            line_up_number -= 1
        line_up_number = 0
        for i in range(6,12):
            for i2 in range(len(scan_diagonal_rtl[i])):
                board_form[5-line_up_number-scan_diagonal_rtl[i][i2]].append(scan_diagonal_rtl[i][i2])
            line_up_number += 1
            
        return board_form
        
        
        
    # AI WIN SCAN =======================================================================================================
        
        
    def get_ai_win_cels():
        """
        *This function is pretty big.* (even has a mark of its own ^)
        It gives a collection of cells that are 1 pin away for the AI to win.
        Manages to do it vertically, horizontally, and diagonally (two diagonals).
        
        The diagonals are a little too long for me to comfortably put here too, so they are managed in another function
        (they are same functions used in get_player_win_cels()).
        
        returns a 2D list. With the length of 7 (width of board) and contains lists filled with indexes of those possible wins in the column.
        """
        ai_win_cels = [[],[],[],[],[],[],[]]
        
        
        # Add vertical winning cels ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        board_form = connect4_board
        
        scan_vertical = [[],[],[],[],[],[],[]]
        line_up_number = 0
        for line_up in board_form:
            for i in range(len(check_ai_win(line_up))):
                scan_vertical[line_up_number].append(check_ai_win(line_up)[i])
            line_up_number += 1
            
        line_up_number = 0
        for line_up in scan_vertical:
            for i in line_up:
                ai_win_cels[line_up_number].append(i)
            line_up_number += 1
        
        
        # Add horizontal winning cels ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        board_form = [[row[i] for row in connect4_board] for i in range(len(connect4_board[0]))]
        
        scan_horizontal = [[],[],[],[],[],[]]
        line_up_number = 0
        for line_up in board_form:
            for i in range(len(check_ai_win(line_up))):
                scan_horizontal[line_up_number].append(check_ai_win(line_up)[i])
            line_up_number += 1
        
        board_form = [[],[],[],[],[],[],[]]
        for i in range(6):
            for i2 in scan_horizontal[i]:
                board_form[i2].append(i)
        scan_horizontal = board_form
        
        line_up_number = 0
        for line_up in scan_horizontal:
            for i in line_up:
                ai_win_cels[line_up_number].append(i)
            line_up_number += 1
            
        
        # Add diagonal (ltr) winning cels ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scan_diagonal_ltr = get_scan_diagonal_ltr_board_form(get_scan_diagonal_ltr(check_ai_win))
        
        line_up_number = 0
        for line_up in scan_diagonal_ltr:
            for i in line_up:
                ai_win_cels[line_up_number].append(i)
            line_up_number += 1
            
        
        # Add diagonal (rtl) winning cels ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scan_diagonal_rtl = get_scan_diagonal_rtl_board_form(get_scan_diagonal_rtl(check_ai_win))
        
        line_up_number = 0
        for line_up in scan_diagonal_rtl:
            for i in line_up:
                ai_win_cels[line_up_number].append(i)
            line_up_number += 1
            
            
        return ai_win_cels
        
        
        
    # PLAYER WIN SCAN =======================================================================================================
        
        
    def get_player_win_cels():
        """
        *This function is pretty big.* (even has a mark of its own ^)
        It gives a collection of cells that are 1 pin away for the player to win.
        Manages to do it vertically, horizontally, and diagonally (two diagonals).
        
        The diagonals are a little too long for me to comfortably put here too, so they are managed in another function
        (they are same functions used in get_ai_win_cels()).
        
        returns a 2D list. With the length of 7 (width of board) and contains lists filled with indexes of those possible wins in the column.
        """
        player_win_cels = [[],[],[],[],[],[],[]]
        
        
        # Add vertical winning cels ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        board_form = connect4_board
        
        scan_vertical = [[],[],[],[],[],[],[]]
        line_up_number = 0
        for line_up in board_form:
            for i in range(len(check_player_win(line_up))):
                scan_vertical[line_up_number].append(check_player_win(line_up)[i])
            line_up_number += 1
            
        line_up_number = 0
        for line_up in scan_vertical:
            for i in line_up:
                player_win_cels[line_up_number].append(i)
            line_up_number += 1
        
        
        # Add horizontal winning cels ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        board_form = [[row[i] for row in connect4_board] for i in range(len(connect4_board[0]))]
        
        scan_horizontal = [[],[],[],[],[],[]]
        line_up_number = 0
        for line_up in board_form:
            for i in range(len(check_player_win(line_up))):
                scan_horizontal[line_up_number].append(check_player_win(line_up)[i])
            line_up_number += 1
        
        board_form = [[],[],[],[],[],[],[]]
        for i in range(6):
            for i2 in scan_horizontal[i]:
                board_form[i2].append(i)
        scan_horizontal = board_form
        
        line_up_number = 0
        for line_up in scan_horizontal:
            for i in line_up:
                player_win_cels[line_up_number].append(i)
            line_up_number += 1
            
        
        # Add diagonal (ltr) winning cels ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scan_diagonal_ltr = get_scan_diagonal_ltr_board_form(get_scan_diagonal_ltr(check_player_win))
        
        line_up_number = 0
        for line_up in scan_diagonal_ltr:
            for i in line_up:
                player_win_cels[line_up_number].append(i)
            line_up_number += 1
            
        
        # Add diagonal (rtl) winning cels ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        scan_diagonal_rtl = get_scan_diagonal_rtl_board_form(get_scan_diagonal_rtl(check_player_win))
        
        line_up_number = 0
        for line_up in scan_diagonal_rtl:
            for i in line_up:
                player_win_cels[line_up_number].append(i)
            line_up_number += 1
            
            
        return player_win_cels
        
        
        
    def ai_move():
        """
        Makes a move based on get_player_win_cels() and get_ai_win_cels().
        If move based on those are not possible, makes a random column move.
        """
        moved = False
        for i in range(len(get_ai_win_cels())):
            if get_ai_win_cels()[i] is not []:
                for i2 in get_ai_win_cels()[i]:
                    if i2 == 0:
                        col_fill(i,CONNECT4_AI)
                        moved = True
                    elif connect4_board[i][i2-1] is not 0:
                        col_fill(i,CONNECT4_AI)
                        moved = True
                    if moved: break
            if moved: break 
                    
        for i in range(len(get_player_win_cels())):
            if get_player_win_cels()[i] is not []:
                for i2 in get_player_win_cels()[i]:
                    if i2 == 0:
                        col_fill(i,CONNECT4_AI)
                        moved = True
                    elif connect4_board[i][i2-1] is not 0:
                        col_fill(i,CONNECT4_AI)
                        moved = True
                    if moved: break
            if moved: break 
                
        if not moved:
            col_fill(renpy.random.randint(0,6),CONNECT4_AI)
            
            
            
screen connect4:
    modal True
    frame:
        xalign 0.5
        yalign 0.5
        
        vbox:
            vbox:
                xalign 0.5
                yalign 0.5
                grid 7 1:
                    spacing 10
                    for i in range(7):
                        frame:
                            imagebutton:
                                id "checker_in_" + str(i)
                                auto "mod_assets/connect4/images/arrow_down_%s.png"
                                action [Return(i)]
            
            frame:
                xalign 0.5
                yalign 0.5
                grid 7 6:
                    transpose True
                    for i in range(7):
                        for i2 in range(5,-1,-1):
                            if "012".find(str(mas_connect4.connect4_board[i][i2])) == -1:
                                add "mod_assets/connect4/images/connect4_cel_g.png"
                            else:
                                add "mod_assets/connect4/images/connect4_cel_" + str(mas_connect4.connect4_board[i][i2]) + ".png"

            
screen connect4_static:
    frame:
        xalign 0.5
        yalign 0.5
        
        vbox:
            vbox:
                xalign 0.5
                yalign 0.5
                grid 7 1:
                    spacing 10
                    for i in range(7):
                        frame:
                            imagebutton:
                                id "checker_in_" + str(i)
                                auto "mod_assets/connect4/images/arrow_down_%s.png"
                                sensitive False
            
            frame:
                xalign 0.5
                yalign 0.5
                grid 7 6:
                    transpose True
                    for i in range(7):
                        for i2 in range(5,-1,-1):
                            if "012".find(str(mas_connect4.connect4_board[i][i2])) == -1:
                                add "mod_assets/connect4/images/connect4_cel_g.png"
                            else:
                                add "mod_assets/connect4/images/connect4_cel_" + str(mas_connect4.connect4_board[i][i2]) + ".png"
        
    
    
label game_connect4:
    
label mas_connect4_game_loop:
    $ done = False
    while not done:
        $ mas_connect4.connect4_turn = mas_connect4.CONNECT4_PLAYER
        
        $ mas_connect4.start_game()
        
        m "Let's start."
        window hide
        while not mas_connect4.connect4_game_over:
            $ mas_connect4.new_turn()
            
            if mas_connect4.connect4_turn == mas_connect4.CONNECT4_PLAYER:
                call screen connect4
                $ mas_connect4.col_fill(_return,mas_connect4.connect4_turn)
            else:
                show screen connect4_static
                $ pause(0.2)
                $ mas_connect4.ai_move()
                hide screen connect4_static
            
            $ mas_connect4.examine_board()
            $ mas_connect4.check_overflow_move()
            $ mas_connect4.check_board_full()
        $ pause(5.0)
        
        
        hide screen connect4_static
        if not mas_connect4.connect4_win:
            m "Oh, it's a draw."
            m "I mean, I saw it coming, but it's quite a rare circumstance."
        else:
            if mas_connect4.connect4_winner == mas_connect4.CONNECT4_AI:
                m "I won!"
            else:
                m "Oh, you won."
            m "No matter the outcome, I love playing with you."
        
        
        m "Would you like to play again?{nw}"
        $ _history_list.pop()
        menu:
            m "Would you like to play again?{fast}"
            "Yes.":
                $ mas_connect4.connect4_game_over = False
            "No.":
                $ done = True
    
    m "Okay, let's play again later."
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



















