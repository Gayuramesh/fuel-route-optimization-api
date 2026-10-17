# API views for the fuel route planning application

import requests
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

        Returns:
            400: If either location is missing or invalid.
            502: If an external routing service fails.
            200: If the route fuel plan is calculated successfully.
        """
        start = request.data.get("start")
        finish = request.data.get("finish")

        # Validate the required locations
        if not start or not finish:
            return Response(
                {"error": "start and finish required"},
                status=400,
            )

        # Validate start location
        if not isinstance(start, str) or not start.strip():
            return Response(
                {"error": "A valid start location is required."},
                status=400,
            )

        # Validate finish location
        if not isinstance(finish, str) or not finish.strip():
            return Response(
                {"error": "A valid finish location is required."},
                status=400,
            )

        # Remove leading and trailing whitespace
        start = start.strip()
        finish = finish.strip()

        # Calculate the optimal fuel route plan
        try:
            result = calculate_route_fuel_plan(start, finish)

        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=400,
            )

        except requests.RequestException:
            return Response(
                {"error": "The routing service is temporarily unavailable."},
                status=502,
            )

        except (KeyError, IndexError):
            return Response(
                {
                    "error": (
                        "Unable to calculate the route "
                        "with the available data."
                    )
                },
                status=502,
            )
        result = calculate_route_fuel_plan(start, finish)
        return Response(result)
