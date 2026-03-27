---
sidebar_position: 3
---

# Coordinated Startup

There are two stages in rosia's coordinated startup: initialization and startup.

## Initialization

The initialization stage is orchestrated by the `Application.execute()` method. It sets up all nodes before execution begins. No inter-node communication happens during this stage. The steps are:

1. **Remote Node Setup**: For each node, the executor calls `init_remote()`, which sets up a ZeroMQ PULL endpoint for receiving messages. The endpoint is stored for later use by other nodes.

2. **Output Transport Initialization**: Each node is updated with the endpoints of all downstream nodes. ZeroMQ PUSH sockets are created for each output port connection, so nodes can send messages to their downstream recipients.

3. **Node Instance Initialization**: The user's `__init__` method is called on each node. This is where nodes load models, allocate resources, and set initial DSTAT values. Nodes do not communicate during this step.

4. **Collect Output Port DSTAT**: The coordinator gathers the initial DSTAT (Downstream Safe To Advance To) from all output ports. DSTAT is a promise about future message timestamps that prevents nodes from waiting indefinitely.

5. **Propagate DSTAT Through Graph**: DSTAT values are recursively propagated from source nodes through port connections. Each downstream input port's safe-to-advance-to is updated based on upstream output port DSTATs.

6. **Update Port DSTATs**: The computed DSTAT values are pushed back to all nodes, so each node has the correct initial safe-to-advance-to on all its ports.

## Startup

After initialization completes, all nodes begin execution simultaneously:

1. **Start Logical Time**: The coordinator records the current physical time as the start time, and sends it to all nodes via `execute(start_logical_time)`.

2. **`start()` Call**: If a node defines a `start()` method, it is called before the event loop begins. This is the first user-controlled function called during execution. Nodes can generate initial messages in `start()`. All node logical
   times are set to `Time(0)`.
