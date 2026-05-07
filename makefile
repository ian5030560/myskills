install:
	npx skills add $(skill) -y -a '*'

uninstall:
	npx skills remove $(skill) -y -a '*'