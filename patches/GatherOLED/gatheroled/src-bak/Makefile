all: daemonize.c daemonize.h main.c
	$(CC) daemonize.c main.c -lrt -lpthread -o GatherOLED

clean:
	rm GatherOLED