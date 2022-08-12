import datetime

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
    player = models.Link(Player)
    group = models.Link(Group)
    content = models.LongStringField()
    created_at = models.StringField()


def to_dict(post: Post):
    return dict(
        content=post.content,
        player_name=post.player.name,
        player_id=post.player.id_in_group,
        created_at=post.created_at,
    )


# FUNCTIONS
def add_live_method(player: Player, data):
    group = player.group
    if data.get("type") == "add":

        content = data.get("message")
        Post.create(content=content, group=group, player=player,
                    created_at=datetime.datetime.strftime(datetime.datetime.now(), '%d/%m/%y %H:%M:%S'))
        posts = Post.filter(group=group)

        return {0: dict(
            posts=[to_dict(item) for item in posts],
            no_of_posts=len(posts),
        )}
    if data.get("type") == "load":
        posts = Post.filter(group=group)
        return {0: dict(
            posts=[to_dict(item) for item in posts],
            no_of_posts=len(posts),
        )}


# PAGES
class Introduction(Page):
    form_model = Player
    form_fields = ['name']


class RoomChat(Page):
    live_method = add_live_method

    @staticmethod
    def js_vars(player: Player):
        return dict(player_id=player.id_in_group)

page_sequence = [
    Introduction,
    RoomChat
]
