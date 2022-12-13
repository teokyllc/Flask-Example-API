# Sample Python API Docker project

To build and run the Docker image:<br>
```
docker-compose build

docker-compose up -d

docker-compose down
```
<br><br>

API testing curl commands<br>

```
Get products
curl http://localhost:5000/products

Get product id
curl http://localhost:5000/product/1

Create product
curl --header "Content-Type: application/json" --request POST --data '{"name": "Product 3"}' http://localhost:5000/product

Update product
curl --header "Content-Type: application/json" --request PUT --data '{"name": "Updated Product 3"}' http://localhost:5000/product/3

Delete product
curl --request DELETE http://localhost:5000/product/3
```