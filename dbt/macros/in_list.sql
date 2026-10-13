{#
  macros/in_list.sql: turn a list from dbt_project.yml into SQL.

  var('test_rounds') is a list, ["Exp3"]. SQL wants ('Exp3') after IN, so
  this writes each value in single quotes, separated by commas:

    round_id in {{ in_list(var('test_rounds')) }}   ->   round_id in ('Exp3')
#}
{% macro in_list(values) -%}
    ({%- for value in values -%}'{{ value }}'{%- if not loop.last -%}, {% endif -%}{%- endfor -%})
{%- endmacro %}
