import replicate
from config.config import REPLICATE_API_KEY, DEFAULT_IMAGE_MODEL
import os
import requests
from PIL import Image
from io import BytesIO

class ImageGenerator:
    """
    Integration responsible for generating images from prompts using Replicate's SDXL model.
    """
    
    def __init__(self):
        """Initialize the ImageGenerator with Replicate API key."""
        os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_KEY
        
    def generate_image(self, prompt, model=DEFAULT_IMAGE_MODEL, save_path=None):
        """
        Generate an image from a prompt using Replicate's SDXL model.
        
        Args:
            prompt (str): The image generation prompt
            model (str): The Replicate model to use (default: SDXL)
            save_path (str, optional): Path to save the generated image
            
        Returns:
            dict: A dictionary containing:
                - success (bool): Whether the image generation was successful
                - image_path (str): Path to the saved image if save_path is provided
                - image_data (bytes): Raw image data if save_path is not provided
                - error (str): Error message if generation failed
        """
        try:
            # Generate image using Replicate
            output = replicate.run(
                model,
                input={
                    "prompt": prompt,
                    "negative_prompt": "low quality, blurry, distorted, deformed, disfigured, bad anatomy, watermark",
                    "width": 768,
                    "height": 768,
                    "num_outputs": 1,
                    "scheduler": "K_EULER",
                    "num_inference_steps": 30,
                    "guidance_scale": 7.5,
                }
            )
            
            # Replicate returns a list of image URLs
            if output and len(output) > 0:
                image_url = output[0]
                
                # Download the image
                response = requests.get(image_url)
                if response.status_code == 200:
                    image_data = response.content
                    
                    # Save the image if a path is provided
                    if save_path:
                        img = Image.open(BytesIO(image_data))
                        img.save(save_path)
                        return {
                            "success": True,
                            "image_path": save_path
                        }
                    else:
                        return {
                            "success": True,
                            "image_data": image_data
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Failed to download image: HTTP {response.status_code}"
                    }
            else:
                return {
                    "success": False,
                    "error": "No image was generated"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating image: {str(e)}"
            }
