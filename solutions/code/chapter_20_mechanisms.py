"""Independent answer; no project or learner imports."""
import re


def word_windows(text,size,overlap=0):
    if type(size)!=int or type(overlap)!=int or size<=0 or overlap<0 or overlap>=size:
        raise ValueError('Invalid window settings')
    spans=[(m.start(),m.end()) for m in re.finditer(r'\S+',text)]
    answer=[];first=0
    while first<len(spans):
        last=min(first+size,len(spans))
        answer.append((spans[first][0],spans[last-1][1]))
        if last==len(spans):return answer
        first+=size-overlap
    return answer
