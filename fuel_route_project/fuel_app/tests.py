from unittest.mock import patch

from rest_framework.test import APITestCase, APIRequestFactory

from .views import RouteFuelAPIView


class RouteFuelAPIViewTests(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RouteFuelAPIView.as_view()

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_missing_locations_returns_400(self, mock_calculate):
        request = self.factory.post(
            "/api/route/",
            {},
            format="json",
        )

        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        mock_calculate.assert_not_called()

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_whitespace_start_returns_400(self, mock_calculate):
        request = self.factory.post(
            "/api/route/",
            {
                "start": "   ",
                "finish": "Dallas, TX",
            },
            format="json",
        )

        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        mock_calculate.assert_not_called()

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_non_string_start_returns_400(self, mock_calculate):
        request = self.factory.post(
            "/api/route/",
            {
                "start": 123,
                "finish": "Dallas, TX",
            },
            format="json",
        )

        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        mock_calculate.assert_not_called()

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_non_string_finish_returns_400(self, mock_calculate):
        request = self.factory.post(
            "/api/route/",
            {
                "start": "Dallas, TX",
                "finish": ["Austin, TX"],
            },
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
            {
                "start": " Dallas, TX ",
                "finish": " Austin, TX ",
            },
            format="json",
        )

        response = self.view(request)

        self.assertEqual(response.status_code, 200)
        mock_calculate.assert_called_once_with(
            "Dallas, TX",
            "Austin, TX",
        )

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_location_not_found_returns_400(self, mock_calculate):
        from .services import LocationNotFoundError

        mock_calculate.side_effect = LocationNotFoundError(
            "No location found for: Unknown Place"
        )

        request = self.factory.post(
            "/api/route/",
            {
                "start": "Unknown Place",
                "finish": "Austin, TX",
            },
            format="json",
        )

        response = self.view(request)

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
