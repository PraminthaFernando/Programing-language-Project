import sys
import re

PATTERNS = [
    (r'<ID>', r'[a-zA-Z]([a-zA-Z]|[0-9]|[_])*'),
    (r'<INT>', r'\d+'),
    (r'<STR>', r"''(\t|\n|\\|\\''|\(|\)|;|,|[a-zA-Z]|[0-9]|[+\-<>&.@/:=~|!#$%^_\[\]{}\"'?\s])*''"),
    (r'<OPERATOR>', r'[+\-*<>&.@/:=~|!#$%^_\[\]{}"\'?]+'),
    (r'<DELETE>', r'(\s+|ht|Eol|//(\'\'|\(|\)|;|,|\\|\s|ht|[a-zA-Z]|[0-9]|[+\-<>&.@/:=~|!#$%^_\[\]{}"\'?])*Eol)+'),
    (r'PUNCTION', r'[();,]')
]

KEYWORDS = ['let', 'where', 'aug', 'in', 'or', 'not', 'within', 'and', 'rec', 'gr', 'ge', 'ls', 'le', 'eq', 'ne']

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

class Tree:
    def __init__(self, root_value):
        self.root = TreeNode(root_value)

    def add_child_to_node(self, parent_node, child_value):
        new_child = TreeNode(child_value)
        parent_node.add_child(new_child)
        return new_child
    
    # def Root(self):
    #     return self.root.value

    def print_tree(self, node=None, level=0):
        if node is None:
            node = self.root
        print('.' * level + str(node.value))
        for child in node.children:
            self.print_tree(child, level + 1)

def tokenize(input_text):
    tokens = []
    while input_text:
        if input_text == "//":
            continue
        else:
            match = None
            for token_type, pattern in PATTERNS:
                match = re.match(pattern, input_text)
                if match:
                    token = (token_type, match.group(0))
                    if token_type != '<DELETE>':
                        tokens.append(token)
                    input_text = input_text[match.end():]
                    break
            if not match:
                raise ValueError('Invalid input: ' + input_text)
    return tokens

def parse(tokens):
    ASTree = Tree('E')
    parser = RPALParser(tokens, ASTree.root)
    result = parser.parse()
    standardize(ASTree.root)
    return result, ASTree

