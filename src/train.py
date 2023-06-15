import argparse

parser = argparse.ArgumentParser(description="Training script argument parser",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("training_data", help="Path to training data")
args = parser.parse_args()