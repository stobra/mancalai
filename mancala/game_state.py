from random import randint

# +----+----+----+----+----+----+----+----+
# |    | 12 | 11 | 10 |  9 |  8 |  7 |    |
# | 13 +----+----+----+----+----+----+  6 |
# |    |  0 |  1 |  2 |  3 |  4 |  5 |    |
# +----+----+----+----+----+----+----+----+

# state is a list, offsets for different bowls
NUM_PLAYERS = 2
PLAYER_1_CAPTURES = 6
PLAYER_1_ROW = 0
PLAYER_2_CAPTURES = 13
PLAYER_2_ROW = 7
PLAYER_TURN = 14
PLAYER_1 = 0
PLAYER_2 = 1
MAX_BEADS = NUM_PLAYERS * 6


class NoMoves(Exception):
    def __init__(self, state=[]):
        Exception.__init__(self, 'No legal moves! [' + ','.join(state) + ']')
        self.state = state


class InvalidMove(Exception):
    def __init___(self, state, move):
        Exception.__init__(self, "InvalidMove: " + move +
                           ' State: ' + ','.join(state))
        self.state = state
        self.move = move


class InvalidPlayer(Exception):
    def __init__(self, player):
        Exception.__init__(self, "InvalidPlayer: " + str(player))
        self.player = player


class InvalidIndex(Exception):
    def __init__(self, index):
        Exception.__init__(self, "InvalidIndex: " + str(index))
        self.index = index


class GameNotOver(Exception):
    def __init__(self):
        Exception.__init__(self, "Game not over!")


def init():
    """
    Creates the game data structure for initial state of the game.

    >>> init()
    [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0, 0]
    """
    newstate = [4, 4, 4, 4, 4, 4, 0,
                4, 4, 4, 4, 4, 4, 0,
                PLAYER_1]
    return newstate


def randomState():
    """
    Creates a random legal game state.
    >>> rs = randomState()
    """
    stones = 48
    state = ([0] * 15)[:]
    bowl = 0
    while stones > 0:
        handful = randint(0, 4)
        state[bowl] += handful
        stones -= handful
        bowl = (bowl + 1) % 14
    return state


def validateIndex(index):
    """
    Is this index on the board at all?
    >>> validateIndex(4)
    4
    >>> validateIndex(-1)
    Traceback (most recent call last):
        ...
    game_state.InvalidIndex: InvalidIndex: -1
    >>> validateIndex(14)
    Traceback (most recent call last):
        ...
    game_state.InvalidIndex: InvalidIndex: 14
    >>> validateIndex(None)
    Traceback (most recent call last):
        ...
    game_state.InvalidIndex: InvalidIndex: None
    """
    if index is None:
        raise InvalidIndex(None)
    if index >= 0 and index < NUM_PLAYERS * 7:
        return index
    else:
        raise InvalidIndex(index)


def validatePlayer(player):
    """
    Ensure player is a valid index.
    >>> validatePlayer(1)
    1
    >>> validatePlayer(2)
    Traceback (most recent call last):
        ...
    game_state.InvalidPlayer: InvalidPlayer: 2
    """
    if player >= 0 and player < NUM_PLAYERS:
        return player
    else:
        raise InvalidPlayer(player)


def getPlayerRowOffset(player):
    """
    Returns the index into the game array for the first of the player's bowls.

    >>> getPlayerRowOffset(0)
    0
    >>> getPlayerRowOffset(1)
    7
    >>> getPlayerRowOffset(2)
    Traceback (most recent call last):
        ...
    game_state.InvalidPlayer: InvalidPlayer: 2
    """
    if player < 0 or player >= NUM_PLAYERS:
        raise InvalidPlayer(player)
    offset = player * 7
    return offset


def getRow(state, player):
    """
    Returns the row for the player as an array of his bowls.

    >>> getRow([1, 2, 3, 4, 5, 6, 0, \
                12, 11, 10, 9, 8, 7, 0, \
                PLAYER_1], PLAYER_1)
    [1, 2, 3, 4, 5, 6]
    """
    offset = getPlayerRowOffset(player)
    return state[offset:offset + 6]


