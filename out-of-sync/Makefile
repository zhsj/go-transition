build:
	go build -ldflags='-w -s' .

sync: build
	rsync -avP ./out-of-sync people.debian.org:go-transition/out-of-sync/
