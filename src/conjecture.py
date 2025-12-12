from math import sqrt, ceil
import networkx as nx
import matplotlib.pyplot as plt

from typing import Mapping, Collection, Hashable, Optional
from theorem import Theorem

class Conjecture:
    @staticmethod
    def graph_exists(n, v):
        return n >= ceil((3 + sqrt(1 + 8*v)) / 2)
    
    @staticmethod
    def save_graph(
        G: nx.Graph, path: str, 
        layout_fun: Optional[Mapping[Hashable, Collection[float]]]
    ) -> None:
        """Saves graph using layout given by layout_fun. 
        Example of layout function is nx.sprint_layout"""
        plt.figure(figsize=(6,6))
        pos = layout_fun(G)
        nx.draw_networkx_nodes(G, pos, node_color='black',node_size=300)
        nx.draw_networkx_edges(G, pos, style='dotted')
        nx.draw_networkx_labels(G, pos, font_size=12, font_color='white')
        plt.axis("off")
        plt.savefig(path, dpi=300)
        plt.close()
    pass 

class Max(Conjecture):
    def find_a_b(self, n, v):
        """Let n be the order of graph G, and let v be its cyclomatic number."""
        assert super().graph_exists(n, v), "Graph does not exist."
        def b_from_a(n, v, a): 
            return (1 + a)*(4 + a - 2*n) / 2 + v
        for a in range(n-2):
            b = b_from_a(n, v, a)
            if 0 < b < n - 2 - a:
                return (int(a), int(b))
        raise Warning("Unexpected error. Parameters (a, b) not found.")

    def cM2(self, n, v):
        """Returns maximum possible cM2 over graphs with order n and cyclomatic number v."""
        assert super().graph_exists(n, v), "Graph does not exist."
        if n >= v + 2:
            return n * (n-1) * (n-2) + v * (v**2 + v - 8)
        a, b = self.find_a_b(n, v)
        term1 = ((n-1)**2 - (2+a+b)**2) * (2 + a)
        term2 = ((2+a+b)**2 - (3+a)**2) * b 
        term3 = ((n-1)**2 - (3+a)**2) * 2 * b 
        term4 = ((n-1)**2 - (3+a)**2) * a * b 
        term5 = ((n-1)**2 - (2+a)**2) * 2 * (n-3-a-b)
        term6 = ((n-1)**2 - (2+a)**2) * a * (n-3-a-b)
        return sum((term1, term2, term3, term4, term5, term6))
    
    def G(self, n, v):
        """Returns graph which reaches maximal cM2 for a given order n and cyclomatic number v."""
        assert super().graph_exists(n, v), "Graph does not exist."
        if n >= v + 2: 
            Z = nx.star_graph(v)
            KC = nx.empty_graph(n-v-2)
            K = nx.empty_graph(1)
            U = nx.disjoint_union(Z, KC)
            G = nx.full_join(U, K, rename=("U_", "K_"))
            G = nx.relabel_nodes(G, {old:i for i,old in enumerate(G.nodes())})
            return G
        else: 
            a, b = self.find_a_b(n, v)
            high_deg_nodes = list(range(2 + a)) 
            low_deg_nodes  = list(range(2 + a, n))
            G = nx.Graph()
            G.add_nodes_from(range(n))
            for u in high_deg_nodes:
                for v in high_deg_nodes:
                    if u < v:
                        G.add_edge(u, v)
            for u in high_deg_nodes:
                for v in low_deg_nodes:
                    G.add_edge(u, v)
            target = low_deg_nodes[0]
            others = [v for v in low_deg_nodes if v != target]
            connect_to = others[0:b]
            for v in connect_to:
                G.add_edge(target, v)
            return G

    def save_graph(self, G, path):
        super().save_graph(G, path, layout_fun=nx.circular_layout)


class Min(Conjecture):
    def cM2(self, n, v):
        assert super().graph_exists(n, v), "Graph does not exist."
        if v == 1: 
            return 0
        if v == 2: 
            return 20 if n == 4 else (18 if n == 5 else 16)
        if n == 2*v - 1: 
            return 10
        if n > 2*v - 1: 
            return 8 
        else: 
            raise ValueError("Not implemented.")
        
    def G(self, n, v):
        """Returns graph which reaches minimal cM2 for a given order n and cyclomatic number v."""
        assert super().graph_exists(n, v), "Graph does not exist."
        if n >= 2*v - 1:
            T = nx.complete_graph(4)
            T.remove_edge(2, 3)
            u, w, order_of_T = 2, 3, 4 
            while order_of_T < 2*v-1:
                if order_of_T + 2 < 2*v-1: 
                    order_of_T += 2
                    T.add_edge(u, u := u + 2)
                    T.add_edge(w, w := w + 2)
                    T.add_edge(u, w)
                else: 
                    order_of_T += 1
                    T.add_edge(u, 2*v-1)
                    T.add_edge(w, 2*v-1)
            for i in range(2*v, n):
                T.add_edge(i-1, i)
            return T
        else: raise ValueError("Not implemented")

    def save_graph(self, G, path):
        super().save_graph(G, path, layout_fun=nx.spring_layout)

if __name__ == "__main__":

    def latex_table(n, m, cols=5, space="0.5cm"):
        conjecture_max = Max()
        theorem = Theorem()
        def g(n):
            k = theorem.gamma(n)
            return tuple({k}) if isinstance(k, int) else k
        values = [
                (
                    n, v, conjecture_max.cM2(n, v), 
                    any(v == theorem.cyclomatic_number_of(n, k) for k in g(n))
            ) 
            for v in range(1, n)
            for n in range(ceil((3 + sqrt(1 + 8*v)) / 2), m) 
        ]
        while len(values) % cols != 0:
            values.append(("", "", "", False))
        total = len(values)
        rows = total // cols
        print(r"\begin{tabular}{" + "|c|c|c|"*cols + "}")
        print(r"\hline")
        header = " & ".join([r"$n$ & $\nu$ & $\cM(G_{n, \nu})$"]*cols)
        print(header + r"\\ \hline")
        h = lambda t: r"\textbf{" + t + "}"
        for r in range(rows):
            row_items = []
            for c in range(cols):
                idx = r + c*rows
                n_val, v_val, k_val, n_opt = values[idx]
                if n_opt:
                    row_items.extend([str(n_val), str(v_val), h(str(k_val))])
                else:
                 row_items.extend([str(n_val), str(v_val), str(k_val)])
            print(" & ".join(row_items) + r"\\ \hline")
        print(r"\end{tabular}")


    # latex_table(20, 19, cols=4) 

    # conjecture_max = Max()
    # print(conjecture_max.cM2(20, 19))

    # conjecture_max = Max()
    # print(conjecture_max.cM2(7, 4))
    # conjecture_max.save_graph(conjecture_max.G(8, 9), path="docs/report/figures/conjecture_max_8_9.png")
    # conjecture_max.save_graph(conjecture_max.G(14, 9), path="docs/report/figures/conjecture_max_14_9.png")

    # conjecture_min = Min() 
    # conjecture_min.save_graph(conjecture_min.G(5, 2), path="docs/report/figures/conjecture_min_5_2.png")


