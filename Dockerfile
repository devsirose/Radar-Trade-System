# syntax=docker/dockerfile:1
FROM eclipse-temurin:21-jre-alpine as runtime

ARG ARTIFACT_NAME
ARG VERSION
ARG EXPOSED_PORT


WORKDIR /app

COPY target/${ARTIFACT_NAME}-${VERSION}.jar app.jar

EXPOSE ${EXPOSED_PORT}

HEALTHCHECK --interval=30s --timeout=10s \
  CMD curl -f http://localhost:${EXPOSED_PORT}/actuator/health || exit 1

ENTRYPOINT ["java", "-jar", "app.jar"]
