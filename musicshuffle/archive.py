import csv
import random

def generate_played(option):
    played = 0
    if option == "1":
        played = random.randint(1, 20)
    elif option == "2":
        played = random.randint(21, 40)
    else:
        played = random.randint(61, 80)
    return played


def convert_csv(file):
    data = {}
    with open(file, encoding='utf-8-sig')as f:
        reader = csv.DictReader(f)
        for row in reader:
            artists = row["artists"].split(";")
            tempo = "s"
            if 80 < float(row["tempo"]) < 120:
                tempo = "m"
            else:
                tempo = "f"
            if row["track_name"] not in data:
                data[row["track_name"]] = {"artist": artists, "played": row["played"], "tempo": tempo, "index": row["index"]}
    return data