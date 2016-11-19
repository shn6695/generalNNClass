import numpy as np
import random


def sigmoid(theta, x):
    '''Standard sigmoid function = 1/(1+exp(-x))
    Input: vector or scalar
    Return: sigmoid of x'''

    return 1 / (1 + np.exp(-np.dot(np.array(theta), np.array(x))))


def sigmoid_prime(theta, x):
    '''Derivative of sigmoid at x
    Input: scalar or vector
    Return: derivative of sigmoid at x'''

    ans = sigmoid(theta, x)
    return ans * (1 - ans)


def tanh(theta, x):
    '''standard tanh function
    Input: scalar or vector
    Return: tanh(x)'''

    t = np.dot(np.array(theta), np.array(x))
    return (np.exp(t) - np.exp(-t)) / (np.exp(t) + np.exp(-t))


def tanh_prime(theta, x):
    '''Derivative of tanh(x)
    Input: scalar or vector
    Return: derivative of tanh at x'''

    return 1 - tanh(theta, x)**2

class DotProductError(Exception):
    def __init__(self, message):
        super(DotProductError, self).__init__(message)

class node(object):

    def __init__(self, n=0, activation_func='sigmoid', bias=False, inpt=False):
        self.theta = [random.uniform(-0.5, 0.5) for i in range(n)]
        self.activation_func = activation_func
        self.bias = False
        self.inpt = False
        if bias:
            self.theta = None
            self.activation_func = None
            self.bias = True
            self.inpt = False
        elif inpt:
            self.theta = None
            self.activation_func = 'input'
            self.bias = False
            self.inpt = True

    def change_theta(self, theta):
        '''Change weights(theta) of node
        Input: new weights'''

        if not self.bias:
            self.theta = theta
        else:
            self.theta = None

    def get_theta(self):
        '''returns theta of node'''

        return self.theta

    def compute_output(self, x=None):
        '''applies activation on input and returns'''

        if not self.bias:
            if not self.inpt:
                if len(x) != len(self.theta):
                    raise DotProductError('Vector Dimension does not match')

            if self.activation_func == 'sigmoid':
                return sigmoid(self.theta, x)
            elif self.activation_func == 'tanh':
                return tanh(self.theta, x)
            elif self.activation_func == 'input':
                return x

        else:
            return 1

if __name__ == '__main__':
    pass
