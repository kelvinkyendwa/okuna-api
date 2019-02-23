from rest_framework import serializers
from django.conf import settings

from openbook_auth.models import UserProfile, User
from openbook_common.models import Emoji, EmojiGroup
from openbook_common.serializers_fields.post_comment import PostCommenterField
from openbook_common.validators import emoji_id_exists, emoji_group_id_exists
from openbook_communities.models import CommunityMembership
from openbook_posts.models import PostComment, PostReaction
from openbook_posts.validators import post_id_exists, post_comment_id_exists, post_reaction_id_exists


class DeletePostSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(
        validators=[post_id_exists],
        required=True,
    )


class PostCommenterProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'avatar',
        )


class PostCommentCommenterSerializer(serializers.ModelSerializer):
    profile = PostCommenterProfileSerializer(many=False)

    class Meta:
        model = User
        fields = (
            'username',
            'profile',
            'id'
        )


class PostCommenterCommunityMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityMembership
        fields = (
            'id',
            'user_id',
            'community_id',
            'is_administrator',
            'is_moderator',
        )


class PostCommentSerializer(serializers.ModelSerializer):
    commenter = PostCommenterField(post_commenter_serializer=PostCommentCommenterSerializer,
                                   community_membership_serializer=PostCommenterCommunityMembershipSerializer)

    class Meta:
        model = PostComment
        fields = (
            'commenter',
            'text',
            'created',
            'id'
        )


class CommentPostSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(
        validators=[post_id_exists],
        required=True,
    )
    text = serializers.CharField(max_length=settings.POST_COMMENT_MAX_LENGTH, required=True, allow_blank=False)


class GetPostCommentsSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(
        validators=[post_id_exists],
        required=True,
    )
    max_id = serializers.IntegerField(
        required=False,
    )
    count = serializers.IntegerField(
        required=False,
        max_value=20
    )


class DeletePostCommentSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(
        validators=[post_id_exists],
        required=True,
    )
    post_comment_id = serializers.IntegerField(
        validators=[post_comment_id_exists],
        required=True,
    )


class PostReactorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'avatar',
        )


class PostReactionReactorSerializer(serializers.ModelSerializer):
    profile = PostReactorProfileSerializer(many=False)

    class Meta:
        model = User
        fields = (
            'username',
            'profile',
            'id'
        )


class PostReactionEmojiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emoji
        fields = (
            'id',
            'keyword',
            'image',
            'created',
        )


class PostReactionSerializer(serializers.ModelSerializer):
    reactor = PostReactionReactorSerializer(many=False)
    emoji = PostReactionEmojiSerializer(many=False)

    class Meta:
        model = PostReaction
        fields = (
            'reactor',
            'created',
            'emoji',
            'id'
        )


class PostEmojiCountSerializer(serializers.Serializer):
    emoji = PostReactionEmojiSerializer(many=False)
    count = serializers.IntegerField(required=True, )


class ReactToPostSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(
        validators=[post_id_exists],
        required=True,
    )
    emoji_id = serializers.IntegerField(
        validators=[emoji_id_exists],
        required=True,
    )
    group_id = serializers.IntegerField(
        validators=[emoji_group_id_exists],
        required=True,
    )


class GetPostReactionsEmojiCountSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(
        validators=[post_id_exists],
        required=True,
    )


class GetPostReactionsSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(
        validators=[post_id_exists],
        required=True,
    )
    max_id = serializers.IntegerField(
        required=False,
    )
    count = serializers.IntegerField(
        required=False,
        max_value=20
    )
    emoji_id = serializers.IntegerField(
        validators=[emoji_id_exists],
        required=False,
    )


class DeletePostReactionSerializer(serializers.Serializer):
    post_id = serializers.IntegerField(
        validators=[post_id_exists],
        required=True,
    )
    post_reaction_id = serializers.IntegerField(
        validators=[post_reaction_id_exists],
        required=True,
    )


class PostReactionEmojiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emoji

        fields = (
            'id',
            'keyword',
            'image',
            'order',
        )


class PostReactionEmojiGroupSerializer(serializers.ModelSerializer):
    emojis = serializers.SerializerMethodField()

    def get_emojis(self, obj):
        emojis = obj.emojis.all().order_by('order')

        request = self.context['request']
        return PostReactionEmojiSerializer(emojis, many=True, context={'request': request}).data

    class Meta:
        model = EmojiGroup

        fields = (
            'id',
            'keyword',
            'color',
            'order',
            'emojis',
        )
