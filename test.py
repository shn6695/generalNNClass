from __future__ import division
from conjugate_gradient import conjugate_gradient as CG
from hypothesis import given
import nn
from hypothesis import strategies as st
import helper as hlp
import grad_descent
import numpy as np
import unittest
import pytest
import node as nd
import math

def simple_func(x):        
	return pow(x[0]-2,6.0)+pow(x[1]-3,6.0)

def grad_of_simple_func(x):
	g = [0,0]
	g[0] = 6.0*pow(x[0]-2,5.0)
	g[1] = 6.0*pow(x[1]-3,5.0)
	return np.array(g)

def least_square_cost(x):
	#x[0] = slope, x[1] = intercept
	m = x[0]
	b = x[1]
	data = [(1.2,1.1), (2.3,2.1), (3.0,3.1), (3.8,4.0), (4.7,4.9), (5.9,5.9)]
	summation = 0
	for xi,yi in data:
		summation += (yi-m*xi-b)**2
	return summation/6.0

def some_complex_func(list_of_variable):
	x = list_of_variable[0]
	y = list_of_variable[1]
	return (x-1)**2 + (y-2)**2 + (x**2)*(y**2) + ((x-1)**2)*((y-3)**2)

def grad_of_some_complex_func(list_of_variable):
	x = list_of_variable[0]
	y = list_of_variable[1]
	grad_x = 2*(x-1) + 2*x*(y**2) + 2*(x-1)*((y-3)**2)
	grad_y = 2*(y-2) + 2*y*(x**2) + 2*(y-3)*((x-1)**2)
	return np.array([grad_x, grad_y])

###################### neural net ###################

class TestNeuralNet(unittest.TestCase):

	def test_neural_net(self):
		obj = nn.neural_network([2,3,2])
		data = [[1,1], [2,2], [3,3], [4,4], [5,5], [6,6]]
		target = [[1,0], [1,0], [1,0], [0,1], [0,1], [0,1]]

		matrix = [[[1,2,3], [4,5,6], [7,8,9]], [[10,11,12,13], [14,15,16,17]]]
		ans = np.array([0.006, 0.1, 0.2, 8.1e-07, 0.4, 0.5, 1.0e-10, 0.6, 0.7, 0.5, 1.4, 1.5, 1.5, 0.5, 1.7, 1.8, 1.9])
		fprime = obj.back_propogation(data,target)
		vec = obj.roll_mat(matrix)
		cal = np.array(fprime(vec))
		self.assertAlmostEqual(cal.all(), ans.all(), delta=1)
		self.assertEqual(np.array(obj.unroll_vector(vec)).all(), np.array(matrix).all())
		matrix = [[[1,2,3], [4,5,6], [7,8,9]], [[1,1,1,1], [4,5,6,7]]]
		vec = obj.roll_mat(matrix)
		obj.change_network_theta(matrix)
		cost_func = obj.compute_cost(data, target)
		cost = cost_func(vec)
		self.assertAlmostEqual(cost, 91, delta=1)


