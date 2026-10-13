{#
  macros/strain_id.sql: one spelling for every strain name.

  The sources write the same strain in more than one way: Leaf15 in most
  tables, the bare number 15 in the Strain_ID column of Vogel et al. 2021
  (Supplementary Table 12). This macro turns any of them into Leaf15:

    15, 15.0          -> Leaf15   (a bare number is a Leaf strain in these sources)
    leaf15, Leaf 15   -> Leaf15   (any capitalisation, a space or _ or - between)
    Leaf15            -> Leaf15
    Fr1               -> Fr1      (anything else is kept as written, trimmed)

  Every staging model that holds a strain uses it, so the rule lives in one
  place. Used like this:  {{ strain_id('"Strain"') }} as strain_id
#}
{% macro strain_id(column) -%}
    {%- set text = "trim(cast(" ~ column ~ " as varchar))" -%}
    case
        when regexp_full_match({{ text }}, '[0-9]+(\.0)?')
            then 'Leaf' || regexp_replace({{ text }}, '\.0$', '')
        when regexp_full_match({{ text }}, '(?i)leaf[ _-]?[0-9]+')
            then 'Leaf' || regexp_extract({{ text }}, '[0-9]+')
        else {{ text }}
    end
{%- endmacro %}


{#
  looks_like_strain(column): true for a cell that holds a strain name (letters
  then digits, or a bare number), false for a heading, a Total row or a
  footnote. Staging models use it to keep only the rows that describe strains.
#}
{% macro looks_like_strain(column) -%}
    coalesce(regexp_full_match(trim(cast({{ column }} as varchar)), '[A-Za-z]*[ _-]?[0-9]+(\.0)?'), false)
{%- endmacro %}
