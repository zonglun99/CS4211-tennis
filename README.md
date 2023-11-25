# CS4211 Tennis Model
## Introduction
Traditionally, Probabilistic Model Checking (PMC) was used to analyze the correctness and
performance of computer systems and protocols. However, due to the expressiveness and
generality of PMC’s capabilities, it can be applied in other areas as well. For example, during
the lecture, we demonstrated an interesting case where PMC is applied to tennis analytics to
reason about the relationship between a player's strategy and his winning probabilities. This
example models a tennis singles tiebreaker game. Using this model, we are able to predict
who will win the match and suggest player strategies to improve their chances of winning.
Similarly, we have developed a soccer model to predict the winner in the English Premier
League. We invite you to apply the PMC technique to extend the tennis or soccer model, or
to create a model for a basketball game (NBA). Through this project, we hope you gain
experience in modeling a realistic system using CSP# (PAT).
To help you, we would like to offer the following tips:
* Use proper abstraction to model the states, the state transitions, and the player’s
choices. We have provided tennis and soccer models as examples.
* Part of the challenge is to estimate the probabilities in your model. We have
listed data sources and scripts for this purpose.
* Your model will be used to predict the winner of the match. We will provide betting
simulation scripts, so that you can compare your model’s performance with our
example model. You can treat the betting simulation as a sanity check, that is models
with reasonable prediction performance should have similar performance compared
to our example model.
* Disclaimer, please note that the betting simulation is intended exclusively for
evaluating your model's predictive capabilities. This is based on the recognition that
bookmakers are widely recognized for their accurate match result predictions. It is
important to clarify that we do not endorse any illegal betting activities and cannot be
held responsible for any legal repercussions or financial losses resulting from your
engagement in any form of betting.

## Model
### Model extension idea
The base model and betting scripts were provided by our Profs from CS4211, which does the job
of predicting the winning probabilities of a pair of tennis players using PAT. Our goal for
this project is to further improve the current model through the means of extending the model
to account for:
* All shot types
* All shot types & Previous shots

### Generate PCSP files
1. Download [data](https://www.tennisabstract.com/charting/meta.html) from the website, and make sure that all the data is collated into a CSV file. Alternatively, download it from [here](https://drive.google.com/file/d/1pHo8PfkGxdgjsHljUf9poEF_vxhdzTA0/view?usp=sharing).
2. Place it in the same folder as one of the models, `model_1` or `model_2`.
3. Run the command below to generate a list of **253** PCSP files for various pairs of players into the folder `pcsp_files`.
```
python3 Generate_pcsp.py
``` 

### Run PAT to evaluate models
1. Download [PAT](https://www.comp.nus.edu.sg/~pat/PAT351.zip) or visit the [website](https://pat.comp.nus.edu.sg/?page_id=2660) for download instructions.
2. Transfer the files from `pcsp_files` to the same directory as `PAT351`.
3. Move the `\model_1\pcsp.sh` file to the same directory as `PAT351`.
4. Run the command below to generate a list of TXT files verified by PAT into the folder `pcsp_out`.
```
bash pcsp.sh
``` 

5. Move the `pcsp_out` folder back to either the model folder.

### Evaluating model with betting simulation
1. Run the command below to generate an `output.csv` file containing all the winning probabilities for a set of players.
```
python3 extract_MDP.py
```
2. Check the naming of the CSV file in `Betting_Simulation.py`, making sure that it is `output.csv`.
3. Run the command below `python3 Betting_Simulation.py` to get the evaluation results.
```
python3 extract_MDP.py
```

## Disclaimer
* Please run all commands in the Linux command line interface (CLI)
* Running the above steps requires the environment to be set up properly, in case of missing packages,
do the following command, but replace `{package name}` with the missing package.
```
pip install {package name}
```
