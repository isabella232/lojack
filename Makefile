CROSSBARFX=/usr/local/bin/crossbarfx
LEGO=/usr/local/bin/lego

run_crossbarfx:
	docker-compose up crossbarfx

download_exe:
	cd /tmp && rm -f ./crossbarfx-latest && \
		wget https://download.crossbario.com/crossbarfx/linux-amd64/crossbarfx-latest && \
		chmod +x ./crossbarfx-latest && sudo cp ./crossbarfx-latest /usr/local/bin/crossbarfx
	$(CROSSBARFX) version

config1:
	python generate_config.py config1.json
	$(CROSSBARFX) edge check --cbdir=./node1/.crossbar/ --config=config.json

config2:
	python generate_config.py config2.json
	$(CROSSBARFX) edge check --cbdir=./node1/.crossbar/ --config=config.json

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
