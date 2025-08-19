# ===== Stage 1: Build Prometheus =====
FROM alpine:3.20 AS builder

# Install build dependencies
RUN apk add --no-cache wget tar ca-certificates

# Set Prometheus version
ENV PROMETHEUS_VERSION=2.54.1

# Download and extract Prometheus
RUN wget https://github.com/prometheus/prometheus/releases/download/v${PROMETHEUS_VERSION}/prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz \
 && tar -xzf prometheus-${PROMETHEUS_VERSION}.linux-amd64.tar.gz \
 && mv prometheus-${PROMETHEUS_VERSION}.linux-amd64 /prometheus-src

# ===== Stage 2: Final Image =====
FROM alpine:3.20

LABEL maintainer="your-email@company.com" \
      description="Custom Prometheus with configuration and rules" \
      version="1.0"

# Install runtime tools
RUN apk add --no-cache curl jq ca-certificates tzdata

# Create prometheus user and group
RUN addgroup -S prometheus && adduser -S prometheus -G prometheus

# Create required directories
RUN mkdir -p /etc/prometheus/rules \
             /etc/prometheus/alerts \
             /etc/prometheus/consoles \
             /etc/prometheus/console_libraries \
             /prometheus-data \
    && chown -R prometheus:prometheus /etc/prometheus /prometheus-data

# Copy Prometheus binaries from builder
COPY --from=builder /prometheus-src/prometheus /usr/local/bin/
COPY --from=builder /prometheus-src/promtool /usr/local/bin/
COPY --from=builder /prometheus-src/consoles/ /etc/prometheus/consoles/
COPY --from=builder /prometheus-src/console_libraries/ /etc/prometheus/console_libraries/

# Copy configuration and rules
COPY --chown=prometheus:prometheus prometheus.yml /etc/prometheus/prometheus.yml
COPY --chown=prometheus:prometheus rules/ /etc/prometheus/rules/
COPY --chown=prometheus:prometheus alerts/ /etc/prometheus/alerts/

# Health check script
RUN echo '#!/bin/sh\ncurl -f http://localhost:9090/-/healthy || exit 1' \
    > /usr/local/bin/health-check.sh \
 && chmod +x /usr/local/bin/health-check.sh

# Set timezone
ENV TZ=UTC

# Switch to non-root user
USER prometheus

# Working directory for TSDB
WORKDIR /prometheus-data

# Expose Prometheus port
EXPOSE 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD ["/usr/local/bin/health-check.sh"]

# Default command
#"--config.file=/etc/prometheus/prometheus.yml", \
CMD ["--storage.tsdb.path=/prometheus-data", \
     "--web.console.libraries=/etc/prometheus/console_libraries", \
     "--web.console.templates=/etc/prometheus/consoles"]
