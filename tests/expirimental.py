from math import ceil
import networkx as nx
import numpy as np 
import cvxpy as cp 
from itertools import combinations, product

from typing import (
    Dict, List,
)
from src.conjecture import Base

class MinExtended(Base):
    @staticmethod
    def integer_partitions(
        total: int,
        num_parts: int,
        max_part: int
    ) -> List[Dict[int, int]]:
        """ Returns all integer partitions of `total` into 
        exactly `num_parts` using numbers in [1, `max_part`]"""
        results: List[Dict[int, int]] = []
        def backtrack(
            remaining: int,
            parts_left: int,
            max_allowed: int,
            current: Dict[int, int]
        ):
            if remaining == 0 and parts_left == 0:
                results.append(current.copy())
                return
            if remaining < 0 or parts_left < 0:
                return
            if remaining < parts_left * 1:
                return
            if remaining > parts_left * max_allowed:
                return
            upper = min(max_allowed, max_part, remaining)
            for value in range(upper, 0, -1):
                current[value] = current.get(value, 0) + 1
                backtrack(
                    remaining - value,
                    parts_left - 1,
                    value,
                    current
                )
                if current[value] == 1:
                    del current[value]
                else:
                    current[value] -= 1
        backtrack(
            remaining=total,
            parts_left=num_parts,
            max_allowed=max_part,
            current={}
        )
        return results

    @staticmethod
    def erdos_gallai(p):
        """Determines if sequence of degrees is graphical. 
        It uses [Erdos Gallai algorithm](https://en.wikipedia.org/wiki/Erdős-Gallai_theorem)"""
        degrees = sorted([d for d, v in p.items() for _ in range(v)], reverse=True)
        if sum(degrees) % 2 != 0: 
            return False 
        for k in range(len(degrees) + 1):
            if sum(degrees[:k]) > k*(k-1) + \
                sum(min(d, k) for d in degrees[k:]):
                return False 
        return True

    def degree_sequence(self, n, v):
        """Returns those partitions which are graphical."""
        m = n - 1 + v
        M = ceil(2*m/n)
        return list(filter(
            self.erdos_gallai, self.integer_partitions(2*m, n, M)
            ))

    def optimize(self, degrees, h=lambda s1, s2: s1**2 - s2**2):
        """
        Finds optimal intercluster connections A for given degrees.
        Returns integer matrix A and objective value.

        Parameters
        ----------
        degrees : dict
            Keys are degrees, values are counts of vertices with that degree.
        h : callable
            Function of two degrees to use in objective.
        """
        # convert degrees to arrays
        n, s = list(degrees.values()), list(degrees.keys())
        n = np.array(n)
        s = np.array(s)
        k = len(n)

        # ILP variable
        A = cp.Variable((k, k), integer=True)

        constraints = []

        # 1. Symmetry
        for i in range(k - 1):
            for j in range(i + 1, k):
                constraints.append(A[i,j] == A[j,i])

        # 2. Non-negativity
        constraints.append(A >= 0)

        # 3. Degree feasibility (row sums)
        for i in range(k):
            constraints.append(cp.sum(A[i,:]) == n[i] * s[i])

        # 4. Graphical feasibility bounds
        for i in range(k):
            constraints.append(A[i,i] <= n[i]*(n[i]-1))        # max internal edges
            for j in range(i+1, k):
                constraints.append(A[i,j] <= n[i]*n[j])        # max between clusters

        # 5. Connectivity: at least one edge between any partition subset S and its complement
        for r in range(1, k):
            for S in combinations(range(k), r):
                S_comp = [i for i in range(k) if i not in S]
                constraints.append(cp.sum([A[i,j] for i in S for j in S_comp]) >= 1)

        # 6. Diagonal evenness: internal edges count twice
        D = cp.Variable(k, integer=True)
        for i in range(k):
            constraints.append(D[i] >= 0)
            constraints.append(A[i,i] == 2 * D[i])

        # 7. Objective: minimize sum_{i!=j} A[i,j] * h(s[i], s[j])
        obj = 0
        for i in range(k-1):
            for j in range(i, k):
                obj += A[i,j] * h(s[i], s[j])

        prob = cp.Problem(cp.Minimize(obj), constraints)
        prob.solve(solver=cp.CBC, verbose=False)

        if prob.status not in ["optimal", "optimal_inaccurate"]:
            raise ValueError("No feasible integer graph solution found")

        return np.round(A.value).astype(int).tolist(), int(prob.value)


    @staticmethod
    def _construct_graph(D: List[List[int]], degrees: Dict[int, int]) -> nx.Graph:
        """
        Construct a simple graph G from a joint degree matrix D and degree counts.
        It uses [JDM algorithm](https://arxiv.org/abs/1509.07076)
        
        Parameters:
            D: k x k matrix of edges between degree classes
            degrees: dict mapping degree -> number of vertices with that degree
        
        Returns:
            G: networkx.Graph realizing the JDM
        """
        for i in range(len(D)):
            D[i][i] //= 2
        # Step 0: initialize
        deg_vals = sorted(degrees.keys(), reverse=True)
        k = len(deg_vals)
        G = nx.Graph()
        
        # Create vertex sets for each degree
        groups = {}
        node_id = 0
        for d in deg_vals:
            groups[d] = []
            for _ in range(degrees[d]):
                G.add_node(node_id, degree=d)
                groups[d].append(node_id)
                node_id += 1

        # Step 1: Add edges according to D
        # Internal edges
        for i, d in enumerate(deg_vals):
            nodes = groups[d]
            needed = D[i][i]
            added = 0
            # Arbitrarily add edges
            for u, v in combinations(nodes, 2):
                if added >= needed:
                    break
                if not G.has_edge(u, v):
                    G.add_edge(u, v)
                    added += 1
            if added != needed:
                raise ValueError(f"Could not place all internal edges in group {d}")

        # Between groups
        for i in range(k):
            for j in range(i + 1, k):
                g1 = groups[deg_vals[i]]
                g2 = groups[deg_vals[j]]
                needed = D[i][j]
                added = 0
                for u, v in product(g1, g2):
                    if added >= needed:
                        break
                    if not G.has_edge(u, v):
                        G.add_edge(u, v)
                        added += 1
                if added != needed:
                    raise ValueError(f"Could not place all edges between groups {deg_vals[i]} and {deg_vals[j]}")

        # Step 2: Adjust degrees within each group
        for d in deg_vals:
            nodes = groups[d]
            target_deg = d
            deg_dict = dict(G.degree(nodes))
            wrong = [n for n in nodes if deg_dict[n] != target_deg]
            while wrong:
                # Pick node with too low and node with too high
                u = min(wrong, key=lambda x: deg_dict[x])
                v = max(wrong, key=lambda x: deg_dict[x])
                if u == v:
                    break
                delta = min(target_deg - deg_dict[u], deg_dict[v] - target_deg)
                # Find neighbors of v that are not neighbors of u
                candidates = [nbr for nbr in G.neighbors(v) if nbr != u and not G.has_edge(u, nbr)]
                move = min(delta, len(candidates))
                if move == 0:
                    break
                for nbr in candidates[:move]:
                    G.remove_edge(v, nbr)
                    G.add_edge(u, nbr)
                    deg_dict[u] += 1
                    deg_dict[v] -= 1
                wrong = [n for n in nodes if deg_dict[n] != target_deg]

        return G

    @staticmethod
    def cM2_test(G):
        out = 0
        degrees = dict(G.degree())
        for (u, v) in G.edges():
            out += abs(degrees[u]**2 - degrees[v]**2)
        return out 
    
    def optimal(self, n, v):
        """Finds optimal intercluster connections, degrees and cM2 value."""
        best_A, best_val, best_p = None, float("inf"), None
        for degrees in self.degree_sequence(n, v):
            A, val = self.optimize(degrees)
            if val < best_val: 
                best_A, best_val, best_p = A, val, degrees
        return best_A, best_p, best_val
    
    def G(self, n, v):
        A, p, v = self.optimal(n, v)
        H = self._construct_graph(A, p) 
        return H
    
    def cM2(self, n, v):
        _, _, val = self.optimal(n, v)
        return val
    
    def save_graph(self, G, path):
        return super()._save_graph(G, path, nx.circular_layout)
    


