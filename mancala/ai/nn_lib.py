import game_state as s
import tensorflow as tf
import json
from timeit import default_timer as timer

INPUT_SIZE = (s.NUM_PLAYERS * 7)
OUTPUT_SIZE = 6

HIDDEN_LAYER_SIZE = 128
LEARNING_RATE = 0.05
BATCH_SIZE = 5000
SAVE_PATH = "./data/"
BETTER_MOVE = 0.5
WINNING_MOVE = 1
LOSING_MOVE = 0

# example code
# https://github.com/shoreason/tensormnist/blob/master/examples/run_mnist_1.py


def trainingStream(f):
    for jsonline in f:
        yield json.loads(jsonline)


def losingVector(m):
    """
    Return vector of moves with losing move score set low, and others higher.
    >>> losingVector(3) == [BETTER_MOVE, BETTER_MOVE, BETTER_MOVE, \
                            LOSING_MOVE, BETTER_MOVE, BETTER_MOVE]
    True
    >>> losingVector(1) == [BETTER_MOVE, LOSING_MOVE, BETTER_MOVE, \
                            BETTER_MOVE, BETTER_MOVE, BETTER_MOVE]
    True
    """
    z = [BETTER_MOVE] * 6
    return z[:m] + [LOSING_MOVE] + z[m + 1:]


def winningVector(m):
    """
    Return vector of moves with winning move score set high, and others low.
    >>> winningVector(3) == [LOSING_MOVE, LOSING_MOVE, LOSING_MOVE, \
                            WINNING_MOVE, LOSING_MOVE, LOSING_MOVE]
    True
    >>> winningVector(1) == [LOSING_MOVE, WINNING_MOVE, LOSING_MOVE, \
                            LOSING_MOVE, LOSING_MOVE, LOSING_MOVE]
    True
    """
    z = [LOSING_MOVE] * 6
    return z[:m] + [WINNING_MOVE] + z[m + 1:]


def legalVector(state, vector):
    """
    >>> state = [1, 2, 3, 0, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 0]
    >>> expected = [WINNING_MOVE, WINNING_MOVE, WINNING_MOVE, \
            LOSING_MOVE, WINNING_MOVE, WINNING_MOVE]
    >>> legalVector(state, [WINNING_MOVE]*6) == expected
    True
    """
    return [vector[m] if s.isLegalMove(
        state, m) else LOSING_MOVE for m in range(6)]


def moveToVector(state, m, iswinner):
    """
    Create a vector of scores for winning moves and losing moves. Treat any
    illegal move as a losing move.

    >>> state = [1, 2, 3, 4, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 0]
    >>> moveToVector(state, 0, 1) == [WINNING_MOVE, LOSING_MOVE, LOSING_MOVE, \
                            LOSING_MOVE, LOSING_MOVE, LOSING_MOVE]
    True
    >>> state = [1, 2, 3, 0, 5, 6, 0, 12, 11, 10, 9, 8, 7, 0, 0]
    >>> moveToVector(state, 2, 0) == [BETTER_MOVE, BETTER_MOVE, LOSING_MOVE, \
                            LOSING_MOVE, BETTER_MOVE, BETTER_MOVE]
    True
    """
    vector = winningVector(m) if iswinner else losingVector(m)
    return legalVector(state, vector)


