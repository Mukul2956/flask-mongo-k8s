# 📊 Resource Management in Kubernetes

## Overview

Resource management in Kubernetes ensures efficient utilization of cluster resources while maintaining application performance and stability. This document explains how we configure CPU and memory resources for our Flask-MongoDB application.

## 🎯 Why Resource Management Matters

### Problems Without Resource Limits
- **Resource starvation** - One pod consuming all cluster resources
- **Unpredictable performance** - Applications competing for resources
- **Cascade failures** - Resource exhaustion causing cluster instability
- **Poor scheduling** - Kubernetes unable to make optimal placement decisions

### Benefits of Proper Resource Management
- **Predictable performance** - Applications get guaranteed resources
- **Efficient scheduling** - Better pod placement decisions
- **Cost optimization** - Right-sizing prevents over-provisioning
- **Stability** - Prevents resource exhaustion scenarios

## 🔧 Resource Configuration Types

### 1. Resource Requests
**Definition**: Minimum guaranteed resources for a container.

**Purpose**:
- Kubernetes scheduler uses requests to decide pod placement
- Container is guaranteed this amount of resources
- Used for capacity planning and scheduling decisions

### 2. Resource Limits
**Definition**: Maximum resources a container can consume.

**Purpose**:
- Prevents containers from consuming excessive resources
- Triggers eviction if memory limit is exceeded
- CPU throttling if CPU limit is exceeded

## ⚡ Our Resource Configuration

### Flask Application Resources
```yaml
# k8s/07-flask-deployment.yaml
resources:
  requests:
    cpu: "200m"      # 0.2 CPU cores guaranteed
    memory: "250Mi"  # 250 MiB memory guaranteed
  limits:
    cpu: "500m"      # Maximum 0.5 CPU cores
    memory: "500Mi"  # Maximum 500 MiB memory
```

### MongoDB Resources
```yaml
# k8s/05-mongo-statefulset.yaml
resources:
  requests:
    cpu: "200m"      # 0.2 CPU cores guaranteed
    memory: "250Mi"  # 250 MiB memory guaranteed
  limits:
    cpu: "500m"      # Maximum 0.5 CPU cores
    memory: "500Mi"  # Maximum 500 MiB memory
```

## 📏 Resource Units Explained

### CPU Units
| Unit | Description | Equivalent |
|------|-------------|------------|
| `1` | 1 CPU core | 1000m (millicores) |
| `500m` | 0.5 CPU core | Half a CPU core |
| `100m` | 0.1 CPU core | 10% of a CPU core |

### Memory Units
| Unit | Description | Bytes |
|------|-------------|-------|
| `Ki` | Kibibyte | 1024 |
| `Mi` | Mebibyte | 1024² |
| `Gi` | Gibibyte | 1024³ |
| `K` | Kilobyte | 1000 |
| `M` | Megabyte | 1000² |
| `G` | Gigabyte | 1000³ |

## 🎯 Resource Planning Strategy

### Flask Application Sizing
```bash
# Our Flask app requirements analysis:
# - Base Python runtime: ~50MB
# - Flask framework: ~20MB
# - Application code: ~5MB
# - Working memory: ~100MB
# - Buffer for requests: ~75MB
# Total estimate: ~250MB
```

### MongoDB Sizing
```bash
# MongoDB requirements analysis:
# - MongoDB binary: ~100MB
# - WiredTiger cache: ~100MB (configurable)
# - Connection overhead: ~25MB
# - Operating buffer: ~25MB
# Total estimate: ~250MB
```

### CPU Sizing Rationale
```bash
# Expected workload:
# - Light to moderate request volume
# - Simple CRUD operations
# - No heavy computation
# - 200m should handle baseline load
# - 500m provides headroom for traffic spikes
```

## 📊 Monitoring Resource Usage

### Real-time Resource Monitoring
```bash
# Check current resource usage
kubectl top pods -n flask-mongo-demo

# Detailed resource information
kubectl describe pod <pod-name> -n flask-mongo-demo

# Historical resource usage (if metrics-server is available)
kubectl top pod <pod-name> --containers -n flask-mongo-demo
```

### Resource Usage Commands
```bash
# Check node capacity
kubectl describe node

# Check resource allocation across cluster
kubectl describe node | grep -A 5 "Allocated resources"

# Monitor specific pod resources
watch kubectl top pod -n flask-mongo-demo
```

## 🚀 Quality of Service (QoS) Classes

Kubernetes assigns QoS classes based on resource configuration:

### 1. Guaranteed QoS
**When**: `requests == limits` for all containers
```yaml
resources:
  requests:
    cpu: "500m"
    memory: "500Mi"
  limits:
    cpu: "500m"     # Same as request
    memory: "500Mi" # Same as request
```

### 2. Burstable QoS (Our Configuration)
**When**: `requests < limits` or only requests specified
```yaml
resources:
  requests:
    cpu: "200m"     # Less than limit
    memory: "250Mi" # Less than limit
  limits:
    cpu: "500m"
    memory: "500Mi"
```

### 3. Best Effort QoS
**When**: No requests or limits specified
```yaml
# No resources specified - not recommended for production
```

## ⚖️ Resource Management Best Practices

### 1. Start Conservative, Scale Up
```yaml
# Initial deployment
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "200m"
    memory: "256Mi"

# After monitoring, increase if needed
resources:
  requests:
    cpu: "200m"
    memory: "250Mi"
  limits:
    cpu: "500m"
    memory: "500Mi"
```