def getMaxBowls():
    """
    Returns the number of bowls in the board.
    >>> getMaxBowls()
    14
    """
    return NUM_PLAYERS * 7


def getOppositeBowl(index):
    """
    Returns the index of the bowl opposite the bowl with the given index.
    >>> getOppositeBowl(3)
    9
    >>> getOppositeBowl(11)
    1
    >>> getOppositeBowl(0)
    12
    >>> getOppositeBowl(14)
    Traceback (most recent call last):
        ...
    game_state.InvalidIndex: InvalidIndex: 14
    """
    # bowl index and opposite add up to 12
    validateIndex(index)
    opposite = (PLAYER_2_CAPTURES - 1 - index)
    return opposite


def getBowlOwner(index):
    """
    Return ID of player who owns this bowl.
    >>> getBowlOwner(4)
    0
    >>> getBowlOwner(12)
    1
    >>> getBowlOwner(14)
    Traceback (most recent call last):
        ...
    game_state.InvalidIndex: InvalidIndex: 14
    """
    return int(validateIndex(index) / 7)


def getBowlCount(state, index):
    """
    Get the number of stones in any bowl on the board.

    >>> getBowlCount([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 0], 7)
    12
    >>> getBowlCount([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 0], 14)
    Traceback (most recent call last):
        ...
    game_state.InvalidIndex: InvalidIndex: 14
    """
    return state[validateIndex(index)]


def getCurrentPlayer(state):
    """
    Get the ID of the player whose turn it is to move.

    >>> getCurrentPlayer([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 1])
    1
    >>> getCurrentPlayer([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 2])
    Traceback (most recent call last):
        ...
    game_state.InvalidPlayer: InvalidPlayer: 2
    """
    return validatePlayer(state[PLAYER_TURN])


def getLegalMoves(state):
    """
    Get list of indexes for legal moves for current player.

    >>> getLegalMoves([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 1])
    [7, 8, 9, 10, 11, 12]

    >>> getLegalMoves([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 0])
    [0, 1, 2, 3, 4, 5]
    """
    player = getCurrentPlayer(state)
    moves = []
    offset = getPlayerRowOffset(player)
    for index in range(offset, offset + 6):
        if getBowlCount(state, index) > 0:
            moves.append(index)
    return moves


def isLegalMove(state, move):
    """
    Determine if move is legal for given game state.

    If trying to move stones for wrong player:
    >>> isLegalMove([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 1], 2)
    False

    Legal move:
    >>> isLegalMove([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 0], 2)
    True
    """
    validateIndex(move)
    if getBowlOwner(move) != getCurrentPlayer(state):
        return False
    elif 0 == getBowlCount(state, move):
        return False
    else:
        return True


def validateMove(state, move):
    """
    Ensure move is valid for state. Raise exception if not. If valid, return a
    copy of state and move.

    >>> validateMove([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 1], 2)
    Traceback (most recent call last):
        ...
    game_state.InvalidMove: ([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, ..., 1], 2)

    >>> validateMove([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 1], 8)
    ([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 1], 8)
    """
    player = getCurrentPlayer(state)
    index = validateIndex(move)
    if getBowlOwner(move) != player:
        raise InvalidMove(state, index)
    if 0 == getBowlCount(state, move):
        raise InvalidMove(state, index)
    return state[:], move


def isGameOver(state):
    """
    Return true if game is ended, else false to keep playing. Game ends when
    either player has an empty row.

    >>> isGameOver([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 1])
    False

    >>> isGameOver([0, 0, 0, 0, 0, 0, 9, 12, 11, 10, 9, 8, 7, 0, 1])
    True

    >>> isGameOver([12, 11, 10, 9, 8, 7, 0, 0, 0, 0, 0, 0, 0, 9, 1])
    True
    """
    for player in range(NUM_PLAYERS):
        row = getRow(state, player)
        # true if any bowl for this player has nonzero count in it.
        # both players have to have stones to move for the game to continue.
        try:
            if next(True for bowl in row if bowl > 0):
                # this player has a stone to move, check next player
                continue
        except StopIteration:
            # this player has no stones to move, game over
            return True
    # both players have at least one stone, still playing
    return False


