import random
pieceScore = {'K':0, 'Q':9, 'R':5, 'B':3, 'N':3, 'P':1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2


def findRandomMoves(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)]


def findBestMove(gs, validMoves):
    global nextMove,counter
    nextMove = None
    random.shuffle(validMoves)
    counter =0
    findMoveNegaMax(gs, validMoves, DEPTH, 1 if gs.whiteToMove else -1)
    print(counter)
    return nextMove


def findMoveNegaMax(gs, validMoves, depth, turnMultiplier):
    global nextMove,counter
    counter +=1
    if depth  == 0:
        return turnMultiplier * scoreBoard(gs)

    maxScore = -CHECKMATE
    for move in validMoves:
        gs.makeMove(move)
        nextMoves = gs.getValidMoves()
        score = -findMoveNegaMax(gs,nextMoves, depth - 1, -turnMultiplier )
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move

        gs.undoMove()
    return maxScore


'''
A Positive score is good for white, a negative score is good for black
'''
def scoreBoard(gs):
    if gs.checkMate:
        if gs.whiteToMove:
            return -CHECKMATE #Black wins
        else:
            return CHECKMATE #White wins
    elif gs.staleMate:
        return STALEMATE


    score = 0
    for row in gs.board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    
    return score

'''
Score the board based on material
'''

def scoreMaterial(board):
    score = 0
    for row in board:
        for square in row:
            if square[0] == 'w':
                score += pieceScore[square[1]]
            elif square[0] == 'b':
                score -= pieceScore[square[1]]
    
    return score