### 2. Set Both Requests and Limits
```yaml
# Good practice - always specify both
resources:
  requests:
    cpu: "200m"
    memory: "250Mi"
  limits:
    cpu: "500m"
    memory: "500Mi"
```

### 3. Memory Limits Should Be Close to Requests
```yaml
# Avoid large gaps for memory (causes OOMKilled)
resources:
  requests:
    memory: "250Mi"
  limits:
    memory: "500Mi"  # 2x request is reasonable
```

### 4. CPU Limits Can Be More Generous
```yaml
# CPU can be throttled, so higher limits are safer
resources:
  requests:
    cpu: "200m"
  limits:
    cpu: "1000m"  # 5x request is acceptable
```

## 🔍 Resource Optimization Strategies

### Application-Level Optimization

#### Flask Application
```python
# Configure connection pooling
client = MongoClient(
    uri,
    maxPoolSize=10,          # Limit connections
    serverSelectionTimeoutMS=5000,
    maxIdleTimeMS=30000      # Release idle connections
)

# Use memory-efficient JSON handling
from flask import json

@app.route("/data", methods=["POST"])
def data():
    # Stream large payloads instead of loading into memory
    payload = request.get_json(force=True, silent=True)
```

#### MongoDB Configuration
```yaml
env:
  - name: MONGO_CACHE_SIZE_GB
    value: "0.1"  # Limit WiredTiger cache
```

### Kubernetes-Level Optimization

#### Resource Quotas
```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: flask-mongo-quota
  namespace: flask-mongo-demo
spec:
  hard:
    requests.cpu: "2"      # Total CPU requests
    requests.memory: "2Gi" # Total memory requests
    limits.cpu: "4"        # Total CPU limits
    limits.memory: "4Gi"   # Total memory limits
    pods: "10"             # Maximum pods
```

#### Limit Ranges
```yaml
apiVersion: v1
kind: LimitRange
metadata:
  name: flask-mongo-limits
  namespace: flask-mongo-demo
spec:
  limits:
  - default:      # Default limits
      cpu: "500m"
      memory: "500Mi"
    defaultRequest: # Default requests
      cpu: "100m"
      memory: "128Mi"
    type: Container
```

## 📈 Horizontal Pod Autoscaler Integration

### HPA Resource Thresholds
```yaml
# k8s/09-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: flask-app-hpa
  namespace: flask-mongo-demo
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: flask-app
  minReplicas: 2
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70  # Scale at 70% of CPU request
```

### Understanding HPA Calculations
```bash
# HPA scaling decision:
# Current CPU usage: 140m (70% of 200m request)
# Target: 70% of request (140m)
# Decision: Current usage = target, no scaling needed

# If CPU usage: 280m (140% of 200m request)
# Target: 70% of request (140m)
# Decision: Scale up (usage > target)
```

## 🚨 Resource Troubleshooting

### Common Resource Issues

#### 1. Pod Stuck in Pending State
```bash
# Check why pod is not scheduled
kubectl describe pod <pod-name> -n flask-mongo-demo

# Look for events like:
# "Insufficient cpu" or "Insufficient memory"
```

**Solutions**:
- Reduce resource requests
- Add more nodes to cluster
- Remove resource quotas temporarily

#### 2. Pod Getting OOMKilled
```bash
# Check pod events
kubectl describe pod <pod-name> -n flask-mongo-demo

# Look for: "OOMKilled" in container status
```

**Solutions**:
- Increase memory limits
- Optimize application memory usage
- Check for memory leaks

#### 3. Application Performance Issues
```bash
# Check if CPU is being throttled
kubectl top pod <pod-name> -n flask-mongo-demo

# Look for CPU usage near limits
```

**Solutions**:
- Increase CPU limits
- Optimize application performance
- Scale horizontally

### Debug Resource Issues
```bash
# Create debug pod with same resource constraints
kubectl run debug-pod --rm -i --tty \
  --image=busybox \
  --requests='cpu=200m,memory=250Mi' \
  --limits='cpu=500m,memory=500Mi' \
  -n flask-mongo-demo \
  -- /bin/sh

# Test resource allocation
kubectl exec -it debug-pod -n flask-mongo-demo -- cat /sys/fs/cgroup/memory/memory.limit_in_bytes
```

## 📋 Resource Configuration Checklist

### Pre-Deployment
- [ ] Resource requests set based on baseline requirements
- [ ] Resource limits set with appropriate headroom
- [ ] QoS class chosen intentionally (Burstable recommended)
- [ ] HPA thresholds align with resource requests
- [ ] Resource quotas configured for namespace
- [ ] Monitoring tools available for resource tracking

### Post-Deployment
- [ ] Monitor actual resource usage vs. requests/limits
- [ ] Adjust resources based on real-world usage patterns
- [ ] Test autoscaling behavior under load
- [ ] Verify no pods are being OOMKilled
- [ ] Check for CPU throttling events
- [ ] Optimize application based on resource constraints

## 🎉 Summary

Effective resource management in Kubernetes requires:

1. **Understanding your application's needs** - Profile before configuring
2. **Setting appropriate requests** - For scheduling and guarantees
3. **Configuring reasonable limits** - For protection and stability
4. **Monitoring continuously** - Adjust based on real usage
5. **Planning for growth** - HPA and resource quotas for scalability

Our configuration strikes a balance between:
- **Resource efficiency** - Not over-provisioning
- **Performance reliability** - Sufficient resources for normal operation  
- **Burst capacity** - Headroom for traffic spikes
- **Cost optimization** - Right-sizing for actual needs

---

**Next:** [Testing Results and Scenarios](TESTING-RESULTS.md)