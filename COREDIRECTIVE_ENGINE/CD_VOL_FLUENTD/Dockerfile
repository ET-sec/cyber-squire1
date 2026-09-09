# Fluentd log shipper with the Datadog output plugin (Tier 0, locally built).
#
# Base tag is arm64-capable. Measured 2026-09-09 against the live registry:
# every tag from v1.16 through v1.18 publishes a single amd64 manifest, so
# none of them builds or runs on the Arm host. arm64 first appears at the
# tag below, which publishes amd64, arm and arm64. Do not move it backwards.
FROM fluent/fluentd:v1.19-1
USER root
# Pure Ruby, no native extension, so no architecture constraint here.
RUN gem install fluent-plugin-datadog
USER fluent
