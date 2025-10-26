Simple debugging
The easiest way to run a debugger in a module, either local or remote, is to use madbg. Add import madbg; madbg.set_trace() in the module code on the control node at the desired break point. To connect to the debugger, run madbg connect. See the madbg documentation for how to specify the host and port. If connecting to a remote node, make sure to use a port that is allowed by any firewall between the control node and the remote node.

This technique should work with any remote debugger, but we do not guarantee any particular remote debugging tool will work.

The q library is another very useful debugging tool.

Since print() statements do not work inside modules, raising an exception is a good approach if you just want to see some specific data. Put raise Exception(some_value) somewhere in the module and run it normally. Ansible will handle this exception, pass the message back to the control node, and display it.