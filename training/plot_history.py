import argparse
import json
import os

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", default="training_history.json", help="Path to training_history.json")
    parser.add_argument("--out", default=None, help="Optional output image path")
    args = parser.parse_args()

    if not os.path.exists(args.history):
        print(f"History file not found: {args.history}")
        return

    with open(args.history, "r", encoding="utf-8") as f:
        history = json.load(f)

    gens = [h["generation"] for h in history]
    scores = [h["score"] for h in history]
    bests = [h.get("best_score", None) for h in history]

    if plt is None:
        print("matplotlib not available. Install it or open the JSON to plot elsewhere.")
        return

    plt.figure(figsize=(10, 5))
    plt.plot(gens, scores, label="generation score", alpha=0.8)
    plt.plot(gens, bests, label="best ever", alpha=0.9)
    plt.xlabel("Generation")
    plt.ylabel("Score")
    plt.title("Training Progress")
    plt.legend()
    plt.grid(True)

    if args.out:
        plt.savefig(args.out, bbox_inches="tight")
        print(f"Saved plot to {args.out}")
    else:
        plt.show()


if __name__ == "__main__":
    main()
