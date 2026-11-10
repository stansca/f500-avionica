import os,sys
sys.path.insert(0,os.path.dirname(__file__))
from sexp import *
STD="/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/"
JS=os.path.expanduser("~/Documents/KiCad/biblioteca-js/symbols/")
_cache={}
def load_lib(lib):
    if lib in _cache: return _cache[lib]
    syms={}
    paths=[]
    base=(JS if lib.startswith("JS_") else STD)+lib
    if os.path.isdir(base+".kicad_symdir"):
        paths=[os.path.join(base+".kicad_symdir",f) for f in os.listdir(base+".kicad_symdir")]
    else: paths=[base+".kicad_sym"]
    for p in paths:
        t=parse(open(p).read())
        for s in findall(t,'symbol'): syms[s[1]]=s
    _cache[lib]=syms; return syms
def get_symbol(libid):
    lib,name=libid.split(':')
    syms=load_lib(lib)
    s=syms[name]
    ext=find(s,'extends')
    if ext:
        parent=[*syms[ext[1]]]
        parent=[x for x in parent]
        # build merged: parent's graphics with child's properties
        import copy
        p=copy.deepcopy(parent); p[1]=name
        props={pr[1]:pr for pr in findall(s,'property')}
        p=[i for i in p if not (isinstance(i,list) and i and i[0]=='property')]
        idx=2
        newp=p[:2]+[i for i in s[2:] if isinstance(i,list) and i[0] not in ('extends','symbol')]+[i for i in p[2:]]
        # rename subunits
        for i in newp:
            if isinstance(i,list) and i and i[0]=='symbol':
                i[1]=i[1].replace(ext[1],name,1)
        # dedupe props: keep child's
        seen=set();out=[]
        for i in newp:
            if isinstance(i,list) and i[0]=='property':
                if i[1] in seen: continue
                seen.add(i[1])
            out.append(i)
        return out
    return s
def pins(sym):
    res=[]
    def walk(x,unit):
        for i in x:
            if isinstance(i,list) and i and i[0]=='symbol':
                u=int(i[1].rsplit('_',2)[-2]); walk(i,u)
            elif isinstance(i,list) and i and i[0]=='pin':
                at=find(i,'at'); num=find(i,'number')[1]; nm=find(i,'name')[1]
                res.append(dict(num=num,name=nm,x=float(at[1]),y=float(at[2]),ang=float(at[3]) if len(at)>3 else 0,unit=unit,type=i[1]))
    walk(sym,0); return res
if __name__=="__main__":
    for a in sys.argv[1:]:
        try:
            s=get_symbol(a); print("==",a, [(p['num'],p['name']) for p in pins(s)])
        except KeyError as e: print("MISSING",a,e)
