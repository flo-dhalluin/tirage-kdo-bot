
import json
import sys

if __name__=="__main__":
    with open("data.json") as jf:
        data = json.loads(jf.read())
    
    with open(sys.argv[1]) as jf:
        former_results = json.loads(jf.read())

    
    for person in data :
        former = former_results[person["nom"]]
        person["blacklist"] = [person["blacklist"][0]] + former


    print(json.dumps(data))