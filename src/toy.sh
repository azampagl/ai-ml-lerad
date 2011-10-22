python lerad.py -e learn -a "../data/toy-attr.txt" -t "../data/toy-train.txt" -m "../results/toy-model.dat" -o "../results/toy-model.txt" -S 6 -L 10 -M 5 -P .1
python lerad.py -e predict -a "../data/toy-attr.txt" -t "../data/toy-test.txt" -m "../results/toy-model.dat" -o "../results/toy-results.txt" -T 0 -N toy -V yes
