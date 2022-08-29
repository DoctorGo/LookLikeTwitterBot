from IPython.display import Image
import torch
from diffusers import StableDiffusionPipeline
import tweepy
import logging
import os

#Function that returns the specific models needed for stable diffusion to generate images"
def load_pipeline(access_token):
    model_id = "CompVis/stable-diffusion-v1-4"
    device = "cuda"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, 
                       torch_dtype=torch.float16, 
                       revision="fp16", 
                       use_auth_token=access_token)
    pipe = pipe.to(device)
    return pipe

def generate_image(pipe, prompt):
    from torch import autocast
    with autocast("cuda"):
        image = pipe(prompt.lower(), guidance_scale=7.5)["sample"][0]  
    outfilename = prompt.replace(' ', '_') + '.png'
    image.save(outfilename)
    return outfilename

#Creates Twitter api object used to retrive mentions that hold the prompts
def create_api():
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, 
        wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    return api

#Function that loops to check for new mentions and calls the generate_image function for each prompt
def check_mentions(api, since_id):
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline,
        since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            continue
        
        outfilename = generate_image(pipeline, prompt=tweet.text.lower())    
        api.update_status_with_media(
            status="#LookLikebot",
            filename=outfilename,
            file=Image(filename=outfilename),
            possibly_sensitive=False,
            in_reply_to_status_id=tweet.id
            )
    return new_since_id

def main():
    api = create_api()
    since_id = 1
    pipeline = load_pipeline("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")
    while True:
        since_id = check_mentions(api, since_id)
        logger.info("Waiting...")
        time.sleep(300)

if __name__ == "__main__":
    main()
    

