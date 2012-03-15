
"""@package myspice

This source file contains class definitions for
various electric compnents used in the simulation.
"""

class Component(object):
	"""Base class for all Components"""
	name = ""
	value = 0
	node1 = 0
	node2 = 0
	exponent = 0
	otherAttributes = ""

	def __init__(self, name, node1, node2, value, exponent, otherAttributes):
		self.name = name
		self.node1 = node1
		self.node2 = node2
		self.value = value
		self.exponent = exponent
		self.otherAttributes = otherAttributes

class VoltageSource(Component):
	"""Contains properties associated with a voltage source"""
	
	def __init__(self, name, node1, node2, value, exponent, otherAttributes):
		super(VoltageSource, self).__init__(name, node1, node2, value, exponent, otherAttributes)

class Resistor(Component):
	"""Contains properties associated with a resistor"""
	
	def __init__(self, name, node1, node2, value, exponent, otherAttributes):
		super(Resistor, self).__init__(name, node1, node2, value, exponent, otherAttributes)
	
class Capacitor(Component):
	"""Contains properties associated with a capacitor"""
	
	def __init__(self, name, node1, node2, value, exponent, otherAttributes):
		super(Capacitor, self).__init__(name, node1, node2, value, exponent, otherAttributes)
		
class Inductor(Component):
	"""Contains properties associated with a inductor"""
	
	def __init__(self, name, node1, node2, value, exponent, otherAttributes):
		super(Inductor, self).__init__(name, node1, node2, value, exponent, otherAttributes)
		
		
		
		
		
		