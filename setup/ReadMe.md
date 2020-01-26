# Setup Types:

## 1. Standalone
Sensordata is gathered, processed and stored on the same device.

+ Simple
+ No network(ing) required
- Only for singe agent deployments
- Backup of the agent would be necessary if data loss isn't acceptable
- Lifetime of the agent hardware may be abbreviated
0 Agents are most often exposed to high humidity and heat

## 2. Agent-Server Setup
Sensordata is gathered on the agent.
Sensordata and logs are stored on the server.
The agent fetches data from the server database for the action processing.

+ Multiple agents supported
+ Data can be stored in a better physical environment than the agents
+ Data can be stored on better hardware
+ Agents can easily be added or removed
+ Server can be secured in a seperated network
+ Safer/Cleaner setup-type - agents can fail without leading to data loss
- Komplexer than the standalone setup
- More hardware needed
- Network connection between agent and server is required
- Backup of the server would be necessary if data loss isn't acceptable