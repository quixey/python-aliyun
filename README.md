python-aliyun
=============

Python API wrapper for the Aliyun cloud. This project is starting to use [git-flow](http://nvie.com/posts/a-successful-git-branching-model/).

Installing
----------

You should build a [virtualenv][virtualenv] to contain this project's Python dependencies. The Makefile will create one for you and put it in `~/.virtualenvs/python-aliyun`.
```
git clone git@github.com:quixey/python-aliyun.git
cd python-aliyun
sudo pip install virtualenv
make virtualenv
source ~/.virtualenvs/python-aliyun/bin/activate
```

Aliyun API
----------

The Aliyun API is well-documented at [dev.aliyun.com](http://dev.aliyun.com/thread.php?spm=0.0.0.0.MqTmNj&fid=8).
Each service's API is very similar: There are regions, actions, and each action has many parameters.
It is an OAuth2 API, so you need to have an ID and a secret. You can get these from the Aliyun management console.

Authentication
--------------

You will need security credentials for your Aliyun account. You can view and
create them in the [Aliyun management console](http://console.aliyun.com). This
library will look for credentials in the following places:

 1. Environment variables `ALI_ACCESS_KEY_ID` and `ALI_SECRET_ACCESS_KEY`
 1. An ini-style configuration file at ~/.aliyun.cfg with contents like:
```
[default]
access_key_id=xxxxxxxxxxxxx
secret_access_key=xxxxxxxxxxxxxxxxxxxxxxx
```
 3. A system-wide version of that file at /etc/aliyun.cfg with similar contents.

We recommend using environment variables whenever possible.

Main Interfaces
---------------

The main components of python-aliyun are ECS and SLB. Other Aliyun products will
be added as API support develops. Within each Aliyun product, we tried to
implement every API Action variation available. We used a boto-style design
where most API interaction is done with a connection object which marshalls
Python objects and API representations.

ECS
---

You can create a new ECS connection and interact with ECS like this:
```python
import aliyun.ecs.connection
conn = aliyun.ecs.connection.EcsConnection('cn-hangzhou')
print conn.get_all_instance_ids()
```

This module makes use of one as-yet undocumented API Action: ModifyInstanceSpec.

This module does not implement the following API Action: ResetDisk.

SLB
---

Similarly for SLB, get the connection object like this:
```python
import aliyun.slb.connection
conn = aliyun.slb.connection.SlbConnection('cn-hangzhou')
print conn.get_all_load_balancer_ids()
```

ali command
-----------

The ali commandline tool is mostly used for debugging the Aliyun API interactions.
It accepts arbitrary Key=Value pairs and passes them on to the API after wrapping them.

```shell
ali --region cn-hangzhou ecs Action=DescribeRegions
ali --region cn-hangzhou slb Action=DescribeLoadBalancers
```

Copyright Notice
---------
```
Copyright 2014, Quixey Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

     http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
```

[virtualenv]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
