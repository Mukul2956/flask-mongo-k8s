@echo off
echo Starting Load Test for Autoscaling Demo...
echo Target: http://192.168.49.2:30001/data
echo.

echo Initial HPA Status:
kubectl get hpa -n flask-mongo-demo

echo.
echo Initial Pod Status:
kubectl get pods -n flask-mongo-demo

echo.
echo Starting load generation... (Press Ctrl+C to stop)
echo This will send continuous requests to trigger CPU usage and autoscaling.

:LOOP
curl -s -X POST http://192.168.49.2:30001/data -H "Content-Type: application/json" -d "{\"name\": \"load-test-%random%\", \"value\": %random%}" > nul
curl -s http://192.168.49.2:30001/data > nul
timeout /t 0 > nul
goto LOOP