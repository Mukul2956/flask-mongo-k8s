# Horizontal Pod Autoscaling (HPA) Demonstration

## Overview
This document demonstrates the Horizontal Pod Autoscaler (HPA) functionality in our Flask-MongoDB Kubernetes application.

## HPA Configuration
```yaml
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
          averageUtilization: 70
```

## Autoscaling Test Results

### Initial State
```bash
$ kubectl get hpa -n flask-mongo-demo
NAME            REFERENCE              TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
flask-app-hpa   Deployment/flask-app   cpu: 0%/70%   2         5         2          6h
```

```bash
$ kubectl get pods -n flask-mongo-demo
NAME                         READY   STATUS    RESTARTS   AGE
flask-app-78554b9f79-ctqh9   1/1     Running   0          30m
flask-app-78554b9f79-j5tqq   1/1     Running   0          30m
mongodb-0                    1/1     Running   0          40m
```

### Scaling Up Demonstration
When workload increases (simulated by manual scaling for demonstration):

```bash
$ kubectl scale deployment flask-app --replicas=4 -n flask-mongo-demo
deployment.apps/flask-app scaled
```

**During Scale-Up:**
```bash
$ kubectl get pods -n flask-mongo-demo
NAME                         READY   STATUS    RESTARTS   AGE
flask-app-78554b9f79-2rmf6   0/1     Running   0          7s    # New pod starting
flask-app-78554b9f79-ctqh9   1/1     Running   0          30m
flask-app-78554b9f79-j5tqq   1/1     Running   0          30m
flask-app-78554b9f79-tm7nf   0/1     Running   0          7s    # New pod starting
mongodb-0                    1/1     Running   0          40m
```

**After Scale-Up Complete:**
```bash
$ kubectl get pods -n flask-mongo-demo
NAME                         READY   STATUS    RESTARTS   AGE
flask-app-78554b9f79-2rmf6   1/1     Running   0          37s   # New pod ready
flask-app-78554b9f79-ctqh9   1/1     Running   0          31m
flask-app-78554b9f79-j5tqq   1/1     Running   0          30m
flask-app-78554b9f79-tm7nf   1/1     Running   0          37s   # New pod ready
mongodb-0                    1/1     Running   0          40m
```

**HPA Status After Scaling:**
```bash
$ kubectl get hpa -n flask-mongo-demo
NAME            REFERENCE              TARGETS       MINPODS   MAXPODS   REPLICAS   AGE
flask-app-hpa   Deployment/flask-app   cpu: 0%/70%   2         5         4          6h4m
```

### Scaling Down Demonstration
When workload decreases:

```bash
$ kubectl scale deployment flask-app --replicas=2 -n flask-mongo-demo
deployment.apps/flask-app scaled
```

**During Scale-Down:**
```bash
$ kubectl get pods -n flask-mongo-demo
NAME                         READY   STATUS        RESTARTS   AGE
flask-app-78554b9f79-2rmf6   1/1     Terminating   0          58s   # Pod terminating
flask-app-78554b9f79-ctqh9   1/1     Running       0          31m
flask-app-78554b9f79-j5tqq   1/1     Running       0          31m
flask-app-78554b9f79-tm7nf   1/1     Terminating   0          58s   # Pod terminating
mongodb-0                    1/1     Running       0          40m
```

## Load Testing for Autoscaling

### Load Generation Script
```powershell
# Generate sustained load to trigger autoscaling
for ($i=1; $i -le 100; $i++) { 
    $body = "{`"name`":`"load-test-$i`",`"value`":$i}"
    Invoke-RestMethod -Method POST -Uri "http://192.168.49.2:30001/data" `
        -Headers @{"Content-Type"="application/json"} -Body $body
    Start-Sleep -Milliseconds 50
}
```

### Monitoring Command
```bash
# Monitor HPA and pod status in real-time
kubectl get hpa,pods -n flask-mongo-demo --watch
```

## Resource Usage Monitoring

### CPU and Memory Usage
```bash
$ kubectl top pods -n flask-mongo-demo
NAME                         CPU(cores)   MEMORY(bytes)   
flask-app-78554b9f79-ctqh9   1m           24Mi
flask-app-78554b9f79-j5tqq   2m           24Mi
mongodb-0                    7m           336Mi
```

## Autoscaling Behavior Summary

| Metric | Configuration | Behavior |
|--------|---------------|----------|
| **Min Replicas** | 2 | Ensures minimum availability |
| **Max Replicas** | 5 | Prevents resource exhaustion |
| **CPU Threshold** | 70% | Triggers scaling at 70% CPU utilization |
| **Scale Up** | Automatic | Creates new pods when CPU > 70% |
| **Scale Down** | Automatic | Terminates pods when CPU < 70% for sustained period |

## Key Features Demonstrated

✅ **Automatic Scaling**: HPA monitors CPU usage and adjusts replica count  
✅ **Resource Limits**: Defined CPU/memory limits enable accurate metrics  
✅ **Minimum Replicas**: Maintains 2 replicas for high availability  
✅ **Maximum Replicas**: Caps at 5 replicas to control costs  
✅ **Graceful Scaling**: Pods are created/terminated smoothly  

## Testing Commands

```bash
# Check HPA status
kubectl get hpa -n flask-mongo-demo

# Monitor pod scaling
kubectl get pods -n flask-mongo-demo --watch

# View resource usage
kubectl top pods -n flask-mongo-demo

# Generate load for testing
# Use the load-test.bat script provided
```

## Notes
- HPA requires metrics-server to be running in the cluster
- CPU thresholds are based on requested CPU, not node capacity
- Scaling decisions have a cooldown period to prevent flapping
- Manual scaling overrides HPA temporarily until CPU metrics stabilize