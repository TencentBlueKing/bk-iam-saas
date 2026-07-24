from backend.apps.policy.serializers import ConditionSLZ


def test_condition_accepts_extended_attribute_dsl():
    slz = ConditionSLZ(
        data={
            "id": "condition-1",
            "instances": [],
            "attribute_aggregation": "OR",
            "attributes": [
                {
                    "id": "title",
                    "name": "Title",
                    "type": "STRING",
                    "operator": "contains",
                    "values": [{"id": "urgent", "name": "urgent"}],
                }
            ],
        }
    )

    assert slz.is_valid(), slz.errors
    assert slz.validated_data["attribute_aggregation"] == "OR"
    assert slz.validated_data["attributes"][0]["operator"] == "contains"


def test_condition_defaults_legacy_attribute_dsl():
    slz = ConditionSLZ(
        data={
            "id": "condition-1",
            "instances": [],
            "attributes": [
                {"id": "service", "name": "Service", "values": [{"id": "network", "name": "Network"}]}
            ],
        }
    )

    assert slz.is_valid(), slz.errors
    assert slz.validated_data["attribute_aggregation"] == "AND"
    assert slz.validated_data["attributes"][0]["type"] == "STRING"
    assert slz.validated_data["attributes"][0]["operator"] == "eq"
