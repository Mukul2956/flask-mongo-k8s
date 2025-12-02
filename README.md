#  Flask MongoDB Kubernetes Project

[![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat&logo=kubernetes&logoColor=white)](https://kubernetes.io/)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0.2-green?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green?style=flat&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

A production-ready Flask application with MongoDB backend deployed on Kubernetes with authentication, autoscaling, and persistent storage.

## 📋 Project Overview

This project demonstrates a complete microservices deployment on Kubernetes featuring:

- **Flask REST API** with health checks and data persistence
- **MongoDB StatefulSet** with authentication and persistent storage
- **Horizontal Pod Autoscaling** based on CPU utilization
- **Service mesh** with proper DNS resolution
- **Resource management** with requests and limits
- **Production-ready** configuration with security best practices

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   NodePort      │    │   ClusterIP     │    │ Persistent      │
│   Service       │────│   Service       │────│ Volume          │
│  (Flask App)    │    │  (MongoDB)      │    │ (MongoDB Data)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Flask Deployment│    │ MongoDB         │    │ PVC: mongo-pvc  │
│ Replicas: 2-5   │    │ StatefulSet     │    │ Size: 2Gi       │
│ HPA Enabled     │    │ Auth Enabled    │    │ Mode: RWO       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ✨ Features

### 🔐 Security
- MongoDB authentication with dedicated app user
- Kubernetes Secrets for sensitive data
- ConfigMaps for application configuration
- Network policies with ClusterIP services

### 📈 Scalability
- Horizontal Pod Autoscaler (2-5 replicas)
- CPU-based scaling (70% threshold)
- Resource requests and limits
- StatefulSet for database consistency

### 💾 Persistence
- Persistent Volume for MongoDB data
- Data survives pod restarts and reschedules
- Configurable storage class

### 🔍 Monitoring
- Health check endpoints
- Readiness and liveness probes
- Resource usage monitoring

## 🚀 Quick Start

### Prerequisites
- **Kubernetes cluster** (Minikube, Docker Desktop, or cloud provider)
- **Docker** for building images
- **kubectl** configured for your cluster

### 1. Clone Repository
```bash
git clone https://github.com/Mukul2956/flask-mongo-k8s.git
cd flask-mongo-k8s
```

### 2. Build and Push Docker Image
```bash
cd app
docker build -t your-registry/flask-mongo-app:v1 .
docker push your-registry/flask-mongo-app:v1
```

### 3. Deploy to Kubernetes
```bash
# Apply all Kubernetes manifests
kubectl apply -f k8s/

# Wait for deployment to be ready
kubectl wait --for=condition=ready pod --selector=app=flask-app -n flask-mongo-demo --timeout=300s
```

### 4. Test the Application
```bash
# Port forward to access locally
kubectl port-forward svc/flask-service 8080:80 -n flask-mongo-demo

# Test endpoints
curl http://localhost:8080/                    # Welcome message
curl -X POST -H "Content-Type: application/json" \
     -d '{"test":"data"}' \
     http://localhost:8080/data                # Insert data
curl http://localhost:8080/data               # Retrieve data
```

## 📁 Project Structure

```
flask-mongo-k8s/
├── app/                          # Flask application
│   ├── app.py                    # Main application code
│   ├── Dockerfile                # Container configuration
│   └── requirements.txt          # Python dependencies
├── k8s/                          # Kubernetes manifests
│   ├── 00-namespace.yaml         # Namespace definition
│   ├── 01-secret-mongo.yaml      # MongoDB secrets
│   ├── 02-configmap-app.yaml     # App configuration
│   ├── 02b-mongo-init-configmap.yaml # MongoDB initialization
│   ├── 03-pv.yaml                # Persistent Volume
│   ├── 04-pvc.yaml               # Persistent Volume Claim
│   ├── 05-mongo-statefulset.yaml # MongoDB StatefulSet
│   ├── 06-mongo-service.yaml     # MongoDB Service
│   ├── 07-flask-deployment.yaml  # Flask Deployment
│   ├── 08-flask-service.yaml     # Flask Service
│   └── 09-hpa.yaml               # Horizontal Pod Autoscaler
├── docs/                         # Documentation
│   ├── DNS-RESOLUTION.md         # DNS configuration guide
│   ├── RESOURCE-MANAGEMENT.md    # Resource management guide
│   └── TESTING-RESULTS.md        # Testing scenarios and results
├── AUTOSCALING-DEMO.md           # Detailed autoscaling demonstration
├── load-test.bat                 # Load testing script for Windows
├── monitor-hpa.bat               # HPA monitoring script for Windows
└── README.md                     # This file
```

## 🔧 Configuration

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://appuser:appsecret@mongodb:27017/flask_db?authSource=admin` |
| `MONGO_USERNAME` | MongoDB application user | `appuser` |
| `MONGO_PASSWORD` | MongoDB application password | `appsecret` |
| `MONGO_DB` | Database name | `flask_db` |

### Resource Limits
| Component | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-----------|-------------|----------------|-----------|--------------|
| Flask App | 200m | 250Mi | 500m | 500Mi |
| MongoDB | 200m | 250Mi | 500m | 500Mi |

## 📊 API Endpoints

### GET `/`
Returns a welcome message with current timestamp.

**Response:**
```
Welcome to the Flask app! The current time is: 2025-12-02 12:00:00.000000
```

### POST `/data`
Insert data into MongoDB.

**Request:**
```json
{
  "key": "value",
  "timestamp": "2025-12-02"
}
```

**Response:**
```json
{
  "status": "Data inserted"
}
```

### GET `/data`
Retrieve all data from MongoDB.

**Response:**
```json
[
  {
    "key": "value",
    "timestamp": "2025-12-02"
  }
]
```

## 🧪 Testing

### Functional Testing
```bash
# Test all endpoints
kubectl exec deployment/flask-app -n flask-mongo-demo -- python3 -c "
import urllib.request, json

# Test welcome endpoint
response = urllib.request.urlopen('http://localhost:5000/')
print('GET /:', response.status)

# Test data insertion
data = json.dumps({'test': 'data'}).encode()
req = urllib.request.Request('http://localhost:5000/data', data=data, 
                            headers={'Content-Type': 'application/json'})
response = urllib.request.urlopen(req)
print('POST /data:', response.status)

# Test data retrieval
response = urllib.request.urlopen('http://localhost:5000/data')
print('GET /data:', response.status)
"
```

### Load Testing (HPA)
```bash
# Generate load to test autoscaling
kubectl run load-generator --rm -i --tty --image=busybox -n flask-mongo-demo \
  -- /bin/sh -c "while true; do wget -q -O- http://flask-service/; done"

# Monitor scaling
kubectl get hpa -n flask-mongo-demo -w
```

## 🔍 Monitoring

### Check Deployment Status
```bash
kubectl get all -n flask-mongo-demo
kubectl get pv,pvc -n flask-mongo-demo
kubectl get hpa -n flask-mongo-demo
```

### View Logs
```bash
kubectl logs deployment/flask-app -n flask-mongo-demo
kubectl logs statefulset/mongodb -n flask-mongo-demo
```

### Monitor Resources
```bash
kubectl top pods -n flask-mongo-demo
kubectl describe hpa flask-app-hpa -n flask-mongo-demo
```

## 📈 Horizontal Pod Autoscaling (HPA)

The application includes Horizontal Pod Autoscaling to automatically adjust the number of Flask application pods based on CPU utilization.

### HPA Configuration
- **Min Replicas**: 2 (ensures high availability)
- **Max Replicas**: 5 (prevents resource exhaustion)
- **CPU Threshold**: 70% (triggers scaling when CPU usage exceeds 70%)
- **Target Deployment**: flask-app

### Autoscaling Results

**Initial State:**
```bash
$ kubectl get hpa -n flask-mongo-demo
NAME            REFERENCE              TARGETS       MINPODS   MAXPODS   REPLICAS
flask-app-hpa   Deployment/flask-app   cpu: 0%/70%   2         5         2
```

**Scale-Up Demonstration:**
```bash
# During high load, HPA automatically creates additional pods
$ kubectl get pods -n flask-mongo-demo
NAME                         READY   STATUS    RESTARTS   AGE
flask-app-78554b9f79-ctqh9   1/1     Running   0          31m
flask-app-78554b9f79-j5tqq   1/1     Running   0          30m
flask-app-78554b9f79-2rmf6   1/1     Running   0          37s   # New pod
flask-app-78554b9f79-tm7nf   1/1     Running   0          37s   # New pod
mongodb-0                    1/1     Running   0          40m
```

**Scale-Down Process:**
```bash
# When load decreases, HPA gracefully terminates excess pods
$ kubectl get pods -n flask-mongo-demo
NAME                         READY   STATUS        RESTARTS   AGE
flask-app-78554b9f79-2rmf6   1/1     Terminating   0          58s   # Terminating
flask-app-78554b9f79-ctqh9   1/1     Running       0          31m
flask-app-78554b9f79-j5tqq   1/1     Running       0          31m
flask-app-78554b9f79-tm7nf   1/1     Terminating   0          58s   # Terminating
```

### Load Testing for Autoscaling
```bash
# Generate load to test autoscaling
for i in {1..100}; do
  curl -X POST http://$(minikube ip):30001/data \
    -H "Content-Type: application/json" \
    -d "{\"load-test\":\"$i\",\"timestamp\":\"$(date)\"}"
done
```

### Resource Monitoring
```bash
$ kubectl top pods -n flask-mongo-demo
NAME                         CPU(cores)   MEMORY(bytes)   
flask-app-78554b9f79-ctqh9   1m           24Mi
flask-app-78554b9f79-j5tqq   2m           24Mi
mongodb-0                    7m           336Mi
```

**Key Autoscaling Features:**
- ✅ **Automatic scaling** based on CPU metrics
- ✅ **Configurable thresholds** for scale-up/down decisions
- ✅ **Resource efficiency** by scaling down during low usage
- ✅ **High availability** maintained with minimum replicas
- ✅ **Cost optimization** with maximum replica limits

📋 **Detailed Autoscaling Documentation**: See [AUTOSCALING-DEMO.md](AUTOSCALING-DEMO.md) for comprehensive test results and screenshots.

## 🛠️ Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pods -n flask-mongo-demo
   kubectl logs <pod-name> -n flask-mongo-demo
   ```

2. **Database connection issues**
   ```bash
   kubectl exec -it mongodb-0 -n flask-mongo-demo -- mongosh admin -u root -p supersecret --eval "db.getUsers()"
   ```

3. **Storage issues**
   ```bash
   kubectl get pv,pvc -n flask-mongo-demo
   kubectl describe pvc mongo-pvc -n flask-mongo-demo
   ```

## 📚 Documentation

- [DNS Resolution Guide](docs/DNS-RESOLUTION.md) - Inter-pod communication
- [Resource Management](docs/RESOURCE-MANAGEMENT.md) - CPU/Memory configuration
- [Testing Results](docs/TESTING-RESULTS.md) - Comprehensive test scenarios

## 🚀 Deployment Strategies

### Production Considerations
- Use proper secrets management (e.g., Kubernetes Secrets, Vault)
- Implement network policies for security
- Configure backup strategies for MongoDB
- Use ingress controllers for external access
- Monitor with Prometheus/Grafana

### Scaling Considerations
- Adjust HPA metrics and thresholds
- Consider vertical pod autoscaling
- Implement database read replicas
- Use distributed storage solutions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask team for the excellent web framework
- MongoDB for the robust database solution
- Kubernetes community for container orchestration
- Docker for containerization platform

---

**Built with ❤️ for learning Kubernetes and microservices architecture**