class RPALParser:
    def __init__(self, tokens, root):
        self.tokens = tokens
        self.current_index = 0
        self.current_token = self.tokens[self.current_index] if self.tokens else None
        self.root = root

    def parse(self):
        self.result = self.E(self.root)
        return self.result

    def match(self, expected_token):
        token = self.current_token[1]
        if token == expected_token or self.current_token[0] == expected_token:
            self.current_index += 1
            if self.current_index < len(self.tokens):
                self.current_token = self.tokens[self.current_index]
            else:
                self.current_token = None
            return True
        return False

    # Expressions
    def E(self, tree):
        if self.current_token == None:
            return True
        if self.current_token[1] == 'let':
            
            self.match('let')
            if tree.value == 'E':
                tree.value = 'let'
                res = self.D(tree)
                res = res and self.match('in')
                return res and self.E(tree)
            else:
                child = TreeNode('let')
                tree.children.append(child)
                res = self.D(child)
                res = res and self.match('in')
                return res and self.E(child)
            
        elif self.current_token[1] == 'fn':
            self.match('fn')
            if tree.value == 'E':
                tree.value = 'lambda'
                res = self.Vb(tree)
                while (self.current_token[0] == '<ID>') and (self.current_token[0] not in KEYWORDS) or (self.current_token[1] == '('):
                    res = res and self.Vb(tree)
                res = res and self.match('.')
                return res and self.E(tree)
            
            else:
                child = TreeNode('lambda')
                tree.children.append(child)
                res = self.Vb(child)
                while (self.current_token[0] == '<ID>') and (self.current_token[0] not in KEYWORDS) or (self.current_token[1] == '('):
                    res = res and self.Vb(child)
                res = res and self.match('.')
                return res and self.E(child)
            
        else:
            return self.Ew(tree)
        pass

    def Ew(self,tree):
        return self.T(tree) and self.Eb(tree)
    
    def Eb(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] == 'where':
            self.match('where')
            if tree.value == 'E':
                tree.value = 'where'
                return self.Dr(tree)
            
            else:
                child = TreeNode('where')
                child.children.append(tree.children[-1])
                tree.children[-1] = child
                return self.Dr(child)
            
            
        return True

    # Tuple Expressions
    def T(self,tree):
        return self.Ta(tree) and self.M(tree)
    
    def M(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] == ',':
            self.match(',')
            
            if tree.value == 'E':
                tree.value = 'tau'
                res = self.Ta(tree)
                while self.current_token[1] == ',':
                    self.match(',')
                    res = res and self.Ta(tree)
                return res
            
            else:
                child = TreeNode('tau')
                child.children.append(tree.children[-1])
                tree.children[-1] = child
                res = self.Ta(child)
                while self.current_token[1] == ',':
                    self.match(',')
                    res = res and self.Ta(child)
                return res
            
        return True

    def Ta(self,tree):
        return self.Tc(tree) and self.Tb(tree)
    
    def Tb(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] == 'aug':
            self.match('aug')
            if tree.value == 'E':
                tree.value = 'aug'
                return self.Ta(tree)
            
            else:
                child = TreeNode('aug')
                child.children.append(tree.children[-1])
                tree.children[-1] = child
                return self.Ta(child)
            
        return True

    def Tc(self,tree):
        return self.B(tree) and self.Td(tree)
    
    def Td(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] == '->':
            self.match('->')
            if tree.value == 'E':
                tree.value = '->'
                return self.Tc(tree) and self.match('|') and self.Tc(tree)
            
            else:
                child = TreeNode('->')
                child.children.append(tree.children[-1])
                tree.children[-1] = child
                return self.Tc(child) and self.match('|') and self.Tc(child)
            
        return True

    # Boolean Expressions
    def B(self,tree):
        return self.Bt(tree) and self.Ba(tree)
    
    def Ba(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] == 'or':
            self.match('or')
            child = TreeNode('or')
            child.children.append(tree.children[-1])
            tree.children[-1] = child
            return self.B(child)
            
        return True

    def Bt(self,tree):
        return self.Bs(tree) and self.K(tree)
    
    def K(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] == '&':
            self.match('&')
            child = TreeNode('&')
            child.children.append(tree.children[-1])
            tree.children[-1] = child
            return self.Bt(child)
            
        return True

    def Bs(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] == 'not':
            self.match('not')
            child = TreeNode('not')
            tree.children.append(child)
            return self.Bp(child)
            
        else:
            return self.Bp(tree)

    def Bp(self,tree):
        return self.A(tree) and self.J(tree)
    
    def J(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] in ['gr','>','ge','>=','ls','<','le','<=','eq','ne']:
            child = TreeNode(self.current_token[1])
            child.children.append(tree.children[-1])
            tree.children[-1] = child
            self.match(self.current_token[1])
            return self.A(child)
            
        return True

    # Arithmetic Expressions
    def A(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] in ['+', '-']:
            if tree.value == 'E':
                tree.value = 'neg' if self.current_token[1] == '-' else None
                self.match(self.current_token[1])
                return self.At(tree)
            
            else:
                if self.current_token[1] == '-':
                    child = TreeNode('neg')
                    tree.children.append(child)
                    self.match(self.current_token[1])
                    return self.At(child)
                else:
                    self.match(self.current_token[1])
                    return self.At(tree)
            
        else:    
            return self.At(tree) and self.Z(tree)
    
    def Z(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] in ['+', '-']:
            child = TreeNode(self.current_token[1])
            child.children.append(tree.children[-1])
            tree.children[-1] = child
            self.match(self.current_token[1])
            return self.A(child)
            
        return True
        

    def At(self,tree):
        return self.Af(tree) and self.S(tree)
    
    def S(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] in ['*','/']:
            child = TreeNode(self.current_token[1])
            child.children.append(tree.children[-1])
            tree.children[-1] = child
            self.match(self.current_token[1])
            return self.At(child)
            
        return True

    def Af(self,tree):
        return self.Ap(tree) and self.Q(tree)
    
    def Q(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] == '**':
            self.match('**')
            child = TreeNode('**')
            child.children.append(tree.children[-1])
            tree.children[-1] = child
            return self.Af(child)
            
        return True

    def Ap(self,tree):
        return self.R(tree) and self.P(tree)
    
    def P(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] == '@':
            self.match('@')
            child = TreeNode('@')
            child.children.append(tree.children[-1])
            child.children.append(TreeNode('<'+'ID'+':'+self.current_token[1]+'>'))
            tree.children[-1] = child
            return self.match('<ID>') and self.Ap(child)
            
        return True

    # Rators And Rands
    def R(self,tree):
        return self.Rn(tree) and self.Y(tree)
    
    def Y(self,tree):
        s1 = ['<ID>', '<INT>', '<STR>']
        s2 = ['true', 'false', 'nil', 'dummy','(']
        if self.current_token == None:
            return True
        if (self.current_token[0] in s1 or self.current_token[1] in s2) and (self.current_token[1] not in KEYWORDS):
            if tree.value == 'E':
                tree.value = 'gamma'
                return self.R(tree)
            
            if self.root.value == 'gamma':
                child = TreeNode('gamma')
                child.children.append(tree.children[0])
                child.children.append(tree.children[1])
                tree.children.pop(-1)
                tree.children[0] = child
                return self.R(tree)
            
            child = TreeNode('gamma')
            child.children.append(tree.children[-1])
            tree.children[-1] = child
            if child.children[0].value == 'print' or 'Print':
                return self.R(child)
            return self.R(tree)
            
        return True

    def Rn(self,tree):
        s = ['true', 'false', 'nil', 'dummy']
        if self.current_token == None:
            return False
        
        elif ((self.current_token[0] in ['<ID>', '<INT>', '<STR>']) and (self.current_token[1] not in KEYWORDS)):
            if tree.value == 'E': 
                child = TreeNode('<'+self.current_token[0][1:-1]+':'+self.current_token[1]+'>')
                tree.children.append(child)
                self.match(self.current_token[0] or self.current_token[1])
                return True
            
            else:
                child = TreeNode('<'+self.current_token[0][1:-1]+':'+self.current_token[1]+'>')
                tree.children.append(child)
                self.match(self.current_token[0] or self.current_token[1])
                return True
            
        elif self.current_token[1] == '(':
            self.match('(')
            if tree.value == 'E':
                child = TreeNode('E')
                tree.children.append(child)
                return self.E(tree.children[0]) and self.match(')')
            return self.E(tree) and self.match(')')
        else:
            return False
    
    # Definitions 
    def D(self,tree):
        result = self.Da(tree)
        return result and self.X(tree)
                
    def X(self,tree):
        if self.current_token == None:
            return True
        if self.current_token[1] == 'within':
            self.match('within')
            child = TreeNode('within')
            child.children.append(tree.children[-1])
            tree.children[-1] = child
            return self.D(child) 
        return True
    
    def Da(self,tree):
        return self.Dr(tree) and self.Dab(tree)
        
    
    def Dab(self,tree):
        if self.current_token == None:
            return True
        
        if self.current_token[1] == 'and':
            self.match('and')
            child = TreeNode('and')
            child.children.append(tree.children[-1])
            tree.children[-1] = child
            return self.Da(child)
         
        return True
        
    def Dr(self,tree):
        if self.current_token == None:
            return True
        
        if self.current_token[1] == 'rec':
            self.match('rec')
            child = TreeNode('rec')
            tree.children.append(child)
            return self.Db(child)
        
        elif (self.current_token[0] == '<ID>' or self.current_token[1] == '(') and (self.current_token[1] not in KEYWORDS):
            return self.Db(tree)
        else:return False
    
    def Db(self,tree):
        if self.current_token == None:
            return True
        
        if (self.current_token[0] == '<ID>') and (self.current_token[1] not in KEYWORDS):
            tree.children.append(TreeNode('<ID:'+self.current_token[1]+'>'))
            self.match('<ID>')
            if self.current_token[0] == '<ID>' and (self.current_token[1] not in KEYWORDS) or self.current_token[1] == '(':
                node = TreeNode('fcn_form')
                node.add_child(tree.children[-1])
                tree.children[-1] = node
                res=self.Vb(node)
                while (self.current_token[0] == '<ID>' or self.current_token == '(') and (self.current_token[1] not in KEYWORDS):
                    res = res and self.Vb(node)
                res = res and self.match('=')
                return res and self.E(node)
            
            res = self.Vl(tree)
            res = res and self.match('=')
            node = TreeNode('=')
            node.add_child(tree.children[-1])
            tree.children[-1] = node
            return res and self.E(node)
            
        elif self.current_token[1] == '(':
            self.match('(')
            return self.D(tree) and self.match(')')
        
        else:
            return False 
        
    # Variables
    def Vb(self,tree):
        if self.current_token == None:
            return False
        
        if self.current_token[0] == '<ID>' and (self.current_token[1] not in KEYWORDS):
            tree.children.append(TreeNode(self.current_token[1]))
            self.match('<ID>')
            return True
        
        elif self.current_token[1] == '(':
            self.match('(')
            if self.current_token[1] == ')':
                tree.children.append(TreeNode('()'))
                self.match(')')
                return True
            else:
                return self.Vl(tree) and self.match(')')
        
        else:
            return False
        
    def Vl(self,tree): 
        if self.current_token[1] == ',':
            child = TreeNode(',')
            child.children.append(tree.children[-1])
            tree.children[-1] = child
            return self.match(',') and self.Vl(child)  
        return True 

