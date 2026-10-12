import argparse
import importlib.util
from pathlib import Path


def check(path):
    spec=importlib.util.spec_from_file_location('attempt',path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    blocks=[{'block_id':'a','start':0,'end':3,'locator':{'page':1}},
            {'block_id':'b','start':5,'end':9,'locator':{'page':2}}]
    assert module.locate_span(blocks,2,7)==[
        {'block_id':'a','canonical_overlap':[2,3],'locator':{'page':1}},
        {'block_id':'b','canonical_overlap':[5,7],'locator':{'page':2}}]
    assert module.locate_span(blocks,3,5)==[]
    assert module.locate_span(blocks,5,9)==[
        {'block_id':'b','canonical_overlap':[5,9],'locator':{'page':2}}]
    for rows,start,end in [(blocks,-1,2),(blocks,1,1),(blocks,0,10),([],0,1),
        ([dict(blocks[0]),{**blocks[1],'start':2}],0,2)]:
        try:
            module.locate_span(rows,start,end)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid map/span accepted')
    print('Independent Chapter19 span fixtures passed')


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--implementation',default=str(Path(__file__).with_name('implement.py')))
    check(p.parse_args().implementation)
