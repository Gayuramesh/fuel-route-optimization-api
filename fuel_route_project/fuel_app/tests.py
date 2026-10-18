from unittest.mock import patch

import requests
from rest_framework.test import APITestCase, APIRequestFactory

from .views import RouteFuelAPIView
from .services import LocationNotFoundError


class RouteFuelAPIViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RouteFuelAPIView.as_view()

    def make_request(self):
        return self.factory.post(
            "/api/route/",
            {"start": "Dallas, TX", "finish": "Austin, TX"},
            format="json",
        )

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_missing_locations_returns_400(self, mock_calculate):
        request = self.factory.post("/api/route/", {}, format="json")
        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        mock_calculate.assert_not_called()

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_whitespace_start_returns_400(self, mock_calculate):
        request = self.factory.post(
            "/api/route/",
            {"start": "   ", "finish": "Dallas, TX"},
            format="json",
        )
        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        mock_calculate.assert_not_called()

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_non_string_start_returns_400(self, mock_calculate):
        request = self.factory.post(
            "/api/route/",
            {"start": 123, "finish": "Dallas, TX"},
            format="json",
        )
        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        mock_calculate.assert_not_called()

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_non_string_finish_returns_400(self, mock_calculate):
        request = self.factory.post(
            "/api/route/",
            {"start": "Dallas, TX", "finish": ["Austin, TX"]},
            format="json",
        )
        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        mock_calculate.assert_not_called()

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_locations_are_trimmed(self, mock_calculate):
        mock_calculate.return_value = {
            "distance_miles": 100,
            "fuel_required_gallons": 10,
            "fuel_stops": [],
            "total_fuel_cost": 0,
        }

        request = self.factory.post(
            "/api/route/",
            {"start": " Dallas, TX ", "finish": " Austin, TX "},
            format="json",
        )
        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        mock_calculate.assert_called_once_with("Dallas, TX", "Austin, TX")

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_unknown_location_returns_400(self, mock_calculate):
        mock_calculate.side_effect = LocationNotFoundError(
            "No location found for: Unknown Place"
        )

        request = self.factory.post(
            "/api/route/",
            {"start": "Unknown Place", "finish": "Austin, TX"},
            format="json",
        )
        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["error"],
            "No location found for: Unknown Place",
        )

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_unexpected_value_error_returns_500(self, mock_calculate):
        mock_calculate.side_effect = ValueError("Unexpected internal error")
        response = self.view(self.make_request())

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.data["error"],
            "Unable to calculate the route.",
        )

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_type_error_returns_500(self, mock_calculate):
        mock_calculate.side_effect = TypeError("Unexpected internal error")
        response = self.view(self.make_request())

        self.assertEqual(response.status_code, 500)

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_key_error_returns_500(self, mock_calculate):
        mock_calculate.side_effect = KeyError("missing_key")
        response = self.view(self.make_request())

        self.assertEqual(response.status_code, 500)

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_index_error_returns_500(self, mock_calculate):
        mock_calculate.side_effect = IndexError("missing item")
        response = self.view(self.make_request())

        self.assertEqual(response.status_code, 500)

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_timeout_returns_502(self, mock_calculate):
        mock_calculate.side_effect = requests.Timeout("Request timed out")
        response = self.view(self.make_request())

        self.assertEqual(response.status_code, 502)
        self.assertEqual(
            response.data["error"],
            "The routing service is temporarily unavailable.",
        )

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_request_exception_returns_502(self, mock_calculate):
        mock_calculate.side_effect = requests.RequestException(
            "Connection failed"
        )
        response = self.view(self.make_request())

        self.assertEqual(response.status_code, 502)

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_provider_http_500_returns_502(self, mock_calculate):
        response_error = requests.Response()
        response_error.status_code = 500

        mock_calculate.side_effect = requests.HTTPError(
            "Provider server error",
            response=response_error,
        )
        response = self.view(self.make_request())

        self.assertEqual(response.status_code, 502)

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_provider_http_400_returns_400(self, mock_calculate):
        response_error = requests.Response()
        response_error.status_code = 400

        mock_calculate.side_effect = requests.HTTPError(
            "Provider rejected request",
            response=response_error,
        )
        response = self.view(self.make_request())

        self.assertEqual(response.status_code, 400)
