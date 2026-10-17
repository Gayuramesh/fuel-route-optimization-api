
# API views for the fuel route planning application

from rest_framework.views import APIView
from rest_framework.response import Response
from .services import calculate_route_fuel_plan


class RouteFuelAPIView(APIView):
    """
    API endpoint for calculating optimal fuel stops along a route.
    """

    def post(self, request):
        """
        Calculate a fuel route plan using start and finish locations.
        """
        start = request.data.get("start")
        finish = request.data.get("finish")

        # Validate that both locations are provided as non-empty strings
        if not isinstance(start, str) or not start.strip():
            return Response(
                {"error": "A valid start location is required."},
                status=400
            )

        if not isinstance(finish, str) or not finish.strip():
            return Response(
                {"error": "A valid finish location is required."},
                status=400
            )

        # Remove unnecessary whitespace
        start = start.strip()
        finish = finish.strip()

        # Calculate the optimal fuel route plan
        result = calculate_route_fuel_plan(start, finish)
        return Response(result)
