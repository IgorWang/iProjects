# -*- coding: utf-8 -*-
# Project : naive-classifier
# Created by igor on 16/8/17

from classifiers.linear_svm import *
from classifiers.softmax import *


class LinearClassifier(object):
    def __init__(self):
        self.W = None

    def train(self, X, y, learning_rate=1e-3, reg=1e-5, num_iters=100,
              batch_size=200, verbose=False):
        '''
        Train this linear classifier using stochastic gradient descent.
        Args:
            X: A numpy array of shape (N, D) containing training data;There are N
            training samples each of dimension D.
            y: A numpy array of shape (N,) containing training labels; y[i] = c
            means that X[i] has label 0 <= c < C for C classes
            learning_rate: (float) learning rate for optimization
            reg: (float) regularization strength.
            num_iters: (integer) number of steps to take when optimizing
            batch_size: (integer) number of training examples to use at each step
            verbose: (boolean) If true, print progress during optimization

        Returns:
            A list containing the values of the loss function at each training iteration.

        '''
        num_train, dim = X.shape
        num_classes = np.max(y) + 1

        if self.W is None:
            # lazily initialize W
            self.W = 0.001 * np.random.randn(dim, num_classes)  # D*C

        # Run stochastic gradient descent to optimize W
        loss_history = []
        for it in range(num_iters):
            index = np.random.choice(num_train, batch_size)
            X_batch = X[index]
            y_batch = y[index]

            loss, grad = self.loss(X_batch, y_batch, reg)
            loss_history.append(loss)

            # update the gradient
            self.W = self.W - learning_rate * grad

            if verbose and it % 100 == 0:
                print("iteration %d / %d: loss %f" % (it, num_iters, loss))
        return loss_history

    def loss(self, X_batch, y_batch, reg):
        '''
        Compute the loss function and its derivative
        Subclasses will override this.
        Args:
            X_batch: A numpy array shape of shape (N,D) containing a minibatch of N
             data points; each point has dimension D
            y_batch: A numpy array of shape (N,) containing labels for the minibach
            reg:(float) regularization strength

        Returns: A tuple containing:
            - loss as a single float
            - gradinet with respect to self.W; an array of the same shape as W

        '''
        pass

    def predict(self, X):
        '''
        Use the trained weights of this linear classifier to predict labels for
        data points.

        Args:
            X: N * D array of training data. Each row is a D-dimensional point.

        Returns:
            y_pred: Predicted labels for the data in X. y_pred is a 1-dimensional
            array of length N, and each element is an integer giving the predicted
            class.

        '''
        y_pred = np.zeros(X.shape[0])

        scores = X.dot(self.W)  # (N*D) * (D * C) = N * C

        y_pred = np.argmax(scores, axis=1)

        return y_pred


class LinearSVM(LinearClassifier):
    '''
     A subclass that uses the Multicalss SVM loss function
    '''

    def loss(self, X_batch, y_batch, reg):
        return svm_loss_vectorized(self.W, X_batch, y_batch, reg)


class Softmax(LinearClassifier):
    def loss(self, X_batch, y_batch, reg):
        return softmax_loss_vectorized(self.W, X_batch, y_batch, reg)
