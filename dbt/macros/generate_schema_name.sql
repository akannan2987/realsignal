{#
  macros/generate_schema_name.sql: put each layer in a schema with its own name.

  dbt's default joins the target schema and the custom one ("main_staging").
  This version uses the custom name as it is, so the warehouse has the schemas
  raw, staging, intermediate, marts and reference, and a query reads
  "select * from marts.dim_strain". Models without a custom schema stay in
  the target schema (main).
#}
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- if custom_schema_name is none -%}
        {{ target.schema }}
    {%- else -%}
        {{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
