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


#def p_expression_not(p):
#    'expression : expression NOT term'
#    p[0] = (p[1], ('~', p[3]))


def p_expression_term(p):
    'expression : term'
    p[0] = p[1]


#def p_expression_not_term(p):
#    'expression : NOT term'
#    p[0] = ('~', p[2])


def p_term_not(p):
    'expression : term NOT factor'
    p[0] = (p[1], ('~', p[3]))


def p_term_or(p):
    'term : term OR factor'
    #p[0] = p[1] or p[3]
    p[0] = ('|', p[1], p[3])


def p_term_and(p):
    'term : term AND factor'
    #p[0] = p[1] and p[3]
    p[0] = ('&', p[1], p[3])


def p_term_implies(p):
    'term : term IMPLIES factor'
    p[0] = ('|', ('~', p[1]), p[3])



def p_term_factor(p):
   'term : factor'
   p[0] = p[1]


def p_term_not_factor(p):
   'term : NOT factor'
   p[0] = ('~', p[2])


def p_factor_id(p):
    'factor : ID'
    p[0] = p[1]

def p_factor_not_id(p):
    'factor : NOT ID'
    p[0] = ('~', p[2])


def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]


def p_empty(p):
    'empty :'
    pass


def p_error(p):
    print "Syntax error at '%s'" % p.value


def to_cnf(knowledge_base):
    KB_CNF = []
    for each_kb in knowledge_base:
        if each_kb[0] != 'single':
            #do something
            print each_kb
        else:
            KB_CNF.append(each_kb)
    return KB_CNF



if __name__ == "__main__":
    input = read_input()
    processed_input = sperate_input(input)
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
    lexer = lex.lex(debug=1)
    yacc.yacc()
    for each_line in kb_original:
        #print "number " + str(kb_original.index(each_line)) + " : " + each_line
        kb.append(yacc.parse(each_line))
    for each in kb:
        if not isinstance(each, tuple):
            kb[kb.index(each)] = ('single', each)
    kb_cnf = to_cnf(kb)
    print kb
