import pygame as p
import pygame
import ChessEngine, SmartMoveFinder

p.display.set_caption('Comp Sci Chess')
width = height = 512
dimension = 8 #8x8 board
s_size = height // dimension
max_fps = 15
images = {}

# 0 = Chess, 1 is checkers
CheckersCheck = input("Do you want to play checkers or Chess (Y for chess, N for checkers): ")

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("Chess&Checkers/" + piece + ".png"), (s_size,s_size))

if CheckersCheck == "Y":
    def main():
        p.init()
        screen = p.display.set_mode((width,height))
        clock = p.time.Clock()
        screen.fill(p.Color("white"))
        gs = ChessEngine.GameState()
        validMoves = gs.getValidMoves()
        moveMade = False #flag variable for when a move is made
        animate = False #flag variable for aniamted moves
        loadImages()
        running = True
        s_selected = () #no square selected, keeps track of the last click of the user (stored as a tuple (row,column))
        p_clicks = [] #keeps track of player clicks (contains two tuples,where it was and where it is moving to)
        gameOver = False
        playerOne = True #if human is playing white, then this will be true. if AI is playing, then false
        playerTwo = False #same as above but for black
        while running:
                humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
                for e in p.event.get():
                    if e.type == p.QUIT:
                        running = False
                    #mouse handler
                    elif e.type == p.MOUSEBUTTONDOWN:
                        if not gameOver and humanTurn:
                            location = p.mouse.get_pos() #x and y position of mouse
                            col = location[0]//s_size
                            row = location[1]//s_size
                            if s_selected == (row, col): #the user clicks the same square
                                s_selected = () #unselect
                                p_clicks = [] #clears player clicks
                        
                            else:
                                s_selected = (row, col)
                                p_clicks.append(s_selected) #append for both 1st and 2nd clicks
                            if len(p_clicks) == 2: #after 2nd click
                                move = ChessEngine.Move(p_clicks[0], p_clicks[1], gs.board)
                                print(move.getChessNotation())
                                for i in range(len(validMoves)):
                                    if move == validMoves[i]:
                                        gs.makeMove(validMoves[i])
                                        moveMade = True
                                        animate = True
                                        s_selected = () #reset user clicks
                                        p_clicks = [] #resets player clicks
                                if not moveMade:
                                    p_clicks = [s_selected]
                    #key handlers
                    elif e.type == p.KEYDOWN:
                        if e.key == p.K_z: #undo the move if 'z' is pressed
                            gs.undoMove()
                            moveMade = True
                            animate = False
                        if e.key == p.K_x: #reset game if r button is clicked
                            gs = ChessEngine.GameState()
                            validMoves = gs.getValidMoves()
                            s_selected = ()
                            p_clicks = []
                            moveMade = False
                            animate = False
                            gameOver = False

                #AI move finder logic
                if not gameOver and not humanTurn:
                    AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
                    if AIMove is None:
                        AIMove = SmartMoveFinder.findRandomMove(validMoves)
                    gs.makeMove(AIMove)
                    moveMade = True
                    animate = True
                            

                if moveMade:
                    if animate:
                        animatedMove(gs.moveLog[-1], screen, gs.board, clock)
                    validMoves = gs.getValidMoves()
                    moveMade = False
                    animate = False

                drawGameState(screen, gs, validMoves, s_selected)

                if gs.checkMate:
                    gameOver = True
                    if gs.whiteToMove:
                        drawText(screen, 'Black wins by checkmate')
                        print("")
                    else:
                        drawText(screen, 'White wins by checkmate')
                elif gs.staleMate:
                    gameOver = True
                    drawText(screen, 'Stalemate')

                clock.tick(max_fps)
                p.display.flip()

    #highlight the square selected and possible moves for selected pieces
    def highlightSquares(screen, gs, validMoves, s_selected):
        if s_selected != ():
            r, c = s_selected
            if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'): #square selected is a piece that can be moved
                #highlight selected square
                s = p.Surface((s_size,s_size))
                s.set_alpha(100)#transparancy value
                s.fill(p.Color('blue'))
                screen.blit(s, (c*s_size, r*s_size))
                #highlight moves from that square
                s.fill(p.Color('yellow'))
                for move in validMoves:
                    if move.startRow == r and move.startCol == c:
                        screen.blit(s, (move.endCol*s_size, move.endRow*s_size))



    def drawGameState(screen, gs, validMoves, s_selected):
        drawBoard(screen) #draw squares on the board
        highlightSquares(screen, gs, validMoves, s_selected)
        drawPieces(screen, gs.board) #draw pieces on the board


    def drawBoard(screen):
        global colours
        colours = [p.Color("gray"), p.Color("red")]
        for r in range(dimension):
            for c in range (dimension):
                color = colours[((r+c) % 2)]
                p.draw.rect(screen, color, p.Rect(c*s_size, r*s_size, s_size, s_size))

    def drawPieces(screen, board):
        for r in range (dimension):
            for c in range (dimension):
                piece = board[r][c]
                if piece != "--": #if not an empty square
                    screen.blit(images[piece], p.Rect(c*s_size, r*s_size, s_size,s_size))

    #Animating moves
    def animatedMove(move, screen, board, clock):
        global colours
        dR = move.endRow - move.startRow
        dC = move.endCol - move.startCol
        framesPerSquare = 10 #frames moved one square
        frameCount = (abs(dR) + abs(dC)) * framesPerSquare
        for frame in range(frameCount + 1):
            r, c = ((move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount))
            drawBoard(screen)
            drawPieces(screen, board)
            #erase piece moved from it's ending square
            colour = colours[(move.endRow + move.endCol) % 2]
            endSquare = p.Rect(move.endCol*s_size, move.endRow*s_size, s_size, s_size)
            p.draw.rect(screen, colour, endSquare)
            #draw the captured piece back onto the rectangle
            if move.pieceCaptured != '--':
                screen.blit(images[move.pieceCaptured], endSquare)
            #draw moving piece
            screen.blit(images[move.pieceMoved], p.Rect(c*s_size, r*s_size, s_size, s_size))
            p.display.flip()
            clock.tick(60)


    def drawText(screen, text):
        font = p.font.SysFont("Helvitca", 32, True, False)
        textObject = font.render(text, 0, p.Color('Black'))
        textLocation = p.Rect(0, 0, width, height).move(width/2 - textObject.get_width()/2, height/2 - textObject.get_height()/2)
        screen.blit(textObject, textLocation)
        textObject = font.render(text, 0, p.Color("white"))
        screen.blit(textObject, textLocation.move(2,2))


    if __name__ == "__main__":
        main()

