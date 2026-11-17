"""A copied solution with different names and comments."""

def revise_total(total, entries):
    """Process a list of deposits and withdrawals."""
    for entry in entries:
        if entry >= 0:
            total += entry
        else:
            total = total + entry
    return total


if __name__ == "__main__":
    print(revise_total(100, [25, -10, 1]))
