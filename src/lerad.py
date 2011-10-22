"""
Python implementation of the the LERAD algorithm.

Learning Rules for Anomaly Detection of Hostile Network Traffic
Matthew V. Mahoney and Philip K. Chan
Department of Computer Sciences
Florida Institute of Technology
Melbourne, FL 32901
{mmahoney,pkc}@cs.fit.edu
@see http://www.cs.fit.edu/~pkc/papers/icdm03.pdf

The style guide follows the strict python PEP 8 guidelines.
@see http://www.python.org/dev/peps/pep-0008/

@author Aaron Zampaglione <azampagl@my.fit.edu>
@course CSE 5800 Advanced Topics in CS: Learning/Mining and the Internet, Fall 2011
@project Proj 02, LERAD
"""
import getopt
import random
import sys

#
# Set the random seed to keep the numbers the same per trial.
#
random.seed(23)

#
# Global META variable.
#
meta = {
        # The options dictionary contains all the user defined arguments.
        'opts': {},
        # The attribute dictionary contains all the attributes found in the
        #  attribute file.
        'attrs': {},
        }

#
# Classes
#

class Rule(object):
    """
    Rule object contains a consequent and an antecedent.
    """
    
    # Antecedent
    antecedent = {}
    
    # Consequent
    consequent = (0, [])
    
    # Number of cases this rule binds to
    bindings = 0
    
    def __init__(self, rule=None):
        """
        Rule init
        
        Key arguments:
        rule -- [optional] rule to copy from.
        """
        if rule == None:
            return
        
        # Copy the previous rule if provided.
        if isinstance(rule, Rule):
            self.antecedent = dict(rule.antecedent)
            self.consequent = rule.consequent
            return
        
        # Builds a rule from a dictionary.
        if isinstance(rule, dict):
            self.antecedent = rule['antecedent']
            self.consequent = rule['consequent']
            self.bindings = rule['bindings']
            return
    
    def __str__(self):
        """
        Prints rule.
        """
        output = "IF "
        
        for attr, value in self.antecedent.items():
            output += meta['attrs'][attr] + " = " + value + " AND "
        
        output = output[:-5] + " THEN "
        output += meta['attrs'][self.consequent[0]] + " = " + ",".join(self.consequent[1])

        return output
    
    def binds(self, case):
        """
        Determines if a rule binds to a case/rule.
        
        Key arguments:
        case -- the case to check.
        """
        for attr, value in self.antecedent.items():
            if not attr in case:
                return False
            
            if case[attr] != value:
                return False
        
        return True
    
    def save(self):
        """
        Returns a str that can be saved to a file.
        """
        rule = {}
        rule['antecedent'] = self.antecedent
        rule['consequent'] = self.consequent
        rule['bindings'] = self.bindings
        return str(rule)
    
    def score(self):
        """
        Calculates the n/r score.
        """
        return self.bindings / float(len(self.consequent[1]))
#
# Methods
#

def attrs(f):
    """
    Parses an attribute file into an attribute dictionary.
    
    Each key in the dictionary (attribute index) contains the
    attribute name and number possible values for that attribute.
    
    e.g.:
    
        attrs[0] = ('duration', 6)
        ...
    
    Key arguments:
    f -- the attribute file handle.
    """
    ret = {}
    
    i = 0
    for line in f:
        # The first item is the attribute name, the rest are possible values.
        split = line[:-1].split(" ")
        ret[i] = split[0]
        i += 1
    
    return ret

def data(f):
    """
    Parses a training/testing file and returns the cases.
    
    e.g.:
    
        cases = [{
                    'duration': 'zero',
                    'protocol_type': 'tcp'
                },
                ...
               ]
    
    Key arguments:
    f  -- the file handle.
    """
    # Cases list.
    ret = []
    
    for line in f:
        case = {}
        i = 0
        split = line[:-1].split(" ")
        for value in split:
            # Set the attribute and the value.
            case[i] = value
            
            i += 1
        
        # Append the case.
        ret.append(case)
    
    # Return the cases.
    return ret

