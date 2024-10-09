# APScavenge

APScavenge is a tool that scavenges a delimited area for data extraction. In this case, the data nature concerns the Wi-Fi connection security of users at enterprise networks, a problem disregarded by institutions that can threaten user credentials and associated account services. This problem is related to the cybersecurity threats in the domain of wireless networks, more specifically to Evil Twin attacks. The Evil Twin is an attack where a rogue Access Point is installed to emit the same Service Set Identifier as the real network to trick devices into establishing a connection.

APScavenge comprises two main modules that are responsible for creating a centralized infrastructure architecture. APServer is the name of the central server module that stores gathered data and provides dashboard views for staff members. The received data is sent by the APAgent module, corresponding to various instances scattered through a handful of independent hardware agents. These mediums run Evil Twin attacks to verify users' susceptibilities to this type of attack.

## Notes

It is recommended to ensure all files are in Unix format, the dos2unix package can be used:

```
sudo apt-get install dos2unix
```

Converting files within a root directory to Unix format can be done with the following command:

```
find . -type f -exec dos2unix {} \;
```

## Modules certificates

The APAgent module communicates with the APServer module in order to deliver information on gathered data and to allow infrastructure flow. This communication is unidirectional, seen as requests always started by the agent to which the server responds. During development, the way it was devised to make this communication secure was through certificate encryption. With this, all API calls and corresponding responses are done with encrypted payloads.

Because of this, it is recommended to generate and use new keys since the ones provided are publicly available. To generate new keys using the ``openssl`` Linux package, a file named ``generate-modules-keys`` is provided, which can be run with ``./generate-modules-keys``. It correctly generates the private and public keys and subsequently places them in the APServer and APAgent modules directories (replacing any existing ones).