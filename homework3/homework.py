import ply.lex as lex
import ply.yacc as yacc


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
    """Given a sentence s consisting of conjunctions and disjunctions
        of literals, return an equivalent sentence in CNF.
        >>> distribute_and_over_or((A & B) | C)
        ((A | C) & (B | C))"""
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


if __name__ == "__main__":
    input_file = read_input()
    processed_input = sperate_input(input_file)
    need_prove = processed_input[0]
    kb_original = processed_input[1]
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
    for each_line in kb_original:
        kb.append(yacc.parse(each_line))
    for each in kb:
        if not isinstance(each, list):
            kb[kb.index(each)] = [each]
    kb_cnf = []
    for each_kb in kb:
        print "number " + str(kb.index(each_kb))
        print "start processing: " + str(each_kb)
        each_kb = to_cnf(each_kb)
        print "processed result:" + str(each_kb)
        print
        kb_cnf.append(each_kb)
    #print kb