# Crown for Kings
CROWN = pygame.transform.scale(pygame.image.load('Chess&Checkers/crown.png'), (44, 25))

# Width and height of window
WIDTH = 800
HEIGHT = 800

# Numbers of rows and columns
ROWS = 8
COLS = 8

# Calculating size of squares
SQUARE_SIZE = WIDTH // COLS

# Colors
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREY = (128, 128, 128)

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

if CheckersCheck == "N":

    class Piece:
        # Padding is distance between circle and square borders
        PADDING = 10
        OUTLINE = 2

        def __init__(self, row, col, color):
            self.row = row
            self.col = col
            self.color = color
            self.king = False
            # Reds go up, whites go down
            # In pygame coords, negative and positive are switched
            if self.color == RED:
                self.direction = -1
            else:
                self.direction = 1

            self.x = 0
            self.y = 0
            self.calc_pos()

        def calc_pos(self):
            # We need to be exactly in the middle of the square
            # Since circles are drawn from their centre
            # So our x position will be the size of the square times our column number
            # Then add another square size to get to the end of the column
            # And divide by two to find the centre x coord
            self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
            # Same thing for y coords but with rows instead
            self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

        def make_king(self):
            self.king = True

        def draw(self, win):
            # Radius is the square size divided by two,
            # Minus how much we want the circle to be from the borders of the square
            radius = SQUARE_SIZE // 2 - self.PADDING
            # Radius plus outline creates a large circle, but...
            pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
            # We cover the outline with a slightly smaller circle, the actual piece
            # so the outline is just the sliver outside the piece
            pygame.draw.circle(win, self.color, (self.x, self.y), radius)
            # Centres crown in the middle
            if self.king:
                win.blit(CROWN, (self.x - CROWN.get_width()//2,self.y - CROWN.get_height()//2))

        def move(self,row,col):
            self.row = row
            self.col = col
            # Recalculate coords after movement
            self.calc_pos()

    class Board:
        def __init__(self):
            self.board = []
            # At start, 12 red and white
            self.red_left = 12
            self.white_left = 12
            # No kings at start
            self.red_kings = 0
            self.white_kings = 0
            self.create_board()

        def draw_squares(self, win):
            # Fill the background with black
            win.fill(BLACK)
            for row in range(ROWS):
                # Reds alternate between column zero or one
                # Mod ensures this alternation by row
                # 2 step ensures alternation in column
                # Skipping the black squares each time
                for col in range(row % 2, COLS, 2):
                    pygame.draw.rect(
                        win, RED, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
                    )

        def move(self, piece, row, col):
            # Piece in moving positiong and place we want to move will swap positions
            self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
            piece.move(row,col)

            # At max row and lowest row, make into king
            # This only happens on movement, so pieces starting at the kinging positions wont turn into kings automatically
            if row == ROWS - 1 or row == 0:
                piece.make_king()
                if piece.color == WHITE:
                    self.white_kings += 1
                else:
                    self.red_kings += 1

        # Gives piece from intersection of row and column 
        def get_piece(self, row, col):
            return self.board[row][col]

        def create_board(self):
            for row in range(ROWS):
                # List represents what each row will have inside of it
                # so for every row this is appended
                self.board.append([])
                for col in range(COLS):
                    # Pieces first drawn second on even columns and
                    # First on odd columns
                    # Rows continue skipping from that square, so that's what we calculate
                    if col % 2 == (row + 1) % 2:
                        # First three rows are white
                        if row < 3:
                            piece = Piece(row, col, WHITE)
                            self.board[row].append(piece)
                        # Over four are red
                        elif row > 4:
                            piece = Piece(row, col, RED)
                            self.board[row].append(piece)
                        # Else (really just rows 3 and 4) are nothing
                        else:
                            self.board[row].append(0)
                    # Squares that are skipped by the formula above have no pieces as well
                    else:
                        self.board[row].append(0)

        def draw(self, win):
            self.draw_squares(win)
            for row in range(ROWS):
                for col in range(COLS):
                    piece = self.board[row][col]
                    # Pieces without the appended zero are drawn
                    if piece != 0:
                        piece.draw(win)

        
        def remove(self, pieces):
            # Removes specified pieces from the board
            for piece in pieces:
                # Set the board position to 0, indicating no piece is present there
                self.board[piece.row][piece.col] = 0
                if piece != 0:  # Ensure the piece is not already empty
                    if piece.color == RED:
                        # Decrease the count of red pieces
                        self.red_left -= 1
                    else:
                        # Decrease the count of white pieces
                        self.white_left -= 1

        def get_valid_moves(self, piece):
            # Computes all valid moves for a given piec
            # Dictionary to store possible moves and any skipped piecese
            moves = {}
            # Column to left and right of piece
            left = piece.col - 1  
            right = piece.col + 1 
            # Piece's row
            row = piece.row  

            # If the piece is red or a king, check upward moves
            if piece.color == RED or piece.king:
                moves.update(
                    self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left)
                )
                moves.update(
                    self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right)
                )
            # If the piece is white or a king, check downward moves
            if piece.color == WHITE or piece.king:
                moves.update(
                    self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left)
                )
                moves.update(
                    self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right)
                )

            # Return the dictionary of valid moves
            return moves  

        def _traverse_left(self, start, stop, step, color, left, skipped=[]):
            # Dictionary to store moves and skipped pieces
            moves = {}  
            # Tracks the last opponent piece seen for jumps
            last = [] 

            for r in range(start, stop, step):
                # Stop if the column index goes out of bounds
                if left < 0:  
                    break
                
                # Get the piece at the current position
                current = self.board[r][left]  

                # The spot is empty
                if current == 0:  
                    if skipped and not last:
                        # If there are skipped pieces but no valid jump, stop
                        break
                    elif skipped:
                        # If there are skipped pieces, add them to the move
                        moves[(r, left)] = last + skipped
                    else:
                        # No skipped pieces, simply add the move
                        moves[(r, left)] = last

                    # Check for further jumps
                    if last:  
                        if step == -1:
                            # Limit the range upwards
                            row = max(r - 3, 0)  
                        else:
                            # Limit the range downwards
                            row = min(r + 3, ROWS)  
                        moves.update(
                            self._traverse_left(r + step, row, step, color, left - 1, skipped=last)
                        )
                        moves.update(
                            self._traverse_right(r + step, row, step, color, left + 1, skipped=last)
                        )
                    break
                # Stop if we hit our own piece
                elif current.color == color:  
                    break
                else:
                    # Track the opponent piece for a potential jump
                    last = [current]
                # Move further left
                left -= 1  
            
            return moves

        # Notes apply parallel to right tranverse
        def _traverse_right(self, start, stop, step, color, right, skipped=[]):
            moves = {}  
            last = []  

            for r in range(start, stop, step):
                if right >= COLS:  
                    break

                current = self.board[r][right] 

                if current == 0: 
                    if skipped and not last:
                        break
                    elif skipped:
                        moves[(r, right)] = last + skipped
                    else:
                        moves[(r, right)] = last

                    if last: 
                        if step == -1:
                            row = max(r - 3, 0)  
                        else:
                            row = min(r + 3, ROWS)  
                        moves.update(
                            self._traverse_left(r + step, row, step, color, right - 1, skipped=last)
                        )
                        moves.update(
                            self._traverse_right(r + step, row, step, color, right + 1, skipped=last)
                        )
                    break
                elif current.color == color:  
                    break
                else:
                    last = [current]

                right += 1  
            
            return moves

    class Game:
        def __init__(self, win):
            self._init()
            self.win = win
        
        def update(self):
            self.board.draw(self.win)
            self.draw_valid_moves(self.valid_moves)
            pygame.display.update()

        def _init(self):
            self.selected = None
            self.board = Board()
            self.turn = RED
            # Gives dictionary for current valid moves
            self.valid_moves = {}

        # Resets the game
        def reset(self):
            self._init()

        def select(self, row, col):
            # if something is already selected, check if we can move it to the newly selected location
            if self.selected:
                result = self._move(row, col)
                # if move invalid, selection is reset
                if not result:
                    self.selected = None
                    self.select(row, col)
            

            piece = self.board.get_piece(row, col)
            # if we selecting a piece, and the color of the piece corresponds whose turn it is (clicking black piece on black's turn
            # piece becomes selected 
            if piece != 0 and piece.color == self.turn:
                self.selected = piece
                self.valid_moves = self.board.get_valid_moves(piece)
                return True
            # Otherwise, false
            return False

        def _move(self, row, col):
            piece = self.board.get_piece(row, col)
            # If something is selected and the next selection is not another piece, and it is in the dictionary of valid moves
            # We can move to the selection
            if self.selected and piece == 0 and (row, col) in self.valid_moves:
                self.board.move(self.selected, row, col)
                skipped = self.valid_moves[(row, col)]
                if skipped:
                    self.board.remove(skipped)
                self.change_turn()
            # If not, false
            else:
                return False

            return True

        # Draws valid moves
        def draw_valid_moves(self, moves):
            for move in moves:
                row, col = move
                pygame.draw.circle(self.win, BLUE, (col * SQUARE_SIZE + SQUARE_SIZE//2, row * SQUARE_SIZE + SQUARE_SIZE//2), 15)

        # Changes turn
        def change_turn(self):
            self.valid_moves = {}
            if self.turn == RED:
                self.turn = WHITE
            else:
                self.turn = RED

    def get_row_col_from_mouse(pos):
        x, y = pos
        # Gets row and column number by dividing coords by square sizes
        row = y // SQUARE_SIZE
        col = x // SQUARE_SIZE
        return row, col

    def checkers():
        game = Game(WIN)
        run = True

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                # get position of mouse and move piece upon press 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    row, col = get_row_col_from_mouse(pos)
                    game.select(row, col)

            # Draw the board and update display
            game.update()

        pygame.quit()


    checkers()

    # Valid move algorithm and crown asset from https://www.youtube.com/watch?v=_kOXGzkbnps&list=PLzMcBGfZo4-lkJr3sqpikNyVzbNZLRiT3&index=3

# https://www.youtube.com/@eddiesharick6649