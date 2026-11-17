"""A distinct solution: return the largest item in a list."""

def largest_value(values):
    """Find the maximum value without calling max."""
    best = values[0]
    for value in values:
        if value > best:
            best = value
    return best


if __name__ == "__main__":
    print(largest_value([4, 8, 2]))
