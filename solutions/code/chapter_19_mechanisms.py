"""Separate answer: no imports of project or learner code."""


def locate_span(blocks, start, end):
    limit=0
    for item in blocks:
        left,right=item['start'],item['end']
        if type(left) is not int or type(right) is not int or left<limit or left>=right:
            raise ValueError('Invalid block map')
        limit=right
    if type(start) is not int or type(end) is not int or start<0 or end>limit or start>=end:
        raise ValueError('Invalid span')
    answer=[]
    for item in blocks:
        left=max(start,item['start'])
        right=min(end,item['end'])
        if left<right:
            answer.append({'block_id':item['block_id'],'canonical_overlap':[left,right],
                           'locator':item['locator']})
    return answer
