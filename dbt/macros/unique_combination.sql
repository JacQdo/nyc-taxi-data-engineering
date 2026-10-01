{% test unique_combination(model, combination_of_columns) %}

SELECT
    {% for column in combination_of_columns %}
        {{ column }}{% if not loop.last %}, {% endif %}
    {% endfor %},
    COUNT(*) AS record_count

FROM {{ model }}

GROUP BY
    {% for column in combination_of_columns %}
        {{ column }}{% if not loop.last %}, {% endif %}
    {% endfor %}

HAVING COUNT(*) > 1

{% endtest %}