'''
###################### node.py ######################

class TestActivation(unittest.TestCase):
	
	# testing sigmoid, sigmoid_prime
	def test_sigmoid(self):
		theta = np.array([1, 2, 3, 4, 5])
		x = np.array([.5, .6, .7, .8, .9])
		self.assertAlmostEqual(nd.sigmoid(theta, x), 0.9999898700090192, places = 10)
		self.assertAlmostEqual(nd.sigmoid(-theta, x), 1.0129990980873921e-05, places = 10)

	def test_sigmoid_prime(self):
		theta = np.array([1, 2, 3, 4, 5])
		x = np.array([.5, .6, .7, .8, .9])
		sgd = nd.sigmoid(theta, x)
		sgd_theoritical = sgd*(1-sgd)
		self.assertAlmostEqual(sgd_theoritical.all(), nd.sigmoid_prime(theta, x).all())
	
	# testing tanh, tanh_prime
	def test_tanh(self):
		theta = np.array([1, 2, 3, 4, 5])
		x = np.array([.5, .6, .7, .8, .9])
		self.assertAlmostEqual(nd.tanh(theta, x), 0.9999999997947623, places = 10)	
		self.assertAlmostEqual(nd.tanh(-theta, x), -0.9999999997947623, places = 10)

	def test_tanh_prime(self):
		theta = np.array([1, 2, 3, 4, 5])
		x = np.array([.5, .6, .7, .8, .9])
		tanhval = nd.tanh(theta, x)
		tanh_theoritical = tanhval*(1-tanhval)
		self.assertAlmostEqual(tanh_theoritical.all(), nd.tanh_prime(theta, x).all())

	def test_node(self):
		obj1 = nd.node(5)
		theta = np.array(obj1.get_theta())
		self.assertAlmostEqual(theta.all(), np.array([1, 1, 1, 1, 1]).all(), delta=1)
		obj1.change_theta([1,2,3,4,5])
		theta = np.array(obj1.get_theta())
		self.assertEqual(theta.all(), np.array([1,2,3,4,5]).all())
		x = np.array([.5, .6, .7, .8, .9])
		self.assertAlmostEqual(obj1.compute_output(x), nd.sigmoid(theta, x))

		obj2 = nd.node(5, activation_func='tanh')
		theta = np.array(obj1.get_theta())
		self.assertAlmostEqual(theta.all(), np.array([1, 1, 1, 1, 1]).all(), delta=1)
		obj1.change_theta([1,2,3,4,5])
		theta = np.array(obj1.get_theta())
		self.assertEqual(theta.all(), np.array([1,2,3,4,5]).all())
		x = np.array([.5, .6, .7, .8, .9])
		self.assertAlmostEqual(obj1.compute_output(x), nd.tanh(theta, x), delta=0.01)

		obj3 = nd.node(inpt=True)
		self.assertEqual(obj3.compute_output(x).all(), x.all())


###################### grad_descent.py and conjugate_gradient.py ######################

class TestOptimization(unittest.TestCase):

	###################### for conjugate descent #################
	@given(strategies.floats(min_value =-20, max_value = 20), strategies.floats(min_value = -20, max_value = 20))
	def test_simple_func_with_conjugate(self,initial_x, initial_y):
		x = CG(simple_func,[initial_x, initial_y], alpha=0.5, norm_lim=1e-7, disp=False)
		self.assertAlmostEqual(x[0],2.0, delta=0.03)
		self.assertAlmostEqual(x[1],3.0, delta=0.03)

	@given(strategies.floats(min_value =-20, max_value = 20), strategies.floats(min_value = -20, max_value = 20))
	def test_simple_func_with_conjugate(self,initial_x, initial_y):
		x = CG(simple_func,[initial_x, initial_y], fprime=grad_of_simple_func, alpha=0.5, norm_lim=1e-7, disp=False)
		self.assertAlmostEqual(x[0],2.0, delta=0.03)
		self.assertAlmostEqual(x[1],3.0, delta=0.03)

	@given(strategies.floats(min_value =-20, max_value = 20), strategies.floats(min_value = -20, max_value = 20))
	def test_least_square_cost_with_conjugate(self,initial_x, initial_y):
		x = CG(least_square_cost,[30,100],alpha=0.5, norm_lim=1e-7, disp=False)
		self.assertAlmostEqual(x[0],1.05, delta=0.03)
		self.assertAlmostEqual(x[1],-0.14, delta=0.03)

	@given(strategies.floats(min_value =-20, max_value = 20), strategies.floats(min_value = -20, max_value = 20))
	def test_some_complex_func_with_conjugate(self,initial_x, initial_y):
		x = CG(some_complex_func,[30,100], alpha=0.5, norm_lim=1e-7, disp=False)
		self.assertAlmostEqual(x[0], 0.215, delta=0.03)
		self.assertAlmostEqual(x[1], 2.31, delta=0.03)

	@given(strategies.floats(min_value =-20, max_value = 20), strategies.floats(min_value = -20, max_value = 20))
	def test_some_complex_func_with_conjugate(self,initial_x, initial_y):
		x = CG(some_complex_func,[30,100], fprime=grad_of_some_complex_func, alpha=0.5, norm_lim=1e-7, disp=False)
		self.assertAlmostEqual(x[0], 0.215, delta=0.03)
		self.assertAlmostEqual(x[1], 2.31, delta=0.03)	

	##################### for gradient descent ##################
	@given(strategies.floats(min_value =-20, max_value = 20), strategies.floats(min_value = -20, max_value = 20))
	def test_simple_with_grad_descent(self, initial_x, initial_y):
		x = grad_descent.grad_descent(simple_func,[initial_x, initial_y], adaptive=True, alpha=0.01, \
										norm_lim=1e-7, disp=False)
		self.assertAlmostEqual(x[0],2.0, delta=0.05 )
		self.assertAlmostEqual(x[1],3.0, delta=0.05)

	@given(strategies.floats(min_value =-20, max_value = 20), strategies.floats(min_value = -20, max_value = 20))
	def test_simple_with_grad_descent(self, initial_x, initial_y):
		x = grad_descent.grad_descent(simple_func, [initial_x, initial_y], fprime=grad_of_simple_func, \
										adaptive=True, alpha=0.5, norm_lim=1e-7, disp=False)
		self.assertAlmostEqual(x[0],2.0, delta=0.05 )
		self.assertAlmostEqual(x[1],3.0, delta=0.05)	

	@given(strategies.floats(min_value =-20, max_value = 20), strategies.floats(min_value = -20, max_value = 20))
	def test_least_square_cost_with_grad_descent(self, initial_x, initial_y):
		x = grad_descent.grad_descent(least_square_cost, [initial_x, initial_y], adaptive=True, alpha=0.5, \
										norm_lim=1e-7, disp=False)
		self.assertAlmostEqual(x[0],1.05, delta=0.03)
		self.assertAlmostEqual(x[1],-0.14, delta=0.03)

	@given(strategies.floats(min_value =-20, max_value = 20), strategies.floats(min_value = -20, max_value = 20))
	def test_some_complex_func_with_grad_descent(self, initial_x, initial_y):
		x = grad_descent.grad_descent(some_complex_func, [initial_x, initial_y], adaptive=True , alpha=0.5, \
										norm_lim=1e-7, disp=False)
		self.assertAlmostEqual(x[0], 0.215, delta=0.03)
		self.assertAlmostEqual(x[1], 2.31, delta=0.03)

	@given(strategies.floats(min_value =-20, max_value = 20), strategies.floats(min_value = -20, max_value = 20))
	def test_some_complex_func_with_grad_descent(self, initial_x, initial_y):
		x = grad_descent.grad_descent(some_complex_func, [initial_x, initial_y], fprime=grad_of_some_complex_func, \
										adaptive=True , alpha=0.5, norm_lim=1e-7, disp=False)
		self.assertAlmostEqual(x[0], 0.215, delta=0.03)
		self.assertAlmostEqual(x[1], 2.31, delta=0.03)	


###################### helper.py ######################

class TestHelpers(unittest.TestCase):

	########################### for compute_numerical_grad ########################
	@given(strategies.floats(min_value=-10000,max_value=10000), strategies.floats(min_value=-10000,max_value=10000))
	def test_compute_numerical_grad(self,x,y):
		numerical_grad_of_some_complex_func = hlp.compute_numerical_grad(some_complex_func,2)
		self.assertAlmostEqual(numerical_grad_of_some_complex_func([x,y]).all(), grad_of_some_complex_func([x,y]).all(), \
								delta=0.1)

	########################## for vector norm callculating function vecnorm#######
	def test_vecnorm(self):
		vector = [1,2,3,4,5]
		self.assertAlmostEqual(hlp.vecnorm(vector),np.sqrt(55))
		self.assertEqual(hlp.vecnorm(vector,order=np.Inf),5)
		self.assertEqual(hlp.vecnorm(vector,order=-np.Inf),1)
'''
if __name__ == '__main__':
	pass