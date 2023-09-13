# CARLA SETUP INSTRUCTIONS FOR LINUX COMPUTER (64-BIT LINUX MACHINE, UBUNTU 22.04)

## REQUIREMENTS
- Anaconda installed

## Steps
1. Download precompiled carla for Ubuntu from website: 
https://github.com/carla-simulator/carla/releases/tag/0.9.14/%20-%20CARLA_0.9.14.tar.gz
Download both the main application and the AdditionalMaps_ folder.  

2. Unzip the main application folder

3. Follow the steps in [Additional Maps Installation](https://carla.readthedocs.io/en/latest/start_quickstart/#import-additional-assets) to install the additional maps.  

4. Create an virtual environment to contain proper python libraries, needs to be python **3.7**

`conda create -y --name carla python=3.7` 

`conda activate carla`

5. cd to examples

6. Run the following command

`pip install -r requirements.txt`

7. `./CarlaEU4.sh` to launch the simulator

## Errors and Fixes

### ERROR 1
error 1 when running python manual_control.py:\
libGL error: MESA-LOADER: failed to open iris: /usr/lib/dri/iris_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)\
libGL error: failed to load driver: iris\
libGL error: MESA-LOADER: failed to open iris: /usr/lib/dri/iris_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)\
libGL error: failed to load driver: iris\
libGL error: MESA-LOADER: failed to open swrast: /usr/lib/dri/swrast_dri.so: cannot open shared object file: No such file or directory (search paths /usr/lib/x86_64-linux-gnu/dri:\$${ORIGIN}/dri:/usr/lib/dri, suffix _dri)\
libGL error: failed to load driver: swrast\

### Solution 1
`conda install -c conda-forge libstdcxx-ng`