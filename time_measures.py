import pandas as pd
from aspbeef import main as beef
import argparse
import time
import tempfile
from itertools import product
from random import shuffle

def main():
    parser = argparse.ArgumentParser(description='Experimental ASP clustering tool')
    parser.add_argument('file', type=str, help="CSV File")
    parser.add_argument('target', type=str, help="Target Feature")
    parser.add_argument('k', type=int, help="K for KMeans")
    parser.add_argument('-i', '--iters', type=int, default=10, help="Number of time to perform each BEEF")
    args = parser.parse_args()

    data = pd.read_csv(args.file)
    data_no_target = data.drop(columns=[args.target])
    dicts = data_no_target.to_dict(orient='records')
    data_features = list(dicts[0].keys())
    
    attr_sizes = list(range(2,5))
    sample_sizes = [60, 90, 150]

    
    cases = product(attr_sizes, sample_sizes)

    with open("beeftimes.csv", "w") as outfile:
        outfile.write("sample_size,\tfeatures,\tfixed,\ttime\n")
        for attr,samp in cases:
            with tempfile.NamedTemporaryFile() as temp_file:
                sample = data.sample(samp)
                sample.to_csv(temp_file.name, index=False)
                beefargs = [temp_file.name, args.target, "-k", str(args.k), "-hm", "weak", "--approximate", "-f", str(attr)]

                exectime = 0
                for i in range(args.iters):
                    start = time.time()
                    beef(beefargs)
                    end = time.time()
                    exectime += end-start
                avg_exectime = exectime/args.iters
            
            outfile.write(f"{samp},\t{attr},\tfalse,\t{avg_exectime:.4}\n")
        
        for attr,samp in cases:
            with tempfile.NamedTemporaryFile() as temp_file:
                sample = data.sample(samp)
                sample.to_csv(temp_file.name, index=False)

                sel_attr = []
                rand_features = shuffle(data_features)
                sel_attr = rand_features[2:attr]

                beefargs = [temp_file.name, args.target, "-k", str(args.k), "-hm", "weak", "--approximate", "-f", str(attr), "-s"] + attr
                
                exectime = 0
                for i in range(args.iters):
                    start = time.time()
                    beef(beefargs)
                    end = time.time()
                    exectime += end-start
                avg_exectime = exectime/args.iters

            outfile.write(f"{samp},\t{len(attr)},\ttrue,\t{avg_exectime:.4}\n")




if __name__ == "__main__":
    main()