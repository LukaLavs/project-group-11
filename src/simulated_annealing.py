import networkx as nx 
from typing import (
    Optional, Dict, Tuple,
)
import random
import math

class SA:
    def __init__(
            self, 
            functions,
            G : nx.Graph, 
            _type : str = 'min',
            T : float = 1000.0, 
            u : float = 0.995, 
            seed : Optional[int] = None,
    ):
        self.functions = functions
        self.type = _type
        self.G = G.copy()
        self.E = self.cM2(G)
        self.T = T 
        self.u = u 
        self.best_state =  G.copy()
        self.best_E = self.E
        self.seed = seed 
    
    @staticmethod
    def cM2(G : nx.Graph) -> int: 
        degrees : Dict[int, int] = dict(G.degree()) # type: ignore
        return sum(
            abs(degrees[u]**2 - degrees[v]**2)
            for u, v in G.edges()
        )

    def accept(
            self, 
            state_next : nx.Graph,
            E_state : int, 
            E_next : int
    ) -> bool: 
        change = E_next - E_state
        if (change < 0 and self.type == 'min') or \
            (change > 0 and self.type == 'max'):
            self.best_state = state_next
            self.best_E = E_next
            return True
        return (
            random.random() < self.functions.cooling_function(change, self)
        )
    
    def new_state(self) -> nx.Graph:
        edges = list(self.G.edges())
        non_edges = list(nx.non_edges(self.G))
        if non_edges == []: return self.G
        while True: 
            H = self.G.copy()
            u_v = self.functions.edge_to_remove(self, edges, non_edges)
            w_x = self.functions.edge_to_add(self, edges, non_edges)
            H.remove_edge(*u_v)
            H.add_edge(*w_x)
            if nx.is_connected(H):
                return H
            
    def simulated_annealing(self) -> Tuple[nx.Graph, int]:
        while self.T > 1:
            state_next = self.new_state()
            E_next = self.cM2(state_next)
            if self.accept(state_next, self.E, E_next):
                self.G = state_next
                self.E = E_next
            
            self.T *= self.u
        print(
            f"Best Energy: {self.best_E}\n"
            f"Edges: {self.best_state.edges()}"
        )
        return (self.best_state, self.best_E)
    
    
class FunctionsMin:
    def __init__(self):
        self.pick = None

    @staticmethod
    def cooling_function(change, milp):
        return math.exp(- change / milp.T)
    
    @staticmethod
    def cM2(milp, uv, wx):
        F = milp.G.copy() 
        F.remove_edge(*uv)
        F.add_edge(*wx)
        return milp.cM2(F)
    
    def edge_to_add(self, milp : SA, edges, non_edges):
        if self.pick is None: raise ValueError("Unexpected.")
        return self.pick[1]
    
    def edge_to_remove(self, milp : SA, edges, non_edges):
        H = milp.G.copy()
        candidates = [(uv, wx) for uv in edges for wx in non_edges]
        weights = {
            (uv, wx) : self.cM2(milp, uv, wx) - milp.E
            for uv in edges for wx in non_edges
        }
        cf_weights = [self.cooling_function(change=weights[(uv, wx)], milp=milp) for (uv, wx) in weights.keys()]
        pick = random.choices(candidates, weights=cf_weights)[0]

        self.pick = pick
        return pick[0]
    
class FunctionsMax:
    def __init__(self):
        self.pick = None

    @staticmethod
    def cooling_function(change, milp):
        return math.exp(change / milp.T)
    
    @staticmethod
    def cM2(milp, uv, wx):
        F = milp.G.copy() 
        F.remove_edge(*uv)
        F.add_edge(*wx)
        return milp.cM2(F)
    
    def edge_to_add(self, milp : SA, edges, non_edges):
        if self.pick is None: raise ValueError("Unexpected.")
        return self.pick[1]
    
    def edge_to_remove(self, milp : SA, edges, non_edges):
        H = milp.G.copy()
        candidates = [(uv, wx) for uv in edges for wx in non_edges]
        weights = {
            (uv, wx) : self.cM2(milp, uv, wx) - milp.E
            for uv in edges for wx in non_edges
        }
        cf_weights = [self.cooling_function(change=weights[(uv, wx)], milp=milp) for (uv, wx) in weights.keys()]
        pick = random.choices(candidates, weights=cf_weights)[0]

        self.pick = pick
        return pick[0]
    
def save_image(best_graph, best_cM2, path):
    plt.figure(figsize=(6,6))
    pos = nx.spring_layout(best_graph)
    nx.draw_networkx_nodes(best_graph, pos, node_color='black',node_size=300)
    nx.draw_networkx_edges(best_graph, pos, style='dotted')
    nx.draw_networkx_labels(best_graph, pos, font_size=12, font_color='white')
    plt.title(f"{_type} cM_2({n=}, {k=}) = {best_cM2}")

    plt.axis("off")
    plt.savefig(path, dpi=300)
    plt.close()

if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import math 

    n = 9; k = 3
    m = n - 1 + k 
    _type = 'min' # OR 'max'
    functions = FunctionsMin() # OR FunctionsMax()
    m = n - 1 + k
    title=f"optimal-graphs-per-cyclomatic-number/{_type}/{_type}_cM_2_n{n}_k{k}.png"
    if n < math.ceil((3 + math.sqrt(1 + 8*k)) / 2):
        raise ValueError("Such graph not possible.")
    print("parameters", n, k, m)
    G = nx.gnm_random_graph(n, m)
    while not nx.is_connected(G):
        G = nx.gnm_random_graph(n, m)
    print("start")
    sa = SA(
        functions=functions,
        G=G,
        _type=_type,
        T=1000000.0,
        u=0.9,
        seed=None,
    )
    print(sa.best_E)
    best_graph, best_cM2 = sa.simulated_annealing()
    save_image(best_graph, best_cM2, path='best_graph.png')
    save_image(best_graph, best_cM2, path=title)

