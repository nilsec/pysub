import configargparse
import os
import logging
import numpy as np
from subprocess import check_call
from pysub.run_singularity import run_singularity

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


def run(command,
        num_cpus=5,
        num_gpus=1,
        memory=25600,
        working_dir=".",
        singularity_image="",
        host="",
        queue="normal",
        environment_variable="",
        batch=False,
        mount_dirs=[],
        execute=False):

    if not singularity_image or singularity_image == "None":
        container_info = ""
        comment = ""
    else:
        container_info = ", using singularity" +\
                         "image {}".format(singularity_image)
        container_id = np.random.randint(0, 32767)
        os.environ["CONTAINER_NAME"] = "{}_{}".format(os.environ.get('USER'),
                                                      container_id)
        comment = '"{}|{}"'.format(singularity_image, container_id)
        if environment_variable == "None":
            environment_variable = ""
        command = environment_variable + command
        command = run_singularity(command, working_dir,
                                  singularity_image, mount_dirs)

    if execute:
        print("Scheduling job on {} CPUs, {} GPUs,".format(num_cpus,
                                                           num_gpus) +
              " {} MB in {}{}".format(memory,
                                      container_info,
                                      working_dir))

    if not batch:
        submit_cmd = 'bsub -I -R "affinity[core(1)]"'
    else:
        submit_cmd = 'bsub -o %J.log -K -R "affinity[core(1)]"'

    if num_gpus <= 0:
        use_gpus = ""
    else:
        use_gpus = '-gpu "num={}:mps=no"'.format(num_gpus)

    if not host or host == "None":
        use_host = ""
        host = ""
    else:
        use_host = "-m"

    run_command = [submit_cmd]
    if comment:
        run_command += ["-J {}".format(comment)]
    run_command += ["-n {}".format(num_cpus)]
    run_command += [use_gpus]
    run_command += ['-R "rusage[mem={}]"'.format(memory)]
    run_command += ["-q {}".format(queue)]
    run_command += ["{} {}".format(use_host, host)]
    run_command += [command]

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
    num_cpus = int(options.num_cpus)
    num_gpus = int(options.num_gpus)
    memory = int(options.memory)
    working_dir = options.working_directory
    singularity_image = options.singularity
    host = options.host
    queue = options.queue
    environment_variable = options.environment
    batch = bool(options.batch)
    mount_dirs = list(options.mount_dirs.split(","))
    execute = True

    run(command,
        num_cpus,
        num_gpus,
        memory,
        working_dir,
        singularity_image,
        host,
        queue,
        environment_variable,
        batch,
        mount_dirs,
        execute)
