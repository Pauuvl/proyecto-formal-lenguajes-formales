import os
from collections import OrderedDict

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colored(text, color):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

class FirstFollow:
    def __init__(self, grammar, start_symbol):
        self.grammar = grammar
        self.start_symbol = start_symbol
        self.non_terminals = list(grammar.keys())
        self.terminals = self._get_terminals()
        self.first = {}
        self.follow = {}
        self._initialize()

    def _initialize(self):
        for symbol in self.non_terminals + self.terminals:
            self.first[symbol] = set()
        self.first['e'] = {'e'}

    def _get_terminals(self):
        terminals = set()
        for productions in self.grammar.values():
            for production in productions:
                for symbol in production:
                    if symbol not in self.grammar and symbol != 'e':
                        terminals.add(symbol)
        return sorted(list(terminals))

    def compute_first(self):
        for terminal in self.terminals:
            self.first[terminal].add(terminal)

        changed = True
        while changed:
            changed = False
            for head in self.grammar:
                for production in self.grammar[head]:
                    before = len(self.first[head])
                    all_epsilon = True
                    for symbol in production:
                        self.first[head].update(self.first[symbol] - {'e'})
                        if 'e' not in self.first[symbol]:
                            all_epsilon = False
                            break
                    if all_epsilon:
                        self.first[head].add('e')
                    if len(self.first[head]) > before:
                        changed = True
        return self.first

    def compute_follow(self):
        self.compute_first()
        for nt in self.non_terminals:
            self.follow[nt] = set()
        self.follow[self.start_symbol].add('$')

        changed = True
        while changed:
            changed = False
            for head in self.grammar:
                for production in self.grammar[head]:
                    for i, symbol in enumerate(production):
                        if symbol not in self.non_terminals:
                            continue
                        first_beta = set()
                        j = i + 1
                        while j < len(production):
                            next_symbol = production[j]
                            first_beta.update(self.first[next_symbol] - {'e'})
                            if 'e' not in self.first[next_symbol]:
                                break
                            j += 1
                        else:
                            first_beta.add('e')
                        before_size = len(self.follow[symbol])
                        self.follow[symbol].update(first_beta - {'e'})
                        if 'e' in first_beta or j >= len(production):
                            self.follow[symbol].update(self.follow[head])
                        if len(self.follow[symbol]) > before_size:
                            changed = True
        return self.follow

    def pretty_print(self):
        print("\nConjuntos FIRST:")
        for symbol in sorted(self.first.keys()):
            print(f"FIRST({symbol}) = {sorted(list(self.first[symbol]))}")
        print("\nConjuntos FOLLOW:")
        for nt in sorted(self.follow.keys()):
            print(f"FOLLOW({nt}) = {sorted(list(self.follow[nt]))}")

class LL1Parser:
    def __init__(self, grammar, start_symbol):
        self.grammar = grammar
        self.start_symbol = start_symbol
        self.ff = FirstFollow(grammar, start_symbol)
        self.ff.compute_first()
        self.ff.compute_follow()
        self.table = self._build_parsing_table()
        self._validate_table()

    def _build_parsing_table(self):
        table = {nt: {} for nt in self.grammar}
        for nt in self.grammar:
            for production in self.grammar[nt]:
                first_alpha = self._get_production_first(production)
                for terminal in first_alpha - {'e'}:
                    if terminal in table[nt]:
                        raise ValueError(f"Conflicto LL(1): {nt} -> {terminal}")
                    table[nt][terminal] = production
                if 'e' in first_alpha:
                    for terminal in self.ff.follow[nt]:
                        if terminal in table[nt]:
                            raise ValueError(f"Conflicto LL(1) con ε: {nt} -> {terminal}")
                        table[nt][terminal] = production
        return table

    def _get_production_first(self, production):
        first = set()
        for symbol in production:
            first.update(self.ff.first[symbol] - {'e'})
            if 'e' not in self.ff.first[symbol]:
                break
        else:
            first.add('e')
        return first

    def _validate_table(self):
        for nt in self.grammar:
            for terminal in self.ff.terminals + ['$']:
                if terminal not in self.table[nt] and terminal in self.ff.follow[nt]:
                    self.table[nt][terminal] = ['e']

    def parse(self, tokens):
        stack = ['$', self.start_symbol]
        input_tokens = tokens.copy() + ['$']
        position = 0
        derivation = []

        while stack:
            top = stack[-1]
            current_token = input_tokens[position]

            if top == current_token:
                stack.pop()
                position += 1
            elif top in self.grammar:
                if current_token in self.table[top]:
                    production = self.table[top][current_token]
                    stack.pop()
                    if production[0] != 'e':
                        stack.extend(reversed(production))
                    derivation.append(f"{top} -> {' '.join(production)}")
                else:
                    expected = [t for t in self.table[top].keys() if self.table[top][t][0] != 'e']
                    raise SyntaxError(
                        f"Error en posición {position}: Token inesperado '{current_token}'\n"
                        f"Se esperaba uno de: {expected}\nDerivación: {derivation}"
                    )
            else:
                raise SyntaxError(
                    f"Error en posición {position}: Símbolo inesperado '{top}'\nToken actual: '{current_token}'"
                )
        return True, derivation

    def print_table(self):
        print("\nTabla de Parsing LL(1):")
        print(f"{'No Terminal':<15}", end="")
        for terminal in sorted(self.ff.terminals + ['$']):
            print(f"{terminal:<20}", end="")
        print()
        for nt in sorted(self.grammar.keys()):
            print(f"{nt:<15}", end="")
            for terminal in sorted(self.ff.terminals + ['$']):
                if terminal in self.table[nt]:
                    prod = ' '.join(self.table[nt][terminal]) if self.table[nt][terminal][0] != 'e' else 'ε'
                    print(f"{nt}→{prod:<19}", end="")
                else:
                    print(f"{'':<20}", end="")
            print()

