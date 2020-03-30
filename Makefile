#CROSSBARFX=/usr/local/bin/crossbarfx
CROSSBAR=crossbarfx edge
#CROSSBAR=crossbar
LEGO=/usr/local/bin/lego


run_backend:
	CBRUL=rs://localhost:8080 CBREALM=dvl1 python backend/backend.py

run_client:
	CBRUL=rs://localhost:8080 CBREALM=dvl1 python backend/client.py


run_cb_host_config1:
	$(CROSSBAR) start --cbdir=./node1/.crossbar/ --config=config1.json

run_cb_host_config2:
	$(CROSSBAR) start --cbdir=./node1/.crossbar/ --config=config2.json

run_cb_host_config3:
	$(CROSSBAR) start --cbdir=./node1/.crossbar/ --config=config3.json

run_cb_host_config4:
	$(CROSSBAR) start --cbdir=./node1/.crossbar/ --config=config4.json

run_cb_host_config5:
	$(CROSSBAR) start --cbdir=./node1/.crossbar/ --config=config5.json


run_cb_docker_config1:
	docker-compose up crossbarfx_config1

run_cb_docker_config2:
	docker-compose up crossbarfx_config2

run_cb_docker_config3:
	docker-compose up crossbarfx_config3

run_cb_docker_config4:
	docker-compose up crossbarfx_config4

run_cb_docker_config5:
	docker-compose up crossbarfx_config5


# run_backend:
# 	CBURL=ws://lojack1.crossbario.com/ws python backend/client.py

# run_backend_secure:
# 	CBURL=wss://lojack1.crossbario.com/ws python backend/client.py

# run_backend_local:
# 	CBURL=ws://localhost:8080/ws python backend/client.py


download_exe:
	cd /tmp && rm -f ./crossbarfx-latest && \
		wget https://download.crossbario.com/crossbarfx/linux-amd64/crossbarfx-latest && \
		chmod +x ./crossbarfx-latest && sudo cp ./crossbarfx-latest /usr/local/bin/crossbarfx
	$(CROSSBAR) version


configs: config1 config2 config3 config4 config5

config1:
	python generate_config.py config1.json.jinja ./node1/.crossbar/config1.json
	$(CROSSBAR) check --cbdir=./node1/.crossbar/ --config=config1.json

config2:
	python generate_config.py config2.json.jinja ./node1/.crossbar/config2.json
	$(CROSSBAR) check --cbdir=./node1/.crossbar/ --config=config2.json

config3:
	python generate_config.py config3.json.jinja ./node1/.crossbar/config3.json
	$(CROSSBAR) check --cbdir=./node1/.crossbar/ --config=config3.json

config4:
	python generate_config.py config4.json.jinja ./node1/.crossbar/config4.json
	$(CROSSBAR) check --cbdir=./node1/.crossbar/ --config=config4.json

config5:
	CBPRODUCTION=1 python generate_config.py config5.json.jinja ./node1/.crossbar/config5.json
	$(CROSSBAR) check --cbdir=./node1/.crossbar/ --config=config5.json

configs_upload: configs
	scp ./node1/.crossbar/config*.json \
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
