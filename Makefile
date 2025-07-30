postgresdb:
	sudo docker run --name postgres-rts-account-service -e POSTGRES_PASSWORD=mysecretpassword -e POSTGRES_USER=root -e POSTGRES_DB=account-service -p 5432:5432 -d postgres
createdb:
	sudo docker exec -it postgres-rts-account-service createdb --username=root --owner=root account-service
dropdb:
	sudo docker exec -it postgres-rts-account-service dropdb account-service
migrateup:
	migrate -path db/migration/ -database "postgresql://root:mysecretpassword@localhost:5432/account-service?sslmode=disable" -verbose up
migratedown:
	yes | migrate -path db/migration/ -database "postgresql://root:mysecretpassword@localhost:5432/account-service?sslmode=disable" -verbose down
redis:
	sudo docker exec -it redis bash

.PHONY: build-push docker-all

docker-build:
	docker build -f Dockerfile --build-arg ARTIFACT_NAME=rts-discovery-server --build-arg VERSION=latest   --build-arg EXPOSED_PORT=8761 --platform linux/amd64 --push -t devops22clc/rts-discovery-server rts-discovery-server  && \
	docker build -f Dockerfile --build-arg ARTIFACT_NAME=rts-api-gateway --build-arg VERSION=latest   --build-arg EXPOSED_PORT=9090 --platform linux/amd64 --push -t devops22clc/rts-api-gateway rts-api-gateway  && \
#	docker build -f Dockerfile --build-arg ARTIFACT_NAME=rts-auth-service --build-arg VERSION=latest  --build-arg EXPOSED_PORT=8081 --platform linux/amd64 --push -t devops22clc/rts-auth-service rts-auth-service && \
	docker build -f Dockerfile --build-arg ARTIFACT_NAME=rts-account-service --build-arg VERSION=latest --build-arg EXPOSED_PORT=8082 --platform linux/amd64 --push -t devops22clc/rts-account-service rts-account-service && \
	docker build -f Dockerfile --build-arg ARTIFACT_NAME=rts-price-service --build-arg VERSION=latest  --build-arg EXPOSED_PORT=8083 --platform linux/amd64 --push -t devops22clc/rts-price-service rts-price-service && \
	docker build -f Dockerfile --build-arg ARTIFACT_NAME=rts-payment-service --build-arg VERSION=latest  --build-arg EXPOSED_PORT=8084 --platform linux/amd64 --push -t devops22clc/rts-payment-service rts-payment-service && \
	docker build -f Dockerfile --build-arg ARTIFACT_NAME=rts-backtest-service --build-arg VERSION=latest  --build-arg EXPOSED_PORT=8085 --platform linux/amd64 --push -t devops22clc/rts-backtest-service rts-backtest-service && \
	docker build -f Dockerfile --build-arg ARTIFACT_NAME=rts-exchange-gateway-processor --build-arg VERSION=latest  --build-arg EXPOSED_PORT=8086 --platform linux/amd64 --push -t devops22clc/rts-exchange-gateway-processor rts-exchange-gateway-processor

.PHONY: postgresdb createdb dropdb migrateup migratedown redis