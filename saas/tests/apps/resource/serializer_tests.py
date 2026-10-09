from backend.apps.resource.serializers import ResourceAttributeQuerySLZ, ResourceAttributeValueQuerySLZ
from backend.service.models.resource import ResourceAttribute


def test_resource_attribute_query_parses_topology_path():
    slz = ResourceAttributeQuerySLZ(
        data={
            "system_id": "bk_itsm",
            "type": "ticket",
            "limit": 100,
            "offset": 0,
            "_iam_topo_path_": '[[{"type":"workflow","id":"1"}]]',
        }
    )

    assert slz.is_valid(), slz.errors
    assert slz.validated_data["_iam_topo_path_"] == [[{"type": "workflow", "id": "1"}]]


def test_resource_attribute_defaults_legacy_metadata():
    attribute = ResourceAttribute(id="service", display_name="Service")

    assert attribute.type == "STRING"
    assert attribute.operators[0].id == "eq"


def test_resource_attribute_normalizes_extended_metadata():
    attribute = ResourceAttribute(
        id="title", display_name="Title", type="string", operators=["contains", {"id": "eq", "name": "Equals"}]
    )

    assert attribute.type == "STRING"
    assert [operator.id for operator in attribute.operators] == ["contains", "eq"]
    assert attribute.operators[0].name == "Contains"


def test_resource_attribute_value_query_accepts_local_value_type():
    slz = ResourceAttributeValueQuerySLZ(
        data={
            "system_id": "bk_itsm",
            "type": "ticket",
            "attribute": "submitter_department",
            "attribute_type": "DEPT",
            "operator": "in",
            "keyword": "platform",
            "limit": 10,
            "offset": 0,
        }
    )

    assert slz.is_valid(), slz.errors
    assert slz.validated_data["attribute_type"] == "DEPT"
