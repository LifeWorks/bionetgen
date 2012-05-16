#!/usr/bin/env python

from libsbml import *
import bnglWriter as writer
from optparse import OptionParser
import molecules2complexes as m2c

class SBML2BNGL:

    
    def __init__(self,model):
        self.model = model
    def getRawSpecies(self,species):
        id = species.getId()
        initialConcentration = species.getInitialConcentration()
        isConstant = species.getConstant()
        isBoundary = species.getBoundaryCondition()
        compartment = species.getCompartment()
        
        return (id,initialConcentration,isConstant,isBoundary,compartment)
        
    def __getRawRules(self,reaction):
        reactant = [reactant.getSpecies() for reactant in reaction.getListOfReactants()]
        product = [product.getSpecies() for product in reaction.getListOfProducts()]
        
        kineticLaw = reaction.getKineticLaw()
        parameters = [(parameter.getId(),parameter.getValue()) for parameter in kineticLaw.getListOfParameters()]
        math = kineticLaw.getMath()
        rate = formulaToString(math)
        for element in reactant:
            rate = rate.replace('* %s' % element,'',1)
        return (reactant,product,parameters,rate)
        
    def __getRawCompartments(self,compartment):
        name = compartment.getName()
        size = compartment.getSize()
        return name,3,size
    
    def getCompartments(self):
        for index,compartment in enumerate(self.model.getListOfCompartments()):
            self.__getRawCompartments(compartment)
            
    def getReactions(self,translator=[]):
        rules = []
        parameters = []
        functions = []
        functionTitle = 'functionRate'
        for index,reaction in enumerate(self.model.getListOfReactions()):
            rawRules =  self.__getRawRules(reaction)
            #print rawRules
            functionName = '%s%d()' % (functionTitle,index)
            rules.append(writer.bnglReaction(rawRules[0],rawRules[1],functionName,translator))
            if len(rawRules[2]) >0:
                parameters.append('%s %f' % (rawRules[2][0][0],rawRules[2][0][1]))
            functions.append(writer.bnglFunction(rawRules[3],functionName))
            
        return parameters, rules,functions
            
    def getParameters(self):
        return ['%s %f' %(parameter.getId(),parameter.getValue()) for parameter in self.model.getListOfParameters()]
    
        
    def getSpecies(self,translator = []):
    
        moleculesText  = []
        speciesText = [] 
        observablesText = []
        
        for species in self.model.getListOfSpecies():
            rawSpecies = self.getRawSpecies(species)
            if(rawSpecies[0] in translator):
                if len(translator[rawSpecies[0]][0])==1:
                    moleculesText.append(writer.printTranslate(rawSpecies[0],translator))
            else:
                moleculesText.append(rawSpecies[0] + '()')
            temp = '$' if rawSpecies[2] != 0 else ''
            speciesText.append(temp + '%s %f' % (writer.printTranslate(rawSpecies[0],translator),rawSpecies[1]))
            observablesText.append('Species %s %s' % (rawSpecies[0], writer.printTranslate(rawSpecies[0],translator)))
            
        return moleculesText,speciesText,observablesText
    
    def getSpeciesAnnotation(self):
        speciesAnnotation = {}
        
        for species in self.model.getListOfSpecies():
            rawSpecies = self.getRawSpecies(species)
            annotationXML = species.getAnnotation()
            lista = CVTermList()
            RDFAnnotationParser.parseRDFAnnotation(annotationXML,lista)
            if lista.getSize() == 0:
                speciesAnnotation[rawSpecies[0]] =  None
            else:
                speciesAnnotation[rawSpecies[0]] = lista.get(0).getResources()
        return speciesAnnotation
        
    def getSpeciesInfo(self,name):
        return self.getRawSpecies(self.model.getSpecies(name))
        

def main():
    
    parser = OptionParser()
    parser.add_option("-i","--input",dest="input",
        default='XMLExamples/curated/BIOMD0000000272.xml',type="string",
        help="The input SBML file in xml format. Default = 'input.xml'",metavar="FILE")
    parser.add_option("-o","--output",dest="output",
        default='output.bngl',type="string",
        help="the output file where we will store our matrix. Default = output.bngl",metavar="FILE")
          
    (options, args) = parser.parse_args()
    reader = SBMLReader()
    document = reader.readSBMLFromFile(options.input)
    print options.input
    parser =SBML2BNGL(document.getModel())
    rawDatabase = {('EpoR',):(['r','U','I'],),('SAv',):(['l'],)}
    translator = m2c.transformMolecules(parser,rawDatabase)
    print translator
    param2 = parser.getParameters()
    param,rules,functions = parser.getReactions(translator)
    parser.getCompartments()
    
    molecules,species,observables = parser.getSpecies(translator)
    
    param += param2
    print rules
         
    writer.finalText(param,molecules,species,observables,rules,functions,options.output)
        
if __name__ == "__main__":
    main()
