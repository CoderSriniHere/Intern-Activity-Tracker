"""The utility file where the intern finding function and 
the intern id generator is present"""

def find_intern(data, intern_id):
    for intern in data:
        if intern["intern_id"].lower() == intern_id.lower():
            return intern
    return None


def generate_intern_id(data):
    return f"INT{len(data) + 1:03d}"
