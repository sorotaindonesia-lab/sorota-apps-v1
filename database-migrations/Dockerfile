FROM alpine:3.19
RUN apk add --no-cache postgresql-client bash
WORKDIR /app
COPY . .
RUN chmod +x entrypoint.sh scripts/*.sh
ENTRYPOINT ["./entrypoint.sh"]
CMD ["up"]
