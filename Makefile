# Define a PHONY target to tell Make that these aren't actual files.
.PHONY: deployment_build_push deployment_delete_pods deployment_redeploy heroku_build_push heroku_redeploy

# Target for building, pushing the Docker image, and applying the Kubernetes deployment.
deployment_build_push:
	docker build -t gcr.io/animax-419913/my-app:tag .
	docker push gcr.io/animax-419913/my-app:tag
	kubectl apply -f deployment.yaml

# Target for deleting pods based on a label selector.
deployment_delete_pods:
	kubectl delete pods -l app=my-app

# Target to redeploy by building, pushing and deleting old pods.
deployment_redeploy: deployment_build_push deployment_delete_pods

heroku_build_push:
	docker build -t registry.heroku.com/stormy-sands-05558/web .
	heroku container:push web -a stormy-sands-05558
	heroku container:release web -a stormy-sands-05558
	heroku apps:info -a stormy-sands-05558
	heroku logs --tail --app stormy-sands-05558

# Target for building Docker image and pushing to Heroku, then releasing it.
heroku_release:
	heroku container:release web -a stormy-sands-05558
	heroku apps:info -a stormy-sands-05558
	heroku logs --tail --app stormy-sands-05558

# Target to perform a full redeploy on Heroku.
heroku_redeploy: heroku_build_push heroku_release
