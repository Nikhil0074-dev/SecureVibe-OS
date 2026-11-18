FROM golang:1.22 AS build
WORKDIR /src
COPY . .
RUN CGO_ENABLED=0 go build -o /out/server ./cmd/server

FROM python:3.12-slim
# checkov is optional but recommended: real HCL scanning on top of the IR policy engine
RUN pip install --no-cache-dir checkov==3.2.255 && useradd -u 10001 app
COPY --from=build /out/server /server
USER app
EXPOSE 8003
ENTRYPOINT ["/server"]
