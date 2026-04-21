FROM fluent/fluentd:v1.16-debian-1
USER root
RUN gem install elasticsearch --version 7.17.10 --no-document && \
    gem install fluent-plugin-elasticsearch --version 5.4.3 --no-document
USER fluent
