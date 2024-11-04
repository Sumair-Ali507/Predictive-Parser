class PredictiveParser:
    def __init__(self, grammar, start_symbol):
        self.grammar = grammar
        self.start_symbol = start_symbol
        self.first_sets = self.compute_first_sets()
        self.follow_sets = self.compute_follow_sets()
        self.parse_table = self.construct_parse_table()

    def compute_first_sets(self):
        first_sets = {non_terminal: set() for non_terminal in self.grammar}
        for non_terminal in self.grammar:
            self.first(non_terminal, first_sets)
        return first_sets

    def first(self, symbol, first_sets):
        if symbol not in self.grammar:
            return {symbol}
        if first_sets[symbol]:
            return first_sets[symbol]
        for production in self.grammar[symbol]:
            for sym in production:
                first_set = self.first(sym, first_sets)
                first_sets[symbol].update(first_set - {'ε'})
                if 'ε' not in first_set:
                    break
            else:
                first_sets[symbol].add('ε')
        return first_sets[symbol]

    def compute_follow_sets(self):
        follow_sets = {non_terminal: set() for non_terminal in self.grammar}
        follow_sets[self.start_symbol].add('$')
        while True:
            updated = False
            for non_terminal, productions in self.grammar.items():
                for production in productions:
                    follow = follow_sets[non_terminal]
                    for i in range(len(production) - 1, -1, -1):
                        symbol = production[i]
                        if symbol in self.grammar:
                            if i + 1 < len(production):
                                next_symbol = production[i + 1]
                                if next_symbol in self.first_sets:
                                    first_next = self.first_sets[next_symbol]
                                    follow_sets[symbol].update(first_next - {'ε'})
                                    if 'ε' in first_next:
                                        follow_sets[symbol].update(follow)
                            else:
                                follow_sets[symbol].update(follow)
                            if follow_sets[symbol] != follow:
                                updated = True
            if not updated:
                break
        return follow_sets

    def construct_parse_table(self):
        parse_table = {non_terminal: {} for non_terminal in self.grammar}
        for non_terminal, productions in self.grammar.items():
            for production in productions:
                first_set = self.first(production[0], self.first_sets)
                for terminal in first_set:
                    if terminal != 'ε':
                        parse_table[non_terminal][terminal] = production
                if 'ε' in first_set:
                    for terminal in self.follow_sets[non_terminal]:
                        parse_table[non_terminal][terminal] = production
        return parse_table

    def parse(self, input_string):
        stack = [self.start_symbol]
        input_string = list(input_string) + ['$']
        index = 0

        while stack:
            top = stack.pop()
            current_input = input_string[index]

            if top.islower() or top in {'+', '*', '(', ')', 'id', '$'}:
                if top == current_input:
                    index += 1
                else:
                    raise SyntaxError(f"Unexpected symbol: {current_input}")
            else:
                if current_input in self.parse_table[top]:
                    production = self.parse_table[top][current_input]
                    if production != ['ε']:
                        stack.extend(reversed(production))
                else:
                    raise SyntaxError(f"No rule for {top} with lookahead {current_input}")

        if index == len(input_string):
            print("Input string successfully parsed.")
        else:
            raise SyntaxError("Input string not fully parsed.")

# Example usage
grammar = {
    'E': [['T', "E'"]],
    "E'": [['+', 'T', "E'"], ['ε']],
    'T': [['F', "T'"]],
    "T'": [['*', 'F', "T'"], ['ε']],
    'F': [['(', 'E', ')'], ['id']]
}

parser = PredictiveParser(grammar, 'E')
parser.parse("id+id*id")
