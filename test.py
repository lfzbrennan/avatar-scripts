from logger import Logger
import subprocess
import os
import sys

defects4j_path = "/home/liam/defects4j/framework/bin/defects4j"

data_root = "/home/liam/defects4j_data/"

avatar_path = "/home/liam/AVATAR/"

augment_path = "/home/liam/avatar_scripts/javaparser.py"

bug_positions_file = avatar_path + "BugPositions.txt"

with open(bug_positions_file, "r") as f:
	lines = f.readlines()
	bug_positions = [line.split("@") for line in lines]


projects = {
	"Chart": 26,
	"Cli": 39,
	"Closure": 174,
	"Codec": 18,
	"Collections": 4,
	"Compress": 47,
	"Csv": 16,
	"Gson": 18,
	"JacksonCore": 26,
	"JacksonDatabind": 112,
	"JacksonXml": 6,
	"Jsoup": 93,
	"JxPath": 22,
	"Lang": 64,
	"Math": 106,
	"Mockito": 38,
	"Time": 26
}

logger = Logger(os.getcwd() + "/out.log")

logger.log("Starting experiment")
for name, n_bugs in projects.items():
	for i in range(1, n_bugs + 1):
		try:
			name_plus_bug = f"{name}_{i}"
			project_directory = data_root + name_plus_bug

			# setup the repo

			checkout = f"{defects4j_path} checkout -p {name} -v {i}b -w {project_directory}"
			subprocess.run(checkout, shell=True, check=True)
			os.chdir(project_directory)
			compile = f"{defects4j_path} compile"
			subprocess.run(compile, shell=True, check=True)
			os.chdir(avatar_path)

			print("done setup")
			# fix normal

			fix_normal = f"{avatar_path}/LineFix.sh {name_plus_bug}"
			fix_normal_out = subprocess.run(fix_normal, shell=True, check=True, capture_output=True).stdout.decode()
			fix_normal_out = fix_normal_out.split("\n")[-1]
			fixed_normal = f"=======Succeeded to fix bug {name_plus_bug}" in fix_normal_out

			print("done normal")
			# create augment

			position = list(filter(lambda x : x[0] == name_plus_bug, bug_positions))[0]
			file = f"{data_root}/{name_plus_bug}/{position[1]}"
			lines_raw = position[2]

			if len(lines_raw.split(",")) != 1:
				lines = [int(line) for line in lines_raw.split(",")]
			elif "-" in lines_raw:
				raw_split = lines_raw.split("-")
				lines = list(range(int(raw_split[0]), int(raw_split[1])))
			else:
				lines = [int(lines_raw)]

			for l in lines:
				command = f"python3 {augment_path} {file} {l}"
				subprocess.run(command, shell=True, check=True)

			os.chdir(project_directory)
			compile = f"{defects4j_path} compile"
			subprocess.run(compile, shell=True, check=True)
			os.chdir(avatar_path)

			print("done augment")
			# redo the fixaugment
			fix_augment = f"{avatar_path}/LineFix.sh {name_plus_bug}"
			fix_augment_out = subprocess.run(fix_augment, shell=True, check=True, capture_output=True).stdout.decode()
			fix_augment_out = fix_augment_out.split("\n")[-1]
			fixed_augment = f"=======Succeeded to fix bug {name_plus_bug}" in fix_augment_out

			# log
			logger.log(f"{name} {i}\tNormal: {fixed_normal}\tAugment: {fixed_augment}")
		except Exception as e:
			print(e)
			logger.log(f"Error with {name} {i}")

print("Done")






