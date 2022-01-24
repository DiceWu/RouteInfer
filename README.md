# RouteInfer

## What is RouteInfer?

RouteInfer is an interdomain path inference algorithm that infers paths between arbitrary sources and destinations in the Internet by capturing ISP routing behavior diversity and generality. You can learn more about RouteInfer in PAM 2022.

The source code of RouteInfer is in 'code/'. The analysis results are in 'analysis_result/'.

## Quickstart

RouteInfer runs with python 3.8

### Bootstrap AS-routing map

**Download BGP routing data from Route View and RIPE RIS and Isolario**

Route View: http://archive.routeviews.org/

RIPE RIS: https://www.ripe.net/analyse/internet-measurements/routing-information-service-ris/ris-raw-data

Isolario: https://www.isolario.it/

After download the raw data, you need to convert MRT files to ASCII. We recommend [BGP dump](https://github.com/RIPE-NCC/bgpdump).

Put BGP routing data in 'code/BGPdata/'.

**Data sanitization**

```sh
$ python code/bootstrap/cleandata.py
```

**Infer AS relationships**

```sh
$ perl code/bootstrap/infer_rel/asrank.pl code/bootstrap/sanitized_rib.txt code/bootstrap/asrel.txt
```

**Refine 3-tuples**

```sh
$ python code/bootstrap/3tuple.py
```

**Get periphery ASes**

```sh
$ python code/bootstrap/links.py
$ python code/bootstrap/periphery.py
```

**Get the mapping between prefixes to ASes**

```sh
$ python code/bootstrap/ip2as.py
```

**Compute the number of quasi-routers of each AS**

```sh
$ python code/bootstrap/quasi-router.py
```

**Classify BGP paths by destination prefix**

```sh
$ python code/bootstrap/paths.py
```

**Get AS links in topology**

```sh
$ python code/bootstrap/corelink.py
```

### 3-layer policies

**Extract prefix policies**

```sh
$ python code/3-layer_policy/infer_prefix_policies.py
```

**Policy aggregation**

```sh
$ python code/3-layer_policy/aggregate2destas.py
$ python code/3-layer_policy/aggregate2neighbor.py
```

### Route decision model

**Generate training data for training the route decision model**

```sh
$ python code/route_decision_model/buildtrain.py
$ python code/route_decision_model/buildtrain2.py
```

**Training the route decision model**

the details are in 'code\route_decision_model\LambdaMart\README.md'

## Analysis result

The analysis result of CDN ASes is in 'analysis_result/Top_Destination_ASes.csv'

The analysis result of IXP ASes is in 'analysis_result/Top_IXP.csv'