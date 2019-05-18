import json

from django.urls import reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APITestCase

from openbook_common.tests.helpers import make_global_moderator, make_user, make_moderation_category, \
    make_authentication_headers_for_user, make_moderation_report_description, make_moderated_object_description, \
    make_community, make_fake_post_text, make_fake_post_comment_text
from openbook_moderation.models import ModeratedObject, ModeratedObjectDescriptionChangedLog, \
    ModeratedObjectCategoryChangedLog

fake = Faker()


class ModeratedObjectAPITests(APITestCase):
    """
    ModeratedObjectAPI
    """

    def test_can_update_user_moderated_object_if_global_moderator(self):
        """
        should be able to update a user moderated object if global moderator
        """
        global_moderator = make_global_moderator()

        user = make_user()

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_user_with_username(username=user.username, category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()
        new_report_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_user(user=user,
                                                                                   category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(global_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
            'category_id': new_report_category.pk
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(ModeratedObject.objects.filter(
            category_id=new_report_category.pk,
            description=new_moderated_object_description,
            object_id=user.pk,
        ).exists())

    def test_cant_update_user_moderated_object_if_not_global_moderator(self):
        """
        should not be able to update a user moderated object if not a global moderator
        """
        non_global_moderator = make_user()

        user = make_user()

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_user_with_username(username=user.username, category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()
        new_report_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_user(user=user,
                                                                                   category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(non_global_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
            'category_id': new_report_category.pk
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(ModeratedObject.objects.filter(
            category_id=new_report_category.pk,
            description=new_moderated_object_description,
            object_id=user.pk,
        ).exists())

    def test_cant_update_user_moderated_object_if_community_moderator(self):
        """
        should not be able to update a user moderated object if community moderator
        """

        community_creator = make_user()
        community = make_community(creator=community_creator)

        community_moderator = make_user()
        community_moderator.join_community_with_name(community_name=community.name)
        community_creator.add_moderator_with_username_to_community_with_name(username=community_moderator.username,
                                                                             community_name=community.name)

        user = make_user()
        user.join_community_with_name(community_name=community.name)

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_user_with_username(username=user.username, category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()
        new_report_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_user(user=user,
                                                                                   category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(community_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
            'category_id': new_report_category.pk
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(ModeratedObject.objects.filter(
            category_id=new_report_category.pk,
            description=new_moderated_object_description,
            object_id=user.pk,
        ).exists())

    def test_creates_description_changed_log_on_update(self):
        """
        should create a description changed log on update
        """
        global_moderator = make_global_moderator()

        user = make_user()

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_user_with_username(username=user.username, category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_user(user=user,
                                                                                   category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(global_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(1, ModeratedObjectDescriptionChangedLog.objects.filter(
            changed_from__isnull=True,
            changed_to=new_moderated_object_description,
            log__actor_id=global_moderator.pk,
            log__moderated_object__object_id=user.pk
        ).count())

    def test_creates_category_changed_log_on_update(self):
        """
        should create a category changed log on update
        """
        global_moderator = make_global_moderator()

        user = make_user()

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_user_with_username(username=user.username, category_id=report_category.pk)

        new_moderated_object_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_user(user=user,
                                                                                   category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(global_moderator)
        response = self.client.patch(url, data={
            'category_id': new_moderated_object_category.pk,
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(1, ModeratedObjectCategoryChangedLog.objects.filter(
            changed_from=report_category,
            changed_to=new_moderated_object_category,
            log__actor_id=global_moderator.pk,
            log__moderated_object__object_id=user.pk
        ).count())

    def test_can_update_community_moderated_object_if_global_moderator(self):
        """
        should be able to update a community moderated object if global moderator
        """
        global_moderator = make_global_moderator()

        community = make_community()

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_community_with_name(community_name=community.name, category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()
        new_report_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_community(community=community,
                                                                                        category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(global_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
            'category_id': new_report_category.pk
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(ModeratedObject.objects.filter(
            category_id=new_report_category.pk,
            description=new_moderated_object_description,
            object_id=community.pk,
        ).exists())

    def test_cant_update_community_moderated_object_if_not_global_moderator(self):
        """
        should not be able to update a community moderated object if not a global moderator
        """
        non_global_moderator = make_user()

        community = make_community()

        reporter_community = make_community()
        report_category = make_moderation_category()

        reporter_community.report_community_with_name(community_name=community.name,
                                                      category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()
        new_report_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_community(community=community,
                                                                                        category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(non_global_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
            'category_id': new_report_category.pk
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(ModeratedObject.objects.filter(
            category_id=new_report_category.pk,
            description=new_moderated_object_description,
            object_id=community.pk,
        ).exists())

    def test_cant_update_community_moderated_object_if_community_moderator(self):
        """
        should not be able to update a community moderated object if community moderator
        """

        community_creator = make_user()
        community = make_community(creator=community_creator)

        community_moderator = make_user()
        community_moderator.join_community_with_name(community_name=community.name)
        community_creator.add_moderator_with_username_to_community_with_name(
            username=community_moderator.username,
            community_name=community.name)

        user = make_user()
        user.join_community_with_name(community_name=community.name)

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_community_with_name(community_name=community.name,
                                                 category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()
        new_report_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_community(community=community,
                                                                                        category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(community_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
            'category_id': new_report_category.pk
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(ModeratedObject.objects.filter(
            category_id=new_report_category.pk,
            description=new_moderated_object_description,
            object_id=community.pk,
        ).exists())

    def test_can_update_community_post_moderated_object_if_global_moderator(self):
        """
        should be able to update a community post moderated object if global moderator
        """
        global_moderator = make_global_moderator()

        community = make_community()
        post_creator = make_user()

        post_creator.join_community_with_name(community_name=community.name)
        post = post_creator.create_community_post(community_name=community.name, text=make_fake_post_text())

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_post(post=post, category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()
        new_report_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_post(post=post,
                                                                                   category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(global_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
            'category_id': new_report_category.pk
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(ModeratedObject.objects.filter(
            category_id=new_report_category.pk,
            description=new_moderated_object_description,
            object_id=post.pk,
        ).exists())

    def test_can_update_community_post_moderated_object_if_community_moderator(self):
        """
        should be able to update a community post moderated object if community moderator
        """
        community_creator = make_user()
        community = make_community(creator=community_creator)
        community_moderator = make_user()
        community_moderator.join_community_with_name(community_name=community.name)

        community_creator.add_moderator_with_username_to_community_with_name(username=community_moderator.username,
                                                                             community_name=community.name)

        post_creator = make_user()

        post_creator.join_community_with_name(community_name=community.name)
        post = post_creator.create_community_post(community_name=community.name, text=make_fake_post_text())

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_post(post=post, category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()
        new_report_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_post(post=post,
                                                                                   category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(community_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
            'category_id': new_report_category.pk
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(ModeratedObject.objects.filter(
            category_id=new_report_category.pk,
            description=new_moderated_object_description,
            object_id=post.pk,
        ).exists())

    def test_cant_update_community_post_moderated_object_if_not_global_nor_community_moderator(self):
        """
        should not be able to update a community post moderated object if not global nor community moderator
        """
        community_creator = make_user()
        community = make_community(creator=community_creator)
        non_moderator = make_user()

        post_creator = make_user()

        post_creator.join_community_with_name(community_name=community.name)
        post = post_creator.create_community_post(community_name=community.name, text=make_fake_post_text())

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_post(post=post, category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()
        new_report_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_post(post=post,
                                                                                   category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(non_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
            'category_id': new_report_category.pk
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(ModeratedObject.objects.filter(
            category_id=new_report_category.pk,
            description=new_moderated_object_description,
            object_id=post.pk,
        ).exists())

    def test_can_update_community_post_comment_moderated_object_if_global_moderator(self):
        """
        should be able to update a community post_comment moderated object if global moderator
        """
        global_moderator = make_global_moderator()

        community = make_community()
        post_comment_creator = make_user()

        post_comment_creator.join_community_with_name(community_name=community.name)
        post = post_comment_creator.create_community_post(text=make_fake_post_text(), community_name=community.name)
        post_comment = post_comment_creator.comment_post(text=make_fake_post_comment_text(),
                                                         post=post)

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_comment_for_post(post=post, post_comment=post_comment, category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()
        new_report_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_post_comment(post_comment=post_comment,
                                                                                           category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(global_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
            'category_id': new_report_category.pk
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(ModeratedObject.objects.filter(
            category_id=new_report_category.pk,
            description=new_moderated_object_description,
            object_id=post_comment.pk,
        ).exists())

    def test_can_update_community_post_comment_moderated_object_if_community_moderator(self):
        """
        should be able to update a community post_comment moderated object if community moderator
        """
        community_creator = make_user()
        community = make_community(creator=community_creator)
        community_moderator = make_user()
        community_moderator.join_community_with_name(community_name=community.name)

        community_creator.add_moderator_with_username_to_community_with_name(username=community_moderator.username,
                                                                             community_name=community.name)

        post_comment_creator = make_user()

        post_comment_creator.join_community_with_name(community_name=community.name)
        post = post_comment_creator.create_community_post(text=make_fake_post_text(), community_name=community.name)
        post_comment = post_comment_creator.comment_post(text=make_fake_post_comment_text(),
                                                         post=post)

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_comment_for_post(post=post, post_comment=post_comment, category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()
        new_report_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_post_comment(post_comment=post_comment,
                                                                                           category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(community_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
            'category_id': new_report_category.pk
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(ModeratedObject.objects.filter(
            category_id=new_report_category.pk,
            description=new_moderated_object_description,
            object_id=post_comment.pk,
        ).exists())

    def test_cant_update_community_post_comment_moderated_object_if_not_global_nor_community_moderator(self):
        """
        should not be able to update a community post_comment moderated object if not global nor community moderator
        """
        non_global_moderator = make_user()

        community = make_community()
        post_comment_creator = make_user()

        post_comment_creator.join_community_with_name(community_name=community.name)
        post = post_comment_creator.create_community_post(text=make_fake_post_text(), community_name=community.name)
        post_comment = post_comment_creator.comment_post(text=make_fake_post_comment_text(),
                                                         post=post)

        reporter_user = make_user()
        report_category = make_moderation_category()

        reporter_user.report_comment_for_post(post=post, post_comment=post_comment, category_id=report_category.pk)

        new_moderated_object_description = make_moderated_object_description()
        new_report_category = make_moderation_category()

        moderated_object = ModeratedObject.get_or_create_moderated_object_for_post_comment(post_comment=post_comment,
                                                                                           category_id=report_category.pk)

        url = self._get_url(moderated_object=moderated_object)
        headers = make_authentication_headers_for_user(non_global_moderator)
        response = self.client.patch(url, data={
            'description': new_moderated_object_description,
            'category_id': new_report_category.pk
        }, **headers)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertFalse(ModeratedObject.objects.filter(
            category_id=new_report_category.pk,
            description=new_moderated_object_description,
            object_id=post_comment.pk,
        ).exists())

    def _get_url(self, moderated_object):
        return reverse('moderated-object', kwargs={
            'moderated_object_id': moderated_object.pk
        })
