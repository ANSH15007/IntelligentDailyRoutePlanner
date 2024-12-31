from fastapi import FastAPI, HTTPException
from models.route import RouteRequest, RouteResponse
from services.route_optimizer import RouteOptimizer
from services.traffic_predictor import TrafficPredictor
from algorithms.path_finding import PathFinder
import networkx as nx
import uuid
from datetime import datetime

app = FastAPI()

# Initialize services
graph = nx.read_gpickle("data/road_network.gpickle")  # Load pre-processed road network
path_finder = PathFinder(graph)
traffic_predictor = TrafficPredictor("models/traffic_model.joblib")
route_optimizer = RouteOptimizer(path_finder, traffic_predictor)

@app.post("/route", response_model=RouteResponse)
async def calculate_route(request: RouteRequest):
    try:
        start = (request.start.latitude, request.start.longitude)
        end = (request.end.latitude, request.end.longitude)
        
        optimized_path = route_optimizer.optimize_route(
            start,
            end,
            request.departure_time,
            request.preferences
        )
        
        # Calculate route metrics
        distance = sum(haversine(optimized_path[i], optimized_path[i+1])
                      for i in range(len(optimized_path)-1))
        
        traffic_level = "LOW"  # This would be calculated based on predictions
        
        return RouteResponse(
            route_id=str(uuid.uuid4()),
            path=[{"latitude": lat, "longitude": lon} for lat, lon in optimized_path],
            distance=distance,
            estimated_time=distance / 35.0,  # Simplified time estimation
            traffic_level=traffic_level,
            updated_at=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))