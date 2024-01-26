Add queue control to wazo-calld and publish to Wazo websocket Queue log from wazo-call-logd.

Installation
------------

    wazo-plugind-cli -c "install git https://github.com/sboily/wazo-calld-queue"

Use
---

Check the API in your wazo in calld section in http://wazo_ip/api

Optional configuration
----------------------

If you want to use agent events within Nodered, you need to add a new file `/etc/wazo-calld/conf.d/01-queue.yml`:

```
calld_queue_tenant_uuid: MY_TENANT_UUID
```
