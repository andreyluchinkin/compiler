from ply import yacc
import mipsy
from lexer import tokens

class Node:
    def parts_str(self):
        st = []
        for part in self.parts:
            st.append( str( part ) )
        return "\n".join(st)

    def __repr__(self):
        return self.type + ":\n\t" + self.parts_str().replace("\n", "\n\t")

    def add_parts(self, parts):
        self.parts += parts
        return self

    def __init__(self, type, parts):
        self.type = type
        self.parts = parts

########################################################################################################################
#############Основная часть парсера#####################################################################################
########################################################################################################################


def p_prog(p):
    '''prog : VAR dec_list START stmt_list END
            | VAR dec_list def_list START stmt_list END'''
    if len(p) == 6:
        p[0] = Node('prog', [p[2], p[4]])
    else:
        p[0] = Node('prog', [p[2], p[3], p[5]])

def p_def_list(p):
    '''def_list : def
               | def_list SEMI_COLON def'''
    if len(p) == 2:
        p[0] = Node('DEF', [p[1]])
    else:
        p[0] = p[1].add_parts([p[3]])

def p_def(p):
    '''def : DEF ID OPEN_SKOBKA dec_list CLOSE_SKOBKA START stmt_list_def END
            | DEF ID OPEN_SKOBKA dec_list CLOSE_SKOBKA START VAR dec_list stmt_list_def END'''
    if len(p) == 9:
        p[0] = Node(p[2], [p[4], p[7]])
    else:
        p[0] = Node(p[2], [p[4], p[8], p[9]])

def p_defstmt(p):
    '''defstmt : ID OPEN_SKOBKA args CLOSE_SKOBKA'''
    p[0] = Node(p[1], [p[3]])

def p_args(p):
    '''args : arg
            | args SEMI_COLON arg'''
    if len(p) == 2:
        p[0] = Node('args', [p[1]])
    else:
        p[0] = p[1].add_parts([p[3]])


def p_arg(p):
    '''arg : ID
            | INTEGER
            | FLOAT_NUM
            | OPEN_SKOBKA exp CLOSE_SKOBKA'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

def p_dec_list(p):
    '''dec_list : dec
               | dec_list SEMI_COLON dec'''
    if len(p) == 2:
        p[0] = Node('VAR', [p[1]])
    else:
        p[0] = p[1].add_parts([p[3]])

def p_dec(p):
    '''dec : id_list DOUBLE_POINT type'''
    p[0] = Node('dec', [p[1], p[3]])

def p_type(p):
    '''type : INT
            | BOOLEAN
            | FLOAT
            | STR'''
    p[0] = Node('type', [p[1]])

def p_id_list(p):
    '''id_list : ID
                | id_list COMA ID'''
    if len(p) == 2:
        p[0] = Node('Id', [p[1]])
    else:
        p[0] = p[1].add_parts([p[3]])

def p_stmt_list(p):
    '''stmt_list : stmt
                | stmt_list SEMI_COLON stmt'''
    if len(p) == 2:
        p[0] = Node('stmt', [p[1]])
    else:
        p[0] = p[1].add_parts([p[3]])

def p_stmt(p):
    '''stmt : assign
            | print
            | while
            | if'''
    if len(p) == 2:
        p[0] = p[1]

def p_stmt_list_if(p):
    '''stmt_list_if : stmt_if
                | stmt_list_if SEMI_COLON stmt_if'''
    if len(p) == 2:
        p[0] = Node('stmt', [p[1]])
    else:
        p[0] = p[1].add_parts([p[3]])

def p_stmt_if(p):
    '''stmt_if : assign
            | print
            | while
            | if
            | CONTINUE
            | BREAK'''
    if len(p) == 2:
        p[0] = p[1]

def p_stmt_list_def(p):
    '''stmt_list_def : stmt_def
                | stmt_list_def SEMI_COLON stmt_def'''
    if len(p) == 2:
        p[0] = Node('stmt', [p[1]])
    else:
        p[0] = p[1].add_parts([p[3]])

def p_stmt_def(p):
    '''stmt_def : assign
            | print
            | while
            | if
            | return'''
    if len(p) == 2:
        p[0] = p[1]

def p_return(p):
    '''return : RETURN exp'''
    p[0] = Node(p[1], [p[2]])

def p_assign(p):
    '''assign : ID ASSiGNSYMBOL exp
              | ID ASSiGNSYMBOL STRING'''
    p[0] = Node('assign', [p[1], p[3]])

def p_exp(p):
    '''exp : term
            | exp PLUS term
            | exp MINUS term'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Node(p[2], [p[1], p[3]])

