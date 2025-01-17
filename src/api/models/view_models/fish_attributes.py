import uuid

from django.contrib.gis.db import models
from django.db import connection, transaction
from django.utils.translation import gettext_lazy as _

from ..mermaid import FishAttribute, Project
from ..base import ExtendedManager


class FishAttributeView(FishAttribute):
    sql = """
CREATE OR REPLACE VIEW public.vw_fish_attributes
 AS
WITH fish_grouping_aggregates AS (
    WITH species_groupings AS (
        SELECT DISTINCT fish_species.fishattribute_ptr_id AS species_id,
        r.grouping_id,
        fish_grouping.name,
        biomass_constant_a, biomass_constant_b, biomass_constant_c,
        fish_group_trophic.name AS trophic_group_name,
        fish_group_function.name AS trophic_function_name,
        trophic_level, vulnerability
        FROM fish_species
        LEFT JOIN fish_group_trophic ON (fish_species.trophic_group_id = fish_group_trophic.id)
        LEFT JOIN fish_group_function ON (fish_species.functional_group_id = fish_group_function.id)
        INNER JOIN fish_genus ON (fish_species.genus_id = fish_genus.fishattribute_ptr_id) 
        INNER JOIN api_fishgroupingrelationship r ON (
            fish_species.fishattribute_ptr_id = r.attribute_id
            OR fish_species.genus_id = r.attribute_id
            OR fish_genus.family_id = r.attribute_id
        )
        INNER JOIN fish_species_regions sr ON (fish_species.fishattribute_ptr_id = sr.fishspecies_id) 
        INNER JOIN fish_grouping ON (r.grouping_id = fish_grouping.fishattribute_ptr_id)
        WHERE sr.region_id IN (
            SELECT region.id 
            FROM region 
            INNER JOIN fish_grouping_regions sr2 ON (region.id = sr2.region_id) 
            WHERE sr2.fishgrouping_id = fish_grouping.fishattribute_ptr_id
        )
    )
    SELECT species_groupings.grouping_id,
    species_groupings.name,
    AVG(biomass_constant_a) AS biomass_constant_a,
    AVG(biomass_constant_b) AS biomass_constant_b,
    AVG(biomass_constant_c) AS biomass_constant_c,
    tg_groupings.trophic_group_name,
    fg_groupings.trophic_function_name,
    AVG(trophic_level) AS trophic_level,
    AVG(vulnerability) AS vulnerability
    FROM species_groupings
    LEFT JOIN (
        SELECT grouping_id, trophic_group_name, cnt
        FROM (
            SELECT grouping_id, trophic_group_name, cnt,
            RANK() OVER (PARTITION BY grouping_id ORDER BY cnt DESC) AS rnk
            FROM (
                SELECT grouping_id, trophic_group_name, COUNT(*) AS cnt
                FROM species_groupings
                GROUP BY grouping_id, trophic_group_name
            ) AS tgg
        ) AS tg_groupings_ranked
        WHERE tg_groupings_ranked.rnk = 1
    ) AS tg_groupings ON (species_groupings.grouping_id = tg_groupings.grouping_id)
    LEFT JOIN (
        SELECT grouping_id, trophic_function_name, cnt
        FROM (
            SELECT grouping_id, trophic_function_name, cnt,
            RANK() OVER (PARTITION BY grouping_id ORDER BY cnt DESC) AS rnk
            FROM (
                SELECT grouping_id, trophic_function_name, COUNT(*) AS cnt
                FROM species_groupings
                GROUP BY grouping_id, trophic_function_name
            ) AS tfg
        ) AS fg_groupings_ranked
        WHERE fg_groupings_ranked.rnk = 1
    ) AS fg_groupings ON (species_groupings.grouping_id = fg_groupings.grouping_id)
    GROUP BY species_groupings.grouping_id, species_groupings.name, tg_groupings.trophic_group_name, 
    fg_groupings.trophic_function_name
)

SELECT fish_attribute.id,
fish_attribute.id AS fishattribute_ptr_id,
fish_attribute.created_on,
fish_attribute.updated_on,
fish_attribute.updated_by_id,
fish_attribute.status,
CASE
    WHEN fish_species.fishattribute_ptr_id IS NOT NULL THEN species_genus_family.fishattribute_ptr_id
    WHEN fish_genus.fishattribute_ptr_id IS NOT NULL THEN genus_family.fishattribute_ptr_id
    WHEN fish_family.fishattribute_ptr_id IS NOT NULL THEN fish_family.fishattribute_ptr_id
    ELSE NULL
END AS id_family,
CASE
    WHEN fish_species.name IS NOT NULL THEN species_genus_family.name
    WHEN fish_genus.name IS NOT NULL THEN genus_family.name
    WHEN fish_family.name IS NOT NULL THEN fish_family.name::text
    ELSE NULL::text
END AS name_family,
CASE
    WHEN fish_species.fishattribute_ptr_id IS NOT NULL THEN species_genus.fishattribute_ptr_id
    WHEN fish_genus.fishattribute_ptr_id IS NOT NULL THEN fish_genus.fishattribute_ptr_id
    ELSE NULL
END AS id_genus,
CASE
    WHEN fish_species.name IS NOT NULL THEN species_genus.name
    WHEN fish_genus.name IS NOT NULL THEN fish_genus.name::text
    ELSE NULL::text
END AS name_genus,
CASE
    WHEN fish_species.fishattribute_ptr_id IS NOT NULL THEN fish_species.fishattribute_ptr_id
    ELSE NULL
END AS id_species,
CASE
    WHEN fish_species.name IS NOT NULL THEN concat(species_genus.name, ' ', fish_species.name)
    WHEN fish_genus.name IS NOT NULL THEN fish_genus.name::text
    WHEN fish_family.name IS NOT NULL THEN fish_family.name::text
    WHEN fish_grouping_aggregates.name IS NOT NULL THEN fish_grouping_aggregates.name::text
    ELSE NULL::text
END AS name,
CASE
    WHEN fish_species.biomass_constant_a IS NOT NULL THEN fish_species.biomass_constant_a
    WHEN fish_genus.name IS NOT NULL THEN round(( SELECT avg(fish_species_1.biomass_constant_a) AS avg
       FROM fish_species fish_species_1
      WHERE fish_species_1.genus_id = fish_attribute.id), 6)
    WHEN fish_family.name IS NOT NULL THEN round(( SELECT avg(fish_species_1.biomass_constant_a) AS avg
       FROM fish_species fish_species_1
         JOIN fish_genus fish_genus_1 ON fish_species_1.genus_id = fish_genus_1.fishattribute_ptr_id
      WHERE fish_genus_1.family_id = fish_attribute.id), 6)
    WHEN fish_grouping_aggregates.name IS NOT NULL THEN ROUND(fish_grouping_aggregates.biomass_constant_a, 6)
    ELSE NULL::numeric
END AS biomass_constant_a,

CASE
    WHEN fish_species.biomass_constant_b IS NOT NULL THEN fish_species.biomass_constant_b
    WHEN fish_genus.name IS NOT NULL THEN round(( SELECT avg(fish_species_1.biomass_constant_b) AS avg
       FROM fish_species fish_species_1
      WHERE fish_species_1.genus_id = fish_attribute.id), 6)
    WHEN fish_family.name IS NOT NULL THEN round(( SELECT avg(fish_species_1.biomass_constant_b) AS avg
       FROM fish_species fish_species_1
         JOIN fish_genus fish_genus_1 ON fish_species_1.genus_id = fish_genus_1.fishattribute_ptr_id
      WHERE fish_genus_1.family_id = fish_attribute.id), 6)
    WHEN fish_grouping_aggregates.name IS NOT NULL THEN ROUND(fish_grouping_aggregates.biomass_constant_b, 6)
    ELSE NULL::numeric
END AS biomass_constant_b,

CASE
    WHEN fish_species.biomass_constant_c IS NOT NULL THEN fish_species.biomass_constant_c
    WHEN fish_genus.name IS NOT NULL THEN round(( SELECT avg(fish_species_1.biomass_constant_c) AS avg
       FROM fish_species fish_species_1
      WHERE fish_species_1.genus_id = fish_attribute.id), 6)
    WHEN fish_family.name IS NOT NULL THEN round(( SELECT avg(fish_species_1.biomass_constant_c) AS avg
       FROM fish_species fish_species_1
         JOIN fish_genus fish_genus_1 ON fish_species_1.genus_id = fish_genus_1.fishattribute_ptr_id
      WHERE fish_genus_1.family_id = fish_attribute.id), 6)
    WHEN fish_grouping_aggregates.name IS NOT NULL THEN ROUND(fish_grouping_aggregates.biomass_constant_c, 6)
    ELSE NULL::numeric
END AS biomass_constant_c,

CASE
    WHEN fish_species.trophic_group_id IS NOT NULL THEN fish_group_trophic.name
    WHEN fish_genus.name IS NOT NULL THEN ( SELECT fgt.name
       FROM ( SELECT fish_group_trophic_1.name,
                count(*) AS freq
               FROM fish_species fish_species_1
                 JOIN fish_group_trophic fish_group_trophic_1 ON fish_species_1.trophic_group_id = 
                 fish_group_trophic_1.id
              WHERE fish_species_1.genus_id = fish_attribute.id
              GROUP BY fish_group_trophic_1.name
              ORDER BY (count(*)) DESC, fish_group_trophic_1.name
             LIMIT 1) fgt)
    WHEN fish_family.name IS NOT NULL THEN ( SELECT fft.name
       FROM ( SELECT fish_group_trophic_1.name,
                count(*) AS freq
               FROM fish_species fish_species_1
                 JOIN fish_group_trophic fish_group_trophic_1 ON fish_species_1.trophic_group_id = 
                 fish_group_trophic_1.id
                 JOIN fish_genus fish_genus_1 ON fish_species_1.genus_id = fish_genus_1.fishattribute_ptr_id
              WHERE fish_genus_1.family_id = fish_attribute.id
              GROUP BY fish_group_trophic_1.name
              ORDER BY (count(*)) DESC, fish_group_trophic_1.name
             LIMIT 1) fft)
    WHEN fish_grouping_aggregates.name IS NOT NULL THEN fish_grouping_aggregates.trophic_group_name
    ELSE NULL::character varying
END AS trophic_group,

CASE
    WHEN fish_species.functional_group_id IS NOT NULL THEN fish_group_function.name
    WHEN fish_genus.name IS NOT NULL THEN ( SELECT fgf.name
       FROM ( SELECT fish_group_function_1.name,
                count(*) AS freq
               FROM fish_species fish_species_1
                 JOIN fish_group_function fish_group_function_1 ON fish_species_1.functional_group_id = 
                 fish_group_function_1.id
              WHERE fish_species_1.genus_id = fish_attribute.id
              GROUP BY fish_group_function_1.name
              ORDER BY (count(*)) DESC, fish_group_function_1.name
             LIMIT 1) fgf)
    WHEN fish_family.name IS NOT NULL THEN ( SELECT fff.name
       FROM ( SELECT fish_group_function_1.name,
                count(*) AS freq
               FROM fish_species fish_species_1
                 JOIN fish_group_function fish_group_function_1 ON fish_species_1.functional_group_id = 
                 fish_group_function_1.id
                 JOIN fish_genus fish_genus_1 ON fish_species_1.genus_id = fish_genus_1.fishattribute_ptr_id
              WHERE fish_genus_1.family_id = fish_attribute.id
              GROUP BY fish_group_function_1.name
              ORDER BY (count(*)) DESC, fish_group_function_1.name
             LIMIT 1) fff)
    WHEN fish_grouping_aggregates.name IS NOT NULL THEN fish_grouping_aggregates.trophic_function_name
    ELSE NULL::character varying
END AS functional_group,

CASE
    WHEN fish_species.trophic_level IS NOT NULL THEN fish_species.trophic_level
    WHEN fish_genus.name IS NOT NULL THEN round(( SELECT avg(fish_species_1.trophic_level) AS avg
       FROM fish_species fish_species_1
      WHERE fish_species_1.genus_id = fish_attribute.id), 2)
    WHEN fish_family.name IS NOT NULL THEN round(( SELECT avg(fish_species_1.trophic_level) AS avg
       FROM fish_species fish_species_1
         JOIN fish_genus fish_genus_1 ON fish_species_1.genus_id = fish_genus_1.fishattribute_ptr_id
      WHERE fish_genus_1.family_id = fish_attribute.id), 2)
    WHEN fish_grouping_aggregates.name IS NOT NULL THEN ROUND(fish_grouping_aggregates.trophic_level, 2)
    ELSE NULL::numeric
END AS trophic_level,

CASE
    WHEN fish_species.vulnerability IS NOT NULL THEN fish_species.vulnerability
    WHEN fish_genus.name IS NOT NULL THEN round(( SELECT avg(fish_species_1.vulnerability) AS avg
       FROM fish_species fish_species_1
      WHERE fish_species_1.genus_id = fish_attribute.id), 2)
    WHEN fish_family.name IS NOT NULL THEN round(( SELECT avg(fish_species_1.vulnerability) AS avg
       FROM fish_species fish_species_1
         JOIN fish_genus fish_genus_1 ON fish_species_1.genus_id = fish_genus_1.fishattribute_ptr_id
      WHERE fish_genus_1.family_id = fish_attribute.id), 2)
    WHEN fish_grouping_aggregates.name IS NOT NULL THEN ROUND(fish_grouping_aggregates.vulnerability, 2)
    ELSE NULL::numeric
END AS vulnerability

FROM fish_attribute
LEFT JOIN fish_species ON fish_attribute.id = fish_species.fishattribute_ptr_id
LEFT JOIN fish_genus species_genus ON fish_species.genus_id = species_genus.fishattribute_ptr_id
LEFT JOIN fish_family species_genus_family ON species_genus.family_id = species_genus_family.fishattribute_ptr_id
LEFT JOIN fish_genus ON fish_attribute.id = fish_genus.fishattribute_ptr_id
LEFT JOIN fish_family genus_family ON fish_genus.family_id = genus_family.fishattribute_ptr_id
LEFT JOIN fish_family ON fish_attribute.id = fish_family.fishattribute_ptr_id
LEFT JOIN fish_grouping_aggregates ON (fish_attribute.id = fish_grouping_aggregates.grouping_id)
LEFT JOIN fish_group_trophic ON fish_species.trophic_group_id = fish_group_trophic.id
LEFT JOIN fish_group_function ON fish_species.functional_group_id = fish_group_function.id

ORDER BY (
    CASE
        WHEN fish_species.name IS NOT NULL THEN concat(species_genus.name, ' ', fish_species.name)
        WHEN fish_genus.name IS NOT NULL THEN fish_genus.name::text
        WHEN fish_family.name IS NOT NULL THEN fish_family.name::text
        WHEN fish_grouping_aggregates.name IS NOT NULL THEN fish_grouping_aggregates.name::text
        ELSE NULL::text
    END);
    """

    reverse_sql = """
      DROP VIEW IF EXISTS public.vw_fish_attributes;
    """

    id_family = models.UUIDField()
    id_genus = models.UUIDField()
    id_species = models.UUIDField()
    name_family = models.CharField(max_length=100)
    name_genus = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    biomass_constant_a = models.DecimalField(
        max_digits=7, decimal_places=6, null=True, blank=True
    )
    biomass_constant_b = models.DecimalField(
        max_digits=7, decimal_places=6, null=True, blank=True
    )
    biomass_constant_c = models.DecimalField(
        max_digits=7, decimal_places=6, default=1, null=True, blank=True
    )
    trophic_group = models.CharField(max_length=100, blank=True)
    trophic_level = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True
    )
    functional_group = models.CharField(max_length=100, blank=True)
    vulnerability = models.DecimalField(
        max_digits=4, decimal_places=2, null=True, blank=True
    )

    class Meta:
        db_table = "vw_fish_attributes"
        managed = False
