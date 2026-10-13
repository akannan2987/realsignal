{#
  tests/generic/accepted_range.sql: a test you can attach to any column.

  dbt ships four generic tests (unique, not_null, accepted_values and
  relationships). This adds a fifth: every value lies between min_value and
  max_value (either may be left out). Like every dbt test, it's a query that
  returns the rows breaking the rule, and the test passes when it returns none.
  Used in the .yml files like this:

      data_tests:
        - accepted_range:
            arguments:
              min_value: 20
              max_value: 80
#}
{% test accepted_range(model, column_name, min_value=none, max_value=none) %}

select {{ column_name }} as value_out_of_range
from {{ model }}
where {{ column_name }} is not null
  and (
      {% if min_value is not none %} {{ column_name }} < {{ min_value }} {% else %} false {% endif %}
      or
      {% if max_value is not none %} {{ column_name }} > {{ max_value }} {% else %} false {% endif %}
  )

{% endtest %}
