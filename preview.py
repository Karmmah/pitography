import time

def get_preview(cam, data):
	cam.capture(data, "rgb")
	return data

def main():
	try:
		print(input())

	except:
		print("no input")

	time.sleep(0.7)

if __name__ == "__main__":
	main()
