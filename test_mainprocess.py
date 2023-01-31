import subprocess
import test_subprocess
import time

def main():
#	with subprocess.Popen(["python test_subprocess.py"], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as sp:
#	with subprocess.Popen(["python test_subprocess.py"], shell=True, stdin=subprocess.PIPE, text=True) as sp:
	with subprocess.Popen(["python", "test_subprocess.py"], stdin=subprocess.PIPE, text=True) as sp:
		i = 0
		time.sleep(2)

		while True:
#			outs, errs = sp.communicate(input="Hello Subprocess"+str(i))
#			print("looop",outs,errs)
#			sp.stdin.write("Hello Subprocess"+str(i)+"\n")
			sp.communicate(input="Hello Subprocess"+str(i)+"\n")
			print("sp.returncode", sp.returncode)
			i += 1
			time.sleep(0.1)

if __name__ == "__main__":
	main()
