# optimization/optimizer.py
"""
Vehicle Routing Problem with Time Windows (VRPTW-ish) using Google OR-Tools
Optimizes delivery routes considering:
- Vehicle capacity constraints
- Max working time per vehicle (route duration)
- Minimize total distance
Uses OSRM table API for distance/duration matrices, with robust fallbacks + sanitization.

Extra behavior added:
- If infeasible, progressively drops the MOST RECENT commandes (latest first)
  until a feasible solution is found.
"""

from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import requests
from typing import List, Dict, Tuple
import math


class RouteOptimizer:
    def __init__(self, osrm_url: str = "http://router.project-osrm.org"):
        self.osrm_url = osrm_url
        self.distance_matrix: List[List[int]] | None = None
        self.time_matrix: List[List[int]] | None = None

    # ----------------------------
    # Matrix utilities
    # ----------------------------
    @staticmethod
    def _sanitize_matrix(matrix, big: int = 10**9) -> List[List[int]]:
        """
        Ensure matrix is square NxN and contains ints only.
        Replace None values with a very large cost to discourage those arcs.
        """
        if not matrix or not isinstance(matrix, list):
            raise ValueError("OSRM returned empty/invalid matrix")

        n = len(matrix)
        if any(row is None or not isinstance(row, list) for row in matrix):
            raise ValueError("OSRM matrix has null/invalid rows")

        if any(len(row) != n for row in matrix):
            raise ValueError("OSRM matrix is not square")

        out: List[List[int]] = []
        for row in matrix:
            new_row: List[int] = []
            for v in row:
                if v is None:
                    new_row.append(big)
                else:
                    # OSRM can return floats; OR-Tools needs ints
                    new_row.append(int(v))
            out.append(new_row)
        return out

    @staticmethod
    def _ensure_coords(lat: float | None, lon: float | None) -> None:
        if lat is None or lon is None:
            raise ValueError("Missing latitude/longitude (None)")
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            raise ValueError("Latitude/longitude must be numeric")

    # ----------------------------
    # OSRM calls + fallbacks
    # ----------------------------
    def get_distance_matrix(self, coordinates: List[Tuple[float, float]]) -> List[List[int]]:
        """
        Fetch distance matrix from OSRM API
        coordinates: list of (lat, lon)
        returns: distances in meters (int)
        """
        if len(coordinates) == 0:
            return [[]]

        # Validate coords early (avoid hidden None bugs)
        for lat, lon in coordinates:
            self._ensure_coords(lat, lon)

        try:
            coords_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
            url = f"{self.osrm_url}/table/v1/driving/{coords_str}"
            resp = requests.get(url, params={"annotations": "distance"}, timeout=20)
            data = resp.json()

            if data.get("code") == "Ok" and data.get("distances"):
                return self._sanitize_matrix(data["distances"])
        except Exception as e:
            print(f"OSRM distance error: {e}")

        # Fallback
        return self._haversine_distance_matrix(coordinates)

    def get_time_matrix(self, coordinates: List[Tuple[float, float]]) -> List[List[int]]:
        """
        Fetch time matrix from OSRM API
        returns: durations in seconds (int)
        """
        if len(coordinates) == 0:
            return [[]]

        for lat, lon in coordinates:
            self._ensure_coords(lat, lon)

        try:
            coords_str = ";".join([f"{lon},{lat}" for lat, lon in coordinates])
            url = f"{self.osrm_url}/table/v1/driving/{coords_str}"
            resp = requests.get(url, params={"annotations": "duration"}, timeout=20)
            data = resp.json()

            if data.get("code") == "Ok" and data.get("durations"):
                return self._sanitize_matrix(data["durations"])
        except Exception as e:
            print(f"OSRM duration error: {e}")

        # Fallback: derive from distance if possible, else empty
        if self.distance_matrix:
            return self._time_from_distance(self.distance_matrix)

        return [[]]

    def _haversine_distance_matrix(self, coordinates: List[Tuple[float, float]]) -> List[List[int]]:
        """Distance matrix using Haversine (meters)."""
        n = len(coordinates)
        matrix = [[0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                lat1, lon1 = coordinates[i]
                lat2, lon2 = coordinates[j]
                dist_km = self._haversine(lat1, lon1, lat2, lon2)
                matrix[i][j] = int(dist_km * 1000)

        return matrix

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Distance in km."""
        R = 6371.0
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def _time_from_distance(distance_matrix: List[List[int]]) -> List[List[int]]:
        """Estimate duration from distance (assume 50 km/h average)."""
        if not distance_matrix:
            return [[]]
        speed_m_s = 50000 / 3600  # 50 km/h
        return [[int(d / speed_m_s) for d in row] for row in distance_matrix]

    # ----------------------------
    # Optimization (progressive drop-latest)
    # ----------------------------
    def optimize(
        self,
        commandes: List[Dict],
        drivers: List[Dict],
        depot_coords: Tuple[float, float],
        planning_date: str,
        max_work_seconds: int = 10 * 3600,  # 10 hours
    ) -> Dict:
        """
        Progressive relaxation:
        - Try schedule all commandes
        - If infeasible, drop the MOST RECENT commandes first until feasible

        commandes items must include: id, latitude, longitude, poids
        Optional: service_time_minutes, created_at (for "latest" ordering)
        drivers items must include: id, capacity_kg
        depot_coords: (lat, lon)
        """
        if not commandes or not drivers:
            return {"error": "No commandes or drivers", "routes": [], "unscheduled_ids": []}

        # Validate depot coords
        depot_lat, depot_lon = depot_coords
        self._ensure_coords(depot_lat, depot_lon)

        # Filter out invalid commandes (coords/poids missing)
        valid_commandes: List[Dict] = []
        invalid_ids: List[int] = []
        for c in commandes:
            lat = c.get("latitude")
            lon = c.get("longitude")
            poids = c.get("poids")
            if lat is None or lon is None or poids is None:
                invalid_ids.append(c.get("id"))
                continue
            valid_commandes.append(c)

        if not valid_commandes:
            return {
                "success": False,
                "error": "No valid commandes (missing coords/poids)",
                "routes": [],
                "planning_date": planning_date,
                "invalid_commandes_dropped": invalid_ids,
                "unscheduled_ids": invalid_ids,
                "commandes_scheduled": 0,
                "commandes_unscheduled": len(invalid_ids),
            }

        # Sort so that we drop LATEST first.
        # Prefer created_at; fallback to id.
        def sort_key(c: Dict):
            created = c.get("created_at")
            if created:
                return created
            return c.get("id", 0)

        sorted_commandes = sorted(valid_commandes, key=sort_key, reverse=True)  # latest -> oldest

        last_error = None

        # Try with all commandes, then drop 1, 2, 3... latest commandes
        for drop_count in range(0, len(sorted_commandes) + 1):
            current_batch = sorted_commandes[drop_count:]  # keep older ones
            dropped_batch = sorted_commandes[:drop_count]  # dropped latest ones

            dropped_ids = [c.get("id") for c in dropped_batch if c.get("id") is not None]

            if not current_batch:
                break

            result = self._optimize_batch(
                commandes=current_batch,
                drivers=drivers,
                depot_coords=(depot_lat, depot_lon),
                max_work_seconds=max_work_seconds,
            )

            if result.get("success"):
                return {
                    "success": True,
                    "routes": result["routes"],
                    "total_distance_m": result["total_distance_m"],
                    "total_time_s": result["total_time_s"],
                    "total_vehicles_used": result["total_vehicles_used"],
                    "planning_date": planning_date,
                    "invalid_commandes_dropped": invalid_ids,
                    "unscheduled_ids": invalid_ids + dropped_ids,
                    "commandes_scheduled": len(current_batch),
                    "commandes_unscheduled": len(invalid_ids) + len(dropped_ids),
                }

            last_error = result.get("error") or "No solution found"

        return {
            "success": False,
            "error": last_error or "Unable to schedule any commandes",
            "routes": [],
            "planning_date": planning_date,
            "invalid_commandes_dropped": invalid_ids,
            "unscheduled_ids": invalid_ids + [c.get("id") for c in sorted_commandes if c.get("id") is not None],
            "commandes_scheduled": 0,
            "commandes_unscheduled": len(invalid_ids) + len(sorted_commandes),
        }

    def _optimize_batch(
        self,
        commandes: List[Dict],
        drivers: List[Dict],
        depot_coords: Tuple[float, float],
        max_work_seconds: int,
    ) -> Dict:
        """One optimization attempt for a given batch of commandes (robust OSRM + correct time)."""

        if not commandes or not drivers:
            return {"success": False, "error": "No commandes or drivers"}

        depot_lat, depot_lon = depot_coords
        self._ensure_coords(depot_lat, depot_lon)

        # Prepare data
        n_locations = len(commandes) + 1  # depot + commandes
        n_vehicles = len(drivers)

        all_coords = [(depot_lat, depot_lon)] + [(c["latitude"], c["longitude"]) for c in commandes]

        # Get & sanitize matrices (safe)
        self.distance_matrix = self.get_distance_matrix(all_coords)
        self.time_matrix = self.get_time_matrix(all_coords)

        # Service times (seconds)
        service_times = [0] + [int(c.get("service_time_minutes", 10) * 60) for c in commandes]

        # Demands (weights), convert to int scale
        weights = [0] + [float(c["poids"]) for c in commandes]
        weights_int = [int(w * 1000) for w in weights]

        vehicle_capacities = [int(d.get("capacity_kg", 0) * 1000) for d in drivers]
        if any(cap <= 0 for cap in vehicle_capacities):
            return {"success": False, "error": "One or more drivers have invalid capacity_kg"}

        # Create routing model
        manager = pywrapcp.RoutingIndexManager(n_locations, n_vehicles, 0)
        routing = pywrapcp.RoutingModel(manager)

        # Distance cost
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return int(self.distance_matrix[from_node][to_node])

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

        # Capacity dimension
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return weights_int[from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # slack
            vehicle_capacities,
            True,
            "Capacity",
        )

        # Time dimension (travel + service at FROM node)
        def time_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            travel = int(self.time_matrix[from_node][to_node])
            return travel + int(service_times[from_node])

        time_callback_index = routing.RegisterTransitCallback(time_callback)
        routing.AddDimension(
            time_callback_index,
            0,  # slack
            int(max_work_seconds),
            True,
            "Time",
        )

        # Search params
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        search_parameters.time_limit.seconds = 10
        # Uncomment for solver logs:
        # search_parameters.log_search = True

        solution = routing.SolveWithParameters(search_parameters)
        if not solution:
            return {"success": False, "error": "No solution found"}

        # Extract solution
        routes = []
        total_distance = 0
        total_time = 0
        time_dimension = routing.GetDimensionOrDie("Time")

        for vehicle_id in range(n_vehicles):
            index = routing.Start(vehicle_id)
            route_distance = 0
            route_commandes = []
            order = 1

            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)

                if node_index > 0:
                    commande = commandes[node_index - 1]
                    route_commandes.append(
                        {
                            "commande_id": commande["id"],
                            "order": order,
                            "lat": commande["latitude"],
                            "lon": commande["longitude"],
                        }
                    )
                    order += 1

                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)

            if route_commandes:
                end_index = routing.End(vehicle_id)
                route_time = solution.Value(time_dimension.CumulVar(end_index))

                routes.append(
                    {
                        "driver_id": drivers[vehicle_id]["id"],
                        "commandes": route_commandes,
                        "distance_m": int(route_distance),
                        "time_s": int(route_time),
                        "commandes_count": len(route_commandes),
                    }
                )
                total_distance += int(route_distance)
                total_time += int(route_time)

        return {
            "success": True,
            "routes": routes,
            "total_distance_m": int(total_distance),
            "total_time_s": int(total_time),
            "total_vehicles_used": len(routes),
        }
