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
    DepthValidator,
    DuplicateValidator,
    LenSurveyedValidator,
    ListRequiredValidator,
    ManagementRuleValidator,
    ObservationCountValidator,
    # QuadratCollectionValidator,
    PointsPerQuadratValidator,
    QuadratCountValidator,
    QuadratNumberSequenceValidator,
    QuadratSizeValidator,
    RegionValidator,
    RequiredValidator,
    SampleDateValidator,
    SampleTimeValidator,
    DrySubmitValidator,
    UniqueManagementValidator,
    UniqueSiteValidator,
    # UniqueQuadratTransectValidator,
)
from ...models import BenthicAttribute

benthic_photo_quadrat_transect_validations = [
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
            path="data.quadrat_transect.number",
        ),
        paths=["data.quadrat_transect.number"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.sample_event.quadrat_size",
        ),
        paths=["data.sample_event.quadrat_size"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.quadrat_transect.depth",
        ),
        paths=["data.quadrat_transect.depth"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.quadrat_transect.num_quadrats",
        ),
        paths=["data.quadrat_transect.num_quadrats"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.quadrat_transect.num_points_per_quadrat",
        ),
        paths=["data.quadrat_transect.num_points_per_quadrat"],
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
        validator=ListRequiredValidator(
            list_path="data.obs_benthic_photo_quadrats",
            path="quadrat_number",
            name_prefix="quadrat_number",
            unique_identifier_label="observation_id",
        ),
        paths=["data.obs_benthic_photo_quadrats"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
    Validation(
        validator=ListRequiredValidator(
            list_path="data.obs_benthic_photo_quadrats",
            path="attribute",
            name_prefix="attribute",
            unique_identifier_label="observation_id",
        ),
        paths=["data.obs_benthic_photo_quadrats"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
    Validation(
        validator=ListRequiredValidator(
            list_path="data.obs_benthic_photo_quadrats",
            path="num_points",
            name_prefix="num_points",
            unique_identifier_label="observation_id",
        ),
        paths=["data.obs_benthic_photo_quadrats"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
    Validation(
        validator=SampleDateValidator(
            sample_date_path="data.sample_event.sample_date",
            sample_time_path="data.quadrat_transect.sample_time",
            site_path="data.sample_event.site",
        ),
        paths=["data.sample_event.sample_date"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=SampleTimeValidator(
            sample_time_path="data.quadrat_transect.sample_time",
        ),
        paths=["data.fishbelt_transect.sample_time"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=LenSurveyedValidator(
            len_surveyed_path="data.quadrat_transect.len_surveyed",
        ),
        paths=["data.quadrat_transect.len_surveyed"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RegionValidator(
            attribute_model_class=BenthicAttribute,
            site_path="data.sample_event.site",
            observations_path="data.obs_benthic_photo_quadrats",
            observation_attribute_path="attribute"
        ),
        paths=["data.obs_benthic_photo_quadrats"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
    Validation(
        validator=ObservationCountValidator(observations_path="data.obs_benthic_photo_quadrats"),
        paths=["data.obs_benthic_photo_quadrats"],
        validation_level=RECORD_LEVEL,
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
        validator=DepthValidator(depth_path="data.quadrat_transect.depth"),
        paths=["data.quadrat_transect.depth"],
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
            quadrat_size_path="data.quadrat_transect.quadrat_size"
        ),
        paths=["data.quadrat_transect.quadrat_size"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=DuplicateValidator(
            list_path="data.obs_benthic_photo_quadrats",
            key_paths=["quadrat_number", "attribute", "growth_form"],
        ),
        paths=["data.obs_benthic_photo_quadrats"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=AllEqualValidator(
            path="data.obs_benthic_photo_quadrats",
            ignore_keys=["id"]
        ),
        paths=["data.obs_belt_fishes"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=PointsPerQuadratValidator(
            num_points_per_quadrat_path="data.quadrat_transect.num_points_per_quadrat",
            obs_benthic_photo_quadrats_path="data.obs_benthic_photo_quadrats",
            observation_quadrat_number_path="quadrat_number",
            observation_num_points_path="num_points",
        ),
        paths=["data.obs_benthic_photo_quadrats"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=QuadratCountValidator(
            num_quadrats_path="data.quadrat_transect.num_quadrats",
            obs_benthic_photo_quadrats_path="data.obs_benthic_photo_quadrats",
            observation_quadrat_number_path="quadrat_number",
        ),
        paths=["data.obs_benthic_photo_quadrats"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=QuadratNumberSequenceValidator(
            num_quadrats_path="data.quadrat_transect.num_quadrats",
            obs_benthic_photo_quadrats_path="data.obs_benthic_photo_quadrats",
            observation_quadrat_number_path="quadrat_number",
        ),
        paths=["data.obs_benthic_photo_quadrats"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
]
