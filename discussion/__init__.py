import datetime
import uuid
from otree.api import *


class C(BaseConstants):
    NAME_IN_URL = 'otree-discussion'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    name = models.StringField()


class Post(ExtraModel):
    unique_id = models.StringField()
    player = models.Link(Player)
    group = models.Link(Group)
    title = models.StringField()
    content = models.LongStringField()
    created_at = models.StringField()


class PostReply(ExtraModel):
    unique_id = models.StringField()
    player = models.Link(Player)
    group = models.Link(Group)
    post_unique_id = models.StringField()
    content = models.LongStringField()
    created_at = models.StringField()


def post_to_dict(post: Post):
    replies = PostReply.filter(group=post.group, post_unique_id=post.unique_id)
    return dict(
        unique_id=post.unique_id,
        title=post.title,
        content=post.content,
        player_name=post.player.name,
        player_id=post.player.id_in_group,
        created_at=post.created_at,
        no_of_replies=len(replies)
    )


def post_reply_to_dict(post: PostReply):
    return dict(
        post_unique_id=post.post_unique_id,
        unique_id=post.unique_id,
        content=post.content,
        player_name=post.player.name,
        player_id=post.player.id_in_group,
        created_at=post.created_at,
    )


# FUNCTIONS
def add_live_method(player: Player, data):
    group = player.group
    if data.get("type") == "add":
        title = data.get("title")
        content = data.get("content")
        Post.create(title=title, content=content, group=group, player=player,
                    created_at=datetime.datetime.strftime(datetime.datetime.now(), '%d/%m/%y %H:%M:%S'))
        posts = Post.filter(group=group)

        return {0: dict(
            posts=[post_to_dict(item) for item in posts],
            no_of_posts=len(posts),
        )}
    if data.get("type") == "load":
        posts = Post.filter(group=group)
        return {0: dict(
            posts=[post_to_dict(item) for item in posts],
            no_of_posts=len(posts),
        )}


def new_post_live_method(player: Player, data):
    group = player.group
    # print(data.get("is_post"))
    if data.get("type") == "add":
        if data.get("is_post"):
            title = data.get("title")
            content = data.get("content")
            Post.create(title=title, content=content, group=group, player=player,
                        unique_id=str(uuid.uuid4()),
                        created_at=datetime.datetime.strftime(datetime.datetime.now(), '%d/%m/%y %H:%M:%S'))
            posts = Post.filter(group=group)
            # print(posts)
            return {0: dict(
                is_post=True,
                posts=[post_to_dict(item) for item in posts],
                no_of_posts=len(posts),
            )}
        else:
            content = data.get("content")
            post_unique_id = data.get("post_unique_id")
            PostReply.create(content=content, group=group, player=player,
                             unique_id=str(uuid.uuid4()), post_unique_id=post_unique_id,
                             created_at=datetime.datetime.strftime(datetime.datetime.now(), '%d/%m/%y %H:%M:%S'))
            replies = PostReply.filter(group=player.group, post_unique_id=post_unique_id)
            parent_post = Post.filter(group=player.group, unique_id=post_unique_id)[0]
            # print({"replies": replies})
            return {0: dict(
                is_post=False,
                replies=[post_reply_to_dict(item) for item in replies],
                parent_post=post_to_dict(parent_post),
            )}

    if data.get("type") == "load":
        if data.get("is_post"):
            posts = Post.filter(group=group)
            return {0: dict(
                is_post=True,
                posts=[post_to_dict(item) for item in posts],
                no_of_posts=len(posts),
            )}
        else:
            post_unique_id = data.get("post_unique_id")
            replies = PostReply.filter(group=player.group, post_unique_id=post_unique_id)
            parent_post = Post.filter(group=player.group, unique_id=post_unique_id)[0]
            # print({"replies": replies})
            return {0: dict(
                is_post=False,
                replies=[post_reply_to_dict(item) for item in replies],
                parent_post=post_to_dict(parent_post),
            )}


# PAGES
class Introduction(Page):
    form_model = Player
    form_fields = ['name']


class Posts(Page):
    live_method = new_post_live_method


class NewPost(Page):
    live_method = new_post_live_method


page_sequence = [
    Introduction,
    Posts
]
