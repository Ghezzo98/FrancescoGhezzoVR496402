from pysmt.smtlib.parser import SmtLibParser
import re

class Custom_parser():
    def __init__(self):
        self.parser = SmtLibParser()

    def parse(self, filename):
        script = SmtLibParser().get_script_fname(filename)
        f = script.get_strict_formula().serialize().__str__()[1:-1]
        symbol = '&'
        result = []
        final = []
        if '|' not in f:
            for item in f.split(symbol):
                item = item.replace(' ', '')
                if item.startswith('('):
                    item = item[1:-1]
                    result.append(item)
            for res in result:
                if '!' in res:
                    res = res.replace('!', '')
                    res = res.replace('=', '!=')
                    res = res[1:-1]
                    final.append(res)
                else:
                    final.append(res)
        else:
            #print(f'f = {f}')
            final = or_eq_parser(f)
            return final
        return symbol.join(final)


def or_eq_parser(input_string):
    input_string = input_string.replace(' ','')
    pattern = r'(!?\((\w+)=(\w+)\))'
    clauses =input_string.split('|')
    final = []
    symbolOR = "or"
    for clause in clauses:
        matches = re.findall(pattern, clause)
        #print(f'matches = {matches}')
        matched_formulas = [(match[0], match[1], match[2]) for match in matches]
        symbol = '&'
        result = []
        #print(f'input_string = {clause}')

        for formula in matched_formulas:
            if '!' in formula[0]:
                result.append(formula[1] + '!=' + formula[2])
            else:
                result.append(formula[1] + '=' + formula[2])
       
        new_clause = symbol.join(result)
        final.append(new_clause)
        # symbol.join(result)
        # final.join(symbol)
        # symbol = '&'
        #print(f'result = {result}')
    #print(f'final = {final}')
    parsed = symbolOR.join(final)
    #print(f'parsed = {parsed}')
    return parsed