#Short introduction about pysnmptools

# Introduction #

This page is a short introduction about pysnmptools.


# Details #
Some packages are needs in order to use pysnmptools :
  * sys
  * cmd
  * pysnmp 2x (http://pysnmp.sourceforge.net/)


Download via http or svn your copy of pysnmptools. After extract it, just launch like this :
python main.py

The first step is to configure a snmp agent. On the cli, type :

```
snmptools >snmpagent ip_of_agent its_community
```

To view the actual configuration, type :
```
snmptools >print_agent
```

After this, you could type in the console help in order to show the functions which are implemented.