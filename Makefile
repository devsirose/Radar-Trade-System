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
.PHONY: postgresdb createdb dropdb migrateup migratedown