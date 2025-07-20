createdb:
	sudo docker run --name timescaledb-market-price \
	  -e POSTGRES_PASSWORD=mysecretpassword \
	  -e POSTGRES_USER=root \
	  -e POSTGRES_DB=market-price \
	  -p 5431:5432 \
	  -d timescale/timescaledb:latest-pg15
initschema:
	sudo docker exec -i timescaledb-market-price psql -U root -d market-price < src/main/resources/db/schema/001_create_kline_table.sql && \
	sudo docker exec -i timescaledb-market-price psql -U root -d market-price < src/main/resources/db/schema/002_create_price_table.sql
