from ply import lex, yacc
import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter

# Define reserved words
reserved = {
    'int': 'INT',
    'main': 'MAIN',
    'do': 'DO',
    'while': 'WHILE',
    'if': 'IF',
    'return': 'RETURN',
    'string': 'STRING',
    'interface': 'Interface',
}

tokens = [
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'SEMI',
    'NUMBER',
    'ASSIGN',
    'ID',
    'GT',
    'LT',
    'DOUBLESTRING',
    'PLUS',
    'MINUS',
    'MULTIPLY',
    'DIVIDE',
    'INTEGER',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'DOT',
    'EXCLAMATION',
    'COLON',
    'BACKSLASH'
] + list(reserved.values())

t_GT = r'>'
t_LT = r'<'
t_DOUBLESTRING = r'"[^"]*"'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_SEMI = r';'
t_ASSIGN = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COMMA = r','
t_DOT = r'\.'
t_EXCLAMATION = r'!'
t_COLON = r':'
t_BACKSLASH = r'\\'

token_to_spanish = {
    'LPAREN': 'Paréntesis Abre',
    'RPAREN': 'Paréntesis Cierra',
    'LBRACE': 'Llave Abre',
    'RBRACE': 'Llave Cierra',
    'SEMI': 'Punto y Coma',
    'ASSIGN': 'Igual',
    'PLUS': 'Más',
    'MINUS': 'Menos',
    'MULTIPLY': 'Multiplica',
    'DIVIDE': 'Divide',
    'LBRACKET': 'Corchete Abre',
    'RBRACKET': 'Corchete Cierra',
    'COMMA': 'Coma',
    'DOT': 'Punto',
    'EXCLAMATION': 'Exclamación',
    'BACKSLASH': 'Barra Inversa',
}

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

def t_INTEGER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t\n'

def t_error(t):
    error_table.insert('', 'end', values=(t.lineno, t.lexpos, f"Illegal character '{t.value[0]}'", '-', '-'))
    t.lexer.skip(1)

lexer = lex.lex()

def p_program(p):
    'program : INT MAIN LPAREN RPAREN LBRACE declarations do_while_loop RETURN INTEGER SEMI RBRACE'

def p_declarations(p):
    'declarations : INT ID ASSIGN INTEGER SEMI STRING ID ASSIGN DOUBLESTRING SEMI'
    global user_value
    user_value = p[2]
    print("user value", user_value)

def p_do_while_loop(p):
    'do_while_loop : DO LBRACE if_clause RBRACE WHILE LPAREN condition RPAREN SEMI'

def p_if_clause(p):
    '''if_clause : IF LPAREN condition RPAREN LBRACE ID ASSIGN INTEGER SEMI RBRACE
                 | IF LPAREN condition RPAREN LBRACE ID ASSIGN INTEGER SEMI if_clause RBRACE'''
    print("dd")
    print(p[6])

def p_condition(p):
    '''condition : ID LT INTEGER
                 | ID GT INTEGER
                 | ID GT INTEGER GT INTEGER'''
    if p[1] != user_value:
        print("gg2")
        print(p[1])
        error_table.insert('', 'end', values=(p.lineno, p.lexpos, "Error: Variable 'num2' not declared", '-', '-'))

    print("Valor de num1:", user_value )

def p_error(p):
    if p:
        error_table.insert('', 'end', values=(p.lineno, p.lexpos, f"Syntax error at token '{p.value}'", p.type, p.lexpos))
    else:
        error_table.insert('', 'end', values=('-', '-', "Syntax error at EOF", '-', '-'))

parser = yacc.yacc()

symbol_table = set()

def check_code():
    operator_counts = {
        'ASSIGN': 0,
        'PLUS': 0,
        'MINUS': 0,
        'MULTIPLY': 0,
        'DIVIDE': 0,
        'BACKSLASH': 0,
        'EXCLAMATION': 0,
        'LBRACKET': 0,
        'RBRACKET': 0,
        'LBRACE': 0,
        'RBRACE': 0,
        'DOT': 0
    }

    for i in token_table.get_children():
        token_table.delete(i)
    for i in error_table.get_children():
        error_table.delete(i)

    code = txt.get("1.0", tk.END).strip()
    if not code:
        messagebox.showinfo('Resultado', 'No hay código para verificar.')
        return

    symbol_table.clear()

    lexer.input(code)

    for token in lexer:
        if token.type in operator_counts.keys():
            operator_counts[token.type] += 1
        token_table.insert('', 'end', values=(token.lineno, token.type, token.value, token.lexpos + 1))

    for operator, count in operator_counts.items():
        operator_table.insert('', 'end', values=(token_to_spanish.get(operator, operator), count))

    print(f'Found the following operators:')
    for operator, count in operator_counts.items():
        print(f'{operator}: {count}')

    parser.parse(code, lexer=lexer)

root = tk.Tk()
root.geometry('800x600')

frm = tk.Frame(root)
frm.pack(padx=10, pady=10)

lbl = tk.Label(frm, text="Inserta tu código aquí")
lbl.pack()

txt = tk.Text(frm, width=80, height=10)
txt.pack()

token_table = ttk.Treeview(frm)
token_table['columns'] = ('line', 'type', 'value', 'position')
token_table.heading('line', text='Línea')
token_table.heading('type', text='Tipo')
token_table.heading('value', text='Valor')
token_table.heading('position', text='Posición')
token_table.pack()

operator_table = ttk.Treeview(frm)
operator_table['columns'] = ('operator', 'count')
operator_table.heading('operator', text='Operador')
operator_table.heading('count', text='Cantidad')
operator_table.pack()

error_table = ttk.Treeview(frm)
error_table['columns'] = ('line', 'position', 'description', 'character', 'index')
error_table.heading('line', text='Línea')
error_table.heading('position', text='Posición')
error_table.heading('description', text='Descripción')
error_table.heading('character', text='Carácter')
error_table.heading('index', text='Índice')
error_table.pack()

btn = tk.Button(frm, text="Verificar Código", command=check_code)
btn.pack(pady=10)

root.mainloop()
