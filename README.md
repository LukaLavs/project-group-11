# The Complementary Second Zagreb Index

## Literature:
- [On a Conjecture Concerning the
Complementary Second Zagreb Index](https://arxiv.org/pdf/2501.01295)
- [Recent Proof of Conjecture](https://www.aimspress.com/article/doi/10.3934/math.2025721?viewType=HTML)

## Report 
Report is found in `docs/report/report.pdf`.

## Main scripts:
- `src/k_as_a_function_of_n.py` computes *Gamma* function and intervals of concavity for a function $f(n, k) = k(n-k)((n-1)^2 - k^2)$ as described in `docs/report.pdf`. 
- `src/MILP.ipynb` is a *SageMath* implementation of *Mixed Integer
Linear Programming* which solves minimal problem of *Second Complementary Zagreb Index* for graphs with small order $n$.
- `src/simulated_annealing.py` is a implementation of an heuristic 
method which finds both graphs which reach minimal *Second Complementary Zagreb Index* as those which reach its maximum.

## Authors:
- Luka Lavš 
- Tinka Napret-Kaučič