def learn(cases):
    """
    Learns rules based on a given set of training cases.
    
    Key arguments:
    cases -- the training cases.
    """
    # Number of validation cases.
    num = int(meta['opts']['P'] * len(cases))
    
    # Can't have a training set of 0.
    if num == len(cases):
        raise "Training set to small or validation percentage to high."
    
    # Make training and validation set.
    train = cases[num:]
    validate = cases[:num]
    
    if meta['opts']['S'] > len(train):
        raise "Desired sample size exceeds training cases provided."
    
    # Subset is a random sample
    subset = sample_subset(train, meta['opts']['S'])
    
    rules = []
    
    # Linear list of the samples we're going to compare.
    pairs = sample_pairs(subset, meta['opts']['L'] * 2)
    
    for pair in pairs:
        for rule in generate_rules(pair[0], pair[1]):
            # For each rule, if the rule binds to to a case
            #  we update the consequents if necessary (r) and the
            #  the number of bindings (n).
            for case in subset:
                if rule.binds(case):
                    # Increase bindings.
                    rule.bindings += 1
                    # Check if we need to update consequents.
                    if not case[rule.consequent[0]] in rule.consequent[1]:
                        rule.consequent[1].append(case[rule.consequent[0]])
                    
            rules.append(rule)
    
    # "Coverage test".
    remove_rules(rules)
    
    # Training pass 2, update the consequents on the remaining
    #  samples in the training set.
    remaining = []
    for case in train:
        if not case in subset:
            remaining.append(case)
    
    for rule in rules:
        for case in remaining:
            if rule.binds(case):
                # Increase bindings.
                rule.bindings += 1
                # Check if we need to update consequents.
                if not case[rule.consequent[0]] in rule.consequent[1]:
                    rule.consequent[1].append(case[rule.consequent[0]])
    
    # "Validation".
    validate_rules(validate, rules)
    
    # Print to files.
    f1 = open(meta['opts']['m'], 'w')
    f2 = open(meta['opts']['o'], 'w')
    for rule in rules:
        f1.write(rule.save() + "\n")
        f2.write(str(rule) + "\n")
    f1.close()
    f2.close()

def generate_rules(case1, case2):
    """
    Generate rules on two cases.
    
    Key arguments:
    case1 -- the first case.
    case2 -- the second case.
    """
    attrs = []
    
    # Find common attributes.
    for attr1, value1 in case1.items():
        if attr1 in case2 and case2[attr1] == value1: 
            attrs.append(attr1)
    
    l = len(attrs)
    
    # Return empty set if no matching attributes.
    if l == 0:
        return attrs
    
    # List of rules.
    rules = []
    
    # Randomly arrange the attributes
    attrs = sample_subset(attrs, l)
        
    # Find a random attribute.
    attr = attrs.pop()
    l -= 1
    
    # Set the base for the following rules.
    rule = Rule()
    rule.consequent = (attr, [case1[attr]])
    
    # Make sure we cap at M rules.  We don't include the first attribute lost.
    #  that made the consequent because we're not doing wildcards.
    if l > meta['opts']['M']:
        l = meta['opts']['M']
    
    while l > 0:
        # Current rule is based on the last one.
        rule = Rule(rule)
        
        attr = attrs.pop()
        rule.antecedent[attr] = case1[attr]
        
        rules.append(rule)
        
        l -= 1
    
    return rules