def p_term(p):
    '''term : factor
            | term MULTIPLICATION factor
            | term DIV factor'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Node(p[2], [p[1], p[3]])

def p_factor(p):
    '''factor : defstmt
            | ID
            | INTEGER
            | FLOAT_NUM
            | OPEN_SKOBKA exp CLOSE_SKOBKA'''
    if len(p) == 2:
        p[0] = p[1]
    else: p[0] = p[2]

def p_print(p):
    '''print : PRINT OPEN_SKOBKA exp CLOSE_SKOBKA
            | PRINT OPEN_SKOBKA STRING CLOSE_SKOBKA'''
    p[0] = Node('print', [p[3]])

def p_while(p):
    '''while : WHILE bool_exp DO START stmt_list END'''
    p[0] = Node('while', [p[2], p[5]])

def p_if(p):
    '''if : IF bool_exp THEN START stmt_list_if END ELSE START stmt_list_if END
            | IF bool_exp THEN START stmt_list_if END'''
    if len(p) == 11:
        p[0] = Node('if', [p[2], p[5], p[9]])
    else:
        p[0] = Node('if', [p[2], p[5]])

def p_bool_exp(p):
    '''bool_exp : bool_exp OR bool_exp_term
                | bool_exp_term
                | NOT bool_exp
                | bool'''
    if len(p) == 4:
        p[0] = Node(p[2], [p[1], p[3]])
    elif len(p) == 3:
        p[0] = Node(p[1], [p[2]])
    else:
        p[0] = p[1]

def p_bool_exp_term(p):
    '''bool_exp_term : bool_exp_term AND bool
                | bool'''
    if len(p) == 4:
        p[0] = Node(p[2], [p[1], p[3]])
    elif len(p) == 3:
        p[0] = Node(p[1], [p[2]])
    else:
        p[0] = p[1]

def p_bool(p):
    '''bool : OPEN_SKOBKA exp EQUALITY exp CLOSE_SKOBKA
            | OPEN_SKOBKA exp MORE exp CLOSE_SKOBKA
            | OPEN_SKOBKA exp LESS exp CLOSE_SKOBKA'''
    p[0] = Node(p[3], [p[2], p[4]])

def p_error(p):
    print ('Unexpected token:', p)

f = open('test.txt', 'r')
text_input = f.read()


parser = yacc.yacc()
result = parser.parse(text_input)
print("================================================")
print("=================PARSER RESAULT=================")
print("================================================")
print(result)
print("")
f_d = {'f0': '', 'f1': '', 'f2': '', 'f3': '', 'f4': '', 'f5': '', 'f6': '', 'f7': '', 'f8': '', 'f9': '', 'f10': '', 'f11': '', 'f12': '', 'f13': '', 'f14': '', 'f15': '', 'f16': '', 'f17': '', 'f18': '', 'f19': '', 'f20': '', 'f21': '', 'f22': '', 'f23': '', 'f24': '', 'f25': '', 'f26': '', 'f27': '', 'f28': '', 'f29': '', 'f30': '', 'f31': '', 'f32': '', 'f33': '', 'f34': ''}

table = []
functions = []

########################################################################################################################
############################Таблица символов############################################################################
########################################################################################################################
counter_f = 0
sym_table = {'main': {}}
tmp_id = '1'
for parts in result.parts:
    for partss in parts.parts:
        if partss.type == 'dec':
            for i in range(len(partss.parts)):
                if partss.parts[i].type == 'type':
                    if partss.parts[i].parts[0] not in sym_table['main']:
                        sym_table['main'][partss.parts[i].parts[0]] = []
                    sym_table['main'][partss.parts[i].parts[0]].append(partss.parts[i-1].parts[0])

for parts in result.parts:
    if parts.type == 'DEF':
        for partss in parts.parts:
            sym_table[partss.type] = {}
            for partsss in partss.parts:
                if partsss.type == 'VAR':
                    for partssss in partsss.parts:
                        if partssss.type == 'dec':
                            for i in range(len(partssss.parts)):
                                if partssss.parts[i].type == 'type':
                                    if partssss.parts[i].parts[0] not in sym_table[partss.type]:
                                        sym_table[partss.type][partssss.parts[i].parts[0]] = []
                                    sym_table[partss.type][partssss.parts[i].parts[0]].append(partssss.parts[i-1].parts[0])

for parts in result.parts:
    if parts.type == 'DEF':
        for i in parts.parts:
            functions.append(i.type)

def print_Sym_table():
    print("===============================================")
    print("=================Symbols Table=================")
    print("===============================================")
    for keys in sym_table:
        print(keys,':')
        for elements in sym_table[keys]:
            print('\t',elements,': ',sym_table[keys][elements])
    print("")
    print('')


print_Sym_table()
def is_float(a):
    smt = False
    for kis in sym_table:
        if 'float' in sym_table[kis]:
            if a in sym_table[kis]['float']:
                smt = True
    return smt
tree = result
tac = {'main': []}
j = 0
ff = 19
if_count = 0
line_count = 0
jopa = False
conditional_flag = False
def walking(tree):
    global line_count
    if len(tree.parts) == 3:
        tacg(tree.parts[0], 'main')
        tacg(tree.parts[2], 'main')
        for funct in tree.parts[1].parts:
            tac[funct.type] = []
            tacg(funct, funct.type)
    else:
        tacg(tree.parts[0], 'main')
        tacg(tree.parts[1], 'main')
    tac['main'].append('GOTO END')

def walking_on_functionts(tree, name):
    global line_count
    if (type(tree) != Node):
        return
    elif (tree.type == 'dec'):
        for i in tree.parts[0].parts:
            tac[name].append('Dec ' + i)
            line_count = line_count + 1
    elif (tree.type == 'assign'):
        assign_tac(tree, name)
        tac[name].append(':= ' + 't' + str(j - 1) + ' ' + tree.parts[0])

        line_count = line_count + 1
    else:
        for i in range(len(tree.parts)):
            walking_on_functionts(tree.parts[i], name)

def tacg(tree, name):
    global j, if_count, line_count, jopa, ff, conditional_flag
    if (type(tree) != Node and (tree == 'break' or tree == 'continue')):
        tac[name].append(tree)
    elif (type(tree) != Node):
        return
    elif (tree.type == 'dec'):
        for i in tree.parts[0].parts:
            tac[name].append('Dec ' + i)
            line_count = line_count + 1
    elif (tree.type == 'assign'):
        if conditional_flag == False:
            tac[name].append('start_assign')
            conditional_flag = True
        if (type(tree.parts[0]) == str and type(tree.parts[1]) == str):
            tac[name].append(':= ' + tree.parts[1] + ' ' + tree.parts[0])
            line_count = line_count + 1
        else:
            assign_tac(tree, name)
            if jopa:
                tac[name].append(':= ' + 'f' + str(ff - 1) + ' ' + tree.parts[0])
                jopa = False
            else:
                tac[name].append(':= ' + 't' + str(j - 1) + ' ' + tree.parts[0])
            line_count = line_count + 1
            j = 0
            ff = 19
    elif (tree.type == 'if'):
        walking_on_expr(tree.parts[0], name)
        if_name = 'if'+str(if_count)
        if_count = if_count + 1
        tac[if_name] = []
        tac[name].append('IF ' + 't' + str(j - 1) + ' GOTO ' + if_name)
        j = 0
        tacg(tree.parts[1], if_name)
        tac[if_name].append('GOTO after_if')
        line_count = line_count + 1
    elif (tree.type == 'while'):
        if conditional_flag==True:
            conditional_flag=False
        walking_on_expr(tree.parts[0], name)
        if_name = 'if'+str(if_count)
        if_count = if_count + 1
        tac[if_name] = []
        tac[name].append('IF ' + 't' + str(j - 1) + ' GOTO ' + if_name)
        tacg(tree.parts[1], if_name)
        tac[if_name].append('GOTO start_if')
        line_count = line_count + 1
    elif (tree.type == 'return'):
        if (name == 'main'):
            print('return not in function')
        else:
            assign_tac(tree.parts[0],name)
            tac[name].append('return ' + 't'+str(j-1))
    elif (tree.type == 'print'):
        tac[name].append('print ' + tree.parts[0])

    else:
        for i in range(len(tree.parts)):
            tacg(tree.parts[i], name)


def assign_tac(tree, name):
    global j, line_count, ff, jopa, f_d, conditional_flag
    if type(tree) != Node:
        return tree
    elif(tree.type == '*' or tree.type == '/' or tree.type == '+' or tree.type == '-'):
        operand = tree.type
        arg1 = assign_tac(tree.parts[0], name)
        arg2 = assign_tac(tree.parts[1], name)
        if arg1 == None and arg2 == None:
            if operand == "-":
                print('отработало тут1')
            if jopa:
                arg1 = 'f' + str(ff - 2)
                arg2 = 'f' + str(ff - 1)
            else:
                arg1 = 't' + str(j - 2)
                arg2 = 't' + str(j - 1)
        if arg1 == None:
            if operand == "-":
                print('отработало тут2')
            if '.' in arg2:
                arg1 = 'f' + str(ff - 1)
            else:
                arg1 = 't' + str(j - 1)
                for kis in sym_table:
                    if arg2 in sym_table[kis]['float']:
                        arg1 = 'f' + str(ff - 1)
                        jopa = True
        if arg2 == None:
            if operand == "-":
                print('отработало тут3')
                print(arg1)
            if '.' in arg1:
                arg2 = 'f' + str(ff - 1)
            else:
                arg2 = 't' + str(j - 1)
                for kis in sym_table:
                    if 'float' in sym_table[kis]:
                        if arg1 in sym_table[kis]['float']:
                            arg2 = 'f' + str(ff - 1)


        if '.' in arg1 or '.' in arg2:
            temp = 'f' + str(ff)
            jopa = True
        else:
            if operand == "-":
                print('отработало тут4')
                print(arg1, arg2)
            temp = 't' + str(j)
            for kis in sym_table:
                if 'float' in sym_table[kis]:
                    if arg1 in sym_table[kis]['float'] and arg2 in sym_table[kis]['float']:
                        temp = 'f' + str(ff)
                        jopa = True
            if arg1 in f_d:

               # arg1 = 'f' + str(ff)

                temp = 'f' + str(ff)
            if arg2 in f_d or is_float(arg2):
                #print(arg2)
               # arg2 = 'f' + str(ff)

                temp = 'f' + str(ff)
        j = j+1
        ff = ff + 1
        #print('asdasD + '+ str(temp))
        #print(' ' + str(arg1) + ' ' + str(arg2))
        tac[name].append(str(operand) + ' ' + str(arg1) + ' ' + str(arg2) + ' ' + str(temp))
        line_count = line_count + 1
    elif (tree.type in functions):
        string = 'Call ' + tree.type + ' '
        for arg in tree.parts[0].parts:
            string = string + arg + ' '
        temp = 't' + str(j)
        j = j + 1
        string = string + temp
        tac[name].append(string)

    else:
        for i in range(len(tree.parts)):
            assign_tac(tree.parts[i], name)

def walking_on_expr(tree, name):
    global j, line_count, conditional_flag
    #print('if')
    if type(tree) != Node:
        return tree
    elif(tree.type == 'and' or tree.type == 'or'):
        operand = tree.type
        arg1 = walking_on_expr(tree.parts[0], name)
        arg2 = walking_on_expr(tree.parts[1], name)
        if arg1 == None and arg2 == None:
            arg1 = 't' + str(j - 2)
            arg2 = 't' + str(j - 1)
        if arg1 == None:
            arg1 = 't'+str(j-1)
        if arg2 == None:
            arg2 = 't'+str(j-1)
        temp = 't'+str(j)
        j = j+1
        #print('op = '+operand)
        #print('arg1='+str(arg1))
        #print('arg2='+str(arg2))
        #print('temp='+str(temp))
        tac[name].append(str(operand) + ' ' + str(arg1) + ' ' + str(arg2) + ' ' + str(temp))
        line_count = line_count + 1
    elif (tree.type == 'not'):
        operand = tree.type
        walking_on_expr(tree.parts[0], name)
        arg = 't'+str(j-1)
        temp = 't' + str(j)
        j = j + 1
        tac[name].append(str(operand) + ' ' + str(arg) + ' ' + str(temp))
        line_count = line_count + 1
    elif (tree.type == '>' or tree.type == '<' or tree.type == '='):
        operand = tree.type
        arg1 = assign_tac(tree.parts[0], name)
        arg2 = assign_tac(tree.parts[1], name)
        temp = 't' + str(j)
        j = j + 1
        if arg1 == None:
            if is_float(arg2):
                arg1 = "f" + str(ff - 1)
            else:
                arg1 ="t"+str(j-2)
        print(arg1, arg2)
        tac[name].append(str(operand) + ' ' + str(arg1) + ' ' + str(arg2) + ' ' + str(temp))
        line_count = line_count + 1
    else:
        for i in range(len(tree.parts)):
            walking_on_expr(tree.parts[i], name)


walking(tree)
print('=======================================================================')
print('=========================Трёхадресный код==============================')
print('=======================================================================')
for key in tac:
    print(key + ' : ')
    for i in tac[key]:
        print('\t' + str(i))

alphabet = ['0','1','2','3','4','5','6','7','8','9']
def is_contained(t, a):
    for kis in t:
        if a == t[kis]:
            return True
        else:
            return False


def findekey(t,a):
    for kis in t:
        if a in "t0t1t2t3t4t5t6t7t8t9":
            return a
        if a == t[kis]:
            return kis

def is_correct(a, b):
    if a.isdigit() and b.isdigit():
        return True
    elif '.' in a and '.' in b:
        return True
    elif 'int' in sym_table[now_scope]:
        if (a.isdigit() and b in sym_table[now_scope]["int"]) or (b.isdigit() and a in sym_table[now_scope]["int"]):
            return True
    elif 'float' in sym_table[now_scope]:
        if ('.' in a and b in sym_table[now_scope]['float']) or ('.' in b and a in sym_table[now_scope]['float']):
            return True
    else:
        return False

now_scope = ''
def translate(tac):
    print("===============================================")
    print("===============ход обработки===================")
    print("===============================================")
    global now_scope, f_d
    t={'t0':'', 't1':'', 't2':'', 't3':'', 't4':'', 't5':'', 't6':'', 't7':''}
    s={'s0':'', 's1':'', 's2':'', 's3':'', 's4':'', 's5':'', 's6':'', 's7':''}
    a= {'a1': '', 'a2': '', 'a3': ''}
    counter_s = []
    need_to_returninto = []
    bc1_counter=0
    toomcuh_counter = 0
    #f_d = {'f0': '', 'f1': '', 'f2': '', 'f3': '', 'f4': '', 'f5': '', 'f6': '', 'f7': '', 'f8': '', 'f9': '', 'f10': '', 'f11': '', 'f12': '', 'f13': '', 'f14': '', 'f15': '', 'f16': '', 'f17': '', 'f18': '', 'f19': '', 'f20': '', 'f21': '', 'f22': '', 'f23': '', 'f24': '', 'f25': '', 'f26': '', 'f27': '', 'f28': '', 'f29': '', 'f30': '', 'f31': '', 'f32': '', 'f33': '', 'f34': ''}
    if_flag = False
    if_count = 0
    if_flag1 = False
    tmp = 7
    string_counter = 0
    reserved = 0
    count = 0
    _data = ''
    f = open('out.a', 'w')
    _data = _data +('.data\n\ttrue: .byte 1\n\tfalse: .byte 0\n')
    _data = _data +('\tstring2: .asciiz'+r' "\n"'+'\n')
    f.write('.text\n')
    for scope in tac:
        if 'if' not in scope:
            now_scope = scope
        f.write(scope+' :\n')
        for operators in tac[scope]:
            operators_list = operators.split(' ')
            print(operators_list)
            if operators_list[0] == 'Dec':
                if now_scope=='main':
                    if 'float' in sym_table['main']:
                        if operators_list[1] in sym_table['main']['float']:
                            if not is_contained(f_d, operators_list[1]):
                                for kis in f_d:
                                    if f_d[kis] == '':
                                        f_d[kis] = operators_list[1]
                                        break
                    if 'int' in sym_table['main']:
                        if operators_list[1] in sym_table['main']['int']:
                            if not is_contained(s, operators_list[1]):
                                for kis in s:
                                    if s[kis] == '':
                                        s[kis] = operators_list[1]
                                        break
            if operators_list[0] == ':=':
                type_of_variable=''
                #определение типа переменной
                if 'if' not in scope:
                    for type in sym_table[scope]:
                        if operators_list[2] in sym_table[scope][type]:
                            type_of_variable=type
                if operators_list[1].isdigit():
                    if not is_contained(s, operators_list[2]):
                        for kis in s:
                            if s[kis] == '':
                                print(operators_list[2])
                                s[kis] = operators_list[2]
                                break
                            if s[kis] == operators_list[2]:
                                break
                    f.write('\tli $' + findekey(s, operators_list[2]) + ', ' + operators_list[1] + '\n')
                elif '.' in operators_list[1]:
                    if is_contained(f_d, operators_list[2])!=True:
                        for kis in f_d:
                            if f_d[kis] == '':
                                f_d[kis] = operators_list[2]
                                break
                            if f_d[kis] == operators_list[2]:
                                break
                    print(operators_list[2])

                    f.write('\tli.s $' + findekey(f_d, operators_list[2]) + ', ' + operators_list[1] + '\n')
                else:
                    if('int' in sym_table[now_scope]):
                        if operators_list[2] in sym_table[now_scope]['int'] and operators_list[1] in sym_table[now_scope]['int']:
                            f.write('\tmove $' + findekey(s, operators_list[2]) + ', $' + findekey(s, operators_list[1]) + '\n')
                        if operators_list[1] in t:
                            if not is_contained(s, operators_list[2]):
                                print('Отработало '+operators_list[2])
                                print(s)
                                for kis in s:
                                    if s[kis] == '':
                                        print(operators_list[2])
                                        s[kis] = operators_list[2]
                                        break
                                    if s[kis] == operators_list[2]:
                                        break
                            f.write('\tmove $' + findekey(s, operators_list[2]) + ', $' + operators_list[1] + '\n')
                        if ('float' in sym_table[now_scope]):
                            if operators_list[2] in sym_table[now_scope]['float'] and operators_list[1] in sym_table[now_scope]['int']:
                                f.write('\tmtc1 $'+findekey(s, operators_list[1])+',$f10\n')
                                f.write('\tcvt.s.w $f10,$f10\n')
                                f.write('\tmov.s $'+findekey(f_d, operators_list[2])+' $f10\n')
                    if('float' in sym_table[now_scope]):
                        if operators_list[2] in sym_table[now_scope]['float'] and operators_list[1] in sym_table[now_scope]['float']:
                            f.write('\tmov.s $' + findekey(f_d, operators_list[2]) + ', $' + findekey(f_d, operators_list[1]) + '\n')
                    if operators_list[1] in f_d:
                        if not is_contained(f_d, operators_list[2]):
                            for kis in f_d:
                                if f_d[kis] == '':
                                    f_d[kis] = operators_list[2]
                                    break
                                if f_d[kis] == operators_list[2]:
                                    break
                        f.write('\tmov.s $' + findekey(f_d, operators_list[2]) + ', $' + operators_list[1] + '\n')
                    if "'" in operators_list[1]:
                        _data = _data + '\t'+operators_list[2]+': .asciiz '+ operators_list[1].replace("'",'"')+ '\n'

            elif operators_list[0] == '+':
                if (operators_list[1].isdigit()):
                    if(operators_list[2].isdigit()):
                        f.write('\tli $t7 '+ operators_list[2]+'\n')
                        f.write('\taddiu $' + operators_list[3] + ', $t7'+ ', ' + operators_list[1] + '\n')
                    elif('.' in operators_list[2]):
                        print(operators_list[3])
                    else:
                        f.write('\taddiu $' + operators_list[3] + ', $' + findekey(s, operators_list[2]) + ', ' + operators_list[1] + '\n')
                elif (operators_list[2].isdigit()):
                    print(s)
                    f.write('\taddiu $' + operators_list[3] + ', $' + findekey(s, operators_list[1]) + ', ' + operators_list[2] + '\n')
                else:
                    if '.' in operators_list[2] and not '.' in operators_list[1]:
                        if not is_contained(f_d, operators_list[1]):
                            for kis in f_d:
                                if f_d[kis] == '':
                                    f_d[kis] = operators_list[1]
                                    break
                                if f_d[kis] == operators_list[2]:
                                    break
                        f.write('\tli.s $f10 , '+operators_list[2]+'\n')
                        f.write('\tadd.s $'+operators_list[3] +', $f10, $'+findekey(f_d, operators_list[1])+'\n')
                    if '.' in operators_list[1] and not '.' in operators_list[2]:
                        if not is_contained(f_d, operators_list[2]):
                            for kis in f_d:
                                if f_d[kis] == '':
                                    f_d[kis] = operators_list[2]
                                    break
                                if f_d[kis] == operators_list[2]:
                                    break
                        f.write('\tli.s $f10 , '+operators_list[1]+'\n')
                        f.write('\tadd.s $'+operators_list[3] +', $f10, $'+findekey(f_d, operators_list[2])+'\n')
                    if '.' in operators_list[1] and '.' in operators_list[2]:
                        f.write('\tli.s $f10 , ' + operators_list[1] + '\n')
                        f.write('\tli.s $f11 , ' + operators_list[2] + '\n')
                        f.write('\tadd.s $' + operators_list[3] + ', $f10, $f11\n')
                    else:
                        if operators_list[3] in f_d:
                            if '.' not in operators_list[1] and '.' not in operators_list[2]:
                                if operators_list[1] in f_d and not operators_list[2] in f_d:
                                    f.write('\tadd.s $' + operators_list[3] + ', $' + operators_list[1] + ', $' + findekey(f_d, operators_list[2]) + '\n')
                                elif operators_list[1] in f_d and operators_list[2] in f_d:
                                    f.write('\tadd.s $' + operators_list[3] + ', $' + operators_list[1] + ', $' + operators_list[2] + '\n')
                                elif not operators_list[1] in f_d and operators_list[2] in f_d:
                                    f.write('\tadd.s $' + operators_list[3] + ', $' + operators_list[1] + ', $' +findekey(f_d, operators_list[2]) + '\n')
                                else:
                                    f.write('\tadd.s $' + operators_list[3] + ', $' + findekey(f_d, operators_list[1]) + ', $' + findekey(f_d, operators_list[2]) + '\n')
                            elif '.' not in operators_list[1] and '.' in operators_list[2]:
                                f.write('\tli.s $f10, '+operators_list[2]+'\n')
                                f.write('\tadd.s $' + operators_list[3] + ', $' + findekey(f_d, operators_list[1]) + ', $f10\n')
                            elif '.'  in operators_list[1] and not '.' in operators_list[2]:
                                f.write('\tli.s $f10, '+operators_list[1]+'\n')
                                f.write('\tadd.s $' + operators_list[3] + ', $' + findekey(f_d, operators_list[2]) + ', $f10\n')
                            elif '.' in operators_list[1] and  '.' in operators_list[2]:
                                f.write('\tli.s $f10, '+operators_list[1]+'\n')
                                f.write('\tli.s $f11, ' + operators_list[2] + '\n')
                                f.write('\tadd.s $' + operators_list[3] + ', $f10, $f11\n')
                        else:
                            f.write('\taddu $' + operators_list[3] + ', $' + findekey(s,operators_list[1]) + ', $' + findekey(s, operators_list[2]) + '\n')

            elif operators_list[0] == "*":
                if operators_list[3] in f_d:
                    if '.' not in operators_list[1] and '.' not in operators_list[2]:
                        if operators_list[1] in f_d and not operators_list[2] in f_d:
                            f.write('\tmul.s $' + operators_list[3] + ', $' + operators_list[1] + ', $' + findekey(f_d,operators_list[2]) + '\n')
                        elif operators_list[1] in f_d and operators_list[2] in f_d:
                            f.write('\tmul.s $' + operators_list[3] + ', $' + operators_list[1] + ', $' + operators_list[2] + '\n')
                        elif not operators_list[1] in f_d and operators_list[2] in f_d:
                            if is_contained(f_d,operators_list[1]):
                                f.write(
                                    '\tmul.s $' + operators_list[3] + ', $' + findekey(f_d,operators_list[1]) + ', $' + findekey(f_d,operators_list[2]) + '\n')
                            else:
                                f.write('\tmul.s $' + operators_list[3] + ', $' + operators_list[1] + ', $' + findekey(f_d,operators_list[2]) + '\n')
                        else:
                            f.write('\tmul.s $' + operators_list[3] + ', $' + findekey(f_d, operators_list[1]) + ', $' + findekey(f_d, operators_list[2]) + '\n')
                    elif '.' not in operators_list[1] and '.' in operators_list[2]:
                        f.write('\tli.s $f10, ' + operators_list[2] + '\n')
                        f.write('\tmul.s $' + operators_list[3] + ', $' + findekey(f_d, operators_list[1]) + ', $f10\n')
                    elif '.' in operators_list[1] and not '.' in operators_list[2]:
                        f.write('\tli.s $f10, ' + operators_list[1] + '\n')
                        f.write('\tmul.s $' + operators_list[3] + ', $f10, $' + findekey(f_d, operators_list[2]) + '\n')
                    elif '.' in operators_list[1] and '.' in operators_list[2]:
                        f.write('\tli.s $f10, ' + operators_list[1] + '\n')
                        f.write('\tli.s $f11, ' + operators_list[2] + '\n')
                        f.write('\tmul.s $' + operators_list[3] + ', $f10, $f11\n')

                else:
                    if '.' not in operators_list[1] and '.' not in operators_list[2]:
                        if (operators_list[1].isdigit()) and (operators_list[2].isdigit()):
                            print('tut1')
                            f.write('\tli $t'+str(tmp)+' '+operators_list[1]+'\n')
                            f.write('\tmul $'+operators_list[3]+', $t'+operators_list[2]+', $'+str(tmp)+'\n')
                        elif not operators_list[1].isdigit() and not operators_list[2].isdigit():
                            print('tut2')
                            if operators_list[3] in f_d:
                                f.write('\tmul.s $'+operators_list[3]+', $'+findekey(f_d, operators_list[1])+', $'+findekey(f_d, operators_list[2])+'\n')
                            else:
                                f.write('\tmul $' + operators_list[3] + ', $' + findekey(s, operators_list[1]) + ', $' + findekey(s,operators_list[2]) + '\n')
                        elif operators_list[1].isdigit() and not operators_list[2].isdigit():
                            print('tut3')
                            f.write('\tmul $' + operators_list[3] + ', $'+findekey(s, operators_list[2])+', '+operators_list[1]+'\n')
                        elif not operators_list[1].isdigit() and operators_list[2].isdigit():
                            print('tut4')
                            f.write('\tmul $' + operators_list[3] + ', $' + findekey(s, operators_list[1]) + ', ' + operators_list[2] + '\n')

            elif operators_list[0] == "-":
                if operators_list[3] in f_d:
                    if '.' not in operators_list[1] and '.' not in operators_list[2]:
                        if operators_list[1] in f_d and not operators_list[2] in f_d:
                            f.write('\tsub.s $' + operators_list[3] + ', $' + operators_list[1] + ', $' + findekey(f_d,operators_list[2]) + '\n')
                        elif operators_list[1] in f_d and operators_list[2] in f_d:
                            f.write('\tsub.s $' + operators_list[3] + ', $' + operators_list[1] + ', $' + operators_list[2] + '\n')
                        elif not operators_list[1] in f_d and operators_list[2] in f_d:
                            f.write('\tsub.s $' + operators_list[3] + ', $' + findekey(f_d, operators_list[1]) + ', $' + operators_list[2] + '\n')
                        else:
                            f.write('\tsub.s $' + operators_list[3] + ', $' + findekey(f_d, operators_list[1]) + ', $' + findekey(f_d, operators_list[2]) + '\n')
                    elif '.' not in operators_list[1] and '.' in operators_list[2]:
                        f.write('\tli.s $f10, ' + operators_list[2] + '\n')
                        f.write('\tsub.s $' + operators_list[3] + ', $' + findekey(f_d, operators_list[1]) + ', $f10\n')
                    elif '.' in operators_list[1] and not '.' in operators_list[2]:
                        f.write('\tli.s $f10, ' + operators_list[1] + '\n')
                        f.write('\tsub.s $' + operators_list[3] + ', $f10, $' + findekey(f_d, operators_list[2]) + '\n')
                    elif '.' in operators_list[1] and '.' in operators_list[2]:
                        f.write('\tli.s $f10, ' + operators_list[1] + '\n')
                        f.write('\tli.s $f11, ' + operators_list[2] + '\n')
                        f.write('\tsub.s $' + operators_list[3] + ', $f10, $f11\n')
                else:
                    if operators_list[1].isdigit() and operators_list[2].isdigit():
                        f.write('\tli $t' + str(tmp) + ' ' + operators_list[1] + '\n')
                        f.write('\tsub $' + operators_list[3] + ' $t' + str(tmp) + ' ' + operators_list[2] + '\n')
                    if operators_list[1].isdigit() and not operators_list[2].isdigit():
                        f.write('\tli $t' + str(tmp) + ' ' + operators_list[1] + '\n')
                        f.write('\tsub $' + operators_list[3] + ' $t' + str(tmp) + ' $' + findekey(s,operators_list[2]) + '\n')
                    if (not operators_list[1].isdigit()) and (operators_list[2].isdigit()):
                        f.write('\tsub $' + operators_list[3] + ' $' + findekey(s,operators_list[1]) + ' ' + operators_list[2] + '\n')
                    if (not operators_list[1].isdigit()) and (not operators_list[2].isdigit()):
                        f.write('\tsub $' + operators_list[3] + ' $' + findekey(s,operators_list[1]) + ' $' + findekey(s,operators_list[2]) + '\n')
            elif operators_list[0] == "/":
                if operators_list[3] in f_d:
                    if '.' not in operators_list[1] and '.' not in operators_list[2]:
                        if operators_list[1] in f_d and not operators_list[2] in f_d:
                            f.write('\tdiv.s $' + operators_list[3] + ', $' + operators_list[1] + ', $' + findekey(f_d,operators_list[2]) + '\n')
                        elif operators_list[1] in f_d and operators_list[2] in f_d:
                            f.write('\tdiv.s $' + operators_list[3] + ', $' + operators_list[1] + ', $' + operators_list[2] + '\n')
                        elif not operators_list[1] in f_d and operators_list[2] in f_d:
                            f.write('\tdiv.s $' + operators_list[3] + ', $' + operators_list[1] + ', $' + findekey(f_d,operators_list[2]) + '\n')
                        else:
                            f.write('\tdiv.s $' + operators_list[3] + ', $' + findekey(f_d, operators_list[1]) + ', $' + findekey(f_d, operators_list[2]) + '\n')
                    elif '.' not in operators_list[1] and '.' in operators_list[2]:
                        f.write('\tli.s $f10, ' + operators_list[2] + '\n')
                        f.write('\tdiv.s $' + operators_list[3] + ', $' + findekey(f_d, operators_list[1]) + ', $f10\n')
                    elif '.' in operators_list[1] and not '.' in operators_list[2]:
                        f.write('\tli.s $f10, ' + operators_list[1] + '\n')
                        f.write('\tdiv.s $' + operators_list[3] + ', $f10, $' + findekey(f_d, operators_list[2]) + '\n')
                    elif '.' in operators_list[1] and '.' in operators_list[2]:
                        f.write('\tli.s $f10, ' + operators_list[1] + '\n')
                        f.write('\tli.s $f11, ' + operators_list[2] + '\n')
                        f.write('\tdiv.s $' + operators_list[3] + ', $f10, $f11\n')
                else:
                    if operators_list[1].isdigit() and operators_list[2].isdigit():
                        f.write('\tli $t' + str(tmp) + ' ' + operators_list[1] + '\n')
                        f.write('\tdiv $' + operators_list[3] + ' $t' + str(tmp) + ' ' + operators_list[2] + '\n')
                    if operators_list[1].isdigit() and not operators_list[2].isdigit():
                        f.write('\tli $t' + str(tmp) + ' ' + operators_list[1] + '\n')
                        f.write('\tdiv $' + operators_list[3] + ' $t' + str(tmp) + ' $' + findekey(s,operators_list[2]) + '\n')
                    if (not operators_list[1].isdigit()) and (operators_list[2].isdigit()):
                        f.write('\tdiv $' + operators_list[3] + ' $' + findekey(s,operators_list[1]) + ' ' + operators_list[2] + '\n')
                    if (not operators_list[1].isdigit()) and (not operators_list[2].isdigit()):
                        f.write('\tdiv $' + operators_list[3] + ' $' + findekey(s,operators_list[1]) + ' $' + findekey(s,operators_list[2]) + '\n')
            elif operators_list[0] == 'print':
                if 'int' in sym_table[now_scope]:
                    if operators_list[1] in sym_table[now_scope]['int']:
                        f.write('\tli $v0, 1\n')
                        f.write('\tla $a0, ($'+findekey(s, operators_list[1])+')\n\tsyscall\n')
                        f.write('\tli $v0, 4\n')
                        f.write('\tla $a0, string2\n\tsyscall\n')
                if 'float' in sym_table[now_scope]:
                    if operators_list[1] in sym_table[now_scope]['float']:
                        f.write('\tli $v0, 2\n')
                        f.write('\tmov.s $f12, $' + findekey(f_d, operators_list[1]) + '\n\tsyscall\n')
                        f.write('\tli $v0, 4\n')
                        f.write('\tla $a0, string2\n\tsyscall\n')
                if 'string' in sym_table[now_scope]:
                    if operators_list[1] in sym_table[now_scope]['string']:
                        f.write('\tli $v0, 4\n')
                        f.write('\tla $a0, '+operators_list[1]+'\n\tsyscall\n')
                        f.write('\tli $v0, 4\n')
                        f.write('\tla $a0, string2\n\tsyscall\n')
                if "'" in operators_list[1]:
                    _data = _data + '\ttmpstring'+str(string_counter)+': .asciiz '+operators_list[1].replace("'",'"')+'\n'
                    f.write('\tli $v0, 4\n')
                    f.write('\tla $a0, ' + 'tmpstring'+str(string_counter) + '\n\tsyscall\n')
                    f.write('\tli $v0, 4\n')
                    f.write('\tla $a0, string2\n\tsyscall\n')
                    string_counter=string_counter+1
            elif operators_list[0] == '<':
                if not if_flag:
                    print(if_flag)
                    if_flag = True
                    f.write("start_if"+str(if_count)+': \n')
                    if_count = if_count + 1
                if '.' in operators_list[1] or '.' in operators_list[2] or (is_float(operators_list[1]) and is_float(operators_list[2])) or (is_float(operators_list[1]) and '.' in operators_list[2] ) or (is_float(operators_list[2]) and '.' in operators_list[1]):
                    if '.' in operators_list[1]:
                        if '.' in operators_list[2]:
                            f.write('\t li.s $f16,'+operators_list[1]+'\n')
                            f.write('\t li.s $f17,' + operators_list[2]+'\n')
                            f.write('\tc.lt.s $f16, $f17\n')
                            f.write('\tli $'+operators_list[3]+', 1\n')
                            f.write('\tmove $s7 $'+operators_list[3]+'\n')
                            f.write('\tbc1f makefalse'+str(bc1_counter)+'\n')
                            f.write('endmakefalse'+str(bc1_counter)+':\n')
                            bc1_counter += 1
                            f.write('\tmove $' + operators_list[3]+' $s7\n')
                        if is_float(operators_list[2]):
                            f.write('\t li.s $f16,' + operators_list[1] + '\n')
                            f.write('\tc.lt.s $f16, $'+findekey(f_d, operators_list[2])+'\n')
                            f.write('\tli $' + operators_list[3] + ', 1\n')
                            f.write('\tmove $s7 $' + operators_list[3] + '\n')
                            f.write('\tbc1f makefalse' + str(bc1_counter) + '\n')
                            f.write('endmakefalse' + str(bc1_counter) + ':\n')
                            bc1_counter += 1
                            f.write('\tmove $' + operators_list[3] + ' $s7\n')
                    if '.' in operators_list[2]:
                        if is_float(operators_list[1]):
                            f.write('\t li.s $f16,' + operators_list[2] + '\n')
                            f.write('\tc.lt.s $'+findekey(f_d, operators_list[1])+', $f16\n')
                            f.write('\tli $' + operators_list[3] + ', 1\n')
                            f.write('\tmove $s7 $' + operators_list[3] + '\n')
                            f.write('\tbc1f makefalse' + str(bc1_counter) + '\n')
                            f.write('endmakefalse' + str(bc1_counter) + ':\n')
                            bc1_counter += 1
                            f.write('\tmove $' + operators_list[3] + ' $s7\n')
                    if is_float(operators_list[1]) and is_float(operators_list[2]):
                        f.write('\tc.lt.s $' + findekey(f_d, operators_list[1]) + ', $'+ findekey(f_d, operators_list[2])+'\n')
                        f.write('\tli $' + operators_list[3] + ', 1\n')
                        f.write('\tmove $s7 $' + operators_list[3] + '\n')
                        f.write('\tbc1f makefalse' + str(bc1_counter) + '\n')
                        f.write('endmakefalse' + str(bc1_counter) + ':\n')
                        bc1_counter += 1
                        f.write('\tmove $' + operators_list[3] + ' $s7\n')

                else:
                    if operators_list[1].isdigit() and operators_list[2].isdigit():
                        f.write("\tli $t7 "+operators_list[1]+'\n')
                        f.write("\tli $t6 " + operators_list[2] + '\n')
                        f.write("\tslt $"+operators_list[3]+', $t7, $t6\n')
                    elif operators_list[1].isdigit() and not operators_list[2].isdigit():
                        f.write("\tli $t7 " + operators_list[1] + '\n')
                        f.write("\tslt $" + operators_list[3] + ', $t7, $'+findekey(s, operators_list[2])+'\n')
                    elif not operators_list[1].isdigit() and operators_list[2].isdigit():
                        f.write("\tli $t7 " + operators_list[2] + '\n')
                        if is_contained(s, operators_list[1]):
                            f.write("\tslt $" + operators_list[3] + ', $' + findekey(s, operators_list[1]) + ', $t7\n')
                        else:
                            f.write("\tslt $" + operators_list[3] + ', $'+findekey(s, operators_list[1])+', $t7\n')
                    elif not operators_list[1].isdigit() and not operators_list[2].isdigit():
                        f.write("\tslt $" + operators_list[3] + ', $' + findekey(s, operators_list[1]) + ', $'+findekey(s, operators_list[2])+'\n')
            elif operators_list[0] == '>':
                if not if_flag:
                    print(if_flag)
                    if_flag = True
                    f.write("start_if"+str(if_count)+': \n')
                    if_count = if_count + 1
                if '.' in operators_list[1] or '.' in operators_list[2] or (is_float(operators_list[1]) and is_float(operators_list[2])) or (is_float(operators_list[1]) and '.' in operators_list[2] ) or (is_float(operators_list[2]) and '.' in operators_list[1]) or is_float(operators_list[2]):
                    temp_op = operators_list[1]
                    operators_list[1] = operators_list[2]
                    operators_list[2] = temp_op
                    if '.' in operators_list[1]:
                        if '.' in operators_list[2]:
                            f.write('\t li.s $f16,'+operators_list[1]+'\n')
                            f.write('\t li.s $f17,' + operators_list[2]+'\n')
                            f.write('\tc.lt.s $f16, $f17\n')
                            f.write('\tli $'+operators_list[3]+', 1\n')
                            f.write('\tmove $s7 $'+operators_list[3]+'\n')
                            f.write('\tbc1f makefalse' + str(bc1_counter) + '\n')
                            f.write('endmakefalse' + str(bc1_counter) + ':\n')
                            bc1_counter += 1
                            f.write('\tmove $' + operators_list[3]+' $s7\n')
                        if is_float(operators_list[2]):
                            f.write('\t li.s $f16,' + operators_list[1] + '\n')
                            f.write('\tc.lt.s $f16, $'+findekey(f_d, operators_list[2])+'\n')
                            f.write('\tli $' + operators_list[3] + ', 1\n')
                            f.write('\tmove $s7 $' + operators_list[3] + '\n')
                            f.write('\tbc1f makefalse' + str(bc1_counter) + '\n')
                            f.write('endmakefalse' + str(bc1_counter) + ':\n')
                            bc1_counter += 1
                            f.write('\tmove $' + operators_list[3] + ' $s7\n')
                    if '.' in operators_list[2]:
                        if is_float(operators_list[1]):
                            f.write('\t li.s $f16,' + operators_list[2] + '\n')
                            f.write('\tc.lt.s $'+findekey(f_d, operators_list[1])+', $16\n')
                            f.write('\tli $' + operators_list[3] + ', 1\n')
                            f.write('\tmove $s7 $' + operators_list[3] + '\n')
                            f.write('\tbc1f makefalse' + str(bc1_counter) + '\n')
                            f.write('endmakefalse' + str(bc1_counter) + ':\n')
                            bc1_counter += 1
                            f.write('\tmove $' + operators_list[3] + ' $s7\n')
                    if is_float(operators_list[1]) and is_float(operators_list[2]):
                        f.write('\tc.lt.s $' + findekey(f_d, operators_list[1]) + ', $'+ findekey(f_d, operators_list[2])+'\n')
                        f.write('\tli $' + operators_list[3] + ', 1\n')
                        f.write('\tmove $s7 $' + operators_list[3] + '\n')
                        f.write('\tbc1f makefalse' + str(bc1_counter) + '\n')
                        f.write('endmakefalse' + str(bc1_counter) + ':\n')
                        bc1_counter += 1
                        f.write('\tmove $' + operators_list[3] + ' $s7\n')
                else:
                    if operators_list[1].isdigit() and operators_list[2].isdigit():
                        f.write("\tli $t7 "+operators_list[1]+'\n')
                        f.write("\tli $t6 " + operators_list[2] + '\n')
                        f.write("\tsgt $"+operators_list[3]+', $t7, $t6\n')
                    elif operators_list[1].isdigit() and not operators_list[2].isdigit():
                        f.write("\tli $t7 " + operators_list[1] + '\n')
                        f.write("\tsgt $" + operators_list[3] + ', $t7, $'+findekey(s, operators_list[2])+'\n')
                    elif not operators_list[1].isdigit() and operators_list[2].isdigit():
                        f.write("\tli $t7 " + operators_list[2] + '\n')
                        f.write("\tsgt $" + operators_list[3] + ', $'+findekey(s, operators_list[1])+', $t7\n')
                    elif not operators_list[1].isdigit() and not operators_list[2].isdigit():
                        f.write("\tsgt $" + operators_list[3] + ', $' + findekey(s, operators_list[1]) + ', $'+findekey(s, operators_list[2])+'\n')
            elif operators_list[0] == '=':
                print(if_flag)
                if not if_flag:
                    if_flag = True
                    f.write("start_if"+str(if_count)+': \n')
                    if_count = if_count + 1
                if '.' in operators_list[1] or '.' in operators_list[2] or (is_float(operators_list[1]) and is_float(operators_list[2])) or (is_float(operators_list[1]) and '.' in operators_list[2] ) or (is_float(operators_list[2]) and '.' in operators_list[1]):
                    if '.' in operators_list[1]:
                        if '.' in operators_list[2]:
                            f.write('\t li.s $f16,'+operators_list[1]+'\n')
                            f.write('\t li.s $f17,' + operators_list[2]+'\n')
                            f.write('\tc.eq.s $f16, $f17\n')
                            f.write('\tli $'+operators_list[3]+', 1\n')
                            f.write('\tmove $s7 $'+operators_list[3]+'\n')
                            f.write('\tbc1f makefalse' + str(bc1_counter) + '\n')
                            f.write('endmakefalse' + str(bc1_counter) + ':\n')
                            bc1_counter += 1
                            f.write('\tmove $' + operators_list[3]+' $s7\n')
                        if is_float(operators_list[2]):
                            f.write('\t li.s $f16,' + operators_list[1] + '\n')
                            f.write('\tc.eq.s $f16, $'+findekey(f_d, operators_list[2])+'\n')
                            f.write('\tli $' + operators_list[3] + ', 1\n')
                            f.write('\tmove $s7 $' + operators_list[3] + '\n')
                            f.write('\tbc1f makefalse' + str(bc1_counter) + '\n')
                            f.write('endmakefalse' + str(bc1_counter) + ':\n')
                            bc1_counter += 1
                            f.write('\tmove $' + operators_list[3] + ' $s7\n')
                    if '.' in operators_list[2]:
                        if is_float(operators_list[1]):
                            print('Aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
                            f.write('\t li.s $f16,' + operators_list[2] + '\n')
                            f.write('\tc.eq.s $'+findekey(f_d, operators_list[1])+', $f16\n')
                            f.write('\tli $' + operators_list[3] + ', 1\n')
                            f.write('\tmove $s7 $' + operators_list[3] + '\n')
                            f.write('\tbc1f makefalse' + str(bc1_counter) + '\n')
                            f.write('endmakefalse' + str(bc1_counter) + ':\n')
                            bc1_counter += 1
                            f.write('\tmove $' + operators_list[3] + ' $s7\n')
                    if is_float(operators_list[1]) and is_float(operators_list[2]):
                        f.write('\tc.eq.s $' + findekey(f_d, operators_list[1]) + ', $'+ findekey(f_d, operators_list[2])+'\n')
                        f.write('\tli $' + operators_list[3] + ', 1\n')
                        f.write('\tmove $s7 $' + operators_list[3] + '\n')
                        f.write('\tbc1f makefalse' + str(bc1_counter) + '\n')
                        f.write('endmakefalse' + str(bc1_counter) + ':\n')
                        bc1_counter += 1
                        f.write('\tmove $' + operators_list[3] + ' $s7\n')
                else:
                    if operators_list[1].isdigit() and operators_list[2].isdigit():
                        f.write("\tli $t7 "+operators_list[1]+'\n')
                        f.write("\tli $t6 " + operators_list[2] + '\n')
                        f.write("\tseq $"+operators_list[3]+', $t7, $t6\n')
                    elif operators_list[1].isdigit() and not operators_list[2].isdigit():
                        f.write("\tli $t7 " + operators_list[1] + '\n')
                        f.write("\tseq $" + operators_list[3] + ', $t7, $'+findekey(s, operators_list[2])+'\n')
                    elif not operators_list[1].isdigit() and operators_list[2].isdigit():
                        f.write("\tli $t7 " + operators_list[2] + '\n')
                        f.write("\tseq $" + operators_list[3] + ', $'+findekey(s, operators_list[1])+', $t7\n')
                    elif not operators_list[1].isdigit() and not operators_list[2].isdigit():
                        f.write("\tseq $" + operators_list[3] + ', $' + findekey(s, operators_list[1]) + ', $'+findekey(s, operators_list[2])+'\n')
            elif (operators_list[0] == 'and' or operators_list[0] == 'or'):
                f.write('\t' + operators_list[0] + ' $' + operators_list[3] + ', $' + operators_list[1] + ', $' + operators_list[2] + '\n')
            elif (operators_list[0]=='not'):
                f.write('\txori $' + operators_list[2] + ', $' + operators_list[1] + ', 1' + '\n')
            elif operators_list[0] == "IF":
                count = count+1
                #f.write('start'+operators_list[3]+':\n')
                if if_flag:
                    if_flag = False
                    f.write('\tbeq $'+operators_list[1]+', $0, END' + operators_list[3] + '\n')
                    f.write('\tli $t9 1\n')
                    f.write('\tbeq $'+operators_list[1]+', $t9, ' + operators_list[3] + '\n')
                f.write('END'+operators_list[3]+':\n')
            elif operators_list[0] == 'GOTO':
                if operators_list[1]=='after_if':
                    f.write("\tj END"+scope+'\n')
                if operators_list[1]=='start_if':
                    f.write('\tj start_'+scope+'\n')
            elif operators_list[0] == 'Call':
                tmp_array = []
                need_to_returninto.append(operators_list[len(operators_list)-1])
                for i in range(len(operators_list)):
                    if i != 0 and i!=1 and i!=len(operators_list)-1:
                        tmp_array.append(operators_list[i])
                if len(tmp_array)==1:
                    if not operators_list[2].isdigit():
                        f.write('\t move $a1, $'+findekey(s, tmp_array[0])+'\n')
                        f.write('\t jal '+operators_list[1]+'\n')
                        #f.write('end'+operators_list[1]+':\n')
                if len(tmp_array)==2:
                    if not operators_list[2].isdigit():
                        f.write('\t move $a1, $'+findekey(s, tmp_array[0])+'\n')
                        f.write('\t move $a2, $' + findekey(s, tmp_array[1]) + '\n')
                        f.write('\t jal '+operators_list[1]+'\n')
                        #f.write('end'+operators_list[1]+':\n')
                if len(tmp_array)==3:
                    if not operators_list[2].isdigit():
                        f.write('\t move $a1, $'+findekey(s, tmp_array[0])+'\n')
                        f.write('\t move $a2, $' + findekey(s, tmp_array[1]) + '\n')
                        f.write('\t move $a3, $' + findekey(s, tmp_array[2]) + '\n')
                        f.write('\t jal '+operators_list[1]+'\n')
                        #f.write('end'+operators_list[1]+':\n')
            elif operators_list[0] == 'Dec':
                if now_scope!='main':
                    if not is_contained(s,operators_list[1]):
                        print('я заношу - ' + operators_list[1])
                        for kis in s:
                            print(s[kis])
                            if s[kis] == '':
                                print(operators_list[1])
                                s[kis] = operators_list[1]
                                counter_s.append(kis)
                                break
                            if s[kis] == operators_list[1]:
                                break
                    f.write('\tmove $' + findekey(s, operators_list[1]) + ', $a' + str(len(counter_s)) + '\n')
            elif operators_list[0] == 'return':
                print('Возвращает в '+str(need_to_returninto))
                f.write('\tmove $'+need_to_returninto.pop()+', $'+operators_list[1]+'\n')
                f.write('\tjr      $ra\n')
                #f.write('\tj end'+now_scope+'\n')
            elif operators_list[0] == 'continue':
                tm_array1 = []
                for i in tac:
                    tm_array1.append(i)
                for i in range(len(tm_array1)):
                    if scope in tm_array1[i]:
                        f.write('\tj start_'+tm_array1[i-1]+'\n')
                tm_array1.clear()
            elif operators_list[0] == 'break':
                tm_array1 = []
                for i in tac:
                    tm_array1.append(i)
                for i in range(len(tm_array1)):
                    if scope in tm_array1[i]:
                        f.write('\tj END' + tm_array1[i - 1] + '\n')
                tm_array1.clear()
            # elif operators_list[0] == 'start_assign':
            #     f.write('start_assign'+str(toomcuh_counter)+':\n')
            #     toomcuh_counter = toomcuh_counter+1
        counter_s.clear()
        f.write('\tj END\n')
    i = 0
    while i < bc1_counter:
        f.write("makefalse"+str(i)+":\n")
        f.write("\tli $s7, 0\n")
        f.write("\tj endmakefalse"+str(i)+"\n")
        i += 1
    f.write("END:\n")
    f.write(_data)

    f.close()
translate(tac)
