import fileinput
import time

def main():
	print("Subprocess is running")

	successes, fails = 0, 0
	while True:
#		for line in fileinput.input():
#			print("stdin:", line)
#		print(fileinput.input()[len(fileinput.input())])
		try:
#			print(fileinput.input())
			print(input())
			successes += 1

			if successes >= 10:
				print("SUCCESS")
				return

		except:
			print("no input")
			fails += 1

			if fails >= 10:
				print("FAIL")
				return

		time.sleep(0.7)

if __name__ == "__main__":
	print("test_subprocess.py started")
	main()
