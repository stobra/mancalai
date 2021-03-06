import random
from .lib import AiNNBase
from .lib.nn_lib import NetworkBase, INPUT_SIZE
# import tensorflow as tf
import tensorflow.compat.v1 as tf 
tf.disable_v2_behavior() 
MAX_BEADS = 48


def oneHot(r, length=MAX_BEADS):
    """
    Given an integer r in the range [0:48] return vector of length 48 where all
    values are zero except the vector at index r which is one.

    >>> oneHot(5, 10)
    [0, 0, 0, 0, 0, 1, 0, 0, 0, 0]

    >>> oneHot(15, 10)
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    """
    if r > length - 1:
        r = length - 1
    return [0] * (r) + [1] + [0] * (length - 1 - r)


class Network(NetworkBase):

    def initInputPlaceholder(self):
        self.input_size = INPUT_SIZE * MAX_BEADS
        # self.pre_x0 = tf.placeholder(
        # tf.float32,
        # shape=(None, MAX_BEADS, INPUT_SIZE),
        # name="raw_input")
        # self.pre_x1 = tf.reshape(self.pre_x0, [-1, self.input_size, 1],
        # name="reshaped")
        # self.x = tf.squeeze(self.pre_x1, [2], name="squeezed")
        self.x = tf.placeholder(
            tf.float32,
            shape=(None, self.input_size),
            name="x")

    def makeInputVector(self, state):
        vector = [oneHot(r) for r in state[:14]]
        return [item for sublist in vector for item in sublist]

    def __init__(self, name):
        super().__init__(name)
        with self.graph.as_default():
            self.initPlaceholders()
            self.addHiddenLayer(80)
            self.addHiddenLayer(80)
            self.addHiddenLayer(80)
            self.initOutputLayer()
            self.initCostFn()
            self.initSession()


class AI(AiNNBase):
    def __init__(self):
        super().__init__()
        self.nn = Network(__name__)

    def taunt(self):
        taunts = [
            'I look at the board in a different way.',
            "I'll win this one for sure.",
            "I have three layers of awesomeness.",
        ]
        return random.choice(taunts)
