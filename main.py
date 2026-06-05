from multiprocessing import Pool
from analyzer import analyze_file
import glob
import time

def main():

    print("="*40)
    print(" PARALLEL FILE ANALYZER ")
    print("="*40)

    files = glob.glob("data/*.txt")

    start = time.time()

    with Pool(processes=4) as pool:
        results = pool.map(analyze_file, files)

    for r in results:
        print("\n----------------------")
        print("File :", r["file"])
        print("Lines :", r["lines"])
        print("Words :", r["words"])
        print("Characters :", r["characters"])
        print("Most Frequent :", r["most_common"])

    end = time.time()

    print("\n======================")
    print("Execution Time :", round(end-start,3),"second")

if __name__ == "__main__":
    main()