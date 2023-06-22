import networkx as nx
import matplotlib.pyplot as plt
import itertools
from copy import deepcopy

class Node:
    def __init__(self, id:int, fn:str, args:list, find:int, ccpar:set):
        self.id = id 
        self.fn = fn
        self.args = args
        self.find = find
        self.ccpar = ccpar
    
    def __hash__(self):
        return hash(self.fn) * hash(tuple(self.args))

    def __eq__(self, other):
        return hash(self) == hash(other)

class DAG:
    def __init__(self):
        self.nodes = []
        self.equalities = []
        self.inequalities = []
        self.forbidden_list = set()

    def add_forbidden_list(self, forbidden_list:set):
        for fl in forbidden_list:
            self.forbidden_list.add(fl)

    def add_equalities(self, equalities:list):
        for eq in equalities:
            self.equalities.append(eq)

    def add_inequalities(self, inequalities:list):
        for ineq in inequalities:
            self.inequalities.append(ineq)

    def remove_node(self, node:Node):
        #node.ccpar = ()
        self.nodes.remove(node)
    
    def add_node(self, node:Node):
        self.nodes.append(node)

    def NODE(self, node_id:int):
        for node in self.nodes:
            if node.id == node_id:
                return node
        print('Node not found')

    def FIND(self, node_id:int):
        node = self.NODE(node_id)
        if node.find == node_id: return node_id
        return self.FIND(node.find)

    def UNION2(self, n1:int, n2:int):
        n1 = self.NODE(self.FIND(n1))
        n2 = self.NODE(self.FIND(n2))
        n1.find = n2.find
        n2.ccpar = n1.ccpar.union(n2.ccpar)
        n1.ccpar = set()


    def UNION(self, n1:int, n2:int):
        n1 = self.NODE(self.FIND(n1))
        n2 = self.NODE(self.FIND(n2))
        if len(n1.ccpar) < len(n2.ccpar):
            n1.find = n2.find
            n2.ccpar = n1.ccpar.union(n2.ccpar)
            n1.ccpar = set()
        else:
            n2.find = n1.find
            n1.ccpar = n2.ccpar.union(n1.ccpar)
            n2.ccpar = set()
    
    def CCPAR(self, node_id:int):
        return self.NODE(self.FIND(node_id)).ccpar
    
    def CONGRUENT(self, node_id1:int, node_id2:int):
        n1 = self.NODE(node_id1)
        n2 = self.NODE(node_id2)
        res = True if (n1.fn == n2.fn and len(n1.args) == len(n2.args) and [self.FIND(n1.args[i]) == self.FIND(n2.args[i]) for i in range(len(n1.args))]) else False
        return res
    
    def MERGE(self, node_id1:int, node_id2:int, count: int):
        if self.FIND(node_id1) != self.FIND(node_id2):
            p1 = self.CCPAR(node_id1)
            p2 = self.CCPAR(node_id2)
            self.UNION(node_id1, node_id2)
            for t1, t2 in list(itertools.product(p1, p2)):
                if self.FIND(t1) != self.FIND(t2) and self.CONGRUENT(t1, t1):
                    self.MERGE(t1, t2, count)
                    return count +1
                else:
                    return count
        return count 
    
    def complete_ccpar(self):
        for node in self.nodes:
            self.add_father(node.id)
            pass

    def add_father(self, id):
        father_args = self.NODE(id).args
        for arg in father_args:
            target = self.NODE(arg)
            target.ccpar.add(id)

    def print_node(self, node_id:int):
        node = self.NODE(node_id)
        print(f"Node \tid: {node.id}\n\tfn: {node.fn}\n\targs: {node.args}\n\tfind: {node.find}\n\tccpar: {node.ccpar}\n")
    
    def print_nodes(self):
        for node in self.nodes:
            self.print_node(node.id)

    def node_string(self, id):
        target = self.NODE(id)
        if len(target.args) == 0:
            return f"{target.fn}"
        else:
            args_str = ""
            for arg in target.args:
                args_str = args_str + self.node_string(arg) + ', '
            args_str = args_str[:-2]
            return f"{target.fn} ({args_str})"  
    
    def solve(self):
        count = 0
        for eq in self.equalities:
            val1, val2 = eq[0], eq[1]
            if (val1, val2) in self.forbidden_list: return "UNSAT -> forbidden list", count
            if (val2, val1) in self.forbidden_list: return "UNSAT -> forbidden list", count
            count = self.MERGE(eq[0], eq[1], count)

        for ineq in self.inequalities:
            val1, val2 = self.FIND(ineq[0]), self.FIND(ineq[1])
            if val1 == val2:
                return "UNSAT", count
        return "SAT", count

    def visualize_dag(dag):
        G = nx.DiGraph()

        # Add nodes to the graph
        for node in dag.nodes:
            G.add_node(node.id)

        # Add edges to the graph
        for node in dag.nodes:
            for child_id in node.ccpar:
                G.add_edge(child_id, node.id)
            

        # Create a dictionary to store node labels
        labels = {node.id: f"{node.fn} (ID: {node.id})" for node in dag.nodes}

        # Draw the graph
        pos = nx.circular_layout(G)
        nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=500, font_size=10, arrows=True)
        plt.show()
    

    def print_final_graph(dag):
        G = nx.DiGraph()

        # Add nodes to the graph
        for node in dag.nodes:
            G.add_node(node.id)

        # Add edges to the graph
        for node in dag.nodes:
            for child_id in node.ccpar:
                G.add_edge(child_id, node.id)

        final_graph = G.copy()

        edges_find = []
        edges_ccpar = []
        for node in dag.nodes:

            #add find edges
            if str(node.find) != str(node.id):
                edges_find.append((node.id,node.find))
            #add ccpar edges

            if len(node.ccpar)>0:
                for v in node.ccpar:
                    #only if it's not its direct parent
                    if node.id not in dag.NODE(v).args:
                        edges_ccpar.append((v,node.id))

        labels = {node.id: f"{node.fn} (ID: {node.id})" for node in dag.nodes}
        pos = nx.circular_layout(final_graph)

        nx.draw_networkx_edges(final_graph, pos=pos,edgelist=edges_find, style = 'dashed',connectionstyle='arc3 ,rad=0.3')
        nx.draw_networkx_edges(final_graph, pos=pos,edgelist=edges_ccpar, style = 'dashdot',connectionstyle='arc3 ,rad=0.3')
        nx.draw(final_graph, pos, labels=labels, font_weight='bold')
        plt.show()






    def visualize_dag1(self, G, find = False):
        G = nx.DiGraph()


        # Create a dictionary to store node labels
        labels = {node: f"{node.fn} (ID: {node.id})" for node in self.graph}

        # Draw the graph
        pos = nx.circular_layout(G)
        

        # Draw the dotted edges with curved lines
        if find:
            dotted_edges = []
            #self.update_find_edge(G)
            for node in self.graph:
                if not (node.find == node.id):
                    #G.add_edge(node, self.graph[node.find],  style="dotted")
                    dotted_edges.append((node, self.graph[node.find]))
                    #dotted_edges = [(child_id, parent_id) for parent_id, child_id, edge_style in G.edges(data='style') if edge_style == 'dotted']
            nx.draw_networkx_edges(G, pos, edgelist=dotted_edges, style='dotted', connectionstyle='arc3,rad=0.3')

        nx.draw(G, pos, with_labels=True, labels=labels, node_color='lightblue', node_size=500, font_size=10, arrows=True)
        plt.show()
        return G