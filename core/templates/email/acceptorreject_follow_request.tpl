{% extends "mail_templated/base.tpl" %}

{% block subject %}
Follow Request
{% endblock %}

{% block html %}
<h2> Hello {{to_user}} </h2>
<h3> {{from_user}} has requested to follow you.
<a href="http://127.0.0.1:8000/accounts/api/v1/profile/acceptrejectfollowrequest/{{accept_token}}"> Accept </a>

<a href="http://127.0.0.1:8000/accounts/api/v1/profile/acceptrejectfollowrequest/{{reject_token}}"> Reject </a>
{% endblock %}