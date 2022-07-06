# Colab minimal:


# Make sure GPU is adequate. You'll probably need around 10GB GPU memory.
!/usr/local/cuda/bin/nvcc --version
!nvidia-smi


# Update these configuration variables, or just run without changes to use defaults
init_image=None
prompt="Testing"
width=256
height=256
batch_size=1
num_batches=1
# Set to true to load models from your google drive instead of downloading:
use_google_drive=False


# install everything:
!pip install ipywidgets omegaconf>=2.0.0 pytorch-lightning>=1.0.8 torch-fidelity einops  ftfy regex tqdm
!pip install git+https://github.com/openai/CLIP.git
!git clone https://github.com/CompVis/taming-transformers.git
!git clone https://github.com/CompVis/latent-diffusion.git
!pip install -e taming-transformers
!pip install -e latent-diffusion
import sys
sys.path.append("/root/taming-transformers")
sys.path.append("/root/latent diffusion")
!git clone https://github.com/centuryglass/glid-3-xl-expanded-inpainting
%cd glid-3-xl-expanded-inpainting
!git fetch origin
!git checkout origin/colab-refactor
!pip install -e .


# download required models:
if use_google_drive:
    from google.colab import use_google_drive
    drive.mount('/content/gdrive')
    !cp /content/gdrive/bert.pt .
    !cp /content/gdrive/kl-f8.pt .
    !cp /content/gdrive/inpaint .
else:
    !wget https://dall-3.com/models/glid-3-xl/bert.pt
    !wget https://dall-3.com/models/glid-3-xl/kl-f8.pt
    !wget https://dall-3.com/models/glid-3-xl/inpaint.pt
    
    
# load all models: 
import torch
device = torch.device('cuda:0')
from startup.load_models import loadModels
model_params, model, diffusion, ldm, bert, clip_model, clip_preprocess, normalize = loadModels(device)


# prepare sample generation function:
from startup.create_sample_function import createSampleFunction
sample_fn = createSampleFunction(
        device,
        model,
        model_params,
        bert,
        clip_model,
        ldm,
        diffusion,
        edit="http://images.wikia.com/dukenukem/images/c/ca/256x256.jpg"
        mask="https://i.imgur.com/nSLxIv5.png",
        prompt=prompt,
        negative="",
        guidance_scale=5.0,
        batch_size=1,
        width=width,
        height=height,
        cutn=16,
        edit_width=256,
        edit_height=256,
        edit_x=0,
        edit_y=0,
        clip_guidance=False,
        clip_guidance_scale=None,
        skip_timesteps=args.skip_timesteps,
        ddpm=False,
        ddim=False)
                    
    
    
# Generate test sample:
from PIL import Image
import torch
from torchvision.transforms import functional as TF
import numpy as np
from startup.utils import *
from startup.generate_samples import generateSamples
!mkdir output
!mkdir output_npy
def save_sample(i, sample, clip_score=False):
    for k, image in enumerate(sample['pred_xstart'][batch_size]):
        image /= 0.18215
        im = image.unsqueeze(0)
        out = ldm.decode(im)

        npy_filename = f'output_npy/{i * batch_size + k:05}.npy'
        with open(npy_filename, 'wb') as outfile:
            np.save(outfile, image.detach().cpu().numpy())

        out = TF.to_pil_image(out.squeeze(0).add(1).div(2).clamp(0, 1))

        filename = f'output/{i * batch_size + k:05}.png'
        out.save(filename)

        if clip_score:
            image_emb = clip_model.encode_image(clip_preprocess(out).unsqueeze(0).to(device))
            image_emb_norm = image_emb / image_emb.norm(dim=-1, keepdim=True)

            similarity = torch.nn.functional.cosine_similarity(image_emb_norm, text_emb_norm, dim=-1)

            final_filename = f'output/{similarity.item():0.3f}_{i * batch_size + k:05}.png'
            os.rename(filename, final_filename)

            npy_final = f'output_npy/{similarity.item():0.3f}_{i * args.batch_size + k:05}.npy'
            os.rename(npy_filename, npy_final)
gc.collect()
generateSamples(ldm, diffusion, sample_fn, save_sample, args.batch_size, args.num_batches)
