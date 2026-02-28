# Kubernetes / Helm Deployment

Deploy HoneyAegis on any Kubernetes cluster using the included Helm chart. This is recommended for enterprise and cloud deployments where you need scaling, rolling updates, and integration with existing Kubernetes infrastructure.

## Prerequisites

- Kubernetes 1.25+
- Helm 3.x
- kubectl configured for your cluster
- A default StorageClass for persistent volumes

## Quick Installation

```bash
# Clone the repository
git clone https://github.com/thesecretchief/HoneyAegis.git
cd HoneyAegis

# Install with auto-generated secrets
helm install honeyaegis ./helm/honeyaegis \
  --namespace honeyaegis --create-namespace \
  --set backend.env.JWT_SECRET=$(openssl rand -hex 32) \
  --set postgres.password=$(openssl rand -hex 16)
```

## Configuration

Edit `helm/honeyaegis/values.yaml` to customize your deployment:

```yaml
# Replica counts
backend:
  replicas: 2
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: "1"
      memory: 512Mi

frontend:
  replicas: 2
  resources:
    requests:
      cpu: 100m
      memory: 128Mi

cowrie:
  replicas: 1
  resources:
    requests:
      cpu: 100m
      memory: 128Mi

postgres:
  storage: 20Gi
  password: ""  # Set via --set or Kubernetes secret

redis:
  storage: 1Gi

ollama:
  enabled: false
  model: "phi3:mini"
  resources:
    requests:
      memory: 2Gi
```

## Ingress

### With NGINX Ingress Controller

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: honeyaegis.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: honeyaegis-tls
      hosts:
        - honeyaegis.example.com
```

### Exposing Honeypot Ports

Honeypot ports require a `LoadBalancer` or `NodePort` service since they operate on non-HTTP protocols:

```yaml
cowrie:
  service:
    type: LoadBalancer
    ports:
      ssh: 22
      telnet: 23
```

## Secrets Management

For production, use Kubernetes Secrets instead of Helm values:

```bash
kubectl create secret generic honeyaegis-secrets \
  --namespace honeyaegis \
  --from-literal=jwt-secret=$(openssl rand -hex 32) \
  --from-literal=postgres-password=$(openssl rand -hex 16) \
  --from-literal=abuseipdb-key=your-api-key
```

Reference in `values.yaml`:

```yaml
backend:
  existingSecret: honeyaegis-secrets
```

## Monitoring

The Helm chart includes optional Prometheus ServiceMonitor and Grafana dashboard:

```yaml
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
  grafanaDashboard:
    enabled: true
```

## Uninstall

```bash
helm uninstall honeyaegis -n honeyaegis
kubectl delete namespace honeyaegis
```

## Related Pages

- [Docker Compose Deployment](docker-compose.md) -- Simpler deployment for single hosts
- [High Availability](../enterprise/high-availability.md) -- HA configuration details
- [Architecture Overview](../architecture/overview.md) -- Component architecture
