# Define a PHONY target to tell Make that these aren't actual files.
.PHONY: deployment_build_push deployment_delete_pods deployment_redeploy heroku_build_push heroku_redeploy

# Target for building, pushing the Docker image, and applying the Kubernetes deployment.
api_build_push:
	docker build -t gcr.io/animax-423606/api:latest -f cloudfiles/api.dockerfile .
	docker push gcr.io/animax-423606/api:latest
	kubectl apply -f ./cloudfiles/api.yaml

# Target for deleting pods based on a label selector.
api_delete_pods:
	kubectl delete pods -l app=execute-app
	kubectl delete pods -l app=api-app

api_redeploy: api_build_push api_delete_pods

# Target for building, pushing the Docker image, and applying the Kubernetes deployment.
executor_build_push:
	docker build -t gcr.io/animax-423606/executor:latest -f cloudfiles/executor.dockerfile .
	docker push gcr.io/animax-423606/executor:latest
	kubectl apply -f ./cloudfiles/executor.yaml

# Target for deleting pods based on a label selector.
executor_delete_pods:
	kubectl delete pods -l app=executor-app

executor_redeploy: executor_build_push executor_delete_pods

# Target to redeploy by building, pushing and deleting old pods.
deployment_redeploy: api_build_push executor_build_push deployment_delete_pods

deployment_delete_pods:
	kubectl delete pods -l app=executor-app
	kubectl delete pods -l app=api-app
