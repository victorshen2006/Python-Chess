#Victor Shen
#June 21, 2023
#AP Computer Science 30

#Import external modules used for the program
import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import Chess_move_history as Cmh
import time

#Define a class to operate the game
class Chess:
    def __init__(self):
        #Initialize a pre-game homepage, and values used for game transition
        self.window = Tk()
        self.pre_game = True
        self.operate = False
        self.in_game = False
        self.new_game = True

        self.starting_screen()
        self.window.mainloop() 

    def starting_screen(self):
        #Generate a homepage
        if self.pre_game:
            self.game_board = Canvas(self.window, width = 800, height = 1000, background = "#eeeed2")
            self.game_board.pack()

        #Create a background image
        self.image = Image.open("Background.png")
        self.image = self.image.resize((800, 1000))
        self.image = ImageTk.PhotoImage(self.image)
        self.game_board.create_image(400, 500, image = self.image)      #The background image is fuond from the following webstie: https://www.pexels.com/public-domain-images/

        #Create a button that starts the game
        start_game = tk.Button(self.window, text = "    Play    ", bg = "#eeeed2", fg = "black", font = ("ComicSans 40 bold"), cursor = "circle", command = self.play_game)
        start_game.place(x=300, y=500)
    
    #Start the game
    def play_game(self):
        self.operate = True
        self.click(None)
    
    #Define a function that allows user to play the game using mouse key
    def click(self, event):
        #Start the game
        if self.operate:
            self.pre_game = False
            self.operate = False
            self.in_game = True
            self.game_board.destroy()
            self.game_map()
            return
        
        #In-game clicks to move pieces
        elif self.in_game:
            #Convert mouse coordinates to position on the grid
            position = [event.x // 75, (event.y - 50) // 75]
            
            #Avoid any clicks outside of the screen
            if position[1] > 7 or (position[0] > 7 or position[0] < 0):
                return

            #Display move history
            if (event.x >= 560 and event.x <= 600) and (event.y >= 10 and event.y <= 40):
                Cmh.show_move_history()
                print("\n")
            
            #Replay the match after the replay button is clicked
            elif (event.x >= 532.5 and event.x <= 557.5) and (event.y >= 12.5 and event.y <= 37.5):
                if self.restart:
                    #Clear the oringal game screen
                    self.game_board.destroy()
                    self.window.destroy()

                    #Load the past move from the text file into the class
                    file = open("Chess moves.txt", "r")
                    replay_moves = Replay(file.readlines())
                    replay_moves.game_map()
                    replay_moves.replay_game()

            #Restart the game
            elif self.restart:
                self.game_board.destroy()
                self.window.destroy()
                restart = Chess()
            
            #Mark the piece being clicked
            current_piece = self.map[position[1]][position[0]][self.opponent]

            #Pause the game for either player to decide their promotion
            if self.freeze:
                #Transform the pawn piece once a designated piece is selected
                if (event.x >= 240 and event.x <= 360) and (event.y >= 10 and event.y <= 40):
                    self.promoted = self.promoted_pieces[(event.x - 240) // 30]
                    self.promotion(self.pawn_postion[0], self.pawn_postion[1])

                    #Check for any check/checkmate/stalement after the promotion
                    self.refresh()
                    self.checked_grid(0, 32)
                    self.checked_moves = [[[] for i in range(8)] for j in range(8)]

                    if self.check[self.current_player]:
                        self.checkmate()
                    if self.turn >= 19:
                        self.stalement()
                else:
                    return
            
            #Avoid any clicks outside of the game board
            if position[1] < 0:
                return
                
            #When a player is being checked, only allow moves that resolves the check
            elif self.check[self.current_player] and (type(current_piece) != int and current_piece.color == self.colors[self.current_player]):
                #Empty out information about pre-existing highlighted moves once a new piece is selected
                for dot in self.grey_dot_display:
                    self.game_board.delete(dot)

                self.grey_dot = []
                self.grey_dot_display = []

                #Highlight (using a grey dot) all possible moves
                for move in self.checked_moves[position[1]][position[0]]:
                    dot = self.game_board.create_oval(move[0] * 75 + 25, move[1] * 75 + 75, move[0] * 75 + 50, move[1] * 75 + 100, fill = "#767676", outline = "")
                    self.grey_dot_display.append(dot)

                    #Update the piece that's ready to be moved
                    self.ready = True
                    self.piece = position

                    #Record the availible positions
                    self.grey_dot.append([move[0], move[1]])

            #Check if an allied piece is clicked 
            elif type(current_piece) != int and current_piece.color == self.colors[self.current_player]:
                #Stop the function if the piece is blocking a check
                self.stuck_piece = 0
                if self.str_stuck(position, self.linear_pieces_str[self.opponent]):
                    return
                self.stuck_piece = 0
                if self.dia_stuck(position, self.linear_pieces_dia[self.opponent]):
                    return

                #Empty out information about pre-existing highlighted moves once a new piece is selected
                for dot in self.grey_dot_display:
                    self.game_board.delete(dot)

                self.grey_dot = []
                self.grey_dot_display = []

                #Categorize pieces based on their types of movement
                #These pieces have a constant number of maximum movements despite their position on the board
                if current_piece.name in ["Pawn", "Knight", "King"]:
                    #Special moves for the king
                    if current_piece.name == "King":
                        #Prohibit the king from moving into a check
                        self.free_move = False
                        
                        #Apply the castling rule if it's availible for either rook
                        for rook in range(2):
                            direction = (-1) ** rook
                            if self.castle[self.current_player][rook]:
                                move = True
                                #Check if all the grids in between are safe
                                for grids in range(1, 3):
                                    if self.map[position[1]][position[0] - grids * direction][self.opponent]:
                                        move = False
                                        break
                                
                                if move:
                                    new_x = position[0] - 2 * direction

                                    dot = self.game_board.create_oval(new_x * 75 + 25, position[1] * 75 + 75, new_x * 75 + 50, position[1] * 75 + 100, fill = "#767676", outline = "")
                                    self.grey_dot_display.append(dot)
                                    self.grey_dot.append([new_x, position[1]])
                                    self.castled_move = [new_x, position[1], direction, direction * (rook - 2)] #Record the following information for castling: coordinates of the king and horizontal position of rook and the movement, horizontal position of the rook relative to the king before castling
                    else:
                        self.free_move = True

                    for move in current_piece.move:
                        #Acquire coordinates after movement
                        new_x = position[0] + move[0]
                        new_y = position[1] + move[1]

                        #Skip moves out of the board
                        if (new_x < 0 or new_x > 7) or (new_y < 0 or new_y > 7):
                            continue

                        possible_move = self.map[new_y][new_x][self.opponent]

                        #Skip moves occupied by an allied piece
                        if type(possible_move) != int:
                            if current_piece.name == "Pawn":
                                break
                            continue
                        
                        #Highlight all possible moves
                        if (not possible_move) or self.free_move: #Prevents the king from moving onto an unsafe spot
                            dot = self.game_board.create_oval(new_x * 75 + 25, new_y * 75 + 75, new_x * 75 + 50, new_y * 75 + 100, fill = "#767676", outline = "")
                            self.grey_dot_display.append(dot)

                            #Update the piece that's ready to be moved
                            self.ready = True
                            self.piece = position

                            #Record the availible positions
                            self.grey_dot.append([new_x, new_y])
                            continue
                    
                    #Special moves for pawns
                    self.direction = (-1) ** self.opponent
                    if current_piece.name == "Pawn":
                        #Pawns are able to take out opponent pieces on its front diagonal spots
                        for diagonal in [1, -1]:
                            #Acquire coordinates after movement
                            new_x = position[0] + diagonal
                            new_y = position[1] + self.direction

                            #Skip moves out of the board
                            if (new_x < 0 or new_x > 7) or (new_y < 0 or new_y > 7):
                                continue

                            #Check if the spot is taken by an opponent's piece
                            if type(self.map[new_y][new_x][self.current_player]) != int:
                                dot = self.game_board.create_oval(new_x * 75 + 25, new_y * 75 + 75, new_x * 75 + 50, new_y * 75 + 100, fill = "#767676", outline = "")
                                self.grey_dot_display.append(dot)

                                #Update the piece that's ready to be moved
                                self.ready = True
                                self.piece = position

                                #Record the availible positions
                                self.grey_dot.append([new_x, new_y])
                                continue

                        #Restrict pawns from taking opponent's piece directly in front of them
                        if type(self.map[position[1] + self.direction][position[0]][self.current_player]) != int:
                                #Remove availibility of the spot from data
                                for move in range(len(current_piece.move)):
                                    self.game_board.delete(self.grey_dot_display[0]) #Since the default move for a pawn is always highlighted first, it will always be on the zeroth position inside the array of highlighted spots
                                    self.grey_dot.pop(0)
                                    self.grey_dot_display.pop(0)

                        #Check if an en passant move is availible
                        if self.en_passant:
                            for side in [1, -1]:
                                if [position[0] + side, position[1] + self.direction] == self.en_passant:
                                        dot = self.game_board.create_oval(self.en_passant[0] * 75 + 25, self.en_passant[1] * 75 + 75, self.en_passant[0] * 75 + 50, self.en_passant[1] * 75 + 100, fill = "#767676", outline = "")
                                        self.grey_dot_display.append(dot)

                                        #Update the piece that's ready to be moved
                                        self.ready = True
                                        self.piece = position

                                        #Record the availible positions
                                        self.grey_dot.append([position[0] + side, position[1] + self.direction])
                                        

                #These pieces have a varying number of maximum movements based on their locations whether there're other pieces around them
                else:
                    for move in current_piece.move:
                        #Acquire coordinates after movement
                        new_x = position[0] + move[0]
                        new_y = position[1] + move[1]

                        #Continuously checking for availible moves in each direction until it runs into the edge of the board or another piece
                        while True:
                            #Skip moves out of the board
                            if (new_x < 0 or new_x > 7) or (new_y < 0 or new_y > 7):
                                break

                            #Skip moves occupied by an allied piece
                            if type(self.map[new_y][new_x][self.opponent]) != int:
                                break

                            #Check if the spot to be moved is empty
                            if type(self.map[new_y][new_x][self.current_player]) == int:
                                dot = self.game_board.create_oval(new_x * 75 + 25, new_y * 75 + 75, new_x * 75 + 50, new_y * 75 + 100, fill = "#767676", outline = "")
                                self.grey_dot_display.append(dot)

                                #Update the piece that's ready to be moved
                                self.ready = True
                                self.piece = position

                                #Record the availible positions
                                self.grey_dot.append([new_x, new_y])
                            
                            #Stop checking in that directon after running into an opponent piece
                            else:
                                dot = self.game_board.create_oval(new_x * 75 + 25, new_y * 75 + 75, new_x * 75 + 50, new_y * 75 + 100, fill = "#767676", outline = "")
                                self.grey_dot_display.append(dot)

                                #Update the piece that's ready to be moved
                                self.ready = True
                                self.piece = position

                                #Record all the availible positions
                                self.grey_dot.append([new_x, new_y])
                                break
                            
                            #Keep on moving forward in the current direction
                            new_x += move[0]
                            new_y += move[1]
        
            #Move a selected piece to a clicked location if it's highlighted
            elif self.ready:
                if position in self.grey_dot:
                    #Take out any opponent piece on that location
                    if type(self.map[position[1]][position[0]][self.current_player]) != int:
                        self.game_board.delete(self.display[position[1]][position[0]])

                    #Move the game piece on the screen
                    self.game_board.delete(self.display[self.piece[1]][self.piece[0]])
                    self.display[self.piece[1]][self.piece[0]] = 0
                    self.display[position[1]][position[0]] = self.game_board.create_image(position[0] * 75 + 37.5, position[1] * 75 + 87.5, image = self.map[self.piece[1]][self.piece[0]][self.opponent].image)

                    #Update data within the grid representation array
                    self.map[position[1]][position[0]][self.opponent] = self.map[self.piece[1]][self.piece[0]][self.opponent]
                    self.map[position[1]][position[0]][self.current_player] = 0
                    self.map[self.piece[1]][self.piece[0]] = [0, 0]

                    #Update position of rook after a castle move
                    if position == self.castled_move[:2] and self.map[position[1]][position[0]][self.opponent].name == "King":
                        self.game_board.delete(self.display[position[1]][position[0] + self.castled_move[3]])
                        self.display[position[1]][position[0] + self.castled_move[2]] = self.game_board.create_image((position[0] + self.castled_move[2]) * 75 + 37.5, position[1] * 75 + 87.5, image = self.map[position[1]][position[0] + self.castled_move[3]][self.opponent].image)
                        self.display[position[1]][position[0] + self.castled_move[3]] = 0

                        self.map[position[1]][position[0] + self.castled_move[2]][self.opponent] = self.map[position[1]][position[0] + self.castled_move[3]][self.opponent]
                        self.map[position[1]][position[0] + self.castled_move[3]][self.opponent] = 0
                        self.castle[self.current_player] = [False, False]

                        for item in range(self.current_player * 16, (self.current_player + 1) * 16):
                            if self.alive_pieces[item] == [self.castled_move[0] + self.castled_move[3], self.castled_move[1]]:
                                self.alive_pieces[item] = [self.castled_move[0] + self.castled_move[2], self.castled_move[1]]
                    
                    #Disable castling once the king or the rook has been moved
                    elif self.map[position[1]][position[0]][self.opponent].name == "King":
                        self.castle[self.current_player] = [False, False]
                    
                    elif self.map[position[1]][position[0]][self.opponent].name == "Rook":
                        self.castle[self.current_player][self.piece[0] % 2] = False

                    #Update the positoin for all pieces
                    for item in range(self.current_player * 16, (self.current_player + 1) * 16):
                        if self.alive_pieces[item] == self.piece:
                            self.alive_pieces[item] = position

                    #Update the pieces moving in straightline
                    self.linear_pieces_str = [[self.alive_pieces[0], self.alive_pieces[1], self.alive_pieces[4]], [self.alive_pieces[16], self.alive_pieces[17], self.alive_pieces[20]]]
                    self.linear_pieces_dia = [[self.alive_pieces[2], self.alive_pieces[3], self.alive_pieces[4]], [self.alive_pieces[18], self.alive_pieces[19], self.alive_pieces[20]]]
                    for item in range(32):
                        if (item % 16) in self.promoted_pawn_dia[item // 16]:
                            self.linear_pieces_dia[item // 16].append(self.alive_pieces[item])
                        elif (item % 16) in self.promoted_pawn_str[item // 16]:
                            self.linear_pieces_str[item // 16].append(self.alive_pieces[item])
                    
                    #Remove pieces that're taken out
                    for item in range(self.opponent * 16, (self.opponent + 1) * 16):
                        if self.alive_pieces[item] == position:
                            self.alive_pieces[item] = 0

                    #Reset game data
                    for dot in self.grey_dot_display:
                        self.game_board.delete(dot)

                    self.grey_dot = []
                    self.grey_dot_display = []
                    self.ready = False

                    #Take out a pawn if an en passant occurs
                    if self.en_passant == position and self.map[position[1]][position[0]][self.opponent].name == "Pawn":  
                        self.game_board.delete(self.display[position[1] - self.direction][position[0]])
                        self.display[position[1]][position[0] - self.direction] = 0
                        self.map[position[1]][position[0] - self.direction] = [0, 0]
                        
                    #Promote a pawn when it reaches the other end
                    if position[1] == self.starting_location[self.opponent] and self.map[position[1]][position[0]][self.opponent].name == "Pawn":
                        self.promotion(position[0], position[1])

                        #Records the position of the pawn
                        self.pawn_postion = position

                    #Remove pawn's ability to move steps forward after it has been moved
                    if self.map[position[1]][position[0]][self.opponent].name == "Pawn" and len(self.map[position[1]][position[0]][self.opponent].move) == 2:
                        self.map[position[1]][position[0]][self.opponent].move = self.map[position[1]][position[0]][self.opponent].move[:1]
                        #Activate the en passant indicator
                        self.en_passant = [position[0], position[1] - self.direction]
                        
                    else:
                        self.en_passant = []

                    #Record the move
                    text = self.number_to_letter.get(self.piece[0]) + str(8 - self.piece[1]) + self.number_to_letter.get(position[0]) + str(8 - position[1])
                    file = open("Chess moves.txt", "a")
                    file.write(text)
                    file.write("\n")
                    file.close()
                    self.piece = 0
                    
                    #Update the grids avaiible for access by pieces
                    self.refresh()
                    self.checked_grid(0, 32)
                    self.checked_moves = [[[] for i in range(8)] for j in range(8)]

                    #Alternate players
                    self.turn += 1
                    self.current_player = self.turn % 2
                    self.opponent = (self.turn + 1) % 2

                    #End the game if a checkmate of stalement occurs
                    if self.check[self.current_player]:
                        self.checkmate()
                    if self.turn >= 19:
                        self.stalement()
                    

#Declares checkmate
    def checkmate(self):
        self.checked_move()
        for row in self.checked_moves:
            for move in row:
                if move:
                    return
        win = tk.Label(self.window, text = "Checkmate for player {}! Click anywhere to restart".format(self.opponent + 1), bg = "#eeeed2", fg = "black", font = ("ComicSans 15 bold"), bd = 0)
        win.place(x=50, y=20)
        self.restart = True

        #Create a replay button icon
        self.replay_icon = Image.open("Replay.png")
        self.replay_icon = self.replay_icon.resize((25, 25))
        self.replay_icon = ImageTk.PhotoImage(self.replay_icon)
        self.game_board.create_image(545, 25, image = self.replay_icon)     #The image of the replay button is downloaded from the following website: https://www.flaticon.com/free-icon/replay_1142347

        
#Declare a stalemate
    def stalement(self):
        #Check if any of the piece is movable
        count = 0
        for item in self.alive_pieces[self.current_player * 16:(self.current_player + 1) * 16]:
            if not item:
                count += 1
                continue

            #Special case for the king
            if count == 7:
                for move in self.map[item[1]][item[0]][self.opponent].move:
                    #Acquire coordinates after movement
                    new_x = item[0] + move[0]
                    new_y = item[1] + move[1]

                    #Skip moves out of the board
                    if (new_x < 0 or new_x > 7) or (new_y < 0 or new_y > 7):
                        count += 1
                        continue

                    if self.map[new_y][new_x][self.opponent] == int:
                        return

            elif self.str_stuck(item, self.linear_pieces_str[self.opponent]) or self.dia_stuck(item, self.linear_pieces_dia[self.opponent]):
                count += 1
                continue
            else:
                if not self.ally_block(item):
                    return
                count += 1
        draw = tk.Label(self.window, text = "Stalement! Click anywhere to restart", bg = "#eeeed2", fg = "black", font = ("ComicSans 15 bold"), bd = 0)
        draw.place(x=50, y=20)
        self.restart = True

        #Create a replay button icon
        self.replay_icon = Image.open("Replay.png")
        self.replay_icon = self.replay_icon.resize((25, 25))
        self.replay_icon = ImageTk.PhotoImage(self.replay_icon)
        self.game_board.create_image(545, 25, image = self.replay_icon)


    #Allow a player to select a piece to promote their pawn into
    def promotion(self, x_position, y_position):
        if self.freeze:
            #Remove the pieces displayed above the game board and related data
            for image in self.selections:
                self.game_board.delete(image)
            
            self.selections = []
            self.temp = []
            self.freeze = False

            #Promote the pawn to the selected piece
            pawn_piece = self.map[y_position][x_position][self.current_player]
            self.game_board.delete(pawn_piece)
            self.map[y_position][x_position][self.current_player] = Pieces(pawn_piece.player, pawn_piece.color, self.promoted, 60)
            self.display[y_position][x_position] = self.game_board.create_image(x_position * 75 + 37.5, y_position * 75 + 87.5, image = self.map[y_position][x_position][self.current_player].image)

            #Record the promoted pieces
            for item in range(32):
                if self.alive_pieces[item] == [x_position, y_position]:
                    location = item

            if self.map[y_position][x_position][self.current_player].name == "Knight":
                return
            
            if self.map[y_position][x_position][self.current_player].name in ["Queen", "Rook"]:
                self.promoted_pawn_str[self.opponent].append(location)
            if self.map[y_position][x_position][self.current_player].name in ["Queen", "Bishop"]:
                self.promoted_pawn_dia[self.opponent].append(location)

        else:
            #Display pieces for the player to select
            self.selections = []
            self.temp = []
            self.promoted_pieces = ["Bishop", "Knight", "Rook", "Queen"]
            
            counter = 0
            for item in self.promoted_pieces:
                stats = Pieces(self.current_player + 1, self.colors[self.current_player], item, 30)
                self.temp.append(stats)
                images = self.game_board.create_image(counter * 30 + 255, 25, image = self.temp[counter].image)
                self.selections.append(images)
                counter += 1

            #Freeze the game
            self.freeze = True
    
    #Refresh the board for checks
    def refresh(self):
        for row in range(8):
            for column in range(8):
                for item in range(2):
                    if type(self.map[row][column][item]) == int:
                        self.map[row][column][item] = 0

    #Define a function to mark positions that can be accessed by pieces, this is done to prevent king from moving into a check spot
    def checked_grid(self, start, finish):
        self.check = [False, False]
        count = start
        for item in self.alive_pieces[start:finish]:
            #Check if each piece is still on the board
            if type(item) != int:
                #Split the pieces into two categories same as the click function
                if count % 16 < 5 or (count in self.promoted_pawn_dia[count // 16] or count in self.promoted_pawn_str[count // 16]):
                    for move in self.map[item[1]][item[0]][1 - count // 16].move:
                        #Acquire coordinates after movement
                        new_x = item[0] + move[0]
                        new_y = item[1] + move[1]

                        #Continuously checking for availible moves in each direction until it runs into the edge of the board or another piece
                        while True:
                            #Skip moves out of the board
                            if (new_x < 0 or new_x > 7) or (new_y < 0 or new_y > 7):
                                break

                            #Break the loop if the postion is taken by an allied piece
                            if type(self.map[new_y][new_x][1 - count // 16]) != int:
                                self.map[new_y][new_x][count // 16] += 1
                                break

                            #Add a count to empty spaces availible for this piece
                            if type(self.map[new_y][new_x][count // 16]) == int:
                                self.map[new_y][new_x][count // 16] += 1

                            #Check whether the current move has made a check toward their opponent
                            elif self.map[new_y][new_x][count // 16].name == "King":
                                self.check[1 - count // 16] = True
                                
                            #Stop checking loops in that directon after running into an opponent piece
                            else:
                                break
                            
                            #Keep on moving forward in the current direction
                            new_x += move[0]
                            new_y += move[1]

                else:
                    #Pawn's possible movement to empty spaces is different from it's movement in taking out other pieces 
                    if self.map[item[1]][item[0]][1 - count // 16].name == "Pawn":
                        moves = [[-1, -1 ** (self.opponent)], [1, -1 ** (self.opponent)]]
                    else:
                        moves = self.map[item[1]][item[0]][1 - count // 16].move

                    for move in moves:
                        #Acquire coordinates after movement
                        new_x = item[0] + move[0]
                        new_y = item[1] + move[1]

                        #Skip moves out of the board
                        if (new_x < 0 or new_x > 7) or (new_y < 0 or new_y > 7):
                            continue

                        #Add a count to empty spaces availible for this piece
                        if type(self.map[new_y][new_x][count // 16]) == int:
                            self.map[new_y][new_x][count // 16] += 1
                        
                        #Check whether the current move has made a check toward their opponent
                        elif self.map[new_y][new_x][count // 16].name == "King":
                            self.check[1 - count // 16] = True            
            count += 1   

    #Create a function to record all the possible moves for a player experiencing a check
    def checked_move(self):
        count = 0
        for item in self.alive_pieces[(self.current_player) * 16: (self.current_player + 1) * 16]:
            #Skip any pieces that're no longer on the board
            if type(item) == int:
                count += 1
                continue

            piece = self.map[item[1]][item[0]][self.opponent]

            #Split the moving pattern of into two categories
            if count < 5 or (count in self.promoted_pawn_dia[self.current_player] or count in self.promoted_pawn_str[self.current_player]):
                for move in piece.move:
                    #Acquire coordinates after movement
                    new_x = item[0] + move[0]
                    new_y = item[1] + move[1]

                    #Continuously checking for availible moves in each direction until it runs into the edge of the board or another piece
                    while True:
                        #Skip moves out of the board
                        if (new_x < 0 or new_x > 7) or (new_y < 0 or new_y > 7):
                            break

                        allied_piece = self.map[new_y][new_x][self.opponent]

                        #Skip moves occupied by an allied piece
                        if type(allied_piece) != int:
                            break
                        
                        possible_move = self.map[new_y][new_x][self.current_player]

                        #Temporarily change the data about opponent piece on that grid
                        if type(possible_move) != int:
                            oringinal_map = possible_move
                            self.map[new_y][new_x][self.current_player] = 0
                            for opp_piece in range(self.opponent * 16, (self.opponent + 1) * 16):
                                if self.alive_pieces[opp_piece] == [new_x, new_y]:
                                    self.alive_pieces[opp_piece] = 0
                                    position_holder = opp_piece
                                    replace_piece = True
                        else:
                            replace_piece = False

                        #Ensure that the check is resolved after the move
                        temp = self.check
                        self.map[new_y][new_x][self.opponent] = piece
                        self.map[item[1]][item[0]][self.opponent] = 0
                        self.refresh()
                        self.checked_grid((self.opponent) * 16, (self.opponent + 1) * 16)

                        #Record the move into the array if it satisfies the requirement
                        if not self.check[self.current_player]:
                            self.checked_moves[item[1]][item[0]].append([new_x, new_y])
                        
                        #Reset the game map to prior this stimulation
                        self.map[item[1]][item[0]][self.opponent] = piece
                        self.map[new_y][new_x][self.opponent] = 0

                        if replace_piece:
                            self.alive_pieces[position_holder] = [new_x, new_y]
                            self.map[new_y][new_x][self.current_player] = oringinal_map

                        #Stop checking loops in that directon after running into an opponent piece
                        if type(possible_move) != int:
                            break
                        
                        #Keep on checking grids in the current direction
                        new_x += move[0]
                        new_y += move[1]

            else:
                for move in piece.move:
                    #Acquire coordinates after movement
                    new_x = item[0] + move[0]
                    new_y = item[1] + move[1]

                    #Skip moves out of the board
                    if (new_x < 0 or new_x > 7) or (new_y < 0 or new_y > 7):
                        continue

                    allied_piece = self.map[new_y][new_x][self.opponent]

                    #Skip moves occupied by an allied piece
                    if type(allied_piece) != int:
                        continue

                    possible_move = self.map[new_y][new_x][self.current_player]

                    #Disable pawn moves that takes out pieces directly in front of them
                    if not (type(possible_move) != int and piece.name == "Pawn"):
                        #Temporarily change the data about opponent piece on that grid
                        if type(self.map[new_y][new_x][self.current_player]) != int:
                            oringinal_map = possible_move
                            self.map[new_y][new_x][self.current_player] = 0
                            for opp_piece in range(self.opponent * 16, (self.opponent + 1)* 16):
                                if self.alive_pieces[opp_piece] == [new_x, new_y]:
                                    self.alive_pieces[opp_piece] = 0
                                    position_holder = opp_piece
                                    replace_piece = True
                        else:
                            replace_piece = False

                        #Ensure that the check is resolved after the move
                        temp = self.check
                        self.map[new_y][new_x][self.opponent] = piece
                        self.map[item[1]][item[0]][self.opponent] = 0
                        self.refresh()
                        self.checked_grid((self.opponent) * 16, ((self.opponent + 1) * 16))

                        #Record the move into the array if it's viable
                        if not self.check[self.current_player]:
                            self.checked_moves[item[1]][item[0]].append([new_x, new_y])
                        
                        #Reset the game map to prior this stimulation
                        self.map[item[1]][item[0]][self.opponent] = piece
                        self.map[new_y][new_x][self.opponent] = 0

                        if replace_piece:
                            self.alive_pieces[position_holder] = [new_x, new_y]
                            self.map[new_y][new_x][self.current_player] = oringinal_map

                    #Special moves for pawns
                    self.direction = 2 * (self.current_player) - 1
                    if piece.name == "Pawn":
                        #Pawns are able to take out opponent pieces on its front diagonal spots
                        for diagonal in [1, -1]:
                            #Acquire item after movement
                            new_x = item[0] + diagonal
                            new_y = item[1] + self.direction

                            #Skip moves out of the board
                            if (new_x < 0 or new_x > 7) or (new_y < 0 or new_y > 7):
                                continue

                            possible_move = self.map[new_y][new_x][self.current_player]

                            #Check if the spot is taken by an opponent's piece
                            if type(possible_move) != int:
                                #Temporarily change the data about opponent piece on that grid
                                oringinal_map = self.map[new_y][new_x][self.current_player]
                                self.map[new_y][new_x][self.current_player] = 0
                                for opp_piece in range(self.opponent * 16, self.opponent * 16 + 16):
                                    if self.alive_pieces[opp_piece] == [new_x, new_y]:
                                        self.alive_pieces[opp_piece] = 0
                                        position_holder = opp_piece

                                #Ensure that the check is resolved after the move
                                temp = self.check
                                self.map[new_y][new_x][self.opponent] = piece
                                self.map[item[1]][item[0]][self.opponent] = 0
                                self.refresh()
                                self.checked_grid((self.opponent) * 16, (self.opponent + 1) * 16)

                                #Reset the game map to prior this stimulation
                                self.map[item[1]][item[0]][self.opponent] = piece
                                self.map[new_y][new_x][self.opponent] = 0
                                self.alive_pieces[position_holder] = [new_x, new_y]
                                self.map[new_y][new_x][self.current_player] = oringinal_map

                        #Check if an en passant move is availible
                        if self.en_passant:
                            for side in [1, -1]:
                                if [item[0] + side, item[1] + self.direction] == self.en_passant: 
                                    #Since en passant only takes a pawn and no other notable changes will occur on the board, it will only cancel a check if the check is done by the pawn that was taken out
                                    for king_position in [-2, 2]:
                                        if self.alive_pieces[(self % 2) * 16 + 7] == [item[0] + king_position, item[1] + (-1 ** (self.current_player))]:
                                            self.checked_moves[item[1]][item[0]].append([new_x, new_y])
                                            break
                                    break
            count += 1

    #Create two fucntions to check for pieces that can't be move (otherwise causing a check toward their own king)
    #The first function checks if a piece is in between the king and an opponnent's rook/queen
    def str_stuck(self, coordinates, pieces):
        #Avoid any input data that's not an array
        if (not coordinates) or coordinates == self.stuck_piece:
            return False

        #Check to see if the pieces its aligned in a straight line with the king
        distance = [coordinates[0] - self.alive_pieces[(self.current_player) * 16 + 7][0], coordinates[1] - self.alive_pieces[(self.current_player) * 16 + 7][1]]
        not_aligned = True
        if distance == [0, 0]:
            return False

        for item in range(2):
            if not distance[item]:
                distance[item - 1] = int(distance[item - 1] / abs(distance[item - 1]))
                not_aligned = False
                break

        if not_aligned:
            return False
        
        #Check if the piece is in between the king and an opponent's rook/queen
        for straight_piece in pieces:
            if not straight_piece:
                continue

            new_distance = [straight_piece[0] - coordinates[0], straight_piece[1] - coordinates[1]]
            if new_distance == [0, 0]:
                return False
            
            for item in range(2):
                if not new_distance[item]:
                    new_distance[item - 1] = int(new_distance[item - 1] / abs(new_distance[item - 1]))
                    break 

            #Use recursion to check if any other pieces is in between the king and the piece that may cause a check
            if new_distance == distance:
                if self.stuck_piece:
                    return True
                
                for other_piece in self.alive_pieces:
                    self.stuck_piece = coordinates
                    if self.str_stuck(other_piece, [straight_piece]):
                        return False
                return True
            else:
                continue
        return False

    #The second function checks if a piece is in between the king and an opponent's bishop/queen
    def dia_stuck(self, coordinates, pieces):
        #Avoid any input data that's not an array
        if (not coordinates) or coordinates == self.stuck_piece:
            return False
        
        #Check to see if the pieces its aligned in a straight line with the king
        distance = [coordinates[0] - self.alive_pieces[(self.current_player) * 16 + 7][0], coordinates[1] - self.alive_pieces[(self.current_player) * 16 + 7][1]]

        if 0 in distance:
            return False
        
        absolute_value = abs(distance[0])
        if  absolute_value == abs(distance[1]):
            distance = [int(distance[0] / absolute_value), int(distance[1] / absolute_value)]
        else:
            return False
        
        #Check if the piece is in between the king and a bishop/queen
        for diagoanl_piece in pieces:
            if not diagoanl_piece:
                continue

            new_distance = [diagoanl_piece[0] - coordinates[0], diagoanl_piece[1] - coordinates[1]]
            aligned = True
            if 0 in new_distance:
                continue
            
            if abs(new_distance[0]) != abs(new_distance[1]):
                continue

            for item in range(2):
                if new_distance[item] // distance[item] < 0:
                    aligned = False
                    break
            
            #Use recursion to check if any other pieces is in between the king and the piece that may cause a check
            if aligned:
                if self.stuck_piece:
                    self.piece = 0
                    return True
                
                for other_piece in self.alive_pieces:
                    self.stuck_piece = coordinates
                    if self.dia_stuck(other_piece, [diagoanl_piece]):
                        return False
                return True
            else:
                continue
        return False

    #Define a function to check if a piece has all of its moves blocked by allied pieces
    def ally_block(self, coordinates):
        piece = self.map[coordinates[1]][coordinates[0]][self.opponent]

        #Special case for pawns
        if piece.name == "Pawn":
            if type(self.map[coordinates[1] - (-1 ** (self.current_player))][self.current_player]) != int:
                return True
            for move in [1, -1]:
                if type(self.map[coordinates[1] - (-1 ** (self.current_player))][coordinates[0] + move][self.current_player]) != int:
                    return False

                elif [coordinates[1] - (-1 ** (self.current_player)), coordinates[0] + move] == self.en_passant:
                    return False
        
        for move in piece.move:
            #Acquire coordinates after movement
            new_x = coordinates[0] + move[0]
            new_y = coordinates[1] + move[1]

            #Skip moves out of the board
            if (new_x < 0 or new_x > 7) or (new_y < 0 or new_y > 7):
                continue

            #Skip moves occupied by an allied piece
            if type(self.map[new_y][new_x][self.opponent]) == int:
                return False
        return True
                                    
    #Generate all inforamtion about the game
    def game_map(self):
        #Create the game board and game data
        self.game_board = Canvas(self.window, width = 600, height = 650, background = "#eeeed2")

        #Filling in the color tiles used for chess
        for row in range(8):
            for column in range(8):
                if (row + column) % 2 == 1:
                    self.game_board.create_rectangle(75 * column, 75 * row + 50, 75 * (column + 1), 75 * (row + 1) + 50, fill = "#769656", outline = "")

        #Createa a dictionary that converts number to alphabetic letters used to track moves
        self.number_to_letter = {0:"a", 1:"b", 2:"c", 3:"d", 4:"e", 5:"f", 6:"g", 7:"h"}

        #Add in letters and numbers indicating the locations of each tile onto the game board
        self.colors = ["#769656", "#eeeed2"]
        for row in range(8):
            self.coordinate = tk.Label(self.window, text = str(8 - row), bg = self.colors[(row + 1) % 2], fg = self.colors[row % 2], bd = 0)
            self.coordinate.place(x=5, y=row*75 + 55)

        for column in range(8):
            self.coordinate = tk.Label(self.window, text = self.number_to_letter.get(column), bg = self.colors[column % 2], fg = self.colors[(column + 1) % 2], bd = 0)
            self.coordinate.place(x=column*75 + 60, y=630)

        #Create arrays recording information about the game board and game pieces
        self.map = [[[0, 0] for i in range(8)] for j in range(8)]  
        self.display = [[0 for i in range(8)] for j in range(8)]
        self.alive_pieces = []
        self.colors = ("White", "Black") #A tuple is used instead of an array since the color of pieces stays unchanged
      
        #Initialize each piece as a class object and display them onto the game board, then record these data
        self.starting_location = [7, 0]
        for players in range(2):
            #Track the horizontal grid poisiton of the array and the board side for each player
            counter = 0
            edge = self.starting_location[players]

            for piece in ["Rook", "Knight", "Bishop"]:
                self.map[edge][counter][(players + 1) % 2] = Pieces(players + 1, self.colors[players], piece, 60)
                self.display[edge][counter] = self.game_board.create_image(counter * 75 + 37.5, edge * 75 + 87.5 , image = self.map[edge][counter][(players + 1) % 2].image) #The number 87.5 can also be seen as 50 + 37.5, 50 for the blank space at the top, and 37.5 to make the image at the center of the grid
                self.alive_pieces.append([counter, edge])

                self.map[edge][7 - counter][(players + 1) % 2] = Pieces(players + 1, self.colors[players], piece, 60)
                self.display[edge][7 - counter] = self.game_board.create_image((7 - counter) * 75 + 37.5, edge * 75 + 87.5, image = self.map[edge][7 - counter][(players + 1) % 2].image)
                self.alive_pieces.append([7 - counter, edge])
                counter += 1

            for piece in ["Queen", "King"]:
                self.map[edge][counter][(players + 1) % 2] = Pieces(players + 1, self.colors[players], piece, 60)
                self.display[edge][counter] = self.game_board.create_image(counter * 75 + 37.5, edge * 75 + 87.5, image = self.map[edge][counter][(players + 1) % 2].image)
                self.alive_pieces.append([counter, edge])
                counter += 1

            for pawn in range(8):
                second_row = edge + (-1) ** (players + 1)
                self.map[second_row][pawn][(players + 1) % 2] = Pieces(players + 1, self.colors[players], "Pawn", 60)
                self.display[second_row][pawn] = self.game_board.create_image(pawn * 75 + 37.5, second_row * 75 + 87.5, image = self.map[second_row][pawn][(players + 1) % 2].image)
                self.alive_pieces.append([pawn, second_row])
        
        #Display a button that shows the move history
        self.move_history = Image.open("History.png")
        self.move_history = self.move_history.resize((30, 30))
        self.move_history = ImageTk.PhotoImage(self.move_history)
        self.move_history_icon = self.game_board.create_image(575, 25, image = self.move_history)

        #Reorganize the order of data inside each array for convenience in later function
        self.alive_pieces = self.alive_pieces[:2] + self.alive_pieces[4:7] + self.alive_pieces[2:4] + [self.alive_pieces[7]] + self.alive_pieces[8:16] + self.alive_pieces[16:18] + self.alive_pieces[20:23] + self.alive_pieces[18:20] + [self.alive_pieces[23]] + self.alive_pieces[24::] #The pieces are now in the order: rook, bishop, queen, knight, king, and pawns. Colors are also sorted to be white for the first half.

        #Create a variables for piece movements
        self.turn = 0
        self.freeze = False
        self.check = [False, False]
        self.ready = False
        self.checked_moves = [[[] for i in range(8)] for j in range(8)]
        self.castle = [[True, True], [True, True]]
        self.castled_move = []
        self.en_passant = []

        #Bind the clicking function with the left key of the mouse
        self.game_board.bind("<Button-1>", self.click)

        #Create an array containing all the availible moves
        self.grey_dot = []
        self.grey_dot_display = []
        
        #Create an array containg pieces with linear movement
        self.linear_pieces_str = [[self.alive_pieces[0], self.alive_pieces[1], self.alive_pieces[4]], [self.alive_pieces[16], self.alive_pieces[17], self.alive_pieces[20]]]
        self.linear_pieces_dia = [[self.alive_pieces[2], self.alive_pieces[3], self.alive_pieces[4]], [self.alive_pieces[18], self.alive_pieces[19], self.alive_pieces[20]]]
        
        #Create arrays recording promoted pieces
        self.promoted_pawn_str = [[], []]
        self.promoted_pawn_dia = [[], []]

        #Store the position that holds data about either player's pieces
        self.current_player = 0
        self.opponent = 1

        #Create a variable to indicate end of the game
        self.restart = False

        #Erase move history recorded from the previous game, unless this function is trigger by replay
        if self.new_game:
            file = open("Chess moves.txt", "w")
            file.close()

        #Updates change on the screen
        self.game_board.pack()

#Define a class for each individual chess piece with their unique attributes
class Pieces:
    def __init__(self, play_number = 0, color = "", name = "", size = 0):
        #Reshape the previously stored images and assign them pieces of the designated name and color
        self.image = Image.open("{} {}.png".format(color, name))
        self.image = self.image.resize((size, size))
        self.image = ImageTk.PhotoImage(self.image)     #The images used for these pieces are downloaded from the following website: https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces
                                                        #These images were resized using tkinter function I learned from this tutorial: https://www.tutorialspoint.com/how-to-resize-an-image-using-tkinter

        #Assign attributes to the piece
        self.name = name
        self.color = color
        self.player = play_number

        #Store the movement pattern of each piece as an array representing horizontal and vertical directions
        if self.name == "Pawn":
            #Note the direction each piece is moving toward, as pawns can only move forward
            direction = 2 * play_number - 3
            self.move = [[0, direction], [0, 2 * direction]]
        #Similiar approach for the other pieces
        elif self.name == "Knight":
            self.move = [[1, 2], [1, -2], [-1, 2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1]]

        elif self.name == "Bishop":
            self.move = []
            for horizontal in [-1, 1]:
                for vertical in [-1, 1]:
                    self.move.append([horizontal, vertical])

            #Use selection sort the organize the directions
            for step in range(len(self.move)):
                max_value = self.move[step][0] + self.move[step][1]
                position = step

                for item in range(step + 1, len(self.move)):
                    value = (self.move[item][0] + self.move[item][1])
                    if  value > max_value:
                        max_value = value
                        position = item

                (self.move[step], self.move[position]) = (self.move [position], self.move[step])

        elif self.name == "Rook":
            self.move = [[0, 1], [0, -1], [1, 0], [-1, 0]]
            

        elif self.name == "Queen" or name == "King":
            self.move = [[-1, 0], [-1, -1], [0, -1], [1, -1], [1, 0], [1, 1], [0, 1], [-1, 1]]

#Define a class that inherits all of the attributes of the chess class to replay the game after it was done
class Replay(Chess):
    #Define an initialization function that takes in all of the past moves within this game
    def __init__(self, past_moves = 0):
        self.replay = past_moves
        self.window = Tk()
        self.new_game = False
        self.line_count = 0

        #Implement a reverse dictoinary to transfer the letters from the text file back into number coordinates
        self.letter_to_number = {"a":0, "b":1, "c":2, "d":3, "e":4, "f":5, "g":6, "h":7}

    #Define a function to play out each move recorded inside the text file
    def replay_game(self):
        #Break the self-cycling function once all of the moves made
        if self.line_count == len(self.replay):
            #Exits the game after the reanimation is done
            time.sleep(1)
            self.game_board.destroy()
            self.window.destroy()
            return
        move = self.replay[self.line_count]

        #Convert the recorded moves back to the coordinates
        before_move = [self.letter_to_number.get(move[0]), 8 - int(move[1])]
        after_move = [self.letter_to_number.get(move[2]), 8 - int(move[3])]
        self.moving_piece = (self.turn + 1) % 2

        #Take out any opponent piece on that location
        if type(self.map[after_move[1]][after_move[0]][self.moving_piece - 1]) != int:
            self.game_board.delete(self.display[after_move[1]][after_move[0]])

        #Move the game piece on the screen
        self.game_board.delete(self.display[before_move[1]][before_move[0]])
        self.display[before_move[1]][before_move[0]] = 0
        self.display[after_move[1]][after_move[0]] = self.game_board.create_image(after_move[0] * 75 + 37.5, after_move[1] * 75 + 87.5, image = self.map[before_move[1]][before_move[0]][self.moving_piece].image)
        
        #Update data within the grid representation array
        self.map[after_move[1]][after_move[0]][self.moving_piece] = self.map[before_move[1]][before_move[0]][self.moving_piece]
        self.map[after_move[1]][after_move[0]][self.moving_piece - 1] = 0
        self.map[before_move[1]][before_move[0]] = [0, 0]
        self.turn += 1
        self.line_count += 1
        self.window.after(1000, self.replay_game)

#Execute the game
execute = Chess()

#The rules of chess is found from this official site: https://www.chess.com/learn-how-to-play-ches
#User Guide Video: See within this folder