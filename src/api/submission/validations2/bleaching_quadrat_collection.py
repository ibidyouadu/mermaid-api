from .base import (
    FIELD_LEVEL,
    LIST_VALIDATION_TYPE,
    RECORD_LEVEL,
    ROW_LEVEL,
    VALUE_VALIDATION_TYPE,
    Validation,
)
from .validators import (
    AllEqualValidator,
    ColonyCountValidator,
    DepthValidator,
    DuplicateValidator,
    ListPositiveIntegerValidator,
    ListRequiredValidator,
    ManagementRuleValidator,
    ObservationCountValidator,
    UniqueQuadratCollectionValidator,
    QuadratSizeValidator,
    RegionValidator,
    RequiredValidator,
    SampleDateValidator,
    SampleTimeValidator,
    DrySubmitValidator,
    UniqueManagementValidator,
    UniqueSiteValidator,
)
from ...models import BenthicAttribute

bleaching_quadrat_collection_validations = [
    Validation(
        validator=RequiredValidator(
            path="data.sample_event.site",
        ),
        paths=["data.sample_event.site"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.sample_event.management",
        ),
        paths=["data.sample_event.management"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.sample_event.sample_date",
        ),
        paths=["data.sample_event.sample_date"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.sample_event.sample_date",
        ),
        paths=["data.sample_event.sample_date"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.quadrat_collection.depth",
        ),
        paths=["data.quadrat_collection.depth"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=SampleTimeValidator(
            sample_time_path="data.quadrat_collection.sample_time",
        ),
        paths=["data.quadrat_collection.sample_time"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=SampleDateValidator(
            sample_date_path="data.sample_event.sample_date",
            sample_time_path="data.quadrat_collection.sample_time",
            site_path="data.sample_event.site",
        ),
        paths=["data.sample_event.sample_date"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RegionValidator(
            attribute_model_class=BenthicAttribute,
            site_path="data.sample_event.site",
            observations_path="data.obs_colonies_bleached",
            observation_attribute_path="attribute",
        ),
        paths=["data.obs_colonies_bleached"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
    Validation(
        validator=UniqueSiteValidator(
            site_path="data.sample_event.site",
        ),
        paths=["data.sample_event.site"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=UniqueManagementValidator(
            management_path="data.sample_event.management",
            site_path="data.sample_event.site",
        ),
        paths=["data.sample_event.management"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=ManagementRuleValidator(
            management_path="data.sample_event.management",
        ),
        paths=["data.sample_event.management"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(path="data.observers"),
        paths=["data.observers"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=DepthValidator(depth_path="data.quadrat_collection.depth"),
        paths=["data.quadrat_collection.depth"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=DrySubmitValidator(),
        paths=["__all__"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
        requires_instance=True,
    ),
    Validation(
        validator=QuadratSizeValidator(
            quadrat_size_path="data.quadrat_collection.quadrat_size"
        ),
        paths=["data.quadrat_collection.quadrat_size"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=UniqueQuadratCollectionValidator(
            protocol_path="data.protocol",
            site_path="data.sample_event.site",
            management_path="data.sample_event.management",
            sample_date_path="data.sample_event.sample_date",
            label_path="data.quadrat_collection.label",
            depth_path="data.quadrat_collection.depth",
            observers_path="data.observers",
        ),
        paths=[
            "data.protocol",
            "data.sample_event.site",
            "data.sample_event.management",
            "data.sample_event.sample_date",
            "data.quadrat_collection.label",
            "data.quadrat_collection.depth",
        ],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=DuplicateValidator(
            list_path="data.obs_quadrat_benthic_percent",
            key_paths=["quadrat_number"],
        ),
        paths=["data.obs_quadrat_benthic_percent"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=ListPositiveIntegerValidator(
            list_path="data.obs_quadrat_benthic_percent",
            key_path="quadrat_number",
        ),
        paths=["data.obs_quadrat_benthic_percent"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
    Validation(
        validator=DuplicateValidator(
            list_path="data.obs_colonies_bleached",
            key_paths=["attribute", "growth_form"],
        ),
        paths=["data.obs_colonies_bleached"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=ObservationCountValidator(
            observations_path="data.obs_quadrat_benthic_percent"
        ),
        paths=["data.obs_quadrat_benthic_percent"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=ObservationCountValidator(
            observations_path="data.obs_colonies_bleached"
        ),
        paths=["data.obs_colonies_bleached"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=ColonyCountValidator(
            obs_colonies_bleached_path="data.obs_colonies_bleached",
            observation_count_normal_path="count_normal",
            observation_count_pale_path="count_pale",
            observation_count_20_path="count_20",
            observation_count_50_path="count_50",
            observation_count_80_path="count_80",
            observation_count_100_path="count_100",
            observation_count_dead_path="count_dead",
        ),
        paths=["data.obs_colonies_bleached"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=AllEqualValidator(
            path="data.obs_quadrat_benthic_percent", ignore_keys=["id"]
        ),
        paths=["data.obs_quadrat_benthic_percent"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=AllEqualValidator(
            path="data.obs_colonies_bleached", ignore_keys=["id"]
        ),
        paths=["data.obs_colonies_bleached"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=ListRequiredValidator(
            list_path="data.obs_colonies_bleached",
            path="attribute",
            name_prefix="attribute",
            unique_identifier_label="observation_id",
        ),
        paths=["data.obs_colonies_bleached"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
    Validation(
        validator=ListRequiredValidator(
            list_path="data.obs_quadrat_benthic_percent",
            path="quadrat_number",
            name_prefix="quadrat_number",
            unique_identifier_label="observation_id",
        ),
        paths=["data.obs_quadrat_benthic_percent"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
]
