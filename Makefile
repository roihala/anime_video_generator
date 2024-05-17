# Define a PHONY target to tell Make that these aren't actual files.
.PHONY: deployment_build_push deployment_delete_pods deployment_redeploy heroku_build_push heroku_redeploy

# Target for building, pushing the Docker image, and applying the Kubernetes deployment.
deployment_build_push:
	docker build -t gcr.io/animax-423606/animax:latest .
	docker push gcr.io/animax-423606/animax:latest
	kubectl apply -f deployment.yaml

# Target for deleting pods based on a label selector.
deployment_delete_pods:
	kubectl delete pods -l app=animax

# Target to redeploy by building, pushing and deleting old pods.
deployment_redeploy: deployment_build_push deployment_delete_pods
