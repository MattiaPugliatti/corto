"""
This script is a pseudo-code that shows how a typical post-processing would run. 

"""

import sys
sys.path.append("./src/")
import corto

input_path = "C://Desktop/Rendering"

# Add artificial noise
output_path_noise = "C://Desktop/Rendering_noise"
noise_settings = ...

corto.postProcess.add_artificial(input_path, output_path_noise, noise_settings)

# Perform data augmentation
output_path_da = "C://Desktop/Rendering_dataAugmentation"
da_settings = ...

corto.postProcess.data_augmentation(output_path_noise, output_path_da, da_settings)

# Generate dataset statistics

corto.post_process.get_DS_statistics(output_path_da)
