import csv
import sys
from collections import defaultdict

sys.path.append('.')

column = defaultdict(list)

file_path = "BusStopInfo.csv"

data = open(file_path)

rdr = csv.DictReader(data)
for row in rdr:
    if(row['모바일단축번호'] == '32350' and row['도시코드'] == '25'):
        print(row)