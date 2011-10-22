"""
Generates the reports data.

@author Aaron Zampaglione <azampagl@my.fit.edu>
@course CSE 5800 Advanced Topics in CS: Learning/Mining and the Internet, Fall 2011
@project Proj 02, LERAD
"""
import commands
import random

random.seed(23)

def main():
    """Main execution method."""
    create_attack()
    robust()

def create_attack():
    
    f1 = open("../data/ids-train.txt", 'r')
    f2 = open("../data/ids-attack.txt", 'r')
    
    train = []
    for line in f1:
        train.append(line)
    
    attacks = []
    for line in f2:
        attacks.append(line)
    
    f1.close()
    f2.close()
    
    start = 0.0
    stop = 0.1
    inc = 0.01
    i = start
    while i <= stop:
        l = int(len(attacks) * i)
        
        new_train = list(train)
        while len(new_train) < len(train) + l:
            new_train.insert(random.randint(0, len(new_train) - 1), attacks[random.randint(0, len(attacks) - 1)])
        
        out = open("../data/robust/train-" + str(int(i * 100)) + ".txt", 'w')
        for item in new_train:
            out.write(item)
        out.close()
        i += inc

def robust():
    d = "ids"
    n = "class"
    v = "normal"
    s = 100
    l = 1000
    m = 4
    p = .1
    
    attr = "../data/" + d + "-attr.txt"
    
    for i in range(11):
        
        train = "../data/robust/train-" + str(i) + ".txt"
        model = "../results/robust/model-" + str(i) + ".dat"
        output = "../results/robust/model-" + str(i) + ".txt"
        
        cmd = "python lerad.py" + \
              " -e learn " + \
              " -a " + attr + \
              " -t " + train + \
              " -m " + model + \
              " -o " + output + \
              " -S " + str(s) + \
              " -L " + str(l) + \
              " -M " + str(m) + \
              " -P " + str(p)
              
        commands.getstatusoutput(cmd)
    
        responses = []
    
        inc = 100
        start = 0
        stop = 10000
        for j in range(start, stop, inc):
        
            test = "../data/" + d + "-test.txt"
            output = "../results/robust/results-" + str(i) + "-" + str(j) + ".txt"
        
            cmd = "python lerad.py" + \
                  " -e predict " + \
                  " -a " + attr + \
                  " -t " + test + \
                  " -m " + model + \
                  " -o " + output + \
                  " -T " + str(j) + \
                  " -N " + n + \
                  " -V " + v
        
            _, response = commands.getstatusoutput(cmd)
        
            response = str(i) + "\t" + str(j) + "\t" + response
            response = response.split("\t")
        
            if responses:
                last_response = responses.pop()
                responses.append(last_response)
            else:
                last_response = [None]
        
            if response[2:] != last_response[2:]:
                #print(response)
                
                #print(response)
                #print(last_response)
                if float(response[-1]) == 0.0:
                    if float(last_response[-1]) != 0.0:
                        rise = (float(last_response[-2]) - float(response[-2])) / 100
                        run = float(last_response[-1]) / 100
                        slope = rise / run
                        # AUC = slope * 1 + detection rate at first point
                        #print("slope: " + str(slope))
                        auc = (float(response[-2]) / 100) + (slope * .1)
                    else:
                        auc = float(last_response[-2]) / 100
                    
                    print(str(i) + "\t" + str(auc))
                    
                    break
                responses.append(response)
        
        #for response in responses:      
        #    print("\t".join(response))