def let(tree):
    if tree.children[0].value == '=':
        node_1 = tree.children[1]
        node_3 = tree.children[0].children[1] 
        tree.children[1] = node_3
        tree.children[0].children[1] = node_1
        tree.value = 'gamma'            
        tree.children[0].value = 'lambda'
        return tree
    else:
        standardize(tree.children[0])
        standardize(tree.children[1])
        standardize(tree)
        return tree
    
def where(tree):
    # print('entered where')
    if tree.children[1].value == '=':
        p = tree.children[0]
        tree.children[0] = tree.children[1]
        tree.children[1] = p
        node_1 = tree.children[0]
        e = node_1[1]
        tree.children[1] = e
        tree.children[0].children[1] = p
        tree.value = 'gamma'            
        tree.children[1].value = 'lambda'
        return tree
        
    else:
        result = standardize(tree.children[0])
        res = standardize(tree.children[1])
        standardize(tree)
        return tree
    
def fcn_form(tree):
    temp = Tree('lambda')
    STree = temp.root
    tree.value = '='
    for child in tree.children[1:-1]:
        node  = temp.add_child_to_node(STree,'lambda')
        temp.add_child_to_node(node,child.value)
        tree.children.pop(1)
        STree = node
    standardize(tree.children[1])
    e =tree.children[1]
    STree.add_child(e)
    tree.children[1] = temp.root.children[0]
    print(STree.children[-1].value)
    return tree
    
