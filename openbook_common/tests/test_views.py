from django.urls import reverse
from django.core.cache import cache
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase

import logging
import json

from openbook_common.tests.helpers import make_emoji_group, make_emoji, make_user, make_authentication_headers_for_user, \
    make_fake_post_text, make_whitelisted_domain

logger = logging.getLogger(__name__)


class TimeAPITests(APITestCase):
    """
    TimeAPITests
    """

    def test_timezone_set(self):
        """
        should set the timezone provided in the Time-Zone header
        """
        url = self._get_url()
        timezone_to_set = 'America/Mexico_City'
        header = {'HTTP_TIME_ZONE': timezone_to_set}
        response = self.client.get(url, **header)
        parsed_response = json.loads(response.content)
        self.assertEqual(parsed_response['timezone'], timezone_to_set)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _get_url(self):
        return reverse('time')


class TestHealth(APITestCase):
    """
    Health API
    """

    url = reverse('health')

    def test_should_say_hello(self):
        response = self.client.get(self.url)
        self.assertTrue(response.status_code, status.HTTP_200_OK)


class TestEmojiGroups(APITestCase):
    """
    EmojiGroups API
    """

    def test_can_retrieve_non_reaction_emoji_groups(self):
        """
         should be able to retrieve non post reaction emoji groups
        """
        user = make_user()
        headers = make_authentication_headers_for_user(user)

        group_ids = []
        amount_of_groups = 4

        for x in range(amount_of_groups):
            group = make_emoji_group(is_reaction_group=False)
            group_ids.append(group.pk)

        url = self._get_url()
        response = self.client.get(url, **headers)
        self.assertTrue(response.status_code, status.HTTP_200_OK)

        response_groups = json.loads(response.content)
        response_groups_ids = [group['id'] for group in response_groups]

        self.assertEqual(len(response_groups), len(group_ids))

        for group_id in group_ids:
            self.assertIn(group_id, response_groups_ids)

    def test_cannot_retrieve_reactions_emoji_groups(self):
        """
         should not able to retrieve post reaction emoji groups
        """
        user = make_user()
        headers = make_authentication_headers_for_user(user)

        group_ids = []
        amount_of_groups = 4

        for x in range(amount_of_groups):
            group = make_emoji_group(is_reaction_group=True)
            group_ids.append(group.pk)

        url = self._get_url()
        response = self.client.get(url, **headers)
        self.assertTrue(response.status_code, status.HTTP_200_OK)

        response_groups = json.loads(response.content)

        self.assertEqual(len(response_groups), 0)

    def _get_url(self):
        return reverse('emoji-groups')


class PreviewLinkDataAPITests(APITestCase):
    """
    PreviewLinkDataAPI
    """

    def test_retrieves_preview_data_for_whitelisted_domain(self):
        """
        should retrieve preview data for a link in a whitelisted domain and return 200
        """
        cache.delete(settings.POST_LINK_WHITELIST_DOMAIN_CACHE_KEY)  # clear cache value
        user = make_user()
        headers = make_authentication_headers_for_user(user)
        preview_url = 'www.okuna.io'
        url = self._get_url()
        make_whitelisted_domain(domain='okuna.io')

        response = self.client.get(url, {'url': preview_url}, **headers)
        preview_data = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('title' in preview_data.keys())
        self.assertTrue('description' in preview_data.keys())
        self.assertTrue('image_url' in preview_data.keys())
        self.assertTrue('favicon_url' in preview_data.keys())
        self.assertTrue('domain_url' in preview_data.keys())

    def test_cannot_retrieve_preview_data_for_domain_not_in_whitelist(self):
        """
        should not retrieve preview data for a link if the domain is not whitelisted and return 400
        """
        user = make_user()
        headers = make_authentication_headers_for_user(user)
        preview_url = 'https://www.techcrunch.com'
        url = self._get_url()

        response = self.client.get(url, {'url': preview_url}, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_retrieve_preview_data_for_invalid_url(self):
        """
        should fail to retrieve preview data for an invalid url and return 400
        """
        user = make_user()
        headers = make_authentication_headers_for_user(user)
        preview_url = make_fake_post_text()

        url = self._get_url()
        response = self.client.get(url, {'url': preview_url}, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_retrieve_post_preview_data_for_url_with_unreachable_link(self):
        """
        should fail to retrieve preview data for a url which is unreachable and return 400
        """
        user = make_user()
        headers = make_authentication_headers_for_user(user)
        preview_url = 'https://www.invalid-XITSrbQomu0pnj2ISa4OOFq_NySDkyXMsw0cBxKYUc.com/doesntexist/eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9/'

        url = self._get_url()
        response = self.client.get(url, {'url': preview_url}, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _get_url(self):
        return reverse('preview-link')
