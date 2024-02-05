from django.test import TestCase
from rest_framework.test import APITestCase
# Create your tests here.


class VideoApiTestCase(APITestCase):
    def test_get_videos_with_pagination(self):
        # Get a list of videos with pagination
        response = self.client.get('/api/video/', {'offset': 10, 'lang': 'en'})
        # Assert that the response is successful
        self.assertEqual(response.status_code, 200)
        # Assert that the response contains a list of videos
        self.assertIsInstance(response.data, list)
        # Assert that the list of videos has the expected number of items
        self.assertEqual(len(response.data), 10)
        # Assert that the videos in the list are in the correct language
        for video in response.data:
            self.assertEqual(video['lang'], 'en')
