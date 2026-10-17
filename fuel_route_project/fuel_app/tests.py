from unittest.mock import patch

from rest_framework.test import APITestCase


class RouteFuelAPIViewTests(APITestCase):
    def test_missing_locations_returns_400(self):
        response = self.client.post(
            "/api/route/",
            {},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    @patch("fuel_app.views.calculate_route_fuel_plan")
    def test_whitespace_location_returns_400(self, mock_calculate):
        response = self.client.post(
            "/api/route/",
            {"start": "   ", "finish": "Dallas, TX"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        mock_calculate.assert_not_called()
