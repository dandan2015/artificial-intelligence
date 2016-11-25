import ply.lex as lex
import ply.yacc as yacc
import copy


def read_input():
    f = open("input.txt", 'r')
    line = f.readline()
    lines = []
    while line:
        line = line.strip().replace(' ', '')
        if line:
            lines.append(line)
        line = f.readline()
    f.close()
    return lines


def sperate_input(input):
    to_prove_num = int(input[0])
    to_prove = input[1:1+to_prove_num]
    KB_num = int(input[1+to_prove_num])
    KB = input[2+to_prove_num:]
    return to_prove, KB


# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]


def p_term_not(p):
    'expression : term NOT factor'
    p[0] = [p[1], ['~', p[3]]]


def p_term_or(p):
    'term : term OR factor'
    p[0] = ['|', p[1], p[3]]


def p_term_and(p):
    'term : term AND factor'
    p[0] = ['&', p[1], p[3]]


def p_term_implies(p):
    'term : term IMPLIES factor'
    p[0] = ['|', ['~', p[1]], p[3]]


def p_term_factor(p):
   'term : factor'
   p[0] = p[1]


def p_term_not_factor(p):
   'term : NOT factor'
   p[0] = ['~', p[2]]


def p_factor_id(p):
    'factor : ID'
    p[0] = p[1]

def p_factor_not_id(p):
    'factor : NOT ID'
    p[0] = ['~', p[2]]


def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]


def p_empty(p):
    'empty :'
    pass


def p_error(p):
    print "Syntax error at '%s'" % p.value


def to_cnf(sentence):
    sentence = move_not_inwards(sentence)
    sentence = distribute_and_over_or(sentence)
    return sentence


def move_not_inwards(s):
    if s[0] == '~':
        if isinstance(s[1], list):
            if s[1][0] == '~':
                return move_not_inwards(s[1][1])
            if s[1][0] == '&':
                return ['|', move_not_inwards(['~', s[1][1]]), move_not_inwards(['~', s[1][2]])]
            if s[1][0] == '|':
                return ['&', move_not_inwards(['~', s[1][1]]), move_not_inwards(['~', s[1][2]])]
        return s
    elif len(s) == 1 or (s[0] != '&' and s[0] != '|'):
        return s
    else:
        return [s[0], move_not_inwards(s[1]), move_not_inwards(s[2])]


def distribute_and_over_or(s):
    #print "distribute_and_over_or: " + str(s)
    if s[0] == '|':
        if isinstance(s[1], list):
            if s[1][0] == '&':
                return ['&', distribute_and_over_or(['|', s[1][1], s[2]]), distribute_and_over_or(['|', s[1][2], s[2]])]
            if s[1][0] == '~':
                return ['|', distribute_and_over_or(s[1]), distribute_and_over_or(s[2])]
            conj = [s[2]]
            temp = s[1]
            and_detected = False
            while isinstance(temp[1], list):
                if temp[0] == '|':
                    if len(conj) > 1:
                        conj = ['|', conj, temp[2]]
                    else:
                        conj = ['|', conj[0], temp[2]]
                    temp = temp[1]
                elif temp[0] == '&':
                    and_detected = True
                    break
                else:
                    break
            if temp[0] == '|':
                if len(conj) > 1:
                    conj = ['|', conj, temp[2]]
                else:
                    conj = ['|', conj[0], temp[2]]
            elif temp[0] == '&':
                and_detected = True
            #print "conj: " + str(conj)
            if and_detected:
                return ['&', distribute_and_over_or(['|', conj, temp[1]]), distribute_and_over_or(['|', conj, temp[2]])]
            else:
                return s
        return s
    elif s[0] == '&':
        return ['&', distribute_and_over_or(s[1]), distribute_and_over_or(s[2])]
    else:
        return s


def divid_and_in_kb(KB):
    kb_separate = []
    changed = False
    for each_kb in KB:
        if each_kb[0] == '&':
            changed = True
            if isinstance(each_kb[1], list):
                kb_separate.append(each_kb[1])
            else:
                kb_separate.append([each_kb[1]])
            if isinstance(each_kb[2], list):
                kb_separate.append(each_kb[2])
            else:
                kb_separate.append([each_kb[2]])
        else:
            kb_separate.append(each_kb)
    return kb_separate, changed


