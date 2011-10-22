python lerad.py -e learn -a "../data/iris-attr.txt" -t "../data/iris-train.txt" -m "../results/iris-model.dat" -o "../results/iris-model.txt" -S 30 -L 20 -M 10 -P .10
python lerad.py -e predict -a "../data/iris-attr.txt" -t "../data/iris-test.txt" -m "../results/iris-model.dat" -o "../results/iris-results.txt" -T 0 -N class -V Iris-setosa
