# -*- coding: utf-8 -*-
# Project : naive-classifier
# Created by igor on 16/8/18

import numpy as np
from random import shuffle


def softmax_loss_naive(W, X, y, reg):
    """
    Soft max loss function, naive implementation (with loops)

    Inputs have dimension D, there are C classes, and we operate on minibatches
     of N examples
    Args:
        W: A numpy array of shape (D,C) containing weights.
        X: A numpy array of shape (N,D) containing a minbatch of data
        y: A numpy array of shape (N,) containing training labels; y[i] = c means
         that X[i] has labels c
        reg: (float) regularization strength

    Returns:
        loss as single float
        gradient with respect to weights W; an array of same shape as W

    """
    loss = 0.0
    dW = np.zeros_like(W)

    num_train = X.shape[0]
    num_class = W.shape[1]

    f = X.dot(W)  # N *C
    f_max = np.reshape(np.max(f, axis=1), (num_train, 1))
    prob = np.exp(f - f_max) / np.sum(np.exp(f - f_max), axis=1, keepdims=True)

    for i in range(num_train):
        for j in range(num_class):
            if j == y[i]:
                loss += -np.log(prob[i, j])  # true class prob loss
                dW[:, j] += (prob[i, j] - 1) * X[i]
            else:
                dW[:, j] += prob[i, j] * X[i]

    loss /= num_train
    dW /= num_train

    loss += 0.5 * reg * np.sum(W * W)
    dW += reg * W

    return loss, dW


def softmax_loss_vectorized(W, X, y, reg):
    '''

    Soft max loss function, vectorized version

    Inputs have dimension D, there are C classes, and we operate on minibatches
     of N examples
    Args:
        W: A numpy array of shape (D,C) containing weights.
        X: A numpy array of shape (N,D) containing a minbatch of data
        y: A numpy array of shape (N,) containing training labels; y[i] = c means
         that X[i] has labels c
        reg: (float) regularization strength

    Returns:
        loss as single float
        gradient with respect to weights W; an array of same shape as W

    '''

    loss = 0.0
    dW = np.zeros_like(W)

    num_train = X.shape[0]
    f = X.dot(W)  # N *C
    f_max = np.reshape(np.max(f, axis=1), (num_train, 1))
    prob = np.exp(f - f_max) / np.sum(np.exp(f - f_max), axis=1, keepdims=True)
    true_class_prob = prob[np.arange(num_train), y]
    loss += np.sum(-np.log(true_class_prob))

    prob[np.arange(num_train), y] = true_class_prob - 1
    dW = np.dot(X.T, prob)

    loss /= num_train
    loss += 0.5 * reg * np.sum(W * W)

    dW /= num_train
    dW += reg * W
    return loss, dW
