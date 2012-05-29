def body(tweet, clean_obj):
    """
    Simpy grabs the tweet body.
    """
    tweet_body = tweet.get('text')
    if tweet_body:
        clean_obj.update({
            "body": tweet_body,
        })
    return clean_obj

def user_data(tweet, clean_obj):
    """
    Simply grabs username, and name.
    """
    user = tweet.get('user', {})
    username = user.get('screen_name')
    name = user.get('name')

    if username and name:
        clean_obj.update({
            "username": username,
            "name": name,
        })

    return clean_obj



def lat_lon(tweet, clean_obj):
    """
    Searches for the lat and lon and returns it.
    """
    geo = tweet.get('geo')
    if geo:
        geo_type = geo.get('type')
        if geo_type.lower() != 'point':
            return None

        lat, lon = geo.get('coordinates')
    else:
        place = tweet.get('place')
        if not place:
            return None

        bounding_box = place.get('bounding_box')
        if not bounding_box:
            return None

        coords = bounding_box.get('coordinates')
        if not coords:
            return None

        lat, lon = coords[0][0]

    if lat and lon:
        clean_obj.update({
            "lat": lat,
            "lon": lon,
        })

    return clean_obj
