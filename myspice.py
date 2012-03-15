#!/usr/bin/python2.7

"""@package myspice
Purpose:
This source file parses a PSPICE netlist
file, checks for errors, then runs a simulation
and outputs a graph of the results.
"""

import sys
import re
from components import *
import matplotlib.pyplot as plt

def main():
	if (len(sys.argv) != 2):
		print >> sys.stderr, "Usage: ./myspice.py <SPICE file>"
		return -1
		
	inputFile = sys.argv[1]
	
	sim = SpiceSimulation()
	sim.parseSpiceFile(inputFile)
	
	readyToRun = sim.generateReport("reports.txt", inputFile)
	if not(readyToRun) and sim.analysisCommandPresent:
		print "Warning: Analysis not run due to netlist errors."
		return -1
	elif sim.analysisCommandPresent:
		print "Running"
		sim.run()
	



class SpiceSimulation(object):	
	"""Simulation object
	
	This class contains methods for parsing a standard SPICE
	file and running a simulation using Eueler's method.
	"""
	
	componentList = []
	tstep = 0.0
	tstop = 0.0
	simulationName = ""
	topology = "unknown"
	containsGround = False
	nodeList = {}
	
	# varaible tracks if an analysis command has been read
	analysisCommandPresent = False
				
	def parseSpiceFile(self, fname):
		file = open(fname)
		self.simulationName = file.readline().strip()
			
		for line in file:
			line = line.strip()
			
			# skip comments
			if line[0] == "*":
				continue
			
			if line[0] == ".":
				self.analysisCommandPresent = True
			
			# break if end of file reached
			if line == ".end":
				break
			
			lineList = line.split()
			
			# check for .tran config command
			if lineList[0].lower() == ".tran":
				(value, exponent) = self.parseComponentValue(lineList[1])
				self.tstep = value * 10**exponent
				
				(value, exponent) = self.parseComponentValue(lineList[2])
				self.tstop = value * 10**exponent
				
			# check for component
			if lineList[0][0].upper() in ["V","R","C","L"]:
				name  = lineList[0]
				node1 = lineList[1]
				node2 = lineList[2]
				otherAtrributes = ""
				
				# remove the "DC" string from the list so we can parse the same
				# list position for all possible components
				if lineList[3] == "DC":
					del lineList[3]
					
				(value, exponent) = self.parseComponentValue(lineList[3])
				
				# check if any other attributes were specified 
				if len(lineList) > 4:
					otherAtrributes = lineList[4]
								
				# add nodes to a node list, allows us to count the numer of nodes easily					
				if self.nodeList.has_key(node1):
					self.nodeList[node1][0] += 1
					self.nodeList[node1].append(name)
				else:
					self.nodeList[node1] = [1, name]
				
				if self.nodeList.has_key(node2):
					self.nodeList[node2][0] += 1
					self.nodeList[node2].append(name)
				else:
					self.nodeList[node2] = [1, name]
				
				# check if one of the nodes is ground
				if node1 == "0" or node2 == "0":
					self.containsGround = True
				
				
				# append the proper component to the component list
				if   lineList[0][0].upper() == "V":
					self.componentList.append(VoltageSource(name, node1, node2, value, exponent, ""))
				
				elif lineList[0][0].upper() == "R":
					self.componentList.append(Resistor(name, node1, node2, value, exponent, otherAtrributes))
				
				elif lineList[0][0].upper() == "C":
					self.componentList.append(Capacitor(name, node1, node2, value, exponent, otherAtrributes))
				
				elif lineList[0][0].upper() == "L":
					self.componentList.append(Inductor(name, node1, node2, value, exponent, otherAtrributes))
				
				
	def parseComponentValue(self, str):
		"""parse out a number and an exponent from a string input"""
		exponent = 0
		str = str.lower()
		number = re.match("\d*\.?\d*", str)
				
		abbreviation = ""
		# check if a postfix comes after the number
		if number.end() < len(str):
			abbreviation = str[number.end()]
		
		# determine the appropriate exponent
		if "meg" in str:
			exponent =  6
		elif "f" in abbreviation:
			exponent = -15
		elif "p" in abbreviation:
			exponent = -12
		elif "n" in abbreviation:
			exponent = -9
		elif "u" in abbreviation:
			exponent = -6
		elif "m" in abbreviation:
			exponent = -3
		elif "k" in abbreviation:
			exponent =  3

		return 	(float(str[number.start():number.end()]), exponent)
		
	def run(self):
		"""Run the simulation using Euler's Method"""
		
		
	def generateReport(self, reportFileName, inputFileName):
		"""Process the netlist for errors and print a report file
		
		Return True if the simulation can be run, False if not
		"""
		
		# create a sorted list of all noes
		sortedKeys = sorted(self.nodeList.keys())
		
		# sort component list by component name
		self.componentList = sorted(self.componentList, key=lambda k: k.name)
		
		# detect topology
		# check if series
		seriesTopology = True
		for i in self.nodeList:
			if self.nodeList[i][0] != 2:
				seriesTopology = False
		
		if seriesTopology:
			self.topology = "series RLC"
		else:
			if len(nodeList) > 2:
				self.topology = "parallel RLC"
		
		error = False
	
		f = open(reportFileName, 'w')
		f.write("Input File: " + inputFileName + "\n")
		f.write("Title: " + self.simulationName + "\n")
		f.write("Topology: " + self.topology + "\n")
		f.write("------------------------------------------------\n")
		f.write("Node Report\n")
		f.write("------------------------------------------------\n")
		f.write("Number of Nodes: " + str(len(self.nodeList)) + "\n")
		f.write("Node".ljust(6) + "# Connections".ljust(15) + "Elements".ljust(9) + "\n")
		for i in sortedKeys:
			f.write(str(i).ljust(6) + str(self.nodeList[i][0]).ljust(15) +
				", ".join(self.nodeList[i][1:]).ljust(9) + "\n")
			
		f.write("\n")
		f.write("------------------------------------------------\n")
		f.write("Component Report\n")
		f.write("------------------------------------------------\n")
		f.write("Type".ljust(16) + "Name".ljust(8) + "Value".ljust(8)
			+ "Other Attributes".ljust(16) + "\n")
		for c in self.componentList:
			if c.name[0].upper() == "V":
				f.write("Voltage Source".ljust(16))
			elif c.name[0].upper() == "R":
				f.write("Resistor".ljust(16))
			elif c.name[0].upper() == "C":
				f.write("Capacitor".ljust(16))
			elif c.name[0].upper() == "L":
				f.write("Inductor".ljust(16))
							
			f.write(c.name.ljust(8))
			
			if c.exponent == 0:
				f.write(str(c.value).ljust(8))
			else:
				f.write( (str(c.value)+"e"+str(c.exponent)).ljust(8))
				
			f.write(c.otherAttributes.ljust(16) + "\n")
		f.write("\n")
		
		# check for errors in the netlist
		# make sure ever node has at least 2 connects
		for i in sortedKeys:
			if self.nodeList[i][0] < 2:
				print >> sys.stderr, "ERROR: Open circuit at node " + str(self.nodeList[i][0])
				f.write("ERROR: Open circuit at node " + str(self.nodeList[i][0]) + "\n")
				error = True
		# make sure a ground exists
		if not(self.containsGround):
			print >> sys.stderr, "ERROR: No reference node \"0\" is defined"
			f.write("ERROR: No reference node \"0\" is defined\n")
			error = True
		
		# return true if the sim is good to run
		# false otherwise
		return not(error)
		
if __name__ == "__main__":
	sys.exit(main())






