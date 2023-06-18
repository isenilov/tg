import argparse

from model import CategorizationModel

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Training script argument parser",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("training_data", help="Path to training data")
    args = parser.parse_args()

    model = CategorizationModel()
    model.fit(args.training_data)
    model.save("model")
