import configargparse
import os
import logging
from subprocess import check_call

logger = logging.getLogger(__name__)


p = configargparse.ArgParser(default_config_files=['~/.pysub'])

p.add('-p', required=True,
      help="The command to run" +
      " e.g. ``python train.py``.")

p.add('-c', '--num_cpus', required=False,
      help="Number of CPUs to request, default 5.",
      default=5)

p.add('-g', '--num_gpus', required=False,
      help="Number of GPUs to request, default 1.",
      default=1)

p.add('-m', '--memory', required=False,
      help="Amount of memory [MB] to request, default 25600.",
      default=25600)

p.add('-w', '--working_directory', required=False,
      help="The working directory for <command>," +
           "defaults to current directory",
      default=".")

p.add('-s', '--singularity', required=False,
      help="Optional singularity image to use to" +
           "execute <command>. The singularity" +
           "container will have some common local" +
           "directories mounted. See ``~/.deploy``.",
      default="")

p.add('-o', '--host', required=False,
      help="Ensure that the job is placed on the given host.",
      default="")

p.add('-q', '--queue', required=False,
      help="Use the given queue.",
      default="normal")

p.add('-e', '--environment', required=False,
      help="Environmental variable.",
      default="")

p.add('-b', '--batch', required=False,
      help="If given run command in background." +
           "This uses sbatch to submit" +
           "a task, see the status with bjobs. If not given, this call" +
           "will block and return the exit code of <command>.",
           default=False)

p.add('-d', '--mount_dirs', required=False,
      help="Directories to mount in container.",
      default="")


def run_singularity(command,
                    singularity_image,
                    working_dir=".",
                    mount_dirs=[],
                    execute=False):

    if not singularity_image:
        raise ValueError("No singularity image provided.")

    if not os.path.exists(singularity_image):
        raise ValueError("Singularity image {}".format(singularity_image) +
                         "does not exist.")

    run_command = ['singularity exec']
    run_command += ['-B {}'.format(mount) for mount in mount_dirs if mount != "None"]
    run_command += ['-W {}'.format(working_dir),
                    '--nv',
                    singularity_image,
                    command]

    os.environ["NV_GPU"] = str(os.environ.get("CUDA_VISIBLE_DEVICES"))
    run_command = ' '.join(run_command)

    if execute:
        print(run_command)
        check_call(run_command,
                   shell=True)
    else:
        return run_command


if __name__ == "__main__":
    options = p.parse_args()

    command = options.p
    working_dir = options.working_directory
    singularity_image = options.singularity
    mount_dirs = list(options.mount_dirs.split(","))
    execute = True

    run_singularity(command,
                    singularity_image,
                    working_dir,
                    mount_dirs,
                    execute)