def pl_resolution(KB, alpha):
    if len(alpha) == 1:
        add_clause = to_cnf(['~', alpha[0]])
    else:
        add_clause = to_cnf(['~', alpha])
    new_kb = copy.deepcopy(KB)
    if not isinstance(new_kb[0],list):
        new_kb = [new_kb]
    if isinstance(add_clause, list):
        new_kb.append(add_clause)
    else:
        new_kb.append([add_clause])
    #print "add_clause: " + str(add_clause)
    #print "new_kb: " + str(new_kb)
    new = []
    while True:
        n = len(new_kb)
        pairs = [(new_kb[i], new_kb[j])
                 for i in range(n) for j in range(i + 1, n)]
        #print "pairs: " + str(pairs)
        for (ci, cj) in pairs:
            #print
            #print "dealing with pair:" + str(ci) + " and " + str(cj)
            resolvents = pl_resolve(ci, cj)
            #print "resolvents: " + str(resolvents)
            if [] in resolvents:
                return True
            for e in resolvents:
                #print "putting: " + str(e)
                if len(e) != 0:
                    if e not in new:
                        new.append(e)

        already_exist = True
        #print "new: " + str(new)
        for each_new in new:
            if each_new not in new_kb:
                already_exist = False
        #print "already_exist: " + str(already_exist)
        if already_exist:
            #print "terminate for already_exist"
            return False
        for c in new:
            if c not in new_kb:
                new_kb.append(list(c))


