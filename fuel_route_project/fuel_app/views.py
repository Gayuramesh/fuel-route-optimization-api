# API views for the fuel route planning application

from rest_framework.views import APIView
from rest_framework.response import Response
from .services import calculate_route_fuel_plan


class RouteFuelAPIView(APIView):
    """
    API endpoint for calculating optimal fuel stops along a route.
    
    This view accepts a start and finish location, then calculates:
    - The total distance of the route
    - Required fuel amount
    - Optimal fuel stop locations with pricing information
    - Total estimated fuel cost
    """
    
    def post(self, request):
        """
        Handle POST request to calculate fuel route plan.
        
        Request body should contain:
            - start (str): Starting location (city name or address)
            - finish (str): Destination location (city name or address)
        
        Returns:
            - 400: If start or finish parameters are missing
            - 200: Route fuel plan with stops and cost information
        """
        start = request.data.get("start")
        finish = request.data.get("finish")

        # Validate that both start and finish locations are provided
        if not start or not finish:
            return Response(
                {"error": "start and finish required"},
                status=400
            )

        # Calculate the optimal fuel route plan
        result = calculate_route_fuel_plan(start, finish)
        return Response(result)