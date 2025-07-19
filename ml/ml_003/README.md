Project Reference:
https://www.youtube.com/watch?v=o6vbe5G7xNo




## Install zenml and mlflow integration
- zenml is used for ml pipeline (to execute learning and evaluation steps)

- mlflow is used to track evalution, metrix and metrics artifacts

- hence, both tool must be integrated.

``` bash
curl -sS https://bootstrap.pypa.io/get-pip.py | python

```
```bash
zenml integration install mlflow --uv -y


zenml experiment-tracker register mlflow_tracker --flavor=mlflow

zenml stack update <stack-name> --experiment-tracker mlflow_tracker

zenml stack update default -e mlflow_tracker

```
