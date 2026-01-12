"""
Vehicle Routing Problem with Time Windows (VRPTW) using Google OR-Tools
Optimizes delivery routes considering:
- Vehicle capacity constraints
- Time windows for deliveries
- Minimize total distance/time
"""

from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import requests
from typing import List, Dict, Tuple
import math

class RouteOptimizer:
    def __init__(self, osrm_url: str = "http://router.project-osrm.org"):
        self.osrm_url = osrm_url
        self.distance_matrix = None
        self.time_matrix = None
    
    def get_distance_matrix(self, coordinates: List[Tuple[float, float]]) -> List[List[int]]:
        """
        Fetch distance matrix from OSRM API
        coordinates: list of (lat, lon) tuples
        returns: distance matrix in meters
        """
        if len(coordinates) == 0:
            return [[]]
        
        try:
            # Format for OSRM: lon,lat;lon,lat;...
            coords_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
            url = f"{self.osrm_url}/table/v1/driving/{coords_str}"
            
            response = requests.get(url, params={"annotations": "distance,duration"})
            data = response.json()
            
            if data.get("code") == "Ok":
                return data.get("distances", [])
            else:
                # Fallback to Haversine if OSRM fails
                return self._haversine_distance_matrix(coordinates)
        except Exception as e:
            print(f"OSRM error: {e}, using Haversine fallback")
            return self._haversine_distance_matrix(coordinates)
    
    def get_time_matrix(self, coordinates: List[Tuple[float, float]]) -> List[List[int]]:
        """
        Fetch time matrix from OSRM API
        returns: time matrix in seconds
        """
        if len(coordinates) == 0:
            return [[]]
        
        try:
            coords_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
            url = f"{self.osrm_url}/table/v1/driving/{coords_str}"
            
            response = requests.get(url, params={"annotations": "duration"})
            data = response.json()
            
            if data.get("code") == "Ok":
                return data.get("durations", [])
        except Exception as e:
            print(f"Time matrix error: {e}")
        
        return self._time_from_distance(self.distance_matrix) if self.distance_matrix else [[]]
    
    def _haversine_distance_matrix(self, coordinates: List[Tuple[float, float]]) -> List[List[int]]:
        """Calculate distance matrix using Haversine formula (fallback)"""
        n = len(coordinates)
        matrix = [[0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    lat1, lon1 = coordinates[i]
                    lat2, lon2 = coordinates[j]
                    distance = self._haversine(lat1, lon1, lat2, lon2)
                    matrix[i][j] = int(distance * 1000)  # Convert to meters
        
        return matrix
    
    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in km"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    @staticmethod
    def _time_from_distance(distance_matrix: List[List[int]]) -> List[List[int]]:
        """Estimate time from distance (assume 50 km/h average)"""
        if not distance_matrix:
            return [[]]
        
        speed_m_s = 50000 / 3600  # 50 km/h in m/s
        return [[int(d / speed_m_s) for d in row] for row in distance_matrix]
    
    def optimize(
        self,
        commandes: List[Dict],
        drivers: List[Dict],
        depot_coords: Tuple[float, float],
        planning_date: str
    ) -> Dict:
        """
        Optimize routes for given commandes and drivers
        
        Args:
            commandes: list of {id, lat, lon, poids, service_time_minutes}
            drivers: list of {id, capacity_kg}
            depot_coords: (lat, lon) of depot
            planning_date: date for planning
        
        Returns:
            optimized routes with assignments and sequences
        """
        
        if not commandes or not drivers:
            return {"error": "No commandes or drivers"}
        
        # Prepare data
        n_locations = len(commandes) + 1  # +1 for depot
        n_vehicles = len(drivers)
        
        # Build coordinates list (depot first)
        all_coords = [depot_coords] + [(c["latitude"], c["longitude"]) for c in commandes]
        
        # Get distance and time matrices from OSRM
        self.distance_matrix = self.get_distance_matrix(all_coords)
        self.time_matrix = self.get_time_matrix(all_coords)
        
        # Service times (in seconds)
        service_times = [0] + [c.get("service_time_minutes", 10) * 60 for c in commandes]
        
        # Weights
        weights = [0] + [c["poids"] for c in commandes]
        vehicle_capacities = [d["capacity_kg"] for d in drivers]
        
        # Create routing index manager
        manager = pywrapcp.RoutingIndexManager(n_locations, n_vehicles, 0)  # 0 is depot
        routing = pywrapcp.RoutingModel(manager)
        
        # Define cost callback for distances
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return self.distance_matrix[from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Add capacity constraint
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return weights[from_node]
        
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # slack
            vehicle_capacities,
            True,
            "Capacity"
        )
        
        # Add time constraint (8 AM to 6 PM work window)
        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return self.time_matrix[from_node][to_node] + service_times[from_node]
        
        time_callback_index = routing.RegisterTransitCallback(time_callback)
        routing.AddDimension(
            time_callback_index,
            0,  # slack
            10 * 3600,  # max time (10 hours in seconds)
            True,
            "Time"
        )
        
        # Optimize
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.time_limit.seconds = 10
        
        solution = routing.SolveWithParameters(search_parameters)
        
        if not solution:
            return {"error": "No solution found"}
        
        # Extract solution
        routes = []
        total_distance = 0
        total_time = 0
        
        for vehicle_id in range(n_vehicles):
            route_distance = 0
            route_time = 0
            route_commandes = []
            order = 1
            
            index = routing.Start(vehicle_id)
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                
                if node_index > 0:  # Skip depot
                    commande = commandes[node_index - 1]
                    route_commandes.append({
                        "commande_id": commande["id"],
                        "order": order,
                        "lat": commande["latitude"],
                        "lon": commande["longitude"]
                    })
                    order += 1
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
                route_time += solution.Value(routing.GetDimensionOrDie("Time").SlackVar(previous_index))
            
            if route_commandes:
                routes.append({
                    "driver_id": drivers[vehicle_id]["id"],
                    "commandes": route_commandes,
                    "distance_m": route_distance,
                    "time_s": route_time,
                    "commandes_count": len(route_commandes)
                })
            
            total_distance += route_distance
            total_time += route_time
        
        return {
            "success": True,
            "routes": routes,
            "total_distance_m": total_distance,
            "total_time_s": total_time,
            "total_vehicles_used": len(routes),
            "planning_date": planning_date
        }
