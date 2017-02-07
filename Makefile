.PHONY: clean add commit push discard status exe bin

clean:
	rm -f *.pyc

add:
	git add .

commit:
	git commit -m "automatico makefile"

push:
	git push

git: clean add commit push
	@echo "fin"

discard:
	git checkout .

status:
	git status

exe:
	pyinstaller Series_win.spec

bin:
	pyinstaller Series_linux.spec
