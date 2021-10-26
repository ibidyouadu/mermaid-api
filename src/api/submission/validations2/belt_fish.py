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
    BiomassValidator,
    DepthValidator,
    FishCountValidator,
    FishFamilySubsetValidator,
    LenSurveyedValidator,
    ObservationCountValidator,
    RequiredValidator,
    SampleDateValidator,
    SampleTimeValidator,
    DrySubmitValidator,
    TotalFishCountValidator,
    UniqueManagementValidator,
    UniqueSiteValidator,
    UniqueTransectValidator,
)

belt_fish_validations = [
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
            path="data.fishbelt_transect.number",
        ),
        paths=["data.fishbelt_transect.number"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.fishbelt_transect.width",
        ),
        paths=["data.fishbelt_transect.width"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.fishbelt_transect.relative_depth",
        ),
        paths=["data.fishbelt_transect.relative_depth"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.fishbelt_transect.depth",
        ),
        paths=["data.fishbelt_transect.depth"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=RequiredValidator(
            path="data.fishbelt_transect.size_bin",
        ),
        paths=["data.fishbelt_transect.size_bin"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=SampleDateValidator(
            sample_date_path="data.sample_event.sample_date",
            sample_time_path="data.fishbelt_transect.sample_time",
            site_path="data.sample_event.site",
        ),
        paths=["data.sample_event.sample_date"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=SampleTimeValidator(
            sample_time_path="data.fishbelt_transect.sample_time",
        ),
        paths=["data.fishbelt_transect.sample_time"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=LenSurveyedValidator(
            len_surveyed_path="data.fishbelt_transect.len_surveyed",
        ),
        paths=["data.fishbelt_transect.len_surveyed"],
        validation_level=FIELD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=FishFamilySubsetValidator(
            observations_path="data.obs_belt_fishes",
            site_path="data.sample_event.site",
        ),
        paths=["data.obs_belt_fishes"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
    Validation(
        validator=FishCountValidator(
            observations_path="data.obs_belt_fishes", observation_count_path="count"
        ),
        paths=["data.obs_belt_fishes"],
        validation_level=ROW_LEVEL,
        validation_type=LIST_VALIDATION_TYPE,
    ),
    Validation(
        validator=TotalFishCountValidator(
            observations_path="data.obs_belt_fishes", observation_count_path="count"
        ),
        paths=["data.obs_belt_fishes"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=ObservationCountValidator(observations_path="data.obs_belt_fishes"),
        paths=["data.obs_belt_fishes"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=BiomassValidator(
            observations_path="data.obs_belt_fishes",
            len_surveyed_path="data.fishbelt_transect.len_surveyed",
            width_path="data.fishbelt_transect.width",
            obs_fish_attribute_path="fish_attribute",
            obs_count_path="count",
            obs_size_path="size",
        ),
        paths=["data.obs_belt_fishes"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=UniqueTransectValidator(
            protocol="fishbelt",
            label_path="data.fishbelt_transect.label",
            number_path="data.fishbelt_transect.number",
            width_path="data.fishbelt_transect.width",
            relative_depth_path="data.fishbelt_transect.relative_depth",
            site_path="data.sample_event.site",
            management_path="data.sample_event.management",
            sample_date_path="data.sample_event.sample_date",
            depth_path="data.fishbelt_transect.depth",
        ),
        paths=[
            "data.fishbelt_transect.label",
            "data.fishbelt_transect.number",
            "data.fishbelt_transect.width",
            "data.fishbelt_transect.relative_depth",
            "data.fishbelt_transect.depth",
            "data.sample_event.site",
            "data.sample_event.management",
            "data.sample_event.sample_date",
        ],
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
        validator=AllEqualValidator(path="data.obs_belt_fishes"),
        paths=["data.obs_belt_fishes"],
        validation_level=RECORD_LEVEL,
        validation_type=VALUE_VALIDATION_TYPE,
    ),
    Validation(
        validator=DepthValidator(depth_path="data.fishbelt_transect.depth"),
        paths=["data.fishbelt_transect.depth"],
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
]
