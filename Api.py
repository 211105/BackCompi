from flask import Flask, request, jsonify, session
from flask_session import Session
from flask_cors import CORS
from flask_redis import FlaskRedis
from collections import Counter
from librouteros import connect
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['SECRET_KEY'] = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['REDIS_URL'] = 'redis://localhost:6379/0'  # Configura la URL de Redis
Session(app)

# Configurar FlaskRedis
redis_store = FlaskRedis(app)

reserved = {
    'int': 'INT',
    'main': 'MAIN',
    'do': 'DO',
    'while': 'WHILE',
}
# Tokens
tokens = (
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
    'BACKSLASH',
    # Palabras reservadas
    'IF',
    'ELSE',
    'WHILE'
)

# Operadores
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

# Ignorar espacios y tabulaciones
t_ignore  = ' \t'

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t


# Regla de error
def t_error(t):
    print("Carácter ilegal '%s'" % t.value[0])
    t.lexer.skip(1)

# Construir lexer
lexer = lex.lex()

# Reglas de parseo
def p_expression_plus(p):
    'expression : expression PLUS term'
    p[0] = p[1] + p[3]

def p_expression_minus(p):
    'expression : expression MINUS term'
    p[0] = p[1] - p[3]

def p_expression_term(p):
    'expression : term'
    p[0] = p[1]

def p_term_times(p):
    'term : term MULTIPLY factor'
    p[0] = p[1] * p[3]

def p_term_divide(p):
    'term : term DIVIDE factor'
    if p[3] == 0:
        print("No se puede dividir entre cero!")
        p[0] = 1
    else:
        p[0] = p[1] / p[3]

def p_term_factor(p):
    'term : factor'
    p[0] = p[1]

def p_factor_num(p):
    'factor : NUMBER'
    p[0] = p[1]

def p_factor_expr(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]

# Regla de error para yacc
def p_error(p):
    print("Error de sintaxis en '%s'" % p.value)

# Construir parser
parser = yacc.yacc()

# Palabras reservadas


app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config['SECRET_KEY'] = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

    
    
def connect_to_mikrotik(ip, username, password):
    try:
        connection = connect(username=username, password=password, host=ip, port=8728)
        return connection
    except Exception as e:
        return None



@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    ip_address = data.get('ip_address')

    if not username or not password or not ip_address:
        return jsonify({"message": "Se requiere el username, password y IP address."}), 400

    session['connection_info'] = {
        'username': username,
        'password': password,
        'ip': ip_address
    }

    return jsonify({"message": "login successful"})


    


import traceback

@app.route('/command', methods=['POST'])
def send_command():
    if 'connection_info' not in session:
        return jsonify({"message": "No se ha iniciado sesión"}), 401

    command = request.get_json().get('command')
    if not command:
        return jsonify({"message": "Se requiere un comando."}), 400

    connection_info = session['connection_info']
    connection = connect(username=connection_info['username'], 
                         password=connection_info['password'],
                         host=connection_info['ip'], 
                         port=8728)
    
    response_generator = connection(cmd=command)

    try:
        response_list = []
        for item in response_generator:
            response_list.append(item)
    except Exception as e:
        print("Error while reading response:", str(e))  # Imprime la excepción en la consola del servidor
        return jsonify({"message": "Error al leer la respuesta del dispositivo", "error": str(e)}), 500








@app.route('/parse_code', methods=['POST'])
def parse_code():
    code = request.json.get('code', '')
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    lexer.input(code)

    token_counts = Counter()
    token_examples = {}

    for token in lexer:
        token_counts[token.type] += 1
        if token.type not in token_examples:
            token_examples[token.type] = token.value

    result = parser.parse(code)

    tokens_dict = {k: [v, token_examples[k]] for k, v in token_counts.items()}

    return jsonify({'result': result, 'tokens': tokens_dict})

@app.route('/token_info', methods=['POST'])
def get_token_info():
    code = request.json.get('code', '')
    if not code:
        return jsonify({'error': 'No code provided'}), 400

    lexer.input(code)

    # Lista para almacenar los tokens
    tokens_list = []

    for token in lexer:
        tokens_list.append({
            'line': token.lineno, 
            'type': token.type, 
            'value': token.value, 
            'position': token.lexpos
        })

    return jsonify({'tokens': tokens_list})


if __name__ == '__main__':
    app.run(port=5000, debug=True)
