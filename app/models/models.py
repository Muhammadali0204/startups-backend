from uuid import uuid4
from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.BigIntField(primary_key=True)
    telegram_id = fields.BigIntField(unique=True)
    first_name = fields.CharField(max_length=255)
    last_name = fields.CharField(max_length=255, null=True)
    username = fields.CharField(max_length=255, null=True)
    photo_url = fields.TextField(null=True)
    created_time = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"


class Project(Model):
    id = fields.UUIDField(pk=True, default=uuid4)
    user = fields.ForeignKeyField("models.User", related_name="projects")
    data = fields.JSONField()
    title = fields.TextField()
    subtitle = fields.TextField()
    image_url = fields.TextField(null=True)
    created_time = fields.DatetimeField(auto_now_add=True)
    required_funds = fields.BigIntField()
    views = fields.ReverseRelation["ProjectView"]
    likes = fields.ReverseRelation["ProjectLike"]

    class Meta:
        table = "projects"


class ProjectLike(Model):
    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="likes")
    project = fields.ForeignKeyField("models.Project", related_name="likes")

    class Meta:
        table = "project_likes"
        unique_together = ("user", "project")

    def __str__(self) -> str:
        return str(self.id)


class ProjectView(Model):
    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="views")
    project = fields.ForeignKeyField("models.Project", related_name="views")

    class Meta:
        table = "project_views"
        unique_together = ("user", "project")

    def __str__(self) -> str:
        return str(self.id)


class ProjectShare(Model):
    id = fields.BigIntField(pk=True)
    user = fields.ForeignKeyField("models.User")
    project = fields.ForeignKeyField("models.Project")

    class Meta:
        table = "project_shares"
        unique_together = ("user", "project")

    def __str__(self) -> str:
        return str(self.id)
