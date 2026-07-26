import json
import msgpack
from collections import deque


print("Loading players...")

with open("players.json", "r", encoding="utf-8") as f:
    players = json.load(f)


print("Loading graph...")

with open("graph.msgpack", "rb") as f:
    graph = msgpack.unpack(f, raw=False, strict_map_key=False)


uuid_to_id = {}
name_to_id = {}

for i, player in enumerate(players):
    uuid_to_id[player["uuid"]] = i

    if player["nickname"]:
        name_to_id[player["nickname"].lower()] = i


print(
    f"Loaded {len(players):,} players"
)


def find_path(start_id, target_id):
    if start_id == target_id:
        return [start_id], []


    queue = deque([start_id])

    visited = {start_id}

    parent = {}
    parent_edge = {}


    while queue:
        current = queue.popleft()

        for neighbour, winner, loser, match_id in graph.get(str(current), graph.get(current, [])):

            if neighbour in visited:
                continue

            visited.add(neighbour)

            parent[neighbour] = current

            parent_edge[neighbour] = {
                "winner": winner,
                "loser": loser,
                "match_id": match_id
            }


            if neighbour == target_id:
                return build_path(
                    start_id,
                    target_id,
                    parent,
                    parent_edge
                )


            queue.append(neighbour)


    return None, None



def build_path(start, end, parent, edges):

    nodes = []
    matches = []

    current = end

    while current != start:
        nodes.append(current)

        matches.append(
            edges[current]
        )

        current = parent[current]


    nodes.append(start)

    nodes.reverse()
    matches.reverse()

    return nodes, matches



def search(name1, name2):

    id1 = name_to_id.get(name1.lower())
    id2 = name_to_id.get(name2.lower())

    if id1 is None:
        print(f"Unknown player: {name1}")
        return

    if id2 is None:
        print(f"Unknown player: {name2}")
        return


    path, matches = find_path(id1, id2)


    if path is None:
        print("No connection found")
        return


    print()
    print(
        f"Distance: {len(path)-1}"
    )
    print()


    for i, player_id in enumerate(path):

        print(
            players[player_id]["nickname"]
        )

        if i < len(matches):

            match = matches[i]

            print(
                f"  └─ Match {match['match_id']}: "
                f"{players[match['winner']]['nickname']} "
                f"defeated "
                f"{players[match['loser']]['nickname']}"
            )



while True:

    a = input("\nPlayer 1: ")
    b = input("Player 2: ")

    search(a, b)