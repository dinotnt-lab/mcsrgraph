import json

with open('players.json', 'r') as f:
    x = json.load(f)

print(x[29710])