# -*- coding: utf-8 -*-
# Project : naive-classifier
# Created by igor on 16/8/13
import numpy as np
from random import shuffle


def svm_loss_naive(W, X, y, reg):
    '''
    Structured SVM loss function
    navie implementation (with loops)

    Inputs have dimension D, there are C classes, and we operate on minibatches
   of N examples.

    Args:
        W: A numpy array of shape (D,C) containing weights
        X: A numpy array of shape (N,D) containing a minibatch of data
        y: A numpy array of shape (N,) containing training labels
        reg: (float) regularization strength

    Returns:
        - loss as single float
        - gradient with respect to weight W; a array of same shape as W
    '''

    dW = np.zeros(W.shape)  # initialize the gradient as zero

    # compute the loss and the gradient
    num_classess = W.shape[1]
    num_train = X.shape[0]
    loss = 0.0
    for i in range(num_train):
        scores = X[i].dot(W)
        correct_class_score = scores[y[i]]

        for j in range(num_classess):
            if j == y[i]:
                continue
            margin = scores[j] - correct_class_score + 1  # note delta =1

            if margin > 0:
                loss += margin
                dW[:, y[i]] += -X[i, :]
                dW[:, j] += X[i, :]
    # average loss
    loss /= num_train
    dW /= num_train
    # L2 regularization
    loss += 0.5 * reg * np.sum(W * W)
    # Compute the gradient of the loss function
    dW += reg * W
    return loss, dW


def svm_loss_vectorized(W, X, y, reg):
    """
   Structured SVM loss function, vectorized implementation.

   Inputs and outputs are the same as svm_loss_naive.
   Args:
        W: A numpy array of shape (D,C) containing weights
        X: A numpy array of shape (N,D) containing a minibatch of data
        y: A numpy array of shape (N,) containing training labels
        reg: (float) regularization strength

    Returns:
        - loss as single float
        - gradient with respect to weight W; a array of same shape as W
    """

    loss = 0.0
    dW = np.zeros(W.shape)
    scores = X.dot(W)  # shape = (N ,C)
    # slice for correct scores
    num_classess = W.shape[1]
    num_train = X.shape[0]
    correct_scores = scores[np.arange(num_train), y].reshape((num_train, 1))  # shape=(N,1)
    margins = scores - correct_scores + 1
    margins[np.arange(num_train), y] = 0.0  # j = y_j
    margins[margins <= 0] = 0.0
    loss += np.sum(margins)
    loss /= num_train
    loss += 0.5 * reg * np.sum(W * W)

    # compute gradient dW
    margins[margins > 0] = 1.0
    row_sum = np.sum(margins, axis=1)  # (1,N)
    margins[np.arange(num_train), y] = - row_sum
    dW += np.dot(X.T, margins) / num_train + reg * W

    return loss, dW
