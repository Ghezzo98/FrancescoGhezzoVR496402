import os
from solver import DAG, Node
from custom_parser import *
from smt_parser import *
from timeit import default_timer as timer
directory = ''
extension_txt = '.txt'
extension_smt = '.smt2'
    

def main():

    file_test = open('inputs/input.txt', 'r')
    filename = "inputs/input1.smt2"
    lines = file_test.readlines()
    # True per far andare il file txt, False per far andare  il file smt
    txt_true_smt_false = False 

    if txt_true_smt_false:
        print('*'*90)
        print("Checking custom files .txt")
        print('*'*90)

        for line in lines:

            if "or" in line:
                n_merge = 0
                print(f"Checking formula: {line.strip()}")
                start = timer()
                linesOR = split_string_by_or(line)
                list_sat = []
                sat_unsat = "UNSAT"
                flag = True
                tot_merge = 0
                for clause in linesOR:
                    res, n_merge = my_alg_OR(clause, list_sat)
                    tot_merge += n_merge
                    if res == "SAT": 
                        sat_unsat = "SAT" 
                        flag = False
                        break
                if flag:
                    for i in range(len(list_sat)):
                        if list_sat[i] == "SAT":
                            sat_unsat = "SAT"

                end = timer()
                print(f'time = {(end-start)*1000}ms')
                print(f'numero di merge = {tot_merge}')
                #print(f' list_sat = {list_sat}')
                #print(f"Equalities  found: {solver.equalities}")
                #print(f"Inequalities found: {solver.inequalities}")
                print(f"The formula is: {sat_unsat}")
                print('-'*90)
                

            else:
                print(f"Checking formula: {line.strip()}")
                n_merge = 0
                start = timer()
                res, n_merge = my_alg_AND(line)
                #print(f"Equalities  found: {solver.equalities}")
                #print(f"Inequalities found: {solver.inequalities}")
                end = timer()
                print(f'time = {(end-start)*1000}ms')
                print(f'numero di merge = {n_merge}')
                print(f"The formula is: {res}")


                print('-'*90)
                
    else: 
        print('*'*90)
        print("Checking smt files")
        print('*'*90)
        start = timer()
        parser_smt = Custom_parser()
        res, input, list_sat, tot_merge  = my_alg_SMT(filename, parser_smt)
        end = timer()
        print(f"Checking formula: {input}")
        print(f'time = {(end-start)*1000}ms')
        print(f'numero di merge = {tot_merge}')
        #print(f' list_sat = {list_sat}')
        print(f"The formula is: {res}")
        print('-'*90)
             

if __name__ == '__main__':
    main()