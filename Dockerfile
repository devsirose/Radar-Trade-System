# syntax=docker/dockerfile:1
FROM eclipse-temurin:21-jre as runtime

ARG ARTIFACT_NAME
ARG EXPOSED_PORT

WORKDIR /app

COPY target/${ARTIFACT_NAME}.jar app.jar

EXPOSE ${EXPOSED_PORT}

ENTRYPOINT ["java", "-jar", "app.jar"]
