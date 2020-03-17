config_upload:
	scp .crossbar/config.json \
		ubuntu@lojack1.crossbario.com:~/scm/crossbario/lojack/node1/.crossbar/

cert_update:
	AWS_REGION=us-east-1 /usr/local/bin/lego \
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

dhparam_upload:
	scp .crossbar/dhparam.pem \
		ubuntu@lojack1.crossbario.com:~/scm/crossbario/lojack/node1/.crossbar/
