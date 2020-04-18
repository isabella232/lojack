# Crossbar.io FX Test Bed

* [Node 1](https://lojack1.crossbario.com/info) - **m5a.8xlarge** (32 cores, AMD EPYC 7571 @ 2.5GHz)
* [Node 2](https://lojack2.crossbario.com/info) - **c5.4xlarge** (16 cores, Intel(R) Xeon(R) Platinum 8124M CPU @ 3.00GHz)

## Test setup

This test runs load clients on one machine, where the clients connect
over RawSocket-TCP (no TLS, CBOR serialization) and call a WAMP
procedure with 256 random bytes as the (single positional) argument.

The backend procedure called is running on the testee machine, and
simply returns the 256 random bytes provided as call argument.

* CrossbarFX configuration: 8 router worker, 16 proxy worker (ratio proxy-to-router workers is 2:1)
* 128 client connections were used (#router X #proxies => 8 X 16 = 128)

![AWS setup](screenshots/aws_setup.png "AWS setup")

## Test results

* more than **150,000 WAMP calls/sec** (@ 256 bytes/call) are performed by the load clients
* traffic runs over a real network (AWS internal) with almost 1Gb/s WAMP client (up+down) traffic
* **CrossbarFX consumes 12 CPU cores and 6GB RAM**
* the test was run constantly at **full load for more than an hour with zero errors**
* memory consumption remained constant, the testee machine stable

![router load](screenshots/parallel16/router_load.png "router load")

### Notes

At this performance (150,000 WAMP calls/sec @ 256 bytes/call), the resulting egress traffic, from CrossbarFX back to clients over the Internet, for which one needs to pay AWS:

* 509Mb/s egress * 24/7 = 158 TB / month
* at AWS prices, this is ~8,000 USD _monthly_ AWS data transfer bill!


### How to run

On **lojack2** (c5.4xlarge):

```
docker-compose up node2
```

and

```
docker-compose up backend
```

On **lojack1** (m5a.8xlarge):

```
(pypy3_1) ubuntu@lojack1:~/scm/crossbario/lojack$ pypy3 backend/client.py --url=rs://lojack2.crossbario.com:80 --parallel=16
```

![client](screenshots/parallel16/client.png "client")


![client load](screenshots/parallel16/client_load.png "client load")


![router load](screenshots/parallel16/router_load.png "router load")



## tldr;

Login:

```console
ssh ubuntu@lojack1.crossbario.com
source ~/cpy381_1/bin/activate
cd ~/scm/crossbario/lojack/
```

```console
ssh ubuntu@lojack2.crossbario.com
source ~/cpy381_1/bin/activate
cd ~/scm/crossbario/lojack/
```

Docker:

```console
docker ps

docker logs --tail 40 lojack_crossbarfx_config5_1
docker logs -f lojack_crossbarfx_config5_1

docker logs lojack_crossbarfx_config5_1 >& cb-logs1.txt

docker top lojack_crossbarfx_config5_1

docker exec -it lojack_crossbarfx_config5_1 bash
```

Crossbar:

```console
docker pull crossbario/crossbarfx:cpy-slim-amd64
docker run --rm crossbario/crossbarfx:cpy-slim-amd64 version

docker pull crossbario/crossbarfx:pypy-slim-amd64
docker run --rm crossbario/crossbarfx:pypy-slim-amd64 version

docker exec -it lojack_crossbarfx_config5_1 ls -la /node/.crossbar/

docker exec -it lojack_crossbarfx_config5_1 \
    /usr/local/bin/crossbarfx edge status --cbdir=/node/.crossbar
```

## Configuration

* Region: `us-east-1`
* AZ: `us-east-1c`
* Placement group: `crossbarfx`
* Instance type: `m5a.xlarge`

### Instances

* VM 1: `lojack1.crossbario.com` (`52.71.32.105`)

### TLS

![shot 1](screenshots/shot1.png "shot 1")
![shot 1](screenshots/shot2.png "shot 2")

## VSCode Jinja highlighting

* https://marketplace.visualstudio.com/items?itemName=samuelcolvin.jinjahtml
* https://github.com/samuelcolvin/jinjahtml-vscode