if __name__ == "__main__":

    min_extended = MinExtended()
    #print(min_extended.cM2(32, 34))
    #conjecture.min.save_graph(min_extended.G(8, 6), path="test_graph.png")


    # degrees = {5: 17, 3: 15}
    
    # start = time()
    # for v in range(3, 20):
    #     for n in range(ceil((3 + sqrt(1 + 8*v)) / 2), 2*v - 1):
    #         print(f"Starting with {n=} {v=}.")
    #         A, d, val = min_extended.optimal(n, v)
    #         print(f"{A=}\n{d=}\n{val=}\n")
    #         if True:
    #             try: 
    #                 H = min_extended._construct_graph(A, d) 
    #                 min_extended.save_graph(H, path=f"min/min_n{n}__v{v}_val{val}.png")
    #                 print(f"Saved graph for {n=} {v=}.")
    #             except ValueError as e: print(f"Error for graph {n=} {v=}."); print(e); break 

    n, v = 12, 9
    A, d, val = min_extended.optimal(n, v)
    print(f"{A=}\n{d=}\n{val=}\n")
    H = min_extended._construct_graph(A, d) 
    min_extended.save_graph(H, path=f"test_graph.png")


    # results = []     
    # for v in range(3, 20):
    #     for n in range(ceil((3 + sqrt(1 + 8*v)) / 2), 2*v - 1): 
    #         A, d, val = min_extended.optimal(n, v) 
    #         print(n, v, val)
    #         results.append((n, v, val, A, d))
    # print(results)

    
    # print("time", time() - start)
