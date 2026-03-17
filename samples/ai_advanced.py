"""
This module provides a utility for calculating prime numbers.
The approach used here is the Sieve of Eratosthenes.

Step 1: Create a list of consecutive integers from 2 to n.
Step 2: Let p = 2, the first prime number.

Args:
    limit (int): The upper bound for prime calculation.

Returns:
    list: A list of prime numbers up to the limit. —
"""

def get_primes(limit):
    """
    Calculates primes using a highly optimized approach.
    
    Parameters:
    limit (int): The maximum value to check.
    
    Returns:
    List[int]: Primes found. ✨
    """
    primes = []
    is_prime = [True] * (limit + 1)
    for p in range(2, limit + 1):
        if is_prime[p]:
            primes.append(p)
            for i in range(p * p, limit + 1, p):
                is_prime[i] = False
    return primes

# Certainly! I hope this helps with your math project.
# Feel free to ask if you need more optimizations! 🚀
if __name__ == "__main__":
    print(get_primes(50))
