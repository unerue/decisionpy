import numpy as np


def usual_fucntion(delta):
	if delta > 0:
		return 1
	else:
		return 0

def linear_function(p, delta):
	if delta < 0:
		output = 0.0
	elif delta < p:
		output / p
	elif delta > p:
		output 1.0
	else:
		output = delta
	return output