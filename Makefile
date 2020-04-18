#CROSSBARFX=/usr/local/bin/crossbarfx
CROSSBAR=crossbarfx edge
#CROSSBAR=crossbar
LEGO=/usr/local/bin/lego



run_backend:
	CBRUL=rs://localhost:8080 CBREALM=dvl1 python backend/backend.py

run_backend_docker:
	docker-compose up -d backend


# client using (secure) websocket
run_client:
	python backend/client.py --url=wss://lojack1.crossbario.com/ws --realm=dvl1 --iter=50

run_client_dev:
	python backend/client.py --url=ws://localhost:80/ws --realm=dvl1 --iter=50

run_client_forever:
	sh -c 'while true; do make run_client; done'

run_client_dev_forever:
	sh -c 'while true; do make run_client_dev; done'

# client using (secure) rawsocket
run_client_rawsocket:
	python backend/client.py --url=rss://lojack1.crossbario.com --realm=dvl1 --iter=50

run_client_dev_rawsocket:
	python backend/client.py --url=rs://localhost:80 --realm=dvl1 --iter=50

run_client_rawsocket_forever:
	sh -c 'while true; do make run_client_rawsocket; done'

run_client_rawsocket_dev_forever:
	sh -c 'while true; do make run_client_dev_rawsocket; done'


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

# sudo setcap 'cap_net_bind_service=+ep' /home/oberstet/cpy381/bin/python3.8
run_cb_host_config5_dev:
	$(CROSSBAR) start --cbdir=./node1/.crossbar/ --config=config5-dev.json


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
	python generate_config.py  lojack1.crossbario.com  config1.json.jinja ./node1/.crossbar/config1.json
	$(CROSSBAR) check --cbdir=./node1/.crossbar/ --config=config1.json

config2:
	python generate_config.py  lojack1.crossbario.com  config2.json.jinja ./node1/.crossbar/config2.json
	$(CROSSBAR) check --cbdir=./node1/.crossbar/ --config=config2.json

config3:
	python generate_config.py  lojack1.crossbario.com  config3.json.jinja ./node1/.crossbar/config3.json
	$(CROSSBAR) check --cbdir=./node1/.crossbar/ --config=config3.json

config4:
	python generate_config.py  lojack1.crossbario.com  config4.json.jinja ./node1/.crossbar/config4.json
	$(CROSSBAR) check --cbdir=./node1/.crossbar/ --config=config4.json

config5:
	CBPRODUCTION=0 python generate_config.py  lojack1.crossbario.com  config5.json.jinja ./node1/.crossbar/config5-dev.json 2 4
	CBPRODUCTION=1 python generate_config.py  lojack1.crossbario.com  config5.json.jinja ./node1/.crossbar/config5.json 2 4
	$(CROSSBAR) check --cbdir=./node1/.crossbar/ --config=config5.json

config5xl:
	CBPRODUCTION=0 python generate_config.py  lojack1.crossbario.com  config5.json.jinja ./node1/.crossbar/config5xl-dev.json 4 8
	CBPRODUCTION=1 python generate_config.py  lojack1.crossbario.com  config5.json.jinja ./node1/.crossbar/config5xl.json 4 8
	$(CROSSBAR) check --cbdir=./node1/.crossbar/ --config=config5xl-dev.json
	$(CROSSBAR) check --cbdir=./node1/.crossbar/ --config=config5xl.json

config5xl_lojack2:
	CBPRODUCTION=0 python generate_config.py  lojack2.crossbario.com  config5.json.jinja ./node2/.crossbar/config5xl-dev.json 8 16
	CBPRODUCTION=1 python generate_config.py  lojack2.crossbario.com  config5.json.jinja ./node2/.crossbar/config5xl.json 8 16
	$(CROSSBAR) check --cbdir=./node2/.crossbar/ --config=config5xl-dev.json
	$(CROSSBAR) check --cbdir=./node2/.crossbar/ --config=config5xl.json


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

cert_update2:
	AWS_REGION=us-east-1 $(LEGO) \
		--path ~/.lego \
		--accept-tos \
		--key-type "rsa4096" \
		--email "ops@crossbario.com" \
		--domains "lojack2.crossbario.com" \
		--dns "route53" \
		run

cert_upload2:
	scp ${HOME}/.lego/certificates/lojack2.crossbario.com.issuer.crt \
		ubuntu@lojack2.crossbario.com:~/scm/crossbario/lojack/node2/.crossbar/
	scp ${HOME}/.lego/certificates/lojack2.crossbario.com.key \
		ubuntu@lojack2.crossbario.com:~/scm/crossbario/lojack/node2/.crossbar/
	scp ${HOME}/.lego/certificates/lojack2.crossbario.com.crt \
		ubuntu@lojack2.crossbario.com:~/scm/crossbario/lojack/node2/.crossbar/

dhparam_generate2:
	openssl dhparam -2 4096 -out ./node2/.crossbar/dhparam.pem

dhparam_upload2:
	scp ./node2/.crossbar/dhparam.pem \
		ubuntu@lojack2.crossbario.com:~/scm/crossbario/lojack/node2/.crossbar/
