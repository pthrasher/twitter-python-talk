def simple_tweet(data):
    return {
        'username': data.get('username', ''),
        'name': data.get('name', ''),
        'body': data.get('body', ''),
    }


def geo_blip(data):
    return {
        'lat': data.get('lat', 0),
        'lon': data.get('lon', 0),
    }