def main():
    """Main execution method."""
    # Determine command line arguments
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "e:a:t:m:o:L:M:S:P:T:N:V:")
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    # Process each command line argument.
    for o, a in opts:
        meta['opts'][o[1]] = a
    
    # The following arguments are required in all cases.
    for opt in ['e', 'a', 't', 'm', 'o']:
        if not opt in meta['opts']:
            usage()
            sys.exit(2)
    
    # Create attribute set.
    f = open(meta['opts']['a'], 'r')
    meta['attrs'] = attrs(f)
    f.close()
    
    # Create cases set.
    f = open(meta['opts']['t'], 'r')
    cases = data(f)
    f.close()
    
    if meta['opts']['e'] == 'learn':
        # The following arguments are required in the learning phase.
        for opt in ['L', 'M', 'S', 'P']:
            if not opt in meta['opts']:
                usage()
                sys.exit(2)
        
        # Cast the options to integers.
        for opt in ['L', 'M', 'S']:
            meta['opts'][opt] = int(meta['opts'][opt])
        # Percentage should be a floating point (percentage).
        meta['opts']['P'] = float(meta['opts']['P'])
        
        # Learn on a sample size of S.
        learn(cases)
    elif meta['opts']['e'] == 'predict':
        # The following arguments are required in the learning case.
        for opt in ['T', 'N', 'V']:
            if not opt in meta['opts']:
                usage()
                sys.exit(2)
        
        # Cast to int.
        meta['opts']['T'] = float(meta['opts']['T'])
        
        # Load rules.
        rules = []
        f = open(meta['opts']['m'], 'r')
        for line in f:
            rules.append(Rule(eval(line)))
        f.close()
        
        predict(cases, rules)
    else:
        usage()
        sys.exit(2)

def predict(cases, rules):
    """
    Predicts each of the cases.
    
    Key arguments:
    cases -- the cases to look at.
    rules -- the rules to check against.
    """
    results = {'tp': 0,
               'tn': 0,
               'fp': 0,
               'fn': 0
               }
    
    # Reverse lookup the index for our key attribute.
    index = None
    for attr, value in meta['attrs'].items():
        if value == meta['opts']['N']:
            index = attr
    
    # Time dictionary.
    t = {}
    for rule in rules:
        t[rule] = 0
    
    # Calculate the score for each case.
    flagged = 0
    unclassified = 0
    
    i = 0
    for case in cases:
        i += 1
        score = 0.0
        flag = False
        classified = False
        for rule in rules:
            if rule.binds(case):
                classified = True
                if not case[rule.consequent[0]] in rule.consequent[1]:
                    flag = True
                    score += (i - t[rule]) * rule.score()
                    t[rule] = i
        if flag:
            flagged += 1
        if not classified:
            unclassified += 1
        
        if score >= meta['opts']['T']:
            if case[index] != meta['opts']['V']:
                results['tp'] += 1
            else:
                results['fp'] += 1
        else:
            if case[index] == meta['opts']['V']:
                results['tn'] += 1
            else:
                results['fn'] += 1
    
    # Accuracy.
    ac = ((results['tp'] + results['tn']) / float(results['tp'] + results['tn'] + results['fp'] + results['fn'])) * 100
    # Detection rate.
    if results['tp'] != 0 or results['fn'] != 0:
        dr = (results['tp'] / float(results['tp'] + results['fn'])) * 100
    else:
        dr = "NaN"
    # False positives.
    if results['fp'] != 0 or results['tn'] != 0:
        fa = (results['fp'] / float(results['fp'] + results['tn'])) * 100
    else:
        fa = "NaN"
    
    output = ""
    output += "Flagged:\t\t\t" + str(flagged) + "\n"
    output += "Unclassified:\t\t\t" + str(unclassified) + "\n\n"
    output += "True Positives:\t\t\t" + str(results['tp']) + "\n"
    output += "True Negatives:\t\t\t" + str(results['tn']) + "\n"
    output += "False Positives:\t\t" + str(results['fp']) + "\n"
    output += "False Negatives:\t\t" + str(results['fn']) + "\n"
    output += "Total:\t\t\t\t" + str(len(cases)) + "\n\n"
    output += "Accuracy:\t\t\t" + str(ac) + "%\n"
    output += "Detection Rate:\t\t\t" + str(dr) + "%\n"
    output += "False Alarm Rate:\t\t" + str(fa) + "%\n"
    
    f = open(meta['opts']['o'], 'w')
    f.write(output)
    f.close()
    
    # Print detection rate and false alarm rate to screen for easy parsing later.
    print(str(ac) + " \t" + str(dr) + "\t" + str(fa))