def pl_resolve(clause_i, clause_j):#, pairs):
    #print "resolving " + str(clause_i) + " and " + str(clause_j)
    clauses = []
    disjuncts_i = disjunction(clause_i, [])
    disjuncts_j = disjunction(clause_j, [])
    #print "Initial"
    #print "disjuncts_i " + str(disjuncts_i)
    #print "disjuncts_j " + str(disjuncts_j)
    if len(disjuncts_i) == 2 and not isinstance(disjuncts_i[0], list) and disjuncts_i[0] == '~':
        disjuncts_i = [disjuncts_i]
    if len(disjuncts_j) == 2 and not isinstance(disjuncts_j[0], list) and disjuncts_j[0] == '~':
        disjuncts_j = [disjuncts_j]
    for d_i in disjuncts_i:
        for d_j in disjuncts_j:
            first = d_i
            second = d_j
            first_not = False
            second_not = False
            unify_dic = {}
            if isinstance(d_i, list) and d_i[0] == '~':
                if isinstance(d_i[1], str):
                    first_not = True
                    first =  d_i[1]
            if isinstance(d_j, list) and d_j[0] == '~':
                if isinstance(d_j[1], str):
                    second_not = True
                    second = d_j[1]
            if isinstance(first, str) and isinstance(second, str):
                #print "first: " + first
                #print "second: " + second
                unify_result = unify_two_sentence(first, second, {})
                if first_not:
                    first = ['~', unify_result[0]]
                else:
                    first = unify_result[0]
                if second_not:
                    second = ['~', unify_result[1]]
                else:
                    second = unify_result[1]
                unify_dic = unify_result[2]

            if first == to_cnf(['~', second]) or to_cnf(['~', first]) == second:
            #if d_i == to_cnf(['~', d_j]) or to_cnf(['~', d_i]) == d_j:
                #print "YES"
                dis_i = copy.deepcopy(disjuncts_i)
                dis_j = copy.deepcopy(disjuncts_j)
                dis_i.remove(d_i)
                dis_j.remove(d_j)
                for each_i in dis_i:
                    ea = each_i
                    ea_not = False
                    if isinstance(ea, list) and ea[0] == '~':
                        if isinstance(ea[1], str):
                            ea_not = True
                            ea = ea[1]
                    if isinstance(ea, str):
                        ea_func_paras = access_func_paras(ea)
                        ea_paras = ea_func_paras[1]
                        for ea_para in ea_paras:
                            if ea_para[0].islower() and ea_para in unify_dic.keys():
                                ea_paras[ea_paras.index(ea_para)] = unify_dic[ea_para]
                        #ea_func_paras[1] = ea_paras
                        ea = resemble_into_sentence([ea_func_paras[0], ea_paras])
                    if ea_not:
                        dis_i[dis_i.index(each_i)] = ['~', ea]
                    else:
                        dis_i[dis_i.index(each_i)] = ea

                for each_j in dis_j:
                    ea = each_j
                    ea_not = False
                    if isinstance(ea, list) and ea[0] == '~':
                        if isinstance(ea[1], str):
                            ea_not = True
                            ea = ea[1]
                    if isinstance(ea, str):
                        ea_func_paras = access_func_paras(ea)
                        ea_paras = ea_func_paras[1]
                        for ea_para in ea_paras:
                            if ea_para[0].islower() and ea_para in unify_dic.keys():
                                ea_paras[ea_paras.index(ea_para)] = unify_dic[ea_para]
                        #ea_func_paras[1] = ea_paras
                        ea = resemble_into_sentence([ea_func_paras[0], ea_paras])
                    if ea_not:
                        dis_j[dis_j.index(each_j)] = ['~', ea]
                    else:
                        dis_j[dis_j.index(each_j)] = ea



                new_clause = []
                i = 0
                for horn in dis_i:
                    if i == 0:
                        if len(horn) == 1:
                            new_clause.append(horn[0])
                        else:
                            new_clause.append(horn)
                    else:
                        if len(horn) == 1:
                            if len(new_clause) == 1:
                                new_clause = ['|', new_clause[0], horn[0]]
                            else:
                                new_clause = ['|', new_clause, horn[0]]
                        else:
                            if len(new_clause) == 1:
                                new_clause = ['|', new_clause[0], horn]
                            else:
                                new_clause = ['|', new_clause, horn]

                    i += 1
                for horn in dis_j:
                    if horn not in dis_i:
                        if i == 0:
                            if len(horn) == 1:
                                new_clause.append(horn[0])
                            else:
                                new_clause.append(horn)
                        else:
                            if len(horn) == 1:
                                if len(new_clause) == 1:
                                    new_clause = ['|', new_clause[0], horn[0]]
                                else:
                                    new_clause = ['|', new_clause, horn[0]]
                            else:
                                if len(new_clause) == 1:
                                    new_clause = ['|', new_clause[0], horn]
                                else:
                                    new_clause = ['|', new_clause, horn]
                    i += 1
                if len(new_clause) == 1:
                    if isinstance(new_clause[0], list):
                        #print "new_clause: " + str(new_clause[0])
                        clauses.append(new_clause[0])
                    else:
                        #print "new_clause: " + str(new_clause)
                        clauses.append(new_clause)
                else:
                    #print "new_clause: " + str(new_clause)
                    clauses.append(new_clause)
    return clauses


def disjunction(c, disjunct):
    #print "disjucting " + str(c)
    if c[0] == '|':
        if isinstance(c[1], list) and c[1][0] == '|':
                disjunction(c[1], disjunct)
        else:
            disjunct.append(disjunction(c[1], disjunct))
        if isinstance(c[2], list) and c[2][0] == '|':
                disjunction(c[2], disjunct)
        else:
            disjunct.append(disjunction(c[2], disjunct))
    else:
        return c

    return disjunct


