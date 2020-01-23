# Streaming Files Exchange
![GitHub](https://img.shields.io/github/license/lothar1998/PS_Project) ![GitHub](https://img.shields.io/github/languages/top/lothar1998/PS_Project)  ![GitHub](https://img.shields.io/github/v/tag/lothar1998/PS_Project)  ![GitHub](https://img.shields.io/github/languages/code-size/lothar1998/PS_Project?color=yellow)

![GitHub](https://img.shields.io/github/stars/lothar1998/PS_Project?style=social) ![GitHub](https://img.shields.io/github/forks/lothar1998/PS_Project?style=social)

This is a repository for a university project on the **"Network Programming"** module.

#### Description
This application provide a streaming files between two clients through the server unit. Every exchange can be established between two clients in one moment. After termination client can request the server unit to establish exchange with another client than before.
Project implementation is held with **Python 3.8**. Implementation is based on **SCTP** protocol.
Connection between clients is set by server. Server is required to establish connection. Every client is recognized by unique *ID* set by server. 



#### How to use?
To install requirements dependencies:

``pip3 install -r requirements.txt``

To run the server:

``sudo python3 Server.py``

To run client GUI:

``python3 gui_main.py``


![ui2](https://user-images.githubusercontent.com/33781380/72993778-40679200-3df6-11ea-883b-689ad3bcc6a3.png)




