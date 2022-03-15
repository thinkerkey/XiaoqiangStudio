sudo apt-get install redis-server
pip install redis
git clone git@gitlab.uisee.ai:cxq10490/MsgManager.git

```python
from MsgManager.manager import NodeRegister

for i in range(1000):
    node = NodeRegister()
    node.pub("test", {"data": 1.23})
    node.wait_next_pub()