import os
import json
from nbtlib import parse_nbt
import nbtlib
import re

instance_path = r"C:\Users\ADMIN\AppData\Local\.ftba\instances\adf085e9-d4dc-43f9-9237-b37d7c1d647a"
lang_name = "ru_RU"

quests_root = r"config\ftbquests\quests"
chapters_path = os.path.join(quests_root, "chapters")
lang_filepath = os.path.join(r"kubejs\assets\ftbgenesis\lang", ".".join((lang_name, "json")))

def abs_listdir(directory):
	for file in os.listdir(directory):
		yield os.path.abspath(os.path.join(directory, file))

def snbt_to_json(snbt):
	formatted = snbt.replace("I;", "")
	formatted = re.sub(r"(\d+)[dbL](\n)", r"\1\2", formatted)                            # remove d after double
	formatted = re.sub(r"([^\{\[]|[\}\]])(\n[ \t]*[^ \t\}\]])", r"\1,\2", formatted) # add separator after newlines
	formatted = re.sub(r"(\t)(\w[\w\d]*)(: )", r"""\1"\2"\3""", formatted)                    # add quotes to keys
	return formatted

quests_json = []
for file in abs_listdir(os.path.join(instance_path, chapters_path)):
	print("parsing ", file)
	with open(file, "r") as fp:
		# formatted = re.sub(r"[^\{\[]\n", ",", fp.read())
		# data = parse_nbt(formatted)
		formatted = snbt_to_json(fp.read())
		with open("test.json", "w") as f:
			f.write(formatted)
		data = json.loads(formatted)
		quests_json.append(data)

with open(os.path.join(chapters_path, "chapter_groups.snbt")) as fp:
	groups_json = parse_nbt(fp.read())

quests = {"" : {}}
for group in groups_json["chapter_groups"]:
	quests[group["id"]] = {}

for quest_json in quests_json:
	group_quests = quests[quest_json["group"]]
	group_quests.update({quest_json["order_index"] : {quest_json["filename"] : quest_json["quests"]}})


print(quests)
input()