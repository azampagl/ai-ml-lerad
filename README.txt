Learning Rules for Anomaly Detection of Hostile Network Traffic
Matthew V. Mahoney and Philip K. Chan
Department of Computer Sciences
Florida Institute of Technology
Melbourne, FL 32901
{mmahoney,pkc}@cs.fit.edu
@see http://www.cs.fit.edu/~pkc/papers/icdm03.pdf

The script (src/lerad.py) handles two phases, learning and prediction, which are described in more detail below.


============================================
Arguments for python ripperk.py
============================================

	The following parameters are required in all phases:

-e: the execution method (learn|predict)
-a: the attribute file location.
-t: the training/testing file location.
-m: the model file (machine readable results).
-o: the output file (human readable results).

	The following arguments are required during the 'learn' phase:

-L: the number of pairs of examples for generating candidate rules.
-M: the maximum number of rules per pair of examples.
-S: number of examples in the sample set.
-P: the number of examples in the validation set as a percentage.

	The following arguments are required during the 'predict' phase:

-T: the threshold.
-N: the attribute that is "normal".
-V: the value of the attribute that is "normal".


============================================
Learning
============================================

	The learning part of the script reads in training cases and builds a rule model.

	It is crucial that "learn" is passed as the -e parameter (-e learn)!  The script also requires the attribute file (-a), and the training file (-t).  Addition parameters required are: the number of pairs of examples for generating candidate rules (L); the maximum number of rules per pair of examples (M); number of examples in the sample set (S); the number of examples in the validation set as a percentage (P).

	Once the rule model is built, the script will output a machine-readable data model file (-m) and a human-readable text file (-o).  The machine-readable file will be used during classification.  The human-readable file will contain an IF ... THEN ... ELSE structure with primitive equalities so that the user can easily read the rules.

======================
	Usage
======================

	The following are some example use cases.

> python lerad.py -e learn -a "../data/toy-attr.txt" -t "../data/toy-train.txt" -m "../results/toy-model.dat" -o "../results/toy-model.txt" -S 6 -L 10 -M 5 -P .1

> python lerad.py -e learn -a "../data/ids-attr.txt" -t "../data/ids-train.txt" -m "../results/ids-model.dat" -o "../results/ids-model.txt" -S 100 -L 1000 -M 4 -P .1


============================================
Predict
============================================

	The prediction part of the script reads in test cases and trys to accurately predict them based on the rule model learned in the learning phase.

	It is crucial that "classify" is passed as the -e parameter (-e predict)!  The script also requires the attribute file (-a), the testing file (-t), and the machine-readable data model file created during the learn phase (-m).  The following parameters are also requred: the score threshold (T); the attribute that is "normal" (N); the value of the attribute that is "normal" (V).

	Once the test cases are analyzed, the results will be put into a human-readable text file (-o).

======================
	Usage
======================

	The following are some example use cases.

> python lerad.py -e predict -a "../data/toy-attr.txt" -t "../data/toy-test.txt" -m "../results/toy-model.dat" -o "../results/toy-results.txt" -T 0 -N toy -V yes

> python lerad.py -e predict -a "../data/ids-attr.txt" -t "../data/ids-test.txt" -m "../results/ids-model.dat" -o "../results/ids-results.txt" -T 1 -N class -V normal