def remove_rules(rules):
    """
    Removes redundant rules (coverage test).
    
    Key arguments:
    rules -- the rules to reduce.
    """
    # Sort in decreasing n/r.
    rules.sort(key=lambda x: x.score(), reverse=True)
    
    # Remove redundant rules.
    l = len(rules)
    i = 1
    while i < l:
        j = 0
        while j < i:
            if rules[j].binds(rules[i].antecedent):
                rules.pop(i)
                l = len(rules)
                j = 0
                if i >= l:
                    break
            else:
                j += 1
        i += 1

def sample_subset(cases, size):
    """
    Returns a random unique subset of (size) samples.
    
    Key arguments:
    cases -- the set of cases.
    size  -- the number of samples to return.
    """
    ret = []
    l = len(cases) - 1
    
    indices = []
    
    i = 0
    while i < size:
        index = random.randint(0, l)
        if not index in indices:
            indices.append(index)
            i += 1
    
    for index in indices:
        ret.append(cases[index])
    
    return ret

def sample_pairs(cases, size):
    """
    Returns (size) random pairs.
    
    Key arguments:
    cases -- the set of cases.
    size  -- the number of samples to return.
    """
    ret = []
    l = len(cases) - 1
    
    i = 0
    while i < size:
        index1 = random.randint(0, l)
        index2 = random.randint(0, l)
        
        # We don't want an instance to compare to itself.
        if index1 == index2:
            continue
        
        ret.append((cases[index1], cases[index2]))
        i += 1
    
    return ret

def usage():
    """Prints the usage of the program."""
    print("\n" + 
          "The following are arguments required:\n" + 
          "-e: the execution method (learn|predict)\n" + 
          "-a: the attribute file location.\n" + 
          "-t: the training/testing file location.\n" + 
          "-m: the model file (machine readable results).\n" + 
          "-o: the output file (human readable results).\n\n" + 
          "The following arguments are required during the 'learn' phase:\n"
          "-L: the number of pairs of examples for generating candidate rules.\n" +
          "-M: the maximum number of rules per pair of examples.\n" + 
          "-S: number of examples in the sample set.\n" +
          "-P: the number of examples in the validation set as a percentage.\n\n" + 
          "The following arguments are required during the 'predict' phase:\n" + 
          "-T: the threshold.\n" + 
          "-N: the attribute that is \"normal\".\n" +
          "-V: the value of the attribute that is \"normal\".\n" + 
          "\n" + 
          "Example Usage:\n" + 
          "python lerad.py -e learn -a \"../data/toy-attr.txt\"" + 
          " -t \"../data/toy-train.txt\" -m \"toy-model.dat\"" + 
          " -o \"toy-model.txt\" -S 8 -L 2 -M 3 -P .5" + 
          "\n" + 
          "python lerad.py -e predict -a \"../data/toy-attr.txt\"" + 
          " -t \"../data/toy-test.txt\" -m \"toy-model.dat\"" + 
          " -o \"test-results.txt\" -T 10.0 -N toy -V yes" + 
          "\n")

def validate_rules(cases, rules):
    """
    Validates (removes) rules against a validation set.
    
    Key arguments:
    cases -- the validation cases.
    rules -- the rules to reduce.
    """
    new_rules = []
    for rule in rules:
        found = True
        for case in cases:
            if rule.binds(case):
                if not case[rule.consequent[0]] in rule.consequent[1]:
                    found = False
                    break
        if found:
            new_rules.append(rule)
    
    rules = new_rules

"""Main execution."""
if __name__ == "__main__":
    main()