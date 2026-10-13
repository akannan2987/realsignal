-- stg_collection__strains: the strain collection as the Layer 1 archive
-- describes it (dataAtLSPHERE.txt): taxonomy, and where each genome was
-- published ("yes" means in Bai et al. 2015). The file lists the 224 strains
-- of the At-LSPHERE and some more; its ExtendedAtSPHERE column says which
-- group a further strain belongs to (NA for the 224).

select
    {{ strain_id('"Strain_ID"') }}                          as strain_id,
    trim("Phylum")                                          as phylum,
    trim("Class")                                           as taxonomic_class,
    trim("Family")                                          as family,
    trim("Genus")                                           as genus,
    trim("Genomes_published_Bai2015")                       as genome_publication,
    trim("Genomes_published_Bai2015") = 'yes'               as genome_in_bai2015,
    case when trim("ExtendedAtSPHERE") = 'NA' then 'At-LSPHERE'
         else trim("ExtendedAtSPHERE") end                  as collection_group,
    _row                                                    as source_row
from {{ source('raw', 'collection_strains') }}
