# coding=utf-8
# import utils
# from preference_functions import PreferenceFunctions


class PROMETHEE:
	"""Preference Ranking Organization Method for Enrichment of Evaluation

	Parameters:
	-----------
	evaluation_matrix : 
	weights : 
	preference_function :
	function_params :


	Returns:
	--------

	"""
	def __init__(self, evaluation_matrix, weights, preference_function, function_params):
		
		assert(len(weights) == len(evaluation_matrix[0]))
		self.evaluationTable = evaluation_matrix
		self.numberAlternatives = len(evaluation_matrix)
		self.numberCriteria = len(evaluation_matrix[0])
		self.weights = weights
		self.normalizeWeights()
		self.p = function_params['p']
		self.q = function_params['q']
		self.sigma = function_params['sigma']
		self.preference_function = preference_function
		self.assignShapeFunctions()
		# compute pair wise comparison
		self.computeAllRankings()

	def computeAllRankings(self):
		self.computePairWiseComparisonMatrix()
		self.computepositiveFlow()
		self.computeNegativeFlow()
		self.computeGlobalFlow()
		self.computePositiveMatrix()
		self.computeNegativeMatrix()
		self.computePrometheeIMatrix()
		self.computePrometheeIIMatrix()

	def normalizeWeights(self):
		# normalizes the weights given as an input;
		sumW = sum(self.weights)
		for i in range(len(self.weights)):
			self.weights[i] = self.weights[i]/sumW

	def computepositiveFlow(self):
		phi_plus = [0]*self.numberAlternatives
		for a in xrange(self.numberAlternatives):
			sum = 0
			for b in xrange(self.numberAlternatives):
				sum += self.pi[a][b]
			phi_plus[a] = sum/(self.numberAlternatives-1)
		self.phi_plus = phi_plus

	def computeNegativeFlow(self):
		phi_minus = [0]*self.numberAlternatives
		for a in xrange(self.numberAlternatives):
			sum = 0
			for b in xrange(self.numberAlternatives):
				sum += self.pi[b][a]
			phi_minus[a] = sum/(self.numberAlternatives-1)
		self.phi_minus = phi_minus

	def computeGlobalFlow(self):
		self.phi_global = [0] * self.numberAlternatives
		for a in xrange(self.numberAlternatives):
			self.phi_global[a] = self.phi_plus[a]-self.phi_minus[a]

	def getPrometheeIIRanking(self):
		for x in range(len(self.phi_global)):
			print(self.phi_global[x])
		self.prometheeII = sorted(range(len(self.phi_global)),key = lambda k: self.phi_global[k], reverse= True);
		for x in range(len(self.prometheeII)):
			print(self.prometheeII[x])
	
	def getPrometheeIRanking(self):
		print("promethee I")

	def assignShapeFunctions(self):
		self.shapeFunction = [None]*self.numberCriteria
		availablePreferenceFunctions = PreferenceFunctions(self.p, self.q, self.sigma).get_preference_functions();
		assert(self.preference_function in availablePreferenceFunctions)
		for i in xrange(self.numberCriteria):
			self.shapeFunction[i] = availablePreferenceFunctions[self.preference_function]

	def getPairwiseComparisonMatrix(self):
		self.computePairWiseComparisonMatrix()
		return self.pi

	def computePairWiseComparisonMatrix(self):
		self.pi = utils.initialise_matrix(self.numberAlternatives,self.numberAlternatives)
		for a in xrange(self.numberAlternatives):
			for b in xrange(self.numberAlternatives):
				if a!=b:
					sum = 0
					for k in xrange(self.numberCriteria):
						delta = self.evaluationTable[a][k]-self.evaluationTable[b][k]
						sum += self.weights[k]*self.shapeFunction[k](delta)
					self.pi[a][b] = sum

	def computePositiveMatrix(self):
		self.positive_matrix = utils.initialise_matrix(self.numberAlternatives,self.numberAlternatives);
		for a in xrange(self.numberAlternatives):
			for b in xrange(self.numberAlternatives):
				if self.phi_plus[a]>self.phi_plus[b]:
					self.positive_matrix[a][b] = 1
				elif self.phi_plus[a]<self.phi_plus[b]:
					self.positive_matrix[a][b] = -1
				else:
					self.positive_matrix[a][b] = 0

	def computeNegativeMatrix(self):
		self.negative_matrix = utils.initialise_matrix(self.numberAlternatives,self.numberAlternatives);
		for a in xrange(self.numberAlternatives):
			for b in xrange(self.numberAlternatives):
				if self.phi_minus[a]<self.phi_minus[b]:
					self.negative_matrix[a][b] = 1
				elif self.phi_minus[a]>self.phi_minus[b]:
					self.negative_matrix[a][b] = -1
				else:
					self.negative_matrix[a][b] = 0

	def computePrometheeIMatrix(self):
		self.prometheeI_matrix = utils.initialise_matrix(self.numberAlternatives,self.numberAlternatives);
		for a in range(self.numberAlternatives):
			for b in range(self.numberAlternatives):
				# case 1 : both fluxes give the same result
				# consequently, promethee I ranking is the one given by negative and positive fluxes
				# this covers the sases cas : double preference, double indifferent
				if (self.positive_matrix[a][b] == self.negative_matrix[a][b]):
					self.prometheeI_matrix[a][b] = self.positive_matrix[a][b]
				# case 2: we handle presenfe of an indifference
				else:
					# casa 1: one of the two rankings gives an equality
					# in this case, ranking is the sum of two rankings
					if (self.positive_matrix[a][b]==0 or self.negative_matrix[a][b]==0):
						self.prometheeI_matrix[a][b]= self.positive_matrix[a][b]+self.negative_matrix[a][b];
					# last case: both results are different but none is zero. This gives an incomparability
					else:
						self.prometheeI_matrix[a][b] = "R"

	def computePrometheeIIMatrix(self):
		self.prometheeII_matrix = utils.initialise_matrix(self.numberAlternatives,self.numberAlternatives);
		for a in range(self.numberAlternatives):
			for b in range(self.numberAlternatives):
				if self.phi_plus[a]>self.phi_plus[b]:
					self.prometheeII_matrix[a][b]=1
				elif self.phi_plus[a]<self.phi_plus[b]:
					self.prometheeII_matrix[a][b]=-1
				else:
					self.prometheeII_matrix[a][b]=0

	def getPrometheeIIMatrix(self):
		return self.prometheeII_matrix

	def getPrometheeIMatrix(self):
		return self.prometheeI_matrix

	def getPositiveMatrix(self):
		return self.positive_matrix

	def getNegativeMatrix(self):
		return self.negative_matrix

	def getPairwiseComparisonMatrix(self):
		return self.pi
	
	def getGlobalFlow(self):
		return self.phi_global

		