import re
class Sym(str): pass
class Raw(str): pass
TOK=re.compile(r'\s*(?:(\()|(\))|("(?:[^"\\]|\\.)*")|([^\s()"]+))')
def parse(text):
    stack=[[]];pos=0;n=len(text)
    while True:
        m=TOK.match(text,pos)
        if not m: break
        pos=m.end()
        o,c,s,a=m.groups()
        if o: stack.append([])
        elif c: x=stack.pop(); stack[-1].append(x)
        elif s is not None: stack[-1].append(Raw(s[1:-1]))
        elif a is not None: stack[-1].append(Sym(a))
    return stack[0][0]
def q(s): return '"'+str(s).replace('\\','\\\\').replace('"','\\"')+'"'
def dump(x,ind=0):
    if isinstance(x,list):
        if all(not isinstance(i,list) for i in x):
            return '('+' '.join(dump(i) for i in x)+')'
        out='('+' '.join(dump(i) for i in x if not isinstance(i,list))
        # keep original order
        parts=[];head=True;s='('
        first=[]
        for i in x:
            if isinstance(i,list): parts.append('\n'+'\t'*(ind+1)+dump(i,ind+1))
            else:
                parts.append((' ' if parts else '')+dump(i))
        return '('+''.join(parts)+'\n'+'\t'*ind+')'
    if isinstance(x,Sym): return str(x)
    if isinstance(x,Raw): return '"'+str(x)+'"'
    if isinstance(x,bool): return 'yes' if x else 'no'
    if isinstance(x,(int,float)): 
        if isinstance(x,float): 
            s=f"{x:.4f}".rstrip('0').rstrip('.'); return s if s not in ('-0','') else '0'
        return str(x)
    return q(x)
def find(x,key): 
    for i in x:
        if isinstance(i,list) and i and i[0]==key: return i
def findall(x,key): return [i for i in x if isinstance(i,list) and i and i[0]==key]
