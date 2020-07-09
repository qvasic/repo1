all: app test

clean:
	rm app

app: app.cpp lib.h lib.cpp
	g++ --std=c++11 -o $@ $^

test: app
	cat test-input | ./app | diff - test-expected