def tau(tree):
    STree = Tree('gamma')
    root1 = STree.root
    for child in tree.children[-2::-1]:
        standardize(child)
        node1 = STree.add_child_to_node(root1,'gamma')
        node2 = STree.add_child_to_node(node1,'gamma')
        node1.children.append(child)
        STree.add_child_to_node(node2,'aug')
        root1 = node2
    STree.add_child_to_node(root1,'nil')
    tree.value = 'gamma'
    e = tree.children[-1]
    standardize(e)
    tree.children.clear()
    # node = ASTree.add_child_to_node(tree,'gamma')
    node = TreeNode('gamma')
    tree.children.append(node)
    tree.children.append(e)
    node.add_child(TreeNode('aug'))
    node.add_child(STree.root.children[0])
    return tree

def lambd(tree):
    STree = Tree('lambda')
    root = STree.root
    for child in tree.children[1:-1]:
        node1 = STree.add_child_to_node(root,'lambda')
        STree.add_child_to_node(node1,child.value)
        tree.children.pop(1)
        root = node1
    standardize(tree.children[1])
    E = tree.children[1]
    root.add_child(E)
    tree.children.pop(1)
    tree.children.append(STree.root.children[0])
    return tree

def within(tree):
    if tree.children[0] == '=':
        X1 = tree.children[0].children[0]
        E1 = tree.children[0].children[1]
        if tree.children[1] == '=':
            X2 = tree.children[1].children[0]
            E2 = tree.children[1].children[1]
            tree.value = '='
            tree.children.pop(0)
            tree.children.pop(0)
            tree.children.append(X2)
            # child = ASTree.add_child_to_node(tree,'gamma')
            child = TreeNode('gamma')
            tree.children.append(child)
            # child1 = ASTree.add_child_to_node(child,'lambda')
            child1 = TreeNode('lambda')
            child.add_child(child1)
            child.add_child(E1)
            child1.add_child(X1)
            child1.add_child(E2)
            return tree
        else:
            standardize(tree.children[1])
            standardize(tree)
            return tree
    else:
        standardize(tree.children[0])
        standardize(tree)
        return tree
    
