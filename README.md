# tg

**Disclaimer:** No generative language models were used for implementing this :)

## Modeling considerations

The task is (seemingly) focused on engineering so the training script is very basic, just enough to show a working model (such model can still be useful in the unit/integration testing though).

These are potential improvements to the training part:

- Data quality control
  - Run a basic EDA for the texts (build distributions for things like text length, labels)
  - Cleanup the data based on the EDA results - remove too short or too long texts, texts containing (too many) non-ASCII (non-alphanumeric for non-English languages) characters.
- The training and serving images must be split for:
  - docker image size efficiency (not all train time dependencies are need at inference time and vice versa)
  - the training code should push a trained model to a model registry and make it available for the inference service instead of baking it into the image
  - the training run metadata (like hyperparameters used, scores) should be recorded  
  - getting rid of redundant model retraining every time the image is built (strictly speaking not every time - the docker layers cache should prevent it if no upstream layers are changed)
- Zero-shot learning using a LLM instructed with a proper prompt is also an option here, however:
  - Depending on the prompt, output might not always belong to a set of predefined labels due to non-deterministic nature of LLMs
  - The inference time would most probably be higher due to redundancy of the universality of LLMs
- Proper model selection, i.e. trying several models, performing cross-validation, etc..
- More advanced model like Transformers could do a better job but they would come with computational cost during training and inference time
- The data has multiple non-exclusive labels so the model inherently supports that. The prediction value is a list of genres detected in provided overview, however it can be changed by predicting "probabilities" and having an `argmax` over them for example.

## Productionalisation considerations

**Note**: a similar setup is covered in [one of my blog posts](https://medium.com/towards-data-science/complete-machine-learning-pipeline-for-nlp-tasks-f39f8b395c0d) and remarks about productionalisation from there are relevant to this use case as well.

The app's implementation is again very basic due to time constraints, but following are the things that need to ba taken into account if it is going to serve reasonable production workloads:

- The app is stateless (doesn't rely on an external state storage which is shared among other instances) which makes scaling it pretty easy with adding a load balancer in from of it and replicating the instances (pods) using Kubernetes for example.
- Infrastructure design is not considered in the solution, but it might be from something as simple as an EC2 instance to a managed services like SageMaker model serving. Preferable, the cloud resources management should be done through (cloud provider agnostic) infrastructure as code tools like Terraform 
- No HTTPS, authentication, authorization and other security hardening were implemented because it is supposed to be an internal service working within a VPC together with other services and behind a firewall. Otherwise, in case of customer facing service, those should be added.
- For simplicity, models are saved as a pickle which is [not safe](https://docs.python.org/3/library/pickle.html). It is better to use an alternative serialization method if possible.
- Extensive testing:
  - Only one basic unit test was implemented, but in a real production app we should check not only happy path but, for example, if correct exceptions are raised etc.. and cover all the code that is coverable by unit tests.
  - Integration tests are also essential as the app is going to be a part of a bigger system. Having a simple docker compose with an additionl sidecar container making requests to the actual app could be a good start. 
  - The tests described above must be run as part of CI/CD pipeline triggered, for example, when a new change is pushed to a PR.
  - Load tests are usually optional or manual (it is hard to run them as part of CI/CD) but it is important to have a canary (or similar) deployment strategy so that a new version is rolled out for a part of the traffic and rolled back in case of errors.
- Monitoring is a must-have if the reliability and the speed of debugging are important (pretty much for any serious production deployment nowadays):
  - A distributed managed monitoring service like Datadog can be used. Otherwise, open-source alternatives like Prometheus are also available.
  - The following metrics could/should be monitored:
    - Prediction time from both server and client (consumer of the API) side.
    - Rate of HTTP codes returned by the server.
    - Rate of different predicted labels and predicted confidences for the model’s predictions drift detection. Change in rate of detections of a certain genre can tell about potential model obsolescence and need for retraining/fine tuning which can be triggered based on some drift threshold for example.
    - Input data parameters for detecting the input data distribution drift, for example, input texts’ lengths, word count, etc… Similar to the previous point but here the change may indicate that the nature of data has changed and the model might need to be adapted to it.
    - Standard host-related metrics like CPU load, memory/disk space, etc…
- The current implementation is fully synchronous which can create problems (data loss for example) if the service is unavailable:
  - Async endpoint handler can be an option but would require a system of delayed response delivery (like callbacks)
  - Switching from API requests to message queues like Kafka would decouple the service from its consumers and might smoothen spikes in load and avoid timeouts if the service can’t handle a high number of requests. In case of a temporary service outage, the service can also catch up on accumulated requests after going back online which would help to avoid data loss.  

## Running the app

### Prerequisites

- The dataset from [Kaggle](https://www.kaggle.com/datasets/rounakbanik/the-movies-dataset?select=movies_metadata.csv) must be placed to the `data` directory, i.e. `data/movies_metadata.csv` (Kaggle requires authentication before one can download the dataset so this prerequisite is added for simplicity).
- `docker` must be installed on the machine (it is assumed that any developer computer should have one nowadays).

### Testing

This is to be implemented as a CI/CD pipeline step but if it needs to be run locally, the following commands need to be executed:

```shell
pip install -r requirements.txt
pytest .
```

### Running the container and making requests

The building could take a couple of minutes, as the model training happens during that stage (depending on the host machine performance).

```shell
docker build -t tg .
docker run -d --name tg_container -p 8000:8000 tg
```
The container needs a couple of seconds to load the embeddings model. After that, requests can be made:
```shell
curl --header "Content-Type: application/json" \
  --request POST \
  --data '{"overview":"A movie about penguins in Antarctica building a spaceship to go to Mars."}' http://localhost:8000/

```
