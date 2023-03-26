import re

from rest_framework import serializers


def validate_username(value):
    regex = r'^[\w.@+-]+$'
    if re.match(regex, value) is None:
        raise serializers.ValidationError(
            'Вы использовали запрещенные символы'
        )
    if value.lower() == 'me':
        raise serializers.ValidationError(
            "Username 'me' использовать нельзя"
        )
    return value
