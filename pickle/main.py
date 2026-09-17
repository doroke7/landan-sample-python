import pickle

data = [1, 2, 3, 4]

with open("data.pkl", "wb") as f:
    pickle.dump(data, f)