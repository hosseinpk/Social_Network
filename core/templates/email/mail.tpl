{% extends "mail_templated/base.tpl" %}

{% block subject %}
Account activation
{% endblock %}

{% block html %}
http://127.0.0.1:8000/accounts/api/v1/verifiedaccount/{{token}}
{% endblock %}