import pygame as p
import ChessEngine,SmartMoveFinder

BOARD_WIDTH, BOARD_HEIGHT = 512, 512
MOVE_LOG_PANEL_WIDTH = 250
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8  # Chess board is 8x8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}

# Load images
def load_images():
    pieces = ['wR', 'wN', 'wB', 'wQ', 'wK', 'wP', 'bR', 'bN', 'bB', 'bQ', 'bK', 'bP']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))

# Initialize the game
def main():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    moveLogFont = p.font.SysFont("Arial", 14, False, False)
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable when a move is made
    animate = False#flag variable for when a move should animate
    load_images()
    running = True
    sqSelected = () #keep track of last click
    playerClicks = [] #keep track of player clicks
    gameOver = False
    playerOne = False #True if Human playing white
    playerTwo = True
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            #mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col) or col >= 8:#user clicked the same box
                        sqSelected =()#unselected
                        playerClicks = []
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected)
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                        print(move.getChessNotation())
                        for i in range (len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = ()
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    if (playerOne and not playerTwo) or (playerTwo and not playerOne):
                        gs.undoMove()
                        moveMade = True
                        animate =False
                        gameOver = False
                        gs.undoMove()
                        moveMade = True
                        animate =False
                        gameOver = False
                    else:
                        gs.undoMove()
                        moveMade = True
                        animate =False
                        gameOver = False
                if e.key == p.K_r: #reset the board when "r" is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks=[]
                    moveMade = False
                    animate = False
                    gameOver = False

        #AI move Finder
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMoves(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False


        drawGameState(screen, gs, validMoves, sqSelected, moveLogFont)
        if gs.checkMate or gs.staleMate:
            gameOver = True
            drawEndGameText(screen, (('Stalemate') if gs.staleMate else 'Black Wins by Checkmate' if gs.whiteToMove else 'White Wins by Checkmate'))
                
        clock.tick(MAX_FPS)
        p.display.flip()

def drawGameState(screen, gs, validMoves, sqSelected, moveLogFont):
    drawBoard(screen)  # Draw squares on the board
    highlightSquares(screen,gs,validMoves,sqSelected)
    kingInCheck(screen,gs)
    drawPieces(screen, gs.board)  # Draw pieces on the board
    drawMoveLog(screen, gs, moveLogFont)
    


def drawBoard(screen):
    global colors
    colors = [p.Color('white'), p.Color('#C4A484')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":  # Not an empty square
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

#Highlight square selected and moves for selected piece
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected !=():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            #Highlight square selected
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #Transperancy value -> 0 transparent; 255-> opaque
            s.fill(p.Color("blue"))
            screen.blit(s,(c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color("yellow"))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))

def kingInCheck(screen,gs):
    if gs.inCheck():
            r,c = (gs.whiteKingLocation[0],gs.whiteKingLocation[1]) if gs.whiteToMove else (gs.blackKingLocation[0],gs.blackKingLocation[1])
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color("red"))
            screen.blit(s,(c*SQ_SIZE, r*SQ_SIZE))

def drawMoveLog(screen, gs, font):
    moveLogRect = p.Rect(BOARD_WIDTH,0,MOVE_LOG_PANEL_WIDTH,MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color("white"), moveLogRect)
    moveLog = gs.moveLog
    moveTexts = []
    for i in range(0,len(moveLog),2):
        moveString = str(i//2 + 1) + '. ' + str(moveLog[i]) + " "
        if i+1 <len(moveLog):
            moveString += (str(moveLog[i+1])+"   ")
        moveTexts.append(moveString)
    
    movesPerRow = 3
    padding = 10
    textY = padding
    lineSpacing = 2
    for i in range(0,len(moveTexts), movesPerRow):
        text = ""
        for j in range(movesPerRow):
            if i+j< len(moveTexts):
                text += moveTexts[i+j]
        textObject = font.render(text, True, p.Color('Black'))  
        textLocation = moveLogRect.move(padding,textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing

def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5 #fps
    frameCount = (abs(dR)+ abs(dC))*framesPerSquare
    for frame in range(frameCount + 1):
        r,c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen,board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece on rectangle
        if move.pieceCaptured != "--":
            if move.isEnpassantMove:
                enPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == 'b' else (move.endRow -1)
                endSquare = p.Rect(move.endCol*SQ_SIZE, enPassantRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)

        #draw Moving Piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawEndGameText(screen, text):
    font = p.font.SysFont("Helvitca", 50, True, False)  
    textObject = font.render(text, 0, p.Color('Black'))  
    textLocation = p.Rect(0,0,BOARD_WIDTH,BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2,BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color("White"))
    screen.blit(textObject, textLocation.move(2,2))

if __name__ == "__main__":
    main()
