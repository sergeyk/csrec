import re

blacklist = ['the', 'I', 'a', 'it', 'myself',]
def clean(chunk_lst):
    cleaned = []
    for chunk in chunk_lst:
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
