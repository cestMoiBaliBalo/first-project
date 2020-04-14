{% for separator, name, separator, main_iter in content %}
#
#
# {{ separator }}
# {{ name }}
# {{ separator }}
    {% for sub_iter in main_iter %}
        {% if not loop.first %}
#
        {% endif %}
        {% for item in sub_iter %}
{{ item|join("`")}}
        {% endfor %}
    {% endfor %}
{% endfor %}
