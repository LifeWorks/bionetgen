# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 14:45:24 2012

@author: proto
"""

'''
this method classifies reactants according to the rdf information, and gives
us information on which reactants are the same, and how do they differ
(compartment etc)
'''

from libsbml2bngl import SBML2BNGL
import libsbml

def getAnnotations(parser,stringKey):
    annotation = parser.getSpeciesAnnotation()
    annotationDictionary = {}
    for key,value in annotation.items():
        annotationList = []
        if annotation[key] != None:
            for index in range(0,annotation[key].getNumAttributes()):
                if stringKey in annotation[key].getValue(index):
                    annotationList.append(annotation[key].getValue(index))
            if frozenset(annotationList) in annotationDictionary:
                annotationDictionary[frozenset(annotationList)].append(key)
            else:
                annotationDictionary[frozenset(annotationList)] = [key]
    return annotationDictionary

def getEquivalence(species,rdf_database):
    '''
    *species* is the species whose equivalence we will go and search
    This method will search through the RDF database and look if param 'species'
    is equal to any other element in the species database
    '''
    
    for element in rdf_database:
        if species in rdf_database[element]:
            return [x for x in rdf_database[element] if x != species]
    return []

if __name__ == "__main__":
    reader = libsbml.SBMLReader()
    #BIOMD0000000272
    document = reader.readSBMLFromFile('XMLExamples/curated/BIOMD0000000272.xml')
    #document = reader.readSBMLFromFile('XMLExamples/simple4.xml')
    model = document.getModel()        
    parser = SBML2BNGL(model)
    annotationDictionary =  getAnnotations(parser,'uniprot')
    print annotationDictionary
    print getEquivalence('SAv_EpoR',annotationDictionary)
    #print annotation
    #print rules    
