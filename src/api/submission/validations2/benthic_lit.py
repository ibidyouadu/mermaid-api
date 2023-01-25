from .base import (
    FIELD_LEVEL,
    LIST_VALIDATION_TYPE,
    RECORD_LEVEL,
    ROW_LEVEL,
    VALUE_VALIDATION_TYPE,
    Validation,
)
from .validators import (
    AllAttributesSameCategoryValidator,
    BenthicLITObservationTotalLengthValidator,
    DepthValidator,
    DrySubmitValidator,
    LenSurveyedValidator,
    ListRequiredValidator,
    ManagementRuleValidator,
    ObservationCountValidator,
    RegionValidator,
    RequiredValidator,
    SampleDateValidator,
    SampleTimeValidator,
    UniqueBenthicTransectValidator,
    UniqueSiteValidator,
    UniqueManagementValidator,
)
from ...models import BenthicAttribute


benthic_lit_validations = [
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
        validator=SampleDateValidator(
            sample_date_path="data.sample_event.sample_date",
            sample_time_path="data.benthic_transect.sample_time",
            site_path="data.sample_event.site",
        ),
        paths=["data.sample_event.sample_date"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=SampleTimeValidator(
            sample_time_path="data.benthic_transect.sample_time",
        ),
        paths=["data.benthic_transect.sample_time"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
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
        validator=RequiredValidator(
            path="data.benthic_transect.number",
        ),
        paths=["data.benthic_transect.number"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.benthic_transect.depth",
        ),
        paths=["data.benthic_transect.depth"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=DepthValidator(depth_path="data.benthic_transect.depth"),
        paths=["data.benthic_transect.depth"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=LenSurveyedValidator(
            len_surveyed_path="data.benthic_transect.len_surveyed",
        ),
        paths=["data.benthic_transect.len_surveyed"],
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
        validator=UniqueBenthicTransectValidator(
            protocol_path="data.protocol",
            site_path="data.sample_event.site",
            management_path="data.sample_event.management",
            sample_date_path="data.sample_event.sample_date",
            number_path="data.benthic_transect.number",
            label_path="data.benthic_transect.label",
            depth_path="data.benthic_transect.depth",
            relative_depth_path="data.benthic_transect.relative_depth",
            observers_path="data.observers",
        ),
        paths=[
            "data.sample_event.site",
            "data.sample_event.management",
            "data.sample_event.sample_date",
            "data.benthic_transect.number",
            "data.benthic_transect.label",
            "data.benthic_transect.depth",
            "data.benthic_transect.relative_depth",
        ],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=ObservationCountValidator(observations_path="data.obs_benthic_lits"),
        paths=["data.obs_benthic_lits"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=ListRequiredValidator(
            list_path="data.obs_benthic_lits",
            path="attribute",
            name_prefix="attribute",
            unique_identifier_label="observation_id",
        ),
        paths=["data.obs_benthic_lits"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
    Validation(
        validator=ListRequiredValidator(
            list_path="data.obs_benthic_lits",
            path="length",
            name_prefix="length",
            unique_identifier_label="observation_id",
        ),
        paths=["data.obs_benthic_lits"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
    Validation(
        validator=BenthicLITObservationTotalLengthValidator(
            len_surveyed_path="data.benthic_transect.len_surveyed",
            obs_benthiclits_path="data.obs_benthic_lits",
        ),
        paths=["data.obs_benthic_pits"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RegionValidator(
            attribute_model_class=BenthicAttribute,
            site_path="data.sample_event.site",
            observations_path="data.obs_benthic_lits",
            observation_attribute_path="attribute",
        ),
        paths=["data.obs_benthic_lits"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
    Validation(
        validator=AllAttributesSameCategoryValidator(
            obs_benthic_path="data.obs_benthic_lits"
        ),
        paths=["data.obs_benthic_lits"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=DrySubmitValidator(),
        paths=["__all__"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
        requires_instance=True,
    ),
]
