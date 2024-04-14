# Define a PHONY target to tell Make that these aren't actual files.
.PHONY: deployment_build_push deployment_delete_pods

# Target for building, pushing the Docker image, and applying the Kubernetes deployment.
deployment_build_push:
	docker build -t gcr.io/animax-419913/my-app:tag .
	docker push gcr.io/animax-419913/my-app:tag
	kubectl apply -f deployment.yaml

# Target for deleting pods based on a label selector.
deployment_delete_pods:
	kubectl delete pods -l app=my-app

deployment_redeploy: deployment_build_push deployment_delete_pods
