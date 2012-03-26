import re
import string
blacklist = ['the', 'I', 'a', 'it', 'myself']
punc = [',',';', '/','(',')',':'] 

def clean(chunk_lst):
    cleaned = []
    for chunk in chunk_lst:
        for p in punc:
            chunk = chunk.replace(p, '') 
        print chunk, '->',
        split_chunk = chunk.split()
        for bl in blacklist:
            if bl in split_chunk:
                split_chunk.remove(bl)
        joined_chunk =  " ".join(split_chunk)
        if joined_chunk:
            cleaned.append(joined_chunk)
        print joined_chunk
    return cleaned

def remove_punctuation(s):
    exclude = set(string.punctuation)
    s = ''.join(ch for ch in s if ch not in exclude)
    return s
