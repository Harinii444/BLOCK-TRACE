def calculate_confidence(trace, vasp):
    score = 0

    # More transaction hops increase tracing confidence
    if len(trace) >= 2:
        score += 30

    if len(trace) >= 4:
        score += 20

    # Final wallet is identified as a VASP
    if vasp:
        score += 50

    return score
