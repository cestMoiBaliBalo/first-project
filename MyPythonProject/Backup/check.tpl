{% for content in contents %}
    {% set separator, target, new_items, new_iter, exi_items, exi_iter = content %}


{{ separator }}
{{ target }}
{{ separator }}

    {% if new_items %}
{{ new_items }}
    {% endif %}

    {%- if new_iter %}
        {% for file in new_iter %}
            {% if loop.first %}
{{ loop.length|format_() }} new file(s) appended since the previous backup.
            {% endif %}
{{ loop.index|format_() }}. {{ file }}
        {% endfor %}
    {% endif %}

    {% if exi_items %}
{{ exi_items }}
    {% endif %}

    {%- if exi_iter %}
        {% for file in exi_iter %}
            {% if loop.first %}
{{ loop.length|format_() }} existing file(s) modified since the previous backup.
            {% endif %}
{{ loop.index|format_() }}. {{ file }}
        {% endfor %}
    {% endif %}


{%- endfor %}
