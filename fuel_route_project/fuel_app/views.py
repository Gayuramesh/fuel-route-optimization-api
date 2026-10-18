# API views for the fuel route planning application

import logging

import requests
from rest_framework.views import APIView
from rest_framework.response import Response

from .services import (
    LocationNotFoundError,
    calculate_route_fuel_plan,
)

logger = logging.getLogger(__name__)


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

        if not start or not finish:
            return Response(
                {"error": "start and finish required"},
                status=400,
            )

        if not isinstance(start, str) or not start.strip():
            return Response(
                {"error": "A valid start location is required."},
                status=400,
            )

        if not isinstance(finish, str) or not finish.strip():
            return Response(
                {"error": "A valid finish location is required."},
                status=400,
            )

        start = start.strip()
        finish = finish.strip()

        try:
            result = calculate_route_fuel_plan(start, finish)

        except LocationNotFoundError as exc:
            return Response(
                {"error": str(exc)},
                status=400,
            )

        except requests.HTTPError as exc:
            status_code = (
                exc.response.status_code
                if exc.response is not None
                else None
            )

            logger.exception(
                "Routing provider HTTP error: %s",
                status_code,
            )

            if status_code is not None and 400 <= status_code < 500:
                return Response(
                    {"error": "The routing provider rejected the request."},
                    status=400,
                )

            return Response(
                {"error": "The routing provider could not process the request."},
                status=502,
            )

        except requests.Timeout:
            logger.exception("Routing provider request timed out")

            return Response(
                {"error": "The routing service is temporarily unavailable."},
                status=502,
            )

        except requests.RequestException:
            logger.exception("Routing provider request failed")

            return Response(
                {"error": "The routing service is temporarily unavailable."},
                status=502,
            )

        except (KeyError, IndexError, TypeError):
            logger.exception(
                "Unexpected data error during route calculation"
            )

            return Response(
                {"error": "Unable to calculate the route."},
                status=500,
            )

        except ValueError:
            logger.exception(
                "Unexpected value error during route calculation"
            )

            return Response(
                {"error": "Unable to calculate the route."},
                status=500,
            )

        return Response(result)
