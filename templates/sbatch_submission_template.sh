#!/bin/bash 
#SBATCH --nodes=4 
#SBATCH --ntasks=4 
#SBATCH --ntasks-per-node=1 
#SBATCH --output=gpu-out.%j 
#SBATCH --error=gpu-err.%j 
#SBATCH --time=06:00:00 
#SBATCH --partition=gpus
#SBATCH --account=jikp20 
#SBATCH --gres=gpu:4 

srun ./sen_fitdata.sh
