import os
from itertools import zip_longest

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

URI = os.getenv("MONGODB_URI")
assert URI, "MONGODB_URI not found in .env"

client = MongoClient(URI)

db = client.busse_data
pkg_coll = db.pkg

# parts = "717, 718, 723, 724, 726, 729, 737, 732, 5822, 7190, 9201"
parts = input("Enter parts: <,> separated: ")

if parts:
    parts = [x.strip() for x in parts.split(",")]


part_map = {}

for part in parts:
    doc = pkg_coll.find_one({"part": part})
    if doc:
        components = doc["components"].split("|")
        descriptions = doc["components_description"].split("|")
        part_map[part] = dict(zip_longest(components, descriptions, fillvalue=""))
        if doc["component_2"] != "":
            component_2 = doc["component_2"].split("|")
            description_2 = doc["components_description_2"].split("|")
            part_map[part].extend(
                dict(zip_longest(component_2, description_2, fillvalue=""))
            )

# print(part_map)

part_description_map = {}

for each in part_map:
    for key, value in part_map[each].items():
        if key not in part_description_map:
            part_description_map[key] = value


# print(part_description_map)

unique_part_map = {}

components = []

for part in part_map.values():
    components.extend(part)

components = list(set(components))

# print(components)

for part, components_list in part_map.items():
    for c in components:
        if c in components_list:
            if c in unique_part_map:
                unique_part_map[c].append(part)
            else:
                unique_part_map[c] = [part]

print("component|show_where_used")
for comp, parts in unique_part_map.items():
    print(
        f"{comp.replace(';', '').strip()}|{','.join([part.replace(';', '').strip() for part in parts])}"
    )

print()

print("component|component_description")
sorted_unique_part_map_keys = sorted(unique_part_map.keys())

iterated = []
for comp in sorted_unique_part_map_keys:
    _comp = comp.replace(";", "").strip()
    if _comp not in iterated:
        iterated.append(_comp)
        print(f"{_comp}|{part_description_map[comp]}")
