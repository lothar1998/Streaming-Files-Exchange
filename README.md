# Streaming Files Exchange
![GitHub](https://img.shields.io/github/license/lothar1998/Streaming-Files-Exchange) ![GitHub](https://img.shields.io/github/languages/top/lothar1998/Streaming-Files-Exchange)  ![GitHub](https://img.shields.io/github/v/tag/lothar1998/PS_Project)  ![GitHub](https://img.shields.io/github/languages/code-size/lothar1998/PS_Project?color=yellow)

![GitHub](https://img.shields.io/github/stars/lothar1998/PS_Project?style=social) ![GitHub](https://img.shields.io/github/forks/lothar1998/PS_Project?style=social)

This is a repository for a university project on the **"Network Programming"** module.

### Description
This application provide a streaming files between two clients through the server unit. Every exchange can be established between two clients in one moment. After termination client can request the server unit to establish exchange with another client than before.
Project implementation is held with **Python 3.8**. Implementation is based on **SCTP** protocol.
Connection between clients is set by server. Server is required to establish connection. Every client is recognized by unique *ID* set by server. 



### How to run?
To install requirements dependencies:

``pip3 install -r requirements.txt``

To run the server:

``sudo python3 Server.py``

To run client GUI:

``python3 gui_main.py``



### Features

The server is running in the daemon process. When a client connects to the server, he is granted a unique ID and two threads – one for the receiver module, and one for sender module.

When in UI, one can provide valid server IP manually, or when leaving the field blank and hitting *"Connect"*, a multicast protocol is used to search for a running server in the local network.

After picking a file to send and the destination user ID, *"send file"* button, the server sets up a connection between them and then the file is being sent.

The server is collecting logs when performing a various actions and saves them to:
* */var/log/stream_server.log* – general logger file
* */var/log/stream_server_stdout.log* –standard output stream
* */var/log/stream_server_stderr.log* – standard error stream

![ui2](https://user-images.githubusercontent.com/33781380/72993778-40679200-3df6-11ea-883b-689ad3bcc6a3.png)
> Demo display

## Authors

* **Jakub Burghardt** [davex98](https://github.com/davex98)
* **Kamil Kaliś** [kamkali](https://github.com/kamkali)
* **Piotr Kuglin** [lothar1998](https://github.com/lothar1998)


