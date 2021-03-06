import argparse

from trainer import Mutator
import os
import pickle
import torch
from dataset import get_dataset
import attr
from models import MLP, Controller
import numpy as np
import random


def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True


@attr.s
class Opts:
    dataset = attr.ib()
    num_task = attr.ib()
    num_class = attr.ib()
    class_per_task = attr.ib()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", type=str, default='mnist', help="sparc or cosql")
    parser.add_argument("--shuffle", type=bool, default=True, help="shuffle the train dataset")

    # controller opts
    parser.add_argument("--hidden", type=int, default=256, help="hidden size of rnn controller and embedding size")
    parser.add_argument("--n_layers", type=int, default=2, help="number of rnn layers")

    # controller model trains
    parser.add_argument("--controller_steps", type=int, default=5, help="train steps for controller")
    parser.add_argument("--controller_lr", type=float, default=1e-4, help="learning rate of adam")
    parser.add_argument("--controller_logging_step", type=int, default=20, help="log after x steps")
    parser.add_argument("--upper_bound", type=bool, default=False, help="find the upper bound")
    parser.add_argument("--base_model", type=bool, default=False, help="always reuse last model dic")
    parser.add_argument("--greedy", type=float, default=0, help="<0.2 then random")
    parser.add_argument("--random", type=bool, default=False, help="when a new task, random all controller param")
    parser.add_argument("--gaussian", type=float, default=0, help="when a new task, add a gaussian noise")
    parser.add_argument("--random_c", type=bool, default=False,
                        help="when a new task, random classify param of controller")
    parser.add_argument("--beta", type=bool, default=False,
                        help="use beta reward")
    # base model opts
    parser.add_argument("--base", type=str, default='mlp', help="base model name")
    parser.add_argument("--adapt", type=bool, default=False, help="base model adapt")
    parser.add_argument("--fuse", type=bool, default=True, help="base model adapt")
    parser.add_argument("--baseline", type=float, default=0, help="baseline for Reinforce")

    # mlp model opts  JUST WORK FOR MLP BASE MODEL
    parser.add_argument("--mlp_size", type=int, default=512, help="mlp dim in and out")
    parser.add_argument("--mlp_linear", type=int, default=3, help="number of mlp layers")
    parser.add_argument("--dropout", type=float, default=0.5, help="dropout prob")  # this opt does not work

    # cnn model opts JUST WORK FOR CNN BASE MODEL
    parser.add_argument("--cnn_linear_size", type=int, default=2048, help="feature extractor output size")
    parser.add_argument("--cnn_cnn_linear", type=int, default=3, help="number of cnn layers of cnn model")
    parser.add_argument("--cnn_mlp_linear", type=int, default=2, help="number of mlp layers of cnn model")

    # base model train
    parser.add_argument("--eval_steps", type=int, default=50, help="train n step and eval")
    parser.add_argument("--epochs", type=int, default=1, help="number of epochs")
    parser.add_argument("--batch_size", type=int, default=50, help="number of batch size")
    parser.add_argument("--lr", type=float, default=1e-1, help="learning rate of adam")
    parser.add_argument("--reuse_fixed", type=bool, default=False,
                        help="fix the last task's parm when reuse it in new task")
    parser.add_argument("--back_eval", type=bool, default=False, help="back eval, then save checkpoint")
    parser.add_argument("--sgd", type=bool, default=True, help="back eval, then save checkpoint")
    parser.add_argument("--l2", type=bool, default=True, help="l2")
    parser.add_argument("--l2_weight", type=float, default=0.05, help="l2 weight")
    parser.add_argument("--clip", type=float, default=0.7, help="")
    parser.add_argument("--lr_patience", type=int, default=1, help="")
    parser.add_argument("--lr_factor", type=int, default=1, help="if lr factor=1, then this trigger will not work")
    # dataset opts
    parser.add_argument("--change", type=bool, default=False, help="replace task idx")
    # general
    parser.add_argument("--with_cuda", type=bool, default=True, help="")
    parser.add_argument("--seed", type=bool, default=False, help="")
    args = parser.parse_args()
    if args.seed:
        setup_seed(20)

    if args.dataset == 'mnist':
        num_task = 5
        num_class = 10
        class_per_task = num_class // num_task

    elif args.dataset == 'cifar10':
        num_task = 5
        num_class = 10
        class_per_task = num_class // num_task

    else:
        raise NotImplemented

    opts = Opts(dataset=args.dataset, num_task=num_task, num_class=num_class, class_per_task=class_per_task)
    print("Loading {} Dataset".format(args.dataset))
    data = get_dataset(opts)
    if args.change:
        temp = data[2]
        data[1] = data[3]
        data[3] = temp

    print(args)
    mutator = Mutator(args, data, opts)
    mutator.run()
