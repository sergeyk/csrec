import _mysql as sql

if __name__=='__main__':
  db = sql.connect(db='csrec',user='sergeyk',unix_socket='/u/vis/x1/sergeyk/mysql/mysql.sock',host='orange4')