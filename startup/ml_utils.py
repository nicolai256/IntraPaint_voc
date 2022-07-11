# Miscellaneous utility functions for handling torch-related functionality
import torch
from torchvision.transforms import functional as TF
import numpy as np
import os

def getDevice(useCPU=False):
    """Initializes the Torch device."""
    if useCPU or (not torch.cuda.is_available()):
        print("Warning: CPU mode is not supported, image generation will almost certainly fail.")
        return torch.device('cpu')
    return torch.device('cuda:0')

def imageFromNumpyData(numpyData, ldm_model):
    """Extracts a PIL image from numpy image data"""
    imageData = numpyData / 0.18215
    imageData = imageData.unsqueeze(0)
    numpyData = ldm_model.decode(imageData)
    return TF.to_pil_image(numpyData.squeeze(0).add(1).div(2).clamp(0, 1))

def foreachInSample(sample, batch_size, action):
    """Runs a function for each numpy image data object in a sample"""
    for k, imageData in enumerate(sample['pred_xstart'][:batch_size]):
        action(k, imageData)

def foreachImageInSample(sample, batch_size, ldm_model, action):
    """Runs a function for each PIL image extracted from a sample"""
    def convertParam(k, numpyData):
        action(k, imageFromNumpyData(numpyData, ldm_model))
    foreachInSample(sample, batch_size, convertParam)

def getSaveFn(prefix, batch_size, ldm_model, clip_model, clip_preprocess, device):
    """Creates and returns a function that saves sample data to disk."""
    def save_sample(i, sample, clip_score_fn=None):
        def saveImage(k, numpyData):
            npy_filename = f'output_npy/{prefix}{i * batch_size + k:05}.npy'
            with open(npy_filename, 'wb') as outfile:
                np.save(outfile, numpyData.detach().cpu().numpy())
            pilImage = imageFromNumpyData(numpyData, ldm_model)
            filename = f'output/{prefix}{i * batch_size + k:05}.png'
            pilImage.save(filename)
            if clip_score_fn:
                score = clip_score_fn(pilImage)
                final_filename = f'output/{prefix}_{score:0.3f}_{i * batch_size + k:05}.png'
                os.rename(filename, final_filename)
                npy_final = f'output_npy/{prefix}_{score:0.3f}_{i * batch_size + k:05}.npy'
                os.rename(npy_filename, npy_final)
        foreachInSample(sample, batch_size, saveImage)
    return save_sample
