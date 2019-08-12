# coding=utf-8
import numpy as np


def generate_preference_function_parameters(delta, function):
	"""
	Generate preference function parameters

	Parameters
	__________
	
	delta : the delta between two evaluation parameters (FLOAT)
	function : the type of function that is used (STRING)

	"""
	objects_array = []

	if function in ['linear', 'level', 'linear_with_indifference']:
		p = np.arange(0,1,delta)
		if function in ['level', 'linear_with_indifference']:
			for x in range(0,len(p)):
				q = np.arange(0,p[x],delta)
				for y in range(0,len(q)):
					objects_array.append({'p': p[x], 'q': q[y],'sigma': 0})
		else :
			for x in range(0, len(p)):
				objects_array.append({'p': p[x], 'q': 0, 'sigma': 0})	
	elif function == 'quasi-criterion':
		q = np.arange(0,1,delta)
		for x in range(0,len(q)):
			objects_array.append({'p':0, 'q': q[x], 'sigma': 0})
	elif function == 'gaussian':
		sigma = np.arange(0,1,delta)
		print(sigma)
		for x in range(0, len(sigma)):
			objects_array.append({'p':0, 'q': 0, 'sigma': sigma[x]})
	elif function == 'usual':
		objects_array.append({'p': 0, 'q': 0, 'sigma': 0})
	return objects_array


class PreferenceFunctions:
	def __init__(self, p, q, sigma):
		self.p = p
		self.q = q
		self.sigma = sigma

	def usual_function(self, delta):
		if (delta > 0):
			return 1
		else:
			return 0

	def linear_function(self, delta):
		if (delta < 0):
			output = 0.0
		elif (delta < self.p):
			output = delta / self.p
		elif (delta > self.p):
			output = 1.0
		else:
			output = (delta)
		return output
	
	def gaussian_function(self, delta):
		if (delta >= 0):
			res = 1 - np.exp(-(delta**2.0) / (2 * (self.sigma**2)))
		else:
			res = 0
		return res
	
	def quasi_criterion(self, delta):
		if delta > self.q:
			res = 1
		else:
			res = 0
		return res

	def level_criterion(self, delta):
		if delta > 0 :
			if delta > self.p:
				res = 1
			elif delta > self.q:
				res = 0.5
			else:
				res = 0
		else:
			res = 0
		return res

	def linear_with_indifference(self, delta):
		if delta < self.q:
			res = 0
		else:
			if delta > self.p:
				res = 1
			else:
				res = (delta - self.q) / (self.p - self.q)
		return res

	def get_preference_functions(self):
		return {
			'usual': self.usual_function,
			'linear': self.linear_function,
			'gaussian': self.gaussian_function,
			'quasi-criterion': self.quasi_criterion, 
			'level': self.level_criterion,
			'linear_with_indifference': self.linear_with_indifference
		}