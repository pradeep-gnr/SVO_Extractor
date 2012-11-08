"""
A Jython Interface to Stanford Parser for Extracting Subject-Verb-Object Relationships
"""
import sys
import os
import pdb

from java.io import CharArrayReader
assert os.getenv("STANFORD_PARSER_HOME")!=None

sys.path.append(os.getenv("STANFORD_PARSER_HOME")+os.sep+"stanford-parser.jar")

from edu.stanford.nlp import *

class SVO(object):
    """
    Class Methods to Extract Subject Verb Object Tuples from a Sentence
    """
    def __init__(self):
        """
        Initialize the SVO Methods 
        """
        self.parser = parser.lexparser.LexicalizedParser.loadModel()    
        self.tlp = trees.PennTreebankLanguagePack()
        self.parser.setOptionFlags(["-maxLength", "80", "-retainTmpSubcategories"])
        self.noun_types = ["NN", "NNP", "NNPS","NNS","PRP"]
        self.verb_types = ["VB","VBD","VBG","VBN", "VBP", "VBZ"]
        self.adjective_types = ["JJ","JJR"]
        self.pred_verb_phrase_siblings = None

    def get_attributes(self,node,parent_node, parent_node_siblings):
        """
        returns the Attributes for a Node
        """

    def get_subject(self,sub_tree):
        """
        Returns the Subject and all attributes for a subject, sub_tree is a Noun Phrase
        """

        sub_nodes = []      
        sub_nodes = sub_tree.subTreeList()
        sub_nodes = [each for each in sub_nodes if each.isPreTerminal()]
        subject = None

        for each in sub_nodes:
            if each.value() in self.noun_types:
                subject = each.getChildrenAsList()[0].value()        
                break
        
        return {'subject':subject, 'attributes' : None}

    def get_object(self,sub_tree):        
        """
        Returns an Object with all attributes of an object
        """        
        siblings = self.pred_verb_phrase_siblings
        Object = None
        for each_tree in siblings:
            if each_tree.value() in ["NP","PP"]:
                sub_nodes = each_tree.subTreeList()
                sub_nodes = [each for each in sub_nodes if each.isPreTerminal()]
                for each in sub_nodes:
                    if each.value() in self.noun_types:
                        Object = each.getChildrenAsList()[0].value()        
                        break
                break
            else:
                sub_nodes = each_tree.subTreeList()
                sub_nodes = [each for each in sub_nodes if each.isPreTerminal()]
                for each in sub_nodes:
                    if each.value() in self.adjective_types:
                        Object = each.getChildrenAsList()[0].value()        
                        break                        
                # Get first noun in the tree                             
        self.pred_verb_phrase_siblings = None
        return {'object':Object, 'attributes' : None}        

    def get_predicate(self, sub_tree):
        """
        Returns the Verb along with its attributes, Also returns a Verb Phrase
        """        
        sub_nodes = []      
        sub_nodes = sub_tree.subTreeList()
        sub_nodes = [each for each in sub_nodes if each.isPreTerminal()]        
        predicate = None
        pred_verb_phrase_siblings = []

        for each in sub_nodes:
            if each.value() in self.verb_types:
                sub_tree = each
                predicate = each.getChildrenAsList()[0].value() 

        if predicate:        
            pred_verb_phrase_siblings = sub_tree.siblings(sub_tree.parent(self.tree_root))
            pred_verb_phrase_siblings = [each for each in pred_verb_phrase_siblings if each.value() in ["NP","PP","ADJP"]]        
            self.pred_verb_phrase_siblings = pred_verb_phrase_siblings
        return {'predicate':predicate, 'attributes':None}                        
        
    def process_parse_tree(self,parse_tree):
        """
        Returns the Subject-Verb-Object Representation of a Parse Tree.
        Can Vary depending on number of 'sub-sentences' in a Parse Tree
        """              
        self.tree_root = parse_tree
        # Step 1 - Extract all the parse trees that start with 'S'        
        candidate_trees = parse_tree.subTreeList()
        svo_list = [] # A List of SVO pairs extracted
        output_list = []
        output_dict ={}
        i=0
        
        for each in candidate_trees:
            subject =None
            predicate = None
            Object = None            
            if each.value() in ["S", "SQ", "SBAR", "SBARQ", "SINV", "FRAG"]:
                children_list = each.getChildrenAsList()
                children_values = [each_child.value() for each_child in children_list]               
                children_dict = dict(zip(children_values,children_list))

                # Extract Subject, Verb-Phrase, Objects from Sentence sub-trees
                if children_dict.get("NP") is not None:
                    subject = self.get_subject(children_dict["NP"])

                if children_dict.get("VP") is not None:
                    # Extract Verb and Object
                    i+=1
                    """
                    if i==1:
                        pdb.set_trace()
                    """
                    predicate = self.get_predicate(children_dict["VP"])
                    Object = self.get_object(children_dict["VP"])

                if subject['subject'] and predicate['predicate'] and Object['object']:
                    output_dict['subject_info'] = subject
                    output_dict['predicate_info'] = predicate
                    output_dict['object_info'] = Object                                         
                    output_list.append(output_dict)

        return output_list
                
    def tree_print(self,parse_tree):
        """
        returns the Pretty PRinting version for Stanford Parse Tree
        """
        parse_tree.pennPrint()

    def get_parse_tree(self,sentence):
        """
        returns the Parse Tree of a Sample 
        """
        self.toke = self.tlp.getTokenizerFactory().getTokenizer(CharArrayReader(sentence));
        wordlist = self.toke.tokenize()
        parse_tree = self.parser.parseTree(wordlist)
        return parse_tree


if __name__=="__main__":
    svo = SVO()
    tree = svo.get_parse_tree("A rare black squirrel has become a regular visitor to a suburban garden")
    svo.tree_print(tree)
    val = svo.process_parse_tree(tree)
    print val
    svo.tree_print(tree)




