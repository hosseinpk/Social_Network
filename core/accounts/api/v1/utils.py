from django.core.signing import Signer


def generate_follow_request_token(from_user, action):
    signer = Signer()
    payload = f"{from_user}:{action}"
    return signer.sign(payload)


def decode_follow_request_token(token):

    signer = Signer()
    try:
        payload = signer.unsign(token)
        follow_request_id, action = payload.split(":")
        return int(follow_request_id), action
    except Exception as e:
        return None, None