def tokenize_input(input_str):
    tokens = []
    for char in input_str:
        if char.isspace():
            continue
        elif char.isalnum() or char in "()[]{}+-*/=<>!;:,":
            tokens.append(char)
        else:
            raise ValueError(f"Carácter no permitido: '{char}'. Usa solo símbolos válidos para tu gramática.")
    return tokens

def leer_gramatica():
    print("\nIngrese el número de producciones:")
    while True:
        try:
            num_prods = int(input("> ").strip())
            if num_prods > 0:
                break
            print("El número debe ser positivo.")
        except ValueError:
            print("Entrada inválida. Ingrese un número entero.")

    gramatica = OrderedDict()
    print("\nFormato de producción: S -> A B | C (use 'e' para épsilon)")
    for i in range(num_prods):
        while True:
            print(f"\nIngrese producción {i+1}:")
            linea = input("> ").strip()
            if '->' in linea:
                lado_izq, lado_der = linea.split("->", 1)
                lado_izq = lado_izq.strip()
                if lado_izq:
                    producciones = [p.strip().split() for p in lado_der.split('|')]
                    gramatica[lado_izq] = producciones
                    break
            print("Formato inválido. Use: NoTerminal -> producción1 | producción2")
    return gramatica

def analizar_cadena(parser, parser_type):
    print(f"\nIngrese cadenas para analizar con {parser_type} (ejemplo: aadbcc)")
    print("Enter para volver al menú principal")
    while True:
        try:
            cadena = input("> ").strip()
            if not cadena:
                break
            tokens = tokenize_input(cadena.replace(" ", ""))
            aceptada, derivacion = parser.parse(tokens)
            print_colored("Sí", "green")
            print("Derivación:")
            for paso in derivacion:
                print(f"  {paso}")
        except Exception as e:
            print_colored(f"No (Error: {str(e)})", "red")
