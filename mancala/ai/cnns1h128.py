import random
from .lib import AiNNBase
from .lib.nn_lib import NetworkBase
# import tensorflow as tf
import tensorflow.compat.v1 as tf 
tf.disable_v2_behavior() 


class Network(NetworkBase):

    def initInputPlaceholder(self):
        self.x = tf.placeholder(
            tf.float32,
            shape=(None, 2, 6, 1),
            name="x")

    def conv2d(self, x, W, b, strides=1):
        # Conv2D wrapper, with bias and relu activation
        x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1],
                         padding='SAME', name="conv_Wx")
        x = tf.nn.bias_add(x, b, name="conv_Wx_b")
        return tf.nn.relu(x, name="conv_Wx_b_relu")

    def maxpool2d(self, x, k=2):
        return tf.nn.max_pool(x,
                              ksize=[1, k, k, 1],
                              strides=[1, k, k, 1],
                              padding='SAME',
                              name="mp")

    def addConvLayer(self):
        '''
        https://www.datacamp.com/community/tutorials/cnn-tensorflow-python
        '''
        depth = 4
        self.Wc = self.variable([2, 2, 1, depth], "Wc")
        self.bc = self.variable([depth], "bc")

        self.conv = self.conv2d(self.x, self.Wc, self.bc)
        self.mp = self.maxpool2d(self.conv, k=2)

        self.reshaped = tf.reshape(self.mp, [-1, 12], name="r")
        self.input_size = 12

        self.hiddenSizes.append(self.input_size)
        self.hiddenParams.append((self.Wc, self.bc, self.mp, self.reshaped))

    def makeInputVector(self, state):
        return [
            [[x] for x in state[0:6]],
            [[x] for x in state[7:13]]
        ]

    def __init__(self, name):
        super().__init__(name)
        with self.graph.as_default():
            self.initPlaceholders()
            self.addConvLayer()
            self.addHiddenLayer(128)
            self.initOutputLayer()
            self.initCostFn()
            self.initSession()


class AI(AiNNBase):
    def __init__(self):
        super().__init__()
        self.nn = Network(__name__)

    def taunt(self):
        taunts = [
            "Feeling convoluted?",
        ]
        return random.choice(taunts)
