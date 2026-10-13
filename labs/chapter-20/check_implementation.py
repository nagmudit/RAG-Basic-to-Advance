import argparse
import importlib.util
from pathlib import Path


def check(path):
    spec=importlib.util.spec_from_file_location('attempt',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    text=' A  BB\nCCC D E '
    assert m.word_windows(text,3,1)==[(1,10),(7,14)]
    assert m.word_windows(text,2,0)==[(1,6),(7,12),(13,14)]
    assert m.word_windows('x y',10,3)==[(0,3)]
    assert m.word_windows(' \n\t',3,1)==[]
    for size,overlap in [(0,0),(3,3),(3,-1),(True,0),(2,False),(2.5,0)]:
        try:m.word_windows(text,size,overlap)
        except ValueError:pass
        else:raise AssertionError('Invalid window settings accepted')
    print('Independent Chapter20 boundary fixtures passed')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--implementation',default=str(Path(__file__).with_name('implement.py')))
    check(p.parse_args().implementation)
