import csv
import cPickle
reader = csv.reader(open('1000_most_common', 'rb'))
common_lst = []
for row in reader:
    common_lst.append(row[0].lower())
cPickle.dump(common_lst, open('1000_most_common.pkl', 'wb'))
