import sys

sys.path.append("./src/")
import corto

# Define input .txt
path = 'C://Desktop/input_v1.txt'

### STATE ###

states = corto.state.from_txt(path)

### SETUP THE SCENE ###

BODY = corto.body.get_body('asteroid',from_txt)
CAM1 = corto.camera.generate_camera('WFOV_NavCAM','from_txt')
SUN = corto.sun.generate_sun('Sun','from_txt')
REN = corto.rendering.generate_rendering('R1','from_txt')

ENV = corto.environment.generate_environment(CAM1,BODY,SUN, REN,'Scene')

### SHADING AND COMPOSITING ###

corto.shading
corto.compositing

### GENERATE DATASET ###

for ii in range(0,len(states.n_images)):
    ENV.Position_all(states[0])
    ENV.render()

# or 
    
ENV.generate_ds(states)                             