def sens():
    
    d = "ids"
    n = "class"
    v = "normal"
    
    vars = {
            's': {'start': 50,
                  'stop': 150,
                  'inc': 10,
                  'best': 50,
                  'curr': 50,
                  },
            'l': {'start': 100,
                  'stop': 1000,
                  'inc': 100,
                  'best': 100,
                  'curr': 100,
                  },
            'm': {'start': 1,
                  'stop': 10,
                  'inc': 1,
                  'best': 1,
                  'curr': 1,
                  },
            'p': {'start': 0.1,
                  'stop': 0.8,
                  'inc': 0.1,
                  'best': 0.1,
                  'curr': 0.1,
                  },
            }
    
    attr = "../data/" + d + "-attr.txt"
    train = "../data/" + d + "-train.txt"
    test = "../data/" + d + "-test.txt"
    model = "../results/" + d + "-model.dat"
    output = "../results/" + d + "-model.txt"

    for var, settings in vars.items():
        print(var)
        i = settings['start']
        best_auc = None
        while i < settings['stop']:
            
            vars[var]['curr'] = i
            
            model = "../results/sensitivity/" + var + "-" + str(i) + "-model.dat"
            output = "../results/sensitivity/" + var + "-" + str(i) + "-model.txt"
            
            cmd = "python lerad.py" + \
              " -e learn " + \
              " -a " + attr + \
              " -t " + train + \
              " -m " + model + \
              " -o " + output + \
              " -S " + str(vars['s']['curr']) + \
              " -L " + str(vars['l']['curr']) + \
              " -M " + str(vars['m']['curr']) + \
              " -P " + str(vars['p']['curr'])
            
            commands.getstatusoutput(cmd)
            responses = []
            
            
            for j in range(0, 10000, 100):
                
                #if len(responses) > 2:
                #    break
                
                output = "../results/sensitivity/" + var + "-" + str(i) + "-" + str(j) + "-results.txt"
                
                cmd = "python lerad.py" + \
                  " -e predict " + \
                  " -a " + attr + \
                  " -t " + test + \
                  " -m " + model + \
                  " -o " + output + \
                  " -T " + str(j) + \
                  " -N " + n + \
                  " -V " + v
        
                _, response = commands.getstatusoutput(cmd)
        
                response = str(i) + "\t" +str(j) + "\t" + response
                response = response.split("\t")
                
                if responses:
                    last_response = responses.pop()
                    responses.append(last_response)
                else:
                    last_response = [None]
                
                if response[2:] != last_response[2:]:
                    #print(response)
                    if float(response[-1]) == 0.0:
                        if float(last_response[-1]) != 0.0:
                            rise = (float(last_response[-2]) - float(response[-2])) / 100
                            run = float(last_response[-1]) / 100
                            slope = rise / run
                            # AUC = slope * 1 + detection rate at first point
                            #print("slope: " + str(slope))
                            auc = (float(response[-2]) / 100) + (slope * .1)
                        else:
                            auc = float(last_response[-2]) / 100
                        
                        if auc > best_auc:
                            best_auc = auc
                            vars[var]['best'] = i
                        
                        print(str(response[0]) + "\t" + str(auc))
                        break
                    responses.append(response)
                 
            i += settings['inc']
        vars[var]['curr'] = vars[var]['best']
        print("**" + str(vars[var]['curr']) + "**")

def auc():
    #d = "toy"
    #n = "toy"
    #v = "yes"
    #s = 6
    #l = 10
    #m = 5
    
    #d = "ids"
    #n = "class"
    #v = "normal"
    #s = 100
    #l = 1000
    #m = 4
    
    d = "iris"
    n = "class"
    v = "Iris-setosa"
    s = 30
    l = 50
    m = 5
    
    attr = "../data/" + d + "-attr.txt"
    train = "../data/" + d + "-train.txt"
    model = "../results/" + d + "-model.dat"
    output = "../results/" + d + "-model.txt"
    
    cmd = "python lerad.py" + \
          " -e learn " + \
          " -a " + attr + \
          " -t " + train + \
          " -m " + model + \
          " -o " + output + \
          " -S " + str(s) + \
          " -L " + str(l) + \
          " -M " + str(m) + \
          " -P .1"
              
    commands.getstatusoutput(cmd)
    
    responses = []

    inc = 1
    start = 0
    stop = 1000
    for i in range(start, stop, inc):
        
        test = "../data/" + d + "-test.txt"
        output = "../results/" + d + "-results.txt"
        
        cmd = "python lerad.py" + \
              " -e predict " + \
              " -a " + attr + \
              " -t " + test + \
              " -m " + model + \
              " -o " + output + \
              " -T " + str(i) + \
              " -N " + n + \
              " -V " + v
        
        _, response = commands.getstatusoutput(cmd)
        
        response = str(i) + "\t" + response
        response = response.split("\t")
        
        if responses:
            last_response = responses.pop()
            responses.append(last_response)
        else:
            last_response = [None]
        
        if response[1:] != last_response[1:]:
            print(response)
            responses.append(response)
    
    for response in responses:      
        print("\t".join(response))

"""Main execution."""
if __name__ == "__main__":
    main()