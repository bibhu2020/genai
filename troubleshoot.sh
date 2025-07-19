### Check the deployment

kubectl port-forward pod/oauthapi-8596744d55-jmw64 3000:3000 

kubectl port-forward service/oauthapi-service 8081:80 

kubectl port-forward service/oauthapp-service 8082:80 

kubectl logs -f pod/oauthapi-7978d7fc5b-xpnn2

kubectl logs -f deployment/apigateway-nestjs -n riskiq

kubectl logs -f deployment/oauthapp-nestjs -n riskiq

#### Clear all docker local images
docker stop $(docker ps -q)

docker rm $(docker ps -a -q)

docker rmi -f $(docker images -q)

### Running locally (via Port Forwarding)
kubectl port-forward service/apigateway-nestjs-service 3001:80 

kubectl port-forward service/northwind-vuejs-service 3011:80 

kubectl port-forward service/mcp-server-service 8000:80 
