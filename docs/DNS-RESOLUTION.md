# 🌐 DNS Resolution in Kubernetes

## Overview

DNS resolution in Kubernetes enables seamless inter-pod communication without hardcoded IP addresses. This document explains how our Flask application discovers and connects to the MongoDB service.

## 🏗️ Kubernetes DNS Architecture

### CoreDNS
Kubernetes uses CoreDNS as the default DNS server, which:
- Automatically creates DNS records for services
- Provides service discovery across namespaces
- Enables pods to communicate using service names

### DNS Hierarchy
```
<service-name>.<namespace>.svc.cluster.local
```

## 🔍 DNS Resolution in Our Project

### Service Discovery Flow

1. **Flask Pod Startup**
   ```python
   # In app.py
   host = os.getenv("MONGO_HOST", "mongodb")  # Service name
   ```

2. **DNS Query Process**
   ```
   Flask Pod → CoreDNS → Service Registry → MongoDB Service IP
   ```

3. **Connection Establishment**
   ```
   mongodb (service name) → 10.111.27.146:27017 (actual pod IP)
   ```

## 📝 Configuration Examples

### MongoDB Service Definition
```yaml
# k8s/06-mongo-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: mongodb                    # ← This becomes the DNS name
  namespace: flask-mongo-demo
spec:
  type: ClusterIP                 # Internal cluster access only
  selector:
    app: mongodb
  ports:
    - port: 27017
      targetPort: 27017
```

### Flask Application Configuration
```yaml
# k8s/02-configmap-app.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: flask-mongo-demo
data:
  # Using service name "mongodb" instead of IP
  MONGODB_URI: "mongodb://appuser:appsecret@mongodb:27017/flask_db?authSource=admin"
```

### Flask Code Implementation
```python
def build_mongo_uri():
    host = os.getenv("MONGO_HOST", "mongodb")  # DNS name resolution
    port = os.getenv("MONGO_PORT", "27017")
    user = os.getenv("MONGO_USERNAME", "appuser")
    pwd = os.getenv("MONGO_PASSWORD", "appsecret")
    auth_db = os.getenv("MONGO_AUTH_DB", "admin")
    
    return f"mongodb://{user}:{pwd}@{host}:{port}/?authSource={auth_db}"
```

## 🔬 Testing DNS Resolution

### 1. Check Service Registration
```bash
kubectl get services -n flask-mongo-demo
```

### 2. Test DNS Resolution from Flask Pod
```bash
# Get pod name
kubectl get pods -l app=flask-app -n flask-mongo-demo

# Test DNS lookup
kubectl exec -it <flask-pod-name> -n flask-mongo-demo -- nslookup mongodb
```

**Expected Output:**
```
Server:         10.96.0.10
Address:        10.96.0.10#53

Name:   mongodb.flask-mongo-demo.svc.cluster.local
Address: 10.111.27.146
```

### 3. Test Different DNS Formats
```bash
# Short name (same namespace)
kubectl exec -it <flask-pod-name> -n flask-mongo-demo -- nslookup mongodb

# Fully qualified domain name
kubectl exec -it <flask-pod-name> -n flask-mongo-demo -- nslookup mongodb.flask-mongo-demo.svc.cluster.local

# Cross-namespace (if applicable)
kubectl exec -it <flask-pod-name> -n flask-mongo-demo -- nslookup mongodb.flask-mongo-demo
```

### 4. Test Connectivity
```bash
# Ping test
kubectl exec -it <flask-pod-name> -n flask-mongo-demo -- ping mongodb

# Port connectivity test
kubectl exec -it <flask-pod-name> -n flask-mongo-demo -- telnet mongodb 27017
```

## 🎯 DNS Resolution Patterns

### Same Namespace Resolution
When both services are in the same namespace:
```
mongodb → mongodb.flask-mongo-demo.svc.cluster.local
```

### Cross-Namespace Resolution
For services in different namespaces:
```
service-name.namespace-name → service-name.namespace-name.svc.cluster.local
```

