from pyparsing import nestedExpr
from solver import Node, DAG
import itertools

class Parser:

    def __init__(self, graph):
        self.customParser = nestedExpr('(', ')')
        self.graph = graph
        self.ids = set()
        self.atoms_dict = dict()

    
    def parse(self, input):
        input = input.replace(' ', '')
        clauses = set(input.split('&'))
        res = set()
        repeated = set()

        for clause in clauses:
            clause = clause.replace('!', '')
            if clause[0] == '(':
                clause = clause[1:-1]
            parts = clause.split('=')
            res.add(parts[0])
            res.add(parts[1])

        for element1 in res:
            for element2 in res:
                if element1 != element2 and element1 in element2 and element2[element2.find(element1) + len(element1)] in ['=', '(', ')']:
                    repeated.add(element1)
                    break
        
        #print(repeated)
        final = [string for string in res if string not in repeated]
        #print(final)
        final2 = final
        for i in range(len(final)):
            for j in range(len(final)):
                if i == j: pass
                else:
                    if final[i] in final[j]:
                        final2[i] = "0"
        while "0" in final2:
            final2.remove("0")

        #print(final2)
            
        unique_atoms = {}
        for atom in final2:
            atom_as_list = self.customParser.parseString('(' + atom + ')').asList()
            _, atoms_dict =self.parse_clause(atom_as_list[0], unique_atoms)
        
        # print(f'AAAA {unique_atoms}')
        # for node in self.graph.nodes:
        #     fn = node.fn
        #     if str(fn) in unique_atoms:
        #         if node.id == unique_atoms[fn]:
        #             pass
        #         else:
        #             node.unique_atoms[fn].ccpar = node.ccpar
        #             self.graph.nodes.append(unique_atoms[fn])
                    

        #print(f' final2 {final2}')

        return atoms_dict,unique_atoms


    
    def parse_clause(self, atom_as_list:list, unique_atoms):
        tmp = []
        #print(f' atom_as_list {atom_as_list}')
        for term in atom_as_list:
            if not isinstance(term, list):
                for t in term.split(','):
                    if not t == '':
                        tmp.append(t)
            else:
                tmp.append(term)
        clause = tmp
        #print(f'clause = {clause}')
        children = []
        atoms_dict = self.atoms_dict  

        graph_add_node = self.graph.add_node  
        node_string = self.graph.node_string  

        for i, literal in enumerate(clause):
            if isinstance(literal, list):
                continue
            id = self.newId()
            if i + 1 < len(clause) and isinstance(clause[i + 1], list):
                args, _ = self.parse_clause(clause[i + 1], unique_atoms)
                #print(f'unique_atoms = {unique_atoms}')
                id_list = [arg.id for arg in args]# if str(arg) in unique_atoms]
                #print(f'args = {id_list}')  
            else:
                id_list = []
            # final_arg = {}
            # for arg in id_list:
            #     if arg not in unique_atoms:
            #         final_arg[str(literal)] = id
            
            #print(f'final arg = {final_arg}')

            new_node = Node(id=id, fn=literal, args=id_list, find=id, ccpar=set())
            #print(f' {literal} args = {new_node.args}')
            children.append(new_node)
            graph_add_node(new_node)
            atoms_dict[node_string(new_node.id).replace(' ', '')] = id
            # if node_string(new_node.id).replace(' ', '') not in unique_atoms:
            #     unique_atoms[node_string(new_node.id).replace(' ', '')] = id
                

                #unique_atoms[node_string(new_node.id).replace(' ', '')] = id
            # print(f'atoms_dict = {atoms_dict}')
            # print(f'unique_atoms = {unique_atoms}')

        
        #print(atoms_dict)

        return children, atoms_dict
    
    def newId(self) -> str:
        id = next(i for i in itertools.count(1) if i not in self.ids)
        self.ids.add(id)
        return id

def split_string_by_or(input_string):
    output_list = input_string.split("or")
    # Remove leading and trailing whitespaces from each element
    output_list = [elem.strip() for elem in output_list]
    return output_list


def eq_ineq(equations, atoms_dict):
    equalities, inequalities = [], []
    equations = equations.split('&')
    forbidden_list = set()

    for eq in equations:
        if eq[0] == '(': eq = eq[1:-1]
        if '!' in eq:
            parts = eq.split('!=')
            new_ineq = [atoms_dict[parts[0].replace(' ', '')], atoms_dict[parts[1].replace(' ', '')]]
            inequalities.append(new_ineq)
            forbidden_list.add((atoms_dict[parts[0].replace(' ', '')], atoms_dict[parts[1].replace(' ', '')]))
        else:
            parts = eq.split('=')
            new_eq = [atoms_dict[parts[0].replace(' ', '')], atoms_dict[parts[1].replace(' ', '')]]
            equalities.append(new_eq)

    return equalities, inequalities, forbidden_list


def my_alg_OR(clause, list_sat):
    solver = DAG()
    parser = Parser(solver)
    clause = clause.replace(' ','')
    clause = clause.replace('\n','')
    parser.parse(clause.strip())
    equalities, inequalities, forbidden_list = eq_ineq(clause.strip(), parser.atoms_dict)
    solver.add_forbidden_list(forbidden_list)
    solver.add_equalities(equalities)
    solver.add_inequalities(inequalities)
    solver.complete_ccpar()
    #solver.visualize_dag()
    res, count = solver.solve()
    list_sat.append(res)
    # print(f' list_sat = {list_sat}')
    return res, count

def my_alg_AND(line):
    solver = DAG()
    parser = Parser(solver)
    line = line.replace(' ','')
    line = line.replace('\n','')
    parser.parse(line.strip())
    equalities, inequalities, forbidden_list = eq_ineq(line.strip(), parser.atoms_dict)
    solver.add_forbidden_list(forbidden_list)
    solver.add_equalities(equalities)
    solver.add_inequalities(inequalities)
    solver.complete_ccpar()
    #solver.visualize_dag()
    res, count = solver.solve()
    #solver.print_final_graph()
    return res, count


def my_alg_SMT(filename, parser):
    solver_smt = DAG()
    parser_smt = parser
    my_parser = Parser(solver_smt)
    f = parser_smt.parse(filename)
    string = f
    #print(f' f = {f}')
    if "or" in f:
        linesOR = split_string_by_or(f)
        list_sat = []
        tot_merge = 0
        for line in linesOR:
            my_parser.parse(line)
            eq, ineq, fl = eq_ineq(line, my_parser.atoms_dict)
            solver_smt.add_equalities(eq)
            solver_smt.add_inequalities(ineq)
            solver_smt.add_forbidden_list(fl)
            solver_smt.complete_ccpar()
            #solver.visualize_dag()
            res = solver_smt.solve()
            #print(f'merge = {res[1]}')
            tot_merge += res[1]
            if res[0] == "SAT": return "SAT", string, list_sat, tot_merge
            else: list_sat.append(res[0])
        res_f = "UNSAT"
    else:
        my_parser.parse(f)
        eq, ineq, fl = eq_ineq(f, my_parser.atoms_dict)
        solver_smt.add_equalities(eq)
        solver_smt.add_inequalities(ineq)
        solver_smt.add_forbidden_list(fl)
        solver_smt.complete_ccpar()
        #solver.visualize_dag()
        res = solver_smt.solve()
        tot_merge = res[1]
        list_sat = [res[0]]
        res_f = res[0]
    return res_f, string, list_sat, tot_merge

