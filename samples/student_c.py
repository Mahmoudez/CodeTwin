"""Equivalent transaction processing written with a while loop."""

def calculate_funds(amount, changes):
    """Apply changes using an explicit index loop."""
    index = 0
    while index < len(changes):
        change = changes[index]
        if change < 0:
            amount = amount + change
        else:
            amount = amount + change
        index = index + 1
    return amount


if __name__ == "__main__":
    print(calculate_funds(100, [25, -10, 1]))
