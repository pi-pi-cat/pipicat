from tortoise import Tortoise

# 导入model
from tortoise.models import Model
from tortoise import fields


class TestSession(Model):
    id = fields.IntField(pk=True)
    start_time = fields.DatetimeField(auto_now_add=True)
    description = fields.CharField(max_length=255, null=True)
    session_name = fields.CharField(max_length=255, null=True)
    visible = fields.BooleanField(default=False)

    class Meta:
        table = "test_sessions"


class CaseModel(Model):
    id = fields.IntField(pk=True)
    predicted_runtime = fields.FloatField(null=True)
    actual_runtime = fields.FloatField(null=True)
    start_time = fields.DatetimeField(auto_now_add=True)
    end_time = fields.DatetimeField(null=True)
    queue_level = fields.IntField()
    result_dir = fields.CharField(max_length=255, null=True)
    status = fields.CharField(max_length=20)
    session = fields.ForeignKeyField("models.TestSession", related_name="cases")

    class Meta:
        table = "cases"
