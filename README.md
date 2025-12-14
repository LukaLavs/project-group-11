# The Complementary Second Zagreb Index

## Literature:
- [On a Conjecture Concerning the
Complementary Second Zagreb Index](https://arxiv.org/pdf/2501.01295)
- [Recent Proof of Conjecture](https://www.aimspress.com/article/doi/10.3934/math.2025721?viewType=HTML)

## Report 
Report is found in `docs/report/report.pdf`.

## Main scripts:
- `src/theorem.py` defines a class **Theorem** which implements $\Gamma$, $f$  and other functions, which come in handy when analyzing graphs in form $K_k + \overline{K}_{n-k}$.
    ```python
    from theorem import Theorem 
    n = 14 
    k = theorem.gamma(n) # NOTE: sometimes gamma returns tuple
    k_tuple = theorem.tuple_gamma(n) # Always returns tuple
    k_real = theorem.relaxed_gamma(n) # optimizes in reals
    cM2 = theorem.f(n, k) # as described in report
    cM2_b = theorem.cM2(n) # cM2_b == cM2 always holds
    a, b = theorem.concave_on(n) # f is concave on [a, b]
    v = theorem.cyclomatic_number_of(n, k) # gives cyclomatic number
    ```
- `src/conjecture.py` defines a class Conjecture. It gives methods to visualize conjectured graphs and calculate their ${cM}_2$. 
    ```python
    from conjecture import Conjecture
    conjecture = Conjecture()
    min_cM_5_2 = conjecture.min.cM(5, 2) # Minimal cM2 for given order 5 and cyclomatic number 2 
    max_cM_20_19 = conjecture.max.cM(20, 19) # Maximal cM2 for given parameters
    conjecture.max.save_graph(conjecture.max.G(20, 19), path="test_max.png") # Gives image of optimal graph
    ```
- `src/MILP.ipynb` is a *SageMath* implementation of *Mixed Integer
Linear Programming* which solves minimal problem of *Second Complementary Zagreb Index* for graphs with small order $n$.
- `src/simulated_annealing.py` is a implementation of an heuristic 
method which finds both graphs which reach minimal *Second Complementary Zagreb Index* as those which reach its maximum.
    ``` python
    H = nx.gnm_random_graph(n, m)
    while not nx.is_connected(H):
        H = nx.gnm_random_graph(n, m)
    from simulated_annealing import SA, FunctionsMax, FunctionsMin 
    sa_min = SA(functions=FunctionsMin(), G=G, _type='min')
    G, min_cM2 = sa_min.simulated_annealing()
    # Similarly for max
    ```
- `src/brute_force.ipynb` uses nauty/geng to enumerate all connected graphs on n vertices, computes the *Second Complementary Zagreb Index* for each, identifies minimal and maximal graphs, and verifies whether maximal graphs are join graphs $K_k + \overline{K}_{n-k}$.
- `src/patterns_in minimal_graphs.ipynb` combines MILP for exact solutions on small graphs and Simulated Annealing (SA) for heuristic solutions on larger graphs to find minimal and maximal *Second Complementary Zagreb Index* values.
- `src/patterns_in maximal_graphs.ipynb` integrates brute-force enumeration for small graphs and simulated annealing (SA) heuristic for larger graphs to find maximal *Second Complementary Zagreb Index* values across different graph sizes.


## Authors:
- Luka Lavš 
- Tinka Napret-Kaučič
