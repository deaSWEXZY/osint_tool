import string
import numpy as np

alphabet = string.ascii_lowercase + string.digits + "_"


def to_vector(username, alphabet):
    vector = []

    for char in alphabet:
        count = username.count(char)
        vector.append(count)
    return vector

def cosine_similiarity(v, u):
    dot_product = np.dot(v, u)
    v_magnitude = np.linalg.norm(v)
    u_magnitude = np.linalg.norm(u)

    return (dot_product / (v_magnitude * u_magnitude)) 


def generate_candidates(username):
    candidates = set()

    common_chars = ["_", "official", "1", "777", "999", "$", "x", "real"]

    for p in common_chars:
        candidates.add(f"{username}{p}")
        candidates.add(f"{p}{username}")
        candidates.add(f"{username}_{p}")
        candidates.add(f"{p}_{username}")
    
    leet_mods = username.replace('e', '3').replace('s', '5').replace('x', 'z')
    candidates.add(leet_mods)


    for x in range(len(username)):
        double_char = username[:x] + username[x] + username[:x]
        candidates.add(double_char)
    
    candidates.discard(username)

    return list(candidates)

print(generate_candidates("swexzy"))