def UoP(tree):
    standardize(tree.children[0])
    op = TreeNode(tree.value)
    tree.value = 'gamma'
    e = tree.children[0]
    tree.children.pop(0)
    tree.children.append(op)
    tree.children.append(e)
    return tree

def BoP(tree):
    standardize(tree.children[0])
    standardize(tree.children[1])
    op = TreeNode(tree.value)
    e1 = tree.children[0]
    e2 = tree.children[1]
    tree.value = 'gamma'
    tree.children.pop(0)
    tree.children.pop(0)
    # child = ASTree.add_child_to_node(tree,'gamma')
    child = TreeNode('gamma')
    tree.children.append(child)
    tree.children.append(e2)
    child.add_child(op)
    child.add_child(e1)
    return tree

def Add(tree):
    standardize(tree.children[0])
    standardize(tree.children[2])
    e1 = tree.children[0]
    n = tree.children[1]
    tree.value = 'gamma'
    child = TreeNode('gamma')
    child.add_child(n)
    child.add_child(e1)
    tree.children[0] = child
    tree.children.pop(1)
    return tree

def And(tree):
    tree.value = '='
    node1 = TreeNode(',')
    node2 = TreeNode('tau')
    for child in tree.children:
        if child.value == '=':
            standardize(child.children[0])
            standardize(child.children[1])
            node1.add_child(child.children[0])
            node2.add_child(child.children[1])
            
        else:
            standardize(child)
            node1.add_child(child.children[0])
            node2.add_child(child.children[1])
    
    tree.children.clear()
    standardize(node1)
    standardize(node2)        
    tree.children.append(node1)
    tree.children.append(node2)
    return tree         



def standardize(tree):
    if len(tree.children) == 0:
        return tree
    else:
        match tree.value:
            case 'let':
                result = let(tree)
                return result
            
            case 'where':
                result = where(tree)
                return result
            
            case 'fcn_form':
                result = fcn_form(tree)
                return result
            
            case 'tau':
                result = tau(tree)
                return result
            
            case 'lambda':
                result = lambd(tree)
                return result
            
            case 'gamma':
                standardize(tree.children[0])
                standardize(tree.children[1])
                return tree
            
            case 'within':
                result = within(tree)
                return result
            
            case 'neg'|'not':
                result = UoP(tree)
                return result
            
            case '+'|'-'|'*'|'/'|'**'|'or'|'&'|'gr'|'ge'|'ls'|'le'|'eq'|'ne'|'>'|'>='|'<'|'<=':
                result = BoP(tree)
                return result
            
            case '@':
                result = Add(tree)
                return result
            
            case 'and':
                result = And(tree)
                return result
    pass

def main():
    if len(sys.argv) < 3 or sys.argv[1] != '-ast':
        print("Usage: python myrpal.py -ast <file_name>")
        return

    file_name = sys.argv[2]
    try:
        with open(file_name, 'r') as file:
            input_text = file.read()
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return

    tokens = tokenize(input_text)
    result, ASTree = parse(tokens)
    if result:
        ASTree.print_tree()
    else:
        print('An error occurred with the input string')

if __name__ == "__main__":
    main()
