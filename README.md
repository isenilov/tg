# tg

## Productionalisation considerations

The app's implementation is very basic due to time constraints, but following are the things that need to ba taken into account if it is going to serve reasonable production workloads. 

- The app is stateless (doesn't rely on an external state storage which is shared among other instances) which makes scaling it pretty easy with adding a load balancer in from of it and replicating the instances (pods) using Kubernetes for example.
- 

## Running the app

```shell
docker build -t tg .
docker run --name tg_container -p 3000:3000 tg
```