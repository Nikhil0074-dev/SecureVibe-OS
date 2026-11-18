FROM rust:1.89 AS build
WORKDIR /src
COPY . .
RUN cargo build --release
FROM debian:bookworm-slim
RUN useradd -u 10001 app
COPY --from=build /src/target/release/reverse-parser-service /server
USER app
EXPOSE 8004
ENTRYPOINT ["/server"]
