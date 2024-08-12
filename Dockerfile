FROM timberio/vector:0.40.0-debian

# remove preinstalled configuration
RUN rm -rf /etc/vector/vector.yaml /etc/vector/examples

# install our configuration
COPY vector-config/vector.toml /etc/vector/vector.toml
COPY vector-config/sinks /etc/vector/sinks

COPY ./start-fly-log-transporter.sh .

CMD ["bash", "start-fly-log-transporter.sh"]
ENTRYPOINT []
