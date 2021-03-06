.PHONY: clean add commit push discard status exe bin


compila:
	python3 compila_ui.py

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

systemd:
	@sudo cp mio_bot_series_manager.service /lib/systemd/system/
	@sudo chmod 644 /lib/systemd/system/mio_bot_series_manager.service
	@sudo systemctl daemon-reload
	@sudo systemctl enable mio_bot_series_manager.service
	@sudo systemctl start mio_bot_series_manager.service

