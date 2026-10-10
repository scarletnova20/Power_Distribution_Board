import re, json

class Atom(str): pass

def parse(text):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|[^\s()]+|[()]', text)
    stack=[]; root=None
    for t in tokens:
        if t=='(':
            a=[]
            if stack: stack[-1].append(a)
            stack.append(a)
        elif t==')': root=stack.pop()
        else: stack[-1].append(json.loads(t) if t.startswith('"') else Atom(t))
    return root

def dump(x, level=0):
    if isinstance(x,Atom): return str(x)
    if isinstance(x,str): return json.dumps(x,ensure_ascii=False)
    if not isinstance(x,list): return str(x)
    if not any(isinstance(a,list) for a in x): return '('+' '.join(dump(a) for a in x)+')'
    out='('; first=True
    for a in x:
        if isinstance(a,list): out+='\n'+'\t'*(level+1)+dump(a,level+1)
        else: out+=('' if first else ' ')+dump(a)
        first=False
    return out+'\n'+'\t'*level+')'

def children(n,key): return [v for v in n if isinstance(v,list) and v and v[0]==key]
def one(n,key): return next((v for v in children(n,key)),None)
def prop(n,key): return next((v for v in children(n,'property') if v[1]==key),None)