def unify_two_sentence(s_1, s_2, dic):
    sen_1 = access_func_paras(s_1)
    sen_2 = access_func_paras(s_2)
    if sen_1[0] == sen_2[0] and len(sen_1[1]) == len(sen_2[1]):
        #print "func same"
        for i in range(0, len(sen_1[1])):
            if sen_1[1][i] != sen_2[1][i]:
                #print "index " + str(i) + " need unify: " + str(sen_1[1][i]) + " and " + sen_2[1][i]
                if sen_1[1][i][0].islower() and sen_2[1][i][0].isupper():
                    #print "case 1"
                    dic[sen_1[1][i]] = sen_2[1][i]
                elif sen_1[1][i][0].isupper() and sen_2[1][i][0].islower():
                    #print "case 2"
                    dic[sen_2[1][i]] = sen_1[1][i]
                elif sen_1[1][i][0].islower() and sen_2[1][i][0].islower():
                    continue
                else:
                    return s_1, s_2, dic
            elif sen_1[1][i] == sen_2[1][i] and sen_1[1][i][0].islower() and sen_2[1][i][0].islower():
                continue
            else:
                return s_1, s_2, dic
        for i in range(0, len(sen_1[1])):
            if sen_1[1][i][0].islower() and sen_1[1][i] in dic.keys():
                sen_1[1][i] = dic[sen_1[1][i]]
            if sen_2[1][i][0].islower() and sen_2[1][i] in dic.keys():
                sen_2[1][i] = dic[sen_2[1][i]]
        #print "sen_1: " + str(sen_1)
        #print "sen_2: " + str(sen_2)
        s_1 = resemble_into_sentence(sen_1)
        s_2 = resemble_into_sentence(sen_2)
        return s_1, s_2, dic
        #return unify_two_sentence(s_1, s_2, dic)

    else:
        return s_1, s_2, dic


def access_func_paras(s):
    s = s[:-1]
    func_name = s.split('(')[0]
    paras = s.split('(')[1].split(',')
    return func_name, paras


def resemble_into_sentence(sen):
    func = sen[0]
    paras = sen[1]
    resemble = func + '(' + ','.join(paras) + ')'
    return resemble


if __name__ == "__main__":
    input_file = read_input()
    processed_input = sperate_input(input_file)
    need_prove = processed_input[0]
    kb_original = processed_input[1]
    need_prove_pool = []
    kb = []
    tokens = (
        'ID',
        'LPAREN',
        'RPAREN',
        'NOT',
        'OR',
        'AND',
        'IMPLIES'
    )
    # Regular expression rules for simple tokens
    t_ID = r'[A-Za-z]+\(([A-Za-z]+){1}((,){1}([A-Za-z]+){1})*\)'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_NOT = r'\~'
    t_OR = r'\|'
    t_AND = r'\&'
    t_IMPLIES = r'\=>'
    # Build the lexer
    lexer = lex.lex()
    yacc.yacc()
    for each_need_prove in need_prove:
        need_prove_pool.append(yacc.parse(each_need_prove))
    for each_line in kb_original:
        kb.append(yacc.parse(each_line))
    for each in kb:
        if not isinstance(each, list):
            kb[kb.index(each)] = [each]
    kb_cnf = []
    for each_kb in kb:
        #print "number " + str(kb.index(each_kb))
        #print "start processing: " + str(each_kb)
        each_kb = to_cnf(each_kb)
        #print "processed result:" + str(each_kb)
        #print
        kb_cnf.append(each_kb)
    kb_and_separate_result = divid_and_in_kb(kb_cnf)
    if kb_and_separate_result[1]:
        kb_and_separate_result = divid_and_in_kb(kb_cnf)
    kb_and_separate = kb_and_separate_result[0]
    #print "kb:"
    #for each in kb_and_separate:
    #    print each
    out = open('output.txt', 'w')
    for each_need_prove in need_prove_pool:
        print "result for # " + str(need_prove_pool.index(each_need_prove))
        out.write(str(pl_resolution(kb_and_separate, each_need_prove)))
        out.write("\n")
    out.close()

    #print pl_resolve(['H(x)'], ['~', 'H(x)'])

    #print pl_resolution(['|', ['~', 'A(x)'], 'H(Tom)'], ['|', ['|', 'G(x)', ['~', 'B(x)']], ['~', 'H(x)']])
    #print pl_resolution([['|', ['~', 'A(x)'], 'H(x)'], ['A(x)']], ['H(x)'])
    #print unify_two_sentence('A(x)', 'A(x)', {})
    #print unify_two_sentence('A(x,John,t)', 'A(Tom,y,q)', {})
    #access_func_paras('A(xew, ywqe, zew)')
    #resemble_into_sentence('Ah',['x','y', 'swd'])
