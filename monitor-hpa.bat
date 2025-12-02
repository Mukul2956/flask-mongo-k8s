@echo off
echo Monitoring Autoscaling Process...
echo Press Ctrl+C to stop monitoring
echo.

:MONITOR
echo ========================================
echo Time: %date% %time%
echo ========================================
echo HPA Status:
kubectl get hpa -n flask-mongo-demo
echo.
echo Pod Status:
kubectl get pods -n flask-mongo-demo
echo.
echo CPU/Memory Usage:
kubectl top pods -n flask-mongo-demo
echo.
timeout /t 10 > nul
goto MONITOR