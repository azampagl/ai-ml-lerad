python lerad.py -e learn -a "../data/ids-attr.txt" -t "../data/ids-train.txt" -m "../results/ids-model.dat" -o "../results/ids-model.txt" -S 100 -L 1000 -M 4 -P .10
python lerad.py -e predict -a "../data/ids-attr.txt" -t "../data/ids-test.txt" -m "../results/ids-model.dat" -o "../results/ids-results.txt" -T 1 -N class -V normal
