"""Basic connection example.
"""

import redis

r = redis.Redis(
    host='redis-13116.c99.us-east-1-4.ec2.redns.redis-cloud.com',
    port=13116,
    decode_responses=True,
    username="bnguye65@gmu.edu",
    password="@Slatt123",
)

success = r.set('foo', 'bar')
# True

result = r.get('foo')
print(result)
# >>> bar