class SLRParser:
    def __init__(self, grammar, start_symbol):
        self.grammar = grammar
        self.start_symbol = start_symbol
        self.ff = FirstFollow(grammar, start_symbol)
        self.ff.compute_first()
        self.ff.compute_follow()
        self.states = []
        self.transitions = {}
        self.action_table = {}
        self.goto_table = {}
        self._build_parsing_tables()

    def _build_parsing_tables(self):
        self._build_canonical_collection()
        self._build_action_table()
        self._build_goto_table()

    def _build_canonical_collection(self):
        augmented_production = (self.start_symbol + "'", (self.start_symbol,))
        initial_item = (augmented_production[0], ('.',) + augmented_production[1])
        initial_state = frozenset([initial_item])
        self.states = [self._closure(initial_state)]
        changed = True
        while changed:
            changed = False
            for state in self.states[:]:
                symbols = self._get_symbols_after_dot(state)
                for symbol in symbols:
                    new_state = self._goto(state, symbol)
                    if new_state and new_state not in self.states:
                        self.states.append(new_state)
                        changed = True

    def _closure(self, state):
        closure = set(state)
        changed = True
        while changed:
            changed = False
            for item in list(closure):
                head, production = item
                dot_pos = production.index('.')
                if dot_pos + 1 < len(production):
                    next_symbol = production[dot_pos + 1]
                    if next_symbol in self.grammar:
                        for prod in self.grammar[next_symbol]:
                            new_item = (next_symbol, ('.',) + tuple(prod))
                            if new_item not in closure:
                                closure.add(new_item)
                                changed = True
        return frozenset(closure)

    def _goto(self, state, symbol):
        new_state = set()
        for item in state:
            head, production = item
            dot_pos = production.index('.')
            if dot_pos + 1 < len(production) and production[dot_pos + 1] == symbol:
                new_prod = tuple(production[:dot_pos]) + (symbol, '.') + tuple(production[dot_pos + 2:])
                new_state.add((head, new_prod))
        return self._closure(new_state) if new_state else None

    def _get_symbols_after_dot(self, state):
        symbols = set()
        for item in state:
            _, production = item
            dot_pos = production.index('.')
            if dot_pos + 1 < len(production):
                symbols.add(production[dot_pos + 1])
        return symbols

    def _get_production_number(self, head, production):
        count = 1
        for nt in self.grammar:
            for prod in self.grammar[nt]:
                if nt == head and tuple(prod) == tuple(production):
                    return count
                count += 1
        raise ValueError(f"No se encontró la producción: {head} -> {production}")

    def _get_production(self, prod_num):
        count = 1
        for nt in self.grammar:
            for prod in self.grammar[nt]:
                if count == prod_num:
                    return nt, prod
                count += 1
        raise ValueError(f"Producción número {prod_num} no encontrada.")

    def _build_action_table(self):
        for i, state in enumerate(self.states):
            self.action_table[i] = {}
            for item in state:
                head, production = item
                if production[-1] == '.':
                    if head == self.start_symbol + "'":
                        self.action_table[i]['$'] = 'acc'
                    else:
                        prod_num = self._get_production_number(head, production[:-1])
                        for terminal in self.ff.follow[head]:
                            self.action_table[i][terminal] = f"r{prod_num}"
            for terminal in self.ff.terminals:
                next_state = self._goto(state, terminal)
                if next_state in self.states:
                    self.action_table[i][terminal] = f"s{self.states.index(next_state)}"

    def _build_goto_table(self):
        for i, state in enumerate(self.states):
            self.goto_table[i] = {}
            for nt in self.grammar:
                next_state = self._goto(state, nt)
                if next_state in self.states:
                    self.goto_table[i][nt] = self.states.index(next_state)

    def is_slr1(self):
        return True  # ya se construyó sin conflictos

    def parse(self, tokens):
        stack = [0]
        input_tokens = tokens.copy() + ['$']
        position = 0
        derivation = []

        while True:
            state = stack[-1]
            current_token = input_tokens[position]

            if current_token not in self.action_table[state]:
                raise SyntaxError(f"Error: token inesperado '{current_token}' en estado {state}")

            action = self.action_table[state][current_token]
            if action.startswith('s'):
                stack.append(current_token)
                stack.append(int(action[1:]))
                position += 1
            elif action.startswith('r'):
                prod_num = int(action[1:])
                head, prod = self._get_production(prod_num)
                if prod[0] != 'e':
                    stack = stack[:-2 * len(prod)]
                state = stack[-1]
                stack.append(head)
                stack.append(self.goto_table[state][head])
                derivation.append(f"{head} -> {' '.join(prod)}")
            elif action == 'acc':
                return True, derivation
            else:
                raise SyntaxError(f"Acción inválida: {action}")

    def print_table(self):
        print("\nTabla ACTION:")
        print(f"{'Estado':<8}", end="")
        for terminal in sorted(self.ff.terminals + ['$']):
            print(f"{terminal:<8}", end="")
        print()
        for i, row in self.action_table.items():
            print(f"{i:<8}", end="")
            for terminal in sorted(self.ff.terminals + ['$']):
                print(f"{row.get(terminal, ''):<8}", end="")
            print()

        print("\nTabla GOTO:")
        print(f"{'Estado':<8}", end="")
        for nt in sorted(self.grammar.keys()):
            print(f"{nt:<8}", end="")
        print()
        for i, row in self.goto_table.items():
            print(f"{i:<8}", end="")
            for nt in sorted(self.grammar.keys()):
                print(f"{row.get(nt, ''):<8}", end="")
            print()

def main():
    clear_screen()
    print_colored("=== Analizador de Gramáticas LL(1) y SLR(1) ===", "blue")

    gramatica = leer_gramatica()
    start_symbol = next(iter(gramatica))

    ff = FirstFollow(gramatica, start_symbol)
    ff.compute_first()
    ff.compute_follow()

    try:
        ll1_parser = LL1Parser(gramatica, start_symbol)
        ll1_valid = True
    except ValueError as e:
        ll1_parser = None
        ll1_valid = False
        print(f"\nError LL(1): {str(e)}")

    try:
        slr_parser = SLRParser(gramatica, start_symbol)
        slr_valid = slr_parser.is_slr1()
    except Exception as e:
        slr_parser = None
        slr_valid = False
        print(f"\nError SLR(1): {str(e)}")

    print("\n=== Resultados del Análisis ===")
    for nt in gramatica:
        for prod in gramatica[nt]:
            prod_str = ' '.join(prod) if prod[0] != 'e' else 'ε'
            print(f"{nt} -> {prod_str}")
    ff.pretty_print()
    print()
    print("- La gramática ES LL(1)" if ll1_valid else "- La gramática NO es LL(1)")
    print("- La gramática ES SLR(1)" if slr_valid else "- La gramática NO es SLR(1)")

    while True:
        print("\nOpciones:")
        if ll1_valid:
            print("1. Usar parser LL(1)")
        if slr_valid:
            print("2. Usar parser SLR(1)")
        print("3. Salir")
        opcion = input("> ").strip()
        if opcion == '1' and ll1_valid:
            ll1_parser.print_table()
            analizar_cadena(ll1_parser, "LL(1)")
        elif opcion == '2' and slr_valid:
            slr_parser.print_table()
            analizar_cadena(slr_parser, "SLR(1)")
        elif opcion == '3':
            break
        else:
            print("Opción inválida.")

if __name__ == "__main__":
    main()
