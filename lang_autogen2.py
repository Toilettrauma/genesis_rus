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

# sorted in future

title_replacer_re = re.comple(r"")
def title_replacer(match):
	pass

description_inner_replacer_re = re.compile(r"\".*?\"")
def description_inner_replacer(match):
	pass

description_outer_replacer_re = re.compile(r"description: ? \[((?:[\t\n ]*(?:\".*?[^\\]\"|\"\")\n?)+)[\t\n ]*\]")
def description_outer_replacer(match):
	pass

with open(os.path.join(instance_path, lang_filepath), "w") as lang_fp:
	for file in abs_listdir(os.path.join(instance_path, chapters_path)):
		print("parsing ", file)
			with open(file, "r") as fp:
