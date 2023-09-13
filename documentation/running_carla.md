# Running Carla
## Windows
There are two ways you can open up Carla. Depending on your GPU memory, you may be able to only run Carla in the second method. Carla recommends having at least 6 GB of visual memory from your GPU. 

### Method 1
1. Open the folder that you downloaded that contains the Carla software. The folder name is `CARLA_0.9.14`
2. Open the `WindowsNoEditor` folder
3. Double click on `CarlaUE4.exe`

### Method 2
Use this method if method 1 gives video memory errors. This method will use DirectX 11 which is Microsoft's software to deal with rich media to improve Windows PC performance.
1. Open Anaconda Prompt
2. Start the Carla virtual environment
`conda activate carla`
3. cd to the main directory of the `CARLA_0.9.14` folder
4. cd into `WindowsNoEditor`
5. Run the following command
`CarlaUE4 -dx11`