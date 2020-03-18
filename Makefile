CROSSBARFX=/usr/local/bin/crossbarfx
LEGO=/usr/local/bin/lego

run_crossbarfx_config1:
	docker-compose up crossbarfx_config1

run_crossbarfx_config2:
	docker-compose up crossbarfx_config2

run_crossbarfx_config3:
	docker-compose up crossbarfx_config3

download_exe:
	cd /tmp && rm -f ./crossbarfx-latest && \
		wget https://download.crossbario.com/crossbarfx/linux-amd64/crossbarfx-latest && \
		chmod +x ./crossbarfx-latest && sudo cp ./crossbarfx-latest /usr/local/bin/crossbarfx
	$(CROSSBARFX) version

configs: config1 config2 config3

config1:
	python generate_config.py config1.json
	$(CROSSBARFX) edge check --cbdir=./node1/.crossbar/ --config=config1.json

config2:
	python generate_config.py config2.json
	$(CROSSBARFX) edge check --cbdir=./node1/.crossbar/ --config=config2.json

config3:
	python generate_config.py config3.json
	$(CROSSBARFX) edge check --cbdir=./node1/.crossbar/ --config=config3.json

config_upload:
	scp ./node1/.crossbar/config.json \
		ubuntu@lojack1.crossbario.com:~/scm/crossbario/lojack/node1/.crossbar/

cert_update:
	AWS_REGION=us-east-1 $(LEGO) \
		--path ~/.lego \
		--accept-tos \
		--key-type "rsa4096" \
		--email "ops@crossbario.com" \
		--domains "lojack1.crossbario.com" \
		--dns "route53" \
		run

cert_upload:
	scp ${HOME}/.lego/certificates/lojack1.crossbario.com.issuer.crt \
		ubuntu@lojack1.crossbario.com:~/scm/crossbario/lojack/node1/.crossbar/
	scp ${HOME}/.lego/certificates/lojack1.crossbario.com.key \
		ubuntu@lojack1.crossbario.com:~/scm/crossbario/lojack/node1/.crossbar/
	scp ${HOME}/.lego/certificates/lojack1.crossbario.com.crt \
		ubuntu@lojack1.crossbario.com:~/scm/crossbario/lojack/node1/.crossbar/

dhparam_generate:
	openssl dhparam -2 4096 -out ./node1/.crossbar/dhparam.pem

dhparam_upload:
	scp ./node1/.crossbar/dhparam.pem \
		ubuntu@lojack1.crossbario.com:~/scm/crossbario/lojack/node1/.crossbar/
