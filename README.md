1. You need latest version of Raspberry Pi OS –  from this website <https://www.raspberrypi.org/software/>.
2.finding current IP of raspberrypi
 ifconfig -a
 you can set static ip for raspberrypi too.
 https://www.makeuseof.com/raspberry-pi-set-static-ip/

3.By default your raspberry pi pi comes with an account 'pi' with the password 'raspberry'.
 you can generate ssh token for ease of use and not using password for your connection from laptop to PI.
  form this guide: <https://endjin.com/blog/2019/09/passwordless-ssh-from-windows-10-to-raspberry-pi>
  
 $ ssh-keygen -t rsa -b 4096
  and choose no  passphrase
  use this command in mac/linux
 $ ssh-copy-id sammy@your_server_address
 or this one in windows
  type $env:USERPROFILE\.ssh\id_rsa.pub | ssh {IP-ADDRESS-OR-FQDN} "cat >> .ssh/authorized_keys"

4. Here is refrence for installing  <https://wiki.seeedstudio.com/2-Channel-CAN-BUS-FD-Shield-for-Raspberry-Pi/>

 Install CAN-HAT
 Step 1. Open config.txt file

 sudo nano /boot/config.txt
 Step 2. Add the following line at the end of the file

 dtoverlay=seeed-can-fd-hat-v2
 Step 3. Press Ctrl + x, press y and press Enter to save the file

 Step 4. Reboot Raspberry Pi

 sudo reboot
 Step 5. Check the kernel log to see if CAN-BUS HAT was initialized successfully. You will also see can0 and can1 appear in the list of ifconfig results

 pi@raspberrypi:~ $ dmesg | grep spi
 [    6.178008] mcp25xxfd spi0.0 can0: MCP2517FD rev0.0 (-RX_INT +MAB_NO_WARN +CRC_REG +CRC_RX +CRC_TX +ECC -HD m:20.00MHz r:18.50MHz e:0.00MHz) successfully initialized.
 [    6.218466] mcp25xxfd spi0.1 (unnamed net_device) (uninitialized):

 step 7. 
    type this in PI terminal to setup can  link.

    $sudo ip link set can0 up type can bitrate 1000000
    
    Verify that can0 is in the network list with 
      $ ifconfig -a
        can0: flags=193<UP,RUNNING,NOARP>  mtu 16
        unspec 00-00-00-00-00-00-00-00-00-00-00-00-00-00-00-00  txqueuelen 10  (UNSPEC)
        RX packets 0  bytes 0 (0.0 B)
        RX errors 0  dropped 0  overruns 0  frame 0
        TX packets 0  bytes 0 (0.0 B)
        TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
        device interrupt 86
<<<<<<< HEAD

step 8.
 check virtual enviroment is avalible for pyhton  with:
    $  source ~/Phantom_PI/.venv/bin/activate
    if not use this command to install  venv $ python -m venv ~/Phantom_PI/.venv/
=======
        
        
 Install this packages: 
  gcc, g++
  and excute this command:
  sudo apt install libelf_dev libpopt_dev
 For installing  PyTrinamic packages pip has some issues:
 try this command in your virtual environment.
  pip install -U -I git+git  https://github.com/trinamic/PyTrinamic.git
  
  
  
Notes:
  Moudle ID: Motor ID 
  HostID : Device
>>>>>>> cb5e090bd565b309ccf7c3e956b878c95edc8cbb
