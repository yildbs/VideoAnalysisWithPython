from scipy import misc
import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
import cv2


class CnnForHumanDetection:
    def __init__(self):
        self._sess = tf.Session()
        self._X = tf.placeholder
        self._Y = tf.placeholder
        self._logits = 0
        self._keep_prob = 0
        self._num_label = 2
        self._shape = [128, 128, 1]

    def initialize(self, shape):
        sess = self._sess
        self._shape = shape

        # Create the model
        self._X = tf.placeholder(tf.float32, [None, shape[0] * shape[1] * shape[2]])
        # Define loss and optimizer
        self._Y = tf.placeholder(tf.float32, [self._num_label])
        # Build the graph for the deep net
        logits, keep_prob = self._deep_nn(self._X, shape, self._num_label)

        saver = tf.train.Saver()
        saver.restore(sess,"./model.ckpt")

    def predict(self, image):
        cv2.imshow('image', image)

        shape = self._shape
        X = self._X
        sess = self._sess
        num_label = self._num_label

        # Build the graph for the deep net
        logits, keep_prob = self._deep_nn(X, shape, num_label)

        batch_size = 1
        image = misc.imresize(image, self._shape[0:3])
        #image = tf.reshape(image, [-1, shape[0], shape[1], shape[2]])
        image = np.reshape(image, (image.size))
        images = []
        images.append(np.asarray(image))
        output = sess.run(logits, feed_dict={X: images, keep_prob: 1})
        labels = sess.run(tf.argmax(output, 1))
        for i in range(batch_size):
            print("label : ", labels[i])

    def _deep_nn(self, x, shape, num_output):
        """deepnn builds the graph for a deep net for classifying digits.
        Args:
        x: an input tensor with the dimensions (N_examples, 784), where 784 is the
        number of pixels in a standard MNIST image.
        Returns:
        A tuple (y, keep_prob). y is a tensor of shape (N_examples, 10), with values
        equal to the logits of classifying the digit into one of 10 classes (the
        digits 0-9). keep_prob is a scalar placeholder for the probability of
        dropout.
        """
        # Reshape to use within a convolutional neural net.
        # Last dimension is for "features" - there is only one here, since images are
        # grayscale -- it would be 3 for an RGB image, 4 for RGBA, etc.
        #x_image = tf.reshape(x, [-1, 28, 28, 1])

        # -------NEW-------#
        #x_image = tf.reshape(x, [-1, 32, 32, 3])
        x_image = tf.reshape(x, [-1, shape[0], shape[1], shape[2]])
        #x_image = x
        ####################

        # First convolutional layer - maps one grayscale image to 32 feature maps.
        #W_conv1 = weight_variable([5, 5, 1, 32])
        #b_conv1 = bias_variable([32])
        #h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)

        # -------NEW-------#
        W_conv1 = self._weight_variable([5, 5, 1, 64])
        b_conv1 = self._bias_variable([64])
        h_conv1 = tf.nn.relu(self._conv2d(x_image, W_conv1) + b_conv1)
        ####################

        # Pooling layer - downsamples by 2X.
        h_pool1 = self._max_pool_2x2(h_conv1)

        norm1 = tf.nn.lrn(h_pool1, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='norm1')

        # Second convolutional layer -- maps 32 feature maps to 64.
        W_conv2 = self._weight_variable([5, 5, 64, 64])
        b_conv2 = self._bias_variable([64])
        h_conv2 = tf.nn.relu(self._conv2d(norm1, W_conv2) + b_conv2)

        # Second pooling layer.
        h_pool2 = self._max_pool_2x2(h_conv2)

        norm2 = tf.nn.lrn(h_pool2, 4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='norm2')

        # Fully connected layer 1 -- after 2 round of downsampling, our 28x28 image
        # is down to 7x7x64 feature maps -- maps this to 1024 features.
        dim_fc1 = int(shape[0] * shape[1] * 4) # shape[0]/4 * shape[1]/4 * 64
        W_fc1 = self._weight_variable([dim_fc1, 384])
        b_fc1 = self._bias_variable([384])

        h_pool2_flat = tf.reshape(norm2, [-1, dim_fc1])
        h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

        # Dropout - controls the complexity of the model, prevents co-adaptation of
        # features.
        keep_prob = tf.placeholder(tf.float32)
        h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

        # Fully connected layer 2 -- after 2 round of downsampling, our 28x28 image
        # is down to 7x7x64 feature maps -- maps this to 1024 features.
        W_fc11 = self._weight_variable([384, 192])
        b_fc11 = self._bias_variable([192])

        h_pool2_flat = tf.reshape(h_fc1_drop, [-1, 384])
        h_fc11 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc11) + b_fc11)

        # Dropout - controls the complexity of the model, prevents co-adaptation of
        # features.
        #keep_prob = tf.placeholder(tf.float32)
        h_fc11_drop = tf.nn.dropout(h_fc11, keep_prob)

        # Map the 1024 features to 10 classes, one for each digit
        W_fc2 = self._weight_variable([192, num_output])
        b_fc2 = self._bias_variable([num_output])

        y_conv = tf.matmul(h_fc11_drop, W_fc2) + b_fc2
        return y_conv, keep_prob

    def _conv2d(self, x, W):
        """conv2d returns a 2d convolution layer with full stride."""
        return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

    def _max_pool_2x2(self, x):
        """max_pool_2x2 downsamples a feature map by 2X."""
        return tf.nn.max_pool(x, ksize=[1, 3, 3, 1], strides=[1, 2, 2, 1], padding='SAME')

    def _weight_variable(self, shape):
        """weight_variable generates a weight variable of a given shape."""
        initial = tf.truncated_normal(shape, stddev=0.1)
        return tf.Variable(initial)

    def _bias_variable(self, shape):
        """bias_variable generates a bias variable of a given shape."""
        initial = tf.constant(0.1, shape=shape)
        return tf.Variable(initial)
