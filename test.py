from aliyun.ecs import connection

c = connection.EcsConnection('cn-hangzhou')
images = c.describe_images(['m-23cgbmqd5'])
print repr(images[0])
print images[0]
print unicode(images[0]).encode('utf-8')