class NetworkBase():

    def __init__(self, name):
        self.name = name
        self.learn_rate = LEARNING_RATE
        self.batch_size = BATCH_SIZE
        self.save_path = SAVE_PATH + self.name + '.ckpt'
        self.hiddenSizes = []
        self.hiddenParams = []
        self.dropout_prob = 0.1

    def variable(self, shape, name):
        initial = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(initial, name=name)

    def initPlaceholders(self):
        # placeholders for inputs and outputs
        self.x = tf.placeholder(tf.float32, shape=[None, INPUT_SIZE], name="x")
        self.y_ = tf.placeholder(
            tf.float32, shape=[
                None, OUTPUT_SIZE], name="y_")
        self.keep_prob = tf.placeholder(tf.float32, name="keep_prob")

    def _lastLayer(self):
        if self.hiddenSizes:
            layernum = len(self.hiddenSizes) + 1
            lastSize = self.hiddenSizes[-1]
            lastLayer = self.hiddenParams[-1][-1]
        else:
            layernum = 1
            lastSize = INPUT_SIZE
            lastLayer = self.x
        return (layernum, lastSize, lastLayer)

    def addHiddenLayer(self, layer_size):
        (layernum, lastSize, lastLayer) = self._lastLayer()
        W = self.variable([lastSize, layer_size], "W" + str(layernum))
        b = self.variable([layer_size], "b" + str(layernum))
        # layer fulfills equation: h = a(Wx + b)
        # a is activation function (relu)
        # x is prior layer output
        # W is weight
        # b is bias
        h = tf.nn.relu(tf.matmul(lastLayer, W) + b, name="h" + str(layernum))
        d = tf.nn.dropout(h, self.keep_prob)
        self.hiddenSizes.append(layer_size)
        self.hiddenParams.append((W, b, h, d))

    def initOutputLayer(self):
        (layernum, lastSize, lastLayer) = self._lastLayer()
        self.W_out = self.variable([lastSize, OUTPUT_SIZE], "W_out")
        self.b_out = self.variable([OUTPUT_SIZE], "b_out")
        self.y = tf.nn.softmax(tf.matmul(lastLayer, self.W_out) +
                               self.b_out, name="y")

    def initCostFn(self):
        # Cost
        self.cross_entropy = tf.reduce_mean(
            -tf.reduce_sum(self.y_ * tf.log(self.y),
                           reduction_indices=[1]),
            name="cross_entropy")

        # Accuracy
        self.correct_prediction = tf.equal(tf.argmax(self.y, 1),
                                           tf.argmax(self.y_, 1))
        self.accuracy = tf.reduce_mean(
            tf.cast(self.correct_prediction, tf.float32),
            name="accuracy")

        # Train step
        self.train_step = tf.train.GradientDescentOptimizer(
            LEARNING_RATE).minimize(self.cross_entropy)

    def initSession(self):
        # use a saver to save/restore with a file
        self.saver = tf.train.Saver()

        # don't need an interactive session here
        # https://stackoverflow.com/q/41791469/5114
        self.sess = tf.Session()
        try:
            # load trained network from file if it exists
            if tf.train.checkpoint_exists(
                    tf.train.latest_checkpoint(self.save_path)):
                self.saver.restore(self.sess, self.save_path)
                loaded = True
        except Exception:
            # could not load
            loaded = False
        if not loaded:
            # start from scratch
            self.sess.run(tf.global_variables_initializer())

    def train_batch(self, batch):
        start = timer()
        dfx = [s[:14] for s, m, w in batch]
        dfy_ = [moveToVector(s, m, w) for s, m, w in batch]
        fd = {
            self.x: dfx,
            self.y_: dfy_,
            self.keep_prob: 1 - self.dropout_prob
        }
        self.train_step.run(
            session=self.sess, feed_dict=fd)
        self.saver.save(self.sess, SAVE_PATH)
        end = timer()
        count = len(batch)
        diff = end - start
        rate = count / diff
        print(
            "trained batch of len {} in {} sec, at rate {}".format(
                count,
                int(diff * 1000) / 1000,
                int(rate * 1000) / 1000
            ))

    def train(self, datastream):
        rows = 0
        head = []
        for row in datastream:
            head.append(row)
            if len(head) >= BATCH_SIZE:
                self.train_batch(head)
                rows += len(head)
                head = []
        if head:
            self.train_batch(head)
            rows += len(head)
            head = []
        print("Trained {} moves.".format(rows))

    def getMove(self, state):
        # rotate the board for current player
        player = s.getCurrentPlayer(state)
        if player != 0:
            flip = True
            board = s.flipBoard(state)
        else:
            flip = False
            board = state
        # get output of neural network
        y = self.sess.run(self.y, {self.x: [board[:14]], self.keep_prob: 1.0})
        # y is a list containing a single output vector
        # y == [[0.0108906 0.1377293 0.370027 0.2287382 0.0950692 0.1575449]]
        scores = list(y[0])
        bestmove = -1
        bestscore = -1
        # we only want to pick from legal moves (the nn will learn these
        # eventually, but we're helping him with this constraint)
        legalMoves = s.getLegalMoves(board)
        for m in legalMoves:
            if bestscore < scores[m]:
                bestmove = m
                bestscore = scores[m]
        if bestmove < 0:
            bestmove = legalMoves[0]
        move = bestmove
        # if we rotated the board before, rotate it back
        if flip:
            move = s.flipMove(move, player)
        return move
