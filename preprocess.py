import requests
import json
import msgpack
from collections import defaultdict


urls = ['https://mcsr-downloads.mrderp.dev/download/season_11_20260726_070247.jsonl', 'https://mcsr-downloads.mrderp.dev/download/season_10_20260612_070659.jsonl', 'https://mcsr-downloads.mrderp.dev/download/season_9_20260120_032706.jsonl', 'https://mcsr-downloads.mrderp.dev/download/season_8_20260120_025544.jsonl', 'https://mcsr-downloads.mrderp.dev/download/season_7_20260120_025141.jsonl', 'https://mcsr-downloads.mrderp.dev/download/season_6_20260120_024942.jsonl', 'https://mcsr-downloads.mrderp.dev/download/season_5_20260120_024814.jsonl', 'https://mcsr-downloads.mrderp.dev/download/season_4_20260120_024646.jsonl', 'https://mcsr-downloads.mrderp.dev/download/season_3_20260120_024539.jsonl', 'https://mcsr-downloads.mrderp.dev/download/season_2_20260120_024453.jsonl', 'https://mcsr-downloads.mrderp.dev/download/season_1_20260120_024355.jsonl']
players = []
uuid_to_id = {}

graph = defaultdict(list)


def get_player_id(player):
    uuid = player["uuid"]

    if uuid not in uuid_to_id:
        uuid_to_id[uuid] = len(players)

        players.append({
            "uuid": uuid,
            "nickname": player.get("nickname")
        })

    return uuid_to_id[uuid]


def process_match(match):
    if match.get('type', 0) != 2:
        return
    
    if len(match.get("players", [])) != 2:
        return

    if match.get('forfeited'):
        return

    players_data = match["players"]

    winner_uuid = match.get("result", {}).get("uuid")

    if winner_uuid is None:
        return

    if players_data[0]["uuid"] == winner_uuid:
        winner = players_data[0]
        loser = players_data[1]
    else:
        winner = players_data[1]
        loser = players_data[0]

    winner_id = get_player_id(winner)
    loser_id = get_player_id(loser)

    match_id = match["id"]

    graph[winner_id].append(
        (
            loser_id,     
            winner_id,    
            loser_id,     
            match_id
        )
    )

    graph[loser_id].append(
        (
            winner_id,
            winner_id,
            loser_id,
            match_id
        )
    )

print("Downloading matches...")

for url in urls:
    with requests.get(url, stream=True) as response:
        response.raise_for_status()

        count = 0

        for line in response.iter_lines():
            if not line:
                continue

            match = json.loads(line)

            process_match(match)

            count += 1

            if count % 100000 == 0:
                print(
                    f"Processed {count:,} matches | "
                    f"Players: {len(players):,}"
                )


print("Saving players...")

with open("players.json", "w", encoding="utf-8") as f:
    json.dump(players, f)

print("Saving graph...")

graph = dict(graph)

with open("graph.msgpack", "wb") as f:
    msgpack.pack(
        graph,
        f,
        use_bin_type=True
    )

print(
    f"Done\n"
    f"Matches: {count:,}\n"
    f"Players: {len(players):,}\n"
    f"Edges: {sum(len(x) for x in graph.values()):,}"
)