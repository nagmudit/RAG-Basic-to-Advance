import importlib.util
import sys
from pathlib import Path


def check(path):
    spec=importlib.util.spec_from_file_location('learner23',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    local=frozenset({'lexical','dense'})
    fixtures=[('identifier',local,False,'en',('lexical','lexical','ready',False,None)),
              ('paraphrase',local,False,'en',('dense','dense','ready',False,None)),
              ('date',local,False,'en',('dense','dense','ready',False,None)),
              ('relationship',local,False,'en',('graph','lexical','partial',True,'evidence_only')),
              ('count',local,False,'en',('sql',None,'unsupported',False,'route_unavailable')),
              ('count',frozenset({'sql'}),False,'en',('sql','sql','ready',False,None)),
              ('paraphrase',frozenset({'lexical'}),False,'en',('dense','lexical','ready',True,'capability_fallback')),
              ('identifier',frozenset({'dense'}),False,'en',('lexical','dense','ready',True,'capability_fallback')),
              ('date',local,True,'es',('dense',None,'clarify',False,'ambiguous_intent')),
              ('identifier',local,False,'es',('lexical',None,'unsupported',False,'unsupported_language')),
              ('relationship',frozenset(),False,'en',('graph',None,'unsupported',False,'route_unavailable'))]
    keys=('primary','selected','outcome','fallback','reason')
    for kind,cap,amb,lang,expected in fixtures:
        got=module.route(kind,cap,amb,lang)
        assert set(got)==set(keys) and tuple(got[k] for k in keys)==expected,(kind,got,expected)
    for args in [('unknown',local),('date',{'dense'}),('date',frozenset({'magic'})),('date',local,1)]:
        try:module.route(*args)
        except ValueError:pass
        else:raise AssertionError('Invalid policy accepted')
    print('Fresh five-kind routing and fallback checks pass.')


if __name__=='__main__':check(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).with_name('implement.py'))
