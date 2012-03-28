import re
import string
blacklist = ['the', 'I', 'a', 'it', 'myself']
punc = [',',';', '/','(',')',':'] 

def clean(chunk_lst):
    #print chunk_lst
    cleaned = []
    for chunk in chunk_lst:
        cleaned.append(remove_punctuation(chunk))
    return cleaned

def remove_punctuation(s):
    exclude = set(string.punctuation)
    exclude.remove('\'')
    s_lst = list(s)
    for x in exclude:
        s_lst = [" " if z==x else z for z in s_lst]
    s = "".join(s_lst)
    return s
