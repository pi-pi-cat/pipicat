from tortoise import fields
from tortoise.models import Model
import datetime


class TestSession(Model):
    id = fields.IntField(pk=True)
    start_time = fields.DatetimeField(auto_now_add=True)
    description = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "test_sessions"


class CaseModel(Model):
    id = fields.IntField(pk=True)
    case_id = fields.IntField()
    predicted_runtime = fields.FloatField()
    actual_runtime = fields.FloatField(null=True)
    queue_level = fields.IntField()
    result_dir = fields.CharField(max_length=255, null=True)
    status = fields.CharField(max_length=20)
    session = fields.ForeignKeyField("models.TestSession", related_name="cases")

    class Meta:
        table = "cases"
