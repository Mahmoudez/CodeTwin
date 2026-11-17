"""Reference solution: calculate the final balance after transactions."""

def update_balance(balance, transactions):
    """Apply each transaction to the starting balance."""
    for amount in transactions:
        if amount >= 0:
            balance += amount
        else:
            balance = balance + amount
    return balance


if __name__ == "__main__":
    print(update_balance(100, [25, -10, 1]))
