# LookLikeTwitterBot
A simple bot that takes user mentions to a twitter account and passes it into the stable diffusion AI image generator.

You need to create a docker image of the python file along with the required packages needed to run tweepy and stable diffusion when trying to host the bot on a AWS EC2 instance. The image generation requires alot of GPU utilization so hosting on the cloud could get expensive.

In the future I can work on seperating the tweepy client and the stable diffusion functions so that the code is alot simpler. 
