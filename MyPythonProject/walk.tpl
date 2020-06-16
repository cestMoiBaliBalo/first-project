       {{ root }} content.
{% for separator, title, iter_obj in content %}


     {{ separator }}
     {{ title }}
     {{ separator }}
    {% for item in iter_obj %}
{{ loop.index|rjustify() }}. {{ item }}
    {% endfor %}
{% endfor %}
