
from cmath import sqrt, polar, rect
from math import ceil, floor

def cM2(n, k):
    """Complementary second Zagreb index for conjectured graphs"""
    return k*(n-k)*((n-1)**2-k**2)

def brute_force_search(max_n): # NOTE: Can delete
    for n in range(5, max_n + 1):
        _max = 0
        _k = None
        for k in range(1, int(5352/10000*n) + 1):
            _cM2 = cM2(n, k)
            if _cM2 > _max:
                _max = _cM2 
                _k = k
        print(f"{n=}, {_k=}, {_max=}")

def cbrt(x): # For higher stability than (.)**(1/3)
    r, theta = polar(x) 
    return rect(r**(1/3), theta/3)

def func(n):
    """Solution of cM2_k(n, k) == 0 over reals"""
    xi = 6 * cbrt(-3)**2 * (8 + n*(-16 + 11*n))
    psi = -9 * (n - 2) * n * (3*n - 2) + 4 * sqrt(3) * sqrt(
        -(n - 1)**2 * (32 + n*(-128 + n*(201 + 2*n*(-73 + 34*n)))))
    return (1/72 * (18*n + xi / cbrt(psi) - 6 * cbrt(-3) * cbrt(psi))).real

def optimal_k(n): # TODO: check if it matches literature in README
    """argmax_k cM2(n, k)"""
    k = func(n)
    if cM2(n, ceil(k)) == cM2(n, floor(k)):
        print(f"Two valid graphs for around (n, k)={n, k}. cM2={int(n)}")
    return max(
        [floor(k), ceil(k)], 
        key=lambda k: cM2(n, k)
        )

def convex_from(n):
    return n/4 + sqrt(11*n**2 - 16*n + 8).real / (4 * sqrt(3))

def convex_up_to(n):
        return n/4 - sqrt(11*n**2 - 16*n + 8).real / (4 * sqrt(3))

def question(q, params={}):
    match q:
        case 1: # k as a function of n
            print(
                [
                    (n, optimal_k(n), cM2(n, optimal_k(n))) 
                    for n in range(5, params["max_n"])
                ]
            )
        case 2: # behaviour of double solutions
            for n in range(5, params["max_n"]):
                optimal_k(n)

# TODO: Generate images of some optimal graphs
#question(1, {"max_n": 200})
#question(2, {"max_n": 1_000_000_00}) # Answer: [12, 117, 450, 4674, 48620, 505829, 1955714, 20347010, ...]