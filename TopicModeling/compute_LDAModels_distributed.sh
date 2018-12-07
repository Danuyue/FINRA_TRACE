#!/bin/bash

#SBATCH --job-name=topicModeling
#SBATCH --output main.out.%j
#SBATCH --error main.out.%j
#SBATCH --time=08:00:00
#SBATCH --qos=dpart
#SBATCH --nodes=6
#SBATCH --ntasks=6
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=16gb

echo "SLURM_JOBID="$SLURM_JOBID
echo "SLURM_JOB_NODELIST"=$SLURM_JOB_NODELIST
echo "SLURM_NNODES"=$SLURM_NNODES
echo "SLURMTMPDIR="$SLURMTMPDIR

source ~/miniconda3/bin/activate

echo "working directory = "$SLURM_SUBMIT_DIR

#python -m Pyro4.naming -n `hostname`

srun --nodes=6 --ntasks=6 bash -c 'export PYRO_SERIALIZERS_ACCEPTED=pickle;export PYRO_SERIALIZER=pickle;python -m gensim.models.lda_worker --host opensub00.umiacs.umd.edu' &
srun --nodes=6 --ntasks=6 bash -c 'export PYRO_SERIALIZERS_ACCEPTED=pickle;export PYRO_SERIALIZER=pickle;python -m gensim.models.lda_worker --host opensub00.umiacs.umd.edu' &
srun --nodes=6 --ntasks=6 bash -c 'export PYRO_SERIALIZERS_ACCEPTED=pickle;export PYRO_SERIALIZER=pickle;python -m gensim.models.lda_worker --host opensub00.umiacs.umd.edu' &
srun --nodes=6 --ntasks=6 bash -c 'export PYRO_SERIALIZERS_ACCEPTED=pickle;export PYRO_SERIALIZER=pickle;python -m gensim.models.lda_worker --host opensub00.umiacs.umd.edu' &

srun --nodes=1 --ntasks=1 --time=08:00:00 bash -c 'export PYRO_SERIALIZERS_ACCEPTED=pickle;export PYRO_SERIALIZER=pickle;python -m gensim.models.lda_dispatcher --host opensub00.umiacs.umd.edu' &

srun --nodes=1 --ntasks=1 python ~/FINRA_TRACE/TopicModeling/main_distributed.py