{% for content in contents %}
    {% set separator, target, separator, app_items, app_iter, chg_items, chg_iter = content %}


{{ separator }}
{{ target }}
{{ separator }}

    {% if app_items %}
{{ app_items }}
    {% endif %}

    {%- if app_iter %}
        {% for file in app_iter %}
            {% if loop.first %}
{{ loop.length|format_() }} new file(s) appended since the previous backup.
            {% endif %}
{{ loop.index|format_() }}. {{ file }}
        {% endfor %}
    {% endif %}

    {% if chg_items %}
{{ chg_items }}
    {% endif %}

    {%- if chg_iter %}
        {% for file in chg_iter %}
            {% if loop.first %}
{{ loop.length|format_() }} existing file(s) modified since the previous backup.
            {% endif %}
{{ loop.index|format_() }}. {{ file }}
        {% endfor %}
    {% endif %}


{%- endfor %}
