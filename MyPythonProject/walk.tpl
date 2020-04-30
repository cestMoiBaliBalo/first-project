       {{ root }} content.
{% for separator1, title, separator2, iter_obj in content %}


     {{ separator1 }}
     {{ title }}
     {{ separator2 }}
    {% for item in iter_obj %}
{{ loop.index|rjustify() }}. {{ item }}
    {% endfor %}
{% endfor %}