def isMancala(index):
    """
    Test if the bowl at the given index is the mancala bowl. This is where a
    player tries to gather the stones for scoring.

    >>> isMancala(6)
    True
    >>> isMancala(13)
    True
    >>> isMancala(10)
    False
    >>> isMancala(14)
    Traceback (most recent call last):
        ...
    game_state.InvalidIndex: InvalidIndex: 14
    """
    m = (validateIndex(index) % 7 == 6)
    return m


def getMancalaIndex(player):
    """
    Get the index of the given player's mancala.

    >>> getMancalaIndex(0)
    6
    >>> getMancalaIndex(1)
    13
    >>> getMancalaIndex(2)
    Traceback (most recent call last):
        ...
    game_state.InvalidPlayer: InvalidPlayer: 2
    """
    return ((validatePlayer(player) * 7) + 6)


def scoreGame(state):
    """
    Move remaining stones to the appropriate Mancala for the endgame scoring.

    >>> scoreGame([0, 0, 0, 0, 0, 0, 9, 12, 11, 10, 9, 8, 7, 0, 1])
    [0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 57, 1]

    >>> scoreGame([0, 0, 1, 0, 0, 0, 9, 12, 11, 10, 9, 8, 7, 0, 1])
    [0, 0, 1, 0, 0, 0, 9, 12, 11, 10, 9, 8, 7, 0, 1]

    """
    if not isGameOver(state):
        return state
    newstate = ([0] * 15)[:]
    newstate[PLAYER_TURN] = state[PLAYER_TURN]
    for player in range(NUM_PLAYERS):
        mindex = getMancalaIndex(player)
        score = getBowlCount(state, mindex)
        row = getRow(state, player)
        score = sum(row, score)
        newstate[mindex] = score
    return newstate


def getScore(state):
    """
    Calculate score for both players.

    >>> getScore([0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 43, 1])
    (5, 43)
    """
    return (state[PLAYER_1_CAPTURES], state[PLAYER_2_CAPTURES])


def getWinner(gamestate):
    """
    Returns the index of the winner of the game.

    >>> getWinner([0, 0, 0, 0, 0, 0, 8, 0, 0, 0, 0, 0, 0, 9, 1])
    1

    >>> getWinner([0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 8, 1])
    0

    >>> getWinner([0, 0, 0, 0, 0, 0, 9, 0, 0, 0, 0, 0, 0, 9, 1])
    -1
    """
    if not isGameOver(gamestate):
        raise GameNotOver()
    winner = -1
    score = -1
    for player in range(NUM_PLAYERS):
        c = getBowlCount(gamestate, getMancalaIndex(player))
        if c > score:
            score = c
            winner = player
        elif c == score:
            winner = -1

    return winner


def nextPlayer(player):
    """
    Return the next player after the given player.

    >>> nextPlayer(1)
    0
    >>> nextPlayer(0)
    1
    """
    return ((validatePlayer(player) + 1) % NUM_PLAYERS)


def getOpponentMancalas(player):
    """
    Get a list of indexes which are opponent Mancalas.

    >>> getOpponentMancalas(1)
    [6]
    >>> getOpponentMancalas(0)
    [13]
    """
    nxt = nextPlayer(player)
    indexes = []
    while nxt != player:
        indexes.append(getMancalaIndex(nxt))
        nxt = nextPlayer(nxt)
    return indexes


def translateMove(state, n):
    """
    This turns a selected move in the range [0,6] into a board index.

    >>> translateMove([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 0], 4)
    4
    >>> translateMove([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 1], 4)
    8
    """
    isPlayer1 = (PLAYER_1 == getCurrentPlayer(state))
    nprime = n if isPlayer1 else PLAYER_2_CAPTURES - 1 - n
    return nprime


