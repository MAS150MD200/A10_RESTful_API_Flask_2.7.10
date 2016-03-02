Here is first version of A10 SLB RESTful API:

|*API call*|*HTTP method*|*Authentication*|*Description*|*Response*|
|/a10-slb/api/v1.0/<slb>/service-groups|GET|no|Get all service groups with members on load balancer|*curl -X GET "http://127.0.0.1:5000/a10-slb/api/v1.0/ax3400/service-groups"*
"us0101aar-vip001-tcp-8080": [
    {
      "port": 8080,
      "priority": 1,
      "server": "us0101aar002",
      "stats_data": 1,
      "status": 1,
      "template": "default"
    },
    {
      "port": 8080,
      "priority": 1,
      "server": "us0101aar001",
      "stats_data": 1,
      "status": 1,
      "template": "default"
    }
  ],
  "us0101aard-vip001-tcp-3306": [
    {
      "port": 3306,
      "priority": 1,
      "server": "us0101aard006",
      "stats_data": 1,
      "status": 1,
      "template": "default"
    },
|
|/a10-slb/api/v1.0/<slb>/service-groups/<service_group_name>|GET|no|Get configuration of the current service group name *with status for each server in group*. May take some time on big cluster.|*curl -X GET "http://127.0.0.1:5000/a10-slb/api/v1.0/ax3400/service-groups/us0101astd-vip001-tcp-443"*
{
  "us0101astd-vip001-tcp-443": [
    {
      "member status": 1,
      "port": 443,
      "server": "us0101astd008",
      "server_status": 0
    },
    {
      "member status": 1,
      "port": 443,
      "server": "us0101astd007",
      "server_status": 0
    },
    {
      "member status": 1,
      "port": 443,
      "server": "us0101astd006",
      "server_status": 1
    },
    {
      "member status": 1,
      "port": 443,
      "server": "us0101astd010",
      "server_status": 0
    },
    {
      "member status": 1,
      "port": 443,
      "server": "us0101astd009",
      "server_status": 0
    },
    {
      "member status": 1,
      "port": 443,
      "server": "us0101astd005",
      "server_status": 1
    },
    {
      "member status": 1,
      "port": 443,
      "server": "us0101astd004",
      "server_status": 1
    },
    {
      "member status": 1,
      "port": 443,
      "server": "us0101astd003",
      "server_status": 1
    },
    {
      "member status": 1,
      "port": 443,
      "server": "us0101astd002",
      "server_status": 1
    },
    {
      "member status": 1,
      "port": 443,
      "server": "us0101astd001",
      "server_status": 1
    }
  ]
}
|
|/a10-slb/api/v1.0/<slb>/service-groups/<service_group_name>/<server_name>:<server_port>|DELETE|yes|Delete member from service group||
|/a10-slb/api/v1.0/<slb>/service-groups/<service_group_name>/<server_name>:<server_port>|POST|yes|Create new member in service group||
|/a10-slb/api/v1.0/<slb>/server/<server_name>|GET|no|Get configuration of server|*curl -X GET "http://127.0.0.1:5000/a10-slb/api/v1.0/ax3400/server/us0101adc001"*
\{
  "server": \{
    "conn_limit" : 8000000,
    "conn_limit_log": 1,
    "conn_resume": 0,
    "extended_stats": 0,
    "gslb_external_address": "0.0.0.0",
    "health_monitor": "(default)",
    "host": "10.101.11.114",
    "name": "us0101adc001",
    "port_list": [
      {
        "conn_limit": 8000000,
        "conn_limit_log": 1,
        "conn_resume": 0,
        "extended_stats": 0,
        "health_monitor": "hm-http-head",
        "no_ssl": 0,
        "port_num": 8080,
        "protocol": 2,
        "stats_data": 1,
        "status": 1,
        "template": "default",
        "weight": 1
      }
    ],
    "slow_start": 0,
    "spoofing_cache": 0,
    "stats_data": 1,
    "status": 1,
    "template": "default",
    "weight": 1
  }
}
|
|/a10-slb/api/v1.0/<slb>/server/<server_name>/status|GET|no|Get status of current server(Enable/Disable)|*curl -X GET "http://127.0.0.1:5000/a10-slb/api/v1.0/ax3400/server/us0101adc001/status"*
{
  "status": 1
}|
|/a10-slb/api/v1.0/<slb>/server/<server_name>/status/<int:new_status>|PUT|yes|Set status for current server:
(0 - disable / 1 - enable)|*curl -X PUT -u user:pass "http://127.0.0.1:5000/a10-slb/api/v1.0/ax3400/server/us0101astd008/status/0"*
\{"response": \{"status": "OK"}}|