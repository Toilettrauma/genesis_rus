import os
import json
import re

quests_chapters_path = r"F:\bts\genesis_rus\orig_quests"
lang_name = "ru_RU"
quests_output_folder = r"F:\bts\genesis_rus\quests"
lang_output_folder = r"F:\bts\genesis_rus"

# lang_filepath = os.path.join(r"kubejs\assets\ftbgenesis\lang", ".".join((lang_name, "json")))

def abs_listdir(directory):
	for file in os.listdir(directory):
		yield os.path.abspath(os.path.join(directory, file)), file

def string_unbackslash(string):
	# return string.encode('utf-8').decode('utf-8')
	return string.replace("\\\\", "\\").replace("\\\"", "\"")
def string_tobackslash(string):
	return string.replace("\\", "\\\\").replace("\"", "\\\"")
def forward_tabs(str_from, str_to):
	return '\t' * str_from.count('\t') + str_to

# sorted in future
def _json_lang_parse(fmt_line, lang_prefix, lang_dict) -> str:
	# print("matched ", string_unbackslash(fmt_line))
	json_format = json.loads(string_unbackslash(fmt_line.strip("\t\"")))
	text_index = 0
	format_index = 0
	for i, item in enumerate(json_format):
		if isinstance(item, str) and item:
			lang_key = f"{lang_prefix}.format.text_{text_index}"
			text_index += 1

			lang_dict.update({lang_key : item})
			json_format[i] = {"translate": lang_key}
		elif isinstance(item, dict):
			lang_key = f"{lang_prefix}.format.format_{format_index}"
			format_index += 1

			lang_dict.update({lang_key : item["text"]})
			del item["text"]
			item["translate"] = lang_key
			

	if json_format[0]:
		json_format.insert(0, "")
	if json_format[-1]:
		json_format.append("")

	return string_tobackslash(json.dumps(json_format))
json_formatting_re = re.compile(r"\\\"text\\\":\\\"([^\"]+)\\\"")
"""
fp: quest .snbt file pointer
lang_prefix: lang keys prefix
out_fp: quest output .snbt file pointer
lang_dict: lang keys dictionary to add
"""
def parser_parse(fp, lang_prefix, out_fp, lang_dict):
	desc_found = False
	tasks_found = False
	display_found = False
	task_index = -1 # :C
	desc_index = 0
	reward_index = 0
	for line in fp:
		line = line.rstrip()
		strip_line = line.strip()

		if strip_line == "]" and desc_found:
			desc_found = False
			desc_index = 0
			out_line = line
		elif strip_line == "]" and tasks_found:
			tasks_found = False
			reward_index = 0
			out_line = line
		elif strip_line == "}" and display_found:
			display_found = False
			out_line = line

		elif desc_found:
			if strip_line == "\"\"" or strip_line == "\"{@pagebreak}\"" or "{image:ftbgenesis" in strip_line:
				# empty line or just pagebreak or image. skip
				out_line = line
			else:
				# JSON formatting
				match = re.search(json_formatting_re, line)
				if match:
					# something with json formatting
					out_json_str = _json_lang_parse(line, f"{lang_prefix}.task_{task_index}.desc_{desc_index}", lang_dict)
					desc_index += 1

					out_line = forward_tabs(line, "\"" + out_json_str + "\"")

				else:
					form_line = line.strip("\t\"\n").replace("\\", "")
					lang_key = f"{lang_prefix}.task_{task_index}.desc_{desc_index}"
					desc_index += 1

					out_line = forward_tabs(line, f"\"{{{lang_key}}}\"")
					lang_dict.update({lang_key : form_line})
		elif tasks_found and display_found and strip_line.startswith("Name: "):
			json_format = json.loads(string_unbackslash(line.replace("Name: ", "").strip("\t\"")))
			lang_key = f"{lang_prefix}.task_{task_index}.reward_{reward_index}.display_name"
			reward_index += 1

			text = json_format.get("text")
			if text:
				del json_format["text"]
				json_format["translate"] = lang_key

				lang_dict.update({lang_key : text})
			out_line = forward_tabs(line, "Name: \"" + string_tobackslash(json.dumps(json_format)) + "\"")

		elif strip_line.startswith("description: ["):
			task_index += 1
			form_line = line.replace("description: ", "", 1).strip("\t[]").strip("\"")
			if "]" in line:
				# one line description
				# JSON formatting
				match = re.search(json_formatting_re, form_line)
				if match:
					# something with json formatting
					out_json_str = _json_lang_parse(form_line, f"{lang_prefix}.task_{task_index}.desc_{desc_index}", lang_dict)

					out_line = forward_tabs(line, "description: [\"" + out_json_str + "\"]")
				else:
					form_line = form_line.replace("\\", "")
					lang_key = f"{lang_prefix}.task_{task_index}.desc"
					out_line = forward_tabs(line, f"description: [\"{{{lang_key}}}\"]")

					lang_dict.update({lang_key : form_line})
			else:
				# multi line description
				desc_found = True
				out_line = line
		elif strip_line.startswith("display: {"):
			display_found = True
			out_line = line
		elif strip_line.startswith("tasks: ["):
			tasks_found = True
			out_line = line

		elif strip_line.startswith("title: "):
			if line.count("\t") == 1:
				# page title
				form_line = line.replace("title: ", "").strip("\t\"\n").replace("\\", "")
				lang_key = f"{lang_prefix}.title"

				lang_dict.update({lang_key : form_line})
				out_line = forward_tabs(line, f"title: \"{{{lang_key}}}\"")
			else:
				# task title
				form_line = line.replace("title: ", "").strip("\t\"\n").replace("\\", "")
				lang_key = f"{lang_prefix}.task_{task_index}.title"
				lang_dict.update({lang_key : form_line})

				lang_dict.update({lang_key : form_line})
				out_line = forward_tabs(line, f"title: \"{{{lang_key}}}\"")
		elif strip_line.startswith("subtitle: "):
			form_line = line.replace("subtitle: ", "").strip("\t\"\n").replace("\\", "")
			lang_key = f"{lang_prefix}.task_{task_index}.subtitle"
			lang_dict.update({lang_key : form_line})

			lang_dict.update({lang_key : form_line})
			out_line = forward_tabs(line, f"subtitle: \"{{{lang_key}}}\"")

		else:
			out_line = line

		out_fp.write(f"{out_line}\n")


with open(os.path.join(lang_output_folder, lang_name) + ".json", "w", encoding="utf-8") as lang_fp:
	lang_dict = {}
	for absfile, file in abs_listdir(quests_chapters_path):
		print("parsing ", file, os.path.join(quests_output_folder, file))
		with open(absfile, "r", encoding="utf-8") as fp, open(os.path.join(quests_output_folder, file), "w", encoding="utf-8") as out_fp:
			parser_parse(fp, "gen." + os.path.splitext(file)[0], out_fp, lang_dict)

	lang_fp.write(json.dumps(lang_dict, indent=4, ensure_ascii=False).encode("utf-8").decode("utf-8"))