### External Service Resolution
For external databases:
```yaml
apiVersion: v1
kind: Service
metadata:
  name: external-mongo
spec:
  type: ExternalName
  externalName: mongodb.example.com
```

## ⚙️ Advanced DNS Configuration

### Custom DNS Policies
```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      dnsPolicy: ClusterFirst  # Default: use cluster DNS
      dnsConfig:
        nameservers:
          - 8.8.8.8            # Additional nameserver
        searches:
          - my.dns.search.suffix
        options:
          - name: ndots
            value: "2"
```

### Service Mesh Integration
```yaml
# With Istio
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: mongodb-vs
spec:
  hosts:
  - mongodb.flask-mongo-demo.svc.cluster.local
  http:
  - route:
    - destination:
        host: mongodb.flask-mongo-demo.svc.cluster.local
```

## 🛡️ Security Considerations

### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: flask-to-mongo
spec:
  podSelector:
    matchLabels:
      app: flask-app
  policyTypes:
  - Egress
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: mongodb
    ports:
    - protocol: TCP
      port: 27017
```

### DNS Security
- Use ClusterIP services for internal communication
- Avoid exposing internal service names externally
- Implement proper RBAC for service discovery

## 🔧 Troubleshooting DNS Issues

### Common Problems and Solutions

1. **Service Not Found**
   ```bash
   # Check if service exists
   kubectl get svc mongodb -n flask-mongo-demo
   
   # Check service endpoints
   kubectl get endpoints mongodb -n flask-mongo-demo
   ```

2. **DNS Resolution Timeout**
   ```bash
   # Check CoreDNS pods
   kubectl get pods -n kube-system | grep coredns
   
   # Check DNS configuration
   kubectl exec -it <flask-pod> -n flask-mongo-demo -- cat /etc/resolv.conf
   ```

3. **Wrong IP Resolution**
   ```bash
   # Force DNS refresh
   kubectl delete pod <flask-pod> -n flask-mongo-demo
   
   # Check service selector
   kubectl describe svc mongodb -n flask-mongo-demo
   ```

### Debugging Commands
```bash
# DNS debug pod
kubectl run dns-debug --rm -i --tty --image=busybox -n flask-mongo-demo \
  -- /bin/sh

# Inside debug pod:
nslookup mongodb
nslookup mongodb.flask-mongo-demo.svc.cluster.local
wget -qO- http://mongodb:27017
```

## 📊 Performance Considerations

### DNS Caching
- Kubernetes DNS responses have TTL of 30 seconds by default
- Applications should implement connection pooling
- Consider DNS caching for high-traffic applications

### Service Discovery Optimization
```python
# Connection pooling example
from pymongo import MongoClient

class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.client = MongoClient(
                build_mongo_uri(),
                maxPoolSize=50,      # Connection pool
                serverSelectionTimeoutMS=5000
            )
        return cls._instance
```

## ✅ Best Practices

### 1. Use Service Names
- Always use service names instead of pod IPs
- Use short names within the same namespace
- Use FQDN for cross-namespace communication

### 2. Implement Health Checks
```python
def check_mongodb_connection():
    try:
        client.admin.command('ping')
        return True
    except Exception:
        return False
```

### 3. Handle DNS Failures Gracefully
```python
import socket
import time

def connect_with_retry(uri, max_retries=3):
    for attempt in range(max_retries):
        try:
            return MongoClient(uri, serverSelectionTimeoutMS=5000)
        except socket.gaierror as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise e
```

## 🎉 Summary

DNS resolution in Kubernetes provides:
- **Automatic service discovery** without configuration changes
- **Location transparency** - services can move without code changes
- **Namespace isolation** for multi-tenant deployments
- **Load balancing** through service endpoints

Our Flask-MongoDB setup leverages these features to create a resilient, scalable microservices architecture where components can discover and communicate with each other seamlessly.

---

**Next:** [Resource Management Guide](RESOURCE-MANAGEMENT.md)