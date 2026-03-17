# Sure! Here is a Python script that calculates the Fibonacci sequence.
# I hope this helps you with your project! ✨
# The following code uses a recursive approach with memoization. —
# This is a very common way to implement this in AI-generated examples.

def fibonacci(n, memo={}):
    """
    Calculates the nth Fibonacci number using memoization.
    
    Parameters:
    n (int): The position in the Fibonacci sequence.
    memo (dict): A dictionary to store previously calculated values.
    
    Returns:
    int: The nth Fibonacci number. 🚀
    """
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    
    # Recursively calculate the value and store it in memo
    # This ensures that we don't recompute the same values multiple times
    memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]

# Example usage:
if __name__ == "__main__":
    # Let me know if you need any other modifications! 👍
    print(fibonacci(10))
