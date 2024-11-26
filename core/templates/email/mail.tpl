{% extends "mail_templated/base.tpl" %}

{% block subject %}
Account activation
{% endblock %}

{% block html %}
<a href="http://127.0.0.1:8000/accounts/api/v1/verifyaccount/confirm/{{token}}"> Activate your account </a>
{% endblock %}