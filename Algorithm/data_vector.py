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

def similiar_names(v1, alphabet):
    new_username = ""
    for char in alphabet:
        new_username += char
        v2 = to_vector(new_username, alphabet)
    similiarity = cosine_similiarity(v1, v2)
    
    return new_username, similiarity

v1 = to_vector("swexzy", alphabet)
print(similiar_names(v1, alphabet))
