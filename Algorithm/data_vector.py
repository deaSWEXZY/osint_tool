import numpy as np

# ----------- USERNAME VECTOR (CHARS APPEAR. IN ALPHABET) -----------
def to_vector(username, alphabet):
    vector = []
    lowercase_username = username.lower()
    for char in alphabet:
        count = lowercase_username.count(char)
        vector.append(count)
    return vector

# ----------- COSINE SIMILIARITY(cos of angle between vectors) -----------
def cosine_similiarity(v, u):
    v_magnitude = np.linalg.norm(v)
    u_magnitude = np.linalg.norm(u)
    if u_magnitude * v_magnitude == 0:
        return 0.0
    dot_product = np.dot(v, u)
    return dot_product / (v_magnitude * u_magnitude)

def generate_candidates(username):
    candidates = set() 
    common_chars = ["_", "official", "1", "777", "999", "$", "x", "real"] # Common Prefixes in names

    # Adding to set Matching Candidates
    for p in common_chars:
        candidates.add(f"{username}{p}")
        candidates.add(f"{p}{username}")
        candidates.add(f"{username}_{p}")
        candidates.add(f"{p}_{username}")
    
    leet_mods = username.replace('e', '3').replace('s', '5').replace('x', 'z')
    candidates.add(leet_mods)
    candidates.discard(username)

    return list(candidates)

def most_accurate(username, alphabet):
    v1 = to_vector(username, alphabet)
    candidates = generate_candidates(username)
    result = []
    username_length = len(username)

    for candidate in candidates:
        u = to_vector(candidate, alphabet) # Vectorizing Candidates 
        len2 = len(candidate)
        length_ratio = min(username_length, len2) / max(username_length, len2) # Lengths ratio (F.E 10/11)

        # Predicting Accurates
        if length_ratio >= 0.70:
            if cosine_similiarity(v1, u) >= 0.90: result.append(candidate)
                
    return result

