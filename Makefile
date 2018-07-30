clean:
	-rm -rf build
	-rm -rf dist
	-rm -rf *.egg-info
	-rm -f tests/.coverage
	-docker rm `docker ps -a -q`
	-docker rmi `docker images -q --filter "dangling=true"`

build: clean
	python setup.py bdist_wheel --universal

uninstall:
	-pip uninstall -y vlab-esrs-api

install: uninstall build
	pip install -U dist/*.whl

test: uninstall install
	cd tests && nosetests -v --with-coverage --cover-package=vlab_esrs_api

images: build
	sudo docker build -f ApiDockerfile -t willnx/vlab-esrs-api .
	sudo docker build -f WorkerDockerfile -t willnx/vlab-esrs-worker .

up:
	docker-compose -p vlabesrs up --abort-on-container-exit