def doMove(state, move):
    """
    This applies a move and returns the new game state.

    Standard move
    >>> doMove([1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 0], 4)
    [1, 2, 3, 4, 0, 7, 1, 13, 12, 11, 9, 8, 7, 0, 1]

    Move capturing opposite side pieces
    >>> doMove([1, 0, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 0], 0)
    [0, 0, 3, 4, 5, 6, 9, 12, 11, 10, 9, 0, 7, 0, 1]

    Move not capturing opposite side pieces, but landing in empty space
    https://boardgamegeek.com/article/3058108#3058108
    >>> doMove([1, 0, 3, 4, 5, 6, 0, 12, 11, 10, 9, 0, 7, 0, 0], 0)
    [0, 1, 3, 4, 5, 6, 0, 12, 11, 10, 9, 0, 7, 0, 1]

    move resulting in free move
    >>> doMove([1, 2, 4, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 0], 2)
    [1, 2, 0, 5, 6, 7, 1, 12, 11, 10, 9, 8, 7, 0, 0]
    """
    newstate, move = validateMove(state, move)
    player = getCurrentPlayer(newstate)
    stones = newstate[move]
    newstate[move] = 0
    skip = getOpponentMancalas(player)
    freeTurn = False
    wasEmpty = False
    nextBowl = move
    for i in range(stones):
        nextBowl = (nextBowl + 1) % getMaxBowls()
        freeTurn = False
        wasEmpty = False
        if nextBowl in skip:
            continue
        if getBowlOwner(nextBowl) == player:
            if isMancala(nextBowl):
                freeTurn = True
            else:
                if 0 == getBowlCount(newstate, nextBowl):
                    wasEmpty = True
        newstate[nextBowl] += 1  # drop a stone
    if wasEmpty:
        opposite = getOppositeBowl(nextBowl)
        if newstate[opposite] > 0:
            # capture moving piece and opposite bowl count
            captured = newstate[opposite] + 1
            newstate[opposite] = 0  # captured opposite
            newstate[nextBowl] = 0  # captured moving piece
            newstate[getMancalaIndex(player)] += captured
    if not freeTurn:
        newstate[PLAYER_TURN] = nextPlayer(player)
    return scoreGame(newstate)


def flipBoard(state):
    """
    Flips the board one player to the right.

    >>> flipBoard([1, 2, 4, 4, 5, 6, 0, 7, 8, 9, 10, 11, 12, 0, 0])
    [7, 8, 9, 10, 11, 12, 0, 1, 2, 4, 4, 5, 6, 0, 1]

    >>> flipBoard([1, 2, 4, 4, 5, 6, 0, 7, 8, 9, 10, 11, 12, 0, 1])
    [7, 8, 9, 10, 11, 12, 0, 1, 2, 4, 4, 5, 6, 0, 0]
    """
    newstate = state[:]
    boardsize = NUM_PLAYERS * 7
    for i in range(boardsize):
        index = (i + 7) % boardsize
        newstate[index] = state[i]
    newstate[boardsize] = state[boardsize]
    newstate[PLAYER_TURN] = (newstate[PLAYER_TURN] + 1) % NUM_PLAYERS
    return newstate


def flipBoardCurrentPlayer(state):
    """
    Flips the board to make the current player think they are player one.
    This can be used for training AI players so they learn board states
    from the same perspective.

    >>> state = [1, 2, 4, 4, 5, 6, 0, 7, 8, 9, 10, 11, 12, 0, 1]
    >>> flipBoardCurrentPlayer(state)
    [7, 8, 9, 10, 11, 12, 0, 1, 2, 4, 4, 5, 6, 0, 0]

    >>> state = [1, 2, 4, 4, 5, 6, 0, 7, 8, 9, 10, 11, 12, 0, 0]
    >>> flipBoardCurrentPlayer(state)
    [1, 2, 4, 4, 5, 6, 0, 7, 8, 9, 10, 11, 12, 0, 0]
    """
    return state if getCurrentPlayer(state) == PLAYER_1 else flipBoard(state)


def flipMove(move, player):
    """
    Converts move as if it was always made by player 1.

    >>> flipMove(9, 1)
    2

    >>> flipMove(1, 0)
    1

    >>> flipMove(3, None)
    Traceback (most recent call last):
        ...
    game_state.InvalidPlayer: InvalidPlayer: None

    >>> flipMove(None, 0) == None
    True
    """
    if move is None:
        return None
    if player is None:
        raise InvalidPlayer(player)
    boardsize = NUM_PLAYERS * 7
    return ((move + (player * 7)) % boardsize)
