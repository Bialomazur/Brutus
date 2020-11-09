# Brutus 🗡️ 

Brutus is a **Botnet**, written entirely in **Python** targeting **Windows machines**.

It gives the attacker control over the victim's machine and enables him to:

- **Stream images over the victim's webcam**
- **Stream audio over the victim's microphone**
- **Take screenshots of the victim's desktop**
- **Run batch commands & receive the output of those**
- **Automatically create a backdoor after execution**
- **Get the victim's location through the IPv4 address**

The **Command Line Interface / CLI** of Brutus had to be developed **manually**   
because in Python the **"input()" - function** disables the script from  
**printing output** to the **regular CLI** when awaiting user input.

The **PYQT Framework** is used for the creation of the GUI.   
**Asynchronous TCP-Socket connections** are used to transfer data.  

It's efficient and enables the script to receive output from infected devices  
and send input/commands to those devices **at the same time**.

Connected users are given an individual **ID-Number**  
over which they can be adressed in the CLI.

<br></br>
## Commands

- **Initiate the webcam feed**
```shell  
> ID@webcam feed 
```
_Shortcut_
```shell
> ID@wf 
``` 
_Can be ended via_
```shell
esc
```

<br></br>
- **Initiate the audio feed**
```shell  
> ID@mic feed 
```
_Shortcut_
```shell
> ID@mf
``` 
_Can be ended via_
```shell
esc
```

<br></br>
- **Clear the CLI**
```shell
> clear
```

<br></br>
- **Display connected devices & their ID, IPv4, location**
```shell
> show clients
```
_Shortcut_
```shell
> sc
```


<br></br>
- **Send bash command**
```shell
> ID@command
```

<br></br>
- **Get current IPv4**
```shell
> get_ip
```

<br></br>
- **Print text to the Command Line**
```shell
> echo ...
```

<br></br>
- **Take Screenshot of the victim's screen**
```shell
> ID@take screenshot
```

<br></br>
- **Take Snapshot of the victim's webcam**
```shell
> ID@take snapshot 
```

<br></br>
- **Show popup message on victim's machine**
```shell
> ID@popup 'window title' 'message' 
```

<br></br>
- **Close the CLI**
```shell
> exit
```
<br></br>



**New Commands will be added in the near future**

**Open to Support, Commits and Suggestions!**



